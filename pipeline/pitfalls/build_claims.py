#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_claims.py — 六格 B1 → 原子 claim 契约（WIRE-P1 交付2 · REV-1/astra 定盘版）。

单一事实源：本脚本 = claim 逐条裁决表 + 派生规则的唯一落盘处（pages/ 与 MANIFEST
均为机器产物，不手改；改裁决改本表重跑）。六格原稿 /mnt/D/EyeKB/kb/known_issues/
只读不动。取代 attempt-1 的 build_pitfalls.py（旧 qwen 契约作废，见卡内 REV-1 更正令）。

契约（astra T1 原子 claim schema + T3 全枚举 + T6 可见性字段）：
  claim_id / scope{species,tissue,assay,preparation,disease_or_treatment}
  failure_mode / observable_signature / risk_level
  mitigation / evidence_source_type / source_check
  home{kind: species|tissue|cell|pattern|unmapped, id}
  visibility / blind_safe / answer_dependency
  status / owner / last_reviewed / links / provenance

入账规则（REV-1 更正令③）：
  - 一 scope 一 claim；跨部分组织非全覆/由 assay·疾病·制备条件决定 → PATTERN。
  - 盲区声明（6 条）与"社区空白"记录（3 条）= 无量纲无失效签名 → **不入账**，
    登记 pages/EXCLUSIONS.json（可追溯）。
  - 映射不进受控词表（COORDINATE_TAXONOMY_v0.md）→ UNMAPPED_SCOPE，禁自动注入。
  - 禁裸 A/B/C：来源类型全枚举 internal_observation|peer_reviewed_literature|
    community_lead；核验状态另立 source_check（题录/指针核过 ≠ claim 成立）。

派生规则（机械，不再手拍）：
  answer_dependency=none      → blind_safe=true,  visibility=pre_annotation
  answer_dependency=sample/dataset_specific → blind_safe=false, visibility=post_decision
  source_check：internal_observation → 文件指针存在性实测（locator_verified/unchecked）
                peer_reviewed_literature → locator_verified（B1 构建时 eutils 题录核验，留痕登记）
                community_lead → unchecked（URL 存在≠claim 成立，astra T2 原文）

用法：
  python build_claims.py            # 重建 pages/ + MANIFEST
  python build_claims.py --check    # 脚本↔产物一致性门（含链接 100% 解析）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/D/EyeKB/kb/known_issues")
PAGES = HERE / "pages"

# 六格坐标系 → canonical 组织 id（COORDINATE_TAXONOMY_v0.md §6；仅 pdr 改名，余直通）
TISSUE_CANON = {"retina": "retina", "pdr_membrane": "fibrovascular_membrane",
                "trabecular_meshwork": "trabecular_meshwork", "cornea": "cornea",
                "vitreous": "vitreous"}
CELLS = ["human__retina", "human__pdr_membrane", "mouse__retina",
         "human__trabecular_meshwork", "human__cornea", "human__vitreous"]
CANON_TISSUES = ["retina", "RPE", "ciliary_body", "optic_nerve", "ocular_surface",
                 "trabecular_meshwork", "lacrimal_gland", "choroid", "conjunctiva",
                 "iris", "lens", "sclera", "cornea", "fibrovascular_membrane", "vitreous"]
SPECIES_PAGE = ["human", "mouse"]
ASSAY_VOCAB = ["scRNA", "snRNA", "spatial"]          # bulk 缺失登记在词表，禁私加
EST_BY_GRADE = {"A库内实证": "internal_observation",
                "B文献PMID": "peer_reviewed_literature",
                "C社区经验": "community_lead"}
HIST_GRADE = {"internal_observation": "PIT-E1", "peer_reviewed_literature": "PIT-E2",
              "community_lead": "PIT-E3"}            # legend 用（禁裸字母）

# ---------------------------------------------------------------- 逐条裁决表
# key=(cell, b1序)。home=("cell",) 默认本格；("species",sp)/("pattern",pid)/("unmapped",None)
# ad: none|sample_specific|dataset_specific；risk: high|medium|low
# fm/obs: 失效模式/可观测签名；sc_ex: scope 例外轴；why: 归属理由；note: 备注
V = {}

def v(cell, i, home, ad, risk, fm, obs, why, sc_ex=None, note=""):
    V[(cell, i)] = dict(home=home, ad=ad, risk=risk, fm=fm, obs=obs,
                        why=why, sc=sc_ex or {}, note=note)

# ---- human__retina (14 条 → 12 claim + 1 exclusion(声明) + #11 merge-note→ 见 EXCL)
HR = "human__retina"
v(HR, 1, ("cell",), "dataset_specific", "high",
  "参考缺类伪影：10 majorclass 词表无独立内皮类，血管簇被引擎硬分给小胶质并呈高置信假象",
  "dr-sc 簇31：引擎臂 Micro share 83.4% vs 判读臂 Endo（E-b 在册）",
  "证据仅人×视网膜格内实测（HRCA 词表+本引擎组合），无跨格双证据不升")
v(HR, 2, ("cell",), "sample_specific", "high",
  "降解/低质量视杆簇被劫持为胶质命名或集体弃权（Rod 质量轴）",
  "低深度+高 MT 簇的具名在引擎与判读间系统性漂移",
  "光感受器质量轴为视网膜特有")
v(HR, 3, ("pattern", "dissociation_stress_transcriptome"), "none", "high",
  "解离诱导应激转录组（HSPA1A/FOS/JUN 类）刷屏，劫持证据窗口",
  "簇 top 基因被热休克/IEG 类主导且与解离方案共变",
  "跨物种跨组织的方法学坑：本条缓解自引 B 档人/鼠两系解离对比文献（PMID:32487174）",
  sc_ex={"species": ["*"], "tissue": ["*"], "assay": ["scRNA"]})
v(HR, 4, ("pattern", "macroglia_granularity_wall"), "none", "medium",
  "MG↔Astro 在证据面难分（宏观胶质粒度墙），词典误导判读有前科",
  "宏观胶质两类互标高频出现；DR 反应性胶质化（GFAP↑）场景加剧",
  "墙本身跨组织成立（视网膜/视神经宏观胶质），证据面为人类→pattern 挂双组织",
  sc_ex={"species": ["*"], "tissue": ["retina", "optic_nerve"]})
v(HR, 5, ("cell",), "dataset_specific", "medium",
  "低深度带 ambient 陷阱：真 BC 沾杆 ambient 被误读为『杆幅低→判双极』盲区带",
  "杆主导簇出现具名 BC；不做 ambient 分解时误判证据不可分",
  "现象限视网膜光感受器主导材料；引用自家盲区卡在册证据")
v(HR, 6, ("cell",), "none", "high",
  "本体系训练池 RPE 面板仅 863 细胞，10 类引擎/小面板词条不可产出 RPE 结论",
  "RPE 类 recall 塌陷/高置信错分（外部纯化数据对照下）",
  "系统适用域声明（answer 无关）；证据锚 D001 池规模=格内事实",
  note="升外部数据或独立面板前对本体系 RPE 具名一律人工复核")
v(HR, 7, ("pattern", "platform_nucleus_vs_cell"), "none", "high",
  "snRNA vs scRNA 平台轴组成压谱：核悬液基线套细胞悬液数据产生系统性假旗",
  "跨设计池级组成越界旗高频触发；分层路由后消除",
  "平台轴为物种/组织无关的技术属性（词表 §4 assay 条件驱动）",
  sc_ex={"species": ["*"], "tissue": ["*"], "assay": ["snRNA", "scRNA"]})
v(HR, 8, ("cell",), "sample_specific", "medium",
  "区域混合假旗：中央凹 vs 周边取材差异被当作组成异常",
  "同组织不同区域样本的组成占比呈双峰",
  "fovea/peripheral 为人视网膜解剖特有；取材区域轴未入词表（缺失登记）")
v(HR, 9, ("pattern", "single_donor_leverage"), "none", "medium",
  "供体杠杆：罕见类 hit 可被单 donor 删除即翻转",
  "留一供体复算翻转（LODO flip）",
  "通用统计纪律（出自组成门决策表 D-2 节，文本不限格）",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(HR, 10, ("pattern", "nomenclature_mg_ambiguity"), "none", "high",
  "MG 二义缩写（Müller glia vs microglia）跨体系撞车，裸写在交付件中致命名歧义",
  "同一缩写在不同体系指向不同类（CL 回证：CL:0000636=Müller cell）",
  "文本明示『任何交付件禁用裸 MG』=全局交付纪律",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(HR, 11, ("cell",), "none", "low",
  "解离/储存偏倚有系统评估在案；稀有类回收依赖核悬液——读作生物学差异前须先扣方法学混杂",
  "scRNA/snRNA 稀有类回收率差在文献两系对比中可复现",
  "B 档锚条：为本格 #3/#7 的题录证据，scope 随本格",
  note="peer-reviewed 锚；不自动产生 hard_gate")
v(HR, 12, ("cell",), "none", "low",
  "引用人视网膜组成区间用点值而非 per_study_spread 会夸大确定性",
  "跨研究组成点值互引时区间信息丢失",
  "B 档题录池锚本格；规则限人视网膜组成引用")
v(HR, 13, ("cell",), "none", "low",
  "线上参考映射工具（Azimuth 类）版本漂移破坏可复现性",
  "同数据不同工具版本映射结果不一致",
  "社区操作提示；工具维护为方法学（限 scRNA 映射路径）",
  sc_ex={"assay": ["scRNA"]}, note="community_lead：仅核查要求，不作证据依据")

# ---- human__pdr_membrane (10 条 → 8 claim + 1 absence + 1 declaration)
PM = "human__pdr_membrane"
v(PM, 1, ("cell",), "dataset_specific", "high",
  "髓样占比压谱：膜样本 79.5-85% 髓系，全局聚类下罕见类被压没",
  "全池聚类罕见类占比≈0；compartment 门控亚聚后重现",
  "比例为膜格实测（在册 GSE165784 系）")
v(PM, 2, ("pattern", "surgical_blood_inflow"), "none", "high",
  "手术标本血液涌入：髓系/血小板/中性粒签名混入，不扣血源直接计数=结论污染",
  "血源锚（FCN1/LYZ）与驻留锚（SELENOP/MRC1/FOLR2）双层可分离；PBMC 配对扣比后占比改变",
  "跨组织成立：膜格实测+玻璃体条文本明记『血源扣减法同膜格』两格在册",
  sc_ex={"species": ["human"], "tissue": ["fibrovascular_membrane", "vitreous"]})
v(PM, 3, ("pattern", "disease_material_vs_healthy_baseline"), "none", "high",
  "疾病材料≠健康器官：拿疾病样本对照健康组织组成做『达标线』误读材料类别",
  "疾病材料组成天然偏离健康基线；三用途口径（身份参考/背景对照/QC 旗）外的对照即误用",
  "规则由 Astra T2 固化为膜格口径，但失效模式本身疾病材料通用",
  sc_ex={"species": ["*"], "tissue": ["*"], "disease_or_treatment": ["PDR"]})
v(PM, 4, ("cell",), "sample_specific", "medium",
  "组织驻留巨噬 vs 小胶质在膜内不可分；『microglia 驱动新生血管』主张须先证驻留",
  "谱系锚与状态锚分簇依据缺失时跨样本整合并簇假象",
  "证据膜格实测（B1/B13 在册）")
v(PM, 5, ("cell",), "dataset_specific", "medium",
  "RRD 与 PDR 混样改变比例口径：增殖占比随口径翻转",
  "两套疾病口径的占比表分别计算结果不同；MT 高簇随样本处理差异变化",
  "疾病口径问题限膜格（PDR/RRD 材料）",
  sc_ex={"disease_or_treatment": ["PDR", "RRD"]})
v(PM, 6, ("cell",), "sample_specific", "medium",
  "增殖群（MKI67/TOP2A）跨谱系并簇：细胞周期签名劫持归因",
  "增殖簇内多谱系 marker 共检；并簇上做 DE 结果不可归因",
  "证据=膜格 B11 行；跨谱系并簇疑似通用坑但未到他格证据，不升（hint 已记）")
v(PM, 7, ("pattern", "chamber_material_distinction"), "none", "high",
  "同疾病不同腔室材料组成相反（PDR 玻璃体 T 系 vs 膜髓系），引用互串=结论反转",
  "PDR 玻璃体 T 91.6% vs 膜髓系 79.5% 双实测在册",
  "文本枚举膜/玻璃体/视网膜三格且两格互引 → 跨组织限人",
  sc_ex={"species": ["human"], "tissue": ["fibrovascular_membrane", "vitreous", "retina"]})
v(PM, 8, ("cell",), "none", "low",
  "写 FVM/髓系主张不带文献锚（方法+组成题录池）致出处不可溯",
  "对外主张缺 PMID 锚",
  "B 档题录池锚本格")

# ---- mouse__retina (10 条 → 9 claim + 1 declaration)
MR = "mouse__retina"
v(MR, 1, ("pattern", "cross_species_panel_id_preflight"), "none", "high",
  "跨物种上面板前不验基因 ID 体系 → 特征空间异名，面板命中率归零（0/2000 血案）",
  "panel_present=0；桥=正式 ortholog 表+大小写不敏感匹配后可恢复",
  "血案在鼠格，规则文本全量化（任何物种任何面板）",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(MR, 2, ("pattern", "symbol_case_ortholog_join"), "none", "high",
  "基因大小写惯例（人全大写/鼠首字母大写）撞车致物种旗误判与 join 失败",
  "面板命中率<50% 且生物学解释前，先查大小写/ID 体系即可复位",
  "B5 治理本体跨物种；规则文本全量化",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(MR, 3, ("species", "mouse"), "none", "medium",
  "鼠参考侧 Müller 常记作 Astrocytes（含 SingleR/厂商口径）：跨体系标注漂移",
  "同一簇在厂商口径与本词表间标签类别漂移（Müller↔Astro）",
  "鼠侧通用标注惯例（文本不限组织）→ SPECIES/mouse")
v(MR, 4, ("cell",), "none", "medium",
  "成体鼠 RGC 单细胞捕获率极低（Drop-seq 系原始限制）：RGC≈0 是制备域偏移非生物学",
  "snRNA 对照可回收 RGC；急性解离方案下 RGC 近零",
  "限鼠×视网膜（RGC 捕获为视网膜解离特有），assay=scRNA",
  sc_ex={"assay": ["scRNA"]})
v(MR, 5, ("cell",), "none", "medium",
  "MRCA 系参考为人工富集设计（分选靶标），类占比外推到天然酶消样本必翻车",
  "训练域 BC 46.7% vs 天然构成差量级；同设计层内对照才稳定",
  "参考设计层声明，锚鼠视网膜参考")
v(MR, 6, ("cell",), "none", "high",
  "鼠引擎适用域硬边界：限成人（P28+）视网膜；血管/免疫态与 P<28 出域",
  "出域样本仍被强制具名（域外硬标前科）；过发育轴门后只出旗不改名",
  "自家引擎声明（answer 无关）")
v(MR, 7, ("pattern", "sklearn_proba_column_order"), "none", "medium",
  "sklearn proba 列序按 classes_ 字母序而非自定义类序：猜列=结果全反",
  "对调二分类概率列后判别结果系统性反转",
  "『消费任何 sklearn 概率输出前先 print classes_』全量化；两撞车例在册",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(MR, 8, ("cell",), "none", "low",
  "鼠侧捕获偏倚有方法学文献原点（Drop-seq 系）；需解离不敏感证据时走空间转录组",
  "文献两系对照可复现；空间路线回收解离丢失类",
  "B 档题录池锚本格", sc_ex={"assay": ["scRNA", "spatial"]})
v(MR, 9, ("cell",), "none", "low",
  "社区经验：解离应激与 doublet 工具坑（操作提示级）",
  "（社区帖观察，未本地复算）",
  "C 档内容条；community_lead 仅核查要求", sc_ex={"assay": ["scRNA"]},
  note="community_lead")

# ---- human__trabecular_meshwork (8 条 → 6 claim + 1 absence + 1 declaration)
TM = "human__trabecular_meshwork"
v(TM, 1, ("cell",), "none", "high",
  "词表无 TM 专类（TM 梁/JCT/SC 内皮行缺失）：TM 组织被硬分进 Fibroblast/Ciliary_Muscle/Endothelium",
  "TM 样本 top 候选全落非 TM 词表类；『引擎出域』旗可复现",
  "本体系词表事实，锚 TM 格")
v(TM, 2, ("cell",), "none", "medium",
  "取材边界混入：TM 条带带 uvea/睫状体/角膜缘成分，解剖邻近决定组成",
  "虹膜括约肌/睫状肌签名出现在 TM 样本=取材正常污染",
  "TM 解剖邻近特有", sc_ex={"preparation": ["blunt_strip_TM"]})
v(TM, 3, ("cell",), "none", "medium",
  "核悬液平台丢失 TM 细胞质转录本（收缩装置/ECM 相关基因）",
  "snRNA 读数系统性缺失胞质签名；scRNA 培养对照不同",
  "TM+核悬液组合特有（平台轴通用部分在 platform_nucleus_vs_cell）",
  sc_ex={"assay": ["snRNA"]})
v(TM, 4, ("cell",), "none", "low",
  "零方差行带[0,0]区间工件：邻近极低类占比对照假旗",
  "donor_range 退化为 [0,0] 的基线行触发越界旗",
  "证据锚 TM Pericyte 行；改判据另案待最终决定，不升")
v(TM, 5, ("cell",), "none", "medium",
  "永生化细胞系表型漂移：TM 文献大量用永生化系，与原代表型有公开发表差异",
  "传代代次与供体系差异在文献记录在案",
  "B 档库外先验登记限 TM", sc_ex={"preparation": ["cultured_cell_line"]})
v(TM, 6, ("cell",), "none", "low",
  "人 outflow 专格文献题录池：TM/SC 亚型词表对账与跨物种同源性核查锚",
  "词表无对账基准时跨物种主张不可判",
  "B 档题录池锚本格")

# ---- human__cornea (9 条 → 7 claim + 1 declaration… cornea#8 社区有内容入账)
CO = "human__cornea"
v(CO, 1, ("cell",), "none", "medium",
  "角膜单细胞材料=眼库捐献/移植内皮边缘碎块（尸体材料学），『正常』标签掩盖材料缺陷",
  "死亡至固定时距与材料来源缺失时 unexpected 旗按在册清单命中",
  "角膜材料学特有；报来源+时距为强制缓解")
v(CO, 2, ("cell",), "none", "medium",
  "无血管≠无血管签名：角膜缘/新生血管材料混入产生内皮/周细胞假簇",
  "CDH5/PTPRC 零检出=正常角膜门控；NEA/移植材料出现血管签名",
  "角膜（无血管器官）特有")
v(CO, 3, ("cell",), "dataset_specific", "high",
  "词条反噬：新词条上线点着邻域（Keratocytes 新词曾把 98.7% 纯周细胞簇拉走）",
  "mini 盲验证只证『能救』不证『不点邻居』时，发布后邻域簇标签漂移",
  "发布纪律（邻域火灾审计）属流程层 KB7；证据个案锚角膜格",
  note="审计规则对 curator；失效观察对判读面")
v(CO, 4, ("cell",), "none", "high",
  "取材层位混合：眼表超级类（角膜/角膜缘/巩膜…）混池后层位比例全是假数",
  "whole mount 默认含角膜缘干龛+结膜过渡带；跨区套基线时占比失真",
  "D002 超级类结构事实；锁取材域为强制缓解")
v(CO, 5, ("pattern", "panbright_epithelial_secreted"), "none", "high",
  "上皮/分泌类标志的广谱泛亮：单基因定类被跨谱系泛亮反噬",
  "同簇外类表达率>阈值；core 组合+泛亮预检后可分离",
  "泪腺 LACRT 教训移植眼表=两格在册证据，跨组织限人",
  sc_ex={"species": ["human"], "tissue": ["cornea", "lacrimal_gland"]})
v(CO, 6, ("cell",), "none", "medium",
  "单供体杠杆在眼表更极端：供眼例数天然个位数",
  "n≤4 donor 研究中稀有类 hit 随单 donor 删除翻转",
  "角膜材料结构特有（通用规则在 single_donor_leverage）",
  sc_ex={"preparation": ["paired_donor_tissue"]})
v(CO, 7, ("cell",), "none", "low",
  "角膜/眼表亚型词表须以图谱文献为基准；培养系引用带漂移声明",
  "词表无图谱对账时亚型不可判",
  "B 档题录池锚本格")
v(CO, 8, ("cell",), "none", "low",
  "社区通用 QC/整合层坑可外推眼表，但须注明非角膜实证",
  "（社区观察，本地未复算）",
  "C 档内容条", note="community_lead")

# ---- human__vitreous (8 条 → 6 claim + 1 absence + 1 declaration)
VI = "human__vitreous"
v(VI, 1, ("cell",), "none", "high",
  "玻璃体坑主体在『样本有无与取材污染』不在注释：取材方式/对照/细胞数三问任一答不清即降级",
  "cassette washing vs 膜剥离、有无配对血/对照眼在标本记录中缺失",
  "本格总坑（玻璃体特有）", sc_ex={"preparation": ["vitrectomy_cassette_wash"]})
v(VI, 2, ("cell",), "none", "high",
  "取材污染三源：视网膜撕脱碎片（光感受器/RPE）、膜组织混入、术中出血",
  "光感受器/RPE 签名在玻璃体样本=取材旗非新发现",
  "玻璃体特有；血源扣减指针→surgical_blood_inflow")
v(VI, 3, ("cell",), "none", "high",
  "近无细胞基线：正常玻璃体单细胞参照不存在，疾病对比无锚",
  "公开数据无正常玻璃体组成条（构建时核对在册）",
  "领域空白事实（词表 §3 冲突②组成面 missing 的依据）")
v(VI, 4, ("cell",), "none", "medium",
  "细胞数与测序深度双低：低质量空滴/ambient 在稀细胞材料里占比放大",
  "每样本 nFeature 分布左移+ambient 估计高；非 ambient 门（表达占比×双细胞联合检验）后稀有类存活",
  "玻璃体材料特性（ambient 方法学通用部分在视网膜 ambient 条）")
v(VI, 5, ("pattern", "chamber_material_distinction"), "none", "high",
  "免疫优势群是材料属性非疾病属性：同病不同料（膜髓系 vs 玻璃体 T 系）",
  "患者级 paired 样本可分离腔室效应；类占比平均会掩盖",
  "与膜格同病不同料条共享 pattern（一 scope 一 claim，本条主语=归因方向）",
  sc_ex={"species": ["human"], "tissue": ["fibrovascular_membrane", "vitreous", "retina"]})
v(VI, 6, ("cell",), "none", "low",
  "玻璃体侧文献规程+免疫对照谱为题录池；中性粒两主张并存须带读出方法引用",
  "不同读出方法（流式 vs 单细胞）给出相反中性粒结论",
  "B 档题录池锚本格")

# ---------------------------------------------------------------- 不入账登记
EXCLUDED = {
    (HR, 14): ("declaration_not_claim", "本格盲区声明=检索留痕元信息，无失效模式无签名"),
    (PM, 9): ("absence_note", "社区讨论空白登记（无任何具体失效观察）"),
    (PM, 10): ("declaration_not_claim", "本格盲区声明"),
    (MR, 10): ("declaration_not_claim", "本格盲区声明"),
    (TM, 7): ("absence_note", "社区零命中登记"),
    (TM, 8): ("declaration_not_claim", "本格盲区声明"),
    (CO, 9): ("declaration_not_claim", "本格盲区声明"),
    (VI, 7): ("absence_note", "专贴未检得登记（通用坑外推另有条目）"),
    (VI, 8): ("declaration_not_claim", "本格盲区声明"),
}

# ---------------------------------------------------------------- 装配
def _pointer_exists_in_source(ref):
    m = re.search(r"/mnt/\S+", str(ref))
    return bool(m) and Path(m.group(0)).exists()


# ---- 入仓清洗（红线：自家样本号禁入仓；工作盘原件不回改，仓侧构建产物统一过此层）----
_SCRUB = [
    ("本室 YAS-2 玻璃体液样本", "本室玻璃体液样本"),  # 患者样本号→通用措辞（claim 本体=文献规程，非衍生结果）
]
def _scrub_text(s: str) -> str:
    for a, b in _SCRUB:
        s = s.replace(a, b)
    s = re.sub(r"YAS-\d+", "本室样本", s)      # 兜底：任何 YAS 样本号
    s = re.sub(r"BMR\d+", "本室小鼠数据集", s)  # 兜底：BMR 编号
    return s

def build():
    claims = []
    seq = 0
    for cell in CELLS:
        src = json.load(open(SRC / f"{cell}.json", encoding="utf-8"))
        sp, ti_raw = cell.split("__", 1)
        ti = TISSUE_CANON[ti_raw]
        for i, it in enumerate(src["card"], 1):
            key = (cell, i)
            if key in EXCLUDED:
                continue
            d = V.get(key)
            if d is None:
                raise SystemExit(f"裁决表缺条目 {key}——禁默认归类（astra T4 失败模式预警）")
            seq += 1
            cid = f"KC-B1-{seq:03d}"
            est = EST_BY_GRADE[it["source_grade"]]
            hraw = d["home"]
            hk = hraw[0]
            hi = hraw[1] if len(hraw) > 1 else None
            if hk == "cell":
                hi = f"{sp}__{ti}"
                scope = {"species": [sp], "tissue": [ti]}
            elif hk == "species":
                scope = {"species": [hi], "tissue": ["*"]}
            elif hk == "pattern":
                scope = {"species": ["*"], "tissue": ["*"]}
            else:
                scope = {"species": [], "tissue": []}
            for axis in ("species", "tissue", "assay", "preparation", "disease_or_treatment"):
                if axis in d["sc"]:
                    scope[axis] = d["sc"][axis]
            for axis in ("assay", "preparation", "disease_or_treatment"):
                scope.setdefault(axis, [])
            # 受控词表机械校验（禁自造词）
            for t in scope["tissue"]:
                assert t == "*" or t in CANON_TISSUES, f"{cid}: tissue {t} 不在受控词表"
            for s_ in scope["species"]:
                assert s_ == "*" or s_ in SPECIES_PAGE, f"{cid}: species {s_} 不在受控词表"
            for a in scope["assay"]:
                assert a in ASSAY_VOCAB, f"{cid}: assay {a} 不在受控词表（bulk 缺失登记，禁私加）"
            if est == "internal_observation":
                scv = "locator_verified" if _pointer_exists_in_source(it["source_ref"]) else "unchecked"
            elif est == "peer_reviewed_literature":
                scv = "locator_verified"   # B1 构建期 eutils 题录核验，留痕=原稿 README 检索留痕段
            else:
                scv = "unchecked"          # URL 存在≠claim 成立（astra T2）
            ad = d["ad"]
            blind = (ad == "none")
            claim = {
                "claim_id": cid,
                "scope": scope,
                "failure_mode": d["fm"],
                "observable_signature": d["obs"],
                "risk_level": d["risk"],
                "mitigation": it["mitigation_or_rule"],
                "evidence_source_type": est,
                "source_check": scv,
                "home": {"kind": hk, "id": hi},
                "visibility": "pre_annotation" if blind else "post_decision",
                "blind_safe": blind,
                "answer_dependency": ad,
                "status": "migrated_draft_pending_audit",
                "owner": "pi-chief (WIRE-P1 migration 2026-09-30)",
                "last_reviewed": None,
                "links": [str(it["source_ref"])],
                "conflicts": [],   # astra T5 冲突对象挂载位（字段模板见 INDEX.legend.conflict_schema）
                "provenance": {
                    "origin_cell": cell, "b1_order": i,
                    "legacy_grade": it["source_grade"],
                    "legacy_code_in_legend": HIST_GRADE[est],
                    "report_confidence": it["confidence"],
                    "home_rationale": d["why"],
                },
            }
            if d["note"]:
                claim["note"] = d["note"]
            claims.append(claim)
    return claims


# ---------------------------------------------------------------- 页面装配（唯一 Home+指针）
def _covers(scope, species, tissue):
    sp_ok = "*" in scope["species"] or species in scope["species"] or not scope["species"]
    ti_ok = "*" in scope["tissue"] or tissue in scope["tissue"] or not scope["tissue"]
    return sp_ok and ti_ok


def pages_of(claims):
    pages = {}
    def page(name):
        return pages.setdefault(name, {
            "schema": "eyekb-known-claims-page/1.0",
            "generated_by": "pipeline/pitfalls/build_claims.py (WIRE-P1 REV-1)",
            "page_type": name.split("/")[0], "entries": [], "pointers": []})
    by_home = {}
    for c in claims:
        key = c["home"]["id"] if c["home"]["kind"] in ("cell", "species") else \
            (f"patterns/{c['home']['id']}" if c["home"]["kind"] == "pattern" else None)
        if c["home"]["kind"] == "cell":
            fname = f"cells/{key}.json"
        elif c["home"]["kind"] == "species":
            fname = f"species/{c['home']['id']}.json"
        elif c["home"]["kind"] == "pattern":
            fname = f"patterns/{c['home']['id']}.json"
        else:
            fname = "unmapped/UNMAPPED_SCOPE.json"
        page(fname)["entries"].append(c)
        by_home.setdefault(c["claim_id"], fname)
    # 坐标页指针：cell 页收 pattern/species 覆盖条；species/tissue 页收 pattern 覆盖条
    for sp in SPECIES_PAGE:
        page(f"species/{sp}.json")  # 保证页存在
    for c in claims:
        if c["home"]["kind"] == "cell":
            continue
        # pattern/species claim → 向其覆盖的每个 cell 页挂指针
        covered_cells = []
        for sp in SPECIES_PAGE:
            for tis in (c["scope"]["tissue"] if c["scope"]["tissue"] != ["*"] else CANON_TISSUES):
                cp = f"{sp}__{tis}"
                if _covers(c["scope"], sp, tis):
                    covered_cells.append(cp)
        for cp in covered_cells:
            fn = f"cells/{cp}.json"
            if fn in pages:
                pages[fn]["pointers"].append({
                    "ref_id": c["claim_id"],
                    "context_note": f"scope-hit ({c['evidence_source_type']}/{c['risk_level']}/blind_safe={c['blind_safe']})"})
        for sp in (c["scope"]["species"] if c["scope"]["species"] != ["*"] else SPECIES_PAGE):
            fn = f"species/{sp}.json"
            if c["home"]["kind"] != "species" and fn in pages:
                pages[fn]["pointers"].append({"ref_id": c["claim_id"],
                                              "context_note": "pattern covers species"})
        for tis in (c["scope"]["tissue"] if c["scope"]["tissue"] != ["*"] else CANON_TISSUES):
            fn = f"tissue/{tis}.json"
            pages.setdefault(fn, page(fn))
            if c["home"]["kind"] != "cell":
                pages[fn]["pointers"].append({"ref_id": c["claim_id"],
                                              "context_note": "pattern covers tissue"})
    page("unmapped/UNMAPPED_SCOPE.json")  # 恒存在（本批 0 条）
    excl = {"schema": "eyekb-known-claims-exclusions/1.0",
            "reason": "盲区声明/社区空白登记=无失效模式无签名，按 REV-1 不入账为 claim；保留可追溯",
            "items": [{"origin_cell": k[0], "b1_order": k[1], "kind": t,
                       "why": w} for k, (t, w) in EXCLUDED.items()]}
    return pages, excl


def write_pages(claims, pages, excl):
    import shutil
    if PAGES.exists():
        shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True)
    for fname, pg in pages.items():
        p = PAGES / fname
        p.parent.mkdir(parents=True, exist_ok=True)
        seen = set()
        pg["entries"] = [e for e in sorted(pg["entries"], key=lambda x: x["claim_id"])
                         if not (e["claim_id"] in seen or seen.add(e["claim_id"]))]
        # pointers 去重（同 ref+note 唯一）
        pu = {}
        for x in pg["pointers"]:
            pu[(x["ref_id"], x["context_note"])] = x
        pg["pointers"] = [pu[k] for k in sorted(pu)]
        p.write_text(_scrub_text(json.dumps(pg, ensure_ascii=False, indent=1) + "\n"), encoding="utf-8")
    (PAGES / "EXCLUSIONS.json").write_text(_scrub_text(json.dumps(excl, ensure_ascii=False, indent=1) + "\n"),
                                           encoding="utf-8")
    tally = {k: sum(1 for c in claims if c["home"]["kind"] == k)
             for k in ("cell", "species", "tissue", "pattern", "unmapped")}
    hashes = [(str(p.relative_to(PAGES)), hashlib.sha256(p.read_bytes()).hexdigest())
              for p in sorted(PAGES.rglob("*.json"))]
    idx = {"schema": "eyekb-known-claims-index/1.0", "n_claims": len(claims),
           "n_excluded": len(EXCLUDED), "home_tally": tally,
           "claim_ids": sorted(c["claim_id"] for c in claims),
           "pages": dict(hashes),
           "legend": {"evidence_source_type": {
                          "internal_observation": "自家库内实证（历史档 PIT-E1/原A）",
                          "peer_reviewed_literature": "同行文献（PIT-E2/原B）",
                          "community_lead": "社区线索（PIT-E3/原C）——禁产生 hard_gate/panel_activation/named_label"},
                      "source_check": {"unchecked": "未核", "locator_verified": "指针/题录核过",
                                       "claim_curated": "人工复审接受（本批无）"},
                      "visibility": {"pre_annotation": "盲评前可见（仅结构化旗标）",
                                     "post_decision": "判读决定后开放",
                                     "curator_only": "仅策展人（本批未用）"},
                      "answer_dependency": {"none": "无答案依赖",
                                            "sample_specific": "样本特异",
                                            "dataset_specific": "数据集特异"},
                      "risk_level": {"high": "结论级翻车/系统性不可信",
                                     "medium": "需降级注记或单列",
                                     "low": "操作提示"},
                      "conflict_schema": ("claim.conflicts 追加对象字段（astra T5）：conflict_id/"
                                          "claim_id/panel_version/decision_record_id/scope/"
                                          "initial_decision/final_decision/rule_applied/reviewer/"
                                          "coordinator_recalculation/timestamp——shadow 阶段恒空，"
                                          "冲突由人工裁决/Phase 3 票规流程写入"),
                      "note": "A/B/C 裸字母全局废止（T3）；历史映射仅 legend 内保留"}}
    (PAGES / "INDEX.json").write_text(_scrub_text(json.dumps(idx, ensure_ascii=False, indent=1) + "\n"),
                                      encoding="utf-8")
    lines = [f"{h}  pages/{n}" for n, h in hashes]
    lines.append(hashlib.sha256((PAGES / "INDEX.json").read_bytes()).hexdigest() + "  pages/INDEX.json")
    (HERE / "MANIFEST.sha256").write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")
    return idx


def validate(claims, pages):
    ids = [c["claim_id"] for c in claims]
    assert len(ids) == len(set(ids)) == 50, f"claim 数={len(set(ids))}（预期 50=59−9 不入账）"
    homes = {}
    for c in claims:
        assert c["home"]["kind"] in ("cell", "species", "tissue", "pattern", "unmapped")
        assert c["evidence_source_type"] in EST_BY_GRADE.values()
        assert c["source_check"] in ("unchecked", "locator_verified", "claim_curated")
        assert c["answer_dependency"] in ("none", "sample_specific", "dataset_specific")
        assert c["risk_level"] in ("high", "medium", "low")
        assert c["blind_safe"] == (c["answer_dependency"] == "none")
        assert c["failure_mode"] and c["observable_signature"], "原子 claim 缺失效模式/签名"
        assert c["owner"] and c["status"], "缺 owner/status"
        homes[c["claim_id"]] = homes.get(c["claim_id"], 0) + 1
    assert all(v_ == 1 for v_ in homes.values()), "唯一 Home 破坏"
    # 链接 100% 解析：所有指针 ref_id 存在于 claim 集
    allrefs = set()
    for pg in pages.values():
        for pt in pg["pointers"]:
            allrefs.add(pt["ref_id"])
    dangling = allrefs - set(ids)
    assert not dangling, f"悬空指针: {sorted(dangling)[:5]}（终止条件：链接 100% 可解析）"
    # 同页禁双写（全量+指针同 ref）
    for name, pg in pages.items():
        ent = {e["claim_id"] for e in pg["entries"]}
        assert not ent & {p["ref_id"] for p in pg["pointers"]}, f"{name} 双写"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    claims = build()
    pages, excl = pages_of(claims)
    validate(claims, pages)
    tally = {k: sum(1 for c in claims if c["home"]["kind"] == k)
             for k in ("cell", "species", "tissue", "pattern", "unmapped")}
    print("claims:", len(claims), "excluded:", len(EXCLUDED), "home tally:", tally)
    n_blind = sum(1 for c in claims if c["blind_safe"])
    print(f"blind_safe: {n_blind} / pre_annotation {n_blind}; "
          f"post_decision {len(claims)-n_blind}")
    if a.check:
        import tempfile, shutil as sh
        tmp = Path(tempfile.mkdtemp())
        # 重写到临时目录并全量 diff
        old = {str(p.relative_to(PAGES)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in PAGES.rglob("*.json")}
        gtmp = tmp / "pages"
        gtmp.mkdir()
        gpages = {}
        for name, pg in pages.items():
            gpages[name] = pg
        # 复用 write_pages 逻辑（临时换 PAGES 全局）
        globals()["PAGES"], keep = gtmp, PAGES
        idx = write_pages(claims, pages, excl)
        globals()["PAGES"] = keep
        new = {str(p.relative_to(gtmp)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in gtmp.rglob("*.json")}
        sh.rmtree(tmp)
        drift = [k for k in set(old) | set(new) if old.get(k) != new.get(k)]
        print("CHECK", "PASS" if not drift else f"DRIFT {drift[:6]}")
        return 0 if not drift else 1
    idx = write_pages(claims, pages, excl)
    print("pages written:", len(list(PAGES.rglob('*.json'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
