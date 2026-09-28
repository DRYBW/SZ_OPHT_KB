#!/usr/bin/env python3
"""RAGGAP step 4 — 覆盖矩阵 join + 初判 (S1/S2/S3 + 档级预分类)。
输入: out/kb_entries_genes.tsv, out/corpus_papers.tsv, out/corpus_text_gene.tsv,
      out/corpus_gene_index.tsv (marker_genes 面板列), out/gene_paper_map.pkl
输出: out/coverage_matrix.tsv (逐 library×entry×gene)
      out/gap_items.tsv (S3 且无库内支撑 → 待 EPMC 外部核查定 A/B)
"""
import csv, pickle, collections, re

OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'

# corpus papers
papers = {}
with open(f'{OUT}/corpus_papers.tsv') as f:
    rd = csv.DictReader(f, delimiter='\t')
    for r in rd:
        papers[r['pmid']] = dict(chunks=int(r['n_chunks']), ghost=int(r['ghost']), pre=int(r['is_preprint']),
                                 year=r['year'], journal=r['journal'], pmcid=r['pmcid'], title=r['title'])

# gene text mentions
gtxt = {}
with open(f'{OUT}/corpus_text_gene.tsv') as f:
    rd = csv.DictReader(f, delimiter='\t')
    for r in rd:
        gtxt[r['gene']] = dict(chunks=int(r['chunks_text_mention']), npapers=int(r['n_papers']),
                               top=r['top_pmids'], tissue=r['tissue_top'])

# gene marker-panel index
gpanel = {}
with open(f'{OUT}/corpus_gene_index.tsv') as f:
    rd = csv.DictReader(f, delimiter='\t')
    for r in rd:
        gpanel[r['gene']] = dict(chunks=int(r['chunks']), npapers=int(r['n_papers']), top=r['top_pmids'])

gene_paper = pickle.load(open(f'{OUT}/gene_paper_map.pkl', 'rb'))  # gene -> set(pmid)

rows = []
with open(f'{OUT}/kb_entries_genes.tsv') as f:
    rd = csv.DictReader(f, delimiter='\t')
    for r in rd:
        cited = [p for p in (r['cited_pmids'].split(',') if r['cited_pmids'] else []) if p]
        ctx = [p for p in (r['pmid_context'].split(',') if r['pmid_context'] else []) if p]
        cov = [p for p in cited if p in papers and papers[p]['chunks'] > 0]
        ghost = [p for p in cited if p in papers and papers[p]['chunks'] == 0]
        absent = [p for p in cited if p not in papers]
        ctx_cov = [p for p in ctx if p in papers and papers[p]['chunks'] > 0]
        g = r['gene']
        tx = gtxt.get(g)
        pn = gpanel.get(g)
        # 支撑判定
        if '_' in g or not re.fullmatch(r'[A-Z][A-Z0-9-]{1,9}', g):
            s = 'S0_not_a_gene'   # v6 状态标签(如 APC_MHCII_HIGH)/伪基因符号
        elif cov:
            s = 'S1_chain_covered'
        elif tx and tx['npapers'] > 0:
            s = 'S2_gene_in_corpus'
        elif ctx_cov:
            s = 'S2b_context_only'
        else:
            s = 'S3_no_corpus_support'
        rows.append(dict(r, chain_covered=','.join(cov), chain_ghost=','.join(ghost),
                         chain_absent=','.join(absent), ctx_covered=','.join(ctx_cov),
                         text_chunks=(tx['chunks'] if tx else 0), text_papers=(tx['npapers'] if tx else 0),
                         text_top=(tx['top'] if tx else ''), panel_chunks=(pn['chunks'] if pn else 0),
                         support=s))

hdr = list(rows[0].keys())
with open(f'{OUT}/coverage_matrix.tsv', 'w', newline='') as w:
    wr = csv.DictWriter(w, fieldnames=hdr, delimiter='\t')
    wr.writeheader(); wr.writerows(rows)

cnt = collections.Counter(r['support'] for r in rows)
print('support tally:', dict(cnt))
by_lib = collections.defaultdict(collections.Counter)
for r in rows:
    lib = r['library'].replace(':prov', '')
    by_lib[lib][r['support']] += 1
for lib in sorted(by_lib):
    print(f"{lib:14s}", dict(by_lib[lib]))

# gap 明细: S3 行 → 按 gene 去重供外部核查
gap_genes = sorted({r['gene'] for r in rows if r['support'] == 'S3_no_corpus_support'})
with open(f'{OUT}/gap_genes.txt', 'w') as w:
    w.write('\n'.join(gap_genes) + '\n')
gap_pmids = sorted({p for r in rows if r['support'] == 'S3_no_corpus_support' and r['chain_absent']
                    for p in r['chain_absent'].split(',') if p})
with open(f'{OUT}/gap_absent_pmids.txt', 'w') as w:
    w.write('\n'.join(gap_pmids) + '\n')
print('S3 rows:', cnt['S3_no_corpus_support'], '| distinct gap genes:', len(gap_genes), '| distinct absent cited PMIDs:', len(gap_pmids))
