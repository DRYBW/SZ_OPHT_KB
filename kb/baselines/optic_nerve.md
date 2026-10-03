# Composition Baseline: Human (Normal) Optic Nerve + Optic Disc snRNA adult-only main archive (OA-D003 HRA006282, donor-level conditional reference distribution, KB2c developmental axis listed separately)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_optic_nerve` | Status: filled_donor_level | Developmental Axis: **organism_stage=adult** | Generated: 2026-09-23 | Card: t_bad1fbab
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
- Two-tier identities: {'adult_only': 'baseline_human_optic_nerve__adult_only__kb2c', 'adult_pool': 'baseline_human_optic_nerve__adult_pool__v1.0'}

## Astra T2 metadata fields
- **Sampling Material**: Human optic nerve/optic disc ex vivo tissue (surgical sampling, eye bank donors; regional composition: ONH (optic disc/papilla) 355,363 nuclei, ON (optic nerve) 604,266 nuclei)
- **Disease Stage**: normal (disease column all normal; donors are systemic death donors, donor_cause_of_death includes tumors/sepsis etc., no ocular disease records for the eyeballs themselves)
- **Treatment Background**: Not recorded (eye bank donation metadata lacks treatment column) —— marked 'not recorded', no speculation
- **scRNA_vs_snRNA**: snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes) —— class proportions cannot be directly compared with scRNA cell suspension entries (e.g., D002 ocular surface)
- **Enrichment Steps**: No sorting records (metadata lacks enrichment column; whole-tissue nuclear suspension loaded directly onto instrument)
- **Dissociation Method**: mechanical dissociation,enzymatic dissociation×813,508 nuclei; mechanical dissociation,centrifugation×146,121 nuclei (sample_preservation=frozen in liquid nitrogen; collection=surgical resection)
- **Donor Count**: Main archive adult-only 74 donors / 98 donor units; Contrast archive adult_pool 83 donors / 107 units (includes 9 non-adult donors including newborn 15,177 nuclei → row-by-row details see excluded_nonadult_units)
- **Counting Denominator**: 959,629 nuclei (majorclass fully annotated)
- **Evidence Source**: Local measured recalculation (A) + CELLxGENE HRA006282 collection official annotation (portal) + Registry OA-D003

## Primary Reference: Donor-level conditional reference distribution (excluding sorting design layer)
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 0.0 | 0.0–1.58 | 0.0–6.7 | 98 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–1.31 | 98 |
| Astrocyte | 28.53 | 20.88–35.01 | 3.25–57.81 | 98 |
| BC | 0.0 | 0.0–7.58 | 0.0–24.76 | 98 |
| B_cell | 0.0 | 0.0–0.02 | 0.0–0.83 | 98 |
| Cone | 0.0 | 0.0–0.73 | 0.0–4.63 | 98 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 98 |
| Endothelial_cell | 3.08 | 1.53–4.88 | 0.0–29.36 | 98 |
| Fibroblast | 8.36 | 2.83–16.54 | 0.42–59.43 | 98 |
| HC | 0.0 | 0.0–1.2 | 0.0–3.44 | 98 |
| MG | 0.0 | 0.0–4.48 | 0.0–15.12 | 98 |
| Macrophage | 0.5 | 0.18–1.25 | 0.0–5.24 | 98 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 98 |
| Melanocyte | 0.0 | 0.0–0.22 | 0.0–19.45 | 98 |
| Microglia | 4.09 | 1.87–6.08 | 0.0–19.1 | 98 |
| Mural_cell | 1.39 | 0.66–2.43 | 0.0–11.76 | 98 |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 98 |
| Oligodendrocyte | 31.17 | 12.58–41.36 | 0.0–70.31 | 98 |
| Oligodendrocyte_precursor_cell | 0.51 | 0.02–2.72 | 0.0–8.05 | 98 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–8.31 | 98 |
| RGC | 0.0 | 0.0–0.49 | 0.0–2.79 | 98 |
| RPE | 0.0 | 0.0–0.61 | 0.0–22.5 | 98 |
| Rod | 0.0 | 0.0–8.64 | 0.0–52.58 | 98 |
| Schwann_cell | 0.06 | 0.0–0.27 | 0.0–2.15 | 98 |
| T_cell | 0.13 | 0.07–0.28 | 0.0–1.59 | 98 |

### Contrast Archive adult_pool (v1.0 mixed metrics, includes non-adult donors; tier=`baseline_human_optic_nerve__adult_pool__v1.0`) —— citing old v1.0 numbers must attach this tier identity

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 0.0 | 0.0–1.57 | 0.0–6.7 | 107 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–1.31 | 107 |
| Astrocyte | 28.94 | 21.17–35.39 | 3.25–70.08 | 107 |
| BC | 0.0 | 0.0–7.56 | 0.0–24.76 | 107 |
| B_cell | 0.01 | 0.0–0.02 | 0.0–0.83 | 107 |
| Cone | 0.0 | 0.0–0.61 | 0.0–4.63 | 107 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 107 |
| Endothelial_cell | 3.27 | 1.69–5.24 | 0.0–31.24 | 107 |
| Fibroblast | 8.92 | 3.24–16.72 | 0.42–59.43 | 107 |
| HC | 0.0 | 0.0–1.2 | 0.0–3.44 | 107 |
| MG | 0.0 | 0.0–3.72 | 0.0–15.12 | 107 |
| Macrophage | 0.51 | 0.2–1.28 | 0.0–5.24 | 107 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 107 |
| Melanocyte | 0.0 | 0.0–0.29 | 0.0–19.45 | 107 |
| Microglia | 4.08 | 1.8–6.3 | 0.0–19.1 | 107 |
| Mural_cell | 1.49 | 0.72–2.45 | 0.0–11.97 | 107 |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 107 |
| Oligodendrocyte | 27.96 | 10.59–40.67 | 0.0–70.31 | 107 |
| Oligodendrocyte_precursor_cell | 0.64 | 0.02–2.98 | 0.0–8.05 | 107 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–8.31 | 107 |
| RGC | 0.0 | 0.0–0.49 | 0.0–3.7 | 107 |
| RPE | 0.0 | 0.0–0.47 | 0.0–22.5 | 107 |
| Rod | 0.0 | 0.0–7.66 | 0.0–52.58 | 107 |
| Schwann_cell | 0.07 | 0.02–0.3 | 0.0–4.03 | 107 |
| T_cell | 0.13 | 0.06–0.28 | 0.0–1.59 | 107 |

### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)
| UBERON development_stage | organism_stage | Grading Rule | Nuclei/Cell Count | Number of Donors |
|---|---|---|---|---|
| 43-year-old stage | adult | Numerical age 43y vs threshold 18y | 78,263 | 3 |
| 69-year-old stage | adult | Numerical age 69y vs threshold 18y | 73,699 | 5 |
| 64-year-old stage | adult | Numerical age 64y vs threshold 18y | 68,748 | 5 |
| 71-year-old stage | adult | Numerical age 71y vs threshold 18y | 56,868 | 4 |
| 62-year-old stage | adult | Numerical age 62y vs threshold 18y | 54,875 | 3 |
| 67-year-old stage | adult | Numerical age 67y vs threshold 18y | 35,962 | 3 |
| 77-year-old stage | adult | Numerical age 77y vs threshold 18y | 32,893 | 5 |
| 65-year-old stage | adult | Numerical age 65y vs threshold 18y | 30,565 | 4 |
| 16-year-old stage | developing | Numerical age 16y vs threshold 18y | 27,212 | 3 |
| 72-year-old stage | adult | Numerical age 72y vs threshold 18y | 26,225 | 4 |
| 81-year-old stage | adult | Numerical age 81y vs threshold 18y | 23,537 | 2 |
| 70-year-old stage | adult | Numerical age 70y vs threshold 18y | 19,483 | 1 |
| 21-year-old stage | adult | Numerical age 21y vs threshold 18y | 19,210 | 1 |
| 10-year-old stage | developing | Numerical age 10y vs threshold 18y | 18,998 | 1 |
| 61-year-old stage | adult | Numerical age 61y vs threshold 18y | 18,682 | 2 |
| 42-year-old stage | adult | Numerical age 42y vs threshold 18y | 17,776 | 1 |
| 27-year-old stage | adult | Numeric age 27y vs threshold 18y | 16,928 | 2 |
| 32-year-old stage | adult | Numeric age 32y vs threshold 18y | 16,501 | 1 |
| 34-year-old stage | adult | Numeric age 34y vs threshold 18y | 16,364 | 2 |
| 25-year-old stage | adult | Numeric age 25y vs threshold 18y | 16,269 | 1 |
| 33-year-old stage | adult | Numeric age 33y vs threshold 18y | 16,010 | 1 |
| 18-year-old stage | adult | Numeric age 18y vs threshold 18y | 15,449 | 1 |
| newborn stage (0-28 days) | developing | Newborn/infant early postpartum → developing (Adjudication Q2) | 15,177 | 1 |
| 60-year-old stage | adult | Numeric age 60y vs threshold 18y | 14,758 | 2 |
| 76-year-old stage | adult | Numeric age 76y vs threshold 18y | 14,488 | 2 |
| 56-year-old stage | adult | Numeric age 56y vs threshold 18y | 14,406 | 1 |
| 30-year-old stage | adult | Numeric age 30y vs threshold 18y | 14,224 | 1 |
| 3-year-old stage | developing | Numeric age 3y vs threshold 18y | 13,748 | 1 |
| 85-year-old stage | adult | Numeric age 85y vs threshold 18y | 13,362 | 1 |
| 52-year-old stage | adult | Numeric age 52y vs threshold 18y | 13,317 | 1 |
| 15-year-old stage | developing | Numeric age 15y vs threshold 18y | 13,317 | 1 |
| 58-year-old stage | adult | Numeric age 58y vs threshold 18y | 12,874 | 2 |
| 47-year-old stage | adult | Numeric age 47y vs threshold 18y | 12,845 | 1 |
| 75-year-old stage | adult | Numeric age 75y vs threshold 18y | 12,130 | 1 |
| 82-year-old stage | adult | Numeric age 82y vs threshold 18y | 10,532 | 1 |
| 46-year-old stage | adult | Numeric age 46y vs threshold 18y | 10,451 | 1 |
| 68-year-old stage | adult | Numeric age 68y vs threshold 18y | 10,357 | 1 |
| 63-year-old stage | adult | Numeric age 63y vs threshold 18y | 8,965 | 1 |
| 90 year-old and over stage | adult | '90 year-old and over' lower bound >= threshold | 8,900 | 1 |
| 17-year-old stage | developing | Numeric age 17y vs threshold 18y | 8,175 | 1 |
| 45-year-old stage | adult | Numeric age 45y vs threshold 18y | 7,777 | 1 |
| 74-year-old stage | adult | Numeric age 74y vs threshold 18y | 7,776 | 1 |
| 54-year-old stage | adult | Numeric age 54y vs threshold 18y | 6,753 | 1 |
| 50-year-old stage | adult | Numeric age 50y vs threshold 18y | 4,676 | 1 |
| 37-year-old stage | adult | Numeric age 37y vs threshold 18y | 3,687 | 1 |
| 11-year-old stage | developing | Numeric age 11y vs threshold 18y | 3,443 | 1 |
| 53-year-old stage | adult | Numeric age 53y vs threshold 18y | 2,974 | 1 |

9 donors excluded from the main adult archive: `MMD_23_17738` (developing, 10-year-old stage, 18,998 nuclei); `BCM_22_0698` (developing, newborn stage (0-28 days), 15,177 nuclei); `BCM_23_0491` (developing, 16-year-old stage, 14,845 nuclei); `MMD_23_22486` (developing, 3-year-old stage, 13,748 nuclei); `MMD_23_21623` (developing, 15-year-old stage, 13,317 nuclei); `BCM_23_0131` (developing, 16-year-old stage, 10,136 nuclei); `MMD_23_21999` (developing, 17-year-old stage, 8,175 nuclei); `BCM_22_0769` (developing, 11-year-old stage, 3,443 nuclei); `MMD_23_20181` (developing, 16-year-old stage, 2,231 nuclei)

## Tool compatibility main table (major_classes)
| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |
|---|---|---|---|---|---|---|
| AC | 0.0 | 0.0–1.58 | 0.0–6.7 | 1.15 |  | A |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–1.31 | 0.06 |  | A |
| Astrocyte | 28.53 | 20.88–35.01 | 3.25–57.81 | 28.52 |  | A |
| BC | 0.0 | 0.0–7.58 | 0.0–24.76 | 3.48 |  | A |
| B_cell | 0.0 | 0.0–0.02 | 0.0–0.83 | 0.04 |  | A |
| Cone | 0.0 | 0.0–0.73 | 0.0–4.63 | 0.45 |  | A |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 0.01 |  | A |
| Endothelial_cell | 3.08 | 1.53–4.88 | 0.0–29.36 | 3.64 |  | A |
| Fibroblast | 8.36 | 2.83–16.54 | 0.42–59.43 | 12.39 |  | A |
| HC | 0.0 | 0.0–1.2 | 0.0–3.44 | 0.5 |  | A |
| MG | 0.0 | 0.0–4.48 | 0.0–15.12 | 1.68 |  | A |
| Macrophage | 0.5 | 0.18–1.25 | 0.0–5.24 | 1.02 |  | A |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 0.02 |  | A |
| Melanocyte | 0.0 | 0.0–0.22 | 0.0–19.45 | 0.86 |  | A |
| Microglia | 4.09 | 1.87–6.08 | 0.0–19.1 | 5.01 |  | A |
| Mural_cell | 1.39 | 0.66–2.43 | 0.0–11.76 | 1.8 |  | A |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 0.04 |  | A |
| Oligodendrocyte | 31.17 | 12.58–41.36 | 0.0–70.31 | 28.97 |  | A |
| Oligodendrocyte_precursor_cell | 0.51 | 0.02–2.72 | 0.0–8.05 | 1.97 |  | A |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–8.31 | 0.28 |  | A |
| RGC | 0.0 | 0.0–0.49 | 0.0–2.79 | 0.37 |  | A |
| RPE | 0.0 | 0.0–0.61 | 0.0–22.5 | 0.89 |  | A |
| Rod | 0.0 | 0.0–8.64 | 0.0–52.58 | 6.32 |  | A |
| Schwann_cell | 0.06 | 0.0–0.27 | 0.0–2.15 | 0.22 |  | A |
| T_cell | 0.13 | 0.07–0.28 | 0.0–1.59 | 0.3 |  | A |

## Stratified Details (Stratify by different enrichment/site priors for display; do not merge across layers; KB2c: Each layer table = adult-only, parentheses = number of pooled donors within the layer)
### Layer: Chen|ON (Optic Nerve)  (n_donors=56, n_cells=551,898, 57.51% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 0.0 | 0.0–0.0 | 0.0–2.57 | 53 |
| Adipocyte | 0.0 | 0.0–0.07 | 0.0–1.31 | 53 |
| Astrocyte | 29.33 | 23.95–35.06 | 5.61–57.81 | 53 |
| BC | 0.0 | 0.0–0.0 | 0.0–8.17 | 53 |
| B_cell | 0.0 | 0.0–0.01 | 0.0–0.45 | 53 |
| Cone | 0.0 | 0.0–0.0 | 0.0–1.15 | 53 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.03 | 53 |
| Endothelial_cell | 4.18 | 2.96–5.58 | 0.38–29.36 | 53 |
| Fibroblast | 14.91 | 8.31–21.01 | 0.82–59.43 | 53 |
| HC | 0.0 | 0.0–0.0 | 0.0–1.43 | 53 |
| MG | 0.0 | 0.0–0.0 | 0.0–3.22 | 53 |
| Macrophage | 0.61 | 0.3–1.46 | 0.0–5.24 | 53 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 53 |
| Melanocyte | 0.0 | 0.0–0.0 | 0.0–0.09 | 53 |
| Microglia | 5.54 | 3.53–8.34 | 0.0–19.1 | 53 |
| Mural_cell | 2.26 | 1.56–3.01 | 0.09–11.76 | 53 |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 53 |
| Oligodendrocyte | 37.35 | 26.3–41.64 | 0.0–63.55 | 53 |
| Oligodendrocyte_precursor_cell | 1.81 | 0.08–3.24 | 0.0–8.05 | 53 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–0.01 | 53 |
| RGC | 0.0 | 0.0–0.0 | 0.0–1.19 | 53 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.42 | 53 |
| Rod | 0.0 | 0.0–0.0 | 0.0–14.09 | 53 |
| Schwann_cell | 0.06 | 0.03–0.2 | 0.0–0.56 | 53 |
| T_cell | 0.14 | 0.07–0.27 | 0.0–1.48 | 53 |

### Layer: Chen|ONH (Optic Nerve Head/Optic Disc)  (n_donors=31, n_cells=261,610, 27.26% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 1.96 | 0.93–4.79 | 0.0–6.69 | 25 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–0.04 | 25 |
| Astrocyte | 25.31 | 13.99–31.82 | 3.25–56.81 | 25 |
| BC | 8.64 | 4.3–13.6 | 0.0–24.76 | 25 |
| B_cell | 0.01 | 0.0–0.08 | 0.0–0.83 | 25 |
| Cone | 0.91 | 0.44–2.08 | 0.0–4.63 | 25 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 25 |
| Endothelial_cell | 2.93 | 2.13–3.74 | 0.53–28.8 | 25 |
| Fibroblast | 7.14 | 3.58–9.55 | 1.08–21.25 | 25 |
| HC | 1.42 | 0.98–2.06 | 0.0–3.44 | 25 |
| MG | 6.55 | 2.92–8.13 | 0.0–15.12 | 25 |
| Macrophage | 0.8 | 0.28–1.5 | 0.06–3.33 | 25 |
| Mast_cell | 0.0 | 0.0–0.01 | 0.0–0.25 | 25 |
| Melanocyte | 0.69 | 0.21–1.26 | 0.0–19.45 | 25 |
| Microglia | 2.45 | 1.3–4.35 | 0.34–9.81 | 25 |
| Mural_cell | 1.03 | 0.78–1.41 | 0.18–3.98 | 25 |
| NK_cell | 0.01 | 0.0–0.03 | 0.0–0.23 | 25 |
| Oligodendrocyte | 9.37 | 1.63–20.06 | 0.0–45.17 | 25 |
| Oligodendrocyte_precursor_cell | 0.03 | 0.0–0.34 | 0.0–6.44 | 25 |
| Pigmented_cell | 0.03 | 0.0–0.11 | 0.0–8.31 | 25 |
| RGC | 0.84 | 0.14–1.95 | 0.0–2.79 | 25 |
| RPE | 1.38 | 0.64–2.08 | 0.0–22.5 | 25 |
| Rod | 13.31 | 4.11–19.31 | 0.05–44.85 | 25 |
| Schwann_cell | 0.14 | 0.02–0.42 | 0.0–1.33 | 25 |
| T_cell | 0.17 | 0.09–0.43 | 0.0–1.59 | 25 |

### Layer: Sanes|ON (Optic Nerve)  (n_donors=7, n_cells=52,368, 5.46% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–0.15 | 7 |
| Astrocyte | 32.62 | 30.91–35.64 | 16.61–44.89 | 7 |
| BC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| B_cell | 0.0 | 0.0–0.0 | 0.0–0.02 | 7 |
| Cone | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Dendritic_cell | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Endothelial_cell | 0.28 | 0.14–0.52 | 0.0–1.57 | 7 |
| Fibroblast | 2.05 | 1.46–2.49 | 0.42–6.79 | 7 |
| HC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| MG | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Macrophage | 0.09 | 0.03–0.12 | 0.0–0.24 | 7 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Melanocyte | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Microglia | 4.36 | 4.11–6.37 | 3.17–8.2 | 7 |
| Mural_cell | 0.05 | 0.02–0.16 | 0.0–0.82 | 7 |
| NK_cell | 0.0 | 0.0–0.0 | 0.0–0.03 | 7 |
| Oligodendrocyte | 54.62 | 53.48–57.6 | 41.15–70.31 | 7 |
| Oligodendrocyte_precursor_cell | 4.89 | 1.68–5.15 | 0.12–6.39 | 7 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| RGC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Rod | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Schwann_cell | 0.0 | 0.0–0.0 | 0.0–0.16 | 7 |
| T_cell | 0.01 | 0.0–0.05 | 0.0–0.1 | 7 |

### Layer: Sanes|ONH (Optic Nerve Head/Optic Disc)  (n_donors=13, n_cells=93,753, 9.77% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 4.86 | 3.82–5.96 | 0.0–6.7 | 13 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–0.05 | 13 |
| Astrocyte | 17.52 | 11.02–31.21 | 8.23–56.59 | 13 |
| BC | 14.5 | 7.28–16.49 | 0.0–18.76 | 13 |
| B_cell | 0.02 | 0.0–0.03 | 0.0–0.21 | 13 |
| Cone | 1.83 | 0.08–2.23 | 0.0–2.94 | 13 |
| Dendritic_cell | 0.0 | 0.0–0.0 | 0.0–0.01 | 13 |
| Endothelial_cell | 0.95 | 0.82–1.38 | 0.51–1.78 | 13 |
| Fibroblast | 1.5 | 1.05–2.52 | 0.51–9.42 | 13 |
| HC | 2.1 | 1.28–2.53 | 0.0–2.9 | 13 |
| MG | 5.66 | 3.34–6.13 | 0.0–12.88 | 13 |
| Macrophage | 0.17 | 0.14–0.27 | 0.0–1.85 | 13 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.1 | 13 |
| Melanocyte | 0.22 | 0.09–0.3 | 0.0–2.19 | 13 |
| Microglia | 1.06 | 0.82–2.33 | 0.36–3.08 | 13 |
| Mural_cell | 0.48 | 0.33–0.79 | 0.23–1.73 | 13 |
| NK_cell | 0.03 | 0.02–0.06 | 0.0–0.08 | 13 |
| Oligodendrocyte | 14.25 | 8.97–20.24 | 0.0–58.03 | 13 |
| Oligodendrocyte_precursor_cell | 0.06 | 0.03–0.5 | 0.0–1.5 | 13 |
| Pigmented_cell | 0.0 | 0.0–0.01 | 0.0–0.28 | 13 |
| RGC | 0.69 | 0.58–1.36 | 0.0–2.72 | 13 |
| RPE | 0.42 | 0.37–1.4 | 0.0–2.67 | 13 |
| Rod | 32.98 | 7.26–41.31 | 0.0–52.58 | 13 |
| Schwann_cell | 0.09 | 0.0–0.25 | 0.0–2.15 | 13 |
| T_cell | 0.13 | 0.1–0.3 | 0.04–0.97 | 13 |

## Subtype layer (% of annotated cells within class, pooled within class basis)

## Flag semantics
**expected_low_but_present**: T/B/NK/DC/Mast total <1% (normal sparse immune presence in neural tissue); Schwann_cell 0.22% (PN myelinating support cells; PN enrichment limited to central segment in single-nucleus suspension); Mural_cell 1.8% / Endothelial_cell 3.6% (vascular support layer)

**unexpected**: Retinal neuron classes (Rod/Cone/BC/HC/AC/RGC) pooled 12.27% + RPE/pigment classes 1.17% — optic disc sampling introduces peripapillary retina/choroid tissue; this is capture composition, not ground truth for optic nerve proper; do not treat this layer as expected proportions for optic nerve when comparing disease samples

**contamination_suspect**: Melanocyte 0.86% (leptomeningeal/pigmented tissue carryover; slightly elevated within normal range, interpret in context of dissection plane)

## Notes
1. MG=Müller glia (1.7%) and Microglia=microglia (5.0%) are two distinct identities, coexisting in the portal vocabulary — do not conflate in downstream references; the same rule applies to retinal abbreviations such as AC(amacrine cells)/BC(bipolar cells).
2. The donor pools of Chen (Baylor, ~85%) and Sanes (Harvard) differ significantly in size; data are stratified into 4 layers by source × anatomical site. In the main view, each donor-level unit is weighted equally, preventing large pools from dominating, but inter-stratum differences must be assessed via strata rather than solely through the main view.
3. The denominator for this count includes peripapillary retinal sources (~15%); for a 'pure optic nerve' reference interval, use the ON (cranial nerve II) layer within strata.
4. Comparisons between snRNA metrics (nuclear suspension, including intronic reads) and scRNA data require caution (Astra T2).
5. v1.1 (KB2c t_be336eee): Main archive = adult-only (>=18y, adjudication Q2); v1.0 mixed scope (including newborn/3-17 years) is retained in donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0); identity signatures of the two archives are separated and not mixed.

## Source List
| sid | Type | Label |
|---|---|---|
| `ON_LOCAL` | dataset | Local file /mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad |
| `ON_PORTAL` | dataset | Human Optic Nerve / Optic Nerve Head Atlas, CELLxGENE collection HRA006282 (portal official annotation; registry OA-D003, verified 2026-08-11) |

