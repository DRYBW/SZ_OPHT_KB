#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n2 -- the general-defect sweep (PREREG G2 + G3).

Three measurements, all on the recorded 28-volume / 721-cluster set:

  A. ROW AUDIT. For every exclusion row of every one of the 12 tissues: how many recorded clusters
     does that row remove a reachable candidate from, and for how many of them is the removal a
     CARRIER LOSS (a family-consistent answer replaced by no answer)?
  B. CORRECTED HARM LINE of the exclusion table, per tissue, under two rulers --
        legacy : family = the raw KB class name (the ruler the original harm line used);
        corrected : R_fam (PREREG section 3.3, which reproduces the recorded pred_family column).
  C. HARM LINE OF THE INCREMENT ITSELF (new panels become reachable), per tissue, with the exclusion
     rows withdrawn -- i.e. the same measurement the antseg wave made on retinal clusters only,
     extended to every tissue.

Read-only. Writes out/SWEEP_EXCLUSIONS.json.
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "out", "SWEEP_EXCLUSIONS.json"))
CROSSWALK_JSON = os.path.abspath(os.path.join(HERE, "..", "out", "CROSSWALK_ROWS.json"))


def legacy_fam(top):
    """The ruler the original harm line used: family derived from the raw KB class name."""
    return str(top).split("::")[-1].strip().casefold() if top else None


def legacy_ok(top, ref_family):
    f = legacy_fam(top)
    return bool(f) and f == str(ref_family).strip().casefold()


def main():
    calls = W.load_set()
    rulers = W.Rulers(calls)
    cw = json.load(open(W.CROSSWALK))
    antseg_added = (cw.get("antseg_fill_20261020") or {}).get("added") or {}

    # ---------------------------------------------------------------- A. row audit
    scon = W.replay(calls, {"EYEKB_TISSUE_SCOPE": "1"}, use_own_tissue=True, label="scon")
    scoff = W.replay(calls, {"EYEKB_TISSUE_SCOPE": "0"}, use_own_tissue=True, label="scoff")

    rows = []
    for tissue, rec in sorted((cw.get("tissues") or {}).items()):
        excl = rec.get("excluded_classes") or []
        added = set(antseg_added.get(tissue) or [])
        for cls in excl:
            rows.append({"tissue": tissue, "row": cls,
                         "from_antseg_increment": cls in added,
                         "inventory_status": rec.get("inventory_status"),
                         "implicated_clusters": [], "carrier_loss_clusters": [],
                         "grade_fall_clusters": []})

    byrow = {(r["tissue"], r["row"]): r for r in rows}
    for c in calls:
        k = (c["vol"], c["cluster"])
        b, a = scoff[k], scon[k]
        # which candidate(s) did this cluster actually lose to the filter?
        lost = []
        # the candidate the OFF arm answered and the ON arm no longer answers
        if b["top"] and (a["top"] is None or a["top"] != b["top"]):
            lost.append(W.base_label(b["top"]))
        # the ON arm names exactly what it removed for this cluster
        tissue_rows = (cw["tissues"].get(c["tissue"]) or {})
        for cls in sorted(set(a["excluded"]) & set(tissue_rows.get("excluded_classes") or [])):
            key = (c["tissue"], cls)
            if key not in byrow:
                continue
            byrow[key]["implicated_clusters"].append(
                {"vol": c["vol"], "cluster": c["cluster"], "n_cells": c["n_cells"],
                 "ref_cell_type": c["ref_cell_type"], "ref_family": c["ref_family"],
                 "before_top": b["top"], "after_top": a["top"]})
        for cls in lost:
            key = (c["tissue"], cls)
            if key not in byrow:
                continue
            entry = {"vol": c["vol"], "cluster": c["cluster"], "n_cells": c["n_cells"],
                     "ref_cell_type": c["ref_cell_type"], "ref_family": c["ref_family"],
                     "before_top": b["top"], "after_top": a["top"],
                     "before_grade": rulers.grade(b["top"], c["ref_family"], c["ref_cell_type"]),
                     "after_grade": rulers.grade(a["top"], c["ref_family"], c["ref_cell_type"]),
                     "before_legacy_ok": legacy_ok(b["top"], c["ref_family"]),
                     "after_legacy_ok": legacy_ok(a["top"], c["ref_family"])}
            if entry["before_grade"] in ("consistent", "related") and \
               entry["after_grade"] == "mixed":
                byrow[key]["carrier_loss_clusters"].append(entry)
            if entry["before_grade"] in ("consistent", "related") and \
               entry["after_grade"] not in ("consistent", "related"):
                byrow[key]["grade_fall_clusters"].append(entry)

    for r in rows:
        r["n_implicated"] = len(r["implicated_clusters"])
        r["n_carrier_loss"] = len(r["carrier_loss_clusters"])
        r["n_grade_fall"] = len(r["grade_fall_clusters"])
        r["cells_carrier_loss"] = sum(x["n_cells"] for x in r["carrier_loss_clusters"])
        r["live_defect"] = r["n_carrier_loss"] > 0

    live = [r for r in rows if r["live_defect"]]
    W.save_json(CROSSWALK_JSON, {"probe": "n2_sweep_exclusions.py (part A)", "rows": rows,
                                 "n_rows": len(rows), "n_live_defects": len(live),
                                 "live_rows": [{k: r[k] for k in
                                                ("tissue", "row", "from_antseg_increment",
                                                 "n_implicated", "n_carrier_loss",
                                                 "cells_carrier_loss")}
                                               for r in live]})

    # ---------------------------------------------------------------- B. corrected harm line
    before_g = W.grade_arm(calls, scoff, rulers)
    after_g = W.grade_arm(calls, scon, rulers)
    ds_b = W.by_dataset(calls, before_g)
    ds_a = W.by_dataset(calls, after_g)
    deltas = W.rank_deltas(calls, before_g, after_g)
    trans = W.transition_matrix(calls, before_g, after_g)

    per_tissue = {}
    for t in sorted({c["tissue"] for c in calls}):
        sub = [c for c in calls if c["tissue"] == t]
        n = sum(c["n_cells"] for c in sub)
        lb = sum(c["n_cells"] for c in sub if legacy_ok(scoff[(c["vol"], c["cluster"])]["top"],
                                                       c["ref_family"]))
        la = sum(c["n_cells"] for c in sub if legacy_ok(scon[(c["vol"], c["cluster"])]["top"],
                                                       c["ref_family"]))
        per_tissue[t] = {
            "clusters": len(sub), "cells": n,
            "legacy_before_cells": lb, "legacy_after_cells": la,
            "legacy_delta_pp": round(100.0 * (la - lb) / (n or 1), 3),
            "legacy_collateral_clusters": [x["cluster"] for x in deltas
                                           if x["tissue"] == t
                                           and legacy_ok(x["before_top"], x["ref_family"])
                                           and not legacy_ok(x["after_top"], x["ref_family"])],
            "rfam_before_consistent_pct": W.shares([before_g[(c["vol"], c["cluster"])]
                                                   for c in sub])["share_pct"]["consistent"],
            "rfam_after_consistent_pct": W.shares([after_g[(c["vol"], c["cluster"])]
                                                   for c in sub])["share_pct"]["consistent"],
            "rfam_collateral_clusters": [x["cluster"] for x in deltas if x["tissue"] == t
                                         and x["before_grade"] in ("consistent", "related")
                                         and x["after_grade"] not in ("consistent", "related")],
            "clusters_changed_top1": len([x for x in deltas if x["tissue"] == t]),
        }
    for t, d in per_tissue.items():
        d["rfam_delta_pp"] = round(d["rfam_after_consistent_pct"]
                                   - d["rfam_before_consistent_pct"], 3)

    # ---- B2. the same harm line under the declarations the external tester finally used --------
    # He re-pointed CX16 (retina -> ocular_surface) and CX11 (optic_nerve -> ocular_surface) after
    # finding a better declaration. The recordings carry the ORIGINAL declarations, so the harm line
    # depends on which declaration set is replayed; both are reported.
    FINAL_DECLS = {"CX16_tabula_sapiens_eye": "ocular_surface",
                   "CX11_posterior_eye_atlas": "ocular_surface"}
    calls_final = [dict(c, tissue=FINAL_DECLS.get(c["vol"], c["tissue"])) for c in calls]
    fcon = W.replay(calls_final, {"EYEKB_TISSUE_SCOPE": "1"}, use_own_tissue=True,
                    label="scon_final")
    fcoff = W.replay(calls_final, {"EYEKB_TISSUE_SCOPE": "0"}, use_own_tissue=True,
                     label="scoff_final")
    f_b = W.grade_arm(calls_final, fcoff, rulers)
    f_a = W.grade_arm(calls_final, fcon, rulers)
    f_deltas = W.rank_deltas(calls_final, f_b, f_a)
    f_coll = [x for x in f_deltas if x["before_grade"] in ("consistent", "related")
              and x["after_grade"] not in ("consistent", "related")]
    per_tissue_final = {}
    for t in sorted({c["tissue"] for c in calls_final}):
        sub = [c for c in calls_final if c["tissue"] == t]
        per_tissue_final[t] = {
            "clusters": len(sub),
            "rfam_before_consistent_pct": W.shares([f_b[(c["vol"], c["cluster"])]
                                                   for c in sub])["share_pct"]["consistent"],
            "rfam_after_consistent_pct": W.shares([f_a[(c["vol"], c["cluster"])]
                                                  for c in sub])["share_pct"]["consistent"],
            "clusters_changed_top1": len([x for x in f_deltas if x["tissue"] == t]),
        }
    for t, d in per_tissue_final.items():
        d["rfam_delta_pp"] = round(d["rfam_after_consistent_pct"]
                                   - d["rfam_before_consistent_pct"], 3)

    # ---------------------------------------------------------------- C. increment harm line
    inc_added_pairs = [(t, c) for t, cs in antseg_added.items() for c in cs]
    base = W.replay(calls, {"EYEKB_TISSUE_SCOPE": "0", "EYEKB_ACT_ANTSEG": "0"},
                    use_own_tissue=True, label="inc_off")
    withinc = W.replay(calls, {"EYEKB_TISSUE_SCOPE": "0", "EYEKB_ACT_ANTSEG": "1"},
                       use_own_tissue=True, label="inc_on")
    inc_b, inc_a = W.grade_arm(calls, base, rulers), W.grade_arm(calls, withinc, rulers)
    inc_deltas = W.rank_deltas(calls, inc_b, inc_a)
    inc_tissue = {}
    for t in sorted({c["tissue"] for c in calls}):
        sub = [c for c in calls if c["tissue"] == t]
        ch = [x for x in inc_deltas if x["tissue"] == t]
        inc_tissue[t] = {
            "clusters": len(sub),
            "clusters_changed_top1": len(ch),
            "consistent_before_pct": W.shares([inc_b[(c["vol"], c["cluster"])]
                                               for c in sub])["share_pct"]["consistent"],
            "consistent_after_pct": W.shares([inc_a[(c["vol"], c["cluster"])]
                                              for c in sub])["share_pct"]["consistent"],
            "grade_falls": len([x for x in ch if x["before_grade"] in ("consistent", "related")
                                and x["after_grade"] not in ("consistent", "related")]),
            "abstain_to_answer": len([x for x in ch if x["before_top"] is None
                                      and x["after_top"] is not None]),
            "answer_to_abstain": len([x for x in ch if x["before_top"] is not None
                                      and x["after_top"] is None]),
        }
    for t, d in inc_tissue.items():
        d["consistent_delta_pp"] = round(d["consistent_after_pct"]
                                         - d["consistent_before_pct"], 3)

    doc = {
        "probe": "n2_sweep_exclusions.py",
        "recorded_set": {"clusters": len(calls), "cells": sum(c["n_cells"] for c in calls),
                         "volumes": len({c["vol"] for c in calls})},
        "A_row_audit": {"n_tissues": len(cw.get("tissues") or {}), "n_rows": len(rows),
                        "n_live_defects": len(live),
                        "live_rows": [{k: r[k] for k in ("tissue", "row",
                                                         "from_antseg_increment", "n_implicated",
                                                         "n_carrier_loss", "cells_carrier_loss")}
                                      for r in live],
                        "rows": rows},
        "B_exclusion_harm_line": {
            "changed_top1_clusters": len(deltas),
            "changed_top1_cells": sum(x["n_cells"] for x in deltas),
            "legacy_rule": "family := raw KB class name, compared to the reference family "
                           "(reproduces gate_a3_no_collateral.py lines 102-115)",
            "legacy_collateral_clusters": [x for x in deltas
                                           if legacy_ok(x["before_top"], x["ref_family"])
                                           and not legacy_ok(x["after_top"], x["ref_family"])],
            "corrected_collateral_clusters": [x for x in deltas
                                              if x["before_grade"] in ("consistent", "related")
                                              and x["after_grade"] not in ("consistent", "related")],
            "per_tissue": per_tissue,
            "overall_before": W.shares([before_g[k] for k in before_g]),
            "overall_after": W.shares([after_g[k] for k in after_g]),
            "transition_matrix": trans,
            "per_cluster_deltas": deltas,
            "B2_final_declarations": {
                "declarations_repointed": FINAL_DECLS,
                "changed_top1_clusters": len(f_deltas),
                "corrected_collateral_clusters": f_coll,
                "per_tissue": per_tissue_final,
            },
        },
        "C_increment_harm_line": {
            "rule": "EYEKB_ACT_ANTSEG 0 -> 1 with EYEKB_TISSUE_SCOPE=0 (exclusion table not applied), "
                    "so this is the raw effect of the new panels becoming reachable",
            "per_tissue": inc_tissue,
            "changed_clusters": len(inc_deltas),
            "changed_cells": sum(x["n_cells"] for x in inc_deltas),
            "per_cluster": inc_deltas,
        },
        "prior_claim_not_reproducible": {
            "claim": "antseg_fill_20261020 recorded the harm line as '10/197 retinal clusters "
                     "changed their top-1'",
            "why_not_reproducible_verbatim": "the recorded set's retina-declared subset has %d "
                                             "clusters, not 197; no subset of size 197 is defined by "
                                             "the recorded declarations, so the denominator cannot "
                                             "be reconstructed from the frozen inputs"
                                             % len([c for c in calls if c["tissue"] == "retina"]),
            "reproducible_analogue": {
                "retina_declared_clusters": len([c for c in calls if c["tissue"] == "retina"]),
                "retina_changed_top1": inc_tissue.get("retina", {}).get("clusters_changed_top1"),
            },
        },
    }
    W.save_json(OUT, doc)

    print("== A. row audit: %d rows over %d tissues, %d live defects"
          % (len(rows), len(cw.get("tissues") or {}), len(live)))
    for r in live:
        print("   LIVE %-20s %-34s implicated=%d carrier_loss=%d cells=%d (antseg_row=%s)"
              % (r["tissue"], r["row"], r["n_implicated"], r["n_carrier_loss"],
                 r["cells_carrier_loss"], r["from_antseg_increment"]))
    print("\n== B. exclusion-table harm line (scope ON vs OFF)")
    print("   changed top-1: %d clusters / %d cells"
          % (len(deltas), sum(x["n_cells"] for x in deltas)))
    print("   legacy ruler  collateral (was ok -> not ok): %d"
          % len(doc["B_exclusion_harm_line"]["legacy_collateral_clusters"]))
    print("   R_fam ruler   collateral (was ok -> not ok): %d"
          % len(doc["B_exclusion_harm_line"]["corrected_collateral_clusters"]))
    for x in doc["B_exclusion_harm_line"]["corrected_collateral_clusters"]:
        print("      FALL %-26s c%-4s n=%-6d %-16s %-30s -> %-10s (%s -> %s)"
              % (x["vol"], x["cluster"], x["n_cells"], x["tissue"], str(x["before_top"]),
                 str(x["after_top"]), x["before_grade"], x["after_grade"]))
    print("   per tissue (legacy vs corrected delta):")
    for t, d in sorted(per_tissue.items(), key=lambda kv: kv[1]["legacy_delta_pp"]):
        print("      %-20s cl=%-4d legacy %+6.3fpp  R_fam %+6.3fpp  changed=%d"
              % (t, d["clusters"], d["legacy_delta_pp"], d["rfam_delta_pp"],
                 d["clusters_changed_top1"]))
    print("\n== B2. same change, the declarations the external tester finally used")
    print("   changed top-1: %d clusters; corrected collateral: %d"
          % (len(f_deltas), len(f_coll)))
    for x in f_coll:
        print("      FALL %-26s c%-4s n=%-6d %-16s %-30s -> %-10s (%s -> %s)"
              % (x["vol"], x["cluster"], x["n_cells"], x["tissue"], str(x["before_top"]),
                 str(x["after_top"]), x["before_grade"], x["after_grade"]))
    for t, d in sorted(per_tissue_final.items(), key=lambda kv: kv[1]["rfam_delta_pp"]):
        print("      %-20s cl=%-4d R_fam %+6.3fpp  changed=%d"
              % (t, d["clusters"], d["rfam_delta_pp"], d["clusters_changed_top1"]))
    print("\n== C. increment harm line (panels reachable, exclusions withdrawn)")
    for t, d in sorted(inc_tissue.items(), key=lambda kv: -kv[1]["clusters"]):
        print("      %-20s cl=%-4d changed=%-4d consistent %+6.3fpp  falls=%d  abstain->ans=%d "
              "ans->abstain=%d"
              % (t, d["clusters"], d["clusters_changed_top1"], d["consistent_delta_pp"],
                 d["grade_falls"], d["abstain_to_answer"], d["answer_to_abstain"]))
    print("\n== prior claim:", json.dumps(doc["prior_claim_not_reproducible"], ensure_ascii=False))
    print("wrote", OUT)


if __name__ == "__main__":
    main()