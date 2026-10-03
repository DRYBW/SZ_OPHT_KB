#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W2: add development_axis column to the disease x material matrix + ROP placeholder cell + explicit adult in the PDR entry header.

Regression-lock bypass design (task brief discipline 1: additive-only + KB2c lock len(rows)==12):
  - rows 12 cells: only **add a column** (development_axis key per row); array length and existing fields untouched.
  - ROP placeholder cell: placed in a new top-level key development_axis_reservations -- cell established,
    content not filled, and a regression lock is on record (evals/regression_kb3_20260924.py locks
    rows==12+reservations==1); any future ROP fill must pass adjudication and change both locks at once
    (prevents silent row expansion).
  - PDR__fibrovascular_membrane.json/md: add explicit development_stage=adult.
NOTE: the Chinese literals matched against existing kb MD tables below ("| 疾病 | ...") are frozen-input
match patterns for this one-shot patch; emitted strings are English per the repo-wide translation contract.
"""
import json
from pathlib import Path

D = Path("/mnt/D/EyeKB/kb/priors/disease")
CARD = "t_5425a7ca"

# ---- matrix JSON ----
mp = D / "_DISEASE_TISSUE_MATRIX.json"
m = json.loads(mp.read_text(encoding="utf-8"))
assert m["schema"] == "eyekb-disease-matrix/1.1" and len(m["rows"]) == 12
for r in m["rows"]:
    assert r.get("organism_stage") == "adult", f"unexpected organism_stage in row: {r}"
    r.setdefault("development_axis", "adult")  # task brief W2: add column
if "development_axis_reservations" not in m:
    m["development_axis_reservations"] = [{
        "disease": "ROP",
        "material": "developing_retina_vascular",
        "development_axis": "fetal_neonatal",
        "organism_stage": "developing",
        "status": "RESERVED (cell established, content not filled)",
        "note": ("retinopathy of prematurity = proliferative vascular disease on the developmental-axis side "
                 "(companion cell for the PI red line): strictly separated from the PDR adult-membrane cell, "
                 "never merged into one cell and never referenced against each other (fetal/preterm material is "
                 "not interchangeable with adult material even within the same tissue). "
                 "Precondition for filling = securing developmental-stage material/literature anchors (e.g. a ROP "
                 "retinal-organoid arm or postmortem single-cell data -- both first subject to the "
                 "developmental-axis separate-column discipline); the fill action must pass adjudication and "
                 "synchronize the regression double lock (rows/reservations)."),
        "reserved_by": {"card": CARD, "date": "2026-09-24"}}]
m["kb3_note"] = ("KB3 (t_5425a7ca): the developmental axis is promoted to an explicit matrix column development_axis; "
                 "all 12 live cells are adult (hard-coded); developmental-axis-side disease cells go through the "
                 "development_axis_reservations placeholders (prevents pooling with adult cells; regression double lock).")
m["kb3_card"] = CARD
mp.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

# ---- matrix MD: add a table column (development_axis same value as the developmental stage = adult; an explicit column so it is not demoted to a "notes" remark) ----
mdp = D / "_DISEASE_TISSUE_MATRIX.md"
t = mdp.read_text(encoding="utf-8")
if "| 疾病 | 组织/材料格 | 发育档 |" in t and "development_axis" not in t.split("\n")[9][:200]:
    lines = t.split("\n")
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("| 疾病 | 组织/材料格 | 发育档 | 状态 | 说明 |"):
            out.append("| Disease | tissue/material cell | developmental stage | development_axis (KB3) | status | notes |")
            continue
        if ln.startswith("|---|---|---|---|---|") and lines[i - 1].startswith("| 疾病 |"):
            out.append("|---|---|---|---|---|---|")
            continue
        if ln.startswith("| ") and ln.count("|") == 5 and (" adult |" in ln or "**FILLED" in ln):
            cells = ln.split("|")
            cells.insert(4, " adult ")
            out.append("|".join(cells))
            continue
        out.append(ln)
    t = "\n".join(out)
    if "## KB3 发育轴预留格" not in t:
        t += ("\n## KB3 developmental-axis reserved cells (t_5425a7ca -- cell established, content not filled)\n\n"
              "| Disease | material cell | development_axis | status |\n|---|---|---|---|\n"
              "| ROP (retinopathy of prematurity) | developing_retina_vascular | **fetal_neonatal** | "
              "RESERVED -- proliferative vascular disease on the developmental-axis side; never pooled with, or cross-referenced to, the PDR adult cell; precondition for filling = developmental-stage data/literature anchor + passing adjudication |\n\n"
              "> Placeholder implementation of architecture rule 6: the adult-cell array rows=12 stays untouched (regression lock); reserved cells go through the independent key "
              "development_axis_reservations (double lock).\n")
    mdp.write_text(t, encoding="utf-8")

# ---- PDR entry: explicit development_stage=adult ----
pp = D / "PDR__fibrovascular_membrane.json"
p = json.loads(pp.read_text(encoding="utf-8"))
assert p["schema"] == "eyekb-disease/1.1" and p.get("organism_stage") == "adult"
if "development_stage" not in p:
    p["development_stage"] = "adult"
    p["kb3_card"] = CARD
    pp.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
pm = D / "PDR__fibrovascular_membrane.md"
mt = pm.read_text(encoding="utf-8")
if "development_stage=adult" not in mt:
    mt = mt.replace("| 发育档: **organism_stage=adult**",
                    "| Developmental stage: **organism_stage=adult | development_stage=adult** (KB3 explicit)")
    pm.write_text(mt, encoding="utf-8")
print("W2 done: matrix rows + column, ROP reserved cell, PDR header explicit")
