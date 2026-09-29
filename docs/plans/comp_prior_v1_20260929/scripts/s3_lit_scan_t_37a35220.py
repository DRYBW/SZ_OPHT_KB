#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3_lit_scan_t_37a35220.py — OB-1: 盘上 RAG chunks 全量扫 goblet/pericyte 组成比例句
零外网。判据(预注册): 人 + 正常成人眼表/结膜语境 + 直接报告组成比例(% of cells 类) 三过滤。
"""
import pandas as pd, json, re, pathlib
OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
df = pd.read_parquet("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/chunks.parquet")
print("chunks:", df.shape, list(df.columns))
txtcol = [c for c in df.columns if df[c].dtype == object and df[c].astype(str).str.len().mean() > 100][0]
idcol = [c for c in df.columns if "paper" in c.lower() or "pmid" in c.lower() or "doc" in c.lower()]
hits = []
for term in ["goblet", "pericyte"]:
    m = df[txtcol].str.contains(term, case=False, na=False)
    sub = df[m]
    print(term, "chunks:", len(sub))
    Q = re.compile(r"(\d+(\.\d+)?\s*%|percentage|proportion|fraction)\s*(of|among)?[^.]{0,80}" + term, re.I)
    Q2 = re.compile(term + r"[^.]{0,120}?(%|percentage|proportion|fraction)", re.I)
    for _, r in sub.iterrows():
        t = str(r[txtcol])
        for sent in re.split(r"(?<=[.;])\s+", t):
            if term in sent.lower() and (Q.search(sent) or Q2.search(sent)):
                hits.append(dict(term=term,
                                 pmid=str(r[idcol[0]]) if idcol else "",
                                 sent=sent.strip()[:400]))
pd.DataFrame(hits).to_csv(OUT / "ob1_lit_candidates.tsv", sep="\t", index=False)
print("candidate sentences:", len(hits))
# 人眼表语境初筛标记
OSCTX = re.compile(r"conjunctiv|corneal|cornea|limbal|ocular surface|lacrimal", re.I)
HUMAN = re.compile(r"\bhuman\b|patients|donor|resection|impression", re.I)
for h in hits:
    h["os_ctx"] = bool(OSCTX.search(h["sent"])); h["human_ctx"] = bool(HUMAN.search(h["sent"]))
print(json.dumps([h for h in hits if h["os_ctx"] and h["term"] == "goblet"], ensure_ascii=False)[:1500])
print("----pericyte os_ctx----")
print(json.dumps([h for h in hits if h["os_ctx"] and h["term"] == "pericyte"], ensure_ascii=False)[:2000])
print("done s3")
