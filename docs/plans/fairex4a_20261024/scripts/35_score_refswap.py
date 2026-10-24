#!/usr/bin/env python3
"""STEP 10 — score the refswap arm with the FROZEN engine (score_engine.py, read-only).

Same gold file, same chain, same stage flags as the official X4A table.
usage: 35_score_refswap.py --arm <name> --cw <tsv> --pred <tsv> --tag <refswap|refswap_S2>
"""
import argparse, json, subprocess, os

ap = argparse.ArgumentParser()
ap.add_argument("--arm", required=True)
ap.add_argument("--cw", required=True)
ap.add_argument("--pred", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--outdir", default="/mnt/D/EyeKB/plans/fairex4a_20261024/out")
A = ap.parse_args()

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
ENGINE = "/mnt/D/EyeKB/plans/toolbenchmark_20261009/s2_crosswalk/score_engine.py"
PY = "/home/ubuntu/.conda/envs/eyecsgpt/bin/python" if False else "/home/ubuntu/.conda/envs/pipeline_env/bin/python"

scores = f"{A.outdir}/scores_x4a_{A.tag}.json"
percls = f"{A.outdir}/perclass_x4a_{A.tag}.tsv"
cmd = [PY, ENGINE, "--gold", f"{P}/arms/engine_gold_x4a.tsv", "--pred", A.pred, "--arm", A.arm,
       "--crosswalk", A.cw, "--arm-stage", "adult", "--gold-stage", "adult", "--per-class-out", percls]
print("CMD:", " ".join(cmd), flush=True)
r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
print("rc=", r.returncode, "stderr=", r.stderr.strip()[:400], flush=True)
assert r.returncode == 0, r.stderr
j = json.loads(r.stdout.strip().splitlines()[-1])
j["status"] = "RUN"
j["command"] = " ".join(cmd)
with open(scores, "w") as fh:
    json.dump(j, fh, ensure_ascii=False, indent=1)

# side-by-side with the official A1b reading
off = json.load(open(f"{P}/arms/scores_x4a_A1b_scgpt.json"))
per = {}
with open(percls) as fh:
    next(fh)
    for ln in fh:
        layer, cls, f1 = ln.rstrip("\n").split("\t")
        per.setdefault(layer, {})[cls] = f1
cmpj = {"refswap_arm": A.arm, "tag": A.tag,
        "official_A1b_lineage_macro_f1": off["lineage"]["macro_f1"],
        "official_A1b_ct_macro_f1": off["cell_type"]["macro_f1"],
        "official_A1b_n_invalid_projection": off["n_invalid_projection"],
        "refswap_lineage": j["lineage"], "refswap_ct": j["cell_type"],
        "refswap_n_invalid_projection": j["n_invalid_projection"],
        "refswap_n_unmapped_label": j["n_unmapped_label"], "refswap_eligible": j["qualification"]["eligible_for_formal_table"],
        "lineage_per_class_f1": per.get("lineage", {}), "cell_type_per_class_f1": per.get("cell_type", {}),
        "command": " ".join(cmd)}
with open(f"{A.outdir}/REFSCORE_{A.tag}_vs_official.json", "w") as fh:
    json.dump(cmpj, fh, ensure_ascii=False, indent=1)
print("REFSCORE", json.dumps({"lineage": j["lineage"], "ct": j["cell_type"],
                              "invalid": j["n_invalid_projection"], "unmapped": j["n_unmapped_label"]}), flush=True)
print("per-class lineage:", json.dumps(cmpj["lineage_per_class_f1"], ensure_ascii=False), flush=True)