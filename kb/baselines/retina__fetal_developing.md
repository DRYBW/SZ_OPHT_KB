# Composition Reference (Developmental Stage): Human fetal retina fetal_developing (author/portal label aggregation, KB3 independent entry)

> schema: `eyekb-baseline-development/1.0` | entry_id: `baseline_human_retina__fetal_developing__kb3` | Status: development_annotated_aggregate | **development_stage=fetal_developing** | Generated: 2026-09-24 | Card: t_5425a7ca
> ⚠ KB3 prohibition (PI red line 2026-09-23): Developmental-stage data must not enter adult baseline statistical pools, and vice versa —— fetal ≠ adult for the same tissue; adult/fetal are not mutual references.
> This file rendered by `/mnt/D/EyeKB/scripts/baselines/kb3_build_dev_entries.py` from material `plans/kb3_evidence/fetal_agg_20260924.json` — modify content via aggregation script + material; manual MD edits will be overwritten.

**Nature**: Developmental stage **composition reference** entry: Numbers = **direct count aggregation** of published cell labels from dataset authors/CELLxGENE portal, not inference by active adult engine (engine must abstain for fetal, E4/E5 OOD_strict frozen artifact); donor-level median/IQR metrics not established (fetal reference pipeline task not started, KB2c adjudication Q5); this entry is a label-distribution-level reference.

**Usage Metric**: Identity reference for fetal/developmental retinal material + OOD behavior control anchor (E5 homologous data); must not be used as composition benchmark; must not serve as mutual reference with adult primary archive (PI red line); prohibited from all scoring (Astra T2 global inheritance).

## Anchor and Availability Verification (KB3 Discipline 3: No entry without evidence)

| Anchor | Role | Cells | Layer | On-disk Evidence |
|---|---|---|---|---|
| GSE268630 | Portal primary anchor | 226,506 (14 donor) | 11w2d–23w4d full fetal period | gse268630_cellxgene.h5ad measured (same file as repo E5 frozen artifact) |
| GSE138002 | Author-label secondary anchor | Final 118,555 (fetal layer 88,013) | Hgw9–Hgw27 measured (task spec GW9-19 narrower) | Final_barcodes.csv.gz umap2_CellType |
| GSE234963 | **Data card only** | 176,849 (24 samples) | ~7.5–21 PCW | obs lacks label column; measured → composition pending backfill |

## Developmental stage label distribution — GSE268630 (portal majorclass, full pool direct count)

| majorclass | % | n_cells |
|---|---|---|
| PRPC | 23.17 | 52,479 |
| RGC | 18.54 | 41,984 |
| Rod | 16.85 | 38,167 |
| AC | 11.65 | 26,384 |
| NRPC | 9.31 | 21,087 |
| BC | 9.27 | 20,996 |
| HC | 4.21 | 9,532 |
| Cone | 4.12 | 9,324 |
| MG | 2.89 | 6,553 |

> Anatomical site: macula lutea 119,111 / peripheral 100,532 / unlabeled 6,863; PRPC/NRPC are development-specific with no adult counterpart — **mapping into the adult 10-class lexical surface is prohibited**.

## Developmental stage label distribution — GSE138002 fetal retina layers (author umap2_CellType)

| celltype | % |  | Sample level | Hgw9–Hgw27 (17 unit) |
|---|---|---|---|---|
| RPCs | 34.49 | | | |
| Rods | 14.65 | | | |
| Amacrine Cells | 12.45 | | | |
| Retinal Ganglion Cells | 10.18 | | | |
| Horizontal Cells | 7.39 | | | |
| Bipolar Cells | 6.8 | | | |
| Cones | 5.05 | | | |
| Neurogenic Cells | 3.77 | | | |
| BC/Photo_Precurs | 2.86 | | | |
| AC/HC_Precurs | 1.97 | | | |
| Muller Glia | 0.39 | | | |

## Newborn layer (GSE138002 Hpnd8) — development_stage=postnatal_neonatal (third value substantiated here)

- Rods: 66.47%
- Bipolar Cells: 30.47%
- Muller Glia: 0.83%
- Horizontal Cells: 0.79%
- Amacrine Cells: 0.62%
- RPCs: 0.56%
- Cones: 0.27%

## Exclusion layer (do not merge, register only)

- **Adult face** (11,618 cells): Adult control material → excluded from developmental entries; also not part of D001 system, no separate adult entry created (isolated record).
- **Organoid Days face** (11,542 cells, ['24_Day', '30_Day', '42_Day', '59_Day']): organoid→unknown+flag (adjudication Q1).

## Cross-source scope statement

Two anchor vocabularies differ (portal majorclass 9 classes vs author 12+ classes) — this entry displays them side-by-side, does not synthesize a single distribution (Astra T6 non-synthesized metric developmental axis inheritance).

⚑ **Current reading engine=adult domain, must abstain for this material; numbers in this entry cannot be used as scoring benchmarks for engine output correctness on fetal data (E5 is behavioral description only).**
⚑ Donor-level interval scope not established (fetal pipeline separate batch), this flag must accompany citations.

## caveats
- Label distribution = transcriptomic face of published annotations; GSE268630 also contains multiome ATAC face GSM matrix (not merged into this entry).
- GSE138002 'Final' is the author-cleaned set (118,555/total 138,672); All_barcodes face lacks label column, aggregation based on Final.
- This entry = independent file for developmental stage; KB2c conceptual entry fetal_development_transitions remains an entry placeholder, both coexist: conceptual entry answers 'what candidates exist', this entry answers 'what is the measured fetal retina label distribution'.

Identity signature: `{"baseline_human_retina__fetal_developing__kb3": "sha256:4c5056b77d1c5e59c7ed5a5cb204f29b14f06eb22078a5e366c120201349d846"}`
