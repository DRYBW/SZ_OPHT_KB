#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB KB1v2-W2: 疾病条目薄层 (疾病×组织矩阵 + PDR 膜示例条目 + 概念 ID 映射)

口径 = BRIEF_KB1v2_20260923.md W2 + ASTRA_ANNOTATION_GUIDANCE_v1.md T4/T6:
  - 疾病条目 = 叠加在组织基线之上的薄层 (疾病×组织矩阵); PDR 膜只是第一个示例格子
  - 身份层级 (大类→细类型→可支持最深级) + 多状态轴 (可共存), 禁止把每种类型×状态
    组合变成新类型
  - 每条签名带出处 + 证据条件 (支持哪种论断 × 条件 × 比较对象 × 定位锚点 × 反例)
  - 条目最小可用标准: 无特异证据不单建亚型条目
  - 批量铺宽暂缓 (T6): 先证 D0 有用再扩展; PDR/RRD/ERM 不同格子不合成一个基线

输入 (只读): kb/priors/disease/proliferative_DR.json (旧 KB1 条目, copy 不 move, 保留为 v1 存档)
输出: kb/priors/disease/PDR__fibrovascular_membrane.{json,md}
      kb/priors/disease/_DISEASE_TISSUE_MATRIX.{json,md}
      kb/priors/concepts.tsv
"""
import json
from pathlib import Path

EYEKB = Path("/mnt/D/EyeKB")
DIS_DIR = EYEKB / "kb/priors/disease"
OLD = json.loads((DIS_DIR / "proliferative_DR.json").read_text(encoding="utf-8"))
TODAY = "2026-09-23"
GEN = "build_disease_v2.py (KB1v2 t_16c3e020)"

# ---------------------------------------------------------------- 概念 ID 映射
# (concept_id, 规范名, 中文, 同义词, 原文命名来源, 层级, 备注)
CONCEPTS = [
    ("EYEKBC-0001", "macrophage_tissue_resident", "组织驻留巨噬细胞",
     "resident macrophage; M2-like; homeostatic-like mac",
     "SELENOP+/FOLR2+/MRC1+/CD163+/STAB1+/VSIG4+/CD5L+ (markers_membrane_v1); Hu2022 'microglia-like' 命名",
     "identity_major", "与 EYEKBC-0018 小胶质的来源区分只到转录相似层级 (Astra T4: 转录相似≠发育来源证明)"),
    ("EYEKBC-0002", "macrophage_recruited_monocyte", "招募型经典单核/单核来源巨噬",
     "classical monocyte; monocyte-derived macrophage; peripherally derived mac",
     "FCN1+/VCAN+/S100A8/9+/CD14+/SELL+ (membrane v1); GSE165784 B5/B9",
     "identity_major", "外周血涌入旗的判读必须先于'疾病募集'结论 (混叠: 手术血液污染)"),
    ("EYEKBC-0003", "macrophage_lipid_laden", "泡沫样/DAM-LAM 巨噬 (状态轴)",
     "foamy macrophage; lipid-associated macrophage (LAM); disease-associated macrophage",
     "GPNMB+/LIPA+/CTSD+/LGMN+/PLD3+/TREM2+/SPP1+/APOE+/MMP9+; Hu2022 亚群命名",
     "state_on_macrophage", "状态轴叠加于 0001/0002 之上, 不单立细胞类型 (T4 防膨胀)"),
    ("EYEKBC-0004", "macrophage_heme_stress", "血红素应激巨噬 (状态轴)",
     "erythrophagocytic macro; iron-handling mac",
     "HMOX1+/FTL+/FTH1+ (CD163 共染) ; GSE165784 v2 sub14",
     "state_on_macrophage", "与出血污染旗共线性高 —— 判读顺序: 先技术后状态"),
    ("EYEKBC-0005", "mhcii_high_apc", "MHC-II 高抗原提呈态 (状态轴)",
     "APC-like; migratory dc-like",
     "HLA-DRA/DRB1/CD74/DQA1/DPB1+", "state_on_macrophage_or_dc",
     "DC 身份在膜标本无独立特异证据 → 不单建 DC 条目 (最小可用标准)"),
    ("EYEKBC-0006", "endothelial_cell", "血管内皮细胞",
     "EC; vascular endothelium", "PECAM1/CDH5/VWF+", "identity_major", ""),
    ("EYEKBC-0007", "endothelial_pathological", "病理态内皮 (状态轴)",
     "tip-like EC; activated EC; hypoxic EC",
     "PLVAP+/NDUFA4L2+/HIF1A+/ICAM1+/VCAM1+/ESM1+; DLL4+ tip 亚态", "state_on_endothelial",
     "tip/stalk 亚态 = C 级外推 (发育/OIR 模型证据), 不设比例预期 (Astra T4 状态≠类型)"),
    ("EYEKBC-0008", "pericyte", "周细胞", "pericyte; mural cell",
     "RGS5/NOTCH3/PDGFRB+", "identity_major", ""),
    ("EYEKBC-0009", "myofibroblast_transition", "周细胞→肌成纤维转变 (连续轴)",
     "myofibroblast; activated pericyte; PRRX1+ stromal",
     "PRRX1+/ACTA2+/TAGLN+/POSTN+/CTHRC1+ (PRRX1-IOVS2025); SOX15+ stromal (JTM2026)",
     "state_axis_continuous", "连续状态不强制二分阳性/阴性 (T4); 与 0010 纤维母细胞边界常未解析 → 允许报告连续/未解析群体 (T1 三分处置)"),
    ("EYEKBC-0010", "fibroblast_membrane_stroma", "膜纤维母/间质细胞",
     "fibroblast; stromal cell; COL1A1-high cell",
     "COL1A1/COL3A1/FN1+", "identity_major", ""),
    ("EYEKBC-0011", "muller_glia_reactive", "反应性 Müller 胶质 (状态轴)",
     "reactive gliosis; gliotic scar",
     "GFAP+/CRYAB+/CLU+/VIM+/TIMP1+ (GLIA_RDG/MULLER_REDD1 背景)", "state_on_muller_glia",
     "膜标本内出现胶质成分 = glial scar 成分预期 (Hu2022); 与视网膜标本 MG 的身份同源"),
    ("EYEKBC-0012", "microglia_homeostatic", "稳态小胶质 (视网膜本体)",
     "homeostatic microglia", "P2RY12+/TMEM119+/CX3CR1+/SALL1+", "identity_major",
     "正常视网膜 0.14% (D001 供者级中位); 膜标本中'小胶质来源'判定封顶 = 转录相似 (T4)"),
    ("EYEKBC-0013", "t_cell_activated", "活化 T 细胞 (状态轴)",
     "CD69+ T", "CD3D/E+/CD69+", "state_on_t_cell", "玻璃体标本 T 绝对优势 (B: 39220810)"),
    ("EYEKBC-0014", "platelet_signal", "血小板信号 (污染/混入旗)",
     "platelet; megakaryocyte transcript reads", "PPBP+/PF4+", "contamination_flag", ""),
    ("EYEKBC-0015", "neutrophil_signal", "中性粒细胞信号 (污染旗为主)",
     "PMN; granulocyte", "FCGR3B+/CSF3R+/ELANE+", "contamination_flag",
     "PDR 膜内 'neutrophil extracellular trap' 类疾病声明证据弱 → 默认按血污旗处置, 除有独立证据"),
    ("EYEKBC-0016", "erythrocyte_signal", "红细胞信号 (污染旗)", "RBC contamination", "HBA1/2+/HBB+", "contamination_flag", ""),
    ("EYEKBC-0017", "rpe_contamination", "RPE/色素上皮混入 (污染旗)", "pigment contamination",
     "BEST1+/RPE65+/TYR+/MLANA+", "contamination_flag", "穿透取材/合并孔源性脱离操作相关"),
]

# 签名 → Astra T4 证据条件 (支持论断类型/关系/条件/比较对象/定位锚点/反例限制)
def sig_evidence():
    base = {
        "tissue_resident_mac": dict(claim_type="identity", relation="支持",
            condition="human, fibrovascular membrane, scRNA", comparator="vs 招募单核 (FCN1 组)",
            locator="Hu2022 (PMID 35061025) 结果节; markers_membrane_v1 canonical 层",
            limits="与稳态小胶质区分不足 —— SELENOP/FOLR2 亦见于血管周围巨噬; 来源断言封顶转录相似"),
        "recruited_monocyte": dict(claim_type="identity+contamination", relation="限定",
            condition="同上", comparator="vs 组织驻留",
            locator="markers_membrane_v1; GSE165784 v2 B5/B9 实测",
            limits="FCN1/LYZ 高表达与手术血液污染混叠 —— 单签名不可判'疾病募集', 必须配血污旗核查"),
        "foam_DAM_LAM": dict(claim_type="state", relation="支持",
            condition="human PDR membrane; 亦见于动脉粥样硬化 LAM (跨病)", comparator="vs 稳态巨噬",
            locator="Hu2022 GPNMB+ 亚群节", limits="LAM 签名非 PDR 特异; '泡沫样'形态学佐证需 OCT/组织学"),
        "heme_stress_mac": dict(claim_type="state", relation="限定",
            condition="PDR 膜 (出血背景)", comparator="vs 非应激巨噬",
            locator="GSE165784 v2 sub14 (A 级实测)", limits="HMOX1/FTL 亦被解离应激与血液存在驱动 —— 先排技术"),
        "MHCII_high_APC": dict(claim_type="state", relation="支持",
            condition="human PDR membrane", comparator="vs MHCII-low mac",
            locator="JCI Insight 2023 (PMID 37917183) APC 亚群", limits="HLA-DR 高≠树突状细胞身份; 单基因 CD74 受双细胞影响"),
        "patho_endothelial": dict(claim_type="state", relation="支持",
            condition="human PDR membrane + 模型", comparator="vs 静止内皮",
            locator="PLVAP/NDUFA4L2 低氧-血管通透性轴 (多文献)", limits="DLL4 tip 亚态人膜直接证据不足 (C 级, 发育外推)"),
        "pericyte_to_myofibro": dict(claim_type="identity+mechanism", relation="支持",
            condition="视网膜纤维化病理 (含 PDR 膜)", comparator="vs 静止周细胞/静止纤维母",
            locator="PMID 41230906 (PRRX1-IOVS2025) 主图", limits="连续转变谱 —— 强制二分会制造假亚型 (T4); '周细胞来源'与'纤维母来源'肌成纤维的区分需要谱系追踪, 转录混合不可判"),
        "reactive_glia": dict(claim_type="state", relation="限定",
            condition="human retina/degeneration contexts", comparator="vs 稳态 MG/Astro",
            locator="PMID 32069977 + 35167652", limits="GFAP 上调非特异 (创伤/应激/发育皆有); 膜标本胶质成分与 glial scar 预期一致"),
        "blood_platelet": dict(claim_type="technical_artifact", relation="支持",
            condition="任何手术材料", comparator="—",
            locator="markers_membrane_v1 血污面板", limits="血小板转录reads 可来自 megakaryocyte 污染或 aggregates —— 只作旗不作群体"),
    }
    return base


# ---------------------------------------------------------------- PDR 膜示例条目
def build_pdr_entry():
    e = {
        "schema": "eyekb-disease/1.1",
        "entry_id": "PDR__fibrovascular_membrane",
        "title": "疾病条目 (示例格): PDR 增殖期 × 纤维血管膜 (人)",
        "disease": "proliferative diabetic retinopathy (PDR), 增殖期",
        "tissue": "fibrovascular membrane",
        "tissue_scope": ["fibrovascular_membrane"],
        "species": "human",
        "organism_stage": "adult",
        "development_stage": "adult",  # KB3 (t_5425a7ca) W2: 条目头显式发育档
        "kb3_card": "t_5425a7ca",
        "stage_note": ("KB2c 发育轴 (裁定 Q3): 疾病格键含发育轴 —— 本格=adult (增殖期 PDR 均为成人"
                       "手术材料; GSE165784/JCI 队列供者皆成人)。发育期样本不进成人疾病格 (PI 指令条款2);"
                       "若未来收 pediatric 膜材料, 单立格不并入本条。"),
        "frozen_date": TODAY, "card": "t_16c3e020", "supersedes": "proliferative_DR (t_39182aa2, v1 存档)",
        "role": "矩阵示例格 = '一个格子'而非项目中心 (PI 2026-09-23 眼科通用口径)",
        "matrix_anchor": "_DISEASE_TISSUE_MATRIX.md",
        "context": {
            "取样材料": "玻璃体切除联合膜剥离术所取纤维血管膜 (可含内界膜/前黄斑膜; "
                       "GSE165784 样本名 PDR-ERM 与 PDR-FM 即同材料两类手术叫法, 均属膜)。",
            "疾病阶段": "增殖期 (新生血管/纤维化期); 非 NPDR/DME 阶段",
            "治疗背景": "既往激光/抗 VEGF 状态在源数据未系统记录 —— 标未记录",
            "方法口径": "scRNA-seq 细胞悬液 (非核); 与 D001 retina 核悬液、D002 眼表细胞悬液口径均不同",
        },
        "usage_scope": ("本条目 = 上下文一致性核查材料 (非白名单): 只产生 expected/unexpected/污染旗, "
                        "禁入打分; 标签不得被强制改成清单内身份 (Astra T2)。"),
        "sampling_mismatch_warning": {
            "statement": ("**取样材料错配警示 (Astra T2 裁定核心)**: 本病发生部位=视网膜, 但手术材料=纤维血管膜。"
                          "健康视网膜组成基线 (kb/baselines/retina, D001) 对本膜标本【不可】作组成达标线 —— "
                          "膜以巨噬/血管/间质为主, 光感受器等神经视网膜类近零是材料性质而非异常。"),
            "correct_uses_of_retina_baseline": ["身份参考 (某髓系簇与视网膜驻留小胶质转录相似度的层级判断)",
                                               "邻近视网膜标本 (retina_adjacent 格) 的背景对照"],
            "wrong_uses": ["膜标本的细胞比例'达标'验收", "把 Rod/Cone 缺失判为质量缺陷 (先查材料!)"],
            "comparable_material_anchor": ("本卡可比材料主锚 = GSE165784 (PDR 膜, PMID 35061025) + JCI Insight 2023 "
                                           "独立 PDR 膜队列 (PMID 37917183) —— 同物种/同材料/同阶段, Astra T2 优先序第 1 档。"),
        },
        # ---- Astra T4 骨架: 身份层级 + 状态轴 (不合成新类型)
        "identity_hierarchies": [
            {"concept_id": "EYEKBC-0001", "canonical": "macrophage_tissue_resident",
             "supportable_level": "major→subcluster", "note": "驻留/招募来源判定封顶=转录相似"},
            {"concept_id": "EYEKBC-0002", "canonical": "macrophage_recruited_monocyte",
             "supportable_level": "major", "note": "与血污混叠, 需先排技术"},
            {"concept_id": "EYEKBC-0006", "canonical": "endothelial_cell",
             "supportable_level": "major→pathologic state", "note": ""},
            {"concept_id": "EYEKBC-0008", "canonical": "pericyte", "supportable_level": "major", "note": ""},
            {"concept_id": "EYEKBC-0010", "canonical": "fibroblast_membrane_stroma",
             "supportable_level": "major", "note": "与 0009 转变轴连续, 边界可未解析"},
            {"concept_id": "EYEKBC-0011", "canonical": "muller_glia (reactive)",
             "supportable_level": "major+state", "note": "glial scar 成分"},
            {"concept_id": "EYEKBC-0013", "canonical": "t_cell", "supportable_level": "major", "note": "低比例"},
        ],
        "state_axes": [
            {"axis": "proliferation (MKI67+)", "applies_to": ["endothelial", "stromal", "microglia(报告为例外,B级)"],
             "binary_forced": False, "note": "细胞周期信号≠血管新生结论 (T7 第四步: 需身份+增殖+空间三层证据)"},
            {"axis": "hypoxia/patho-activation (HIF1A/PLVAP/NDUFA4L2)", "applies_to": ["endothelial"]},
            {"axis": "ECM remodeling / PMT transition (PRRX1/ACTA2/POSTN/CTHRC1)",
             "applies_to": ["pericyte", "stromal"], "continuous": True},
            {"axis": "lipid_laden/foam (GPNMB/TREM2/SPP1)", "applies_to": ["macrophage"]},
            {"axis": "heme_stress (HMOX1/FTL)", "applies_to": ["macrophage"], "tech_confound": "出血+解离"},
            {"axis": "MHC-II antigen presentation", "applies_to": ["macrophage"]},
            {"axis": "reactive gliosis (GFAP/CRYAB/CLU)", "applies_to": ["muller_glia", "astrocyte"]},
        ],
        "expected_cell_state_matrix": OLD["expected_cell_state_matrix"][:1] + [
            {"tissue": "__cross_material_note__(非本格条目)",
             "expected": ["vitreous 格参考: T 细胞绝对优势 91.6% (B: VITREOUS_T) —— 属 PDR__vitreous 格子, "
                          "未达独立条目门槛前只作材料对照",
                          "retina_adjacent 格参考: 早中期 DR 小胶质状态改变无大规模髓系涌入 (B: MG_EARLY_DR/DR_RETINA_SC); "
                          "Müller 反应性 (B: MULLER_REDD1) —— 属 PDR__retina_adjacent 格子"],
             "evidence": "B", "source_ids": ["VITREOUS_T", "MG_EARLY_DR", "DR_RETINA_SC", "MULLER_REDD1"]}],
        "signatures": OLD["signatures"],
        "signature_evidence_T4": sig_evidence(),
        "unexpected_flags": [
            {**f, "disposition_queue_v2": "candidate_biology"} for f in OLD["unexpected_flags"]
        ] + [
            {"flag": "基线/文献清单外身份 (如意外的淋巴/髓外类群)",
             "when": "任何簇无法归入已解析概念", "action": "unexpected-report",
             "disposition_queue_v2": "out_of_baseline_coverage",
             "note": "清单外身份只触发旗, 不得被强制改成清单内身份 (T2)"}],
        "unexpected_disposition_queues": {
            "out_of_baseline_coverage": "超出基线覆盖范围 → 记录并评估是否扩基线 (回填 W1 映射)",
            "conflicts_with_literature": "与现有资料冲突 → 逐条引用核验 + 打架清单上报 PI",
            "technical_suspect": "技术可疑 (双细胞/ambient/应激) → 进 T1 技术可信度门复核队列",
            "candidate_biology": "候选生物学现象 → 走 T3 处置链 (确认观测→排技术→身份状态→临床上下文→独立验证)",
        },
        "contamination_flags": OLD["contamination_flags"],
        "minimum_usability_criteria": {
            "statement": ("条目最小可用标准 (Astra T4/P4): ①至少一条与该材料直接可比的身份或状态证据 (物种+材料+疾病"
                          "条件写明) ②每条签名带出处+证据条件 ③无特异证据不单建亚型格子 ④名称合并只按表达程序/谱系/"
                          "上下文, 不按文字相似度 (概念 ID 映射表) ⑤区间无法估计=合法状态, 不阻断条目成立。"),
            "gate_for_new_cell": "新格子开建 = 有该 疾病×材料 的直接证据集; 批量铺宽暂缓 (T6), 等 PRIOR_DIFF 对照证明 D0 有用",
        },
        "caveats": OLD["caveats"] + [
            "v1.1 (本条): 按 T4 重排为 身份层级+状态轴 两级; 旧 proliferative_DR.json 保留为 v1 存档 (copy 不 move)。",
            "概念 ID 映射 = 起步版 (17 概念), 不同文章命名不自动合并 —— 合并判据=表达程序/谱系/上下文 (T4)。",
        ],
        "sources": OLD["sources"],
        "concept_refs": [c[0] for c in CONCEPTS],
    }
    return e


MATRIX_ROWS = [
    # (disease, tissue/material, status, note)
    ("PDR", "fibrovascular_membrane", "FILLED (示例格)", "PDR__fibrovascular_membrane.md"),
    ("PDR", "vitreous", "placeholder", "定性锚已有 (B: PMID 39220810, T 91.6%); 未达最小可用标准的独立条目门槛 — 暂记于示例格 cross_material_note"),
    ("PDR", "retina_adjacent", "placeholder", "B 级文献锚 (MG_EARLY_DR/DR_RETINA_SC/MULLER_REDD1)"),
    ("NPDR/DME", "retina", "placeholder", "与 PDR 不同阶段不同材料, 不得并入 (T6: 不合成一个组成基线)"),
    ("nAMD/GA", "RPE_choroid", "placeholder", "组织基线侧 RPE/choroid 现为骨架 → 先回填 W1 骨架再谈疾病格"),
    ("RRD", "subretinal/ERM membrane", "placeholder", "GSE165784 RRD-ERM n=1 —— 单样本只可报告'该样本中观察到', 不建普遍条目 (T3)"),
    ("ERM (特发性)", "membrane", "placeholder", "与 PDR 膜同材料不同病 —— 复用概念 ID, 另立格子"),
    ("glaucoma", "optic_nerve_RGC", "placeholder", "组织侧 optic_nerve 骨架已回填映射 (HRA006282 本地可算)"),
    ("keratoconus", "cornea", "placeholder", "组织侧 ocular_surface 基线已 filled → 该格证据门槛最低"),
    ("Fuchs/内皮失代偿", "corneal_endothelium", "placeholder", "D002 内皮层仅 404 细胞, 基线侧先扩"),
    ("uveitis (中间型)", "vitreous", "placeholder", "与 PDR__vitreous 共享材料概念"),
    ("cataract", "lens", "placeholder", "组织侧 lens 骨架=LEC 域裁定"),
]


def render_pdr_md(e):
    L = [f"# {e['title']}", "",
         f"> schema: `{e['schema']}` | entry_id: `{e['entry_id']}` | 冻结: {e['frozen_date']} "
         f"| 卡片: {e['card']} | supersedes: {e['supersedes']} | 发育档: **organism_stage={e.get('organism_stage','—')}"
         + (f" | development_stage={e['development_stage']}** (KB3 显式)" if e.get("development_stage") else "**"),
         f"> 由 `/mnt/D/EyeKB/scripts/disease/{GEN.split()[0]}` 生成; 手改 MD 会被覆盖。", "",
         f"> **发育轴**: {e.get('stage_note','')}", "",
         f"**{e['usage_scope']}**", "",
         "## 疾病×组织矩阵定位", "",
         f"本条目是矩阵的**第一个示例格子** ({e['role']})。矩阵总览: `_DISEASE_TISSUE_MATRIX.md`。", "",
         "## 上下文 (T4)", ""]
    for k, v in e["context"].items():
        L.append(f"- **{k}**: {v}")
    L += ["", "## 取样材料错配警示 (必读)", "", e["sampling_mismatch_warning"]["statement"], ""]
    L.append("**正确用法**: " + "; ".join(e["sampling_mismatch_warning"]["correct_uses_of_retina_baseline"]))
    L.append("")
    L.append("**错误用法**: " + "; ".join(e["sampling_mismatch_warning"]["wrong_uses"]))
    L.append("")
    L.append("**可比材料主锚**: " + e["sampling_mismatch_warning"]["comparable_material_anchor"])
    L += ["", "## 身份层级 (T4: 分层身份, 每层标可支持最深级)", "",
          "| 概念ID | 规范身份 | 可支持层级 | 备注 |", "|---|---|---|---|"]
    for h in e["identity_hierarchies"]:
        L.append(f"| {h['concept_id']} | {h['canonical']} | {h['supportable_level']} | {h['note']} |")
    L += ["", "## 状态轴 (可共存; 连续态不强制二分)", ""]
    for s in e["state_axes"]:
        extra = " [连续轴]" if s.get("continuous") else ""
        L.append(f"- **{s['axis']}** → 适用于 {', '.join(s['applies_to'])}{extra}"
                 + (f"; ⚠ {s['note']}" if s.get("note") else "")
                 + (f"; 技术混叠: {s['tech_confound']}" if s.get("tech_confound") else ""))
    L += ["", "## 预期矩阵 (本格)", ""]
    m = e["expected_cell_state_matrix"][0]
    for x in m["expected"]:
        L.append(f"- {x}")
    L.append(f"- 证据 {m['evidence']} | 出处: {', '.join(m['source_ids'])}")
    L += ["", "## 跨材料对照注记 (非本格内容, 未建条目)  ", ""]
    for x in e["expected_cell_state_matrix"][1]["expected"]:
        L.append(f"- {x}")
    L += ["", "## 签名 × 证据条件 (T4: 不止 PMID —— 论断类型/条件/比较对象/定位锚点/反例限制)", "",
          "| 签名 | marker | 论断类型 | 关系 | 条件 | 比较对象 | 定位锚点 | 反例/限制 |",
          "|---|---|---|---|---|---|---|---|"]
    for name, cond in e["signature_evidence_T4"].items():
        mk = ", ".join(e["signatures"].get(name, []))
        L.append(f"| {name} | {mk} | {cond['claim_type']} | {cond['relation']} | {cond['condition']} "
                 f"| {cond['comparator']} | {cond['locator']} | {cond['limits']} |")
    L += ["", "## 非预期旗 (含四分处置队列)", "",
          "| 旗 | 触发条件 | 处置 | 队列 |", "|---|---|---|---|"]
    for f in e["unexpected_flags"]:
        L.append(f"| {f['flag']} | {f['when']} | {f['action']} | {f['disposition_queue_v2']} |")
    L += ["", "**队列语义**: ", ""]
    for k, v in e["unexpected_disposition_queues"].items():
        L.append(f"- `{k}`: {v}")
    L += ["", "## 污染旗", ""]
    for f in e["contamination_flags"]:
        L.append(f"- **{f['flag']}** → {f['meaning']}")
    L += ["", "## 条目最小可用标准", "",
          e["minimum_usability_criteria"]["statement"], "",
          "开新格门槛: " + e["minimum_usability_criteria"]["gate_for_new_cell"], "",
          "## 注意事项", ""]
    for i, c in enumerate(e["caveats"], 1):
        L.append(f"{i}. {c}")
    L += ["", "## 出处清单", "", "| sid | 类型 | 标签 |", "|---|---|---|"]
    for s in e["sources"]:
        L.append(f"| `{s['sid']}` | {s.get('kind','')} | {s.get('label','')} |")
    L.append("")
    return "\n".join(L)


def render_matrix_md():
    L = ["# 疾病 × 组织/材料 × 发育档 矩阵 (薄层架构总览)", "",
         f"> schema: eyekb-disease-matrix/1.1 | 生成: {TODAY} | 卡片: t_be336eee | 生成器: {GEN}",
         "> 眼科通用架构 (PI 2026-09-23): 疾病条目=叠加在组织基线 (kb/baselines/) 之上的薄层; "
         "**批量铺宽暂缓** (Astra T6) —— 先以 PDR 膜一个格子验证判读收益 (PRIOR_DIFF), 再按样本入口增量扩展。",
         "> **KB2c 发育轴 (裁定 Q3)**: 格子键=(disease, material, organism_stage) 三键; 现网全部格=adult; "
         "发育期/胎儿样本不进成人疾病格 (PI 指令: '即使是一个组织也不对的')。", "",
         "| 疾病 | 组织/材料格 | 发育档 | development_axis (KB3) | 状态 | 说明 |", "|---|---|---|---|---|---|"]
    for d, t, st, n in MATRIX_ROWS:
        L.append(f"| {d} | {t} | adult | adult | **{st}** | {n} |")
    L += ["", "## KB3 发育轴预留格 (t_5425a7ca — 只立格不填内容)", "",
          "| 疾病 | 材料格 | development_axis | 状态 |",
          "|---|---|---|---|",
          "| ROP (早产儿视网膜病变) | developing_retina_vascular | **fetal_neonatal** | "
          "RESERVED —— 发育轴侧血管增殖病, 与 PDR 成人格永不并池/互参照; 填格前提=发育期数据/文献锚+过裁定 |",
          "",
          "> 架构规则 6 的占位实现: 成人格数组 rows=12 不动 (回归锁), 预留格走独立键 "
          "development_axis_reservations (双锁)。", ""]
    L += ["", "## 架构规则", "",
          "1. 组织基线与疾病条目解耦: 疾病格不重复组织比例, 只写 疾病×材料 的预期/旗标/签名 (身份+状态两级)。",
          "2. 同一疾病不同材料=不同格 (PDR 膜 ≠ PDR 玻璃体 ≠ 邻近视网膜; Astra T2 取样材料锚定)。",
          "3. 同一材料不同病不合并 (PDR 膜与特发 ERM 膜复用概念 ID 但分格; T6)。",
          "4. 开格门槛=条目最小可用标准 (见示例格), 无特异证据不单建亚型格 (T4/P4)。",
          "5. 每格链接: 组织基线文件 ↔ RAG reason-tag (evidence_meta sidecar) ↔ 文献索引页 ↔ 概念表 (W5 四向链接)。",
          "6. **发育轴单列 (KB2c)**: 格子键含 organism_stage; 成人疾病格只收 adult 材料, "
          "发育期疾病样本 (如 pediatric ROP 膜) 单立新格, 禁并入成人格 (PI 红线)。", ""]
    return "\n".join(L)


def main():
    DIS_DIR.mkdir(parents=True, exist_ok=True)
    e = build_pdr_entry()
    (DIS_DIR / "PDR__fibrovascular_membrane.json").write_text(
        json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIS_DIR / "PDR__fibrovascular_membrane.md").write_text(render_pdr_md(e), encoding="utf-8")
    mx = {"schema": "eyekb-disease-matrix/1.1", "generated": TODAY, "generator": GEN,
          "card": "t_be336eee",
          "stage_axis_note": ("KB2c 裁定 Q3: 格子键=(disease, material, organism_stage) 三键。"
                              "现网全部格=adult (疾病手术材料皆成人); 发育期/胎儿样本不进成人疾病格 "
                              "(PI 指令条款2: '即使是一个组织也不对的')。"),
          "rows": [{"disease": d, "material": t, "status": s, "note": n,
                    "organism_stage": "adult", "development_axis": "adult"}
                   for d, t, s, n in MATRIX_ROWS],
          # ---- KB3 (t_5425a7ca): 发育轴显式列 + 预留格 (rows==12 回归锁不动) ----
          "kb3_note": ("KB3 (t_5425a7ca): 发育轴升为矩阵显式列 development_axis; 现网 12 格全 adult (写死); "
                       "发育轴侧疾病格走 development_axis_reservations 占位 (防与成人格混池, 回归双锁)。"),
          "kb3_card": "t_5425a7ca",
          "development_axis_reservations": [{
              "disease": "ROP", "material": "developing_retina_vascular",
              "development_axis": "fetal_neonatal", "organism_stage": "developing",
              "status": "RESERVED (只立格不填内容)",
              "note": ("早产儿视网膜病变 = 发育轴侧血管增殖病 (PI 红线配套格): 与 PDR 成人膜格严格分离, "
                       "永不并格、永不互为参照 (胎儿/早产儿的这些和成人的即使是一个组织也不对的)。"
                       "填格前提 = 拿到发育期材料/文献锚 (如 ROP 视网膜类器官方或尸材料单细胞——均先过"
                       "发育轴单列纪律); 填格动作须过裁定并同步改回归双锁 (rows/reservations)。"),
              "reserved_by": {"card": "t_5425a7ca", "date": "2026-09-24"}}]}
    (DIS_DIR / "_DISEASE_TISSUE_MATRIX.json").write_text(
        json.dumps(mx, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIS_DIR / "_DISEASE_TISSUE_MATRIX.md").write_text(render_matrix_md(), encoding="utf-8")
    ct = Path("/mnt/D/EyeKB/kb/priors/concepts.tsv")
    with open(ct, "w", encoding="utf-8") as f:
        f.write("concept_id\tcanonical_name\tname_cn\tsynonyms\tsource_namings\tlevel\tnotes\n")
        for row in CONCEPTS:
            f.write("\t".join(row) + "\n")
    print("W2 written:", DIS_DIR / "PDR__fibrovascular_membrane.md", "|", ct)


if __name__ == "__main__":
    main()
