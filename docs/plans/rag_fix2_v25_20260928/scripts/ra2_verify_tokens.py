#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 stage ra2_verify_tokens: chunks_ra2_raw.jsonl 词边界 token 终裁
判据逐字=gate3 text 路口径 (re.compile(r'\\b'+G+'\\b', re.I) finditer over chunk texts)。
每基因: primary_text_hit / backup_text_hit / chain_hit(cited∈白名单且该文有 chunks) → eliminated。
输出 out/RA2_token_verification.tsv + 预测新消除数。
"""
import json, re, csv
PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"
P1 = "/mnt/D/EyeKB/plans/rag_fix_20260928"
GENES = ["ATP8B4","CALD1","CDH8","CST1","CST4","FAM135A","FBXL7","FCER1G","GPR143",
         "GRM5","LMOD1","LRRTM3","MUC7","PTPRK","SAMSN1","SHISA6"]
by_paper = {}
for line in open(f"{PLAN2}/work/chunks_ra2_raw.jsonl", encoding="utf-8"):
    d = json.loads(line)
    by_paper.setdefault(d["paper_id"], []).append(d["text"] or "")
wl = list(csv.DictReader(open(f"{PLAN2}/out/RA2_WHITELIST.tsv"), delimiter="\t"))
prim, back = {}, {}
for w in wl:
    if not w["pmid"]:
        continue
    (prim if w["slot"] == "primary" else back)[w["gene"]] = w["pmid"]
cited = {}
for r in csv.DictReader(open(f"{P1}/out/GATE3_residual_units.tsv"), delimiter="\t"):
    cited[r["gene"]] = [p for p in (r["cited"] or "").split(",") if p]

def hits(pm, rx):
    if not pm:
        return 0, 0
    ts = by_paper.get(pm, [])
    n = sum(len(rx.findall(t)) for t in ts)
    nch = sum(1 for t in ts if rx.search(t))
    return n, nch

rows = []
for g in GENES:
    rx = re.compile(r"\b" + g + r"\b", re.I)
    p, b = prim.get(g, ""), back.get(g, "")
    np_, cp = hits(p, rx)
    nb_, cb = hits(b, rx)
    chain_pms = [c for c in cited.get(g, []) if c in (p, b) and by_paper.get(c)]
    elim = bool(np_ or nb_ or chain_pms)
    route = "chain" if chain_pms and not np_ else ("text_primary" if np_ else
            ("text_backup" if nb_ else ("chain" if chain_pms else "NONE_honest")))
    rows.append(dict(gene=g, ctx=(wl[0] and next((w["ctx"] for w in wl if w["gene"] == g), "")),
                     primary=p, primary_tok_hits=np_, primary_chunks_with_tok=cp,
                     backup=b, backup_tok_hits=nb_, backup_chunks_with_tok=cb,
                     chain_hit=",".join(chain_pms), route=route, eliminated=int(elim)))
    print(f"{g:8s} primary={np_} backup={nb_} chain={len(chain_pms)} -> {route:12s} elim={elim}")
with open(f"{PLAN2}/out/RA2_token_verification.tsv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
    wr.writeheader(); wr.writerows(rows)
el = sum(r["eliminated"] for r in rows)
print(f"\nprojected new eliminations: {el}/16 -> gate3 predicted {(67+el)}/92 = {(67+el)/92*100:.1f}%")
