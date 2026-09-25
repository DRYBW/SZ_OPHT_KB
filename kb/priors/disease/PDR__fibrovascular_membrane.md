# 疾病条目 (示例格): PDR 增殖期 × 纤维血管膜 (人)

> schema: `eyekb-disease/1.1` | entry_id: `PDR__fibrovascular_membrane` | 冻结: 2026-09-23 | 卡片: t_16c3e020 | supersedes: proliferative_DR (t_39182aa2, v1 存档) | 发育档: **organism_stage=adult | development_stage=adult** (KB3 显式)
> 由 `/mnt/D/EyeKB/scripts/disease/build_disease_v2.py` 生成; 手改 MD 会被覆盖。

> **发育轴**: KB2c 发育轴 (裁定 Q3): 疾病格键含发育轴 —— 本格=adult (增殖期 PDR 均为成人手术材料; GSE165784/JCI 队列供者皆成人)。发育期样本不进成人疾病格 (PI 指令条款2);若未来收 pediatric 膜材料, 单立格不并入本条。

**本条目 = 上下文一致性核查材料 (非白名单): 只产生 expected/unexpected/污染旗, 禁入打分; 标签不得被强制改成清单内身份 (Astra T2)。**

## 疾病×组织矩阵定位

本条目是矩阵的**第一个示例格子** (矩阵示例格 = '一个格子'而非项目中心 (PI 2026-09-23 眼科通用口径))。矩阵总览: `_DISEASE_TISSUE_MATRIX.md`。

## 上下文 (T4)

- **取样材料**: 玻璃体切除联合膜剥离术所取纤维血管膜 (可含内界膜/前黄斑膜; GSE165784 样本名 PDR-ERM 与 PDR-FM 即同材料两类手术叫法, 均属膜)。
- **疾病阶段**: 增殖期 (新生血管/纤维化期); 非 NPDR/DME 阶段
- **治疗背景**: 既往激光/抗 VEGF 状态在源数据未系统记录 —— 标未记录
- **方法口径**: scRNA-seq 细胞悬液 (非核); 与 D001 retina 核悬液、D002 眼表细胞悬液口径均不同

## 取样材料错配警示 (必读)

**取样材料错配警示 (Astra T2 裁定核心)**: 本病发生部位=视网膜, 但手术材料=纤维血管膜。健康视网膜组成基线 (kb/baselines/retina, D001) 对本膜标本【不可】作组成达标线 —— 膜以巨噬/血管/间质为主, 光感受器等神经视网膜类近零是材料性质而非异常。

**正确用法**: 身份参考 (某髓系簇与视网膜驻留小胶质转录相似度的层级判断); 邻近视网膜标本 (retina_adjacent 格) 的背景对照

**错误用法**: 膜标本的细胞比例'达标'验收; 把 Rod/Cone 缺失判为质量缺陷 (先查材料!)

**可比材料主锚**: 本卡可比材料主锚 = GSE165784 (PDR 膜, PMID 35061025) + JCI Insight 2023 独立 PDR 膜队列 (PMID 37917183) —— 同物种/同材料/同阶段, Astra T2 优先序第 1 档。

## 身份层级 (T4: 分层身份, 每层标可支持最深级)

| 概念ID | 规范身份 | 可支持层级 | 备注 |
|---|---|---|---|
| EYEKBC-0001 | macrophage_tissue_resident | major→subcluster | 驻留/招募来源判定封顶=转录相似 |
| EYEKBC-0002 | macrophage_recruited_monocyte | major | 与血污混叠, 需先排技术 |
| EYEKBC-0006 | endothelial_cell | major→pathologic state |  |
| EYEKBC-0008 | pericyte | major |  |
| EYEKBC-0010 | fibroblast_membrane_stroma | major | 与 0009 转变轴连续, 边界可未解析 |
| EYEKBC-0011 | muller_glia (reactive) | major+state | glial scar 成分 |
| EYEKBC-0013 | t_cell | major | 低比例 |

## 状态轴 (可共存; 连续态不强制二分)

- **proliferation (MKI67+)** → 适用于 endothelial, stromal, microglia(报告为例外,B级); ⚠ 细胞周期信号≠血管新生结论 (T7 第四步: 需身份+增殖+空间三层证据)
- **hypoxia/patho-activation (HIF1A/PLVAP/NDUFA4L2)** → 适用于 endothelial
- **ECM remodeling / PMT transition (PRRX1/ACTA2/POSTN/CTHRC1)** → 适用于 pericyte, stromal [连续轴]
- **lipid_laden/foam (GPNMB/TREM2/SPP1)** → 适用于 macrophage
- **heme_stress (HMOX1/FTL)** → 适用于 macrophage; 技术混叠: 出血+解离
- **MHC-II antigen presentation** → 适用于 macrophage
- **reactive gliosis (GFAP/CRYAB/CLU)** → 适用于 muller_glia, astrocyte

## 预期矩阵 (本格)

- Macrophage: 组织型驻留(SELENOP/FOLR2) + 招募型经典单核(FCN1/LYZ) + 泡沫样DAM-LAM(GPNMB/TREM2/SPP1) + MHC-II高APC + 血红素应激(HMOX1)
- Endothelial: 病理态(PLVAP/NDUFA4L2/HIF1A/ICAM1/VCAM1) + tip/stak 亚态(DLL4; C级外推自 TIPCELL_DEV/RAB5IF)
- Pericyte→Myofibroblast 连续转变 (PRRX1 驱动, B: PRRX1)
- Stromal: COL1A1/COL3A1/FN1 高细胞外基质
- Lymphoid: T(CD69 活化)、浆细胞低比例
- Proliferating: MKI67+ 群存在 (含 MKI67+ 小胶质, B: PDR_MKI67MG)
- Glial: Müller/反应性胶质瘢痕成分 (GFAP↑, B: GLIA_RDG)
- 证据 A+B | 出处: GSE165784V2, PDR_HU2022, PDR_JCI2023, PRRX1, PDR_MKI67MG, GLIA_RDG, TIPCELL_DEV, RAB5IF

## 跨材料对照注记 (非本格内容, 未建条目)  

- vitreous 格参考: T 细胞绝对优势 91.6% (B: VITREOUS_T) —— 属 PDR__vitreous 格子, 未达独立条目门槛前只作材料对照
- retina_adjacent 格参考: 早中期 DR 小胶质状态改变无大规模髓系涌入 (B: MG_EARLY_DR/DR_RETINA_SC); Müller 反应性 (B: MULLER_REDD1) —— 属 PDR__retina_adjacent 格子

## 签名 × 证据条件 (T4: 不止 PMID —— 论断类型/条件/比较对象/定位锚点/反例限制)

| 签名 | marker | 论断类型 | 关系 | 条件 | 比较对象 | 定位锚点 | 反例/限制 |
|---|---|---|---|---|---|---|---|
| tissue_resident_mac | SELENOP, MRC1, FOLR2, CD163, STAB1, VSIG4, CD5L | identity | 支持 | human, fibrovascular membrane, scRNA | vs 招募单核 (FCN1 组) | Hu2022 (PMID 35061025) 结果节; markers_membrane_v1 canonical 层 | 与稳态小胶质区分不足 —— SELENOP/FOLR2 亦见于血管周围巨噬; 来源断言封顶转录相似 |
| recruited_monocyte | FCN1, VCAN, S100A8, S100A9, CD14, SELL, S100A12 | identity+contamination | 限定 | 同上 | vs 组织驻留 | markers_membrane_v1; GSE165784 v2 B5/B9 实测 | FCN1/LYZ 高表达与手术血液污染混叠 —— 单签名不可判'疾病募集', 必须配血污旗核查 |
| foam_DAM_LAM | GPNMB, LIPA, CTSD, LGMN, PLD3, TREM2, SPP1, APOE, MMP9 | state | 支持 | human PDR membrane; 亦见于动脉粥样硬化 LAM (跨病) | vs 稳态巨噬 | Hu2022 GPNMB+ 亚群节 | LAM 签名非 PDR 特异; '泡沫样'形态学佐证需 OCT/组织学 |
| heme_stress_mac | HMOX1, FTL, FTH1, CD163 | state | 限定 | PDR 膜 (出血背景) | vs 非应激巨噬 | GSE165784 v2 sub14 (A 级实测) | HMOX1/FTL 亦被解离应激与血液存在驱动 —— 先排技术 |
| MHCII_high_APC | HLA-DRA, HLA-DRB1, CD74, HLA-DQA1, HLA-DPB1 | state | 支持 | human PDR membrane | vs MHCII-low mac | JCI Insight 2023 (PMID 37917183) APC 亚群 | HLA-DR 高≠树突状细胞身份; 单基因 CD74 受双细胞影响 |
| patho_endothelial | PLVAP, NDUFA4L2, HIF1A, ICAM1, VCAM1, DLL4, ESM1 | state | 支持 | human PDR membrane + 模型 | vs 静止内皮 | PLVAP/NDUFA4L2 低氧-血管通透性轴 (多文献) | DLL4 tip 亚态人膜直接证据不足 (C 级, 发育外推) |
| pericyte_to_myofibro | PRRX1, ACTA2, TAGLN, POSTN, COL1A1, COL1A2, CTHRC1, TIMP1 | identity+mechanism | 支持 | 视网膜纤维化病理 (含 PDR 膜) | vs 静止周细胞/静止纤维母 | PMID 41230906 (PRRX1-IOVS2025) 主图 | 连续转变谱 —— 强制二分会制造假亚型 (T4); '周细胞来源'与'纤维母来源'肌成纤维的区分需要谱系追踪, 转录混合不可判 |
| reactive_glia | GFAP, VIM, CRYAB, CLU, TIMP1 | state | 限定 | human retina/degeneration contexts | vs 稳态 MG/Astro | PMID 32069977 + 35167652 | GFAP 上调非特异 (创伤/应激/发育皆有); 膜标本胶质成分与 glial scar 预期一致 |
| blood_platelet | PPBP, PF4 | technical_artifact | 支持 | 任何手术材料 | — | markers_membrane_v1 血污面板 | 血小板转录reads 可来自 megakaryocyte 污染或 aggregates —— 只作旗不作群体 |

## 非预期旗 (含四分处置队列)

| 旗 | 触发条件 | 处置 | 队列 |
|---|---|---|---|
| 视网膜神经元 (Rod/Cone/BC/AC/HC) 大簇 | 膜标本 >5% | 旗标: 标本疑含视网膜本体, 报PI | candidate_biology |
| 光感受器外节/裂解碎片高背景 (HBA 除外) | 线粒体+ROS 应激签名弥散 | 解离应激旗, 不打疾病旗 | candidate_biology |
| progenitor/类器官特征 | 任何临床膜标本 | 疑样本混入/注释错误, 旗标上报 | candidate_biology |
| 肥大细胞/嗜酸粒细胞富集群 | 过敏背景 | unexpected-report | candidate_biology |
| 基线/文献清单外身份 (如意外的淋巴/髓外类群) | 任何簇无法归入已解析概念 | unexpected-report | out_of_baseline_coverage |

**队列语义**: 

- `out_of_baseline_coverage`: 超出基线覆盖范围 → 记录并评估是否扩基线 (回填 W1 映射)
- `conflicts_with_literature`: 与现有资料冲突 → 逐条引用核验 + 打架清单上报 PI
- `technical_suspect`: 技术可疑 (双细胞/ambient/应激) → 进 T1 技术可信度门复核队列
- `candidate_biology`: 候选生物学现象 → 走 T3 处置链 (确认观测→排技术→身份状态→临床上下文→独立验证)

## 污染旗

- **外周血 (经典单核 FCN1/LYZ/S100A8/9 + 血小板 PF4/PPBP + 中性粒 FCGR3B/CSF3R)** → 手术标本血液涌入 —— 髓系计数解读必须先扣血源成分 (B: GSE165784 v2 B10/sub14 A级实测)
- **RPE/脉络膜色素成分 (BEST1/RPE65/TYR+黑素)** → 穿透取材/合并孔源性脱离操作
- **玻璃体来源 T 优势 (对照 91.6%)** → 玻璃体切除标本残留液相成分

## 条目最小可用标准

条目最小可用标准 (Astra T4/P4): ①至少一条与该材料直接可比的身份或状态证据 (物种+材料+疾病条件写明) ②每条签名带出处+证据条件 ③无特异证据不单建亚型格子 ④名称合并只按表达程序/谱系/上下文, 不按文字相似度 (概念 ID 映射表) ⑤区间无法估计=合法状态, 不阻断条目成立。

开新格门槛: 新格子开建 = 有该 疾病×材料 的直接证据集; 批量铺宽暂缓 (T6), 等 PRIOR_DIFF 对照证明 D0 有用

## 注意事项

1. tip/stalk 内皮亚态: 人 PDR 膜直接单细胞证据有限 (DLL4+ tip 生物学多来自发育/OIR), 标 C 级 —— 预期存在但比例不设区间。
2. PDR 与 RRD 膜的组成差异尚无充分独立对照 —— 任何'疾病特异簇'判定必须做疾病端对照后才可写 (v2 草稿 RRD 分层教训)。
3. PI: PDR 注释本身不一定准 → 本先验为对照与 QC 旗, 非真值; 与数据冲突时输出'先验与数据打架清单'上报。
4. v1.1 (本条): 按 T4 重排为 身份层级+状态轴 两级; 旧 proliferative_DR.json 保留为 v1 存档 (copy 不 move)。
5. 概念 ID 映射 = 起步版 (17 概念), 不同文章命名不自动合并 —— 合并判据=表达程序/谱系/上下文 (T4)。

## 出处清单

| sid | 类型 | 标签 |
|---|---|---|
| `GSE165784V2` | dataset | GSE165784 人 PDR 纤维血管膜+RRD 膜 scRNA, v2 整合轨 Track B (harmonypy, 17 簇, 10,069 细胞; PDR-only 7,142) |
| `PDR_HU2022` | paper | Hu et al. Single-Cell Transcriptomics Reveals Novel Role of Microglia in Fibrovascular Membrane of PDR. Diabetes 2022 (GSE165784 原文) |
| `PDR_JCI2023` | paper | Single-cell transcriptomics analysis of PDR fibrovascular membranes. JCI Insight 2023 |
| `PDR_SOX15` | paper | Human single-cell atlas of PDR reveals a SOX15-overexpressing stromal population. J Transl Med 2026 |
| `PDR_MKI67MG` | paper | Single-cell analysis identifies MKI67+ microglia as drivers of neovascularization in PDR. J Transl Med 2025 |
| `PDR_NICHE` | paper | Metabolic reprogramming of the neovascular niche promotes regenerative angiogenesis in proliferative retinopathies. Nat Commun 2025 |
| `PRRX1` | paper | PRRX1 Orchestrates Pericyte-Myofibroblast Transition in Pathological Retinal Fibrosis. IOVS 2025 (库内) |
| `RAB5IF` | paper | Endothelial RAB5IF is required for pathological and developmental retinal angiogenesis. Nat Commun 2025 (库内) |
| `VITREOUS_T` | paper | Liquid Biopsy for PDR: Single-Cell Transcriptomics of Human Vitreous. Ophthalmol Sci 2024 — PDR 玻璃体 T 细胞 91.6% (对照组织: 玻璃体≠膜) |
| `MEMLIB` | kb | 本地膜 marker 库 markers_membrane_v1.json v1-membrane-20260923 (逐基因溯源) |
| `MULLER_REDD1` | paper | Müller Glial Expression of REDD1 Is Required for Retinal Neurodegeneration... Diabetes 2022 (库内; 反应性胶质背景) |
| `GLIA_RDG` | paper | scRNA-seq in Human Retinal Degeneration Reveals Distinct Glial Cell Populations. Cells 2020 (库内; 人视网膜退变胶质状态) |
| `DR_RETINA_SC` | paper | In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying DR. Sci Rep 2021 (库内) |
| `MG_EARLY_DR` | paper | scRNA-seq reveals roles of unique retinal microglia types in early DR. DMS 2024 (库内) |
| `TIPCELL_DEV` | paper | Specialized endothelial tip cells guide neuroretina vascularization and blood-retina-barrier formation. Nat Commun 2021 (库内; tip/stalk 生物学来源, 发育/模型证据→PDR 外推 C 级) |
