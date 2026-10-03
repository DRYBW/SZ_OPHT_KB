# Composition baseline: Human(normal) ciliary_body snRNA adult-only main record (ciliary_body slice 863,922 nuclei / 59 donors, donor-level conditional reference distribution, KB2c development axis listed separately)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_ciliary_body` | Status: filled_donor_level | Development axis: **organism_stage=adult** | Generated: 2026-09-23 | Card: t_bad1fbab
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
- Two-tier identity: {'adult_only': 'baseline_human_ciliary_body__adult_only__kb2c', 'adult_pool': 'baseline_human_ciliary_body__adult_pool__v1.0'}

## Astra T2 metadata fields
- **Sampling Material**: ciliary_body anatomical component from human anterior segment surgical specimens (tissue column='ciliary body' slice; additionally, 53,406 nuclei from the uvea fraction are not included in this entry)
- **Disease Stage**: normal (disease column all normal; donor systemic death eye bank/surgical material)
- **Treatment Context**: Not recorded (no treatment column in metadata) — marked 'Not recorded', no speculation
- **scRNA_vs_snRNA**: snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes)
- **Enrichment Steps**: No sorting records (whole-tissue nuclear suspension loaded directly onto instrument)
- **Dissociation Method**: mechanical dissociation,detergent solubilization×824,681 nuclei; mechanical dissociation,centrifugation×29,948 nuclei; mechanical dissociation,enzymatic dissociation×9,293 nuclei (sample_collection_method=surgical resection)
- **Number of Donors**: Main archive adult-only 55 donors / 55 donor units; Control archive adult_pool 59 donors / 59 units (including 4 non-adult donors → see excluded_nonadult_units row by row)
- **Count Denominator**: 863,922 nuclei (majorclass fully annotated within the ciliary_body slice)
- **Evidence Source**: Local empirical recalculation (A) + portal/HASA official annotation (t_6f5cc731 judged as 'portal official')

## Primary Reference: Donor-level conditional reference distribution (excluding sorting design layer)
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 17.9 | 15.08–21.31 | 5.94–41.57 | 55 |
| CB_PCE | 28.51 | 23.96–33.84 | 2.68–56.55 | 55 |
| Ciliary_Muscle | 16.25 | 12.18–19.03 | 3.9–32.03 | 55 |
| Endothelium | 2.08 | 1.63–2.55 | 0.0–4.36 | 55 |
| Fibroblast | 14.45 | 11.2–16.83 | 2.59–25.78 | 55 |
| Immune Cell | 4.72 | 3.35–6.61 | 1.18–18.99 | 55 |
| Melanocyte | 5.96 | 4.98–7.4 | 0.0–10.43 | 55 |
| Pericyte | 0.67 | 0.52–0.74 | 0.0–1.07 | 55 |
| Schwann Cell | 7.44 | 6.18–8.51 | 0.18–12.97 | 55 |

### Control Archive adult_pool (v1.0 mixed criteria, including non-adult donors; tier=`baseline_human_ciliary_body__adult_pool__v1.0`) —— Citing v1.0 legacy figures must be associated with this archive identity

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 17.87 | 14.83–21.31 | 2.51–41.57 | 59 |
| CB_PCE | 28.51 | 23.89–34.67 | 2.47–57.12 | 59 |
| Ciliary_Muscle | 16.25 | 11.79–19.41 | 3.9–32.03 | 59 |
| Endothelium | 2.2 | 1.66–2.61 | 0.0–9.65 | 59 |
| Fibroblast | 14.45 | 10.31–16.83 | 2.59–32.46 | 59 |
| Immune Cell | 4.72 | 3.35–6.34 | 1.18–18.99 | 59 |
| Melanocyte | 5.96 | 4.88–7.67 | 0.0–15.38 | 59 |
| Pericyte | 0.65 | 0.52–0.74 | 0.0–1.65 | 59 |
| Schwann Cell | 7.44 | 6.08–8.51 | 0.18–12.97 | 59 |

### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)
| UBERON development_stage | organism_stage | Grading Rule | Nuclei/Cell Count | Number of Donors |
|---|---|---|---|---|
| 62-year-old stage | adult | Numerical age 62y vs threshold 18y | 64,491 | 3 |
| 71-year-old stage | adult | Numerical age 71y vs threshold 18y | 58,911 | 4 |
| 69-year-old stage | adult | Numerical age 69y vs threshold 18y | 52,817 | 3 |
| 64-year-old stage | adult | Numerical age 64y vs threshold 18y | 49,788 | 2 |
| 46-year-old stage | adult | Numerical age 46y vs threshold 18y | 38,633 | 1 |
| 72-year-old stage | adult | Numerical age 72y vs threshold 18y | 38,322 | 4 |
| 53-year-old stage | adult | Numerical age 53y vs threshold 18y | 37,753 | 2 |
| 58-year-old stage | adult | Numerical age 58y vs threshold 18y | 34,884 | 2 |
| 67-year-old stage | adult | Numerical age 67y vs threshold 18y | 33,062 | 2 |
| 16-year-old stage | developing | Numerical age 16y vs threshold 18y | 32,061 | 2 |
| 70-year-old stage | adult | Numerical age 70y vs threshold 18y | 30,580 | 1 |
| 77-year-old stage | adult | Numerical age 77y vs threshold 18y | 26,976 | 2 |
| 65-year-old stage | adult | Numerical age 65y vs threshold 18y | 26,593 | 2 |
| 60-year-old stage | adult | Numerical age 60y vs threshold 18y | 23,870 | 2 |
| 18-year-old stage | adult | Numerical age 18y vs threshold 18y | 23,862 | 1 |
| 68-year-old stage | adult | Numerical age 68y vs threshold 18y | 23,269 | 3 |
| 56-year-old stage | adult | Numerical age 56y vs threshold 18y | 20,318 | 1 |
| 17-year-old stage | developing | Numerical age 17y vs threshold 18y | 17,548 | 1 |
| 81-year-old stage | adult | Numerical age 81y vs threshold 18y | 16,132 | 1 |
| 44-year-old stage | adult | Numerical age 44y vs threshold 18y | 15,736 | 1 |
| 73-year-old stage | adult | Numerical age 73y vs threshold 18y | 15,563 | 1 |
| 80 year-old and over stage | adult | Lower bound of '80 year-old and over' >= threshold | 15,231 | 1 |
| 34-year-old stage | adult | Numerical age 34y vs threshold 18y | 14,892 | 1 |
| 57-year-old stage | adult | Numerical age 57y vs threshold 18y | 13,965 | 1 |
| 51-year-old stage | adult | Numerical age 51y vs threshold 18y | 13,488 | 1 |
| 82-year-old stage | adult | Numerical age 82y vs threshold 18y | 13,017 | 1 |
| 85-year-old stage | adult | Numerical age 85y vs threshold 18y | 12,424 | 1 |
| 20-year-old stage | adult | Numerical age 20y vs threshold 18y | 11,952 | 1 |
| 15-year-old stage | developing | Numerical age 15y vs threshold 18y | 11,508 | 1 |
| 78-year-old stage | adult | Numeric age 78y vs threshold 18y | 9,693 | 1 |
| 27-year-old stage | adult | Numeric age 27y vs threshold 18y | 9,293 | 1 |
| 63-year-old stage | adult | Numeric age 63y vs threshold 18y | 9,100 | 1 |
| 47-year-old stage | adult | Numeric age 47y vs threshold 18y | 8,313 | 1 |
| 43-year-old stage | adult | Numeric age 43y vs threshold 18y | 8,196 | 1 |
| 52-year-old stage | adult | Numeric age 52y vs threshold 18y | 7,149 | 1 |
| 66-year-old stage | adult | Numeric age 66y vs threshold 18y | 7,089 | 1 |
| 21-year-old stage | adult | Numeric age 21y vs threshold 18y | 6,493 | 1 |
| 50-year-old stage | adult | Numeric age 50y vs threshold 18y | 6,097 | 1 |
| 30-year-old stage | adult | Numeric age 30y vs threshold 18y | 4,853 | 1 |

4 donors excluded from the adult main archive: `BCM_23_0491` (developing, 16-year-old stage, 19,530 nuclei); `MMD_23_21999` (developing, 17-year-old stage, 17,548 nuclei); `MMD_23_20181` (developing, 16-year-old stage, 12,531 nuclei); `MMD_23_21623` (developing, 15-year-old stage, 11,508 nuclei)

## Tool compatibility main table (major_classes)
| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |
|---|---|---|---|---|---|---|
| CB_NPCE | 17.9 | 15.08–21.31 | 5.94–41.57 | 18.52 |  | A |
| CB_PCE | 28.51 | 23.96–33.84 | 2.68–56.55 | 29.67 |  | A |
| Ciliary_Muscle | 16.25 | 12.18–19.03 | 3.9–32.03 | 15.86 |  | A |
| Endothelium | 2.08 | 1.63–2.55 | 0.0–4.36 | 2.34 |  | A |
| Fibroblast | 14.45 | 11.2–16.83 | 2.59–25.78 | 14.21 |  | A |
| Immune Cell | 4.72 | 3.35–6.61 | 1.18–18.99 | 5.28 |  | A |
| Melanocyte | 5.96 | 4.98–7.4 | 0.0–10.43 | 6.25 |  | A |
| Pericyte | 0.67 | 0.52–0.74 | 0.0–1.07 | 0.65 |  | A |
| Schwann Cell | 7.44 | 6.18–8.51 | 0.18–12.97 | 7.22 |  | A |

## Stratified Details (Stratify by different enrichment/site priors for display; do not merge across layers; KB2c: Each layer table = adult-only, parentheses = number of pooled donors within the layer)
### Layer: chen_tm_cb|ciliary_body (n_donors=55, n_cells=833,974, accounting for 96.53% of the atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 17.94 | 15.39–21.65 | 5.94–41.57 | 51 |
| CB_PCE | 27.85 | 23.96–33.03 | 8.99–48.12 | 51 |
| Ciliary_Muscle | 16.25 | 12.76–19.03 | 3.9–32.03 | 51 |
| Endothelium | 2.2 | 1.7–2.56 | 0.0–4.36 | 51 |
| Fibroblast | 14.45 | 11.56–16.7 | 2.59–25.78 | 51 |
| Immune Cell | 4.69 | 3.35–6.3 | 1.18–18.99 | 51 |
| Melanocyte | 6.0 | 5.08–7.67 | 0.0–10.43 | 51 |
| Pericyte | 0.67 | 0.54–0.74 | 0.0–1.04 | 51 |
| Schwann Cell | 7.44 | 6.18–8.48 | 0.18–12.97 | 51 |

### Layer: sanes_GSE199013|ciliary_body (n_donors=4, n_cells=29,948, accounting for 3.47% of the atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 16.08 | 14.15–18.7 | 13.81–21.1 | 4 |
| CB_PCE | 38.96 | 22.9–50.35 | 2.68–56.55 | 4 |
| Ciliary_Muscle | 14.13 | 8.68–21.01 | 4.82–29.18 | 4 |
| Endothelium | 0.45 | 0.22–0.76 | 0.0–1.24 | 4 |
| Fibroblast | 13.14 | 8.59–17.17 | 6.39–17.84 | 4 |
| Immune Cell | 6.83 | 4.46–10.33 | 3.02–15.17 | 4 |
| Melanocyte | 3.77 | 3.38–4.62 | 3.19–6.15 | 4 |
| Pericyte | 0.33 | 0.19–0.57 | 0.0–1.07 | 4 |
| Schwann Cell | 7.73 | 6.44–8.89 | 4.98–9.97 | 4 |

## Subtype layer (% of annotated cells within class, pooled within class basis)

## Flag semantics
**expected_low_but_present**: Pericyte <1% (Endothelium also only ~2%: predominantly large vessels, low nuclear capture efficiency for capillaries)

**unexpected**: Immune Cell ~5% (predominantly macrophages) is at normal levels for innate immunity, serving as an inflammatory control baseline

**contamination_suspect**: No additional contamination flag required (section boundary corresponds to this tissue)

## Notes
1. This entry = ciliary body anatomical component section: PCE/NPCE/ciliary muscle are the three main classes constituting the tissue proper; Melanocyte/Schwann Cell proportions reflect the capture composition of uveal pigmentation + neural innervation layers — note for disease controls (Astra T2).
2. Fibroblast in this section = CB fibroblasts (CBFibro), distinct sublayers from TM/corneal fibroblasts (distinguishable via author_cell_type).
3. Supported by 59 donors; however, there is a significant scale disparity between the two study layers (chen_tm_cb dominant vs sanes uvea fraction outside this section), stratified details must be reviewed.
4. snRNA scope (single-nucleus suspension, intronic reads included), cannot be directly compared with scRNA entries.
5. v1.1 (KB2c t_be336eee): Main archive = adult-only (>=18y, adjudication Q2) — this section empirically excludes 4 non-adult donor units (adolescent stages, see excluded_nonadult_units line-by-line); v1.0 mixed-scope retained in donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), signatures separated into two tiers.

## Source List
| sid | Type | Label |
|---|---|---|
| `CILIARY_BODY_LOCAL` | dataset | Local file /mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad |
| `CILIARY_BODY_HASA` | dataset | HASA/anterior segment snRNA collection (t_6f5cc731 inventory mapping OA-D004/OA-D016; this section = the ciliary_body component of its chen_tm_cb+sanes integration) |

