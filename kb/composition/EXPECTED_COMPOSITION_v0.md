# EXPECTED_COMPOSITION_v0 — Normal Adult Eye Composition Prior Surface (Human-readable Version)

> Generated 2026-09-28 | Card t_fa03e1d7 | Authorization: USER_DIRECTIVE_20260928_eyekb_improve_wave.md Appendix VII-B (D-1); Task Brief plans/comp_prior_20260928/BRIEF_DISC_COMP.md
>
> **⛔ Wiring Status: `OFF — Not Wired (Zero MCP/runtime references; wiring and activation require separate cards and approvals, any activation of this surface requires PI adjudication)`** —— Any runtime consumption of this surface (MCP/baselines/scoring/gating) requires separate cards and approvals, PI adjudication.

## 0. Positioning and Scope (Read This First)
- Surface Semantics: **Surface = Composition reference for captured events from this sampling material under this experimental workflow (identity reference + background control), not histological ground truth, not a composition compliance threshold; Flags = prompts for re-review ≠ annotation errors**
- Evidence Levels: A=Registry ledger external author annotations locally recomputed (kb/baselines adult-only donor-level master file, with paths); B=On-disk ingested RAG literature original text directly reported (chunks verbatim sentences); C=Cross-study empirical intervals (kb/priors/composition/human_retina.json, card t_39182aa2); no_evidence=No A/B/C available → Do not fabricate numbers
- Lineage Declaration (Anti-circularity Clause): Proportion interval sources = D001(HRCA)/D002(OcularSurface) portal author annotation recomputation (via kb/baselines v1.1 adult-only master file) + priors v1 empirical intervals + ingested literature original sentences; Entire process did not use in-house clustering/in-house demo annotations (anti-circularity clause)
- Interval Mechanical Rule (Pre-registered): low=floor(min(donor_iqr_low, priors_expected_low, fold_lit_low)); high=ceil(max(donor_iqr_high, priors_expected_high, fold_lit_high)); mid=donor_median; No source row=null(no_evidence)
- Scope: {"species": "human", "organism_stage": "adult_only", "disease_states": "Not built (PDR annotation unreliable scope maintained; diseased materials must not be validated against healthy surface, Astra T2 usage_scope)", "fetal_organoid_developing": "Numerical folding excluded; exclusion reasons explicitly marked in citation records (32946783 organoid sentence/39117640 developing/36645183 fetal)", "tissues_out_of_v0": "Other tissues left for v1"}

## 1.1 Page: retina_normal_adult_human
- Registry Anchor: OA-D001 (HCA-HRCA-v1.0), PMID 41578023, path <STORE>/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad
- Donor-level Master File: kb/baselines/retina.json adult-only master file (97 donors)

| Cell Type | Low % | Mid % | High % | Evidence | B Status | Row-wise PMID | Donor-level Measured (median/iqr/range) |
|---|---|---|---|---|---|---|---|
| Rod (Rod Photoreceptor) | 22 | 48.9 | 58 | A_registry_recompute+B_literature | B | 37388908, 38012720, 41578023 | 48.85 / [22.06, 57.56] / [0.0, 77.97] |
| Cone (Cone Photoreceptor) | 1 | 3.3 | 7 | A_registry_recompute+B_literature | B | 32555229, 37388908, 41578023 | 3.27 / [2.3, 5.21] / [0.0, 13.1] |
| BC (Bipolar Cell) | 12 | 20.0 | 33 | A_registry_recompute+B_literature | B | 37388908, 41578023 | 19.99 / [15.21, 26.98] / [0.13, 49.97] |
| AC (Amacrine Cell) | 6 | 8.5 | 28 | A_registry_recompute+B_literature | B | 37388908, 41578023 | 8.46 / [6.55, 10.96] / [3.59, 70.83] |
| HC (Horizontal Cell) | 1 | 2.8 | 8 | A_registry_recompute+B_literature | B | 37388908, 41578023 | 2.78 / [1.38, 4.47] / [0.0, 13.25] |
| RGC (Retinal Ganglion Cell) | 0 | 3.2 | 15 | A_registry_recompute+B_literature | B | 37388908, 38012720, 41578023 | 3.23 / [0.88, 8.7] / [0.0, 92.41] |
| MG (Müller Glia) | 3 | 8.8 | 12 | A_registry_recompute+B_literature | B | 32069977, 41578023 | 8.75 / [5.28, 11.48] / [0.0, 24.66] |
| Astro (Astrocyte) | 0 | 0.4 | 2 | A_registry_recompute+B_literature | B | 32555229, 41578023 | 0.37 / [0.05, 0.9] / [0.0, 5.38] |
| Micro (Microglia) | 0 | 0.1 | 1 | A_registry_recompute+B_literature | B | 37017569, 41578023 | 0.14 / [0.0, 0.22] / [0.0, 1.22] |
| RPE (Retinal Pigment Epithelium) | 0 | 0.0 | 1 | A_registry_recompute+B_literature | B | 32946783, 41578023 | 0.0 / [0.0, 0.0] / [0.0, 2.03] |
| Endo_vascular (Vascular Endothelial (off-panel)) | null | null | null | no_evidence | B | 41578023 | – |
| Pericyte_vascular (Pericyte (off-panel)) | null | null | null | no_evidence | B | 41578023 | – |

### Row-wise Literature Anchors (On-disk ingested literature original sentences, B-level locatable)
- **Rod**
  - PMID 38012720 [fold] “the distributions of cell type proportions ... ranging from 2.5% RGC to 55.2% Rod” — snRNA+snATAC multi-omics cross-sample composition extremes (human, adult)
  - PMID 37388908 [identity] “the highest overlap (63.9%) is observed for the most abundant cell type, Rod” — Human snRNA-seq atlas: Rod is the most abundant cell type (qualitative)
  - PMID 41578023 [identity] (Bibliographic record anchor, no verbatim sentence) — HRCA integrated atlas majorclass includes Rod (registry ledger OA-D001)
- **Cone**
  - PMID 37388908 [context] “S cones (0.07% of total retinal cells)” — S-cone subtype scope, not folded; supports overall existence of Cone
  - PMID 32555229 [identity] (Bibliographic record anchor, no verbatim sentence) — Human fovea/peripheral retina cell atlas includes cone cells
  - PMID 41578023 [identity] (Bibliographic record anchor, no verbatim sentence) — HRCA majorclass includes Cone
- **BC**
  - PMID 37388908 [fold] “AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset” — Human snRNA-seq bipolar cell proportion at this dataset level (fold high)
  - PMID 41578023 [identity] (Bibliographic record anchor, no verbatim sentence) — HRCA majorclass includes BC
- **AC**
  - PMID 37388908 [fold] “AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset” — Same dataset level AC proportion (fold high)
  - PMID 37388908 [context] “vGlut3 excitatory ACs (0.7% of total retinal cells)” — Excitatory AC subtype scope, not folded
  - PMID 41578023 [identity] (Bibliographic record anchor, no verbatim sentence) — HRCA majorclass includes AC
- **HC**
  - PMID 37388908 [identity] “lowest overlap is observed for HC (49.0%)” — Human atlas includes horizontal cells (qualitative)
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA majorclass includes HC
- **RGC**
  - PMID 37388908 [context] “the total number of RGCs only accounts for approximately 1% of the cell population in the retina” — Histological theoretical estimate basis, not folded; directional anchor
  - PMID 37388908 [fold] “AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset” — Human dataset capture layer RGC proportion (fold high)
  - PMID 38012720 [fold] “ranging from 2.5% RGC to 55.2% Rod” — Cross-sample RGC lower bound extreme value (fold low)
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA majorclass includes RGC
- **MG**
  - PMID 32069977 [identity] “Within the fovea, Müller cells and horizontal cells ...” — Human fovea AIR atlas confirms presence of Müller cells (qualitative)
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA majorclass includes MG
- **Astro**
  - PMID 32555229 [context] “depletion of astrocytes from fovea (0.9% of all non-neuronal cells in fovea and 12% in periphery)” — Denominator = non-neuronal cells, different basis, not folded; regional difference directional anchor
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA majorclass includes Astro
- **Micro**
  - PMID 37017569 [context] “microglia (11 cells, 0.0146% of total cell count) directly mapped to the chromatin landscape” — scATAC direct mapping subset basis, not folded; rarity directional anchor
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA majorclass includes Microglia
- **RPE**
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA neural retina majorclass includes RPE (capture 0.03%)
  - PMID 32946783 [context] “pigment epithelial cells had 2% RPE65 (expression in organoids)” — Organoid expression basis involving organoids, not folded nor included in surface; registration exclusion only
- **Endo_vascular**
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — HRCA 10-class lexical surface does not include vascular class; true whole retina contains low-proportion vascular components, appearance of small clusters is normal (baselines/retina.json caveat)
- **Pericyte_vascular**
  - PMID 41578023 [identity] (bibliographic anchor, no verbatim sentence) — Same caveat: appearance of vascular mural components does not trigger contamination flag

## 1.2 Page: ocular_surface_normal_adult_human
- registry anchor: OA-D002 (CELLxGENE-OcularSurface), path <STORE>/data/D002_ocularsurface/D002_allcells_578K.h5ad
- Donor-level master file: kb/baselines/ocular_surface.json adult-only master file (41 donors/67 units); super-class regional mixed basis prohibited for cross-region application

| Cell Type | Low % | Mid % | High % | Evidence | B Status | Row-wise PMID | Donor-level Measured (median/iqr/range) |
|---|---|---|---|---|---|---|---|
| Corneal Endothelium (Corneal Endothelium) | 0 | 0.0 | 1 | A_registry_recompute+B_literature | B | 33865984, 34381080 | 0.0 / [0.0, 0.0] / [0.0, 100.0] |
| Endothelium (Endothelium) | 0 | 3.4 | 9 | A_registry_recompute+B_literature | B | 34381080 | 3.42 / [0.0, 8.99] / [0.0, 43.48] |
| Epithelium (Epithelium) | 7 | 50.5 | 71 | A_registry_recompute+B_literature | B | 32502616, 34381080, 34741068 | 50.48 / [7.26, 70.25] / [0.0, 99.62] |
| Fibroblasts (Fibroblasts) | 12 | 28.5 | 45 | A_registry_recompute+B_literature | B | 34381080, 34741068, 40838019 | 28.53 / [12.65, 44.01] / [0.0, 93.77] |
| Immune Cells (Immune Cells) | 0 | 1.1 | 3 | A_registry_recompute+B_literature | B | 34381080, 41552884 | 1.12 / [0.4, 2.6] / [0.0, 37.71] |
| Melanocytes (Melanocytes) | 0 | 0.3 | 3 | A_registry_recompute+B_literature | B | 34381080, 40216818 | 0.29 / [0.0, 2.45] / [0.0, 48.63] |
| Pericytes (Pericytes) | 0 | 2.0 | 5 | A_registry_recompute | B_missing | — | 2.03 / [0.0, 4.27] / [0.0, 41.31] |
| Schwann Cells (Schwann Cells) | 0 | 0.2 | 2 | A_registry_recompute+B_context_only | B_context_only | 40649793 | 0.23 / [0.0, 1.06] / [0.0, 20.52] |
| Smooth Muscle Cells (Smooth Muscle Cells) | 0 | 0.0 | 1 | A_registry_recompute+B_context_only | B_context_only | 40649793 | 0.0 / [0.0, 0.0] / [0.0, 63.33] |
| Conjunctival_epithelium(sub) (Conjunctival epithelium (D002 internal subclass)) | null | null | null | no_evidence | B | 32502616 | – |
| Goblet_cell (Goblet cell) | null | null | null | no_evidence | B_missing | — | – |

### Row-wise Literature Anchors (On-disk ingested literature original sentences, B-level locatable)
- **Corneal Endothelium**
  - PMID 33865984 [context] “endothelial cells in humans are not endogenously renewed ... density declines at an average of approximately 0.6% per year” — Cell density basis (cell/mm^2), not composition percentage, not folded; CEC identity/rarity anchor
  - PMID 34381080 [identity] (bibliographic anchor, no verbatim sentence) — Corneal single-cell catalog includes corneal endothelial cells (CenC)
- **Endothelium**
  - PMID 34381080 [identity] (bibliographic anchor, no verbatim sentence) — Corneal single-cell catalog includes vascular endothelial cells
- **Epithelium**
  - PMID 34381080 [identity] “These 16 clusters correspond to 11 subtypes of epithelial cells, keratocytes, Langerhans cells, melanocytes, vascular endothelial cells and corneal endothelial cells” — Adult human corneal single-cell catalog: epithelium as major class (qualitative)
  - PMID 34741068 [identity] “The cornea is composed of five layers: its outer surface is a stratified sheet of corneal epithelial cells” — Human corneal layered structure (qualitative)
  - PMID 32502616 [identity] (bibliographic anchor, no verbatim sentence) — Adult conjunctiva/limbus/corneal epithelium scRNA included
- **Fibroblasts**
  - PMID 34381080 [fold] “Over 15% of cells in our analysis are keratocytes within a single cluster” — Adult corneal scRNA: keratocyte single cluster >15% (fold low)
  - PMID 40838019 [identity] “The corneal stroma, composed mainly of keratocytes” — Main resident cell of corneal stroma is keratocyte (qualitative)
  - PMID 34741068 [identity] “The keratocytes populate the corneal stroma” — Qualitative
- **Immune Cells**
  - PMID 34381080 [identity] (bibliographic anchor, no verbatim sentence) — Corneal single-cell catalog includes Langerhans cells (immune)
  - PMID 41552884 [identity] (bibliographic anchor, no verbatim sentence) — Corneal macrophage review (emphasis on human evidence)
- **Melanocytes**
  - PMID 34381080 [identity] (bibliographic anchor, no verbatim sentence) — Corneal single-cell catalog includes melanocytes
  - PMID 40216818 [identity] “PAX3 expression in LM as well in the conjunctival melanocytes” — Presence of limbal/conjunctival melanocytes (qualitative)
- **Pericytes**
  - PMID D002-PORTAL-ONLY [identity] (bibliographic anchor, no verbatim sentence) — No literature sentence on adult ocular surface pericyte composition on disk; identity based solely on D002 official annotation (Grade A) — Grade B missing items registered truthfully
- **Schwann Cells**
  - PMID 40649793 [context] “NGF ... corneal nerve regeneration” — Ocular surface nerve review (qualitative), Schwann composition % not pinned down
- **Smooth Muscle Cells**
  - PMID 40649793 [context] “NGF has been found to be produced by ... smooth muscle cells” — Review mentions presence of ocular surface SMC (qualitative)
- **Conjunctival_epithelium(sub)**
  - PMID 32502616 [identity] (bibliographic anchor, no verbatim sentence) — Adult conjunctival epithelium scRNA; D002 has no independent super class (portal label assigned to Epithelium)

## 2. PMID Bibliographic Triple-Criteria Self-Check
- Criteria: j1=bibliographic record parseable in v2.4.2 papers.jsonl (three bibliographic elements non-empty); j2=not ghost (n_chunks>0); j3=traceable in database (vk page ∨ sidecar ∨ papers.jsonl); Total PMIDs 15, ledger non-compliant rows 0
- Itemized details in `ledgers/PROVENANCE_COMP_v0.tsv`

## 3. Known Limitations and Caveats
- RGC/neuron proportions are influenced by nuclear sorting and library design (NeuN±, RGC enrichment) — check library strategy before flagging anomalies (inherits baselines caveat)
- snRNA (nucleus) and scRNA (cell) class proportions cannot be directly compared (Astra T2)
- Ocular surface Immune pool is only 1.7%: inherent immune cells on the ocular surface are sparse; immune proportions cannot be benchmarked against inflammatory samples
- Corneal Endothelium main file median 0%: For pure CEC material (fragment layer), denominator=100%, this row does not apply
- Goblet/conjunctiva detail rows = dual absence of data and literature, marked as no_evidence
- PAPER 41578023 (HRCA) n_chunks=1 (incremental ingestion, not full chunking) — j2 barely passes, content anchors do not rely on it
- Rows missing per-line PMID (obligation OB-1 prior to activation): ocular_surface_normal_adult_human:Pericytes, ocular_surface_normal_adult_human:Goblet_cell
- Rows missing per-line PMID for activation obligation OB-1 (D002 portal identity, no composition literature sentences on disk): see rows_missing_pmid — must supplement literature or maintain OFF prior to activation
- Activation obligation OB-2: Ocular surface = regional mixed super-class (D002 scope); upon activation wiring, stratify intervals by tissue_group or route by region (category_note prohibits cross-region application)
- Activation obligation OB-3 reverse quality control triggered (Q1/Q2/Q3 healthy set flag rate >20%, see COMP_SELFFLAG_20260928.md §3): v0 intervals are too narrow for cross-platform/cross-sampling region/sorting designs, a known limitation on the face side — must stratify/exempt via rules and obtain PI adjudication prior to activation
- Disease-state proportions not built (PDR annotation unreliable scope maintained); developmental axis (fetal/organoid) values folded out, citation records retained.
- 'INTAKE ledger 392 entries' executed per task specification original text, incorporated into 'on-disk ingested RAG literature (papers.jsonl v2.4.2) metadata verifiable' scope (deviation statement: no literature ledger file named INTAKE with exactly 392 entries found on disk; methods-scrna index page has exactly 392 papers, included as one of the verifiable sets).

## 4. Self-check and Activation
- Self-check flag report: `COMP_SELFFLAG_20260928.md` (outputs only flag list and proportion distribution, no erroneous annotation conclusions).
- This face defaults OFF; wiring it into the interpretation layer (unexpected flagger) is a separate-card, separate-batch item.