#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W4: RAG papers 级 dev_stage 标签 sidecar (additive; chunk 级本次不做)。

输入: /mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.2_2026-09.jsonl (3,696 paper 行, 含 title)
输出: /mnt/D/EyeKB/kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl
      —— 新文件 (v2.2 sidecar 本体零改动, OcularKB 库零改动);
      plans/kb3_evidence/REVIEW_SHEET_devstage.tsv (人工抽验 30 篇留痕)
口径:
  - 三值起步 adult / fetal_developing / unknown (任务书 W4); mixed 信号 (两侧同中) → unknown
    + conflict 旗, 禁造 mixed。
  - 规则=标题正则 (词表见下, 全落文件头供溯源); 抽验=分层随机 30 篇人工判 ok/mismatch,
    mismatch 改判并记录 (matched_terms 保留原值, final 字段覆盖)。
  - chunk 级 development_stage 明确不做 → 留 v2.3+ 语料迭代 (任务书"本次不做, 写明")。
用法: python3 kb3_dev_stage_tag.py            # 全量打标 + 出抽验表
      python3 kb3_dev_stage_tag.py --apply-review  # 读回人工判定后重建 final sidecar
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

SRC = Path("/mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.2_2026-09.jsonl")
OUT = Path("/mnt/D/EyeKB/kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl")
REV = Path("/mnt/D/EyeKB/plans/kb3_evidence/REVIEW_SHEET_devstage.tsv")
ABSTRACTS = Path("/mnt/D/EyeKB/plans/kb3_evidence/abstract_dev_stage_hits_20260924.json")
CARD = "t_5425a7ca"

FETAL_RE = re.compile(
    r"\b(fetal|foetal|embryon\w*|embryo\w*|prenatal|gestational|postnat\w*|neonat\w*|"
    r"infant\w*|juvenile|pediatric|paediatric|developing|organoids?\b|hESC|iPSC|"
    r"pluripotent stem cell\w*|retinal progenitor|time.?course of (retinal )?development|"
    r"in vitro (retinal )?differentiation)\b"
    # v1.1 (人工抽验 30 篇修正, 见 REVIEW_SHEET_devstage.tsv #23): 发育名词搭配类。
    # 只收 组织+development 搭配, 不收裸 development (防 'drug development' 方法学假 hits)。
    r"|\b(ocular|retinal|retina|eye|corneal|cornea|lens|neural retina|visual system)\s+"
    r"development(?! of \w*(?:drug|therap|marker|method|tool|pipeline|model system))", re.I)
ADULT_RE = re.compile(
    r"\b(adult\w*|aged|aging|age-?related|senile|geriatric|mature\w*\s+(donor|eye|retina)|"
    r"(older|elderly)\s+adult\w*)\b", re.I)
# adult 词表注意: "mature" 裸词歧义大(成熟剪接), 只收 mature+名词搭配; AMD 类疾病词不判 adult
# (年龄相关疾病文献主体是成人, 但标题不含 adult 字样者按 unknown 处理, 保守)。


def tag(title, ab=None):
    """v1.2 合并: title 信号优先; title 无信号看 abstract (只中一侧→该侧+abs_only 旗;
    两侧同中/双无→unknown)。title 与 abstract 各中一侧互斥 → conflict→unknown。"""
    f, a = FETAL_RE.findall(title), ADULT_RE.findall(title)
    tf = bool(f)
    ta = bool(a)
    af = aa = False
    if ab:
        af, aa = bool(ab.get("fetal_hits")), bool(ab.get("adult_hits"))
    terms = {"fetal": f, "adult": [x if isinstance(x, str) else x[0] for x in a]}
    if tf and ta:
        return "unknown", {**terms, "conflict": "title_both"}
    if tf and aa and not af:      # title 发育 vs abstract 成人 → 矛盾, 保守
        return "unknown", {**terms, "conflict": "title_fetal_abstract_adult"}
    if ta and af and not aa:      # title 成人 vs abstract 发育 → 矛盾, 保守
        return "unknown", {**terms, "conflict": "title_adult_abstract_fetal"}
    if tf:
        return "fetal_developing", terms
    if ta:
        return "adult", terms
    # title 无信号 → abstract 层
    if ab:
        terms["abstract"] = {"fetal": ab.get("fetal_hits", []),
                             "adult": ab.get("adult_hits", [])}
        if af and aa:
            return "unknown", {**terms, "conflict": "abstract_both"}
        if af:
            return "fetal_developing", {**terms, "abs_only": 1}
        if aa:
            return "adult", {**terms, "abs_only": 1}
    return "unknown", terms


def load_papers():
    rows = []
    for ln in SRC.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        d = json.loads(ln)
        if "paper_id" in d:
            rows.append(d)
    return rows


def build(apply_review=False):
    papers = load_papers()
    review_map = {}
    if apply_review and REV.is_file():
        with open(REV, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r.get("manual_call") in ("adult", "fetal_developing", "unknown"):
                    review_map[r["paper_id"]] = r["manual_call"]
    head = {"schema": "eyekb-dev-stage-meta/1.0", "generated": "2026-09-24",
            "card": CARD, "source_db": "v2.2_2026-09 (OcularKB, 只读) ← titles via "
                                        "evidence_meta_v2.2 sidecar (EyeKB)",
            "method": "title+abstract regex v1.2 (词表单一真源="
                      "scripts/rag_meta/kb3_dev_stage_tag.py; abstract 命中素材="
                      "plans/kb3_evidence/abstract_dev_stage_hits_20260924.json, "
                      "merge=title 优先/互斥矛盾保守 unknown/abs_only 旗) + "
                      "人工抽验 30 篇 (REVIEW_SHEET_devstage.tsv)",
            "values": ["adult", "fetal_developing", "unknown"],
            "scope_note": "papers 级标签; **chunk 级 development_stage 本次不做**, 留 v2.3+ "
                          "语料迭代 (KB3 任务书 W4)。两侧同中=unknown+conflict 旗, 禁造 mixed。"}
    ab_hits = {}
    if ABSTRACTS.is_file():
        ab_hits = json.loads(ABSTRACTS.read_text(encoding="utf-8")).get("hits", {})
    out, stats = [head], {"adult": 0, "fetal_developing": 0, "unknown": 0, "conflict": 0,
                          "manual_overridden": 0, "abs_only": 0}
    tagged = []
    for d in papers:
        dev, terms = tag(d.get("title", ""), ab_hits.get(str(d["paper_id"])))
        row = {"paper_id": d["paper_id"], "pmid": d.get("pmid", d["paper_id"]),
               "title": d.get("title", ""), "year": d.get("year"),
               "dev_stage": dev, "matched_terms": terms,
               "dev_stage_final": dev, "manual_check": None}
        if terms.get("conflict"):
            stats["conflict"] += 1
        if terms.get("abs_only"):
            stats["abs_only"] += 1
        tagged.append(row)
    # 抽验 30: 每类 10, 不足则补 unknown; 确定性 seed=20260924
    rng = random.Random(20260924)
    sample = []
    for v in ("adult", "fetal_developing", "unknown"):
        pool = [r for r in tagged if r["dev_stage"] == v]
        sample += rng.sample(pool, min(10, len(pool)))
    ids = {r["paper_id"] for r in sample}
    for r in tagged:
        if apply_review and r["paper_id"] in review_map:
            r["dev_stage_final"] = review_map[r["paper_id"]]
            r["manual_check"] = "sample30:reviewed"
            if r["dev_stage_final"] != r["dev_stage"]:
                r["manual_check"] = "sample30:mismatch->reassigned"
                stats["manual_overridden"] += 1
        stats[r["dev_stage_final"]] += 1
        out.append(r)
    OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in out) + "\n",
                   encoding="utf-8")
    if not apply_review:  # 首轮: 出待人工表 (judgment 列留空)
        with open(REV, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["paper_id", "auto_call", "matched", "title", "manual_call", "note"])
            for r in sample:
                w.writerow([r["paper_id"], r["dev_stage"],
                            json.dumps(r["matched_terms"], ensure_ascii=False),
                            r["title"], "", ""])
    print(json.dumps(stats, ensure_ascii=False), "| papers:", len(tagged),
          "| sample:", len(sample), "| mode:", "apply-review" if apply_review else "tag+sheet")


if __name__ == "__main__":
    build(apply_review="--apply-review" in sys.argv)
