#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l2 -- measure the flip with the predecessor wave's harness (the instrument is reused, not
re-implemented).

What is reused, byte-for-byte: `docs/plans/noregr_20261022/scripts/n3_harness.py` and its
`wave_common.py` (rulers, replay engine, acceptance rule). One thing is ADDED and declared: the
harness's switch-hygiene tuple did not yet name `EYEKB_ACT_HOLEFILL` (it is the newest switch in the
service), so this script extends `wave_common.SWITCHES` with that one name -- otherwise an arm's
switch value could leak into the next arm. No rule, ruler, grade or threshold is changed.

Arms (all on the flipped core, in this process):
  F1  harness run: before = kill switch OFF, after = default (switch unset/ON)   [recorded decls]
  F2  same, under the external tester's re-declarations                          [tester decls]
  F3  control: before = OFF, after = the predecessor wave's measurement-only `inject:holefill_v12`
  D   the DEFAULT route itself (no `tissue` argument), OFF vs ON -- the surface a default-route flip
      actually changes, which the harness's own arms cannot build (they carry the recorded tissue)
Cross-checks written into the artefact:
  * the flipped default reproduces the measurement-only injection arm cluster by cluster;
  * every moved cluster is classified `library-gain` / `rank-shift` / `unexpected` with its truth
    label and its before/after answer; `unexpected` is never absorbed;
  * the four pre-registered target directions are re-read on the shipped code and compared with the
    predecessor wave's own MERGED-arm numbers, which are read from its `out/wave_measurement.json`.

The card's acceptance rule (PREREG section 4) has four clauses; this script judges (a), (b) and (c),
and `l3` judges (d):
  (a) no dataset's cell-weighted `consistent` share falls -- PASS required, PASS_ATTRIBUTED is not
      sufficient for an activation;
  (b) the aggregate cell-weighted `inconsistent` share must not rise (overall, and on no dataset);
  (c) every moved cluster is attributed, with zero `unexpected`.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
L6 = os.path.join(REPO, "docs", "plans", "noregr_20261022")
HOLEFILL_WAVE = "/mnt/D/EyeKB/plans/holefill_v12_20261021"
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, os.path.join(L6, "scripts"))
import wave_common as W          # noqa: E402  (the predecessor wave's engine, reused)
import n3_harness as H           # noqa: E402  (the predecessor wave's harness, reused)

TESTER_DECLS = {"CX16_tabula_sapiens_eye": "ocular_surface",
                "CX11_posterior_eye_atlas": "ocular_surface"}
OFF = {"EYEKB_ACT_HOLEFILL": "0"}
ON = {"EYEKB_ACT_HOLEFILL": "1"}
LIB = "holefill_v12"
LIB_BASENAME = "markers_v12_holefill_increment.json"
LIB_TOP_PREFIX = "holefill_v12::"
SWITCH = "EYEKB_ACT_HOLEFILL"
ORDER = {"consistent": 3, "related": 2, "inconsistent": 1, "mixed": 0}
TARGETS = {"endothelial cell": "CL:0000115", "macrophage": "CL:0000235",
           "retinal rod cell": "CL:0000604", "retinal pigment epithelial cell": "CL:0002586"}


def lib_in_view(v):
    return (str(v.get("library") or "") == LIB_BASENAME
            or any(str(t[2]) == LIB_BASENAME for t in (v.get("top3") or [])))


_LIB_CLASSES = None


def lib_classes():
    """The library's own class names, read from the file under activation (I4).

    Needed because the library's entries are presented under the Cell Ontology label with NO
    `holefill_v12::` prefix: their names do not collide with any shipped class, so the loader emits
    them as ordinary canonical classes. An earlier version of this classifier keyed on that prefix and
    therefore mislabelled 90 library takeovers as `unexpected` -- a diagnostic run
    (`diag_top1_moves.py`) caught it before the ruling was written.
    """
    global _LIB_CLASSES
    if _LIB_CLASSES is None:
        inc = json.load(open(os.path.join(REPO, "kb", "markers",
                                          "markers_v12_holefill_increment.json")))
        _LIB_CLASSES = {str(k).casefold() for k in (inc.get("markers") or {})}
    return _LIB_CLASSES


def won_by_the_library(view):
    if str(view.get("library") or "") == LIB_BASENAME:
        return True
    top = str(view.get("top") or "")
    if top.startswith(LIB_TOP_PREFIX):
        return True
    return top.split("::")[-1].strip().casefold() in lib_classes()


def exact_at_cl(rulers, top, ref_cell_type, cl_id):
    """same_cl at the given ontology term: the answer resolves to this CL id and so does the truth."""
    return rulers.cl_of_pred(top) == cl_id and rulers.cl_of_truth(ref_cell_type) == cl_id


def inconsistent_reading(calls, g_before, g_after, label):
    """Clause (b): the aggregate cell-weighted `inconsistent` share must not rise."""
    ob = W.shares([g_before[k] for k in g_before])
    oa = W.shares([g_after[k] for k in g_after])
    ds_b, ds_a = W.by_dataset(calls, g_before), W.by_dataset(calls, g_after)
    per_ds = {}
    for ds in sorted(ds_b):
        b = ds_b[ds]["share_pct"]["inconsistent"]
        a = ds_a[ds]["share_pct"]["inconsistent"]
        if abs(a - b) > 1e-9:
            per_ds[ds] = {"before_pct": b, "after_pct": a, "delta_pp": round(a - b, 3)}
    delta = round(oa["share_pct"]["inconsistent"] - ob["share_pct"]["inconsistent"], 3)
    return {"reading": label,
            "overall_before_pct": ob["share_pct"]["inconsistent"],
            "overall_after_pct": oa["share_pct"]["inconsistent"],
            "overall_delta_pp": delta,
            "overall_rises": delta > 0,
            "datasets_rising": {k: v for k, v in per_ds.items() if v["before_pct"] < v["after_pct"]},
            "per_dataset_delta_pp": per_ds,
            "consistent_before_pct": ob["share_pct"]["consistent"],
            "consistent_after_pct": oa["share_pct"]["consistent"],
            "abstain_or_mixed_before_pct": ob["share_pct"]["mixed"],
            "abstain_or_mixed_after_pct": oa["share_pct"]["mixed"],
            "note": ("abstention falling is the intended effect of this library and is NOT a gain by "
                     "itself; the criterion is that the inconsistent share does not rise (L1 "
                     "precedent: abstention 23.25% -> 5.55% came with contradictions 17.95% -> "
                     "29.32% and was ruled NO-GO)")}


def target_readings(rulers, calls, g_before, g_after):
    out = {}
    for label, cl in TARGETS.items():
        keys = [(c["vol"], c["cluster"]) for c in calls if c["ref_cell_type"] == label]
        b = sum(1 for k in keys if exact_at_cl(rulers, g_before[k]["top"], label, cl))
        a = sum(1 for k in keys if exact_at_cl(rulers, g_after[k]["top"], label, cl))
        out[label] = {"cl_id": cl, "clusters": len(keys),
                      "cells": sum(next(c["n_cells"] for c in calls
                                        if (c["vol"], c["cluster"]) == k) for k in keys),
                      "exact_before": b, "exact_after": a,
                      "answers_after": {g_after[k]["top"]: sum(
                          1 for kk in keys if g_after[kk]["top"] == g_after[k]["top"])
                          for k in keys}}
    return out


def rod_shared_gene_reading(calls):
    """The rod panel's own pre-registered direction: clusters clearing the >= 2 shared-gene bar."""
    inc = json.load(open(os.path.join(REPO, "kb", "markers",
                                      "markers_v12_holefill_increment.json")))
    new_panel = {str(g).upper() for g in inc["markers"]["retinal rod cell"]}
    shipped = json.load(open(os.path.join(REPO, "kb", "markers", "markers_v4.1_clean.json")))
    old_panel = {str(g).upper() for g in (shipped["markers"].get("Rod") or [])}
    rod_keys = [c for c in calls if c["ref_cell_type"] == "retinal rod cell"]
    old_n = sum(1 for c in rod_keys
                if len({str(g).upper() for g in c["genes"]} & old_panel) >= 2)
    new_n = sum(1 for c in rod_keys
                if len({str(g).upper() for g in c["genes"]} & new_panel) >= 2)
    return {"panel_shipped_genes": len(old_panel), "panel_increment_genes": len(new_panel),
            "rod_truth_clusters": len(rod_keys),
            "clusters_clearing_bar_shipped": old_n, "clusters_clearing_bar_increment": new_n,
            "delta": new_n - old_n}


def predecessor_reference():
    p = os.path.join(HOLEFILL_WAVE, "out", "wave_measurement.json")
    d = json.load(open(p))
    rod = d.get("rod_depth") or []
    return {"file": p,
            "totals": {k: v for k, v in (d.get("totals") or {}).items()},
            "rod_depth": {"clusters": len(rod),
                          "old_shared_at_least_2": sum(1 for r in rod if (r.get("old_shared") or 0) >= 2),
                          "new_shared_at_least_2": sum(1 for r in rod if (r.get("new_shared") or 0) >= 2)},
            "target_class_diagnosis": d.get("target_class_diagnosis"),
            "note": ("the predecessor wave judged verdicts at Cell-Ontology level with its own four "
                     "arms; this card re-reads the same quantities through the no-regression harness "
                     "on the shipped default route, so the two are compared as directions, not as "
                     "identical instruments")}


def main():
    declared_extension = None
    if SWITCH not in W.SWITCHES:
        declared_extension = list(W.SWITCHES)
        W.SWITCHES = tuple(W.SWITCHES) + (SWITCH,)

    calls = W.load_set()
    rulers = W.Rulers(calls)
    selfcheck = rulers.ruler_selfcheck(calls)

    specs = [
        ("F1_flip_recorded_decls", {
            "name": "F1 activation of holefill_v12 on the default route (recorded declarations)",
            "declared_change": "a whitelist entry for holefill_v12 joins the default `all` route when "
                               "EYEKB_ACT_HOLEFILL is unset/on",
            "before": {"env": OFF}, "after": {"env": ON}}),
        ("F2_flip_tester_decls", {
            "name": "F2 same flip under the external tester's re-declarations",
            "declared_change": "as F1, with CX16 and CX11 re-pointed to ocular_surface",
            "tissue_declarations": TESTER_DECLS,
            "before": {"env": OFF}, "after": {"env": ON}}),
        ("F3_control_inject_recorded_decls", {
            "name": "F3 control: the measurement-only injection arm",
            "declared_change": "measurement-only: the OFF core with holefill_v12 injected into `all`",
            "before": {"env": OFF}, "after": {"env": OFF, "inject": [LIB]}}),
    ]
    runs = {}
    for tag, spec in specs:
        d = H.run_spec(spec, calls, rulers, os.path.join(OUT, "harness", tag))
        runs[tag] = d
        print("   %-34s verdict=%-16s changed_clusters=%d changed_cells=%d overall consistent %+.3fpp"
              % (tag, d["ruling"]["verdict"], d["changed_clusters"], d["changed_cells"],
                 d["overall_delta_pp"]["consistent"]))

    # ---- arm views (full rankings, for the cross-checks and the per-cluster classification)
    v_kill = W.replay(calls, OFF, label="kill")
    v_flip = W.replay(calls, ON, label="flip")
    v_inject = W.replay(calls, OFF, inject=[LIB], label="inject")
    g_kill = W.grade_arm(calls, v_kill, rulers)
    g_flip = W.grade_arm(calls, v_flip, rulers)

    keys = [(c["vol"], c["cluster"]) for c in calls]
    ident = [k for k in keys
             if (v_flip[k]["top"], v_flip[k]["n_shared"], v_flip[k]["n_ranked"], v_flip[k]["library"])
             == (v_inject[k]["top"], v_inject[k]["n_shared"], v_inject[k]["n_ranked"],
                 v_inject[k]["library"])]
    equivalence = {"clusters": len(keys), "identical": len(ident),
                   "differing": [[k[0], k[1]] for k in keys if k not in set(ident)][:20]}

    # ---- the DEFAULT route (no tissue argument): the surface the flip changes
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
        "transition_matrix_clusters": trans_default["clusters"],
        "harm_cells": harm_default,
        "per_dataset": {ds: {"before": ds_kd[ds]["share_pct"]["consistent"],
                             "after": ds_fd[ds]["share_pct"]["consistent"],
                             "delta_pp": round(ds_fd[ds]["share_pct"]["consistent"]
                                               - ds_kd[ds]["share_pct"]["consistent"], 3),
                             "inconsistent_before": ds_kd[ds]["share_pct"]["inconsistent"],
                             "inconsistent_after": ds_fd[ds]["share_pct"]["inconsistent"]}
                        for ds in sorted(ds_kd)},
        "clusters_top1_changed": sum(1 for k in g_kill_d
                                     if g_kill_d[k]["top"] != g_flip_d[k]["top"]),
    }

    # ---- (b) the aggregate inconsistent share, on all three readings
    inconsistent = {
        "F1_recorded_decls": inconsistent_reading(calls, g_kill, g_flip, "recorded declarations"),
        "D_default_route": inconsistent_reading(calls, g_kill_d, g_flip_d, "default route"),
    }
    # F2 runs under the tester overlay, so it is read from the harness's own tables
    f2 = runs["F2_flip_tester_decls"]
    inconsistent["F2_tester_decls"] = {
        "reading": "external tester re-declarations",
        "overall_before_pct": f2["overall_before"]["share_pct"]["inconsistent"],
        "overall_after_pct": f2["overall_after"]["share_pct"]["inconsistent"],
        "overall_delta_pp": round(f2["overall_after"]["share_pct"]["inconsistent"]
                                  - f2["overall_before"]["share_pct"]["inconsistent"], 3),
        "overall_rises": (f2["overall_after"]["share_pct"]["inconsistent"]
                          > f2["overall_before"]["share_pct"]["inconsistent"]),
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
        "abstain_or_mixed_before_pct": f2["overall_before"]["share_pct"]["mixed"],
        "abstain_or_mixed_after_pct": f2["overall_after"]["share_pct"]["mixed"],
        "note": inconsistent["F1_recorded_decls"]["note"]}
    # F1's table is read the same way for symmetry with F2
    f1 = runs["F1_flip_recorded_decls"]
    inconsistent["F1_recorded_decls"]["datasets_rising"] = {
        ds: {"before_pct": v["before"]["inconsistent"], "after_pct": v["after"]["inconsistent"],
             "delta_pp": v["delta_pp"]["inconsistent"]}
        for ds, v in f1["per_dataset"].items() if v["delta_pp"]["inconsistent"] > 0}
    inconsistent["F1_recorded_decls"]["per_dataset_delta_pp"] = {
        ds: v["delta_pp"]["inconsistent"] for ds, v in f1["per_dataset"].items()
        if abs(v["delta_pp"]["inconsistent"]) > 1e-9}
    b_ok = all(not v["overall_rises"] for v in inconsistent.values())

    # ---- (c) every moved cluster attributed
    moved = []
    for c in calls:
        k = (c["vol"], c["cluster"])
        b, a = v_kill[k], v_flip[k]
        if (b["top"], b["n_shared"], b["n_ranked"]) == (a["top"], a["n_shared"], a["n_ranked"]):
            continue
        top_changed = a["top"] != b["top"]
        lib_top = won_by_the_library(a)
        if top_changed and lib_top:
            kind = "library-gain"
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
            "lib_in_after_candidates": lib_in_view(a),
            "before_grade": g_kill[k]["grade"], "after_grade": g_flip[k]["grade"],
            "before_cl": g_kill[k]["cl"], "after_cl": g_flip[k]["cl"], "kind": kind,
            "gain_quality": (g_flip[k]["cl"] if kind == "library-gain" else None),
            "grade_up": ORDER[g_flip[k]["grade"]] > ORDER[g_kill[k]["grade"]],
            "grade_down": ORDER[g_flip[k]["grade"]] < ORDER[g_kill[k]["grade"]]})
    moved.sort(key=lambda r: -r["n_cells"])
    kinds = Counter(m["kind"] for m in moved)
    gains_by_quality = Counter(m["gain_quality"] for m in moved if m["kind"] == "library-gain")
    unexpected = [m for m in moved if m["kind"] == "unexpected"]
    grade_down = [m for m in moved if m["grade_down"]]
    grade_up = [m for m in moved if m["grade_up"]]

    harm_cells = sum(v for k, v in runs["F1_flip_recorded_decls"]["transition_matrix_cells"].items()
                     if ORDER[k.split("->")[1]] < ORDER[k.split("->")[0]])

    # ---- the acceptance ruling
    f1v = runs["F1_flip_recorded_decls"]["ruling"]["verdict"]
    f2v = runs["F2_flip_tester_decls"]["ruling"]["verdict"]
    f3v = runs["F3_control_inject_recorded_decls"]["ruling"]["verdict"]
    a_ok = (f1v == "PASS" and f2v == "PASS" and verdict_default == "PASS")
    c_ok = (len(unexpected) == 0 and equivalence["identical"] == equivalence["clusters"])
    acceptance = {
        "rule": ("PREREG section 4: GO requires (a) PASS on all three readings -- PASS_ATTRIBUTED is "
                 "not sufficient for an activation, (b) the aggregate `inconsistent` share rising on "
                 "no reading and on no dataset, (c) every moved cluster attributed with zero "
                 "`unexpected` and the flipped default equal to the injection arm, (d) the kill "
                 "switch restoring the pre-flip default byte-for-byte (judged by l3)"),
        "a_no_dataset_falls": {"F1": f1v, "F2": f2v, "D_default_route": verdict_default,
                               "F3_control": f3v, "ok": a_ok,
                               "datasets_falling": sorted(set(
                                   list(runs["F1_flip_recorded_decls"]["ruling"].get("drops") or {})
                                   + list(runs["F2_flip_tester_decls"]["ruling"].get("drops") or {})
                                   + list(ruling_default.get("drops") or {})))},
        "b_inconsistent_does_not_rise": {"ok": b_ok,
                                         "per_reading": {k: {"delta_pp": v["overall_delta_pp"],
                                                             "rises": v["overall_rises"],
                                                             "datasets_rising": sorted(
                                                                 v["datasets_rising"])}
                                                         for k, v in inconsistent.items()}},
        "c_attribution": {"ok": c_ok, "moved_clusters": len(moved), "kinds": dict(kinds),
                          "unexpected": len(unexpected),
                          "flip_equals_injection": "%d/%d" % (equivalence["identical"],
                                                              equivalence["clusters"])},
        "d_kill_switch": {"judged_by": "l3_default_face.py", "in_this_artefact": False},
    }
    acceptance["verdict"] = "GO" if (a_ok and b_ok and c_ok) else "NO-GO"

    doc = {
        "probe": "l2_flip_measure.py",
        "instrument": {
            "harness": "docs/plans/noregr_20261022/scripts/n3_harness.py (reused unchanged)",
            "engine": "docs/plans/noregr_20261022/scripts/wave_common.py (reused unchanged)",
            "harness_preimage": runs["F1_flip_recorded_decls"]["harness_preimage"],
            "declared_extension": {
                "what": "wave_common.SWITCHES extended with EYEKB_ACT_HOLEFILL",
                "why": "the newest service switch was not named in the hygiene tuple, so an arm's "
                       "value could leak into the next arm; only the tuple grew, no rule changed",
                "switches_before": declared_extension,
                "switches_after": list(W.SWITCHES)},
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
        "default_route_reading": default_route,
        "inconsistent_share_reading": inconsistent,
        "target_class_readings": target_readings(rulers, calls, g_kill, g_flip),
        "rod_shared_gene_reading": rod_shared_gene_reading(calls),
        "predecessor_reference": predecessor_reference(),
        "moved_clusters": moved,
        "moved_kinds": dict(kinds),
        "library_gains_by_cl_quality": dict(gains_by_quality),
        "library_gains_note": ("every takeover is graded against the author's own label for the "
                               "cluster, so a `truly_inconsistent` gain is a takeover on a cluster of "
                               "another class, not a repair"),
        "unexpected_clusters": unexpected,
        "clusters_graded_down": grade_down,
        "clusters_graded_up": grade_up,
        "harm_cells": harm_cells,
        "harm_cells_note": ("cells whose grade moved DOWN (consistent -> anything lower, related -> "
                            "lower, inconsistent -> mixed), cell-weighted, under the recorded "
                            "declarations; reported whether or not a criterion trips, never omitted"),
        "acceptance": acceptance,
        "in_sample_disclosure": (
            "IN-SAMPLE READING: the library was selected on the same 28 public volumes it is measured "
            "on, so this is a coverage/harm reading, not a validation, not an independent test and "
            "not an accuracy claim. It is measured at Cell-Ontology level against the author's "
            "per-cluster majority label; two of the library's 17 entries (classical / non-classical "
            "monocyte) already fail their own pre-registered coverage bar and are carried as FAIL in "
            "the library's own record."),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "FLIP_MEASUREMENT.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    write_markdown(doc)

    print("   ruler self-check: agree=%d differ=%d" % (selfcheck["agree"], selfcheck["differ"]))
    print("   flipped default == injection arm on %d/%d clusters"
          % (equivalence["identical"], equivalence["clusters"]))
    print("   moved clusters: %d  kinds=%s  unexpected=%d  harm_cells=%d  grade_down=%d"
          % (len(moved), dict(kinds), len(unexpected), harm_cells, len(grade_down)))
    for k, v in sorted(inconsistent.items()):
        print("   (b) %-18s inconsistent %.3f%% -> %.3f%% (%+.3fpp) rising=%s"
              % (k, v["overall_before_pct"], v["overall_after_pct"], v["overall_delta_pp"],
                 v["overall_rises"]))
    print("   (a) F1=%s F2=%s default=%s  -> ok=%s" % (f1v, f2v, verdict_default, a_ok))
    print("   (b) ok=%s" % b_ok)
    print("   (c) ok=%s  unexpected=%d" % (c_ok, len(unexpected)))
    print("   ACCEPTANCE (a,b,c):", acceptance["verdict"])
    return 0


def write_markdown(doc):
    L = []
    A = L.append
    A("# Flip measurement — `holefill_v12` on the default route (card t_be11fd4a)")
    A("")
    A("Instrument: `docs/plans/noregr_20261022/scripts/n3_harness.py` + `wave_common.py`, reused")
    A("unchanged; one declared extension (the switch name `EYEKB_ACT_HOLEFILL` joins the hygiene")
    A("tuple). Recorded set: %d clusters / %d cells / %d volumes."
      % (doc["recorded_set"]["clusters"], doc["recorded_set"]["cells"], doc["recorded_set"]["volumes"]))
    A("")
    A("## Acceptance (a/b/c measured here; d is `l3`)")
    A("")
    A("| clause | reading | result |")
    A("|---|---|---|")
    acc = doc["acceptance"]
    A("| (a) no dataset's consistent share falls | F1 %s / F2 %s / default %s | %s |"
      % (acc["a_no_dataset_falls"]["F1"], acc["a_no_dataset_falls"]["F2"],
         acc["a_no_dataset_falls"]["D_default_route"],
         "ok" if acc["a_no_dataset_falls"]["ok"] else "**FAIL**"))
    A("| (b) aggregate inconsistent share does not rise | %s | %s |"
      % ("; ".join("%s %+.3fpp" % (k, v["delta_pp"]) for k, v
                   in sorted(acc["b_inconsistent_does_not_rise"]["per_reading"].items())),
         "ok" if acc["b_inconsistent_does_not_rise"]["ok"] else "**FAIL**"))
    A("| (c) every move attributed | %d moved, kinds %s, unexpected %d | %s |"
      % (acc["c_attribution"]["moved_clusters"], acc["c_attribution"]["kinds"],
         acc["c_attribution"]["unexpected"], "ok" if acc["c_attribution"]["ok"] else "**FAIL**"))
    A("")
    A("**Verdict on (a)(b)(c): %s**" % acc["verdict"])
    A("")
    A("## Overall, cell-weighted (recorded declarations, F1)")
    A("")
    A("| grade | before % | after % | delta pp |")
    A("|---|---:|---:|---:|")
    for g in W.GRADES:
        A("| %s | %.3f | %.3f | %+.3f |" % (g, doc["arms"]["F1_flip_recorded_decls"]["overall_before"]["share_pct"][g],
                                            doc["arms"]["F1_flip_recorded_decls"]["overall_after"]["share_pct"][g],
                                            doc["arms"]["F1_flip_recorded_decls"]["overall_delta_pp"][g]))
    A("")
    A("## Default route (no tissue argument)")
    A("")
    A("| grade | before % | after % |")
    A("|---|---:|---:|")
    for g in W.GRADES:
        A("| %s | %.3f | %.3f |" % (g, doc["default_route_reading"]["overall_before"]["share_pct"][g],
                                    doc["default_route_reading"]["overall_after"]["share_pct"][g]))
    A("")
    A("Path changed clusters: %d. Harm cells: %d."
      % (doc["default_route_reading"]["clusters_top1_changed"], doc["default_route_reading"]["harm_cells"]))
    A("")
    A("## Target classes (pre-registered directions)")
    A("")
    A("| class | CL | clusters | exact before | exact after |")
    A("|---|---|---:|---:|---:|")
    for k, v in sorted(doc["target_class_readings"].items()):
        A("| %s | %s | %d | %d | %d |" % (k, v["cl_id"], v["clusters"], v["exact_before"],
                                          v["exact_after"]))
    rd = doc["rod_shared_gene_reading"]
    A("")
    A("Rod panel: shipped %d genes clear the >=2 shared-gene bar on %d of %d rod-truth clusters;"
      % (rd["panel_shipped_genes"], rd["clusters_clearing_bar_shipped"], rd["rod_truth_clusters"]))
    A("the increment's %d-gene panel clears it on %d (%+d)."
      % (rd["panel_increment_genes"], rd["clusters_clearing_bar_increment"], rd["delta"]))
    A("")
    A("## Moved clusters")
    A("")
    A("| volume | cluster | cells | truth | before | after | grade | kind |")
    A("|---|---|---:|---|---|---|---|---|")
    for m in doc["moved_clusters"][:60]:
        A("| %s | %s | %d | %s | %s (%s) | %s (%s) | %s -> %s | %s |"
          % (m["vol"], m["cluster"], m["n_cells"], m["ref_cell_type"], m["before_top"],
             m["before_n_shared"], m["after_top"], m["after_n_shared"], m["before_grade"],
             m["after_grade"], m["kind"]))
    if len(doc["moved_clusters"]) > 60:
        A("")
        A("(%d further moved clusters in `FLIP_MEASUREMENT.json`.)"
          % (len(doc["moved_clusters"]) - 60))
    A("")
    A("## In-sample disclosure")
    A("")
    A(doc["in_sample_disclosure"])
    A("")
    with open(os.path.join(OUT, "FLIP_MEASUREMENT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())