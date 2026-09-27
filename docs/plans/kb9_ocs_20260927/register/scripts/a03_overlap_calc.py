#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-A03: 新词条 agg 参考池 × D002 评测 33 簇 study/donor 重叠登记表。
只读输入: agg_kb6b_v1.npz(池定义+层键) / D002_allcells_578K.h5ad(obs only) / Q6_clusters.tsv(评测面细胞)。
零 LLM，确定性。输出 register/A03_OVERLAP_REGISTRY.tsv (+stdout 摘要)。
"""
import numpy as np, json, collections
import anndata as ad

AGG = '/mnt/D/EyeKB/plans/kb6b_face_20260925/out/agg_kb6b_v1.npz'
H5  = '/mnt/D/OcularKB/data/D002_ocularsurface/D002_allcells_578K.h5ad'
Q6  = '/mnt/D/EyeKB/plans/evalset/clustering/Q6_clusters.tsv'
OUT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927/register/A03_OVERLAP_REGISTRY.tsv'

# 新词条参考池定义（KB9_PREREG §1.1 冻结；与 out/kb9_term_candidates.json 一致）
POOLS = {
    'Melanocyte': ['Melanocytes'],
    'Schwann': ['Schwann_M', 'Schwann_N'],
    'Conj_epithelium_suprabasal': ['Conj_suprabasal'],
    'Limbus_Sclera_fibroblast_C1': ['Limbus/Sclera Fibroblasts - C1'],
}

z = np.load(AGG, allow_pickle=True)
cats = json.loads(str(z['layer_cats']))
auth = [str(a) for a in cats['AUTHOR']]
donors = [str(d) for d in cats['DONOR']]
studies = [str(s) for s in cats['STUDY']]
ND = len(donors)
offs = json.loads(str(z['offs']))
oA, nA = offs['DONORxAUTHOR']
da_keys = z['da_keys'].astype(np.int64); NCda = z['NC'][oA:oA+nA].astype(np.int64)
assert nA == len(da_keys), (nA, len(da_keys))
da_d = da_keys // len(auth); da_a = da_keys % len(auth)

# 池的 (study,donor) 细胞构成（来自 npz DONORxAUTHOR 层 = 规则开发用聚合的同一账本）
pool_layer = {}
for term, members in POOLS.items():
    st = collections.Counter(); do = collections.Counter()
    cells = 0
    for a in members:
        ai = auth.index(a)
        m = da_a == ai
        for d, nc in zip(da_d[m], NCda[m]):
            si = int(d) // ND; di = int(d) % ND
            st[studies[si]] += int(nc); do[(studies[si], donors[di])] += int(nc); cells += int(nc)
    pool_layer[term] = {'cells': cells, 'studies': st, 'donors': do}

# 评测面 33 簇（Q6_clusters.tsv: barcode, leiden, donor, truth）—— obs 只读
ev_barcodes = set()
ev_donor_study = collections.Counter()
with open(Q6) as f:
    hdr = f.readline()
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) < 4: continue
        ev_barcodes.add(p[0])
        ev_donor_study[p[2]] += 1
print('eval cells:', len(ev_barcodes), 'distinct donors col:', len(ev_donor_study))

a = ad.read_h5ad(H5, backed='r')
o = a.obs
idx = o.index.astype(str)
col_study = o['study'].astype(str).values
col_donor = o['donor_id'].astype(str).values
col_auth = o['author_cell_type'].astype(str).values
is_ev = np.fromiter((b in ev_barcodes for b in idx), dtype=bool, count=len(idx))
print('D002 cells:', len(idx), 'barcode join hits (eval∩D002):', int(is_ev.sum()))

rows = []
for term, members in POOLS.items():
    m_pool = np.isin(col_auth, members)
    cells_pool = int(m_pool.sum())
    ev_in_pool = int((m_pool & is_ev).sum())
    st_pool = collections.Counter(col_study[m_pool])
    do_pool = set(zip(col_study[m_pool], col_donor[m_pool]))
    st_ev = collections.Counter(col_study[m_pool & is_ev])
    do_ev = set(zip(col_study[m_pool & is_ev], col_donor[m_pool & is_ev]))
    stx = ';'.join(f'{k}={v}' for k, v in sorted(st_pool.items(), key=lambda x: -x[1]))
    rows.append({
        'term': term, 'pool_members': '|'.join(members),
        'pool_cells_h5ad': cells_pool, 'pool_cells_npz_layer': pool_layer[term]['cells'],
        'eval33_cells_in_pool': ev_in_pool,
        'pool_studies_n': len(st_pool), 'eval_studies_in_pool_n': len(st_ev),
        'pool_donors_n': len(do_pool), 'eval_donors_in_pool_n': len(do_ev),
        'pool_study_breakdown': stx,
    })

with open(OUT, 'w') as f:
    f.write('\t'.join(rows[0].keys()) + '\n')
    for r in rows:
        f.write('\t'.join(str(r[k]) for k in r) + '\n')
print(json.dumps(rows, ensure_ascii=False, indent=1))
print('WROTE', OUT)
