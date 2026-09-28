#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P1b: 面板终判（KBX_PREREG_v2 §1.2 两档语境门，对 ledgers/eurpmc/ 缓存原始返回执行）。
Tier1=强语境（基因 token ∧ 语境 token 同现于 title+abstract）；
Tier2=语境档（存在 title 含语境 token 的命中 且 hitCount>=2，基因 token 匹配在索引全文）。
输出 ledgers/KBX_PANEL_FINAL.tsv + 逐群统计 + Tier2 样本目检行。"""
import json, os, re, csv

BASE = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
LEDGER = f'{BASE}/ledgers/eurpmc'
CTX = re.compile(r'lacrim|tear|exocrine|gland', re.I)
EXCLUDED = {'LYZ', 'LTF'}  # 候选侧排除（平台 ambient 先验，PREREG §1.1）

def token_in(text, gene):
    return re.search(r'(?<![A-Za-z0-9])' + re.escape(gene) + r'(?![A-Za-z0-9])', text or '') is not None

rows, samples2 = [], []
for fp in sorted(os.listdir(LEDGER)):
    if not fp.endswith('.json') or fp.endswith('.tmp'):
        continue
    grp, gene = fp[:-5].split('_', 1)
    data = json.load(open(f'{LEDGER}/{fp}'))
    hits = data.get('resultList', {}).get('result', []) or []
    tier, pmid, why = 'FAIL', '', ''
    for h in hits:
        title, ab = h.get('title') or '', h.get('abstractText') or ''
        if h.get('pmid') and token_in(title + ' ' + ab, gene) and CTX.search(title + ' ' + ab):
            tier, pmid, why = 'TIER1', h['pmid'], 'gene+ctx in title/abstract'
            break
    if tier == 'FAIL':
        cand = [h for h in hits if h.get('pmid') and CTX.search(h.get('title') or '')]
        if cand and (data.get('hitCount') or 0) >= 2:
            h = cand[0]
            tier, pmid = 'TIER2', h['pmid']
            why = f"title-ctx hit; hitCount={data.get('hitCount')}; gene-token match indexed (not abstract-visible)"
            if len(samples2) < 12:
                samples2.append(f'  [{grp}/{gene}] PMID {pmid}: {h.get("title")[:110]}')
    if gene in EXCLUDED:
        tier = 'EXCLUDED-AMBIENT'
    rows.append(dict(group=grp, gene=gene, tier=tier, pmid=pmid,
                     hits=data.get('hitCount'), why=why, query=data.get('_query')))

rows.sort(key=lambda r: (r['group'], r['gene']))
with open(f'{BASE}/ledgers/KBX_PANEL_FINAL.tsv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter='\t')
    w.writeheader(); w.writerows(rows)

groups = {}
for r in rows:
    g = groups.setdefault(r['group'], {'T1': [], 'T2': [], 'FAIL': []})
    if r['tier'] == 'TIER1': g['T1'].append(r['gene'])
    elif r['tier'] == 'TIER2': g['T2'].append(r['gene'])
    elif r['tier'] == 'EXCLUDED-AMBIENT': g['FAIL'].append(r['gene'] + '(amb-excl)')
    else: g['FAIL'].append(r['gene'])
print('=== FINAL panel by group ===')
for grp in ['ACINAR','DUCT','MYOEPITH','IMMUNE','ENDO','NEUROGLIA','STROMA']:
    d = groups.get(grp, {'T1':[], 'T2':[], 'FAIL':[]})
    print(f"{grp}: T1={d['T1']}")
    print(f"       T2={d['T2']}")
    print(f"       FAIL={d['FAIL']}")
print('\n=== Tier2 样本目检 ===')
print('\n'.join(samples2))
