#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n5 -- measure the carrier fix on the recorded 28-volume / 721-cluster set (PREREG G4).

Four runs, all through the regression harness (n3_harness.py), so every reading carries the same
pre-image and the same ruler as the gate:

  R1  exclusion-table narrowing, recorded declarations        == the shipped state vs the OFF state
  R2  carrier fix ON (merge `onfibro_v13`), recorded declarations
  R3  carrier fix ON, the declarations the external tester finally used
  R4  narrowing + carrier fix together, the tester's final declarations

Readings are IN-SAMPLE: the carrier was selected on the same volumes it is measured on. No accuracy
claim is made; this is a harm-line reading plus the recovery of one measured drop.

Writes out/FIX_MEASUREMENT.json and out/FIX_MEASUREMENT.md.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import n3_harness as H  # noqa: E402
import wave_common as W  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
LIB = "onfibro_v13"
FINAL_DECLS = {"CX16_tabula_sapiens_eye": "ocular_surface",
               "CX11_posterior_eye_atlas": "ocular_surface"}

SPECS = [
    {"key": "R1_narrowing_recorded_decls",
     "spec": {"name": "R1 exclusion-table narrowing (scope ON vs OFF), recorded declarations",
              "declared_change": "the tissue-scope candidate narrowing, as shipped",
              "before": {"env": {"EYEKB_TISSUE_SCOPE": "0"}},
              "after": {"env": {"EYEKB_TISSUE_SCOPE": "1"}}}},
    {"key": "R2_fix_recorded_decls",
     "spec": {"name": "R2 carrier fix ON (`%s` merged), recorded declarations" % LIB,
              "declared_change": "merge the registered-but-OFF optic-nerve fibroblast carrier",
              "before": {"env": {"EYEKB_TISSUE_SCOPE": "1"}},
              "after": {"env": {"EYEKB_TISSUE_SCOPE": "1"}, "inject": [LIB]}}},
    {"key": "R3_fix_tester_decls",
     "spec": {"name": "R3 carrier fix ON, the declarations the external tester finally used",
              "declared_change": "merge the carrier, with CX16 and CX11 re-declared ocular_surface",
              "tissue_declarations": FINAL_DECLS,
              "before": {"env": {"EYEKB_TISSUE_SCOPE": "1"}},
              "after": {"env": {"EYEKB_TISSUE_SCOPE": "1"}, "inject": [LIB]}}},
    {"key": "R4_narrowing_plus_fix_tester_decls",
     "spec": {"name": "R4 narrowing + carrier fix, the tester's final declarations",
              "declared_change": "the narrowing with the carrier available",
              "tissue_declarations": FINAL_DECLS,
              "before": {"env": {"EYEKB_TISSUE_SCOPE": "0"}},
              "after": {"env": {"EYEKB_TISSUE_SCOPE": "1"}, "inject": [LIB]}}},
]

TARGET = ("CX15_optic_nerve_all", "31")


def main():
    calls = W.load_set()
    rulers = W.Rulers(calls)
    doc = {"probe": "n5_measure_fix.py", "library": LIB, "runs": {}}
    md = ["# Carrier fix -- before/after on the recorded 28 volumes x 721 clusters", "",
          "Every row below comes from a regression-harness run (n3_harness.py); the harness's "
          "pre-image is stored in each run directory.", ""]

    for item in SPECS:
        key = item["key"]
        outdir = os.path.join(OUT, "harness", key)
        print("[%s] running..." % key, flush=True)
        d = H.run_spec(item["spec"], calls, rulers, outdir)
        # the motivating cluster, read out explicitly
        k = TARGET
        hit = [c for c in calls if (c["vol"], c["cluster"]) == k][0]
        tcalls = H.overlays(item["spec"], calls)
        b = W.replay(tcalls, item["spec"]["before"].get("env"),
                     inject=item["spec"]["before"].get("inject"), use_own_tissue=True, label="t_b")
        a = W.replay(tcalls, item["spec"]["after"].get("env"),
                     inject=item["spec"]["after"].get("inject"), use_own_tissue=True, label="t_a")
        doc["runs"][key] = {
            "name": item["spec"]["name"],
            "outdir": os.path.relpath(outdir, os.path.abspath(os.path.join(HERE, ".."))),
            "ruling": d["ruling"],
            "overall_before": d["overall_before"], "overall_after": d["overall_after"],
            "overall_delta_pp": d["overall_delta_pp"],
            "changed_clusters": d["changed_clusters"], "changed_cells": d["changed_cells"],
            "per_dataset_delta_consistent_pp": {ds: v["delta_pp"]["consistent"]
                                                for ds, v in d["per_dataset"].items()},
            "motivating_cluster": {
                "vol": k[0], "cluster": k[1], "n_cells": hit["n_cells"],
                "ref_cell_type": hit["ref_cell_type"], "ref_family": hit["ref_family"],
                "before_top": b[k]["top"], "before_n_shared": b[k]["n_shared"],
                "before_excluded": b[k]["excluded"],
                "after_top": a[k]["top"], "after_n_shared": a[k]["n_shared"],
                "after_library": a[k]["library"],
                "after_grade": rulers.grade(a[k]["top"], hit["ref_family"],
                                            hit["ref_cell_type"]),
                "before_grade": rulers.grade(b[k]["top"], hit["ref_family"],
                                            hit["ref_cell_type"]),
            },
        }
        r = doc["runs"][key]
        print("   verdict=%s changed=%d/%d cells  CX15/c31: %s(%s) -> %s(%s) [%s -> %s]"
              % (r["ruling"]["verdict"], r["changed_clusters"], r["changed_cells"],
                 r["motivating_cluster"]["before_top"], r["motivating_cluster"]["before_n_shared"],
                 r["motivating_cluster"]["after_top"], r["motivating_cluster"]["after_n_shared"],
                 r["motivating_cluster"]["before_grade"], r["motivating_cluster"]["after_grade"]),
              flush=True)

    # ---- G4 judgement -------------------------------------------------------------------
    r2 = doc["runs"]["R2_fix_recorded_decls"]
    r3 = doc["runs"]["R3_fix_tester_decls"]
    falls2 = {k: v for k, v in r2["per_dataset_delta_consistent_pp"].items() if v < -1e-9}
    falls3 = {k: v for k, v in r3["per_dataset_delta_consistent_pp"].items() if v < -1e-9}
    g4 = {
        "a_motivating_cluster_answered_family_consistently":
            r2["motivating_cluster"]["after_grade"] in ("consistent", "related"),
        "b_no_dataset_consistent_share_falls_recorded_decls": not falls2,
        "b_no_dataset_consistent_share_falls_tester_decls": not falls3,
        "falls_recorded_decls": falls2, "falls_tester_decls": falls3,
        "c_every_changed_cluster_listed": all(
            os.path.exists(os.path.join(OUT, "harness", k, "REPORT.json"))
            for k in ("R2_fix_recorded_decls", "R3_fix_tester_decls")),
        "net_overall_delta_pp_recorded_decls": r2["overall_delta_pp"]["consistent"],
        "net_overall_delta_pp_tester_decls": r3["overall_delta_pp"]["consistent"],
    }
    g4["verdict"] = ("PASS" if g4["a_motivating_cluster_answered_family_consistently"]
                     and g4["b_no_dataset_consistent_share_falls_recorded_decls"]
                     and g4["b_no_dataset_consistent_share_falls_tester_decls"]
                     and g4["c_every_changed_cluster_listed"] else "FAIL")
    doc["G4"] = g4

    W.save_json(os.path.join(OUT, "FIX_MEASUREMENT.json"), doc)

    md += ["## G4 verdict: **%s**" % g4["verdict"], "",
           "| run | changed clusters | changed cells | overall consistent before | after | delta pp | ruling |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for k, r in doc["runs"].items():
        md.append("| %s | %d | %d | %.3f | %.3f | %+.3f | %s |"
                  % (k, r["changed_clusters"], r["changed_cells"],
                     r["overall_before"]["share_pct"]["consistent"],
                     r["overall_after"]["share_pct"]["consistent"],
                     r["overall_delta_pp"]["consistent"], r["ruling"]["verdict"]))
    md += ["", "## The motivating cluster (CX15_optic_nerve_all cluster 31, 1,822 cells, "
               "truth `fibroblast`)", "",
           "| run | before top-1 | n_shared | after top-1 | n_shared | grade |",
           "|---|---|---:|---|---:|---|"]
    for k, r in doc["runs"].items():
        m = r["motivating_cluster"]
        md.append("| %s | %s | %s | %s | %s | %s -> %s |"
                  % (k, m["before_top"], m["before_n_shared"], m["after_top"],
                     m["after_n_shared"], m["before_grade"], m["after_grade"]))
    md += ["", "## Per-dataset consistent-share deltas (pp), the fix runs", ""]
    for k in ("R2_fix_recorded_decls", "R3_fix_tester_decls"):
        md.append("### %s" % k)
        md.append("")
        md.append("| dataset | delta pp |")
        md.append("|---|---:|")
        for ds, v in sorted(doc["runs"][k]["per_dataset_delta_consistent_pp"].items(),
                            key=lambda kv: kv[1]):
            if abs(v) > 1e-9:
                md.append("| %s | %+.3f |" % (ds, v))
        md.append("")
    with open(os.path.join(OUT, "FIX_MEASUREMENT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("G4 verdict:", g4["verdict"])
    print("wrote", os.path.join(OUT, "FIX_MEASUREMENT.json"))
    sys.exit(0 if g4["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()