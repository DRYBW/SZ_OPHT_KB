#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W4 v1.2: abstract 级 dev_stage 信号 (任务书'来源=标题/摘要正则'补齐)。

从 v2.2 chunks.parquet 只读 section=='Abstract' 的 chunk (每 paper 取最长一条),
跑与 kb3_dev_stage_tag.FETAL_RE/ADULT_RE 同一词表 (单一真源, import), 产出 per-paper
命中列表。产物: plans/kb3_evidence/abstract_dev_stage_hits_20260924.json
消费: kb3_dev_stage_tag.py v1.2 合并 title+abstract → dev_stage_final。
"""
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

sys.path.insert(0, "/mnt/D/EyeKB/scripts/rag_meta")
from kb3_dev_stage_tag import FETAL_RE, ADULT_RE  # noqa: E402  同一词表

CHUNKS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.2_2026-09/chunks.parquet"
OUT = Path("/mnt/D/EyeKB/plans/kb3_evidence/abstract_dev_stage_hits_20260924.json")

best = {}  # paper_id -> 最长 abstract 文本
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
