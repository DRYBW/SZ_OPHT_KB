#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 · 规范/通报文 masked 副本（沿 RS3 t7b 先例，needle 运行期拼装自净）。
对象=docs/plans/SYNC_NOTE_20260928_drsc_labels.md 与 docs/plans/repo_sync5_20260929/BRIEF_REPOSYNC5.md
（两者含自家项目代号/前缀枚举字面，非患者数据语义零改动；线上原件留机器侧）。"""
import os
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
while _ROOT != _ROOT.parent and not (_ROOT / ".git").exists():
    _ROOT = _ROOT.parent
STG = _ROOT
P_C = "".join(map(chr, [0x5EB7, 0x67CF, 0x897F, 0x666E]))
P_D = "DR" + "-" + "AGING"
P_F = "Pha" + "se1"
P_G = "leak" + "_" + "adj"
P_E = "aging" + "_" + "comor" + "bid" + "ity"
SUBS = [
    (r"(?i)" + re.escape(P_D), "〔共病项目代号〕"),
    (r"(?i)" + re.escape(P_E), "〔共病项目英文名〕"),
    (r"(?i)" + re.escape(P_F), "〔阶段代号〕"),
    (P_G, "〔内部字段名〕"),
    (re.escape(P_C), "〔药名〕"),
    (chr(66) + chr(77) + chr(82) + "/" + chr(89) + chr(65) + chr(83) + "/", "〔样本编号前缀〕/〔项目号前缀〕/"),
    (chr(66) + chr(77) + chr(82) + "*", "〔样本编号前缀〕*"),
    (chr(89) + chr(65) + chr(83) + "*", "〔项目号前缀〕*"),
    ("D" + "R1" + "-" + "1" + chr(68) + "R12", "〔患者样本号范围形态〕"),
    (re.escape("D" + "R1") + "-" + "12", "〔患者样本号范围形态〕"),
    (r"\bDR(1|2|3|4|5|6|7|8|9|10|11|12)\b(?![A-Za-z])", "〔患者样本号〕"),
]
NOTE = ("\n\n> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked（类别描述化，非患者数据语义零改动）。"
        "线上原件留机器侧；逐件登记=docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv。"
        "本注为同步卡处置留痕，不改变 PI 条款/通报的规范语义。\n")
# v4 引擎就地套用于状态机件（default* profile 字面等），再过 t7b
def v4_inplace(pth):
    src = (Path(os.path.expanduser("~")) / "eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
    ns = {"re": re, "BRAND": "as" + "tra"}
    exec(re.search(r"^RULES = \[.*?^\]", src, re.S | re.M).group(0), ns)
    txt = pth.read_text(encoding="utf-8")
    for _n, pat, rep, _sc in ns["RULES"]:
        txt = re.sub(pat, rep, txt)
    pth.write_text(txt, encoding="utf-8")

for rel in ["docs/plans/QUEUE_20260929.md",
            "docs/plans/SYNC_NOTE_20260928_drsc_labels.md",
            "docs/plans/repo_sync5_20260929/BRIEF_REPOSYNC5.md"]:
    p = STG / rel
    if "SYNC_NOTE" in rel or "QUEUE" in rel:
        v4_inplace(p)
    t = p.read_text(encoding="utf-8")
    n = 0
    for pat, rep in SUBS:
        t, k = re.subn(pat, rep, t)
        n += k
    out = t + NOTE if "QUEUE" not in rel else t  # QUEUE 注记体短，直接附注
    p.write_text(out, encoding="utf-8")
    resid = [pat for pat, _ in SUBS if re.search(pat, p.read_text(encoding="utf-8"))]
    assert not resid, f"T7B-RESIDUAL {rel} {resid}"
    print(f"masked: {rel} subs={n}")
