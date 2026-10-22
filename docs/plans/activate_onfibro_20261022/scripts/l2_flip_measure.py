#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l2 -- measure the flip with the predecessor wave's harness (the instrument is reused, not
re-implemented).

What is reused, byte-for-byte: `docs/plans/noregr_20261022/scripts/n3_harness.py` and its
`wave_common.py` (rulers, replay engine, acceptance rule). One thing is ADDED and declared: the
harness's switch-hygiene tuple did not yet name `EYEKB_ACT_ONFIBRO` (it is the newest switch in the
service), so this script extends `wave_common.SWITCHES` with that one name -- otherwise an arm's
switch value could leak into the next arm. No rule, ruler, grade or threshold is changed.

Arms (all on the flipped core, in this process):
  F1  harness run: before = kill switch OFF, after = default (switch unset/ON)  [recorded decls]
  F2  same, under the external tester's re-declarations                        [tester decls]
  F3  control: before = OFF, after = the predecessor wave's measurement-only `inject:onfibro_v13`
Cross-checks written into the artefact:
  * the flipped default reproduces the injection arm cluster by cluster (721/721 identical rankings);
  * the kill-switch arm reproduces the predecessor wave's R2 *before* arm exactly (same overall
    grades) -- i.e. the pre-flip state has not drifted since that wave;
  * every moved cluster is classified `carrier-gain` / `rank-shift` / `unexpected` with its truth
    label and its before/after answer; `unexpected` is never absorbed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
L6 = os.path.join(REPO, "docs", "plans", "noregr_20261022")
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, os.path.join(L6, "scripts"))
import wave_common as W          # noqa: E402  (the predecessor wave's engine, reused)
import n3_harness as H           # noqa: E402  (the predecessor wave's harness, reused)

TESTER_DECLS = {"CX16_tabula_sapiens_eye": "ocular_surface",
                "CX11_posterior_eye_atlas": "ocular_surface"}
OFF = {"EYEKB_ACT_ONFIBRO": "0"}
ON = {"EYEKB_ACT_ONFIBRO": "1"}


def main():
    # one declared extension: the newest switch is named in the harness's hygiene tuple
    declared_extension = None
    if "EYEKB_ACT_ONFIBRO" not in W.SWITCHES:
        declared_extension = list(W.SWITCHES)
        W.SWITCHES = tuple(W.SWITCHES) + ("EYEKB_ACT_ONFIBRO",)

    calls = W.load_set()
    rulers = W.Rulers(calls)
    selfcheck = rulers.ruler_selfcheck(calls)

    specs = [
        ("F1_flip_recorded_decls", {
            "name": "F1 activation of onfibro_v13 on the default route (recorded declarations)",
            "declared_change": "ONFIBRO_DEFAULT_LIBS gains onfibro_v13: the carrier becomes part of "
                               "the default `all` route when EYEKB_ACT_ONFIBRO is unset/on",
            "before": {"env": OFF}, "after": {"env": ON}}),
        ("F2_flip_tester_decls", {
            "name": "F2 same flip under the external tester's re-declarations",
            "declared_change": "as F1, with CX16 and CX11 re-pointed to ocular_surface",
            "tissue_declarations": TESTER_DECLS,
            "before": {"env": OFF}, "after": {"env": ON}}),
        ("F3_control_inject_recorded_decls", {
            "name": "F3 control: the predecessor wave's measurement-only injection arm",
            "declared_change": "measurement-only: the OFF core with onfibro_v13 injected into `all` "
                               "(this is predecessor wave arm R2, re-run on today's code)",
            "before": {"env": OFF}, "after": {"env": OFF, "inject": ["onfibro_v13"]}}),
    ]
    runs = {}
    for tag, spec in specs:
        d = H.run_spec(spec, calls, rulers, os.path.join(OUT, "harness", tag))
        runs[tag] = d
        print("   %-34s verdict=%-16s changed_clusters=%d changed_cells=%d overall %+.3fpp"
              % (tag, d["ruling"]["verdict"], d["changed_clusters"], d["changed_cells"],
                 d["overall_delta_pp"]["consistent"]))

    # ---- arm views (full rankings, for the cross-checks and the per-cluster classification)
    v_kill = W.replay(calls, OFF, label="kill")
    v_flip = W.replay(calls, ON, label="flip")
    v_inject = W.replay(calls, OFF, inject=["onfibro_v13"], label="inject")
    g_kill = W.grade_arm(calls, v_kill, rulers)
    g_flip = W.grade_arm(calls, v_flip, rulers)

    keys = [(c["vol"], c["cluster"]) for c in calls]
    ident = [k for k in keys
             if (v_flip[k]["top"], v_flip[k]["n_shared"], v_flip[k]["n_ranked"], v_flip[k]["library"])
             == (v_inject[k]["top"], v_inject[k]["n_shared"], v_inject[k]["n_ranked"],
                 v_inject[k]["library"])]
    equivalence = {"clusters": len(keys), "identical": len(ident),
                   "differing": [[k[0], k[1]] for k in keys if k not in set(ident)][:20]}

    # ---- cross-wave identity: the kill-switch arm must reproduce the predecessor R2 before-arm
    r2 = json.load(open(os.path.join(L6, "out", "harness", "R2_fix_recorded_decls", "REPORT.json")))
    r3 = json.load(open(os.path.join(L6, "out", "harness", "R3_fix_tester_decls", "REPORT.json")))
    overall_kill = W.shares([g_kill[k] for k in g_kill])
    overall_flip = W.shares([g_flip[k] for k in g_flip])
    cross_wave = {
        "kill_arm_overall_vs_predecessor_R2_before": {
            "this_card": overall_kill["share_pct"], "predecessor_R2_before": r2["overall_before"]["share_pct"],
            "identical": overall_kill["share_pct"] == r2["overall_before"]["share_pct"]},
        "f1_after_vs_predecessor_R2_after": {
            "this_card": runs["F1_flip_recorded_decls"]["overall_after"]["share_pct"],
            "predecessor_R2_after": r2["overall_after"]["share_pct"],
            "identical": (runs["F1_flip_recorded_decls"]["overall_after"]["share_pct"]
                          == r2["overall_after"]["share_pct"])},
        "f2_after_vs_predecessor_R3_after": {
            "this_card": runs["F2_flip_tester_decls"]["overall_after"]["share_pct"],
            "predecessor_R3_after": r3["overall_after"]["share_pct"],
            "identical": (runs["F2_flip_tester_decls"]["overall_after"]["share_pct"]
                          == r3["overall_after"]["share_pct"])},
    }

    # ---- classification of every moved cluster (A2).  The three pre-registered kinds are decided by
    # the pre-specified reading "which entry won, and did the carrier appear in the candidate list?":
    #   carrier-gain  the carrier entry is the after top-1 (the coarse family answer now wins)
    #   rank-shift    the after top-1 is unchanged; only the candidate list moved
    #   unexpected    the after top-1 changed to something that is NOT the carrier entry
    # `unexpected` is never absorbed.  Inside the carrier-gain set the truth side is reported
    # separately: the intended repair is a cluster whose reference family is `fibro`; a carrier
    # takeover on a cluster of another family is listed explicitly as a harm candidate.
    CARRIER_LIB_BASENAME = "markers_v13_onfibro_increment.json"
    CARRIER_TOP_PREFIX = "onfibro_v13::"

    def carrier_in_view(v):
        for t in (v.get("top3") or []):
            if str(t[2]) == CARRIER_LIB_BASENAME:
                return True
        return str(v.get("library") or "") == CARRIER_LIB_BASENAME

    moved = []
    for c in calls:
        k = (c["vol"], c["cluster"])
        b, a = v_kill[k], v_flip[k]
        if (b["top"], b["n_shared"], b["n_ranked"]) == (a["top"], a["n_shared"], a["n_ranked"]):
            continue
        top_changed = a["top"] != b["top"]
        carrier_top = str(a["top"] or "").startswith(CARRIER_TOP_PREFIX)
        if top_changed and carrier_top:
            kind = "carrier-gain"
        elif not top_changed:
            kind = "rank-shift"
        else:
            kind = "unexpected"
        moved.append({
            "vol": c["vol"], "cluster": c["cluster"], "tissue": c["tissue"],
            "n_cells": c["n_cells"], "ref_cell_type": c["ref_cell_type"],
            "ref_family": c["ref_family"], "truth": c["truth"]["recorded_pred_top1"],
            "before_top": b["top"], "before_n_shared": b["n_shared"],
            "after_top": a["top"], "after_n_shared": a["n_shared"], "after_library": a["library"],
            "carrier_in_after_candidates": carrier_in_view(a),
            "before_grade": g_kill[k]["grade"], "after_grade": g_flip[k]["grade"],
            "before_cl": g_kill[k]["cl"], "after_cl": g_flip[k]["cl"], "kind": kind,
            "intended_repair": bool(kind == "carrier-gain" and c["ref_family"] == "fibro"),
            "takeover_on_other_family": bool(kind == "carrier-gain" and c["ref_family"] != "fibro")})
    moved.sort(key=lambda r: -r["n_cells"])
    kinds = {}
    for m in moved:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    takeovers = [m for m in moved if m["takeover_on_other_family"]]
    unexpected = [m for m in moved if m["kind"] == "unexpected"]

    # ---- the same reading on the DEFAULT route (no tissue argument), because the flip's surface is
    # the default route: the harness's own arms carry the recorded declarations, this one does not.
    ORDER = {"consistent": 3, "related": 2, "inconsistent": 1, "mixed": 0}
    v_kill_d = W.replay(calls, OFF, use_own_tissue=False, label="kill_default")
    v_flip_d = W.replay(calls, ON, use_own_tissue=False, label="flip_default")
    g_kill_d = W.grade_arm(calls, v_kill_d, rulers)
    g_flip_d = W.grade_arm(calls, v_flip_d, rulers)
    ds_kd, ds_fd = W.by_dataset(calls, g_kill_d), W.by_dataset(calls, g_flip_d)
    verdict_default, ruling_default = W.judge(ds_kd, ds_fd, {}, {})
    trans_default = W.transition_matrix(calls, g_kill_d, g_flip_d)
    harm_default = sum(v for k, v in trans_default["cells"].items()
                       if ORDER[k.split("->")[1]] < ORDER[k.split("->")[0]])
    default_route = {
        "route": "default (no `tissue` argument) -- the surface the flip changes",
        "overall_before": W.shares([g_kill_d[k] for k in g_kill_d]),
        "overall_after": W.shares([g_flip_d[k] for k in g_flip_d]),
        "verdict": verdict_default, "ruling": ruling_default,
        "transition_matrix_cells": trans_default["cells"],
        "harm_cells": harm_default,
        "per_dataset": {ds: {"before": ds_kd[ds]["share_pct"]["consistent"],
                             "after": ds_fd[ds]["share_pct"]["consistent"],
                             "delta_pp": round(ds_fd[ds]["share_pct"]["consistent"]
                                               - ds_kd[ds]["share_pct"]["consistent"], 3)}
                        for ds in sorted(ds_kd)},
        "clusters_top1_changed": sum(1 for k in g_kill_d
                                     if g_kill_d[k]["top"] != g_flip_d[k]["top"]),
        "note": ("this arm answers whether the activation lowers any dataset's consistent share on "
                 "the surface it actually changes, not only on the declared-tissue surface the "
                 "harness's overlay builds"),
    }

    # ---- card-level acceptance ruling (A1: no dataset falls, under EITHER declaration set)
    f1v = runs["F1_flip_recorded_decls"]["ruling"]["verdict"]
    f2v = runs["F2_flip_tester_decls"]["ruling"]["verdict"]
    expect_f1 = r2["overall_delta_pp"]["consistent"]
    got_f1 = runs["F1_flip_recorded_decls"]["overall_delta_pp"]["consistent"]
    expect_f2 = r3["overall_delta_pp"]["consistent"]
    got_f2 = runs["F2_flip_tester_decls"]["overall_delta_pp"]["consistent"]
    acceptance = {
        "rule": "A1 (pre-registered): no dataset's cell-weighted `consistent` share may fall, under "
                "either declaration set; for an ACTIVATION the predecessor's PASS_ATTRIBUTED is not "
                "sufficient -- the verdict must be PASS.",
        "F1_verdict": f1v, "F2_verdict": f2v,
        "F3_control_verdict": runs["F3_control_inject_recorded_decls"]["ruling"]["verdict"],
        "default_route_verdict": verdict_default,
        "default_route_datasets_falling": sorted((ruling_default.get("drops") or {}).keys()),
        "verdict": "PASS" if (f1v == "PASS" and f2v == "PASS" and verdict_default == "PASS")
                   else "FAIL",
        "datasets_falling": sorted(set(list(runs["F1_flip_recorded_decls"]["ruling"].get("drops") or {})
                                       + list(runs["F2_flip_tester_decls"]["ruling"].get("drops") or {}))),
    }

    # ---- harm cells (the negative column, reported whether or not the acceptance rule trips)
    ORDER = {"consistent": 3, "related": 2, "inconsistent": 1, "mixed": 0}
    harm_cells = sum(v for k, v in runs["F1_flip_recorded_decls"]
                     ["transition_matrix_cells"].items()
                     if ORDER[k.split("->")[1]] < ORDER[k.split("->")[0]])

    doc = {
        "probe": "l2_flip_measure.py",
        "instrument": {
            "harness": "docs/plans/noregr_20261022/scripts/n3_harness.py (reused unchanged)",
            "engine": "docs/plans/noregr_20261022/scripts/wave_common.py (reused unchanged)",
            "harness_preimage": runs["F1_flip_recorded_decls"]["harness_preimage"],
            "declared_extension": {
                "what": "wave_common.SWITCHES extended with EYEKB_ACT_ONFIBRO",
                "why": "the newest service switch was not named in the hygiene tuple, so an arm's "
                       "value could leak into the next arm; only the tuple grew, no rule changed",
                "switches_before": declared_extension,
                "switches_after": list(W.SWITCHES),
            },
        },
        "recorded_set": {"clusters": len(calls), "volumes": len({c["vol"] for c in calls}),
                         "cells": sum(c["n_cells"] for c in calls)},
        "ruler_selfcheck": selfcheck,
        "arms": {tag: {"before_arm": runs[tag]["before_arm"], "after_arm": runs[tag]["after_arm"],
                       "tissue_declarations": runs[tag]["tissue_declarations_overlay"],
                       "verdict": runs[tag]["ruling"]["verdict"],
                       "overall_before": runs[tag]["overall_before"],
                       "overall_after": runs[tag]["overall_after"],
                       "overall_delta_pp": runs[tag]["overall_delta_pp"],
                       "per_dataset": runs[tag]["per_dataset"],
                       "changed_clusters": runs[tag]["changed_clusters"],
                       "changed_cells": runs[tag]["changed_cells"],
                       "transition_matrix_cells": runs[tag]["transition_matrix_cells"],
                       "ruling": runs[tag]["ruling"]}
                for tag in runs},
        "equivalence_flip_vs_inject": equivalence,
        "cross_wave_identity": cross_wave,
        "default_route_reading": default_route,
        "moved_clusters": moved,
        "moved_kinds": kinds,
        "takeovers_on_other_family": takeovers,
        "unexpected_clusters": unexpected,
        "harm_cells": harm_cells,
        "harm_cells_note": ("cells whose grade moved DOWN (consistent* away, related* down, "
                            "inconsistent->mixed), cell-weighted, under the recorded declarations. "
                            "The acceptance rule that decides this card is A1 (no dataset's "
                            "consistent share falls); this column is reported whether or not it "
                            "trips, and it is never omitted."),
        "motivating_cluster": next(m for m in moved
                                   if m["vol"] == "CX15_optic_nerve_all" and m["cluster"] == "31"),
        "expectation_vs_measurement": {
            "pre_registered_F1_delta_pp": expect_f1, "measured_F1_delta_pp": got_f1,
            "pre_registered_F2_delta_pp": expect_f2, "measured_F2_delta_pp": got_f2,
            "pre_registered_moved_clusters": r2["changed_clusters"], "measured": len(moved),
            "matches": (expect_f1 == got_f1 and expect_f2 == got_f2
                        and len(moved) == r2["changed_clusters"]),
        },
        "acceptance": acceptance,
        "in_sample_disclosure": (
            "IN-SAMPLE READING: the carrier was selected on the same volumes it is measured on, so "
            "this is a harm-line/regression reading of one measured drop and its repair. It is NOT a "
            "validation, NOT an independent test and NOT an accuracy claim; the carrier is a "
            "family-level (coarse) answer that clears the >=2 shared-gene bar only at the bar."),
        "verdict": "PASS" if (acceptance["verdict"] == "PASS" and equivalence["identical"] == equivalence["clusters"]
                              and kinds.get("unexpected", 0) == 0) else "FAIL",
    }
    with open(os.path.join(OUT, "FLIP_MEASUREMENT.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print("   ruler self-check: agree=%d differ=%d" % (selfcheck["agree"], selfcheck["differ"]))
    print("   flipped default == injection arm on %d/%d clusters"
          % (equivalence["identical"], equivalence["clusters"]))
    print("   kill arm == predecessor R2 before-arm:",
          cross_wave["kill_arm_overall_vs_predecessor_R2_before"]["identical"])
    print("   moved clusters: %d  kinds=%s  takeovers-on-other-family=%d  harm_cells=%d"
          % (len(moved), kinds, len(takeovers), harm_cells))
    print("   motivating cluster:", json.dumps(doc["motivating_cluster"], ensure_ascii=False))
    print("   acceptance:", acceptance["verdict"], "datasets_falling=%s" % acceptance["datasets_falling"])
    print("   default route (no tissue): verdict=%s overall %+.3fpp  top1-changed clusters=%d  "
          "harm_cells=%d" % (verdict_default,
                             default_route["overall_after"]["share_pct"]["consistent"]
                             - default_route["overall_before"]["share_pct"]["consistent"],
                             default_route["clusters_top1_changed"], harm_default))
    print("   l2 verdict:", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())