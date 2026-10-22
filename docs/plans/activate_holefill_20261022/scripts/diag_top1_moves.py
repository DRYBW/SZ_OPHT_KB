#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diagnostic -- why do 90 clusters change their top-1 answer to a class that is NOT one of the
library's own entries?

`l2_flip_measure.py` classifies every moved cluster whose top-1 changed to a non-`holefill_v12` class
as `unexpected`; the card's clause (c) requires the movement to be attributable, so the mechanism is
named here rather than assumed. The script reads the two arms through the frozen engine, and for every
cluster whose top-1 moved records the before/after top-3 with their `n_shared` and owning library, plus
the candidate count. Writes out/DIAG_TOP1_MOVES.json.

Measurement only: nothing is written outside this wave's out/ directory.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, "/home/ubuntu/EYEKB_REPO/docs/plans/noregr_20261022/scripts")
import wave_common as W          # noqa: E402

OFF = {"EYEKB_ACT_HOLEFILL": "0"}
ON = {"EYEKB_ACT_HOLEFILL": "1"}


def short(label):
    return str(label or "").split("::")[-1]


def main():
    if "EYEKB_ACT_HOLEFILL" not in W.SWITCHES:
        W.SWITCHES = tuple(W.SWITCHES) + ("EYEKB_ACT_HOLEFILL",)
    calls = W.load_set()
    b = W.replay(calls, OFF, label="diag_kill")
    a = W.replay(calls, ON, label="diag_flip")
    moved = []
    for c in calls:
        k = (c["vol"], c["cluster"])
        if b[k]["top"] == a[k]["top"]:
            continue
        moved.append({
            "vol": c["vol"], "cluster": c["cluster"], "n_cells": c["n_cells"],
            "truth": c["ref_cell_type"], "family": c["ref_family"], "tissue": c["tissue"],
            "before_top": b[k]["top"], "before_n_shared": b[k]["n_shared"],
            "after_top": a[k]["top"], "after_n_shared": a[k]["n_shared"],
            "n_ranked_before": b[k]["n_ranked"], "n_ranked_after": a[k]["n_ranked"],
            "before_top3": b[k]["top3"], "after_top3": a[k]["top3"]})
    moved.sort(key=lambda r: -r["n_cells"])
    pairs = Counter("%s -> %s" % (short(m["before_top"]), short(m["after_top"])) for m in moved)
    after_classes = Counter(short(m["after_top"]) for m in moved)
    lib_won = sum(1 for m in moved if str(m["after_top"]).startswith("holefill_v12::")
                  or (m["after_top"] or "").startswith("holefill_v12::"))
    # was a library entry present anywhere in the after candidate window?
    lib_in_window = sum(1 for m in moved
                        if any("markers_v12_holefill_increment" in str(x[2])
                               for x in (m["after_top3"] or [])))
    doc = {"probe": "diag_top1_moves.py",
           "question": ("of the clusters whose top-1 answer changed, how many changed TO a library "
                        "entry, and what are the rest?"),
           "n_top1_moved": len(moved),
           "n_top1_changed_to_a_library_entry": lib_won,
           "n_with_a_library_entry_in_the_after_top3_window": lib_in_window,
           "transition_pairs": dict(pairs.most_common()),
           "after_top1_class_census": dict(after_classes.most_common()),
           "examples": moved[:8],
           "note": ("the diagnostic reads the two arms through the frozen engine; it changes nothing "
                    "and is reported as a finding of this card, whichever way the acceptance rule "
                    "rules")}
    with open(os.path.join(OUT, "DIAG_TOP1_MOVES.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("top-1 moved clusters:", len(moved),
          "| changed TO a library entry:", lib_won,
          "| library entry inside the after top-3 window:", lib_in_window)
    print("transition pairs (top 15):")
    for k, v in pairs.most_common(15):
        print("   %4d  %s" % (v, k))
    print("after-top-1 class census (top 15):")
    for k, v in after_classes.most_common(15):
        print("   %4d  %s" % (v, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())