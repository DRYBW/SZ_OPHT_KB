#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX2 指针注册: EYEKB_DB_POINTER.yaml 纯追加 v2.4.1 条目 (latest-ragfix2, frozen read-only;
MCP default=v2.0 一字不动=off 态)。纯追加不动既有行 (追加前 sha 记录, 追加后校验前缀不变)。
嵌套口径沿 v2.4 块先例 (文件尾追加=同构 quirk, 严格 yaml 归位随 REPOSYNC 面统一处理)。"""
import hashlib, os, json

POINTER = "/mnt/D/EyeKB/kb/literature_db/EYEKB_DB_POINTER.yaml"
V241 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.1_2026-09"
PLAN2 = "/mnt/D/EyeKB/plans/rag_fix2_v25_20260928"

pre = open(POINTER, encoding="utf-8").read()
pre_sha = hashlib.sha256(pre.encode()).hexdigest()
assert "v2.4.1_2026-09" not in pre, "pointer 已含 v2.4.1 (勿重复)"

stats = json.load(open(f"{V241}/build_stats.json"))
n_lines = sum(1 for _ in open(f"{V241}/papers.jsonl"))
gate3 = json.load(open(f"{PLAN2}/out/GATE3_COVERAGE_v25.json"))
verdict = gate3["verdict"]

block = f"""  v2.4.1_2026-09:
    path: {V241}
    role: latest-ragfix2 (frozen read-only; = v2.4 全量继承零重算 + ragfix2_v25_whitelist 17 篇 1,281 chunks; 卡 t_6848d3de D21)
    chunks: {stats['n_chunks']}
    unique_papers: {stats['n_papers']}   # papers.jsonl 行数 = {n_lines} (含历史 0-chunk ghost 15)
    manifest: {V241}/manifest.yaml
    increment_ledger: {PLAN2}/work/ra2_availability.tsv (逐 PMID C2 复核+成败+体积; 2.34MB ≤ 6MB 上限)
    whitelist_ledger: {PLAN2}/out/RA2_WHITELIST.tsv (三条件题录核验=断言词/PMID可核/非HRCA自引∧不在库防重蹈)
    token_verification: {PLAN2}/out/RA2_token_verification.tsv (词边界 token 终裁; CALD1 替补顶岗)
    gate_status: "③原分母92/原阈值80%/原判据复算 = {gate3['units_eliminated']}/92 = {gate3['unit_elimination_rate']:.1%} {verdict} (RA2 新兑现 {len(gate3['new_eliminated_ra2'])} 单元含 CPNE5 副产品, 单调性核 v2.4 67 项零倒退; 残差 {92 - gate3['units_eliminated']} = 7 备选104覆盖单元(另案) + 6 诚实none(ATP8B4/FAM135A/FBXL7/LMOD1/LRRTM3/SHISA6) + LILRB2 撤证设计) ①黄金41/41 off全等 PASS (top5 与前轮逐字零漂移; all_list_plus10 失效仅绝对计数半句=前置轮旧快照期望过期, 两分句复证 TRUE, 非本卡) ②retina gate 8/10 用例级+10/10 gate 级 PASS (同 v2.1 形态)"
    # MCP/stage3 default 未切 (v2.0 不变, 沿先例待用户拍板; 回归门经 --db-dir 显式指向 v2.4.1 实测)
"""
post = pre + block
with open(POINTER, "w", encoding="utf-8") as f:
    f.write(post)
assert open(POINTER, encoding="utf-8").read().startswith(pre), "prefix changed?!"
print(f"pointer appended. pre_sha={pre_sha[:16]} post starts-with-pre=True")
