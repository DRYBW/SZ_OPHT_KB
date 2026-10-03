# Composition baseline: Cellular composition of human (normal) neural retina

> schema: `eyekb-prior/1.0` | entry_id: `human_retina` | Frozen: 2026-09-23 | Source card: t_39182aa2
> This file is automatically rendered by `/mnt/D/EyeKB/scripts/priors/build_priors.py` from the same-named .json —— To modify content, edit JSON+script; manual MD edits will be overwritten.
> **Reading Discipline**: This entry is a prior and QC flag, prohibited in scoring; if conflicting with data → report via flag, do not force fit.

## Evidence grade definitions

- **A**: Local empirical recomputation (with path)
- **B**: Direct reporting in original literature
- **C**: Empirical intervals derived from cross-study distribution of A-grade source data

## Main table: Cell type × proportion interval

| Cell type | Chinese name | HRCA measured % | Expected interval % | Cross-study spread % | Local library marker | Evidence | Notes |
|---|---|---|---|---|---|---|---|
| Rod | Rod photoreceptor | 33.55 | 28–46 | 19.05–47.77 | RHO, NRL, NR2E3, PDE6B, GNAT1 | A | — |
| Cone | Cone photoreceptor | 4.0 | 1.5–7 | 0.95–6.44 | OPN1SW, OPN1MW, ARR3, PDE6H, GNAT2 | A | — |
| BC | Bipolar cell | 21.75 | 12–33 | 5.54–32.64 | VSX2, GRM6, CACNA1S, ISL1, OTX2 | A | — |
| AC | Amacrine cells | 17.99 | 8–28 | 7.87–27.67 | TFAP2A, GAD1, GAD2, SLC6A9, ONECUT2 | A | — |
| HC | Horizontal cells | 2.54 | 1–8 | 0.51–7.65 | ONECUT1, ONECUT3, GAD1, ISL1, CX3CR1 | A | — |
| RGC | Retinal ganglion cells | 12.58 | 3–15 | 0.18–43.64 | RBPMS, SLC17A6, POU4F1, POU4F2, NEFL | A | RGC-targeted studies (Chen_rgc pooled 46.2%, Shekhar_legacy 43.6%) use sorting/enrichment designs; high proportion ≠ anomaly |
| MG | Müller glia | 6.97 | 3–12 | 1.93–10.44 | RLBP1, GLUL, SOX9, VIM, S100B | A | — |
| Astrocyte | Astrocytes | 0.44 | 0.1–1.5 | 0.23–1.03 | GFAP, AQP4, S100B, VIM, SLC1A3 | A | — |
| Microglia | Microglia | 0.15 | 0.05–0.8 | 0.0–0.26 | C1QB | A | — |
| RPE | Retinal pigment epithelium | 0.03 | 0–1.0 | 0.0–0.12 | BEST1, RPE65, TTR, LRAT, RDH5 | A | High RPE proportion in neural retina sections suggests RPE/choroid contamination (not native neural retina component) |

## Subtype layer (annotated cell proportion % within class)

*cell_type column subdivision covers only finely annotated cells within the majorclass; % represents subtype/annotated cell count within class*

- **BC** (BC subtype-annotated cells): flat midget bipolar cell 20.9%; invaginating midget 15.4%; rod bipolar cell 14.7%; diffuse bipolar 2 9.9%; DB1 7.3%; DB4 7.1%; DB3b 5.1%; giant bipolar (GB) 3.7%; DB3a 3.2%; DB6 2.7%
- **AC** (AC annotated cells): GABAergic amacrine 63.5%; glycinergic amacrine 23.0%; amacrine (unclassified) 10.0%; starburst amacrine 3.5%
- **RGC** (RGC annotated cells): OFF midget GC 50.2%; ON midget GC 38.0%; retinal ganglion cell (untyped) 7.8%; OFF parasol 2.5%; ON parasol 1.5%
- **HC** (HC annotated cells): H1 85.2%; H2 14.8%
- **Cone** (Cone annotated cells): retinal cone cell 93.3%; S cone 6.7%

## State layer (cell type × state)

| Cell type | State | Marker | Evidence | Notes |
|---|---|---|---|---|
| Microglia | homeostatic | P2RY12, TMEM119, CX3CR1, IRF8, C1QA/B, TYROBP, AIF1, SALL1, HEXB | A+B | Merged legacy_v4 + AUC candidates from retina library; extremely low proportion in normal retina (HRCA 0.15%) |
| Müller glia | homeostatic | RLBP1, GLUL, SOX9, S100B, VIM, AQP4(low) | A | — |
| RPE | homeostatic | BEST1, RPE65, LRAT, RDH5, MITF, TTR | A | RPE should be near-zero in neural retina specimens; presence triggers RPE/choroid contamination flag |
| Astrocyte | homeostatic (perivascular) | GFAP, AQP4, SLC1A3, S100B | A | GFAP upregulation = reactive gliosis flag, see disease entries |

## Flag semantics

**Expected but low proportion**:

- Microglia (0.05~0.8%)
- RPE (≈0, >1% indicates contamination)
- Astrocyte (0.1~1.5%)

**Unexpected (→ unexpected flag)**:

- Large progenitor/PCNA+ clusters (adult retina)
- Abundant mast cells/eosinophils

**Contamination suspicion (→ contamination-suspect flag)**:

- High MT photoreceptor debris regions (dissociation stress, see disease entries)
- Large peripheral blood myeloid clusters (FCN1/LYZ) —— residual blood flag for whole-retina specimens

## Notes

1. Single-sample proportions are strongly influenced by sampling/sorting design (NeuN± nuclear sorting, RGC enrichment, fovea vs periphery, lobe vs macular): Cross-study spread (basis for Grade C interval derivation) = min~max of pooled data from 6 groups: Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy, excluding RGC-targeted groups.
2. The HRCA 10-class lexical surface does not include endothelial/pericytes (neural retina integration excludes vascular classes). True whole retina contains low proportions of vascular components; small Endo/Pericyte clusters in annotated data represent normal vasculature and do not trigger a contamination flag (contrast with disease entries).
3. RGC-enriched samples (e.g., Chen_rgc 46.2% RGC, Shekhar legacy 43.6%) have high proportions due to design intent — dataset construction strategy must be checked before adjudicating 'anomaly'.
4. Developmental/organoid specimens are not applicable to this baseline (progenitor and subtype proportions differ completely; anchor DEV_DUAL/RETINA_ORGANOIDS).
5. PI reminder: Self-annotation of public data may itself be inaccurate — all proportions in this entry are 'priors with evidence grades'; when conflicting with data, raise flags rather than forcing alignment.

## Source List

| sid | Type | Grade clue | Label |
|---|---|---|---|
| `HRCA317M` | dataset | 41578023 | HRCA CELLxGENE merged version, 3,177,310 cells (10 majorclasses, all normal, 6 studies/104 donors, fovea~periphery) |
| `HRCA_PAPER` | paper | 41578023 | Li et al., Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nat Genet 2026 (full atlas ~3.9M cells, 123 RNA classes) |
| `FOVEA_PERIPH` | paper | 32555229 | Cell Atlas of the Human Fovea and Peripheral Retina (2020) — shared types between central fovea/periphery but regional differences in proportions and expression |
| `AGING_ATLAS` | paper | 34691611 | A single-cell transcriptome atlas of the aging human and macaque retina (2021) |
| `MULTIOMICS_ATLAS` | paper | 37388908 | A multi-omics atlas of the human retina at single-cell resolution (2023) |
| `RETINA_ORGANOIDS` | paper | 32946783 | Cell Types of the Human Retina and Its Organoids at Single-Cell Resolution (2020) |
| `DEV_DUAL` | paper | 39117640 | Single cell dual-omic atlas of the human developing retina (2024) — developmental stage includes progenitors, adult baseline not applicable |
| `RETLIB41` | kb | /mnt/D/EyeKB/kb/markers/markers_v4.1_clean.json | Local marker library markers_v4.1_clean.json v4.1-clean-P0.4 |
