# 组成基线: 人(正常)新鲜分离 RPE 悬液 scRNA — 发育阶段=unknown 档 (OA GSE158629, 供者级 4 供者, 簇身份 marker 推断, KB2c 披露)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_RPE` | 状态: filled_donor_level | 发育轴: **organism_stage=unknown** | 生成: 2026-09-23 | 卡片: t_bad1fbab
> **KB3 发育档 (卡片 t_5425a7ca)**: development_stage=**unknown** | 适用档(回填时写死): unknown —— KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。
> 本文件由 `/mnt/D/EyeKB/scripts/baselines/build_baselines.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。
> ⚠ 发育轴披露: 本地 GSE158629 cells_meta (export_rpe_meta.R 导出) 仅 donor/cluster/tech 列, 无 development_stage/年龄列; GEO Summary 记 'four adult human donor eyes' (证据 B 级)。

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
- 两档身份: {'unknown_descriptive': 'baseline_human_RPE__stage_unknown__kb2c'}

## Astra T2 元数据字段
- **取样材料**: 人新鲜分离 RPE 单层细胞 (4 具成人供体眼, stage=Fresh; GEO: 'RPE cells were isolated from four adult human donor eyes')
- **疾病阶段**: normal (健康供体; 处理件元数据无疾病列)
- **治疗背景**: 未记录 (处理件元数据无治疗列) —— 标'未记录', 不臆测
- **scRNA_vs_snRNA**: scRNA-seq 全细胞 (donor1=10x 3'; donor2-4=ICELL8 液滴克隆) —— 与 snRNA 条 (retina/optic_nerve) 口径不同, 不可直接互比
- **富集步骤**: RPE 层机械+酶分离富集 (组织级); 无荧光分选记录 —— 分离流程本身即'富集'
- **解离方法**: 新鲜眼离体后 RPE 分离 (GEO Methods; 处理件无解离试剂列, 细节未记录)
- **供者数**: 4 (donor1=10x, donor2-4=ICELL8 —— 平台与供者完全捆绑, tech 分层=描述性) —— KB2c: cells_meta 无年龄列, 本条 organism_stage=unknown (GEO 文字记 'four adult human donor eyes' 为 B 级文献描述, 不可逐行核验, 禁静默归 adult)
- **计数分母**: 10,917 cells (4 个 donor 对象 26 簇, 全标注)
- **证据来源**: 本地实测复算 (A: 比例; RData→CSV 导出脚本 export_rpe_meta.R) + GEO 记录作者簇描述 (B: rod/cone/TF+SPP1/干细胞候选) + 本项目 marker 推断 (C)

## 主参考: 供者级条件参考分布 (n=4 供者; marker 推断 canonical 类)
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| RPE | 60.25 | 48.25–75.33 | 47.06–85.79 | 4 |
| PR-associated | 22.4 | 16.43–30.18 | 9.27–42.78 | 4 |
| neuron-like | 0.0 | 0.0–0.54 | 0.0–2.17 | 4 |
| erythroid | 6.56 | 2.21–15.75 | 0.0–32.54 | 4 |
| myeloid | 0.0 | 0.0–0.5 | 0.0–1.99 | 4 |

### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)
| 来源 | organism_stage | 规则 | 细胞数 | 供者数 | 文献级描述 (B) |
|---|---|---|---|---|---|
| GSE158629 cells_meta (全 4 donor) | unknown | 无年龄列 → 禁静默归 adult (红线2) | 10,917 | 4 | GEO: 'RPE cells were isolated from four adult human donor eyes' |

## 工具兼容主表 (major_classes)
| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |
|---|---|---|---|---|---|---|
| RPE | 60.25 | 48.25–75.33 | 47.06–85.79 | 67.98 |  | A |
| PR-associated | 22.4 | 16.43–30.18 | 9.27–42.78 | 24.92 |  | A |
| neuron-like | 0.0 | 0.0–0.54 | 0.0–2.17 | 1.36 |  | A |
| erythroid | 6.56 | 2.21–15.75 | 0.0–32.54 | 5.48 |  | A |
| myeloid | 0.0 | 0.0–0.5 | 0.0–1.99 | 0.27 |  | A |

## 亚型层 (类内注释细胞占比%, pooled within class 口径)

## 状态层
- **donor1 cl0** [RPE: pigment-high (TYRP1+/BEST1+/RPE65+)]: m, a, r, k, e, r, :,  , R, P, E, 6, 5, #, 3,  , T, Y, R, P, 1, #, 1, 1,  , B, E, S, T, 1, #, 1, 2,  , T, I, M, P, 3, #, 1,  , (, A, ) (证据 A+B/C)
- **donor1 cl1** [RPE: canonical (RBP1/RLBP1)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor1 cl2** [PR-associated: rod-program (SAG/PDE6A/RHO)]: 作, 者, 描, 述,  , r, o, d,  , R, N, A,  , 簇,  , R, H, O, /, P, D, E, 6, A,  , (, B, ),  , +,  , m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor1 cl3** [RPE: TF+SPP1/VEGF state (VIM+/TF+/SPP1+/MT1X+)]: 作, 者, 描, 述,  , V, E, G, F,  , s, i, g, n, a, l, i, n, g,  , 簇,  , T, F, /, S, P, P, 1,  , (, B, ),  , +,  , m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor1 cl4** [PR-associated: rod-pure (RHO/RBP3/IMPG1/CNGA1)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor1 cl5** [PR-associated: rod/cone-mixed (SAG/GNAT1/PDE6G)]: m, a, r, k, e, r,  , (, A, ), ;,  , 作, 者,  , c, o, n, e,  , 簇,  , A, R, R, 3, /, P, D, E, 6, H,  , 未, 入, 本, 簇,  , t, o, p, 2, 5, ,,  , 归, 属, 存, 疑,  , (, C, ) (证据 A+B/C)
- **donor1 cl6** [neuron-like: VSX1+/SNAP25+ (bipolar/cone-like)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor1 cl7** [neuron-like: ISL1+/SNAP25+ (amacrine-like)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor2 cl0** [RPE: canonical]: m, a, r, k, e, r, :,  , R, P, E, 6, 5, #, 7,  , T, T, R,  , (, A, ) (证据 A+B/C)
- **donor2 cl1** [RPE: mito-high]: m, a, r, k, e, r, :,  , M, T, -, *,  , 主, 导,  , +,  , R, P, E, 6, 5, /, B, E, S, T, 1,  , (, A, ) (证据 A+B/C)
- **donor2 cl2** [PR-associated: rod/cone-transcripts]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor2 cl3** [RPE: canonical (NDUFS7+)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor2 cl4** [RPE: pigment (TYRP1+/BEST1+)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor2 cl5** [erythroid: HBG1/HBG2+ribosomal]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor2 cl6** [RPE: complement-high (C4A/C4B+/PMEL+/TRPM3+)]: R, P, E,  , 谱, 系,  , (, T, R, P, M, 3, /, P, M, E, L, ),  , +,  , 补, 体, 状, 态,  , (, A, ) (证据 A+B/C)
- **donor2 cl7** [myeloid: CD74/AIF1/HLA-DR/CCL3]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor3 cl0** [RPE: canonical]: m, a, r, k, e, r, :,  , R, P, E, 6, 5, #, 2,  , (, A, ) (证据 A+B/C)
- **donor3 cl1** [erythroid: HBG+ribosomal]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor3 cl2** [PR-associated: rod-transcripts (RHO/RCVRN/ABCA4)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor3 cl3** [RPE: pigment-high (TYRP1+/BEST1+)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor3 cl4** [erythroid: HBG+ribosomal]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor4 cl0** [PR-associated: rod-program (SAG/RHO/PDE6A)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor4 cl1** [RPE: mito-high]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor4 cl2** [erythroid: HBG+ribosomal]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)
- **donor4 cl3** [RPE: TF/GPX3 stress state (TF#2/TRPM3+)]: 与,  , d, o, n, o, r, 1,  , T, F, +, S, P, P, 1,  , 簇,  , m, a, r, k, e, r,  , 重, 叠,  , (, C, ) (证据 A+B/C)
- **donor4 cl4** [RPE: canonical (HSP-high)]: m, a, r, k, e, r,  , (, A, ) (证据 A+B/C)

## 旗标语义
**expected_low_but_present**: myeloid (CD74/AIF1/HLA-DR) 仅 donor2 检出; erythroid 仅 ICELL8 供者检出; 干细胞候选群 (RPE65+/VIM/GNL3/MKI67, 作者描述 B): 未在任何簇 top25 浮现 —— 小群未量化, 区间无法估计 (合法状态, Astra T2)

**unexpected**: PR-associated 类 3.8–28.5%: 作者称 RPE 亚群 (cone/rod 转录本簇, B), 亦可为吞噬 PR 外节mRNA 或盘膜附着污染 —— 双重解释保留, 不下单一结论; neuron-like 类 (VSX1/ISL1/SNAP25) 仅 donor1 (10x) 检出 2.2% —— 视网膜神经污染或低丰度前体, 存疑

**contamination_suspect**: erythroid (HBG1/HBG2) 供者内最高 32.54% —— 血液残留

## 注意事项
1. 身份标注非作者官方命名: 处理件只有 donor×cluster 编号, canonical 类标签为本项目 marker 推断 (证据 C), 仅 rod/cone/TF+SPP1/干细胞候选四类有 GEO 作者描述锚 (证据 B)。对外引用须带此口径。
2. n=4 供者, donor 级 median/IQR 极粗 (每供者权重 25%); 区间只作'新鲜分离 RPE 捕获构成'的描述性参考。
3. 各 donor 对象独立聚类无全局整合; 同类簇跨 donor 合并依赖 marker 一致性 (RPE/PR/erythroid 清晰, neuron-like/状态细分谨慎)。
4. 平台×供者完全捆绑 (10x n=1 / ICELL8 n=3): donor1 独有 neuron-like、donor2-4 独有 erythroid 的差异不能区分平台效应与供者变异。
5. 本条=分离后 RPE 悬液的捕获构成 (计数分母不含非 RPE 组织的完整组织学), 不代表 RPE 层在完整眼球/脉络膜组织中的位置丰度; 组织学丰度参考须用带 RPE 的全组织条 (retina/choroid 骨架)。
6. KB2c t_be336eee 红线2: 本条无逐供者发育/年龄元数据 → 发育档=unknown + 披露行, 不得作为 '成人 RPE 基线' 引用; 升级 adult-only 需补逐 donor 年龄 (GEO 附表/作者通信) 后另裁。

## 出处清单
| sid | 类型 | 标签 |
|---|---|---|
| `RPE_LOCAL` | dataset | 作者处理件 /mnt/D/OcularKB/data/GSE158629/GSE158629_scrRNA_RPE_donors1-4.RData.gz (GSE158629); 导出件 /mnt/D/EyeKB/scripts/baselines/data/rpe_GSE158629_cells_meta.csv + /mnt/D/EyeKB/scripts/baselines/data/rpe_GSE158629_cluster_markers.csv (scripts/baselines/data/export_rpe_meta.R)  |
| `RPE_GEO` | dataset | GEO GSE158629 — Single-Cell RNA Sequencing Reveals the Heterogeneity of the Human RPE (摘要含 rod/cone/TF+SPP1/干细胞候选簇描述)  |

