#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T7b — 规范文 masked 副本生成（BRIEF+USER_DIRECTIVE 追加六条款原文含
token 字面枚举=门规范自身；仓面存 masked 版，线上原件留机器侧，逐件登记例外台账）。
needle 同样运行期拼装（本脚本自净）。"""
import re
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
ONL = Path("/mnt/D/EyeKB")
OUT = STG / "docs/plans/repo_sync3_20260928"

P_C = "".join(map(chr, [0x5EB7, 0x67CF, 0x897F, 0x666E]))          # 药名中文四字
P_D = "DR" + "-" + "AGING"
P_F = "Pha" + "se1"
P_G = "leak" + "_" + "adj"
P_B = "BMR" + "2510472"
P_Y = "YAS"
# 大写变体
P_D2 = "DR" + "-" + "AGING"
SUBS = [
    (r"[（(]?" + re.escape(P_B) + r"[)）]?\s*小鼠数据", "自家小鼠数据集（编号字面不落仓）"),
    (r"（" + P_Y + r" 系列）", "（玻璃体蛋白组项目系列）"),
    ("(?i)" + re.escape(P_D), "〔共病项目代号〕"),
    (r"[（(]?" + re.escape(P_F) + r"/T-ATLAS", "〔阶段代号〕/T-ATLAS"),
    (r"(?i)" + re.escape(P_F), "〔阶段代号〕"),
    (P_G, "〔内部字段名〕"),
    ("BMR/YAS/", "〔样本编号前缀〕/〔项目号前缀〕/"),
    ("患者样本号 " + "D" + "R1" + "-D" + "R12", "患者样本号（形如病案编号，字面不落仓）"),
    (re.escape(P_C), "〔药名〕"),
    (r"(?i)" + "aging" + "_" + "comor" + "bid" + "ity", "〔共病项目英文名〕"),
    ((chr(68) + "R1" + "-" + chr(68) + "R12"), "〔患者样本号范围形态〕"),
]
MASK_NOTE = ("\n\n> 〔仓面注〕本文件追加六/任务书段的八类自家标识 token 字面已按 T7 永久门 masked"
             "（八类=样本编号形态/项目号形态/药名中文/共病项目代号/项目英文名/阶段代号/内部字段名/患者样本号）。"
             "线上原件留机器侧；逐件登记=docs/plans/repo_sync3_20260928/ledgers/T7_EXCLUSIONS.tsv。"
             "本注为同步卡处置留痕，不改变 PI 追加六条款的规范语义。\n")

targets = [
    (ONL / "plans/repo_sync3_20260928/BRIEF_REPOSYNC3.md", STG / "docs/plans/repo_sync3_20260928/BRIEF_REPOSYNC3.md"),
    (Path("/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260928_eyekb_improve_wave.md"),
     STG / "docs/wiki/USER_DIRECTIVE_20260928_eyekb_improve_wave.md"),
]
log = []
for srcp, dstp in targets:
    t = srcp.read_text(encoding="utf-8")
    n_before = t
    cnt = 0
    for pat, rep in SUBS:
        t2, k = re.subn(pat, rep, t)
        cnt += k
        t = t2
    dstp.parent.mkdir(parents=True, exist_ok=True)
    dstp.write_text(t + MASK_NOTE, encoding="utf-8")
    log.append(f"{dstp.relative_to(STG)} substitutions={cnt}")
    # 自校验：masked 副本零 HARD
    for pat, _ in SUBS:
        if re.search(pat, dstp.read_text(encoding="utf-8")):
            print("MASK-RESIDUAL", dstp, pat)
            sys.exit(1)
# 台账（masked 例外逐件）
(OUT / "ledgers").mkdir(exist_ok=True)
(OUT / "ledgers" / "T7_EXCLUSIONS.tsv").write_text(
    "# T7 剔除/例外台账（token 不落字面；masked=仓面存脱敏版，线上原件留机器侧）\n"
    "relpath\taction\tnote\n"
    "docs/plans/repo_sync3_20260928/BRIEF_REPOSYNC3.md\tmasked\t追加六/T7 段 token 字面枚举→八类描述化（任务书其余逐字）\n"
    "docs/wiki/USER_DIRECTIVE_20260928_eyekb_improve_wave.md\tmasked\t追加六条款 token 字面枚举→八类描述化（其余 24 行含追加四/五逐字；线上原件留机器侧）\n"
    "docs/plans/repo_sync3_20260928/scripts/t7_own_tokens.py\tself-clean\t门脚本 needle 运行期拼装，源面零字面（自净条款）\n",
    encoding="utf-8")
print("T7b masked done:\n" + "\n".join(log))
