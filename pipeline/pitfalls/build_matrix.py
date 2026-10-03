#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_matrix.py — KNOWNISSUES-B2 execution step 2 (after ARBITRATION_RULING_C1-C14_v1):
6 species × 15 canonical tissues = **90-cell full placeholder matrix** (C1/C10 approved area; zero manual entry, script-generated).

Scope discipline (red line):
  - **Placeholder ≠ Activation**: Maintain the honest reporting standard for this batch where qualifying candidates = 0 (Execution Order 5) — do not activate any grid cells via C-item approvals;
    WORKFLOW_READY prerequisite = manual audit gate (claim_curated); EVIDENCE_READY limited to existing six cells (provisional).
  - RESERVED species (macaque/rat/rabbit/zebrafish) are restricted to PLACEHOLDER status per C10 (promotion follows
    pre-registered "≥3 sourced pitfalls per species + manual audit gate" channel, approved per application, self-promotion forbidden).
  - Lexicon coordinates uniformly adopt finalized values from COORDINATE_TAXONOMY_v1.md (15 faces + 6 species); species/tissues not in the table are marked UNMAPPED and excluded from statistics.
  - All grid/claim changes go through build regeneration: this artifact produces three files under matrix/ (MATRIX_GRID.json /
    GRID_LEDGER.csv / MANIFEST.sha256); do not hand-edit; `--check` = deterministic script↔artifact gate (regenerate in a temp dir, byte-compare).
  - Panel status = on-disk measurement (status field in kb/baselines/*.json), mouse-side/RESERVED side honestly registered as no panel
    (Structural obligation of panel_backlog_worklist; do not build panels in this item).

Usage:
  python build_matrix.py            # Generate three items in matrix/
  python build_matrix.py --check    # Determinism gate (no disk write)
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

# Import vocabulary from single source of truth (double-writing coordinate lists prohibited)
_spec = importlib.util.spec_from_file_location("_bc", HERE / "build_claims.py")
_bc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bc)
CANON = list(_bc.CANON_TISSUES)                       # 15 tissues (C1 approval)
ACTIVE_SPECIES = list(_bc.SPECIES_PAGE)               # human, mouse
RESERVED_SPECIES = ["macaque", "rat", "rabbit", "zebrafish"]  # v1 §2 (C10 ruling: placeholder only)
SPECIES = ACTIVE_SPECIES + RESERVED_SPECIES           # 6 (matrix row order)
RESERVED_SET = set(RESERVED_SPECIES)

# Existing coordinate system for six cells (canonical names, derived by build_claims, second manual table prohibited)
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
    """baselines are currently all human facets (disk measurement shows no mouse/RESERVED facet files) — do not substitute human facets."""
    if sp == "human":
        return panel_human(t)
    if sp == "mouse":
        return "no_mouse_surface"
    return "no_surface_reserved_species"


def load_cell_claims():
    """home=cell entries in pages/cells/*.json (pattern coverage entries do not count as cell-specific—five-state thresholds follow the specific entry)."""
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
                why = ("RESERVED species placeholder (C10 approval) — knowledge grids must not be created; promotion via pre-registration channel"
                       "(≥3 sourced pitfall entries per species + manual audit gate, approved per request, self-control prohibited);"
                       "macaque×retina formalization = separate case submitted with second batch deep supplementation (richest material registered)")
            elif cid in ACTIVE6:
                state = "EVIDENCE_READY"
                why = ("provisional——existing six cells, ≥3 distinct failure modes and pointers mechanically verified;"
                       "Failed manual audit gate (audit_pipeline); WORKFLOW_READY/hard gates prohibited")
            elif len(ok) >= 3 and len(fms) >= 3:
                state = "CANDIDATE_EVIDENCE_READY"
                why = "(Should not appear in this batch—appearance indicates quota violation, see Execution Sequence 5 for accurate reporting)"
            else:
                state = "UNEXPLORED"
                why = ("Fewer than 3 locatable claims specific to this cell (distinct failure modes)—0 qualifying candidates remain (execution order 5: do not activate via approval);"
                       "Deep-fill queue see plans/known_issues_b2_20261001/out/panel_backlog_worklist.md and second-batch retrieval plan")
            rows.append(dict(species=sp, tissue=ti, cell_id=cid, grid_state=state,
                             panel=panel_state(sp, ti),
                             n_cell_claims=len(es), n_distinct_fm=len(fms), n_eligible=len(ok),
                             activated="NO",  # always NO across the table — the mechanical assertion slot for placeholder ≠ activated
                             why=why))
    assert len(rows) == 90, f"Matrix area must equal 6×15=90 (C10), actual={len(rows)}"
    assert all(r["activated"] == "NO" for r in rows), "activated always=NO violation (activation prohibited in this batch)"
    assert not any(r["grid_state"] == "CANDIDATE_EVIDENCE_READY" for r in rows), \
        "Appearance of compliant candidates = violation of Execution Sequence 5 'faithful reporting' standard."
    tally = {}
    for r in rows:
        tally[r["grid_state"]] = tally.get(r["grid_state"], 0) + 1
    grid = {"schema": "eyekb-matrix-grid/1.0",
            "generated_by": "pipeline/pitfalls/build_matrix.py (zero manual writing, manual modification of artifacts prohibited)",
            "taxonomy": "COORDINATE_TAXONOMY_v1.md（RATIFIED v1）",
            "ruling": {"file": "plans/known_issues_b2_20261001/out/" + RULING,
                       "sha256": RULING_SHA256, "request_sha256": REQUEST_SHA256},
            "area": "6 species × 15 canonical tissues = 90 cells all placeholders (C1/C10 approval)",
            "activation_policy": ("Placeholder ≠ activation: current batch activation=0, qualified candidates=0 (accurate metric, execution sequence 5);"
                                  "WORKFLOW_READY prerequisite=manual audit gate claim_curated;"
                                  "RESERVED species promotion=per-application pre-registration channel"),
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
