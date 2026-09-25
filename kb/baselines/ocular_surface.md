# 组成基线: 人(正常)眼表 adult-only 主档 — 角膜/limbus/巩膜超级类 (D002, 供者级条件参考分布, KB2c 发育轴单列)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_ocular_surface` | 状态: filled_donor_level | 发育轴: **organism_stage=adult** | 生成: 2026-09-23 | 卡片: t_16c3e020
> **KB3 发育档 (卡片 t_5425a7ca)**: development_stage=**adult** —— KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。
> 本文件由 `/mnt/D/EyeKB/scripts/baselines/build_baselines.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。

**用途口径 (Astra T2 裁定固化): 本基线 = 该取样材料在该实验流程下捕获到的细胞构成的身份参考 + 背景对照; **不得当组成达标线**。疾病手术材料的取样对象 ≠ 健康器官 (如 PDR 纤维血管膜不得对照健康视网膜组成验收); 注释数据出现清单外身份 → 触发 unexpected 旗即可, 不得强制改成清单内身份 (标签接受上下文一致性核查, 非白名单定位)。**

## 证据等级口径
- **A**: 本地实测复算 (带文件路径+脚本)
- **B**: 文献原文直接报告
- **C**: A 级源数据供者级/跨研究分布推得的经验区间
- **qualitative**: 文献仅定性描述 → 只存定性, 不补造区间 (Astra T2)
- **not_estimable**: 区间无法估计 —— 合法状态, 注释仍可开展 (Astra T2)

## 发育轴口径 (KB2c 裁定 2026-09-23 — 阈值改动须过裁定)
- 顶层轴: `organism_stage` ∈ ['fetal', 'adult', 'developing', 'unknown']
- **adult**: UBERON development_stage 数字化年龄 >= 18y 判 adult; 显式成年术语 (late/prime/middle/mature/human adult stage, 年代段>=3rd) 亦判 adult 并记 rule; 阈值改动须过裁定 (KB2c Q2, 2026-09-23)
- **developing**: newborn/infant/postnatal stage 与 <18y 数字年龄/年龄段 → developing (KB2c Q2)
- **fetal**: fetal/embryonic/gestation/Carnegie 术语 → fetal; 永不并入 adult 主档 (红线1)
- **unknown**: 无年龄列/未映射术语/organoid/年龄段跨阈值 → unknown, 必须披露行, 禁静默归 adult (红线2)
- aging 正交轴: >=60 老年分层不在本轴 — aging 是正交独立轴, 将来单独立条目 (裁定 Q2)
- 两档身份: {'adult_only': 'baseline_human_ocular_surface__adult_only__kb2c', 'adult_pool': 'baseline_human_ocular_surface__adult_pool__v1.0'}

## Astra T2 元数据字段
- **取样材料**: 人眼表离体组织: cornea / corneo-scleral junction(limbus) / sclera / ocular surface region / corneal endothelium (移植角膜内皮边缘碎块)
- **疾病阶段**: normal (disease 列全 normal; 供者为眼库捐献角膜缘/巩膜环)
- **治疗背景**: 未记录 (眼库捐献元数据无治疗列)
- **平台**: scRNA-seq (suspension_type=cell 100%, 10x 3' v2/v3) —— 与 D001 retina(核) 不同口径, 跨基线比较注意
- **富集步骤**: 无细胞分选记录 (全组织解离直接上机)
- **解离方法**: 机械+酶解离; 主要试剂: 2 mg/ml Collagenase A×206,010细胞; 1.5 mg/ml Collagenase A×166,417细胞; 2.5 mg/ml Collagenase A×88,531细胞; 5 mg/ml collagenase A×46,892细胞
- **供者数**: 主档 adult-only 41 donors / 67 供者单元; 对照档 adult_pool 50 donors / 84 单元 (含 9 非 adult 供者如 newborn 0-28d → 逐行见 excluded_nonadult_units)
- **计数分母**: 577,857 cells (majorclass 全标注)
- **证据来源**: 本地实测复算 (A) + CELLxGENE collection 官方注释 (portal)

## 主参考: 供者级条件参考分布 (排除分选设计层)
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–100.0 | 67 |
| Endothelium | 3.42 | 0.0–8.99 | 0.0–43.48 | 67 |
| Epithelium | 50.48 | 7.26–70.25 | 0.0–99.62 | 67 |
| Fibroblasts | 28.53 | 12.65–44.01 | 0.0–93.77 | 67 |
| Immune Cells | 1.12 | 0.4–2.6 | 0.0–37.71 | 67 |
| Melanocytes | 0.29 | 0.0–2.45 | 0.0–48.63 | 67 |
| Pericytes | 2.03 | 0.0–4.27 | 0.0–41.31 | 67 |
| Schwann Cells | 0.23 | 0.0–1.06 | 0.0–20.52 | 67 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–63.33 | 67 |


### 角膜基质 Keratocyte 参考格 (卡片 t_e1febb8e, 2026-09-24 追加; astra R5 修订版)
> 根因: KB2 Q6::15 (ALDH3A1+KERA) 系统性误标 Corneal Endothelium。本格=证据覆盖/层级映射修复的组成侧; 不新增 major_classes 行 (避免与 Fibroblasts 超类重复计数)。
- **D002 实测 (A 级, 主档同口径)**: adult 67 供者单元; keratocyte 标签类内 pooled 23.42%, 单元中位 20.68% [IQR 6.19–40.26, range 0–91.19]; 分母=D002 混合眼表捕获事件 (cornea 组), 非独立验证身份、非纯 cornea 组织真值、不作达标线。全文件 (含非 adult) 口径 17.95% 仅存档工作区。
- **文献范围格**: 缺项落阻塞 (可定位正文级百分比区间未钉死; 共聚焦密度口径不得冒充组成百分比) —— 见 JSON stromal_keratocyte_reference.literature_anchor。
- **配套**: marker 库补录 (Keratocytes/Corneal Endothelium, v1-membrane-20260924-r2) + 概念条 EYEKBC-0018/0019; 层级关系: Keratocytes ⊂ Fibroblasts 超类 (Q6 体系)。

### 对照档 adult_pool (v1.0 混口径, 含非 adult 供者; tier=`baseline_human_ocular_surface__adult_pool__v1.0`) —— 引用 v1.0 旧数字只能挂此档身份

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–100.0 | 84 |
| Endothelium | 3.32 | 0.0–8.89 | 0.0–43.48 | 84 |
| Epithelium | 51.18 | 6.97–71.49 | 0.0–99.62 | 84 |
| Fibroblasts | 29.96 | 13.76–53.83 | 0.0–93.77 | 84 |
| Immune Cells | 1.1 | 0.41–2.28 | 0.0–37.71 | 84 |
| Melanocytes | 0.27 | 0.0–2.17 | 0.0–48.63 | 84 |
| Pericytes | 2.27 | 0.0–6.01 | 0.0–41.31 | 84 |
| Schwann Cells | 0.23 | 0.0–1.14 | 0.0–20.52 | 84 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–63.33 | 84 |

### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)
| UBERON development_stage | organism_stage | 判级规则 | 核/细胞数 | 供者数 |
|---|---|---|---|---|
| 64-year-old stage | adult | 数字年龄 64y vs 阈值 18y | 56,324 | 3 |
| 43-year-old stage | adult | 数字年龄 43y vs 阈值 18y | 45,727 | 2 |
| 32-year-old stage | adult | 数字年龄 32y vs 阈值 18y | 39,770 | 1 |
| 72-year-old stage | adult | 数字年龄 72y vs 阈值 18y | 30,149 | 1 |
| 2-year-old stage | developing | 数字年龄 2y vs 阈值 18y | 27,157 | 1 |
| 25-year-old stage | adult | 数字年龄 25y vs 阈值 18y | 26,051 | 1 |
| newborn stage (0-28 days) | developing | newborn/infant 产后早期→developing (裁定 Q2) | 25,018 | 1 |
| 1-year-old stage | developing | 数字年龄 1y vs 阈值 18y | 23,364 | 1 |
| 55-year-old stage | adult | 数字年龄 55y vs 阈值 18y | 22,600 | 1 |
| 67-year-old stage | adult | 数字年龄 67y vs 阈值 18y | 22,556 | 1 |
| 11-year-old stage | developing | 数字年龄 11y vs 阈值 18y | 22,308 | 1 |
| 70-year-old stage | adult | 数字年龄 70y vs 阈值 18y | 21,432 | 1 |
| 87-year-old stage | adult | 数字年龄 87y vs 阈值 18y | 19,901 | 1 |
| 61-year-old stage | adult | 数字年龄 61y vs 阈值 18y | 19,093 | 2 |
| 51-year-old stage | adult | 数字年龄 51y vs 阈值 18y | 17,436 | 2 |
| 10-year-old stage | developing | 数字年龄 10y vs 阈值 18y | 15,667 | 1 |
| 27-year-old stage | adult | 数字年龄 27y vs 阈值 18y | 15,052 | 1 |
| 34-year-old stage | adult | 数字年龄 34y vs 阈值 18y | 12,347 | 1 |
| 53-year-old stage | adult | 数字年龄 53y vs 阈值 18y | 11,393 | 1 |
| 75-year-old stage | adult | 数字年龄 75y vs 阈值 18y | 10,823 | 4 |
| postnatal stage | developing | postnatal→developing (裁定 Q1 映射) | 10,550 | 2 |
| 65-year-old stage | adult | 数字年龄 65y vs 阈值 18y | 9,813 | 1 |
| 41-year-old stage | adult | 数字年龄 41y vs 阈值 18y | 8,904 | 1 |
| 13-year-old stage | developing | 数字年龄 13y vs 阈值 18y | 8,281 | 1 |
| 90 year-old and over stage | adult | '90 year-old and over' 下界>=阈值 | 7,997 | 1 |
| 74-year-old stage | adult | 数字年龄 74y vs 阈值 18y | 7,504 | 1 |
| 33-year-old stage | adult | 数字年龄 33y vs 阈值 18y | 7,159 | 1 |
| 69-year-old stage | adult | 数字年龄 69y vs 阈值 18y | 6,063 | 1 |
| 84-year-old stage | adult | 数字年龄 84y vs 阈值 18y | 4,320 | 2 |
| 86-year-old stage | adult | 数字年龄 86y vs 阈值 18y | 4,293 | 2 |
| 77-year-old stage | adult | 数字年龄 77y vs 阈值 18y | 3,352 | 1 |
| 48-year-old stage | adult | 数字年龄 48y vs 阈值 18y | 3,224 | 1 |
| 62-year-old stage | adult | 数字年龄 62y vs 阈值 18y | 3,047 | 1 |
| 22-year-old stage | adult | 数字年龄 22y vs 阈值 18y | 2,533 | 1 |
| 16-year-old stage | developing | 数字年龄 16y vs 阈值 18y | 2,245 | 1 |
| 45-year-old stage | adult | 数字年龄 45y vs 阈值 18y | 1,879 | 1 |
| 83-year-old stage | adult | 数字年龄 83y vs 阈值 18y | 1,595 | 1 |
| 39-year-old stage | adult | 数字年龄 39y vs 阈值 18y | 732 | 1 |
| eighth decade stage | adult | eighth decade = 70-79y 下界>=阈值 | 198 | 1 |

被剔出 adult 主档的供者 9 个: `BCM_22_0496`(developing, 2-year-old stage, 27,157核); `BCM_22_0698`(developing, newborn stage (0-28 days), 25,018核); `BCM_22_0485`(developing, 1-year-old stage, 23,364核); `BCM_22_0769`(developing, 11-year-old stage, 22,308核); `BCM_21_0999`(developing, 10-year-old stage, 15,667核); `shi_donor1`(developing, 13-year-old stage, 8,281核); `chen_donor1`(developing, postnatal stage, 6,249核); `chen_donor2`(developing, postnatal stage, 4,301核); `BCM_23_0131`(developing, 16-year-old stage, 2,245核)

## 工具兼容主表 (major_classes)
| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |
|---|---|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–100.0 | 0.07 |  | A |
| Endothelium | 3.42 | 0.0–8.99 | 0.0–43.48 | 5.76 |  | A |
| Epithelium | 50.48 | 7.26–70.25 | 0.0–99.62 | 43.32 |  | A |
| Fibroblasts | 28.53 | 12.65–44.01 | 0.0–93.77 | 39.84 |  | A |
| Immune Cells | 1.12 | 0.4–2.6 | 0.0–37.71 | 1.73 |  | A |
| Melanocytes | 0.29 | 0.0–2.45 | 0.0–48.63 | 1.25 |  | A |
| Pericytes | 2.03 | 0.0–4.27 | 0.0–41.31 | 6.49 |  | A |
| Schwann Cells | 0.23 | 0.0–1.06 | 0.0–20.52 | 1.05 |  | A |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–63.33 | 0.48 |  | A |

## 分层明细 (不同富集/部位先分层展示, 不跨层合并; KB2c: 各层表=adult-only, 括号内=层内 pool 供者数)
### 层: |cornea (含角膜上皮/固有质)  (n_donors=34, n_cells=218,598)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–2.64 | 29 |
| Endothelium | 0.0 | 0.0–1.35 | 0.0–15.6 | 29 |
| Epithelium | 63.08 | 29.31–79.27 | 4.83–99.62 | 29 |
| Fibroblasts | 32.09 | 14.88–67.25 | 0.0–93.77 | 29 |
| Immune Cells | 0.55 | 0.31–1.58 | 0.0–9.5 | 29 |
| Melanocytes | 0.0 | 0.0–0.71 | 0.0–6.6 | 29 |
| Pericytes | 0.0 | 0.0–0.25 | 0.0–3.72 | 29 |
| Schwann Cells | 0.0 | 0.0–0.0 | 0.0–3.31 | 29 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–0.64 | 29 |

### 层: |corneal endothelium (单独层, 仅 404 细胞)  (n_donors=2, n_cells=404)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 100.0 | 100.0–100.0 | 100.0–100.0 | 2 |
| Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Epithelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Fibroblasts | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Immune Cells | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Melanocytes | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Pericytes | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Schwann Cells | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–0.0 | 2 |

### 层: |corneo-scleral junction (limbus 区)  (n_donors=28, n_cells=244,108)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 22 |
| Endothelium | 7.25 | 5.38–12.02 | 0.92–18.67 | 22 |
| Epithelium | 58.44 | 36.9–67.75 | 0.0–91.73 | 22 |
| Fibroblasts | 26.39 | 7.23–37.8 | 0.0–89.24 | 22 |
| Immune Cells | 1.8 | 0.85–2.66 | 0.23–37.71 | 22 |
| Melanocytes | 1.66 | 0.31–4.75 | 0.0–21.21 | 22 |
| Pericytes | 3.71 | 2.58–6.07 | 0.0–19.37 | 22 |
| Schwann Cells | 0.7 | 0.23–1.06 | 0.0–20.52 | 22 |
| Smooth Muscle Cells | 0.0 | 0.0–0.0 | 0.0–11.81 | 22 |

### 层: |ocular surface region (混合)  (n_donors=4, n_cells=14,934)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 4 |
| Endothelium | 5.1 | 3.98–6.51 | 2.45–8.9 | 4 |
| Epithelium | 58.19 | 48.71–67.9 | 43.42–73.92 | 4 |
| Fibroblasts | 23.07 | 17.06–30.8 | 16.93–36.1 | 4 |
| Immune Cells | 4.95 | 3.7–5.87 | 2.2–6.4 | 4 |
| Melanocytes | 0.71 | 0.28–3.28 | 0.0–9.99 | 4 |
| Pericytes | 2.11 | 1.93–2.59 | 1.63–3.79 | 4 |
| Schwann Cells | 0.86 | 0.55–1.26 | 0.27–1.82 | 4 |
| Smooth Muscle Cells | 0.53 | 0.05–1.04 | 0.03–1.13 | 4 |

### 层: |sclera  (n_donors=16, n_cells=99,813)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| Corneal Endothelium | 0.0 | 0.0–0.0 | 0.0–0.0 | 10 |
| Endothelium | 11.88 | 8.63–17.21 | 6.56–43.48 | 10 |
| Epithelium | 0.15 | 0.0–2.71 | 0.0–9.73 | 10 |
| Fibroblasts | 40.45 | 34.26–51.56 | 3.04–77.02 | 10 |
| Immune Cells | 1.16 | 0.51–4.4 | 0.0–22.81 | 10 |
| Melanocytes | 0.27 | 0.0–5.71 | 0.0–48.63 | 10 |
| Pericytes | 16.4 | 12.88–34.62 | 0.0–41.31 | 10 |
| Schwann Cells | 1.64 | 0.28–2.24 | 0.0–3.85 | 10 |
| Smooth Muscle Cells | 0.0 | 0.0–0.41 | 0.0–63.33 | 10 |

## 亚型层 (类内注释细胞占比%, pooled within class 口径)
- **Fibroblasts**: Corneal Stromal Keratocytes 45.1%; Limbus Fibroblasts 18.3%; Limbus/Sclera Fibroblasts - C2 18.3%; Limbus/Sclera Fibroblasts - C1 14.3%; Sclera Fibroblasts 4.0%
- **Epithelium**: Corneal_superficial_TDC 25.4%; Corneal_suprabasal_PMC 18.2%; Limbus_suprabasal_eTAC_ConjFate 11.8%; Limbus_suprabasal_eTAC_CorFate 11.5%; Limbus_basal_LSC/LPC 11.0%; Conj_basal 7.5%
- **Pericytes**: Pericytes 100.0%
- **Endothelium**: Venule_Sclera 53.4%; Capillary 16.4%; Venule_postCapillary 16.3%; Lymphatic_Endo 10.3%; Artery 3.6%
- **Schwann Cells**: Schwann_N 89.2%; Schwann_M 10.8%
- **Immune Cells**: Macrophages 49.6%; NK/T Cells 39.4%; Mast Cells 6.3%; Monocytes 2.5%; B Cells 2.1%
- **Melanocytes**: Melanocytes 100.0%
- **Smooth Muscle Cells**: Smooth Muscle Cells 100.0%
- **Corneal Endothelium**: Corneal_Endo 100.0%

## 旗标语义
**expected_low_but_present**: Corneal Endothelium (pooled 0.07%) —— 仅眼库内皮边缘碎块贡献, 常规角膜缘样本近零; Melanocytes/Schwann Cells/Smooth Muscle Cells <2%

**unexpected**: 光感受器/视网膜神经元类出现 (取材越界到视网膜?); 大量造血成熟标志 (FCN1/LYZ 粒系) —— 供体血液残留旗

**contamination_suspect**: published_annotation 列含 red blood cells 主导层 (525,617 标注) —— 血液残留是本库已知主污染, 见 caveat; 黑素颗粒/色素组织污染 (色素性供者巩膜)

## 注意事项
1. 本地 D002 文件 = 577,857 cells / 50 donors, 为 collection 级 (>1M/102) 的子集提取 (口径=本地实测); 回填全 collection 需下载审批, 列'待回填'。
2. 'Majorclass=Immune Cells' 仅 1.7%: 眼表固有免疫稀少 + 无免疫富集步骤 —— 免疫比例不可对照炎症疾病样本。
3. published_annotation 与 majorclass 并存: published_annotation='red blood cells' 占大头说明 RBC 未从 majorclass 里剔除干净? 不 —— majorclass 9 类无 RBC 类, RBC 信号散入各类, 计数分母含 RBC 污染核, 各类% 为'捕获事件构成'非组织真值 (Astra T2 口径声明)。
4. sclera/conjunctiva 独立条目见对应骨架文件; 本条 corneo-scleral junction 层 ≠ 独立结膜基线。
5. v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y); v1.0 混口径 (含 newborn 0-28d 25,018 细胞 + postnatal/儿童青少年) 保留于 donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0)。FALLBACK_BLOCKED 守卫已实装（组织组 0 adult 供者时触发禁回退）——本次实测 0 层触发, 各组织组 adult-only 均有真实支撑。

## 出处清单
| sid | 类型 | 标签 |
|---|---|---|
| `D002_LOCAL` | dataset | 本地文件 /mnt/D/OcularKB/data/D002_ocularsurface/D002_allcells_578K.h5ad  |
| `D002_PORTAL` | dataset | Human Ocular Surface Cell Atlas, CELLxGENE collection (portal 官方注释)  |

