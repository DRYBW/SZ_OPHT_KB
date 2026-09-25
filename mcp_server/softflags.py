#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP 软复核提示层 (t_d6f2a0a0 / D4 放行, PI 2026-09-25)
v0.2 · 按 astra CONDITIONAL 回函七项必修重写 (review/ASTRA_SOFTFLAG_v01_verdict.md)

两条软提示 (reminder, 非硬旗标, 不新增定名/弃权/候选排除条件):
  1) rod_bc_review  —— 依据 /mnt/D/OcularKB/models/V2PROD_ROD_BC_BLINDSPOT_20260925.md
     (C18 案: 清洁窗口排除 C18 后 2/48,517; 孤立簇非系统性盲区 → 只软提示不设旗标)
  2) mural_crosstalk —— 依据 /mnt/D/EyeKB/plans/kb6b_face_20260925/AUDIT_KB6b_D002_separation.md
     + STROMAL_WARNING_DRAFT.md; 措辞基线 = EVAL_RUN5FACE_20260925.md v1.1 勘误
     (Q6::24 = Myofibroblast/SMC mural 词条接管链, 不是 Keratocytes)。

纪律 (astra §3.6/§3.7/B4/B5/B7):
- 注记只在既有结果产生后附加; 不反馈改变候选/分数/排序/原有字段; 不新增可被解释为
  权重/风险分的字段 (severity 类字段已按 §3.7 删除)。
- 同分并列组 (TOP) 语义消除 dict 插入序依赖; 不给 ranking 加二级排序。
- 角色三层: 已审计共享/反向证据 / 目标类别存活锚 / 仅面板成员事实。
- 运行时消息不输出未经本执行件 OLS 回证的 CL 标识符 (红线3); 本体包含关系以已审计
  定义文本引用 (出处 = KB6b §2 要点4, 其 OLS 引文在册)。
- 面板 = 当次 query_marker 实际加载的 markers 快照 (来源/版本随 trigger 落字),
  不隐式汇总历史或未来版本。
- 开关: env EYEKB_MCP_SOFTFLAGS 每调用读一次; strip().casefold() ∈ {0,false,off,no}
  → off; 其余值一律 on; off 时整 key 不存在。
"""
import os

SCHEMA = "eyekb-softflag/1.0"

# ---- flag#1 参数 (§2 + astra Q1/Q2 裁决: TOP 并列组, 不扩到严格次位) ----
ROD_MIN_HITS = 2         # |R| ≥ 2 (基因证据级启发式; 非表达主导性观测)
ROD_GE_BCCORE = True     # |R| ≥ |B| 条款保留 (astra Q1: 不为扩命中删比较项)

# ---- flag#2 参数 (§3 + astra Q3 裁决 A: 单命中=“家族面板关联提醒”) ----
MURAL_RANK_BOUNDARY = 3  # TOP3 = 第三个不同类别的命中数边界及其全部同分类别

# canonical 归一 (astra §3.1): 去空白 → 取 "::" 后缀 → casefold → 有限同义词表;
# 仅用于 notes 判据, 不回写响应/词条解析; 表外名称不做模糊匹配。
_SYNONYM = {
    "pericyte": "Pericyte", "pericytes": "Pericyte",
    "fibroblast": "Fibroblast", "fibroblasts": "Fibroblast",
    "myofibroblast": "Myofibroblast", "myofibroblasts": "Myofibroblast",
    "keratocyte": "Keratocytes", "keratocytes": "Keratocytes",
    "smc": "SMC", "smooth muscle cells": "SMC",
    "bc": "BC", "rod": "Rod",
}
MURAL_CLASSES = {"Keratocytes", "Fibroblast", "Pericyte", "SMC", "Myofibroblast"}


def _canon(ct):
    s = str(ct).strip()
    s = s.split("::")[-1]
    return _SYNONYM.get(s.casefold(), None) if s.casefold() in _SYNONYM else s


# 角色三层 (证据分层, 不夸大):
#   T2 = KB6b 逐格三色审计在册的 共享/反向 证据 (文件+节号随消息披露)
#   T2a = STROMAL_WARNING_DRAFT 在册的方向反转/上皮源/通签判读
#   T3 = 仅"面板成员"事实 (无独立审计角色) —— 不得被读作已证串扰
ROLES = {
    "audited_shared": {  # KB6b §2 逐格红判据在册 (T2)
        "NNMT": "已审计: Keratocytes 词条反向假锚——对纤维基质 donor 一致率 0.167, 方向反转"
                " (KB6b §2 要点2)",
        "ALDH3A1": "已审计: 对角膜上皮亚型反向——Corneal_suprabasal_PMC lfc=-0.32/cons=0.125,"
                   " 系角膜上皮分化程序基因, pooled 掩盖致 RED (KB6b §2 要点3)",
        "DCN": "已审计: 对 Keratocytes 反向 lfc≤-1.96 (Fibroblast 词条红基因, KB6b §2 表)",
        "LUM": "已审计: 对 Keratocytes 反向 lfc≤-1.96 (同上)",
        "PTGDS": "已审计: 对 Keratocytes 反向 lfc≤-1.96 (同上)",
        "COL1A2": "已审计: Fibroblast 与 Pericyte 两词条共同红基因; 对 Keratocytes 反向 -1.99、"
                  "对纤维基质 -2.81 (KB6b §2 表)",
        "ACTA2": "已审计: SMC 词条红基因, lfc 0.83@Pericytes (被邻组触发, KB6b §2 表)",
        "TAGLN": "已审计: SMC 红基因 (-0.25@Pericytes) 且 Myofibroblast 词条最高负荷组"
                 "=Pericytes (KB6b §2 表/§3)",
        "PRRX1": "已审计: Pericyte 词条红基因 (KB6b §2 表)",
        "MGP": "已审计: Pericyte 词条红基因 (KB6b §2 表)",
        "ITGA1": "已审计: Pericyte 词条红基因 (KB6b §2 表)",
        "THY1": "已审计: Pericyte 词条红基因; Fibroblast 的 THY1/COL3A1 对 Schwann/动脉亚型"
                "亦失败 (KB6b §2 表/§4)",
        "FN1": "已审计: Fibroblast 词条红基因 (KB6b §2 表)",
    },
    "survival_anchor": {  # KB6b §2 要点5/§8 存活锚, 按目标类别语境 (B2 修复: 不跨类计数)
        "KERA": "Keratocytes 侧存活锚 (D002 三色全绿, 对 9 邻组全绿)——拟定 Keratocytes 请复核"
                " KERA 及角膜基质语境",
        "NOTCH3": "Pericyte 侧存活锚——用于 Pericyte 邻类比较, 不替代其他类支持证据",
        "HIGD1B": "Pericyte 侧存活锚——同上",
        "CALD1": "Pericyte 侧存活锚 (亦为壁细胞通签成员, 两种语境各按其审计条目解读)",
        "CNN1": "SMC 侧存活锚——用于 SMC 邻类比较, 不替代其他类支持证据",
        "MYH11": "SMC 侧存活锚——同上",
        "MYL9": "SMC 侧存活锚; 同时是 SMC/Myofibroblast 面板共有成员 (语境分开)",
        "DES": "SMC 侧存活锚——同上 (结构零审计仅涉 SMC·DES 一格, KB6b §7 A4)",
        "LMOD1": "SMC 侧存活锚——同上",
    },
}


def panel_member_note(gene):
    """T3: 未列入审计角色表的家族面板基因——只报面板成员事实。"""
    return "面板成员事实 (当次 markers 快照中位于 mural 家族面板; 本执行件未含其独立审计角色)"


def enabled():
    v = (os.environ.get("EYEKB_MCP_SOFTFLAGS") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _class_hits(markers):
    """从当次 markers 快照派生 (canonical 类名→基因 set) 与 文件版本清单。"""
    per_class = {}
    for ct, gs in markers.items():
        c = _canon(ct)
        s = per_class.setdefault(c, set())
        s.update(str(g).strip().upper() for g in gs)
    return per_class


def _snapshot_sources(prov):
    return [{"library": f.get("library"), "version": f.get("version"), "path": f.get("path")}
            for f in (prov or {}).get("files", [])]


def _top_groups(ranking):
    """h(c) = canonical 类 c 各行现有 n_shared 的最大值 (不相加, 不生成新排名输出)。
    TOP = 达全局最大 h 的类集合。"""
    h = {}
    for e in ranking or []:
        try:
            n = int(e.get("n_shared", 0))
        except (TypeError, ValueError):
            n = 0
        if n <= 0:
            continue  # 零命中行不构成证据
        c = _canon(e.get("cell_type", ""))
        h[c] = max(h.get(c, 0), n)
    if not h:
        return {}, set(), set()
    mx = max(h.values())
    top = {c for c, v in h.items() if v == mx}
    # TOP3 = 第三个不同**类别**的命中数边界及其全部同分类别 (astra R2 必修4:
    # 每类别保留一个分数、不去重分数层; 与"前三个不同分数层级"的反例已区分)
    scores = sorted(h.values(), reverse=True)   # 按类别计, 不去重 set()
    b3 = scores[min(2, len(scores) - 1)]
    top3 = {c for c, v in h.items() if v >= b3}
    return h, top, top3


SUFFIX = ("本提示非硬旗标, 不构成定名或弃权条件; 其出现不代表误注释; "
          "不得用于 module score、标签加权、置信度加分或候选排序输入 (服务级红线)。")


def build_notes(markers, mode, query_genes=None, ranking=None, found_classes=None,
                provenance=None):
    """返回 notes list (可为空)。纯注记: 不触碰 ranking/其他字段。"""
    if not enabled():
        return []
    per_class = _class_hits(markers)
    rod = per_class.get("Rod", set())
    bc_all = per_class.get("BC", set())
    # BC core = canonical BC 的 v4.1 正名面板 (显示名恰为 "BC" 者); 若当次库无 "BC"
    # 显示名 (如 library=retina_interneuron 单库), core 退化为该 BC 面板本身。
    bc_core = set()
    for ct, gs in markers.items():
        if str(ct).strip() == "BC":
            bc_core = {str(g).strip().upper() for g in gs}
    if not bc_core:
        bc_core = bc_all
    mural_union = set()
    for c, gs in per_class.items():
        if c in MURAL_CLASSES:
            mural_union |= gs

    # 符号集合 U = 核心匹配用的当次规范序列去重 (query 已被 core 大写; 不改其输出)
    u = {str(g).strip().upper() for g in (query_genes or []) if str(g).strip()}
    r_hits = sorted(u & rod)
    b_hits_n = len(u & bc_core)
    h_map, top, top3 = _top_groups(ranking)
    notes = []
    src = _snapshot_sources(provenance)

    # ---------- flag#1 rod_bc_review (genes 模式 only) ----------
    if mode == "genes" and "BC" in top and len(r_hits) >= ROD_MIN_HITS \
            and (not ROD_GE_BCCORE or len(r_hits) >= b_hits_n):
        bc_max = h_map.get("BC", 0)
        tied = sorted(top)
        notes.append({
            "flag_id": "rod_bc_review",
            "hard_flag": False,
            "affects_score": False,
            "trigger": {
                "mode": "genes",
                "rod_panel_hits": r_hits,
                "rod_hits_n": len(r_hits),
                "bc_core_hits_n": b_hits_n,
                "bc_h": bc_max,
                "max_tied_classes": tied,
                "rule": ("mode==genes ∧ BC∈TOP(最高命中并列组) ∧ |R|≥%d ∧ |R|≥|B_core|"
                         % ROD_MIN_HITS),
                "data_snapshot": src,
            },
            "message": (
                "复核提醒: 本查询基因证据含视杆面板基因 " + ",".join(r_hits) +
                ", 且 BC 处于本工具 ranking 的最高命中并列组"
                + (f" (与 {'|'.join(x for x in tied if x != 'BC') or '—'} 同分)" if len(tied) > 1 else "")
                + "。若拟采用 BC 定名, 请结合表达量 (rod3/bc3 per-10k 口径) 与共表达背景复核;"
                " 本工具未观测表达主导性, 也未观测最终注释。历史审计背景 (口径=训练池外"
                " truth=Rod∧rod_dominant 清洁窗口, 非当前基因集代理规则的准确率,"
                " 亦非当前查询的风险估计): 排除 C18 单簇后"
                " 2/48,517 (0.004%); C18 同口径 511/660 (77.42%); 含 C18 为 513/49,177"
                " (1.043%)——盲区为 GSE155288 C18 孤立簇样态 (方向指向退化/低质量 rod),"
                " 非系统性低幅度盲区, 且该汇总含 Q8 胎儿集不构成成人总体率; 勿用无真值"
                " 过滤的低杆带率外表述盲区规模。" + SUFFIX),
            "evidence": {
                "interpretation_source":
                    "/mnt/D/OcularKB/models/V2PROD_ROD_BC_BLINDSPOT_20260925.md",
                "note": "本条为基因集层复核启发式, 非表达主导性检测器。"},
        })

    # ---------- flag#2 mural_crosstalk ----------
    conditions = []
    role_lines = []
    if mode == "cell_type":
        hit_classes = sorted({_canon(ct) for ct in (found_classes or []) if ct})
        fam = [c for c in hit_classes if c in MURAL_CLASSES]
        if fam:
            conditions.append("词条查询命中家族类: " + "|".join(fam))
    elif mode == "genes":
        gene_hits = sorted(u & mural_union)
        if gene_hits:
            conditions.append(f"家族面板关联提醒: 输入基因命中 mural 家族面板"
                              f" {len(gene_hits)} 个: " + ",".join(gene_hits) +
                              " (单命中即附注, 不构成已发现串扰的证据)")
            for g in gene_hits:
                role = ROLES["audited_shared"].get(g) or ROLES["survival_anchor"].get(g) \
                    or panel_member_note(g)
                kind = ("T2-已审计共享/反向证据" if g in ROLES["audited_shared"] else
                        "T2a-目标类别存活锚" if g in ROLES["survival_anchor"] else
                        "T3-仅面板成员事实")
                role_lines.append(f"[{kind}] {g}: {role}")
        fam_top3 = sorted(c for c in top3 if c in MURAL_CLASSES)
        if fam_top3:
            conditions.append("ranking 最高命中并列组/第三类别边界内出现家族类: "
                              + "|".join(fam_top3))
    if conditions:
        notes.append({
            "flag_id": "mural_crosstalk",
            "hard_flag": False,
            "affects_score": False,
            "trigger": {
                "mode": mode,
                "conditions": conditions,
                "rule": ("cell_type: found 词条 canonical∈家族; genes: U∩家族面板≠∅ 或 "
                         "TOP3∩家族≠∅ (TOP3=第三不同类别命中数边界含并列)"),
                "data_snapshot": src,
            },
            "message": (
            "串扰警示 (D002 眼表): Pericytes/Smooth Muscle Cells/Fibroblasts/"
            "Myofibroblasts/Keratocytes 家族存在共 marker 判读风险——KB6b 三色复审下"
            " 4 词条全红、纤维基质词条 0 绿; 已审计定义 (OLS 原文见 KB6b §2 要点4,"
            " 本运行时消息按红线3 不转抄 CL 号): keratocyte 为驻角膜基质的特化成纤维"
            " 细胞 (keratocyte⊂fibroblast 本体含义)。判读涉及本家族时——"
            " ①NNMT 为已审计反向假锚 (donor 一致率 0.167, 方向反转), 该审计不支持以它"
            "作为间质区分证据;"
            " ②ALDH3A1 为已审计上皮程序基因 (对 suprabasal PMC 反向), 见它先查上皮语境;"
            " ③方向关系按 KB6b 逐格表: DCN/LUM/PTGDS 已审计对 Keratocytes 反向"
            " (lfc≤-1.96), COL1A2 已审计对 Keratocytes 反向 (-1.99) 且对纤维基质 -2.81;"
            " FN1 等其余红基因成员: 红基因身份不隐含对特定邻类的方向, 以对应表项为准;"
            " Keratocytes↔Fibroblast 互判建议对照 KB6b 红/绿判据复核, 其中 Keratocytes"
            " 侧唯一全绿锚为 KERA——拟定 Keratocytes 请复核 KERA 及角膜基质语境;"
            " Pericyte 侧存活锚 NOTCH3/HIGD1B/CALD1 与 SMC 侧 CNN1/MYH11/MYL9/DES/LMOD1"
            " 各用于其目标类邻类比较, 不跨类计数、不替代彼此支持证据;"
            " ④比较 Pericyte vs SMC vs Myofibroblast 时, 建议结合共表达背景解释;"
            " ⑤Myofibroblast 词条: KB6b §3 交叉扫描登记其在 D002 眼表无一专属高表达"
            " 立足组 (见该节逐格表), 判读引用它时注意此审计背景。"
                " 已证伪措辞提醒: RUN5-face Q6::24 (truth=Pericytes 98.7% 纯) 的归因是"
                " Myofibroblast/SMC mural 词条接管链 (kb_top1=Myofibroblast, 三票=SMC,"
                " Pericyte 词条未上榜) 之表达层相容证据, 不是 Keratocytes; 查询引擎侧排序"
                " 机制未审 (KB6b astra A10 边界)。"
                + ("".join(" 逐基因角色 " + ln + ";" for ln in role_lines[:14]))
                + SUFFIX),
            "evidence": {
                "interpretation_source": [
                    "/mnt/D/EyeKB/plans/kb6b_face_20260925/AUDIT_KB6b_D002_separation.md",
                    "/mnt/D/EyeKB/plans/kb6b_face_20260925/STROMAL_WARNING_DRAFT.md",
                    "/mnt/D/EyeKB/plans/evalset/EVAL_RUN5FACE_20260925.md (v1.1 勘误)"],
                "role_layers": "T2=KB6b 逐格审计在册; T2a=存活锚按目标类语境; "
                               "T3=仅当次面板成员事实 (无独立审计角色)"},
        })

    notes.sort(key=lambda n: n["flag_id"])
    return notes


def wrap_resp(resp, markers, mode, provenance=None, **kw):
    """eyekb_core 挂载 helper: 有 note 才加 soft_flags key (off/空 → 不挂 key;
    与改前输出的等价性按规范序列化层由 sf13 验证, 不声称会话级字节一致)。"""
    notes = build_notes(markers, mode, provenance=provenance, **kw)
    if notes:
        resp["soft_flags"] = {"schema": SCHEMA, "enabled": True, "notes": notes}
    return resp
