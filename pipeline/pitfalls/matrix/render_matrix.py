#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_matrix.py — 90 格占位矩阵三态图（house style；执行序②正式件，随批复入仓）。

行=6 物种（human/mouse ACTIVE + macaque/rat/rabbit/zebrafish RESERVED），
列=15 canonical 组织（COORDINATE_TAXONOMY_v1.md §3，C1 批复面积 6×15=90）。
数据源=matrix/MATRIX_GRID.json（build_matrix.py 产物，零手写）。
状态色：EVIDENCE_READY(provisional)=蓝 / UNEXPLORED=绿 / PLACEHOLDER(RESERVED 物种)=橙 /
无值=灰。本批激活=0——占位≠激活（执行序 5 如实口径直接写在图注）。

用法: python render_matrix.py [--out DIR]
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

HERE = Path(__file__).resolve().parent          # pipeline/pitfalls/matrix
REPO = HERE.parent.parent.parent                # 仓根
STYLE = REPO / "scripts" / "eyekb_house.mplstyle"
GRID = json.loads((HERE / "MATRIX_GRID.json").read_text(encoding="utf-8"))

CANON = sorted({c["tissue"] for c in GRID["cells"]},
               key=lambda t: [c["tissue"] for c in GRID["cells"]].index(t))
SPECIES = sorted({c["species"] for c in GRID["cells"]},
                 key=lambda s: [c["species"] for c in GRID["cells"]].index(s))
CODE = {"EVIDENCE_READY": 3, "CANDIDATE_EVIDENCE_READY": 2,
        "PLACEHOLDER": 1, "UNEXPLORED": 0}
M = np.full((len(SPECIES), len(CANON)), -1.0)
for c in GRID["cells"]:
    M[SPECIES.index(c["species"]), CANON.index(c["tissue"])] = CODE[c["grid_state"]]

plt.style.use(str(STYLE))
fig, ax = plt.subplots(figsize=(13.5, 5.2), dpi=300)
cmap = colors.ListedColormap(["#d9d9d9", "#fdae61", "#7fc97f", "#2c7fb8"], N=4)
cmap.set_under("#f0f0f0")
norm = colors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
ax.imshow(M, cmap=cmap, norm=norm, aspect="equal")
ax.set_xticks(range(len(CANON))); ax.set_xticklabels(CANON, rotation=38, ha="right", fontsize=7.5)
ax.set_yticks(range(len(SPECIES))); ax.set_yticklabels(SPECIES, fontsize=8.5)
for i in range(len(SPECIES)):
    for j in range(len(CANON)):
        v = M[i, j]
        lab = {3: "ER", 2: "CER", 1: "PH", 0: "UN"}.get(int(v) if v >= 0 else -1, "×")
        ax.text(j, i, lab, ha="center", va="center", fontsize=6.5,
                color="white" if v == 3.0 else "#262626")
handles = [plt.Rectangle((0, 0), 1, 1, color=cmap(n)) for n in [3.5, 0.5, 1.5, -0.5]]
ax.legend(handles, ["EVIDENCE_READY(provisional, 6 格待人工审计门)", "UNEXPLORED(达标候选=0 如实)",
                    "PLACEHOLDER(RESERVED 物种占位, C10)", "词表外=UNMAPPED(不入矩阵)"],
          loc="upper right", bbox_to_anchor=(1.30, 1.0), fontsize=7.5, frameon=False)
tally = GRID["grid_states_seen"]
ax.set_title("物种×组织 90 格占位矩阵（C1/C10 批复面积=6×15；build_matrix.py 零手写）\n"
             f"占位≠激活：本批激活=0｜ER={tally.get('EVIDENCE_READY',0)} provisional｜"
             f"PH={tally.get('PLACEHOLDER',0)} RESERVED｜UN={tally.get('UNEXPLORED',0)}",
             fontsize=9.5)
ax.set_xlabel("canonical tissue（v1 §3 定案 15 面）")
fig.tight_layout()
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(HERE))
a = ap.parse_args()
dst = Path(a.out) / "matrix_coverage_90.png"
fig.savefig(dst, bbox_inches="tight")
print("saved", dst)
