#!/usr/bin/env python3
"""RAGGAP step 5b — 语境匹配细化:
 (a) S2/S2b 行计算 ctx_papers(库望组织 ∩ 提及该基因的在库论文) → C_strong/mid/weak
 (b) ctx_papers==0 的 S2 行 = "库内提及但语境错配" → 与 S3 同路，补 EPMC 语境计数
产出 out/s2_ctx_rows.tsv, out/gap_ctx_extra.tsv (待补查 gene×ctx 对), out/epmc_gene_check_extra.tsv
"""
import csv, pickle, collections, json, time, urllib.request, urllib.parse, sys

OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'

CTX_MAP = {
    'retina': {'retina', 'RPE', 'choroid', 'optic_nerve'},
    'membrane': None,   # 全眼通用面板 → 任何眼组织均算语境
    'face': {'cornea', 'conjunctiva', 'sclera'},
    'lacrimal': {'lacrimal', 'Harderian', 'meibomian', 'tear'},   # 语料库内预期为空
    'kb9': {'cornea', 'conjunctiva', 'sclera', 'iris'},
}

def lib_ctx(lib):
    l = lib.replace(':prov', '')
    if l.startswith('retina'): return 'retina'
    if l == 'membrane_v1': return 'membrane'
    if l == 'face_v6': return 'face'
    if l == 'lacrimal_v6': return 'lacrimal'
    if l == 'kb9': return 'kb9'
    return 'membrane'

papers = {}
with open(f'{OUT}/corpus_papers.tsv') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        papers[r['pmid']] = set((r['tissues'] or '').split(';')) - {''}

gene_paper = pickle.load(open(f'{OUT}/gene_paper_map.pkl', 'rb'))

rows = list(csv.DictReader(open(f'{OUT}/coverage_matrix.tsv'), delimiter='\t'))
out = []
extra_pairs = {}
for r in rows:
    if r['support'] not in ('S2_gene_in_corpus', 'S2b_context_only'):
        continue
    ctx = lib_ctx(r['library'])
    want = CTX_MAP[ctx]
    g = r['gene']
    pmset = gene_paper.get(g, set())
    # 语境候选 PMID: 提及基因且有 chunks 的论文；membrane=全眼 any，其余=组织交集
    if want is None:
        ctxp = [p for p in pmset if p in papers]
    else:
        ctxp = [p for p in pmset if p in papers and (papers[p] & want)]
    n = len(ctxp)
    tier = 'C_strong' if n >= 3 else ('C_mid' if n >= 1 else 'C_ctx_mismatch')
    out.append(dict(r, ctx_family=ctx, ctx_papers=n, ctx_top=','.join(sorted(ctxp, key=lambda p: -len(papers[p]))[:5]),
                    c_grade=tier))
    if tier == 'C_ctx_mismatch':
        extra_pairs.setdefault((g, ctx), set()).add(f"{r['library']}/{r['entry']}")

with open(f'{OUT}/s2_ctx_rows.tsv', 'w', newline='') as w:
    wr = csv.DictWriter(w, fieldnames=list(out[0].keys()), delimiter='\t')
    wr.writeheader(); wr.writerows(out)
c = collections.Counter(o['c_grade'] for o in out)
print('S2 rows graded:', dict(c))

# 补查: 只查没在 s5 主查里出现过的 (gene, ctx)
done = set()
try:
    for r in csv.DictReader(open(f'{OUT}/epmc_gene_check.tsv'), delimiter='\t'):
        done.add((r['gene'], r['ctx']))
except FileNotFoundError:
    pass
todo = [(g, x, e) for (g, x), e in extra_pairs.items() if (g, x) not in done]
print('extra gene-ctx to check:', len(todo))

BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
CONTEXT = {
    'retina': '(retina OR retinal OR photoreceptor OR macula OR "retinal pigment")',
    'membrane': '(eye OR ocular OR retinal OR choroid OR "optic nerve")',
    'face': '(cornea OR corneal OR conjunctiva OR conjunctival OR "ocular surface" OR limbal)',
    'lacrimal': '(lacrimal OR tear OR "dry eye" OR meibomian)',
    'kb9': '(ocular OR eye OR conjunctiva OR cornea OR "ocular surface")',
}
def epmc(query, pageSize=1):
    url = BASE + '?' + urllib.parse.urlencode({'query': query, 'format': 'json', 'pageSize': pageSize, 'resultType': 'core'})
    for att in range(4):
        try:
            with urllib.request.urlopen(url, timeout=45) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print('RETRY', e, file=sys.stderr); time.sleep(3 + att * 4)
    return None

res = []
for g, x, entries in sorted(todo):
    q = f'"{g}" AND {CONTEXT[x]} AND SPECIES:"HUMAN"'
    d = epmc(q)
    n = d['hitCount'] if d else -1
    verdict = 'B_scarce_1_5' if 1 <= n <= 5 else ('B_none' if n == 0 else ('A_candidate' if n > 5 else 'API_FAIL'))
    res.append(dict(gene=g, ctx=x, n_eye_hits=n, n_entries=len(entries),
                    entries=';'.join(sorted(entries))[:200], verdict=verdict, note='was_S2_ctx_mismatch'))
    print(g, x, n, verdict, flush=True)
    time.sleep(0.5)
if res:
    with open(f'{OUT}/epmc_gene_check_extra.tsv', 'w', newline='') as w:
        wr = csv.DictWriter(w, fieldnames=list(res[0].keys()), delimiter='\t')
        wr.writeheader(); wr.writerows(res)
print('extra checks done')
