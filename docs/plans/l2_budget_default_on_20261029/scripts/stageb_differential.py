#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Criteria C4 and C5a/C5b/C5c of this card (as amended by AMENDMENT_2).

Reads five Stage B runs of the G4 fixture volume (11 clusters), all produced on 2026-10-29
with the same inputs and the pinned pipeline interpreter:

  old        pre-change module, variable unset, no judge        -> budget 10
  off        first implementation (whole-pipeline default), env=0 -> budget 10
  def30      first implementation, variable unset               -> budget 30  (C5 refutation)
  plain      final module, variable unset, no judge             -> budget 10  (C5a)
  judge      final module, variable unset, --adjudicate         -> budget 30  (C5b)
  judgeoff   final module, env=0, --adjudicate                  -> budget 10  (C5c)

Compares the per-cluster candidate payload as canonical JSON and the normalized evidence
report (timestamp stripped by verify_pipeline's own normalizer, reused not re-implemented).

Usage: python3 docs/plans/l2_budget_default_on_20261029/scripts/stageb_differential.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(CARD, "..", "..", ".."))
RUNS = {
    "old": "/tmp/l2gate/old",
    "off": "/tmp/l2gate/off",
    "def30": "/tmp/l2gate/def",
    "plain": "/tmp/l2gate/v2_plain",
    "judge": "/tmp/l2gate/v2_judge",
    "judgeoff": "/tmp/l2gate/judge_off",
}
OUT = os.path.join(CARD, "out")
CAND_KEYS = ("candidates", "candidates_post_gate", "unranked_candidates", "celltype_ranking")

sys.path.insert(0, os.path.join(REPO, "tests"))
import verify_pipeline as V          # noqa: E402
from pathlib import Path             # noqa: E402


def canon(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def load(tag):
    root = RUNS[tag]
    d = json.load(open(os.path.join(root, "annotation_evidence_report.json")))
    clusters = {c.get("cluster"): c for c in d["clusters"]}
    return {
        "genes": {cid: len((c.get("top_genes") or [])) for cid, c in clusters.items()},
        "payload": {cid: {k: c.get(k) for k in CAND_KEYS} for cid, c in clusters.items()},
        "norm_report": V.norm_report_sha(Path(os.path.join(root, "annotation_evidence_report.md"))),
        "adjudication_present": any(c.get("adjudication") for c in clusters.values()),
        "generated_at": d.get("generated_at"),
    }


def compare(a, b):
    same = sorted(c for c in a["payload"] if canon(a["payload"][c]) == canon(b["payload"][c]))
    diff = sorted(c for c in a["payload"] if canon(a["payload"][c]) != canon(b["payload"][c]))
    return {"clusters": len(a["payload"]), "payload_identical": len(same),
            "payload_differing": diff,
            "normalized_report_identical": a["norm_report"] == b["norm_report"]}


def main():
    missing = [t for t, p in RUNS.items() if not os.path.isdir(p)]
    if missing:
        print("missing runs:", missing)
        return 1
    a = {t: load(t) for t in RUNS}
    doc = {"probe": "stageb_differential.py", "runs": RUNS,
           "generated_at": {t: a[t]["generated_at"] for t in RUNS},
           "top_genes_per_cluster": {t: a[t]["genes"] for t in RUNS},
           "normalized_report_sha": {t: a[t]["norm_report"] for t in RUNS},
           "adjudication_column_present": {t: a[t]["adjudication_present"] for t in RUNS}}

    doc["C4_rollback_vs_pre"] = compare(a["old"], a["off"])
    doc["C4_rollback_vs_pre"]["verdict"] = (
        "PASS" if (not doc["C4_rollback_vs_pre"]["payload_differing"]
                   and doc["C4_rollback_vs_pre"]["normalized_report_identical"]) else "FAIL")

    doc["C5_original_criterion"] = compare(a["old"], a["def30"])
    doc["C5_original_criterion"]["gene_counts"] = {
        "old": sorted(set(a["old"]["genes"].values())),
        "def30": sorted(set(a["def30"]["genes"].values()))}
    doc["C5_original_criterion"]["verdict"] = (
        "PASS" if doc["C5_original_criterion"]["payload_differing"] else "FAIL (refuted)")

    doc["C5a_plain_matches_pre"] = compare(a["old"], a["plain"])
    doc["C5a_plain_matches_pre"]["verdict"] = (
        "PASS" if (not doc["C5a_plain_matches_pre"]["payload_differing"]
                   and doc["C5a_plain_matches_pre"]["normalized_report_identical"]) else "FAIL")

    doc["C5b_judge_widens_panel"] = compare(a["old"], a["judge"])
    wide = sum(1 for c, n in a["judge"]["genes"].items() if n > a["old"]["genes"].get(c, 0))
    doc["C5b_judge_widens_panel"].update({
        "clusters_widened": wide,
        "gene_counts": {"old": sorted(set(a["old"]["genes"].values())),
                        "judge": sorted(set(a["judge"]["genes"].values()))}})
    doc["C5b_judge_widens_panel"]["verdict"] = (
        "PASS" if wide == len(a["judge"]["genes"]) and not doc["C5b_judge_widens_panel"]["payload_differing"]
        else "FAIL")

    doc["C5c_rollback_beats_judge"] = compare(a["old"], a["judgeoff"])
    doc["C5c_rollback_beats_judge"]["verdict"] = (
        "PASS" if (not doc["C5c_rollback_beats_judge"]["payload_differing"]
                   and doc["C5c_rollback_beats_judge"]["normalized_report_identical"]) else "FAIL")

    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "STAGEB_DIFFERENTIAL.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    for k in ("C4_rollback_vs_pre", "C5_original_criterion", "C5a_plain_matches_pre",
              "C5b_judge_widens_panel", "C5c_rollback_beats_judge"):
        r = doc[k]
        print("%-26s payload identical %2d/%2d  report-identical=%-5s  verdict=%s"
              % (k, r["payload_identical"], r["clusters"],
                 r["normalized_report_identical"], r["verdict"]))
    print("gene counts  old:", doc["C5b_judge_widens_panel"]["gene_counts"]["old"],
          " judge:", doc["C5b_judge_widens_panel"]["gene_counts"]["judge"])
    ok = all(doc[k]["verdict"].startswith("PASS") for k in
             ("C4_rollback_vs_pre", "C5a_plain_matches_pre", "C5b_judge_widens_panel",
              "C5c_rollback_beats_judge"))
    print("VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())