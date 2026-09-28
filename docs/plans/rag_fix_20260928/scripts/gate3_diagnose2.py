#!/usr/bin/env python3
"""17 个"任何表都没挂过"残差的根因: RAGGAP s5 检索基因→候选论文映射里到底有没有给这些基因选过必补论文"""
import csv, json, re
from collections import defaultdict
RAGGAP="/mnt/D/EyeKB/plans/rag_gap_20260928"
PLAN="/mnt/D/EyeKB/plans/rag_fix_20260928"
closed=set(l.strip() for l in open(f"{PLAN}/out/closed_set_pmids.txt") if l.strip())

# gene → (top hit papers) 从 s5 检查表
genemap=defaultdict(list)
try:
    with open(f"{RAGGAP}/out/epmc_gene_check.tsv",encoding="utf-8") as f:
        rd=csv.DictReader(f,delimiter="\t")
        cols=rd.fieldnames
        print("epmc_gene_check cols:",cols)
        for r in rd:
            genemap[r[cols[0]].upper()].append(r)
    with open(f"{RAGGAP}/out/epmc_gene_check_extra.tsv",encoding="utf-8") as f:
        rd=csv.DictReader(f,delimiter="\t")
        cols=rd.fieldnames
        print("extra cols:",cols)
        for r in rd:
            genemap[r[cols[0]].upper()].append(r)
except FileNotFoundError as e:
    print("missing:",e)

res17=["ATP8B4","CALD1","CDH8","CST1","CST4","FAM135A","FBXL7","FCER1G","GPR143","GRM5",
       "LILRB2","LMOD1","LRRTM3","MUC7","PTPRK","SAMSN1","SHISA6"]
for g in res17:
    rows=genemap.get(g,[])
    if not rows:
        print(f"{g}: 不在 s5 检查表")
        continue
    r0=rows[0]
    s=json.dumps(r0)[:220]
    print(f"{g}: {s}")
