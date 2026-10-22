#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n3 -- THE REGRESSION HARNESS (card part 3; PREREG G6 + G7).

"Does not lower accuracy" as a machine gate, over the recorded 28 volumes x 721 clusters.

Usage
-----
  python3 n3_harness.py --spec <spec.json> --out <dir>            # measure one change
  python3 n3_harness.py --self-test --out <dir>                   # exercise the acceptance rule
  python3 n3_harness.py --spec <spec.json> --out <dir> --ruling-only

spec.json
---------
{
  "name":        "free text, becomes the run's title",
  "declared_change": "one line of prose: what a caller is proposing",
  "tissue_declarations": {"<volume>": "<tissue>"},   # optional overlay on the recorded declarations
  "before": {"env": {...}, "inject": ["<library>", ...], "withdraw": [["<tissue>","<row>"], ...]},
  "after":  { ... same shape ... },
  "attribution": {"<dataset>": {"cluster": "...", "cause": "...", "row_or_panel": "..."}}
}

What it reports, for the change `before -> after`
-------------------------------------------------
  * per-dataset ranking deltas and cell-weighted consistent/related/inconsistent/mixed before/after;
  * per-cluster top-1 / n_shared / n_ranked deltas;
  * the cells moved in each direction (a 4x4 grade transition matrix, cell-weighted);
  * the Cell Ontology reading (same_cl / kb_coarser / kb_finer / truly_inconsistent / abstain);
  * the harness's own pre-image, so the numbers are re-derivable.

The ACCEPTANCE RULE (pre-registered, implemented here as code, not as prose)
---------------------------------------------------------------------------
A candidate change may not be reported as complete while any dataset's cell-weighted `consistent`
share has fallen -- unless the drop is attributed, IN THE ARTEFACT, to a named cluster, a named
cause and a named row/panel. Verdicts: PASS (no fall), PASS_ATTRIBUTED (falls, all attributed),
FAIL (a fall with an incomplete attribution).

The harness is measurement only: it changes no score, no admission floor, no tie-break, and it
writes nothing outside its own --out directory.
"""
import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

HARNESS_FILES = ("n3_harness.py", "wave_common.py")


def preimage():
    doc = {"role": "the harness's own pre-image: every number it reports is re-derivable from "
                    "these files plus the frozen inputs",
           "files": [], "inputs": None}
    for f in HARNESS_FILES:
        p = os.path.join(HERE, f)
        doc["files"].append({"path": "scripts/" + f, "sha256": W.sha256_file(p),
                             "bytes": os.path.getsize(p)})
    man = os.path.abspath(os.path.join(HERE, "..", "out", "INPUT_MANIFEST.json"))
    if os.path.exists(man):
        m = json.load(open(man))
        dig = W.sha256_file(man)
        doc["inputs"] = {"input_manifest_sha256": dig,
                         "recordings_sha256": {os.path.basename(x["path"]): x["sha256"]
                                               for x in m["recordings"]},
                         "fixed_sha256": {os.path.basename(x["path"]): x["sha256"]
                                          for x in m["fixed"]}}
    return doc


def overlays(spec, calls):
    dec = spec.get("tissue_declarations") or {}
    if dec:
        calls = [dict(c, tissue=dec.get(c["vol"], c["tissue"])) for c in calls]
    return calls


def apply_arm(calls, arm, rulers, label):
    view = W.replay(calls, arm.get("env"), inject=arm.get("inject"),
                    withdraw=[tuple(x) for x in (arm.get("withdraw") or [])],
                    use_own_tissue=True, label=label)
    return view, W.grade_arm(calls, view, rulers)


def run_spec(spec, calls, rulers, outdir):
    calls = overlays(spec, calls)
    bview, bgrade = apply_arm(calls, spec.get("before") or {}, rulers, "before")
    aview, agrade = apply_arm(calls, spec.get("after") or {}, rulers, "after")

    ds_b = W.by_dataset(calls, bgrade)
    ds_a = W.by_dataset(calls, agrade)
    per_ds = {}
    for ds in sorted(set(ds_b) | set(ds_a)):
        b = ds_b.get(ds, {})
        a = ds_a.get(ds, {})
        per_ds[ds] = {
            "clusters": b.get("n_clusters") or a.get("n_clusters"),
            "cells": b.get("n_cells") or a.get("n_cells"),
            "before": b.get("share_pct"), "after": a.get("share_pct"),
            "delta_pp": {g: round((a.get("share_pct", {}).get(g, 0.0)
                                   - b.get("share_pct", {}).get(g, 0.0)), 3)
                         for g in W.GRADES},
            "clusters_before": b.get("clusters"), "clusters_after": a.get("clusters"),
            "cells_before": b.get("cells"), "cells_after": a.get("cells"),
        }

    deltas = W.rank_deltas(calls, bgrade, agrade)
    trans = W.transition_matrix(calls, bgrade, agrade)
    cl_trans = Counter()
    for c in calls:
        k = (c["vol"], c["cluster"])
        cl_trans["%s->%s" % (bgrade[k]["cl"], agrade[k]["cl"])] += 1

    overall_b = W.shares([bgrade[k] for k in bgrade])
    overall_a = W.shares([agrade[k] for k in agrade])
    verdict, ruling = W.judge(ds_b, ds_a, spec.get("attribution") or {}, trans["cells"])

    doc = {
        "probe": "n3_harness.py", "name": spec.get("name"),
        "declared_change": spec.get("declared_change"),
        "before_arm": {k: v for k, v in (spec.get("before") or {}).items()},
        "after_arm": {k: v for k, v in (spec.get("after") or {}).items()},
        "tissue_declarations_overlay": spec.get("tissue_declarations") or {},
        "recorded_set": {"clusters": len(calls), "cells": sum(c["n_cells"] for c in calls),
                         "volumes": len({c["vol"] for c in calls})},
        "overall_before": overall_b, "overall_after": overall_a,
        "overall_delta_pp": {g: round(overall_a["share_pct"][g] - overall_b["share_pct"][g], 3)
                             for g in W.GRADES},
        "per_dataset": per_ds,
        "transition_matrix_cells": trans["cells"],
        "transition_matrix_clusters": trans["clusters"],
        "cl_transition_clusters": dict(sorted(cl_trans.items())),
        "changed_clusters": len(deltas),
        "changed_cells": sum(x["n_cells"] for x in deltas),
        "per_cluster_deltas": deltas,
        "ruling": {"verdict": verdict, **ruling,
                   "rule": "a change may not be reported as complete while any dataset's "
                           "cell-weighted consistent share has fallen, unless the drop is "
                           "attributed to a named cluster + named cause + named row/panel"},
        "harness_preimage": preimage(),
    }
    os.makedirs(outdir, exist_ok=True)
    W.save_json(os.path.join(outdir, "REPORT.json"), doc)
    write_markdown(doc, os.path.join(outdir, "REPORT.md"))
    return doc


def write_markdown(doc, path):
    L = []
    A = L.append
    A("# Regression-harness report -- %s" % (doc.get("name") or "(unnamed)"))
    A("")
    A("Declared change: %s" % (doc.get("declared_change") or "(none given)"))
    A("")
    A("Before arm: `%s`" % json.dumps(doc["before_arm"], ensure_ascii=False))
    A("After arm:  `%s`" % json.dumps(doc["after_arm"], ensure_ascii=False))
    A("")
    A("Recorded set: %d clusters / %d cells / %d volumes"
      % (doc["recorded_set"]["clusters"], doc["recorded_set"]["cells"],
         doc["recorded_set"]["volumes"]))
    A("")
    A("## Ruling: **%s**" % doc["ruling"]["verdict"])
    A("")
    A(doc["ruling"]["rule"])
    if doc["ruling"].get("unattributed_drops"):
        A("")
        A("Unattributed falls: %s" % ", ".join(doc["ruling"]["unattributed_drops"]))
    if doc["ruling"].get("drops"):
        A("")
        for ds, d in sorted(doc["ruling"]["drops"].items()):
            A("- **%s** consistent %.3f%% -> %.3f%% (%+.3fpp)%s"
              % (ds, d.get("before_pct", float("nan")), d.get("after_pct", float("nan")),
                 d.get("delta_pp", float("nan")),
                 "" if not d.get("unattributed") else
                 "  UNATTRIBUTED (missing: %s)" % ", ".join(d["unattributed"])))
    A("")
    A("## Overall, cell-weighted")
    A("")
    A("| grade | before % | after % | delta pp | clusters before | clusters after |")
    A("|---|---:|---:|---:|---:|---:|")
    for g in W.GRADES:
        A("| %s | %.3f | %.3f | %+.3f | %d | %d |"
          % (g, doc["overall_before"]["share_pct"][g], doc["overall_after"]["share_pct"][g],
             doc["overall_delta_pp"][g], doc["overall_before"]["clusters"][g],
             doc["overall_after"]["clusters"][g]))
    A("")
    A("## Per dataset")
    A("")
    A("| dataset | clusters | cells | before consistent % | after consistent % | delta pp |")
    A("|---|---:|---:|---:|---:|---:|")
    for ds, d in sorted(doc["per_dataset"].items(),
                        key=lambda kv: kv[1]["delta_pp"]["consistent"]):
        A("| %s | %s | %s | %s | %s | %+.3f |"
          % (ds, d["clusters"], d["cells"], d["before"]["consistent"], d["after"]["consistent"],
             d["delta_pp"]["consistent"]))
    A("")
    A("## Cells moved, by grade transition")
    A("")
    A("| transition | clusters | cells |")
    A("|---|---:|---:|")
    for k, v in sorted(doc["transition_matrix_cells"].items(), key=lambda kv: -kv[1]):
        A("| %s | %s | %d |" % (k, doc["transition_matrix_clusters"].get(k, 0), v))
    A("")
    A("## Clusters whose ranking moved (%d clusters / %d cells)"
      % (doc["changed_clusters"], doc["changed_cells"]))
    A("")
    A("| volume | cluster | n_cells | tissue | before | after | grade |")
    A("|---|---|---:|---|---|---|---|")
    for x in doc["per_cluster_deltas"]:
        A("| %s | %s | %d | %s | %s (%s) | %s (%s) | %s -> %s |"
          % (x["vol"], x["cluster"], x["n_cells"], x["tissue"], x["before_top"],
             x["before_n_shared"], x["after_top"], x["after_n_shared"],
             x["before_grade"], x["after_grade"]))
    A("")
    A("## Harness pre-image")
    A("")
    A("```json")
    A(json.dumps(doc["harness_preimage"], ensure_ascii=False, indent=1)[:4000])
    A("```")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def self_test(outdir):
    """G7: the acceptance rule must be able to fail, not only to pass."""
    results = []
    calls = W.load_set()
    rulers = W.Rulers(calls)

    # a real, measured change is used as the fixture: the exclusion-table narrowing, which DOES
    # drop optic_nerve by 2.53pp when the recorded declarations are used.
    spec = {"name": "self-test fixture (exclusion table ON vs OFF, recorded declarations)",
            "declared_change": "tissue-scope narrowing applied to the declared tissue",
            "before": {"env": {"EYEKB_TISSUE_SCOPE": "0"}},
            "after": {"env": {"EYEKB_TISSUE_SCOPE": "1"}}}
    d1 = run_spec(spec, calls, rulers, os.path.join(outdir, "selftest_unattributed"))
    results.append({"case": "unattributed drop", "verdict": d1["ruling"]["verdict"],
                    "expected": "FAIL",
                    "ok": d1["ruling"]["verdict"] == "FAIL"})

    spec2 = dict(spec)
    spec2["name"] = "self-test fixture (same change, drop attributed in the artefact)"
    spec2["attribution"] = {
        "CX15_optic_nerve_all": {
            "cluster": "31",
            "cause": "the exclusion row removes the only reachable carrier of the fibroblast "
                     "family for this cluster; the legitimate generic Fibroblast panel shares 0 "
                     "genes with its 10-gene window, so no coarse answer survives",
            "row_or_panel": "kb/baselines/_tissue_class_crosswalk_v1.json :: optic_nerve :: "
                            "Limbus_Sclera_fibroblast_C1"},
        "CX11_posterior_eye_atlas": {
            "cluster": "4",
            "cause": "same mechanism, same row (the volume is declared optic_nerve in the recording)",
            "row_or_panel": "kb/baselines/_tissue_class_crosswalk_v1.json :: optic_nerve :: "
                            "Limbus_Sclera_fibroblast_C1"},
        "CX16_tabula_sapiens_eye": {
            "cluster": "11,12,13,15",
            "cause": "declaration/content mismatch: the volume is declared retina in the recording "
                     "while its conjunctival clusters are removed by the retina exclusion rows; the "
                     "external tester re-declared this volume to ocular_surface",
            "row_or_panel": "kb/baselines/_tissue_class_crosswalk_v1.json :: retina :: "
                            "Conj_epithelium_basal / Conj_epithelium_suprabasal"},
        "CX13_TM_corneal_scleral": {
            "cluster": "3",
            "cause": "same declaration/content mismatch pattern on a trabecular-meshwork-declared "
                     "volume",
            "row_or_panel": "kb/baselines/_tissue_class_crosswalk_v1.json :: trabecular_meshwork :: "
                            "Conj_epithelium_basal"},
    }
    d2 = run_spec(spec2, calls, rulers, os.path.join(outdir, "selftest_attributed"))
    results.append({"case": "attributed drop", "verdict": d2["ruling"]["verdict"],
                    "expected": "PASS_ATTRIBUTED",
                    "ok": d2["ruling"]["verdict"] == "PASS_ATTRIBUTED"})

    # a change that moves nothing must PASS (the gate is not a blanket refusal)
    spec3 = {"name": "self-test fixture (no-op change)",
             "declared_change": "nothing at all",
             "before": {"env": {"EYEKB_TISSUE_SCOPE": "1"}},
             "after": {"env": {"EYEKB_TISSUE_SCOPE": "1"}}}
    d3 = run_spec(spec3, calls, rulers, os.path.join(outdir, "selftest_noop"))
    results.append({"case": "no-op change", "verdict": d3["ruling"]["verdict"],
                    "expected": "PASS", "ok": d3["ruling"]["verdict"] == "PASS"})

    doc = {"probe": "n3_harness.py --self-test",
           "purpose": "G7: the acceptance rule must be able to FAIL, not only to pass",
           "cases": results,
           "verdict": "PASS" if all(r["ok"] for r in results) else "FAIL"}
    W.save_json(os.path.join(outdir, "SELFTEST_ACCEPTANCE_RULE.json"), doc)
    for r in results:
        print("   %-22s verdict=%-16s expected=%-16s %s"
              % (r["case"], r["verdict"], r["expected"], "OK" if r["ok"] else "*** MISMATCH"))
    print("   acceptance-rule self-test verdict:", doc["verdict"])
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--ruling-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.self_test:
        d = self_test(a.out)
        sys.exit(0 if d["verdict"] == "PASS" else 1)
    spec = json.load(open(a.spec))
    calls = W.load_set()
    rulers = W.Rulers(calls)
    doc = run_spec(spec, calls, rulers, a.out)
    print("verdict=%s  datasets_checked=%s  changed_clusters=%d  changed_cells=%d"
          % (doc["ruling"]["verdict"], doc["ruling"].get("datasets_checked"),
             doc["changed_clusters"], doc["changed_cells"]))
    for ds, d in sorted(doc["per_dataset"].items(), key=lambda kv: kv[1]["delta_pp"]["consistent"]):
        if abs(d["delta_pp"]["consistent"]) > 1e-9:
            print("   %-28s consistent %7.3f%% -> %7.3f%%  (%+.3fpp)"
                  % (ds, d["before"]["consistent"], d["after"]["consistent"],
                     d["delta_pp"]["consistent"]))
    print("wrote", os.path.join(a.out, "REPORT.json"))
    sys.exit(0 if doc["ruling"]["verdict"] != "FAIL" else 1)


if __name__ == "__main__":
    main()