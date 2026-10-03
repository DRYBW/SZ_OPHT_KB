# Composition baseline: Human(normal) trabecular_meshwork snRNA adult-only main archive (trabecular_meshwork slice 184,922 nuclei / 25 donors, donor-level conditional reference distribution, KB2c developmental axis listed separately)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_trabecular_meshwork` | status: filled_donor_level | developmental axis: **organism_stage=adult** | generated: 2026-09-23 | card: t_bad1fbab
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
- Two-tier identity: {'adult_only': 'baseline_human_trabecular_meshwork__adult_only__kb2c', 'adult_pool': 'baseline_human_trabecular_meshwork__adult_pool__v1.0'}

## Astra T2 metadata fields
- **Sampling material**: Trabecular_meshwork anatomical component from human anterior segment surgical resection (tissue column='eye trabecular meshwork' slice; uvea component 53,406 nuclei not included in this entry)
- **Disease Stage**: normal (disease column all normal; donor systemic death eye bank/surgical material)
- **Treatment Context**: Not recorded (no treatment column in metadata) — marked 'Not recorded', no speculation
- **scRNA_vs_snRNA**: snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes)
- **Enrichment Steps**: No sorting records (whole-tissue nuclear suspension loaded directly onto instrument)
- **Dissociation method**: mechanical dissociation,detergent solubilization×157,161 nuclei; mechanical dissociation,centrifugation×27,761 nuclei (sample_collection_method=surgical resection)
- **Donor count**: Main archive adult-only 25 donors / 25 donor units; Control archive adult_pool 25 donors / 25 units (includes 0 non-adult donors → see excluded_nonadult_units row by row)
- **Count denominator**: 184,922 nuclei (all annotated majorclass within trabecular_meshwork slice)
- **Evidence Source**: Local empirical recalculation (A) + portal/HASA official annotation (t_6f5cc731 judged as 'portal official')

## Primary Reference: Donor-level conditional reference distribution (excluding sorting design layer)
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 25 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 25 |
| Ciliary_Muscle | 34.22 | 30.18–43.43 | 17.61–59.17 | 25 |
| Endothelium | 2.35 | 1.47–3.2 | 0.78–10.68 | 25 |
| Fibroblast | 37.37 | 31.05–42.69 | 20.83–65.3 | 25 |
| Immune Cell | 4.58 | 3.44–6.58 | 0.67–18.82 | 25 |
| Melanocyte | 5.31 | 3.46–7.21 | 0.63–11.45 | 25 |
| Pericyte | 0.33 | 0.27–0.42 | 0.0–0.88 | 25 |
| Schwann Cell | 11.58 | 7.72–13.6 | 3.73–22.85 | 25 |

### Control archive adult_pool (v1.0 mixed scope, includes non-adult donors; tier=`baseline_human_trabecular_meshwork__adult_pool__v1.0`) —— citing v1.0 old numbers can only attach to this archive identity

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 25 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 25 |
| Ciliary_Muscle | 34.22 | 30.18–43.43 | 17.61–59.17 | 25 |
| Endothelium | 2.35 | 1.47–3.2 | 0.78–10.68 | 25 |
| Fibroblast | 37.37 | 31.05–42.69 | 20.83–65.3 | 25 |
| Immune Cell | 4.58 | 3.44–6.58 | 0.67–18.82 | 25 |
| Melanocyte | 5.31 | 3.46–7.21 | 0.63–11.45 | 25 |
| Pericyte | 0.33 | 0.27–0.42 | 0.0–0.88 | 25 |
| Schwann Cell | 11.58 | 7.72–13.6 | 3.73–22.85 | 25 |

### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)
| UBERON development_stage | organism_stage | Grading Rule | Nuclei/Cell Count | Number of Donors |
|---|---|---|---|---|
| 53-year-old stage | adult | Numeric age 53y vs threshold 18y | 22,052 | 2 |
| 68-year-old stage | adult | Numeric age 68y vs threshold 18y | 20,418 | 2 |
| 80 year-old and over stage | adult | '80 year-old and over' lower bound>=threshold | 16,802 | 2 |
| 69-year-old stage | adult | Numeric age 69y vs threshold 18y | 16,533 | 2 |
| 66-year-old stage | adult | Numeric age 66y vs threshold 18y | 12,159 | 1 |
| 20-year-old stage | adult | Numeric age 20y vs threshold 18y | 10,682 | 1 |
| 72-year-old stage | adult | Numeric age 72y vs threshold 18y | 8,741 | 1 |
| 56-year-old stage | adult | Numeric age 56y vs threshold 18y | 8,567 | 1 |
| 58-year-old stage | adult | Numeric age 58y vs threshold 18y | 8,501 | 1 |
| 76-year-old stage | adult | Numeric age 76y vs threshold 18y | 8,015 | 1 |
| 57-year-old stage | adult | Numeric age 57y vs threshold 18y | 7,975 | 1 |
| 47-year-old stage | adult | Numeric age 47y vs threshold 18y | 6,492 | 1 |
| 24-year-old stage | adult | Numeric age 24y vs threshold 18y | 6,284 | 1 |
| 50-year-old stage | adult | Numeric age 50y vs threshold 18y | 5,526 | 1 |
| 65-year-old stage | adult | Numeric age 65y vs threshold 18y | 5,270 | 1 |
| 64-year-old stage | adult | Numeric age 64y vs threshold 18y | 4,313 | 1 |
| 51-year-old stage | adult | Numeric age 51y vs threshold 18y | 3,889 | 1 |
| 30-year-old stage | adult | Numeric age 30y vs threshold 18y | 3,840 | 1 |
| 34-year-old stage | adult | Numeric age 34y vs threshold 18y | 3,510 | 1 |
| 61-year-old stage | adult | Numeric age 61y vs threshold 18y | 2,994 | 1 |
| 44-year-old stage | adult | Numeric age 44y vs threshold 18y | 2,359 | 1 |

## Tool compatibility main table (major_classes)
| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |
|---|---|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 0.18 |  | A |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 0.31 |  | A |
| Ciliary_Muscle | 34.22 | 30.18–43.43 | 17.61–59.17 | 36.93 |  | A |
| Endothelium | 2.35 | 1.47–3.2 | 0.78–10.68 | 2.47 |  | A |
| Fibroblast | 37.37 | 31.05–42.69 | 20.83–65.3 | 36.38 |  | A |
| Immune Cell | 4.58 | 3.44–6.58 | 0.67–18.82 | 5.28 |  | A |
| Melanocyte | 5.31 | 3.46–7.21 | 0.63–11.45 | 5.94 |  | A |
| Pericyte | 0.33 | 0.27–0.42 | 0.0–0.88 | 0.39 |  | A |
| Schwann Cell | 11.58 | 7.72–13.6 | 3.73–22.85 | 12.11 |  | A |

## Stratified Details (Stratify by different enrichment/site priors for display; do not merge across layers; KB2c: Each layer table = adult-only, parentheses = number of pooled donors within the layer)
### Layer: chen_tm_cb|trabecular_meshwork (n_donors=21, n_cells=157,161, 84.99% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 21 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 21 |
| Ciliary_Muscle | 33.09 | 30.06–37.84 | 17.61–59.17 | 21 |
| Endothelium | 2.35 | 2.04–3.2 | 0.78–9.43 | 21 |
| Fibroblast | 38.04 | 32.24–43.24 | 20.83–65.3 | 21 |
| Immune Cell | 4.58 | 3.3–6.37 | 0.67–18.82 | 21 |
| Melanocyte | 6.18 | 3.71–7.45 | 0.63–11.45 | 21 |
| Pericyte | 0.31 | 0.26–0.36 | 0.0–0.77 | 21 |
| Schwann Cell | 11.46 | 7.72–13.01 | 3.73–17.67 | 21 |

### Layer: sanes_GSE199013|trabecular_meshwork (n_donors=4, n_cells=27,761, 15.01% of atlas)

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–0.0 | 4 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–0.0 | 4 |
| Ciliary_Muscle | 43.88 | 42.97–45.02 | 41.56–47.12 | 4 |
| Endothelium | 1.95 | 1.35–4.52 | 1.09–10.68 | 4 |
| Fibroblast | 29.95 | 27.47–31.1 | 22.05–32.53 | 4 |
| Immune Cell | 5.57 | 4.31–6.75 | 3.56–7.23 | 4 |
| Melanocyte | 3.65 | 2.48–4.62 | 1.22–5.28 | 4 |
| Pericyte | 0.72 | 0.67–0.78 | 0.55–0.88 | 4 |
| Schwann Cell | 12.91 | 10.22–16.38 | 6.15–22.85 | 4 |

## Subtype layer (% of annotated cells within class, pooled within class basis)

## Flag semantics
**expected_low_but_present**: Schwann Cell ~12% (innervated tissue); Pericyte ~0.4%

**unexpected**: Melanocyte ~6% (incidental uveal pigmented tissue, related to dissection plane)

**contamination_suspect**: CB_PCE/CB_NPCE ~0.5% (dissection boundary overrun into ciliary body)

## Notes
1. This entry = trabecular meshwork anatomical component dissection slice: High Ciliary_Muscle proportion results from integrated sampling of adjacent scleral spur/trabecular muscle; this reflects capture composition rather than ground truth for the TM cell layer; author-level TM-specific subtypes (BeamA/BeamB/JCT, author_cell_type) are found in fine_types.
2. The primary Fibroblast class in this slice = TM fibroblasts/beam cells (TMFibro) — do not directly compare with corneal/scleral fibroblasts.
3. Minor CB_PCE/CB_NPCE (total ~0.5%) = ciliary body dissection boundary contamination.
4. Donor count is 25 but donor scale within units is uneven; n=25 donor-level interval remains moderate support; direction must be re-reviewed after disease control usage.
5. snRNA scope, cannot be directly compared with scRNA entries (Astra T2); uvea component (53,406 nuclei) and sclera/uvea entries are discussed separately.
6. v1.1 (KB2c t_be336eee): Primary archive = adult-only (>=18y, adjudication Q2) — measured exclusion of 0 items in this slice (all donors >=18y → values for both tiers are legally identical, only identity signatures separated); v1.0 mixed scope retained in donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), two-tier signature separation.

## Source List
| sid | Type | Label |
|---|---|---|
| `TRABECULAR_MESHWORK_LOCAL` | dataset | Local file /mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad |
| `TRABECULAR_MESHWORK_HASA` | dataset | HASA/anterior segment snRNA collection (t_6f5cc731 inventory mapping OA-D004/OA-D016; this slice = trabecular_meshwork component of its chen_tm_cb+sanes integration) |

