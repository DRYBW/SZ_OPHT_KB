#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n1 -- reproduce the source-of-truth finding (PREREG G1), and measure the two derived quantities
the narrative asserts rather than shows:

  (a) the shared-gene count between CX15 cluster 31's recorded window and the generic `Fibroblast`
      panel -- the narrative says 1; it is measured here and a different value is reported as a
      correction;
  (b) the arithmetic that makes the drop 2.53pp: which cells leave the consistent bucket.

Read-only. Writes out/REPRODUCE.json.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "out", "REPRODUCE.json"))
PROBE = "/mnt/D/EyeKB/plans/pi_asks_20261021/probe_opticnerve_scope_ab.py"
PY = "/home/ubuntu/training-venv/bin/python3"
VOL = "CX15_optic_nerve_all"


def main():
    doc = {"probe": "n1_reproduce.py", "volume": VOL}

    # --- (0) run the source-of-truth probe verbatim and keep its stdout -------------
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    pr = subprocess.run([PY, PROBE], capture_output=True, text=True, env=env, timeout=1800)
    doc["source_of_truth_probe"] = {"cmd": "%s %s" % (PY, PROBE), "rc": pr.returncode,
                                    "stdout": pr.stdout, "stderr_tail": pr.stderr[-2000:]}

    calls = W.load_set()
    cx15 = [c for c in calls if c["vol"] == VOL]
    tot_cells = sum(c["n_cells"] for c in cx15)

    # --- (1) independent recompute: flip ONLY EYEKB_TISSUE_SCOPE, tissue = optic_nerve --
    off = W.replay(cx15, {"EYEKB_TISSUE_SCOPE": "0"}, use_own_tissue=True, label="off")
    on = W.replay(cx15, {"EYEKB_TISSUE_SCOPE": "1"}, use_own_tissue=True, label="on")

    changed = []
    for c in cx15:
        k = (c["vol"], c["cluster"])
        if (off[k]["top"], off[k]["n_ranked"]) != (on[k]["top"], on[k]["n_ranked"]):
            changed.append({"cluster": c["cluster"], "n_cells": c["n_cells"],
                            "ref_cell_type": c["ref_cell_type"], "ref_family": c["ref_family"],
                            "off_top": off[k]["top"], "off_n_shared": off[k]["n_shared"],
                            "on_top": on[k]["top"],
                            "excluded_on": on[k]["excluded"],
                            "scope_status_on": on[k]["scope_status"],
                            "scope_n_before": on[k]["scope_n_before"],
                            "scope_n_after": on[k]["scope_n_after"]})
    doc["scope_ab"] = {"clusters": len(cx15), "cells": tot_cells,
                       "changed_clusters": len(changed), "changed": changed}

    # --- (2) the mechanism: one cluster, one row ------------------------------------
    mech = []
    for r in changed:
        fam_lost = None
        if r["off_top"] and not r["on_top"]:
            fam_lost = W.base_label(r["off_top"])
        mech.append({"cluster": r["cluster"], "carrier_lost": fam_lost,
                     "loss_share_pct": round(100.0 * r["n_cells"] / tot_cells, 3)})
    doc["carrier_loss"] = mech
    fibro_losses = [m for m in mech if m["carrier_lost"] == "Limbus_Sclera_fibroblast_C1"]
    doc["G1_single_carrier_loss"] = {
        "n_carrier_losses": len([m for m in mech if m["carrier_lost"]]),
        "n_limbus_sclera_fibroblast_losses": len(fibro_losses),
        "clusters": [m["cluster"] for m in fibro_losses],
    }

    # --- (3) the arithmetic: does the loss share equal the measured drop? -----------
    # recorded consistent cells for CX15 under the ledger's own ruler
    cons_cells = sum(c["n_cells"] for c in cx15 if c["truth"]["recorded_fam_eq_raw"])
    lost = [c for c in cx15 if c["cluster"] in [m["cluster"] for m in fibro_losses]]
    lost_cells = sum(c["n_cells"] for c in lost)
    doc["drop_arithmetic"] = {
        "cells_total": tot_cells,
        "recorded_consistent_cells": cons_cells,
        "recorded_consistent_pct": round(100.0 * cons_cells / tot_cells, 3),
        "carrier_loss_cells": lost_cells,
        "after_cells": cons_cells - lost_cells,
        "after_pct": round(100.0 * (cons_cells - lost_cells) / tot_cells, 3),
        "delta_pp": round(-100.0 * lost_cells / tot_cells, 3),
        "carrier_loss_share_of_volume_pct": round(100.0 * lost_cells / tot_cells, 3),
    }

    # --- (4) the generic Fibroblast panel: how many genes does it actually share? ---
    fib_file = W.sha256_file
    panels = {}
    for name in ("markers_membrane_v1.json", "markers_v6_face_increment.json",
                 "markers_v10_antseg_increment.json", "markers_k9_ocs_increment.json"):
        p = os.path.join(W.REPO, "kb", "markers", name)
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        m = d.get("markers")
        if isinstance(m, dict):
            for cls, genes in m.items():
                if "fibroblast" in str(cls).casefold() or "fibro" in str(cls).casefold():
                    panels["%s::%s" % (name, cls)] = sorted({str(g).upper() for g in genes})
    c31 = [c for c in cx15 if c["cluster"] == "31"][0]
    win = [str(g).upper() for g in c31["genes"][:10]]
    shared = {k: sorted(set(win) & set(v)) for k, v in panels.items()}
    doc["cluster31"] = {"n_cells": c31["n_cells"], "genes_recorded": c31["genes"],
                        "window_10": win, "ref_cell_type": c31["ref_cell_type"],
                        "ref_family": c31["ref_family"],
                        "fibroblast_panels": {k: len(v) for k, v in panels.items()},
                        "shared_with_panels": shared,
                        "off_top": off[(VOL, "31")]["top"],
                        "off_shared_genes": off[(VOL, "31")]["shared_genes"],
                        "on_top": on[(VOL, "31")]["top"],
                        "on_excluded": on[(VOL, "31")]["excluded"]}
    doc["cluster31_correction"] = {
        "narrative_claim": "the legitimate generic Fibroblast panel shares only 1 gene with its "
                           "top-10 window (below the >=2 admission bar)",
        "measured_max_shared_with_any_fibroblast_named_panel":
            max([len(v) for v in shared.values()] or [0]),
        "measured": shared,
        "reading": ("correction: the generic panel shares %d gene(s), not 1"
                    % max([len(v) for v in shared.values()] or [0])),
    }

    # --- (5) the external tester's own row -----------------------------------------
    import csv as _csv
    tester = None
    tp = "/mnt/D/EyeKB/plans/zjy_feedback_20261021/from_oss/cross_dataset_summary.csv"
    if os.path.exists(tp):
        for row in _csv.DictReader(open(tp, encoding="utf-8")):
            if row["id"] == VOL:
                tester = row
    doc["external_tester"] = tester
    if tester:
        doc["external_tester_check"] = {
            "consistent_pct_reported": tester["consistent_pct"],
            "consistent_cells_reported": tester["consistent_cells"],
            "cells_reported": tester["cells"],
            "implied_pre_pct": round(
                100.0 * (int(tester["consistent_cells"]) + lost_cells) / int(tester["cells"]), 3),
            "lost_cells_used": lost_cells,
        }

    # --- (6) rulers self-check ------------------------------------------------------
    rulers = W.Rulers(calls)
    doc["ruler_selfcheck"] = rulers.ruler_selfcheck(calls)
    doc["ruler_provenance"] = {
        "labels_from_recording": len(rulers.from_recording),
        "labels_from_crosswalk": len(rulers.from_crosswalk),
        "cl_terms_loaded": len(rulers.terms),
        "class_labels_with_cl": len(rulers.label_cl),
        "truth_labels_resolvable_to_cl": len(rulers.cllabel_cl),
    }

    W.save_json(OUT, doc)
    print("== source-of-truth probe (rc=%s)" % pr.returncode)
    print(pr.stdout.rstrip())
    print("\n== scope A/B recomputed on %d clusters / %d cells: %d changed"
          % (len(cx15), tot_cells, len(changed)))
    for r in changed:
        print("   cl %-3s n=%-6d ref=%-24s off=%-30s -> on=%s"
              % (r["cluster"], r["n_cells"], r["ref_cell_type"], str(r["off_top"]),
                 str(r["on_top"])))
    print("\n== carrier losses:", json.dumps(mech, ensure_ascii=False))
    print("== drop arithmetic:", json.dumps(doc["drop_arithmetic"], ensure_ascii=False))
    print("== cluster 31:", json.dumps(doc["cluster31"], ensure_ascii=False))
    print("== CORRECTION:", json.dumps(doc["cluster31_correction"], ensure_ascii=False))
    print("== tester row:", json.dumps(tester, ensure_ascii=False))
    print("== tester check:", json.dumps(doc.get("external_tester_check"), ensure_ascii=False))
    print("== ruler selfcheck:", json.dumps(doc["ruler_selfcheck"], ensure_ascii=False))
    print("== ruler provenance:", json.dumps(doc["ruler_provenance"], ensure_ascii=False))
    print("wrote", OUT)


if __name__ == "__main__":
    main()