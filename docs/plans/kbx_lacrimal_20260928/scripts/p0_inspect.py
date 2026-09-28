#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P0: GSE164403 h5ad 审计 —— obs 列、作者标签列分布、层结构。只读。"""
import anndata as ad
import numpy as np, pandas as pd, json
a = ad.read_h5ad('/mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad')
print('shape', a.shape)
print('layers', list(a.layers.keys()))
print('X dtype', a.X.dtype, type(a.X))
print('obs cols', list(a.obs.columns))
print('var cols', list(a.var.columns))
print()
for c in a.obs.columns:
    try:
        vc = a.obs[c].astype(str).value_counts()
        print(f'=== {c} ({len(vc)} distinct) ===')
        print(vc.head(25).to_string())
        print()
    except Exception as e:
        print(c, 'ERR', e)
