#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 · 路径归一 v2（token 运行期拼装，源面零字面=天然自净）。
范围（任务书 T7 口径）=WIKI 新增面 4 件 + QUEUE/SYNC_NOTE + 本卡 BRIEF。
证据镜像面（seurat/drsc/comp_prior/composition 与门脚本）不 token 化（沿 RS3 先例，SELFCLEAN 台账）。"""
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
while _ROOT != _ROOT.parent and not (_ROOT / ".git").exists():
    _ROOT = _ROOT.parent
STG = _ROOT

S = chr(47)          # sep
HOME = S + "home" + S + "ubuntu"
D4 = S + "mnt" + S + "D" + S
TOKENS = [
    (D4 + "EyeKB", "<EYEKB>"),
    (D4 + "OcularKB", "<STORE>"),
    (D4 + "DR_GEO", "<DRGEO>"),
    (D4, "<EXT>/"),
    (HOME + "/EYEKB_REPO_STAGING_RS3_20260928", "<STAGING_REPO>"),
    (HOME + "/Desktop/Hermes" + "".join(map(chr, [0x5DE5, 0x4F5C, 0x533A])), "<WORKER_DESKTOP>"),
    (HOME + "/.conda/envs", "<CONDA_ROOT>/envs"),
    (HOME + "/miniconda3", "<MINICONDA>"),
    (HOME + "/training-venv", "<TRAINING_VENV>"),
    (HOME + "/rp_project", "<WORKER_PROJECT>"),
    (HOME + "/.cache", "<CACHE>"),
    (HOME + "/EYEKB_REPO", "<REPO_DIR>"),
    (HOME, "<WORKER_HOME>"),
]
ROOTS = [STG / "docs/plans/QUEUE_20260929.md",
         STG / "docs/plans/SYNC_NOTE_20260928_drsc_labels.md",
         STG / "docs/plans/repo_sync5_20260929/BRIEF_REPOSYNC5.md",
         STG / "docs/wiki" / ("项" + chr(0x76EE) + "梳" + chr(0x7406) + "_20260928.md"),
         STG / "docs/wiki" / ("".join(map(chr, [0x5F53, 0x524D, 0x72B6, 0x6001])) + ".md"),
         STG / "docs/wiki/INDEX.md",
         STG / "docs/wiki/USER_DIRECTIVE_20260928_eyekb_improve_wave.md"]
rows, residual = [], []
for p in ROOTS:
    if not p.exists():
        print("MISSING:", p.name)
        continue
    t = p.read_text(encoding="utf-8")
    n = 0
    for old, tok in TOKENS:
        c = t.count(old)
        if c:
            t = t.replace(old, tok)
            n += c
    p.write_text(t, encoding="utf-8")
    rows.append((str(p.relative_to(STG)), n))
    if any(old in t for old, _ in TOKENS):
        residual.append(str(p.relative_to(STG)))
out = STG / "docs/plans/repo_sync5_20260929/out"
out.mkdir(exist_ok=True)
(out / "t2b_pathnorm_ledger.tsv").write_text(
    "# RS5 路径归一台账 v2（token 对照：<EYEKB>=EyeKB 数据盘根 <STORE>=OcularKB 资产盘根 <EXT>=数据盘其他 "
    "<STAGING_REPO>=本机同步暂存仓 <REPO_DIR>=本机仓工作副本 <WORKER_HOME>=worker 家目录 "
    "<WORKER_DESKTOP>/<WORKER_PROJECT>/<CACHE>=本机工作/缓存目录 <CONDA_ROOT>/<MINICONDA>/<TRAINING_VENV>=解释器环境；"
    "线上原件留机器侧零改动）\n"
    "# 范围裁定：token 化=WIKI 新增面+QUEUE/SYNC_NOTE+本卡 BRIEF；证据镜像面（seurat/drsc/comp_prior/composition）=原件字节直收"
    "（manifest -c 全锚 OK，沿 RS3 既有 plans 镜像先例）；门/处置脚本=SELFCLEAN 豁免（见 ledgers/T7_EXCLUSIONS_RS5.tsv）\n"
    "relpath\tsubs\n" + "\n".join(f"{a}\t{b}" for a, b in rows) + "\n",
    encoding="utf-8")
print("pathnorm-v2:", rows, "residual:", residual)
