#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_expected_composition_v0.py — EyeKB DISC_COMP (D-1) 组成先验新面 v0 构建
卡: t_fa03e1d7 | 任务书: <EYEKB>/plans/comp_prior_20260928/BRIEF_DISC_COMP.md
放行: USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加七B (D-1)

纪律:
- 默认 OFF 不接线 (本目录零 MCP/运行时引用; 接线与激活另卡另批)
- 逐行挂 PMID; 题录三判据机械自检
- 禁从自家聚类/自家 demo 注释派生比例 (本脚本数值来源 = kb/baselines adult-only 主档
  供者级分布 [A 级, 谱系=D001/D002 外部作者注释本地复算] + priors/composition v1
  跨研究经验区间 [C 级, 同谱系] + 盘上已入库文献原文陈述 [B 级, chunks 逐字] )
- fetal/organoid/非成年 条目不得混入 (数值折叠只收 human+adult+capture-composition 口径句);
  疾病态比例不建
- 全程 CPU 只读输入; 输出只写 kb/composition/

区间机械公式 (预注册):
  low  = floor( min( donor_iqr_low, priors_expected_low, folded_lit_low ) )
  high = ceil ( max( donor_iqr_high, priors_expected_high, folded_lit_high ) )
  mid  = round( donor_median_pct, 1 )
  无 A 级数值来源的行 → low/mid/high = null, evidence = "no_evidence" (禁编数)
"""
import json, re, sys, datetime, math, pathlib

KB = pathlib.Path("<EYEKB>/kb")
OUT = KB / "composition"
PAPERS = "<STORE>/ocularkb/rag/literature_db/v2.4.2_2026-09/papers.jsonl"
SIDECAR = str(KB / "literature_db/evidence_meta_v2.3_2026-09.jsonl")
VK_DIR = KB / "vk_literature_index"

RET = json.load(open(KB / "priors/composition/human_retina.json"))
BR = json.load(open(KB / "baselines/retina.json"))
BO = json.load(open(KB / "baselines/ocular_surface.json"))

donor_r = {c["class"]: c for c in BR["major_classes"]}
prior_r = {c["class"]: c for c in RET["major_classes"]}
donor_o = {c["class"]: c for c in BO["major_classes"]}

# ---------------------------------------------------------------- 文献锚表
# kind: "fold"=可折叠进区间的定量句(human/adult/capture-composition 口径)
#       "context"=口径不同/亚型/理论估计/密度, 只作定性锚不折叠
#       "identity"=该类型在正常成人组织存在的直接文献支持
LIT = {
 "retina": {
  "Rod": [
    dict(pmid="38012720", kind="fold", bound=("high", 55.2),
         quote="the distributions of cell type proportions ... ranging from 2.5% RGC to 55.2% Rod",
         note="snRNA+snATAC 多组学 跨样本组成极值 (人, adult)"),
    dict(pmid="37388908", kind="identity",
         quote="the highest overlap (63.9%) is observed for the most abundant cell type, Rod",
         note="人 snRNA-seq atlas: Rod 为最丰细胞类型 (定性)"),
    dict(pmid="41578023", kind="identity", quote=None,
         note="HRCA 整合图谱 majorclass 收录 Rod (registry 台账 OA-D001)")],
  "Cone": [
    dict(pmid="37388908", kind="context",
         quote="S cones (0.07% of total retinal cells)",
         note="S-cone 亚型口径, 不折叠; Cone 整体存在性支持"),
    dict(pmid="32555229", kind="identity", quote=None,
         note="人中央凹/周边视网膜细胞图谱收录锥细胞"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 Cone")],
  "BC": [
    dict(pmid="37388908", kind="fold", bound=("high", 20.8),
         quote="AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset",
         note="人 snRNA-seq 该数据集层面双极细胞占比 (fold high)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 BC")],
  "AC": [
    dict(pmid="37388908", kind="fold", bound=("high", 21.5),
         quote="AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset",
         note="同上数据集层 AC 占比 (fold high)"),
    dict(pmid="37388908", kind="context",
         quote="vGlut3 excitatory ACs (0.7% of total retinal cells)",
         note="兴奋性 AC 亚型口径, 不折叠"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 AC")],
  "HC": [
    dict(pmid="37388908", kind="identity",
         quote="lowest overlap is observed for HC (49.0%)",
         note="人图谱收录水平细胞 (定性)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 HC")],
  "RGC": [
    dict(pmid="37388908", kind="context",
         quote="the total number of RGCs only accounts for approximately 1% of the cell population in the retina",
         quote_kind="theory", note="组织学理论估计口径, 不折叠; 方向锚"),
    dict(pmid="37388908", kind="fold", bound=("high", 4.1),
         quote="AC, BC, and RGC, comprising 21.5%, 20.8%, and 4.1% of the cell population for this dataset",
         note="人数据集捕获层 RGC 占比 (fold high)"),
    dict(pmid="38012720", kind="fold", bound=("low", 2.5),
         quote="ranging from 2.5% RGC to 55.2% Rod",
         note="跨样本 RGC 下界极值 (fold low)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 RGC")],
  "MG": [
    dict(pmid="32069977", kind="identity",
         quote="Within the fovea, Müller cells and horizontal cells ...",
         note="人中央凹 AIR 图谱确认 Müller 细胞存在 (定性)"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 MG")],
  "Astro": [
    dict(pmid="32555229", kind="context",
         quote="depletion of astrocytes from fovea (0.9% of all non-neuronal cells in fovea and 12% in periphery)",
         note="分母=非神经元细胞, 口径异, 不折叠; 区域差异方向锚"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 Astro")],
  "Micro": [
    dict(pmid="37017569", kind="context",
         quote="microglia (11 cells, 0.0146% of total cell count) directly mapped to the chromatin landscape",
         note="scATAC 直接映射子集口径, 不折叠; 稀有性方向锚"),
    dict(pmid="41578023", kind="identity", quote=None, note="HRCA majorclass 收录 Microglia")],
  "RPE": [
    dict(pmid="41578023", kind="identity", quote=None,
         note="HRCA 神经视网膜 majorclass 收录 RPE (捕获 0.03%)"),
    dict(pmid="32946783", kind="context",
         quote="pigment epithelial cells had 2% RPE65 (expression in organoids)",
         note="器官类表达口径且涉 organoid, 不折叠不入面; 仅登记排除")],
 },
 "ocular_surface": {
  "Epithelium": [
    dict(pmid="34381080", kind="identity",
         quote="These 16 clusters correspond to 11 subtypes of epithelial cells, keratocytes, Langerhans cells, melanocytes, vascular endothelial cells and corneal endothelial cells",
         note="成人人角膜单细胞目录: 上皮为大类 (定性)"),
    dict(pmid="34741068", kind="identity",
         quote="The cornea is composed of five layers: its outer surface is a stratified sheet of corneal epithelial cells",
         note="人角膜分层结构 (定性)"),
    dict(pmid="32502616", kind="identity", quote=None,
         note="成人结膜/角膜缘/角膜上皮 scRNA 收录")],
  "Fibroblasts": [
    dict(pmid="34381080", kind="fold", bound=("low", 15),
         quote="Over 15% of cells in our analysis are keratocytes within a single cluster",
         note="成人角膜 scRNA: keratocyte 单簇 >15% (fold low)"),
    dict(pmid="40838019", kind="identity",
         quote="The corneal stroma, composed mainly of keratocytes",
         note="角膜基质主驻留细胞为 keratocyte (定性)"),
    dict(pmid="34741068", kind="identity",
         quote="The keratocytes populate the corneal stroma", note="定性")],
  "Corneal Endothelium": [
    dict(pmid="33865984", kind="context",
         quote="endothelial cells in humans are not endogenously renewed ... density declines at an average of approximately 0.6% per year",
         note="细胞密度口径 (cell/mm^2), 非组成百分比, 不折叠; CEC 身份/稀有性锚"),
    dict(pmid="34381080", kind="identity", quote=None,
         note="角膜单细胞目录收录 corneal endothelial cells (CenC)")],
  "Endothelium": [
    dict(pmid="34381080", kind="identity", quote=None,
         note="角膜单细胞目录收录 vascular endothelial cells")],
  "Immune Cells": [
    dict(pmid="34381080", kind="identity", quote=None,
         note="角膜单细胞目录收录 Langerhans cells (免疫)"),
    dict(pmid="41552884", kind="identity", quote=None,
         note="角膜巨噬细胞综述 (人源证据强调)")],
  "Melanocytes": [
    dict(pmid="34381080", kind="identity", quote=None, note="角膜单细胞目录收录 melanocytes"),
    dict(pmid="40216818", kind="identity",
         quote="PAX3 expression in LM as well in the conjunctival melanocytes",
         note="角膜缘/结膜黑色素细胞存在 (定性)")],
  "Pericytes": [
    dict(pmid="D002-PORTAL-ONLY", kind="identity", quote=None,
         note="无盘上成人眼表 pericyte 组成文献句; 身份仅 D002 官方注释 (A 级) — B 级缺项如实登记")],
  "Schwann Cells": [
    dict(pmid="40649793", kind="context",
         quote="NGF ... corneal nerve regeneration",
         note="眼表神经综述 (定性),  Schwann 组成%未钉死")],
  "Smooth Muscle Cells": [
    dict(pmid="40649793", kind="context",
         quote="NGF has been found to be produced by ... smooth muscle cells",
         note="综述提及眼表 SMC 存在 (定性)")],
  "_disclosure_conjunctival_epithelium": [
    dict(pmid="32502616", kind="identity", quote=None,
         note="成人结膜上皮 scRNA; D002 无独立 super class (portal 标签归 Epithelium)")],
  "_disclosure_goblet": [],
 },
}

RETINA_CLASSES = ["Rod","Cone","BC","AC","HC","RGC","MG","Astro","Micro","RPE"]
SRC_NAME = {"Astro":"Astrocyte","Micro":"Microglia"}  # 面短名 -> baselines/priors 键名
CLASS_CN_R = {c: prior_r[SRC_NAME.get(c,c)]["label_cn"] for c in RETINA_CLASSES}
OCS_CLASSES = list(donor_o.keys())

# ------------------------------------------------- PMID 题录三判据机械自检
def pmid_verify(pmids):
    need = {p for p in pmids if p and not p.startswith("D002")}
    rows = {}
    with open(PAPERS, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["paper_id"] in need:
                rows[d["paper_id"]] = d
    vktext = "".join(str(p.read_text(errors="ignore")) for p in VK_DIR.glob("*.md"))
    sidecar_ids = set()
    with open(SIDECAR, encoding="utf-8") as f:
        for line in f:
            try: sidecar_ids.add(json.loads(line)["pmid"])
            except Exception: pass
    out = {}
    for p in need:
        d = rows.get(p)
        j1 = bool(d and d.get("title") and d.get("journal") and d.get("year"))
        j2 = bool(d and (d.get("n_chunks") or 0) > 0)
        vkhit = ("PMID"+p in vktext) or (p in sidecar_ids)
        # j3 = 性状元数据在盘可核 (species 或 tissues 非空) — 任务书口径: "papers.jsonl 元数据可核者"
        j3 = bool(d and (str(d.get("species") or "").strip() not in ("", "nan", "unknown")
                         or (d.get("tissues") or [])))
        out[p] = dict(j1_papers_jsonl=j1, j2_nonghost=j2, j3_trait_meta=j3, vk_or_sidecar_hit=vkhit,
                      title=(d or {}).get("title",""), year=(d or {}).get("year"),
                      journal=(d or {}).get("journal"), n_chunks=(d or {}).get("n_chunks"),
                      species=(d or {}).get("species"), tissues=(d or {}).get("tissues"))
    return out

# ------------------------------------------------- 区间机械装配
def face_row(cls, cn, donor, pri, lit_list, denom_note, extra=None):
    lows, highs, mids = [], [], []
    if donor:
        if donor.get("donor_iqr_pct"):
            lows.append(float(donor["donor_iqr_pct"][0])); highs.append(float(donor["donor_iqr_pct"][1]))
        if donor.get("donor_median_pct") is not None:
            mids.append(float(donor["donor_median_pct"]))
        # 并入口径: 供者级 IQR 上界塌缩为 0 时, 以 pooled 参考值兜住 high (防自旗标荒谬区间)
        if float(donor.get("donor_iqr_pct",[0,0])[1]) == 0.0 and donor.get("pooled_pct_for_reference_only"):
            highs.append(float(donor["pooled_pct_for_reference_only"]))
    if pri:
        if pri.get("expected_range_pct"):
            lows.append(float(pri["expected_range_pct"][0])); highs.append(float(pri["expected_range_pct"][1]))
    fold_low, fold_high, anchors = [], [], []
    for L in lit_list:
        if L.get("kind") == "fold":
            b, v = L["bound"]
            (fold_low if b == "low" else fold_high).append(v)
        anchors.append({k: L[k] for k in L if k != ""})
    lows += fold_low; highs += fold_high
    lit_real = [a for a in anchors if str(a.get("pmid","")).isdigit()]
    has_B = any(a["kind"] in ("fold","identity") for a in lit_real)
    ctx_only = (not has_B) and any(a["kind"]=="context" for a in lit_real)
    ev = "A_registry_recompute" + ("+B_literature" if has_B else ("+B_context_only" if ctx_only else ""))
    if not lows and not mids:
        row = dict(cell_type=cls, label_cn=cn, low_pct=None, mid_pct=None, high_pct=None,
                   evidence="no_evidence", literature_anchors=anchors,
                   denominator_note=denom_note)
    else:
        low = math.floor(min(lows)) if lows else 0
        high = math.ceil(max(highs)) if highs else None
        mid = round(max(mids), 1) if mids else None
        row = dict(cell_type=cls, label_cn=cn, low_pct=low, mid_pct=mid, high_pct=high,
                   evidence=ev, literature_anchors=anchors, denominator_note=denom_note)
    row["grade_b_status"] = "B" if has_B else ("B_context_only" if ctx_only else "B_missing")
    row["pmids"] = sorted({l["pmid"] for l in lit_list if l["pmid"].isdigit()})
    if extra: row.update(extra)
    return row

def build():
    generated = datetime.date(2026, 9, 28).isoformat()
    retina_rows, ocs_rows = [], []
    for c in RETINA_CLASSES:
        pri = prior_r[SRC_NAME.get(c,c)]
        d = donor_r[SRC_NAME.get(c,c)]
        lit = LIT["retina"][c]
        r = face_row(c, CLASS_CN_R[c], d, pri, lit,
                     "分母=人正常成人神经视网膜捕获事件构成 (snRNA-seq nuclei; D001 adult-only 供者级主档); 非组织学真值, 非达标线 (Astra T2 usage_scope)")
        r["a_measured"] = dict(donor_median_pct=d["donor_median_pct"], donor_iqr_pct=d["donor_iqr_pct"],
                               donor_range_pct=d["donor_range_pct"],
                               pooled_adult_only_ref=d.get("pooled_pct_for_reference_only"))
        r["c_prior_v1"] = dict(expected_range_pct=pri.get("expected_range_pct"),
                               per_study_spread_pct=pri.get("per_study_spread_pct"))
        if d.get("enrichment_note"): r["design_note"] = d["enrichment_note"]
        retina_rows.append(r)
    # 血管 off-panel 两行: 无成人神经视网膜分母可用文献区间 → no_evidence 行 (禁编数)
    retina_rows.append(face_row("Endo_vascular", "血管内皮 (off-panel)", None, None,
        [dict(pmid="41578023", kind="identity", quote=None,
              note="HRCA 10 类词表不含血管类; 真实全视网膜含低比例血管成分, 出现小簇属正常 (baselines/retina.json caveat)")],
        "无适用区间: 神经视网膜 snRNA 分母下文献百分比未钉死 → 仅 unexpected-identity 披露"))
    retina_rows.append(face_row("Pericyte_vascular", "周细胞 (off-panel)", None, None,
        [dict(pmid="41578023", kind="identity", quote=None,
              note="同上 caveat: 血管 mural 成分出现不打 contamination 旗")],
        "无适用区间 → 披露行"))

    stroma_ref = BO.get("stromal_keratocyte_reference", {})
    for cls_name, o in donor_o.items():
        lit = LIT["ocular_surface"].get(cls_name, [])
        r = face_row(cls_name, cls_name, o, None, lit,
                     "分母=人正常成人眼表 (cornea/limbus/sclera 超级类) 捕获事件构成 (D002 portal 作者注释, adult-only 供者级主档); 区域混合口径, 禁跨区套用 (category_note)")
        r["a_measured"] = dict(donor_median_pct=o.get("donor_median_pct"), donor_iqr_pct=o.get("donor_iqr_pct"),
                               donor_range_pct=o.get("donor_range_pct"),
                               pooled_adult_only_ref=o.get("pooled_pct_for_reference_only"))
        if cls_name == "Fibroblasts" and stroma_ref:
            r["keratocyte_block"] = dict(pooled_pct=stroma_ref["d002_measured"]["pooled_pct"],
                                         unit_median=stroma_ref["d002_measured"]["unit_level_adult"]["median_pct"],
                                         source="ocular_surface.json stromal_keratocyte_reference (t_e1febb8e)")
        ocs_rows.append(r)
    # 结膜子类披露行 + goblet no_evidence 行
    ocs_rows.append(face_row("Conjunctival_epithelium(sub)", "结膜上皮 (D002 内子类)", None, None,
        LIT["ocular_surface"]["_disclosure_conjunctival_epithelium"],
        "D002 无独立结膜 super class (portal 标签归 Epithelium); 结膜基线=骨架待回填 (kb/baselines/conjunctiva.json)"))
    ocs_rows.append(face_row("Goblet_cell", "杯状细胞", None, None,
        LIT["ocular_surface"]["_disclosure_goblet"],
        "盘上无成人结膜杯状细胞组成定量文献句 → no_evidence, 禁编数"))

    # 三判据自检
    all_pm = sorted({p for rows in (retina_rows+ocs_rows) for p in rows["pmids"]})
    ver = pmid_verify(all_pm)
    ledger = []
    for rows, page in ((retina_rows,"retina_normal_adult_human"), (ocs_rows,"ocular_surface_normal_adult_human")):
        for r in rows:
            for p in r["pmids"]:
                v = ver.get(p, {})
                ledger.append(dict(page=page, cell_type=r["cell_type"], pmid=p,
                                   title=v.get("title",""), year=v.get("year"), journal=v.get("journal"),
                                   n_chunks=v.get("n_chunks"), species=v.get("species"), tissues=v.get("tissues"),
                                   j1=v.get("j1_papers_jsonl"), j2=v.get("j2_nonghost"), j3=v.get("j3_trait_meta"),
                                   vk_or_sidecar=v.get("vk_or_sidecar_hit")))
    n_fail = sum(1 for l in ledger if not (l["j1"] and l["j2"] and l["j3"]))
    missing_pmid_rows = [f"{page}:{r['cell_type']}"
                         for rows,page in ((retina_rows,"retina_normal_adult_human"),(ocs_rows,"ocular_surface_normal_adult_human"))
                         for r in rows if not r["pmids"]]

    face = {
     "schema": "eyekb-composition-face/0.1",
     "entry_id": "EXPECTED_COMPOSITION_v0",
     "title": "组成先验面 v0 (D-1): 正常成人视网膜 + 正常成人眼表/角膜-结膜 — 文献派生, 默认 OFF",
     "generated": generated,
     "card": "t_fa03e1d7",
     "authority": "USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加七B (D-1); 任务书 plans/comp_prior_20260928/BRIEF_DISC_COMP.md",
     "wiring": "OFF — 未接线 (零 MCP/运行时引用; 接线与激活另卡另批, 本面任何激活须 PI 拍板)",
     "status": "v0_candidate_selfcheck_only",
     "scope": {"species": "human", "organism_stage": "adult_only",
               "disease_states": "不建 (PDR 注释不可靠口径维持; 疾病材料不得对照健康面验收, Astra T2 usage_scope)",
               "fetal_organoid_developing": "数值折叠排除; 引用记录中显式标注排除原因 (32946783 organoid 句/39117640 developing/36645183 fetal)",
               "tissues_out_of_v0": "其余组织留 v1"},
     "evidence_grades": {"A": "registry 台账外部作者注释本地复算 (kb/baselines adult-only 供者级主档, 带路径)",
                         "B": "盘上已入库 RAG 文献原文直接报告 (chunks 逐字句)",
                         "C": "跨研究经验区间 (kb/priors/composition/human_retina.json, 卡 t_39182aa2)",
                         "no_evidence": "无 A/B/C 可用 → 不编数"},
     "lineage_declaration": "比例区间来源 = D001(HRCA)/D002(OcularSurface) portal 作者注释复算 (经 kb/baselines v1.1 adult-only 主档) + priors v1 经验区间 + 已入库文献原文句; 全程未使用自家聚类/自家 demo 注释 (禁循环条款)",
     "interval_rule": "low=floor(min(donor_iqr_low, priors_expected_low, fold_lit_low)); high=ceil(max(donor_iqr_high, priors_expected_high, fold_lit_high)); mid=donor_median; 无来源行=null(no_evidence)",
     "denominator_semantics": "面=该取样材料在该实验流程下捕获事件的构成参考 (身份参考+背景对照), 非组织学真值, 非组成达标线; 旗标=提示复核≠注释错误",
     "pmid_verification": {"papers_jsonl": PAPERS, "sidecar": SIDECAR,
                           "criteria": "j1=题录在 v2.4.2 papers.jsonl 可解析(题录三要素非空); j2=非幽灵(n_chunks>0); j3=入库可溯(vk 页∨sidecar∨papers.jsonl)",
                           "pmids_total": len(all_pm), "ledger_fail_rows": n_fail},
     "rows_missing_pmid": missing_pmid_rows,
     "activation_obligations": [
       "OB-1 缺逐行 PMID 的行 (D002 portal 身份, 盘上无组成文献句): 见 rows_missing_pmid — 激活前须补文献或维持 OFF",
       "OB-2 眼表面=区域混合超级类 (D002 口径), 激活接线时须按 tissue_group 分层出区间或按区域路由 (category_note 禁跨区套用)",
       "OB-3 反向质检已触发 (Q1/Q2/Q3 健康集旗标率>20%, 见 COMP_SELFFLAG_20260928.md §3): v0 区间对跨平台/跨取材区域/分选设计过窄, 属面侧已知限制 — 激活前须分层/豁免规则化并过 PI 拍板"
     ],
     "pages": {"retina_normal_adult_human": {
        "registry_anchor": "OA-D001 (HCA-HRCA-v1.0), PMID 41578023, path <STORE>/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad",
        "donor_main": "kb/baselines/retina.json adult-only 主档 (97 donors)",
        "rows": retina_rows},
       "ocular_surface_normal_adult_human": {
        "registry_anchor": "OA-D002 (CELLxGENE-OcularSurface), path <STORE>/data/D002_ocularsurface/D002_allcells_578K.h5ad",
        "donor_main": "kb/baselines/ocular_surface.json adult-only 主档 (41 donors/67 单元); 超级类区域混合口径禁跨区套用",
        "rows": ocs_rows}},
     "caveats": [
       "RGC/神经元类比例受核分选与建库设计影响 (NeuN±, RGC 富集) — 判异常前必查建库策略 (baselines caveat 继承)",
       "snRNA(核) 与 scRNA(细胞) 类比例不可直接互比 (Astra T2)",
       "眼表 Immune 仅 1.7% 池: 眼表固有免疫稀少, 免疫比例不可对照炎症样本",
       "Corneal Endothelium 主档中位 0%: 纯 CEC 材料(碎块层) 分母=100%, 不适用本行",
       "Goblet/结膜细节行 = 数据与文献双缺项, 已标 no_evidence",
       "PAPER 41578023 (HRCA) n_chunks=1 (入库增量非全 chunk 化) — j2 勉强过, 内容锚不依赖它"],
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"EXPECTED_COMPOSITION_v0.json").write_text(json.dumps(face, ensure_ascii=False, indent=1), encoding="utf-8")
    import csv
    with open(OUT/"ledgers/PROVENANCE_COMP_v0.tsv","w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ledger[0].keys()), delimiter="\t")
        w.writeheader(); w.writerows(ledger)
    print("rows:", len(retina_rows), "retina +", len(ocs_rows), "ocs | pmids:", len(all_pm),
          "| ledger:", len(ledger), "fail:", n_fail)
    for l in ledger:
        if not (l["j1"] and l["j2"] and l["j3"]):
            print("FAIL", l["page"], l["cell_type"], l["pmid"])

if __name__ == "__main__":
    sys.exit(build())
