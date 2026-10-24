#!/usr/bin/env python3
"""STEP 11c — run-to-run spread of the two headline readings, measured with the frozen engine.

Scores (all against the frozen X4A gold, engine read-only):
  strict   : our run1 / run2 query embeddings vs the FROZEN official reference index
  refswap  : our run1 / run2 query embeddings vs the rebuilt reference index
Output: out/SPREAD_strict_and_refswap.json
"""
import json, subprocess
R = "/mnt/D/EyeKB/plans/fairex4a_20261024"
O, W = f"{R}/out", f"{R}/work"
P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
ENGINE = "/mnt/D/EyeKB/plans/toolbenchmark_20261009/s2_crosswalk/score_engine.py"
PY = "/home/ubuntu/.conda/envs/pipeline_env/bin/python"

JOBS = [
    ("strict_run1", "A1b_scgpt", f"{P}/arms/cw_x4a.tsv", f"{O}/pred_A1b_scgpt_x4a_rerun.tsv",
     f"{P}/arms/engine_gold_x4a.tsv"),
    ("strict_run2", "A1b_scgpt", f"{P}/arms/cw_x4a.tsv", f"{O}/pred_A1b_scgpt_x4a_run2_raw.tsv",
     f"{P}/arms/engine_gold_x4a.tsv"),
    ("refswap_run1", "A1b_scgpt_refswap", f"{O}/cw_x4a_refswap.tsv", f"{O}/pred_A1b_scgpt_x4a_refswap_raw.tsv",
     f"{P}/arms/engine_gold_x4a.tsv"),
    ("refswap_run2", "A1b_scgpt_refswap", f"{O}/cw_x4a_refswap.tsv", f"{O}/pred_A1b_scgpt_x4a_refswap_run2_raw.tsv",
     f"{P}/arms/engine_gold_x4a.tsv"),
]
out = {}
for tag, arm, cw, pred, gold in JOBS:
    cmd = [PY, ENGINE, "--gold", gold, "--pred", pred, "--arm", arm, "--crosswalk", cw,
           "--arm-stage", "adult", "--gold-stage", "adult", "--per-class-out", f"{O}/perclass_x4a_{tag}.tsv"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    assert r.returncode == 0, (tag, r.stderr[:300])
    j = json.loads(r.stdout.strip().splitlines()[-1])
    j["command"] = " ".join(cmd)
    j["status"] = "RUN"
    out[tag] = j
    print(tag, "lineage_macro_f1", j["lineage"]["macro_f1"], "ct_macro_f1",
          (j["cell_type"] or {}).get("macro_f1"), "invalid", j["n_invalid_projection"], flush=True)
json.dump(out, open(f"{O}/SPREAD_strict_and_refswap.json", "w"), ensure_ascii=False, indent=1)
print("SPREAD_OK")