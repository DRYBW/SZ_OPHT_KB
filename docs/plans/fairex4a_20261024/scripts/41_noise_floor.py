#!/usr/bin/env python3
"""STEP 11b — instrument noise floor: same script, same input, same GPU, second run.

Decides how the B0 gate failure must be read:
  * if run1 vs run2 reproduce each other closely, the instrument is deterministic and the
    residual vs the frozen official pred is an INPUT/ARCHIVE difference;
  * if they do not, 0.99 cell-level agreement is not attainable by this instrument on this
    volume, and the B-arm movement has to be read against this measured floor.
Also rescores the refswap arm from run2's embeddings, so the headline refswap number gets a
run-to-run spread (not just a point value).
"""
import json, os, subprocess
import numpy as np, faiss

R = "/mnt/D/EyeKB/plans/fairex4a_20261024"
W, O = f"{R}/work", f"{R}/out"
P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
CACHE = "/mnt/D/HermesAI/shared/reproduction/scgpt/a1b_formal"

import anndata as ad
q = ad.read_h5ad(f"{P}/gold/x4a_input.h5ad", backed="r")
ids = list(map(str, q.obs_names))

E1 = np.load(f"{W}/E_x4a.npy").astype("float32")
E2 = np.load(f"{W}/E_x4a_r2.npy").astype("float32")
assert E1.shape == E2.shape
d = np.abs(E1 - E2)
n1 = np.linalg.norm(E1, axis=1); n2 = np.linalg.norm(E2, axis=1)
cos = (E1 * E2).sum(1) / (n1 * n2)
res = {"comparison": "same script + same input h5ad + same GPU, run 1 vs run 2",
       "max_abs_elementwise_diff": float(d.max()),
       "median_abs_elementwise_diff": float(np.median(d)),
       "per_cell_cosine: min": float(cos.min()), "median": float(np.median(cos)), "max": float(cos.max()),
       "n_cells_with_cosine_lt_0.999": int((cos < 0.999).sum()),
       "n_cells_with_cosine_lt_0.99": int((cos < 0.99).sum()),
       "n_cells_with_cosine_lt_0.95": int((cos < 0.95).sum())}

# label agreement, frozen reference index (the reading the official table is built on)
idx = faiss.read_index(f"{CACHE}/formal200k.index")
meta = np.load(f"{CACHE}/meta200k.npy", allow_pickle=True)
labels = {}
for tag, E in (("run1", E1), ("run2", E2)):
    Ec = np.ascontiguousarray(E.copy()); faiss.normalize_L2(Ec)
    _, i = idx.search(Ec, 50)
    lab = []
    for votes in meta[i]:
        v, c = np.unique(votes, return_counts=True)
        lab.append(str(v[c.argmax()]))
    labels[tag] = lab
    with open(f"{O}/pred_A1b_scgpt_x4a_{tag}_raw.tsv", "w", newline="") as fh:
        fh.write("cell_id\traw_label\tvote_frac\n")
        for cid, votes in zip(ids, meta[i]):
            v, c = np.unique(votes, return_counts=True)
            fh.write(f"{cid}\t{v[c.argmax()]}\t{c.max()/50.0}\n")
off = {}
with open(f"{P}/arms/pred_A1b_scgpt_x4a_raw.tsv") as fh:
    next(fh)
    for ln in fh:
        c, l, _ = ln.rstrip("\n").split("\t"); off[c] = l
res["frozen_index_label_agreement_run1_vs_run2"] = round(sum(a == b for a, b in zip(labels["run1"], labels["run2"])) / len(ids), 6)
res["frozen_index_label_agreement_run1_vs_official"] = round(sum(a == off[c] for a, c in zip(labels["run1"], ids)) / len(ids), 6)
res["frozen_index_label_agreement_run2_vs_official"] = round(sum(a == off[c] for a, c in zip(labels["run2"], ids)) / len(ids), 6)

# refswap votes from run2 embeddings -> score -> spread of the headline number
Eref = np.ascontiguousarray(np.load(f"{W}/E_ref_hra006282.npy").astype("float32"))
faiss.normalize_L2(Eref)
fi = faiss.IndexFlatIP(Eref.shape[1]); fi.add(Eref)
Rr = ad.read_h5ad(f"{W}/ref_hra006282.h5ad")
rl = np.array([str(x) for x in Rr.obs["ref_label"]])
Ec = np.ascontiguousarray(E2.copy()); faiss.normalize_L2(Ec)
_, j = fi.search(Ec, 50)
outp = f"{O}/pred_A1b_scgpt_x4a_refswap_run2_raw.tsv"
with open(outp, "w", newline="") as fh:
    fh.write("cell_id\traw_label\tvote_frac\n")
    for cid, votes in zip(ids, rl[j]):
        v, c = np.unique(votes, return_counts=True)
        fh.write(f"{cid}\t{v[c.argmax()]}\t{c.max()/50.0}\n")
res["refswap_pred_run2"] = outp
print(json.dumps(res, indent=1), flush=True)
json.dump(res, open(f"{O}/INSTRUMENT_noise_floor.json", "w"), ensure_ascii=False, indent=1)