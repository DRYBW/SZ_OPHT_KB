#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W2: 疾病×材料矩阵加 development_axis 列 + ROP 占位格 + PDR 条目头显式 adult。

回归锁绕行设计 (任务书纪律1 additive-only + KB2c 套锁 len(rows)==12):
  - rows 12 格: 只**加列** (每行 development_axis 键), 数组长度与既有字段零改动。
  - ROP 占位格: 放新增顶层键 development_axis_reservations —— 立格不填内容,
    且有回归锁在案 (evals/regression_kb3_20260924.py 锁 rows==12+reservations==1),
    未来 ROP 填格须过裁定并同时改两锁 (防静默扩行)。
  - PDR__fibrovascular_membrane.json/md: 加显式 development_stage=adult。
"""
import json
from pathlib import Path

D = Path("/mnt/D/EyeKB/kb/priors/disease")
CARD = "t_5425a7ca"

# ---- 矩阵 JSON ----
mp = D / "_DISEASE_TISSUE_MATRIX.json"
m = json.loads(mp.read_text(encoding="utf-8"))
assert m["schema"] == "eyekb-disease-matrix/1.1" and len(m["rows"]) == 12
for r in m["rows"]:
    assert r.get("organism_stage") == "adult", f"行物种档异常: {r}"
    r.setdefault("development_axis", "adult")  # 任务书 W2: 加列
if "development_axis_reservations" not in m:
    m["development_axis_reservations"] = [{
        "disease": "ROP",
        "material": "developing_retina_vascular",
        "development_axis": "fetal_neonatal",
        "organism_stage": "developing",
        "status": "RESERVED (只立格不填内容)",
        "note": ("早产儿视网膜病变 = 发育轴侧血管增殖病 (PI 红线配套格): 与 PDR 成人膜格严格分离, "
                 "永不并格、永不互为参照 (胎儿/早产儿的这些和成人的即使是一个组织也不对的)。"
                 "填格前提 = 拿到发育期材料/文献锚 (如 ROP 视网膜类器官方或尸材料单细胞——均先过"
                 "发育轴单列纪律); 填格动作须过裁定并同步改回归双锁 (rows/reservations)。"),
        "reserved_by": {"card": CARD, "date": "2026-09-24"}}]
m["kb3_note"] = ("KB3 (t_5425a7ca): 发育轴升为矩阵显式列 development_axis; 现网 12 格全 adult (写死); "
                 "发育轴侧疾病格走 development_axis_reservations 占位 (防与成人格混池, 回归双锁)。")
m["kb3_card"] = CARD
mp.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- 矩阵 MD: 表格加列 (development_axis 与发育档同值=adult, 显式成列防'备注'级待遇) ----
mdp = D / "_DISEASE_TISSUE_MATRIX.md"
t = mdp.read_text(encoding="utf-8")
if "| 疾病 | 组织/材料格 | 发育档 |" in t and "development_axis" not in t.split("\n")[9][:200]:
    lines = t.split("\n")
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("| 疾病 | 组织/材料格 | 发育档 | 状态 | 说明 |"):
            out.append("| 疾病 | 组织/材料格 | 发育档 | development_axis (KB3) | 状态 | 说明 |")
            continue
        if ln.startswith("|---|---|---|---|---|") and lines[i - 1].startswith("| 疾病 |"):
            out.append("|---|---|---|---|---|---|")
            continue
        if ln.startswith("| ") and ln.count("|") == 5 and (" adult |" in ln or "**FILLED" in ln):
            cells = ln.split("|")
            cells.insert(4, " adult ")
            out.append("|".join(cells))
            continue
        out.append(ln)
    t = "\n".join(out)
    if "## KB3 发育轴预留格" not in t:
        t += ("\n## KB3 发育轴预留格 (t_5425a7ca — 只立格不填内容)\n\n"
              "| 疾病 | 材料格 | development_axis | 状态 |\n|---|---|---|---|\n"
              "| ROP (早产儿视网膜病变) | developing_retina_vascular | **fetal_neonatal** | "
              "RESERVED —— 发育轴侧血管增殖病, 与 PDR 成人格永不并池/互参照; 填格前提=发育期数据/文献锚+过裁定 |\n\n"
              "> 架构规则 6 的占位实现: 成人格数组 rows=12 不动 (回归锁), 预留格走独立键 "
              "development_axis_reservations (双锁)。\n")
    mdp.write_text(t, encoding="utf-8")

# ---- PDR 条目: 显式 development_stage=adult ----
pp = D / "PDR__fibrovascular_membrane.json"
p = json.loads(pp.read_text(encoding="utf-8"))
assert p["schema"] == "eyekb-disease/1.1" and p.get("organism_stage") == "adult"
if "development_stage" not in p:
    p["development_stage"] = "adult"
    p["kb3_card"] = CARD
    pp.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
pm = D / "PDR__fibrovascular_membrane.md"
mt = pm.read_text(encoding="utf-8")
if "development_stage=adult" not in mt:
    mt = mt.replace("| 发育档: **organism_stage=adult**",
                    "| 发育档: **organism_stage=adult | development_stage=adult** (KB3 显式)")
    pm.write_text(mt, encoding="utf-8")
print("W2 done: matrix rows+列, ROP 预留格, PDR 头显式")
