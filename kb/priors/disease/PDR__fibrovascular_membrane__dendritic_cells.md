# Disease knowledge page: dendritic cell subsets in the PDR fibrovascular membrane (human)

> schema: `eyekb-disease-prior/1.0` | entry_id: `PDR__fibrovascular_membrane__dendritic_cells` | frozen: 2026-10-21
> Tissue scope: **fibrovascular membrane** (proliferative diabetic retinopathy, surgical material) · Species: **human** · Stage: adult
> Marker library: `membrane` = `kb/markers/markers_membrane_v1.json` (v1-membrane-20260924)
> Companion JSON: `kb/priors/disease/PDR__fibrovascular_membrane__dendritic_cells.json`

## 1. Purpose

This page is the written description of the two conventional dendritic cell subsets that the
`membrane` marker library registers for proliferative-diabetic-retinopathy (PDR) fibrovascular
membrane: **cDC1** (conventional type 1 dendritic cell) and **cDC2** (conventional type 2 dendritic
cell). Both are entries in the membrane marker library, and both are part of the library's `immune`
panel (`kb/markers/markers_membrane_v1.json`, `panels.immune`). Until this page existed, the two
library entries were reachable in the knowledge base only through a generated evidence appendix;
this page is a human-written record that names their marker panels and carries their registered
paper trail.

Dendritic cell subsets are annotated here as part of the myeloid compartment of the membrane
specimen. A fibrovascular membrane is dominated by myeloid cells together with vascular and stromal
cells, and is near-void of neural retina; a dendritic cell call in this material therefore describes
an immune population in a fibrovascular/stromal context, not a retinal cell type.

## 2. Marker panels

The panels below are the identification panels recorded in the `membrane` marker library
(`kb/markers/markers_membrane_v1.json`, `markers` section). They are the genes a reader should use to
recognise each subset in a membrane scRNA-seq dataset.

| Subset | Entry id | Panel genes | n genes | Source |
|---|---|---|---|---|
| cDC1 (conventional type 1 dendritic cell) | `membrane::cDC1` | CLEC9A, XCR1, C1S, C1R, CADM1, ZBTB46, FLT3, IRF8 | 8 | `kb/markers/markers_membrane_v1.json` |
| cDC2 (conventional type 2 dendritic cell) | `membrane::cDC2` | CD1C, FCER1A, CLEC10A, CD4, HLA-DRA, S100A10 | 6 | `kb/markers/markers_membrane_v1.json` |

Core discriminators within the panels: cDC1 — CLEC9A, XCR1, ZBTB46, IRF8, FLT3 (the CLEC9A/XCR1 axis
is the defining cDC1 receptor pair, with the lineage-defining transcription factor ZBTB46 and the
IRF8/FLT3 developmental program); cDC2 — CD1C, FCER1A, CLEC10A, with CD4 and HLA-DRA marking the
antigen-presenting, MHC-II-high state. `S100A10` (cDC2) and `C1S`/`C1R`/`CADM1` (cDC1) complete the
library panels. Per-gene provenance (canonical / literature-context) is recorded in the library's
`provenance` block for each of these genes.

## 3. Registered citations — cDC1 (`membrane::cDC1`)

Every citation below is registered against the `membrane::cDC1` entry in
`kb/link_registry/LINK_REGISTRY_v1.jsonl`. The PMID, journal, year and the panel genes that the
paper's own text names are copied from that entry. 28 citations are registered; 10
of them have at least one panel gene in the paper's full text.

### 3.1 Citations whose paper text names at least one panel gene

| PMID | Journal | Year | Panel genes named in the paper's text | Evidence locator | Title |
|---|---|---|---|---|---|
| 38716077 | Upsala journal of medical sciences | 2024 | CADM1, CLEC9A, FLT3, IRF8, XCR1 | paragraph:5 @ Introduction > The DC3 and mregDC states | Exploring dendritic cell subtypes in cancer immunotherapy: unraveling the role of mature regulatory dendritic cells |
| 35784369 | Frontiers in immunology | 2022 | C1R, C1S | paragraph:7 @ Discussion > A Refined Map of Complement Expression in Retina, RPE and Choroid | — (no title recorded in registry) |
| 31840941 | Stem cells translational medicine | 2020 | C1R, C1S | paragraph:24 @ DISCUSSION | — (no title recorded in registry) |
| 35882847 | Nature communications | 2022 | C1R, C1S | paragraph:10 @ Results > Profiling of geographic atrophy-related expression patterns in RPE and RPE subpopulations | — (no title recorded in registry) |
| 36899910 | Cells | 2023 | C1R, C1S | paragraph:20 @ 3. Results > 3.5. Sub-RPE Deposition-Related Gene Expression Pattern Depends on Maturation State and Zinc Supplementation > 3.5.2. Genelist 02 | — (no title recorded in registry) |
| 36936905 | Frontiers in immunology | 2023 | C1R, C1S | paragraph:21 @ The cellular microenvironment as a site of origin of immune dysfunction and inflammation in ocular disease > Sorsby fundus dystrophy | — (no title recorded in registry) |
| 38722314 | eLife | 2024 | C1R, C1S | paragraph:6 @ Results > Biological aspects that correlated with the pigmentation of iPSC-RPE | — (no title recorded in registry) |
| 40060903 | iScience | 2025 | CLEC9A, XCR1 | paragraph:7 @ Results > The landscape of ocular immune cells in uveitis | — (no title recorded in registry) |
| 42149027 | Investigative ophthalmology & visual science | 2026 | CADM1 | paragraph:26 @ Results > Other Notable Proteins | The Human Lens Fiber Cytoskeletome Reveals Neuronal Signatures and the Presence of Chaperonins, Proteasome, Signaling, a |
| 35565057 | International journal of environmental research and public health | 2022 | IRF8 | paragraph:13 @ 3. Results > 3.2. Function Enrichment Analysis | — (no title recorded in registry) |

### 3.2 Citations registered at the label level (no panel gene in the paper's text)

These papers are registered against cDC1 by literature label; none of them states a panel gene in
its text, so they are the weaker part of the trail. They are listed for completeness so the entry's
registered citation set stays whole. Editor/author fields and the empty evidence locator are
reproduced as recorded.

| PMID | Journal | Year | Panel genes named in the paper's text | Evidence locator | Title |
|---|---|---|---|---|---|
| 37880369 | Nature | 2023 | — | — | An ON-type direction-selective ganglion cell in primate retina. |
| 35212809 | Cellular and molecular life sciences : CMLS | 2022 | — | — | CD73 controls ocular adenosine levels and protects retina from light-induced phototoxicity. |
| 37156914 | Nature biotechnology | 2023 | — | — | Multimodal spatiotemporal phenotyping of human retinal organoid development. |
| 37272764 | Investigative ophthalmology & visual science | 2023 | — | — | Sortilin Inhibition Protects Neurons From Degeneration in the Diabetic Retina. |
| 34006945 | Scientific reports | 2021 | — | — | In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying diabetic retinopathy. |
| 39196935 | Science advances | 2024 | — | — | Top-down modulation of the retinal code via histaminergic neurons of the hypothalamus. |
| 35167652 | Diabetes | 2022 | — | — | Müller Glial Expression of REDD1 Is Required for Retinal Neurodegeneration and Visual Dysfunction in Diabetic Mice. |
| 42018650 | JCI insight | 2026 | — | — | Spatial proteomic mapping of the human and mouse retina using IBEX. |
| 36261438 | Nature communications | 2022 | — | — | HBEGF-TNF induce a complex outer retinal pathology with photoreceptor cell extrusion in human organoids. |
| 40050124 | Genome research | 2025 | — | — | Integrating short-read and long-read single-cell RNA sequencing for comprehensive transcriptome profiling in mouse retin |
| 38334673 | Cells | 2024 | — | — | Recent Achievements in the Heterogeneity of Mammalian and Human Retinal Pigment Epithelium: In Search of a Stem Cell. |
| 40131296 | Investigative ophthalmology & visual science | 2025 | — | — | The Spatial Transcriptomic Atlas of Human Limbus and Vital Niche Microenvironment Regulating the Fate of Limbal Epitheli |
| 37022761 | The Journal of cell biology | 2023 | — | — | Homophilic interaction of cell adhesion molecule 3 coordinates retina neuroepithelial cell proliferation. |
| 42136961 | Human mutation | 2026 | — | — | Integrated Bulk and Single‐Cell Transcriptomic Analysis Reveals Xenobiotic Metabolism Genes Drive Progression From Liver |
| 39952952 | Scientific data | 2025 | — | — | Divergence in cellular markers observed in single-cell transcriptomics datasets between cultured primary trabecular mesh |
| 33307245 | Genomics, proteomics & bioinformatics | 2021 | — | — | Transcriptomic Profiling of Human Pluripotent Stem Cell-derived Retinal Pigment Epithelium over Time. |
| 32347797 | eLife | 2020 | — | — | OTX2 represses sister cell fate choices in the developing retina to promote photoreceptor specification. |
| 34946963 | Genes | 2021 | — | — | Single Cell Sequencing of Induced Pluripotent Stem Cell Derived Retinal Ganglion Cells (iPSC-RGC) Reveals Distinct Molec |

## 4. Registered citations — cDC2 (`membrane::cDC2`)

Same construction for the `membrane::cDC2` entry: 27 citations registered, 15 with
at least one panel gene in the paper's full text.

### 4.1 Citations whose paper text names at least one panel gene

| PMID | Journal | Year | Panel genes named in the paper's text | Evidence locator | Title |
|---|---|---|---|---|---|
| 38716077 | Upsala journal of medical sciences | 2024 | CD1C, CD4, CLEC10A, FCER1A | paragraph:3 @ Introduction > Dendritic cell subtypes | Exploring dendritic cell subtypes in cancer immunotherapy: unraveling the role of mature regulatory dendritic cells |
| 37917183 | JCI insight | 2023 | CD1C, CD4, CLEC10A, FCER1A | paragraph:10 @ Results > Immune cells in the fibrovascular membranes express proangiogenic genes. | — (no title recorded in registry) |
| 42021381 | Biology direct | 2026 | CD1C, CD4, CLEC10A | abstract:1 @ Abstract | Single-cell analysis highlights the role of CD4 +  IFN-I-related T cells in Behcet’s uveitis during Interferonα-2a thera |
| 42059276 | Journal of diabetes research | 2026 | CD1C, CD4, FCER1A | abstract:1 @ 3. Results > 3.5. The Association Between Three Differential Immune Cells and Two Biomarkers | Exploring Vitamin D Signaling‐Associated Biomarkers and Their Diagnostic Value in Diabetic Retinopathy: A Combined Trans |
| 40060903 | iScience | 2025 | CD4, CD1C, CLEC10A | paragraph:7 @ Discussion > The role of ocular antigen in uveitis | — (no title recorded in registry) |
| 39774261 | Genes and immunity | 2025 | CD4, HLA-DRA | paragraph:10 @ Results > Construction of the developmental trajectory of monocytes under pathologic states on the basis of scRNA-seq | Immune pathogenic response landscape of acute posterior multifocal placoid pigment epitheliopathy revealed by scRNA sequ |
| 39220810 | Ophthalmology science | 2024 | CD4, HLA-DRA | abstract:1 @ Abstract | — (no title recorded in registry) |
| 41684508 | Ophthalmology science | 2026 | HLA-DRA, S100A10 | paragraph:25 @ Results > Comprehensive Profiling of Aging Retina Uncovers Cell-Type-Specific Differentially Expressed Genes and Shared Hallmarks | — (no title recorded in registry) |
| 35280984 | Frontiers in immunology | 2022 | CD4, HLA-DRA | paragraph:12 @ Discussion | — (no title recorded in registry) |
| 39466230 | Investigative ophthalmology & visual science | 2024 | CD4, HLA-DRA | paragraph:15 @ Results > Characterization of Immune Cell Clusters in Mouse Leptomeninges and Their Unique Transcriptomic Signatures | — (no title recorded in registry) |
| 41651377 | The ocular surface | 2026 | CD4, HLA-DRA | paragraph:14 @ Discussion | — (no title recorded in registry) |
| 40069725 | Journal of translational medicine | 2025 | CD1C, FCER1A | paragraph:20 @ Results > scRNA-seq data integration and clustering of fibrovascular membrane | — (no title recorded in registry) |
| 40131296 | Investigative ophthalmology & visual science | 2025 | CD4 | paragraph:29 @ Discussion | The Spatial Transcriptomic Atlas of Human Limbus and Vital Niche Microenvironment Regulating the Fate of Limbal Epitheli |
| 42136961 | Human mutation | 2026 | CD4 | paragraph:24 @ 3. Results > 3.5. Correlation of Hub Genes With Immune Cells | Integrated Bulk and Single‐Cell Transcriptomic Analysis Reveals Xenobiotic Metabolism Genes Drive Progression From Liver |
| 36277849 | Cell genomics | 2022 | HLA-DRA | paragraph:4 @ Results > Single-cell multiomics reveal the gene expression and chromatin accessibility landscapes of cell types in the human retina | Single-cell multiome of the human retina and deep learning nominate causal variants in complex eye diseases. |

### 4.2 Citations registered at the label level (no panel gene in the paper's text)

| PMID | Journal | Year | Panel genes named in the paper's text | Evidence locator | Title |
|---|---|---|---|---|---|
| 37880369 | Nature | 2023 | — | — | An ON-type direction-selective ganglion cell in primate retina. |
| 37156914 | Nature biotechnology | 2023 | — | — | Multimodal spatiotemporal phenotyping of human retinal organoid development. |
| 40050124 | Genome research | 2025 | — | — | Integrating short-read and long-read single-cell RNA sequencing for comprehensive transcriptome profiling in mouse retin |
| 35212809 | Cellular and molecular life sciences : CMLS | 2022 | — | — | CD73 controls ocular adenosine levels and protects retina from light-induced phototoxicity. |
| 34006945 | Scientific reports | 2021 | — | — | In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying diabetic retinopathy. |
| 37272764 | Investigative ophthalmology & visual science | 2023 | — | — | Sortilin Inhibition Protects Neurons From Degeneration in the Diabetic Retina. |
| 39196935 | Science advances | 2024 | — | — | Top-down modulation of the retinal code via histaminergic neurons of the hypothalamus. |
| 37388908 | Cell genomics | 2023 | — | — | A multi-omics atlas of the human retina at single-cell resolution. |
| 41632798 | PLoS genetics | 2026 | — | — | Rare heterozygous missense variants in  VSX2  are associated with retinal detachment |
| 36261438 | Nature communications | 2022 | — | — | HBEGF-TNF induce a complex outer retinal pathology with photoreceptor cell extrusion in human organoids. |
| 38334673 | Cells | 2024 | — | — | Recent Achievements in the Heterogeneity of Mammalian and Human Retinal Pigment Epithelium: In Search of a Stem Cell. |
| 41636427 | Investigative ophthalmology & visual science | 2026 | — | — | Time-Dependent Glucocorticoid-Induced Transcriptomic Changes in Human Trabecular Meshwork and Schlemm's Canal Cells |

## 5. How to read the citations

- **PMID, journal, year, genes named in the text, evidence locator** are copied unchanged from the
  registry row for the entry. Where the registry records an empty title or an empty evidence
  locator, that emptiness is preserved rather than filled in.
- **"Panel genes named in the paper's text"** is the intersection of the paper's own full text with
  the entry's panel. It is the checkable claim: the reader can open the paper and confirm the gene
  symbol is stated. A citation with no gene named is a label-level link only.
- The gene-anchored citations are the strong evidence for the panel. The label-level citations place
  the subset in the literature but do not by themselves support any specific panel gene.

## 6. Limits

1. Dendritic cell subsets are a small myeloid minority in a membrane specimen; a cDC1/cDC2 call
   should be supported by more than one panel gene and reported with its own denominator.
2. A high MHC-II signal alone (HLA-DRA and the broader antigen-presenting program) is not proof of
   dendritic cell identity; macrophages in the same material are also MHC-II high. The cDC1/cDC2
   panel genes above are what separates the subsets from the neighbouring macrophage/monocyte
   classes in the `membrane` library.
3. Several registered citations discuss dendritic cell biology in tissues other than the eye; where a
   citation is not ocular, it is reported as such through its journal and, where recorded, its
   evidence locator. No claim on this page asserts that a non-ocular paper studied the membrane.

## 7. Retrieval

- `query_marker(cell_type='cDC1', library='membrane')`
- `query_marker(cell_type='cDC2', library='membrane')`

## 8. Provenance

- Marker panels: `kb/markers/markers_membrane_v1.json` (v1-membrane-20260924), `markers` and `provenance` sections.
- Citations: `kb/link_registry/LINK_REGISTRY_v1.jsonl`, entries `membrane::cDC1` and
  `membrane::cDC2` (fields: pmid, title, journal, year, genes_in_text, evidence_locator).
- The .json twin of this page holds the same panels and the same citation objects in machine-readable
  form and is the source of this rendered text.
