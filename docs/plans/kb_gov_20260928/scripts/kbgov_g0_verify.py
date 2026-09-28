#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kbgov_g0_verify.py — G0 复刻验证门（PREREG §2）。
对 calls_2026-09-26/27.jsonl 中 tool=query_marker ∧ resp.mode=genes ∧ args.library=all
∧ act_v6_on=true 的行，用实验侧复刻件重算 ranking，与留痕 ranking_classes_top（top20）
及 n_ranking 对账。错行>0 → exit 2（fail-closed，全线中止）。
注：09-26 行按同条件扫描（tag 各异，activation/obs 流量同样构成验证样本，如实登记 tag 分布）。"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbgov_replica import load_markers, rank_genes

OUT = "/mnt/D/EyeKB/plans/kb_gov_20260928"
mk, ow = load_markers()

rows_checked = 0
mismatch = []
tags = {}
skip = {}
for day in ("2026-09-26", "2026-09-27"):
    p = f"/mnt/D/EyeKB/logs/mcp_trace/calls_{day}.jsonl"
    if not os.path.isfile(p):
        continue
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                skip['unparse'] = skip.get('unparse', 0) + 1
                continue
            if d.get("tool") != "query_marker":
                continue
            if not d.get("act_v6_on"):
                skip['act_v6_off'] = skip.get('act_v6_off', 0) + 1
                continue
            args = d.get("args") or {}
            if (args.get("library") or "all") != "all":
                skip['library_specific'] = skip.get('library_specific', 0) + 1
                continue
            resp = d.get("resp") or {}
            if resp.get("mode") != "genes":
                skip['not_genes_mode'] = skip.get('not_genes_mode', 0) + 1
                continue
            genes = args.get("genes") or []
            if isinstance(genes, str):
                genes = genes.replace(",", " ").split()
            if not genes:
                skip['empty_genes'] = skip.get('empty_genes', 0) + 1
                continue
            tag = d.get("tag") or ""
            tags[tag] = tags.get(tag, 0) + 1
            r, gl = rank_genes(genes, mk, ow)
            got_classes = [c for c, n, s in r]
            got_n = len(r)
            want = resp.get("ranking_classes_top") or []
            want_n = resp.get("n_ranking")
            bad = []
            if got_n != want_n:
                bad.append(f"n_ranking {got_n}!={want_n}")
            if got_classes[:20] != want[:20]:
                bad.append(f"order replica={got_classes[:20]} logged={want[:20]}")
            rows_checked += 1
            if bad:
                mismatch.append({"day": day, "ts": d.get("ts"), "tag": tag,
                                 "genes_n": len(gl), "why": "; ".join(bad),
                                 "genes_first10": genes[:10]})
with open(f"{OUT}/ledgers/kbgov_replica_vs_calllog.tsv", "w", encoding="utf-8") as f:
    f.write("rows_checked\tmismatch_n\ttags\tskipped\n")
    f.write(f"{rows_checked}\t{len(mismatch)}\t{json.dumps(tags, ensure_ascii=False)}\t{json.dumps(skip, ensure_ascii=False)}\n")
    for m in mismatch[:200]:
        f.write(json.dumps(m, ensure_ascii=False) + "\n")
print(f"rows_checked={rows_checked} mismatch={len(mismatch)}")
print("tags:", json.dumps(tags, ensure_ascii=False))
print("skipped:", json.dumps(skip, ensure_ascii=False))
for m in mismatch[:10]:
    print("MISMATCH:", json.dumps(m, ensure_ascii=False)[:400])
if mismatch:
    sys.exit(2)
print("G0 PASS — 复刻件与服务端留痕逐行序零差异")
