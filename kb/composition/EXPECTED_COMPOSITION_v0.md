# EXPECTED_COMPOSITION_v0 — 正常成人眼组成先验面（人读版）

> 生成 2026-09-28 | 卡 t_fa03e1d7 | 授权：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加七B (D-1); 任务书 plans/comp_prior_20260928/BRIEF_DISC_COMP.md
>
> **⛔ 接线状态：`OFF — 未接线 (零 MCP/运行时引用; 接线与激活另卡另批, 本面任何激活须 PI 拍板)`** —— 本面任何运行时消费（MCP/baselines/打分/门控）须另卡另批、PI 拍板。

## 0. 定位与口径（先读这里）
- 面语义：**面=该取样材料在该实验流程下捕获事件的构成参考 (身份参考+背景对照), 非组织学真值, 非组成达标线; 旗标=提示复核≠注释错误**
- 证据等级：A=registry 台账外部作者注释本地复算 (kb/baselines adult-only 供者级主档, 带路径)；B=盘上已入库 RAG 文献原文直接报告 (chunks 逐字句)；C=跨研究经验区间 (kb/priors/composition/human_retina.json, 卡 t_39182aa2)；no_evidence=无 A/B/C 可用 → 不编数
- 谱系声明（禁循环条款）：比例区间来源 = D001(HRCA)/D002(OcularSurface) portal 作者注释复算 (经 kb/baselines v1.1 adult-only 主档) + priors v1 经验区间 + 已入库文献原文句; 全程未使用自家聚类/自家 demo 注释 (禁循环条款)
- 区间机械规则（预注册）：low=floor(min(donor_iqr_low, priors_expected_low, fold_lit_low)); high=ceil(max(donor_iqr_high, priors_expected_high, fold_lit_high)); mid=donor_median; 无来源行=null(no_evidence)
- 范围：{"species": "human", "organism_stage": "adult_only", "disease_states": "不建 (PDR 注释不可靠口径维持; 疾病材料不得对照健康面验收, Astra T2 usage_scope)", "fetal_organoid_developing": "数值折叠排除; 引用记录中显式标注排除原因 (32946783 organoid 句/39117640 developing/36645183 fetal)", "tissues_out_of_v0": "其余组织留 v1"}

## 1.1 页: retina_normal_adult_human
- registry 锚: OA-D001 (HCA-HRCA-v1.0), PMID 41578023, path <STORE>/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad
- 供者级主档: kb/baselines/retina.json adult-only 主档 (97 donors)

| 细胞类型 | 低% | 中% | 高% | 证据 | B 状态 | 逐行 PMID | 供者级实测(median/iqr/range) |
|---|---|---|---|---|---|---|---|
| Rod (视杆光感受器) | 22 | 48.9 | 58 | A_registry_recompute+B_literature | B | 37388908, 38012720, 41578023 | 48.85 / [22.06, 57.56] / [0.0, 77.97] |
| Cone (视锥光感受器) | 1 | 3.3 | 7 | A_registry_recompute+B_literature | B | 32555229, 37388908, 41578023 | 3.27 / [2.3, 5.21] / [0.0, 13.1] |
| BC (双极细胞) | 12 | 20.0 | 33 | A_registry_recompute+B_literature | B | 37388908, 41578023 | 19.99 / [15.21, 26.98] / [0.13, 49.97] |
| AC (无长突细胞) | 6 | 8.5 | 28 | A_registry_recompute+B_literature | B | 37388908, 41578023 | 8.46 / [6.55, 10.96] / [3.59, 70.83] |
| HC (水平细胞) | 1 | 2.8 | 8 | A_registry_recompute+B_literature | B | 37388908, 41578023 | 2.78 / [1.38, 4.47] / [0.0, 13.25] |
| RGC (神经节细胞) | 0 | 3.2 | 15 | A_registry_recompute+B_literature | B | 37388908, 38012720, 41578023 | 3.23 / [0.88, 8.7] / [0.0, 92.41] |
| MG (Müller 胶质) | 3 | 8.8 | 12 | A_registry_recompute+B_literature | B | 32069977, 41578023 | 8.75 / [5.28, 11.48] / [0.0, 24.66] |
| Astro (星形胶质) | 0 | 0.4 | 2 | A_registry_recompute+B_literature | B | 32555229, 41578023 | 0.37 / [0.05, 0.9] / [0.0, 5.38] |
| Micro (小胶质) | 0 | 0.1 | 1 | A_registry_recompute+B_literature | B | 37017569, 41578023 | 0.14 / [0.0, 0.22] / [0.0, 1.22] |
| RPE (视网膜色素上皮) | 0 | 0.0 | 1 | A_registry_recompute+B_literature | B | 32946783, 41578023 | 0.0 / [0.0, 0.0] / [0.0, 2.03] |
| Endo_vascular (血管内皮 (off-panel)) | null | null | null | no_evidence | B | 41578023 | – |
| Pericyte_vascular (周细胞 (off-panel)) | null | null | null | no_evidence | B | 41578023 | – |

### 逐行文献锚点（盘上已入库文献原文句，B 级可定位）
- **Rod**
  - PMID 38012720 [fold] “the distributions of cell type proportions ... ranging from 2.5% RGC to 55.2% Rod” — snRNA+snATAC 多组学 跨样本组成极值 (人, adult)
  - PMID 37388908 [identity] “the highest overlap (63.9%) is observed for the most abundant cell type, Rod” — 人 snRNA-seq atlas: Rod 为最丰细胞类型 (定性)
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA 整合图谱 majorclass 收录 Rod (registry 台账 OA-D001)
- **Cone**
  - PMID 37388908 [context] “S cones (0.07% of total retinal cells)” — S-cone 亚型口径, 不折叠; Cone 整体存在性支持
  - PMID 32555229 [identity] (题录锚, 无逐字句) — 人中央凹/周边视网膜细胞图谱收录锥细胞
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 Cone
- **BC**
  - PMID 37388908 [fold] “AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset” — 人 snRNA-seq 该数据集层面双极细胞占比 (fold high)
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 BC
- **AC**
  - PMID 37388908 [fold] “AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset” — 同上数据集层 AC 占比 (fold high)
  - PMID 37388908 [context] “vGlut3 excitatory ACs (0.7% of total retinal cells)” — 兴奋性 AC 亚型口径, 不折叠
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 AC
- **HC**
  - PMID 37388908 [identity] “lowest overlap is observed for HC (49.0%)” — 人图谱收录水平细胞 (定性)
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 HC
- **RGC**
  - PMID 37388908 [context] “the total number of RGCs only accounts for approximately 1% of the cell population in the retina” — 组织学理论估计口径, 不折叠; 方向锚
  - PMID 37388908 [fold] “AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset” — 人数据集捕获层 RGC 占比 (fold high)
  - PMID 38012720 [fold] “ranging from 2.5% RGC to 55.2% Rod” — 跨样本 RGC 下界极值 (fold low)
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 RGC
- **MG**
  - PMID 32069977 [identity] “Within the fovea, Müller cells and horizontal cells ...” — 人中央凹 AIR 图谱确认 Müller 细胞存在 (定性)
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 MG
- **Astro**
  - PMID 32555229 [context] “depletion of astrocytes from fovea (0.9% of all non-neuronal cells in fovea and 12% in periphery)” — 分母=非神经元细胞, 口径异, 不折叠; 区域差异方向锚
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 Astro
- **Micro**
  - PMID 37017569 [context] “microglia (11 cells, 0.0146% of total cell count) directly mapped to the chromatin landscape” — scATAC 直接映射子集口径, 不折叠; 稀有性方向锚
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA majorclass 收录 Microglia
- **RPE**
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA 神经视网膜 majorclass 收录 RPE (捕获 0.03%)
  - PMID 32946783 [context] “pigment epithelial cells had 2% RPE65 (expression in organoids)” — 器官类表达口径且涉 organoid, 不折叠不入面; 仅登记排除
- **Endo_vascular**
  - PMID 41578023 [identity] (题录锚, 无逐字句) — HRCA 10 类词表不含血管类; 真实全视网膜含低比例血管成分, 出现小簇属正常 (baselines/retina.json caveat)
- **Pericyte_vascular**
  - PMID 41578023 [identity] (题录锚, 无逐字句) — 同上 caveat: 血管 mural 成分出现不打 contamination 旗

## 1.2 页: ocular_surface_normal_adult_human
- registry 锚: OA-D002 (CELLxGENE-OcularSurface), path <STORE>/data/D002_ocularsurface/D002_allcells_578K.h5ad
- 供者级主档: kb/baselines/ocular_surface.json adult-only 主档 (41 donors/67 单元); 超级类区域混合口径禁跨区套用

| 细胞类型 | 低% | 中% | 高% | 证据 | B 状态 | 逐行 PMID | 供者级实测(median/iqr/range) |
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
| Conjunctival_epithelium(sub) (结膜上皮 (D002 内子类)) | null | null | null | no_evidence | B | 32502616 | – |
| Goblet_cell (杯状细胞) | null | null | null | no_evidence | B_missing | — | – |

### 逐行文献锚点（盘上已入库文献原文句，B 级可定位）
- **Corneal Endothelium**
  - PMID 33865984 [context] “endothelial cells in humans are not endogenously renewed ... density declines at an average of approximately 0.6% per year” — 细胞密度口径 (cell/mm^2), 非组成百分比, 不折叠; CEC 身份/稀有性锚
  - PMID 34381080 [identity] (题录锚, 无逐字句) — 角膜单细胞目录收录 corneal endothelial cells (CenC)
- **Endothelium**
  - PMID 34381080 [identity] (题录锚, 无逐字句) — 角膜单细胞目录收录 vascular endothelial cells
- **Epithelium**
  - PMID 34381080 [identity] “These 16 clusters correspond to 11 subtypes of epithelial cells, keratocytes, Langerhans cells, melanocytes, vascular endothelial cells and corneal endothelial cells” — 成人人角膜单细胞目录: 上皮为大类 (定性)
  - PMID 34741068 [identity] “The cornea is composed of five layers: its outer surface is a stratified sheet of corneal epithelial cells” — 人角膜分层结构 (定性)
  - PMID 32502616 [identity] (题录锚, 无逐字句) — 成人结膜/角膜缘/角膜上皮 scRNA 收录
- **Fibroblasts**
  - PMID 34381080 [fold] “Over 15% of cells in our analysis are keratocytes within a single cluster” — 成人角膜 scRNA: keratocyte 单簇 >15% (fold low)
  - PMID 40838019 [identity] “The corneal stroma, composed mainly of keratocytes” — 角膜基质主驻留细胞为 keratocyte (定性)
  - PMID 34741068 [identity] “The keratocytes populate the corneal stroma” — 定性
- **Immune Cells**
  - PMID 34381080 [identity] (题录锚, 无逐字句) — 角膜单细胞目录收录 Langerhans cells (免疫)
  - PMID 41552884 [identity] (题录锚, 无逐字句) — 角膜巨噬细胞综述 (人源证据强调)
- **Melanocytes**
  - PMID 34381080 [identity] (题录锚, 无逐字句) — 角膜单细胞目录收录 melanocytes
  - PMID 40216818 [identity] “PAX3 expression in LM as well in the conjunctival melanocytes” — 角膜缘/结膜黑色素细胞存在 (定性)
- **Pericytes**
  - PMID D002-PORTAL-ONLY [identity] (题录锚, 无逐字句) — 无盘上成人眼表 pericyte 组成文献句; 身份仅 D002 官方注释 (A 级) — B 级缺项如实登记
- **Schwann Cells**
  - PMID 40649793 [context] “NGF ... corneal nerve regeneration” — 眼表神经综述 (定性),  Schwann 组成%未钉死
- **Smooth Muscle Cells**
  - PMID 40649793 [context] “NGF has been found to be produced by ... smooth muscle cells” — 综述提及眼表 SMC 存在 (定性)
- **Conjunctival_epithelium(sub)**
  - PMID 32502616 [identity] (题录锚, 无逐字句) — 成人结膜上皮 scRNA; D002 无独立 super class (portal 标签归 Epithelium)

## 2. PMID 题录三判据自检
- 判据：j1=题录在 v2.4.2 papers.jsonl 可解析(题录三要素非空); j2=非幽灵(n_chunks>0); j3=入库可溯(vk 页∨sidecar∨papers.jsonl)；PMID 总数 15，台账不合格行 0
- 逐条明细见 `ledgers/PROVENANCE_COMP_v0.tsv`

## 3. 已知限制与 caveat
- RGC/神经元类比例受核分选与建库设计影响 (NeuN±, RGC 富集) — 判异常前必查建库策略 (baselines caveat 继承)
- snRNA(核) 与 scRNA(细胞) 类比例不可直接互比 (Astra T2)
- 眼表 Immune 仅 1.7% 池: 眼表固有免疫稀少, 免疫比例不可对照炎症样本
- Corneal Endothelium 主档中位 0%: 纯 CEC 材料(碎块层) 分母=100%, 不适用本行
- Goblet/结膜细节行 = 数据与文献双缺项, 已标 no_evidence
- PAPER 41578023 (HRCA) n_chunks=1 (入库增量非全 chunk 化) — j2 勉强过, 内容锚不依赖它
- 缺逐行 PMID 的行（激活前义务 OB-1）：ocular_surface_normal_adult_human:Pericytes, ocular_surface_normal_adult_human:Goblet_cell
- 激活义务 OB-1 缺逐行 PMID 的行 (D002 portal 身份, 盘上无组成文献句): 见 rows_missing_pmid — 激活前须补文献或维持 OFF
- 激活义务 OB-2 眼表面=区域混合超级类 (D002 口径), 激活接线时须按 tissue_group 分层出区间或按区域路由 (category_note 禁跨区套用)
- 激活义务 OB-3 反向质检已触发 (Q1/Q2/Q3 健康集旗标率>20%, 见 COMP_SELFFLAG_20260928.md §3): v0 区间对跨平台/跨取材区域/分选设计过窄, 属面侧已知限制 — 激活前须分层/豁免规则化并过 PI 拍板
- 疾病态比例不建（PDR 注释不可靠口径维持）；发育轴（fetal/organoid）数值折叠排除，引用记录留痕。
- “INTAKE 台账 392 条”按任务书原文并入“盘上已入库 RAG 文献（papers.jsonl v2.4.2）元数据可核者”口径执行（deviation 声明：盘上未寻得名含 INTAKE 且恰 392 条的文献台账文件；methods-scrna 索引页恰 392 篇，作为可核集之一纳入）。

## 4. 自检与激活
- 自检旗标报告：`COMP_SELFFLAG_20260928.md`（只出旗标清单与比例分布，不出注释错误结论）。
- 本面默认 OFF；接入判读层（unexpected 旗标器）为另卡另批事项。