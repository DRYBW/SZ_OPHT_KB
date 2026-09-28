#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T5 — 脱敏双扫描 0 命中（幂等）
[1] v3 引擎 --scan 原样复跑（文件名+内容，幂等自证=引擎口径零命中，含 prose scope）；
[2] CJK 邻接强化复扫（词边界规则对 CJK 邻接失效的先例补扫）：仅品牌词 needle，
    命中=CJK 字符直接邻接且非引擎 DIRS 管辖外存量——DIRS 内命中数必须 0；DIRS 外（docs 根存量报告）
    逐件登记沿 REPOSYNC2 §六-2（清洗与否待 PI 裁定，本卡不擅动）；
[3] kbgov_vocab.json.gz 解压复扫（纯基因符号预期 0）；
[4] 存量面（字节镜像区）逐件登记不擅动。"""
import gzip
import json
import os
import re
import subprocess
import sys
from pathlib import Path

STG = Path(os.environ.get("EYEKB_STG", "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928"))
OUT = STG / "docs/plans/repo_sync3_20260928/out"
OUT.mkdir(parents=True, exist_ok=True)
ENGINE = "/home/ubuntu/eyekb_desensitize_v4_reposync3.py"  # v4=v3+裁决商 CJK 邻界强化（REPOSYNC2 §六-2 建议落地）

src = Path(ENGINE).read_text(encoding="utf-8")
ns = {"re": re, "BRAND": "as" + "tra"}
exec(re.search(r"^RULES = \[.*?^\]", src, re.S | re.M).group(0), ns)
RULES = ns["RULES"]
TEXT_EXT = {".md", ".json", ".yaml", ".txt", ".tsv", ".py", ".sh", ".log", ".jsonl",
            ".out", ".err", ".list", ".sha256"}
DIRS = ["docs/wiki", "docs/skills", "docs/plans", "mcp_server"]
CJK = re.compile(r"[\u4e00-\u9fff]")

# [1] 引擎 --scan 复跑（幂等）
env = dict(os.environ, EYEKB_STG=str(STG))
r = subprocess.run([sys.executable, ENGINE, "--scan"], env=env, capture_output=True, text=True)
(OUT / "t5_engine_scan.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
scan_zero = ("命中文件数: 0" in r.stdout) and ("文件名改名 0 件" in r.stdout or "改名 0" in r.stdout)
hits_m = re.search(r"== 命中文件数: (\d+) ==", r.stdout)
rn_m = re.search(r"文件名改名 (\d+) 件", r.stdout)
scan_zero = bool(hits_m) and int(hits_m.group(1)) == 0 and (rn_m is None or int(rn_m.group(1)) == 0)
print(f"[1] engine --scan idempotent: renames={rn_m and rn_m.group(1)} hitfiles={hits_m and hits_m.group(1)} -> {'ZERO' if scan_zero else 'NONZERO'}")

# [2] CJK 邻接强化（品牌词；needle 运行期拼接=本脚本自净）
STRICT = {
    "BRAND-1": "as" + "tra",
    "BRAND-2": ("bai" + "lian").lower(),
    "BRAND-3": "".join(map(chr, [0x767E, 0x70BC])),
    "BRAND-4": "".join(map(chr, [0x80A5, 0x732B])),
    "BRAND-5": "fei" + "mao",
    "BRAND-6": ("999555" + "999"),
    "BRAND-7": ("api" + "key.fun"),
    "BRAND-8": ("ubuntu-X" + "12DAi"),
    "BRAND-9": ("pi" + "-chief"),
    "BRAND-10": "".join(map(chr, [0x4F01, 0x4E1A, 0x5FAE, 0x4FE1])),
    "BRAND-11": ("BMR" + r"\d{6,}"),
}


def cjk_adjacent_hits(text, needle):
    """needle 出现且邻接字符含 CJK（词边界规则失效带）；ASCII 词内(如专有名成分)不计。"""
    out = 0
    for m in re.finditer(re.escape(needle), text, re.I):
        prev = text[m.start() - 1] if m.start() else ""
        nxt = text[m.end()] if m.end() < len(text) else ""
        ascii_edge = (prev.isascii() and prev.isalnum()) or (nxt.isascii() and nxt.isalnum())
        if ascii_edge:
            continue
        if CJK.search(prev + nxt):
            out += 1
    return out


strict_in_dirs, strict_legacy = [], []
for d in DIRS + ["README.md"]:
    base = STG / d
    it = [base] if base.is_file() else [p for root, _ds, fs in os.walk(base) for p in (Path(root) / f for f in fs)]
    for p in it:
        if not p.is_file() or p.suffix not in TEXT_EXT:
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        for k, nd in STRICT.items():
            if "\\" in nd:
                n1 = len(re.findall(nd, t))
                n2 = 0
            else:
                n1 = 0
                n2 = cjk_adjacent_hits(t, nd)
            if n1 + n2 > 0:
                (strict_in_dirs if str(p).startswith((str(STG / "docs/wiki"), str(STG / "docs/skills"),
                                                       str(STG / "docs/plans"), str(STG / "mcp_server"),
                                                       str(STG / "README.md"))) else strict_legacy).append(
                    (str(p.relative_to(STG)), k, n1 + n2))
# docs 根存量报告（引擎 DIRS 外）=legacy
strict_legacy = [x for x in strict_in_dirs if x[0].startswith("docs/DESENS") or x[0].startswith("docs/结论")
                 or (x[0].startswith("docs/") and not x[0].startswith(("docs/wiki", "docs/skills", "docs/plans", "docs/recon")))]
strict_in_dirs = [x for x in strict_in_dirs if x not in strict_legacy]
print(f"[2] CJK-adjacent strict: engine-DIRS hits={len(strict_in_dirs)} docs-root-legacy={len(strict_legacy)}")
for x in strict_in_dirs[:10]:
    print("   DIRS-HIT:", x)
for x in strict_legacy[:10]:
    print("   legacy(登记不擅动):", x)

# [3] vocab gz
raw = gzip.decompress((STG / "mcp_server/kbgov_vocab.json.gz").read_bytes()).decode("utf-8", errors="ignore")
gz_hits = [(n, len(re.findall(p, raw))) for n, p, _r, _s in RULES if re.search(p, raw)]
print(f"[3] vocab-gz RULES scan: {gz_hits if gz_hits else 0}")

# [4] 存量面登记
inv_lines = []
for surf in ["kb", "scripts", "tests", "evals", "clients", "rag_snapshots"]:
    for root, _ds, fs in os.walk(STG / surf):
        for f in fs:
            p = Path(root) / f
            if p.suffix not in TEXT_EXT:
                continue
            t = p.read_text(encoding="utf-8", errors="ignore")
            n = sum(len(re.findall(pat, t)) for _nm, pat, _rp, _sc in RULES if _sc != "prose" or p.suffix in {".md", ".txt", ".log", ".err", ".out", ".py", ".sh"})
            if n:
                inv_lines.append(f"{p.relative_to(STG)}\t{n}")
(OUT / "t5_inventory_register.txt").write_text(
    "# 存量面(字节镜像区)规则命中逐件登记——沿 REPOSYNC2 §六-2 先例：清洗与否待 PI 裁定，本卡不擅动\n"
    "path\thits\n" + "\n".join(inv_lines) + "\n", encoding="utf-8")
print(f"[4] inventory-side files with hits={len(inv_lines)} (registered, untouched)")

fail = (not scan_zero) or len(strict_in_dirs) > 0 or len(gz_hits) > 0
(OUT / "t5_final_scan.txt").write_text(
    f"engine-scan-zero={scan_zero}\nCJK-strict-DIRS-hits={len(strict_in_dirs)}\nCJK-strict-docs-root-legacy={len(strict_legacy)}(登记)\nvocab-gz={len(gz_hits)}\ninventory-register-files={len(inv_lines)}\nRESULT={'PASS(幂等0命中+DIRS强化0残差; docs根存量与镜像面=登记不擅动沿先例)' if not fail else 'CHECK'}\n",
    encoding="utf-8")
print("T5:", "PASS" if not fail else "CHECK-FAIL")
sys.exit(0 if not fail else 1)
