#!/usr/bin/env python3
"""STEP 11 — consolidate the numbers from the artifacts on disk (no hand-typed statistics).

Emits:
  out/C_table.tsv                  the closing table (four settings, one instrument)
  out/B_arm_comparison.tsv         official A1b X4A  vs  refswap  vs  refswap_S2 (if present)
  out/REPORT_NUMBERS.json          every figure the report quotes, with its source file
"""
import json, os, csv, glob
import numpy as np

R = "/mnt/D/EyeKB/plans/fairex4a_20261024"
O = f"{R}/out"; W = f"{R}/work"
P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
out = {}


def jload(p):
    with open(p) as fh:
        return json.load(fh)


official = jload(f"{P}/arms/ALL_SCORES.json")["x4a"]
out["official_x4a"] = official
armA = {}
with open(f"{O}/ARM_A_both_rulers.tsv") as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        armA[r["arm"]] = r
out["arm_A_both_rulers_source"] = f"{O}/ARM_A_both_rulers.tsv"

# --- C table ---
OPENBOOK = {   # quoted from plans/toolbenchmark_20261009/TOOL_ACCESS_MATRIX.md (lines 23-31) via PREREG §4
    "A1a_eyesgpt": ("Microglia 79/79 = 100% | RPE 29/48 = 60.4%", "author eval slices, n=79/48, open-book, not a capability reading"),
    "A1b_scgpt": ("Microglia 79/79 = 100% | RPE 48/48 = 100%", "author eval slices, n=79/48, open-book, not a capability reading"),
    "B1a_celltypist": ("Microglia 78/79 = 98.7%", "install smoke test, n=79, open-book, not a capability reading"),
    "B1b_celltypist": ("Microglia 55/79 = 69.6%", "install smoke test, n=79, open-book, not a capability reading"),
    "C1": ("NA", "no author slice in register"),
    "C2": ("NA", "no author slice in register"),
}
with open(f"{O}/C_table.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["arm", "own_openbook_slice(quoted)", "openbook_caveat", "X4A_strict_lineage_macro_f1",
                "X4A_lenient_lineage_macro_f1", "X4B_super_lineage_macro_f1", "source"])
    for arm in ["A1a_eyesgpt", "A1b_scgpt", "B1a_celltypist", "B1b_celltypist", "C1", "C2"]:
        ob, caveat = OPENBOOK[arm]
        w.writerow([arm, ob, caveat,
                    official[arm]["lineage"]["macro_f1"],
                    armA[arm]["lenient_lineage_macro_f1"],
                    jload(f"{P}/arms/scores_x4b_super_{arm}.json")["lineage"]["macro_f1"]
                    if os.path.exists(f"{P}/arms/scores_x4b_super_{arm}.json") else "NA",
                    f"{P}/arms/ALL_SCORES.json ; {O}/ARM_A_both_rulers.tsv"])
out["C_table"] = f"{O}/C_table.tsv"

# --- B arm ---
b = {"official_A1b": official["A1b_scgpt"]}
rf = f"{O}/scores_x4a_refswap.json"
if os.path.exists(rf):
    b["refswap"] = jload(rf)
    b["refswap_vs_official"] = jload(f"{O}/REFSCORE_refswap_vs_official.json")
    b["refvote_ledger"] = jload(f"{O}/REFVOTE_refswap_ledger.json")
    b["ref_build_ledger"] = jload(f"{W}/ref_build_ledger.json")
rf2 = f"{O}/scores_x4a_refswap_S2.json"
if os.path.exists(rf2):
    b["refswap_S2"] = jload(rf2)
    b["refswap_S2_vs_official"] = jload(f"{O}/REFSCORE_refswap_S2_vs_official.json")
    b["refvote_ledger_S2"] = jload(f"{O}/REFVOTE_refswap_S2_ledger.json")
b0 = f"{O}/B0_reproduction_gate.json"
if os.path.exists(b0):
    b["B0_gate"] = jload(b0)
out["B_arm"] = b

with open(f"{O}/B_arm_comparison.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["setting", "lineage_overall_acc", "lineage_macro_f1", "lineage_coverage", "lineage_selective_acc",
                "ct_overall_acc", "ct_macro_f1", "ct_coverage", "ct_selective_acc", "n_invalid_projection",
                "n_unmapped", "label"])
    rows = [("A1b X4A official (our retinal 189k reference)", b["official_A1b"]),
            ("A1b X4A refswap (reference rebuilt with the gold's own classes)", b.get("refswap")),
            ("A1b X4A refswap_S2 (same + Mueller->astrocyte)", b.get("refswap_S2"))]
    for label, r in rows:
        if not r:
            continue
        ct = r.get("cell_type") or {}
        w.writerow([r.get("arm", "A1b_scgpt"), r["lineage"]["overall_acc"], r["lineage"]["macro_f1"],
                    r["lineage"]["coverage"], r["lineage"]["selective_acc"],
                    ct.get("overall_acc", "NA"), ct.get("macro_f1", "NA"), ct.get("coverage", "NA"),
                    ct.get("selective_acc", "NA"), r["n_invalid_projection"], r["n_unmapped_label"], label])

# --- within-class vs cross-class: how the previously unreachable classes came back ---
pf = f"{O}/perclass_x4a_refswap.tsv"
if os.path.exists(pf):
    per = {}
    with open(pf) as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            per.setdefault(r["layer"], {})[r["class"]] = r["f1"]
    out["refswap_per_class"] = per
    off = {}
    with open(f"{P}/arms/perclass_x4a_A1b_scgpt.tsv") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            off.setdefault(r["layer"], {})[r["class"]] = r["f1"]
    out["official_per_class"] = off

# --- experiment noise floor (run-to-run) ---
nf = f"{O}/INSTRUMENT_noise_floor.json"
if os.path.exists(nf):
    out["instrument_noise_floor"] = jload(nf)

json.dump(out, open(f"{O}/REPORT_NUMBERS.json", "w"), ensure_ascii=False, indent=1)
print("REPORT_NUMBERS_OK", list(out))
print("C table at", out["C_table"])