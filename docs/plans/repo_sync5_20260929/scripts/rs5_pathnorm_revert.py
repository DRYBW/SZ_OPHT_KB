#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 · 撤销 rs5_pathnorm 对"证据面"的 token 化（范围修正）。
判据（沿 REPOSYNC3 先例=既有 plans 镜像含机器路径字节直收 + T7 门实际 token=患者/项目数据类）：
- 证据面=drsc/seurat/comp_prior/kb/composition（盘上原件镜像+manifest sha 锚定件）→ 从线上 cp 原样重刷（token 撤销）
- wiki 新增面=项目梳理/当前状态/INDEX/directive(追加八) + QUEUE/SYNC_NOTE → 保持 token 化+masked（任务书明令）
执行=对证据面重新 copy 线上原件；wiki 面零改动。"""
import os
import shutil
import subprocess
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
ONL = Path("/mnt/D/EyeKB")

# 1) kb/composition 重刷
dst = STG / "kb/composition"
subprocess.run(["rm", "-rf", str(dst)], check=True)
shutil.copytree(ONL / "kb/composition", dst)

# 2) drsc + comp_prior 重刷
for d in ["drsc_disc_quant_20260928", "comp_prior_20260928"]:
    dd = STG / "docs/plans" / d
    subprocess.run(["rm", "-rf", str(dd)], check=True)
    shutil.copytree(ONL / "plans" / d, dd)

# 3) seurat 重刷（除 data/）
seu_o, seu_s = ONL / "plans/seurat_probe_20260928", STG / "docs/plans/seurat_probe_20260928"
subprocess.run(["rm", "-rf", str(seu_s)], check=True)
seu_s.mkdir(parents=True)
for p in seu_o.rglob("*"):
    rel = p.relative_to(seu_o)
    if rel.parts and rel.parts[0] == "data":
        continue
    if "__pycache__" in str(rel):
        continue
    if p.is_file():
        (seu_s / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, seu_s / rel)

# 4) sha 对线上断言（证据面=原件字节镜像）
import hashlib
def sha(x): return hashlib.sha256(x.read_bytes()).hexdigest()
mism = 0
for d in ["drsc_disc_quant_20260928", "comp_prior_20260928"]:
    for p in (STG / "docs/plans" / d).rglob("*"):
        if p.is_file():
            o = ONL / "plans" / d / p.relative_to(STG / "docs/plans" / d)
            if sha(p) != sha(o): mism += 1; print("MISMATCH", p)
for p in (STG / "kb/composition").rglob("*"):
    if p.is_file():
        o = ONL / "kb/composition" / p.relative_to(STG / "kb/composition")
        if sha(p) != sha(o): mism += 1; print("MISMATCH", p)
for p in seu_s.rglob("*"):
    if p.is_file():
        o = seu_o / p.relative_to(seu_s)
        if sha(p) != sha(o): mism += 1; print("MISMATCH", p)
print(f"evidence-surface refreshed, mismatch-vs-online={mism}")
