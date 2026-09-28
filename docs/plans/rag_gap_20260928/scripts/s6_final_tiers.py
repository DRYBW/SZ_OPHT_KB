#!/usr/bin/env python3
"""RAGGAP step 6 — 终判分档 + A 档 HEAD 实测体积 + 报批清单 + 结论统计（零下载）。
HEAD 目标: EPMC OA 全文 (fullTextXML + 有 PDF 则 PDF)，非 OA 记摘要字节。
产出: out/tier_FINAL.tsv (逐行终档), out/tier_A_items.tsv (PMID 级报批),
      out/tier_B_register.tsv, out/tier_C_backlog.tsv, out/RAGGAP_STATS.json
"""
import csv, json, time, urllib.request, urllib.error, collections, os, sys

OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest'

def head(url):
    req = urllib.request.Request(url, method='HEAD')
    for att in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                cl = r.headers.get('Content-Length')
                return int(cl) if cl else -1
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                return None        # 客户端错误(非OA/404)是确定的，不重试
            time.sleep(2 + att * 3)
        except Exception:
            time.sleep(2 + att * 3)
    return None

def epmc_json(query, pageSize=1):
    url = BASE + '/search?' + urllib.parse.urlencode({'query': query, 'format': 'json', 'pageSize': pageSize, 'resultType': 'core'})
    for att in range(4):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(3 + att * 4)
    return None

import urllib.parse

# ---------- 输入 ----------
rows = list(csv.DictReader(open(f'{OUT}/coverage_matrix.tsv'), delimiter='\t'))
gene_check = {}
for fn in ('epmc_gene_check.tsv', 'epmc_gene_check_extra.tsv'):
    p = f'{OUT}/{fn}'
    if os.path.exists(p):
        for r in csv.DictReader(open(p), delimiter='\t'):
            key = (r['gene'], r['ctx'])
            # 主查覆盖 extra（同 key 保留更权威者：两者判据相同）
            gene_check.setdefault(key, r)
s2ctx = {}
p = f'{OUT}/s2_ctx_rows.tsv'
if os.path.exists(p):
    for r in csv.DictReader(open(p), delimiter='\t'):
        s2ctx[(r['library'], r['entry'], r['gene'])] = r

def lib_ctx(lib):
    l = lib.replace(':prov', '')
    if l.startswith('retina'): return 'retina'
    return {'membrane_v1': 'membrane', 'face_v6': 'face', 'lacrimal_v6': 'lacrimal', 'kb9': 'kb9'}.get(l, 'membrane')

# corpus membership (for A item annotation)
corpus_chunks = {}
for _r in csv.DictReader(open(f'{OUT}/corpus_papers.tsv'), delimiter='\t'):
    corpus_chunks[_r['pmid']] = int(_r['n_chunks'])

# ---------- 终档 ----------
final = []
a_pmids = collections.defaultdict(lambda: dict(benefit_rows=set(), origin=set()))
for r in rows:
    key = (r['library'], r['entry'], r['gene'])
    ctx = lib_ctx(r['library'])
    if r['support'] == 'S0_not_a_gene':
        tier, note = 'NONGENE', 'state label / non-symbol token'
    elif r['support'] == 'S1_chain_covered':
        tier, note = 'COVERED', 'chain PMID in-corpus with chunks'
    elif r['support'] in ('S2_gene_in_corpus', 'S2b_context_only'):
        s = s2ctx.get(key, {})
        g = s.get('c_grade', 'C_mid')
        if g == 'C_ctx_mismatch':
            chk = gene_check.get((r['gene'], ctx))
            v = chk['verdict'] if chk else 'API_FAIL'
            if v.startswith('A_'):
                tier, note = 'A', 'S2 mention ctx-mismatch; EPMC eye-lit exists'
            else:
                tier, note = 'B', f'ctx-mismatch + EPMC {v} (n={chk["n_eye_hits"] if chk else "?"})'
        else:
            tier, note = 'C', f"{g}; link in-corpus pmids → {s.get('ctx_top','')[:80]}"
    else:  # S3
        if r['cited_pmids']:
            tier, note = 'A', 'cited chain PMID(s) absent/ghost in corpus'
            for p_ in r['cited_pmids'].split(','):
                if p_:
                    a_pmids[p_]['benefit_rows'].add('|'.join(key)); a_pmids[p_]['origin'].add('cited_chain')
        else:
            chk = gene_check.get((r['gene'], ctx))
            if chk is None:
                tier, note = 'B', 'no gene-check (API fail)'
            elif chk['verdict'].startswith('A_'):
                tier, note = 'A', f"EPMC eye-hits={chk['n_eye_hits']}"
                for p_ in (chk.get('top_pmids') or '').split(','):
                    if p_ and p_.isdigit():
                        a_pmids[p_]['benefit_rows'].add('|'.join(key)); a_pmids[p_]['origin'].add('gene_scan_top')
            else:
                tier, note = chk['verdict'], f"EPMC eye-hits={chk['n_eye_hits']}"
    final.append(dict(r, ctx_family=ctx, tier=tier, tier_note=note))

with open(f'{OUT}/tier_FINAL.tsv', 'w', newline='') as w:
    wr = csv.DictWriter(w, fieldnames=list(final[0].keys()), delimiter='\t')
    wr.writeheader(); wr.writerows(final)
tc = collections.Counter(f['tier'] for f in final)
print('row tiers:', dict(tc))

# ---------- A 档 PMID 级 HEAD 体积 ----------
allpm = sorted(a_pmids)
print('A-tier distinct PMIDs:', len(allpm))
meta = {}
B = 50
for i in range(0, len(allpm), B):
    d = epmc_json(' OR '.join(f'EXT_ID:{p}' for p in allpm[i:i+B]), pageSize=B)
    if d:
        for h in d.get('resultList', {}).get('result', []):
            meta[str(h.get('pmid'))] = h
    time.sleep(0.4)
arows = []
for p_ in allpm:
    h = meta.get(p_, {})
    pmcid = h.get('pmcid') or ''
    oa = (h.get('isOpenAccess') == 'Y')
    # 实测声明: EPMC fullTextXML 为 chunked 流式，HEAD 200 无 Content-Length，
    # Range 被忽略（不接受 206）→ 单篇体积无法零下载实测。
    # 报批清单以 n_items × 经验上界 0.5 MB 估算（报告中声明，>1GB 条款按总估判定）。
    size_xml = size_pdf = None
    absl = h.get('abstractText') or ''
    arows.append(dict(pmid=p_, exists=1 if h else 0, pmcid=pmcid, oa='Y' if oa else 'N',
                      year=h.get('pubYear', ''), journal=(h.get('journalTitle') or '')[:70],
                      title=' '.join((h.get('title') or '').split())[:180],
                      fulltext_xml_bytes=size_xml if size_xml and size_xml > 0 else '',
                      abstract_bytes=len(absl.encode()),
                      benefit_rows=len(a_pmids[p_]['benefit_rows']),
                      origin=';'.join(sorted(a_pmids[p_]['origin'])),
                      in_corpus=('Y' if corpus_chunks.get(p_, 0) > 0 else ('GHOST' if p_ in corpus_chunks else 'N'))))
    time.sleep(0.3)
with open(f'{OUT}/tier_A_items.tsv', 'w', newline='') as w:
    wr = csv.DictWriter(w, fieldnames=list(arows[0].keys()), delimiter='\t')
    wr.writeheader(); wr.writerows(arows)

# B 档登记
brows = [f for f in final if f['tier'].startswith('B')]
with open(f'{OUT}/tier_B_register.tsv', 'w', newline='') as w:
    wr = csv.writer(w, delimiter='\t')
    wr.writerow('gene\tctx_family\tlib_entry\tn_eye_hits\ttier')
    for f in brows:
        chk = gene_check.get((f['gene'], f['ctx_family']))
        wr.writerow([f['gene'], f['ctx_family'], f"{f['library']}/{f['entry']}",
                     chk['n_eye_hits'] if chk else '', f['tier']])
# C 档 backlog
crows = [f for f in final if f['tier'] == 'C']
with open(f'{OUT}/tier_C_backlog.tsv', 'w', newline='') as w:
    wr = csv.writer(w, delimiter='\t')
    wr.writerow('gene\tlib_entry\tc_grade\tctx_papers\tlink_candidate_pmids')
    for f in crows:
        s = s2ctx.get((f['library'], f['entry'], f['gene']), {})
        wr.writerow([f['gene'], f"{f['library']}/{f['entry']}", s.get('c_grade', ''),
                     s.get('ctx_papers', ''), s.get('ctx_top', '')])

tot = sum(int(a['fulltext_xml_bytes']) for a in arows if a['fulltext_xml_bytes'] != '')
stats = dict(row_tiers=dict(tc), n_A_items=len(arows), A_total_fulltext_bytes=tot,
             n_A_gt_100MB=[a['pmid'] for a in arows if a['fulltext_xml_bytes'] != '' and int(a['fulltext_xml_bytes']) > 100_000_000],
             n_B_rows=len(brows), n_C_rows=len(crows),
             C_strong=sum(1 for f in crows if s2ctx.get((f['library'], f['entry'], f['gene']), {}).get('c_grade') == 'C_strong'))
json.dump(stats, open(f'{OUT}/RAGGAP_STATS.json', 'w'), indent=1)
print(json.dumps(stats, indent=1))
