#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2R-1 清单化：v5 pmid_context(n_hits>0) 120 对提取 + 三方一致性门（E2R_PREREG §0）。
产物: data/e2r_pcx_pairs.tsv, data/e2r_pcx_pairs.jsonl"""
import json, sys, datetime

ROOT = '/mnt/D/EyeKB/plans/e2r_s5audit_20260927'
MD = '/mnt/D/EyeKB/kb/markers'
E2 = '/mnt/D/EyeKB/plans/e2_decontam_20260926'

db = json.load(open(f'{MD}/markers_v5_retina_interneuron.json', encoding='utf-8'))
prov = db.get('provenance') or {}
markers = db.get('markers') or {}

pairs = []
for cls, genes in prov.items():
    for gene, recs in genes.items():
        for r in recs:
            if isinstance(r, dict) and r.get('type') == 'pmid_context' and int(r.get('n_hits') or 0) > 0:
                tt = [str(x) for x in (r.get('top_titles') or [])]
                pairs.append({'lib': 'retina_interneuron', 'cls': cls, 'gene': gene.upper(),
                              'query': r.get('query', ''), 'n_hits': int(r['n_hits']),
                              'title1': tt[0] if len(tt) > 0 else '',
                              'title2': tt[1] if len(tt) > 1 else ''})

# 门0：一致性
n_prov = len(pairs)
n_mx = sum(1 for i, l in enumerate(open(f'{E2}/data/e2_gene_panel_pmid.tsv'))
           if i > 0 and l.split('\t')[8].strip() == 'Y')
inpanel = sum(1 for p in pairs
              if p['gene'] in {str(g).upper() for g in (markers.get(p['cls']) or [])})
print(f'provenance pcx>0={n_prov}  E2 matrix pcx_ext=Y={n_mx}  in-panel={inpanel}')
assert n_prov == 120 and n_mx == 120 and inpanel == 120, 'GATE0 FAIL: 三方一致性不满足，停工'

# 去重检查（每对应恰一条 pmid_context？如有多条取并集前先验证）
from collections import Counter
c = Counter((p['cls'], p['gene']) for p in pairs)
dups = {k: v for k, v in c.items() if v > 1}
print('dup (cls,gene) records:', dups if dups else 'none')

with open(f'{ROOT}/data/e2r_pcx_pairs.tsv', 'w') as f:
    f.write('\t'.join(['lib', 'cls', 'gene', 'query', 'n_hits', 'title1', 'title2']) + '\n')
    for p in pairs:
        f.write('\t'.join([p['lib'], p['cls'], p['gene'], p['query'], str(p['n_hits']),
                           p['title1'], p['title2']]) + '\n')
with open(f'{ROOT}/data/e2r_pcx_pairs.jsonl', 'w') as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + '\n')

n_empty1 = sum(1 for p in pairs if not p['title1'])
n_2t = sum(1 for p in pairs if p['title2'])
print(f'pairs={len(pairs)} title1_empty={n_empty1} two_titles={n_2t} ran {datetime.datetime.now()}')
print('E2R_EXTRACT_DONE')
