#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kbgov_verdicts.py — top1 中心判词精化 + 过杀账汇总（描述性层，注册门数值不改）。
读 data/kbgov_ab_lesion.tsv + out/kbgov_regression_shift.tsv，产：
  out/kbgov_lesion_verdicts.tsv（逐簇×变体：A top1 条目 → B 下状态）
  out/kbgov_overkill_ledger.json（34 位移 top1/非top1 拆分、7 正确名伤亡、鼠侧账、门汇总）
  out/kbgov_gates_final.json（逐变体两门判定 + 入围结论）"""
import json, csv

OUT = "/mnt/D/EyeKB/plans/kb_gov_20260928"
VARIANTS = ("B1", "B2", "B3", "B4", "B5")
les = list(csv.DictReader(open(f"{OUT}/data/kbgov_ab_lesion.tsv"), delimiter="\t"))

with open(f"{OUT}/out/kbgov_lesion_verdicts.tsv", "w") as f:
    f.write("cluster_id\ttruth\tA_top1\tA_top1_shared\t" + "\t".join(
        f"{v}_status\t{v}_top1_after" for v in VARIANTS) + "\n")
    verdicts = {}
    for r in les:
        A = json.loads(r["A_ranking"])
        truth = r["truth"]
        top1 = A[0] if A else None
        row = {"cluster_id": r["cluster_id"], "truth": truth,
               "A_top1": top1["cell_type"] + f"(n={top1['n_shared']},shared={','.join(top1['shared'])})"
               if top1 else "EMPTY", "A_top1_shared": ",".join(A[0]["shared"]) if A else ""}
        vrec = {}
        for v in VARIANTS:
            named = json.loads(r[f"{v}_named"])
            flags = set(json.loads(r.get(f"{v}_flags") or "[]"))
            qual = r.get(f"{v}_qualified") == "True"
            tier = r[f"{v}_tier"]
            if not top1:
                st = "A_no_artifact"
            elif top1["cell_type"] not in named:
                st = "refused" if (tier == "mouse_confirmed" and not named) else "removed"
            elif top1["cell_type"] in flags:
                st = "kept_flagged"
            elif qual:
                st = "kept_annotated"
            else:
                st = "kept_bare"
            row[f"{v}_status"] = st
            row[f"{v}_top1_after"] = named[0] if named else "NONE"
            vrec[v] = st
        verdicts[r["cluster_id"]] = vrec
        f.write("\t".join(str(row.get(k, "")) for k in row) + "\n")

# ---- 过杀账 ----
shift = list(csv.DictReader(open(f"{OUT}/out/kbgov_regression_shift.tsv"), delimiter="\t"))
b23 = [s for s in shift if s["variant"] in ("B2", "B3")]
top1_shift, mid_shift = [], []
for s in b23:
    A = json.loads(s["A"]); B = json.loads(s["B"])
    if (A[0] if A else None) != (B[0] if B else None):
        top1_shift.append(s["cluster_id"])
    else:
        mid_shift.append(s["cluster_id"])
metrics = json.load(open(f"{OUT}/out/kbgov_ab_metrics.json"))
mouse = list(csv.DictReader(open(f"{OUT}/out/kbgov_mouse_side.tsv"), delimiter="\t"))
mouse_no_named = {v: sum(1 for r in mouse if r[f"{v}_named"] == "[]") for v in VARIANTS}
correct_casualty = metrics["correct_name_casualty"]

# ---- 门汇总（PREREG §5 判词映射：refused/removed/kept_flagged=清零档；kept_annotated=物种化档；kept_bare=未达）----
CLEARED = {"refused", "removed", "kept_flagged"}
QUALIFIED = CLEARED | {"kept_annotated", "A_no_artifact"}
gates = {}
for v in VARIANTS:
    les_clear = {cid: st[v] for cid, st in verdicts.items()
                 if cid not in ("Q5b::35", "Q2::22")}
    mouse_res = {"cleared": sum(1 for st in les_clear.values() if st in CLEARED),
                 "qualified_only": sum(1 for st in les_clear.values() if st == "kept_annotated"),
                 "not": sum(1 for st in les_clear.values() if st not in QUALIFIED)}
    q22 = verdicts["Q2::22"][v]
    gates[v] = {
        "lesion_mouse": mouse_res,
        "lesion_mouse_pass(lenient)": mouse_res["not"] == 0,
        "lesion_mouse_strict_cleared": mouse_res["cleared"],
        "lesion_Q2x22": q22,
        "lesion_Q2x22_constrained": q22 in CLEARED,
        "regression_shift_n": metrics["shift_counts"][v],
        "regression_shift_rate": metrics["shift_rate"][v],
        "regression_gate": metrics["gate_5pct"][v],
        "correct_name_casualty_n": len(correct_casualty[v]),
        "mouse_side_all_refused_n": mouse_no_named[v],
    }
    shortlist = (gates[v]["lesion_mouse_pass(lenient)"]
                 and gates[v]["lesion_Q2x22_constrained"]
                 and gates[v]["regression_gate"] == "PASS")
    gates[v]["入围"] = shortlist

out = {"top1_shift_B2B3": sorted(set(top1_shift)), "top1_shift_n": len(set(top1_shift)),
       "midlist_only_shift_n": len(set(mid_shift)), "midlist_only_shift": sorted(set(mid_shift)),
       "correct_name_casualty": correct_casualty,
       "flag_casualty_note": "casualty 计数=truth==A_top1 且 B 剥夺具名（removed 或 kept_flagged）；"
                             "B1/B4/B5 的 7 簇为 kept_flagged（具名资格受限、条目保留、序不变）",
       "lesion_status": verdicts, "gates": gates}
json.dump(out, open(f"{OUT}/out/kbgov_overkill_ledger.json", "w"), indent=1, ensure_ascii=False)
json.dump(gates, open(f"{OUT}/out/kbgov_gates_final.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(gates, indent=1, ensure_ascii=False))
print("top1-shift(B2/B3 描述列) n=", len(set(top1_shift)), " mid-only n=", len(set(mid_shift)))
