# Composition Baseline: Human PDR Fibrovascular Membrane

> schema: `eyekb-prior/1.0` | entry_id: `human_pdr_membrane` | Frozen: 2026-09-23 | Source Card: t_39182aa2
> This file is automatically rendered by `/mnt/D/EyeKB/scripts/priors/build_priors.py` from the same-named .json —— To modify content, edit JSON+script; manual MD edits will be overwritten.
> **Reading Discipline**: This entry is a prior and QC flag, prohibited in scoring; if conflicting with data → report via flag, do not force fit.

## Evidence grade definitions

- **A**: Local empirical recomputation (with path)
- **B**: Direct reporting in original literature
- **C**: Cross-study empirical range

## Main Table: Compartment × Proportion

| Compartment | PDR-only% | Total Sample% | Cell Count (PDR) | Evidence | Description |
|---|---|---|---|---|---|
| myeloid (Myeloid total (Macrophage/Monocyte/DC/pDC, Track B cluster assignment)) | 79.5 | 82.28 | 5,677 | A(count)+B(qualitative) | Myeloid dominance in PDR membrane is literature consensus (B: PDR_HU2022/PDR_JCI2023) and consistent with local empirical measurement (A) |
| stromal_myofibro (Myofibroblast (COL1A1/COL1A2/ACTA2/TAGLN/POSTN/PRRX1)) | 4.4 | 3.69 | 317 | A(count)+B(qualitative) | Fibrous component = naming subject of membrane specimen; pericyte-to-myofibroblast transition driven by PRRX1 (B) |
| stromal_pericyte (Pericyte (RGS5/PDGFRB/NOTCH3/PRRX1)) | 3.5 | 2.48 | 250 | A(count)+B(qualitative) | Vascular wall cells, together with endothelial cells constitute the 'fibrovascular' triad |
| endothelial (Endothelial (CLDN5/VWF/PECAM1; pathological state PLVAP/DLL4/NDUFA4L2)) | 3.8 | 2.68 | 270 | A(count)+B(qualitative) | Proliferative vascular end; tip/stalk sub-state evidence mainly from developmental/OIR models (Grade C extrapolation) |
| lymphoid_T (T cells (CD3D/CD2/CD69 activation)) | 4.7 | 3.52 | 333 | A(count)+B(qualitative) | Present in membrane specimens; note distinction from vitreous humor (T 91.6%) tissue side |
| lymphoid_plasma (Plasma cells (MZB1/JCHAIN/IGHG1)) | 0.8 | 0.61 | 58 | A(count)+B(qualitative) | Presence at low proportion meets expectation |
| proliferating (Proliferating group (MKI67/TOP2A/CENPF; mixed origin)) | 1.7 | 3.12 | 121 | A(count)+B(qualitative) | Proliferation proportion in PDR-only scope lower than total sample (RRD stress myeloid contribution large); MKI67+ microglia drive neovascularization (B: PDR_MKI67MG) |
| glial_candidate (Glial candidate (Müller/reactive glial scar; CRYAB/CLU, RLBP1 absent)) | 1.6 | 1.62 | 116 | A(count)+B(qualitative) | Fibrotic membrane contains glial scar components (B: GLIA_RDG/MULLER_REDD1); but markers for this cluster incomplete → indistinguishable flag, do not hard-label |

## Myeloid State Layer

| Cell Type | State | Signature/Description | Cluster | Total Sample% | PDR-only% | Evidence |
|---|---|---|---|---|---|---|
| Macrophage | homeostatic-like | Tissue-resident macrophages SELENOP/MRC1/FOLR2/STAB1/CD163 | B13+mye sub7 | 7.0 | 9.6 | A |
| Macrophage | foam_DAM_LAM | Foam-like/lipid phagolysosome GPNMB/LIPA/PLD3/CTSD/TREM2/SPP1 | B5+sub10/sub12 | 10.0 | 14.0 | A |
| Macrophage | MHCII-high_APC | High MHC-II presentation HLA-DR/DQ/CD74 (B1/B3/B4 merged) | B1+B3+B4 | 25.5 | 28.7 | A |
| Macrophage | inflammatory_heme | Inflammation/heme stress HMOX1/CCL3/CXCL8 | B2+sub8 | 10.7 | 13.2 | A |
| Monocyte | classical_blood | Peripheral blood classical monocytes FCN1/LYZ/VCAN/S100A8/9 (main body of blood contamination flag) | B10+sub14 | 6.8 | 9.5 | A |
| Monocyte | nonclassical | Non-classical FCGR3A+/CD14-low | B4 | 8.2 | 9.0 | A |
| Microglia | homeostatic | Resident microglia P2RY12/TMEM119/CX3CR1 low proportion; difficult to distinguish from macrophages in membrane specimens | B0 partial | — | — | B |
| Macrophage | RRD_stress | High MT/hypoxic stress state in RRD specimens (S100A8/9/NUPR1/FABP5/MMP9) — not PDR-specific | B0+B6+sub0/1/2/11 | 21.7 | 3.9 | A |

## Flag semantics

**Expected**:

- Myeloid dominance (70~85%)
- Endothelial + pericyte + myofibroblast triad
- Foam-like/DAM-LAM macrophages
- MHC-II high APCs
- Few T/plasma cells

**Unexpected (→ unexpected flag)**:

- Large retinal neuron cluster (>5% → specimen suspected to contain retinal body, conflicting with 'membrane' naming)
- Progenitor/organoid features (should not be present in membrane specimens)
- Large RPE cluster (>3% → suspected non-membrane tissue or sampling included RPE-choroid)

**Contamination suspicion (→ contamination-suspect flag)**:

- Blood-derived myeloid (FCN1/LYZ/S100A8 classic monocyte high) — residual blood in surgical specimens, note interpretation of proportions
- Platelet gene signals (PF4/PPBP)
- Mixed dominant vitreous T-cell component (control VITREOUS_T: vitreous T 91.6%)

## Notes

1. GSE165784 is a mixed dataset of PDR membranes + RRD (rhegmatogenous retinal detachment) membranes; RRD accounts for 29.1% of cells. PDR-specific readouts use the PDR-only scope (n=7,142); the stress states of B0/B6/sub0/1/2/11 are driven by RRD samples and are not PDR biology (v2-draft audit trail).
2. Membrane specimens ≠ whole retina: Rod/BC/AC/HC neurons lacking independent clusters is expected, do not raise unexpected flag.
3. n=1~2 PDR donor-level differences are large, proportion ranges only provide 'order of magnitude' precision; no second self-calculated PDR membrane dataset exists in the library for cross-validation (B-grade literature anchors did not provide exact %).
4. PI reminder: Self-annotations of public PDR data may not be accurate — B-grade entries serve only as qualitative direction, numerical adjudication relies on A-grade local recalculation.

## Source List

| sid | Type | Grade clue | Label |
|---|---|---|---|
| `GSE165784V2` | dataset | 35061025 | GSE165784 human PDR fibrovascular membrane + RRD membrane scRNA, v2 integration track Track B (harmonypy, 17 clusters, 10,069 cells; PDR-only 7,142) |
| `PDR_HU2022` | paper | 35061025 | Hu et al. Single-Cell Transcriptomics Reveals Novel Role of Microglia in Fibrovascular Membrane of PDR. Diabetes 2022 (original source for GSE165784) |
| `PDR_JCI2023` | paper | 37917183 | Single-cell transcriptomics analysis of PDR fibrovascular membranes. JCI Insight 2023 |
| `PDR_SOX15` | paper | 42601615 | Human single-cell atlas of PDR reveals a SOX15-overexpressing stromal population. J Transl Med 2026 |
| `PDR_MKI67MG` | paper | 40069725 | Single-cell analysis identifies MKI67+ microglia as drivers of neovascularization in PDR. J Transl Med 2025 |
| `PDR_NICHE` | paper | 40562775 | Metabolic reprogramming of the neovascular niche promotes regenerative angiogenesis in proliferative retinopathies. Nat Commun 2025 |
| `PRRX1` | paper | 41230906 | PRRX1 Orchestrates Pericyte-Myofibroblast Transition in Pathological Retinal Fibrosis. IOVS 2025 (in-library) |
| `RAB5IF` | paper | 41390488 | Endothelial RAB5IF is required for pathological and developmental retinal angiogenesis. Nat Commun 2025 (in-library) |
| `VITREOUS_T` | paper | 39220810 | Liquid Biopsy for PDR: Single-Cell Transcriptomics of Human Vitreous. Ophthalmol Sci 2024 — PDR vitreous T-cells 91.6% (tissue control: vitreous ≠ membrane) |
| `MEMLIB` | kb | /mnt/D/EyeKB/kb/markers/markers_membrane_v1.json | Local membrane marker library markers_membrane_v1.json v1-membrane-20260923 (gene-by-gene provenance) |
| `MULLER_REDD1` | paper | 35167652 | Müller Glial Expression of REDD1 Is Required for Retinal Neurodegeneration... Diabetes 2022 (in-library; reactive glial background) |
| `GLIA_RDG` | paper | 32069977 | scRNA-seq in Human Retinal Degeneration Reveals Distinct Glial Cell Populations. Cells 2020 (in-library; human retinal degeneration glial states) |
| `DR_RETINA_SC` | paper | 34006945 | In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying DR. Sci Rep 2021 (in-library) |
| `MG_EARLY_DR` | paper | 38409074 | scRNA-seq reveals roles of unique retinal microglia types in early DR. DMS 2024 (in-library) |
| `TIPCELL_DEV` | paper | 34273276 | Specialized endothelial tip cells guide neuroretina vascularization and blood-retina-barrier formation. Nat Commun 2021 (in-library; tip/stalk biological origin, developmental/model evidence → PDR extrapolation C-grade) |
