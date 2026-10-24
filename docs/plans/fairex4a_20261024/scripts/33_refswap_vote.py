#!/usr/bin/env python3
"""STEP 8+9 — build the B-arm index from the reference embeddings and query the X4A pool.

Only the reference label space changed; the instrument (model, checkpoint, gene set, k=50,
vote rule) is the one B0 just proved reproduces the official readout.
usage: 33_refswap_vote.py --emb <E_ref.npy> --ref <ref h5ad> --tag refswap|refswap_S2
"""
import argparse, json, os
import numpy as np, faiss
import anndata as ad

ap = argparse.ArgumentParser()
ap.add_argument("--emb", required=True)
ap.add_argument("--ref", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--outdir", default="/mnt/D/EyeKB/plans/fairex4a_20261024/out")
ap.add_argument("--workdir", default="/mnt/D/EyeKB/plans/fairex4a_20261024/work")
A = ap.parse_args()

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"

Eref = np.ascontiguousarray(np.load(A.emb).astype("float32"))
R = ad.read_h5ad(A.ref)
assert Eref.shape[0] == R.shape[0], (Eref.shape, R.shape)
faiss.normalize_L2(Eref)
index = faiss.IndexFlatIP(Eref.shape[1])
index.add(Eref)

E = np.ascontiguousarray(np.load(f"{A.workdir}/E_x4a.npy").astype("float32"))
faiss.normalize_L2(E)
d, i = index.search(E, 50)

q = ad.read_h5ad(f"{P}/gold/x4a_input.h5ad", backed="r")
ids = list(map(str, q.obs_names))
assert len(ids) == E.shape[0]

labs = np.array([str(x) for x in R.obs["ref_label"]])
rows = []
for cid, votes in zip(ids, labs[i]):
    vals, cnt = np.unique(votes, return_counts=True)
    rows.append((cid, str(vals[cnt.argmax()]), float(cnt.max() / 50.0)))

out = f"{A.outdir}/pred_A1b_scgpt_x4a_{A.tag}_raw.tsv"
with open(out, "w", newline="") as fh:
    fh.write("cell_id\traw_label\tvote_frac\n")
    for r in rows:
        fh.write("\t".join(map(str, r)) + "\n")

vf = np.array([r[2] for r in rows])
lab_ct = {}
for r in rows:
    lab_ct[r[1]] = lab_ct.get(r[1], 0) + 1
led = {"tag": A.tag, "reference": A.ref, "reference_embeddings": A.emb,
       "index": "faiss.IndexFlatIP (exact, same metric as the frozen index)",
       "index_ntotal": int(index.ntotal), "k": 50, "n_query": len(rows),
       "vote_frac_mean": round(float(vf.mean()), 4), "vote_frac_median": round(float(np.median(vf)), 4),
       "vote_frac_lt_0.5": int((vf < 0.5).sum()),
       "emitted_labels": dict(sorted(lab_ct.items(), key=lambda kv: -kv[1])),
       "pred_out": out, "ts": __import__("time").strftime("%F %T")}
json.dump(led, open(f"{A.outdir}/REFVOTE_{A.tag}_ledger.json", "w"), ensure_ascii=False, indent=1)
print("REFVOTE_OK", A.tag, json.dumps({k: led[k] for k in ["index_ntotal", "vote_frac_mean", "vote_frac_lt_0.5"]}), flush=True)
print("emitted labels:", json.dumps(led["emitted_labels"], ensure_ascii=False), flush=True)