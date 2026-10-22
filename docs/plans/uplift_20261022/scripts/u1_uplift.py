#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""u1_uplift.py -- the recorded 28 volumes x 721 clusters, re-measured on the tree as it stands.

Why a separate runner rather than re-running the previous wave's n5
------------------------------------------------------------------
`docs/plans/noregr_20261022/scripts/n5_measure_fix.py` hard-codes its output
directory to that wave's own `out/`, which is a frozen, manifest-listed artefact
(49/49 sha256 lines). Re-running it in place overwrites measurements that a
delivered report already quotes. This runner imports the same harness
(`n3_harness.py`) and the same replay layer (`wave_common.py`) read-only, and
writes everything under its own directory.

What changed since the previous measurement, and why the old specs are degenerate
--------------------------------------------------------------------------------
The carrier library `onfibro_v13` is now in the DEFAULT route
(`mcp_server/eyekb_core.py`: `ONFIBRO_DEFAULT_LIBS = ("onfibro_v13",)`), with a
registered kill switch `EYEKB_ACT_ONFIBRO=0`. The previous wave's R2/R3 specs
expressed the fix as `inject: ["onfibro_v13"]` on top of the default face, so on
today's tree the "before" arm already carries it and the comparison is a
self-comparison: re-running them gives `changed = 0 / 0 cells`. That is not a
null result about the fix -- it is evidence the activation took effect -- but it
cannot be used to report the size of the uplift.

Specs measured here
-------------------
  C1  the carrier's own contribution on today's tree, single variable:
        before = kill switch ON  (EYEKB_ACT_ONFIBRO=0, route reverted)
        after  = the tree as shipped (carrier in the default route)
  C0  cumulative uplift from the pre-narrowing baseline to today's default:
        before = EYEKB_TISSUE_SCOPE=0  AND  EYEKB_ACT_ONFIBRO=0
        after  = the tree as shipped

Stdlib only, zero network. Reads nothing writable outside --out.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE is this wave's scripts/ dir, so the repo root is four levels up
# (scripts -> <wave> -> plans -> docs -> <repo root>).
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
NOREGR_SCRIPTS = os.path.join(REPO, "docs", "plans", "noregr_20261022", "scripts")
sys.path.insert(0, NOREGR_SCRIPTS)

import n3_harness as H  # noqa: E402
import wave_common as W  # noqa: E402

OUT = os.path.join(HERE, "..", "out")
OUT = os.path.abspath(OUT)

FINAL_DECLS = {"CX16_tabula_sapiens_eye": "ocular_surface",
               "CX11_posterior_eye_atlas": "ocular_surface"}
CARRIER_OFF = {"EYEKB_ACT_ONFIBRO": "0"}
CARRIER_ON = {"EYEKB_ACT_ONFIBRO": "1"}
SCOPE_OFF = {"EYEKB_TISSUE_SCOPE": "0"}
SCOPE_ON = {"EYEKB_TISSUE_SCOPE": "1"}
TARGET = ("CX15_optic_nerve_all", "31")

# ARM HYGIENE (found the hard way, 2026-10-22)
# -------------------------------------------
# `wave_common.SWITCHES` predates the onfibro flip and therefore does NOT list
# `EYEKB_ACT_ONFIBRO`. `fresh_core()` calls `clear_switches()`, which only pops the names in that
# tuple, so a key set by the BEFORE arm stays set in the AFTER arm *inside the same process*.
# An after arm of `{}` -- the natural way to write "today's tree as shipped" -- is then silently a
# self-comparison and reports `changed = 0`. Both arms below therefore name every switch they touch
# explicitly, and `preflight()` asserts that the two arms really realise different switch states
# before any number is produced. (Scanned every REPORT.json under docs/plans: the only arms with a
# before-only switch key were these two, i.e. no previously delivered measurement is affected.)
SPECS = [
    {"key": "C1_carrier_only_today",
     "spec": {"name": "C1 carrier library on/off, today's tree (single variable)",
              "declared_change": "the registered carrier onfibro_v13 as it is shipped (default route)",
              "tissue_declarations": FINAL_DECLS,
              "before": {"env": dict(CARRIER_OFF)},
              "after": {"env": dict(CARRIER_ON)}}},
    {"key": "C0_cumulative_vs_baseline",
     "spec": {"name": "C0 pre-narrowing baseline -> today's default",
              "declared_change": "whole wave: tissue-scope narrowing + carrier, as shipped",
              "tissue_declarations": FINAL_DECLS,
              "before": {"env": {**SCOPE_OFF, **CARRIER_OFF}},
              "after": {"env": {**SCOPE_ON, **CARRIER_ON}}}},
    # C2 isolates the narrowing itself, which is the step that produced the optic-nerve
    # regression the carrier then had to repair. C1 + C2 decompose C0 exactly.
    {"key": "C2_narrowing_only_carrier_off",
     "spec": {"name": "C2 tissue-scope narrowing alone, carrier held OFF on both arms",
              "declared_change": "the tissue-scope narrowing, measured with the carrier out of both arms",
              "tissue_declarations": FINAL_DECLS,
              "before": {"env": {**SCOPE_OFF, **CARRIER_OFF}},
              "after": {"env": {**SCOPE_ON, **CARRIER_OFF}},
              "attribution": {
                  "CX15_optic_nerve_all": {
                      "cluster": "31 (1,822 cells, reference cell type = fibroblast, family = fibro)",
                      "cause": "the optic-nerve declaration excludes the class "
                               "`Limbus_Sclera_fibroblast_C1`, which was the only reachable carrier "
                               "for the fibro family in that tissue (before: n_ranked = 1, n_shared "
                               "= 1, grade consistent / same_cl; after: n_ranked = 0, no candidate, "
                               "grade mixed / abstain)",
                      "row_or_panel": "the optic_nerve record's `excluded_classes` row for "
                                      "`Limbus_Sclera_fibroblast_C1` in the tissue crosswalk "
                                      "(`eyekb_core._tissue_crosswalk()`)"},
                  "CX13_TM_corneal_scleral": {
                      "cluster": "3 (1,430 cells, reference cell type = conjunctival epithelial cell)",
                      "cause": "the narrowing moves the top candidate to a label string supplied by "
                               "a library the knowledge base does not own; the label is "
                               "`conjunctival epithelial cell`, which is the reference string "
                               "augmented exactly, but the grading layer cannot resolve it to a CL id "
                               "(after_cl = unmappable_pred) whereas the previous label "
                               "`Conj_epithelium_basal` did resolve (before_cl = same_cl). The "
                               "ranking did not degrade: this is a mapping-layer artefact of the "
                               "ruler, counted here rather than hidden",
                      "row_or_panel": "the label-to-CL knowledge source used by the predicate side of "
                                      "the ruler (not the marker panel)"}}}},
]

OBJ = {"onfibro": ("_onfibro_act_enabled", "EYEKB_ACT_ONFIBRO"),
       "scope": ("_tissue_scope_enabled", "EYEKB_TISSUE_SCOPE")}


def preflight():
    """Realise each arm the way `W.replay` will, and report the switch state it actually lands in.

    Refuses (raises) when a spec's two arms do not differ in at least one switch, because such a
    comparison cannot measure its declared change.
    """
    doc = {"role": "arm hygiene: the switch state each arm really lands in, read out of the live "
                    "module rather than inferred from the spec text",
           "switches": {}, "specs": {}}
    for key, (fn, envname) in OBJ.items():
        states = {}
        for label, env in (("unset", {}), (envname + "=0", {envname: "0"}),
                           (envname + "=1", {envname: "1"})):
            core = W.fresh_core(env)
            states[label] = bool(getattr(core, fn)())
        doc["switches"][key] = {"env": envname, "probe": fn, "states": states}
    for entry in SPECS:
        b = (entry["spec"].get("before") or {}).get("env") or {}
        a = (entry["spec"].get("after") or {}).get("env") or {}
        realised, differs = {}, set()
        for label, env in (("before", b), ("after", a)):
            core = W.fresh_core(env)
            realised[label] = {k: bool(getattr(core, fn)()) for k, (fn, _) in OBJ.items()}
        for k in OBJ:
            if realised["before"][k] != realised["after"][k]:
                differs.add(k)
        doc["specs"][entry["key"]] = {"specified_env_before": b, "specified_env_after": a,
                                      "realised": realised,
                                      "differs_on": sorted(differs),
                                      "declared_change_is_measurable": bool(differs)}
        if not differs:
            raise SystemExit("ARM HYGIENE FAIL: %s does not differ from its before arm on any "
                             "tracked switch -- it would report a self-comparison as a null"
                             % entry["key"])
    return doc


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    pf = preflight()
    with open(os.path.join(OUT, "ARM_HYGIENE.json"), "w", encoding="utf-8") as fh:
        json.dump(pf, fh, ensure_ascii=False, indent=1)
    for key, rec in pf["specs"].items():
        print("arm-hygiene %s: differs_on=%s measurable=%s"
              % (key, rec["differs_on"], rec["declared_change_is_measurable"]), flush=True)

    calls = W.load_set()
    rulers = W.Rulers(calls)
    doc = {"probe": "u1_uplift.py",
           "note": "28 volumes x 721 recorded clusters; harness imported read-only from the "
                   "noregr wave; nothing written outside this directory",
           "runs": {}}

    for item in SPECS:
        key = item["key"]
        outdir = os.path.join(OUT, "harness", key)
        print("[%s] running..." % key, flush=True)
        d = H.run_spec(item["spec"], calls, rulers, outdir)
        doc["runs"][key] = d
        rul = d.get("ruling", {})
        print("   verdict=%s" % rul.get("verdict"), flush=True)

        # per-dataset cell-weighted `consistent` share, before -> after
        tcalls = H.overlays(item["spec"], calls)
        b = W.replay(tcalls, item["spec"]["before"].get("env"),
                     inject=item["spec"]["before"].get("inject"), use_own_tissue=True, label="u_b")
        a = W.replay(tcalls, item["spec"]["after"].get("env"),
                     inject=item["spec"]["after"].get("inject"), use_own_tissue=True, label="u_a")
        bds = W.by_dataset(calls, W.grade_arm(calls, b, rulers))
        ads = W.by_dataset(calls, W.grade_arm(calls, a, rulers))
        rows = []
        for vol in sorted(bds):
            bb = bds[vol]["share_pct"].get("consistent")
            aa = ads[vol]["share_pct"].get("consistent")
            rows.append({"volume": vol, "before": bb, "after": aa,
                         "delta_pp": None if (bb is None or aa is None) else round(aa - bb, 3)})
        doc["runs"][key]["per_dataset"] = rows
        deltas = [r["delta_pp"] for r in rows if r["delta_pp"] is not None]
        print("   datasets=%d  delta_pp min=%.3f max=%.3f  sum_positive=%.3f  sum_negative=%.3f"
              % (len(deltas), min(deltas), max(deltas),
                 sum(x for x in deltas if x > 0), sum(x for x in deltas if x < 0)), flush=True)

    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, "UPLIFT_MEASUREMENT.json")
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("wrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())