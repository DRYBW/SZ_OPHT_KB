# Composition Baseline Skeleton: Human conjunctiva (all fields present, proportions=pending backfill)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_conjunctiva` | status: skeleton_mapping_backfilled | developmental axis: **organism_stage=unknown** | generated: 2026-09-23 | card: t_16c3e020
> **KB3 development record (Card t_5425a7ca)**: development_stage=**unknown** | Applicable record (hardcoded during backfill): adult —— KB3 prohibition (PI Red Line 2026-09-23): developmental data must not enter the adult baseline statistical pool, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal do not serve as mutual references.
> This file is automatically rendered from the corresponding .json by `/mnt/D/EyeKB/scripts/baselines/build_baselines.py` — modify content in JSON+script; manual MD edits will be overwritten.
> ⚠ Development axis disclosure: KB2c development axis: Skeleton entry=unknown (not computed). During backfill, must list separately by development axis — adult material yields adult-only main record (>=18y adjudication Q2), fetal/developmental material creates separate entries, mixing fetal and adult records for the same tissue is prohibited (PI Red Line).

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
- Two-tier identities: {'adult_only': 'baseline_human_conjunctiva__adult_only__kb2c', 'adult_pool': 'baseline_human_conjunctiva__adult_pool__v1.0'}

## Astra T2 metadata fields
- **Sampling material**: TBD (Skeleton: actual sampling material scope must be fixed before building baseline, Astra T2)
- **Disease stage**: TBD
- **Treatment background**: TBD
- **scRNA_vs_snRNA**: TBD
- **Enrichment steps**: TBD
- **Dissociation method**: TBD
- **Donor count**: TBD
- **Count denominator**: TBD
- **Evidence source**: See candidate datasets in mapping_from_t_6f5cc731

## Composition data status
**Interval cannot be estimated (valid state, Astra T2) — pending donor-level calculation based on mapped candidate datasets; data not local must first pass download approval iron rule**

## Candidate dataset mapping (t_6f5cc731 inventory backfill)
- `GSE191232` [human] 7 samples (adult conjunctival epithelium, isolates C16/C15/C10) | annotation: cell types present in meta.txt | availability: counts+meta+umap processed files directly retrievable | the only "adult normal conjunctival epithelium" processed dataset; note samples = air-liquid-interface organoid model, not a fresh-tissue atlas
- `GSE155683` [Human] 17 fetal + 4 adult conjunctiva | Annotation: paper | Availability: SRA+portal | Development-focused accessory coverage
- `GSE217707` [Human] 10 samples (conjunctival melanoma TME) | Annotation: paper | Availability: RAW.tar only | Tumor context, not a normal reference
- `Tabula Sapiens - Eye (34,273)` [Human] Whole-body organs include conjunctiva labels, small eye proportion | Annotation: portal | Availability: portal h5ad | Scattered coverage does not constitute an atlas
- `OA-D002 Ocular Surface Collection` [Human] Portal tissue labels do not list conjunctiva separately (only cornea/limbus/sclera) | Annotation: portal | Availability: portal | ⚠ GEO original has conjunctiva but portal label did not expose it — building a conjunctival reference requires cutting from GSE155683 original annotations

**Adjudication (t_6f5cc731)**: ⚠️ Insufficient data (no dedicated single-cell atlas for adult normal conjunctiva; only organoid model GSE191232 + developmental accessory GSE155683 + scattered Tabula. Recommendation: Integrate into ocular surface as "conjunctival epithelium" subgroup annotation, do not build an independent model of 11 classes)

**Backfill path**: ① Verify localization status of candidate data → ② Official annotation slicing (celltype-annotation-sourcing discipline) → ③ Append build_<tissue>() donor-level recalculation via this script → ④ Change baseline status to filled_donor_level → ⑤ KB2c development axis: only adult (>=18y) donors enter main record, non-adult disclosed line-by-line; fetal/developmental material creates separate entries, prohibited from merging into adult

## Notes
1. Skeleton entries must not be used for external statements like 'this tissue has a composition baseline' (Astra T6: engineering consistency ≠ correctness evidence)

