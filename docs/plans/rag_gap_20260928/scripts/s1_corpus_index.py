#!/usr/bin/env python3
"""RAGGAP step 1 — 语料库侧索引（零下载；只读 v2.1 papers.jsonl + chunks 非向量列）。
产出:
  out/corpus_papers.tsv      PMID -> n_chunks/title/pmcid/year/journal/is_preprint（含 ghost 标记）
  out/corpus_gene_index.tsv  gene -> 在库 chunk 数 / 支持论文数 / 代表 PMID(top5) / 组织标签分布
"""
import json, collections, pyarrow.parquet as pq, os

DB = '/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.1_2026-09'
OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'

# ---- papers.jsonl ----
papers = {}
with open(os.path.join(DB, 'papers.jsonl')) as f:
    for line in f:
        d = json.loads(line)
        pm = str(d['paper_id'])
        papers[pm] = dict(n_chunks=int(d.get('n_chunks', 0)),
                          title=' '.join((d.get('title') or '').split()),
                          pmcid=d.get('pmcid') or '', year=d.get('year') or '',
                          journal=' '.join((d.get('journal') or '').split()),
                          is_preprint=d.get('is_preprint', 0), tissues=';'.join(d.get('tissues') or []))
with open(os.path.join(OUT, 'corpus_papers.tsv'), 'w') as w:
    w.write('pmid\tn_chunks\tis_preprint\tyear\tjournal\tpmcid\ttissues\tghost\ttitle\n')
    for pm, d in sorted(papers.items()):
        w.write(f"{pm}\t{d['n_chunks']}\t{d['is_preprint']}\t{d['year']}\t{d['journal']}\t{d['pmcid']}\t{d['tissues']}\t{1 if d['n_chunks']==0 else 0}\t{d['title']}\n")
ghosts = sum(1 for d in papers.values() if d['n_chunks'] == 0)
print(f"papers={len(papers)} with_chunks={len(papers)-ghosts} ghost0={ghosts}")

# ---- chunks: 非向量列，逐 row group 流式，防内存爆 ----
pf = pq.ParquetFile(os.path.join(DB, 'chunks.parquet'))
gene_chunks = collections.Counter()
gene_papers = collections.defaultdict(set)
gene_tissue = collections.defaultdict(collections.Counter)
ct_chunks = collections.Counter()          # cell_type_mentioned -> chunks
ct_papers = collections.defaultdict(set)
n = 0
for i in range(pf.metadata.num_row_groups):
    t = pf.read_row_group(i, columns=['paper_id', 'marker_genes', 'cell_type_mentioned', 'tissue_labels']).to_pylist()
    for r in t:
        n += 1
        pm = str(r['paper_id'])
        for g in (r.get('marker_genes') or []):
            g = g.strip()
            if g:
                gene_chunks[g] += 1; gene_papers[g].add(pm)
                for tl in (r.get('tissue_labels') or []):
                    gene_tissue[g][tl] += 1
        for c in (r.get('cell_type_mentioned') or []):
            c = c.strip()
            if c:
                ct_chunks[c] += 1; ct_papers[c].add(pm)
print('chunks scanned:', n)

with open(os.path.join(OUT, 'corpus_gene_index.tsv'), 'w') as w:
    w.write('gene\tchunks\tn_papers\ttop_pmids\ttissue_top\n')
    for g in sorted(gene_chunks):
        tops = sorted(gene_papers[g], key=lambda p: -papers.get(p, {}).get('n_chunks', 0))[:5]
        tis = ';'.join(f'{k}:{v}' for k, v in gene_tissue[g].most_common(6))
        w.write(f"{g}\t{gene_chunks[g]}\t{len(gene_papers[g])}\t{','.join(tops)}\t{tis}\n")
with open(os.path.join(OUT, 'corpus_celltype_index.tsv'), 'w') as w:
    w.write('cell_type\tchunks\tn_papers\n')
    for c in sorted(ct_chunks):
        w.write(f"{c}\t{ct_chunks[c]}\t{len(ct_papers[c])}\n")
print('unique genes with marker-gene hits:', len(gene_chunks))
print('unique cell types mentioned:', len(ct_chunks))
