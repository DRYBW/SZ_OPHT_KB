#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TIEP-t0: 全部只读输入件 sha256 台账（证据冻结）。只读，不改动任何源件。"""
import hashlib, os, datetime

SRC = [
    '/mnt/D/EyeKB/plans/evalset/scoring/run3_object_B_table_v1.1.tsv',
    '/mnt/D/EyeKB/plans/evalset/scoring/run4r_verdict.json',
    '/mnt/D/EyeKB/plans/evalset/scoring/run5_verdict.json',
    '/mnt/D/EyeKB/plans/evalset/annotation/ANN_A_run4.jsonl',
    '/mnt/D/EyeKB/plans/evalset/annotation/ANN_B_run4.jsonl',
    '/mnt/D/EyeKB/plans/evalset/annotation/ANN_C_run4r.jsonl',
    '/mnt/D/EyeKB/plans/evalset/RUN4_TARGETS_v1.1.json',
    '/mnt/D/EyeKB/plans/face_v21_20260926/scoring/FACEV21_VERDICT.json',
    '/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_verdict.json',
    '/mnt/D/EyeKB/plans/e2_decontam_20260926/data/e2_scores_S1.tsv',
    '/mnt/D/EyeKB/plans/evidence_scoring_20260926/e1_class_map.json',
    '/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_changed_clusters.json',
]
OUT = '/mnt/D/EyeKB/plans/tiep_20260927/ledgers/SHA_SOURCES.txt'

lines = [f'# TIEP source ledger {datetime.datetime.now().isoformat(timespec="seconds")} (read-only inputs)']
for p in SRC:
    if not os.path.exists(p):
        lines.append(f'MISSING\t{p}')
        continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    lines.append(f'{h}\t{os.path.getsize(p)}\t{p}')
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
missing = sum(1 for l in lines if l.startswith('MISSING'))
print(f'\n[ledger] {len(SRC) - missing}/{len(SRC)} ok -> {OUT}')
raise SystemExit(1 if missing else 0)
