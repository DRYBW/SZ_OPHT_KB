#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E1 收口前验证：①F-RET-minus-Q5b 同分母基线 ②代表簇手算抽查 ③Q7 泄漏案引用明细。"""
import json, csv
from collections import defaultdict

ROOT = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'
EV = '/mnt/D/EyeKB/plans/evalset'
RET_MEMBERS = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5b', 'Q7']
M = json.load(open(f'{ROOT}/e1_class_map.json'))['map']

ON = defaultdict(list)
for i, l in enumerate(open(f'{ROOT}/data/e1_scores_ON.tsv')):
    if i == 0: continue
    f = l.rstrip('\n').split('\t')
    ON[f[0]].append({'canon': f[3], 'n': int(f[4]), 'genes': f[5], 'alias': f[6], 'lit_n': int(f[7]), 'lit_pm': f[8]})
leak = {f[0]: f[6] for i, f in enumerate((l.rstrip('\n').split('\t') for l in open(f'{ROOT}/data/e1_leak_table.tsv'))) if i > 0}
rows3 = list(csv.DictReader(open(f'{EV}/scoring/run3_object_B_table_v1.1.tsv'), delimiter='\t'))
r3 = {x['cluster_id']: x for x in rows3}

def ab_consensus(x):
    a, b = x['ann_A'], x['ann_B']
    if a and b and a == b and not a.startswith(('undetermined', 'coarse:')): return a
    return None

def top1(cid):
    cands = ON.get(cid)
    if not cands: return None, None
    c = sorted(cands, key=lambda c: (-c['n'], c['canon']))[0]
    e = M.get(c['canon']) or {}
    lab = e.get('retina' if not cid.startswith('Q6') else 'ocular')
    if isinstance(lab, str) or lab is None: return c, lab
    return c, None

# ① F-RET minus Q5b，无泄漏列，同分母三行
sub = [x for x in rows3 if x['truth'] and x['member'] in RET_MEMBERS and x['member'] != 'Q5b' and leak.get(x['cluster_id']) == '无']
n = len(sub)
ev1 = sum(1 for x in sub if top1(x['cluster_id'])[1] == x['truth'])
a = sum(1 for x in sub if x['matchA'] == 'True')
b = sum(1 for x in sub if x['matchB'] == 'True')
c = sum(1 for x in sub if ab_consensus(x) == x['truth'])
print(f'[minusQ5b 无泄漏] n={n} ev1={ev1} ({100*ev1/n:.2f}%) A={100*a/n:.2f}% B={100*b/n:.2f}% ABcons={100*c/n:.2f}%')
print(f'  delta ev1-ABcons={100*(ev1-c)/n:+.2f}pp  ev1-B={100*(ev1-b)/n:+.2f}pp')
with open(f'{ROOT}/out/e1_sensitivity_grid.tsv', 'a') as g:
    g.write(f'marker_channel\tF-RET minus Q5b baseline ABcons\t\t{n}\t{round(100*c/n,2)}\t\t\n')
    g.write(f'marker_channel\tF-RET minus Q5b baseline B\t\t{n}\t{round(100*b/n,2)}\t\t\n')

# ② 抽查 Q2::22 / Q4::23 / Q7::x 泄漏例
dig = {json.loads(l)['cluster_id']: json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl')}
for cid in ['Q2::22', 'Q4::23']:
    g = dig[cid]
    print(f'\n[{cid}] truth={r3[cid]["truth"]} n_cells={g["n_cells"]}')
    print('  top10:', ', '.join([(s or x) for s, x in zip(g['top_genes_sym'][:10], g['top_genes'][:10])]))
    for c in sorted(ON.get(cid, []), key=lambda c: (-c['n'], c['canon']))[:5]:
        print(f"   {c['canon']:28s} n={c['n']} genes={c['genes']} alias={c['alias'][:60]} lit_n={c['lit_n']}")
    print('  seats A/B:', r3[cid]['ann_A'], '/', r3[cid]['ann_B'])

# ③ Q7 泄漏案：引用了 38812536 的簇
q7 = [x for x in rows3 if x['member'] == 'Q7' and x['truth']]
cited = [x for x in q7 if '38812536' in (leak.get(x['cluster_id'], '') or '')]
lk = {f[0]: f for i, f in enumerate((l.rstrip('\n').split('\t') for l in open(f'{ROOT}/data/e1_leak_table.tsv'))) if i > 0}
cited = [x for x in q7 if '38812536' in (lk.get(x['cluster_id'], [None]*5)[5] or '')]
hit_ev = sum(1 for x in cited if top1(x['cluster_id'])[1] == x['truth'])
print(f'\n[Q7 leak] clusters citing 38812536: {len(cited)}  ev1-hit={hit_ev}  A-hit={sum(1 for x in cited if x["matchA"]=="True")}  B-hit={sum(1 for x in cited if x["matchB"]=="True")}')
for x in cited[:12]:
    print(f"   {x['cluster_id']:8s} truth={x['truth']:4s} ev={top1(x['cluster_id'])[1] or 'NONE':5s} A={x['ann_A'][:12]:12s} B={x['ann_B'][:12]}")
print('VERIFY_DONE')
