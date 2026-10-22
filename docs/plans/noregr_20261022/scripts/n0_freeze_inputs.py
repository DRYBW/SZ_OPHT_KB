#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n0 -- freeze the inputs: the sha256 of every frozen input this wave reads, plus the recorded
set's own shape. Run first; nothing downstream may claim a number that is not traceable to one of
these files.

Writes out/INPUT_MANIFEST.json.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

OUT = os.path.join(HERE, "..", "out", "INPUT_MANIFEST.json")


def main():
    docs = []
    for p in sorted(glob.glob(os.path.join(W.REPORTS, "*", "annotation_evidence_report.json"))):
        docs.append(p)
    fixed = [W.LEDGER, W.FAMILY_CROSSWALK, W.CROSSWALK, W.CL_MAP, W.CL_OBO, W.ANTSEG,
             os.path.join(W.REPO, "mcp_server", "eyekb_core.py"),
             os.path.join(W.REPO, "kb", "markers", "markers_membrane_v1.json"),
             os.path.join(W.REPO, "kb", "markers", "markers_k9_ocs_increment.json"),
             os.path.join(W.REPO, "kb", "markers", "markers_v12_holefill_increment.json"),
             os.path.join(W.REPO, "tests", "probe_tool_panel_identity.py"),
             "/mnt/D/EyeKB/plans/pi_asks_20261021/probe_opticnerve_scope_ab.py",
             "/mnt/D/EyeKB/plans/pi_asks_20261021/FINDING_OPTIC_NERVE_REGRESSION_20261022.md",
             "/mnt/D/EyeKB/plans/oss_check_20261019/scorer_guard_20261020/tissue_scope/GATE_A3.json",
             "/mnt/D/EyeKB/plans/oss_check_20261019/scorer_guard_20261020/tissue_scope/"
             "gate_a3_no_collateral.py",
             "/mnt/D/EyeKB/plans/oss_check_20261019/scorer_guard_20261020/tissue_scope/"
             "REPORT_TISSUE_SCOPE_v2.0_DEFAULT_ON.md",
             "/mnt/D/EyeKB/plans/oss_check_20261019/scorer_guard_20261020/"
             "PREREG_TISSUE_SCOPE_20261020.md",
             "/mnt/D/EyeKB/plans/zjy_feedback_20261021/from_oss/cross_dataset_summary.csv",
             "/mnt/D/EyeKB/plans/zjy_feedback_20261021/from_oss/EyeKB更新后重评_20261021.md"]

    man = {"probe": "n0_freeze_inputs.py",
           "purpose": "freeze the sha256 of every input this wave reads",
           "recordings": [], "fixed": [], "missing": []}
    for p in docs:
        if os.path.exists(p):
            man["recordings"].append({"path": p, "sha256": W.sha256_file(p),
                                      "bytes": os.path.getsize(p)})
        else:
            man["missing"].append(p)
    for p in fixed:
        if os.path.exists(p):
            man["fixed"].append({"path": p, "sha256": W.sha256_file(p),
                                 "bytes": os.path.getsize(p)})
        else:
            man["missing"].append(p)

    calls = W.load_set()
    vols = sorted({c["vol"] for c in calls})
    man["recorded_set"] = {
        "volumes": len(vols), "volume_ids": vols, "clusters": len(calls),
        "cells": sum(c["n_cells"] for c in calls),
        "per_volume": {v: sum(1 for c in calls if c["vol"] == v) for v in vols},
        "per_tissue": {},
        "per_species": {},
        "n_recordings_read": len(man["recordings"]),
    }
    pt, ps = {}, {}
    for c in calls:
        pt[c["tissue"]] = pt.get(c["tissue"], 0) + 1
        ps[c["species"]] = ps.get(c["species"], 0) + 1
    man["recorded_set"]["per_tissue"] = pt
    man["recorded_set"]["per_species"] = ps

    W.save_json(os.path.abspath(OUT), man)
    print("volumes=%d clusters=%d cells=%d missing_inputs=%d"
          % (man["recorded_set"]["volumes"], man["recorded_set"]["clusters"],
             man["recorded_set"]["cells"], len(man["missing"])))
    print("per_tissue:", json.dumps(pt, ensure_ascii=False))
    print("per_species:", json.dumps(ps, ensure_ascii=False))
    for p in man["missing"]:
        print("  MISSING", p)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()