#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB pipeline — Stage B: per-cluster five-tool evidence collection (MCP stdio, spawning the in-repo mcp_server).

This file is a copied-and-adapted version of /mnt/D/EyeKB/plans/evalset/scripts/kb2_mcp_v2.py (the original is frozen, untouched).
Decoupled: no longer bound to the evalset frozen volume / no longer reads an external ENSG mapping / no longer hardcodes tissue mappings;
it now consumes Stage A outputs (processed.h5ad + cluster_markers.csv).

═══ Discipline redlines (identical to the server-side redlines, do not change) ═══
1. The default path is **zero LLM** — the five query tools do local mechanical retrieval,
   emitting evidence only, never conclusions.
2. This script contains no automatic scoring/auto-naming logic. The "confidence grade" below
   is a pre-registered mechanical QC flag (trigger conditions written item-by-item into the
   report, auditable), not an annotation conclusion; needs_review / abstention is a legal
   output — never write needs_review as a definite label.
3. The decision/proposed_label columns of decisions_template.csv are always left empty for the
   researcher to adjudicate (the three values accept / modify / abstain are filled by a human).
4. Server-side B5 cross-species governance clears named rankings for mouse-origin input
   (no_named_ranking_for); this script passes it through verbatim — no bypassing, no backfilling ranks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER = REPO_ROOT / "mcp_server" / "server.py"
from kb9_consume_guard import demote_kb9  # [KB9B t_3bbc769f] consumer-side narrow guard (env EYEKB_KB9_CONSUME_GUARD)

CONTROLISH = {"control", "ctrl", "normal", "untrig", "unpaired", "vehicle",
              "rrd_control", "non_dm", "nondisease", "healthy"}


def _log(logf, step, **kw):
    rec = {"ts": time.strftime("%F %T"), "step": step, **kw}
    with open(logf, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    print(f"[stageB] {step}: " + " ".join(f"{k}={v}" for k, v in kw.items()), flush=True)


def parse_mcp(res):
    """MCP CallToolResult -> dict (same method as kb2_mcp_v2)."""
    if res.is_error:
        return {"__isError__": True, "text": [c.text for c in res.content]}
    sc_ = getattr(res, "structured_content", None)
    if isinstance(sc_, dict):
        return sc_.get("result", sc_) if set(sc_.keys()) == {"result"} else sc_
    texts = [c.text for c in res.content if getattr(c, "type", "") == "text"]
    return json.loads(texts[0]) if texts else None


# ---------------------------------------------------------------- mechanical QC flags
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _find_baseline_row(rows, cand):
    """Mechanical match between a candidate class name and a baseline row class/label (normalized equality, or containment with length>=4)."""
    nc = _norm(cand)
    if len(nc) < 2:
        return None
    for r in rows:
        for key in ("class", "label_cn"):
            nr = _norm(r.get(key, ""))
            if nr == nc or (len(nc) >= 4 and nc in nr):
                return r
    return None


def composition_flag(rows, candidate, fraction_pct):
    """Cluster fraction (% of cells) versus the donor-level baseline interval — flags only, never scores."""
    if not candidate:
        return {"flag": "no_candidate", "note": "query_marker produced no named candidate; no comparison"}
    row = _find_baseline_row(rows, candidate)
    if row is None:
        return {"flag": "no_baseline_row",
                "note": f"candidate {candidate!r} has no matching row in this tissue's composition baseline; no comparison"}
    lo_hi = row.get("donor_range_pct")
    iqr = row.get("donor_iqr_pct")
    out = {"flag": "", "candidate": candidate, "baseline_class": row.get("class"),
           "observed_pct": round(fraction_pct, 3),
           "donor_median_pct": row.get("donor_median_pct"),
           "donor_iqr_pct": iqr, "donor_range_pct": lo_hi,
           "provenance": [s.get("label") or s.get("pmid") or s.get("sid", "")
                          for s in (row.get("sources_resolved") or [])][:6]}
    if not lo_hi:
        out["flag"] = "range_not_estimated"
        out["note"] = "baseline row provides no donor-level interval (skeleton entry / too few samples); no out-of-range verdict"
    elif fraction_pct < lo_hi[0] or fraction_pct > lo_hi[1]:
        out["flag"] = "outside_range"
    elif iqr and not (iqr[0] <= fraction_pct <= iqr[1]):
        out["flag"] = "within_range_outside_iqr"
    else:
        out["flag"] = "within_iqr"
    return out


def prior_hits_for_cluster(dp, candidates):
    """Mechanical mentions of the candidate classes in the disease prior's expected_cell_state_matrix (evidence excerpts, not a consistency score)."""
    if not dp or dp.get("error") or dp.get("__isError__"):
        return []
    hits = []
    for row in dp.get("expected_cell_state_matrix") or []:
        for exp in row.get("expected") or []:
            low = str(exp).lower()
            for cand in candidates:
                if cand and len(cand) >= 3 and cand.lower() in low:
                    hits.append({"cell_type": cand, "tissue": row.get("tissue"),
                                 "expected_line": str(exp)[:220],
                                 "evidence_grade": row.get("evidence")})
                    break
    return hits[:8]


def grade_cluster(kb_marker, comp, lit, group_present, gene_degraded):
    """Pre-registered mechanical grading rules (order = priority; fired reasons are written into the report, auditable).
    Outputs one of three values: evidence_consistent | mixed_or_insufficient | needs_review
    — these are review-order hint flags, not annotation conclusions, and feed into no scoring."""
    ranking = (kb_marker or {}).get("celltype_ranking") or []
    unranked = (kb_marker or {}).get("unranked_candidates") or []
    no_named = (kb_marker or {}).get("no_named_ranking_for")
    if isinstance(lit, dict) and lit.get("per_celltype"):
        n_lit = sum(len((v or {}).get("results") or []) for v in lit["per_celltype"].values())
        degraded = any(bool((v or {}).get("degraded")) for v in lit["per_celltype"].values())
    else:
        n_lit = len((lit or {}).get("results") or [])
        degraded = bool((lit or {}).get("degraded"))
    rules = []
    if gene_degraded:
        rules.append("gene_ids_unmapped: input gene IDs are not mapped to symbols; marker comparison unreliable")
    if no_named:
        rules.append(f"named_ranking_removed_by_server: {no_named} (server-side cross-species governance; named ranking unavailable)")
    if not ranking:
        rules.append("no_named_marker_candidates")
    if n_lit == 0:
        rules.append("no_literature_results")
    if rules or (not unranked and not ranking):
        return "needs_review", (rules or ["no_evidence"])
    reasons = list(rules)
    top1 = ranking[0]
    if top1.get("n_shared", 0) <= 1:
        reasons.append("weak_marker_match: top1 shared-gene count <=1")
    if len(ranking) > 1 and ranking[1].get("n_shared") == top1.get("n_shared"):
        reasons.append("candidate_tie: top1/top2 tied on shared-gene count")
    if comp.get("flag") == "outside_range":
        reasons.append("composition_outside_baseline_range")
    if degraded:
        reasons.append("literature_degraded: retrieval degraded (embedding model/corpus unavailable); snippets are for reference only")
    if reasons:
        return "mixed_or_insufficient", reasons
    return "evidence_consistent", ["marker_candidate+within_baseline+literature_present"]


# ---------------------------------------------------------------- main flow
def run_stage_b(processed_h5ad, markers_csv, sizes_csv, out_dir, species, tissue,
                disease="", group_col="group", gene_degraded=False, top_genes_n=10,
                llm_assist=False, logf=None):
    import anyio
    import pandas as pd
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    logf = logf or (out / "stage_b_log.jsonl")

    mk = pd.read_csv(markers_csv)
    sizes = pd.read_csv(sizes_csv)
    total_cells = int(sizes["n_cells"].sum())
    clusters = [str(c) for c in sizes["cluster"].astype(str)]

    try:  # group labels (for the disease-prior enable check + per-cluster group-fraction evidence)
        import anndata as ad
        a = ad.read_h5ad(processed_h5ad, backed="r")
        gcol = None
        if group_col and group_col in a.obs.columns:
            gcol = group_col
        elif "group" in a.obs.columns:
            gcol = "group"
        obs = None
        if gcol:
            obs = a.obs[["sample", gcol]].copy()
            obs["cluster"] = a.obs["leiden"].astype(str)
        del a
    except Exception as e:  # a failed read does not affect the evidence main flow; record it faithfully
        _log(logf, "warn", note=f"failed to read the group column: {e!r}")
        obs = None
    group_present = bool(obs is not None and obs[gcol].nunique() >= 2)

    calls = []
    dp_cache = {}  # run-level disease-prior cache (filled inside the closure, read by the report section)

    async def collect():
        params = StdioServerParameters(command=sys.executable, args=[str(SERVER)], env=None)
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()

                async def call(tool, args):
                    t0 = time.time()
                    res = parse_mcp(await s.call_tool(tool, args))
                    ok = not (isinstance(res, dict) and res.get("__isError__"))
                    calls.append({"tool": tool, "args": {k: (str(v)[:120] if isinstance(v, list) else v)
                                                        for k, v in args.items()},
                                  "secs": round(time.time() - t0, 2), "ok": ok})
                    return res

                # tissue baseline and disease priors are both run-level caches (queried once per argument set)
                tc = await call("get_tissue_composition", {"species": species, "tissue": tissue})
                rows = (tc or {}).get("rows") or []
                dp_cache.clear()
                if group_present:
                    labels = [str(x) for x in sorted(obs[gcol].unique())]
                    want = [disease] if disease else \
                        [l for l in labels if _norm(l) not in {_norm(x) for x in CONTROLISH}] \
                        or labels
                    for lab in dict.fromkeys(want):
                        dp_cache[lab] = await call("get_disease_prior",
                                                  {"disease": lab, "tissue": tissue})
                per_cluster = []
                for i, cl in enumerate(clusters, 1):
                    sub = mk[mk["cluster"].astype(str) == cl].sort_values("rank")
                    top = [str(g) for g in sub["gene"].head(top_genes_n)]
                    frac_pct = 100.0 * int(sizes.loc[sizes["cluster"].astype(str) == cl, "n_cells"].iloc[0]) \
                        / max(total_cells, 1)
                    qm = await call("query_marker", {"genes": top}) if top else None
                    cands = [x.get("cell_type") for x in demote_kb9((qm or {}).get("celltype_ranking") or [])][:3]  # [KB9B t_3bbc769f]
                    cands_unranked = [x.get("cell_type") for x in demote_kb9((qm or {}).get("unranked_candidates") or [])][:3]  # [KB9B t_3bbc769f]
                    comp = composition_flag(rows, cands[0] if cands else None, frac_pct)
                    lit = {"per_celltype": {}}
                    query_cands = cands or cands_unranked
                    if query_cands:
                        for ct in query_cands:
                            lit["per_celltype"][ct] = await call(
                                "search_literature",
                                {"cell_type": ct, "species": species, "tissue": tissue, "top_k": 4})
                    else:  # no candidates: use the top genes for a lexical query — still evidence, no conclusion
                        lit["gene_query"] = await call(
                            "search_literature",
                            {"cell_type": "", "species": species, "tissue": tissue,
                             "query": " ".join(top[:6]) + f" {tissue}", "top_k": 4})
                    dp_hits = {}
                    if group_present:
                        for lab, dp in dp_cache.items():
                            dp_hits[lab] = {
                                "entry_id": (dp or {}).get("entry_id") or (dp or {}).get("error"),
                                "mentions": prior_hits_for_cluster(dp, query_cands)}
                    gf = {}
                    if group_present and obs is not None:
                        cm = obs[obs["cluster"] == cl]
                        n = max(len(cm), 1)
                        gf = {str(k): round(100.0 * v / n, 2)
                              for k, v in cm[gcol].value_counts().items()}
                    grade, reasons = grade_cluster(qm, comp, lit, group_present, gene_degraded)
                    per_cluster.append({
                        "cluster": cl,
                        "n_cells": int(sizes.loc[sizes["cluster"].astype(str) == cl, "n_cells"].iloc[0]),
                        "fraction_pct": round(frac_pct, 3),
                        "top_genes": top,
                        "kb_marker": qm,
                        "tissue_composition": {"observed_vs_baseline": comp,
                                               "baseline_entry_id": (tc or {}).get("entry_id"),
                                               "baseline_tissue": (tc or {}).get("tissue"),
                                               "usage_redline": (tc or {}).get("usage_redline")},
                        "disease_prior": ({"group_fractions_pct": gf, "per_disease": dp_hits}
                                          if group_present else
                                          {"enabled": False,
                                           "reason": "no grouping column provided or only one group (--group-col); disease-prior comparison not enabled"}),
                        "literature": _trim_lit(lit),
                        "confidence": grade,
                        "confidence_rules_fired": reasons,
                    })
                    if i % 5 == 0:
                        print(f"[stageB] progress {i}/{len(clusters)} clusters", flush=True)
                return tc, per_cluster

    tc, per_cluster = anyio.run(collect)

    # optional LLM assist (off by default; writes evidence-summary narratives only, never changes grades or assigns labels)
    llm_meta = {"enabled": False, "note": "zero LLM by default; enabled only with --llm-assist, and a user-supplied channel is required"}
    if llm_assist:
        from llm_assist import assist  # noqa: E402
        llm_meta = assist(per_cluster, out)

    report = {
        "schema": "eyekb-pipeline-evidence-v1",
        "generated_at": time.strftime("%F %T"),
        "inputs": {"processed_h5ad": str(processed_h5ad), "species": species,
                   "tissue": tissue, "group_col_enabled": group_present,
                   "disease_queried": list(dp_cache.keys()) if group_present else [],
                   "top_genes_n": top_genes_n},
        "redlines": [
            "zero LLM on the default path; this file is produced by local five-tool mechanical retrieval",
            "the confidence grade is a pre-registered mechanical QC flag (rule triggers individually auditable), not an annotation conclusion",
            "abstention (needs_review) / review (mixed_or_insufficient) are legal outputs; never treat a QC flag as a definite label",
            "all evidence (marker hits / baseline intervals / disease-prior mentions / literature snippets) carries provenance for human adjudication",
        ],
        "baseline_entry": {"entry_id": (tc or {}).get("entry_id"),
                           "tissue": (tc or {}).get("tissue"),
                           "frozen_date": (tc or {}).get("frozen_date"),
                           "error": (tc or {}).get("error")},
        "llm_assist": llm_meta,
        "mcp_calls": {"total": len(calls),
                      "errors": sum(1 for c in calls if not c["ok"])},
        "clusters": per_cluster,
    }
    (out / "annotation_evidence_report.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "annotation_evidence_report.md").write_text(
        render_md(report), encoding="utf-8")

    dec = out / "decisions_template.csv"
    with open(dec, "w", encoding="utf-8") as f:
        f.write("cluster_id,n_cells,fraction_pct,top_candidates,composition_flag,"
                "confidence_grade,decision,proposed_label,notes\n")
        for c in per_cluster:
            qm = c["kb_marker"] or {}
            tops = ";".join(x.get("cell_type", "")
                            for x in demote_kb9(qm.get("celltype_ranking") or [])[:3]) or "ABSTAIN(no candidate)"  # [KB9B t_3bbc769f]
            f.write(f'{c["cluster"]},{c["n_cells"]},{c["fraction_pct"]},"{tops}",'
                    f'{c["tissue_composition"]["observed_vs_baseline"].get("flag","")},'
                    f'{c["confidence"]},,,\n')
    (out / "mcp_calls.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False, default=str) for c in calls) + "\n",
        encoding="utf-8")
    sha = hashlib.sha256((out / "annotation_evidence_report.json").read_bytes()).hexdigest()
    _log(logf, "done", clusters=len(per_cluster), report_sha=sha[:16],
         grades={g: sum(1 for c in per_cluster if c["confidence"] == g)
                 for g in ("evidence_consistent", "mixed_or_insufficient", "needs_review")},
         calls=len(calls))
    return report


def _trim_lit(lit):
    """Slim down literature snippets: keep the top3 results per candidate and truncate snippets to 300 characters (evidence-report readability)."""
    out = {}
    for k, v in (lit or {}).items():
        if k == "per_celltype":
            out[k] = {}
            for ct, resp in v.items():
                r = dict(resp or {})
                rs = []
                for h in (r.get("results") or [])[:3]:
                    h2 = dict(h)
                    h2["snippet"] = str(h2.get("snippet", ""))[:300]
                    rs.append(h2)
                r["results"] = rs
                out[k][ct] = r
        else:
            r = dict(v or {})
            rs = []
            for h in (r.get("results") or [])[:3]:
                h2 = dict(h)
                h2["snippet"] = str(h2.get("snippet", ""))[:300]
                rs.append(h2)
            r["results"] = rs
            out[k] = r
    return out


def render_md(rep):
    L = ["# Annotation Evidence Report (EyeKB pipeline Stage B output)", "",
         f"- Generated at: {rep['generated_at']}",
         f"- Input: `{rep['inputs']['processed_h5ad']}` (species {rep['inputs']['species']}, "
         f"tissue {rep['inputs']['tissue']}, disease prior "
         f"{'enabled' if rep['inputs']['group_col_enabled'] else 'not enabled (no grouping)'})",
         f"- MCP calls: {rep['mcp_calls']['total']} total, {rep['mcp_calls']['errors']} errors",
         "- **How to read**: this report presents evidence and mechanical QC flags only, with no annotation conclusions; "
         "the final naming of each cluster is filled in by the researcher in decisions_template.csv as accept / modify / abstain. "
         "Abstention is a legal output.", ""]
    for r in rep["redlines"]:
        L.append(f"- Redline: {r}")
    L.append("")
    for c in rep["clusters"]:
        qm = c["kb_marker"] or {}
        cr = demote_kb9(qm.get("celltype_ranking") or [])  # [KB9B t_3bbc769f] display slice only; raw resp in report json untouched
        ur = demote_kb9(qm.get("unranked_candidates") or [])  # [KB9B t_3bbc769f]
        comp = c["tissue_composition"]["observed_vs_baseline"]
        L += [f"## Cluster {c['cluster']} ({c['n_cells']} cells, {c['fraction_pct']}%)",
              f"- Confidence grade (mechanical QC flag): **{c['confidence']}**",
              f"  - Rules fired: {', '.join(c['confidence_rules_fired'])}",
              f"- top genes: {', '.join(c['top_genes'])}",
              "- query_marker candidates: " + (
                  "; ".join(f"{x['cell_type']} (n_shared={x['n_shared']}, "
                            f"{','.join(x.get('shared_genes', [])[:4])})" for x in cr[:3])
                  or ("no named candidates" + (f" (unranked: {', '.join(x['cell_type'] for x in ur[:3])}; "
                                               f"{qm.get('no_named_ranking_for', '')})" if ur else ""))),
              f"- Composition check (baseline row {c['tissue_composition'].get('baseline_entry_id')}): "
              f"flag={comp.get('flag')}" + (
                  f"; observed {comp.get('observed_pct')}% vs donor median {comp.get('donor_median_pct')}%"
                  f" (IQR {comp.get('donor_iqr_pct')}, range {comp.get('donor_range_pct')})"
                  if comp.get("observed_pct") is not None and comp.get("flag") not in
                  ("no_candidate", "no_baseline_row") else ""),
              "- Disease prior: " + (
                  "; ".join(f"{k}: {v.get('entry_id')} — {len(v.get('mentions') or [])} mention(s)"
                            for k, v in (c["disease_prior"].get("per_disease") or {}).items())
                  if c["disease_prior"].get("per_disease") else str(c["disease_prior"].get("reason"))),
              "- Literature snippets (top3, each with a PMID):"]
        lit = c["literature"] or {}
        anyres = False
        for ct, resp in (lit.get("per_celltype") or {}).items():
            for h in (resp.get("results") or [])[:2]:
                anyres = True
                L.append(f"  - [{ct}] PMID {h.get('pmid')} ({h.get('journal')} {h.get('year')}): "
                         f"{str(h.get('snippet'))[:140]}…")
        for k, resp in lit.items():
            if k == "per_celltype":
                continue
            for h in (resp.get("results") or [])[:2]:
                anyres = True
                L.append(f"  - [gene_query] PMID {h.get('pmid')} ({h.get('journal')} "
                         f"{h.get('year')}): {str(h.get('snippet'))[:140]}…")
        if not anyres:
            L.append("  - (no retrieval results — handled via the abstention path)")
        if c["disease_prior"].get("group_fractions_pct"):
            L.append(f"- Group composition (% of cells): {c['disease_prior']['group_fractions_pct']}")
        L.append("")
    L.append("---\n*This report was generated by the in-repo `pipeline/` of EyeKB; service redline: "
             "evidence feeds human review and QC flags only — never wire it into any scoring/weighting/ranking.*")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="EyeKB pipeline Stage B (per-cluster five-tool evidence collection, zero LLM by default)")
    ap.add_argument("--processed", required=True, help="Stage A's processed.h5ad")
    ap.add_argument("--markers", required=True, help="Stage A's cluster_markers.csv")
    ap.add_argument("--sizes", required=True, help="Stage A's cluster_sizes.csv")
    ap.add_argument("--out", required=True)
    ap.add_argument("--species", required=True, choices=["human", "mouse"])
    ap.add_argument("--tissue", required=True, help="known tissue dictionary name (e.g. retina / fibrovascular_membrane / ocular_surface …)")
    ap.add_argument("--disease", default="", help="disease name (if omitted, group labels are used to query disease entries)")
    ap.add_argument("--group-col", default="group")
    ap.add_argument("--top-genes-n", type=int, default=10)
    ap.add_argument("--gene-degraded", action="store_true",
                    help="set when Stage A reports gene IDs unmapped to symbols (affects grading)")
    ap.add_argument("--llm-assist", action="store_true",
                    help="optional: call a user-supplied OpenAI-compatible channel to generate evidence summaries (off by default; does not affect grading)")
    a = ap.parse_args()
    run_stage_b(a.processed, a.markers, a.sizes, a.out, a.species, a.tissue,
                disease=a.disease, group_col=a.group_col,
                gene_degraded=a.gene_degraded, top_genes_n=a.top_genes_n,
                llm_assist=a.llm_assist)


if __name__ == "__main__":
    main()
