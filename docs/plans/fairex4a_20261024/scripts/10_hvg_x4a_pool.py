#!/usr/bin/env python3
"""STEP 4 — X4A pool HVG recipe, recomputed this run (single-variable ledger item).
Recipe copied line-for-line from x4arms/a1b_x4_gpu.py (official A1b X4 arm):
  var.index = feature_name; var_names_make_unique(); filter_genes(min_cells=10);
  highly_variable_genes(n_top_genes=5000, flavor='seurat_v3'); take those 5000 columns.
Outputs: work/q5_x4a_hvg5000.h5ad (139978 x N genes, raw counts), work/hvg5000_genes.txt
Reads pool with backed='r' for the QC pass; only the 5000-gene slice is materialised."""
import os, sys, json, time
import numpy as np
import anndata as ad
import scanpy as sc

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
W = "/mnt/D/EyeKB/plans/fairex4a_20261024/work"
os.makedirs(W, exist_ok=True)
t0 = time.time()

q = sc.read_h5ad(f"{P}/gold/x4a_input.h5ad")
print("raw pool", q.shape, "X dtype", q.X.dtype, "max", q.X.max(), flush=True)
q.var.index = q.var["feature_name"].astype(str).values
q.var_names_make_unique()
sc.pp.filter_genes(q, min_cells=10)
print("after filter_genes(min_cells=10)", q.shape, flush=True)
sc.pp.highly_variable_genes(q, n_top_genes=5000, flavor="seurat_v3")
genes = [str(g) for g in q.var_names[q.var["highly_variable"].values]]
assert len(genes) == 5000, len(genes)
q5 = q[:, q.var["highly_variable"].values].copy()
print("q5", q5.shape, flush=True)
q5.write_h5ad(f"{W}/q5_x4a_hvg5000.h5ad", compression="gzip")
with open(f"{W}/hvg5000_genes.txt", "w") as fh:
    fh.write("\n".join(genes) + "\n")
meta = dict(n_cells=int(q5.shape[0]), n_genes=5000,
            n_genes_after_mincells10=int(q.shape[1]),
            genes_sha_placeholder=None,
            nonfinite=int((~np.isfinite(q5.X.data)).sum()) if hasattr(q5.X, "data") else 0,
            wall_s=round(time.time() - t0, 1), ts=time.strftime("%F %T"))
json.dump(meta, open(f"{W}/hvg5000_meta.json", "w"), indent=1)
print("HVG_OK", json.dumps(meta), flush=True)