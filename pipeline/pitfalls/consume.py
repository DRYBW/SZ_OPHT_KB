#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""consume.py — 已知问题 claim 的 shadow 消费（拉页 + 风险旗标）。WIRE-P1 交付3（REV-1 定盘版）。

消费语义（astra T4/T5/T6 定盘，取更严者；推翻 qwen 代审版 PITFALL_OVERRIDE）：
  - **shadow：只记旗标与复核要求，禁任何自动改标/降档/覆票**。
    判读改判仍走原三独立判读票与 S0 硬门。本模块不产生 suggested_grade_cap（该列已废止）。
  - 拉页：(species, tissue) → cells 页全量 + species/tissue/pattern 页被引指针解析
    → 合并本格适用 claim 集。
  - 可见性防火墙（T6）：answer_dependency≠none（=blind_safe=false）的条目，
    在**预标注人类面**（evidence_report.md 头段 + decisions_template.csv）
    只输出结构化旗标（claim_id + risk_level + review_required），
    failure_mode/mitigation 自由文本**不注入**（留 post_decision/curator 面）；
    blind_safe=true 的通用方法学条可随带 mitigation 短规则。
  - 本模块只在判读完成段被 run_pipeline 调用；判读证据 JSON/喂料件/盲评 digest
    不 import 本模块（tests/test_s0_gate.py T4 ast 级机检 + firewall grep）。

审计：每次风险旗标命中写 shadow_flags.jsonl
  {ts, run_id, claim_id, cluster_id, risk_level, evidence_source_type,
   answer_dependency, blind_safe, action:"risk_flag_only(no_auto_override)"}。
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE / "pages"

# 类锚 token（词首匹配）→ 受控类名。变量名避开 *TOKENS 关键词族（网关脱敏陷阱，2026-09-29 实证）。
def _anchor_vocab():
    return {
        "Endo": ["endo", "endothel"], "Micro": ["microglia", "micro"],
        "MG": ["müller glia", "muller glia", "müller", "muller", "mg"],
        "Astro": ["astro"], "Rod": ["rod"], "Cone": ["cone"],
        "BC": ["bipolar", "bc"], "RPE": ["rpe", "pigment epithel"],
        "RGC": ["ganglion", "rgc"], "Pericyte": ["pericyte"],
        "SMC": ["smooth muscle", "smc"], "Keratocytes": ["keratocyt"],
        "Fibroblast": ["fibroblast"], "Proliferating": ["proliferat", "cell cycle", "mki67"],
        "Erythroid": ["erythro", "rbc"], "T_cell": ["t cell", "t-cell", "lymphoid"],
        "Mac_Tissue": ["mac", "macrophage", "myeloid", "mono"],
        "Epithelium_generic": ["epithel"],
    }


CLASS_MAP_VOCAB = _anchor_vocab()

# claim 的 applies_to_classes 未落原子契约（astra schema 无此类锚字段）；
# 本批为消费侧增强：按 origin 的 failure_mode 关键词推断类锚，仅作**风险提示命中**，
# 绝不驱动改判。命中逻辑保守：仅当候选类名与失效模式文本里的类直接对应才挂旗。
_ANCHOR_HINTS = {
    "endothel": ["Endo"], "内皮": ["Endo"], "microglia": ["Micro"], "小胶质": ["Micro"],
    "müller": ["MG"], "星形": ["Astro"], "astrocyte": ["Astro"],
    "视杆": ["Rod"], "rod": ["Rod"], "双极": ["BC"], "bipolar": ["BC"],
    "rpe": ["RPE"], "增殖": ["Proliferating"], "proliferat": ["Proliferating"],
    "髓系": ["Mac_Tissue", "Micro"], "myeloid": ["Mac_Tissue", "Micro"],
    "血液": ["Erythroid"], "blood": ["Erythroid"], "上皮": ["Epithelium_generic"],
    "epithel": ["Epithelium_generic"], "周细胞": ["Pericyte"], "pericyte": ["Pericyte"],
    "granularity": ["MG", "Astro"], "ambient": ["Rod", "BC"],
}


def _claim_class_anchors(claim):
    fm = (claim.get("failure_mode", "") + " " + claim.get("observable_signature", "")).lower()
    out = set()
    for kw, cls in _ANCHOR_HINTS.items():
        if kw.lower() in fm:
            out.update(cls)
    return sorted(out)


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def class_match(candidate, applies):
    if not applies or not candidate:
        return False
    low = _norm(candidate)
    for a in applies:
        for tok in CLASS_MAP_VOCAB.get(a, [a.lower()]):
            t = _norm(tok)
            if t and re.search(r"\b" + re.escape(t), low):
                return True
    return False


# 词典组织名 → canonical 页坐标（COORDINATE_TAXONOMY_v1.md §6，C6/C7 批复；服务词典零改动）
PULL_TISSUE_ALIAS = {"fibrovascular_membrane": "fibrovascular_membrane",
                     "fibrovascular membrane": "fibrovascular_membrane",
                     "pdr_membrane": "fibrovascular_membrane",
                     "lacrimal": "lacrimal_gland"}


def _load(fname):
    p = PAGES / fname
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def pull_claims(species, tissue):
    """返回 (本格适用 claim 全量, 悬空 ref_id 列表)。claim 全量=各可见页 entries ∪ 被引指针解析。"""
    tissue = PULL_TISSUE_ALIAS.get(tissue, tissue)
    # 全局 claim 索引（用于指针解析）
    gidx = {}
    for pg in (PAGES.rglob("*.json")):
        if pg.name in ("INDEX.json", "EXCLUSIONS.json"):
            continue
        d = json.loads(pg.read_text(encoding="utf-8"))
        for e in d.get("entries") or []:
            if "claim_id" in e:
                gidx.setdefault(e["claim_id"], e)
    wanted = [f"cells/{species}__{tissue}.json", f"species/{species}.json",
              f"tissue/{tissue}.json"]
    seen, out, dangling = set(), [], []
    for w in wanted:
        pg = _load(w)
        if not pg:
            continue
        for e in pg.get("entries") or []:
            if e["claim_id"] not in seen:
                seen.add(e["claim_id"])
                out.append(e)
        for pt in pg.get("pointers") or []:
            rid = pt["ref_id"]
            if rid in seen:
                continue
            if rid in gidx:
                seen.add(rid)
                c = dict(gidx[rid])
                c["_cited_from"] = w
                out.append(c)
            else:
                dangling.append((w, rid))
    out.sort(key=lambda x: x["claim_id"])
    return out, dangling


def _pre_annotation_line(c):
    """预标注人类面短行。blind_safe=false 只结构化旗标，不放自由文本。"""
    if c.get("blind_safe", True):
        mit = c.get("mitigation") or c.get("failure_mode", "")
        return (f"- `{c['claim_id']}` [{c['evidence_source_type']}/"
                f"risk={c['risk_level']}] {mit}")
    return (f"- `{c['claim_id']}` [risk={c['risk_level']}/"
            f"review_required=manual_post_decision]（自由文本判读后开放）")


def attention_section(species, tissue, s0_meta=None):
    claims, dangling = pull_claims(species, tissue)
    pub = [c for c in claims if c.get("blind_safe", True)]
    red = [c for c in claims if not c.get("blind_safe", True)]
    lines = ["## 本格注意清单（known-issues shadow：只记旗标，不改判；本段无自由文本）", "",
             f"- 判定坐标：species=`{species}`，tissue=`{tissue}`"
             + (f"（来源 `{(s0_meta or {}).get('source', 'manual')}`"
                + ("，override 留痕：s0_overridden_by_user"
                   if (s0_meta or {}).get("overridden_by_user") else "") + "）"
                if s0_meta else ""),
             f"- 适用 claim：{len(claims)} 条（盲评安全 {len(pub)} / 判读后开放 {len(red)}）。"
             "本段仅结构化旗标（astra 保守默认：盲评前不给 known-issues 自由文本）；"
             "短规则与出处见 `shadow_attention.json`（判读后人类面），"
             "自动具名/降级变化恒=0。", "",
             "| claim_id | risk | source_type | blind_safe | 复核要求 |",
             "|---|---|---|---|---|"]
    for c in claims:
        lines.append(f"| `{c['claim_id']}` | {c['risk_level']} | "
                     f"{c['evidence_source_type']} | {str(c['blind_safe']).lower()} | "
                     + ("判读后人工复核（自由文本 post_decision）"
                        if not c["blind_safe"] else "可选复核（通用方法学短规则见机读件）")
                     + " |")
    lines.append("")
    machine = {"schema": "eyekb-shadow-attention/1.0", "species": species, "tissue": tissue,
               "mode": "shadow_no_auto_override", "n_claims": len(claims),
               "claims": [{k: c.get(k) for k in
                           ("claim_id", "risk_level", "evidence_source_type", "source_check",
                            "answer_dependency", "blind_safe", "visibility", "home")}
                          for c in claims]}
    return lines, machine, claims, dangling


def cluster_flags(claims, cluster_top_candidates):
    """逐簇：类锚命中的风险旗标。**无 cap、无 override**，只给复核要求。"""
    flags, audit = [], []
    for c in claims:
        anchors = _claim_class_anchors(c)
        if not anchors:
            continue
        hit = next((cand for cand in (cluster_top_candidates or [])
                    if class_match(cand, anchors)), None)
        if not hit:
            continue
        flags.append(f"REVIEW:{c['claim_id']}({c['risk_level']})")
        audit.append({"claim_id": c["claim_id"],
                      "cluster_candidate": hit,
                      "risk_level": c["risk_level"],
                      "evidence_source_type": c["evidence_source_type"],
                      "answer_dependency": c["answer_dependency"],
                      "blind_safe": c["blind_safe"],
                      "action": "risk_flag_only(no_auto_override)"})
    return flags, audit


def write_outputs(out_dir, species, tissue, claims, per_cluster_audit, run_id, dangling):
    out_dir = Path(out_dir)
    def _red(c, k):
        # 非盲评安全条：全记录文件内也按 post_decision 口径脱敏自由文本
        if not c.get("blind_safe", True) and k in ("failure_mode", "mitigation",
                                                   "observable_signature"):
            return "REDACTED:post_decision"
        return c.get(k)
    att = {"schema": "eyekb-shadow-attention/1.0", "species": species, "tissue": tissue,
           "mode": "shadow_no_auto_override", "run_id": run_id,
           "link_resolution": {"dangling_pointers": dangling, "all_resolved": not dangling},
           "claims": [{**{k: c.get(k) for k in
                          ("claim_id", "risk_level", "evidence_source_type", "source_check",
                           "answer_dependency", "blind_safe", "visibility")},
                       **{k: _red(c, k) for k in ("failure_mode", "mitigation")}}
                      for c in claims]}
    (out_dir / "shadow_attention.json").write_text(
        json.dumps(att, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    n = 0
    with open(out_dir / "shadow_flags.jsonl", "w", encoding="utf-8") as f:
        for a in per_cluster_audit:
            f.write(json.dumps({"ts": time.strftime("%F %T"), "run_id": run_id, **a},
                               ensure_ascii=False) + "\n")
            n += 1
    with open(out_dir / "shadow_flags.jsonl", "a", encoding="utf-8") as f:
        f.write(f"# shadow：本 run 风险旗标数={n}；全部为复核提示，自动具名/降级变化=0"
                "（终止条件监控：坑致自动改标必须恒为 0）\n")
    return att, n
