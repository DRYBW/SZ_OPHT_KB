import anndata as ad
import pandas as pd
import numpy as np

a = ad.read_h5ad('/mnt/D/RetinaAging/retinaA1_data_GSE325478/AAA/MRCA all cells h5ad.h5ad', backed='r')
print('shape', a.shape)
print('obs cols:', list(a.obs.columns))
for c in a.obs.columns:
    low = c.lower()
    if any(k in low for k in ('cell', 'type', 'label', 'clust', 'anno')):
        v = a.obs[c]
        try:
            arr = np.asarray(v)
        except Exception:
            try:
                arr = np.asarray(v.to_dense())
            except Exception:
                arr = np.asarray(pd.Categorical(v).categories)
        if arr.ndim == 1:
            u = pd.Series(arr).astype(str).unique()
            print(c, ':', len(u), 'uniq;', list(u)[:16])
        else:
            print(c, 'shape', arr.shape)
