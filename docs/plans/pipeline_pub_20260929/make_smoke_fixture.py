#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1 冒烟输入构造器：从本地已有 demo 卷（GSE165784 PDR 膜，人）取
两样本各 1000 细胞 → smoke.h5ad + 10X 三件套两目录（RRD-ERM1 / PDR-ERM-210630）。
源卷只读；产物为病人来源数据，按仓规 *.h5ad 永不入库（磁盘保留即证据）。
"""
import numpy as np
import anndata as ad
import scipy.io as sio
import scipy.sparse as sp

SRC = "/mnt/D/EyeKB/plans/demo_gse165784/proc/00_merged_raw.h5ad"
OUT = "/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928/docs/plans/pipeline_pub_20260929/fixtures"
SAMPLES = ["RRD-ERM1", "PDR-ERM-210630"]
N_PER = 1000
rng = np.random.default_rng(20260929)

a = ad.read_h5ad(SRC)
keep = np.zeros(a.shape[0], dtype=bool)
for s in SAMPLES:
    idx = np.where(a.obs["sample"].astype(str) == s)[0]
    keep[rng.choice(idx, size=min(N_PER, len(idx)), replace=False)] = True
sub = a[keep].copy()
sub.write(f"{OUT}/smoke.h5ad")
print("smoke.h5ad", sub.shape)

X = sp.csc_matrix(sub.X)
genes = np.asarray(sub.var_names)
for s in SAMPLES:
    m = (sub.obs["sample"].astype(str) == s).values
    d = f"{OUT}/10x_{s}"
    import os
    os.makedirs(d, exist_ok=True)
    sio.mmwrite(f"{d}/matrix.mtx", X[m, :].T.tocoo())  # genes x cells
    with open(f"{d}/barcodes.tsv", "w") as f:
        for b in sub.obs_names[m]:
            f.write(str(b).split("|")[-1] + "\n")
    with open(f"{d}/genes.tsv", "w") as f:
        for g in genes:
            f.write(f"{g}\t{g}\n")  # 两列：id + symbol（符号形态冒烟）
    print(d, int(m.sum()), "cells")
print("OK")
