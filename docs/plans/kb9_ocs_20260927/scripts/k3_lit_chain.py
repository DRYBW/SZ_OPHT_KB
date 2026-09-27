#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K3 v2: 逐基因文献链。v1 教训: SPECIES:HUMAN 字段使 hitCount=0(该索引组合失效) → 改后处理物种判定。
通道: EuropePMC 相关性检索(基因+细胞类型语境词) → 命中取 top → eutils esummary 物种核验(明确非人=拒)。
grade: pmid(基因+语境同现且人) / pmid_context(共现级) / weak_evidence(0 可核)。raw 全落 ledgers/。"""
import json, os, time, urllib.request, urllib.parse

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
RAW = f'{ROOT}/ledgers/epmc_raw_v2'; os.makedirs(RAW, exist_ok=True)
RAW2 = f'{ROOT}/ledgers/esummary'; os.makedirs(RAW2, exist_ok=True)
UA = {'User-Agent': 'curl/8 KB9-lit-v2'}

CTX = {
    'Melanocyte': ['melanocyte', 'melanoma', 'pigment cell', 'melanocytic', 'uvea', 'iris'],
    'Schwann': ['schwann', 'myelin', 'peripheral nerve', 'nerve sheath', 'glial'],
    'Conj_epithelium_suprabasal': ['conjunctival', 'conjunctiva', 'ocular surface', 'corneal epithel', 'stratified epithel', 'suprabasal', 'skin epithel'],
}
GENES = {
    'Melanocyte': ['TRPM1', 'MLANA', 'TYRP1', 'PMEL', 'DCT', 'TYR', 'GPR143', 'SLC24A5', 'BCAN', 'ABCB5', 'GAPDHS', 'GALNTL6'],
    'Schwann': ['MPZ', 'SCN7A', 'SOX2', 'NRXN1', 'CADM2', 'NTM', 'NRXN3', 'FRMD5', 'MYOT', 'COL28A1', 'GRIK2', 'XKR4'],
    'Conj_epithelium_suprabasal': ['S100A8', 'S100A9', 'KLK12', 'KLK13', 'SPRR3', 'IVL', 'SPINK5', 'KRT4', 'RHCG', 'PDZK1IP1'],
}

def jget(url, fn):
    if os.path.exists(fn):
        return json.load(open(fn))
    for i in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as e:
            if i == 2:
                return {'_error': str(e)}
            time.sleep(2 * (i + 1))

def species_ok(pmid):
    fn = f'{RAW2}/{pmid}.json'
    d = jget(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json', fn)
    try:
        r = d['result'][pmid]
        sp = (r.get('species') or '').lower()
        title = (r.get('title') or '').lower()
        bad = any(a in sp for a in ['mus musculus', 'rat', 'mouse', 'macaca', 'bovine', 'porcine', 'zebrafish', 'xenopus', 'chicken', 'canine', 'feline'])
        return (not bad), sp or 'n/a', title
    except Exception:
        return True, 'lookup_failed', ''

ledger = []
for term, genes in GENES.items():
    for g in genes:
        q = f'"{g}" AND (' + ' OR '.join(f'"{w}"' if ' ' in w else w for w in CTX[term][:5]) + ')'
        url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=' + urllib.parse.quote(q) +
               '&format=json&pageSize=5&resultType=core')
        tag = f'{term}__{g}'
        d = jget(url, f'{RAW}/{tag}.json')
        cands = []
        for x in (d.get('resultList', {}) or {}).get('result', []) or []:
            pmid = x.get('pmid')
            if not pmid:
                continue
            blob = ((x.get('title') or '') + ' ' + (x.get('abstractText') or '')).lower()
            gene_in = g.lower() in blob
            ctx_words = [w for w in CTX[term] if w.lower() in blob]
            if not gene_in:
                continue
            cands.append({'pmid': pmid, 'yr': x.get('pubYear'), 't': (x.get('title') or '')[:140],
                          'ctx': ctx_words, 'pmc': bool(x.get('pmcid'))})
        picks = []
        for c in sorted(cands, key=lambda z_: (len(z_['ctx']) > 0, z_['pmc']), reverse=True)[:3]:
            ok, sp, _ = species_ok(c['pmid'])
            if not ok:
                continue
            grade = 'pmid' if (c['ctx'] and len(c['ctx']) >= 1) else 'pmid_context'
            c['grade'] = grade
            c['species'] = sp
            picks.append(c)
            if len(picks) >= 2:
                break
        verdict = 'pmid' if any(h['grade'] == 'pmid' for h in picks) else ('pmid_context' if picks else 'weak_evidence')
        ledger.append({'term': term, 'gene': g, 'query': q, 'n_cands': len(cands),
                       'pmids': [h['pmid'] for h in picks], 'grades': [h['grade'] for h in picks],
                       'ctx': [','.join(h['ctx'][:3]) for h in picks], 'titles': [h['t'] for h in picks],
                       'verdict': verdict, 'epmc_raw': f'ledgers/epmc_raw_v2/{tag}.json'})
        print(f"{term:26s} {g:8s} {verdict:12s} {[(h['pmid'], h['grade']) for h in picks]}")
        time.sleep(0.3)

with open(f'{ROOT}/ledgers/PMID_LEDGER.tsv', 'w') as f:
    f.write('term\tgene\tquery\tn_cands\tpmids\tgrades\tctx_hits\tverdict\tepmc_raw\ttitles\n')
    for r in ledger:
        f.write('\t'.join([r['term'], r['gene'], r['query'].replace('\t', ' '), str(r['n_cands']),
                           ','.join(r['pmids']), ','.join(r['grades']), ' | '.join(r['ctx']),
                           r['verdict'], r['epmc_raw'],
                           ' || '.join(r['titles']).replace('\t', ' ')]) + '\n')
json.dump(ledger, open(f'{ROOT}/ledgers/PMID_LEDGER.json', 'w'), ensure_ascii=False, indent=1)
print('LIT DONE', len(ledger), 'weak:', sum(1 for r in ledger if r['verdict'] == 'weak_evidence'))
