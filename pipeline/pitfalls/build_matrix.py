#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_matrix.py — KNOWNISSUES-B2 执行序②（ARBITRATION_RULING_C1-C14_v1 批复后）：
6 物种 × 15 canonical 组织 = **90 格全占位矩阵**（C1/C10 批复面积；零手写，脚本生成）。

口径纪律（红线）：
  - **占位≠激活**：本批达标候选=0 的如实口径维持（执行序 5）——不借任何 C 项批复激活格子；
    WORKFLOW_READY 前置=人工审计门（claim_curated），EVIDENCE_READY 仅既有六格（provisional）。
  - RESERVED 物种（macaque/rat/rabbit/zebrafish）按 C10 只能 PLACEHOLDER（升格走
    "逐物种 ≥3 条有出处坑 + 人工审计门"预注册通道，逐申请批复，禁自控）。
  - 词表坐标一律取 COORDINATE_TAXONOMY_v1.md 定案值（15 面+6 物种）；未入表物种/组织=UNMAPPED 不入统计。
  - 格子/claim 变更全部走 build 重生成：本件产物 matrix/ 下三件（MATRIX_GRID.json /
    GRID_LEDGER.csv / MANIFEST.sha256），禁手改；`--check`=脚本↔产物确定性门（临时目录重生成逐字节对拍）。
  - 面板状态=盘上实测（kb/baselines/*.json status 字段），鼠侧/RESERVED 侧如实登记无面
    （panel_backlog_worklist 的结构性义务，不在本件建面板）。

用法：
  python build_matrix.py            # 生成 matrix/ 三件
  python build_matrix.py --check    # 确定性门（不写盘）
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE / "pages"
MATRIX = HERE / "matrix"
BASE_DIR = Path("/mnt/D/EyeKB/kb/baselines")

RULING = "ARBITRATION_RULING_C1-C14_v1.md"
RULING_SHA256 = ("aea4b4c592a092f115c78b4ee1ec81ecaf4eea1b9e2453c8ead39615f3b7fb8a")
REQUEST_SHA256 = ("88996f1039042fbdea8a1fd4bd9c6f109cbbc170adbd3e6ca4cffae159dd37a3")

# 词表从单一事实源 import（禁双写坐标清单）
_spec = importlib.util.spec_from_file_location("_bc", HERE / "build_claims.py")
_bc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bc)
CANON = list(_bc.CANON_TISSUES)                       # 15 面（C1 批复）
ACTIVE_SPECIES = list(_bc.SPECIES_PAGE)               # human, mouse
RESERVED_SPECIES = ["macaque", "rat", "rabbit", "zebrafish"]  # v1 §2（C10 批复：只能占位）
SPECIES = ACTIVE_SPECIES + RESERVED_SPECIES           # 6（矩阵行序）
RESERVED_SET = set(RESERVED_SPECIES)

# 六格既有坐标系（canonical 名，build_claims 派生，禁手写第二表）
ACTIVE6 = {f"{c.split('__', 1)[0]}__{_bc.TISSUE_CANON[c.split('__', 1)[1]]}"
           for c in _bc.CELLS}

PANEL_MAP = {"filled_donor_level": "filled", "skeleton_mapping_backfilled": "skeleton",
             "observed_single_study_pilot": "pilot",
             "development_annotated_aggregate": "dev_aggregate"}


def panel_human(t):
    f = BASE_DIR / f"{t}.json"
    if not f.exists():
        return "missing_no_surface"
    st = json.load(open(f, encoding="utf-8")).get("status", "?")
    return PANEL_MAP.get(st, st)


def panel_state(sp, t):
    """baselines 现全为人面（盘上实测无任何 mouse/RESERVED 面文件）——禁拿人面板冒充。"""
    if sp == "human":
        return panel_human(t)
    if sp == "mouse":
        return "no_mouse_surface"
    return "no_surface_reserved_species"


def load_cell_claims():
    """pages/cells/*.json 的 home=cell 本格条（pattern 覆盖条不算格专属——五态阈值按本格条）。"""
    out = {}
    for f in sorted(PAGES.glob("cells/*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for e in d.get("entries") or []:
            if e.get("home", {}).get("kind") == "cell":
                out.setdefault(e["home"]["id"], []).append(e)
    return out


def build_grid():
    cell_claims = load_cell_claims()
    rows = []
    for sp in SPECIES:
        for ti in CANON:
            cid = f"{sp}__{ti}"
            es = cell_claims.get(cid, [])
            fms = {e["failure_mode"][:40] for e in es}
            ok = [e for e in es
                  if e["evidence_source_type"] in ("internal_observation", "peer_reviewed_literature")
                  and e["source_check"] == "locator_verified"]
            if sp in RESERVED_SET:
                state = "PLACEHOLDER"
                why = ("RESERVED 物种占位（C10 批复）——不得建知识格；升格走预注册通道"
                       "（逐物种 ≥3 条有出处坑+人工审计门，逐申请批复，禁自控）；"
                       "macaque×retina 转正=另案随二批深补呈报（素材最厚已登记）")
            elif cid in ACTIVE6:
                state = "EVIDENCE_READY"
                why = ("provisional——既有六格，≥3 条不同 failure mode 且指针机械核过；"
                       "未过人工审计门（audit_pipeline），禁 WORKFLOW_READY/硬门")
            elif len(ok) >= 3 and len(fms) >= 3:
                state = "CANDIDATE_EVIDENCE_READY"
                why = "（本批不应出现——出现即限额违规，见执行序 5 如实口径）"
            else:
                state = "UNEXPLORED"
                why = ("本格专属可定位 claim <3（不同 failure mode）——达标候选=0 维持（执行序 5：不借批复激活）；"
                       "深补队列见 plans/known_issues_b2_20261001/out/panel_backlog_worklist.md 与二批检索计划")
            rows.append(dict(species=sp, tissue=ti, cell_id=cid, grid_state=state,
                             panel=panel_state(sp, ti),
                             n_cell_claims=len(es), n_distinct_fm=len(fms), n_eligible=len(ok),
                             activated="NO",  # 全表恒 NO——占位≠激活的机械断言位
                             why=why))
    assert len(rows) == 90, f"矩阵面积必须=6×15=90（C10），实={len(rows)}"
    assert all(r["activated"] == "NO" for r in rows), "activated 恒=NO 破坏（本批禁激活）"
    assert not any(r["grid_state"] == "CANDIDATE_EVIDENCE_READY" for r in rows), \
        "出现达标候选=违反执行序 5 如实口径"
    tally = {}
    for r in rows:
        tally[r["grid_state"]] = tally.get(r["grid_state"], 0) + 1
    grid = {"schema": "eyekb-matrix-grid/1.0",
            "generated_by": "pipeline/pitfalls/build_matrix.py（零手写，禁手改产物）",
            "taxonomy": "COORDINATE_TAXONOMY_v1.md（RATIFIED v1）",
            "ruling": {"file": "plans/known_issues_b2_20261001/out/" + RULING,
                       "sha256": RULING_SHA256, "request_sha256": REQUEST_SHA256},
            "area": "6 species × 15 canonical tissues = 90 格全占位（C1/C10 批复）",
            "activation_policy": ("占位≠激活：本批激活=0、达标候选=0（如实口径，执行序 5）；"
                                  "WORKFLOW_READY 前置=人工审计门 claim_curated；"
                                  "RESERVED 物种升格=逐申请预注册通道"),
            "grid_states_seen": tally, "cells": rows}
    return grid, rows


def write_grid(grid, rows, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "MATRIX_GRID.json").write_text(
        json.dumps(grid, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cols = ["species", "tissue", "cell_id", "grid_state", "panel", "n_cell_claims",
            "n_distinct_fm", "n_eligible", "activated", "why"]
    with open(dest / "GRID_LEDGER.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    lines = []
    for n in ("GRID_LEDGER.csv", "MATRIX_GRID.json"):
        lines.append(f"{hashlib.sha256((dest / n).read_bytes()).hexdigest()}  {n}")
    (dest / "MANIFEST.sha256").write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    grid, rows = build_grid()
    if a.check:
        with tempfile.TemporaryDirectory() as td:
            write_grid(grid, rows, Path(td))
            old = {n: hashlib.sha256((MATRIX / n).read_bytes()).hexdigest()
                   for n in ("MATRIX_GRID.json", "GRID_LEDGER.csv")}
            new = {n: hashlib.sha256((Path(td) / n).read_bytes()).hexdigest()
                   for n in ("MATRIX_GRID.json", "GRID_LEDGER.csv")}
            drift = [n for n in old if old[n] != new[n]]
            print("CHECK", "PASS" if not drift else f"DRIFT {drift}")
            return 0 if not drift else 1
    write_grid(grid, rows, MATRIX)
    print("matrix written:", grid["grid_states_seen"], "total", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
