#!/usr/bin/env python3
"""STEP 11e — vote-confidence comparison across the settings (from the pred files on disk).
Output: out/VOTE_FRAC_comparison.json  (no search; pure read of frozen+new pred files)"""
import json
import numpy as np

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
O = "/mnt/D/EyeKB/plans/fairex4a_20261024/out"
FILES = {
    "official_A1b_x4a": f"{P}/arms/pred_A1b_scgpt_x4a_raw.tsv",
    "our_rerun_run1": f"{O}/pred_A1b_scgpt_x4a_rerun.tsv",
    "our_rerun_run2": f"{O}/pred_A1b_scgpt_x4a_run2_raw.tsv",
    "refswap_run1": f"{O}/pred_A1b_scgpt_x4a_refswap_raw.tsv",
    "refswap_run2": f"{O}/pred_A1b_scgpt_x4a_refswap_run2_raw.tsv",
    "refswap_S2": f"{O}/pred_A1b_scgpt_x4a_refswap_S2_raw.tsv",
}
res = {}
for k, p in FILES.items():
    v = []
    labs = {}
    with open(p) as fh:
        next(fh)
        for ln in fh:
            c, l, f = ln.rstrip("\n").split("\t")
            v.append(float(f)); labs[l] = labs.get(l, 0) + 1
    v = np.array(v)
    res[k] = {"file": p, "n": len(v), "vote_frac_mean": round(float(v.mean()), 4),
              "vote_frac_median": round(float(np.median(v)), 4),
              "frac_at_1.0": round(float((v == 1.0).mean()), 4),
              "n_below_0.5": int((v < 0.5).sum()), "n_distinct_labels": len(labs)}
json.dump(res, open(f"{O}/VOTE_FRAC_comparison.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))