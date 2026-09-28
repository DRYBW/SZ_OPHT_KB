#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 gate3 复算 (v2.5 口径, 判据逐字=gate3_coverage.py, 只扩"新增论文"与"闭集"面):
  单元 = tier_FINAL.tsv tier==A (gene, ctx_family) = 92 (分母不变=不移动球门, DECISION_1/REVIEWER_LLM 红线)
  消除 = 该 gene 被 ≥1 篇 新增论文 (v2.4 闭集 64 ∪ RA2 白名单 17) chunk 文本词边界提及,
        或该行 cited_pmids ∩ 闭集(64∪17) 且该文在 v2.4.1 库 n_chunks>0
  >=80% → PASS; 行级 232 对照同口径; 单调性断言: v2.4 已消除 67 单元全部仍消除 (证据=同一 chunk 文件 sha 复核)
前置断言: work/chunks_ra_raw.jsonl sha==43d02db66b9a3f235ff4f1b5beaafbc9ba5338aef53a4e26896649ff66a10196
输出: out/GATE3_COVERAGE_v25.json + out/GATE3_residual_units_v25.tsv
"""
import json, os, re, csv, collections, hashlib

PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
P1 = "/mnt/D/EyeKB/plans/rag_fix_20260928"
RAGGAP = "/mnt/D/EyeKB/plans/rag_gap_20260928"
V241 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.1_2026-09"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

# 0) 证据有效性复核 (REVIEWER_LLM 裁决点 3)
s = sha(f"{P1}/work/chunks_ra_raw.jsonl")
assert s == "43d02db66b9a3f235ff4f1b5beaafbc9ba5338aef53a4e26896649ff66a10196", f"v2.4 increment sha drift: {s}"

closed = set(l.strip() for l in open(f"{P1}/out/closed_set_pmids.txt") if l.strip())
closed |= set(l.strip() for l in open(f"{PLAN2}/out/closed_set_ra2_pmids.txt") if l.strip())

units = {}
with open(f"{RAGGAP}/out/tier_FINAL.tsv", encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["tier"] != "A":
            continue
        key = (r["gene"].strip().upper(), r["ctx_family"].strip())
        u = units.setdefault(key, {"rows": 0, "cited": set()})
        u["rows"] += 1
        for p in re.findall(r"\d{6,9}", r.get("cited_pmids") or ""):
            u["cited"].add(p)
print(f"A units = {len(units)} (expect 92), rows = {sum(u['rows'] for u in units.values())} (expect 232)")
assert len(units) == 92

genes = sorted({g for (g, _) in units}, key=len, reverse=True)
pat = re.compile(r"\b(" + "|".join(re.escape(g) for g in genes) + r")\b", re.I)
mentioned = set()
n_chunks_new = 0
for path in (f"{P1}/work/chunks_ra_raw.jsonl", f"{PLAN2}/work/chunks_ra2_raw.jsonl"):
    for line in open(path, encoding="utf-8"):
        d = json.loads(line)
        n_chunks_new += 1
        for m in pat.finditer(d["text"] or ""):
            mentioned.add(m.group(0).upper())
print(f"new-paper chunks scanned = {n_chunks_new} (230k? no: 9772+1281)")

nch = {}
for line in open(f"{V241}/papers.jsonl", encoding="utf-8"):
    d = json.loads(line)
    nch[str(d["paper_id"])] = int(d.get("n_chunks", 0))

res = []
for (g, ctx), u in sorted(units.items()):
    text_ok = g.upper() in mentioned
    chain_ok = any(p in closed and nch.get(p, 0) > 0 for p in u["cited"])
    res.append({"gene": g, "ctx": ctx, "rows": u["rows"],
                "eliminated_text": text_ok, "eliminated_chain": chain_ok,
                "eliminated": text_ok or chain_ok, "cited": sorted(u["cited"])})
elim_u = sum(1 for r in res if r["eliminated"])
elim_rows = sum(r["rows"] for r in res if r["eliminated"])
rate = elim_u / len(res)

# 单调性断言: v2.4 结果 67 单元不得倒退
v24 = json.load(open(f"{P1}/out/GATE3_COVERAGE_v24.json"))
assert v24["units_eliminated"] == 67
v24_elim = {(r["gene"], r["ctx"]) for r in res if r["eliminated"]}
# 用 v2.4 残差单元反向核对: 残差 25 之外必消除
v24_resid = set()
with open(f"{P1}/out/GATE3_residual_units.tsv") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        v24_resid.add((r["gene"], r["ctx"]))
regress = [(g, c) for (g, c) in [(k[0], k[1]) for k in units]
           if (g, c) not in v24_resid and not any(x["gene"] == g and x["ctx"] == c and x["eliminated"] for x in res)]
assert not regress, f"monotonicity violated: {regress}"

new_elim = [[r["gene"], r["ctx"]] for r in res if r["eliminated"] and (r["gene"], r["ctx"]) in v24_resid]
out = {"gate": ">=0.80 单元级消除 (分母92/阈值80%/判据=gate3_coverage.py 逐字, 新增面=closed64∪RA2_17)",
       "card": "t_6848d3de", "corpus": "v2.4.1",
       "units_total": len(res), "units_eliminated": elim_u,
       "unit_elimination_rate": round(rate, 4),
       "rows_total": 232, "rows_eliminated": elim_rows,
       "row_elimination_rate": round(elim_rows / 232, 4),
       "verdict": "PASS" if rate >= 0.80 else "FAIL",
       "baseline_v24": {"units_eliminated": 67, "rate": 0.7283,
                        "monotonicity_verified": True},
       "new_eliminated_ra2": new_elim,
       "by_ctx": {c: [sum(1 for r in res if r['ctx'] == c),
                       sum(1 for r in res if r['ctx'] == c and r['eliminated'])]
                  for c in sorted({r["ctx"] for r in res})},
       "new_corpus_chunks": n_chunks_new,
       "evidence_sha_check": "chunks_ra_raw.jsonl == 43d02db6... PASS"}
json.dump(out, open(f"{PLAN2}/out/GATE3_COVERAGE_v25.json", "w"), indent=1, ensure_ascii=False)
with open(f"{PLAN2}/out/GATE3_residual_units_v25.tsv", "w") as f:
    f.write("gene\tctx\trows\teliminated_text\teliminated_chain\tcited\n")
    for r in res:
        if not r["eliminated"]:
            f.write(f"{r['gene']}\t{r['ctx']}\t{r['rows']}\t0\t0\t{','.join(r['cited'])}\n")
print(json.dumps({k: out[k] for k in ("units_total", "units_eliminated",
          "unit_elimination_rate", "rows_eliminated", "row_elimination_rate", "verdict")}))
print("by_ctx units elim [tot,elim]:", out["by_ctx"])
print("RA2 newly eliminated:", out["new_eliminated_ra2"])
