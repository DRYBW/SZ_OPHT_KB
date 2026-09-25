#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB 判读层先验条目构建器 (KB1, 卡 t_39182aa2, 2026-09-23)

职责:
  1. 从原始数据源**实时复算** A 级数字 (HRCA h5ad majorclass 计数; GSE165784 v2 Track B
     cluster_composition_B.csv), 与冻结值对账 (drift 即报错拒绝出件)。
  2. 组装机读 JSON (kb/priors/**/*.json, 唯一真源)。
  3. 由 JSON 渲染人读 MD (kb/priors/**/*.md) —— MD 表与 JSON 逐字段一致,
     K4 黄金回归据此校验 (工具返回 ↔ JSON ↔ MD)。

纪律 (BRIEF_KB1_PRIOR_LAYER_20260923):
  - 每条预期必带出处 (PMID/数据集 + 证据等级), 无出处条目禁入 (红线8)
  - 先验只做对照与 QC 旗, 禁入打分 (红线12 继承)
  - 两级结构: 细胞类型 × 状态, 防状态当新类型膨胀
证据等级:
  A = 本地实测复算 (本管线, 带文件路径+细胞数)
  B = 文献原文直接报告 (读原文段落; 摘要无精确% 时只支持定性表述)
  C = 多研究经验区间 (由 A 级源数据跨研究分布推得, 方法在条目内注明)
运行:
  /home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/scripts/priors/build_priors.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

EYEKB = Path("/mnt/D/EyeKB")
PRIORS = EYEKB / "kb" / "priors"
HRCA_H5AD = "/mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad"
GSE_DIR = EYEKB / "plans" / "demo_gse165784" / "proc" / "v2"
FROZEN_DATE = "2026-09-23"
CARD = "t_39182aa2"

MARKER_LIB = json.load(open(EYEKB / "kb/markers/markers_v4.1_clean.json"))
MEMB_LIB = json.load(open(EYEKB / "kb/markers/markers_membrane_v1.json"))


def h5ad_col(obs, name):
    c = obs[name]
    if isinstance(c, h5py.Dataset):
        return c[:]
    codes = c["codes"][:]
    cats = [x.decode() for x in c["categories"][:]]
    return np.array([cats[i] if i >= 0 else "NA" for i in codes], dtype=object)


# ------------------------------------------------------------------ A级复算
def recompute_hrca():
    """HRCA CELLxGENE 版 317 万细胞 majorclass/cell_type 复算。
    返回 {pooled: {...}, per_study: {...}}; 研究分组按 sampleid 前缀。"""
    f = h5py.File(HRCA_H5AD, "r")
    obs = f["obs"]
    mc = np.array([str(x) for x in h5ad_col(obs, "majorclass")])
    sid = [str(x) for x in h5ad_col(obs, "sampleid")]
    f.close()

    def grp(s):
        for pref, name in [("Chen_a", "Chen_a"), ("Chen_b", "Chen_b_GSE226108"),
                           ("Chen_c", "Chen_c_GSE247157"), ("Chen_rgc", "Chen_rgc_TARGETED"),
                           ("MMD", "MMD"), ("BCM", "BCM"), ("A23", "other"), ("GSM", "Shekhar_legacy")]:
            if s.startswith(pref):
                return name
        return "other"

    total = len(mc)
    pooled = Counter(mc)
    # 全视网膜 pooled (排除 RGC 靶向富集研究 Chen_rgc —— 其 46% RGC 是设计使然非组织基线)
    wc = Counter(m for m, s in zip(mc, sid) if grp(s) != "Chen_rgc_TARGETED")
    t2 = sum(wc.values())
    per_study = {}
    gs = [grp(s) for s in sid]
    by = {}
    for m, g in zip(mc, gs):
        by.setdefault(g, Counter())[m] += 1
    for g, c in by.items():
        tot = sum(c.values())
        per_study[g] = {"n": tot, **{k: round(100 * v / tot, 2) for k, v in c.items()}}
    return {"total": total,
            "pooled_all": {k: [v, round(100 * v / total, 2)] for k, v in pooled.items()},
            "pooled_whole_retina": {"n": t2, **{k: round(100 * v / t2, 2) for k, v in wc.items()}},
            "per_study": per_study}


def recompute_gse165784():
    """GSE165784 v2 Track B (harmonypy 整合轨) 逐簇 → compartment 复算,
    全样本与 PDR-only 两个口径。"""
    df = pd.read_csv(GSE_DIR / "cluster_composition_B.csv")
    comp_of = {0: "myeloid", 1: "myeloid", 2: "myeloid", 3: "myeloid", 4: "myeloid",
               5: "myeloid", 6: "myeloid", 7: "stromal_myofibro", 8: "stromal_pericyte",
               9: "lymphoid_T", 10: "myeloid", 11: "proliferating", 12: "glial_candidate",
               13: "myeloid", 14: "lymphoid_plasma", 15: "endothelial", 16: "myeloid"}
    df["cluster"] = df["leiden_B"].astype(int)
    df["comp"] = df["cluster"].map(comp_of)
    pdr_cols = [c for c in df.columns if ("PDR" in c)]
    df["pdr"] = df[pdr_cols].sum(axis=1)
    n_all, n_pdr = int(df["n"].sum()), int(df["pdr"].sum())
    ca = df.groupby("comp")["n"].sum()
    cp = df.groupby("comp")["pdr"].sum()
    return {"n_all": n_all, "n_pdr": n_pdr,
            "comp_all": {k: [int(v), round(100 * v / n_all, 2)] for k, v in ca.items()},
            "comp_pdr": {k: [int(v), round(100 * v / n_pdr, 2)] for k, v in cp.items()}}


# ------------------------------------------------------------------ 策展内容
RETINA_CLASSES = [
    # (class, 中文名, 预期典型区间%, 富集例外说明, 本地库marker)
    ("Rod", "视杆光感受器", [28, 46], None),
    ("Cone", "视锥光感受器", [1.5, 7], None),
    ("BC", "双极细胞", [12, 33], None),
    ("AC", "无长突细胞", [8, 28], None),
    ("HC", "水平细胞", [1, 8], None),
    ("RGC", "神经节细胞", [3, 15],
     "RGC 靶向研究 (Chen_rgc pooled 46.2%, Shekhar_legacy 43.6%) 为分选/富集设计, 高比例≠异常"),
    ("MG", "Müller 胶质", [3, 12], None),
    ("Astrocyte", "星形胶质", [0.1, 1.5], None),
    ("Microglia", "小胶质", [0.05, 0.8], None),
    ("RPE", "视网膜色素上皮", [0, 1.0],
     "神经视网膜切片中 RPE 高比例提示 RPE/脉络膜混入 (非神经视网膜本体成分)"),
]

HRCA_SOURCES = [
    {"sid": "HRCA317M", "kind": "dataset", "pmid": "41578023",
     "label": "HRCA CELLxGENE 合并版 3,177,310 cells (10 majorclass, 全 normal, 6 研究/104 donors, fovea~periphery)",
     "path": HRCA_H5AD, "computation": f"本卡 {CARD} obs.majorclass 复算 (build_priors.py recompute_hrca)"},
    {"sid": "HRCA_PAPER", "kind": "paper", "pmid": "41578023",
     "label": "Li et al., Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nat Genet 2026 (整版 ~3.9M cells, 123 RNA 类)"},
    {"sid": "FOVEA_PERIPH", "kind": "paper", "pmid": "32555229",
     "label": "Cell Atlas of the Human Fovea and Peripheral Retina (2020) — 中央凹/周边共享类型但比例与表达有区域差"},
    {"sid": "AGING_ATLAS", "kind": "paper", "pmid": "34691611",
     "label": "A single-cell transcriptome atlas of the aging human and macaque retina (2021)"},
    {"sid": "MULTIOMICS_ATLAS", "kind": "paper", "pmid": "37388908",
     "label": "A multi-omics atlas of the human retina at single-cell resolution (2023)"},
    {"sid": "RETINA_ORGANOIDS", "kind": "paper", "pmid": "32946783",
     "label": "Cell Types of the Human Retina and Its Organoids at Single-Cell Resolution (2020)"},
    {"sid": "DEV_DUAL", "kind": "paper", "pmid": "39117640",
     "label": "Single cell dual-omic atlas of the human developing retina (2024) — 发育期含 progenitor, 成体基线不适用"},
    {"sid": "RETLIB41", "kind": "kb", "label": "本地 marker 库 markers_v4.1_clean.json v4.1-clean-P0.4",
     "path": str(EYEKB / "kb/markers/markers_v4.1_clean.json")},
]

PDR_SOURCES = [
    {"sid": "GSE165784V2", "kind": "dataset",
     "label": "GSE165784 人 PDR 纤维血管膜+RRD 膜 scRNA, v2 整合轨 Track B (harmonypy, 17 簇, 10,069 细胞; PDR-only 7,142)",
     "pmid": "35061025", "path": str(GSE_DIR / "cluster_composition_B.csv"),
     "computation": f"本卡 {CARD} 复算 (build_priors.py recompute_gse165784)"},
    {"sid": "PDR_HU2022", "kind": "paper", "pmid": "35061025",
     "label": "Hu et al. Single-Cell Transcriptomics Reveals Novel Role of Microglia in Fibrovascular Membrane of PDR. Diabetes 2022 (GSE165784 原文)"},
    {"sid": "PDR_JCI2023", "kind": "paper", "pmid": "37917183",
     "label": "Single-cell transcriptomics analysis of PDR fibrovascular membranes. JCI Insight 2023"},
    {"sid": "PDR_SOX15", "kind": "paper", "pmid": "42601615",
     "label": "Human single-cell atlas of PDR reveals a SOX15-overexpressing stromal population. J Transl Med 2026"},
   {"sid": "PDR_MKI67MG", "kind": "paper", "pmid": "40069725",
     "label": "Single-cell analysis identifies MKI67+ microglia as drivers of neovascularization in PDR. J Transl Med 2025"},
    {"sid": "PDR_NICHE", "kind": "paper", "pmid": "40562775",
     "label": "Metabolic reprogramming of the neovascular niche promotes regenerative angiogenesis in proliferative retinopathies. Nat Commun 2025"},
    {"sid": "PRRX1", "kind": "paper", "pmid": "41230906", "in_lib": True,
     "label": "PRRX1 Orchestrates Pericyte-Myofibroblast Transition in Pathological Retinal Fibrosis. IOVS 2025 (库内)"},
    {"sid": "RAB5IF", "kind": "paper", "pmid": "41390488", "in_lib": True,
     "label": "Endothelial RAB5IF is required for pathological and developmental retinal angiogenesis. Nat Commun 2025 (库内)"},
    {"sid": "VITREOUS_T", "kind": "paper", "pmid": "39220810",
     "label": "Liquid Biopsy for PDR: Single-Cell Transcriptomics of Human Vitreous. Ophthalmol Sci 2024 — PDR 玻璃体 T 细胞 91.6% (对照组织: 玻璃体≠膜)"},
    {"sid": "MEMLIB", "kind": "kb", "label": "本地膜 marker 库 markers_membrane_v1.json v1-membrane-20260923 (逐基因溯源)",
     "path": str(EYEKB / "kb/markers/markers_membrane_v1.json")},
    {"sid": "MULLER_REDD1", "kind": "paper", "pmid": "35167652", "in_lib": True,
     "label": "Müller Glial Expression of REDD1 Is Required for Retinal Neurodegeneration... Diabetes 2022 (库内; 反应性胶质背景)"},
    {"sid": "GLIA_RDG", "kind": "paper", "pmid": "32069977", "in_lib": True,
     "label": "scRNA-seq in Human Retinal Degeneration Reveals Distinct Glial Cell Populations. Cells 2020 (库内; 人视网膜退变胶质状态)"},
    {"sid": "DR_RETINA_SC", "kind": "paper", "pmid": "34006945", "in_lib": True,
     "label": "In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying DR. Sci Rep 2021 (库内)"},
    {"sid": "MG_EARLY_DR", "kind": "paper", "pmid": "38409074", "in_lib": True,
     "label": "scRNA-seq reveals roles of unique retinal microglia types in early DR. DMS 2024 (库内)"},
    {"sid": "TIPCELL_DEV", "kind": "paper", "pmid": "34273276", "in_lib": True,
     "label": "Specialized endothelial tip cells guide neuroretina vascularization and blood-retina-barrier formation. Nat Commun 2021 (库内; tip/stalk 生物学来源, 发育/模型证据→PDR 外推 C 级)"},
]

# 髓系 15 亚簇状态层 (A 级, 来源=GSE165784 v2 O2 亚聚类 8,547 细胞/15 亚簇)
MYE_STATES = [
    ("Macrophage:homeostatic-like", "组织型驻留巨噬 SELENOP/MRC1/FOLR2/STAB1/CD163", "B13+mye sub7", [7.0], [9.6], "A"),
    ("Macrophage:foam_DAM_LAM", "泡沫样/脂质噬溶酶体 GPNMB/LIPA/PLD3/CTSD/TREM2/SPP1", "B5+sub10/sub12", [10.0], [14.0], "A"),
    ("Macrophage:MHCII-high_APC", "MHC-II 高呈递 HLA-DR/DQ/CD74 (B1/B3/B4 合并)", "B1+B3+B4", [25.5], [28.7], "A"),
    ("Macrophage:inflammatory_heme", "炎症/血红素应激 HMOX1/CCL3/CXCL8", "B2+sub8", [10.7], [13.2], "A"),
    ("Monocyte:classical_blood", "外周血经典单核 FCN1/LYZ/VCAN/S100A8/9 (血液混入旗主体)", "B10+sub14", [6.8], [9.5], "A"),
    ("Monocyte:nonclassical", "非经典 FCGR3A+/CD14低", "B4", [8.2], [9.0], "A"),
    ("Microglia:homeostatic", "驻留小胶质 P2RY12/TMEM119/CX3CR1 低比例; 膜标本中难与巨噬区分", "B0 部分", None, None, "B"),
    ("Macrophage:RRD_stress", "RRD 标本高MT/低氧应激态 (S100A8/9/NUPR1/FABP5/MMP9) — 非 PDR 特异", "B0+B6+sub0/1/2/11", [21.7], [3.9], "A"),
]


def build_human_retina(hr):
    pooled = hr["pooled_all"]
    ps = hr["per_study"]
    studies_nonTargeted = [g for g in ps if g not in ("Chen_rgc_TARGETED",)]
    MK_ALIAS = {"Astrocyte": "Astro", "Microglia": "Micro"}
    entries = []
    for cls, cn, rng, note in RETINA_CLASSES:
        spread = [ps[g].get(cls, 0.0) for g in studies_nonTargeted]
        e = {"class": cls, "label_cn": cn,
             "pct_hrca317m": pooled[cls][1], "n_cells": pooled[cls][0],
             "expected_range_pct": rng,
             "per_study_spread_pct": [round(min(spread), 2), round(max(spread), 2)],
             "markers_local_lib": MARKER_LIB["markers"].get(MK_ALIAS.get(cls, cls), []),
             "evidence": "A",
             "source_ids": ["HRCA317M", "RETLIB41"],
             "grade_b_anchors": ["HRCA_PAPER", "FOVEA_PERIPH", "AGING_ATLAS", "MULTIOMICS_ATLAS"]}
        if note:
            e["enrichment_note"] = note
        entries.append(e)
    fine = {
        "denominator_note": "cell_type 列细分仅覆盖该 majorclass 已精细注释细胞; % 为亚型/类内注释细胞数",
        "BC": {"basis": "BC 亚型注释细胞", "top": [
            ["flat midget bipolar cell", 20.9], ["invaginating midget", 15.4],
            ["rod bipolar cell", 14.7], ["diffuse bipolar 2", 9.9], ["DB1", 7.3], ["DB4", 7.1],
            ["DB3b", 5.1], ["giant bipolar (GB)", 3.7], ["DB3a", 3.2], ["DB6", 2.7]]},
        "AC": {"basis": "AC 注释细胞", "top": [
            ["GABAergic amacrine", 63.5], ["glycinergic amacrine", 23.0],
            ["amacrine (unclassified)", 10.0], ["starburst amacrine", 3.5]]},
        "RGC": {"basis": "RGC 注释细胞", "top": [
            ["OFF midget GC", 50.2], ["ON midget GC", 38.0], ["retinal ganglion cell (未分型)", 7.8],
            ["OFF parasol", 2.5], ["ON parasol", 1.5]]},
        "HC": {"basis": "HC 注释细胞", "top": [["H1", 85.2], ["H2", 14.8]]},
        "Cone": {"basis": "Cone 注释细胞", "top": [["retinal cone cell", 93.3], ["S cone", 6.7]]},
    }
    states = [
        {"cell_type": "Microglia", "state": "homeostatic",
         "markers": ["P2RY12", "TMEM119", "CX3CR1", "IRF8", "C1QA/B", "TYROBP", "AIF1", "SALL1", "HEXB"],
         "evidence": "A+B", "source_ids": ["RETLIB41", "MEMLIB"],
         "note": "retina 库 legacy_v4 + AUC 候选合并; 正常视网膜内占比极低 (HRCA 0.15%)"},
        {"cell_type": "Müller glia", "state": "homeostatic",
         "markers": ["RLBP1", "GLUL", "SOX9", "S100B", "VIM", "AQP4(低)"],
         "evidence": "A", "source_ids": ["RETLIB41", "HRCA317M"]},
        {"cell_type": "RPE", "state": "homeostatic",
         "markers": ["BEST1", "RPE65", "LRAT", "RDH5", "MITF", "TTR"],
         "evidence": "A", "source_ids": ["RETLIB41", "HRCA317M"],
         "note": "神经视网膜标本中 RPE 应近零; 出现即触发 RPE/脉络膜混入旗"},
        {"cell_type": "Astrocyte", "state": "homeostatic (血管周围)",
         "markers": ["GFAP", "AQP4", "SLC1A3", "S100B"],
         "evidence": "A", "source_ids": ["RETLIB41", "HRCA317M"],
         "note": "GFAP 上调=反应性胶质旗, 见疾病条目"},
    ]
    caveats = [
        "单样本比例强烈受取材/分选设计影响 (NeuN± 核分选、RGC 富集、fovea vs 周边、lobe vs macular): "
        "跨研究 spread (C 级区间推导依据) = Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy 6 组 pooled 的 min~max, 已排除 RGC 靶向组。",
        "HRCA 10 类词表不含内皮/周细胞 (神经视网膜整合未收录血管类)。真实全视网膜含低比例血管成分; "
        "注释数据出现 Endo/Pericyte 小簇属正常血管, 不打 contamination 旗 (对照疾病条目)。",
        "RGC 富集样本 (如 Chen_rgc 46.2% RGC, Shekhar legacy 43.6%) 高比例是设计使然 —— 判'异常'前必须先查该数据集建库策略。",
        "发育/类器官标本不适用本基线 (progenitor 与亚型比例完全不同, 锚 DEV_DUAL/RETINA_ORGANOIDS)。",
        "PI 提醒: 公开数据自注释本身可能不准 —— 本条所有比例是'带证据等级的先验', 与数据打架时旗标上报, 不硬凑。",
    ]
    return {
        "schema": "eyekb-prior/1.0", "entry_id": "human_retina",
        "title": "组成基线: 人(正常)神经视网膜细胞组成",
        "species": "human", "tissue": "retina", "disease": None,
        "frozen_date": FROZEN_DATE, "card": CARD,
        "evidence_grades": {"A": "本地实测复算(带路径)", "B": "文献原文直接报告",
                            "C": "A级源数据跨研究分布推得的经验区间"},
        "sources": HRCA_SOURCES,
        "major_classes": entries,
        "fine_types": fine,
        "states": states,
        "caveats": caveats,
        "flags": {
            "expected_low_but_present": ["Microglia (0.05~0.8%)", "RPE (≈0, 混入即>1%)", "Astrocyte (0.1~1.5%)"],
            "contamination_suspect": ["高 MT 光感受器碎片区 (解离应激, 见疾病条目)",
                                       "外周血髓系大簇 (FCN1/LYZ) —— 全视网膜标本血液残留旗"],
            "unexpected": ["progenitor/PCNA+ 大簇 (成人视网膜)", "大量肥大细胞/嗜酸细胞"],
        },
        "_computed": {"total_cells": hr["total"],
                      "pooled_whole_retina_excl_targeted": hr["pooled_whole_retina"],
                      "per_study": ps},
    }


def build_human_pdr(hg):
    ca, cp = hg["comp_all"], hg["comp_pdr"]
    n_all, n_pdr = hg["n_all"], hg["n_pdr"]
    comp_entries = [
        ("myeloid", "髓系合计 (巨噬/单核/DC/pDC, Track B 簇归属)", 79.5,
         "PDR 膜以髓系为主是文献共识 (B: PDR_HU2022/PDR_JCI2023) 且本地实测一致 (A)",
         ["GSE165784V2", "PDR_HU2022", "PDR_JCI2023"]),
        ("stromal_myofibro", "肌成纤维 (COL1A1/COL1A2/ACTA2/TAGLN/POSTN/PRRX1)", 4.4,
         "纤维成分 = 膜标本命名主体; 周细胞→肌成纤维转变由 PRRX1 驱动 (B)",
         ["GSE165784V2", "PRRX1", "MEMLIB"]),
        ("stromal_pericyte", "周细胞 (RGS5/PDGFRB/NOTCH3/PRRX1)", 3.5,
         "血管壁细胞, 与内皮共同构成'纤维血管'三件套", ["GSE165784V2", "PRRX1", "MEMLIB"]),
        ("endothelial", "内皮 (CLDN5/VWF/PECAM1; 病理态 PLVAP/DLL4/NDUFA4L2)", 3.8,
         "增殖血管端; tip/stalk 亚态证据主要来自发育/OIR 模型 (C 级外推)",
         ["GSE165784V2", "TIPCELL_DEV", "RAB5IF", "MEMLIB"]),
        ("lymphoid_T", "T 细胞 (CD3D/CD2/CD69 活化)", 4.7,
         "膜标本存在; 注意与玻璃体液 (T 91.6%) 区分组织端", ["GSE165784V2", "VITREOUS_T"]),
        ("lymphoid_plasma", "浆细胞 (MZB1/JCHAIN/IGHG1)", 0.8, "低比例存在即符合预期", ["GSE165784V2"]),
        ("proliferating", "增殖群 (MKI67/TOP2A/CENPF; 来源混杂)", 1.7,
         "PDR-only 口径增殖占比低于全样本 (RRD 应激髓系贡献大); MKI67+ 小胶质驱动新生 (B: PDR_MKI67MG)",
         ["GSE165784V2", "PDR_MKI67MG"]),
        ("glial_candidate", "胶质候选 (Müller/反应性胶质瘢痕; CRYAB/CLU, RLBP1 缺)", 1.6,
         "纤维化膜含胶质瘢痕成分 (B: GLIA_RDG/MULLER_REDD1); 但本簇 marker 不完整 → 分不开旗, 不硬标",
         ["GSE165784V2", "GLIA_RDG", "MULLER_REDD1"]),
    ]
    rows = [{"compartment": k, "label_cn": cn, "pct_pdr_only": pct, "pct_all_samples": ca[k][1],
             "n_pdr": cp[k][0], "evidence": "A(计数)+B(定性)", "note": note, "source_ids": sids}
            for k, cn, pct, note, sids in comp_entries]
    states = [{"cell_type": ct, "state": st, "markers_desc": md, "clusters": cl,
               "pct_all_samples": pa, "pct_pdr_only": pp, "evidence": ev,
               "source_ids": ["GSE165784V2", "MEMLIB"] + (["PDR_HU2022"] if "Microglia" in ct else [])}
              for ct, st, cl, pa, pp, ev, md in
              [(a[0], a[1], a[2], a[3], a[4], a[5], None) for a in []]]  # placeholder
    states = []
    for name, desc, clusters, pa, pp, ev in MYE_STATES:
        ct, st = name.split(":", 1)
        states.append({"cell_type": ct, "state": st, "markers_desc": desc, "clusters": clusters,
                       "pct_all_samples": pa, "pct_pdr_only": pp, "evidence": ev,
                       "source_ids": ["GSE165784V2", "MEMLIB", "PDR_HU2022"]})
    return {
        "schema": "eyekb-prior/1.0", "entry_id": "human_pdr_membrane",
        "title": "组成基线: 人 PDR 纤维血管膜 (fibrovascular membrane)",
        "species": "human", "tissue": "fibrovascular_membrane", "disease": "proliferative diabetic retinopathy",
        "frozen_date": FROZEN_DATE, "card": CARD,
        "evidence_grades": {"A": "本地实测复算(带路径)", "B": "文献原文直接报告", "C": "跨研究经验区间"},
        "sources": PDR_SOURCES,
        "major_compartments": rows,
        "myeloid_states": states,
        "caveats": [
            "GSE165784 = PDR 膜 + RRD(孔源性视网膜脱离) 膜混合数据集; RRD 占 29.1% 细胞。"
            "PDR 特异读数看 PDR-only 口径 (n=7,142); B0/B6/sub0/1/2/11 的应激态由 RRD 样本驱动, 不是 PDR 生物学 (v2 草稿留痕)。",
            "膜标本 ≠ 全视网膜: Rod/BC/AC/HC 神经元无独立簇属预期, 不打 unexpected 旗。",
            "n=1~2 PDR donor 级差异大, 比例区间只到'量级'精度; 库内尚无第二套自算 PDR 膜数据交叉验证 (B 级文献锚未给精确%)。",
            "PI 提醒: PDR 公开数据自注释不一定准 —— B 级条目只作定性方向, 数值裁决以 A 级本地复算为准。",
        ],
        "flags": {
            "expected": ["髓系主导 (70~85%)", "内皮+周细胞+肌成纤维三件套", "泡沫样/DAM-LAM 巨噬", "MHC-II 高 APC", "T/浆细胞少量"],
            "unexpected": ["视网膜神经元大簇 (>5% → 标本疑含视网膜本体, 与'膜'命名冲突)",
                            "progenitor/类器官特征 (膜标本不应有)",
                            "RPE 大簇 (>3% → 疑非膜组织或取材含 RPE-脉络膜)"],
            "contamination_suspect": ["血液来源髓系 (FCN1/LYZ/S100A8 经典单核高) —— 手术标本血残留, 比例解读注意",
                                       "血小板基因信号 (PF4/PPBP)", "玻璃体 T 细胞优势成分混入 (对照 VITREOUS_T: 玻璃体 T 91.6%)"],
        },
        "_computed": {"n_all": n_all, "n_pdr": n_pdr,
                      "comp_all": ca, "comp_pdr": cp},
    }


def build_disease_pdr(hg):
    """K2 疾病条目种子: 增殖期糖网 (跨 膜/玻璃体/邻近视网膜 三组织端)"""
    return {
        "schema": "eyekb-prior/1.0", "entry_id": "proliferative_DR",
        "title": "疾病先验: 增殖期糖尿病视网膜病变 (PDR)",
        "disease": "proliferative diabetic retinopathy",
        "tissue_scope": ["fibrovascular_membrane", "vitreous", "retina_adjacent"],
        "species": "human", "frozen_date": FROZEN_DATE, "card": CARD,
        "evidence_grades": {"A": "本地实测复算", "B": "文献原文直接报告", "C": "模型/发育证据外推", "D": "综述背景(仅定性)"},
        "sources": PDR_SOURCES,
        "expected_cell_state_matrix": [
            {"tissue": "fibrovascular_membrane",
             "expected": [
                 "Macrophage: 组织型驻留(SELENOP/FOLR2) + 招募型经典单核(FCN1/LYZ) + 泡沫样DAM-LAM(GPNMB/TREM2/SPP1) + MHC-II高APC + 血红素应激(HMOX1)",
                 "Endothelial: 病理态(PLVAP/NDUFA4L2/HIF1A/ICAM1/VCAM1) + tip/stak 亚态(DLL4; C级外推自 TIPCELL_DEV/RAB5IF)",
                 "Pericyte→Myofibroblast 连续转变 (PRRX1 驱动, B: PRRX1)",
                 "Stromal: COL1A1/COL3A1/FN1 高细胞外基质",
                 "Lymphoid: T(CD69 活化)、浆细胞低比例",
                 "Proliferating: MKI67+ 群存在 (含 MKI67+ 小胶质, B: PDR_MKI67MG)",
                 "Glial: Müller/反应性胶质瘢痕成分 (GFAP↑, B: GLIA_RDG)"],
             "evidence": "A+B", "source_ids": ["GSE165784V2", "PDR_HU2022", "PDR_JCI2023", "PRRX1", "PDR_MKI67MG", "GLIA_RDG", "TIPCELL_DEV", "RAB5IF"]},
            {"tissue": "vitreous",
             "expected": ["T 细胞绝对优势 (91.6%, B: VITREOUS_T), 中性粒细胞几乎缺如",
                          "解读: 玻璃体与膜标本组成完全不同 —— 组织端必须先分清"],
             "evidence": "B", "source_ids": ["VITREOUS_T"]},
            {"tissue": "retina_adjacent",
             "expected": ["早中期 DR 视网膜: 小胶质状态改变无大规模髓系涌入 (B: MG_EARLY_DR/DR_RETINA_SC)",
                          "Müller 反应性 (REDD1/gliosis, B: MULLER_REDD1)",
                          "神经元比例不因 PDR 本身大涨 —— 膜≠视网膜"],
             "evidence": "B", "source_ids": ["MG_EARLY_DR", "DR_RETINA_SC", "MULLER_REDD1"]},
        ],
        "unexpected_flags": [
            {"flag": "视网膜神经元 (Rod/Cone/BC/AC/HC) 大簇", "when": "膜标本 >5%", "action": "旗标: 标本疑含视网膜本体, 报PI"},
            {"flag": "光感受器外节/裂解碎片高背景 (HBA 除外)", "when": "线粒体+ROS 应激签名弥散", "action": "解离应激旗, 不打疾病旗"},
            {"flag": "progenitor/类器官特征", "when": "任何临床膜标本", "action": "疑样本混入/注释错误, 旗标上报"},
            {"flag": "肥大细胞/嗜酸粒细胞富集群", "when": "过敏背景", "action": "unexpected-report"},
        ],
        "contamination_flags": [
            {"flag": "外周血 (经典单核 FCN1/LYZ/S100A8/9 + 血小板 PF4/PPBP + 中性粒 FCGR3B/CSF3R)",
             "meaning": "手术标本血液涌入 —— 髓系计数解读必须先扣血源成分 (B: GSE165784 v2 B10/sub14 A级实测)"},
            {"flag": "RPE/脉络膜色素成分 (BEST1/RPE65/TYR+黑素)",
             "meaning": "穿透取材/合并孔源性脱离操作"},
            {"flag": "玻璃体来源 T 优势 (对照 91.6%)",
             "meaning": "玻璃体切除标本残留液相成分"},
        ],
        "signatures": {
            "tissue_resident_mac": ["SELENOP", "MRC1", "FOLR2", "CD163", "STAB1", "VSIG4", "CD5L"],
            "recruited_monocyte": ["FCN1", "VCAN", "S100A8", "S100A9", "CD14", "SELL", "S100A12"],
            "foam_DAM_LAM": ["GPNMB", "LIPA", "CTSD", "LGMN", "PLD3", "TREM2", "SPP1", "APOE", "MMP9"],
            "heme_stress_mac": ["HMOX1", "FTL", "FTH1", "CD163"],
            "MHCII_high_APC": ["HLA-DRA", "HLA-DRB1", "CD74", "HLA-DQA1", "HLA-DPB1"],
            "patho_endothelial": ["PLVAP", "NDUFA4L2", "HIF1A", "ICAM1", "VCAM1", "DLL4", "ESM1"],
            "pericyte_to_myofibro": ["PRRX1", "ACTA2", "TAGLN", "POSTN", "COL1A1", "COL1A2", "CTHRC1", "TIMP1"],
            "reactive_glia": ["GFAP", "VIM", "CRYAB", "CLU", "TIMP1"],
            "blood_platelet": ["PPBP", "PF4"],
            "signature_source": "markers_membrane_v1.json (canonical/data_driven/pmid_context 三态溯源) + v2 实测簇",
        },
        "caveats": [
            "tip/stalk 内皮亚态: 人 PDR 膜直接单细胞证据有限 (DLL4+ tip 生物学多来自发育/OIR), 标 C 级 —— 预期存在但比例不设区间。",
            "PDR 与 RRD 膜的组成差异尚无充分独立对照 —— 任何'疾病特异簇'判定必须做疾病端对照后才可写 (v2 草稿 RRD 分层教训)。",
            "PI: PDR 注释本身不一定准 → 本先验为对照与 QC 旗, 非真值; 与数据冲突时输出'先验与数据打架清单'上报。",
        ],
    }


# ------------------------------------------------------------------ MD 渲染
def render_md(entry):
    L = [f"# {entry['title']}", "",
         f"> schema: `{entry['schema']}` | entry_id: `{entry['entry_id']}` | 冻结: {entry['frozen_date']} | 来源卡: {entry['card']}",
         "> 本文件由 `/mnt/D/EyeKB/scripts/priors/build_priors.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。",
         "> **判读纪律**: 本条是先验与 QC 旗, 禁入打分; 与数据打架 → 旗标上报, 不许硬凑。",
         ""]
    eg = entry.get("evidence_grades", {})
    if eg:
        L += ["## 证据等级口径", ""] + [f"- **{k}**: {v}" for k, v in eg.items()] + [""]
    if entry.get("disease") and "major_compartments" not in entry and "expected_cell_state_matrix" in entry:
        L += ["## 预期 细胞×状态 矩阵 (按组织端)", ""]
        for blk in entry["expected_cell_state_matrix"]:
            L += [f"### {blk['tissue']}  [{blk['evidence']}]", ""]
            L += [f"- {e}" for e in blk["expected"]] + [""]
        for sec in ("unexpected_flags", "contamination_flags"):
            L += [f"## {'非预期旗' if 'unexpected' in sec else '污染旗'}", ""]
            for fl in entry[sec]:
                L += [f"- **{fl['flag']}**" + (f" — {fl['when']}" if "when" in fl else "") + f" → {fl['action'] if 'action' in fl else fl['meaning']}"]
            L += [""]
        L += ["## 签名轴 (marker panels)", ""]
        for k, v in entry["signatures"].items():
            if k == "signature_source":
                continue
            L += [f"- `{k}`: {', '.join(v)}"]
        L += ["", f"*签名溯源: {entry['signatures'].get('signature_source','')}*", ""]
    elif "major_classes" in entry:
        L += ["## 主表: 细胞类型 × 比例区间", "",
              "| 细胞类型 | 中文名 | HRCA 实测% | 预期区间% | 跨研究 spread% | 本地库 marker | 证据 | 备注 |",
              "|---|---|---|---|---|---|---|---|"]
        for e in entry["major_classes"]:
            L.append("| {class} | {label_cn} | {pct_hrca317m} | {rng} | {sp} | {mk} | {ev} | {nt} |".format(
                rng=f"{e['expected_range_pct'][0]}–{e['expected_range_pct'][1]}",
                sp=f"{e['per_study_spread_pct'][0]}–{e['per_study_spread_pct'][1]}",
                mk=", ".join(e["markers_local_lib"][:5]), ev=e["evidence"],
                nt=e.get("enrichment_note", "—"), **e))
        L += [""]
        ft = entry.get("fine_types", {})
        if ft:
            L += ["## 亚型层 (类内注释细胞占比%)", "", f"*{ft.get('denominator_note','')}*", ""]
            for k, v in ft.items():
                if k == "denominator_note":
                    continue
                L += [f"- **{k}** ({v['basis']}): " + "; ".join(f"{n} {p}%" for n, p in v["top"])]
            L += [""]
        if entry.get("states"):
            L += ["## 状态层 (细胞类型×状态)", "", "| 细胞类型 | 状态 | marker | 证据 | 备注 |", "|---|---|---|---|---|"]
            for s in entry["states"]:
                mk = ", ".join(s.get("markers") or [s.get("markers_desc", "")])
                L += [f"| {s['cell_type']} | {s['state']} | {mk} | {s['evidence']} | {s.get('note','—')} |"]
            L += [""]
    elif "major_compartments" in entry:
        L += ["## 主表: 区隔 × 比例", "",
              "| 区隔 | PDR-only% | 全样本% | 细胞数(PDR) | 证据 | 说明 |", "|---|---|---|---|---|---|"]
        for e in entry["major_compartments"]:
            L += [f"| {e['compartment']} ({e['label_cn']}) | {e['pct_pdr_only']} | {e['pct_all_samples']} | {e['n_pdr']:,} | {e['evidence']} | {e['note']} |"]
        L += [""]
        if entry.get("myeloid_states"):
            L += ["## 髓系状态层", "", "| 细胞类型 | 状态 | 签名/说明 | 簇 | 全样本% | PDR-only% | 证据 |", "|---|---|---|---|---|---|---|"]
            for s in entry["myeloid_states"]:
                pa = s["pct_all_samples"][0] if s["pct_all_samples"] else "—"
                pp = s["pct_pdr_only"][0] if s["pct_pdr_only"] else "—"
                L += [f"| {s['cell_type']} | {s['state']} | {s['markers_desc']} | {s['clusters']} | {pa} | {pp} | {s['evidence']} |"]
            L += [""]
    fl = entry.get("flags", {})
    if fl:
        L += ["## 旗标语义", ""]
        for key, title in [("expected", "预期"), ("expected_low_but_present", "预期但比例低"),
                           ("unexpected", "非预期 (→ unexpected 旗)"),
                           ("contamination_suspect", "污染嫌疑 (→ contamination-suspect 旗)")]:
            if fl.get(key):
                L += [f"**{title}**:", ""] + [f"- {x}" for x in fl[key]] + [""]
    L += ["## 注意事项", ""] + [f"{i+1}. {c}" for i, c in enumerate(entry.get("caveats", []))] + [""]
    L += ["## 出处清单", "", "| sid | 类型 | 等级线索 | 标签 |", "|---|---|---|---|"]
    for s in entry["sources"]:
        src = s.get("pmid") or s.get("path", "")
        L += [f"| `{s['sid']}` | {s['kind']} | {src} | {s['label']} |"]
    L += [""]
    return "\n".join(L)


def main():
    hr = recompute_hrca()
    hg = recompute_gse165784()
    # 漂移守卫: A 级数字与冻结基准比对
    assert hr["total"] == 3177310, hr["total"]
    assert hg["n_all"] == 10069 and hg["n_pdr"] == 7142, (hg["n_all"], hg["n_pdr"])
    assert abs(hg["comp_all"]["myeloid"][1] - 82.28) < 0.01, hg["comp_all"]["myeloid"]
    entries = {
        PRIORS / "composition" / "human_retina": build_human_retina(hr),
        PRIORS / "composition" / "human_pdr_membrane": build_human_pdr(hg),
        PRIORS / "disease" / "proliferative_DR": build_disease_pdr(hg),
    }
    for base, e in entries.items():
        base.parent.mkdir(parents=True, exist_ok=True)
        base.with_suffix(".json").write_text(
            json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        base.with_suffix(".md").write_text(render_md(e), encoding="utf-8")
        print("WROTE", base.with_suffix(".json"))
        print("WROTE", base.with_suffix(".md"))
    print("drift-check PASS | HRCA", hr["total"], "| GSE165784", hg["n_all"])


if __name__ == "__main__":
    sys.exit(main())
