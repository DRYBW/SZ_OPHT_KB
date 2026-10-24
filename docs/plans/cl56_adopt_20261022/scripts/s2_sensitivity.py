# -*- coding: utf-8 -*-
"""s2_sensitivity.py -- the acceptance reading under a CORRECTED ontology closure (instrument sensitivity).

Why: the frozen harness's `Rulers._load_obo` keeps the trailing qualifier on `is_a` lines, so the
686 qualified edges of the pinned release never enter its ancestor closure. Measured on the shipped
tree: 26 of the 721 recorded clusters are read `truly_inconsistent` by the harness and
`kb_coarser`/`kb_finer` by a closure that strips the qualifier (out/CLOSURE_INSTRUMENT_DIFFERENCE.json)
-- and because R_fam's `related()` calls the same closure, those clusters are also graded
`inconsistent` instead of `related`.

This script re-reads BOTH arms under the corrected closure and reports the acceptance quantities
again, so the ruling in out/ACCEPTANCE.json can be checked for instrument dependence. It changes no
delivered artefact and no primary reading; the harness reading stays primary (comparability with the
cards that reused it).

Run: /usr/bin/python3 s2_sensitivity.py
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, "/mnt/D/EyeKB/plans/noregr_20261022/scripts")
sys.path.insert(0, HERE)
import wave_common as W          # noqa: E402
import ont_closure_probe as P    # noqa: E402

LIB = "cl56_v15"
ON = {"EYEKB_ACT_CL56": "1"}
GRADES = ("consistent", "related", "inconsistent", "mixed")


def corrected_grade(rulers, top, ref_family, ref_cell_type):
    if not top:
        return "mixed"
    if rulers.fam_of(top) == ref_family:
        return "consistent"
    if P.cl_grade(top, ref_cell_type) in ("same_cl", "kb_coarser", "kb_finer"):
        return "related"
    return "inconsistent"


def shares(rows):
    tot = sum(r["n_cells"] for r in rows) or 1
    c = Counter(r["grade"] for r in rows)
    cells = Counter()
    for r in rows:
        cells[r["grade"]] += r["n_cells"]
    return {"n_clusters": len(rows), "n_cells": tot,
            "share_pct": {g: round(100.0 * cells.get(g, 0) / tot, 3) for g in GRADES},
            "clusters": {g: c.get(g, 0) for g in GRADES}}


def main():
    if "EYEKB_ACT_CL56" not in W.SWITCHES:
        W.SWITCHES = tuple(W.SWITCHES) + ("EYEKB_ACT_CL56",)
    calls = W.load_set()
    rulers = W.Rulers(calls)
    views = {"before": W.replay(calls, ON, label="sens_before"),
             "after": W.replay(calls, ON, inject=[LIB], label="sens_after")}
    out = {"probe": "s2_sensitivity.py", "library": LIB,
           "note": ("both arms are read under each ruler; the harness ruler is primary and unchanged, "
                    "this is a sensitivity reading of the verdict"),
           "rulers": {}}
    for name, fn in (("harness", lambda k, c: rulers.grade(views["before"][k]["top"], c["ref_family"],
                                                           c["ref_cell_type"])),
                     ("corrected_closure", lambda k, c: corrected_grade(
                         rulers, views["before"][k]["top"], c["ref_family"], c["ref_cell_type"]))):
        pass  # placeholder, replaced below (each arm needs its own view)

    readings = {}
    for ruler_name in ("harness", "corrected_closure"):
        per = {}
        for arm in ("before", "after"):
            rows = []
            for c in calls:
                k = (c["vol"], c["cluster"])
                top = views[arm][k]["top"]
                if ruler_name == "harness":
                    g = rulers.grade(top, c["ref_family"], c["ref_cell_type"])
                else:
                    g = corrected_grade(rulers, top, c["ref_family"], c["ref_cell_type"])
                rows.append({"grade": g, "n_cells": c["n_cells"], "vol": c["vol"]})
            per[arm] = rows
        sh_b, sh_a = shares(per["before"]), shares(per["after"])
        by = {}
        for arm in ("before", "after"):
            d = {}
            for r in per[arm]:
                d.setdefault(r["vol"], []).append(r)
            by[arm] = {v: shares(rs) for v, rs in d.items()}
        falls = {ds: {"before_pct": by["before"][ds]["share_pct"]["consistent"],
                      "after_pct": by["after"][ds]["share_pct"]["consistent"],
                      "delta_pp": round(by["after"][ds]["share_pct"]["consistent"]
                                        - by["before"][ds]["share_pct"]["consistent"], 3)}
                 for ds in sorted(by["before"])
                 if by["after"][ds]["share_pct"]["consistent"]
                 - by["before"][ds]["share_pct"]["consistent"] < -1e-9}
        rising = {ds: {"before_pct": by["before"][ds]["share_pct"]["inconsistent"],
                       "after_pct": by["after"][ds]["share_pct"]["inconsistent"],
                       "delta_pp": round(by["after"][ds]["share_pct"]["inconsistent"]
                                         - by["before"][ds]["share_pct"]["inconsistent"], 3)}
                  for ds in sorted(by["before"])
                  if by["after"][ds]["share_pct"]["inconsistent"]
                  - by["before"][ds]["share_pct"]["inconsistent"] > 1e-9}
        readings[ruler_name] = {
            "overall_before": sh_b, "overall_after": sh_a,
            "delta_pp": {g: round(sh_a["share_pct"][g] - sh_b["share_pct"][g], 3) for g in GRADES},
            "clause_a_falls": falls, "n_falls": len(falls),
            "clause_b_rising": rising, "n_rising": len(rising),
            "clause_a_verdict": "FAIL" if falls else "PASS",
            "clause_b_verdict": "FAIL" if (rising or
                                           sh_a["share_pct"]["inconsistent"]
                                           > sh_b["share_pct"]["inconsistent"]) else "PASS"}
    out["rulers"] = readings
    out["verdict_under_each_ruler"] = {k: {"a": v["clause_a_verdict"], "b": v["clause_b_verdict"],
                                          "overall": ("NO-GO" if "FAIL" in (v["clause_a_verdict"],
                                                                            v["clause_b_verdict"])
                                                      else "GO")}
                                      for k, v in readings.items()}
    with open(os.path.join(OUT, "SENSITIVITY.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    for k, v in readings.items():
        print("%-18s consistent %.3f -> %.3f (%+.3fpp) | inconsistent %.3f -> %.3f (%+.3fpp) | "
              "falls=%d rising=%d -> %s"
              % (k, v["overall_before"]["share_pct"]["consistent"],
                 v["overall_after"]["share_pct"]["consistent"], v["delta_pp"]["consistent"],
                 v["overall_before"]["share_pct"]["inconsistent"],
                 v["overall_after"]["share_pct"]["inconsistent"], v["delta_pp"]["inconsistent"],
                 v["n_falls"], v["n_rising"], out["verdict_under_each_ruler"][k]["overall"]))
    print("wrote out/SENSITIVITY.json")


if __name__ == "__main__":
    main()