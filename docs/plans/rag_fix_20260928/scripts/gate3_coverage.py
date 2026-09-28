#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 gate3: A 档 92 基因覆盖复扫对照 (缺口感应消除 >=80%)
口径 (与 RAGGAP 预注册判据同源, 只把语料面从 v2.1 换成 v2.4):
  单元 = tier_FINAL.tsv tier==A 行去重 (gene, ctx_family) = A_summary.by_ctx 合计 92 (face3+kb93+lacrimal7+membrane21+retina58)
  消除 = 该 gene 被 ≥1 篇 v2.4 新增论文 (64 闭集) chunk 文本词边界提及 (RAGGAP S2 token 匹配口径),
        或该行的 cited_pmids 现已在 v2.4 库且有 chunk (S1 chain_covered 口径, R1 引用链 7 篇走此路)
  分母 92, 消除数/92 >= 0.80 → PASS; 同时报行级 (232 行) 消除率作对照
输出: out/GATE3_COVERAGE_v24.json + out/GATE3_residual_units.tsv
"""
import json, os, re, csv, collections

PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"
RAGGAP = "/mnt/D/EyeKB/plans/rag_gap_20260928"
V24 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09"

closed = set(l.strip() for l in open(f"{PLAN}/out/closed_set_pmids.txt") if l.strip())

# 1) A 档单元 (gene, ctx_family) + 行级 cited chains
units = {}   # (gene, ctx) -> {"rows":n, "cited":set}
rowctx = collections.Counter()
with open(f"{RAGGAP}/out/tier_FINAL.tsv", encoding="utf-8") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for r in rd:
        if r["tier"] != "A":
            continue
        key = (r["gene"].strip().upper(), r["ctx_family"].strip())
        u = units.setdefault(key, {"rows": 0, "cited": set()})
        u["rows"] += 1
        for p in re.findall(r"\d{6,9}", r.get("cited_pmids") or ""):
            u["cited"].add(p)
print(f"A units = {len(units)} (expect 92), rows = {sum(u['rows'] for u in units.values())} (expect 232)")
assert len(units) == 92

# 2) v2.4 新增论文 chunk 文本 gene 提及 (词边界, 大小写不敏感 — RAGGAP s3 口径)
genes = sorted({g for (g, _) in units}, key=len, reverse=True)
pat = re.compile(r"\b(" + "|".join(re.escape(g) for g in genes) + r")\b", re.I)
mentioned = set()
n_chunks_new = 0
with open(f"{PLAN}/work/chunks_ra_raw.jsonl", encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        n_chunks_new += 1
        for m in pat.finditer(d["text"] or ""):
            mentioned.add(m.group(0).upper())
print(f"new-paper chunks scanned = {n_chunks_new}; distinct A-genes mentioned = {len(mentioned & set(g.upper() for g in genes))}")

# 3) 链覆盖: cited ∩ closed 且 n_chunks>0 (v2.4 papers.jsonl)
nch = {}
for line in open(f"{V24}/papers.jsonl", encoding="utf-8"):
    d = json.loads(line)
    nch[str(d["paper_id"])] = int(d.get("n_chunks", 0))

res = []
for (g, ctx), u in sorted(units.items()):
    text_ok = g.upper() in mentioned
    chain_ok = any(p in closed and nch.get(p, 0) > 0 for p in u["cited"])
    res.append({"gene": g, "ctx": ctx, "rows": u["rows"],
                "eliminated_text": text_ok, "eliminated_chain": chain_ok,
                "eliminated": text_ok or chain_ok,
                "cited": sorted(u["cited"])})
elim_u = sum(1 for r in res if r["eliminated"])
elim_rows = sum(r["rows"] for r in res if r["eliminated"])
rate = elim_u / len(res)
out = {"gate": ">=0.80 单元级消除", "units_total": len(res), "units_eliminated": elim_u,
       "unit_elimination_rate": round(rate, 4),
       "rows_total": 232, "rows_eliminated": elim_rows,
       "row_elimination_rate": round(elim_rows / 232, 4),
       "verdict": "PASS" if rate >= 0.80 else "FAIL",
       "by_ctx": {c: [sum(1 for r in res if r['ctx'] == c),
                       sum(1 for r in res if r['ctx'] == c and r['eliminated'])]
                  for c in sorted({r["ctx"] for r in res})},
       "new_corpus_chunks": n_chunks_new}
json.dump(out, open(f"{PLAN}/out/GATE3_COVERAGE_v24.json", "w"), indent=1, ensure_ascii=False)
with open(f"{PLAN}/out/GATE3_residual_units.tsv", "w") as f:
    f.write("gene\tctx\trows\teliminated_text\teliminated_chain\tcited\n")
    for r in res:
        if not r["eliminated"]:
            f.write(f"{r['gene']}\t{r['ctx']}\t{r['rows']}\t0\t0\t{','.join(r['cited'])}\n")
print(json.dumps({k: out[k] for k in ("units_total", "units_eliminated",
                "unit_elimination_rate", "rows_eliminated", "row_elimination_rate", "verdict")}))
print("by_ctx units elim [tot,elim]:", out["by_ctx"])
