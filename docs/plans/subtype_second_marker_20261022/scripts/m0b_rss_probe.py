#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m0b -- resource probe: RSS + wall time of reading ONE volume the way the ruler reads it.

The ruler's reader (plans/consensus_subtype_20261022/scripts/c3_separation.py:values_for) builds the
volume's full CSR matrix, then keeps the wanted columns.  This probe reproduces exactly that shape
for the largest in-scope volume so the MemoryMax of the real runs is measured, not guessed.

argv: <volume> [n_wanted_genes]
Prints one JSON line with: volume, n_cells, n_genes, nnz, peak_rss_kb, wall_s.
"""
import json
import os
import resource
import sys
import time

import h5py
import numpy as np
import scipy.sparse as sp

WORKDIR = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/workdir"


def main():
    vol = sys.argv[1]
    n_want = int(sys.argv[2]) if len(sys.argv) > 2 else 250
    path = os.path.join(WORKDIR, vol, "input.h5ad")
    t0 = time.time()
    with h5py.File(path, "r") as f:
        idx = f["var"]["_index"][:]
        idx = np.array([x.decode() if isinstance(x, bytes) else str(x) for x in idx], dtype=object)
        cols = list(range(0, len(idx), max(1, len(idx) // n_want)))[:n_want]
        X = f["X"]
        shape = tuple(int(x) for x in X.attrs["shape"])
        mat = sp.csr_matrix((X["data"][:], X["indices"][:], X["indptr"][:]), shape=shape)
        block = np.asarray(mat.tocsc()[:, cols].todense())
        n_cells, n_genes = shape
        nnz = int(mat.nnz)
        del mat, block
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps({"volume": vol, "n_cells": n_cells, "n_genes": n_genes, "nnz": nnz,
                      "wanted": len(cols), "peak_rss_kb": peak, "wall_s": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()