# Composition baseline: Human (normal) freshly dissociated RPE suspension scRNA — developmental stage=unknown tier (OA GSE158629, donor-level 4 donors, cluster identity inferred by markers, KB2c disclosure)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_RPE` | status: filled_donor_level | developmental axis: **organism_stage=unknown** | generated: 2026-09-23 | card: t_bad1fbab
> **KB3 developmental tier (card t_5425a7ca)**: development_stage=**unknown** | applicable tier (hardcoded upon backfill): unknown —— KB3 prohibition (PI red line 2026-09-23): developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.
> This file is automatically rendered from the corresponding .json by `/mnt/D/EyeKB/scripts/baselines/build_baselines.py` — modify content in JSON+script; manual MD edits will be overwritten.
> ⚠ Developmental axis disclosure: local GSE158629 cells_meta (exported by export_rpe_meta.R) contains only donor/cluster/tech columns, no development_stage/age column; GEO Summary states 'four adult human donor eyes' (Evidence Grade B).

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
- Two-tier identity: {'unknown_descriptive': 'baseline_human_RPE__stage_unknown__kb2c'}

## Astra T2 metadata fields
- **Sampling material**: Human freshly dissociated RPE monolayer cells (4 adult donor eyes, stage=Fresh; GEO: 'RPE cells were isolated from four adult human donor eyes')
- **Disease stage**: normal (healthy donors; processed metadata has no disease column)
- **Treatment context**: Not recorded (processed metadata has no treatment column) — mark 'Not recorded', do not speculate
- **scRNA_vs_snRNA**: scRNA-seq whole cells (donor1=10x 3'; donor2-4=ICELL8 droplet cloning) — different scope from snRNA entries (retina/optic_nerve), not directly comparable
- **Enrichment step**: Mechanical+enzymatic isolation enrichment of RPE layer (tissue level); no fluorescence sorting records — the isolation process itself constitutes 'enrichment'
- **Dissociation method**: RPE isolation from fresh excised eyes (GEO Methods; processed metadata has no dissociation reagent column, details not recorded)
- **Donor count**: 4 (donor1=10x, donor2-4=ICELL8 — platform fully bundled with donor, tech stratification=descriptive) — KB2c: cells_meta has no age column, this entry organism_stage=unknown (GEO text stating 'four adult human donor eyes' is B-grade literature description, not row-verifiable, silent assignment to adult prohibited)
- **Count denominator**: 10,917 cells (4 donor objects, 26 clusters, all annotated)
- **Evidence sources**: Local empirical recalculation (A: proportions; RData→CSV export script export_rpe_meta.R) + GEO record author cluster descriptions (B: rod/cone/TF+SPP1/stem cell candidates) + project marker inference (C)

## Main reference: Donor-level conditional reference distribution (n=4 donors; marker-inferred canonical classes)
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.

| Cell class | Donor median % | Donor IQR % | Donor range % | n donors |
|---|---|---|---|---|
| RPE | 60.25 | 48.25–75.33 | 47.06–85.79 | 4 |
| PR-associated | 22.4 | 16.43–30.18 | 9.27–42.78 | 4 |
| neuron-like | 0.0 | 0.0–0.54 | 0.0–2.17 | 4 |
| erythroid | 6.56 | 2.21–15.75 | 0.0–32.54 | 4 |
| myeloid | 0.0 | 0.0–0.5 | 0.0–1.99 | 4 |

### Developmental stage line-by-line disclosure (KB2c Red Line 2: exclusions/unknowns explicitly listed)
| Source | organism_stage | Rule | Cell count | Donor count | Literature-level description (B) |
|---|---|---|---|---|---|
| GSE158629 cells_meta (all 4 donors) | unknown | No age column → silent assignment to adult prohibited (Red Line 2) | 10,917 | 4 | GEO: 'RPE cells were isolated from four adult human donor eyes' |

## Tool compatibility main table (major_classes)
| Class | Median % across donors | IQR% | range% | pooled% (control only) | Local library marker | Evidence |
|---|---|---|---|---|---|---|
| RPE | 60.25 | 48.25–75.33 | 47.06–85.79 | 67.98 |  | A |
| PR-associated | 22.4 | 16.43–30.18 | 9.27–42.78 | 24.92 |  | A |
| neuron-like | 0.0 | 0.0–0.54 | 0.0–2.17 | 1.36 |  | A |
| erythroid | 6.56 | 2.21–15.75 | 0.0–32.54 | 5.48 |  | A |
| myeloid | 0.0 | 0.0–0.5 | 0.0–1.99 | 0.27 |  | A |

## Subtype layer (% of annotated cells within class, pooled within class basis)

## State layer
- **donor1 cl0** [RPE: pigment-high (TYRP1+/BEST1+/RPE65+)]: m, a, r, k, e, r, :,  , R, P, E, 6, 5, #, 3,  , T, Y, R, P, 1, #, 1, 1,  , B, E, S, T, 1, #, 1, 2,  , T, I, M, P, 3, #, 1,  , (, A, ) (Evidence A+B/C)
- **donor1 cl1** [RPE: canonical (RBP1/RLBP1)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor1 cl2** [PR-associated: rod-program (SAG/PDE6A/RHO)]: Author described rod RNA cluster RHO/PDE6A (B), + marker (A) (Evidence A+B/C)
- **donor1 cl3** [RPE: TF+SPP1/VEGF state (VIM+/TF+/SPP1+/MT1X+)]: Author described VEGF signaling cluster TF/SPP1 (B), + marker (A) (Evidence A+B/C)
- **donor1 cl4** [PR-associated: rod-pure (RHO/RBP3/IMPG1/CNGA1)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor1 cl5** [PR-associated: rod/cone-mixed (SAG/GNAT1/PDE6G)]: m, a, r, k, e, r,  , (, A, ), ;,  , Author cone cluster ARR3/PDE6H not in this cluster top25, attribution uncertain (C) (Evidence A+B/C)
- **donor1 cl6** [neuron-like: VSX1+/SNAP25+ (bipolar/cone-like)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor1 cl7** [neuron-like: ISL1+/SNAP25+ (amacrine-like)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor2 cl0** [RPE: canonical]: m, a, r, k, e, r, :,  , R, P, E, 6, 5, #, 7,  , T, T, R,  , (, A, ) (Evidence A+B/C)
- **donor2 cl1** [RPE: mito-high]: m, a, r, k, e, r, :,  , MT-* dominant + RPE65/BEST1 (A) (Evidence A+B/C)
- **donor2 cl2** [PR-associated: rod/cone-transcripts]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor2 cl3** [RPE: canonical (NDUFS7+)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor2 cl4** [RPE: pigment (TYRP1+/BEST1+)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor2 cl5** [erythroid: HBG1/HBG2+ribosomal]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor2 cl6** [RPE: complement-high (C4A/C4B+/PMEL+/TRPM3+)]: RPE lineage (TRPM3/PMEL) + complement state (A) (Evidence A+B/C)
- **donor2 cl7** [myeloid: CD74/AIF1/HLA-DR/CCL3]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor3 cl0** [RPE: canonical]: m, a, r, k, e, r, :,  , R, P, E, 6, 5, #, 2,  , (, A, ) (Evidence A+B/C)
- **donor3 cl1** [erythroid: HBG+ribosomal]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor3 cl2** [PR-associated: rod-transcripts (RHO/RCVRN/ABCA4)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor3 cl3** [RPE: pigment-high (TYRP1+/BEST1+)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor3 cl4** [erythroid: HBG+ribosomal]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor4 cl0** [PR-associated: rod-program (SAG/RHO/PDE6A)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor4 cl1** [RPE: mito-high]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor4 cl2** [erythroid: HBG+ribosomal]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)
- **donor4 cl3** [RPE: TF/GPX3 stress state (TF#2/TRPM3+)]: Overlaps with donor1 TF+SPP1 cluster marker (C) (Evidence A+B/C)
- **donor4 cl4** [RPE: canonical (HSP-high)]: m, a, r, k, e, r,  , (, A, ) (Evidence A+B/C)

## Flag semantics
**expected_low_but_present**: Myeloid (CD74/AIF1/HLA-DR) detected only in donor2; erythroid detected only in ICELL8 donors; stem cell candidate population (RPE65+/VIM/GNL3/MKI67, author description B): did not emerge in any cluster top25 — small population unquantified, interval cannot be estimated (legitimate state, Astra T2)

**unexpected**: PR-associated class 3.8–28.5%: Authors describe as RPE subpopulation (cone/rod transcript clusters, B), could also be phagocytosed PR outer segment mRNA or disk membrane attachment contamination — dual interpretation retained, no single conclusion drawn; neuron-like class (VSX1/ISL1/SNAP25) detected only in donor1 (10x) at 2.2% — retinal neural contamination or low-abundance precursors, uncertain

**contamination_suspect**: Erythroid (HBG1/HBG2) up to 32.54% within donor — blood residue

## Notes
1. Identity annotations are not official author names: processed files contain only donor×cluster IDs; canonical class labels are inferred by project markers (Evidence C). Only rod/cone/TF+SPP1/stem cell candidate classes have GEO author description anchors (Evidence B). External citations must include this caveat.
2. n=4 donors, donor-level median/IQR is extremely coarse (each donor weight 25%); intervals serve only as descriptive reference for 'freshly dissociated RPE capture composition'.
3. Each donor object is clustered independently without global integration; cross-donor merging of similar clusters relies on marker consistency (RPE/PR/erythroid are clear, while neuron-like/state subdivisions require caution).
4. Platform and donor are completely confounded (10x n=1 / ICELL8 n=3): differences such as donor1-specific neuron-like or donor2-4-specific erythroid cannot distinguish platform effects from donor variability.
5. This entry represents the capture composition of RPE suspension after dissociation (the counting denominator excludes complete histology of non-RPE tissue), and does not reflect the positional abundance of the RPE layer within intact globe/choroid tissue; reference for histological abundance requires full-tissue entries including RPE (retina/choroid skeleton).
6. KB2c t_be336eee Red Line 2: This entry lacks per-donor developmental/age metadata → developmental stage = unknown + disclosure line; it must not be cited as 'adult RPE baseline'; upgrading to adult-only requires supplementing per-donor age data (GEO supplementary tables/author correspondence) followed by separate adjudication.

## Source List
| sid | Type | Label |
|---|---|---|
| `RPE_LOCAL` | dataset | Author-processed file /mnt/D/OcularKB/data/GSE158629/GSE158629_scrRNA_RPE_donors1-4.RData.gz (GSE158629); Exported files /mnt/D/EyeKB/scripts/baselines/data/rpe_GSE158629_cells_meta.csv + /mnt/D/EyeKB/scripts/baselines/data/rpe_GSE158629_cluster_markers.csv (scripts/baselines/data/export_rpe_meta.R) |
| `RPE_GEO` | dataset | GEO GSE158629 — Single-Cell RNA Sequencing Reveals the Heterogeneity of the Human RPE (Abstract includes descriptions of rod/cone/TF+SPP1/stem cell candidate clusters) |

