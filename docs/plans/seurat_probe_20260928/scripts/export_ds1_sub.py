#!/usr/bin/env python3
"""Export DS1 random 20k subset (counts mtx + features + truth) for G1 pilot, seed=20260928."""
import numpy as np, h5py, scipy.io as sio
from scipy.sparse import csr_matrix
import pandas as pd

W = "<EYEKB>/plans/seurat_probe_20260928"
DS1 = "<STORE>/data/shekhar_annotated/human_homo_sapiens_annotated.h5ad"
def dec(x): return x.decode() if isinstance(x,(bytes,np.bytes_)) else str(x)

with h5py.File(DS1,"r") as f:
    g=f["X"]; X=csr_matrix((g["data"][:],g["indices"][:],g["indptr"][:]),shape=tuple(int(x) for x in g.attrs["shape"]))
    genes=[dec(x) for x in f["var"]["gene_id"][:]]
    cells=[dec(x) for x in f["obs"]["barcode"][:]]
    gc=f["obs"]["shekhar_class"]; cats=[dec(c) for c in gc["categories"][:]]; lab=np.array(cats)[gc["codes"][:]]
rng=np.random.default_rng(20260928)
idx=np.sort(rng.choice(X.shape[0],20000,replace=False))
sub=X[idx]
print("subset",sub.shape,"nnz",sub.nnz,"truth dist", dict(zip(*np.unique(lab[idx],return_counts=True))))
sio.mmwrite(f"{W}/data/DS1sub20k_counts.mtx", sub.T.tocoo())
open(f"{W}/data/DS1sub20k_features.tsv","w").write("\n".join(genes)+"\n")
open(f"{W}/data/DS1sub20k_barcodes.tsv","w").write("\n".join([cells[i] for i in idx])+"\n")
pd.DataFrame({"barcode":[cells[i] for i in idx],"truth":lab[idx]}).to_csv(f"{W}/data/DS1sub20k_truth.tsv",sep="\t",index=False)
print("SUBSET DONE")
