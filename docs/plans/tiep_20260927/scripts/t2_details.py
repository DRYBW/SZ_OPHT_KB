#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TIEP-t2: 差集明细提取（只读 t1 逻辑复用 + 源件，落 out/*_lists.tsv）。
1) 每一 FIXED/BROKEN/OVERTURN 条目含票面原文；2) RUN5/KB9 各规则新 P2 污染违规簇清单；
3) 硬校验: 任何规则不得改动既有已定名(hit)结论——was_published_hit 且改名的差集行数必须=0；
4) KB9 已知案 Q6::30 与 RUN5 关键案在各规则下的去向。"""
import json, collections, sys
import pandas as pd

sys.path.insert(0, '/mnt/D/EyeKB/plans/tiep_20260927/scripts')
from t1_revote import (load_faces, load_s1, c4_consensus, rule_c1, rule_c2, rule_c3,
                       hit_of, flip_class, W_DEFAULT)

ROOT = '/mnt/D/EyeKB/plans/tiep_20260927'
RULES = {'C1_default': ('C1', W_DEFAULT), 'C2a': ('C2', False), 'C2b': ('C2', True),
         'C3a': ('C3', False), 'C3b': ('C3', True)}

def new_name(r, kind, arg, s1map):
    if kind == 'C1':
        return rule_c1(r['ballots'], arg)
    if kind == 'C2':
        return rule_c2(r['ballots'], arg)
    return rule_c3(r['ballots'], s1map, r['cid'], allow_sole=arg)

def ballots_str(r):
    out = []
    for s in ('A', 'B', 'C'):
        b = r['ballots'][{'A': 0, 'B': 1, 'C': 2}[s]]
        lab = b['label'] or (f"coarse:{b['coarse']}" if b['kind'] == 'COARSE' else b['kind'].lower())
        out.append(f"{s}={lab}/{b['grade']}")
    return ' '.join(out)

def main():
    faces, _ = load_faces()
    s1map, _ = load_s1()
    rows_flip, rows_p2, bad = [], [], []
    for face, rr in faces.items():
        for r in rr:
            c4n, c4m, _ = c4_consensus(r['ballots'])
            for gname, (kind, arg) in RULES.items():
                nm = new_name(r, kind, arg, s1map)
                fc = flip_class(c4n, nm, r['truth'])
                if fc == 'unchanged':
                    continue
                rows_flip.append(dict(face=face, rule=gname, cid=r['cid'], truth=r['truth'],
                                      c4_name=c4n, new_name=nm, flip=fc, ballots=ballots_str(r)))
                if c4n and hit_of(c4n, r['truth']):
                    bad.append(dict(face=face, rule=gname, cid=r['cid'], c4_name=c4n, new_name=nm, flip=fc))
                # P2 违规复算（仅 Q6 两面有 kb_classes 字段）
                if 'kb_classes_any' in r and nm:
                    for scope in ('strict', 'any'):
                        if nm in r[f'kb_classes_{scope}'] and nm != r['truth'] and r['n_truth_marker'] >= 3:
                            rows_p2.append(dict(face=face, rule=gname, cid=r['cid'], truth=r['truth'],
                                                name=nm, scope=scope, n_truth_marker=r['n_truth_marker']))
    fdf = pd.DataFrame(rows_flip)
    fdf.to_csv(f'{ROOT}/out/flip_lists.tsv', sep='\t', index=False)
    pdf = pd.DataFrame(rows_p2)
    pdf.to_csv(f'{ROOT}/out/p2_violation_lists.tsv', sep='\t', index=False)

    print(f'[flip 明细] {len(fdf)} 行 -> out/flip_lists.tsv')
    print(fdf[fdf.flip != 'RENAME-still-wrong'].to_string(index=False))
    print('\n[P2 违规复算 (any 口径)]')
    if len(pdf):
        piv = pdf[pdf.scope == 'any'].groupby(['face', 'rule'])['cid'].apply(list)
        print(piv.to_string())
    print('\n[已发布 hit 被改动检查]')
    if bad:
        print('!! 发现改动既有已对结论的条目:'); print(pd.DataFrame(bad).to_string(index=False)); raise SystemExit(1)
    print('PASS: 0 条——五规则均未改动任何既有已定名且正确的结论 (无静默改判、无 OVERTURN)')
    # Q6::30 / 关键案追踪
    print('\n[重点案去向]')
    key = [c for c in (('Q6::30', 'KB9'), ('Q6::30', 'RUN5'), ('Q6::16', 'KB9'), ('Q6::31', 'KB9'),
                       ('Q6::12', 'KB9'), ('Q6::13', 'RUN5'), ('Q4::15', 'RUN4-r'), ('Q1::4', 'RUN4-r'))]
    for cid, face in key:
        rr = next(r for r in faces[face] if r['cid'] == cid)
        c4n, c4m, _ = c4_consensus(rr['ballots'])
        res = {g: new_name(rr, k, a, s1map) for g, (k, a) in RULES.items()}
        print(f'  {face} {cid} truth={rr["truth"]} ballots: {ballots_str(rr)}')
        print(f'    C4={c4n}({c4m}) ' + ' '.join(f'{g}={v}' for g, v in res.items()))

if __name__ == '__main__':
    main()
