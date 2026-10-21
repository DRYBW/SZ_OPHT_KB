#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""d1_check_report_numbers.py - every headline number in the prose must exist in the artefacts.

The failure mode this guards against is mundane and has bitten this project before: a number is
written into a report by hand, the artefact is rebuilt, and the prose silently stops matching the
data. So: take each headline figure out of the JSON artefacts, format it exactly as the report
formats it, and require the same string to appear in the prose. A miss is a FAIL with the figure
printed, not a warning.

Covers REPORT.md, README.md, GRANULARITY_READER_PAGE.md and LINEAGE_READER_PAGE.md.

Usage: python3 scripts/d1_check_report_numbers.py [--json out/REPORT_NUMBER_CHECK.json]
rc: 0 = every figure found, 2 = at least one figure missing.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)

PROSE = ("REPORT.md", "README.md", "GRANULARITY_READER_PAGE.md", "LINEAGE_READER_PAGE.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(WAVE, "out", "REPORT_NUMBER_CHECK.json"))
    a = ap.parse_args()

    text = "\n".join(open(os.path.join(WAVE, f), encoding="utf-8").read() for f in PROSE)
    gs = json.load(open(os.path.join(WAVE, "out", "GRANULARITY_SUMMARY.json"), encoding="utf-8"))
    nav = json.load(open(os.path.join(WAVE, "out", "ONT_NAV_v1.json"), encoding="utf-8"))
    lin = json.load(open(os.path.join(WAVE, "out", "LINEAGE_SUMMARY.json"), encoding="utf-8"))
    cand = json.load(open(os.path.join(WAVE, "out", "CHILD_TERM_CANDIDATES.json"), encoding="utf-8"))

    want = []

    def w(figure, source):
        want.append({"figure": figure, "source": source})

    # ontology identity
    w(f"{nav['primary']['n_cl_terms_in_file']:,}", "ONT_NAV n_cl_terms_in_file")
    w(f"{nav['primary']['n_active']:,}", "ONT_NAV n_active")
    w(f"{nav['primary']['n_obsolete']}", "ONT_NAV n_obsolete")
    w(f"{nav['primary']['n_develops_from_edges']}", "ONT_NAV n_develops_from_edges")
    w(nav["primary"]["release"], "ONT_NAV release")
    w(f"{nav['label_map']['n_labels']}", "label map labels")
    w(f"{nav['label_map']['n_mapped']}", "label map mapped")
    w(f"{nav['label_map']['n_unresolved']}", "label map unresolved")
    w(f"{nav['second_file']['n_shared']:,}", "cross-file shared ids")

    # four-way
    w(f"{gs['n_clusters']}", "GRANULARITY n_clusters")
    w(f"{gs['cells']:,}", "GRANULARITY cells")
    for v, rec in gs["verdicts"].items():
        w(f"{rec['cells']:,}", f"verdict {v} cells")
        w(f"{rec['pct_cells']:.1f}%", f"verdict {v} pct")
    for k, rec in gs["no_mapping_kind"].items():
        w(f"{rec['cells']:,}", f"no_mapping_kind {k}")
    w(f"{gs['family_regex']['family_consistent']['cells']:,}", "family consistent cells")
    w(f"{gs['family_regex']['family_inconsistent']['cells']:,}", "family inconsistent cells")
    d = gs["family_inconsistent_decomposition"]
    for k in ("same_term_pure_naming", "granularity", "true_mismatch_survives", "no_mapping"):
        w(f"{d[k]:,}", f"decomposition {k}")
    ag = gs["agreement_readings"]
    w(f"{ag['family_regex_pct_of_cells']:.2f}%", "family regex rate")
    w(f"{ag['ontology_same_term_pct_of_cells']:.2f}%", "same-term rate of cells")
    w(f"{ag['ontology_same_term_pct_of_judged']:.2f}%", "same-term rate of judged")
    w(f"{ag['ontology_same_plus_granularity_pct_of_cells']:.2f}%", "same+granularity rate")
    w(f"{ag['judged_cells']:,}", "judged cells")
    r = gs["tester_reconciliation"]
    w(f"{r['his_total_cells']:,}", "tester total cells")
    w(f"{r['our_cells_on_those_pairs']:,}", "our cells on his pairs")
    w(f"{r['our_clusters_on_those_pairs']}", "our clusters on his pairs")
    w(f"{r['our_family_inconsistent_same_or_granularity_cells']:,}", "our equivalent mass cells")

    # candidates
    w(f"{cand['n_candidates']}", "n candidates")
    w(f"{cand['cells_involved']:,}", "candidate cells")
    w(f"{cand['with_corpus_support']}", "candidates with corpus support")
    multi = [c for c in cand["candidates"] if int(c["is_a_depth"]) >= 2]
    w(f"{len(multi)}", "multi-hop candidate pairs")
    w(f"{sum(int(c['cells']) for c in multi):,}", "multi-hop candidate cells")

    # lineage
    for k in ("nodes", "edges", "roots", "marker_rows", "unresolved_classes",
              "edges_with_supported_transition"):
        w(f"{lin[k]}", f"lineage {k}")
    for k, v in lin["edge_types"].items():
        w(f"{v}", f"edge type {k}")
    for k, v in lin["germ_layer_tiers"].items():
        w(f"{v}", f"germ tier {k}")
    w(f"{sum(1 for n in csv.DictReader(open(os.path.join(WAVE, 'out', 'LINEAGE_NODES.tsv'),
                                           encoding='utf-8'), delimiter='\t')
            if n['stage_scope'] == 'developing')}", "developing nodes")

    missing = [x for x in want if x["figure"] not in text]
    res = {"generated_by": "scripts/d1_check_report_numbers.py", "prose": list(PROSE),
           "figures_checked": len(want), "figures_missing": len(missing),
           "verdict": "PASS" if not missing else "FAIL", "missing": missing}
    json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[report numbers] checked={len(want)} missing={len(missing)} verdict={res['verdict']}")
    for m in missing:
        print(f"  MISSING {m['figure']}  (from {m['source']})")
    print(f"wrote {a.json}")
    return 0 if not missing else 2


if __name__ == "__main__":
    sys.exit(main())