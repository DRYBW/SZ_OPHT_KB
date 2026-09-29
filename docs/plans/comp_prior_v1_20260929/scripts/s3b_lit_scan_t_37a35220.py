#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3b_lit_scan_t_37a35220.py — OB-1 重扫（修正句切分把 "3.8%" 小数点截断的假阴性）
整 chunk 窗口匹配: term 与 数字% 双向邻近(<=180字符, 允许内部句点), 再人工三过滤。
"""
import pandas as pd, re, json, pathlib
OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
df = pd.read_parquet("/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/chunks.parquet",
                     columns=["paper_id", "pmcid", "title", "species", "tissue", "tissue_labels", "text"])
PCT = r"(?:\d+(?:\.\d+)?\s*(?:%|percent)|proportion|percentage|fraction)"
hits = []
for term in ["goblet", "pericyte"]:
    T = re.escape(term)
    m1 = re.compile(T + r"[^%]{0,180}?\d+(?:\.\d+)?\s?%", re.I)
    m2 = re.compile(r"\d+(?:\.\d+)?\s?%[^.]{0,40}?" + T, re.I)
    m3 = re.compile(T + r"[^.]{0,160}?(?:proportion|percentage|fraction)", re.I)
    sub = df[df["text"].str.contains(term, case=False, na=False)]
    for _, r in sub.iterrows():
        t = str(r["text"])
        for mo in list(m1.finditer(t)) + list(m2.finditer(t)) + list(m3.finditer(t)):
            s = max(0, mo.start() - 40); e = min(len(t), mo.end() + 40)
            hits.append(dict(term=term, paper_id=r["paper_id"], pmcid=r["pmcid"],
                             species=str(r["species"]), tissue=str(r["tissue"]),
                             window=t[s:e].replace("\n", " ")))
h = pd.DataFrame(hits).drop_duplicates()
OSCTX = re.compile(r"conjunctiv|corneal|cornea\b|limbal|ocular surface|lacrimal|palpebra", re.I)
h["os_ctx"] = h["window"].str.contains(OSCTX)
h.to_csv(OUT / "ob1_lit_candidates.tsv", sep="\t", index=False)
print("total windows:", len(h), " os_ctx:", int(h["os_ctx"].sum()))
for term in ["goblet", "pericyte"]:
    sel = h[(h["term"] == term) & h["os_ctx"]]
    print(f"#### {term} os-context windows: {len(sel)}")
    for _, r in sel.head(30).iterrows():
        print(" -", r["paper_id"], "|", r["species"], "|", r["window"][:200])
