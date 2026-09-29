#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC5 t_433b5282 · 哈希清单重锚（manifest re-anchor）。
背景=rs5_pathnorm.py 对新收面做机器路径 token 化后，三件盘上原件 manifest 的 sha 与仓副本失配。
处置=仓内 manifest 重锚到仓副本现字节（头部 # 注记：原件 manifest=盘上权威，仓面=token 化派生版；
     每行"原sha->新sha"可追溯）。seurat manifest 的 data/ 条目转 DATA-EXCLUDED 注记（>50MB 不收，size 保留）。
线上原件 manifest 零改动。"""
import hashlib
import re
from pathlib import Path

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def reanchor(mf: Path, base: Path, header_note: str, drop_data=False):
    orig_lines = [l for l in mf.read_text(encoding="utf-8").splitlines() if l.strip()]
    orig = {}
    order = []
    for l in orig_lines:
        m = re.match(r"^([0-9a-f]{64}|\s*\d+\s+)?\s*(SIZE-ONLY|\d+)\s+(.+)$", l)
        mm = re.match(r"^([0-9a-f]{64})\s+[* ]?(.+)$", l)
        ms = re.match(r"^SIZE-ONLY\s+(\d+)\s+(.+)$", l)
        if mm:
            orig[mm.group(2)] = ("sha", mm.group(1))
            order.append(mm.group(2))
        elif ms:
            orig[ms.group(2)] = ("size", ms.group(1))
            order.append(ms.group(2))
    out = [header_note]
    changed = 0
    for f in order:
        kind, val = orig[f]
        p = base / f.lstrip("./")
        if not p.exists():
            out.append(f"# MISSING-IN-REPO {f} (orig {kind}={val[:16]})")
            continue
        if kind == "size" and drop_data and str(f).startswith("data/"):
            out.append(f"DATA-EXCLUDED {val}  {f}  # >50MB 不收（清单沿任务书纪律），原件留机器侧 manifest 行={val}")
            continue
        h = sha(p)
        if kind == "sha" and h != val:
            out.append(f"{h}  {f}  # re-anchored from {val}")
            changed += 1
        else:
            out.append(f"{h}  {f}")
    mf.write_text("\n".join(out) + "\n", encoding="utf-8")
    return len(order), changed


jobs = [
    (STG / "kb/composition/SHA256SUMS.txt", STG / "kb/composition",
     "# RS5 re-anchor：本表=仓副本（rs5_pathnorm token 化后）现字节锚；盘上原件 manifest 留机器侧为权威（EXPECTED_COMPOSITION_v0.{json,md} 两件 sha 因 token 化变化，其余同源）"),
    (STG / "docs/plans/drsc_disc_quant_20260928/out/MANIFEST_sha256.txt", STG / "docs/plans/drsc_disc_quant_20260928",
     "# RS5 re-anchor：仓副本 token 化后现字节锚；原件 manifest 留机器侧"),
    (STG / "docs/plans/seurat_probe_20260928/MANIFEST_SEURATPROBE.sha256", STG / "docs/plans/seurat_probe_20260928",
     "# RS5 re-anchor：仓副本 token 化后现字节锚；data/ 大件按任务书纪律不收仓（DATA-EXCLUDED 行保留原件 size 锚）；原件 manifest 留机器侧"),
]
for mf, base, note in jobs:
    n, c = reanchor(mf, base, note, drop_data="seurat" in mf.name)
    print(f"{mf.relative_to(STG)}: lines={n} re-anchored={c}")
