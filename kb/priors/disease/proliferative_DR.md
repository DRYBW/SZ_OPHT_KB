# Disease Prior: Proliferative Diabetic Retinopathy (PDR)

> schema: `eyekb-prior/1.0` | entry_id: `proliferative_DR` | Frozen: 2026-09-23 | Source card: t_39182aa2
> This file is automatically rendered by `/mnt/D/EyeKB/scripts/priors/build_priors.py` from the same-named .json —— To modify content, edit JSON+script; manual MD edits will be overwritten.
> **Reading Discipline**: This entry is a prior and QC flag, prohibited in scoring; if conflicting with data → report via flag, do not force fit.

## Evidence grade definitions

- **A**: Local empirical recalculation
- **B**: Direct reporting in original literature
- **C**: Model/developmental evidence extrapolation
- **D**: Review background (qualitative only)

## Expected Cell×Status Matrix (by tissue end)

### fibrovascular_membrane  [A+B]

- Macrophages: tissue-resident (SELENOP/FOLR2) + recruited classical monocytes (FCN1/LYZ) + foamy DAM-LAM (GPNMB/TREM2/SPP1) + MHC-II-high APCs + heme-associated stress (HMOX1)
- Endothelial: Pathological state (PLVAP/NDUFA4L2/HIF1A/ICAM1/VCAM1) + tip/stak sub-states (DLL4; Grade C extrapolated from TIPCELL_DEV/RAB5IF)
- Pericyte→Myofibroblast continuous transition (PRRX1 driven, B: PRRX1)
- Stromal: High extracellular matrix COL1A1/COL3A1/FN1
- Lymphoid: T (CD69 activated), low proportion of plasma cells
- Proliferating: MKI67+ population present (including MKI67+ microglia, B: PDR_MKI67MG)
- Glial: Müller/reactive glial scar components (GFAP↑, B: GLIA_RDG)

### vitreous  [B]

- Absolute dominance of T cells (91.6%, B: VITREOUS_T), neutrophils nearly absent
- Interpretation: Composition of vitreous and membrane specimens is completely different — must distinguish tissue ends first

### retina_adjacent  [B]

- Early-mid DR retina: Microglia status changes without large-scale myeloid influx (B: MG_EARLY_DR/DR_RETINA_SC)
- Müller reactivity (REDD1/gliosis, B: MULLER_REDD1)
- Neuron proportion does not significantly increase due to PDR itself — membrane ≠ retina

## Unexpected Flags

- **Large clusters of retinal neurons (Rod/Cone/BC/AC/HC)** — Membrane specimen >5% → Flag: Specimen suspected to contain retinal body, report to PI
- **High background of photoreceptor outer segments/lysis fragments (excluding HBA)** — Diffuse mitochondrial+ROS stress signature → Dissociation stress flag, not a disease flag
- **Progenitor/organoid features** — Any clinical membrane specimen → Suspected sample contamination/misannotation, flag and escalate
- **Enriched clusters of mast cells/eosinophils** — Allergic background → unexpected-report

## Contamination Flags

- **Peripheral blood (classical monocytes FCN1/LYZ/S100A8/9 + platelets PF4/PPBP + neutrophils FCGR3B/CSF3R)** → Blood influx in surgical specimens — Myeloid count interpretation must first deduct blood-derived components (B: GSE165784 v2 B10/sub14 Grade A measured)
- **RPE/choroidal pigment components (BEST1/RPE65/TYR+melanin)** → Penetrating sampling/concurrent rhegmatogenous detachment procedures
- **Vitreous-derived T dominance (control 91.6%)** → Residual liquid phase components in vitrectomy specimens

## Signature Axes (marker panels)

- `tissue_resident_mac`: SELENOP, MRC1, FOLR2, CD163, STAB1, VSIG4, CD5L
- `recruited_monocyte`: FCN1, VCAN, S100A8, S100A9, CD14, SELL, S100A12
- `foam_DAM_LAM`: GPNMB, LIPA, CTSD, LGMN, PLD3, TREM2, SPP1, APOE, MMP9
- `heme_stress_mac`: HMOX1, FTL, FTH1, CD163
- `MHCII_high_APC`: HLA-DRA, HLA-DRB1, CD74, HLA-DQA1, HLA-DPB1
- `patho_endothelial`: PLVAP, NDUFA4L2, HIF1A, ICAM1, VCAM1, DLL4, ESM1
- `pericyte_to_myofibro`: PRRX1, ACTA2, TAGLN, POSTN, COL1A1, COL1A2, CTHRC1, TIMP1
- `reactive_glia`: GFAP, VIM, CRYAB, CLU, TIMP1
- `blood_platelet`: PPBP, PF4

*Signature provenance: markers_membrane_v1.json (canonical/data_driven/pmid_context tri-state provenance) + v2 empirical clusters*

## Notes

1. tip/stalk endothelial substates: Limited direct single-cell evidence from human PDR membranes (DLL4+ tip biology mostly from development/OIR), marked Grade C — Expected presence but no interval set for proportions.
2. Composition differences between PDR and RRD membranes lack sufficient independent controls — Any 'disease-specific cluster' determination requires disease-end controls before writing (lesson from v2 draft RRD stratification).
3. PI: PDR annotations themselves may not be accurate → This prior serves as control and QC flags, not ground truth; when conflicting with data, output 'prior vs. data conflict list' for escalation.

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
