# Composition baseline: Human (normal) neural retina adult-only main archive (D001 HRCA, donor-level conditional reference distribution, KB2c developmental axis listed separately)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_retina` | status: filled_donor_level | developmental axis: **organism_stage=adult** | generated: 2026-09-23 | card: t_16c3e020
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
- Two-tier identities: {'adult_only': 'baseline_human_retina__adult_only__kb2c', 'adult_pool': 'baseline_human_retina__adult_pool__v1.0'}

## Astra T2 metadata fields
- **Sampling material**: Human neural retina ex vivo tissue (regional composition: peripheral region of retina 1,568,477, macula lutea 1,077,597, fovea centralis 434,131, macula lutea proper 97,105)
- **Disease stage**: normal (disease column all normal; donors predominantly elderly, with the 90+ age segment being largest)
- **Treatment background**: Not recorded (public atlas metadata lacks treatment column) — marked as 'not recorded', no speculation
- **Platform**: snRNA-seq (suspension_type=nucleus 100%, nuclear suspension)
- **Enrichment steps**: Stratification: majority naive; 1,334,033 nuclei underwent NeuN+ neuronal nucleus sorting (Chen_a/ancestry subset); Chen_rgc study entire layer designed for RGC enrichment
- **Dissociation methods**: Chen_a=0.02% NP40 (nuclear extraction); Chen_ancestry=0.02% NP40 (nuclear extraction); Chen_b_GSE226108=0.02% NP40 (nuclear extraction); Chen_c_GSE247157=0.02% NP40 (nuclear extraction); Chen_rgc=0.02% NP40 (nuclear extraction); Shekhar_GSE237204=unknown
- **Number of donors**: Main archive adult-only 97 donors / 113 donor units; contrast archive adult_pool 104 donors / 120 units (includes 7 non-adult donors → see excluded_nonadult_units row-by-row, KB2c adjudication Q2 threshold >=18y)
- **Count denominator**: 3,177,310 nuclei (majorclass fully annotated)
- **Evidence sources**: Local empirical recalculation (A) + HRCA paper (B, PMID 41578023) + old KB1 literature anchors

## Primary Reference: Donor-level conditional reference distribution (excluding sorting design layer)
> Stratification scope: Main archive = 6 studies excluding Chen_rgc (RGC enrichment design) and NeuN+ sorted layers from each study, and only organism_stage=adult (>=18y) donor units (113 total); Method: Donor-level: calculate proportions for 10 classes per donor unit first, then aggregate median/IQR/range across donors; Stratification = Study × Enrichment (× Site, D002 side); pooled columns are for comparison only and suffer from weighting bias due to large donors
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 8.46 | 6.55–10.96 | 3.59–70.83 | 113 |
| Astrocyte | 0.37 | 0.05–0.9 | 0.0–5.38 | 113 |
| BC | 19.99 | 15.21–26.98 | 0.13–49.97 | 113 |
| Cone | 3.27 | 2.3–5.21 | 0.0–13.1 | 113 |
| HC | 2.78 | 1.38–4.47 | 0.0–13.25 | 113 |
| MG | 8.75 | 5.28–11.48 | 0.0–24.66 | 113 |
| Microglia | 0.14 | 0.0–0.22 | 0.0–1.22 | 113 |
| RGC | 3.23 | 0.88–8.7 | 0.0–92.41 | 113 |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 113 |
| Rod | 48.85 | 22.06–57.56 | 0.0–77.97 | 113 |

### Contrast archive adult_pool (v1.0 mixed scope, including non-adult donors; tier=`baseline_human_retina__adult_pool__v1.0`) —— citations of v1.0 legacy figures must attach this archive identity

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 8.45 | 6.54–10.77 | 3.59–70.83 | 120 |
| Astrocyte | 0.37 | 0.05–0.92 | 0.0–12.93 | 120 |
| BC | 20.35 | 15.27–27.86 | 0.13–49.97 | 120 |
| Cone | 3.26 | 2.14–4.97 | 0.0–13.1 | 120 |
| HC | 2.91 | 1.41–4.52 | 0.0–13.25 | 120 |
| MG | 8.78 | 5.22–11.64 | 0.0–24.66 | 120 |
| Microglia | 0.14 | 0.0–0.23 | 0.0–1.22 | 120 |
| RGC | 2.95 | 0.86–8.42 | 0.0–92.41 | 120 |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 120 |
| Rod | 48.27 | 23.91–57.46 | 0.0–77.97 | 120 |

### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)
| UBERON development_stage | organism_stage | Grading Rule | Nuclei/Cell Count | Number of Donors |
|---|---|---|---|---|
| 90 year-old and over stage | adult | '90 year-old and over' lower bound >= threshold | 369,477 | 5 |
| 69-year-old stage | adult | Numeric age 69y vs threshold 18y | 170,764 | 6 |
| 64-year-old stage | adult | Numeric age 64y vs threshold 18y | 170,635 | 4 |
| 73-year-old stage | adult | Numeric age 73y vs threshold 18y | 164,811 | 2 |
| 82-year-old stage | adult | Numeric age 82y vs threshold 18y | 162,339 | 3 |
| 86-year-old stage | adult | Numeric age 86y vs threshold 18y | 133,685 | 3 |
| 71-year-old stage | adult | Numeric age 71y vs threshold 18y | 130,930 | 5 |
| 77-year-old stage | adult | Numeric age 77y vs threshold 18y | 110,926 | 5 |
| 67-year-old stage | adult | Numeric age 67y vs threshold 18y | 105,577 | 4 |
| 81-year-old stage | adult | Numeric age 81y vs threshold 18y | 95,313 | 3 |
| 68-year-old stage | adult | Numeric age 68y vs threshold 18y | 94,341 | 2 |
| 43-year-old stage | adult | Numeric age 43y vs threshold 18y | 85,308 | 3 |
| 80-year-old stage | adult | Numeric age 80y vs threshold 18y | 82,752 | 1 |
| 65-year-old stage | adult | Numeric age 65y vs threshold 18y | 80,114 | 4 |
| 66-year-old stage | adult | Numeric age 66y vs threshold 18y | 72,396 | 1 |
| 85-year-old stage | adult | Numeric age 85y vs threshold 18y | 66,992 | 2 |
| 72-year-old stage | adult | Numeric age 72y vs threshold 18y | 66,338 | 3 |
| 21-year-old stage | adult | Numeric age 21y vs threshold 18y | 65,728 | 1 |
| 78-year-old stage | adult | Numeric age 78y vs threshold 18y | 64,271 | 1 |
| 62-year-old stage | adult | Numeric age 62y vs threshold 18y | 60,886 | 3 |
| late adult stage | adult | UBERON adult term tier (no numeric age; mapping rule see stage_axis) | 56,087 | 3 |
| 88-year-old stage | adult | Numeric age 88y vs threshold 18y | 55,003 | 1 |
| 84-year-old stage | adult | Numeric age 84y vs threshold 18y | 54,100 | 1 |
| 52-year-old stage | adult | Numeric age 52y vs threshold 18y | 48,328 | 1 |
| 32-year-old stage | adult | Numeric age 32y vs threshold 18y | 45,370 | 1 |
| 25-year-old stage | adult | Numeric age 25y vs threshold 18y | 40,614 | 1 |
| 53-year-old stage | adult | Numeric age 53y vs threshold 18y | 39,355 | 1 |
| 60-year-old stage | adult | Numeric age 60y vs threshold 18y | 38,614 | 2 |
| 83-year-old stage | adult | Numeric age 83y vs threshold 18y | 37,829 | 1 |
| 75-year-old stage | adult | Numeric age 75y vs threshold 18y | 35,801 | 1 |
| 16-year-old stage | developing | Numeric age 16y vs threshold 18y | 35,683 | 2 |
| 63-year-old stage | adult | Numeric age 63y vs threshold 18y | 27,655 | 1 |
| 27-year-old stage | adult | Numeric age 27y vs threshold 18y | 26,380 | 2 |
| 34-year-old stage | adult | Numeric age 34y vs threshold 18y | 25,985 | 2 |
| 80 year-old and over stage | adult | '80 year-old and over' lower bound >= threshold | 23,946 | 1 |
| 46-year-old stage | adult | Numeric age 46y vs threshold 18y | 23,916 | 1 |
| 11-year-old stage | developing | Numeric age 11y vs threshold 18y | 20,466 | 1 |
| 58-year-old stage | adult | Numeric age 58y vs threshold 18y | 20,118 | 2 |
| prime adult stage | adult | UBERON adult term tier (no numeric age; mapping rule see stage_axis) | 16,640 | 2 |
| eighth decade stage | adult | eighth decade = 70-79y lower bound >= threshold | 16,459 | 2 |
| 50-year-old stage | adult | Numeric age 50y vs threshold 18y | 14,949 | 1 |
| 30-year-old stage | adult | Numeric age 30y vs threshold 18y | 13,026 | 1 |
| 17-year-old stage | developing | Numeric age 17y vs threshold 18y | 12,347 | 1 |
| 15-year-old stage | developing | Numeric age 15y vs threshold 18y | 11,892 | 1 |
| 47-year-old stage | adult | Numeric age 47y vs threshold 18y | 11,732 | 1 |
| 10-year-old stage | developing | Numeric age 10y vs threshold 18y | 10,625 | 1 |
| 18-year-old stage | adult | Numeric age 18y vs threshold 18y | 10,613 | 1 |
| 70-year-old stage | adult | Numeric age 70y vs threshold 18y | 9,690 | 1 |
| 3-year-old stage | developing | Numeric age 3y vs threshold 18y | 8,925 | 1 |
| 76-year-old stage | adult | Numeric age 76y vs threshold 18y | 8,685 | 1 |
| 60-79 year-old stage | adult | Age range 60-79 lower bound >= threshold | 8,475 | 1 |
| 74-year-old stage | adult | Numeric age 74y vs threshold 18y | 6,401 | 1 |
| 41-year-old stage | adult | Numeric age 41y vs threshold 18y | 4,827 | 1 |
| 24-year-old stage | adult | Numeric age 24y vs threshold 18y | 3,191 | 1 |

7 donors excluded from the main adult tier: `BCM_23_0131` (developing, 16-year-old stage, 26,671 nuclei); `BCM_22_0769` (developing, 11-year-old stage, 20,466 nuclei); `MMD_23_21999` (developing, 17-year-old stage, 12,347 nuclei); `MMD_23_21623` (developing, 15-year-old stage, 11,892 nuclei); `MMD_23_17738` (developing, 10-year-old stage, 10,625 nuclei); `MMD_23_20181` (developing, 16-year-old stage, 9,012 nuclei); `MMD_23_22486` (developing, 3-year-old stage, 8,925 nuclei)

## Tool compatibility main table (major_classes)
| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |
|---|---|---|---|---|---|---|
| AC | 8.46 | 6.55–10.96 | 3.59–70.83 | 17.99 | TFAP2A, GAD1, GAD2, SLC6A9, ONECUT2 | A |
| Astrocyte | 0.37 | 0.05–0.9 | 0.0–5.38 | 0.44 | GFAP, AQP4, S100B, VIM, SLC1A3 | A |
| BC | 19.99 | 15.21–26.98 | 0.13–49.97 | 21.75 | VSX2, GRM6, CACNA1S, ISL1, OTX2 | A |
| Cone | 3.27 | 2.3–5.21 | 0.0–13.1 | 4.0 | OPN1SW, OPN1MW, ARR3, PDE6H, GNAT2 | A |
| HC | 2.78 | 1.38–4.47 | 0.0–13.25 | 2.54 | ONECUT1, ONECUT3, GAD1, ISL1, CX3CR1 | A |
| MG | 8.75 | 5.28–11.48 | 0.0–24.66 | 6.97 | RLBP1, GLUL, SOX9, VIM, S100B | A |
| Microglia | 0.14 | 0.0–0.22 | 0.0–1.22 | 0.15 | C1QB | A |
| RGC | 3.23 | 0.88–8.7 | 0.0–92.41 | 12.58 | RBPMS, SLC17A6, POU4F1, POU4F2, NEFL | A |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 0.03 | BEST1, RPE65, TTR, LRAT, RDH5, MITF | A |
| Rod | 48.85 | 22.06–57.56 | 0.0–77.97 | 33.55 | RHO, NRL, NR2E3, PDE6B, GNAT1 | A |

## Stratified Details (Stratify by different enrichment/site priors for display; do not merge across layers; KB2c: Each layer table = adult-only, parentheses = number of pooled donors within the layer)
### Layer: Chen_a|NeuN+ ⚠ Sorting design layer (n_donors=20, n_cells=802,830, 25.27% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 25.5 | 20.57–28.15 | 16.38–44.12 | 20 |
| Astrocyte | 0.24 | 0.05–0.42 | 0.0–3.51 | 20 |
| BC | 36.28 | 30.86–42.5 | 3.22–53.15 | 20 |
| Cone | 4.68 | 1.77–5.53 | 0.21–8.37 | 20 |
| HC | 0.28 | 0.03–0.56 | 0.0–0.84 | 20 |
| MG | 6.86 | 4.83–7.89 | 2.56–12.29 | 20 |
| Microglia | 0.15 | 0.05–0.29 | 0.0–0.96 | 20 |
| RGC | 0.17 | 0.11–0.36 | 0.0–1.7 | 20 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.05 | 20 |
| Rod | 27.0 | 19.29–35.81 | 2.54–48.5 | 20 |

### Layer: Chen_a|naive (n_donors=20, n_cells=259,272, 8.16% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 5.02 | 4.38–7.1 | 3.59–13.01 | 20 |
| Astrocyte | 0.2 | 0.0–0.34 | 0.0–1.41 | 20 |
| BC | 15.13 | 13.62–17.32 | 11.57–29.16 | 20 |
| Cone | 2.59 | 1.98–2.99 | 1.26–3.57 | 20 |
| HC | 1.21 | 0.87–1.51 | 0.68–2.91 | 20 |
| MG | 8.78 | 6.12–11.28 | 2.99–17.06 | 20 |
| Microglia | 0.13 | 0.0–0.18 | 0.0–0.98 | 20 |
| RGC | 0.0 | 0.0–0.08 | 0.0–0.15 | 20 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.0 | 20 |
| Rod | 67.63 | 61.12–70.53 | 41.55–77.97 | 20 |

### Layer: Chen_ancestry|NeuN+ ⚠ Sorting design layer (n_donors=27, n_cells=299,171, 9.42% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 19.82 | 13.95–38.23 | 1.42–88.44 | 27 |
| Astrocyte | 0.0 | 0.0–0.03 | 0.0–0.51 | 27 |
| BC | 2.61 | 0.67–4.95 | 0.2–11.92 | 27 |
| Cone | 1.21 | 0.36–3.63 | 0.0–10.14 | 27 |
| HC | 0.54 | 0.07–1.0 | 0.0–3.03 | 27 |
| MG | 0.96 | 0.34–1.57 | 0.0–7.95 | 27 |
| Microglia | 0.0 | 0.0–0.03 | 0.0–1.42 | 27 |
| RGC | 63.59 | 37.65–77.61 | 1.83–92.69 | 27 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.69 | 27 |
| Rod | 3.86 | 1.93–9.59 | 0.21–52.04 | 27 |

### Layer: Chen_ancestry|naive (n_donors=59, n_cells=1,052,958, 33.14% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 8.97 | 6.94–10.89 | 3.68–14.52 | 52 |
| Astrocyte | 0.38 | 0.11–0.96 | 0.0–5.38 | 52 |
| BC | 23.2 | 19.8–32.46 | 14.2–49.97 | 52 |
| Cone | 4.04 | 3.08–6.89 | 1.09–13.1 | 52 |
| HC | 4.26 | 2.89–8.65 | 1.45–13.25 | 52 |
| MG | 9.56 | 6.83–13.59 | 2.63–24.66 | 52 |
| Microglia | 0.18 | 0.07–0.27 | 0.0–1.22 | 52 |
| RGC | 3.34 | 1.5–8.51 | 0.05–14.87 | 52 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.99 | 52 |
| Rod | 47.19 | 12.6–55.85 | 0.0–68.17 | 52 |

### Layer: Chen_b_GSE226108|NeuN+ ⚠ Sorting design layer (n_donors=4, n_cells=69,345, 2.18% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 71.85 | 62.23–78.53 | 46.93–85.01 | 4 |
| Astrocyte | 0.0 | 0.0–0.05 | 0.0–0.19 | 4 |
| BC | 0.86 | 0.49–1.32 | 0.42–1.7 | 4 |
| Cone | 1.17 | 0.57–2.47 | 0.12–5.02 | 4 |
| HC | 0.16 | 0.0–0.32 | 0.0–0.34 | 4 |
| MG | 0.62 | 0.34–1.06 | 0.14–1.73 | 4 |
| Microglia | 0.05 | 0.0–0.12 | 0.0–0.18 | 4 |
| RGC | 7.77 | 4.64–12.31 | 0.28–20.88 | 4 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.01 | 4 |
| Rod | 15.5 | 2.89–30.63 | 1.79–39.29 | 4 |

### Layer: Chen_b_GSE226108|naive  (n_donors=4, n_cells=200,055, 6.3% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 9.22 | 8.41–9.83 | 7.29–10.34 | 4 |
| Astrocyte | 0.46 | 0.36–0.48 | 0.13–0.5 | 4 |
| BC | 28.34 | 26.71–29.88 | 25.83–30.46 | 4 |
| Cone | 4.14 | 3.59–4.92 | 3.0–6.17 | 4 |
| HC | 4.69 | 4.08–5.81 | 3.64–7.76 | 4 |
| MG | 4.91 | 4.52–7.43 | 4.44–13.89 | 4 |
| Microglia | 0.09 | 0.08–0.09 | 0.06–0.1 | 4 |
| RGC | 3.37 | 2.37–3.98 | 0.88–4.33 | 4 |
| RPE | 0.0 | 0.0–0.02 | 0.0–0.09 | 4 |
| Rod | 45.1 | 39.0–48.76 | 26.42–54.02 | 4 |

### Layer: Chen_c_GSE247157|naive  (n_donors=20, n_cells=153,621, 4.83% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 7.32 | 6.72–8.86 | 5.19–13.14 | 20 |
| Astrocyte | 0.95 | 0.64–1.2 | 0.21–2.93 | 20 |
| BC | 20.07 | 17.97–23.82 | 13.5–37.68 | 20 |
| Cone | 4.06 | 3.27–5.56 | 2.63–6.89 | 20 |
| HC | 2.58 | 2.18–3.86 | 0.49–7.33 | 20 |
| MG | 10.35 | 8.15–12.16 | 2.1–24.38 | 20 |
| Microglia | 0.15 | 0.09–0.23 | 0.0–0.99 | 20 |
| RGC | 3.46 | 2.7–5.73 | 0.25–9.67 | 20 |
| RPE | 0.0 | 0.0–0.1 | 0.0–0.35 | 20 |
| Rod | 51.45 | 39.06–55.46 | 6.64–66.68 | 20 |

### Layer: Chen_rgc|NeuN+ ⚠ Sorting design layer  (n_donors=7, n_cells=162,687, 5.12% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 52.69 | 36.34–67.52 | 17.44–84.75 | 7 |
| Astrocyte | 0.02 | 0.0–0.03 | 0.0–0.06 | 7 |
| BC | 0.88 | 0.63–1.01 | 0.45–1.1 | 7 |
| Cone | 1.09 | 0.28–4.11 | 0.08–7.45 | 7 |
| HC | 0.1 | 0.08–0.13 | 0.04–0.21 | 7 |
| MG | 0.16 | 0.12–0.28 | 0.06–0.85 | 7 |
| Microglia | 0.03 | 0.0–0.08 | 0.0–0.2 | 7 |
| RGC | 29.9 | 23.74–59.02 | 0.0–79.69 | 7 |
| RPE | 0.0 | 0.0–0.03 | 0.0–0.22 | 7 |
| Rod | 3.24 | 1.74–6.88 | 0.74–14.5 | 7 |

### Layer: Shekhar_GSE237204|naive  (n_donors=17, n_cells=177,371, 5.58% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| AC | 23.69 | 9.75–49.31 | 4.63–70.83 | 17 |
| Astrocyte | 0.0 | 0.0–0.19 | 0.0–2.18 | 17 |
| BC | 2.0 | 0.55–7.69 | 0.13–21.69 | 17 |
| Cone | 0.2 | 0.0–1.03 | 0.0–4.04 | 17 |
| HC | 0.32 | 0.0–0.89 | 0.0–3.77 | 17 |
| MG | 0.94 | 0.14–2.4 | 0.0–6.44 | 17 |
| Microglia | 0.0 | 0.0–0.15 | 0.0–0.43 | 17 |
| RGC | 37.77 | 18.86–72.36 | 1.54–92.41 | 17 |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 17 |
| Rod | 7.84 | 0.88–34.94 | 0.16–53.07 | 17 |

## Subtype layer (% of annotated cells within class, pooled within class basis)
- **BC** (BC subtype-annotated cells): flat midget bipolar cell 20.9%; invaginating midget 15.4%; rod bipolar cell 14.7%; diffuse bipolar 2 9.9%; DB1 7.3%; DB4 7.1%; DB3b 5.1%; giant bipolar (GB) 3.7%; DB3a 3.2%; DB6 2.7%
- **AC** (AC annotated cells): GABAergic amacrine 63.5%; glycinergic amacrine 23.0%; amacrine (unclassified) 10.0%; starburst amacrine 3.5%
- **RGC** (RGC annotated cells): OFF midget GC 50.2%; ON midget GC 38.0%; retinal ganglion cell (untyped) 7.8%; OFF parasol 2.5%; ON parasol 1.5%
- **HC** (HC annotated cells): H1 85.2%; H2 14.8%
- **Cone** (Cone annotated cells): retinal cone cell 93.3%; S cone 6.7%

## State layer
- **Microglia** [homeostatic]: P2RY12, TMEM119, CX3CR1, IRF8, C1QA/B, TYROBP, AIF1, SALL1, HEXB (Evidence A+B)
- **Müller glia** [homeostatic]: RLBP1, GLUL, SOX9, S100B, VIM, AQP4(low) (Evidence A)
- **RPE** [homeostatic]: BEST1, RPE65, LRAT, RDH5, MITF, TTR (Evidence A)
- **Astrocyte** [homeostatic (perivascular)]: GFAP, AQP4, SLC1A3, S100B (Evidence A)

## Flag semantics
**expected_low_but_present**: Microglia (0.05~0.8%); RPE (≈0, >1% if mixed in); Astrocyte (0.1~1.5%)

**unexpected**: progenitor/PCNA+ large cluster (adult retina); abundant mast cells/eosinophils

**contamination_suspect**: High MT photoreceptor debris zone (dissociation stress, see disease entries); large peripheral blood myeloid cluster (FCN1/LYZ) — residual blood flag for whole-retina specimens

## Notes
1. Single-sample proportions are strongly influenced by sampling/sorting design (NeuN± nuclear sorting, RGC enrichment, fovea vs periphery, lobe vs macular): Cross-study spread (basis for Grade C interval derivation) = min~max of pooled data from 6 groups: Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy, excluding RGC-targeted groups.
2. The HRCA 10-class lexical surface does not include endothelial/pericytes (neural retina integration excludes vascular classes). True whole retina contains low proportions of vascular components; small Endo/Pericyte clusters in annotated data represent normal vasculature and do not trigger a contamination flag (contrast with disease entries).
3. RGC-enriched samples (e.g., Chen_rgc 46.2% RGC, Shekhar legacy 43.6%) have high proportions due to design intent — dataset construction strategy must be checked before adjudicating 'anomaly'.
4. Developmental/organoid specimens are not applicable to this baseline (progenitor and subtype proportions differ completely; anchor DEV_DUAL/RETINA_ORGANOIDS).
5. PI reminder: Self-annotation of public data may itself be inaccurate — all proportions in this entry are 'priors with evidence grades'; when conflicting with data, raise flags rather than forcing alignment.
6. v1.1 (this entry): Proportion metrics upgraded from 'all-cells pooled + cross-study spread' to 'donor-level stratified distribution' (Astra T2); old pooled values retained in pooled_all_cells for reference only — among 3.17M nuclei, Chen_ancestry accounts for 42.6%, with pooled large donors dominating weight.
7. NeuN+ sorting layers systematically elevate neuronal classes/decrease MG·Astro·RPE; intervals from two layers must not be mixed before confirming whether control samples underwent nuclear sorting.
8. suspension_type is all-nuclei — snRNA intronic reads are counted (intronic_reads_counted=yes), making class proportions directly incomparable with scRNA cell suspension data (Astra T2: differences between scRNA and snRNA are sufficient to alter observed composition).
9. v1.1 (KB2c t_be336eee): Primary archive metric upgraded to adult-only (donor_age>=18y, adjudication Q2) — v1.0 mixed metrics (previously included developmental donors aged 3-17; measured fetal period had 0 nuclei) fully preserved in donor_level_adult_pool_contrast (tier_id=...__adult_pool__v1.0); citing v1.0 numbers must attach the contrast archive identity; signatures of the two archives must not be mixed (red line).

## Source List
| sid | Type | Label |
|---|---|---|
| `HRCA317M` | dataset | HRCA CELLxGENE merged version 3,177,310 cells (10 majorclass, all normal, 6 studies/104 donors, fovea~periphery) (PMID 41578023) |
| `HRCA_PAPER` | paper | Li et al., Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nat Genet 2026 (full version ~3.9M cells, 123 RNA classes) (PMID 41578023) |
| `FOVEA_PERIPH` | paper | Cell Atlas of the Human Fovea and Peripheral Retina (2020) — shared types between central fovea/periphery but regional differences in proportions and expression (PMID 32555229) |
| `AGING_ATLAS` | paper | A single-cell transcriptome atlas of the aging human and macaque retina (2021) (PMID 34691611) |
| `MULTIOMICS_ATLAS` | paper | A multi-omics atlas of the human retina at single-cell resolution (2023) (PMID 37388908) |
| `RETINA_ORGANOIDS` | paper | Cell Types of the Human Retina and Its Organoids at Single-Cell Resolution (2020) (PMID 32946783) |
| `DEV_DUAL` | paper | Single cell dual-omic atlas of the human developing retina (2024) — developmental stage includes progenitors, adult baseline not applicable (PMID 39117640) |
| `RETLIB41` | kb | Local marker library markers_v4.1_clean.json v4.1-clean-P0.4  |
| `D001_DONOR_LEVEL` | dataset | Donor-level distribution in this entry recalculated from /mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad obs by build_baselines.py (KB1v2 t_16c3e020; KB2c developmental axis separate t_be336eee) (PMID 41578023) |

