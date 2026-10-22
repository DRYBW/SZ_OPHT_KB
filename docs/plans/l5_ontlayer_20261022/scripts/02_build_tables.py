#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the three reporting tables over the recorded cluster population, with this layer.

One command rebuilds every table below from the frozen pair list:

    python3 docs/plans/l5_ontlayer_20261022/scripts/02_build_tables.py --out <dir>

Input (frozen, committed, hash recorded): out/GRANULARITY_PAIRS_721.tsv - one row per recorded
cluster, carrying our CL term, the reference CL term, the cell count and the verdict the earlier
card recorded. It is a reading of a comparison the project had already run and already exposed; it
is therefore regression and leak-detection material, not a blind validation volume, and it is
described that way wherever these tables are cited.

Outputs
    FOURWAY_721_v2.tsv          one row per cluster: bucket, is_a_relation, ancestor_path,
                                levels crossed, unresolved_reason, assessment status
    TABLE_1_SAME_TERM.tsv       same-term agreement, canonical equality only
    TABLE_2_GRANULARITY.tsv     the granularity relation, with the below-minimum-reporting-granularity
                                count kept separate
    TABLE_3_TASK_VALIDITY.tsv   task validity components
    BUCKET_SUMMARY.json         bucket counts, the cross-check against the earlier reading, and the
                                declarations the three tables depend on

There is deliberately no blended "lenient accuracy" table: a correct-but-coarse answer is a
resolution limitation, not a biological error, and the two must not be added up. Every table keeps
the full recorded denominator; nothing is dropped from a denominator when it has no answer, and
`not_supported_by_is_a` is counted neither as correct nor as a confirmed error.

Exit codes: 0 = tables built; 3 = the fixed snapshot could not be read (no table is written).
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(d for d in [HERE] + list(HERE.parents) if (d / "kb").is_dir() and (d / "mcp_server").is_dir())
sys.path.insert(0, str(ROOT / "mcp_server"))
import ontology_layer as OL  # noqa: E402

PAIRS_REL = "docs/plans/l5_ontlayer_20261022/out/GRANULARITY_PAIRS_721.tsv"
LEGACY_MAP = {"same_term": "same_term", "we_are_coarser": "ours_broader",
              "we_are_finer": "ours_narrower", "true_mismatch": "not_supported_by_is_a",
              "no_mapping": "not_supported_by_is_a"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs/plans/l5_ontlayer_20261022/out"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    snap = OL.layer()
    if snap.anchor.get("status") != "RESOLVED":
        print(f"CANNOT RUN: the fixed ontology snapshot is not resolvable "
              f"({snap.anchor.get('status')}). No table is written and nothing is claimed.")
        return 3

    pairs = list(csv.DictReader(open(ROOT / PAIRS_REL, encoding="utf-8"), delimiter="\t"))
    rows, legacy = [], collections.Counter()
    for r in pairs:
        c = snap.compare_terms(r["ours_cl"] or "", r["theirs_cl"] or "")
        bucket = c["verdict"]
        cells = int(r["n_cells"])
        legacy[LEGACY_MAP[r["recorded_verdict"]]] += 1
        rows.append({
            "vol": r["vol"], "cluster": r["cluster"], "n_cells": cells, "tissue": r["tissue"],
            "ours_cl": c["ours"]["canonical_id"], "theirs_cl": c["theirs"]["canonical_id"],
            "recorded_verdict": r["recorded_verdict"],
            "bucket": bucket,
            "is_a_relation": c["is_a_relation"],
            "ancestor_path": " -> ".join(c["ancestor_path"] or []),
            "levels_crossed": "" if c["levels_crossed"] is None else c["levels_crossed"],
            "min_report_granularity_met": c["assessment"].get("min_report_granularity_met"),
            "assessment_status": c["assessment"]["status"],
            "unresolved_reason": c["unresolved_reason"] or "",
            "counts_as_correct": str(bucket == "same_term").lower(),
            "counts_as_confirmed_error": str(bucket == "confirmed_incompatible").lower(),
        })

    with open(out / "FOURWAY_721_v2.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    n_total = len(rows)
    cells_total = sum(r["n_cells"] for r in rows)
    by_bucket = collections.Counter(r["bucket"] for r in rows)
    cells_by_bucket = collections.Counter()
    for r in rows:
        cells_by_bucket[r["bucket"]] += r["n_cells"]

    # --- table 1: same-term agreement (canonical equality only; fixed denominator)
    with open(out / "TABLE_1_SAME_TERM.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["row", "n_clusters", "n_cells", "denominator_clusters",
                    "denominator_cells", "pct_clusters", "pct_cells", "counts_as_correct", "note"])
        w.writerow(["same canonical CL term", by_bucket["same_term"], cells_by_bucket["same_term"],
                    n_total, cells_total, round(100 * by_bucket["same_term"] / n_total, 3),
                    round(100 * cells_by_bucket["same_term"] / cells_total, 3), "true",
                    "canonical identity only; no naming-only credit is given elsewhere in this table"])
        w.writerow(["all other buckets", n_total - by_bucket["same_term"],
                    cells_total - cells_by_bucket["same_term"], n_total, cells_total,
                    round(100 * (n_total - by_bucket["same_term"]) / n_total, 3),
                    round(100 * (cells_total - cells_by_bucket["same_term"]) / cells_total, 3),
                    "false", "kept in the denominator; nothing is removed for having no answer"])

    # --- table 2: granularity relation
    with open(out / "TABLE_2_GRANULARITY.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["relation", "n_clusters", "n_cells", "levels_crossed_min", "levels_crossed_max",
                    "n_below_min_reporting_granularity", "counts_as_correct",
                    "counts_as_confirmed_error", "note"])
        def lv(b):
            v = [int(r["levels_crossed"]) for r in rows
                 if r["bucket"] == b and r["levels_crossed"] != ""]
            return (min(v), max(v)) if v else ("", "")
        for b, note in (
                ("ours_broader", "our term is an ancestor of the reference term: a coarser answer, "
                                 "which is a resolution limitation"),
                ("ours_narrower", "our term is finer than the reference term: the extra resolution is "
                                  "unverified and earns nothing"),
                ("confirmed_incompatible", "requires explicit incompatibility evidence; the graph "
                                           "alone never establishes exclusion"),
                ("not_supported_by_is_a", "no ancestor relation, or one side unmapped: counted "
                                          "neither as correct nor as a confirmed error"),
                ("same_term", "reported in table 1 as agreement, listed here for the denominator")):
            lo, hi = lv(b)
            below = sum(1 for r in rows if r["bucket"] == b
                        and r["min_report_granularity_met"] is False)
            w.writerow([b, by_bucket[b], cells_by_bucket[b], lo, hi, below,
                        str(b == "same_term").lower(), str(b == "confirmed_incompatible").lower(), note])
        w.writerow(["TOTAL", n_total, cells_total, "", "", "", "", "", "fixed denominator = the whole "
                    "recorded population"])

    # --- table 3: task validity
    n_ctx = sum(1 for r in rows if r["tissue"])
    n_meets = sum(1 for r in rows if r["min_report_granularity_met"] is True)
    n_evid = sum(1 for r in rows if r["assessment_status"] in ("supported", "resolution_limited",
                                                               "incompatible"))
    n_review = sum(1 for r in rows if r["assessment_status"] in ("under_review", "unmapped"))
    with open(out / "TABLE_3_TASK_VALIDITY.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["component", "n_clusters", "denominator_clusters", "note"])
        w.writerow(["context recorded in the row (tissue/volume)", n_ctx, n_total,
                    "a recorded tissue is not a pre-registered task context; context qualification is "
                    "not assessable from this population and no credit is taken for it"])
        w.writerow(["meets the minimum reporting granularity", n_meets, n_total,
                    "a relation that only reaches a blanket ancestor does not qualify"])
        w.writerow(["evidence sufficient for the answer", n_evid, n_total,
                    "coarse-but-correct counts here only as a resolution limitation"])
        w.writerow(["still under review / unmapped", n_review, n_total,
                    "kept in the denominator, counted as neither correct nor a confirmed error"])

    legacy_full = {b: legacy.get(b, 0) for b in OL.BUCKETS}
    summary = {
        "generated_by": "docs/plans/l5_ontlayer_20261022/scripts/02_build_tables.py",
        "input": {"path": PAIRS_REL, "n_rows": n_total},
        "ontology": snap.snapshot_record(),
        "buckets": {b: {"clusters": by_bucket[b], "cells": cells_by_bucket[b],
                        "pct_clusters": round(100 * by_bucket[b] / n_total, 3),
                        "pct_cells": round(100 * cells_by_bucket[b] / cells_total, 3)}
                    for b in OL.BUCKETS},
        "denominator": {"clusters": n_total, "cells": cells_total,
                        "rule": "fixed: every recorded cluster stays in the denominator, including "
                                "the ones with no answer on our side"},
        "unmapped": {
            "clusters": sum(1 for r in rows if r["is_a_relation"] == "unresolved"),
            "note": "reported inside not_supported_by_is_a and separately here; counted as neither "
                    "correct nor a confirmed error"},
        "cross_check_against_the_earlier_reading": {
            "source": "the delivered four-way table of the earlier ontology-navigation card, carried "
                      "in the frozen pair list as recorded_verdict",
            "recorded_bucket_counts": legacy_full,
            "recomputed_bucket_counts": {k: by_bucket[k] for k in OL.BUCKETS},
            "identical": legacy_full == {k: by_bucket[k] for k in OL.BUCKETS},
            "note": "bucket names changed with the ruling (we_are_coarser -> ours_broader, "
                    "true_mismatch and no_mapping both -> not_supported_by_is_a, which is why the "
                    "latter two are additionally split by is_a_relation)"},
        "declarations": {
            "population_is_regression_material": "this population is a comparison the project had "
                "already run and already exposed; it is regression and leak-detection material, not "
                "a blind validation volume",
            "no_lenient_accuracy": "no table blends the buckets into one accuracy figure",
            "granularity_rule": f"blanket ancestor threshold = "
                                f"{snap.blanket_threshold} active CL descendants, declared before "
                                f"this run",
        },
    }
    (out / "BUCKET_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"n_total": n_total, "cells": cells_total,
                      "buckets": {k: by_bucket[k] for k in OL.BUCKETS},
                      "cross_check_identical": summary[
                          "cross_check_against_the_earlier_reading"]["identical"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())