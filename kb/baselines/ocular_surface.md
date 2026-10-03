# Composition Baseline: Human (Normal) Ocular Surface Adult-only Main Archive — Cornea/Limbus/Sclera Superclass (D002, Donor-level Conditional Reference Distribution, KB2c Developmental Axis Listed Separately)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_ocular_surface` | status: filled_donor_level | developmental axis: **organism_stage=adult** | generated: 2026-09-23 | card: t_16c3e020
> **KB3 development record (Card t_5425a7ca)**: development_stage=**adult** —— KB3 prohibition (PI Red Line 2026-09-23): developmental data must not enter the adult baseline statistical pool, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal do not serve as mutual references.
> This file is automatically rendered from the corresponding .json by `/mnt/D/EyeKB/scripts/baselines/build_baselines.py` — modify content in JSON+script; manual MD edits will be overwritten.

**Usage scope (Astra T2 adjudication finalized): This baseline = identity reference + background control for cell composition captured from this sampling material under this experimental workflow; **must not be used as a composition compliance threshold**. Sampling targets for disease surgical materials ≠ healthy organs (e.g., PDR fibrovascular membrane must not be validated against healthy retina composition); if annotation data yields identities outside the list → trigger unexpected flag only, do not force into listed identities (label acceptance requires contextual consistency check, not whitelist positioning).**

## Evidence grade definitions
- **A**: Local empirical recalculation (with file paths+scripts)
- **B**: Direct reporting in original literature
- **C**: Empirical intervals derived from A-grade source data at donor level/cross-study distribution
- **qualitative**: Literature provides only qualitative description → store qualitative only, do not fabricate intervals (Astra T2)
- **not_estimable**: Interval cannot be estimated — valid state, annotation may proceed (Astra T2)

## Developmental axis definitions (KB2c adjudication 2026-09-23 — threshold changes require adjudication)
- Top-level axis: `organism_stage` ∈ ['fetal', 'adult', 'developing', 'unknown']
- **adult**: UBERON development_stage digital age >= 18y judged adult; explicit adult terms (late/prime/middle/mature/human adult stage, decade>=3rd) also judged adult and rule recorded; threshold changes require adjudication (KB2c Q2, 2026-09-23)
- **developing**: newborn/infant/postnatal stage and <18y digital age/age range → developing (KB2c Q2)
- **fetal**: fetal/embryonic/gestation/Carnegie terms → fetal; never merged into adult main tier (red line 1)
- **unknown**: No age column/unmapped terms/organoid/age range crossing thresholds → unknown, disclosure line required, silent assignment to adult prohibited (red line 2)
- aging orthogonal axis: >=60 elderly stratification is not on this axis — aging is an orthogonal independent axis, to be established as a separate entry in the future (adjudication Q2)
- Two-tier identity: {'adult_only': 'baseline_human_ocular_surface__adult_only__kb2c', 'adult_pool': 'baseline_human_ocular_surface__adult_pool__v1.0'}

## Astra T2 metadata fields
- **Sampling Material**: Human ocular surface ex vivo tissue: cornea / corneo-scleral junction(limbus) / sclera / ocular surface region / corneal endothelium (transplant corneal endothelial edge fragments)
- **Disease Stage**: normal (disease column all normal; donors are eye bank donated limbus/scleral ring)
- **Treatment Background**: Not recorded (eye bank donation metadata lacks treatment column)
- **Platform**: scRNA-seq (suspension_type=cell 100%, 10x 3' v2/v3) —— Different metric from D001 retina(nuclei), note when comparing across baselines
- **Enrichment Steps**: No cell sorting records (whole tissue dissociation directly sequenced)
- **Dissociation Method**: Mechanical+enzymatic dissociation; main reagents: 2 mg/ml Collagenase A×206,010 cells; 1.5 mg/ml Collagenase A×166,417 cells; 2.5 mg/ml Collagenase A×88,531 cells; 5 mg/ml collagenase A×46,892 cells
- **Donor Count**: Main archive adult-only 41 donors / 67 donor units; control archive adult_pool 50 donors / 84 units (incl 9 non-adult donors such as newborn 0-28d → row-by-row see excluded_nonadult_units)
- **Count Denominator**: 577,857 cells (majorclass fully annotated)
- **Evidence Source**: Local empirical recomputation (A) + CELLxGENE collection official annotation (portal)

## Primary Reference: Donor-level conditional reference distribution (excluding sorting design layer)
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–100.0 | 67 |
| Endothelium | 3.42 | 0.0–8.99 | 0.0–43.48 | 67 |
| Epithelium | 50.48 | 7.26–70.25 | 0.0–99.62 | 67 |
| Fibroblasts | 28.53 | 12.65–44.01 | 0.0–93.77 | 67 |
| Immune Cells | 1.12 | 0.4–2.6 | 0.0–37.71 | 67 |
| Melanocytes | 0.29 | 0.0–2.45 | 0.0–48.63 | 67 |
| Pericytes | 2.03 | 0.0–4.27 | 0.0–41.31 | 67 |
| Schwann Cells | 0.23 | 0.0–1.06 | 0.0–20.52 | 67 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–63.33 | 67 |


### Corneal Stroma Keratocyte Reference Cell (Card t_e1febb8e, added 2026-09-24; astra R5 revised version)
> Root cause: KB2 Q6::15 (ALDH3A1+KERA) systematically mislabeled as Corneal Endothelium. This cell=composition side of evidence coverage/hierarchical mapping fix; no new major_classes rows added (to avoid double counting with Fibroblasts superclass).
- **D002 Empirical (Grade A, main archive same metric)**: adult 67 donor units; keratocyte label pooled within class 23.42%, unit median 20.68% [IQR 6.19–40.26, range 0–91.19]; denominator=D002 mixed ocular surface capture events (cornea group), not independently verified identity, not pure cornea tissue ground truth, not used as compliance threshold. Whole file (incl non-adult) metric 17.95% archived workspace only.
- **Literature Range Cell**: Missing items fall into blocked (locatable full-text percentage intervals not pinned down; confocal density metrics must not masquerade as composition percentages) —— see JSON stromal_keratocyte_reference.literature_anchor.
- **Supporting**: Marker library supplement (Keratocytes/Corneal Endothelium, v1-membrane-20260924-r2) + concept entries EYEKBC-0018/0019; hierarchical relationship: Keratocytes ⊂ Fibroblasts superclass (Q6 system).

### Control Archive adult_pool (v1.0 mixed metric, incl non-adult donors; tier=`baseline_human_ocular_surface__adult_pool__v1.0`) —— Citing v1.0 old numbers can only attach to this archive identity

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–100.0 | 84 |
| Endothelium | 3.32 | 0.0–8.89 | 0.0–43.48 | 84 |
| Epithelium | 51.18 | 6.97–71.49 | 0.0–99.62 | 84 |
| Fibroblasts | 29.96 | 13.76–53.83 | 0.0–93.77 | 84 |
| Immune Cells | 1.1 | 0.41–2.28 | 0.0–37.71 | 84 |
| Melanocytes | 0.27 | 0.0–2.17 | 0.0–48.63 | 84 |
| Pericytes | 2.27 | 0.0–6.01 | 0.0–41.31 | 84 |
| Schwann Cells | 0.23 | 0.0–1.14 | 0.0–20.52 | 84 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–63.33 | 84 |

### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)
| UBERON development_stage | organism_stage | Grading Rule | Nuclei/Cell Count | Number of Donors |
|---|---|---|---|---|
| 64-year-old stage | adult | Numeric age 64y vs threshold 18y | 56,324 | 3 |
| 43-year-old stage | adult | Numeric age 43y vs threshold 18y | 45,727 | 2 |
| 32-year-old stage | adult | Numeric age 32y vs threshold 18y | 39,770 | 1 |
| 72-year-old stage | adult | Numeric age 72y vs threshold 18y | 30,149 | 1 |
| 2-year-old stage | developing | Numeric age 2y vs threshold 18y | 27,157 | 1 |
| 25-year-old stage | adult | Numeric age 25y vs threshold 18y | 26,051 | 1 |
| newborn stage (0-28 days) | developing | Newborn/infant early postnatal→developing (Adjudication Q2) | 25,018 | 1 |
| 1-year-old stage | developing | Numeric age 1y vs threshold 18y | 23,364 | 1 |
| 55-year-old stage | adult | Numeric age 55y vs threshold 18y | 22,600 | 1 |
| 67-year-old stage | adult | Numeric age 67y vs threshold 18y | 22,556 | 1 |
| 11-year-old stage | developing | Numeric age 11y vs threshold 18y | 22,308 | 1 |
| 70-year-old stage | adult | Numeric age 70y vs threshold 18y | 21,432 | 1 |
| 87-year-old stage | adult | Numeric age 87y vs threshold 18y | 19,901 | 1 |
| 61-year-old stage | adult | Numeric age 61y vs threshold 18y | 19,093 | 2 |
| 51-year-old stage | adult | Numeric age 51y vs threshold 18y | 17,436 | 2 |
| 10-year-old stage | developing | Numeric age 10y vs threshold 18y | 15,667 | 1 |
| 27-year-old stage | adult | Numeric age 27y vs threshold 18y | 15,052 | 1 |
| 34-year-old stage | adult | Numeric age 34y vs threshold 18y | 12,347 | 1 |
| 53-year-old stage | adult | Numeric age 53y vs threshold 18y | 11,393 | 1 |
| 75-year-old stage | adult | Numeric age 75y vs threshold 18y | 10,823 | 4 |
| postnatal stage | developing | Postnatal→developing (Adjudication Q1 mapping) | 10,550 | 2 |
| 65-year-old stage | adult | Numeric age 65y vs threshold 18y | 9,813 | 1 |
| 41-year-old stage | adult | Numeric age 41y vs threshold 18y | 8,904 | 1 |
| 13-year-old stage | developing | Numeric age 13y vs threshold 18y | 8,281 | 1 |
| 90 year-old and over stage | adult | '90 year-old and over' lower bound >= threshold | 7,997 | 1 |
| 74-year-old stage | adult | Numeric age 74y vs threshold 18y | 7,504 | 1 |
| 33-year-old stage | adult | Numeric age 33y vs threshold 18y | 7,159 | 1 |
| 69-year-old stage | adult | Numeric age 69y vs threshold 18y | 6,063 | 1 |
| 84-year-old stage | adult | Numeric age 84y vs threshold 18y | 4,320 | 2 |
| 86-year-old stage | adult | Numeric age 86y vs threshold 18y | 4,293 | 2 |
| 77-year-old stage | adult | Numeric age 77y vs threshold 18y | 3,352 | 1 |
| 48-year-old stage | adult | Numeric age 48y vs threshold 18y | 3,224 | 1 |
| 62-year-old stage | adult | Numeric age 62y vs threshold 18y | 3,047 | 1 |
| 22-year-old stage | adult | Numeric age 22y vs threshold 18y | 2,533 | 1 |
| 16-year-old stage | developing | Numeric age 16y vs threshold 18y | 2,245 | 1 |
| 45-year-old stage | adult | Numeric age 45y vs threshold 18y | 1,879 | 1 |
| 83-year-old stage | adult | Numeric age 83y vs threshold 18y | 1,595 | 1 |
| 39-year-old stage | adult | Numeric age 39y vs threshold 18y | 732 | 1 |
| eighth decade stage | adult | Eighth decade = 70-79y lower bound >= threshold | 198 | 1 |

9 donors excluded from the main adult archive: `BCM_22_0496`(developing, 2-year-old stage, 27,157 nuclei); `BCM_22_0698`(developing, newborn stage (0-28 days), 25,018 nuclei); `BCM_22_0485`(developing, 1-year-old stage, 23,364 nuclei); `BCM_22_0769`(developing, 11-year-old stage, 22,308 nuclei); `BCM_21_0999`(developing, 10-year-old stage, 15,667 nuclei); `shi_donor1`(developing, 13-year-old stage, 8,281 nuclei); `chen_donor1`(developing, postnatal stage, 6,249 nuclei); `chen_donor2`(developing, postnatal stage, 4,301 nuclei); `BCM_23_0131`(developing, 16-year-old stage, 2,245 nuclei)

## Tool compatibility main table (major_classes)
| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |
|---|---|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–100.0 | 0.07 |  | A |
| Endothelium | 3.42 | 0.0–8.99 | 0.0–43.48 | 5.76 |  | A |
| Epithelium | 50.48 | 7.26–70.25 | 0.0–99.62 | 43.32 |  | A |
| Fibroblasts | 28.53 | 12.65–44.01 | 0.0–93.77 | 39.84 |  | A |
| Immune Cells | 1.12 | 0.4–2.6 | 0.0–37.71 | 1.73 |  | A |
| Melanocytes | 0.29 | 0.0–2.45 | 0.0–48.63 | 1.25 |  | A |
| Pericytes | 2.03 | 0.0–4.27 | 0.0–41.31 | 6.49 |  | A |
| Schwann Cells | 0.23 | 0.0–1.06 | 0.0–20.52 | 1.05 |  | A |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–63.33 | 0.48 |  | A |

## Stratified Details (Stratify by different enrichment/site priors for display; do not merge across layers; KB2c: Each layer table = adult-only, parentheses = number of pooled donors within the layer)
### Layer: |cornea (including corneal epithelium/stroma)  (n_donors=34, n_cells=218,598)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–2.64 | 29 |
| Endothelium | 0.0 | 0.0–1.35 | 0.0–15.6 | 29 |
| Epithelium | 63.08 | 29.31–79.27 | 4.83–99.62 | 29 |
| Fibroblasts | 32.09 | 14.88–67.25 | 0.0–93.77 | 29 |
| Immune Cells | 0.55 | 0.31–1.58 | 0.0–9.5 | 29 |
| Melanocytes | 0.0 | 0.0–0.71 | 0.0–6.6 | 29 |
| Pericytes | 0.0 | 0.0–0.25 | 0.0–3.72 | 29 |
| Schwann Cells | 0.0 | 0.0–0.0 | 0.0–3.31 | 29 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–0.64 | 29 |

### Layer: |corneal endothelium (separate layer, only 404 cells)  (n_donors=2, n_cells=404)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 100.0 | 100.0–100.0 | 100.0–100.0 | 2 |
| Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Epithelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Fibroblasts | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Immune Cells | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Melanocytes | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Pericytes | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Schwann Cells | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |

### Layer: |corneo-scleral junction (limbus region)  (n_donors=28, n_cells=244,108)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 22 |
| Endothelium | 7.25 | 5.38–12.02 | 0.92–18.67 | 22 |
| Epithelium | 58.44 | 36.9–67.75 | 0.0–91.73 | 22 |
| Fibroblasts | 26.39 | 7.23–37.8 | 0.0–89.24 | 22 |
| Immune Cells | 1.8 | 0.85–2.66 | 0.23–37.71 | 22 |
| Melanocytes | 1.66 | 0.31–4.75 | 0.0–21.21 | 22 |
| Pericytes | 3.71 | 2.58–6.07 | 0.0–19.37 | 22 |
| Schwann Cells | 0.7 | 0.23–1.06 | 0.0–20.52 | 22 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–11.81 | 22 |

### Layer: |ocular surface region (mixed)  (n_donors=4, n_cells=14,934)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 4 |
| Endothelium | 5.1 | 3.98–6.51 | 2.45–8.9 | 4 |
| Epithelium | 58.19 | 48.71–67.9 | 43.42–73.92 | 4 |
| Fibroblasts | 23.07 | 17.06–30.8 | 16.93–36.1 | 4 |
| Immune Cells | 4.95 | 3.7–5.87 | 2.2–6.4 | 4 |
| Melanocytes | 0.71 | 0.28–3.28 | 0.0–9.99 | 4 |
| Pericytes | 2.11 | 1.93–2.59 | 1.63–3.79 | 4 |
| Schwann Cells | 0.86 | 0.55–1.26 | 0.27–1.82 | 4 |
| Smooth Muscle Cells | 0.53 | 0.05–1.04 | 0.03–1.13 | 4 |

### Layer: |sclera (n_donors=16, n_cells=99,813)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 10 |
| Endothelium | 11.88 | 8.63–17.21 | 6.56–43.48 | 10 |
| Epithelium | 0.15 | 0.0–2.71 | 0.0–9.73 | 10 |
| Fibroblasts | 40.45 | 34.26–51.56 | 3.04–77.02 | 10 |
| Immune Cells | 1.16 | 0.51–4.4 | 0.0–22.81 | 10 |
| Melanocytes | 0.27 | 0.0–5.71 | 0.0–48.63 | 10 |
| Pericytes | 16.4 | 12.88–34.62 | 0.0–41.31 | 10 |
| Schwann Cells | 1.64 | 0.28–2.24 | 0.0–3.85 | 10 |
| Smooth Muscle Cells | 0.0 | 0.0–0.41 | 0.0–63.33 | 10 |

## Subtype layer (% of annotated cells within class, pooled within class basis)
- **Fibroblasts**: Corneal Stromal Keratocytes 45.1%; Limbus Fibroblasts 18.3%; Limbus/Sclera Fibroblasts - C2 18.3%; Limbus/Sclera Fibroblasts - C1 14.3%; Sclera Fibroblasts 4.0%
- **Epithelium**: Corneal_superficial_TDC 25.4%; Corneal_suprabasal_PMC 18.2%; Limbus_suprabasal_eTAC_ConjFate 11.8%; Limbus_suprabasal_eTAC_CorFate 11.5%; Limbus_basal_LSC/LPC 11.0%; Conj_basal 7.5%
- **Pericytes**: Pericytes 100.0%
- **Endothelium**: Venule_Sclera 53.4%; Capillary 16.4%; Venule_postCapillary 16.3%; Lymphatic_Endo 10.3%; Artery 3.6%
- **Schwann Cells**: Schwann_N 89.2%; Schwann_M 10.8%
- **Immune Cells**: Macrophages 49.6%; NK/T Cells 39.4%; Mast Cells 6.3%; Monocytes 2.5%; B Cells 2.1%
- **Melanocytes**: Melanocytes 100.0%
- **Smooth Muscle Cells**: Smooth Muscle Cells 100.0%
- **Corneal Endothelium**: Corneal_Endo 100.0%

## Flag semantics
**expected_low_but_present**: Corneal Endothelium (pooled 0.07%) —— contributed only by corneal endothelial edge fragments from eye banks; near-zero in routine limbal samples; Melanocytes/Schwann Cells/Smooth Muscle Cells <2%

**unexpected**: Presence of photoreceptors/retinal neuron classes (sampling overflow into retina?); abundant hematopoietic maturation markers (FCN1/LYZ granulocytic lineage) —— donor blood residue flag

**contamination_suspect**: published_annotation column dominated by red blood cells layer (525,617 annotations) —— blood residue is a known primary contamination in this library, see caveat; melanin granule/pigmented tissue contamination (pigmented donor sclera)

## Notes
1. Local D002 file = 577,857 cells / 50 donors, a subset extraction from collection level (>1M/102) (metric=local measurement); backfilling full collection requires download approval, listed as 'pending backfill'.
2. 'Majorclass=Immune Cells' is only 1.7%: sparse ocular surface resident immunity + no immune enrichment step —— immune proportion cannot be compared against inflammatory disease samples.
3. Coexistence of published_annotation and majorclass: published_annotation='red blood cells' dominating indicates RBCs were not cleanly removed from majorclass? No —— the 9 majorclasses contain no RBC class, RBC signals are dispersed across all classes, counting denominator includes RBC-contaminated nuclei, percentages per class represent 'captured event composition' rather than tissue ground truth (Astra T2 metric declaration).
4. Independent entries for sclera/conjunctiva refer to corresponding skeleton files; this corneo-scleral junction layer ≠ independent conjunctival baseline.
5. v1.1 (KB2c t_be336eee): Main archive = adult-only (>=18y); v1.0 mixed metrics (including newborn 0-28d 25,018 cells + postnatal/children/adolescents) retained in donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0). FALLBACK_BLOCKED guard implemented (triggers fallback prohibition when 0 adult donors in tissue group) —— current measurement triggered 0 layers, each tissue group's adult-only has real support.

## Source List
| sid | Type | Label |
|---|---|---|
| `D002_LOCAL` | dataset | Local file /mnt/D/OcularKB/data/D002_ocularsurface/D002_allcells_578K.h5ad |
| `D002_PORTAL` | dataset | Human Ocular Surface Cell Atlas, CELLxGENE collection (portal official annotation) |

