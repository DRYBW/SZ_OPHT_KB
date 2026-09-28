#!/usr/bin/env python3
"""gate3 FAIL 归因: 残差基因 × 备选104 收益覆盖 + 必补闭集里哪些篇本应覆盖它们"""
import re, csv, json
PLAN="/mnt/D/EyeKB/plans/rag_fix_20260928"
res=[r.split("\t") for r in open(f"{PLAN}/out/GATE3_residual_units.tsv").read().splitlines()[1:]]
resg={r[0] for r in res}
txt=open("/mnt/D/EyeKB/plans/rag_gap_20260928/TIER_A_approval_list.md").read()
must=txt.split("## 必补")[1].split("## 备选")[0]
alt=txt.split("## 备选")[1]
alt_pairs=set(re.findall(r"([A-Z0-9]+)\((retina|membrane|face|lacrimal|kb9)\)",alt))
must_pairs=set(re.findall(r"([A-Z0-9]+)\((retina|membrane|face|lacrimal|kb9)\)",must))
res_units={(r[0],r[1]) for r in res}
print("residual units:",len(res_units))
alt_c=sorted(u for u in res_units if u in alt_pairs)
must_c=sorted(u for u in res_units if u in must_pairs)
none=sorted(u for u in res_units if u not in alt_pairs and u not in must_pairs)
print("\n残差单元中 [必补表曾声称覆盖]=下载了但新文本未提及该符号 (措辞变体/缩写可能):",len(must_c))
for u in must_c: print("  ",u)
print("\n残差单元中 [仅备选104覆盖] (本轮按任务书不下):",len(alt_c))
for u in alt_c: print("  ",u)
print("\n残差单元中 [任何表都没挂过]:",len(none))
for u in none: print("  ",u)
# 检查 must_c 的基因在 64 篇新文本里到底有没有任何大小写变体
genes={}
import io
for line in open(f"{PLAN}/work/chunks_ra_raw.jsonl",encoding="utf-8"):
    d=json.loads(line)
    for g,_ in must_c: genes.setdefault(g,0)
# quick token scan
for g in sorted({g for g,_ in must_c}):
    pat=re.compile(r"\b"+re.escape(g)+r"\b",re.I)
    hits=0
    for line in open(f"{PLAN}/work/chunks_ra_raw.jsonl",encoding="utf-8"):
        if pat.search(line): hits+=1
    if hits: print(f"NOTE: {g} 实有 {hits} 行新文本含符号 — gate3 应命中, 请核查")
