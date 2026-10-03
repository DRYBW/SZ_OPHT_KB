# Composition Baseline · Observation Tier: Human Lacrimal Gland (lacrimal_gland) — KB8 t_e7ec73ab, 2026-09-25

**status = observed_single_study_pilot**: single study (GSE164403, the only human lacrimal gland in-vivo single-cell atlas to date, PMID:33730555),
measured composition after tissue pool QC of 1,076 cells, 3 donor labels (patient 3 accounts for 76% dominance). **Not** a cross-study reference distribution,
prohibited as composition benchmark (Astra T2 scope retained), prohibited from entering all scoring.

## Cluster Partition (self-built clustering scope for this card — authors did not deposit cell type labels)

| cluster | cells | proportion | lexical surface/reference |
|---|---|---|---|
| Lacrimal_secretory_tearcell | 65 | 6.0% | markers_v6_lacrimal_increment（LACRT/SCGB1D1/SCGB2A1/CST4/CST1/MUC7）|
| Lacrimal_duct_epithelial | 455 | 42.3% | markers_v6_lacrimal_increment (PRR27 single-gene core) |
| Lacrimal_myoepithelial | 18 | 1.7% | warning entry core=[] (mural×epithelial bidirectional firestorm, see lexical entry file) |
| T cells | 106 | 9.9% | reference layer (membrane v1 panel) |
| IgA plasma cells | 292 | 27.1% | reference layer; risk of upward bias in proportion (IGH ambient plate-level carryover) |
| Endothelial | 14 | 1.3% | reference layer; extremely weak support |
| Fibroblast/stroma | 115 | 10.7% | KB6b general signature note, does not enter independent new lexical entry |
| Surface epithelium contamination | 11 | 1.0% | true conjunctival epithelium (face_v6 lexical entry audit empirical hit = positive control) |

## Three Hard Disclosures

1. **Acinar Zymogen Gap**: PRSS1/CTRB1/PNLIP undetectable in the entire pool—"lacrimal gland acini" unproven at the transcriptomic level;
   Secretome=LACRT+ serum mucin pool (CL:0000315 tear secreting cell).
2. **384-well plate ambient**: LYZ 0.8–14.9k CPM, LTF 0.5–5.9k CPM across groups det≈1.0;
   LACRT non-secretory baseline 1.5–5k CPM. The secretory/plasma-cell fractions carry upward-bias risk.
3. **Organoid Pool (1,395 QC cells) never enters this archive**: Source paper limits organoids=ductal model;
   KB8 red line (separate accounting for two pools). Patient "3" cross-pool ID match unproven as same individual.

Data binding sha see JSON `data_binding`; recomputation chain=entry file `provenance.pipeline`.
Backfill path (backfill_path): Second independent human lacrimal dataset currently does not exist → This archive maintains pilot status as terminal state until new material.
