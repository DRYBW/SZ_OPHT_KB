# 组成基线: 人(正常)神经视网膜细胞组成

> schema: `eyekb-prior/1.0` | entry_id: `human_retina` | 冻结: 2026-09-23 | 来源卡: t_39182aa2
> 本文件由 `/mnt/D/EyeKB/scripts/priors/build_priors.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。
> **判读纪律**: 本条是先验与 QC 旗, 禁入打分; 与数据打架 → 旗标上报, 不许硬凑。

## 证据等级口径

- **A**: 本地实测复算(带路径)
- **B**: 文献原文直接报告
- **C**: A级源数据跨研究分布推得的经验区间

## 主表: 细胞类型 × 比例区间

| 细胞类型 | 中文名 | HRCA 实测% | 预期区间% | 跨研究 spread% | 本地库 marker | 证据 | 备注 |
|---|---|---|---|---|---|---|---|
| Rod | 视杆光感受器 | 33.55 | 28–46 | 19.05–47.77 | RHO, NRL, NR2E3, PDE6B, GNAT1 | A | — |
| Cone | 视锥光感受器 | 4.0 | 1.5–7 | 0.95–6.44 | OPN1SW, OPN1MW, ARR3, PDE6H, GNAT2 | A | — |
| BC | 双极细胞 | 21.75 | 12–33 | 5.54–32.64 | VSX2, GRM6, CACNA1S, ISL1, OTX2 | A | — |
| AC | 无长突细胞 | 17.99 | 8–28 | 7.87–27.67 | TFAP2A, GAD1, GAD2, SLC6A9, ONECUT2 | A | — |
| HC | 水平细胞 | 2.54 | 1–8 | 0.51–7.65 | ONECUT1, ONECUT3, GAD1, ISL1, CX3CR1 | A | — |
| RGC | 神经节细胞 | 12.58 | 3–15 | 0.18–43.64 | RBPMS, SLC17A6, POU4F1, POU4F2, NEFL | A | RGC 靶向研究 (Chen_rgc pooled 46.2%, Shekhar_legacy 43.6%) 为分选/富集设计, 高比例≠异常 |
| MG | Müller 胶质 | 6.97 | 3–12 | 1.93–10.44 | RLBP1, GLUL, SOX9, VIM, S100B | A | — |
| Astrocyte | 星形胶质 | 0.44 | 0.1–1.5 | 0.23–1.03 | GFAP, AQP4, S100B, VIM, SLC1A3 | A | — |
| Microglia | 小胶质 | 0.15 | 0.05–0.8 | 0.0–0.26 | C1QB | A | — |
| RPE | 视网膜色素上皮 | 0.03 | 0–1.0 | 0.0–0.12 | BEST1, RPE65, TTR, LRAT, RDH5 | A | 神经视网膜切片中 RPE 高比例提示 RPE/脉络膜混入 (非神经视网膜本体成分) |

## 亚型层 (类内注释细胞占比%)

*cell_type 列细分仅覆盖该 majorclass 已精细注释细胞; % 为亚型/类内注释细胞数*

- **BC** (BC 亚型注释细胞): flat midget bipolar cell 20.9%; invaginating midget 15.4%; rod bipolar cell 14.7%; diffuse bipolar 2 9.9%; DB1 7.3%; DB4 7.1%; DB3b 5.1%; giant bipolar (GB) 3.7%; DB3a 3.2%; DB6 2.7%
- **AC** (AC 注释细胞): GABAergic amacrine 63.5%; glycinergic amacrine 23.0%; amacrine (unclassified) 10.0%; starburst amacrine 3.5%
- **RGC** (RGC 注释细胞): OFF midget GC 50.2%; ON midget GC 38.0%; retinal ganglion cell (未分型) 7.8%; OFF parasol 2.5%; ON parasol 1.5%
- **HC** (HC 注释细胞): H1 85.2%; H2 14.8%
- **Cone** (Cone 注释细胞): retinal cone cell 93.3%; S cone 6.7%

## 状态层 (细胞类型×状态)

| 细胞类型 | 状态 | marker | 证据 | 备注 |
|---|---|---|---|---|
| Microglia | homeostatic | P2RY12, TMEM119, CX3CR1, IRF8, C1QA/B, TYROBP, AIF1, SALL1, HEXB | A+B | retina 库 legacy_v4 + AUC 候选合并; 正常视网膜内占比极低 (HRCA 0.15%) |
| Müller glia | homeostatic | RLBP1, GLUL, SOX9, S100B, VIM, AQP4(低) | A | — |
| RPE | homeostatic | BEST1, RPE65, LRAT, RDH5, MITF, TTR | A | 神经视网膜标本中 RPE 应近零; 出现即触发 RPE/脉络膜混入旗 |
| Astrocyte | homeostatic (血管周围) | GFAP, AQP4, SLC1A3, S100B | A | GFAP 上调=反应性胶质旗, 见疾病条目 |

## 旗标语义

**预期但比例低**:

- Microglia (0.05~0.8%)
- RPE (≈0, 混入即>1%)
- Astrocyte (0.1~1.5%)

**非预期 (→ unexpected 旗)**:

- progenitor/PCNA+ 大簇 (成人视网膜)
- 大量肥大细胞/嗜酸细胞

**污染嫌疑 (→ contamination-suspect 旗)**:

- 高 MT 光感受器碎片区 (解离应激, 见疾病条目)
- 外周血髓系大簇 (FCN1/LYZ) —— 全视网膜标本血液残留旗

## 注意事项

1. 单样本比例强烈受取材/分选设计影响 (NeuN± 核分选、RGC 富集、fovea vs 周边、lobe vs macular): 跨研究 spread (C 级区间推导依据) = Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy 6 组 pooled 的 min~max, 已排除 RGC 靶向组。
2. HRCA 10 类词表不含内皮/周细胞 (神经视网膜整合未收录血管类)。真实全视网膜含低比例血管成分; 注释数据出现 Endo/Pericyte 小簇属正常血管, 不打 contamination 旗 (对照疾病条目)。
3. RGC 富集样本 (如 Chen_rgc 46.2% RGC, Shekhar legacy 43.6%) 高比例是设计使然 —— 判'异常'前必须先查该数据集建库策略。
4. 发育/类器官标本不适用本基线 (progenitor 与亚型比例完全不同, 锚 DEV_DUAL/RETINA_ORGANOIDS)。
5. PI 提醒: 公开数据自注释本身可能不准 —— 本条所有比例是'带证据等级的先验', 与数据打架时旗标上报, 不硬凑。

## 出处清单

| sid | 类型 | 等级线索 | 标签 |
|---|---|---|---|
| `HRCA317M` | dataset | 41578023 | HRCA CELLxGENE 合并版 3,177,310 cells (10 majorclass, 全 normal, 6 研究/104 donors, fovea~periphery) |
| `HRCA_PAPER` | paper | 41578023 | Li et al., Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nat Genet 2026 (整版 ~3.9M cells, 123 RNA 类) |
| `FOVEA_PERIPH` | paper | 32555229 | Cell Atlas of the Human Fovea and Peripheral Retina (2020) — 中央凹/周边共享类型但比例与表达有区域差 |
| `AGING_ATLAS` | paper | 34691611 | A single-cell transcriptome atlas of the aging human and macaque retina (2021) |
| `MULTIOMICS_ATLAS` | paper | 37388908 | A multi-omics atlas of the human retina at single-cell resolution (2023) |
| `RETINA_ORGANOIDS` | paper | 32946783 | Cell Types of the Human Retina and Its Organoids at Single-Cell Resolution (2020) |
| `DEV_DUAL` | paper | 39117640 | Single cell dual-omic atlas of the human developing retina (2024) — 发育期含 progenitor, 成体基线不适用 |
| `RETLIB41` | kb | /mnt/D/EyeKB/kb/markers/markers_v4.1_clean.json | 本地 marker 库 markers_v4.1_clean.json v4.1-clean-P0.4 |
