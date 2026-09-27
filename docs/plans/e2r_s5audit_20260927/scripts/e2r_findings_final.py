#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2R 质量清单定稿（五类发现，去重）：out/e2r_quality_findings.tsv"""
import json, csv, re, collections

ROOT = '/mnt/D/EyeKB/plans/e2r_s5audit_20260927'
pairs = {(p['cls'], p['gene']): p for p in (json.loads(l) for l in open(f'{ROOT}/data/e2r_pcx_pairs.jsonl'))}
res = {}
for l in open(f'{ROOT}/data/e2r_title_resolution.jsonl'):
    d = json.loads(l); res[d['title']] = d
verd = list(csv.DictReader(open(f'{ROOT}/data/e2r_pair_verdicts.tsv'), delimiter='\t'))
TERMS = {'BC': ['bipolar'], 'AC': ['amacrine'], 'HC': ['horizontal']}
rows = set()
for v in verd:
    p = pairs[(v['cls'], v['gene'])]
    if v['status'] == 'unverifiable':
        rows.add((v['cls'], v['gene'], 'storage_empty_title(题字段全空,n_hits>0)', f"n_hits={v['n_hits']}"))
        continue
    for slot in ('title1', 'title2'):
        t = p[slot]
        if not t:
            continue
        r = res.get(t, {})
        if not r.get('verifiable'):
            rows.add((v['cls'], v['gene'], 'title_unresolvable_EuropePMC_MED', t[:90]))
        elif r.get('hrca_self'):
            rows.add((v['cls'], v['gene'], 'hrca_self_hit_first' if slot == 'title1' else 'hrca_self_hit', t[:90]))
        elif v['status'] == 'creditable':
            mt = (r.get('matched_title', '') or t).lower()
            gh = bool(re.search(r'(?<![a-z0-9])' + re.escape(p['gene'].lower()) + r'(?![a-z0-9])', mt))
            ch = any(x in mt for x in TERMS.get(v['cls'], []))
            if not (gh or ch):
                rows.add((v['cls'], v['gene'], 'offtopic_title(非自引但题不含基因/类词)', t[:90]))
out = ['\t'.join(['cls', 'gene', 'finding', 'detail'])]
out += ['\t'.join(r) for r in sorted(rows)]
open(f'{ROOT}/out/e2r_quality_findings.tsv', 'w').write('\n'.join(out) + '\n')
print(len(rows), 'rows;', dict(collections.Counter(r[2] for r in rows)))
print('FINDINGS_DONE')
