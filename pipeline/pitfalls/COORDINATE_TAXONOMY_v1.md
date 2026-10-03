# COORDINATE_TAXONOMY_v1.md — Controlled vocabulary for species × tissue × assay and old/new coordinate mapping (WIRE-P1 prerequisite · v1 ratified version)

**Status**: RATIFIED v1 (approved on 2026-09-30; approval document `plans/known_issues_b2_20261001/out/ARBITRATION_RULING_C1-C14_v1.md`
sha256=aea4b4c592a092f115c78b4ee1ec81ecaf4eea1b9e2453c8ead39615f3b7fb8a; request document
`ARBITRATION_REQUEST_coordinates_C1-C14.md` sha256=88996f1039042fbdea8a1fd4bd9c6f109cbbc170adbd3e6ca4cffae159dd37a3）。
C1-C14 all approved per strict v0 proposal. The attribution table for known issue entries is **governed by this document**; coordinates not covered by the vocabulary are uniformly UNMAPPED and must not be auto-injected.
Basis: Architecture review adjudication (Astra formal review T1/T2): 'The organizational lexical surface of the formal matrix is not yet unified; resolution required first'; 'Fix conflicts in 17 faces/12 tissues/6 skeleton definitions first'.

## 1. Fact-checking of definition conflicts ("17 vs 12")

| Number | Actual Reference | Verification Result |
|---|---|---|
| "17 faces" | **File count** in `kb/baselines/*.json` | 17 = 12 tissue faces + 5 meta/variant files (`baselines.json` index, `_STAGE_DISCLOSURE`, `_marker_repair_retina_v6`, `fetal_development_transitions`, `retina__fetal_developing` developmental variant). **17 is not the length of the tissue axis** |
| "12 tissues" (Design draft §2.1) | List of tissue pages in cross-network proposal | retina, cornea, trabecular_meshwork, sclera, choroid, ciliary_body, lens, vitreous, optic_nerve, lacrimal, conjunctiva, pdr_membrane |
| "12 baseline faces" (Measured) | Tissue face entries in `kb/baselines` | retina, RPE, ciliary_body, optic_nerve, ocular_surface, trabecular_meshwork, lacrimal_gland, choroid, conjunctiva, iris, lens, sclera |
| "6 skeletons" | Baseline faces lacking donor-level composition data | choroid, conjunctiva, iris, lens, sclera (status=skeleton_mapping_backfilled) + lacrimal_gland (observed_single_study_pilot, no donor-level intervals)—composition controls do not participate in scoring, ≠ no risk ≠ no marker (Review stop order 6) |

**The two "12s" are not the same 12**: Baseline faces include RPE/iris/ocular_surface (super-classes) but lack cornea/vitreous/pdr_membrane;
The design axis is the reverse. Conflicting faces are registered line-by-line in §3, **C1-C14 approved (2026-09-30)**: canonical tissue axis = 15 faces, matrix area = 6×15=90 cells all placeholders (C1/C10),
Placeholder matrix is a machine artifact `pipeline/pitfalls/matrix/MATRIX_GRID.json` (regenerated on build, manual modification prohibited); cell activation uniformly goes through manual audit gates, **does not activate with area approval**.

## 2. Species Axis (Controlled Vocabulary)

| canonical id | Status | Notes |
|---|---|---|
| `human` | ACTIVE (evidence on record) | 5 of the six migrated cells |
| `mouse` | ACTIVE (evidence on record) | 1 of the six migrated cells |
| `rat` / `macaque` / `rabbit` / `zebrafish` | RESERVED (design vocabulary on record, no evidence) | C10 Approval: RESERVED species entering matrix = placeholder (only PLACEHOLDER/UNEXPLORED allowed), **no knowledge cells to be built**; promotion via "≥3 sourced pitfalls + manual audit gate" pre-registration channel (per-application approval, self-control prohibited). macaque×retina regularization not in this batch, submitted separately with second-batch deep-supplement materials (thickest material registered). S0 sample prediction for rat is currently out-of-domain abstain |

Species convention differences (case sensitivity/MT prefix/ID system) are registered as controlled observations outside entry scope.preparation/assay
in nomenclature pattern entries, not establishing a separate axis (C13 confirmation item).

## 3. Tissue Axis (Canonical ID Finalization = Minimum Merge Set of Baseline Faces ∪ Design Tissues, 15 Faces)

Canonical IDs prioritize retaining `kb/baselines` face names (do not modify existing knowledge layer primary keys); unique items from design axis added;
Mappings and conflicts registered line-by-line (C1 Approval: 15-face finalization; row rulings = approval results):

| # | canonical tissue_id | Baseline Face Mapping | Design Draft Mapping | Data Face Status | Conflict/Ruling Registration |
|---|---|---|---|---|---|
| 1 | `retina` | retina.json | retina | Composition filled | Regional sub-axis established as orthogonal region axis (§3.1, C8 Approval); entry KC-B1-human-retina-08 regenerated with region_scope annotation |
| 2 | `RPE` | RPE.json | (None) | filled | Design 12 lacks RPE—**C2 Approval adds independent face** (main player in eye diseases, category follows biology; "few" means low-support, not exclusion) |
| 3 | `ciliary_body` | ciliary_body.json | ciliary_body | filled | Consistent |
| 4 | `optic_nerve` | optic_nerve.json | optic_nerve | filled | Consistent |
| 5 | `trabecular_meshwork` | trabecular_meshwork.json | trabecular_meshwork | filled | Consistent |
| 6 | `lacrimal_gland` | lacrimal_gland.json | lacrimal | pilot (no donor-level intervals) | **C7 Approval: Naming unified to baseline face name lacrimal_gland** (design draft `lacrimal` is alias, no separate face) |
| 7 | `choroid` | choroid.json | choroid | skeleton | Composition panel construction queue (risk_notice and panel_gap are two independent objects, Review T5) |
| 8 | `conjunctiva` | conjunctiva.json | conjunctiva | skeleton | Same as above |
| 9 | `iris` | iris.json | (None) | skeleton | **C3 Approval retains baseline face name** (coordinates valid, status honestly skeleton) |
| 10 | `lens` | lens.json | lens | skeleton | Composition missing |
| 11 | `sclera` | sclera.json | sclera | skeleton | Composition missing |
| 12 | `ocular_surface` | ocular_surface.json | (Position of cornea) | filled | **Conflict ① (C4 Approval)**: cornea as independent canonical (six-cell evidence under cornea name), simultaneously hanging pointer on ocular_surface face; **"Corneal composition control must lock sampling domain" is mandatory mitigation** (baseline super-class = mixed pool of cornea/corneal limbus/sclera, entry KC-B1-human-cornea-04) |
| 13 | `cornea` | (Indirectly via ocular_surface) | cornea | Via super-class | See Conflict ①: After C4 Approval, cornea enters axis independently |
| 14 | `vitreous` | (No composition face) | vitreous | **Composition face missing** | **Conflict ② (C5 Approval)**: Coordinates valid, panel status=missing (**not skeleton**—normal vitreous has nearly no cells, "healthy composition face" may never hold); cell building transferred to panel_gap assessment; do not build healthy vitreous composition panel (entry KC-B1-human-vitreous-03 self-proves) |
| 15 | `fibrovascular_membrane` | (Composition in priors/composition/human_pdr_membrane.json; disease prior in priors/disease/PDR__fibrovascular_membrane.json; service dictionary name fibrovascular_membrane) | pdr_membrane | Has priors, no baselines face | **Conflict ③ (C6 Approval)**: canonical=`fibrovascular_membrane` (current service dictionary name, for MCP consumption); `pdr_membrane` retained as provenance name, pull-page layer performs alias mapping (consume.py PULL_TISSUE_ALIAS); **Current MCP service dictionary zero changes**; register panel_gap=lacking healthy control semantics, prohibit "disease material compared against healthy organ composition" (C14 Approval; entry KC-B1-human-pdr_membrane-03); panel supplementation obligation registration ≠ building panel |

### 3.1 Region Orthogonal Axis (C8 Approval, 2026-09-30)

`region ∈ {fovea, macula_peripheral_mix, peripheral, not_recorded}`—orthogonal to species/tissue/stage,
**Does not occupy tissue axis position, does not build grid dimension**. Semantics = claim-level/sample-level scope annotation axis:
- Mitigation action for high-risk entry KC-B1-008 (regional mixing false flag) in human×retina cell, "align region in composition control first", uses this axis as grammatical prerequisite—
  After establishing this axis, the mitigation is executable (previously registered as "missing sub-axis", with entry references having no landing point);
- Consumer side (S0/reading) groups by sample region_scope for comparison; **`not_recorded` must not be applied as `fovea` or `peripheral`**
  (Registration discipline, analogous to C12 treatment tri-state where not_recorded≠naive);
- Historical entries involving regional observation scope reset are regenerated per deep-supplement batch (this batch only supplements region_scope annotation for KC-B1-008).

stage (developmental stage) is an **orthogonal axis**, not occupying tissue axis position: `adult | fetal | developing` (source `retina__fetal_developing`
and `fetal_development_transitions`, `_STAGE_DISCLOSURE`); S0 suspected fetal hard gate consumes this axis.
Developmental pitfalls belong to PATTERN (C11 approval, branch 4; stage serves as claim-level scope annotation, do not create CELL variant grid).

## 4. assay axis (controlled vocabulary)

| canonical assay_id | Notes |
|---|---|
| `scRNA` | Single-cell suspension |
| `snRNA` | Nucleus suspension (left end of platform axis for entry KC-B1-human-retina-07) |
| `spatial` | Spatial transcriptomics (mouse-side dissociation-insensitive evidence route, KC-B1-mouse-retina-08) |
| `bulk` | **C9 approval supplemented term** (S0 main ledger includes GSE160306/179568 type bulk items; controlled vocabulary validation synchronously released). Scope reset for existing bulk observation entries in this batch = regenerate per deep-supplement batch, this batch only releases vocabulary and validation; bulk averaging-type failures establish separate PATTERN candidate (P24, bibliographic record unverified, not entered into ledger) |

preparation vocabulary (minimal proposal, used for entry scope.preparation):
`enzymatic_dissociation`、`short_dissociation_cold_protease`、`nuclear_extraction`、
`surgical_stripped_membrane`、`excised_whole_mount`、`vitrectomy_cassette_wash`、
`blunt_strip_TM`、`cultured_cell_line`、`paired_donor_tissue`。
Preparation descriptions not in vocabulary → entries handled as UNMAPPED_SCOPE or left blank and registered, do not inject self-created terms.
Sorting preparation family (immuno-sorting type) expanded term proposal attached to C9 same-batch registration (U15), **approved vocabulary is based on this document, unlisted terms must not be injected**.

disease_or_treatment vocabulary (minimal proposal):
`PDR`、`RRD`、`diabetic_retinopathy_nonPNR`、`glaucoma_TM`、`aging`、`anti_VEGT_treated`、`none_healthy`。
Conflict registration (**C12 approval**): `anti_VEGT_treated` term retained in register; treatment status observations uniformly registered as tri-state
`{treated, naive, not_recorded}`, **"not_recorded must not be treated as naive" is a mandatory mitigation** (six-grid generally lacks treatment records =
metadata gap, do not force fit); P23 (mixed pool due to missing treatment records) awaits on-disk source verification then transfers to claim with deep-supplement batch.

## 5. Attribution Adjudication Tree (This batch and B2 strictly execute per these five branches)

```text
1 Single species whole tissue            → SPECIES/{species}
2 Single tissue all species             → TISSUE/{tissue}
3 Single species × single tissue coordinate       → CELL/{species}__{tissue}
4 Multiple but not all OR determined by assay/preparation/disease/treatment conditions → PATTERN/{pattern_id}
5 Cannot map to this vocabulary          → UNMAPPED_SCOPE (automatic injection prohibited, registration only)
```

- No GLOBAL page type: Universal laws across species and tissues = Branch 4 (assay/method condition driven) attributed to PATTERN.
- "More specific takes precedence" is only used to determine applicable scope, not knowledge truth; low evidence level entries must not automatically override high evidence commonalities (Review T1).
- Pure community experience (community_lead) can only generate clues/verification_task/manual_review_required,
  must not generate hard_gate/panel_activation/named_label (Review T2).
- Grid five states (UNMAPPED/PLACEHOLDER/LEAD_ONLY/EVIDENCE_READY/WORKFLOW_READY) registered in page metadata;
  Six grids currently = EVIDENCE_READY (provisional) — ≥3 atomic entries from different failure modes with source localization mechanically verified
  (file pointer existence), **has not yet** completed six-grid manual audit (WORKFLOW_READY requires manual review, awaiting audit gate).
- Matrix area = 6 species × 15 canonical tissues = **90 grids fully placeholder** (C10 approval; machine-generated product, zero handwriting):
  human/mouse × 15 totaling 30 grids registered truthfully per five states, RESERVED four species × 15 totaling 60 grids uniformly PLACEHOLDER/UNEXPLORED.
  **Placeholder ≠ Activation**: This batch's criteria for qualifying candidates = 0 maintained (C item approval does not change activation state of any grid).

## 6. Migration Mapping (Six-grid coordinate system → canonical, C6/C7 approval finalized)

| Six-grid file system coordinate | canonical coordinate | Description |
|---|---|---|
| human__retina | human×retina | Direct pass-through |
| mouse__retina | mouse×retina | Direct pass-through |
| human__pdr_membrane | human×fibrovascular_membrane | Alias mapping (Conflict ③, C6 approval: canonical=fibrovascular_membrane, pdr_membrane retained as provenance name) |
| human__trabecular_meshwork | human×trabecular_meshwork | Direct pass-through |
| human__cornea | human×cornea | Legal after Conflict ① (C4 approval): cornea is an independent canonical entity; ocular_surface holds a pointer |
| human__vitreous | human×vitreous | Conflict ② (C5 approval): coordinates legal, composition aspect registered as missing (not skeleton) |
