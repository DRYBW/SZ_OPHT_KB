#!/usr/bin/env python3
"""FAIRX4A / step A2 — score X4A under BOTH rulers with the FROZEN engine (zero changes to it).

For every arm:
  (1) strict rerun   : official cw_x4a.tsv            -> out/verify_scores_x4a_<arm>.json
      GATE: must equal arms/ALL_SCORES.json['x4a'][arm] on every reported quantity, else abort.
  (2) lenient rerun  : frozen cw_x4a_lenient.tsv      -> out/scores_x4a_lenient_<arm>.json + perclass
Then emit out/ARM_A_both_rulers.tsv (strict | lenient | delta) and out/ARM_A_perclass_delta.tsv.
Nothing official is written. Engine invoked exactly as score_x4.py does (same interpreter, same args).
"""
import csv, json, os, subprocess, sys

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
WORK = "/mnt/D/EyeKB/plans/fairex4a_20261024"
OUT = f"{WORK}/out"
ENGINE = "/mnt/D/EyeKB/plans/toolbenchmark_20261009/s2_crosswalk/score_engine.py"
PY = "/home/ubuntu/.conda/envs/pipeline_env/bin/python"
GOLD = f"{P}/arms/engine_gold_x4a.tsv"
CW_OFF = f"{P}/arms/cw_x4a.tsv"
CW_LEN = f"{WORK}/cw_x4a_lenient.tsv"

ARMS = {  # identical to score_x4.py ARMS (stage + pred path), X4A volume only
    "C1": dict(stage="adult", pred=f"{P}/arms/pred_C1_x4a.tsv"),
    "C2": dict(stage="adult", pred=f"{P}/arms/pred_C2_x4a.tsv"),
    "A1a_eyesgpt": dict(stage="adult", pred=f"{P}/arms/pred_A1a_eyesgpt_x4a.tsv"),
    "A1b_scgpt": dict(stage="adult", pred=f"{P}/arms/pred_A1b_scgpt_x4a_raw.tsv"),
    "B1a_celltypist": dict(stage="developing", pred=f"{P}/arms/pred_B1a_celltypist_x4a.tsv"),
    "B1b_celltypist": dict(stage="developing", pred=f"{P}/arms/pred_B1b_celltypist_x4a.tsv"),
}
FIELDS = ["overall_acc", "macro_f1", "coverage", "selective_acc"]


def run(arm, cw, outjson, perclass=None):
    cmd = [PY, ENGINE, "--gold", GOLD, "--pred", ARMS[arm]["pred"], "--arm", arm,
           "--crosswalk", cw, "--arm-stage", ARMS[arm]["stage"], "--gold-stage", "adult"]
    if perclass:
        cmd += ["--per-class-out", perclass]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        sys.exit(f"CONTRACT_ERROR {arm} {cw}: rc={r.returncode} {r.stderr[:600]}")
    j = json.loads(r.stdout.strip().splitlines()[-1])
    json.dump(j, open(outjson, "w"), ensure_ascii=False, indent=1)
    return j


official = json.load(open(f"{P}/arms/ALL_SCORES.json"))["x4a"]
rows, percl_rows = [], []
all_ok = True
for arm in ARMS:
    v = run(arm, CW_OFF, f"{OUT}/verify_scores_x4a_{arm}.json")
    o = official[arm]
    diffs = []
    for layer in ("lineage", "cell_type"):
        if o.get(layer) is None:
            if v.get(layer) is not None:
                diffs.append(f"{layer}: official NA but rerun {v.get(layer)}")
            continue
        for k in FIELDS:
            if v[layer].get(k) != o[layer].get(k):
                diffs.append(f"{layer}.{k}: official {o[layer].get(k)} vs rerun {v[layer].get(k)}")
    for k in ("n_gold", "n_abstain", "n_missing_pred", "n_unmapped_label",
              "n_suspended_mapping", "n_invalid_projection"):
        if v.get(k) != o.get(k):
            diffs.append(f"{k}: official {o.get(k)} vs rerun {v.get(k)}")
    ok = not diffs
    all_ok &= ok
    print(f"GATE strict-rerun {arm:16s} {'EXACT' if ok else 'MISMATCH: ' + '; '.join(diffs[:5])}", flush=True)

    L = run(arm, CW_LEN, f"{OUT}/scores_x4a_lenient_{arm}.json",
            f"{OUT}/perclass_x4a_lenient_{arm}.tsv")
    print(f"  lenient {arm:16s} lineage.macro_f1 {o['lineage']['macro_f1']} -> {L['lineage']['macro_f1']}"
          f" | invalid {o['n_invalid_projection']} -> {L['n_invalid_projection']}", flush=True)

    row = [arm]
    for lay in ("lineage", "cell_type"):
        for k in FIELDS:
            row.append("" if o.get(lay) is None else o[lay][k])        # strict
    row.append(o["n_invalid_projection"]); row.append(o["n_abstain"])
    for lay in ("lineage", "cell_type"):
        for k in FIELDS:
            row.append("" if L.get(lay) is None else L[lay][k])        # lenient
    row.append(L["n_invalid_projection"]); row.append(L["n_abstain"])
    for lay in ("lineage", "cell_type"):
        row.append("" if (o.get(lay) is None or L.get(lay) is None) else
                   round(L[lay]["macro_f1"] - o[lay]["macro_f1"], 4))
    rows.append(row)

    # per-class lineage F1 delta
    for src, tag in ((f"{P}/arms/perclass_x4a_{arm}.tsv", "strict"),
                     (f"{OUT}/perclass_x4a_lenient_{arm}.tsv", "lenient")):
        if not os.path.exists(src):
            continue
        for r in csv.DictReader(open(src), delimiter="\t"):
            if r["layer"] != "lineage":
                continue
            percl_rows.append([arm, r["class"], r["f1"], tag])

hdr = (["arm"] +
       [f"strict_lineage_{k}" for k in FIELDS] + [f"strict_ct_{k}" for k in FIELDS] +
       ["strict_n_invalid", "strict_n_abstain"] +
       [f"lenient_lineage_{k}" for k in FIELDS] + [f"lenient_ct_{k}" for k in FIELDS] +
       ["lenient_n_invalid", "lenient_n_abstain", "delta_lineage_macro_f1", "delta_ct_macro_f1"])
with open(f"{OUT}/ARM_A_both_rulers.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(hdr); w.writerows(rows)

# long-format per-class lineage F1 (strict vs lenient)
per_map = {}
for arm, cls, f1, tag in percl_rows:
    per_map.setdefault((arm, cls), {})[tag] = f1
with open(f"{OUT}/ARM_A_perclass_lineage_delta.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["arm", "lineage_class", "f1_strict", "f1_lenient", "delta"])
    for (arm, cls), d in sorted(per_map.items()):
        s, l = d.get("strict"), d.get("lenient")
        w.writerow([arm, cls, s, l, "" if (s in (None, "") or l in (None, "")) else round(float(l) - float(s), 4)])

print("WROTE", f"{OUT}/ARM_A_both_rulers.tsv")
print("STRICT_RERUN_GATE", "ALL_EXACT" if all_ok else "MISMATCH")
print("ARM_A_SCORE_DONE")
sys.exit(0 if all_ok else 9)
