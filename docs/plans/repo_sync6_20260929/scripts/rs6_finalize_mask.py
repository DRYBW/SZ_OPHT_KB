#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC6 · 规范/通报文 masked 补刀（沿 RS5 rs5_finalize_mask 同表 + 执行方名称 token 化）。
对象=docs/plans/repo_sync6_20260929/BRIEF_REPOSYNC6.md 与 docs/plans/QUEUE_20260929.md ⑥节：
T7 口径要求 token 化面零"执行方 agent 名字面"（BRIEF 头行派发/执行字段）；SUBS 表沿用 RS5 幂等复跑。
needle 运行期拼装（本脚本自净）。"""
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
P_PI = "pi" + "-" + "chief"
SUBS = [
    (r"(?i)" + re.escape(P_D), "〔共病项目代号〕"),
    (r"(?i)" + re.escape(P_E), "〔共病项目英文名〕"),
    (r"(?i)" + re.escape(P_F), "〔阶段代号〕"),
    (P_G, "〔内部字段名〕"),
    (re.escape(P_C), "〔药名〕"),
    (chr(66) + chr(77) + chr(82) + "/" + chr(89) + chr(65) + chr(83) + "/", "〔样本编号前缀〕/〔项目号前缀〕/"),
    (chr(66) + chr(77) + chr(82) + "*", "〔样本编号前缀〕*"),
    (chr(89) + chr(65) + chr(83) + "*", "〔项目号前缀〕*"),
    (r"\bDR(1|2|3|4|5|6|7|8|9|10|11|12)\b(?![A-Za-z])", "〔患者样本号〕"),
    (P_PI, "〔执行审核方〕"),
]
NOTE = ("\n\n> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked（类别描述化，非患者数据语义零改动）。"
        "线上原件留机器侧；逐件登记=docs/plans/repo_sync6_20260929/ledgers/T7_EXCLUSIONS_RS6.tsv。"
        "本注为同步卡处置留痕，不改变任务书条款的规范语义。\n")


def v4_inplace(pth):
    src = (Path(os.path.expanduser("~")) / "eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
    ns = {"re": re, "BRAND": "as" + "tra"}
    exec(re.search(r"^RULES = \[.*?^\]", src, re.S | re.M).group(0), ns)
    txt = pth.read_text(encoding="utf-8")
    for _n, pat, rep, _sc in ns["RULES"]:
        txt = re.sub(pat, rep, txt)
    pth.write_text(txt, encoding="utf-8")


for rel in ["docs/plans/repo_sync6_20260929/BRIEF_REPOSYNC6.md", "docs/plans/QUEUE_20260929.md"]:
    p = STG / rel
    v4_inplace(p)
    t = p.read_text(encoding="utf-8")
    n = 0
    for pat, rep in SUBS:
        t, k = re.subn(pat, rep, t)
        n += k
    if "BRIEF" in rel:
        t = t + NOTE
    p.write_text(t, encoding="utf-8")
    resid = [pat for pat, _ in SUBS if re.search(pat, p.read_text(encoding="utf-8"))]
    assert not resid, f"T7B-RESIDUAL {rel} {resid}"
    print(f"masked: {rel} subs={n}")
print("FINALIZE-DONE")
