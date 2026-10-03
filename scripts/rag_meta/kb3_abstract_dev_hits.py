#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W4 v1.2: abstract-level dev_stage signal (closes the task-brief requirement
"source = title/abstract regex").

Reads only section=='Abstract' chunks from v2.2 chunks.parquet (longest one per paper),
runs the same vocabulary as kb3_dev_stage_tag.FETAL_RE/ADULT_RE (single source of truth,
imported), and produces a per-paper hit list. Output:
plans/kb3_evidence/abstract_dev_stage_hits_20260924.json
Consumed by: kb3_dev_stage_tag.py v1.2, which merges title+abstract into dev_stage_final.
"""
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, "/mnt/D/EyeKB/scripts/rag_meta")
from kb3_dev_stage_tag import FETAL_RE, ADULT_RE  # noqa: E402  same vocabulary

CHUNKS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.2_2026-09/chunks.parquet"
OUT = Path("/mnt/D/EyeKB/plans/kb3_evidence/abstract_dev_stage_hits_20260924.json")

best = {}  # paper_id -> longest abstract text
ph = pq.ParquetFile(CHUNKS)
for b in ph.iter_batches(columns=["paper_id", "section", "text"], batch_size=8192):
    for pid, sec, txt in zip(b.column("paper_id").to_pylist(),
                             b.column("section").to_pylist(),
                             b.column("text").to_pylist()):
        if sec == "Abstract" and txt:
            if pid not in best or len(txt) > len(best[pid]):
                best[pid] = txt


def hits(rx, txt):
    out = set()
    for m in rx.finditer(txt):
        g = m.group(1) or m.group(0)
        out.add(g.lower())
    return sorted(out)


res = {str(pid): {"fetal_hits": hits(FETAL_RE, txt), "adult_hits": hits(ADULT_RE, txt),
                  "n_chars": len(txt)} for pid, txt in best.items()}
OUT.write_text(json.dumps({"schema": "eyekb-abstract-devhits/1.0", "card": "t_5425a7ca",
                           "papers": len(res), "hits": res}, ensure_ascii=False),
               encoding="utf-8")
n_f = sum(1 for v in res.values() if v["fetal_hits"])
n_a = sum(1 for v in res.values() if v["adult_hits"])
n_c = sum(1 for v in res.values() if v["fetal_hits"] and v["adult_hits"])
print(f"abstracts={len(res)} fetal={n_f} adult={n_a} conflict={n_c} -> {OUT}")
