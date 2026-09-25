# 组成基线: 人 PDR 纤维血管膜 (fibrovascular membrane)

> schema: `eyekb-prior/1.0` | entry_id: `human_pdr_membrane` | 冻结: 2026-09-23 | 来源卡: t_39182aa2
> 本文件由 `/mnt/D/EyeKB/scripts/priors/build_priors.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。
> **判读纪律**: 本条是先验与 QC 旗, 禁入打分; 与数据打架 → 旗标上报, 不许硬凑。

## 证据等级口径

- **A**: 本地实测复算(带路径)
- **B**: 文献原文直接报告
- **C**: 跨研究经验区间

## 主表: 区隔 × 比例

| 区隔 | PDR-only% | 全样本% | 细胞数(PDR) | 证据 | 说明 |
|---|---|---|---|---|---|
| myeloid (髓系合计 (巨噬/单核/DC/pDC, Track B 簇归属)) | 79.5 | 82.28 | 5,677 | A(计数)+B(定性) | PDR 膜以髓系为主是文献共识 (B: PDR_HU2022/PDR_JCI2023) 且本地实测一致 (A) |
| stromal_myofibro (肌成纤维 (COL1A1/COL1A2/ACTA2/TAGLN/POSTN/PRRX1)) | 4.4 | 3.69 | 317 | A(计数)+B(定性) | 纤维成分 = 膜标本命名主体; 周细胞→肌成纤维转变由 PRRX1 驱动 (B) |
| stromal_pericyte (周细胞 (RGS5/PDGFRB/NOTCH3/PRRX1)) | 3.5 | 2.48 | 250 | A(计数)+B(定性) | 血管壁细胞, 与内皮共同构成'纤维血管'三件套 |
| endothelial (内皮 (CLDN5/VWF/PECAM1; 病理态 PLVAP/DLL4/NDUFA4L2)) | 3.8 | 2.68 | 270 | A(计数)+B(定性) | 增殖血管端; tip/stalk 亚态证据主要来自发育/OIR 模型 (C 级外推) |
| lymphoid_T (T 细胞 (CD3D/CD2/CD69 活化)) | 4.7 | 3.52 | 333 | A(计数)+B(定性) | 膜标本存在; 注意与玻璃体液 (T 91.6%) 区分组织端 |
| lymphoid_plasma (浆细胞 (MZB1/JCHAIN/IGHG1)) | 0.8 | 0.61 | 58 | A(计数)+B(定性) | 低比例存在即符合预期 |
| proliferating (增殖群 (MKI67/TOP2A/CENPF; 来源混杂)) | 1.7 | 3.12 | 121 | A(计数)+B(定性) | PDR-only 口径增殖占比低于全样本 (RRD 应激髓系贡献大); MKI67+ 小胶质驱动新生 (B: PDR_MKI67MG) |
| glial_candidate (胶质候选 (Müller/反应性胶质瘢痕; CRYAB/CLU, RLBP1 缺)) | 1.6 | 1.62 | 116 | A(计数)+B(定性) | 纤维化膜含胶质瘢痕成分 (B: GLIA_RDG/MULLER_REDD1); 但本簇 marker 不完整 → 分不开旗, 不硬标 |

## 髓系状态层

| 细胞类型 | 状态 | 签名/说明 | 簇 | 全样本% | PDR-only% | 证据 |
|---|---|---|---|---|---|---|
| Macrophage | homeostatic-like | 组织型驻留巨噬 SELENOP/MRC1/FOLR2/STAB1/CD163 | B13+mye sub7 | 7.0 | 9.6 | A |
| Macrophage | foam_DAM_LAM | 泡沫样/脂质噬溶酶体 GPNMB/LIPA/PLD3/CTSD/TREM2/SPP1 | B5+sub10/sub12 | 10.0 | 14.0 | A |
| Macrophage | MHCII-high_APC | MHC-II 高呈递 HLA-DR/DQ/CD74 (B1/B3/B4 合并) | B1+B3+B4 | 25.5 | 28.7 | A |
| Macrophage | inflammatory_heme | 炎症/血红素应激 HMOX1/CCL3/CXCL8 | B2+sub8 | 10.7 | 13.2 | A |
| Monocyte | classical_blood | 外周血经典单核 FCN1/LYZ/VCAN/S100A8/9 (血液混入旗主体) | B10+sub14 | 6.8 | 9.5 | A |
| Monocyte | nonclassical | 非经典 FCGR3A+/CD14低 | B4 | 8.2 | 9.0 | A |
| Microglia | homeostatic | 驻留小胶质 P2RY12/TMEM119/CX3CR1 低比例; 膜标本中难与巨噬区分 | B0 部分 | — | — | B |
| Macrophage | RRD_stress | RRD 标本高MT/低氧应激态 (S100A8/9/NUPR1/FABP5/MMP9) — 非 PDR 特异 | B0+B6+sub0/1/2/11 | 21.7 | 3.9 | A |

## 旗标语义

**预期**:

- 髓系主导 (70~85%)
- 内皮+周细胞+肌成纤维三件套
- 泡沫样/DAM-LAM 巨噬
- MHC-II 高 APC
- T/浆细胞少量

**非预期 (→ unexpected 旗)**:

- 视网膜神经元大簇 (>5% → 标本疑含视网膜本体, 与'膜'命名冲突)
- progenitor/类器官特征 (膜标本不应有)
- RPE 大簇 (>3% → 疑非膜组织或取材含 RPE-脉络膜)

**污染嫌疑 (→ contamination-suspect 旗)**:

- 血液来源髓系 (FCN1/LYZ/S100A8 经典单核高) —— 手术标本血残留, 比例解读注意
- 血小板基因信号 (PF4/PPBP)
- 玻璃体 T 细胞优势成分混入 (对照 VITREOUS_T: 玻璃体 T 91.6%)

## 注意事项

1. GSE165784 = PDR 膜 + RRD(孔源性视网膜脱离) 膜混合数据集; RRD 占 29.1% 细胞。PDR 特异读数看 PDR-only 口径 (n=7,142); B0/B6/sub0/1/2/11 的应激态由 RRD 样本驱动, 不是 PDR 生物学 (v2 草稿留痕)。
2. 膜标本 ≠ 全视网膜: Rod/BC/AC/HC 神经元无独立簇属预期, 不打 unexpected 旗。
3. n=1~2 PDR donor 级差异大, 比例区间只到'量级'精度; 库内尚无第二套自算 PDR 膜数据交叉验证 (B 级文献锚未给精确%)。
4. PI 提醒: PDR 公开数据自注释不一定准 —— B 级条目只作定性方向, 数值裁决以 A 级本地复算为准。

## 出处清单

| sid | 类型 | 等级线索 | 标签 |
|---|---|---|---|
| `GSE165784V2` | dataset | 35061025 | GSE165784 人 PDR 纤维血管膜+RRD 膜 scRNA, v2 整合轨 Track B (harmonypy, 17 簇, 10,069 细胞; PDR-only 7,142) |
| `PDR_HU2022` | paper | 35061025 | Hu et al. Single-Cell Transcriptomics Reveals Novel Role of Microglia in Fibrovascular Membrane of PDR. Diabetes 2022 (GSE165784 原文) |
| `PDR_JCI2023` | paper | 37917183 | Single-cell transcriptomics analysis of PDR fibrovascular membranes. JCI Insight 2023 |
| `PDR_SOX15` | paper | 42601615 | Human single-cell atlas of PDR reveals a SOX15-overexpressing stromal population. J Transl Med 2026 |
| `PDR_MKI67MG` | paper | 40069725 | Single-cell analysis identifies MKI67+ microglia as drivers of neovascularization in PDR. J Transl Med 2025 |
| `PDR_NICHE` | paper | 40562775 | Metabolic reprogramming of the neovascular niche promotes regenerative angiogenesis in proliferative retinopathies. Nat Commun 2025 |
| `PRRX1` | paper | 41230906 | PRRX1 Orchestrates Pericyte-Myofibroblast Transition in Pathological Retinal Fibrosis. IOVS 2025 (库内) |
| `RAB5IF` | paper | 41390488 | Endothelial RAB5IF is required for pathological and developmental retinal angiogenesis. Nat Commun 2025 (库内) |
| `VITREOUS_T` | paper | 39220810 | Liquid Biopsy for PDR: Single-Cell Transcriptomics of Human Vitreous. Ophthalmol Sci 2024 — PDR 玻璃体 T 细胞 91.6% (对照组织: 玻璃体≠膜) |
| `MEMLIB` | kb | /mnt/D/EyeKB/kb/markers/markers_membrane_v1.json | 本地膜 marker 库 markers_membrane_v1.json v1-membrane-20260923 (逐基因溯源) |
| `MULLER_REDD1` | paper | 35167652 | Müller Glial Expression of REDD1 Is Required for Retinal Neurodegeneration... Diabetes 2022 (库内; 反应性胶质背景) |
| `GLIA_RDG` | paper | 32069977 | scRNA-seq in Human Retinal Degeneration Reveals Distinct Glial Cell Populations. Cells 2020 (库内; 人视网膜退变胶质状态) |
| `DR_RETINA_SC` | paper | 34006945 | In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying DR. Sci Rep 2021 (库内) |
| `MG_EARLY_DR` | paper | 38409074 | scRNA-seq reveals roles of unique retinal microglia types in early DR. DMS 2024 (库内) |
| `TIPCELL_DEV` | paper | 34273276 | Specialized endothelial tip cells guide neuroretina vascularization and blood-retina-barrier formation. Nat Commun 2021 (库内; tip/stalk 生物学来源, 发育/模型证据→PDR 外推 C 级) |
