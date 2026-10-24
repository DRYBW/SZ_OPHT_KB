# -*- coding: utf-8 -*-
"""m1_measure.py -- measure the CL-56 adoption with the predecessor harness (reused, not re-implemented).

Instrument reused byte-for-byte: plans/noregr_20261022/scripts/{wave_common.py,n3_harness.py}.
One thing is ADDED and declared: the harness's switch-hygiene tuple predates `EYEKB_ACT_CL56`, so this
script extends `wave_common.SWITCHES` with that one name. No ruler, grade, threshold or rule changes.

Arms (all in-process, on the shipped tree with the increment registered default OFF):
  A1  recorded declarations   before = switch ON / empty whitelist (the shipped default)
                              after  = same + measurement-only inject:["cl56_v15"]
  A2  tester re-declarations  same, with CX16/CX11 re-pointed to ocular_surface
  A3  the DEFAULT route (no `tissue` argument): the surface a default-route flip changes
Plus, on the same run: the equivalence check (the injected arm == the flipped arm, cluster by cluster,
once the whitelist is flipped -- run after the flip), the moved-cluster attribution, the ontology
reading, and the per-cluster clause-(d) table for the adopted demand clusters.

Writes out/MEASURE.json + out/harness/<tag>/REPORT.json|.md
Run: /usr/bin/python3 m1_measure.py
"""
import json
import os
import resource
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
NRE = "/mnt/D/EyeKB/plans/noregr_20261022/scripts"
REPO = "/home/ubuntu/EYEKB_REPO"
sys.path.insert(0, NRE)
sys.path.insert(0, HERE)
import wave_common as W          # noqa: E402
import n3_harness as H           # noqa: E402

LIB = "cl56_v15"
INC_FILE = os.path.join(REPO, "kb/markers/markers_v15_cl56_increment.json")
SWITCH = "EYEKB_ACT_CL56"
TESTER_DECLS = {"CX16_tabula_sapiens_eye": "ocular_surface",
                "CX11_posterior_eye_atlas": "ocular_surface"}
ON = {SWITCH: "1"}
ORDER = {"consistent": 3, "related": 2, "inconsistent": 1, "mixed": 0}


def lib_classes():
    inc = json.load(open(INC_FILE, encoding="utf-8"))
    return {str(k).casefold() for k in (inc.get("markers") or {})}


def adopted_entries():
    inc = json.load(open(INC_FILE, encoding="utf-8"))
    return {e["class_name"]: e for e in inc.get("entries") or []}


def won_by_the_library(view, classes):
    if str(view.get("library") or "").endswith("markers_v15_cl56_increment.json"):
        return True
    top = str(view.get("top") or "")
    return top.split("::")[-1].strip().casefold() in classes


def inconsistent_reading(calls, g_before, g_after, label):
    ob = W.shares([g_before[k] for k in g_before])
    oa = W.shares([g_after[k] for k in g_after])
    ds_b, ds_a = W.by_dataset(calls, g_before), W.by_dataset(calls, g_after)
    per_ds = {}
    for ds in sorted(set(ds_b) | set(ds_a)):
        b, a = ds_b[ds]["share_pct"], ds_a[ds]["share_pct"]
        if abs(a["inconsistent"] - b["inconsistent"]) > 1e-9:
            per_ds[ds] = {"before_pct": b["inconsistent"], "after_pct": a["inconsistent"],
                          "delta_pp": round(a["inconsistent"] - b["inconsistent"], 3)}
    delta = round(oa["share_pct"]["inconsistent"] - ob["share_pct"]["inconsistent"], 3)
    return {"reading": label, "overall_before_pct": ob["share_pct"]["inconsistent"],
            "overall_after_pct": oa["share_pct"]["inconsistent"], "overall_delta_pp": delta,
            "overall_rises": delta > 0,
            "datasets_rising": {k: v for k, v in per_ds.items() if v["delta_pp"] > 0},
            "per_dataset_delta_pp": per_ds,
            "consistent_before_pct": ob["share_pct"]["consistent"],
            "consistent_after_pct": oa["share_pct"]["consistent"],
            "mixed_before_pct": ob["share_pct"]["mixed"],
            "mixed_after_pct": oa["share_pct"]["mixed"]}


def consistent_falls(calls, g_before, g_after, label):
    ds_b, ds_a = W.by_dataset(calls, g_before), W.by_dataset(calls, g_after)
    falls = {}
    for ds in sorted(set(ds_b) | set(ds_a)):
        b, a = ds_b[ds]["share_pct"]["consistent"], ds_a[ds]["share_pct"]["consistent"]
        if a - b < -1e-9:
            falls[ds] = {"before_pct": b, "after_pct": a, "delta_pp": round(a - b, 3)}
    return {"reading": label, "datasets_checked": len(set(ds_b) | set(ds_a)),
            "falls": falls, "n_falls": len(falls)}


def cl_counts(graded, keys):
    return dict(Counter(graded[k]["cl"] for k in keys))


def main():
    t0 = time.time()
    declared_extension = None
    if SWITCH not in W.SWITCHES:
        declared_extension = list(W.SWITCHES)
        W.SWITCHES = tuple(W.SWITCHES) + (SWITCH,)
    classes = lib_classes()
    entries = adopted_entries()

    calls = W.load_set()
    rulers = W.Rulers(calls)
    selfcheck = rulers.ruler_selfcheck(calls)
    keys = [(c["vol"], c["cluster"]) for c in calls]
    scope_rows = json.load(open(os.path.join(OUT, "SCOPE.json")))
    adopted_labels = {r["child_label"].strip() for r in scope_rows["rows"] if r["adopted"]}
    scope_keys = [k for k in keys if next(c for c in calls
                                          if (c["vol"], c["cluster"]) == k)["ref_cell_type"].strip()
                  in adopted_labels]

    specs = [
        ("A1_recorded_decls", {
            "name": "A1 adoption of cl56_v15 (recorded tissue declarations)",
            "declared_change": "measurement-only: cl56_v15 merged into the default `all` route",
            "before": {"env": dict(ON)}, "after": {"env": dict(ON), "inject": [LIB]}}),
        ("A2_tester_decls", {
            "name": "A2 same adoption under the external tester's re-declarations",
            "declared_change": "as A1, with CX16 and CX11 re-pointed to ocular_surface",
            "tissue_declarations": TESTER_DECLS,
            "before": {"env": dict(ON)}, "after": {"env": dict(ON), "inject": [LIB]}}),
    ]
    runs = {}
    for tag, spec in specs:
        runs[tag] = H.run_spec(spec, calls, rulers, os.path.join(OUT, "harness", tag))
        d = runs[tag]
        print("   %-20s verdict=%-16s changed=%d clusters / %d cells | consistent %+.3fpp | inconsistent %+.3fpp"
              % (tag, d["ruling"]["verdict"], d["changed_clusters"], d["changed_cells"],
                 d["overall_delta_pp"]["consistent"], d["overall_delta_pp"]["inconsistent"]))

    # ---- arm views (full rankings) for the default route, the attribution and the clause-(d) table
    v_before = W.replay(calls, ON, label="before")
    v_after = W.replay(calls, ON, inject=[LIB], label="after")
    g_before = W.grade_arm(calls, v_before, rulers)
    g_after = W.grade_arm(calls, v_after, rulers)

    # the DEFAULT route: the same two arms with no `tissue` argument
    v_before_d = W.replay(calls, ON, use_own_tissue=False, label="before_default")
    v_after_d = W.replay(calls, ON, inject=[LIB], use_own_tissue=False, label="after_default")
    g_before_d = W.grade_arm(calls, v_before_d, rulers)
    g_after_d = W.grade_arm(calls, v_after_d, rulers)

    # the injection arm must equal the flipped arm once the whitelist is flipped (checked later, post-flip)
    equiv = {"checked": False, "note": "run m2_killswitch.py after the flip"}

    # ---- (a)/(b) on the two spec readings + the default route
    a_readings = {
        "A1_recorded_decls": consistent_falls(calls, g_before, g_after, "recorded declarations"),
        "A2_tester_decls": {
            "reading": "external tester re-declarations",
            "datasets_checked": len(runs["A2_tester_decls"]["per_dataset"]),
            "falls": {ds: {"before_pct": v["before"]["consistent"], "after_pct": v["after"]["consistent"],
                           "delta_pp": v["delta_pp"]["consistent"]}
                      for ds, v in runs["A2_tester_decls"]["per_dataset"].items()
                      if v["delta_pp"]["consistent"] < -1e-9},
            "n_falls": sum(1 for v in runs["A2_tester_decls"]["per_dataset"].values()
                           if v["delta_pp"]["consistent"] < -1e-9)},
        "A3_default_route": consistent_falls(calls, g_before_d, g_after_d, "default route (no tissue)"),
    }
    b_readings = {
        "A1_recorded_decls": inconsistent_reading(calls, g_before, g_after, "recorded declarations"),
        "A3_default_route": inconsistent_reading(calls, g_before_d, g_after_d, "default route (no tissue)"),
    }
    f2 = runs["A2_tester_decls"]
    b_readings["A2_tester_decls"] = {
        "reading": "external tester re-declarations",
        "overall_before_pct": f2["overall_before"]["share_pct"]["inconsistent"],
        "overall_after_pct": f2["overall_after"]["share_pct"]["inconsistent"],
        "overall_delta_pp": f2["overall_delta_pp"]["inconsistent"],
        "overall_rises": f2["overall_delta_pp"]["inconsistent"] > 0,
        "datasets_rising": {ds: {"before_pct": v["before"]["inconsistent"],
                                 "after_pct": v["after"]["inconsistent"],
                                 "delta_pp": v["delta_pp"]["inconsistent"]}
                            for ds, v in f2["per_dataset"].items()
                            if v["delta_pp"]["inconsistent"] > 0},
        "per_dataset_delta_pp": {ds: v["delta_pp"]["inconsistent"]
                                 for ds, v in f2["per_dataset"].items()
                                 if abs(v["delta_pp"]["inconsistent"]) > 1e-9},
        "consistent_before_pct": f2["overall_before"]["share_pct"]["consistent"],
        "consistent_after_pct": f2["overall_after"]["share_pct"]["consistent"],
        "mixed_before_pct": f2["overall_before"]["share_pct"]["mixed"],
        "mixed_after_pct": f2["overall_after"]["share_pct"]["mixed"]}
    # fill the per-dataset detail for A1 the same way the A2 row is built
    f1 = runs["A1_recorded_decls"]
    b_readings["A1_recorded_decls"]["datasets_rising"] = {
        ds: {"before_pct": v["before"]["inconsistent"], "after_pct": v["after"]["inconsistent"],
             "delta_pp": v["delta_pp"]["inconsistent"]}
        for ds, v in f1["per_dataset"].items() if v["delta_pp"]["inconsistent"] > 0}
    b_readings["A1_recorded_decls"]["per_dataset_delta_pp"] = {
        ds: v["delta_pp"]["inconsistent"] for ds, v in f1["per_dataset"].items()
        if abs(v["delta_pp"]["inconsistent"]) > 1e-9}

    # ---- (c) every moved cluster attributed, on the recorded-declaration arm
    moved = []
    for c in calls:
        k = (c["vol"], c["cluster"])
        b, a = v_before[k], v_after[k]
        if (b["top"], b["n_shared"], b["n_ranked"]) == (a["top"], a["n_shared"], a["n_ranked"]):
            continue
        top_changed = a["top"] != b["top"]
        adopted_top = won_by_the_library(a, classes)
        kind = ("adopted-name-gain" if (top_changed and adopted_top)
                else ("rank-shift" if not top_changed else "unexpected"))
        moved.append({"vol": c["vol"], "cluster": c["cluster"], "tissue": c["tissue"],
                      "n_cells": c["n_cells"], "ref_cell_type": c["ref_cell_type"],
                      "ref_family": c["ref_family"], "before_top": b["top"],
                      "before_n_shared": b["n_shared"], "before_n_ranked": b["n_ranked"],
                      "after_top": a["top"], "after_n_shared": a["n_shared"],
                      "after_n_ranked": a["n_ranked"], "after_library": a["library"],
                      "before_grade": g_before[k]["grade"], "after_grade": g_after[k]["grade"],
                      "before_cl": g_before[k]["cl"], "after_cl": g_after[k]["cl"], "kind": kind,
                      "truth_is_the_adopted_name": (c["ref_cell_type"].strip() in adopted_labels),
                      "grade_up": ORDER[g_after[k]["grade"]] > ORDER[g_before[k]["grade"]],
                      "grade_down": ORDER[g_after[k]["grade"]] < ORDER[g_before[k]["grade"]]})
    moved.sort(key=lambda r: -r["n_cells"])
    kinds = Counter(m["kind"] for m in moved)

    # ---- (d) the clause-(d) table: every adopted demand cluster, before/after and the truth label
    clause_d = []
    for c in calls:
        k = (c["vol"], c["cluster"])
        if c["ref_cell_type"].strip() not in adopted_labels:
            continue
        clause_d.append({"vol": c["vol"], "cluster": c["cluster"], "n_cells": c["n_cells"],
                         "truth_label": c["ref_cell_type"], "truth_family": c["ref_family"],
                         "adopted_name": c["ref_cell_type"].strip(),
                         "truth_is_exactly_the_adopted_name": True,
                         "before_top": v_before[k]["top"], "before_grade": g_before[k]["grade"],
                         "before_cl": g_before[k]["cl"], "before_n_shared": v_before[k]["n_shared"],
                         "after_top": v_after[k]["top"], "after_grade": g_after[k]["grade"],
                         "after_cl": g_after[k]["cl"], "after_n_shared": v_after[k]["n_shared"],
                         "moved": v_before[k]["top"] != v_after[k]["top"],
                         "answered_by_the_adoption": won_by_the_library(v_after[k], classes)})
    clause_d.sort(key=lambda r: -r["n_cells"])

    # ---- the ontology reading, overall and on the in-scope subset
    ontology = {
        "overall_before": cl_counts(g_before, keys), "overall_after": cl_counts(g_after, keys),
        "overall_before_pct": {k: round(100.0 * v / len(keys), 3)
                              for k, v in cl_counts(g_before, keys).items()},
        "overall_after_pct": {k: round(100.0 * v / len(keys), 3)
                             for k, v in cl_counts(g_after, keys).items()},
        "scope_subset_clusters": len(scope_keys),
        "scope_before": cl_counts(g_before, scope_keys), "scope_after": cl_counts(g_after, scope_keys),
        "note": ("this reads naming agreement against author labels, not recognition ability; an "
                 "ontology-consistent name is not evidence of a better call"),
    }
    # the frozen harness's own ancestor closure drops the qualified `is_a` edges (662 of them in this
    # release); the same reading under a closure that keeps them is reported beside it
    from ont_closure_probe import corrected_cl_counts  # noqa: E402  (local, declares the difference)
    ontology["scope_corrected_closure"] = {
        "before": corrected_cl_counts(calls, g_before, scope_keys),
        "after": corrected_cl_counts(calls, g_after, scope_keys)}

    doc = {
        "probe": "m1_measure.py", "card": "t_fabddb85", "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "library": LIB, "switch": SWITCH,
        "harness": {"dir": NRE, "wave_common_sha256": W.sha256_file(os.path.join(NRE, "wave_common.py")),
                    "n3_harness_sha256": W.sha256_file(os.path.join(NRE, "n3_harness.py")),
                    "switch_hygiene_declared_extension": declared_extension,
                    "note": "the harness's switch tuple predates EYEKB_ACT_CL56; it is extended with that "
                            "one name here and the extension is declared"},
        "recorded_set": {"clusters": len(calls), "cells": sum(c["n_cells"] for c in calls),
                         "volumes": len({c["vol"] for c in calls})},
        "ruler_selfcheck": selfcheck,
        "increment": {"file": INC_FILE, "sha256": W.sha256_file(INC_FILE),
                      "class_names": sorted(classes)},
        "readings": {"a_consistent_falls": a_readings, "b_inconsistent_rises": b_readings},
        "moved": moved, "moved_kinds": dict(kinds),
        "moved_unexpected": [m for m in moved if m["kind"] == "unexpected"],
        "clause_d": clause_d,
        "clause_d_violations": [r for r in clause_d if not r["truth_is_exactly_the_adopted_name"]],
        "ontology": ontology,
        "harness_reports": {t: os.path.join(OUT, "harness", t, "REPORT.json") for t in runs},
        "elapsed_s": round(time.time() - t0, 1),
        "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1),
    }
    with open(os.path.join(OUT, "MEASURE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    print("\n== moved: %d clusters / %d cells  kinds=%s" % (len(moved),
          sum(m["n_cells"] for m in moved), dict(kinds)))
    print("== clause(d): %d adopted demand clusters, violations=%d"
          % (len(clause_d), len(doc["clause_d_violations"])))
    print("== ontology (whole recording, clusters): before=%s after=%s"
          % (ontology["overall_before"], ontology["overall_after"]))
    print("== ontology (scope subset): before=%s after=%s"
          % (ontology["scope_before"], ontology["scope_after"]))
    print("== peak RSS %.1f MB, %.1fs" % (doc["peak_rss_mb"], doc["elapsed_s"]))
    print("wrote out/MEASURE.json")


if __name__ == "__main__":
    main()