#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diagnostic -- is the pre-registered judge able to read the answers this library supplies?

Why this exists
---------------
The frozen harness resolves a candidate's Cell-Ontology identity through
`kb/markers/markers_cl_alignment_v2_unified.json`, a map of the 76 SHIPPED class names. `holefill_v12`
names its entries by the Cell Ontology label itself ('retinal rod cell', 'macrophage', 'endothelial
cell', ...), and those names are not in that map -- measured:

    map has 'retinal rod cell'          False
    map has 'Rod' (-> CL:0000604)       True

So every answer the library supplies is resolved as `unmappable_pred` at Cell-Ontology level and as
`inconsistent` at family level (its names are in neither the recording's label->family table nor the
frozen family crosswalk), even where the class it names is the correct one. The 90 takeovers measured
by `l2_flip_measure.py` are therefore graded `inconsistent` for a labelling reason, not necessarily
for a biological one.

This script re-reads the SAME two arms with a resolver that falls back to the library's own `cl_id`
(the entries carry one, read from the Cell Ontology release at build time), so the report can state
both numbers and say which one the pre-registered rule binds. It changes nothing and judges nothing;
it writes out/DIAG_LABELMAP_GAP.json.

Arms: OFF (`EYEKB_ACT_HOLEFILL=0`) vs ON (unset-equivalent), for the recorded declarations AND for the
default route (no `tissue` argument).
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, "/home/ubuntu/EYEKB_REPO/docs/plans/noregr_20261022/scripts")
import wave_common as W          # noqa: E402

OFF = {"EYEKB_ACT_HOLEFILL": "0"}
ON = {"EYEKB_ACT_HOLEFILL": "1"}
INCREMENT = os.path.join(REPO, "kb", "markers", "markers_v12_holefill_increment.json")
GRADES = ("same_cl", "kb_coarser", "kb_finer", "truly_inconsistent", "abstain", "unmappable_pred")
TARGETS = {"endothelial cell": "CL:0000115", "macrophage": "CL:0000235",
           "retinal rod cell": "CL:0000604", "retinal pigment epithelial cell": "CL:0002586"}


def main():
    if "EYEKB_ACT_HOLEFILL" not in W.SWITCHES:
        W.SWITCHES = tuple(W.SWITCHES) + ("EYEKB_ACT_HOLEFILL",)
    inc = json.load(open(INCREMENT))
    entry_cl = {str(k).casefold(): (v or {}).get("cl_id")
                for k, v in (inc.get("entries_by_class") or {}).items()} if \
        isinstance(inc.get("entries_by_class"), dict) else {}
    if not entry_cl:
        entry_cl = {str(k).casefold(): None for k in (inc.get("markers") or {})}
        for e in (inc.get("entries") or []):
            entry_cl[str(e.get("class_name", "")).casefold()] = e.get("cl_id")

    calls = W.load_set()
    rulers = W.Rulers(calls)

    def resolve_pred(label):
        """Frozen map first (the shipped names), then the library's own entry cl_id."""
        cid = rulers.cl_of_pred(label)
        if cid:
            return cid, "frozen_map"
        cid = entry_cl.get(str(label or "").split("::")[-1].strip().casefold())
        if cid:
            return cid, "library_entry"
        return None, None

    def cl_verdict(pred_label, ref_cell_type):
        if not pred_label:
            return "abstain"
        a, src = resolve_pred(pred_label)
        b = rulers.cl_of_truth(ref_cell_type)
        if not a:
            return "unmappable_pred"
        if not b:
            return "unmappable_truth"
        if a == b:
            return "same_cl"
        if a in rulers.anc(b):
            return "kb_coarser"
        if b in rulers.anc(a):
            return "kb_finer"
        return "truly_inconsistent"

    def arm_profile(arm_view, use_own_tissue, label):
        rows = defaultdict(list)
        for c in calls:
            k = (c["vol"], c["cluster"])
            v = arm_view[k]
            rows["all"].append((c, v))
        out = {}
        for scope, items in rows.items():
            cells = Counter()
            clus = Counter()
            for c, v in items:
                vd = cl_verdict(v["top"], c["ref_cell_type"])
                cells[vd] += c["n_cells"]
                clus[vd] += 1
            tot = sum(cells.values()) or 1
            out[scope] = {"cells": tot,
                          "share_pct": {g: round(100.0 * cells.get(g, 0) / tot, 3) for g in GRADES},
                          "clusters": {g: clus.get(g, 0) for g in GRADES}}
        targets = {}
        for name, cl in TARGETS.items():
            keys = [(c["vol"], c["cluster"]) for c in calls if c["ref_cell_type"] == name]
            targets[name] = {
                "clusters": len(keys),
                "exact": sum(1 for k in keys if cl_verdict(arm_view[k]["top"], name) == "same_cl"),
                "cells": sum(c["n_cells"] for c in calls
                             if (c["vol"], c["cluster"]) in set(keys))}
        return {"label": label, "profile": out, "targets": targets}

    arms = {
        "recorded_declarations": (W.replay(calls, OFF, label="gap_kill"),
                                  W.replay(calls, ON, label="gap_flip")),
        "default_route": (W.replay(calls, OFF, use_own_tissue=False, label="gap_kill_d"),
                          W.replay(calls, ON, use_own_tissue=False, label="gap_flip_d")),
    }
    doc = {"probe": "diag_labelmap_gap.py",
           "question": ("can the frozen judge resolve the class names this library emits?"),
           "frozen_map_labels": len(rulers.label_cl),
           "library_entry_cl_ids": len([v for v in entry_cl.values() if v]),
           "class_names_not_in_the_frozen_map": sorted(
               k for k in entry_cl if k not in rulers.label_cl),
           "source_of_each_resolution": {},
           "readings": {}}
    src_census = Counter()
    for scope, (v_off, v_on) in arms.items():
        off = arm_profile(v_off, scope == "recorded_declarations", "OFF")
        on = arm_profile(v_on, scope == "recorded_declarations", "ON")
        doc["readings"][scope] = {"OFF": off, "ON": on}
        for c in calls:
            _, s = resolve_pred(v_on[(c["vol"], c["cluster"])]["top"])
            if s:
                src_census[s] += 1
    doc["source_of_each_resolution"] = dict(src_census)
    # how the 90 takeovers read under the library-aware resolver
    takeovers = []
    v_off = arms["recorded_declarations"][0]
    v_on = arms["recorded_declarations"][1]
    for c in calls:
        k = (c["vol"], c["cluster"])
        if v_on[k]["top"] != v_off[k]["top"] and str(v_on[k]["library"] or "") == \
                "markers_v12_holefill_increment.json":
            takeovers.append({"vol": c["vol"], "cluster": c["cluster"], "n_cells": c["n_cells"],
                              "truth": c["ref_cell_type"], "before": v_off[k]["top"],
                              "after": v_on[k]["top"],
                              "verdict_library_aware": cl_verdict(v_on[k]["top"], c["ref_cell_type"]),
                              "verdict_frozen": rulers.cl_grade(v_on[k]["top"], c["ref_cell_type"])})
    doc["takeovers"] = {"n": len(takeovers),
                        "cells": sum(t["n_cells"] for t in takeovers),
                        "frozen_verdicts": dict(Counter(t["verdict_frozen"] for t in takeovers)),
                        "library_aware_verdicts": dict(Counter(t["verdict_library_aware"]
                                                               for t in takeovers)),
                        "examples": takeovers[:12]}
    with open(os.path.join(OUT, "DIAG_LABELMAP_GAP.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print("frozen map labels:", doc["frozen_map_labels"],
          "| library entries with a CL id:", doc["library_entry_cl_ids"])
    print("library class names absent from the frozen map:",
          len(doc["class_names_not_in_the_frozen_map"]))
    for scope, r in doc["readings"].items():
        off = r["OFF"]["profile"]["all"]["share_pct"]
        on = r["ON"]["profile"]["all"]["share_pct"]
        print("  %-22s same_cl %.3f%% -> %.3f%%   truly_inconsistent %.3f%% -> %.3f%%   "
              "unmappable_pred %.3f%% -> %.3f%%"
              % (scope, off["same_cl"], on["same_cl"], off["truly_inconsistent"],
                 on["truly_inconsistent"], off["unmappable_pred"], on["unmappable_pred"]))
        for name in TARGETS:
            print("      target %-32s exact %d -> %d (of %d clusters)"
                  % (name, r["OFF"]["targets"][name]["exact"], r["ON"]["targets"][name]["exact"],
                     r["ON"]["targets"][name]["clusters"]))
    print("takeovers:", doc["takeovers"]["n"], "clusters /", doc["takeovers"]["cells"], "cells")
    print("   frozen verdicts        :", doc["takeovers"]["frozen_verdicts"])
    print("   library-aware verdicts :", doc["takeovers"]["library_aware_verdicts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())