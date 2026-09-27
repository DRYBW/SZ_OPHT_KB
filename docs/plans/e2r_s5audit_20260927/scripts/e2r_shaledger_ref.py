#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2 sha 台账生成器：PRE=跑数前，POST=收口时。用法: e2_shaledger.py PRE|POST <outfile>
对全部输入件 sha256；本卡对输入件零写入（红线①），POST 与 PRE 全等即零触碰实证。"""
import hashlib, sys, datetime

INPUTS = [
    # 任务书与上游裁决/指令
    '/mnt/D/EyeKB/plans/e2_decontam_20260926/BRIEF_E2.md',
    '/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260926_redline_rewrite.md',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/E1_VERDICT.md',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/E1_PREREG_v1.0.md',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/e1_class_map.json',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/e1_leak_lineage.json',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/data/e1_scores_ON.tsv',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/data/e1_scores_OFF.tsv',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/data/e1_leak_table.tsv',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/out/e1_truth_region_table.tsv',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/out/e1_sensitivity_grid.tsv',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/out/e1_metrics.json',
    # 面板派生证据（只读）
    '/mnt/D/EyeKB/kb/markers/markers_v4.1_clean.json',
    '/mnt/D/EyeKB/kb/markers/markers_membrane_v1.json',
    '/mnt/D/EyeKB/kb/markers/markers_v5_retina_interneuron.json',
    '/mnt/D/EyeKB/kb/markers/markers_v6_retina_repair.json',
    '/mnt/D/EyeKB/kb/markers/markers_v6_face_increment.json',
    '/mnt/D/EyeKB/kb/markers/markers_v6_lacrimal_increment.json',
    '/mnt/D/EyeKB/kb/markers/markers_cl_alignment_v1.json',
    # 真值与基线（冻结件）
    '/mnt/D/EyeKB/plans/evalset/digest/EV_DIGEST_SLIM_v3full.jsonl',
    '/mnt/D/EyeKB/plans/evalset/scoring/run3_object_B_table_v1.1.tsv',
    '/mnt/D/EyeKB/plans/evalset/scoring/run5_truth_table.tsv',
    '/mnt/D/EyeKB/plans/face_v21_20260926/out/per_cluster_flip_table_facev21.tsv',
    # 语料成员判定（lit 通道审计输入）
    '/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09/papers.jsonl',
    # 生产代码路径（本卡禁调用；sha 以证零改动——只读也算触碰面登记）
    '/mnt/D/EyeKB/mcp_server/eyekb_core.py',
]

def main():
    mode, out = sys.argv[1], sys.argv[2]
    assert mode in ('PRE', 'POST')
    lines = []
    for p in INPUTS:
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        lines.append(f'{h}  {p}')
    with open(out, 'w') as f:
        f.write('\n'.join(lines) + f'\n# {mode} ledger ran {datetime.datetime.now()} '
                f'({len(INPUTS)} inputs)\n')
    print(f'{mode} ledger: {len(INPUTS)} inputs -> {out}')

if __name__ == '__main__':
    main()
