#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P3: 证据面构建（PREREG_v2 §6）。
输入：out/kbx_clustered_{tissue,organoid}.h5ad（本卡 p2 产物）+ 三词条 core（sha 4e7e001a… 只读）
输出：face/EV_DIGEST_SLIM_kbx.jsonl + face/build_meta.json
纪律：top_genes 展示窗=前20，digest_pool=前60；无 lit/无组成参考/无 pred_hint（§6.2）。"""
import json, os, sys, time, hashlib
import numpy as np
import pandas as pd
import anndata as ad
import scanpy as sc

BASE = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
TERMS = {  # §6.1 被测词条（core 逐字抄录自 markers_v6_lacrimal_increment.json sha 4e7e001a…）
    'Lacrimal_secretory_tearcell': ['LACRT', 'SCGB1D1', 'SCGB2A1', 'CST4', 'CST1', 'MUC7'],
    'Lacrimal_duct_epithelial': ['PRR27'],
    'Lacrimal_myoepithelial': [],
}
NC_MIN = 30
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()

pool_h5 = {'TIS': 'tissue'}  # 定稿 §2.2：定量题面=组织池唯一；类器官=附录不投票
rows_out = []
meta = {'terms_sha_source': sha('/mnt/D/EyeKB/kb/markers/markers_v6_lacrimal_increment.json')}
for pref, pool in pool_h5.items():
    a = ad.read_h5ad(f'{BASE}/out/kbx_clustered_{pool}.h5ad')
    a.layers['counts'] = a.layers['counts_int32']
    a.X = a.layers['counts'].astype('float32')
    sc.pp.normalize_total(a, target_sum=1e4)
    sc.pp.log1p(a)
    sc.tl.rank_genes_groups(a, 'kbx_cluster', method='wilcoxon', n_genes=60)
    dft = pd.DataFrame(a.uns['rank_genes_groups']['names'])
    cid2genes = {c: [str(x) for x in dft[c].tolist()] for c in dft.columns}
    for cid in sorted(cid2genes, key=lambda x: int(x.split('::')[1])):
        m = a.obs['kbx_cluster'] == cid
        n = int(m.sum())
        if n < NC_MIN:
            continue
        pool_genes = cid2genes[cid]
        P = {g.upper() for g in pool_genes}
        hits, rank = {}, []
        for t, genes in TERMS.items():
            shared = [g for g in genes if g.upper() in P]
            if shared:
                hits[t] = shared
        rank = sorted([{'cell_type': t, 'n_shared': len(g)} for t, g in hits.items()],
                      key=lambda x: (-x['n_shared'], x['cell_type']))[:5]
        obs = a.obs.loc[m]
        rows_out.append({
            'cluster_id': cid, 'member': 'LG',
            'material': {'species': 'homo sapiens', 'tissue': 'lacrimal_gland', 'pool': pool},
            'n_cells': n,
            'qc': f"median_n_genes={float(obs['n_genes_by_counts'].median()):.0f}|median_pct_mt={float(obs['pct_counts_mt'].median()):.2f}",
            'sorts': '|'.join(f'{k}:{v}' for k, v in obs['author_sort'].astype(str).value_counts().items()),
            'donors': '|'.join(f'{k}:{v}' for k, v in obs['patient_number'].astype(str).value_counts().items()),
            'top_genes': pool_genes[:20], 'top_genes_sym': pool_genes[:20],
            'digest_pool': pool_genes,
            'kb_celltype_ranking': rank, 'kb_gene_hits': hits,
        })

face_path = f'{BASE}/face/EV_DIGEST_SLIM_kbx.jsonl'
os.makedirs(f'{BASE}/face', exist_ok=True)
with open(face_path, 'w', encoding='utf-8') as f:
    for r in rows_out:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

# 票量断言（§2.4）：3×N<=120
N = len(rows_out)
if N > 40:
    rows_out = sorted(rows_out, key=lambda r: -r['n_cells'])[:40]
    with open(face_path, 'w', encoding='utf-8') as f:
        for r in rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f'TRUNCATED to top40 by n_cells (was {N})')
    N = 40
assert 3 * N <= 120, f'vote cap exceeded: {N} clusters'

# 自检：digest_pool<=60；window<=20；词条 ranking 只含三词条
assert all(len(r['digest_pool']) <= 60 for r in rows_out)
assert all(len(r['top_genes']) <= 20 for r in rows_out)
assert all(set(x['cell_type'] for x in r['kb_celltype_ranking']) <= set(TERMS) for r in rows_out)

json.dump({'card': 't_0fb07fd6', 'prereg': 'KBX_PREREG_v2.md',
           'prereg_sha256': sha(f'{BASE}/KBX_PREREG_v2.md'),
           'n_face': N, 'votes': 3 * N,
           'face_sha256': sha(face_path),
           'inputs': {'clustered_tissue': sha(f'{BASE}/out/kbx_clustered_tissue.h5ad'),
                       'clustered_organoid': sha(f'{BASE}/out/kbx_clustered_organoid.h5ad')},
           'row_order': [r['cluster_id'] for r in rows_out],
           'written_at': time.strftime('%F %T')},
          open(f'{BASE}/face/build_meta.json', 'w'), ensure_ascii=False, indent=1)
print(f'BUILT {face_path} n={N} votes={3*N} sha={sha(face_path)[:16]}')
for r in rows_out:
    print(f"  {r['cluster_id']:8s} n={r['n_cells']:4d} rank={json.dumps(r['kb_celltype_ranking'], ensure_ascii=False)[:80]}")
