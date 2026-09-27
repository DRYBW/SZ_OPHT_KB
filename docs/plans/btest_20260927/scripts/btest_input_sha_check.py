#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTEST 输入 PRE/POST sha 台账（BTEST_PREREG_v1.0.md §8.3/§11）。
用法: python3 btest_input_sha_check.py pre|post  → ledgers/INPUT_SHA_PRE.txt / INPUT_SHA_POST.txt
post 模式逐行对账 PRE 台账，任何冻结件 sha 变化即 rc=1 退出（calllog 目录不在台账内=服务端追加白名单）。"""
import hashlib, os, sys

P = '/mnt/D/EyeKB/plans'
E = f'{P}/evalset'
FILES = [
    f'{P}/btest_20260927/BTEST_PREREG_v1.0.md',
    f'{P}/btest_20260927/BRIEF_BTEST.md',
    f'{P}/face_v21_20260926/face/EV_DIGEST_SLIM_facev21.jsonl',
    f'{P}/face_v21_20260926/scoring/FACEV21_VERDICT.json',
    f'{P}/face_v21_20260926/annotation/ANN_A_facev21.jsonl',
    f'{P}/face_v21_20260926/annotation/ANN_B_facev21.jsonl',
    f'{P}/face_v21_20260926/annotation/ANN_C_facev21.jsonl',
    f'{P}/face_v21_20260926/annotation/ANN_A_facev21_META.json',
    f'{P}/face_v21_20260926/annotation/ANN_B_facev21_META.json',
    f'{P}/face_v21_20260926/annotation/ANN_C_facev21_META.json',
    f'{P}/face_v21_20260926/FACE_PROTOCOL_V2_1_PREREG.md',
    f'{P}/face_v21_20260926/scripts/run_annotator_facev21.py',
    f'{P}/face_v21_20260926/scripts/facev21_verdict.py',
    f'{E}/annotation/ANNOT_INSTRUCTIONS.md',
    f'{E}/RUN4_TARGETS_v1.1.json',
    f'{E}/scoring/run3_M4_hotspots_v1.1.tsv',
    f'{E}/scoring/run4r_verdict.json',
    f'{E}/scoring/run3_object_B_table_v1.1.tsv',
    f'{E}/scripts/kb2_bscore_v4_truthfix_t_2ae2610d.py',
    f'{P}/run7rg_20260926/scoring/RG_VERDICT.json',
    f'{P}/rag_anno_usability_20260927/RAG_ANNOTATION_USABILITY.md',
    f'{P}/tiep_20260927/scripts/t1_revote.py',
    f'{P}/tiep_20260927/out/revote_matrix.tsv',
    f'{P}/tiep_20260927/out/tiep_counts.json',
    '/mnt/D/EyeKB/mcp_server/server.py',
    '/mnt/D/EyeKB/mcp_server/eyekb_core.py',
    '/mnt/D/EyeKB/mcp_server/calllog.py',
    '/mnt/D/EyeKB/mcp_server/softflags.py',
    '/mnt/D/EyeKB/kb/markers/markers_v6_retina_repair.json',
    '/mnt/D/EyeKB/kb/markers/markers_v6_face_increment.json',
    '/mnt/D/EyeKB/kb/literature_db/EYEKB_DB_POINTER.yaml',
    '/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md',
]


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'pre'
    out = f'{P}/btest_20260927/ledgers/INPUT_SHA_{mode.upper()}.txt'
    recs = []
    for p in FILES:
        recs.append((sha(p), p) if os.path.exists(p) else ('MISSING', p))
    with open(out, 'w') as f:
        for h, p in recs:
            f.write(f'{h}  {p}\n')
    print(f'WROTE {out} n={len(recs)} missing={sum(1 for h,_ in recs if h=="MISSING")}')
    if mode == 'post':
        pre = {}
        for l in open(f'{P}/btest_20260927/ledgers/INPUT_SHA_PRE.txt'):
            h, p = l.split(None, 1)
            pre[p.strip()] = h
        diff = [(p, pre[p], h) for h, p in recs if p in pre and h != pre[p]]
        if diff:
            print('[FAIL] 冻结件 sha 变化：')
            for p, a, b in diff:
                print(' ', p, a, '->', b)
            sys.exit(1)
        print('[PASS] POST 与 PRE 全部冻结件逐字节全等')


if __name__ == '__main__':
    main()
