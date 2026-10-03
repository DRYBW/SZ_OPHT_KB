#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_matrix.py — tri-state figure of the 90-cell placeholder matrix (house style; formal artifact of execution step 2, shipped with the ruling batch).

Rows=6 species (human/mouse ACTIVE + macaque/rat/rabbit/zebrafish RESERVED),
Columns = 15 canonical tissues (COORDINATE_TAXONOMY_v1.md §3, C1 approved area 6×15=90).
Data source=matrix/MATRIX_GRID.json (output of build_matrix.py, zero manual entry).
State colors: EVIDENCE_READY(provisional)=blue / UNEXPLORED=green / PLACEHOLDER(RESERVED species)=orange /
No value = gray. This batch activation count = 0 — placeholder ≠ activation (Execution sequence 5 states this directly in figure captions).

Usage: python render_matrix.py [--out DIR]
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
REPO = HERE.parent.parent.parent                # repo root
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
ax.legend(handles, ["EVIDENCE_READY(provisional, 6 cells pending manual audit gate)", "UNEXPLORED(qualified candidates=0 as-is)",
                    "PLACEHOLDER(RESERVED species placeholder, C10)", "Out-of-vocabulary = UNMAPPED (excluded from matrix)"],
          loc="upper right", bbox_to_anchor=(1.30, 1.0), fontsize=7.5, frameon=False)
tally = GRID["grid_states_seen"]
ax.set_title("Species × tissue 90-cell placeholder matrix (C1/C10 approved area = 6×15; build_matrix.py zero hand-writing)\\n"
             f"Placeholder ≠ activation: current batch activation=0 | ER={tally.get('EVIDENCE_READY',0)} provisional |"
             f"PH={tally.get('PLACEHOLDER',0)} RESERVED｜UN={tally.get('UNEXPLORED',0)}",
             fontsize=9.5)
ax.set_xlabel("canonical tissue (v1 §3 finalized 15 facets)")
fig.tight_layout()
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(HERE))
a = ap.parse_args()
dst = Path(a.out) / "matrix_coverage_90.png"
fig.savefig(dst, bbox_inches="tight")
print("saved", dst)
