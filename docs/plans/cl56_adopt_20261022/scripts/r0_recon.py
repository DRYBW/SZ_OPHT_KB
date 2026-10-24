# -*- coding: utf-8 -*-
"""CL56-ADOPT reconnaissance (READ-ONLY).

Purpose: read the FROZEN RECORDING's current state for the 93 recorded clusters that belong to the
25 corpus-supported (parent -> child) pairs, under the reused no-regression harness
(docs/plans/noregr_20261022/scripts/wave_common.py), BEFORE any increment exists and BEFORE the
pre-registration numbers are fixed.

This measures the SHIPPED tree only. It applies no overlay, writes nothing outside its own stdout
log, and touches no repository file. Nothing here is an after-arm reading.

Run:  /usr/bin/python3 r0_recon.py
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

WAVE = "/mnt/D/EyeKB/plans/cl_depth_devlineage_20261021/out"
TWO = "/mnt/D/EyeKB/plans/cl_depth_devlineage_20261021/out/GRANULARITY_FOURWAY_721.tsv"
CAND = os.path.join(WAVE, "CHILD_TERM_CANDIDATES.json")
NREGR = "/mnt/D/EyeKB/plans/noregr_20261022/scripts"
sys.path.insert(0, NREGR)
import wave_common as W  # noqa: E402


def in_scope_pairs():
    d = json.load(open(CAND))
    sup = [c for c in d["candidates"] if c["corpus_support_status"].startswith("corpus_")]
    return {(c["our_labels"], c["child_cl"]): c for c in sup}


def scope_rows(key):
    rows = list(csv.DictReader(open(TWO), delimiter="\t"))
    out = []
    for r in rows:
        if r["verdict"] == "we_are_coarser" and (r["ours_label"], r["their_cl"]) in key:
            out.append(r)
    return out


def main():
    key = in_scope_pairs()
    rows = scope_rows(key)
    calls = W.load_set()
    rulers = W.Rulers(calls)
    by_key = {(c["vol"], c["cluster"]): c for c in calls}

    print("== recorded set: %d clusters / %d cells" % (len(calls), sum(c["n_cells"] for c in calls)))
    print("== in-scope pairs: %d (corpus-supported) ; recorded coarser rows matched: %d"
          % (len(key), len(rows)))
    missing = [(r["vol"], r["cluster"]) for r in rows if (r["vol"], r["cluster"]) not in by_key]
    print("== in-scope rows with no recorded query window: %d %s" % (len(missing), missing[:5]))

    before = W.replay(calls, label="recon_before")
    graded = W.grade_arm(calls, before, rulers)
    sh = W.shares([graded[k] for k in graded])
    print("== whole recording (shipped tree, no overlay):")
    print("   share_pct", sh["share_pct"], " clusters", sh["clusters"])

    # scope subset
    sub = [(r["vol"], r["cluster"]) for r in rows if (r["vol"], r["cluster"]) in graded]
    print("== the in-scope subset: %d clusters / %d cells"
          % (len(sub), sum(by_key[k]["n_cells"] for k in sub)))
    print("   grade:", dict(Counter(graded[k]["grade"] for k in sub)))
    print("   cl   :", dict(Counter(graded[k]["cl"] for k in sub)))
    print("   top-1:", dict(Counter(graded[k]["top"] for k in sub)))

    print("== per pair: cells, before grade counts, before top-1 counts")
    g = defaultdict(list)
    for r in rows:
        k = (r["vol"], r["cluster"])
        if k in graded:
            g[(r["ours_label"], r["their_cl"])].append(k)
    agg = {}
    for kk, ks in sorted(g.items(), key=lambda kv: -sum(by_key[x]["n_cells"] for x in kv[1])):
        cells = sum(by_key[x]["n_cells"] for x in ks)
        agg["%s->%s" % kk] = {"clusters": len(ks), "cells": cells,
                              "grade": dict(Counter(graded[x]["grade"] for x in ks)),
                              "cl": dict(Counter(graded[x]["cl"] for x in ks)),
                              "top1": dict(Counter(graded[x]["top"] for x in ks)),
                              "child_label": key[kk]["child_cl_label"]}
        print("  %-10s %-12s %-38s cells=%7d %s | %s"
              % (kk[0], kk[1], key[kk]["child_cl_label"][:38], cells,
                 dict(Counter(graded[x]["grade"] for x in ks)),
                 dict(Counter(graded[x]["cl"] for x in ks))))
    os.makedirs("/mnt/D/EyeKB/plans/cl56_adopt_20261022/out", exist_ok=True)
    W.save_json("/mnt/D/EyeKB/plans/cl56_adopt_20261022/out/RECON_BEFORE_SCOPE.json",
                {"scope_pairs": len(key), "scope_clusters": len(sub),
                 "scope_cells": sum(by_key[k]["n_cells"] for k in sub),
                 "whole_recording_shares": sh, "per_pair": agg,
                 "ruler_selfcheck": rulers.ruler_selfcheck(calls)})
    print("== wrote out/RECON_BEFORE_SCOPE.json")


if __name__ == "__main__":
    main()