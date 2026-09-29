# 注释证据报告（EyeKB pipeline 阶段 B 输出）

- 生成时间：2026-09-29 20:50:48
- 输入：`docs/plans/pipeline_pub_20260929/out/smoke_degraded/stage_a/processed.h5ad`（物种 human，组织 fibrovascular_membrane，疾病先验启用）
- MCP 调用：32 次，错误 0 次
- **阅读须知**：本报告只呈现证据与机械 QC 旗，不含注释结论；每簇的最终命名由研究者在 decisions_template.csv 填写 accept / modify / abstain。弃权是合法输出。

- 红线：默认路径零 LLM；本文件由本地五工具机械检索生成
- 红线：置信度分级是预注册机械 QC 旗（规则触发原因逐条可查），不是注释结论
- 红线：弃权(needs_review)/复核(mixed_or_insufficient) 是合法输出；禁止把 QC 旗当确定标签
- 红线：全部证据（marker 命中/基线区间/疾病先验提及/文献片段）带出处，供人工裁决

## 簇 0（305 细胞，占 15.427%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000133048, ENSG00000100985, ENSG00000155368, ENSG00000164687, ENSG00000115414, ENSG00000165140, ENSG00000142669, ENSG00000198695, ENSG00000164713, ENSG00000212907
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
  - [gene_query] PMID 39863929 (Molecular therapy : the journal of the American Society of Gene Therapy 2025): Our X-ray crystallographic study revealed that hAS0326 makes MFAP4 inaccessible for integrin receptor interaction through steric hindrance. …
- 分组构成（%细胞）: {'RRD_control': 100.0, 'PDR': 0.0}

## 簇 1（289 细胞，占 14.618%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000142227, ENSG00000210082, ENSG00000163191, ENSG00000211459, ENSG00000233913, ENSG00000196154, ENSG00000197747, ENSG00000212907, ENSG00000158869, ENSG00000142669
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
- 分组构成（%细胞）: {'RRD_control': 100.0, 'PDR': 0.0}

## 簇 2（157 细胞，占 7.941%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000143546, ENSG00000163220, ENSG00000164713, ENSG00000198695, ENSG00000019169, ENSG00000142227, ENSG00000163191, ENSG00000129538, ENSG00000158869, ENSG00000196154
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
- 分组构成（%细胞）: {'RRD_control': 100.0, 'PDR': 0.0}

## 簇 3（20 细胞，占 1.012%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000122026, ENSG00000077984, ENSG00000105372, ENSG00000115268, ENSG00000168685, ENSG00000101439, ENSG00000204472, ENSG00000160307, ENSG00000237541, ENSG00000174748
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
- 分组构成（%细胞）: {'RRD_control': 100.0, 'PDR': 0.0}

## 簇 4（265 细胞，占 13.404%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000125730, ENSG00000090104, ENSG00000019582, ENSG00000231389, ENSG00000204287, ENSG00000223865, ENSG00000196126, ENSG00000196735, ENSG00000229391, ENSG00000179344
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
- 分组构成（%细胞）: {'PDR': 76.23, 'RRD_control': 23.77}

## 簇 5（94 细胞，占 4.755%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠
- top 基因: H2AFZ, ENSG00000148773, ENSG00000189403, ENSG00000117632, ENSG00000137804, ENSG00000164104, ENSG00000198830, ENSG00000131747, ENSG00000187514, HIST1H4C
- query_marker 候选: Proliferating (n_shared=1, H2AFZ)
- 组成对照（基线条 human_pdr_membrane）: flag=no_baseline_row
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 1 条
- 文献片段（top3，逐条带 PMID）:
  - [Proliferating] PMID 41390488 (Nature communications 2025): Single-cell RNA sequencing datasets were obtained from the Gene Expression Omnibus (GEO), including OIR (oxygen-induced retinopathy) and age…
  - [Proliferating] PMID 39422453 (eLife 2024): Raw reads were aligned to mm10 reference genome by STAR and summarized to gene counts. After transcripts Per Kilobase Million (TPM) normaliz…
- 分组构成（%细胞）: {'RRD_control': 77.66, 'PDR': 22.34}

## 簇 6（38 细胞，占 1.922%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000245532, ENSG00000115355, ENSG00000210082, ENSG00000151914, ENSG00000198695, ENSG00000198888, ENSG00000198899, ENSG00000198886, ENSG00000251562, ENSG00000198763
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
- 分组构成（%细胞）: {'RRD_control': 65.79, 'PDR': 34.21}

## 簇 7（42 细胞，占 2.124%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000163453, ENSG00000127920, ENSG00000152583, ENSG00000169908, ENSG00000113140, ENSG00000115380, ENSG00000166681, ENSG00000122786, ENSG00000117318, ENSG00000117519
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38183022 (Cell communication and signaling : CCS 2024): SB431542 significantly alleviated retinopathy in the CNV model. The proliferation, migration and adhesion in RPE cells decreased to a certai…
- 分组构成（%细胞）: {'PDR': 76.19, 'RRD_control': 23.81}

## 簇 8（87 细胞，占 4.401%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000163453, ENSG00000164692, ENSG00000113140, ENSG00000122786, ENSG00000140416, ENSG00000109846, ENSG00000108821, ENSG00000198832, ENSG00000102265, ENSG00000117519
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
- 分组构成（%细胞）: {'PDR': 63.22, 'RRD_control': 36.78}

## 簇 9（159 细胞，占 8.042%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000250722, ENSG00000260314, ENSG00000165457, ENSG00000010327, ENSG00000170458, ENSG00000178573, ENSG00000104870, ENSG00000136156, ENSG00000124491, ENSG00000159189
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 39863929 (Molecular therapy : the journal of the American Society of Gene Therapy 2025): Our X-ray crystallographic study revealed that hAS0326 makes MFAP4 inaccessible for integrin receptor interaction through steric hindrance. …
- 分组构成（%细胞）: {'PDR': 98.11, 'RRD_control': 1.89}

## 簇 10（181 细胞，占 9.155%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000164733, ENSG00000100292, ENSG00000117984, ENSG00000087086, ENSG00000130203, ENSG00000135047, ENSG00000111640, ENSG00000135821, ENSG00000167996, ENSG00000143162
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
- 分组构成（%细胞）: {'PDR': 98.9, 'RRD_control': 1.1}

## 簇 11（38 细胞，占 1.922%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000169442, ENSG00000277734, ENSG00000177600, ENSG00000137818, ENSG00000213741, ENSG00000167286, ENSG00000008517, ENSG00000149273, ENSG00000116824, ENSG00000177954
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 39863929 (Molecular therapy : the journal of the American Society of Gene Therapy 2025): Our X-ray crystallographic study revealed that hAS0326 makes MFAP4 inaccessible for integrin receptor interaction through steric hindrance. …
- 分组构成（%细胞）: {'PDR': 89.47, 'RRD_control': 10.53}

## 簇 12（128 细胞，占 6.474%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000156482, ENSG00000090382, ENSG00000198242, ENSG00000169442, ENSG00000070756, ENSG00000075624, ENSG00000213741, ENSG00000145425, ENSG00000085265, ENSG00000265972
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
- 分组构成（%细胞）: {'PDR': 98.44, 'RRD_control': 1.56}

## 簇 13（166 细胞，占 8.397%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000117984, ENSG00000135821, ENSG00000100600, ENSG00000179163, ENSG00000135047, ENSG00000100292, ENSG00000101160, ENSG00000138449, ENSG00000030582, ENSG00000105223
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 39863929 (Molecular therapy : the journal of the American Society of Gene Therapy 2025): Our X-ray crystallographic study revealed that hAS0326 makes MFAP4 inaccessible for integrin receptor interaction through steric hindrance. …
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
- 分组构成（%细胞）: {'PDR': 100.0, 'RRD_control': 0.0}

## 簇 14（8 细胞，占 0.405%）
- 置信度分级（机械 QC 旗）：**needs_review**
  - 触发规则: gene_ids_unmapped: 输入基因 ID 未映射到符号，marker 比对不可靠, no_named_marker_candidates, no_literature_results
- top 基因: ENSG00000100453, ENSG00000198178, ENSG00000145287, ENSG00000185507, ENSG00000135916, ENSG00000132465, ENSG00000211592, ENSG00000235162, ENSG00000140968, ENSG00000185291
- query_marker 候选: 无具名候选
- 组成对照（基线条 human_pdr_membrane）: flag=no_candidate
- 疾病先验: PDR: PDR__fibrovascular_membrane 提及 0 条
- 文献片段（top3，逐条带 PMID）:
  - [gene_query] PMID 37550343 (Scientific reports 2023): To establish the biological functions and possible active signaling pathways of fibrovascular membranes, we selected fibrovascular membranes…
  - [gene_query] PMID 38247931 (Bioengineering (Basel, Switzerland) 2024): First, we established the electrospinning conditions to impart the necessary characteristics for utilizing the produced gelNF membrane as a …
- 分组构成（%细胞）: {'PDR': 100.0, 'RRD_control': 0.0}

---
*本报告由 EyeKB 仓内 `pipeline/` 生成；服务红线：证据只作人工判读与 QC 旗，禁止接进任何打分/加权/排序。*