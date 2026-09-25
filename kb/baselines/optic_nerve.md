# 组成基线: 人(正常)视神经+视神经盘 snRNA adult-only 主档 (OA-D003 HRA006282, 供者级条件参考分布, KB2c 发育轴单列)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_optic_nerve` | 状态: filled_donor_level | 发育轴: **organism_stage=adult** | 生成: 2026-09-23 | 卡片: t_bad1fbab
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
- 两档身份: {'adult_only': 'baseline_human_optic_nerve__adult_only__kb2c', 'adult_pool': 'baseline_human_optic_nerve__adult_pool__v1.0'}

## Astra T2 元数据字段
- **取样材料**: 人视神经/视神经盘离体组织 (手术取材, 眼库供体; 区域构成: ONH (视神经盘/视乳头) 355,363核, ON (视神经) 604,266核)
- **疾病阶段**: normal (disease 列全 normal; 供者为系统性死亡捐献者, donor_cause_of_death 含肿瘤/脓毒症等, 眼球本身无眼病记录)
- **治疗背景**: 未记录 (眼库捐献元数据无治疗列) —— 标'未记录', 不臆测
- **scRNA_vs_snRNA**: snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes) —— 与 scRNA 细胞悬液条 (如 D002 眼表) 类比例不可直接互比
- **富集步骤**: 无分选记录 (metadata 无 enrichment 列; 全组织核悬液直接上机)
- **解离方法**: mechanical dissociation,enzymatic dissociation×813,508核; mechanical dissociation,centrifugation×146,121核 (sample_preservation=frozen in liquid nitrogen; collection=surgical resection)
- **供者数**: 主档 adult-only 74 donors / 98 供者单元; 对照档 adult_pool 83 donors / 107 单元 (含 9 非 adult 供者含 newborn 15,177 核 → 逐行见 excluded_nonadult_units)
- **计数分母**: 959,629 核 (majorclass 全标注)
- **证据来源**: 本地实测复算 (A) + CELLxGENE HRA006282 collection 官方注释 (portal) + 注册表 OA-D003

## 主参考: 供者级条件参考分布 (排除分选设计层)
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 0.0 | 0.0–1.58 | 0.0–6.7 | 98 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–1.31 | 98 |
| Astrocyte | 28.53 | 20.88–35.01 | 3.25–57.81 | 98 |
| BC | 0.0 | 0.0–7.58 | 0.0–24.76 | 98 |
| B_cell | 0.0 | 0.0–0.02 | 0.0–0.83 | 98 |
| Cone | 0.0 | 0.0–0.73 | 0.0–4.63 | 98 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 98 |
| Endothelial_cell | 3.08 | 1.53–4.88 | 0.0–29.36 | 98 |
| Fibroblast | 8.36 | 2.83–16.54 | 0.42–59.43 | 98 |
| HC | 0.0 | 0.0–1.2 | 0.0–3.44 | 98 |
| MG | 0.0 | 0.0–4.48 | 0.0–15.12 | 98 |
| Macrophage | 0.5 | 0.18–1.25 | 0.0–5.24 | 98 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 98 |
| Melanocyte | 0.0 | 0.0–0.22 | 0.0–19.45 | 98 |
| Microglia | 4.09 | 1.87–6.08 | 0.0–19.1 | 98 |
| Mural_cell | 1.39 | 0.66–2.43 | 0.0–11.76 | 98 |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 98 |
| Oligodendrocyte | 31.17 | 12.58–41.36 | 0.0–70.31 | 98 |
| Oligodendrocyte_precursor_cell | 0.51 | 0.02–2.72 | 0.0–8.05 | 98 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–8.31 | 98 |
| RGC | 0.0 | 0.0–0.49 | 0.0–2.79 | 98 |
| RPE | 0.0 | 0.0–0.61 | 0.0–22.5 | 98 |
| Rod | 0.0 | 0.0–8.64 | 0.0–52.58 | 98 |
| Schwann_cell | 0.06 | 0.0–0.27 | 0.0–2.15 | 98 |
| T_cell | 0.13 | 0.07–0.28 | 0.0–1.59 | 98 |

### 对照档 adult_pool (v1.0 混口径, 含非 adult 供者; tier=`baseline_human_optic_nerve__adult_pool__v1.0`) —— 引用 v1.0 旧数字只能挂此档身份

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 0.0 | 0.0–1.57 | 0.0–6.7 | 107 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–1.31 | 107 |
| Astrocyte | 28.94 | 21.17–35.39 | 3.25–70.08 | 107 |
| BC | 0.0 | 0.0–7.56 | 0.0–24.76 | 107 |
| B_cell | 0.01 | 0.0–0.02 | 0.0–0.83 | 107 |
| Cone | 0.0 | 0.0–0.61 | 0.0–4.63 | 107 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 107 |
| Endothelial_cell | 3.27 | 1.69–5.24 | 0.0–31.24 | 107 |
| Fibroblast | 8.92 | 3.24–16.72 | 0.42–59.43 | 107 |
| HC | 0.0 | 0.0–1.2 | 0.0–3.44 | 107 |
| MG | 0.0 | 0.0–3.72 | 0.0–15.12 | 107 |
| Macrophage | 0.51 | 0.2–1.28 | 0.0–5.24 | 107 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 107 |
| Melanocyte | 0.0 | 0.0–0.29 | 0.0–19.45 | 107 |
| Microglia | 4.08 | 1.8–6.3 | 0.0–19.1 | 107 |
| Mural_cell | 1.49 | 0.72–2.45 | 0.0–11.97 | 107 |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 107 |
| Oligodendrocyte | 27.96 | 10.59–40.67 | 0.0–70.31 | 107 |
| Oligodendrocyte_precursor_cell | 0.64 | 0.02–2.98 | 0.0–8.05 | 107 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–8.31 | 107 |
| RGC | 0.0 | 0.0–0.49 | 0.0–3.7 | 107 |
| RPE | 0.0 | 0.0–0.47 | 0.0–22.5 | 107 |
| Rod | 0.0 | 0.0–7.66 | 0.0–52.58 | 107 |
| Schwann_cell | 0.07 | 0.02–0.3 | 0.0–4.03 | 107 |
| T_cell | 0.13 | 0.06–0.28 | 0.0–1.59 | 107 |

### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)
| UBERON development_stage | organism_stage | 判级规则 | 核/细胞数 | 供者数 |
|---|---|---|---|---|
| 43-year-old stage | adult | 数字年龄 43y vs 阈值 18y | 78,263 | 3 |
| 69-year-old stage | adult | 数字年龄 69y vs 阈值 18y | 73,699 | 5 |
| 64-year-old stage | adult | 数字年龄 64y vs 阈值 18y | 68,748 | 5 |
| 71-year-old stage | adult | 数字年龄 71y vs 阈值 18y | 56,868 | 4 |
| 62-year-old stage | adult | 数字年龄 62y vs 阈值 18y | 54,875 | 3 |
| 67-year-old stage | adult | 数字年龄 67y vs 阈值 18y | 35,962 | 3 |
| 77-year-old stage | adult | 数字年龄 77y vs 阈值 18y | 32,893 | 5 |
| 65-year-old stage | adult | 数字年龄 65y vs 阈值 18y | 30,565 | 4 |
| 16-year-old stage | developing | 数字年龄 16y vs 阈值 18y | 27,212 | 3 |
| 72-year-old stage | adult | 数字年龄 72y vs 阈值 18y | 26,225 | 4 |
| 81-year-old stage | adult | 数字年龄 81y vs 阈值 18y | 23,537 | 2 |
| 70-year-old stage | adult | 数字年龄 70y vs 阈值 18y | 19,483 | 1 |
| 21-year-old stage | adult | 数字年龄 21y vs 阈值 18y | 19,210 | 1 |
| 10-year-old stage | developing | 数字年龄 10y vs 阈值 18y | 18,998 | 1 |
| 61-year-old stage | adult | 数字年龄 61y vs 阈值 18y | 18,682 | 2 |
| 42-year-old stage | adult | 数字年龄 42y vs 阈值 18y | 17,776 | 1 |
| 27-year-old stage | adult | 数字年龄 27y vs 阈值 18y | 16,928 | 2 |
| 32-year-old stage | adult | 数字年龄 32y vs 阈值 18y | 16,501 | 1 |
| 34-year-old stage | adult | 数字年龄 34y vs 阈值 18y | 16,364 | 2 |
| 25-year-old stage | adult | 数字年龄 25y vs 阈值 18y | 16,269 | 1 |
| 33-year-old stage | adult | 数字年龄 33y vs 阈值 18y | 16,010 | 1 |
| 18-year-old stage | adult | 数字年龄 18y vs 阈值 18y | 15,449 | 1 |
| newborn stage (0-28 days) | developing | newborn/infant 产后早期→developing (裁定 Q2) | 15,177 | 1 |
| 60-year-old stage | adult | 数字年龄 60y vs 阈值 18y | 14,758 | 2 |
| 76-year-old stage | adult | 数字年龄 76y vs 阈值 18y | 14,488 | 2 |
| 56-year-old stage | adult | 数字年龄 56y vs 阈值 18y | 14,406 | 1 |
| 30-year-old stage | adult | 数字年龄 30y vs 阈值 18y | 14,224 | 1 |
| 3-year-old stage | developing | 数字年龄 3y vs 阈值 18y | 13,748 | 1 |
| 85-year-old stage | adult | 数字年龄 85y vs 阈值 18y | 13,362 | 1 |
| 52-year-old stage | adult | 数字年龄 52y vs 阈值 18y | 13,317 | 1 |
| 15-year-old stage | developing | 数字年龄 15y vs 阈值 18y | 13,317 | 1 |
| 58-year-old stage | adult | 数字年龄 58y vs 阈值 18y | 12,874 | 2 |
| 47-year-old stage | adult | 数字年龄 47y vs 阈值 18y | 12,845 | 1 |
| 75-year-old stage | adult | 数字年龄 75y vs 阈值 18y | 12,130 | 1 |
| 82-year-old stage | adult | 数字年龄 82y vs 阈值 18y | 10,532 | 1 |
| 46-year-old stage | adult | 数字年龄 46y vs 阈值 18y | 10,451 | 1 |
| 68-year-old stage | adult | 数字年龄 68y vs 阈值 18y | 10,357 | 1 |
| 63-year-old stage | adult | 数字年龄 63y vs 阈值 18y | 8,965 | 1 |
| 90 year-old and over stage | adult | '90 year-old and over' 下界>=阈值 | 8,900 | 1 |
| 17-year-old stage | developing | 数字年龄 17y vs 阈值 18y | 8,175 | 1 |
| 45-year-old stage | adult | 数字年龄 45y vs 阈值 18y | 7,777 | 1 |
| 74-year-old stage | adult | 数字年龄 74y vs 阈值 18y | 7,776 | 1 |
| 54-year-old stage | adult | 数字年龄 54y vs 阈值 18y | 6,753 | 1 |
| 50-year-old stage | adult | 数字年龄 50y vs 阈值 18y | 4,676 | 1 |
| 37-year-old stage | adult | 数字年龄 37y vs 阈值 18y | 3,687 | 1 |
| 11-year-old stage | developing | 数字年龄 11y vs 阈值 18y | 3,443 | 1 |
| 53-year-old stage | adult | 数字年龄 53y vs 阈值 18y | 2,974 | 1 |

被剔出 adult 主档的供者 9 个: `MMD_23_17738`(developing, 10-year-old stage, 18,998核); `BCM_22_0698`(developing, newborn stage (0-28 days), 15,177核); `BCM_23_0491`(developing, 16-year-old stage, 14,845核); `MMD_23_22486`(developing, 3-year-old stage, 13,748核); `MMD_23_21623`(developing, 15-year-old stage, 13,317核); `BCM_23_0131`(developing, 16-year-old stage, 10,136核); `MMD_23_21999`(developing, 17-year-old stage, 8,175核); `BCM_22_0769`(developing, 11-year-old stage, 3,443核); `MMD_23_20181`(developing, 16-year-old stage, 2,231核)

## 工具兼容主表 (major_classes)
| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |
|---|---|---|---|---|---|---|
| AC | 0.0 | 0.0–1.58 | 0.0–6.7 | 1.15 |  | A |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–1.31 | 0.06 |  | A |
| Astrocyte | 28.53 | 20.88–35.01 | 3.25–57.81 | 28.52 |  | A |
| BC | 0.0 | 0.0–7.58 | 0.0–24.76 | 3.48 |  | A |
| B_cell | 0.0 | 0.0–0.02 | 0.0–0.83 | 0.04 |  | A |
| Cone | 0.0 | 0.0–0.73 | 0.0–4.63 | 0.45 |  | A |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 0.01 |  | A |
| Endothelial_cell | 3.08 | 1.53–4.88 | 0.0–29.36 | 3.64 |  | A |
| Fibroblast | 8.36 | 2.83–16.54 | 0.42–59.43 | 12.39 |  | A |
| HC | 0.0 | 0.0–1.2 | 0.0–3.44 | 0.5 |  | A |
| MG | 0.0 | 0.0–4.48 | 0.0–15.12 | 1.68 |  | A |
| Macrophage | 0.5 | 0.18–1.25 | 0.0–5.24 | 1.02 |  | A |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 0.02 |  | A |
| Melanocyte | 0.0 | 0.0–0.22 | 0.0–19.45 | 0.86 |  | A |
| Microglia | 4.09 | 1.87–6.08 | 0.0–19.1 | 5.01 |  | A |
| Mural_cell | 1.39 | 0.66–2.43 | 0.0–11.76 | 1.8 |  | A |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 0.04 |  | A |
| Oligodendrocyte | 31.17 | 12.58–41.36 | 0.0–70.31 | 28.97 |  | A |
| Oligodendrocyte_precursor_cell | 0.51 | 0.02–2.72 | 0.0–8.05 | 1.97 |  | A |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–8.31 | 0.28 |  | A |
| RGC | 0.0 | 0.0–0.49 | 0.0–2.79 | 0.37 |  | A |
| RPE | 0.0 | 0.0–0.61 | 0.0–22.5 | 0.89 |  | A |
| Rod | 0.0 | 0.0–8.64 | 0.0–52.58 | 6.32 |  | A |
| Schwann_cell | 0.06 | 0.0–0.27 | 0.0–2.15 | 0.22 |  | A |
| T_cell | 0.13 | 0.07–0.28 | 0.0–1.59 | 0.3 |  | A |

## 分层明细 (不同富集/部位先分层展示, 不跨层合并; KB2c: 各层表=adult-only, 括号内=层内 pool 供者数)
### 层: Chen|ON (视神经)  (n_donors=56, n_cells=551,898, 占图谱57.51%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 0.0 | 0.0–0.0 | 0.0–2.57 | 53 |
| Adipocyte | 0.0 | 0.0–0.07 | 0.0–1.31 | 53 |
| Astrocyte | 29.33 | 23.95–35.06 | 5.61–57.81 | 53 |
| BC | 0.0 | 0.0–0.0 | 0.0–8.17 | 53 |
| B_cell | 0.0 | 0.0–0.01 | 0.0–0.45 | 53 |
| Cone | 0.0 | 0.0–0.0 | 0.0–1.15 | 53 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.03 | 53 |
| Endothelial_cell | 4.18 | 2.96–5.58 | 0.38–29.36 | 53 |
| Fibroblast | 14.91 | 8.31–21.01 | 0.82–59.43 | 53 |
| HC | 0.0 | 0.0–0.0 | 0.0–1.43 | 53 |
| MG | 0.0 | 0.0–0.0 | 0.0–3.22 | 53 |
| Macrophage | 0.61 | 0.3–1.46 | 0.0–5.24 | 53 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.3 | 53 |
| Melanocyte | 0.0 | 0.0–0.0 | 0.0–0.09 | 53 |
| Microglia | 5.54 | 3.53–8.34 | 0.0–19.1 | 53 |
| Mural_cell | 2.26 | 1.56–3.01 | 0.09–11.76 | 53 |
| NK_cell | 0.02 | 0.0–0.04 | 0.0–0.24 | 53 |
| Oligodendrocyte | 37.35 | 26.3–41.64 | 0.0–63.55 | 53 |
| Oligodendrocyte_precursor_cell | 1.81 | 0.08–3.24 | 0.0–8.05 | 53 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–0.01 | 53 |
| RGC | 0.0 | 0.0–0.0 | 0.0–1.19 | 53 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.42 | 53 |
| Rod | 0.0 | 0.0–0.0 | 0.0–14.09 | 53 |
| Schwann_cell | 0.06 | 0.03–0.2 | 0.0–0.56 | 53 |
| T_cell | 0.14 | 0.07–0.27 | 0.0–1.48 | 53 |

### 层: Chen|ONH (视神经盘/视乳头)  (n_donors=31, n_cells=261,610, 占图谱27.26%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 1.96 | 0.93–4.79 | 0.0–6.69 | 25 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–0.04 | 25 |
| Astrocyte | 25.31 | 13.99–31.82 | 3.25–56.81 | 25 |
| BC | 8.64 | 4.3–13.6 | 0.0–24.76 | 25 |
| B_cell | 0.01 | 0.0–0.08 | 0.0–0.83 | 25 |
| Cone | 0.91 | 0.44–2.08 | 0.0–4.63 | 25 |
| Dendritic_cell | 0.0 | 0.0–0.01 | 0.0–0.09 | 25 |
| Endothelial_cell | 2.93 | 2.13–3.74 | 0.53–28.8 | 25 |
| Fibroblast | 7.14 | 3.58–9.55 | 1.08–21.25 | 25 |
| HC | 1.42 | 0.98–2.06 | 0.0–3.44 | 25 |
| MG | 6.55 | 2.92–8.13 | 0.0–15.12 | 25 |
| Macrophage | 0.8 | 0.28–1.5 | 0.06–3.33 | 25 |
| Mast_cell | 0.0 | 0.0–0.01 | 0.0–0.25 | 25 |
| Melanocyte | 0.69 | 0.21–1.26 | 0.0–19.45 | 25 |
| Microglia | 2.45 | 1.3–4.35 | 0.34–9.81 | 25 |
| Mural_cell | 1.03 | 0.78–1.41 | 0.18–3.98 | 25 |
| NK_cell | 0.01 | 0.0–0.03 | 0.0–0.23 | 25 |
| Oligodendrocyte | 9.37 | 1.63–20.06 | 0.0–45.17 | 25 |
| Oligodendrocyte_precursor_cell | 0.03 | 0.0–0.34 | 0.0–6.44 | 25 |
| Pigmented_cell | 0.03 | 0.0–0.11 | 0.0–8.31 | 25 |
| RGC | 0.84 | 0.14–1.95 | 0.0–2.79 | 25 |
| RPE | 1.38 | 0.64–2.08 | 0.0–22.5 | 25 |
| Rod | 13.31 | 4.11–19.31 | 0.05–44.85 | 25 |
| Schwann_cell | 0.14 | 0.02–0.42 | 0.0–1.33 | 25 |
| T_cell | 0.17 | 0.09–0.43 | 0.0–1.59 | 25 |

### 层: Sanes|ON (视神经)  (n_donors=7, n_cells=52,368, 占图谱5.46%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–0.15 | 7 |
| Astrocyte | 32.62 | 30.91–35.64 | 16.61–44.89 | 7 |
| BC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| B_cell | 0.0 | 0.0–0.0 | 0.0–0.02 | 7 |
| Cone | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Dendritic_cell | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Endothelial_cell | 0.28 | 0.14–0.52 | 0.0–1.57 | 7 |
| Fibroblast | 2.05 | 1.46–2.49 | 0.42–6.79 | 7 |
| HC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| MG | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Macrophage | 0.09 | 0.03–0.12 | 0.0–0.24 | 7 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Melanocyte | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Microglia | 4.36 | 4.11–6.37 | 3.17–8.2 | 7 |
| Mural_cell | 0.05 | 0.02–0.16 | 0.0–0.82 | 7 |
| NK_cell | 0.0 | 0.0–0.0 | 0.0–0.03 | 7 |
| Oligodendrocyte | 54.62 | 53.48–57.6 | 41.15–70.31 | 7 |
| Oligodendrocyte_precursor_cell | 4.89 | 1.68–5.15 | 0.12–6.39 | 7 |
| Pigmented_cell | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| RGC | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Rod | 0.0 | 0.0–0.0 | 0.0–0.0 | 7 |
| Schwann_cell | 0.0 | 0.0–0.0 | 0.0–0.16 | 7 |
| T_cell | 0.01 | 0.0–0.05 | 0.0–0.1 | 7 |

### 层: Sanes|ONH (视神经盘/视乳头)  (n_donors=13, n_cells=93,753, 占图谱9.77%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 4.86 | 3.82–5.96 | 0.0–6.7 | 13 |
| Adipocyte | 0.0 | 0.0–0.0 | 0.0–0.05 | 13 |
| Astrocyte | 17.52 | 11.02–31.21 | 8.23–56.59 | 13 |
| BC | 14.5 | 7.28–16.49 | 0.0–18.76 | 13 |
| B_cell | 0.02 | 0.0–0.03 | 0.0–0.21 | 13 |
| Cone | 1.83 | 0.08–2.23 | 0.0–2.94 | 13 |
| Dendritic_cell | 0.0 | 0.0–0.0 | 0.0–0.01 | 13 |
| Endothelial_cell | 0.95 | 0.82–1.38 | 0.51–1.78 | 13 |
| Fibroblast | 1.5 | 1.05–2.52 | 0.51–9.42 | 13 |
| HC | 2.1 | 1.28–2.53 | 0.0–2.9 | 13 |
| MG | 5.66 | 3.34–6.13 | 0.0–12.88 | 13 |
| Macrophage | 0.17 | 0.14–0.27 | 0.0–1.85 | 13 |
| Mast_cell | 0.0 | 0.0–0.0 | 0.0–0.1 | 13 |
| Melanocyte | 0.22 | 0.09–0.3 | 0.0–2.19 | 13 |
| Microglia | 1.06 | 0.82–2.33 | 0.36–3.08 | 13 |
| Mural_cell | 0.48 | 0.33–0.79 | 0.23–1.73 | 13 |
| NK_cell | 0.03 | 0.02–0.06 | 0.0–0.08 | 13 |
| Oligodendrocyte | 14.25 | 8.97–20.24 | 0.0–58.03 | 13 |
| Oligodendrocyte_precursor_cell | 0.06 | 0.03–0.5 | 0.0–1.5 | 13 |
| Pigmented_cell | 0.0 | 0.0–0.01 | 0.0–0.28 | 13 |
| RGC | 0.69 | 0.58–1.36 | 0.0–2.72 | 13 |
| RPE | 0.42 | 0.37–1.4 | 0.0–2.67 | 13 |
| Rod | 32.98 | 7.26–41.31 | 0.0–52.58 | 13 |
| Schwann_cell | 0.09 | 0.0–0.25 | 0.0–2.15 | 13 |
| T_cell | 0.13 | 0.1–0.3 | 0.04–0.97 | 13 |

## 亚型层 (类内注释细胞占比%, pooled within class 口径)

## 旗标语义
**expected_low_but_present**: T/B/NK/DC/Mast 合计 <1% (正常神经组织免疫稀少); Schwann_cell 0.22% (PN 髓鞘支持细胞; 核悬液下 PN 富集度受限于中枢段); Mural_cell 1.8% / Endothelial_cell 3.6% (血管支持层)

**unexpected**: 视网膜神经元类 (Rod/Cone/BC/HC/AC/RGC) pooled 12.27% + RPE/色素类 1.17% —— 视盘取材带入盘旁视网膜/脉络膜组织, 属捕获构成非视神经本体真组成; 疾病样本对照时不得把该层当'视神经应有比例'

**contamination_suspect**: Melanocyte 0.86% (软脑膜/色素组织附带, 正常范围内偏高需结合取材平面解读)

## 注意事项
1. MG=Müller 胶质细胞 (1.7%) 与 Microglia=小胶质细胞 (5.0%) 为两套不同身份, portal 词表并存 —— 下游引用勿混; 同规则适用 AC(无长细胞)/BC(双极细胞)等视网膜缩写。
2. Chen (Baylor, ~85%) 与 Sanes (Harvard) 两供体池规模悬殊, 已按 来源×部位 分 4 层展示; main 供者级每单元等权, 大池不再压秤, 但层间差异需看 strata 而非只看 main。
3. 本条计数分母含视盘旁视网膜来源类 (~15%); 如需'纯视神经'参考区间, 用 strata 中 ON (cranial nerve II) 层。
4. snRNA 口径 (核悬液, 内含子 reads 计入) 与 scRNA 数据比较须谨慎 (Astra T2)。
5. v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y, 裁定 Q2); v1.0 混口径 (含 newborn/3-17 岁) 保留于 donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), 两档身份签名分离不混用。

## 出处清单
| sid | 类型 | 标签 |
|---|---|---|
| `ON_LOCAL` | dataset | 本地文件 /mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad  |
| `ON_PORTAL` | dataset | Human Optic Nerve / Optic Nerve Head Atlas, CELLxGENE collection HRA006282 (portal 官方注释; registry OA-D003, verified 2026-08-11)  |

