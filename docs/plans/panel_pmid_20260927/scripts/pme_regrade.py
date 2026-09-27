#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PME A5 重判：APC_MHCII_high doc_re 去循环（HLA-D* 基因名自身不再充当类语境 token）。
统一对全部 280 键从存留 raw 重算（确定性规则修复，非选择性改判）。
输出 out/pme_hits_v2.jsonl + ledgers/regrade_diff.txt（每键 old->new）。"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pme_search as ps

NEW_APC = r'MHC\s*class\s*II|\bMHC-?II\b|antigen[-\s]presenting|\bAPCs?\b|class\s*II\s+(?:HLA|MHC|antigen)'
OLD_APC = ps.CLASSES['APC_MHCII_high'][1]
ps.CLASSES['APC_MHCII_high'] = (ps.CLASSES['APC_MHCII_high'][0], NEW_APC, None)

def load_raw(cls, gene):
    p = f'{ps.RAW}/{ps.slug(cls, gene)}.json'
    d = json.load(open(p))
    raws = [r for r in (d.get('raw1'), d.get('raw2')) if r]
    return raws

diff = []
out = open(f'{ps.ROOT}/out/pme_hits_v2.jsonl', 'w')
for l in open(f'{ps.ROOT}/out/pme_hits.jsonl'):
    d = json.loads(l)
    c, g = d['class'], d['gene']
    raws = load_raw(c, g)
    gv, st, wk, nc = ps.grade(c, g, raws)
    rec = dict(d); rec['grade'] = gv; rec['strong_evidence'] = st; rec['weak_refs'] = wk; rec['n_candidates'] = nc
    rec['regrade_A5'] = (gv != d['grade'])
    if gv != d['grade']:
        diff.append(f"{c}/{g}: {d['grade']} -> {gv}")
    out.write(json.dumps(rec, ensure_ascii=False) + '\n')
out.close()
open(f'{ps.ROOT}/ledgers/regrade_diff.txt', 'w').write(
    f"A5 rule fix: APC_MHCII_high doc_re de-circularized (HLA-D*/DR* gene names no longer count as class context).\n"
    f"Uniform re-grade of all 280 keys from stored raw (deterministic; not selective). diffs={len(diff)}\n" + '\n'.join(diff) + '\n')
print(f"regrade done, diffs={len(diff)}")
for x in diff: print(' ', x)
