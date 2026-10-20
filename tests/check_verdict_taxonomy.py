#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a verdict summary table against docs/VERDICT_TAXONOMY.md.

Usage:
    python3 tests/check_verdict_taxonomy.py <summary.json> [...]

Accepted shape, either flat or wrapped in a container that names the total:

    {"axis": "A", "total": 1495330, "weighting": "cells", "states": {...}}
    {"axis": "B", "total": 1495330, "weighting": "cells", "states": {...}}

Exit 0 if every input passes, 1 otherwise. Read-only.
"""
import json
import sys

AXIS_A = ("same_cl", "we_finer", "we_coarser", "kb_lacks_class",
          "mismatch", "abstain", "unmappable")
AXIS_B = ("in_top1", "same_count_lost", "lower_count",
          "not_admitted", "no_entry", "abstain")
TOL = 0  # exact counts; percentages are display only


def check(path):
    errs = []
    try:
        d = json.load(open(path))
    except Exception as exc:
        return [f"{path}: not JSON ({exc})"]
    axis = d.get("axis")
    if axis not in ("A", "B"):
        return [f"{path}: missing or invalid 'axis' (must be 'A' or 'B')"]
    allowed = AXIS_A if axis == "A" else AXIS_B
    states = d.get("states")
    if not isinstance(states, dict):
        return [f"{path}: missing 'states' object"]
    unknown = sorted(set(states) - set(allowed))
    if unknown:
        errs.append(f"{path}: state names not in axis {axis}: {unknown}")
    if not any(k in states for k in allowed):
        errs.append(f"{path}: no recognised state present")
    total = d.get("total")
    if not isinstance(total, int):
        errs.append(f"{path}: missing integer 'total'")
    else:
        got = sum(v for v in states.values() if isinstance(v, (int, float)))
        if abs(got - total) > TOL:
            errs.append(f"{path}: states sum to {got:,.0f} but total is {total:,}")
    if "weighting" not in d:
        errs.append(f"{path}: missing 'weighting' (cells or clusters)")
    if axis == "A":
        for k in ("mismatch", "kb_lacks_class"):
            if k in states and states[k] < 0:
                errs.append(f"{path}: negative count for {k}")
        if "mismatch" in states and "kb_lacks_class" not in states:
            errs.append(f"{path}: axis A reports 'mismatch' without separating "
                        f"'kb_lacks_class' - this is the 2026-10-20 defect")
    if axis == "B" and d.get("cache_width") is None:
        errs.append(f"{path}: axis B must declare 'cache_width' (panel width "
                    f"that produced the candidate cache)")
    return errs


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    bad = 0
    for p in argv[1:]:
        errs = check(p)
        if errs:
            bad += 1
            print(f"FAIL {p}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"PASS {p}")
    print(f"\n{len(argv)-1 - bad}/{len(argv)-1} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
