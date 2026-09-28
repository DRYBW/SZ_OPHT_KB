#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC3 t_09e9a4a3 · T8 — §9 语料同源筛查前置盘点（只盘点不修库；票面层排除机制沿 RULING_1）。
registry truth 血缘=view FACE_V21_ledger.tsv 注释行（study→source_pmid）；
筛查体= v2.4/v2.4.1/v2.4.2 三版语料 papers.jsonl 行（PMID∈watchlist=标题级命中）
+ 命中者补片段级复核（own-deposit GSE/指派关系，沿 o4/o7 冻结正则）；
+ 票面 v2.1 全 33 簇 lit 行 PMID × 三版语料存在性对照（覆盖面账）
+ v2.4.2 增量 103 篇 × watchlist。产 S9_SCREENING.md + out/t8_s9_hits.tsv。"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

STG = Path("/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928")
OBL = Path("/mnt/D/EyeKB/plans/obligrun_20260928")
LITDB = Path("/mnt/D/OcularKB/ocularkb/rag/literature_db")
VERS = ["v2.4_2026-09", "v2.4.1_2026-09", "v2.4.2_2026-09"]
OUT = STG / "docs/plans/repo_sync3_20260928"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "out").mkdir(exist_ok=True)

# ---- 血缘 watchlist（ledger 注释逐行解析，规则件在仓面）----
line_rows, unresolved = [], []
for ln in (OBL / "out/FACE_V21_ledger.tsv").read_text(encoding="utf-8").splitlines():
    m = re.match(r"^# (\S+) \| source_pmid=(\S+)", ln)
    if m:
        study, pmid = m.group(1), m.group(2)
        if pmid.isdigit():
            line_rows.append((study, pmid))
        elif pmid == "None":
            unresolved.append(study)
WATCH = {p: s for s, p in line_rows}
print("WATCHLIST:", WATCH, "| unresolved studies:", unresolved)

ASSIGN_RE = re.compile(r'(cluster[s]?|cell (?:population|type|state)s?|CL)\b[^.]{0,160}?\b(?:was|were|is|are)?\s*(annotated|labeled|labelled|identified|defined|classified|designated)\b', re.I)
GSE_RE = re.compile(r'GSE\d{5,8}')

hits = []
corp_counts = {}
for v in VERS:
    pp = LITDB / v / "papers.jsonl"
    papers = [json.loads(l) for l in open(pp, encoding="utf-8")]
    ids = {str(p.get("paper_id")) for p in papers}
    corp_counts[v] = {"n_papers": len(papers), "n_ids": len(ids)}
    for pid, study in WATCH.items():
        present = pid in ids
        rec = dict(version=v, pmid=pid, study=study, in_corpus=present)
        if present:
            df = pd.read_parquet(LITDB / v / "chunks.parquet", columns=["paper_id", "section", "text"])
            g = df[df["paper_id"].astype(str) == pid]
            own_dep, assign_n = set(), 0
            for _, row in g.iterrows():
                t = str(row["text"])
                for mm in re.finditer(r"deposited[\s\S]{0,200}?(GSE\d{5,8})", t, re.I):
                    own_dep.add(mm.group(1))
                if ASSIGN_RE.search(t):
                    assign_n += 1
            rec.update(n_chunks=int(len(g)), own_deposit=sorted(own_dep), assign_hits=assign_n)
        hits.append(rec)

# ---- 票面 33 簇 lit 行 × 三版存在性（覆盖面账）----
face = [json.loads(l) for l in open(OBL / "face/kb9_face_v2.1.jsonl", encoding="utf-8")]
lit_pmids = set()
for r in face:
    for ct, es in (r.get("lit") or {}).items():
        for e in es:
            lit_pmids.add(str(e.get("pmid")))
face_presence = {}
for v in VERS:
    ids = {str(p.get("paper_id")) for p in (json.loads(l) for l in open(LITDB / v / "papers.jsonl", encoding="utf-8"))}
    face_presence[v] = {"n_lit_pmids": len(lit_pmids), "present": len(lit_pmids & ids),
                        "watch_in_present": sorted(set(map(str, WATCH)) & ids)}

# ---- v2.4.2 增量 103 篇 × watchlist ----
ra3 = [json.loads(l) for l in open("/mnt/D/EyeKB/plans/rag_fix3_20260928/work/ra3_selected.jsonl", encoding="utf-8")]
ra3_ids = {str(p.get("pmid", p.get("paper_id", ""))) for p in ra3}
ra3_watch = sorted(set(map(str, WATCH)) & ra3_ids)
print("RA3 103 ∩ WATCH:", ra3_watch)

# ---- 落件 ----
rows_out = ["version\tpmid\tstudy\tin_corpus\tn_chunks\town_deposit\tassign_hits"]
for h in hits:
    rows_out.append(f"{h['version']}\t{h['pmid']}\t{h['study']}\t{h['in_corpus']}\t{h.get('n_chunks','')}\t{','.join(h.get('own_deposit',[]))}\t{h.get('assign_hits','')}")
(OUT / "out/t8_s9_hits.tsv").write_text("\n".join(rows_out) + "\n", encoding="utf-8")
json.dump({"corp_counts": corp_counts, "face_presence": face_presence,
           "watchlist": WATCH, "unresolved_studies": unresolved,
           "ra3_n": len(ra3), "ra3_watch_hits": ra3_watch},
          open(OUT / "out/t8_s9_stats.json", "w"), ensure_ascii=False, indent=1)
print("T8 DONE. hits rows:", len(hits))
