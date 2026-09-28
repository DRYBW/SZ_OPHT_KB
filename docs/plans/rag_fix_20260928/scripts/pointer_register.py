#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_d0bea5a6 指针注册: EYEKB_DB_POINTER.yaml 追加 v2.4 条目 (latest-raggap, frozen read-only;
MCP default=v2.0 一字不动 = off 态)。纯追加, 不动既有行 (追加前 sha 记录, 追加后校验前缀不变)。"""
import hashlib, os, json

POINTER = "/mnt/D/EyeKB/kb/literature_db/EYEKB_DB_POINTER.yaml"
V24 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09"
PLAN = "/mnt/D/EyeKB/plans/rag_fix_20260928"

pre = open(POINTER, encoding="utf-8").read()
pre_sha = hashlib.sha256(pre.encode()).hexdigest()
assert "v2.4_2026-09" not in pre, "pointer 已含 v2.4 (勿重复)"

stats = json.load(open(f"{V24}/build_stats.json"))
n_lines = sum(1 for _ in open(f"{V24}/papers.jsonl"))

block = f"""  v2.4_2026-09:
    path: {V24}
    role: latest-raggap (frozen read-only; = v2.3 全量继承零重算 + raggap_tier_a_eyekb 64 篇 9,772 chunks; 卡 t_d0bea5a6 D19)
    chunks: {stats['n_chunks']}
    unique_papers: {stats['n_papers']}   # papers.jsonl 行数 = {n_lines} (含历史 0-chunk ghost)
    manifest: {V24}/manifest.yaml
    increment_ledger: {PLAN}/work/ra_availability.tsv (逐 PMID 成败+体积; 13.9MB << 85MB 预算)
    errata: /mnt/D/EyeKB/kb/markers/_raggap_errata_v1.json (LILRB2 撤证 + sample20 误引登记, INERT)
    c_sidecars: /mnt/D/EyeKB/kb/markers/_raggap_c_linkbackfill_v1.json (830 行链回填, INERT 默认 OFF)
    # MCP/stage3 default 未切 (v2.0 不变, 沿先例待用户拍板; 回归门经 --db-dir 显式指向 v2.4 实测)
"""
post = pre + block
with open(POINTER, "w", encoding="utf-8") as f:
    f.write(post)
assert open(POINTER, encoding="utf-8").read().startswith(pre), "prefix changed?!"
print(f"pointer appended. pre_sha={pre_sha[:16]} post starts-with-pre=True")
