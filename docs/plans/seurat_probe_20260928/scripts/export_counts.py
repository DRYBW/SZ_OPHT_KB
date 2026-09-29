#!/usr/bin/env python3
"""Export DS1(shekhar human) & DS2(lukowski) raw counts to MatrixMarket + truth label TSVs,
plus a marker-mean probe to decide whether DS1 'MG' == microglia or Mller glia."""
import json
import numpy as np
import h5py
import scipy.io as sio
from scipy.sparse import csr_matrix

W = "<EYEKB>/plans/seurat_probe_20260928"
DS1 = "<STORE>/data/shekhar_annotated/human_homo_sapiens_annotated.h5ad"
DS2 = "<STORE>/data/GSE137400/lukowski2019_retina.h5ad"

def read_sparse(f, path):
    g = f[path] if path in f else None
    if g is None: return None
    d = g["data"][:]; i = g["indices"][:]; p = g["indptr"][:]
    shape = tuple(int(x) for x in g.attrs["shape"])
    return csr_matrix((d, i, p), shape=shape)

def derep(names):
    seen = {}
    out = []
    for n in names:
        if n in seen:
            seen[n] += 1
            out.append(f"{n}_{seen[n]}")
        else:
            seen[n] = 0
            out.append(n)
    return out

def dec(x):
    return x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x)

# ---------- DS1 ----------
with h5py.File(DS1, "r") as f:
    X = read_sparse(f, "X")
    genes = [dec(x) for x in f["var"]["gene_id"][:]]
    cells = [dec(x) for x in f["obs"]["barcode"][:]]
    lab = [dec(x) for x in f["obs"]["shekhar_class"].__getitem__(
        slice(None)) if True] if False else None
    gcol = f["obs"]["shekhar_class"]
    cats = [dec(c) for c in gcol["categories"][:]]
    codes = gcol["codes"][:]
    lab1 = np.array(cats)[codes]
print(f"DS1 X={X.shape} nnz={X.nnz} genes_dup={len(genes)-len(set(genes))} cells_dup={len(cells)-len(set(cells))}")
g1 = derep(genes); cells = derep(cells)
sio.mmwrite(f"{W}/data/DS1_counts.mtx", X.T.tocoo())
open(f"{W}/data/DS1_features.tsv","w").write("\n".join(g1)+"\n")
open(f"{W}/data/DS1_barcodes.tsv","w").write("\n".join(cells)+"\n")
import pandas as pd
pd.DataFrame({"barcode": cells, "truth": lab1}).to_csv(f"{W}/data/DS1_truth.tsv", sep="\t", index=False)
print("DS1 truth dist:", dict(zip(*np.unique(lab1, return_counts=True))))

# marker probe on DS1 (which glia is MG?)
MARK = {"Mller": ["RLBP1","GLUL","AQP4","S100B","CRYAB"],
        "microglia": ["C1QA","C1QB","CX3CR1","P2RY12","TMEM119","CSF1R"]}
idx = {g:i for i,g in enumerate(g1)}
Xc = X.tocsr()
rng = np.random.default_rng(0)
sel = rng.choice(X.shape[0], 20000, replace=False)
for cls in sorted(set(lab1)):
    rows = sel[np.array(lab1)[sel]==cls][:3000]
    sub = Xc[rows]
    tot = np.asarray(sub.sum(0)).ravel()
    for name, gs in MARK.items():
        hit = [(g, idx[g]) for g in gs if g in idx]
        if hit:
            frac = np.mean([(tot[j]>0).mean() for _,j in hit])
            print(f"  DS1 {cls} {name}: mean detection frac={frac:.3f} ({[g for g,_ in hit]})")

# ---------- DS2 ----------
with h5py.File(DS2, "r") as f:
    Xr = read_sparse(f, "raw/X")
    fn = f["raw"]["var"]["feature_name"]
    if isinstance(fn, h5py.Group):
        fcats = [dec(c) for c in fn["categories"][:]]
        genes = np.array([fnc if i >= 0 else "NA" for i, fnc in zip(fn["codes"][:], fcats)])
    else:
        genes = [dec(x) for x in fn[:]]
    nm = f["obs"].attrs.get("_index", "_index")
    if isinstance(nm, bytes): nm = nm.decode()
    cells = [dec(x) for x in (f["obs"]["_index"][:] if "_index" in f["obs"] else f["obs"][nm][:])]
    gcol = f["obs"]["author_cell_type"]
    cats = [dec(c) for c in gcol["categories"][:]]
    codes = gcol["codes"][:]
    lab2 = np.array(cats)[codes]
print(f"DS2 X={Xr.shape} nnz={Xr.nnz} genes_dup={len(genes)-len(set(genes))} cells_dup={len(cells)-len(set(cells))}")
g2 = derep(genes); cells = derep(cells)
sio.mmwrite(f"{W}/data/DS2_counts.mtx", Xr.T.tocoo())
open(f"{W}/data/DS2_features.tsv","w").write("\n".join(g2)+"\n")
open(f"{W}/data/DS2_barcodes.tsv","w").write("\n".join(cells)+"\n")
pd.DataFrame({"barcode": cells, "truth": lab2}).to_csv(f"{W}/data/DS2_truth.tsv", sep="\t", index=False)
print("DS2 truth dist:", dict(sorted(zip(*np.unique(lab2, return_counts=True)), key=lambda kv:-kv[1])))
pd.Series(lab2).astype(str).to_csv(f"{W}/data/DS2_author_labels_raw.csv")
# save a quick provenance record
prov = {"DS1": {"path": DS1, "n": int(X.shape[0]), "genes": len(g1), "counts_int": bool(np.allclose(X.data[:5000], np.round(X.data[:5000]))), "sample_cells": [str(c) for c in cells[:3]]},
        "DS2": {"path": DS2, "n": int(Xr.shape[0]), "genes": len(g2), "counts_int": bool(np.allclose(Xr.data[:5000], np.round(Xr.data[:5000]))), "sample_cells": [str(c) for c in cells[:3]]}}
json.dump(prov, open(f"{W}/tables/export_provenance.json","w"), indent=1)
print("EXPORT DONE")
