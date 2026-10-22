# Annotation Evidence Report (EyeKB pipeline Stage B output)

- Generated at: 2026-10-22 13:38:32
- Input: `/home/ubuntu/EYEKB_REPO/docs/plans/activate_onfibro_20261022/out/g4_reanchor/on_run2/stage_a/processed.h5ad` (species human, tissue fibrovascular_membrane, disease prior not enabled (no grouping))
- MCP calls: 38 total, 0 errors
- **How to read**: this report presents evidence and mechanical QC flags only, with no annotation conclusions; the final naming of each cluster is filled in by the researcher in decisions_template.csv as accept / modify / abstain. Abstention is a legal output.

- Redline: zero LLM on the default path; this file is produced by local five-tool mechanical retrieval
- Redline: the confidence grade is a pre-registered mechanical QC flag (rule triggers individually auditable), not an annotation conclusion
- Redline: abstention (needs_review) / review (mixed_or_insufficient) are legal outputs; never treat a QC flag as a definite label
- Redline: all evidence (marker hits / baseline intervals / disease-prior mentions / literature snippets) carries provenance for human adjudication

## This-slot attention list (known-issues shadow: log flags only, do not alter readings; no free text in this segment)

- Judgment coordinates: species=`human`, tissue=`fibrovascular_membrane`(Source `manual`, override audit trail: s0_overridden_by_user）
- Applicable claims: 48 entries (blind-evaluation safe 44 / open after reading 4).This segment contains only structured flags (6.1sol conservative default: no free-text known-issues before blind review);Short rules and sources see `shadow_attention.json` (human-facing after reading),Automatic naming/downgrade change always = 0.

| claim_id | risk | source_type | blind_safe | re-review requirement |
|---|---|---|---|---|
| `KC-B1-003` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-004` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-007` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-009` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-010` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-014` | high | internal_observation | false | Manual re-review after reading (free-text post_decision) |
| `KC-B1-015` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-016` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-017` | medium | internal_observation | false | Manual re-review after reading (free-text post_decision) |
| `KC-B1-018` | medium | internal_observation | false | Manual re-review after reading (free-text post_decision) |
| `KC-B1-019` | medium | internal_observation | false | Manual re-review after reading (free-text post_decision) |
| `KC-B1-020` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-021` | low | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-022` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-023` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-024` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-028` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-041` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B1-049` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-001` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-002` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-003` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-004` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-005` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-006` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-007` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-008` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-009` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-010` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-011` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-012` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-013` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-014` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-015` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-016` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-017` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-018` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-019` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-020` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-021` | high | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-022` | medium | internal_observation | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-023` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-024` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-025` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-026` | low | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-027` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-028` | low | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |
| `KC-B2-029` | medium | peer_reviewed_literature | true | Optional re-review (general methodological short rules in machine-readable file) |

## Cluster 0 (43 cells, 9.598%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: candidate_tie: top1/top2 tied on shared-gene count
- top genes: IFI27, S100A8, TIMD4, CFD, NUPR1, C1QB, FTL, S100A9, GLRX, S100A4
- query_marker candidates: Mono_Classical (n_shared=2, S100A8,S100A9); Micro (n_shared=1, C1QB); Mac_Tissue (n_shared=1, C1QB)
- Composition check (baseline row human_pdr_membrane): flag=no_baseline_row
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
  - [Micro] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [Micro] PMID 37550343 (Scientific reports 2023): To establish which cellular components are associated with formation of PDR fibrovascular membranes, we downloaded the  GSE165784  sequencin…
  - [Mac_Tissue] PMID 39422453 (eLife 2024): Raw reads were aligned to mm10 reference genome by STAR and summarized to gene counts. After transcripts Per Kilobase Million (TPM) normaliz…
  - [Mac_Tissue] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…

## Cluster 1 (62 cells, 13.839%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: weak_marker_match: top1 shared-gene count <=1, candidate_tie: top1/top2 tied on shared-gene count
- top genes: FN1, FABP5, RNASE1, MMP9, NPC2, CXCL2, SH3BGRL3, APOC1, APOE, SPP1
- query_marker candidates: Fibroblast (n_shared=1, FN1); Myofibroblast (n_shared=1, FN1); onfibro_v13::Fibroblast (n_shared=1, FN1)
- Composition check (baseline row human_pdr_membrane): flag=range_not_estimated; observed 13.839% vs donor median None% (IQR None, range None)
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [Fibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Fibroblast] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
  - [onfibro_v13::Fibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [onfibro_v13::Fibroblast] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…

## Cluster 2 (31 cells, 6.92%)
- Confidence grade (mechanical QC flag): **needs_review**
  - Rules fired: no_named_marker_candidates, no_literature_results
- top genes: HMGB1, MKI67, H2AFZ, HMGN2, NUSAP1, BIRC5, STMN1, PTMA, HMGB2, TUBB
- query_marker candidates: no named candidates
- Composition check (baseline row human_pdr_membrane): flag=no_candidate
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [gene_query] PMID 35586662 (Eye and brain 2022): Abstract Introduction Diabetic patients routinely have high levels of high mobility group box 1 (HMGB1) protein in their plasma, vitreous an…
  - [gene_query] PMID 39117640 (Nature communications 2024): RGC | ATOH7, ISL1, PBX4, POU4F2 | EGR1 (AC, HC), ZIC1 (Rod) | E2F7, EBF2, EBF3, FOXM1, HES5, LEF1, MECOM, MXD3, MYBL1, PAX5, PBX3, POU6F2, S…

## Cluster 3 (41 cells, 9.152%)
- Confidence grade (mechanical QC flag): **evidence_consistent**
  - Rules fired: marker_candidate+within_baseline+literature_present
- top genes: HLA-DPB1, CD74, HLA-DRA, C3, HLA-DRB1, RGS1, HAMP, CST3, ALOX5AP, HLA-DPA1
- query_marker candidates: APC_MHCII_high (n_shared=6, HLA-DPB1,CD74,HLA-DRA,HLA-DRB1); cDC2 (n_shared=1, HLA-DRA)
- Composition check (baseline row human_pdr_membrane): flag=no_baseline_row
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [APC_MHCII_high] PMID 39774261 (Genes and immunity 2025): To provide a comprehensive atlas of human PBMCs in the APMPPE patient, we conducted single-cell RNA sequencing on PBMCs obtained from an APM…
  - [APC_MHCII_high] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [cDC2] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [cDC2] PMID 41684508 (Ophthalmology science 2026): Raw sequencing data were processed using Cell Ranger v8.0.1 (10x Genomics) for demultiplexing, alignment to the human reference genome (GRCh…

## Cluster 4 (12 cells, 2.679%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: candidate_tie: top1/top2 tied on shared-gene count
- top genes: IGFBP7, CFH, COL1A2, RPS27L, NNMT, CRYAB, S100A13, TPM1, VCAN, SELENOM
- query_marker candidates: Pericyte (n_shared=2, IGFBP7,COL1A2); Myofibroblast (n_shared=2, COL1A2,TPM1); Fibroblast (n_shared=1, COL1A2)
- Composition check (baseline row human_pdr_membrane): flag=range_not_estimated; observed 2.679% vs donor median None% (IQR None, range None)
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [Pericyte] PMID 39806101 (The EMBO journal 2025): Keywords:  Pericytes, Higd1b, Capillary, Pulmonary Hypertension, Single-cell RNA Sequence…
  - [Pericyte] PMID 41230906 (Investigative ophthalmology & visual science 2025): scRNA-seq datasets from  GSE150703 28  and  GSE165784 34  were processed using Seurat (v5.1.0). 35   GSE150703  included two normoxia (NOR) …
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
  - [Fibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Fibroblast] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…

## Cluster 5 (34 cells, 7.589%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: weak_marker_match: top1 shared-gene count <=1, candidate_tie: top1/top2 tied on shared-gene count
- top genes: EMP3, S100A10, EZR, S100A4, TIMP1, PTMA, LRRFIP1, FOS, SH3BGRL3, HSPB1
- query_marker candidates: Myofibroblast (n_shared=1, TIMP1); cDC2 (n_shared=1, S100A10); Granulocyte (n_shared=1, TIMP1)
- Composition check (baseline row human_pdr_membrane): flag=range_not_estimated; observed 7.589% vs donor median None% (IQR None, range None)
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
  - [cDC2] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [cDC2] PMID 41684508 (Ophthalmology science 2026): Raw sequencing data were processed using Cell Ranger v8.0.1 (10x Genomics) for demultiplexing, alignment to the human reference genome (GRCh…
  - [Granulocyte] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
  - [Granulocyte] PMID 39574940 (Research (Washington, D.C.) 2024): In our dataset, 107,718 single cells were filtered and grouped into 29 clusters. The clusters were annotated using known marker genes (Table…

## Cluster 6 (37 cells, 8.259%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: weak_marker_match: top1 shared-gene count <=1, candidate_tie: top1/top2 tied on shared-gene count
- top genes: MARCO, CXCL8, AIF1, RNASE1, S100A8, CXCL3, CXCL2, C1orf162, C1QA, FN1
- query_marker candidates: Fibroblast (n_shared=1, FN1); Myofibroblast (n_shared=1, FN1); Mono_Classical (n_shared=1, S100A8)
- Composition check (baseline row human_pdr_membrane): flag=range_not_estimated; observed 8.259% vs donor median None% (IQR None, range None)
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [Fibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Fibroblast] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…

## Cluster 7 (19 cells, 4.241%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: weak_marker_match: top1 shared-gene count <=1, candidate_tie: top1/top2 tied on shared-gene count
- top genes: RPLP0, IL7R, HLA-DRA, S100B, AIF1, CST7, HLA-DQA2, MT-RNR2, LYZ, CST3
- query_marker candidates: MG (n_shared=1, S100B); Astro (n_shared=1, S100B); Mono_Classical (n_shared=1, LYZ)
- Composition check (baseline row human_pdr_membrane): flag=no_baseline_row
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [MG] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [MG] PMID 41636427 (Investigative ophthalmology & visual science 2026): To confirm the endogenous identity of the TM and SCE cell strains used, an inclusive list of cell-type marker genes taken from the single-ce…
  - [Astro] PMID 33627831 (Communications biology 2021): Mixed primary cultures of glia cells from the optic nerve of WT and Nuc1 rats were prepared as described previously 81 . Single-cell RNA seq…
  - [Astro] PMID 39574940 (Research (Washington, D.C.) 2024): In our dataset, 107,718 single cells were filtered and grouped into 29 clusters. The clusters were annotated using known marker genes (Table…
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…

## Cluster 8 (36 cells, 8.036%)
- Confidence grade (mechanical QC flag): **mixed_or_insufficient**
  - Rules fired: weak_marker_match: top1 shared-gene count <=1
- top genes: MMP9, CHI3L1, CSTB, ANXA2, DBI, NUPR1, GPNMB, CTSS, CAPG, FTH1
- query_marker candidates: Mono_Classical (n_shared=1, CTSS)
- Composition check (baseline row human_pdr_membrane): flag=no_baseline_row
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…

## Cluster 9 (62 cells, 13.839%)
- Confidence grade (mechanical QC flag): **needs_review**
  - Rules fired: no_named_marker_candidates, no_literature_results
- top genes: CCL4, CCL4L2, CCL3L1, PLEK, CCL3, S100A11, EMP3, GADD45B, IER3, NFKBIZ
- query_marker candidates: no named candidates
- Composition check (baseline row human_pdr_membrane): flag=no_candidate
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [gene_query] PMID 36712326 (PNAS nexus 2022): A small cluster in the cornea (CL9, 426 cells) and the organoid (CL 15, 108 cells) expressed high levels of CC-motif chemokine ligands  CCL3…
  - [gene_query] PMID 42589173 (Biology 2026): Biochemical studies support TLR4 as a candidate receptor for selected extracellular S100A9-related molecular forms [ 28 ]. In an experimenta…

## Cluster 10 (71 cells, 15.848%)
- Confidence grade (mechanical QC flag): **evidence_consistent**
  - Rules fired: marker_candidate+within_baseline+literature_present
- top genes: MT-CO1, PSAP, ACTB, CD74, CTSS, CTSB, A2M, CTSZ, HLA-DRA, LIPA
- query_marker candidates: APC_MHCII_high (n_shared=2, CD74,HLA-DRA); Mono_Classical (n_shared=1, CTSS); cDC2 (n_shared=1, HLA-DRA)
- Composition check (baseline row human_pdr_membrane): flag=no_baseline_row
- Disease prior: no grouping column provided or only one group (--group-col); disease-prior comparison not enabled
- Literature snippets (top3, each with a PMID):
  - [APC_MHCII_high] PMID 39774261 (Genes and immunity 2025): To provide a comprehensive atlas of human PBMCs in the APMPPE patient, we conducted single-cell RNA sequencing on PBMCs obtained from an APM…
  - [APC_MHCII_high] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
  - [cDC2] PMID 40069725 (Journal of translational medicine 2025): Figure  1  illustrates the flowchart of this study. First, single-cell RNA sequencing data from fibrovascular membrane of five samples diagn…
  - [cDC2] PMID 41684508 (Ophthalmology science 2026): Raw sequencing data were processed using Cell Ranger v8.0.1 (10x Genomics) for demultiplexing, alignment to the human reference genome (GRCh…

---
*This report was generated by the in-repo `pipeline/` of EyeKB; service redline: evidence feeds human review and QC flags only — never wire it into any scoring/weighting/ranking.*