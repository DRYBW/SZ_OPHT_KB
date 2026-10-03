# Reading Layer Prior Entry Template (TEMPLATE — structure frozen 2026-09-23, card t_39182aa2)

> Purpose: All new tissue/disease prior entries must follow this template. Machine-readable source of truth = same-name `.json`
> (`schema: eyekb-prior/1.0`); `.md` is automatically rendered by `/mnt/D/EyeKB/scripts/priors/build_priors.py`
> **manual MD edits are invalid and will be overwritten**. Content changes = edit curated data in script + rerun.

## Directory Layout (Frozen)

```
kb/priors/
├── TEMPLATE.md                    ← This file
├── composition/                   ← K1 Composition Baseline (species_tissue.md/json)
│   ├── human_retina.{md,json}
│   └── human_pdr_membrane.{md,json}
└── disease/                       ← K2 Disease Entries (disease_name.{md,json})
    └── proliferative_DR.{md,json}
```

## JSON Structure (Required Fields)

| Field | Description |
|---|---|
| `schema` | `eyekb-prior/1.0` |
| `entry_id` | Consistent with filename |
| `species` / `tissue` / `disease` | Disease entries may provide `tissue_scope` multi-tissue ends |
| `frozen_date` / `card` | Issue date and source task card |
| `sources[]` | **one sid per entry**; must have either `pmid` (literature) or `path` (dataset/local library) — Red Line 8: entries without provenance are prohibited |
| `evidence_grades{}` | Grade criteria used in this entry |
| `major_classes[]` or `major_compartments[]` | Main table; each row contains `evidence` + `source_ids[]` |
| `states[]` / `myeloid_states[]` | **Two-level structure: cell type × state** (e.g., Macrophage: foam_DAM_LAM), prevents "state-as-new-type" causing library bloat |
| `unexpected_flags[]` / `contamination_flags[]` / `flags{}` | Reading flag definitions |
| `signatures{}` | Marker panel, with traceability notes |
| `caveats[]` | Known limitations and interpretation discipline (includes "prior≠truth" statement) |
| `_computed{}` | Snapshot of recomputed results for Grade A figures (regression comparison baseline) |

## Evidence Grades (Frozen Criteria)

- **A** = Local empirical recomputation —— Recalculated from raw objects using this laboratory's pipeline (must include file path + cell count + computation script)
- **B** = Directly reported in original literature —— Explicitly stated in the original text paragraph (if abstract lacks precise %, supports only qualitative statements, must not be cited as numbers)
- **C** = Cross-study empirical range / model evidence extrapolation —— Derived from distribution of Grade A source data or multi-study consensus; method specified within entry
- **D** = Review/background narrative —— Supports only qualitative descriptions and flag semantics, does not support any numerical expectations

## Reading Discipline (Inherited by All Entries)

1. Priors serve only as **controls and QC flags** (expected / unexpected / contamination-suspect); **prohibited from replacing or modifying annotation scores** (Red Line 12 inheritance: RAG prohibited in scoring).
2. If priors conflict with data → output "conflict list" to **report to PI**; prohibited from altering data to fit priors, or altering priors to fit data (Red Line 9).
3. Proportion ranges are influenced by **library construction design** (sorting/enrichment/sampling region) —— Before judging "anomaly", must check dataset library construction strategy (see human_retina caveats 1–3).
4. Self-annotations of public data may themselves be inaccurate (PI explicitly stated) —— All entries are graded priors, not ground truth.

## New Entry Workflow

1. Add curated data + (if containing Grade A) recomputation functions and drift assertions in `build_priors.py`
2. Run `/home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/scripts/priors/build_priors.py`
3. Run `check_priors_consistency.py` (JSON↔MD↔tool three-way consistency) and MCP golden regression
4. Register new entry links in WIKI retrieval index (K5 mechanism)
