# RAGGAP — A 档报批清单（零下载盘点产物，勾了才动）

生成: 2026-09-27 | 口径: RAG v2.1（附属核查 v2.2/v2.3 去重）| 全部 **未下载未重建**

判据预注册: R1 库外引用链=R 必须补 / R2 EPMC 眼语境命中>5=可补 / R3 命中1-5=B 稀缺登记 / R4 命中0=B 真缺。

体积说明: EPMC fullTextXML 为 chunked 流式（HEAD 无 Content-Length、拒绝 Range），单篇体积**无法零下载实测**；
按经验上界 ≤0.5 MB/篇估算，**全清单 ≤ ~85 MB，>1GB 单独批条款不触发**；PI 批准执行时按所选管线复测。

## 汇总
- A 档缺口基因（去重 gene×组织语境）: **92**（retina 58 / membrane 21 / lacrimal 7 / face 3 / kb9 3）

- 候选一手论文去重: **167** 篇（其中 OA 全文 151 篇、摘要级 16 篇）

- 已被 v2.2/v2.3 增量吸收: **5** 篇（免补）

- **净需批 = 65 篇必补 + 104 篇备选**


## 必补（每基因保 1 篇覆盖 + KB 词条引用链在库外的 7 篇）

| 勾选 | PMID | 年份 | OA | 全文化语境 | 收益基因 | 标题(截断) | 备注 |
|---|---|---|---|---|---|---|---|
| ☐ | 16395610 | 2006 | N |  | 0 | Immunohistochemical analysis of secretoglobin SCGB 2A1 exp | 词条引用链(R1)  |
| ☐ | 26173177 | 2015 | N |  | 0 | Characterization of human reflex tear proteome reveals hig | 词条引用链(R1)  |
| ☐ | 34249897 | 2021 | Y |  | 0 | Sperm-Specific Glycolysis Enzyme Glyceraldehyde-3-Phosphat | 词条引用链(R1)  |
| ☐ | 37591874 | 2023 | Y |  | 0 | Cell-specific and shared regulatory elements control a mul | 词条引用链(R1)  |
| ⛔ | 41349939 | 2026 | N |  | 0 | Urinary exosomes: Emerging biomarkers for urinary tract infection | **不建议补——本条=词条误引**（retina_v6 microglia_repair LILRB2 链引的 PMID 经 EPMC 逐字复核为泌尿科论文；先修词条再谈补库，见报告 §6.4） |
| ☐ | 42191868 | 2026 | Y |  | 0 | Mapping galectin-3 ligands in human tear fluid establishes | 词条引用链(R1)  |
| ☐ | 42777860 | 2026-09-23 | N(新) |  | 0 | (EPMC MEDLINE 未收录；NCBI eutils 实证存在：Ocul Surf, Kamalasanan & Ahmed et al., 人泪液蛋白组种属特异) | 词条引用链(R1)——补录时须走 PubMed 源 |
| ☐ | 39317184 | 2024 | Y |  | 4 | The sodium-bicarbonate cotransporter Slc4a5 mediates feedb | 基因扫描(R2) ；覆盖基因:CMYA5(retina),GJA10(retina),NAT16(retina),SLC4A3(retina) |
| ☐ | 42021381 | 2026 | Y |  | 3 | Single-cell analysis highlights the role of CD4&lt;sup&gt; | 基因扫描(R2) ；覆盖基因:CLEC4C(membrane),KLRF1(membrane),LILRA4(membrane) |
| ☐ | 38045700 | 2023 | Y |  | 2 | PolySialic acid-nanoparticles inhibit macrophage mediated  | 基因扫描(R2) ；覆盖基因:SIGLEC11(membrane),SIGLEC11(retina) |
| ☐ | 41026912 | 2025 | N |  | 2 | The SLC-ome of membrane transport: From molecular discover | 基因扫描(R2) ；覆盖基因:SLC24A3(retina),SLC35F3(retina) |
| ☐ | 41953651 | 2026 | Y |  | 2 | Review: The role of microglia in diabetic retinopathy and  | 基因扫描(R2) ；覆盖基因:GPR34(membrane),GPR34(retina) |
| ☐ | 42059276 | 2026 | Y |  | 2 | Exploring Vitamin D Signaling-Associated Biomarkers and Th | 基因扫描(R2) ；覆盖基因:CLEC4C(membrane),KLRF1(membrane) |
| ☐ | 42173563 | 2026 | N |  | 2 | Principles of resident tissue macrophages revealed by the  | 基因扫描(R2) ；覆盖基因:CLEC10A(membrane),XCR1(membrane) |
| ☐ | 42346024 | 2026 | Y |  | 2 | SIRT4 Alleviates Retinal Ischemia-Reperfusion Injury Via M | 基因扫描(R2) ；覆盖基因:GPR34(membrane),GPR34(retina) |
| ☐ | 42365006 | 2026 | Y |  | 2 | NAD+ modulates mitochondrial vulnerability in MERTK-associ | 基因扫描(R2) ；覆盖基因:KHDRBS3(retina),RAPGEF5(retina) |
| ☐ | 42569310 | 2026 | Y |  | 2 | An exploratory exome-wide machine learning analysis identi | 基因扫描(R2) ；覆盖基因:CMYA5(retina),PIK3R5(retina) |
| ☐ | 42653219 | 2026 | Y |  | 2 | Non-Random Association of Ultraconserved Genomic Elements  | 基因扫描(R2) ；覆盖基因:SKAP1(membrane),SNTG1(retina) |
| ☐ | 32290826 | 2020 | Y |  | 1 | Identification of potential molecular targets associated w | 基因扫描(R2)  |
| ☐ | 33929509 | 2021 | N |  | 1 | Cis-regulatory dissection of cone development reveals a br | 基因扫描(R2)  |
| ☐ | 35721135 | 2022 | Y |  | 1 | Low-Dose Anti-HIV Drug Efavirenz Mitigates Retinal Vascula | 基因扫描(R2)  |
| ☐ | 36230967 | 2022 | Y |  | 1 | Metabolomics in Diabetic Retinopathy: From Potential Bioma | 基因扫描(R2)  |
| ☐ | 36266625 | 2022 | Y |  | 1 | Differential distribution of steroid hormone signaling net | 基因扫描(R2)  |
| ☐ | 37025170 | 2023 | Y |  | 1 | Cellular heterogeneity and stem cells of vascular endothel | 基因扫描(R2)  |
| ☐ | 37137886 | 2023 | Y |  | 1 | Loss of function of FIP200 in human pluripotent stem cell- | 基因扫描(R2)  |
| ☐ | 37181651 | 2023 | Y |  | 1 | Disease-causing mutations in genes encoding transcription  | 基因扫描(R2)  |
| ☐ | 37328058 | 2024 | Y |  | 1 | Inhibition of oxidative stress-induced epithelial-mesenchy | 基因扫描(R2)  |
| ☐ | 37894748 | 2023 | Y |  | 1 | Transcriptome Profiling of Etridiazole-Exposed Zebrafish ( | 基因扫描(R2)  |
| ☐ | 38067097 | 2023 | Y |  | 1 | Patterns of Gene Expression, Splicing, and Allele-Specific | 基因扫描(R2)  |
| ☐ | 38914302 | 2024 | N |  | 1 | Differential gene expression between central and periphera | 基因扫描(R2)  |
| ☐ | 39806101 | 2025 | Y |  | 1 | Specialized pericyte subtypes in the pulmonary capillaries | 基因扫描(R2)  |
| ☐ | 40001930 | 2025 | Y |  | 1 | Meliponini Geopropolis Extracts Induce ROS Production and  | 基因扫描(R2)  |
| ☐ | 40210893 | 2025 | Y |  | 1 | Role of alpha-1 antitrypsin in Bruch's membrane integrity. | 基因扫描(R2)  |
| ☐ | 40444179 | 2025 | Y |  | 1 | Transporters in vitamin uptake and cellular metabolism: im | 基因扫描(R2)  |
| ☐ | 40595645 | 2025 | Y |  | 1 | The molecular basis for acetylhistidine synthesis by HisAT | 基因扫描(R2)  |
| ☐ | 40604065 | 2025 | Y |  | 1 | Functional significance of commonly regulated genes in mec | 基因扫描(R2)  |
| ☐ | 40867565 | 2025 | Y |  | 1 | The Advance of Single-Cell RNA Sequencing Applications in  | 基因扫描(R2)  |
| ☐ | 40937643 | 2025 | Y |  | 1 | PM2.5 exposure induces transcriptomic changes in ARPE-19 c | 基因扫描(R2)  |
| ☐ | 41097990 | 2025 | Y |  | 1 | Integrative transcriptomic and genomic insights into diabe | 基因扫描(R2)  |
| ☐ | 41146943 | 2025 | Y |  | 1 | Proteome-wide and network pharmacology integration identif | 基因扫描(R2)  |
| ☐ | 41162502 | 2025 | Y |  | 1 | Mechanistic analysis of luteolin in mitigating dry age-rel | 基因扫描(R2)  |
| ☐ | 41326763 | 2025 | Y |  | 1 | A comparative review of single-cell atlases: mapping cellu | 基因扫描(R2)  |
| ☐ | 41409301 | 2025 | Y |  | 1 | Identification and validation of prognostic genes and prog | 基因扫描(R2)  |
| ☐ | 41418782 | 2026 | Y |  | 1 | Human CRX regulates photoreceptor cells development via bi | 基因扫描(R2)  |
| ☐ | 41440117 | 2025 | Y |  | 1 | Core Circadian Protein BMAL1: Implication for Nervous Syst | 基因扫描(R2)  |
| ☐ | 41516124 | 2025 | Y |  | 1 | Regeneration-Associated Factors in the Regulation of Adult | 基因扫描(R2)  |
| ☐ | 41533905 | 2026 | Y |  | 1 | Genetic Link Across Species: SIX6, a Major Human Glaucoma  | 基因扫描(R2)  |
| ☐ | 41596760 | 2026 | Y |  | 1 | A Decade-Old Atlas of TMEM (Transmembrane) Protein Family  | 基因扫描(R2)  |
| ☐ | 41657945 | 2026 | Y |  | 1 | Glycosaminoglycans in tissue regeneration: Insights into g | 基因扫描(R2)  |
| ☐ | 41670256 | 2026 | Y |  | 1 | Longitudinal Genome-Wide Association Study for Female Fert | 基因扫描(R2)  |
| ☐ | 41787658 | 2026 | Y |  | 1 | Engineered Energy-Harvesting Hybrid Nanoscintillators for  | 基因扫描(R2)  |
| ☐ | 41853890 | 2026 | N |  | 1 | Single-cell atlas of B cell heterogeneity in lacrimal IgG4 | 基因扫描(R2)  |
| ☐ | 41987275 | 2026 | Y |  | 1 | Neutrophil extracellular traps in the tumor microenvironme | 基因扫描(R2)  |
| ☐ | 42095275 | 2026 | Y |  | 1 | Proteolytic remodelling of the extracellular matrix by per | 基因扫描(R2)  |
| ☐ | 42100732 | 2026 | Y |  | 1 | Role of CNTN6 in neurodevelopment and neuropathology. | 基因扫描(R2)  |
| ☐ | 42152388 | 2026 | Y |  | 1 | An integrated bioinformatics analysis identifying ALOX15 a | 基因扫描(R2)  |
| ☐ | 42363437 | 2026 | Y |  | 1 | Nonclustered Protocadherins in Autism: Integrating Cell Ad | 基因扫描(R2)  |
| ☐ | 42406957 | 2026 | Y |  | 1 | Time-resolved morphological and transcriptomic characteriz | 基因扫描(R2)  |
| ☐ | 42444979 | 2026 | Y |  | 1 | Delivery Systems for Therapeutic Genome Editing: Challenge | 基因扫描(R2)  |
| ☐ | 42508771 | 2026 | N |  | 1 | Genome-Wide and Rare Variant Association Studies of Amblyo | 基因扫描(R2)  |
| ☐ | 42511033 | 2026 | Y |  | 1 | Genomic Analysis of the Columbian Plumage Pattern in Vario | 基因扫描(R2)  |
| ☐ | 42563687 | 2026 | Y |  | 1 | Multi‑omics insights into uveitis: From mechanisms to prec | 基因扫描(R2)  |
| ☐ | 42589173 | 2026 | Y |  | 1 | S100A9 as a Candidate Molecular Bridge in Hepato-Ocular Cr | 基因扫描(R2)  |
| ☐ | 42630359 | 2026 | Y |  | 1 | Spatial multi-omics unveils sphingolipid metabolic reprogr | 基因扫描(R2)  |
| ☐ | 42653217 | 2026 | Y |  | 1 | Benefits and Limitations Associated with the Use of Altern | 基因扫描(R2)  |

## 备选（同基因第 2-3 候选，加厚检索面；不批不补）

| 勾选 | PMID | 年份 | OA | 收益基因 | 标题(截断) |
|---|---|---|---|---|---|
| ☐ | 39228105 | 2024 | Y | DERL3(membrane),SIGLEC11(membrane),SIGLEC11(retina) | Decreased sialylation elicits complement-related microglia r |
| ☐ | 40520596 | 2025 | Y | ADARB2(retina),GABRA5(retina) | Evolution is in the details: Regulatory differences in moder |
| ☐ | 39164496 | 2024 | Y | DGKB(retina),DOCK10(retina) | Large field of view and spatial region of interest transcrip |
| ☐ | 41010507 | 2025 | Y | GABRA5(retina),IGSF21(retina) | Genetic Susceptibility and Genetic Variant-Diet Interactions |
| ☐ | 39541108 | 2024 | Y | GFRA2(retina),GLCE(retina) | Potential Drug Targets for Diabetic Retinopathy Identified T |
| ☐ | 39630030 | 2024 | Y | GLCE(retina),HS3ST4(retina) | Genetic variability in proteoglycan biosynthetic genes revea |
| ☐ | 42318797 | 2026 | Y | KHDRBS3(retina),RAPGEF5(retina) | Research progress of ferroptosis in gynecological diseases. |
| ☐ | 40151640 | 2025 | Y | ADARB2(retina) | Single-nucleus profiling decoding the subcortical visual pat |
| ☐ | 42636350 | 2026 | Y | AK5(retina) | Exploring genetic diversity in genome-wide association studi |
| ☐ | 35300368 | 2020 | Y | AK5(retina) | Molecular docking investigation of the amantadine binding to |
| ☐ | 40646788 | 2025 | Y | B3GAT2(retina) | Genetic Parameters, Linear Associations, and Genome-Wide Ass |
| ☐ | 41462664 | 2025 | Y | BEGAIN(retina) | Chronic Stress and Astrocyte Dysfunction in Depression: Mole |
| ☐ | 31161422 | 2019 | Y | BEGAIN(retina) | Uveitis and Multiple Sclerosis: Potential Common Causal Muta |
| ☐ | 37287642 | 2023 | Y | C8ORF76(retina) | The retina-specific basigin isoform does not induce IL-6 exp |
| ☐ | 30572641 | 2018 | Y | C8ORF76(retina) | Functional Assessment of Patient-Derived Retinal Pigment Epi |
| ☐ | 28669898 | 2018 | N | CACNG7(retina) | Relevance of tissue specific subunit expression in channelop |
| ☐ | 31783119 | 2020 | N | CACNG7(retina) | Druggable genome screen identifies new regulators of the abu |
| ☐ | 41224955 | 2026 | Y | CAMK2A(retina) | Therapeutic in vivo genome editing: innovations and challeng |
| ☐ | 40171795 | 2025 | Y | CAMK2A(retina) | Circadian clock disruption promotes retinal photoreceptor de |
| ☐ | 32867129 | 2020 | Y | CAMKV(retina) | Proteomics Reveals the Potential Protective Mechanism of Hyd |
| ☐ | 40947010 | 2025 | Y | CAMKV(retina) | Comparative transcriptomics of lateral hypothalamic cell typ |
| ☐ | 41708780 | 2026 | Y | CD5L(membrane) | Combined proteomics and metabolomics analyses revealed molec |
| ☐ | 41744810 | 2026 | Y | CD5L(membrane) | Plasma Extracellular Vesicles from Bronchopulmonary Dysplasi |
| ☐ | 42397694 | 2026 | Y | CLEC10A(membrane) | Border-Associated Macrophages in CNS Health and Disease: A C |
| ☐ | 40060903 | 2025 | Y | CLEC10A(membrane) | Compositional variation in eye-infiltrating immune cells dis |
| ☐ | 38156998 | 2024 | Y | CLEC1A(retina) | The effect of psychoactive bacteria, Bifidobacterium longum  |
| ☐ | 39927770 | 2025 | N | CLEC1A(retina) | Recent developments in &lt;i&gt;Aspergillus fumigatus&lt;/i& |
| ☐ | 42311785 | 2026 | Y | CLEC4C(membrane) | Neuregulin-1 promotes early regenerative and autophagic resp |
| ☐ | 42276015 | 2026 | Y | CMYA5(retina) | Prenatal acoustic communication triggers adaptive vascular p |
| ☐ | 39303842 | 2024 | N | CNTN5(retina) | Comparative analysis of In vivo endothelial cell translatome |
| ☐ | 41193841 | 2025 | Y | COL19A1(retina) | Conservation and alteration of mammalian striatal interneuro |
| ☐ | 42428548 | 2025 | Y | COL19A1(retina) | Effect of high glucose on the gene expression profiling in c |
| ☐ | 36207342 | 2022 | Y | CPNE5(retina) | A multi-omics longitudinal study of the murine retinal respo |
| ☐ | 30866042 | 2019 | N | CPNE5(retina) | Differential expression and subcellular localization of Copi |
| ☐ | 42017663 | 2026 | Y | DERL3(membrane) | Systematic evaluation of TCGA tumor microbiota reveals conte |
| ☐ | 37213234 | 2023 | Y | DGKB(retina) | Oxygen-induced pathological angiogenesis promotes intense li |
| ☐ | 40188093 | 2025 | Y | DOCK10(retina) | RNA-Seq analysis reveals the long noncoding RNAs associated  |
| ☐ | 42758005 | 2026 | Y | DOCK2(retina) | Human inborn errors of the phagocyte respiratory burst: Chro |
| ☐ | 42528538 | 2026 | Y | DOCK2(retina) | Druggable Mendelian randomization prioritizes CDH2 and suppo |
| ☐ | 39062975 | 2024 | Y | ELANE(membrane) | Neutrophils in Ocular Diseases. |
| ☐ | 42453126 | 2026 | Y | ELANE(membrane) | Exosomes in corneal diseases: advances in diagnosis and ther |
| ☐ | 38003067 | 2023 | Y | FAM107B(retina) | Evolutionary Insights into the Relationship of Frogs, Salama |
| ☐ | 42074142 | 2026 | Y | FAM107B(retina) | Potential Applications of Genome-Wide Association Studies in |
| ☐ | 37180776 | 2023 | Y | FAM171B(retina) | WGCNA and molecular docking identify hub genes for cardiac a |
| ☐ | 34794440 | 2021 | Y | FAM171B(retina) | Selection shapes the landscape of functional variation in wi |
| ☐ | 40785550 | 2025 | Y | FGFBP2(membrane) | IgG4-Related Disease: Emerging Roles of Novel Genetic Varian |
| ☐ | 41194198 | 2025 | Y | FGFBP2(membrane) | Prognostic evaluation and experimental validation of cupropt |
| ☐ | 34502527 | 2021 | Y | GFRA2(retina) | Pathogenic Effects of Mineralocorticoid Pathway Activation i |
| ☐ | 39628560 | 2024 | Y | GJA10(retina) | The first interneuron of the mouse visual system is tailored |
| ☐ | 35444239 | 2022 | Y | GJA10(retina) | Lateral gain is impaired in macular degeneration and can be  |
| ☐ | 39885670 | 2026 | Y | GPR34(membrane) | Roles of central nervous system resident and recruited macro |
| ☐ | 41227304 | 2025 | Y | GREB1L(retina) | Study Models for Non-Syndromic Hearing Loss. |
| ☐ | 38351681 | 2024 | Y | GREB1L(retina) | High Incidence of <i>CPLANE1</i>-Related Joubert Syndrome in |
| ☐ | 41938695 | 2026 | Y | HIGD1B(membrane) | Identifying transcriptomic signatures that mediate the causa |
| ☐ | 42537647 | 2026 | N | HIGD1B(membrane) | Spatial atlas of the human brain vasculature reveals special |
| ☐ | 35005108 | 2022 | Y | HS3ST4(retina) | Age-related macular degeneration: Epidemiology, genetics, pa |
| ☐ | 40866756 | 2026 | Y | IGSF21(retina) | Non-invasive pharmacological advances in early retinopathy t |
| ☐ | 38438733 | 2024 | Y | KHDRBS3(retina) | Unique transcriptomes of sensory and non-sensory neurons: in |
| ☐ | 41495483 | 2026 | Y | KLRF1(membrane) | Sensing of DNA double-strand breaks by the NHEJ system stabi |
| ☐ | 40211281 | 2025 | Y | LGMN(membrane) | The CD163 + tissue-infiltrating macrophages regulate ferropt |
| ☐ | 41907140 | 2026 | Y | LGMN(membrane) | Research on the role and mechanisms of Cystatin 6 in disease |
| ☐ | 40868918 | 2025 | Y | LILRA4(membrane) | Microarray Analysis of Differentially Expressed Genes in Per |
| ☐ | 38716077 | 2024 | Y | LILRA4(membrane) | Exploring dendritic cell subtypes in cancer immunotherapy: u |
| ☐ | 39863103 | 2025 | Y | LNX1(retina) | NUMB alternative splicing and isoform-specific functions in  |
| ☐ | 42218382 | 2026 | Y | LNX1(retina) | Integrated environmental and genomic analysis reveals the dr |
| ☐ | 42010735 | 2026 | Y | MNDA(membrane) | Hub genes of neutrophil extracellular traps in abdominal aor |
| ☐ | 40299722 | 2025 | Y | MNDA(membrane) | Type I interferon signalling and interferon-responsive micro |
| ☐ | 40924455 | 2025 | Y | NAT16(retina) | Modeling human retinal ganglion cell axonal outgrowth, devel |
| ☐ | 42421968 | 2026 | Y | NCR3(membrane) | Delving into the innate and adaptive immunity of camelids: a |
| ☐ | 42633379 | 2026 | Y | NCR3(membrane) | DAMPs, PAMPs, and Alarmins: From Mechanism to Therapy. |
| ☐ | 41390476 | 2025 | Y | OLFML3(membrane) | The glymphatic system in neurodegenerative diseases and brai |
| ☐ | 39929889 | 2025 | Y | PCDH11X(retina) | Sigma-2 receptor modulator CT1812 alters key pathways and re |
| ☐ | 42311937 | 2026 | Y | PCDH11X(retina) | Intrinsic elaboration of prefrontal modularity: a dual-contr |
| ☐ | 40905150 | 2025 | Y | PCSK6(retina) | Mild Hyperuricemia Attenuates Salt-Sensitive Hypertension an |
| ☐ | 41751104 | 2026 | Y | PCSK6(retina) | Kinglet in the Poultry Court of Russia: Whole-Genome Insight |
| ☐ | 37807874 | 2024 | N | PIK3R5(retina) | Aberrant gene expression yet undiminished retinal ganglion c |
| ☐ | 41359379 | 2025 | Y | PLD4(membrane) | The lysosomal catabolism of nucleic acids-critical regulator |
| ☐ | 35565057 | 2022 | Y | PLD4(membrane) | Potential Biomarkers and Drugs for Nanoparticle-Induced Cyto |
| ☐ | 40399499 | 2025 | N | RAPGEF5(retina) | Genome-Wide Association Study of Age-Related Hearing Loss in |
| ☐ | 42088622 | 2026 | Y | S100A12(membrane) | S100A9 Integrates Autophagic Deficiency With Immunopathology |
| ☐ | 39774261 | 2025 | Y | S100A12(membrane) | Immune pathogenic response landscape of acute posterior mult |
| ☐ | 39286668 | 2024 | Y | SESTD1(retina) | A Review of the Retinal Impact of Traumatic Brain Injury and |
| ☐ | 38731826 | 2024 | Y | SESTD1(retina) | Herpes Simplex Virus ICP27 Protein Inhibits AIM 2-Dependent  |
| ☐ | 36833422 | 2023 | Y | SIGLEC11(membrane) | Whole Exome Sequencing Reveals Novel Candidate Genes in Fami |
| ☐ | 32423062 | 2020 | Y | SIGLEC11(retina) | Microglia Contribution to the Regulation of the Retinal and  |
| ☐ | 40524449 | 2025 | Y | SKAP1(membrane) | Disruption of mc1r Disturbs Skin Pigmentation in Xenopus tro |
| ☐ | 36614039 | 2022 | Y | SLC24A3(retina) | Regulation of K<sup>+</sup>-Dependent Na<sup>+</sup>/Ca<sup> |
| ☐ | 38731230 | 2024 | Y | SLC24A3(retina) | The Dawn and Advancement of the Knowledge of the Genetics of |
| ☐ | 42494142 | 2026 | Y | SLC35F3(retina) | Renal Phosphate Reabsorption in Humans Depends on at Least T |
| ☐ | 39608565 | 2025 | N | SLC4A3(retina) | pH in the vertebrate retina and its naturally occurring and  |
| ☐ | 42533102 | 2026 | Y | SNTG1(retina) | Single-cell spatial mapping of human kidney development impl |
| ☐ | 36975205 | 2023 | Y | SNTG1(retina) | Longitudinal fundus imaging and its genome-wide association  |
| ☐ | 42136961 | 2026 | Y | SSR4(membrane) | Integrated Bulk and Single-Cell Transcriptomic Analysis Reve |
| ☐ | 38612470 | 2024 | Y | SSR4(membrane) | Adult Neurogenesis of Teleost Fish Determines High Neuronal  |
| ☐ | 41120831 | 2025 | Y | TMEM132C(retina) | A comprehensive genome-wide analysis for signatures of selec |
| ☐ | 36198871 | 2023 | Y | TMEM132C(retina) | Vascular endothelial cell development and diversity. |
| ☐ | 42221844 | 2026 | Y | TMEM196(retina) | Integrated Transcriptomics and Experimental Validation Revea |
| ☐ | 24837086 | 2014 | Y | TMEM196(retina) | The db/db mouse: a useful model for the study of diabetic re |
| ☐ | 39353729 | 2024 | N | TRBC2(membrane) | Monocyte Invasion into the Retina Restricts the Regeneration |
| ☐ | 40386178 | 2025 | Y | TRBC2(membrane) | Integrative Analysis and Experimental Validation Reveal FCGR |
| ☐ | 42330349 | 2026 | Y | XCR1(membrane) | Eye-Brain Neuroimmune Axis Enables Long-Term Survival in Gli |
| ☐ | 42724236 | 2026 | Y | XCR1(membrane) | Construction of a prediction model for retinopathy of premat |
| ☐ | 41014753 | 2025 | Y | ZNF804B(retina) | Integrative Spatial and Single-Nucleus Transcriptomics Eluci |
| ☐ | 34529728 | 2021 | Y | ZNF804B(retina) | Genetic differentiation of mainland-island sheep of Greece:  |

> ⚠ 候选=检索词族 top 命中（元数据级），个别相关性存疑（如 40971959 实为斑马鱼论文——词族不严格的实例，PI 勾选时复核）。
> ⚠ 引用链 7 篇 PMID 若 PI 亦判不补，则相应词条（LACRT/PRR27/SCGB1D1/GAPDHS/LILRB2）维持"链在库外"现状——功能上 query_marker/search_literature 双通道已可用，仅"库内一手溯源"缺。
