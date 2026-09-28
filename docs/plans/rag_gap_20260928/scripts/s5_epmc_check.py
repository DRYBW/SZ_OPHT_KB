#!/usr/bin/env python3
"""RAGGAP step 5 — EuropePMC 外部元数据核查（零下载：只读 REST 计数/存在性）。
预注册判据（HC-LITRE 教训固化，先落纸）:
  R1 引用 PMID 库外但 EPMC 可证存在      → A 档（一手文献明确，补该篇）
  R2 无引用链基因: eye-context 命中 >5   → A 档候选（列 top 命中；仍按 R1 逐篇看 OA）
  R3 eye-context 命中 1-5               → B 档（文献面薄=固有稀缺型，登记计数不列补）
  R4 eye-context 命中 0                 → B 档（真缺文献）
  注意: 只有 eye-context（人+眼组织词族）计数才算数，全库命中不算（防虚报）。
产出 out/epmc_absent_pmids.tsv, out/epmc_gene_check.tsv
"""
import json, time, urllib.request, urllib.parse, csv, sys

OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'

def epmc(query, pageSize=1, fl=None):
    q = {'query': query, 'format': 'json', 'pageSize': pageSize, 'resultType': 'core'}
    if fl: q['flFields'] = 'PMID,PMCID,JOURNAL,YPUBYEAR'
    url = BASE + '?' + urllib.parse.urlencode(q)
    for att in range(4):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print('RETRY', e, file=sys.stderr); time.sleep(3 + att * 4)
    return None

CONTEXT = {
    'retina': '(retina OR retinal OR photoreceptor OR macula OR "retinal pigment")',
    'membrane': '(eye OR ocular OR retinal OR choroid OR "optic nerve")',
    'face': '(cornea OR corneal OR conjunctiva OR conjunctival OR "ocular surface" OR limbal)',
    'lacrimal': '(lacrimal OR tear OR "dry eye" OR meibomian)',
    'kb9': '(ocular OR eye OR conjunctiva OR cornea OR "ocular surface")',
}

def lib_ctx(lib):
    l = lib.replace(':prov', '')
    if l.startswith('retina'): return 'retina'
    if l == 'membrane_v1': return 'membrane'
    if l == 'face_v6': return 'face'
    if l == 'lacrimal_v6': return 'lacrimal'
    if l == 'kb9': return 'kb9'
    return 'membrane'

# ---------- 1) 库外引用 PMID 存在性 ----------
absent = [p.strip() for p in open(f'{OUT}/gap_absent_pmids.txt') if p.strip()]
print('absent cited PMIDs:', len(absent))
# 同时把 S3 行里有链但 ghost 的 PMID 也纳入（后面从 gap 行拿）
rows_s3 = []
with open(f'{OUT}/coverage_matrix.tsv') as f:
    rd = csv.DictReader(f, delimiter='\t')
    for r in rd:
        if r['support'] == 'S3_no_corpus_support':
            rows_s3.append(r)
extra = set()
for r in rows_s3:
    for p in (r['chain_ghost'].split(',') if r['chain_ghost'] else []):
        if p: extra.add(p)
allp = sorted(set(absent) | extra)
recs = {}
B = 50
for i in range(0, len(allp), B):
    batch = allp[i:i+B]
    q = ' OR '.join(f'EXT_ID:{p}' for p in batch)
    d = epmc(q, pageSize=B)
    if not d: continue
    for hit in d.get('resultList', {}).get('result', []):
        pm = str(hit.get('pmid') or hit.get('medlinePuid') or '')
        recs[pm] = dict(pmid=pm, exists=1, pmcid=hit.get('pmcid', ''), oa=hit.get('isOpenAccess', 'N'),
                        intext='Y' if hit.get('inEPMC') == 'Y' else 'N',
                        year=hit.get('pubYear', ''), journal=(hit.get('journalTitle') or '')[:80],
                        title=' '.join((hit.get('title') or '').split())[:200],
                        n_cit=hit.get('citedByCount', 0))
    time.sleep(0.5)
with open(f'{OUT}/epmc_absent_pmids.tsv', 'w', newline='') as w:
    wr = csv.writer(w, delimiter='\t')
    wr.writerow('pmid exists pmcid isOpenAccess inEPMC fulltext_year journal title'.split())
    for p in allp:
        r = recs.get(p)
        if r: wr.writerow([r['pmid'], 1, r['pmcid'], r['oa'], r['intext'], r['year'], r['journal'], r['title']])
        else: wr.writerow([p, 0, '', '', '', '', '', ''])
print('epmc absent PMID check done:', sum(1 for p in allp if p in recs), '/', len(allp))

# ---------- 2) 无链 gap 基因的 eye-context 计数 ----------
# (gene, ctx) 对
pairs = {}
for r in rows_s3:
    g = r['gene']
    if r['cited_pmids']:      # 有链（absent/ghost）→ R1 处理，不再做基因级计数（防双计）
        continue
    pairs.setdefault((g, lib_ctx(r['library'])), set()).add(f"{r['library']}/{r['entry']}")
print('gene-context checks:', len(pairs))
out = []
for (g, ctx), entries in sorted(pairs.items()):
    q = f'"{g}" AND {CONTEXT[ctx]} AND SPECIES:"HUMAN"'
    d = epmc(q, pageSize=1)
    n_eye = d['hitCount'] if d else -1
    top = ''
    if d and n_eye and n_eye > 0:
        d2 = epmc(q, pageSize=3, fl=1)
        if d2:
            top = ','.join(str(h.get('pmid', h.get('doi', '?'))) for h in d2.get('resultList', {}).get('result', []))
    verdict = 'B_scarce_1_5' if 1 <= n_eye <= 5 else ('B_none' if n_eye == 0 else ('A_candidate' if n_eye > 5 else 'API_FAIL'))
    out.append(dict(gene=g, ctx=ctx, n_eye_hits=n_eye, top_pmids=top,
                    n_entries=len(entries), entries=';'.join(sorted(entries))[:200], verdict=verdict))
    print(g, ctx, n_eye, verdict, flush=True)
    time.sleep(0.5)
with open(f'{OUT}/epmc_gene_check.tsv', 'w', newline='') as w:
    wr = csv.DictWriter(w, fieldnames=['gene', 'ctx', 'n_eye_hits', 'top_pmids', 'n_entries', 'entries', 'verdict'], delimiter='\t')
    wr.writeheader(); wr.writerows(out)
print('gene checks done:', len(out))
