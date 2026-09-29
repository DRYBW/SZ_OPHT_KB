# 注释证据报告（EyeKB pipeline 阶段 B 输出）

- 生成时间：2026-09-29 20:52:14
- 输入：`docs/plans/pipeline_pub_20260929/out/smoke_ensgmap/stage_a/processed.h5ad`（物种 human，组织 fibrovascular_membrane，疾病先验启用）
- MCP 调用：47 次，错误 0 次
- **阅读须知**：本报告只呈现证据与机械 QC 旗，不含注释结论；每簇的最终命名由研究者在 decisions_template.csv 填写 accept / modify / abstain。弃权是合法输出。

- 红线：默认路径零 LLM；本文件由本地五工具机械检索生成
- 红线：置信度分级是预注册机械 QC 旗（规则触发原因逐条可查），不是注释结论
- 红线：弃权(needs_review)/复核(mixed_or_insufficient) 是合法输出；禁止把 QC 旗当确定标签
- 红线：全部证据（marker 命中/基线区间/疾病先验提及/文献片段）带出处，供人工裁决

## 簇 0（359 细胞，占 19.736%）
- 置信度分级（机械 QC 旗）：**mixed_or_insufficient**
  - 触发规则: weak_marker_match: top1 共享基因数 <=1, candidate_tie: top1/top2 共享基因数并列
- top 基因: MT-ND6, FN1, BRI3, MTATP6P1, MT-ND4L, MARCO, S100A11, FBP1, MT-RNR2, RNASE1
- query_marker 候选: Fibroblast (n_shared=1, FN1); Myofibroblast (n_shared=1, FN1)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 1 条
- 文献片段（top3，逐条带 PMID）:
  - [Fibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Fibroblast] PMID 40402520 (Investigative ophthalmology & visual science 2025): The transcriptomic profiling of scleral fibroblasts remains largely unexplored. To elucidate their heterogeneity, we performed single-cell R…
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
- 分组构成（%细胞）: {'RRD_control': 100.0, 'PDR': 0.0}

## 簇 1（306 细胞，占 16.822%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: MT-RNR2, MT-RNR1, MT-ND4L, RPL10P9, SH3BGRL3, S100A11, FCER1G, EMP3, BHLHE41, TYROBP
- query_marker 候选: Microglia (n_shared=2, FCER1G,TYROBP)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [Microglia] PMID 37550343 (Scientific reports 2023): To establish which cellular components are associated with formation of PDR fibrovascular membranes, we downloaded the  GSE165784  sequencin…
  - [Microglia] PMID 40858363 (Genome research 2025): We selected the clusters with the highest module score for microglia and regenerated the cell embeddings and UMAP plot. We then run unsuperv…
- 分组构成（%细胞）: {'RRD_control': 100.0, 'PDR': 0.0}

## 簇 2（92 细胞，占 5.058%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: H2AFZ, HMGB1, STMN1, MKI67, HMGN2, NUSAP1, PTMA, HMGB2, PTTG1, BIRC5
- query_marker 候选: Proliferating (n_shared=6, H2AFZ,STMN1,MKI67,NUSAP1)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 1 条
- 文献片段（top3，逐条带 PMID）:
  - [Proliferating] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Proliferating] PMID 39422453 (eLife 2024): Raw reads were aligned to mm10 reference genome by STAR and summarized to gene counts. After transcripts Per Kilobase Million (TPM) normaliz…
- 分组构成（%细胞）: {'RRD_control': 78.26, 'PDR': 21.74}

## 簇 3（253 细胞，占 13.909%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: C3, RGS1, CD74, HLA-DPA1, HLA-DRA, HLA-DPB1, HLA-DRB1, HLA-DQA1, HLA-DRB6, RNASET2
- query_marker 候选: APC_MHCII_high (n_shared=7, RGS1,CD74,HLA-DPA1,HLA-DRA); cDC2 (n_shared=1, HLA-DRA)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [APC_MHCII_high] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
  - [APC_MHCII_high] PMID 33173609 (Translational vision science & technology 2020): The RNA from dissected cells was then amplified and used to generate cDNA libraries using the Smart-seq2 protocol. After RNA sequencing usin…
  - [cDC2] PMID 41684508 (Ophthalmology science 2026): Raw sequencing data were processed using Cell Ranger v8.0.1 (10x Genomics) for demultiplexing, alignment to the human reference genome (GRCh…
  - [cDC2] PMID 41057298 (Cell death & disease 2025): Raw single-cell RNA sequencing (scRNA-seq) data from the Illumina NextSeq 500 underwent initial quality assessment using Illumina Sequencing…
- 分组构成（%细胞）: {'PDR': 79.45, 'RRD_control': 20.55}

## 簇 4（182 细胞，占 10.005%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: CTSB, HMOX1, CTSD, APOE, FTL, CTSL, GLUL, LIPA, GAPDH, CTSZ
- query_marker 候选: Mac_DAM_LAM (n_shared=5, HMOX1,CTSD,APOE,FTL); MG (n_shared=1, GLUL); retina_interneuron::MG (n_shared=1, GLUL)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [Mac_DAM_LAM] PMID 39574940 (Research (Washington, D.C.) 2024): In our dataset, 107,718 single cells were filtered and grouped into 29 clusters. The clusters were annotated using known marker genes (Table…
  - [Mac_DAM_LAM] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
  - [MG] PMID 41636427 (Investigative ophthalmology & visual science 2026): To confirm the endogenous identity of the TM and SCE cell strains used, an inclusive list of cell-type marker genes taken from the single-ce…
  - [MG] PMID 37441592 (Theranostics 2023): To gain insight into the angiogenic regulation mediated by microglia, we analysed the single-cell RNA sequencing dataset  GSE150871 , which …
  - [retina_interneuron::MG] PMID 38278154 (Stem cell reports 2024): (G) Feature plot of Gap43 transcripts in the UMAP of integrated Seurat objects. Scale bar: 50 μm; bar graph (n ≥ 4 animals) with SEM error b…
  - [retina_interneuron::MG] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
- 分组构成（%细胞）: {'PDR': 97.8, 'RRD_control': 2.2}

## 簇 5（21 细胞，占 1.154%）
- 置信度分级（机械 QC 旗）：**mixed_or_insufficient**
  - 触发规则: weak_marker_match: top1 共享基因数 <=1, candidate_tie: top1/top2 共享基因数并列
- top 基因: RPL21, CST7, RPS15, RPS19, IL7R, MT-ND4L, RPL32, S100B, RPS8, CDC42
- query_marker 候选: MG (n_shared=1, S100B); Astro (n_shared=1, S100B); T (n_shared=1, IL7R)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [MG] PMID 41636427 (Investigative ophthalmology & visual science 2026): To confirm the endogenous identity of the TM and SCE cell strains used, an inclusive list of cell-type marker genes taken from the single-ce…
  - [MG] PMID 37441592 (Theranostics 2023): To gain insight into the angiogenic regulation mediated by microglia, we analysed the single-cell RNA sequencing dataset  GSE150871 , which …
  - [Astro] PMID 33627831 (Communications biology 2021): Mixed primary cultures of glia cells from the optic nerve of WT and Nuc1 rats were prepared as described previously 81 . Single-cell RNA seq…
  - [Astro] PMID 39574940 (Research (Washington, D.C.) 2024): In our dataset, 107,718 single cells were filtered and grouped into 29 clusters. The clusters were annotated using known marker genes (Table…
  - [T] PMID 32231223 (Nature communications 2020): Sixty-day hPSC-RPE cells were dissociated using TrypLE Select and passed through a cell strainer (ø 40 μm, BD Biosciences). They were resusp…
  - [T] PMID 37156914 (Nature biotechnology 2023): Based on the combinatorial expression of canonical cell type markers in the mentioned Louvain clusters (resolution = 0.5), cells in the inte…
- 分组构成（%细胞）: {'RRD_control': 80.95, 'PDR': 19.05}

## 簇 6（64 细胞，占 3.518%）
- 置信度分级（机械 QC 旗）：**mixed_or_insufficient**
  - 触发规则: candidate_tie: top1/top2 共享基因数并列
- top 基因: IGFBP7, CRYAB, TPM1, CNN3, CTHRC1, SPARC, CCDC80, CALD1, RPS27L, SELENOM
- query_marker 候选: Pericyte (n_shared=2, IGFBP7,CALD1); Myofibroblast (n_shared=2, TPM1,CTHRC1); SMC (n_shared=1, CALD1)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 1 条
- 文献片段（top3，逐条带 PMID）:
  - [Pericyte] PMID 41230906 (Investigative ophthalmology & visual science 2025): scRNA-seq datasets from  GSE150703 28  and  GSE165784 34  were processed using Seurat (v5.1.0). 35   GSE150703  included two normoxia (NOR) …
  - [Pericyte] PMID 39952952 (Scientific data 2025): Pericyte | DCN, TAGLN, ACTA2, RGS5, PDGFRB, FLT1 | …
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
  - [SMC] PMID 41636427 (Investigative ophthalmology & visual science 2026): To confirm the endogenous identity of the TM and SCE cell strains used, an inclusive list of cell-type marker genes taken from the single-ce…
  - [SMC] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
- 分组构成（%细胞）: {'PDR': 50.0, 'RRD_control': 50.0}

## 簇 7（154 细胞，占 8.466%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: SELENOP, MRC1, FOLR2, STAB1, CD14, MAF, FCGRT, F13A1, ITM2B, SLC40A1
- query_marker 候选: Mac_Tissue (n_shared=8, SELENOP,MRC1,FOLR2,STAB1); Mono_Classical (n_shared=1, CD14); retina_interneuron::AC (n_shared=1, MAF)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [Mac_Tissue] PMID 39422453 (eLife 2024): Raw reads were aligned to mm10 reference genome by STAR and summarized to gene counts. After transcripts Per Kilobase Million (TPM) normaliz…
  - [Mac_Tissue] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
  - [retina_interneuron::AC] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
  - [retina_interneuron::AC] PMID 37156914 (Nature biotechnology 2023): Based on the combinatorial expression of canonical cell type markers in the mentioned Louvain clusters (resolution = 0.5), cells in the inte…
- 分组构成（%细胞）: {'PDR': 98.05, 'RRD_control': 1.95}

## 簇 8（50 细胞，占 2.749%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: CD52, TRAC, IL32, CD2, CD3D, TRBC2, RPS29, RPLP1, RPL23A, EEF1D
- query_marker 候选: T (n_shared=4, TRAC,CD2,CD3D,TRBC2)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [T] PMID 32231223 (Nature communications 2020): Sixty-day hPSC-RPE cells were dissociated using TrypLE Select and passed through a cell strainer (ø 40 μm, BD Biosciences). They were resusp…
  - [T] PMID 37156914 (Nature biotechnology 2023): Based on the combinatorial expression of canonical cell type markers in the mentioned Louvain clusters (resolution = 0.5), cells in the inte…
- 分组构成（%细胞）: {'PDR': 88.0, 'RRD_control': 12.0}

## 簇 9（128 细胞，占 7.037%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: LYZ, RPL30, RPL23A, CD52, ACTB, PABPC1, FCN1, RPS29, ARPC3, COTL1
- query_marker 候选: Mono_Classical (n_shared=2, LYZ,FCN1)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [Mono_Classical] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Mono_Classical] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
- 分组构成（%细胞）: {'PDR': 99.22, 'RRD_control': 0.78}

## 簇 10（148 细胞，占 8.136%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: CTSD, LGMN, GLUL, FUCA1, FTL, CREG1, GRN, SDCBP, CTSZ, PLD3
- query_marker 候选: Mac_DAM_LAM (n_shared=4, CTSD,LGMN,FTL,PLD3); MG (n_shared=1, GLUL); retina_interneuron::MG (n_shared=1, GLUL)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [Mac_DAM_LAM] PMID 39574940 (Research (Washington, D.C.) 2024): In our dataset, 107,718 single cells were filtered and grouped into 29 clusters. The clusters were annotated using known marker genes (Table…
  - [Mac_DAM_LAM] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
  - [MG] PMID 41636427 (Investigative ophthalmology & visual science 2026): To confirm the endogenous identity of the TM and SCE cell strains used, an inclusive list of cell-type marker genes taken from the single-ce…
  - [MG] PMID 37441592 (Theranostics 2023): To gain insight into the angiogenic regulation mediated by microglia, we analysed the single-cell RNA sequencing dataset  GSE150871 , which …
  - [retina_interneuron::MG] PMID 38278154 (Stem cell reports 2024): (G) Feature plot of Gap43 transcripts in the UMAP of integrated Seurat objects. Scale bar: 50 μm; bar graph (n ≥ 4 animals) with SEM error b…
  - [retina_interneuron::MG] PMID 34946963 (Genes 2021): Keywords:  retinal ganglion cells, transcriptome, single cell sequencing, iPSC-RGCs, iPSCs, RGC subtypes, FACS analysis, marker genes, clust…
- 分组构成（%细胞）: {'PDR': 100.0, 'RRD_control': 0.0}

## 簇 11（32 细胞，占 1.759%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: GNG11, CRIP2, VWF, TM4SF1, ITM2A, FKBP1A, TCIM, IGFBP7, SPARC, SPARCL1
- query_marker 候选: Endo (n_shared=3, GNG11,VWF,TM4SF1); Pericyte (n_shared=1, IGFBP7)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 2 条
- 文献片段（top3，逐条带 PMID）:
  - [Endo] PMID 39332053 (Redox biology 2024): RNA-Seq datasets of corneal endothelial samples from 47 patients with FECD and 21 donor controls were obtained from publicly available datas…
  - [Endo] PMID 37443842 (Cells 2023): The marker genes used to identify corneal endothelial cells were only partially shared between studies. In the studies by Català et al., Lig…
  - [Pericyte] PMID 41230906 (Investigative ophthalmology & visual science 2025): scRNA-seq datasets from  GSE150703 28  and  GSE165784 34  were processed using Seurat (v5.1.0). 35   GSE150703  included two normoxia (NOR) …
  - [Pericyte] PMID 39952952 (Scientific data 2025): Pericyte | DCN, TAGLN, ACTA2, RGS5, PDGFRB, FLT1 | …
- 分组构成（%细胞）: {'PDR': 100.0, 'RRD_control': 0.0}

## 簇 12（22 细胞，占 1.209%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: RGS5, SEPT4, FRZB, CCDC102B, THY1, CALD1, IGFBP7, MYL9, TPM2, TAGLN
- query_marker 候选: Pericyte (n_shared=4, RGS5,THY1,CALD1,IGFBP7); SMC (n_shared=3, CALD1,MYL9,TAGLN); Myofibroblast (n_shared=3, MYL9,TPM2,TAGLN)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 1 条
- 文献片段（top3，逐条带 PMID）:
  - [Pericyte] PMID 41230906 (Investigative ophthalmology & visual science 2025): scRNA-seq datasets from  GSE150703 28  and  GSE165784 34  were processed using Seurat (v5.1.0). 35   GSE150703  included two normoxia (NOR) …
  - [Pericyte] PMID 39952952 (Scientific data 2025): Pericyte | DCN, TAGLN, ACTA2, RGS5, PDGFRB, FLT1 | …
  - [SMC] PMID 41636427 (Investigative ophthalmology & visual science 2026): To confirm the endogenous identity of the TM and SCE cell strains used, an inclusive list of cell-type marker genes taken from the single-ce…
  - [SMC] PMID 37443842 (Cells 2023): Single-cell RNA sequencing is a powerful tool to identify genes that drive cell identity at a single-cell resolution. Using this technology,…
  - [Myofibroblast] PMID 40576432 (Investigative ophthalmology & visual science 2025): Fibroblast Subpopulations | Marker Genes | Description…
  - [Myofibroblast] PMID 42652101 (Biomedicines 2026): Since the peak phenotypic changes of fibroblasts to myofibroblasts occurred at day 5 following treatment with TGFβ1, we performed RNA-seq on…
- 分组构成（%细胞）: {'PDR': 100.0, 'RRD_control': 0.0}

## 簇 13（8 细胞，占 0.44%）
- 置信度分级（机械 QC 旗）：**evidence_consistent**
  - 触发规则: marker_candidate+within_baseline+literature_present
- top 基因: GZMB, CLEC4C, PLAC8, IRF7, ITM2C, JCHAIN, IGKC, C12ORF75, IRF8, IL3RA
- query_marker 候选: pDC (n_shared=5, GZMB,CLEC4C,IRF7,JCHAIN); Microglia (n_shared=1, IRF8); cDC1 (n_shared=1, IRF8)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [pDC] PMID 37550343 (Scientific reports 2023): To establish which cellular components are associated with formation of PDR fibrovascular membranes, we downloaded the  GSE165784  sequencin…
  - [pDC] PMID 41254671 (Journal of translational medicine 2025): The datasets  GSE102485 ,  GSE160306 ,  GSE165784 ,  GSE245561 ,  GSE135922 , and  GSE178121  from the GEO database were downloaded ( https:…
  - [Microglia] PMID 37550343 (Scientific reports 2023): To establish which cellular components are associated with formation of PDR fibrovascular membranes, we downloaded the  GSE165784  sequencin…
  - [Microglia] PMID 40858363 (Genome research 2025): We selected the clusters with the highest module score for microglia and regenerated the cell embeddings and UMAP plot. We then run unsuperv…
  - [cDC1] PMID 39574940 (Research (Washington, D.C.) 2024): In our dataset, 107,718 single cells were filtered and grouped into 29 clusters. The clusters were annotated using known marker genes (Table…
  - [cDC1] PMID 41057298 (Cell death & disease 2025): Raw single-cell RNA sequencing (scRNA-seq) data from the Illumina NextSeq 500 underwent initial quality assessment using Illumina Sequencing…
- 分组构成（%细胞）: {'PDR': 100.0, 'RRD_control': 0.0}

---
*本报告由 EyeKB 仓内 `pipeline/` 生成；服务红线：证据只作人工判读与 QC 旗，禁止接进任何打分/加权/排序。*