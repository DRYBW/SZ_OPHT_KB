# 组成基线: 人(正常)ciliary_body snRNA adult-only 主档 (ciliary_body 切片 863,922 核 / 59 供者, 供者级条件参考分布, KB2c 发育轴单列)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_ciliary_body` | 状态: filled_donor_level | 发育轴: **organism_stage=adult** | 生成: 2026-09-23 | 卡片: t_bad1fbab
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
- 两档身份: {'adult_only': 'baseline_human_ciliary_body__adult_only__kb2c', 'adult_pool': 'baseline_human_ciliary_body__adult_pool__v1.0'}

## Astra T2 元数据字段
- **取样材料**: 人前节段手术取材中 ciliary_body 解剖组分 (tissue 列='ciliary body' 切片; 另有 uvea 分量 53,406 核未入本条)
- **疾病阶段**: normal (disease 列全 normal; 供者系统性死亡眼库/手术材料)
- **治疗背景**: 未记录 (元数据无治疗列) —— 标'未记录', 不臆测
- **scRNA_vs_snRNA**: snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes)
- **富集步骤**: 无分选记录 (全组织核悬液直接上机)
- **解离方法**: mechanical dissociation,detergent solubilization×824,681核; mechanical dissociation,centrifugation×29,948核; mechanical dissociation,enzymatic dissociation×9,293核 (sample_collection_method=surgical resection)
- **供者数**: 主档 adult-only 55 donors / 55 供者单元; 对照档 adult_pool 59 donors / 59 单元 (含 4 非 adult 供者 → 逐行见 excluded_nonadult_units)
- **计数分母**: 863,922 核 (ciliary_body 切片内 majorclass 全标注)
- **证据来源**: 本地实测复算 (A) + portal/HASA 官方注释 (t_6f5cc731 判 'portal官方')

## 主参考: 供者级条件参考分布 (排除分选设计层)
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 17.9 | 15.08–21.31 | 5.94–41.57 | 55 |
| CB_PCE | 28.51 | 23.96–33.84 | 2.68–56.55 | 55 |
| Ciliary_Muscle | 16.25 | 12.18–19.03 | 3.9–32.03 | 55 |
| Endothelium | 2.08 | 1.63–2.55 | 0.0–4.36 | 55 |
| Fibroblast | 14.45 | 11.2–16.83 | 2.59–25.78 | 55 |
| Immune Cell | 4.72 | 3.35–6.61 | 1.18–18.99 | 55 |
| Melanocyte | 5.96 | 4.98–7.4 | 0.0–10.43 | 55 |
| Pericyte | 0.67 | 0.52–0.74 | 0.0–1.07 | 55 |
| Schwann Cell | 7.44 | 6.18–8.51 | 0.18–12.97 | 55 |

### 对照档 adult_pool (v1.0 混口径, 含非 adult 供者; tier=`baseline_human_ciliary_body__adult_pool__v1.0`) —— 引用 v1.0 旧数字只能挂此档身份

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 17.87 | 14.83–21.31 | 2.51–41.57 | 59 |
| CB_PCE | 28.51 | 23.89–34.67 | 2.47–57.12 | 59 |
| Ciliary_Muscle | 16.25 | 11.79–19.41 | 3.9–32.03 | 59 |
| Endothelium | 2.2 | 1.66–2.61 | 0.0–9.65 | 59 |
| Fibroblast | 14.45 | 10.31–16.83 | 2.59–32.46 | 59 |
| Immune Cell | 4.72 | 3.35–6.34 | 1.18–18.99 | 59 |
| Melanocyte | 5.96 | 4.88–7.67 | 0.0–15.38 | 59 |
| Pericyte | 0.65 | 0.52–0.74 | 0.0–1.65 | 59 |
| Schwann Cell | 7.44 | 6.08–8.51 | 0.18–12.97 | 59 |

### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)
| UBERON development_stage | organism_stage | 判级规则 | 核/细胞数 | 供者数 |
|---|---|---|---|---|
| 62-year-old stage | adult | 数字年龄 62y vs 阈值 18y | 64,491 | 3 |
| 71-year-old stage | adult | 数字年龄 71y vs 阈值 18y | 58,911 | 4 |
| 69-year-old stage | adult | 数字年龄 69y vs 阈值 18y | 52,817 | 3 |
| 64-year-old stage | adult | 数字年龄 64y vs 阈值 18y | 49,788 | 2 |
| 46-year-old stage | adult | 数字年龄 46y vs 阈值 18y | 38,633 | 1 |
| 72-year-old stage | adult | 数字年龄 72y vs 阈值 18y | 38,322 | 4 |
| 53-year-old stage | adult | 数字年龄 53y vs 阈值 18y | 37,753 | 2 |
| 58-year-old stage | adult | 数字年龄 58y vs 阈值 18y | 34,884 | 2 |
| 67-year-old stage | adult | 数字年龄 67y vs 阈值 18y | 33,062 | 2 |
| 16-year-old stage | developing | 数字年龄 16y vs 阈值 18y | 32,061 | 2 |
| 70-year-old stage | adult | 数字年龄 70y vs 阈值 18y | 30,580 | 1 |
| 77-year-old stage | adult | 数字年龄 77y vs 阈值 18y | 26,976 | 2 |
| 65-year-old stage | adult | 数字年龄 65y vs 阈值 18y | 26,593 | 2 |
| 60-year-old stage | adult | 数字年龄 60y vs 阈值 18y | 23,870 | 2 |
| 18-year-old stage | adult | 数字年龄 18y vs 阈值 18y | 23,862 | 1 |
| 68-year-old stage | adult | 数字年龄 68y vs 阈值 18y | 23,269 | 3 |
| 56-year-old stage | adult | 数字年龄 56y vs 阈值 18y | 20,318 | 1 |
| 17-year-old stage | developing | 数字年龄 17y vs 阈值 18y | 17,548 | 1 |
| 81-year-old stage | adult | 数字年龄 81y vs 阈值 18y | 16,132 | 1 |
| 44-year-old stage | adult | 数字年龄 44y vs 阈值 18y | 15,736 | 1 |
| 73-year-old stage | adult | 数字年龄 73y vs 阈值 18y | 15,563 | 1 |
| 80 year-old and over stage | adult | '80 year-old and over' 下界>=阈值 | 15,231 | 1 |
| 34-year-old stage | adult | 数字年龄 34y vs 阈值 18y | 14,892 | 1 |
| 57-year-old stage | adult | 数字年龄 57y vs 阈值 18y | 13,965 | 1 |
| 51-year-old stage | adult | 数字年龄 51y vs 阈值 18y | 13,488 | 1 |
| 82-year-old stage | adult | 数字年龄 82y vs 阈值 18y | 13,017 | 1 |
| 85-year-old stage | adult | 数字年龄 85y vs 阈值 18y | 12,424 | 1 |
| 20-year-old stage | adult | 数字年龄 20y vs 阈值 18y | 11,952 | 1 |
| 15-year-old stage | developing | 数字年龄 15y vs 阈值 18y | 11,508 | 1 |
| 78-year-old stage | adult | 数字年龄 78y vs 阈值 18y | 9,693 | 1 |
| 27-year-old stage | adult | 数字年龄 27y vs 阈值 18y | 9,293 | 1 |
| 63-year-old stage | adult | 数字年龄 63y vs 阈值 18y | 9,100 | 1 |
| 47-year-old stage | adult | 数字年龄 47y vs 阈值 18y | 8,313 | 1 |
| 43-year-old stage | adult | 数字年龄 43y vs 阈值 18y | 8,196 | 1 |
| 52-year-old stage | adult | 数字年龄 52y vs 阈值 18y | 7,149 | 1 |
| 66-year-old stage | adult | 数字年龄 66y vs 阈值 18y | 7,089 | 1 |
| 21-year-old stage | adult | 数字年龄 21y vs 阈值 18y | 6,493 | 1 |
| 50-year-old stage | adult | 数字年龄 50y vs 阈值 18y | 6,097 | 1 |
| 30-year-old stage | adult | 数字年龄 30y vs 阈值 18y | 4,853 | 1 |

被剔出 adult 主档的供者 4 个: `BCM_23_0491`(developing, 16-year-old stage, 19,530核); `MMD_23_21999`(developing, 17-year-old stage, 17,548核); `MMD_23_20181`(developing, 16-year-old stage, 12,531核); `MMD_23_21623`(developing, 15-year-old stage, 11,508核)

## 工具兼容主表 (major_classes)
| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |
|---|---|---|---|---|---|---|
| CB_NPCE | 17.9 | 15.08–21.31 | 5.94–41.57 | 18.52 |  | A |
| CB_PCE | 28.51 | 23.96–33.84 | 2.68–56.55 | 29.67 |  | A |
| Ciliary_Muscle | 16.25 | 12.18–19.03 | 3.9–32.03 | 15.86 |  | A |
| Endothelium | 2.08 | 1.63–2.55 | 0.0–4.36 | 2.34 |  | A |
| Fibroblast | 14.45 | 11.2–16.83 | 2.59–25.78 | 14.21 |  | A |
| Immune Cell | 4.72 | 3.35–6.61 | 1.18–18.99 | 5.28 |  | A |
| Melanocyte | 5.96 | 4.98–7.4 | 0.0–10.43 | 6.25 |  | A |
| Pericyte | 0.67 | 0.52–0.74 | 0.0–1.07 | 0.65 |  | A |
| Schwann Cell | 7.44 | 6.18–8.51 | 0.18–12.97 | 7.22 |  | A |

## 分层明细 (不同富集/部位先分层展示, 不跨层合并; KB2c: 各层表=adult-only, 括号内=层内 pool 供者数)
### 层: chen_tm_cb|ciliary_body  (n_donors=55, n_cells=833,974, 占图谱96.53%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 17.94 | 15.39–21.65 | 5.94–41.57 | 51 |
| CB_PCE | 27.85 | 23.96–33.03 | 8.99–48.12 | 51 |
| Ciliary_Muscle | 16.25 | 12.76–19.03 | 3.9–32.03 | 51 |
| Endothelium | 2.2 | 1.7–2.56 | 0.0–4.36 | 51 |
| Fibroblast | 14.45 | 11.56–16.7 | 2.59–25.78 | 51 |
| Immune Cell | 4.69 | 3.35–6.3 | 1.18–18.99 | 51 |
| Melanocyte | 6.0 | 5.08–7.67 | 0.0–10.43 | 51 |
| Pericyte | 0.67 | 0.54–0.74 | 0.0–1.04 | 51 |
| Schwann Cell | 7.44 | 6.18–8.48 | 0.18–12.97 | 51 |

### 层: sanes_GSE199013|ciliary_body  (n_donors=4, n_cells=29,948, 占图谱3.47%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 16.08 | 14.15–18.7 | 13.81–21.1 | 4 |
| CB_PCE | 38.96 | 22.9–50.35 | 2.68–56.55 | 4 |
| Ciliary_Muscle | 14.13 | 8.68–21.01 | 4.82–29.18 | 4 |
| Endothelium | 0.45 | 0.22–0.76 | 0.0–1.24 | 4 |
| Fibroblast | 13.14 | 8.59–17.17 | 6.39–17.84 | 4 |
| Immune Cell | 6.83 | 4.46–10.33 | 3.02–15.17 | 4 |
| Melanocyte | 3.77 | 3.38–4.62 | 3.19–6.15 | 4 |
| Pericyte | 0.33 | 0.19–0.57 | 0.0–1.07 | 4 |
| Schwann Cell | 7.73 | 6.44–8.89 | 4.98–9.97 | 4 |

## 亚型层 (类内注释细胞占比%, pooled within class 口径)

## 旗标语义
**expected_low_but_present**: Pericyte <1% (Endothelium 也仅 ~2%: 大血管为主, 毛细血管核捕获效率低)

**unexpected**: Immune Cell ~5% (巨噬为主) 属固有免疫正常水平, 供炎症对照基线

**contamination_suspect**: 无需额外污染旗 (切片边界即本组织)

## 注意事项
1. 本条=睫状体解剖组分取材切片: PCE/NPCE/睫状肌三主类为组织本体; Melanocyte/Schwann Cell 比例为葡萄膜色素+神经支配层的捕获构成 —— 疾病对照注意 (Astra T2)。
2. Fibroblast 在本切片 = CB 成纤维 (CBFibro), 与 TM/角膜成纤维不同亚层 (author_cell_type 可辨)。
3. 供者 59, 支撑较强; 但两研究层规模悬殊 (chen_tm_cb 主力 vs sanes uvea 分量在本切片外), 分层明细必看。
4. snRNA 口径 (核悬液, 内含子 reads 计入), 与 scRNA 条不可直接互比。
5. v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y, 裁定 Q2) —— 本切片实测剔除 4 个非 adult 供者单元 (青少年段, 逐行见 excluded_nonadult_units); v1.0 混口径保留于 donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), 两档签名分离。

## 出处清单
| sid | 类型 | 标签 |
|---|---|---|
| `CILIARY_BODY_LOCAL` | dataset | 本地文件 /mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad  |
| `CILIARY_BODY_HASA` | dataset | HASA/前节段 snRNA collection (t_6f5cc731 盘点映射 OA-D004/OA-D016; 本切片=其 chen_tm_cb+sanes 集成件的 ciliary_body 分量)  |

