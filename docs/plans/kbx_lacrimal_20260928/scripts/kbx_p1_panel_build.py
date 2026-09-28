#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P1: 外部文献 marker 参考面板构建（KBX_RULING_1 §O2.1）。
纪律：禁参考 KB 任何词条/KB8 面板/自建聚类派生——候选基因仅凭一般领域知识列出，
过门=EuropePMC 机械语境门（人 + 泪腺/腺体语境，逐基因挂可核 PMID），原始返回留 ledgers/。
机械判据（冻结）：query = "GENE" AND lacrimal AND "Homo sapiens"[Organism]；
过门 = 至少 1 条命中且其 title/abstractText 同时含基因 token 与语境 token
{lacrim|tear|exocrine|lacrimal gland|gland}（大小写不敏感）；记录 best PMID。
不过门 = 照实出局（诚实阴性，禁凑数）。
"""
import json, os, sys, time, urllib.request, urllib.parse, re

BASE = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
LEDGER = f'{BASE}/ledgers/eurpmc'
os.makedirs(LEDGER, exist_ok=True)

# 候选矩阵（领域知识列举，非 KB 引用；语境门裁决）
PANEL_CAND = {
  'ACINAR':   ['PRB1','PRB2','PRB3','LPO','PIP','STATH','HTN1','PRSS1','CTRB1','CTRB2',
               'AMY2A','PNLIP','CELA2A','PLA2G1B','CA6','BPIFA2','ZG16B','AQP5','PRR4',
               'LACRT','MUC7','SCGB2A2','CST11','DCD'],
  'DUCT':     ['KRT19','KRT7','CFTR','SOX9','KRT8','SPP1','CEACAM6','PIGR','AQP1','ELF3',
               'BPIFB1','PRR27','MSMB','PSCA','KRT13','ANXA8'],
  'MYOEPITH': ['ACTA2','CNN1','MYH11','TAGLN','KRT5','KRT14','TP63','MYL9','LMOD1','PRLR',
               'CNGB1','CALD1','ACTG2','TPM2'],
  'IMMUNE':   ['PTPRC','CD3D','CD3E','CD68','MS4A1','MZB1','NKG7','CD74','IL7R','MNC1','CCL5','CSF1R'],
  'ENDO':     ['PECAM1','CLDN5','VWF','CDH5','KDR','ESAM','RAMP2'],
  'NEUROGLIA':['PLP1','S100B','SOX10','MAG','ST8SIA3','NGFR','GFAP','S100A4'],
  'STROMA':   ['DCN','LUM','COL1A1','COL1A2','FBN1','PDGFRB','MMP2','LUM'],
}
# 明示出局（非语境门，平台污染先验；理由入档）
EXPLICIT_EXCL = {
  'LYZ': '泪液超丰富蛋白/板法 ambient 风险，候选侧直接排除（语境不计）',
  'LTF': '泪液超丰富蛋白/板法 ambient 风险，候选侧直接排除（语境不计）',
}
CTX = re.compile(r'lacrim|tear|exocrine|gland', re.I)

def eurpmc(gene):
    q = f'"{gene}" AND lacrimal AND "Homo sapiens"[Organism]'
    url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='
           + urllib.parse.quote(q) + '&format=json&pageSize=5&resultType=core')
    req = urllib.request.Request(url, headers={'User-Agent': 'KBX-panel/1.0'})
    last = None
    for att in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode('utf-8')), q
        except Exception as e:
            last = e
            time.sleep(3 * (att + 1))
    raise RuntimeError(f'eurpmc {gene} failed 3x: {last}')

def gene_token_in(text, gene):
    return re.search(r'(?<![A-Za-z0-9])' + re.escape(gene) + r'(?![A-Za-z0-9])', text or '') is not None

rows = []
for grp, genes in PANEL_CAND.items():
    for g in dict.fromkeys(genes):
        fp = f'{LEDGER}/{grp}_{g}.json'
        if os.path.exists(fp):
            data = json.load(open(fp)); q = data.get('_query')
        else:
            data, q = eurpmc(g)
            data['_query'] = q
            tmp = fp + '.tmp'
            json.dump(data, open(tmp, 'w'))
            os.replace(tmp, fp)
            time.sleep(0.4)
        hits = data.get('resultList', {}).get('result', []) or []
        passed, best = False, None
        for h in hits:
            title = h.get('title') or ''
            ab = h.get('abstractText') or ''
            body = title + ' \u00a7 ' + ab
            if h.get('pmid') and gene_token_in(title + ' ' + ab, g) and CTX.search(body):
                passed = True
                best = h['pmid']
                break
        rows.append(dict(group=grp, gene=g, pmid_channel='PASS' if passed else 'FAIL',
                         pmid=best or '', n_hits=data.get('hitCount'),
                         query=q, excl_note=EXPLICIT_EXCL.get(g, '')))
        print(f'{grp:9s} {g:9s} {rows[-1]["pmid_channel"]:4s} pmid={best or "-"} hits={data.get("hitCount")}', flush=True)

import csv
with open(f'{BASE}/ledgers/KBX_PANEL_CANDIDATES.tsv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter='\t')
    w.writeheader(); w.writerows(rows)
np = sum(1 for r in rows if r['pmid_channel'] == 'PASS' and not r['excl_note'])
print(f'\nTOTAL candidates={len(rows)} PASS(with PMID, not excluded)={np}')
print('by group:', {g: sum(1 for r in rows if r['group'] == g and r['pmid_channel'] == 'PASS' and not r['excl_note']) for g in PANEL_CAND})
