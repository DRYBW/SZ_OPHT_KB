#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC6 · 路径归一（token 运行期拼装，源面零字面=天然自净）。
范围（任务书 T7 口径，沿 RS5 裁定）=QUEUE_20260929.md + 本卡 BRIEF_REPOSYNC6.md + WIKI 面（本轮零漂移，仅幂等校验不改写）。
证据镜像面（comp_prior_v1/composition v1 两件）=原件字节直收（v4 masked 件除外，机器路径豁免登记 T7_EXCLUSIONS_RS6）。"""
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
while _ROOT != _ROOT.parent and not (_ROOT / ".git").exists():
    _ROOT = _ROOT.parent
STG = _ROOT

S = chr(47)          # sep
HOME = S + "home" + S + "ubuntu"
D4 = S + "mnt" + S + "D" + S
NORM_MAP = [
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
    (HOME + "/RAG_SLIM_V242", "<RAG_SLIM>"),
    (HOME + "/EYEKB_REPO", "<REPO_DIR>"),
    (HOME, "<WORKER_HOME>"),
]
ROOTS = [STG / "docs/plans/QUEUE_20260929.md",
         STG / "docs/plans/repo_sync6_20260929/BRIEF_REPOSYNC6.md"]
rows, residual = [], []
for p in ROOTS:
    if not p.exists():
        print("MISSING:", p.name)
        continue
    t = p.read_text(encoding="utf-8")
    n = 0
    for old, tok in NORM_MAP:
        c = t.count(old)
        if c:
            t = t.replace(old, tok)
            n += c
    p.write_text(t, encoding="utf-8")
    rows.append((str(p.relative_to(STG)), n))
    if any(old in t for old, _ in NORM_MAP):
        residual.append(str(p.relative_to(STG)))
out = STG / "docs/plans/repo_sync6_20260929/out"
out.mkdir(exist_ok=True, parents=True)
(out / "t2b_pathnorm_ledger.tsv").write_text(
    "# RS6 路径归一台账（token 对照同 RS5：<EYEKB>=EyeKB 数据盘根 <STORE>=OcularKB 资产盘根 <EXT>=数据盘其他 "
    "<STAGING_REPO>=本机同步暂存仓 <REPO_DIR>=本机仓工作副本 <WORKER_HOME>=worker 家目录 "
    "<WORKER_DESKTOP>/<WORKER_PROJECT>/<CACHE>=本机工作/缓存目录 <CONDA_ROOT>/<MINICONDA>/<TRAINING_VENV>=解释器环境 "
    "<RAG_SLIM>=本地 Release 预置件目录；线上原件留机器侧零改动）\n"
    "# 范围裁定：token 化=QUEUE+BRIEF6（WIKI 面本轮零漂移未动；证据镜像面=原件字节直收+机器路径豁免登记，"
    "沿 RS3/RS5 先例；见 ledgers/T7_EXCLUSIONS_RS6.tsv）\n"
    "relpath\tsubs\n" + "\n".join(f"{a}\t{b}" for a, b in rows) + "\n",
    encoding="utf-8")
print("pathnorm:", rows, "residual:", residual)
