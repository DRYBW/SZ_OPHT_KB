# 组成基线: 人(正常)神经视网膜 adult-only 主档 (D001 HRCA, 供者级条件参考分布, KB2c 发育轴单列)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_retina` | 状态: filled_donor_level | 发育轴: **organism_stage=adult** | 生成: 2026-09-23 | 卡片: t_16c3e020
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
- 两档身份: {'adult_only': 'baseline_human_retina__adult_only__kb2c', 'adult_pool': 'baseline_human_retina__adult_pool__v1.0'}

## Astra T2 元数据字段
- **取样材料**: 人神经视网膜离体组织 (区域构成: peripheral region of retina 1,568,477, macula lutea 1,077,597, fovea centralis 434,131, macula lutea proper 97,105)
- **疾病阶段**: normal (disease 列全 normal; 供者以老年为主, 90+ 岁段最大)
- **治疗背景**: 未记录 (公开 atlas 元数据无治疗列) —— 标'未记录', 不臆测
- **平台**: snRNA-seq (suspension_type=nucleus 100%, 核悬液)
- **富集步骤**: 分层: 多数 naive; 1,334,033 核经 NeuN+ 神经元核分选 (Chen_a/ancestry 部分); Chen_rgc 研究整层为 RGC 富集设计
- **解离方法**: Chen_a=0.02% NP40 (核提取); Chen_ancestry=0.02% NP40 (核提取); Chen_b_GSE226108=0.02% NP40 (核提取); Chen_c_GSE247157=0.02% NP40 (核提取); Chen_rgc=0.02% NP40 (核提取); Shekhar_GSE237204=unknown
- **供者数**: 主档 adult-only 97 donors / 113 供者单元; 对照档 adult_pool 104 donors / 120 单元 (含 7 非 adult 供者 → 逐行见 excluded_nonadult_units, KB2c 裁定 Q2 阈值>=18y)
- **计数分母**: 3,177,310 核 (majorclass 全标注)
- **证据来源**: 本地实测复算 (A) + HRCA 论文 (B, PMID 41578023) + 旧 KB1 文献锚

## 主参考: 供者级条件参考分布 (排除分选设计层)
> 分层口径: 主档=6 研究排除 Chen_rgc (RGC 富集设计) 与各研究 NeuN+ 分选层、且仅 organism_stage=adult (>=18y) 供者单元 113 个; 方法: 供者级: 每供者单元先算 10 类占比, 再跨供者汇总 median/IQR/range; 分层=研究×富集(×部位, D002 侧); pooled 列仅对照, 有大供者压秤问题
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 8.46 | 6.55–10.96 | 3.59–70.83 | 113 |
| Astrocyte | 0.37 | 0.05–0.9 | 0.0–5.38 | 113 |
| BC | 19.99 | 15.21–26.98 | 0.13–49.97 | 113 |
| Cone | 3.27 | 2.3–5.21 | 0.0–13.1 | 113 |
| HC | 2.78 | 1.38–4.47 | 0.0–13.25 | 113 |
| MG | 8.75 | 5.28–11.48 | 0.0–24.66 | 113 |
| Microglia | 0.14 | 0.0–0.22 | 0.0–1.22 | 113 |
| RGC | 3.23 | 0.88–8.7 | 0.0–92.41 | 113 |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 113 |
| Rod | 48.85 | 22.06–57.56 | 0.0–77.97 | 113 |

### 对照档 adult_pool (v1.0 混口径, 含非 adult 供者; tier=`baseline_human_retina__adult_pool__v1.0`) —— 引用 v1.0 旧数字只能挂此档身份

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 8.45 | 6.54–10.77 | 3.59–70.83 | 120 |
| Astrocyte | 0.37 | 0.05–0.92 | 0.0–12.93 | 120 |
| BC | 20.35 | 15.27–27.86 | 0.13–49.97 | 120 |
| Cone | 3.26 | 2.14–4.97 | 0.0–13.1 | 120 |
| HC | 2.91 | 1.41–4.52 | 0.0–13.25 | 120 |
| MG | 8.78 | 5.22–11.64 | 0.0–24.66 | 120 |
| Microglia | 0.14 | 0.0–0.23 | 0.0–1.22 | 120 |
| RGC | 2.95 | 0.86–8.42 | 0.0–92.41 | 120 |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 120 |
| Rod | 48.27 | 23.91–57.46 | 0.0–77.97 | 120 |

### 发育阶段逐行披露 (KB2c 红线2: 排除项/unknown 全部显式列出)
| UBERON development_stage | organism_stage | 判级规则 | 核/细胞数 | 供者数 |
|---|---|---|---|---|
| 90 year-old and over stage | adult | '90 year-old and over' 下界>=阈值 | 369,477 | 5 |
| 69-year-old stage | adult | 数字年龄 69y vs 阈值 18y | 170,764 | 6 |
| 64-year-old stage | adult | 数字年龄 64y vs 阈值 18y | 170,635 | 4 |
| 73-year-old stage | adult | 数字年龄 73y vs 阈值 18y | 164,811 | 2 |
| 82-year-old stage | adult | 数字年龄 82y vs 阈值 18y | 162,339 | 3 |
| 86-year-old stage | adult | 数字年龄 86y vs 阈值 18y | 133,685 | 3 |
| 71-year-old stage | adult | 数字年龄 71y vs 阈值 18y | 130,930 | 5 |
| 77-year-old stage | adult | 数字年龄 77y vs 阈值 18y | 110,926 | 5 |
| 67-year-old stage | adult | 数字年龄 67y vs 阈值 18y | 105,577 | 4 |
| 81-year-old stage | adult | 数字年龄 81y vs 阈值 18y | 95,313 | 3 |
| 68-year-old stage | adult | 数字年龄 68y vs 阈值 18y | 94,341 | 2 |
| 43-year-old stage | adult | 数字年龄 43y vs 阈值 18y | 85,308 | 3 |
| 80-year-old stage | adult | 数字年龄 80y vs 阈值 18y | 82,752 | 1 |
| 65-year-old stage | adult | 数字年龄 65y vs 阈值 18y | 80,114 | 4 |
| 66-year-old stage | adult | 数字年龄 66y vs 阈值 18y | 72,396 | 1 |
| 85-year-old stage | adult | 数字年龄 85y vs 阈值 18y | 66,992 | 2 |
| 72-year-old stage | adult | 数字年龄 72y vs 阈值 18y | 66,338 | 3 |
| 21-year-old stage | adult | 数字年龄 21y vs 阈值 18y | 65,728 | 1 |
| 78-year-old stage | adult | 数字年龄 78y vs 阈值 18y | 64,271 | 1 |
| 62-year-old stage | adult | 数字年龄 62y vs 阈值 18y | 60,886 | 3 |
| late adult stage | adult | UBERON 成年术语档 (无数字年龄; 映射规则见 stage_axis) | 56,087 | 3 |
| 88-year-old stage | adult | 数字年龄 88y vs 阈值 18y | 55,003 | 1 |
| 84-year-old stage | adult | 数字年龄 84y vs 阈值 18y | 54,100 | 1 |
| 52-year-old stage | adult | 数字年龄 52y vs 阈值 18y | 48,328 | 1 |
| 32-year-old stage | adult | 数字年龄 32y vs 阈值 18y | 45,370 | 1 |
| 25-year-old stage | adult | 数字年龄 25y vs 阈值 18y | 40,614 | 1 |
| 53-year-old stage | adult | 数字年龄 53y vs 阈值 18y | 39,355 | 1 |
| 60-year-old stage | adult | 数字年龄 60y vs 阈值 18y | 38,614 | 2 |
| 83-year-old stage | adult | 数字年龄 83y vs 阈值 18y | 37,829 | 1 |
| 75-year-old stage | adult | 数字年龄 75y vs 阈值 18y | 35,801 | 1 |
| 16-year-old stage | developing | 数字年龄 16y vs 阈值 18y | 35,683 | 2 |
| 63-year-old stage | adult | 数字年龄 63y vs 阈值 18y | 27,655 | 1 |
| 27-year-old stage | adult | 数字年龄 27y vs 阈值 18y | 26,380 | 2 |
| 34-year-old stage | adult | 数字年龄 34y vs 阈值 18y | 25,985 | 2 |
| 80 year-old and over stage | adult | '80 year-old and over' 下界>=阈值 | 23,946 | 1 |
| 46-year-old stage | adult | 数字年龄 46y vs 阈值 18y | 23,916 | 1 |
| 11-year-old stage | developing | 数字年龄 11y vs 阈值 18y | 20,466 | 1 |
| 58-year-old stage | adult | 数字年龄 58y vs 阈值 18y | 20,118 | 2 |
| prime adult stage | adult | UBERON 成年术语档 (无数字年龄; 映射规则见 stage_axis) | 16,640 | 2 |
| eighth decade stage | adult | eighth decade = 70-79y 下界>=阈值 | 16,459 | 2 |
| 50-year-old stage | adult | 数字年龄 50y vs 阈值 18y | 14,949 | 1 |
| 30-year-old stage | adult | 数字年龄 30y vs 阈值 18y | 13,026 | 1 |
| 17-year-old stage | developing | 数字年龄 17y vs 阈值 18y | 12,347 | 1 |
| 15-year-old stage | developing | 数字年龄 15y vs 阈值 18y | 11,892 | 1 |
| 47-year-old stage | adult | 数字年龄 47y vs 阈值 18y | 11,732 | 1 |
| 10-year-old stage | developing | 数字年龄 10y vs 阈值 18y | 10,625 | 1 |
| 18-year-old stage | adult | 数字年龄 18y vs 阈值 18y | 10,613 | 1 |
| 70-year-old stage | adult | 数字年龄 70y vs 阈值 18y | 9,690 | 1 |
| 3-year-old stage | developing | 数字年龄 3y vs 阈值 18y | 8,925 | 1 |
| 76-year-old stage | adult | 数字年龄 76y vs 阈值 18y | 8,685 | 1 |
| 60-79 year-old stage | adult | 年龄段 60-79 下界>=阈值 | 8,475 | 1 |
| 74-year-old stage | adult | 数字年龄 74y vs 阈值 18y | 6,401 | 1 |
| 41-year-old stage | adult | 数字年龄 41y vs 阈值 18y | 4,827 | 1 |
| 24-year-old stage | adult | 数字年龄 24y vs 阈值 18y | 3,191 | 1 |

被剔出 adult 主档的供者 7 个: `BCM_23_0131`(developing, 16-year-old stage, 26,671核); `BCM_22_0769`(developing, 11-year-old stage, 20,466核); `MMD_23_21999`(developing, 17-year-old stage, 12,347核); `MMD_23_21623`(developing, 15-year-old stage, 11,892核); `MMD_23_17738`(developing, 10-year-old stage, 10,625核); `MMD_23_20181`(developing, 16-year-old stage, 9,012核); `MMD_23_22486`(developing, 3-year-old stage, 8,925核)

## 工具兼容主表 (major_classes)
| 类 | 供者中位% | IQR% | range% | pooled%(仅对照) | 本地库marker | 证据 |
|---|---|---|---|---|---|---|
| AC | 8.46 | 6.55–10.96 | 3.59–70.83 | 17.99 | TFAP2A, GAD1, GAD2, SLC6A9, ONECUT2 | A |
| Astrocyte | 0.37 | 0.05–0.9 | 0.0–5.38 | 0.44 | GFAP, AQP4, S100B, VIM, SLC1A3 | A |
| BC | 19.99 | 15.21–26.98 | 0.13–49.97 | 21.75 | VSX2, GRM6, CACNA1S, ISL1, OTX2 | A |
| Cone | 3.27 | 2.3–5.21 | 0.0–13.1 | 4.0 | OPN1SW, OPN1MW, ARR3, PDE6H, GNAT2 | A |
| HC | 2.78 | 1.38–4.47 | 0.0–13.25 | 2.54 | ONECUT1, ONECUT3, GAD1, ISL1, CX3CR1 | A |
| MG | 8.75 | 5.28–11.48 | 0.0–24.66 | 6.97 | RLBP1, GLUL, SOX9, VIM, S100B | A |
| Microglia | 0.14 | 0.0–0.22 | 0.0–1.22 | 0.15 | C1QB | A |
| RGC | 3.23 | 0.88–8.7 | 0.0–92.41 | 12.58 | RBPMS, SLC17A6, POU4F1, POU4F2, NEFL | A |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 0.03 | BEST1, RPE65, TTR, LRAT, RDH5, MITF | A |
| Rod | 48.85 | 22.06–57.56 | 0.0–77.97 | 33.55 | RHO, NRL, NR2E3, PDE6B, GNAT1 | A |

## 分层明细 (不同富集/部位先分层展示, 不跨层合并; KB2c: 各层表=adult-only, 括号内=层内 pool 供者数)
### 层: Chen_a|NeuN+ ⚠分选设计层  (n_donors=20, n_cells=802,830, 占图谱25.27%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 25.5 | 20.57–28.15 | 16.38–44.12 | 20 |
| Astrocyte | 0.24 | 0.05–0.42 | 0.0–3.51 | 20 |
| BC | 36.28 | 30.86–42.5 | 3.22–53.15 | 20 |
| Cone | 4.68 | 1.77–5.53 | 0.21–8.37 | 20 |
| HC | 0.28 | 0.03–0.56 | 0.0–0.84 | 20 |
| MG | 6.86 | 4.83–7.89 | 2.56–12.29 | 20 |
| Microglia | 0.15 | 0.05–0.29 | 0.0–0.96 | 20 |
| RGC | 0.17 | 0.11–0.36 | 0.0–1.7 | 20 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.05 | 20 |
| Rod | 27.0 | 19.29–35.81 | 2.54–48.5 | 20 |

### 层: Chen_a|naive  (n_donors=20, n_cells=259,272, 占图谱8.16%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 5.02 | 4.38–7.1 | 3.59–13.01 | 20 |
| Astrocyte | 0.2 | 0.0–0.34 | 0.0–1.41 | 20 |
| BC | 15.13 | 13.62–17.32 | 11.57–29.16 | 20 |
| Cone | 2.59 | 1.98–2.99 | 1.26–3.57 | 20 |
| HC | 1.21 | 0.87–1.51 | 0.68–2.91 | 20 |
| MG | 8.78 | 6.12–11.28 | 2.99–17.06 | 20 |
| Microglia | 0.13 | 0.0–0.18 | 0.0–0.98 | 20 |
| RGC | 0.0 | 0.0–0.08 | 0.0–0.15 | 20 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.0 | 20 |
| Rod | 67.63 | 61.12–70.53 | 41.55–77.97 | 20 |

### 层: Chen_ancestry|NeuN+ ⚠分选设计层  (n_donors=27, n_cells=299,171, 占图谱9.42%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 19.82 | 13.95–38.23 | 1.42–88.44 | 27 |
| Astrocyte | 0.0 | 0.0–0.03 | 0.0–0.51 | 27 |
| BC | 2.61 | 0.67–4.95 | 0.2–11.92 | 27 |
| Cone | 1.21 | 0.36–3.63 | 0.0–10.14 | 27 |
| HC | 0.54 | 0.07–1.0 | 0.0–3.03 | 27 |
| MG | 0.96 | 0.34–1.57 | 0.0–7.95 | 27 |
| Microglia | 0.0 | 0.0–0.03 | 0.0–1.42 | 27 |
| RGC | 63.59 | 37.65–77.61 | 1.83–92.69 | 27 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.69 | 27 |
| Rod | 3.86 | 1.93–9.59 | 0.21–52.04 | 27 |

### 层: Chen_ancestry|naive  (n_donors=59, n_cells=1,052,958, 占图谱33.14%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 8.97 | 6.94–10.89 | 3.68–14.52 | 52 |
| Astrocyte | 0.38 | 0.11–0.96 | 0.0–5.38 | 52 |
| BC | 23.2 | 19.8–32.46 | 14.2–49.97 | 52 |
| Cone | 4.04 | 3.08–6.89 | 1.09–13.1 | 52 |
| HC | 4.26 | 2.89–8.65 | 1.45–13.25 | 52 |
| MG | 9.56 | 6.83–13.59 | 2.63–24.66 | 52 |
| Microglia | 0.18 | 0.07–0.27 | 0.0–1.22 | 52 |
| RGC | 3.34 | 1.5–8.51 | 0.05–14.87 | 52 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.99 | 52 |
| Rod | 47.19 | 12.6–55.85 | 0.0–68.17 | 52 |

### 层: Chen_b_GSE226108|NeuN+ ⚠分选设计层  (n_donors=4, n_cells=69,345, 占图谱2.18%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 71.85 | 62.23–78.53 | 46.93–85.01 | 4 |
| Astrocyte | 0.0 | 0.0–0.05 | 0.0–0.19 | 4 |
| BC | 0.86 | 0.49–1.32 | 0.42–1.7 | 4 |
| Cone | 1.17 | 0.57–2.47 | 0.12–5.02 | 4 |
| HC | 0.16 | 0.0–0.32 | 0.0–0.34 | 4 |
| MG | 0.62 | 0.34–1.06 | 0.14–1.73 | 4 |
| Microglia | 0.05 | 0.0–0.12 | 0.0–0.18 | 4 |
| RGC | 7.77 | 4.64–12.31 | 0.28–20.88 | 4 |
| RPE | 0.0 | 0.0–0.0 | 0.0–0.01 | 4 |
| Rod | 15.5 | 2.89–30.63 | 1.79–39.29 | 4 |

### 层: Chen_b_GSE226108|naive  (n_donors=4, n_cells=200,055, 占图谱6.3%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 9.22 | 8.41–9.83 | 7.29–10.34 | 4 |
| Astrocyte | 0.46 | 0.36–0.48 | 0.13–0.5 | 4 |
| BC | 28.34 | 26.71–29.88 | 25.83–30.46 | 4 |
| Cone | 4.14 | 3.59–4.92 | 3.0–6.17 | 4 |
| HC | 4.69 | 4.08–5.81 | 3.64–7.76 | 4 |
| MG | 4.91 | 4.52–7.43 | 4.44–13.89 | 4 |
| Microglia | 0.09 | 0.08–0.09 | 0.06–0.1 | 4 |
| RGC | 3.37 | 2.37–3.98 | 0.88–4.33 | 4 |
| RPE | 0.0 | 0.0–0.02 | 0.0–0.09 | 4 |
| Rod | 45.1 | 39.0–48.76 | 26.42–54.02 | 4 |

### 层: Chen_c_GSE247157|naive  (n_donors=20, n_cells=153,621, 占图谱4.83%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 7.32 | 6.72–8.86 | 5.19–13.14 | 20 |
| Astrocyte | 0.95 | 0.64–1.2 | 0.21–2.93 | 20 |
| BC | 20.07 | 17.97–23.82 | 13.5–37.68 | 20 |
| Cone | 4.06 | 3.27–5.56 | 2.63–6.89 | 20 |
| HC | 2.58 | 2.18–3.86 | 0.49–7.33 | 20 |
| MG | 10.35 | 8.15–12.16 | 2.1–24.38 | 20 |
| Microglia | 0.15 | 0.09–0.23 | 0.0–0.99 | 20 |
| RGC | 3.46 | 2.7–5.73 | 0.25–9.67 | 20 |
| RPE | 0.0 | 0.0–0.1 | 0.0–0.35 | 20 |
| Rod | 51.45 | 39.06–55.46 | 6.64–66.68 | 20 |

### 层: Chen_rgc|NeuN+ ⚠分选设计层  (n_donors=7, n_cells=162,687, 占图谱5.12%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 52.69 | 36.34–67.52 | 17.44–84.75 | 7 |
| Astrocyte | 0.02 | 0.0–0.03 | 0.0–0.06 | 7 |
| BC | 0.88 | 0.63–1.01 | 0.45–1.1 | 7 |
| Cone | 1.09 | 0.28–4.11 | 0.08–7.45 | 7 |
| HC | 0.1 | 0.08–0.13 | 0.04–0.21 | 7 |
| MG | 0.16 | 0.12–0.28 | 0.06–0.85 | 7 |
| Microglia | 0.03 | 0.0–0.08 | 0.0–0.2 | 7 |
| RGC | 29.9 | 23.74–59.02 | 0.0–79.69 | 7 |
| RPE | 0.0 | 0.0–0.03 | 0.0–0.22 | 7 |
| Rod | 3.24 | 1.74–6.88 | 0.74–14.5 | 7 |

### 层: Shekhar_GSE237204|naive  (n_donors=17, n_cells=177,371, 占图谱5.58%)

| 细胞类 | 供者中位% | 供者IQR% | 供者range% | n供者 |
|---|---|---|---|---|
| AC | 23.69 | 9.75–49.31 | 4.63–70.83 | 17 |
| Astrocyte | 0.0 | 0.0–0.19 | 0.0–2.18 | 17 |
| BC | 2.0 | 0.55–7.69 | 0.13–21.69 | 17 |
| Cone | 0.2 | 0.0–1.03 | 0.0–4.04 | 17 |
| HC | 0.32 | 0.0–0.89 | 0.0–3.77 | 17 |
| MG | 0.94 | 0.14–2.4 | 0.0–6.44 | 17 |
| Microglia | 0.0 | 0.0–0.15 | 0.0–0.43 | 17 |
| RGC | 37.77 | 18.86–72.36 | 1.54–92.41 | 17 |
| RPE | 0.0 | 0.0–0.0 | 0.0–2.03 | 17 |
| Rod | 7.84 | 0.88–34.94 | 0.16–53.07 | 17 |

## 亚型层 (类内注释细胞占比%, pooled within class 口径)
- **BC** (BC 亚型注释细胞): flat midget bipolar cell 20.9%; invaginating midget 15.4%; rod bipolar cell 14.7%; diffuse bipolar 2 9.9%; DB1 7.3%; DB4 7.1%; DB3b 5.1%; giant bipolar (GB) 3.7%; DB3a 3.2%; DB6 2.7%
- **AC** (AC 注释细胞): GABAergic amacrine 63.5%; glycinergic amacrine 23.0%; amacrine (unclassified) 10.0%; starburst amacrine 3.5%
- **RGC** (RGC 注释细胞): OFF midget GC 50.2%; ON midget GC 38.0%; retinal ganglion cell (未分型) 7.8%; OFF parasol 2.5%; ON parasol 1.5%
- **HC** (HC 注释细胞): H1 85.2%; H2 14.8%
- **Cone** (Cone 注释细胞): retinal cone cell 93.3%; S cone 6.7%

## 状态层
- **Microglia** [homeostatic]: P2RY12, TMEM119, CX3CR1, IRF8, C1QA/B, TYROBP, AIF1, SALL1, HEXB (证据 A+B)
- **Müller glia** [homeostatic]: RLBP1, GLUL, SOX9, S100B, VIM, AQP4(低) (证据 A)
- **RPE** [homeostatic]: BEST1, RPE65, LRAT, RDH5, MITF, TTR (证据 A)
- **Astrocyte** [homeostatic (血管周围)]: GFAP, AQP4, SLC1A3, S100B (证据 A)

## 旗标语义
**expected_low_but_present**: Microglia (0.05~0.8%); RPE (≈0, 混入即>1%); Astrocyte (0.1~1.5%)

**unexpected**: progenitor/PCNA+ 大簇 (成人视网膜); 大量肥大细胞/嗜酸细胞

**contamination_suspect**: 高 MT 光感受器碎片区 (解离应激, 见疾病条目); 外周血髓系大簇 (FCN1/LYZ) —— 全视网膜标本血液残留旗

## 注意事项
1. 单样本比例强烈受取材/分选设计影响 (NeuN± 核分选、RGC 富集、fovea vs 周边、lobe vs macular): 跨研究 spread (C 级区间推导依据) = Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy 6 组 pooled 的 min~max, 已排除 RGC 靶向组。
2. HRCA 10 类词表不含内皮/周细胞 (神经视网膜整合未收录血管类)。真实全视网膜含低比例血管成分; 注释数据出现 Endo/Pericyte 小簇属正常血管, 不打 contamination 旗 (对照疾病条目)。
3. RGC 富集样本 (如 Chen_rgc 46.2% RGC, Shekhar legacy 43.6%) 高比例是设计使然 —— 判'异常'前必须先查该数据集建库策略。
4. 发育/类器官标本不适用本基线 (progenitor 与亚型比例完全不同, 锚 DEV_DUAL/RETINA_ORGANOIDS)。
5. PI 提醒: 公开数据自注释本身可能不准 —— 本条所有比例是'带证据等级的先验', 与数据打架时旗标上报, 不硬凑。
6. v1.1 (本条): 比例口径已从'全细胞 pooled + 跨研究 spread'升级为'供者级分层分布' (Astra T2); 旧 pooled 值保留于 pooled_all_cells 仅作对照 —— 3.17M 核中 Chen_ancestry 占 42.6%, pooled 大供者压秤。
7. NeuN+ 分选层系统性抬升神经元类/压低 MG·Astro·RPE; 对照样本是否做过核分选前, 不得混用两层区间。
8. suspension_type 全核 —— snRNA 内含子 reads 计入 (intronic_reads_counted=yes), 与 scRNA 细胞悬液数据的类比例不可直接互比 (Astra T2: scRNA vs snRNA 差别足以改变观察组成)。
9. v1.1 (KB2c t_be336eee): 主档口径升级为 adult-only (donor_age>=18y, 裁定 Q2) —— v1.0 混口径(曾含 3-17 岁发育期供者; 实测胎儿期 0 核) 完整保留于 donor_level_adult_pool_contrast (tier_id=...__adult_pool__v1.0), 引用 v1.0 数字必须挂对照档身份, 两档签名不混用 (红线)。

## 出处清单
| sid | 类型 | 标签 |
|---|---|---|
| `HRCA317M` | dataset | HRCA CELLxGENE 合并版 3,177,310 cells (10 majorclass, 全 normal, 6 研究/104 donors, fovea~periphery) (PMID 41578023) |
| `HRCA_PAPER` | paper | Li et al., Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nat Genet 2026 (整版 ~3.9M cells, 123 RNA 类) (PMID 41578023) |
| `FOVEA_PERIPH` | paper | Cell Atlas of the Human Fovea and Peripheral Retina (2020) — 中央凹/周边共享类型但比例与表达有区域差 (PMID 32555229) |
| `AGING_ATLAS` | paper | A single-cell transcriptome atlas of the aging human and macaque retina (2021) (PMID 34691611) |
| `MULTIOMICS_ATLAS` | paper | A multi-omics atlas of the human retina at single-cell resolution (2023) (PMID 37388908) |
| `RETINA_ORGANOIDS` | paper | Cell Types of the Human Retina and Its Organoids at Single-Cell Resolution (2020) (PMID 32946783) |
| `DEV_DUAL` | paper | Single cell dual-omic atlas of the human developing retina (2024) — 发育期含 progenitor, 成体基线不适用 (PMID 39117640) |
| `RETLIB41` | kb | 本地 marker 库 markers_v4.1_clean.json v4.1-clean-P0.4  |
| `D001_DONOR_LEVEL` | dataset | 本条供者级分布由 build_baselines.py (KB1v2 t_16c3e020; KB2c 发育轴单列 t_be336eee) 从 /mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad obs 复算 (PMID 41578023) |

