#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2R-4 复刻验收闸：本卡 raw/S1/S5 三张 scores TSV 必须与 E2 冻结件逐行零差异。
不过闸禁进 metrics。产物: out/e2r_verify_replica.tsv"""
import sys

ROOT = '/mnt/D/EyeKB/plans/e2r_s5audit_20260927'
E2 = '/mnt/D/EyeKB/plans/e2_decontam_20260926'

PAIRS = [('raw', 'e2r_scores_raw_replica.tsv', 'e2_scores_raw_replica.tsv'),
         ('S1', 'e2r_scores_S1.tsv', 'e2_scores_S1.tsv'),
         ('S5', 'e2r_scores_S5.tsv', 'e2_scores_S5.tsv')]

rows = ['variant\tmine_lines\te2_lines\tdiff_lines\tresult']
ok = True
for v, mine_f, e2_f in PAIRS:
    mine = open(f'{ROOT}/data/{mine_f}').read().splitlines()
    theirs = open(f'{E2}/data/{e2_f}').read().splitlines()
    diffs = []
    if len(mine) != len(theirs):
        diffs.append(f'length {len(mine)} vs {len(theirs)}')
    for i, (a, b) in enumerate(zip(mine, theirs)):
        if a != b:
            diffs.append(f'line{i+1}')
        if len(diffs) > 50:
            break
    res = 'PASS' if not diffs else 'FAIL:' + ';'.join(diffs[:5])
    if diffs:
        ok = False
    rows.append(f'{v}\t{len(mine)}\t{len(theirs)}\t{len(diffs)}\t{res}')
open(f'{ROOT}/out/e2r_verify_replica.tsv', 'w').write('\n'.join(rows) + '\n')
print('\n'.join(rows))
if not ok:
    print('E2R_VERIFY_REPLICA FAIL — 禁进 metrics')
    sys.exit(2)
print('E2R_VERIFY_REPLICA DONE (PASS)')
