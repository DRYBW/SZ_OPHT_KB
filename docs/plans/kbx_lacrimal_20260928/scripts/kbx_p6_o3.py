#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P6: O3 定性 sanity（RULING §4/PREREG §8 分支：不发任何票）。
三词条 core × 组织池簇表达域拓扑 + 腺泡酶原缺口佐证。输入=p2 主档产物 h5ad（含 kbx_cluster）。"""
import json
import numpy as np
import pandas as pd
import anndata as ad
import scipy.sparse as sp

BASE = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
a = ad.read_h5ad(f'{BASE}/out/kbx_clustered_tissue.h5ad')

TERM_CORE = {'Lacrimal_secretory_tearcell': ['LACRT', 'SCGB1D1', 'SCGB2A1', 'CST4', 'CST1', 'MUC7'],
             'Lacrimal_duct_epithelial': ['PRR27'],
             'Lacrimal_myoepithelial': []}
ZYM = ['PRSS1', 'CTRB1', 'CTRB2', 'PNLIP', 'CELA2A', 'AMY2A']
GENES = sorted({g for gs in TERM_CORE.values() for g in gs} | set(ZYM))

C = a.layers['counts_int32'].tocsr().astype(np.float64)
lib = np.asarray(C.sum(axis=1)).ravel(); lib[lib == 0] = 1
X = np.asarray((sp.diags(1e4 / lib) @ C).todense(), dtype=np.float32)
vn = np.array(list(map(str, a.var_names)))
cid = a.obs['kbx_cluster'].astype(str).values

rows = []
for c in sorted(np.unique(cid), key=lambda x: int(x.split('::')[1])):
    m = cid == c
    n = int(m.sum())
    if n < 30:
        continue
    rec = {'cluster': c, 'n_cells': n}
    for g in GENES:
        if not (vn == g).any():
            rec[f'det_{g}'] = None; rec[f'cp10k_{g}'] = None
            continue
        j = int(np.where(vn == g)[0][0])
        rec[f'det_{g}'] = round(float((X[m][:, j] >= 5).mean()), 3)
        rec[f'cp10k_{g}'] = round(float(X[m][:, j].mean()), 1)
    for t, gs in TERM_CORE.items():
        if gs:
            rec[f'n_core>=0.3det_{t}'] = int(sum(1 for g in gs if (rec.get(f'det_{g}') or 0) >= 0.3))
    rows.append(rec)
t = pd.DataFrame(rows)
t.to_csv(f'{BASE}/out/kbx_o3_topology.tsv', sep='\t', index=False)
pd.set_option('display.width', 250)
print(t[['cluster', 'n_cells', 'det_LACRT', 'det_MUC7', 'det_CST1', 'det_CST4', 'det_SCGB1D1',
         'det_SCGB2A1', 'det_PRR27', 'n_core>=0.3det_Lacrimal_secretory_tearcell',
         'det_PRSS1', 'det_CTRB1', 'det_PNLIP']].to_string(index=False))
print('\nWROTE out/kbx_o3_topology.tsv')
