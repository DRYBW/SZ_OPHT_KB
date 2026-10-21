#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""a2_fourway_721.py - classify every recorded (our class, their class) pair with the ontology.

Input (all local, none of it is generated here):
  * plans/oss_check_20261019/scorer_guard_20261020/cl_unify/CLKEY_28VOL_AB.json
      the recorded 28-volume reading: 721 clusters / 1,495,330 cells, each row carrying the
      author cell type, our top candidate, the family-level (regex) verdict, and the CL ids
      the earlier judge resolved. Its cluster rows are the "721 recorded clusters".
  * out/ONT_LABELMAP_V2.tsv   our label -> CL term (built in a1)
  * the ontology file named in out/ONT_NAV_v1.json

What this script adds over the earlier judge:
  * it re-resolves BOTH sides itself (author label by name against the ontology file, our label
    through the library label map) instead of trusting the recorded ids - the recorded ids are
    kept as a column so any drift is visible;
  * it splits the earlier single "subsumed" bucket into we_are_coarser and we_are_finer;
  * it reports the family-regex verdict crossed with the ontology verdict, so the question
    "how much of the disagreement mass is naming, how much is granularity, how much survives"
    is answered with cell counts instead of adjectives.

Outputs: out/GRANULARITY_FOURWAY_721.tsv, out/GRANULARITY_SUMMARY.json,
         out/FAMILY_VS_ONTOLOGY_CROSSTAB.tsv
"""
from __future__ import annotations

import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ont_nav import Ontology, VERDICTS, SAME_TERM, WE_COARSER, WE_FINER, TRUE_MISMATCH, NO_MAPPING  # noqa: E402

RECORDED = ("/mnt/D/EyeKB/plans/oss_check_20261019/scorer_guard_20261020/"
            "cl_unify/CLKEY_28VOL_AB.json")
FAMILY_BAD = "不一致"          # the family-regex verdict string contains 一致 as a substring
FAMILY_OK = "一致"


def strip_prefix(label):
    """The scorer names candidates 'library::Label'; the prefix is provenance, not a cell type."""
    if not label:
        return None
    return str(label).split("::")[-1].strip()


def load_labelmap(path):
    m = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            m[r["label"]] = r
    return m


def main() -> int:
    nav = json.load(open(os.path.join(WAVE, "out", "ONT_NAV_v1.json"), encoding="utf-8"))
    obo = nav["primary_path"]
    ont = Ontology(obo)
    lm = load_labelmap(os.path.join(WAVE, "out", "ONT_LABELMAP_V2.tsv"))
    rec = json.load(open(RECORDED, encoding="utf-8"))
    clusters = rec["clusters"]

    rows = []
    res_drift = {"truth": [], "ours": []}
    for c in clusters:
        ours_label = strip_prefix(c.get("off_top"))
        ours_rec = lm.get(ours_label) if ours_label else None
        ours_cl = ours_rec["cl_id"] if (ours_rec and ours_rec["cl_id"]) else None
        ours_method = (ours_rec["mapping_method"] if ours_rec else "label_not_in_libraries")
        truth_label = c.get("truth")
        r = ont.resolve(truth_label) if truth_label else {"cl_id": None, "method": "no_label"}
        their_cl, their_method = r["cl_id"], r["method"]
        rel = ont.relate(ours_cl, their_cl)
        if their_cl != c.get("truth_cl"):
            res_drift["truth"].append({"vol": c["vol"], "cluster": c["cluster"],
                                       "truth": truth_label,
                                       "recorded": c.get("truth_cl"), "ours": their_cl,
                                       "method": their_method})
        if ours_cl != c.get("off_cl"):
            res_drift["ours"].append({"vol": c["vol"], "cluster": c["cluster"],
                                      "ours_label": ours_label,
                                      "recorded": c.get("off_cl"), "ours": ours_cl,
                                      "method": ours_method})
        path = " -> ".join(rel["path"]) if rel["path"] else ""
        n = int(c["n"])
        # Which kind of "no mapping" is this, on our side? An abstention (no candidate at all)
        # is a legitimate outcome; a candidate that carries no CL term is our own naming debt.
        if ours_cl:
            miss_kind = ""
        elif not ours_label:
            miss_kind = "ours_abstain"
        else:
            miss_kind = "ours_candidate_without_cl_term"
        if not their_cl:
            miss_kind = (miss_kind + "+" if miss_kind else "") + "theirs_no_cl_term"
        rows.append({
            "vol": c["vol"], "cluster": c["cluster"], "n_cells": n,
            "tissue": c.get("tissue"),
            "ours_label": ours_label or "",
            "ours_cl": ours_cl or "", "ours_cl_label": ont.label(ours_cl) or "",
            "ours_mapping_method": ours_method,
            "their_label": truth_label or "",
            "their_cl": their_cl or "", "their_cl_label": ont.label(their_cl) or "",
            "their_resolution": their_method,
            "verdict": rel["verdict"], "missing_side": rel["missing_side"] or "",
            "no_mapping_kind": miss_kind,
            "relation_path": path,
            "recorded_ours_cl": c.get("off_cl") or "",
            "recorded_their_cl": c.get("truth_cl") or "",
            "family_verdict": c.get("old_verdict") or "",
            "recorded_cl_verdict": c.get("off_verdict") or "",
        })

    out_tsv = os.path.join(WAVE, "out", "GRANULARITY_FOURWAY_721.tsv")
    cols = list(rows[0].keys())
    with open(out_tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out_tsv}  ({len(rows)} rows)")

    tot_cells = sum(r["n_cells"] for r in rows)
    by_verdict = collections.Counter()
    cells_by_verdict = collections.Counter()
    missing_side_cells = collections.Counter()
    miss_kind_clusters = collections.Counter()
    miss_kind_cells = collections.Counter()
    for r in rows:
        by_verdict[r["verdict"]] += 1
        cells_by_verdict[r["verdict"]] += r["n_cells"]
        if r["verdict"] == NO_MAPPING:
            missing_side_cells[r["missing_side"]] += r["n_cells"]
            miss_kind_clusters[r["no_mapping_kind"]] += 1
            miss_kind_cells[r["no_mapping_kind"]] += r["n_cells"]

    # ---- reconciliation with the external tester's ontology reading ----
    # The 13 pairs below are transcribed from the upstream evidence file
    # plans/zjy_feedback_20261021/from_oss/EyeKB更新后重评_20261021.md section 5-2 item 2, together
    # with the cell count he reports for each. His own per-cluster file (2026-10-21, post-update
    # arm) is not on this machine; the local recording is the 2026-10-20 arm. So this table
    # compares his numbers with ours on the same (our class, their label) pairs - it does not
    # claim to reproduce his arm.
    HIS_PAIRS = [("Endo", "blood vessel endothelial cell", 23948),
                 ("Mac_Tissue", "macrophage", 23468),
                 ("BC", "rod bipolar cell", 19682),
                 ("Endo", "endothelial cell", 18780),
                 ("Endo", "fenestrated endothelial cell", 9456),
                 ("Endo", "endothelial cell of artery", 6987),
                 ("Endo", "endothelial cell of venule", 5261),
                 ("NK", "natural killer cell", 4378),
                 ("BC", "OFFx cell", 4062),
                 ("BC", "ON-blue cone bipolar cell", 2837),
                 ("Astro", "glial cell", 492),
                 ("Endo", "endothelial cell of vascular tree", 205),
                 ("SMC", "smooth muscle cell", 116)]
    recon = []
    print("\n=== reconciliation with the external tester's 13 pairs (section 5-2 of his report) ===")
    print(f"{'our class':<12}{'their label':<34}{'his cells':>10}{'our cells':>10}"
          f"{'clusters':>9}  our verdict / path")
    his_total = sum(p[2] for p in HIS_PAIRS)
    our_total, our_clusters = 0, 0
    for lab, their, his_cells in HIS_PAIRS:
        sel = [r for r in rows if r["ours_label"] == lab and r["their_label"] == their]
        cells = sum(r["n_cells"] for r in sel)
        verdict = sel[0]["verdict"] if sel else "absent"
        path = sel[0]["relation_path"] if sel else ""
        our_total += cells
        our_clusters += len(sel)
        recon.append({"ours_label": lab, "their_label": their, "his_cells": his_cells,
                      "our_cells": cells, "our_clusters": len(sel), "our_verdict": verdict,
                      "our_path": path})
        print(f"{lab:<12}{their:<34}{his_cells:>10}{cells:>10}{len(sel):>9}  {verdict} "
              f"{('| ' + path) if path else ''}")
    print(f"{'TOTAL':<12}{'':<34}{his_total:>10}{our_total:>10}{our_clusters:>9}")
    recon_total = {"his_cells": his_total, "our_cells": our_total, "our_clusters": our_clusters}

    # family-regex reading, same rows
    fam = collections.Counter()
    fam_cells = collections.Counter()
    for r in rows:
        fv = r["family_verdict"]
        if FAMILY_BAD in fv:
            k = "family_inconsistent"
        elif FAMILY_OK in fv:
            k = "family_consistent"
        else:
            k = "family_other"
        fam[k] += 1
        fam_cells[k] += r["n_cells"]

    # the cross-tab the question needs
    crosstab = collections.Counter()
    cross_cells = collections.Counter()
    for r in rows:
        fv = "family_inconsistent" if FAMILY_BAD in r["family_verdict"] else (
            "family_consistent" if FAMILY_OK in r["family_verdict"] else "family_other")
        crosstab[(fv, r["verdict"])] += 1
        cross_cells[(fv, r["verdict"])] += r["n_cells"]

    bad_cells = fam_cells["family_inconsistent"]
    naming_cells = cross_cells[("family_inconsistent", SAME_TERM)]
    granular_cells = (cross_cells[("family_inconsistent", WE_COARSER)]
                      + cross_cells[("family_inconsistent", WE_FINER)])
    survives_cells = cross_cells[("family_inconsistent", TRUE_MISMATCH)]
    unmapped_cells = cross_cells[("family_inconsistent", NO_MAPPING)]
    same_cells = cells_by_verdict[SAME_TERM]
    judged = (cells_by_verdict[SAME_TERM] + cells_by_verdict[WE_COARSER]
              + cells_by_verdict[WE_FINER] + cells_by_verdict[TRUE_MISMATCH])

    print(f"\n=== (our class, their class) over the recorded {len(rows)} clusters ===")
    print(f"cells total: {tot_cells}")
    hdr = f"{'verdict':<16}{'clusters':>9}{'cells':>9}{'%cells':>8}"
    print(hdr)
    for v in VERDICTS:
        print(f"{v:<16}{by_verdict[v]:>9}{cells_by_verdict[v]:>9}"
              f"{100 * cells_by_verdict[v] / tot_cells:>7.1f}%")
    print(f"  no_mapping by side: "
          f"{ {k: v for k, v in missing_side_cells.items()} }")
    for k in sorted(miss_kind_cells):
        print(f"    {k:<34}{miss_kind_clusters[k]:>6} clusters {miss_kind_cells[k]:>9} cells")

    print(f"\n=== family regex (the reading that produced the 8.0%) ===")
    for k in ("family_consistent", "family_inconsistent", "family_other"):
        print(f"  {k:<22}{fam[k]:>6} clusters {fam_cells[k]:>9} cells "
              f"({100 * fam_cells[k] / tot_cells:.1f}%)")

    print(f"\n=== of the family-inconsistent mass, what it actually is ===")
    print(f"  same CL term (pure naming)      : {naming_cells:>9} cells "
          f"({100 * naming_cells / tot_cells:.1f}% of all cells, "
          f"{100 * naming_cells / max(bad_cells, 1):.1f}% of the inconsistent mass)")
    print(f"  granularity (we coarser/finer)  : {granular_cells:>9} cells "
          f"({100 * granular_cells / tot_cells:.1f}% of all cells, "
          f"{100 * granular_cells / max(bad_cells, 1):.1f}% of the inconsistent mass)")
    print(f"  survives as a real disagreement : {survives_cells:>9} cells "
          f"({100 * survives_cells / tot_cells:.1f}% of all cells, "
          f"{100 * survives_cells / max(bad_cells, 1):.1f}% of the inconsistent mass)")
    print(f"  no mapping on one side          : {unmapped_cells:>9} cells")
    print(f"  family-inconsistent total       : {bad_cells:>9} cells "
          f"({100 * bad_cells / tot_cells:.1f}% of all cells)")
    fam_bad_same_gran_clusters = (crosstab[("family_inconsistent", SAME_TERM)]
                                  + crosstab[("family_inconsistent", WE_COARSER)]
                                  + crosstab[("family_inconsistent", WE_FINER)])
    print(f"  his headline: 43 clusters / {recon_total['his_cells']} cells "
          f"({100 * recon_total['his_cells'] / tot_cells:.1f}% of {tot_cells}) are the same cell "
          f"under ontology authority")
    print(f"  our reading : {fam_bad_same_gran_clusters} clusters / {naming_cells + granular_cells} "
          f"cells ({100 * (naming_cells + granular_cells) / tot_cells:.1f}%) = same-term "
          f"{naming_cells} + granularity {granular_cells}")

    print(f"\n=== agreement readings on the same 721 clusters ===")
    print(f"  family regex   : {100 * fam_cells['family_consistent'] / tot_cells:.2f}% of cells")
    print(f"  ontology, same term only        : {100 * same_cells / tot_cells:.2f}% of cells")
    print(f"  ontology, same term of judged   : {100 * same_cells / max(judged, 1):.2f}% "
          f"({judged} judged cells)")
    print(f"  ontology, same+granularity      : "
          f"{100 * (same_cells + cells_by_verdict[WE_COARSER] + cells_by_verdict[WE_FINER]) / tot_cells:.2f}% of cells")

    # cross-tab file
    xt = os.path.join(WAVE, "out", "FAMILY_VS_ONTOLOGY_CROSSTAB.tsv")
    with open(xt, "w", encoding="utf-8") as f:
        f.write("family_verdict\tontology_verdict\tclusters\tcells\tpct_of_all_cells\n")
        for key in sorted(crosstab):
            f.write(f"{key[0]}\t{key[1]}\t{crosstab[key]}\t{cross_cells[key]}\t"
                    f"{100 * cross_cells[key] / tot_cells:.3f}\n")
    print(f"\nwrote {xt}")

    summary = {
        "generated_by": "scripts/a2_fourway_721.py",
        "recorded_input": RECORDED,
        "ontology": {"path": obo, "sha256": ont.sha256, "release": ont.release},
        "n_clusters": len(rows), "cells": tot_cells,
        "verdicts": {v: {"clusters": by_verdict[v], "cells": cells_by_verdict[v],
                         "pct_cells": round(100 * cells_by_verdict[v] / tot_cells, 3)}
                     for v in VERDICTS},
        "no_mapping_by_side_cells": dict(missing_side_cells),
        "no_mapping_kind": {k: {"clusters": miss_kind_clusters[k], "cells": miss_kind_cells[k]}
                            for k in sorted(miss_kind_cells)},
        "tester_reconciliation": {
            "source": "plans/zjy_feedback_20261021/from_oss/EyeKB更新后重评_20261021.md section 5-2 item 2",
            "pairs": recon,
            "his_total_cells": recon_total["his_cells"],
            "our_cells_on_those_pairs": recon_total["our_cells"],
            "our_clusters_on_those_pairs": recon_total["our_clusters"],
            "his_headline_clusters": 43,
            "our_family_inconsistent_same_or_granularity_clusters": fam_bad_same_gran_clusters,
            "our_family_inconsistent_same_or_granularity_cells": naming_cells + granular_cells,
        },
        "family_regex": {k: {"clusters": fam[k], "cells": fam_cells[k],
                             "pct_cells": round(100 * fam_cells[k] / tot_cells, 3)}
                         for k in fam},
        "family_inconsistent_decomposition": {
            "cells": bad_cells,
            "same_term_pure_naming": naming_cells,
            "granularity": granular_cells,
            "true_mismatch_survives": survives_cells,
            "no_mapping": unmapped_cells,
            "granularity_we_are_coarser_cells": cross_cells[("family_inconsistent", WE_COARSER)],
            "granularity_we_are_finer_cells": cross_cells[("family_inconsistent", WE_FINER)],
        },
        "agreement_readings": {
            "family_regex_pct_of_cells": round(100 * fam_cells["family_consistent"] / tot_cells, 2),
            "ontology_same_term_pct_of_cells": round(100 * same_cells / tot_cells, 2),
            "ontology_same_term_pct_of_judged": round(100 * same_cells / max(judged, 1), 2),
            "ontology_same_plus_granularity_pct_of_cells":
                round(100 * (same_cells + cells_by_verdict[WE_COARSER]
                             + cells_by_verdict[WE_FINER]) / tot_cells, 2),
            "judged_cells": judged,
        },
        "cross_tab": {f"{k[0]}|{k[1]}": {"clusters": crosstab[k], "cells": cross_cells[k]}
                      for k in sorted(crosstab)},
        "resolution_drift_vs_recorded": {
            "n_truth_drift": len(res_drift["truth"]), "truth": res_drift["truth"][:20],
            "n_ours_drift": len(res_drift["ours"]), "ours": res_drift["ours"][:20]},
        "files": {"fourway_tsv": out_tsv, "crosstab_tsv": xt},
    }
    sp = os.path.join(WAVE, "out", "GRANULARITY_SUMMARY.json")
    json.dump(summary, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {sp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())