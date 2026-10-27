#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LINKKEY v1 独立复算器（供协调者"亲自重跑并逐节点比对"用；与 build_connect_key.py 分属两条实现路径）。

复算内容（全部从两个输入件 + 已落盘 TSV 现读，不采信任何自述数字）:
  1. 结构不变量：物理行数 == 逻辑行数（无内嵌换行）、无空 reason、A⊂B、每行 pmid 在语料中存在
  2. 头条数字：三档对上率 / 逐条原因计数 / 语料两档 / pmid 可用性
  3. 与 LINKKEY_STATS_v1.json 声明值逐项比对 → 不一致即 FAIL（exit 1）
用法: python3 verify_deliverables.py
"""
import json, csv, os, sys, collections

OUT = os.path.dirname(os.path.abspath(__file__))
CITED = "/mnt/D/EyeKB/plans/kbreach_fix_20261024/clone_check/kb/link_registry/LINK_REGISTRY_v1.jsonl"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl"
fails, oks = [], []


def chk(name, got, want):
    if got == want:
        oks.append(f"{name} = {got}")
    else:
        fails.append(f"{name}: got {got!r} want {want!r}")


def rows(fn):
    with open(os.path.join(OUT, fn), encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def phys(fn):
    with open(os.path.join(OUT, fn), encoding="utf-8") as f:
        return sum(1 for _ in f)


# ---- 结构不变量 -------------------------------------------------------
for fn, n in [("CONNECT_KEY_v1.tsv", 803), ("UNMATCHED_v1.tsv", 1003),
              ("CORPUS_TOUCH_v1.tsv", 3917), ("REGISTRY_SOURCES_v1.tsv", 5)]:
    r = rows(fn)
    chk(f"{fn} logical_rows", len(r), n)
    chk(f"{fn} physical_lines==logical+1", phys(fn), n + 1)   # 口径：无内嵌换行

u = rows("UNMATCHED_v1.tsv")
chk("UNMATCHED empty reason rows (A 判据)",
    sum(1 for r in u if not r["reason_code"].strip() or not r["reason_text"].strip()), 0)

c = rows("CONNECT_KEY_v1.tsv")
chk("CONNECT key_used values", sorted(set(r["key_used"] for r in c)), ["pmid"])
chk("CONNECT match_level values", sorted(set(r["match_level"] for r in c)), ["exact"])
chk("A-hit not B-hit rows (A⊂B)", sum(1 for r in c
    if r["caliber_A_strict_title"] == "hit" and r["caliber_B_title_prefix40"] != "hit"), 0)

# ---- 从输入件独立重算（不复用 build 脚本的函数）------------------------
corpus_ids = set()
with open(CORPUS, encoding="utf-8") as f:
    for i, line in enumerate(f):
        corpus_ids.add(json.loads(line)["paper_id"])
chk("corpus unique paper_id", len(corpus_ids), 3917)

cited = collections.defaultdict(int)
with open(CITED, encoding="utf-8") as f:
    for line in f:
        for cc in (json.loads(line).get("citations") or []):
            if cc.get("pmid"):
                cited[str(cc["pmid"])] += 1
chk("cited unique pmid", len(cited), 803)
chk("cited absent from corpus", sum(1 for p in cited if p not in corpus_ids), 0)
chk("CONNECT pmid set == cited set", set(r["pmid"] for r in c) == set(cited), True)

# ---- 与声明值比对 -----------------------------------------------------
s = json.load(open(os.path.join(OUT, "LINKKEY_STATS_v1.json"), encoding="utf-8"))
chk("A_strict.hit", sum(1 for r in c if r["caliber_A_strict_title"] == "hit"),
    s["caliber_A_strict_title"]["hit"])
chk("B_prefix40.hit", sum(1 for r in c if r["caliber_B_title_prefix40"] == "hit"),
    s["caliber_B_relaxed_title_prefix40"]["hit"])
chk("C_identifier.hit", sum(1 for r in c if r["match_level"] == "exact"),
    s["caliber_C_identifier_pmid"]["hit"])
A = [r for r in u if r["caliber"] == "A_strict_title_exact"]
chk("A reason counts", dict(collections.Counter(r["reason_code"] for r in A)),
    s["unmatched_rows_reason_counts"])
chk("A bucket counts", dict(collections.Counter(r["bucket"] for r in A)),
    s["unmatched_rows_bucket_counts"])
t = rows("CORPUS_TOUCH_v1.tsv")
chk("TOUCH cited", sum(1 for r in t if r["touch_class"] == "CITED_AS_EVIDENCE"),
    s["corpus_rows_cited_as_evidence"])
chk("TOUCH not_cited", sum(1 for r in t if r["touch_class"] == "NOT_CITED"),
    s["corpus_rows_not_cited"])
chk("pmid_available=yes", sum(1 for r in t if r["pmid_available"] == "yes"), 3688)
chk("pmid_available=no", sum(1 for r in t if r["pmid_available"] == "no"), 229)
chk("cited_side_has_doi any",
    sum(1 for r in c if r["cited_side_has_doi"] == "yes"), s["doi_key_available_on_cited_side"])
chk("cited_side_has_pmcid any",
    sum(1 for r in c if r["cited_side_has_pmcid"] == "yes"), s["pmcid_key_available_on_cited_side"])
chk("matched rows with zero chunks",
    sum(1 for r in c if r["corpus_n_chunks"] == "0"), s["matched_rows_with_zero_chunks"])

# ---- 语料稳健性交叉（独立重算：只用 paper_id 集合，规则同框架但不复用 build 的计数）----
ALT = "/home/ubuntu/EYEKB_REPO/literature_db/v2.4.2_2026-09_slim/papers.jsonl"
if os.path.exists(ALT):
    alt_ids = set()
    with open(ALT, encoding="utf-8") as f:
        for line in f:
            alt_ids.add(json.loads(line)["paper_id"])
    chk("alt corpus C_hit (803 篇是否都在随件 slim 里)",
        sum(1 for p in cited if p in alt_ids), s["corpus_robustness"]["C_hit_alt"])
    chk("corpus_robustness.identical", s["corpus_robustness"]["identical"], True)
else:
    fails.append(f"alt corpus missing: {ALT}")

print(f"PASS {len(oks)} / FAIL {len(fails)}")
for x in oks:
    print("  [OK] " + x)
for x in fails:
    print("  [FAIL] " + x)
sys.exit(1 if fails else 0)