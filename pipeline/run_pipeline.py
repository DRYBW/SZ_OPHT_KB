#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — one-command annotation entry point (S0 sample pre-check shadow layer + Stage A standard processing + Stage B per-cluster evidence collection).

Usage (from repo root):
  python pipeline/run_pipeline.py --input <10X dir|multi-10X parent dir|data.h5ad> \\
      [--species human|mouse|auto] [--tissue <dictionary name|auto>] --out results/run1 \\
      [--group-col treatment]

S0 sample pre-check (WIRE-P1, REV-1=astra ruling: Phase-1 runs in shadow mode):
  - Default run: three evidence channels + six hard gates decide species x tissue automatically;
    all readings are written in full to `s0_gate_report.json`; gate passed -> Stage A/B parameters
    are backfilled (an explicit human --species/--tissue counts as an override, recorded in the
    report as s0_overridden_by_user for the audit trail).
  - **Shadow semantics: a failed gate (abstain) does not block the run** — REPORT_ABSTAIN.md is
    written (a human-readable record, not a terminal artifact) and execution continues (provided
    species/tissue remain resolvable from human parameters; if neither is resolvable, the run
    exits on missing arguments).
    Blocking hard gate = Phase 3 (switched on via `EYEKB_S0_ENFORCE=1` after later acceptance
    stages; this batch defaults to non-blocking).
  - Known-issues consumption is also shadow: risk flags + review requirements go into two
    decisions columns and the report header block (pipeline/pitfalls/, short rules for the
    blind-review-safe strip; non-blind-safe rules emit structured flags only);
    **no automatic relabeling/downgrading/vote-overriding** — adjudication changes still go
    through the original three independent reviewer votes and the hard gates.
  - Full rollback: `EYEKB_S0_GATE=0` = pre-wiring legacy behavior (no S0, no flags,
    --species/--tissue mandatory), used for air-gapped baseline comparison (astra T4.3) and emergencies.

Outputs (all under --out):
  stage_a/processed.h5ad          processed matrix (QC/normalization/Harmony marks/leiden)
  stage_a/figures/*.png           QC figures (mitochondrial %, genes detected, doublets, UMAP before/after)
  stage_a/cluster_markers.csv     per-cluster wilcoxon top30
  annotation_evidence_report.json per-cluster five-field evidence (structure = pre-wiring contract; known-issues excluded)
  annotation_evidence_report.md   evidence report (with S0 enabled, header block carries the applicable-claim list = human-side shadow injection)
  decisions_template.csv          one row per cluster awaiting human adjudication (decision/proposed_label left empty;
                                   with S0 enabled, pitfall_risk_flags / pitfall_review_required
                                   columns appended — risk hints only, no auto-relabel column)
  mcp_calls.jsonl                 evidence-service call audit trail
  s0_gate_report.json             S0 three-evidence readings + gate reasons + full ranking + override audit trail (absent in rollback state)
  shadow_attention.json           applicable-claim list for this cell type (incl. blind-safe / post-review open flags)
  shadow_flags.jsonl              per-cluster risk-flag audit (auto-rename/auto-downgrade changes always = 0)

Discipline redlines: the default path is **zero LLM**; this entry point contains no automatic
scoring/auto-naming logic; needs_review/abstention is a legal output; the last step from evidence
to conclusion is always completed by the researcher.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---- numeric determinism pins (ERRATA-E3, 2026-09-30) ----
# Measured: without pinned threads, consecutive runs of the same input show 16/15/16 cluster
# jitter (results vary with machine load and BLAS/numba thread scheduling); with
# OMP_NUM_THREADS=1 two runs are byte-identical (processed.h5ad sha matches). Stage A
# (Scrublet/neighborhood graph/Harmony/leiden) is a serial implementation and single-thread
# wall time ~= multithread (measured 110 s), so determinism wins. setdefault preserves explicit
# overrides (reproduction contract = keep the default pins).
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from kb9_consume_guard import demote_kb9  # [KB9B t_3bbc769f] consumer-side narrow guard (env EYEKB_KB9_CONSUME_GUARD)


def known_tissues():
    """Known tissue dictionary = kb/baselines main entries + tissue fields of review-layer entries (mechanically enumerated, never hardcoded)."""
    tis = set()
    for p in (REPO_ROOT / "kb" / "baselines").glob("*.json"):
        if not p.name.startswith(("_", "fetal", "retina__")):
            tis.add(p.stem)
    priors = REPO_ROOT / "kb" / "priors"
    for sub in ("composition", "disease"):
        d = priors / sub
        if d.is_dir():
            for p in d.glob("*.json"):
                try:
                    e = json.loads(p.read_text(encoding="utf-8"))
                    t = (e.get("tissue") or "").strip().lower()
                    if t:
                        tis.add(t)
                except Exception:
                    continue
    return sorted(tis)


def _s0_enabled():
    return (os.environ.get("EYEKB_S0_GATE", "1") or "1").strip().casefold() not in (
        "0", "false", "off", "no")


def _s0_enforce():
    """Phase-3 forward switch: blocking only when EYEKB_S0_ENFORCE=1 is set explicitly; this batch defaults to shadow (non-blocking)."""
    return (os.environ.get("EYEKB_S0_ENFORCE", "") or "").strip().casefold() in (
        "1", "true", "on", "yes")


def run_s0_gate(input_path, sample_col, species_arg, tissue_arg, out, thr_json=None):
    """S0 scoring. Returns (can_run, species, tissue, meta). Always writes s0_gate_report.json."""
    import s0_check
    if thr_json:
        s0_check.THR.update(json.load(open(thr_json)))
    rec = s0_check.gate_from_input(input_path, sample_col=sample_col)
    final = rec["final"]
    overridden = bool(species_arg != "auto" or tissue_arg != "auto")
    meta = {"s0_name": rec["name"], "input_kind": rec["input_kind"],
            "evidence_A_id": rec["evidence_A_id"],
            "evidence_B_symbol": rec["evidence_B_symbol"],
            "evidence_C_tissue": rec["evidence_C_tissue"],
            "final": final, "thresholds": rec["thresholds"],
            "mode": "enforce" if _s0_enforce() else "shadow",
            "s0_overridden_by_user": overridden,
            "manual_species": None if species_arg == "auto" else species_arg,
            "manual_tissue": None if tissue_arg == "auto" else tissue_arg}
    out.mkdir(parents=True, exist_ok=True)

    def _dump():
        (out / "s0_gate_report.json").write_text(
            json.dumps(meta, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    species = species_arg if species_arg != "auto" else (
        final["species_call"] if final["species_call"] in ("human", "mouse") else None)
    tissue = tissue_arg if tissue_arg != "auto" else None
    if tissue is None and final.get("tissue_top1"):
        tissue, note = s0_check.map_tissue_to_dict(final["tissue_top1"])
        meta["tissue_map_note"] = note
    if final["abstain"]:
        lines = ["# REPORT_ABSTAIN — S0 sample pre-check abstention record (shadow: run not blocked)", "",
                 f"- Input: `{input_path}`",
                 f"- Time: {time.strftime('%F %T')}",
                 f"- Species call: `{final['species_call']}`; tissue top1: `{final['tissue_top1']}`",
                 f"- Gate reasons (any hit records an abstention): {'; '.join(final['gate_reasons'])}",
                 f"- Mode: shadow (default for this batch). " +
                 ("continued with human-supplied parameters" if (species and tissue) else
                  "cannot continue: species/tissue unresolvable (exit on missing args, not a hard-gate block)"),
                 "- Adjudication channel for label changes: the three independent reviewer votes and the existing hard gates; this record changes no labels."
                 " Under Phase 3 (later acceptance stage), with EYEKB_S0_ENFORCE=1 this abstention would block.",
                 "- Full readings: `s0_gate_report.json` (same directory)."]
        (out / "REPORT_ABSTAIN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        meta["abstain"] = True
        meta["continued"] = bool(species and tissue)
        _dump()
        if _s0_enforce():
            return False, None, None, meta
        if not (species and tissue):
            return False, None, None, meta
    # audit trail for divergence between manual override and the S0 call
    if species_arg != "auto" and final["species_call"] not in ("undetermined", "conflicted", "out_of_domain") \
            and final["species_call"] != species_arg:
        meta["s0_conflict_manual_vs_auto"] = {"s0": final["species_call"], "manual": species_arg}
    meta["backfill"] = {"species": species, "tissue": tissue}
    _dump()
    return True, species, tissue, meta


def _candidates_of(rep_cluster):
    qm = rep_cluster.get("kb_marker") or {}
    cands = [x.get("cell_type", "") for x in demote_kb9(qm.get("celltype_ranking") or [])][:3]  # [KB9B t_3bbc769f] narrow guard, slice depth unchanged
    cands += [x.get("cell_type", "") for x in demote_kb9(qm.get("unranked_candidates") or [])][:3]  # [KB9B t_3bbc769f]
    return [c for c in cands if c]


def inject_shadow(out, species, tissue, meta):
    """Human-side shadow injection: md-header attention block + two decisions flag columns + machine-readable/audit artifacts.
    Evidence JSON untouched (feed-face firewall); no auto-relabel column is ever written."""
    sys.path.insert(0, str(HERE / "pitfalls"))
    import consume
    lines, machine, claims, dangling = consume.attention_section(species, tissue, {
        "source": "s0" if meta and not meta.get("s0_overridden_by_user") else "manual",
        "overridden_by_user": bool(meta and meta.get("s0_overridden_by_user"))})
    rep_path = out / "annotation_evidence_report.json"
    dec_path = out / "decisions_template.csv"
    per_cluster_audit = []
    if rep_path.exists():
        import csv
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
        run_id = f"{species}__{tissue}__{time.strftime('%Y%m%dT%H%M%S')}"
        by_cluster = {}
        for c in rep.get("clusters") or []:
            flags, rows = consume.cluster_flags(claims, _candidates_of(c))
            by_cluster[str(c["cluster"])] = flags
            for r in rows:
                per_cluster_audit.append({"cluster_id": str(c["cluster"]), **r})
        consume.write_outputs(out, species, tissue, claims, per_cluster_audit, run_id, dangling)
        if dec_path.exists():
            rows = list(csv.reader(open(dec_path, encoding="utf-8")))
            if rows:
                rows[0] += ["pitfall_risk_flags", "pitfall_review_required"]
                cid_i = rows[0].index("cluster_id")
                for r in rows[1:]:
                    fl = by_cluster.get(str(r[cid_i]), [])
                    r += [";".join(fl), "yes" if fl else "no"]
                import io
                buf = io.StringIO()
                csv.writer(buf, lineterminator="\n").writerows(rows)
                dec_path.write_text(buf.getvalue(), encoding="utf-8")
    md_path = out / "annotation_evidence_report.md"
    if md_path.exists():
        txt = md_path.read_text(encoding="utf-8")
        idx = txt.find("## Cluster ")
        block = "\n".join(lines) + "\n"
        txt = (txt[:idx] + block + txt[idx:]) if idx >= 0 else (txt + "\n" + block)
        md_path.write_text(txt, encoding="utf-8")
    return {"n_claims_applicable": len(claims), "n_flag_rows": len(per_cluster_audit),
            "dangling_pointers": len(dangling)}


def main():
    ap = argparse.ArgumentParser(
        description="EyeKB batch-annotation evidence entry point (Stage S0(shadow)+A+B; zero LLM by default)")
    ap.add_argument("--input", required=True,
                    help="10X triplet directory / parent directory containing multiple triplet subdirs / .h5ad")
    ap.add_argument("--species", default="auto", choices=["human", "mouse", "auto"],
                    help="default auto (S0-decided backfill); an explicit value = S0 override, recorded (mandatory in rollback state)")
    ap.add_argument("--tissue", default="auto",
                    help="known tissue dictionary name (see --list-tissues) or auto (S0-decided backfill)")
    ap.add_argument("--out", required=True, help="output directory (created if absent)")
    ap.add_argument("--sample-col", default="", help="h5ad sample column (defaults to obs.sample / input name)")
    ap.add_argument("--sample-group", default="", dest="group_col",
                    help="grouping: h5ad column name, or for triplet inputs a 'sample=group;...' mapping"
                         " (disease-prior comparison is enabled only when grouping is provided)")
    ap.add_argument("--group-col", default="", dest="group_col",
                    help="alias of --sample-group")
    ap.add_argument("--disease", default="", help="disease name (used with grouping; by default queries the labels of non-control groups)")
    ap.add_argument("--gene-symbol-col", default="")
    ap.add_argument("--ensg-map", default="", help="ENSG<TAB>SYMBOL two-column TSV")
    ap.add_argument("--resolution", type=float, default=1.0)
    ap.add_argument("--min-genes", type=int, default=200)
    ap.add_argument("--max-pct-mt", type=float, default=20.0)
    ap.add_argument("--top-genes-n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260929)
    ap.add_argument("--no-scrublet", action="store_true")
    ap.add_argument("--no-harmony", action="store_true")
    ap.add_argument("--s0-thr", default=None, dest="s0_thr",
                    help="S0 threshold-override JSON (for sensitivity sweeps; hardcoded thresholds by default)")
    ap.add_argument("--list-tissues", action="store_true", help="print the known tissue dictionary and exit")
    ap.add_argument("--llm-assist", action="store_true",
                    help="optional switch: call a user-supplied channel to generate evidence-summary drafts (off by default; does not affect grading)")
    a = ap.parse_args()

    if a.list_tissues:
        print("\n".join(known_tissues()))
        return 0

    gate = _s0_enabled()
    out = Path(a.out)
    meta = None
    if not gate:
        # rollback state (air-gapped baseline comparison / emergency): legacy semantics byte-equivalent to pre-wiring — human parameters mandatory
        if a.species == "auto" or a.tissue == "auto":
            print("[run_pipeline] EYEKB_S0_GATE=0 (rollback state) requires explicit "
                  "--species and --tissue (legacy mandatory-argument semantics).", file=sys.stderr)
            return 2
        species, tissue = a.species, a.tissue
    else:
        ok, species, tissue, meta = run_s0_gate(a.input, a.sample_col,
                                                a.species, a.tissue, out, a.s0_thr)
        if not ok:
            if _s0_enforce() and meta["final"]["abstain"]:
                print("[run_pipeline] S0 hard gate (enforce mode, Phase-3 forward switch) abstained: "
                      f"pipeline stopped. See {out/'REPORT_ABSTAIN.md'}", file=sys.stderr)
                return 3
            print("[run_pipeline] S0 abstained and species/tissue unresolvable (human parameters missing): "
                  "exit on missing arguments (not a hard-gate block). Supply --species/--tissue explicitly, "
                  f"or see {out/'REPORT_ABSTAIN.md'}", file=sys.stderr)
            return 4
        mode = meta.get("mode", "shadow")
        extra = " (abstained, shadow continued)" if meta.get("abstain") else ""
        print(f"[run_pipeline] S0 call: species={species} tissue={tissue}"
              f" (confidence={meta['final']['confidence']}, mode={mode}{extra}"
              f"{ ', manual override recorded' if meta['s0_overridden_by_user'] else ''})",
              flush=True)

    kt = known_tissues()
    if tissue.lower() not in {t.lower() for t in kt}:
        print(f"[warn] --tissue={tissue!r} is not in the known tissue dictionary (execution continues; "
              f"the composition comparison may return no matching entries and records that faithfully in the report). "
              f"List: {', '.join(kt)}",
              file=sys.stderr)

    (out / "stage_a").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    from stage_a_processing import run_stage_a
    from stage_b_evidence import run_stage_b

    sa = run_stage_a(a.input, out / "stage_a", species, sample_col=a.sample_col,
                     group_col=a.group_col, gene_symbol_col=a.gene_symbol_col,
                     ensg_map=a.ensg_map, min_genes=a.min_genes,
                     max_pct_mt=a.max_pct_mt, resolution=a.resolution,
                     expected_doublet_rate=0.06, seed=a.seed,
                     no_scrublet=a.no_scrublet, no_harmony=a.no_harmony)
    rep = run_stage_b(out / "stage_a" / "processed.h5ad",
                      out / "stage_a" / "cluster_markers.csv",
                      out / "stage_a" / "cluster_sizes.csv",
                      out, species, tissue, disease=a.disease,
                      group_col="group" if sa["group_present"] else "",
                      gene_degraded=bool(sa["gene_id"].get("degraded")),
                      top_genes_n=a.top_genes_n, llm_assist=a.llm_assist)
    att_stats = inject_shadow(out, species, tissue, meta) if gate else None
    grades = {}
    for c in rep["clusters"]:
        grades[c["confidence"]] = grades.get(c["confidence"], 0) + 1
    summary = {"out": str(out), "secs": round(time.time() - t0, 1),
               "n_clusters": len(rep["clusters"]), "grades": grades,
               "empty_decision_cells": True,
               "next_step": "fill decisions_template.csv per cluster with decision "
                            "(accept|modify|abstain) and proposed_label; abstention is legal"}
    if gate:
        summary["s0"] = {"species": species, "tissue": tissue,
                         "confidence": meta["final"]["confidence"],
                         "abstain": bool(meta.get("abstain", meta["final"]["abstain"])),
                         "mode": meta.get("mode", "shadow"),
                         "overridden_by_user": meta["s0_overridden_by_user"]}
        summary["pitfalls_shadow"] = att_stats
    (out / "run_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print("[pipeline] DONE", json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
