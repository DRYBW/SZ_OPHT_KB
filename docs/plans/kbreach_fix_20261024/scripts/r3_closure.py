# -*- coding: utf-8 -*-
"""r3_closure.py (v2) -- re-derive the frozen harness's qualified-is_a closure gap, two top sources:

 (A) TOP SOURCE = service replay (the CLOSURE_INSTRUMENT_DIFFERENCE caliber):
     W.replay(calls, {"EYEKB_ACT_CL56": "1"}, label="kbreach_sens_before") gives per-cluster top,
     exactly as s2_sensitivity.py consumed it; 4-way grades under
       harness = Rulers.cl_grade (keeps the "{...}" qualifier on is_a parents), and
       corrected = ont_closure_probe.cl_grade (qualifier stripped, same truth maps).
     Also the R_fam 3-state reading (rulers.grade vs corrected_grade of s2) so the
     "graded inconsistent instead of related" implication is counted, not asserted.
 (B) TOP SOURCE = the recorded ledger's pred_top1 (no service call; a second opinion).

Zero writes outside out/; zero network. Replay runs the shipped core in-process (~24 s).
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
NOREGR = "/mnt/D/EyeKB/plans/noregr_20261022/scripts"
L6CL = "/mnt/D/EyeKB/plans/cl56_adopt_20261022/scripts"
sys.path.insert(0, NOREGR)
sys.path.insert(0, L6CL)
import wave_common as W            # noqa: E402
import ont_closure_probe as P      # noqa: E402

ON = {"EYEKB_ACT_CL56": "1"}
calls = W.load_set()
if "EYEKB_ACT_CL56" not in W.SWITCHES:
    W.SWITCHES = tuple(W.SWITCHES) + ("EYEKB_ACT_CL56",)
rulers = W.Rulers(calls)


def corrected_grade(rulers_, top, ref_family, ref_cell_type):
    """s2_sensitivity.caliber: fam match = consistent; corrected-closure relation = related."""
    if not top:
        return "mixed"
    if rulers_.fam_of(top) == ref_family:
        return "consistent"
    if P.cl_grade(top, ref_cell_type) in ("same_cl", "kb_coarser", "kb_finer"):
        return "related"
    return "inconsistent"


def fourway_block(rows):
    """rows: list of (c, top, g_harness, g_corrected)."""
    dist_h = Counter(g_h for _, _, g_h, _ in rows)
    dist_c = Counter(g_c for _, _, _, g_c in rows)
    changed = [{"vol": c["vol"], "cluster": str(c["cluster"]), "pred_top1": top,
                "truth": c["ref_cell_type"], "harness": g_h, "corrected": g_c,
                "n_cells": c.get("n_cells")}
               for c, top, g_h, g_c in rows if g_h != g_c]
    return {"dist_harness": dict(dist_h), "dist_corrected": dict(dist_c),
            "n_changed": len(changed), "changed_clusters": changed}


# ---------------- (A) replay-top caliber ----------------
views_before = W.replay(calls, ON, label="kbreach_sens_before")
rows_a = [None] * len(calls)
for i, c in enumerate(calls):
    top = views_before[(c["vol"], c["cluster"])]["top"]
    rows_a[i] = (c, top, rulers.cl_grade(top, c["ref_cell_type"]),
                 P.cl_grade(top, c["ref_cell_type"]))
blockA = fourway_block(rows_a)
# R_fam 3-state under both rulers (same replay tops)
tri_h = Counter(rulers.grade(m[1], c["ref_family"], c["ref_cell_type"])
                for c, m in zip(calls, rows_a))
tri_c = Counter(corrected_grade(rulers, m[1], c["ref_family"], c["ref_cell_type"])
                for c, m in zip(calls, rows_a))
fam_moves = [{"vol": c["vol"], "cluster": str(c["cluster"]),
              "pred_top1": m[1],
              "truth": c["ref_cell_type"],
              "state_harness": rulers.grade(m[1], c["ref_family"], c["ref_cell_type"]),
              "state_corrected": corrected_grade(rulers, m[1], c["ref_family"], c["ref_cell_type"])}
             for c, m in zip(calls, rows_a)
             if rulers.grade(m[1], c["ref_family"], c["ref_cell_type"])
             != corrected_grade(rulers, m[1], c["ref_family"], c["ref_cell_type"])]

# ---------------- (B) recorded-ledger-top caliber ----------------
rows_b = [None] * len(calls)
for i, c in enumerate(calls):
    top = (c.get("truth") or {}).get("recorded_pred_top1")
    rows_b[i] = (c, top, rulers.cl_grade(top, c["ref_cell_type"]),
                 P.cl_grade(top, c["ref_cell_type"]))
blockB = fourway_block(rows_b)

d = P._load()
doc = {
    "probe": "r3_closure.py (v2)",
    "command": "/usr/bin/python3 scripts/r3_closure.py",
    "n_recorded_clusters": len(calls),
    "obo_sha256": d.get("obo_sha256"),
    "qualified_is_a_lines_any_qualifier": d.get("n_qualified_is_a_lines"),
    "A_replay_top": {**blockA,
                     "rfam_states_harness": dict(tri_h), "rfam_states_corrected": dict(tri_c),
                     "n_rfam_state_moves": len(fam_moves),
                     "rfam_state_moved_clusters": fam_moves[:40]},
    "B_ledger_top": blockB,
}
with open(os.path.join(OUT, "R3_CLOSURE_READING.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps({k: doc[k] for k in ("n_recorded_clusters", "qualified_is_a_lines_any_qualifier")}, indent=1))
for blk in ("A_replay_top", "B_ledger_top"):
    b = doc[blk]
    print(blk, "harness:", b["dist_harness"])
    print(" " * len(blk), "corrected:", b["dist_corrected"], "| n_changed:", b["n_changed"])
print("A rfam harness:", doc["A_replay_top"]["rfam_states_harness"],
      "corrected:", doc["A_replay_top"]["rfam_states_corrected"],
      "moves:", doc["A_replay_top"]["n_rfam_state_moves"])
