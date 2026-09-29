#!/usr/bin/env python3
"""Decide DS1 'MG' class identity: per-cell detection rate of Muller vs microglia marker sets."""
import numpy as np, h5py
from scipy.sparse import csr_matrix
def dec(x): return x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x)
p="<STORE>/data/shekhar_annotated/human_homo_sapiens_annotated.h5ad"
with h5py.File(p,"r") as f:
    g=f["X"]; X=csr_matrix((g["data"][:],g["indices"][:],g["indptr"][:]),shape=tuple(int(x) for x in g.attrs["shape"])).tocsr().astype(np.float32)
    genes=[dec(x) for x in f["var"]["gene_id"][:]]
    gc=f["obs"]["shekhar_class"]; cats=[dec(c) for c in gc["categories"][:]]; lab=np.array(cats)[gc["codes"][:]]
idx={g:i for i,g in enumerate(genes)}
SETS={"Muller":["RLBP1","GLUL","AQP4","S100B","CRYAB","SLC1A3"],
      "microglia":["C1QA","C1QB","CX3CR1","P2RY12","TMEM119","CSF1R","AIF1","TYROBP"],
      "astro":["GFAP","AQP1"],"Proliferating":["MKI67"],"RPE":["BEST1","RPE65"]}
rng=np.random.default_rng(7)
for cls in ["MG","RGC","Rod"]:
    rows=np.where(lab==cls)[0]
    sel=rng.choice(rows,min(4000,len(rows)),replace=False)
    sub=X[sel]
    print(f"== DS1 class {cls} n={len(rows)} sampled={len(sel)}")
    for name,gs in SETS.items():
        hit=[(g,idx[g]) for g in gs if g in idx]
        percell=[ (np.asarray(sub[:,j].todense()).ravel()>0).mean() for _,j in hit]
        print(f"   {name}: " + " ".join(f"{g}={pc:.3f}" for (g,_),pc in zip(hit,percell)))
