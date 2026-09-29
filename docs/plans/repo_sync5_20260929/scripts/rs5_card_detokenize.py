#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 · 本卡目录去 token 化（作用域修正 #2）。
背景：rs5_pathnorm.py 首跑把 ROOTS 里的"本卡目录"一并替换了，其中 rs5_gates.py /
rs5_wiki_mask.py / v4-copy 是在 pathnorm 之后新写入/被覆写的件，也被波及——脚本体内
机器路径为功能字面（引擎默认值/证据面扫描根），必须还原。
豁免：rs5_pathnorm.py 的 SUBS 映射定义与台账 token 对照行=定义本体，保留不还原。
本脚本自身含 token 字面=self-clean 豁免（终扫登记）。"""
from pathlib import Path

CARD = Path(__file__).resolve().parent
REV = [
    ("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928", "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928"),
    ("/home/ubuntu/Desktop/Hermes工作区", "/home/ubuntu/Desktop/Hermes工作区"),
    ("/home/ubuntu/rp_project", "/home/ubuntu/rp_project"),
    ("/home/ubuntu/training-venv", "/home/ubuntu/training-venv"),
    ("/home/ubuntu/.conda", "/home/ubuntu/.conda"),
    ("/home/ubuntu/miniconda3", "/home/ubuntu/miniconda3"),
    ("/home/ubuntu", "/home/ubuntu"),
    ("/home/ubuntu/.cache", "/home/ubuntu/.cache"),
    ("/mnt/D/EyeKB", "/mnt/D/EyeKB"),
    ("/mnt/D/OcularKB", "/mnt/D/OcularKB"),
    ("/mnt/D/DR_GEO", "/mnt/D/DR_GEO"),
    ("/mnt/D/", "/mnt/D/"),
]
KEEP = {CARD / "scripts/rs5_pathnorm.py", CARD / "out/t2b_pathnorm_ledger.tsv", Path(__file__).resolve()}
n = 0
for p in CARD.rglob("*"):
    if not p.is_file() or p in KEEP or "__pycache__" in str(p):
        continue
    t0 = p.read_text(encoding="utf-8", errors="ignore")
    t = t0
    for a, b in REV:
        t = t.replace(a, b)
    if t != t0:
        p.write_text(t, encoding="utf-8")
        n += 1
print("detokenized files:", n)
