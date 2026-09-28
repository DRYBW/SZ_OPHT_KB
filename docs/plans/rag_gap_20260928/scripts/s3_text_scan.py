#!/usr/bin/env python3
"""RAGGAP step 3 — chunk 文本 gene-token 扫描（只读，不碰向量）。
对 425 个 KB 基因做词边界大写 token 匹配 → gene -> (n_chunks, n_papers, top pmids, tissue 分布)。
产出 out/corpus_text_gene.tsv + 全量 paper_textgene.pkl（gene→set(pmid) 供逐行 join）。
"""
import re, json, pickle, collections
import pyarrow.parquet as pq

DB = '/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.1_2026-09'
OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'

genes = set()
with open(f'{OUT}/kb_entries_genes.tsv') as f:
    next(f)
    for line in f:
        genes.add(line.split('\t')[2])
genes = {g for g in genes if re.fullmatch(r'[A-Z][A-Z0-9-]{1,9}', g)}
print('query genes:', len(genes))

# 词边界 alternation（长名优先防止子串吞并）
alt = '|'.join(sorted((re.escape(g) for g in genes), key=len, reverse=True))
RX = re.compile(rf'(?<![A-Za-z0-9-])({alt})(?![A-Za-z0-9-])')
TOK = re.compile(r'(?<![a-z0-9])[A-Z][A-Z0-9-]{2,9}(?![a-z])')  # 宽松大写 token 统计噪声用

gene_chunks = collections.Counter()
gene_papers = collections.defaultdict(set)
gene_tissue = collections.defaultdict(collections.Counter)
n = 0
pf = pq.ParquetFile(f'{DB}/chunks.parquet')
for i in range(pf.metadata.num_row_groups):
    t = pf.read_row_group(i, columns=['paper_id', 'tissue', 'text']).to_pylist()
    for r in t:
        n += 1
        pm = str(r['paper_id'])
        hits = set(RX.findall(r['text'] or ''))
        for g in hits:
            gene_chunks[g] += 1
            gene_papers[g].add(pm)
            gene_tissue[g][r.get('tissue') or '?'] += 1
print('chunks scanned:', n)

papers_meta = {}
with open(f'{OUT}/corpus_papers.tsv') as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t')
        papers_meta[p[0]] = dict(chunks=int(p[1]), pre=int(p[2]))

with open(f'{OUT}/corpus_text_gene.tsv', 'w') as w:
    w.write('gene\tchunks_text_mention\tn_papers\ttop_pmids\ttissue_top\n')
    for g in sorted(gene_chunks):
        tops = sorted(gene_papers[g], key=lambda x: -papers_meta.get(x, {}).get('chunks', 0))[:5]
        tis = ';'.join(f'{k}:{v}' for k, v in gene_tissue[g].most_common(6))
        w.write(f"{g}\t{gene_chunks[g]}\t{len(gene_papers[g])}\t{','.join(tops)}\t{tis}\n")

with open(f'{OUT}/gene_paper_map.pkl', 'wb') as w:
    pickle.dump({g: set(s) for g, s in gene_papers.items()}, w)
print('genes with text mentions in corpus:', len(gene_chunks))
