# 疾病先验: 增殖期糖尿病视网膜病变 (PDR)

> schema: `eyekb-prior/1.0` | entry_id: `proliferative_DR` | 冻结: 2026-09-23 | 来源卡: t_39182aa2
> 本文件由 `/mnt/D/EyeKB/scripts/priors/build_priors.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。
> **判读纪律**: 本条是先验与 QC 旗, 禁入打分; 与数据打架 → 旗标上报, 不许硬凑。

## 证据等级口径

- **A**: 本地实测复算
- **B**: 文献原文直接报告
- **C**: 模型/发育证据外推
- **D**: 综述背景(仅定性)

## 预期 细胞×状态 矩阵 (按组织端)

### fibrovascular_membrane  [A+B]

- Macrophage: 组织型驻留(SELENOP/FOLR2) + 招募型经典单核(FCN1/LYZ) + 泡沫样DAM-LAM(GPNMB/TREM2/SPP1) + MHC-II高APC + 血红素应激(HMOX1)
- Endothelial: 病理态(PLVAP/NDUFA4L2/HIF1A/ICAM1/VCAM1) + tip/stak 亚态(DLL4; C级外推自 TIPCELL_DEV/RAB5IF)
- Pericyte→Myofibroblast 连续转变 (PRRX1 驱动, B: PRRX1)
- Stromal: COL1A1/COL3A1/FN1 高细胞外基质
- Lymphoid: T(CD69 活化)、浆细胞低比例
- Proliferating: MKI67+ 群存在 (含 MKI67+ 小胶质, B: PDR_MKI67MG)
- Glial: Müller/反应性胶质瘢痕成分 (GFAP↑, B: GLIA_RDG)

### vitreous  [B]

- T 细胞绝对优势 (91.6%, B: VITREOUS_T), 中性粒细胞几乎缺如
- 解读: 玻璃体与膜标本组成完全不同 —— 组织端必须先分清

### retina_adjacent  [B]

- 早中期 DR 视网膜: 小胶质状态改变无大规模髓系涌入 (B: MG_EARLY_DR/DR_RETINA_SC)
- Müller 反应性 (REDD1/gliosis, B: MULLER_REDD1)
- 神经元比例不因 PDR 本身大涨 —— 膜≠视网膜

## 非预期旗

- **视网膜神经元 (Rod/Cone/BC/AC/HC) 大簇** — 膜标本 >5% → 旗标: 标本疑含视网膜本体, 报PI
- **光感受器外节/裂解碎片高背景 (HBA 除外)** — 线粒体+ROS 应激签名弥散 → 解离应激旗, 不打疾病旗
- **progenitor/类器官特征** — 任何临床膜标本 → 疑样本混入/注释错误, 旗标上报
- **肥大细胞/嗜酸粒细胞富集群** — 过敏背景 → unexpected-report

## 污染旗

- **外周血 (经典单核 FCN1/LYZ/S100A8/9 + 血小板 PF4/PPBP + 中性粒 FCGR3B/CSF3R)** → 手术标本血液涌入 —— 髓系计数解读必须先扣血源成分 (B: GSE165784 v2 B10/sub14 A级实测)
- **RPE/脉络膜色素成分 (BEST1/RPE65/TYR+黑素)** → 穿透取材/合并孔源性脱离操作
- **玻璃体来源 T 优势 (对照 91.6%)** → 玻璃体切除标本残留液相成分

## 签名轴 (marker panels)

- `tissue_resident_mac`: SELENOP, MRC1, FOLR2, CD163, STAB1, VSIG4, CD5L
- `recruited_monocyte`: FCN1, VCAN, S100A8, S100A9, CD14, SELL, S100A12
- `foam_DAM_LAM`: GPNMB, LIPA, CTSD, LGMN, PLD3, TREM2, SPP1, APOE, MMP9
- `heme_stress_mac`: HMOX1, FTL, FTH1, CD163
- `MHCII_high_APC`: HLA-DRA, HLA-DRB1, CD74, HLA-DQA1, HLA-DPB1
- `patho_endothelial`: PLVAP, NDUFA4L2, HIF1A, ICAM1, VCAM1, DLL4, ESM1
- `pericyte_to_myofibro`: PRRX1, ACTA2, TAGLN, POSTN, COL1A1, COL1A2, CTHRC1, TIMP1
- `reactive_glia`: GFAP, VIM, CRYAB, CLU, TIMP1
- `blood_platelet`: PPBP, PF4

*签名溯源: markers_membrane_v1.json (canonical/data_driven/pmid_context 三态溯源) + v2 实测簇*

## 注意事项

1. tip/stalk 内皮亚态: 人 PDR 膜直接单细胞证据有限 (DLL4+ tip 生物学多来自发育/OIR), 标 C 级 —— 预期存在但比例不设区间。
2. PDR 与 RRD 膜的组成差异尚无充分独立对照 —— 任何'疾病特异簇'判定必须做疾病端对照后才可写 (v2 草稿 RRD 分层教训)。
3. PI: PDR 注释本身不一定准 → 本先验为对照与 QC 旗, 非真值; 与数据冲突时输出'先验与数据打架清单'上报。

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
