#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 gate3 复算 (判据逐字=gate3_coverage_v25.py, 只扩"新增论文"与"闭集"面, DECISION_MATRIX R5):
  单元 = tier_FINAL.tsv tier==A (gene, ctx_family) = 92 (分母不变=不移动球门)
  消除 = 该 gene 被 ≥1 篇 新增论文 (closed64 ∪ RA2_17 ∪ RA3_准入103) chunk 文本词边界提及,
        或该行 cited_pmids ∩ 闭集 且该文在 v2.4.2 库 n_chunks>0
  >=80% → PASS; 行级 232 对照同口径
  证据有效性复核断言: chunks_ra_raw sha==43d02db6... ∧ chunks_ra2_raw sha==ab941a8a... (预注册 R5)
  单调性断言: v2.4.1 已消除 78 单元 (92 − residual_v25 14) 全部仍消除
  副产品/弱相关兑现 provenance 逐单元登记 (兑现论文 PMID 集 + 目标面/副产品标注)
输出: out/GATE3_COVERAGE_v3.json + out/GATE3_residual_units_v3.tsv + out/GATE3_new_elim_provenance_v3.tsv
"""
import json, os, re, csv, collections, hashlib

PLAN3 = "/mnt/D/EyeKB/plans/rag_fix3_20260928"
P1 = "/mnt/D/EyeKB/plans/rag_fix_20260928"
PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
RAGGAP = "/mnt/D/EyeKB/plans/rag_gap_20260928"
V242 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

# 0) 证据有效性复核 (DECISION_MATRIX R5 预注册 sha)
s1 = sha(f"{P1}/work/chunks_ra_raw.jsonl")
assert s1 == "43d02db66b9a3f235ff4f1b5beaafbc9ba5338aef53a4e26896649ff66a10196", f"v2.4 increment sha drift: {s1}"
s2 = sha(f"{PLAN2}/work/chunks_ra2_raw.jsonl")
assert s2 == "ab941a8ae3b00b29bc80bbdd359e6dad70b0d7a0eaa1122a9f0d6b3ab9962a53", f"v2.4.1 increment sha drift: {s2}"

closed = set(l.strip() for l in open(f"{P1}/out/closed_set_pmids.txt") if l.strip())
closed |= set(l.strip() for l in open(f"{PLAN2}/out/closed_set_ra2_pmids.txt") if l.strip())
ra3 = set(l.strip() for l in open(f"{PLAN3}/out/closed_set_ra3_pmids.txt") if l.strip())
closed |= ra3

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
prov = collections.defaultdict(set)   # gene -> {pmid}
n_chunks_new = 0
for path in (f"{P1}/work/chunks_ra_raw.jsonl", f"{PLAN2}/work/chunks_ra2_raw.jsonl",
             f"{PLAN3}/work/chunks_ra3_raw.jsonl"):
    for line in open(path, encoding="utf-8"):
        d = json.loads(line)
        n_chunks_new += 1
        for m in pat.finditer(d["text"] or ""):
            g = m.group(0).upper()
            mentioned.add(g)
            prov[g].add(str(d["paper_id"]))
print(f"new-paper chunks scanned = {n_chunks_new} (9772+1281+11221)")

nch = {}
for line in open(f"{V242}/papers.jsonl", encoding="utf-8"):
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

# 单调性断言: v2.4.1 残差 14 之外必消除
v25 = json.load(open(f"{PLAN2}/out/GATE3_COVERAGE_v25.json"))
assert v25["units_eliminated"] == 78
v25_resid = set()
with open(f"{PLAN2}/out/GATE3_residual_units_v25.tsv") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        v25_resid.add((r["gene"], r["ctx"]))
assert len(v25_resid) == 14, f"v25 residual set drift: {len(v25_resid)}"
now_elim = {(r["gene"], r["ctx"]) for r in res if r["eliminated"]}
regress = [(g, c) for (g, c) in units if (g, c) not in v25_resid and (g, c) not in now_elim]
assert not regress, f"monotonicity violated: {regress}"

new_elim = [[r["gene"], r["ctx"]] for r in res if r["eliminated"] and (r["gene"], r["ctx"]) in v25_resid]
# provenance: 新兑现单元的 RA3 兑现论文 + 目标面/副产品标注
SEVEN = {("C8ORF76","retina"),("COL19A1","retina"),("FAM107B","retina"),("SLC24A3","retina"),
         ("SSR4","membrane"),("XCR1","membrane"),("ZNF804B","retina")}
benefit = {}
for row in csv.reader(open(f"{PLAN3}/work/backup104_raw.tsv"), delimiter="\t"):
    if len(row) > 4 and row[1].isdigit():
        benefit[row[1]] = row[4]
with open(f"{PLAN3}/out/GATE3_new_elim_provenance_v3.tsv", "w") as f:
    f.write("gene\tctx\tface\tra3_realizing_pmids\tra2_carryover\tin_104_benefit_table\n")
    for (g, c) in [tuple(x) for x in new_elim]:
        ra3_hits = sorted(prov.get(g, set()) & ra3)
        ra2_hits = sorted(prov.get(g, set()) & set(l.strip() for l in open(f"{PLAN2}/out/closed_set_ra2_pmids.txt") if l.strip()))
        in_table = ";".join(sorted({benefit[p] for p in ra3_hits if p in benefit})) or "-"
        face = "target7" if (g, c) in SEVEN else "byproduct"
        f.write(f"{g}\t{c}\t{face}\t{','.join(ra3_hits) or '-'}\t{','.join(ra2_hits) or '-'}\t{in_table}\n")

out = {"gate": ">=0.80 单元级消除 (分母92/阈值80%/判据=gate3_coverage.py 逐字, 新增面=closed64∪RA2_17∪RA3_103)",
       "card": "t_b94d0999", "corpus": "v2.4.2",
       "units_total": len(res), "units_eliminated": elim_u,
       "unit_elimination_rate": round(rate, 4),
       "rows_total": 232, "rows_eliminated": elim_rows,
       "row_elimination_rate": round(elim_rows / 232, 4),
       "verdict": "PASS" if rate >= 0.80 else "FAIL",
       "baseline_v241": {"units_eliminated": 78, "rate": 0.8478, "monotonicity_verified": True},
       "new_eliminated_ra3": new_elim,
       "by_ctx": {c: [sum(1 for r in res if r['ctx'] == c),
                       sum(1 for r in res if r['ctx'] == c and r['eliminated'])]
                  for c in sorted({r["ctx"] for r in res})},
       "new_corpus_chunks": n_chunks_new,
       "evidence_sha_check": "chunks_ra_raw==43d02db6... PASS; chunks_ra2_raw==ab941a8a... PASS"}
json.dump(out, open(f"{PLAN3}/out/GATE3_COVERAGE_v3.json", "w"), indent=1, ensure_ascii=False)
with open(f"{PLAN3}/out/GATE3_residual_units_v3.tsv", "w") as f:
    f.write("gene\tctx\trows\teliminated_text\teliminated_chain\tcited\n")
    for r in res:
        if not r["eliminated"]:
            f.write(f"{r['gene']}\t{r['ctx']}\t{r['rows']}\t0\t0\t{','.join(r['cited'])}\n")
print(json.dumps({k: out[k] for k in ("units_total", "units_eliminated",
          "unit_elimination_rate", "rows_eliminated", "row_elimination_rate", "verdict")}))
print("by_ctx units elim [tot,elim]:", out["by_ctx"])
print("RA3 newly eliminated:", out["new_eliminated_ra3"])
