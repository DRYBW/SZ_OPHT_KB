#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_05_evalbasis.py — ITEM 4: the evaluation-basis flag, measured panel by panel.

The finding to deliver
    75 genes were refused by the marker layer because their only basis is an evaluation volume,
    and markers_v12_holefill_increment.json was refused outright because its own scope says it
    fills the measured coverage holes of the 28-volume / 721-cluster run — its candidate list is
    the benchmark's own output. That refusal is correct (contract red line: never derive a marker
    or a lineage edge from the evaluation volumes' own queries). The question this card has to
    answer is the next one: which shipped panels carry such genes, how many each, and what a
    flag would have to assert to make the distinction machine-checkable without rewriting a
    panel body.

Three readings, because "basis" is not one thing
    A  panel_basis_eval_only_and_no_independent_evidence   the gene's entry carries only
       evaluation-volume provenance and the corpus holds nothing admissible for it -> refused
    B  panel_basis_eval_only_with_an_independent_anchor    the gene's entry carries only
       evaluation-volume provenance, but an independent corpus row exists -> admitted, while the
       panel's *selection* of that gene still leaned on the benchmark
    C  panel_basis_independent                            the entry names a non-evaluation basis

Nothing is activated, no panel body is touched, and the marker layer's own loader and evaluation
vocabulary are reused rather than re-implemented.

Outputs: out/ITEM4_EVAL_BASIS_BY_PANEL.tsv, out/ITEM4_EVAL_BASIS_BY_GENE.tsv,
         out/ITEM4_NONBENCHMARK_FLAG_SPEC.md, out/ITEM4_SUMMARY.json
Usage  : python3 scripts/w5_05_evalbasis.py
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402


def main() -> int:
    M = C.markers_common()
    panels = M.load_panels()
    refusals = C.read_tsv(os.path.join(C.MK_OUT, "NODE_GENE_REFUSALS.tsv"))
    gap = C.read_tsv(os.path.join(C.MK_OUT, "GAP_REGISTER.tsv"))
    # the dev panels declare their own two tracks (D = the dev-exam substrate's data track, L =
    # literature) in a file beside the panel; the marker layer's admission test reads that file,
    # so this measurement reads the same one rather than guessing from the JSON provenance keys.
    dev_core, _dev_markers = M.load_dev_core_evidence()

    refused_eval = collections.defaultdict(set)      # library -> {gene}
    refused_species = collections.defaultdict(set)
    for r in refusals:
        if r["reason"] == "evidence_only_from_evaluation_volume":
            refused_eval[r["library"]].add(r["gene"])
        elif r["reason"] == "different_species_not_stitchable":
            refused_species[r["library"]].add(r["gene"])

    per_panel, per_gene = {}, []
    for lib, p in sorted(panels.items()):
        n_genes, a, b, cc = set(), set(), set(), set()
        dev_volume_eval = 0
        for label, rec in p["labels"].items():
            if rec.get("dev_volume") and M.is_eval_token(str(rec.get("dev_volume"))):
                dev_volume_eval += 1
            for g in rec["genes"]:
                n_genes.add(g)
                entries = list(rec.get("provenance", {}).get(g) or [])
                entries += list(rec.get("evidence", {}).get(g) or [])
                blobs = [json.dumps(e, ensure_ascii=False) for e in entries]
                eval_hit = any(M.is_eval_token(x) for x in blobs)
                non_eval = [x for x in blobs if not M.is_eval_token(x)]
                if lib in ("dev_v8", "dev_v9"):
                    tk = str(((dev_core.get(label) or {}).get(g) or {}).get("track") or "")
                    if "D" in tk and "L" not in tk:
                        kind = "panel_basis_eval_only"
                    elif "D" in tk and "L" in tk:
                        kind = "panel_basis_mixed"
                    elif tk:
                        kind = "panel_basis_independent"
                    else:
                        kind = "panel_basis_unstated"
                    basis_basis = "dev_panel_declared_track:" + (tk or "none")
                else:
                    if not blobs:
                        kind = "panel_basis_unstated"
                    elif eval_hit and not non_eval:
                        kind = "panel_basis_eval_only"
                    elif eval_hit and non_eval:
                        kind = "panel_basis_mixed"
                    else:
                        kind = "panel_basis_independent"
                    basis_basis = "panel_provenance_entries"
                row = {"library": lib, "panel_file": p["file"], "label": label, "gene": g,
                       "panel_basis_class": kind, "basis_read_from": basis_basis,
                       "n_provenance_entries": len(entries),
                       "in_corpus_gene_index": "",
                       "refused_reason": ("evidence_only_from_evaluation_volume"
                                          if g in refused_eval.get(lib, set()) else "")}
                per_gene.append(row)
                if kind == "panel_basis_eval_only":
                    if g in refused_eval.get(lib, set()):
                        a.add(g)
                    else:
                        b.add(g)
                else:
                    cc.add(g)
        per_panel[lib] = {
            "panel_file": p["file"], "path": p["path"], "n_labels": len(p["labels"]),
            "n_genes": len(n_genes),
            "declared_selection_basis": p["selection_basis"],
            "entries_carrying_an_evaluation_volume_as_dev_volume": dev_volume_eval,
            "A_refused_eval_only_no_independent_evidence": len(a),
            "B_admitted_but_panel_basis_eval_only": len(b),
            "C_panel_basis_independent_or_mixed": len(cc),
            "has_any_evaluation_basis_gene": "yes" if (a or b) else "no",
            "refused_genes_sample": sorted(a)[:6],
            "admitted_with_eval_only_panel_basis_sample": sorted(b)[:6],
        }

    # the corpus index is what decides whether an independent anchor exists, so it is read once
    gidx = {r["gene"]: r for r in C.read_tsv(os.path.join(C.MK_OUT, "CORPUS_GENE_INDEX_v1.tsv"))}
    for row in per_gene:
        g = row["gene"]
        row["in_corpus_gene_index"] = "yes" if g in gidx else "no"

    rows = sorted(per_panel.values(), key=lambda r: (-(r["A_refused_eval_only_no_independent_evidence"]
                                                      + r["B_admitted_but_panel_basis_eval_only"]),
                                                    r["panel_file"]))
    C.write_tsv(os.path.join(C.OUT, "ITEM4_EVAL_BASIS_BY_PANEL.tsv"), rows,
                ["panel_file", "path", "n_labels", "n_genes", "declared_selection_basis",
                 "entries_carrying_an_evaluation_volume_as_dev_volume",
                 "A_refused_eval_only_no_independent_evidence",
                 "B_admitted_but_panel_basis_eval_only",
                 "C_panel_basis_independent_or_mixed", "has_any_evaluation_basis_gene",
                 "refused_genes_sample", "admitted_with_eval_only_panel_basis_sample"])
    C.write_tsv(os.path.join(C.OUT, "ITEM4_EVAL_BASIS_BY_GENE.tsv"), per_gene,
                ["library", "panel_file", "label", "gene", "panel_basis_class",
                 "basis_read_from", "n_provenance_entries", "in_corpus_gene_index",
                 "refused_reason"])

    # markers_v12: the panel refused outright, and why its scope settles the question
    v12 = os.path.join(C.REPO_KB_MARKERS, "markers_v12_holefill_increment.json")
    v11 = os.path.join(C.REPO_KB_MARKERS, "markers_v11_lensiris_increment.json")
    def scope_of(path):
        if not os.path.isfile(path):
            return {"present": "no"}
        d = json.load(open(path, encoding="utf-8"))
        txt = " ".join(str(d.get(k) or "") for k in ("scope", "applicability", "provenance",
                                                     "selection_basis"))
        genes = set()
        for label, gs in (d.get("markers") or {}).items():
            if isinstance(gs, list):
                genes.update(str(g).upper() for g in gs)
        n_entries = len(d.get("entries") or [])
        for ent in (d.get("entries") or []):
            for g in (ent.get("markers") or []):
                genes.add(str(g).upper())
        return {"present": "yes", "n_entries": n_entries, "n_genes": len(genes),
                "scope_says_it_fills_the_evaluation_runs_own_holes":
                    "yes" if ("measured coverage holes" in txt or "721-cluster" in txt) else "no",
                "scope_excerpt": txt.strip()[:400]}
    v12_info, v11_info = scope_of(v12), scope_of(v11)

    # a non-benchmark flag has to be checkable. What it must assert, drawn from the measurements:
    spec = {
        "generated_by": "scripts/w5_05_evalbasis.py",
        "what_is_being_flagged": ("a gene, or an entry, whose basis for being in a shipped panel "
                                  "is an evaluation volume — i.e. the benchmark's own substrate — "
                                  "rather than independent literature or an in-house non-benchmark "
                                  "atlas"),
        "why_a_file_level_bit_is_not_enough": [
            "the same panel file mixes the three readings: measured per panel in "
            "ITEM4_EVAL_BASIS_BY_PANEL.tsv (columns A, B, C sum to the panel's gene count)",
            "a panel whose declared selection basis is an evaluation volume still carries genes "
            "whose own entry names an independent source (reading C), so flagging the file would "
            "condemn them",
            "a panel whose declared basis is independent can still carry an entry whose only "
            "provenance is an evaluation volume (reading B), so not flagging the file would "
            "exonerate them",
        ],
        "what_the_flag_must_assert": [
            "granularity: per entry (label) inside a panel file, and per gene inside that entry — "
            "not per file",
            "a basis class drawn from a closed vocabulary: independent_literature | "
            "independent_in_house_atlas_non_benchmark | evaluation_volume | evaluation_report_holes "
            "| unstated",
            "when the basis class is evaluation_volume or evaluation_report_holes: the entry must "
            "carry an independent anchor (a PMID or a corpus row) for every gene it wants to be "
            "usable for a lineage/marker claim, named per gene — the flag says 'this candidate "
            "list leaned on the benchmark', not 'this gene is unusable'",
            "the name of the evaluation artefact it leaned on (volume id / report id), so a reader "
            "can re-derive the exclusion list instead of trusting the bit",
            "an explicit statement of what the flag does NOT claim: it does not assert that the "
            "gene is wrong, and it does not authorise changing a shipped panel body",
        ],
        "where_it_must_be_enforced": ("at the consuming layer (the marker layer's admission test), "
                                      "not by editing the shipped panels: the contract's red line "
                                      "forbids deriving a marker from the evaluation volumes' own "
                                      "queries, and a rewrite of kb/ is an activation by another "
                                      "name"),
        "machine_check": ("for every assertion in a lineage artefact: if the source entry's basis "
                          "class is evaluation_volume or evaluation_report_holes, the assertion "
                          "must carry an anchor that is not derived from that volume; the marker "
                          "layer already implements exactly this for reading A (the four-condition "
                          "corpus test), and reading B is what is not yet checkable"),
        "status": "registered here; not activated, and no panel body is changed by this card",
    }
    md = ["# A non-benchmark flag: what it would have to assert",
          "",
          "Decision-ready finding from the lineage-hygiene wave (item 4). Nothing was activated and",
          "no panel body was changed.",
          "",
          "## Measured",
          ""]
    tot_a = sum(r["A_refused_eval_only_no_independent_evidence"] for r in rows)
    tot_b = sum(r["B_admitted_but_panel_basis_eval_only"] for r in rows)
    md.append("| panel | genes | A refused (no independent basis) | B admitted with "
              "evaluation-only panel basis | declared selection basis |")
    md.append("|---|---|---|---|---|")
    for r in rows:
        md.append("| %s | %d | %d | %d | %s |" % (r["panel_file"], r["n_genes"],
                                                   r["A_refused_eval_only_no_independent_evidence"],
                                                   r["B_admitted_but_panel_basis_eval_only"],
                                                   r["declared_selection_basis"]))
    md += ["", "Totals across the consumed panels: A = %d gene-panel rows, B = %d." % (tot_a, tot_b),
           "",
           "`markers_v12_holefill_increment.json` (present only in the git tree): %s entries / %d "
           "genes; its own scope names the measured coverage holes of the 28-volume / 721-cluster "
           "run — %s." % (v12_info.get("n_entries"), v12_info.get("n_genes", 0),
                          v12_info.get("scope_says_it_fills_the_evaluation_runs_own_holes")),
           "",
           "## Why a file-level bit is not enough", ""]
    md += ["- " + s for s in spec["why_a_file_level_bit_is_not_enough"]]
    md += ["", "## What the flag must assert", ""]
    md += ["- " + s for s in spec["what_the_flag_must_assert"]]
    md += ["", "## Where it must be enforced", "", "- " + spec["where_it_must_be_enforced"],
           "", "## Machine check", "", "- " + spec["machine_check"], ""]
    open(os.path.join(C.OUT, "ITEM4_NONBENCHMARK_FLAG_SPEC.md"), "w",
         encoding="utf-8").write("\n".join(md))

    summ = {
        "panels_consumed": len(rows),
        "totals": {
            "A_refused_eval_only_no_independent_evidence": tot_a,
            "B_admitted_but_panel_basis_eval_only": tot_b,
            "C_panel_basis_independent_or_mixed": sum(
                r["C_panel_basis_independent_or_mixed"] for r in rows),
        },
        "panels_with_any_evaluation_basis_gene": [r["panel_file"] for r in rows
                                                  if r["has_any_evaluation_basis_gene"] == "yes"],
        "panels_without": [r["panel_file"] for r in rows
                           if r["has_any_evaluation_basis_gene"] == "no"],
        "refused_panel": {"file": "markers_v12_holefill_increment.json", **v12_info},
        "lensiris_increment": {"file": "markers_v11_lensiris_increment.json", **v11_info},
        "gap_register_rows_with_this_reason": sum(
            1 for r in gap if r["reason"] == "evidence_only_from_evaluation_volume"),
        "flag_spec": spec,
        "activation": "none",
        "panel_bodies_changed": 0,
    }
    C.write_json(os.path.join(C.OUT, "ITEM4_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())