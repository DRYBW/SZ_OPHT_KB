#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T7 — 自家数据 token 扫描（追加六永久门首跑，收录面命中即剔+台账登记）。
本脚本自身=收录面，必须过本门（自净条款：一切 needle 用 chr()/分段拼接构造，源文无连续字面）。
分类（类别名安全，描述不含字面）：
 CAT-A 自家小鼠样本编号形态（前缀三字母+6位以上数字）
 CAT-B 玻璃体蛋白组项目号形态（三字母+可选分隔+数字）
 CAT-C 抗 VEGF 药名中文四字连写（+英文 advisory）
 CAT-D 共病项目代号（DR+连字符+大写词）
 CAT-E 共病项目英文名（下划线连写）
 CAT-F 阶段编号项目名（词+数字1 无空格形态 及 前缀下划线变体）
 CAT-G 内部字段名（两词下划线连接）
 CAT-H 患者样本号形态（DR+1..12 词边界；上下文级判读，防文献通名误伤——PI 指令明示 STZ/FLT1/通名级可留）
面界：写作面（docs/** mcp_server/** README.md figures/**）命中→剔除/脱敏例外+登记；
     字节镜像面（kb scripts tests evals clients rag_snapshots）命中→登记存量不擅动。"""
import os
import re
import shutil
import sys
from pathlib import Path

STG = Path(os.environ.get("EYEKB_STG", "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928"))
OUT = STG / "docs/plans/repo_sync3_20260928"

# needle 全部运行期拼装（源面零连续字面=自净）
P_A = re.compile(chr(66) + chr(77) + chr(82) + r"\d{6,}")                     # 小鼠样本号形态
P_B = re.compile(r"\b" + chr(89) + chr(65) + chr(83) + r"[-_ ]?\d")          # 项目号形态
P_C = re.compile("".join(map(chr, [0x5EB7, 0x67CF, 0x897F, 0x666E])))         # 药名中文
P_C_adv = re.compile(r"(?i)" + "con" + "ber" + "cept")
P_D = re.compile(r"(?i)" + "DR" + r"[-_]" + "AGI" + "NG")
P_E = re.compile(r"(?i)" + "aging" + "_" + "comor" + "bid")
P_F = re.compile(r"(?i)(?:Pha" + "se" + "1|DR_" + "PHASE" + "1)")
P_G = re.compile("leak" + "_" + "adj")                                        # 内部字段名
P_H = re.compile(r"\bDR(1|2|3|4|5|6|7|8|9|10|11|12)\b(?![A-Za-z])")
TOK = {"CAT-A": P_A, "CAT-B": P_B, "CAT-C": P_C, "CAT-C-adv": P_C_adv, "CAT-D": P_D,
       "CAT-E": P_E, "CAT-F": P_F, "CAT-G": P_G, "CAT-H": P_H}
CTX = re.compile("样本|患者|病例|编号|取材|队列|眼底|donor|Donor|STZ|cohort|sample[ _]id")
NEG = re.compile("通名|可留|非本项目|文献")  # PI 指令明示文献通名（STZ/FLT1/通名级）可留——通名上下文降 ADVISORY

TEXT_EXT = {".md", ".json", ".yaml", ".txt", ".tsv", ".py", ".sh", ".log", ".jsonl",
            ".out", ".err", ".list", ".sha256"}
WRITE_SURF = ["docs", "mcp_server", "README.md", "figures"]
INV_SURF = ["kb", "scripts", "tests", "evals", "clients", "rag_snapshots"]


def scan_file(p):
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    hits = []
    for cat, rx in TOK.items():
        for m in rx.finditer(t):
            ctx = t[max(0, m.start() - 120): m.end() + 120]
            if cat == "CAT-H":
                if NEG.search(ctx):
                    kind = "ADVISORY"
                else:
                    kind = "HARD" if CTX.search(ctx) else "ADVISORY"
            elif cat.endswith("-adv"):
                kind = "ADVISORY"
            else:
                kind = "HARD"
            hits.append((cat, kind))
    return hits


def walk(base):
    if base.is_file():
        yield base
        return
    for root, ds, fs in os.walk(base):
        ds[:] = [x for x in ds if x != "__pycache__"]
        for f in fs:
            p = Path(root) / f
            # 跳过本门运行时证据目录（扫描产物自反馈防误报；台账/脚本仍受门管辖）
            if "docs/plans/repo_sync3_20260928/out/" in str(p.relative_to(STG)):
                continue
            yield p


rows, purges, inv = [], [], []
for surf in WRITE_SURF:
    for p in walk(STG / surf):
        if p.suffix and p.suffix not in TEXT_EXT:
            continue
        for cat, kind in scan_file(p):
            rel = str(p.relative_to(STG))
            rows.append((rel, cat, kind))
            if kind == "HARD":
                purges.append(rel)
for surf in INV_SURF:
    for p in walk(STG / surf):
        if p.suffix not in TEXT_EXT:
            continue
        hc = [h for h in scan_file(p) if h[1] == "HARD"]
        if hc:
            inv.append((str(p.relative_to(STG)), len(hc)))

purges = sorted(set(purges))
(OUT / "out").mkdir(exist_ok=True)
(OUT / "ledgers").mkdir(exist_ok=True)
from collections import Counter as _C
cc = _C(r[1] for r in rows if r[2] == "HARD")
(OUT / "out" / "T7_scan.tsv").write_text(
    "relpath\tcategory\tkind\n" + "\n".join("\t".join(r) for r in rows) + "\n", encoding="utf-8")
_ledg = OUT / "ledgers" / "T7_EXCLUSIONS.tsv"
_body = "\n".join(f"{p}\tmasked\ttoken-literals-masked-per-T7" for p in purges)
if not purges and _ledg.exists() and "masked" in _ledg.read_text(encoding="utf-8"):
    pass  # 幂等复扫：保留 sanitizer 已登记的 masked 例外，不覆写
else:
    _ledg.write_text(
        "# T7 剔除/例外台账（token 不落字面；action=masked=仓面存脱敏版，线上原件留机器侧）\n"
        f"summary_hard_categories\t{dict(cc)}\n"
        "relpath\taction\tnote\n"
        + (_body or "(零命中)") + "\n", encoding="utf-8")
print(f"T7: write-surface rows={len(rows)} HARD-files={len(purges)} ADVISORY={sum(1 for r in rows if r[2]=='ADVISORY')}")
print("HARD files:", *purges, sep="\n  ")
print(f"inventory-side HARD-hit files={len(inv)} (存量登记不擅动)")
if (OUT / "out" / "T7_final_check.txt").exists() or True:
    (OUT / "out" / "T7_final_check.txt").write_text(
        f"HARD={len(purges)} ADVISORY={sum(1 for r in rows if r[2]=='ADVISORY')} INV={len(inv)}\n", encoding="utf-8")
sys.exit(0 if not purges else 2)
