# Composition Baseline Skeleton: Human lens (all fields present, ratios=pending backfill)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_lens` | status: skeleton_mapping_backfilled | developmental axis: **organism_stage=unknown** | generated: 2026-09-23 | card: t_16c3e020
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
- Two-tier identity: {'adult_only': 'baseline_human_lens__adult_only__kb2c', 'adult_pool': 'baseline_human_lens__adult_pool__v1.0'}

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
- `HASA "Lens" (OA-D004/016)` [Human] 13,900 cells(nuclei) | annotation: portal | availability: portal h5ad | Human lens portal annotation source
- `GSE287919` [Human] 16 lens(8 pairs donor,<65/≥65 years) | annotation: paper(Gu2025 SCRT PMID40598599;6 clusters incl TAC/LPLC) | availability: suppl directory empty→data via SRA (verified) | Human lens epithelium + aging atlas; fiber cells dominated by crystallins require ambient protection
- `GSE113887` [Mouse] 24 samples differentiation time series | annotation: — | availability: suppl | Time-series bulk dominant (PMID29883638)
- `GSE215953` [Mouse] 30 samples SuperSeries(RNA+ATAC) | annotation: paper | availability: via subseries | Vitreous-induced fibrotic differentiation
- `Zebrafish Dev Atlas(CELxGENE)` [Zebrafish] lens label 1.2M(whole fish) | annotation: portal | availability: portal | Developmental cross-species corroboration, not human reference

**Adjudication (t_6f5cc731)**: ✅Reference model buildable-limited (HASA Lens 13.9K+GSE287919 human 16-lens aging atlas; only epithelial layer reliable, fiber cells=crystallin-dominated+ambient risk, reference model should limit to LEC domain)

**Backfill path**: ① Verify localization status of candidate data → ② Official annotation slicing (celltype-annotation-sourcing discipline) → ③ Append build_<tissue>() donor-level recalculation via this script → ④ Change baseline status to filled_donor_level → ⑤ KB2c development axis: only adult (>=18y) donors enter main record, non-adult disclosed line-by-line; fetal/developmental material creates separate entries, prohibited from merging into adult

## Notes
1. Skeleton entries must not be used for external statements like 'this tissue has a composition baseline' (Astra T6: engineering consistency ≠ correctness evidence)

