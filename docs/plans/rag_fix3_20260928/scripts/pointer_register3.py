#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 指针注册: EYEKB_DB_POINTER.yaml 纯追加 v2.4.2 条目 (latest-ragfix3, frozen read-only;
MCP default=v2.0 一字不动=off 态)。纯追加不动既有行 (追加前 sha 记录, 追加后校验前缀不变, 沿 RA2 先例)。
嵌套口径沿 v2.4/v2.4.1 块先例 (文件尾追加=同构 quirk, 严格 yaml 归位随 REPOSYNC 面统一处理)。"""
import hashlib, os, json

POINTER = "/mnt/D/EyeKB/kb/literature_db/EYEKB_DB_POINTER.yaml"
V242 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09"
PLAN3 = "/mnt/D/EyeKB/plans/rag_fix3_20260928"

pre = open(POINTER, encoding="utf-8").read()
pre_sha = hashlib.sha256(pre.encode()).hexdigest()
assert "v2.4.2_2026-09" not in pre, "pointer 已含 v2.4.2 (勿重复)"
# 开卡快照绑定: 前缀必须=预注册 pre_sha (SHA_PRE_inputs_20260928.txt 行 c7f2e0f7...)
assert pre_sha == "c7f2e0f7d583cfc56ce8bfb821b0517513e81316e416b55ecd0aa30d1f6e15c7", \
    f"pointer 基线漂移: {pre_sha[:16]} != c7f2e0f7d583 (非本链预期前置态, 停车)"

stats = json.load(open(f"{V242}/build_stats.json"))
n_lines = sum(1 for _ in open(f"{V242}/papers.jsonl"))
gate3 = json.load(open(f"{PLAN3}/out/GATE3_COVERAGE_v3.json"))
verdict = gate3["verdict"]
n_new = len(gate3["new_eliminated_ra3"])

block = f"""  v2.4.2_2026-09:
    path: {V242}
    role: latest-ragfix3 (frozen read-only; = v2.4.1 全量继承零重算 + ragfix3_backup104_scan 103 篇 11,221 chunks; 卡 t_b94d0999, PI 整链授权=USER_DIRECTIVE_20260928 追加五)
    chunks: {stats['n_chunks']}
    unique_papers: {stats['n_papers']}   # papers.jsonl 行数 = {n_lines} (含历史 0-chunk ghost 15)
    manifest: {V242}/manifest.yaml
    increment_ledger: {PLAN3}/work/ra3_availability.tsv (逐 PMID 下载成败+体积+物种; 19.33MB ≤ 100MB 波次预算, 零清单外下载, 零付费墙触碰)
    scan_ledger: {PLAN3}/work/ra3_scan_ledger.tsv (104 行机械四检零 LLM=题录可核∧不在库查重∧非HRCA自引∧OA实测curl -sI; 拒1=40171795 防双计)
    decision_matrix: {PLAN3}/out/DECISION_MATRIX_RAGFIX3.md (判读矩阵预注册 sha=b3787101187ceba27bdf9357662b6be501b0c6165e1d103015eb979982d80836, 开算前落纸)
    gate_status: "③原分母92/原阈值80%/原判据复算 = {gate3['units_eliminated']}/92 = {gate3['unit_elimination_rate']:.1%} {verdict} (RA3 新兑现 {n_new} 单元=目标7中6+副产品 FAM135A/LILRB2/LMOD1, C8ORF76 诚实 MISS[两候选全文无词边界token]; 单调性核 v2.4.1 78 项零倒退; 残差 {92 - gate3['units_eliminated']} 如实登记禁回调) ①黄金41/41 off全等+top5对ragfix2基线逐字零漂移 PASS; 接线契约8/9, all_list_plus10=前两轮REVIEWER_LLM已裁'绝对计数半句过期'形态(两分句超集∧reti::10计数本轮TRUE, 非本卡) ②retina gate 8/10用例级+10/10gate级 PASS(劣化点=RPE/Astrocyte同v2.1既有形态) 见 out/GATE2_RETINA_v242.json"
    # MCP/stage3 default 未切 (v2.0 不变, 沿先例待用户拍板; 回归门经判据文件显式指向 v2.4.2 实测)
"""
post = pre + block
with open(POINTER, "w", encoding="utf-8") as f:
    f.write(post)
assert open(POINTER, encoding="utf-8").read().startswith(pre), "prefix changed?!"
print(f"pointer appended. pre_sha={pre_sha[:16]} post starts-with-pre=True")
