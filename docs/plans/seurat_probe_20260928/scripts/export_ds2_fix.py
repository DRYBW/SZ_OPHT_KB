#!/usr/bin/env python3
"""Re-export DS2 counts mtx + features (fixed categorical indexing)."""
import numpy as np, h5py, scipy.io as sio
from scipy.sparse import csr_matrix
W="<EYEKB>/plans/seurat_probe_20260928"
p="<STORE>/data/GSE137400/lukowski2019_retina.h5ad"
def dec(x): return x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x)
with h5py.File(p,"r") as f:
    g=f["raw/X"]; X=csr_matrix((g["data"][:],g["indices"][:],g["indptr"][:]),shape=tuple(int(x) for x in g.attrs["shape"]))
    fn=f["raw"]["var"]["feature_name"]
    fcats=np.array([dec(c) for c in fn["categories"][:]]); codes=fn["codes"][:]
    genes=np.array([fcats[i] if i>=0 else "NA" for i in codes])
    nm=f["obs"].attrs.get("_index","_index"); nm=dec(nm)
    cells=[dec(x) for x in (f["obs"]["_index"][:] if "_index" in f["obs"] else f["obs"][nm][:])]
print("genes",len(genes),"empty_name_genes",int((genes=="").sum()),"NA",int((genes=="NA").sum()),"X",X.shape)
def derep(names):
    seen={}; out=[]
    for n in names:
        n = n if n not in ("","NA") else "UNNAMED"
        if n in seen: seen[n]+=1; out.append(f"{n}_{seen[n]}")
        else: seen[n]=0; out.append(n)
    return out
g2=derep(genes); c2=derep([str(c) for c in cells])
sio.mmwrite(f"{W}/data/DS2_counts.mtx", X.T.tocoo())
open(f"{W}/data/DS2_features.tsv","w").write("\n".join(g2)+"\n")
open(f"{W}/data/DS2_barcodes.tsv","w").write("\n".join(c2)+"\n")
print("DS2 REEXPORT DONE", len(g2), len(c2))
