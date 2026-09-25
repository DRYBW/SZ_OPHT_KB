# 组成基线: 人(正常)trabecular_meshwork snRNA adult-only 主档 (trabecular_meshwork 切片 184,922 核 / 25 供者, 供者级条件参考分布, KB2c 发育轴单列)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_trabecular_meshwork` | 状态: filled_donor_level | 发育轴: **organism_stage=adult** | 生成: 2026-09-23 | 卡片: t_bad1fbab
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
- 两档身份: {'adult_only': 'baseline_human_trabecular_meshwork__adult_only__kb2c', 'adult_pool': 'baseline_human_trabecular_meshwork__adult_pool__v1.0'}

## Astra T2 元数据字段
- **取样材料**: 人前节段手术取材中 trabecular_meshwork 解剖组分 (tissue 列='eye trabecular meshwork' 切片; 另有 uvea 分量 53,406 核未入本条)
- **疾病阶段**: normal (disease 列全 normal; 供者系统性死亡眼库/手术材料)
- **治疗背景**: 未记录 (元数据无治疗列) —— 标'未记录', 不臆测
- **scRNA_vs_snRNA**: snRNA-seq (suspension_type=nucleus 100%; intronic_reads_counted=yes)
- **富集步骤**: 无分选记录 (全组织核悬液直接上机)
- **解离方法**: mechanical dissociation,detergent solubilization×157,161核; mechanical dissociation,centrifugation×27,761核 (sample_collection_method=surgical resection)
- **供者数**: 主档 adult-only 25 donors / 25 供者单元; 对照档 adult_pool 25 donors / 25 单元 (含 0 非 adult 供者 → 逐行见 excluded_nonadult_units)
- **计数分母**: 184,922 核 (trabecular_meshwork 切片内 majorclass 全标注)
- **证据来源**: 本地实测复算 (A) + portal/HASA 官方注释 (t_6f5cc731 判 'portal官方')

## 主参考: 供者级条件参考分布 (排除分选设计层)
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 25 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 25 |
| Ciliary_Muscle | 34.22 | 30.18–43.43 | 17.61–59.17 | 25 |
| Endothelium | 2.35 | 1.47–3.2 | 0.78–10.68 | 25 |
| Fibroblast | 37.37 | 31.05–42.69 | 20.83–65.3 | 25 |
| Immune Cell | 4.58 | 3.44–6.58 | 0.67–18.82 | 25 |
| Melanocyte | 5.31 | 3.46–7.21 | 0.63–11.45 | 25 |
| Pericyte | 0.33 | 0.27–0.42 | 0.0–0.88 | 25 |
| Schwann Cell | 11.58 | 7.72–13.6 | 3.73–22.85 | 25 |

### 对照档 adult_pool (v1.0 混口径, 含非 adult 供者; tier=`baseline_human_trabecular_meshwork__adult_pool__v1.0`) —— 引用 v1.0 旧数字只能挂此档身份

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 25 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 25 |
| Ciliary_Muscle | 34.22 | 30.18–43.43 | 17.61–59.17 | 25 |
| Endothelium | 2.35 | 1.47–3.2 | 0.78–10.68 | 25 |
| Fibroblast | 37.37 | 31.05–42.69 | 20.83–65.3 | 25 |
| Immune Cell | 4.58 | 3.44–6.58 | 0.67–18.82 | 25 |
| Melanocyte | 5.31 | 3.46–7.21 | 0.63–11.45 | 25 |
| Pericyte | 0.33 | 0.27–0.42 | 0.0–0.88 | 25 |
| Schwann Cell | 11.58 | 7.72–13.6 | 3.73–22.85 | 25 |

### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)
| UBERON development_stage | organism_stage | 判级规则 | 核/细胞数 | 供者数 |
|---|---|---|---|---|
| 53-year-old stage | adult | 数字年龄 53y vs 阈值 18y | 22,052 | 2 |
| 68-year-old stage | adult | 数字年龄 68y vs 阈值 18y | 20,418 | 2 |
| 80 year-old and over stage | adult | '80 year-old and over' 下界>=阈值 | 16,802 | 2 |
| 69-year-old stage | adult | 数字年龄 69y vs 阈值 18y | 16,533 | 2 |
| 66-year-old stage | adult | 数字年龄 66y vs 阈值 18y | 12,159 | 1 |
| 20-year-old stage | adult | 数字年龄 20y vs 阈值 18y | 10,682 | 1 |
| 72-year-old stage | adult | 数字年龄 72y vs 阈值 18y | 8,741 | 1 |
| 56-year-old stage | adult | 数字年龄 56y vs 阈值 18y | 8,567 | 1 |
| 58-year-old stage | adult | 数字年龄 58y vs 阈值 18y | 8,501 | 1 |
| 76-year-old stage | adult | 数字年龄 76y vs 阈值 18y | 8,015 | 1 |
| 57-year-old stage | adult | 数字年龄 57y vs 阈值 18y | 7,975 | 1 |
| 47-year-old stage | adult | 数字年龄 47y vs 阈值 18y | 6,492 | 1 |
| 24-year-old stage | adult | 数字年龄 24y vs 阈值 18y | 6,284 | 1 |
| 50-year-old stage | adult | 数字年龄 50y vs 阈值 18y | 5,526 | 1 |
| 65-year-old stage | adult | 数字年龄 65y vs 阈值 18y | 5,270 | 1 |
| 64-year-old stage | adult | 数字年龄 64y vs 阈值 18y | 4,313 | 1 |
| 51-year-old stage | adult | 数字年龄 51y vs 阈值 18y | 3,889 | 1 |
| 30-year-old stage | adult | 数字年龄 30y vs 阈值 18y | 3,840 | 1 |
| 34-year-old stage | adult | 数字年龄 34y vs 阈值 18y | 3,510 | 1 |
| 61-year-old stage | adult | 数字年龄 61y vs 阈值 18y | 2,994 | 1 |
| 44-year-old stage | adult | 数字年龄 44y vs 阈值 18y | 2,359 | 1 |

## 工具兼容主表 (major_classes)
| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |
|---|---|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 0.18 |  | A |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 0.31 |  | A |
| Ciliary_Muscle | 34.22 | 30.18–43.43 | 17.61–59.17 | 36.93 |  | A |
| Endothelium | 2.35 | 1.47–3.2 | 0.78–10.68 | 2.47 |  | A |
| Fibroblast | 37.37 | 31.05–42.69 | 20.83–65.3 | 36.38 |  | A |
| Immune Cell | 4.58 | 3.44–6.58 | 0.67–18.82 | 5.28 |  | A |
| Melanocyte | 5.31 | 3.46–7.21 | 0.63–11.45 | 5.94 |  | A |
| Pericyte | 0.33 | 0.27–0.42 | 0.0–0.88 | 0.39 |  | A |
| Schwann Cell | 11.58 | 7.72–13.6 | 3.73–22.85 | 12.11 |  | A |

## 分层明细 (不同富集/部位先分层展示, 不跨层合并; KB2c: 各层表=adult-only, 括号内=层内 pool 供者数)
### 层: chen_tm_cb|trabecular_meshwork  (n_donors=21, n_cells=157,161, 占图谱84.99%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–2.81 | 21 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–4.9 | 21 |
| Ciliary_Muscle | 33.09 | 30.06–37.84 | 17.61–59.17 | 21 |
| Endothelium | 2.35 | 2.04–3.2 | 0.78–9.43 | 21 |
| Fibroblast | 38.04 | 32.24–43.24 | 20.83–65.3 | 21 |
| Immune Cell | 4.58 | 3.3–6.37 | 0.67–18.82 | 21 |
| Melanocyte | 6.18 | 3.71–7.45 | 0.63–11.45 | 21 |
| Pericyte | 0.31 | 0.26–0.36 | 0.0–0.77 | 21 |
| Schwann Cell | 11.46 | 7.72–13.01 | 3.73–17.67 | 21 |

### 层: sanes_GSE199013|trabecular_meshwork  (n_donors=4, n_cells=27,761, 占图谱15.01%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| CB_NPCE | 0.0 | 0.0–0.0 | 0.0–0.0 | 4 |
| CB_PCE | 0.0 | 0.0–0.0 | 0.0–0.0 | 4 |
| Ciliary_Muscle | 43.88 | 42.97–45.02 | 41.56–47.12 | 4 |
| Endothelium | 1.95 | 1.35–4.52 | 1.09–10.68 | 4 |
| Fibroblast | 29.95 | 27.47–31.1 | 22.05–32.53 | 4 |
| Immune Cell | 5.57 | 4.31–6.75 | 3.56–7.23 | 4 |
| Melanocyte | 3.65 | 2.48–4.62 | 1.22–5.28 | 4 |
| Pericyte | 0.72 | 0.67–0.78 | 0.55–0.88 | 4 |
| Schwann Cell | 12.91 | 10.22–16.38 | 6.15–22.85 | 4 |

## 亚型层 (类内注释细胞占比%, pooled within class 口径)

## 旗标语义
**expected_low_but_present**: Schwann Cell ~12% (神经支配组织); Pericyte ~0.4%

**unexpected**: Melanocyte ~6% (葡萄膜色素组织附带, 取材平面相关)

**contamination_suspect**: CB_PCE/CB_NPCE ~0.5% (取材越界到睫状体)

## 注意事项
1. 本条=小梁网解剖组分取材切片: Ciliary_Muscle 占比高系紧邻的巩膜 spur/小梁肌一体取材, 属捕获构成非 TM 细胞层真值; 作者级 TM 特异亚型 (BeamA/BeamB/JCT, author_cell_type) 见 fine_types。
2. Fibroblast 主表类在本切片 = TM 成纤维/梁细胞 (TMFibro) —— 勿与角膜/巩膜成纤维直接混比。
3. CB_PCE/CB_NPCE 少量 (合计 ~0.5%) = 睫状体取材边界污染。
4. 供者 25 但单元内供者规模不均; n=25 供者级区间仍属中等支撑, 疾病对照用后须复核方向。
5. snRNA 口径, 与 scRNA 条不可直接互比 (Astra T2); uvea 分量 (53,406 核) 与巩膜/葡萄膜条另议。
6. v1.1 (KB2c t_be336eee): 主档=adult-only (>=18y, 裁定 Q2) —— 本切片实测剔除 0 个 (本切片全部供者 >=18y → 两档数值合法全等, 仅身份签名分离); v1.0 混口径保留于 donor_level_adult_pool_contrast (tier=...__adult_pool__v1.0), 两档签名分离。

## 出处清单
| sid | 类型 | 标签 |
|---|---|---|
| `TRABECULAR_MESHWORK_LOCAL` | dataset | 本地文件 /mnt/D/OcularKB/data/HRA000728_tm_cb/HRA000728_tm_cb.h5ad  |
| `TRABECULAR_MESHWORK_HASA` | dataset | HASA/前节段 snRNA collection (t_6f5cc731 盘点映射 OA-D004/OA-D016; 本切片=其 chen_tm_cb+sanes 集成件的 trabecular_meshwork 分量)  |

