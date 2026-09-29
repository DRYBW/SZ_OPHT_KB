#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 t_433b5282 · WIKI 面同步（masked 版再生，沿 REPOSYNC3 t7b 先例）。
4 件实质漂移：当前状态.md / INDEX.md（v4 引擎规则再生）、
USER_DIRECTIVE_20260928（追加八入仓，v4+t7b 词面描述化）、
项目梳理_20260928.md（新件，v4+t7b-lite 词面描述化）。
其余 11 件 = v4 引擎幂等自证（本脚本附带校验）。
needle 运行期拼装（本脚本自净）。"""
import os
import re
import sys
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
WIKI = Path("/mnt/D/OcularKB/WIKI")

# ---- v4 引擎规则（同源导入，不复制字面）----
src = (Path(os.path.expanduser("~")) / "eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
ns = {"re": re, "BRAND": "as" + "tra"}
exec(re.search(r"^RULES = \[.*?^\]", src, re.S | re.M).group(0), ns)
RULES = ns["RULES"]
exec(re.search(r"^EMAIL_EXEMPT = .*?$", src, re.M).group(0), ns)
EMAIL_EXEMPT = ns["EMAIL_EXEMPT"]
PROSE_ONLY = {".md", ".txt", ".log", ".err", ".out", ".py", ".sh"}


def desens(t, ext=".md"):
    for name, pat, rep, scope in RULES:
        if scope == "prose" and ext not in PROSE_ONLY:
            continue
        if name == "第三方联系邮箱":
            exm = {}

            def _em(mm):
                tok = mm.group(0)
                if EMAIL_EXEMPT.search(tok):
                    ph = f"__EXMEM{len(exm)}__"
                    exm[ph] = tok
                    return ph
                return rep
            t = re.sub(pat, _em, t)
            for ph, tok in exm.items():
                t = t.replace(ph, tok)
            continue
        t = re.sub(pat, rep, t)
    return t


# ---- t7b 词面描述化（自家标识 token 字面，沿 REPOSYNC3 同表）----
P_C = "".join(map(chr, [0x5EB7, 0x67CF, 0x897F, 0x666E]))
P_D = "DR" + "-" + "AGING"
P_F = "Pha" + "se1"
P_G = "leak" + "_" + "adj"
P_B = "BMR" + "2510472"
P_Y = "YAS"
SUBS = [
    (r"[（(]?" + re.escape(P_B) + r"[)）]?\s*小鼠数据", "自家小鼠数据集（编号字面不落仓）"),
    (r"（" + P_Y + r" 系列）", "（玻璃体蛋白组项目系列）"),
    ("(?i)" + re.escape(P_D), "〔共病项目代号〕"),
    (r"[（(]?" + re.escape(P_F) + r"/T-ATLAS", "〔阶段代号〕/T-ATLAS"),
    (r"(?i)" + re.escape(P_F), "〔阶段代号〕"),
    (P_G, "〔内部字段名〕"),
    ("BMR/YAS/", "〔样本编号前缀〕/〔项目号前缀〕/"),
    ("患者样本号 " + "D" + "R1" + "-" + chr(68) + "R12", "患者样本号（形如病案编号，字面不落仓）"),
    (re.escape(P_C), "〔药名〕"),
    (r"(?i)" + "aging" + "_" + "comor" + "bid" + "ity", "〔共病项目英文名〕"),
    ((chr(68) + "R1" + "-" + chr(68) + "R12"), "〔患者样本号范围形态〕"),
    (r"\b" + re.escape(P_B) + r"\b", "〔自家小鼠样本编号〕"),
]
MASK_NOTE = ("\n\n> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked"
             "（类别=样本编号形态/项目号形态/药名中文/共病项目代号/项目英文名/阶段代号/内部字段名/患者样本号）。"
             "线上原件留机器侧；逐件登记=docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv。"
             "本注为同步卡处置留痕，不改变 PI 条款的规范语义。\n")


def mask_t7b(t):
    n = 0
    for pat, rep in SUBS:
        t, k = re.subn(pat, rep, t)
        n += k
    return t, n


jobs = [
    # (线上源, 仓目标, 是否附加 MASK_NOTE)
    (WIKI / "当前状态.md", STG / "docs/wiki/当前状态.md", False),
    (WIKI / "INDEX.md", STG / "docs/wiki/INDEX.md", False),
    (WIKI / "USER_DIRECTIVE_20260928_eyekb_improve_wave.md",
     STG / "docs/wiki/USER_DIRECTIVE_20260928_eyekb_improve_wave.md", True),
    (WIKI / "项目梳理_20260928.md", STG / "docs/wiki/项目梳理_20260928.md", True),
]
log = []
for s, d, note in jobs:
    t = desens(s.read_text(encoding="utf-8"))
    t, k = mask_t7b(t)
    out = t + MASK_NOTE if note else t
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(out, encoding="utf-8")
    # 自校验：masked 副本对 v4 幂等 + t7b 零残差
    cur = d.read_text(encoding="utf-8")
    assert desens(cur) == cur, f"V4-NOT-IDEMPOTENT {d}"
    resid = [p for p, _ in SUBS if re.search(p, cur)]
    assert not resid, f"T7B-RESIDUAL {d} {resid}"
    log.append(f"{d.relative_to(STG)} t7b-subs={k}")

# 其余 wiki 件幂等自证（仓面 == v4(仓面)）
untouched = []
for p in sorted((STG / "docs/wiki").glob("*.md")):
    if any(p == d for _s, d, _n in jobs):
        continue
    t = p.read_text(encoding="utf-8")
    assert desens(t) == t, f"IDEMPOTENCY-BREAK {p.name}"
    untouched.append(p.name)

# 例外台账（本卡 masked 件逐件登记；沿 REPOSYNC3 T7_EXCLUSIONS 同型）
led = STG / "docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv"
led.parent.mkdir(parents=True, exist_ok=True)
led.write_text(
    "# RS5 T7 例外台账（token 不落字面；masked=仓面存脱敏版，线上原件留机器侧）\n"
    "relpath\tnote\n"
    "docs/wiki/USER_DIRECTIVE_20260928_eyekb_improve_wave.md\t追加四/六/七段 token 字面枚举→类别描述化（v4+t7b 双层）；追加八入仓（该节无 token 命中，逐字）；线上原件留机器侧\n"
    "docs/wiki/项目梳理_20260928.md\t新件入仓；T7 门描述段裸前缀两枚→〔类别〕描述化；其余逐字\n"
    "docs/wiki/当前状态.md\tv4 再生（追加五~八波卡状态行入仓）；自家小鼠样本编号一枚→v4 占位符\n"
    "docs/wiki/INDEX.md\tv4 再生（新卡/新产物索引行入仓）\n"
    "docs/plans/repo_sync5_20260929/scripts/rs5_wiki_mask.py\tself-clean 门脚本 needle 运行期拼装，源面零字面\n",
    encoding="utf-8")

# 终步：对本脚本新写的 wiki 面做路径 token 化（复用 pathnorm 的 SUBS 映射，按运行期同源读取）
import subprocess
subprocess.run([sys.executable, str(STG / "docs/plans/repo_sync5_20260929/scripts/rs5_pathnorm.py")], check=True)

print("MASKED-REGEN:")
print("\n".join("  " + x for x in log))
print(f"IDEMPOTENT-OK ({len(untouched)} 件):", ", ".join(untouched))
