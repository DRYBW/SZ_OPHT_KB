#!/usr/bin/env python3
"""STEP 5+7 — scGPT embeddings for the B arm, ONE instrument, TWO matrices.

The call is copied verbatim from the official X4A runner
(plans/toolbenchmark_20261010_x4clean/scripts/x4arms/a1b_x4_gpu.py), including the three
shims it documents (py3.14 forkserver sched_getaffinity, ENSG->symbol via feature_name,
annData(dtype=) strip).  No seed, no normalisation, no gene reordering is added: the two
matrices carry the SAME 5,000 symbols in the SAME order, so the collator builds an
identical gene_ids array for both.

usage: 30_embed.py --h5ad <path> --out <npy> --timelog <json>
"""
import argparse, os, sys, time, json
import numpy as np
import scgpt as sg

ap = argparse.ArgumentParser()
ap.add_argument("--h5ad", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--timelog", required=True)
A = ap.parse_args()

DEV, BS = "cuda", 256
MODEL = None
for cand in [os.path.expanduser("~/.cache/scgpt/scGPT_human"),
             "/mnt/D/HermesAI/shared/reproduction/scgpt/scGPT_human",
             "/mnt/D/EyeKB/plans/toolbenchmark_20261009/s1_tools/scgpt_base"]:
    if os.path.isdir(cand) and os.path.exists(os.path.join(cand, "best_model.pt")):
        MODEL = cand; break
assert MODEL, "scGPT_human model dir not found"
print("MODEL:", MODEL, flush=True)

import anndata as ad
q5 = ad.read_h5ad(A.h5ad)
print("input", q5.shape, "X dtype", q5.X.dtype, "max", q5.X.max(), flush=True)

# --- shim (1) py3.14 forkserver: cell_emb derives num_workers from sched_getaffinity ---
import types
import scgpt.tasks.cell_emb
_ce = sys.modules["scgpt.tasks.cell_emb"]
_real_os = _ce.os
_shim = types.ModuleType("os_shim_for_cell_emb")
_shim.__dict__.update({k: v for k, v in _real_os.__dict__.items() if k != "sched_getaffinity"})
_shim.sched_getaffinity = lambda *a, **kw: frozenset()
_ce.os = _shim
assert len(_ce.os.sched_getaffinity(0)) == 0, "num_workers shim failed"
# --- shim (3) new anndata rejects AnnData(dtype=) ---
_sc_mod = _ce.sc
_ce.sc = types.SimpleNamespace(
    read_h5ad=_sc_mod.read_h5ad,
    AnnData=lambda *a, **kw: _sc_mod.AnnData(*a, **{k: v for k, v in kw.items() if k != "dtype"}),
)

t0 = time.time()
emb = sg.tasks.embed_data(q5, MODEL, gene_col="index", batch_size=BS, device=DEV,
                          use_fast_transformer=False, return_new_adata=True)
t_emb = time.time() - t0
E = np.ascontiguousarray(np.asarray(emb.X, dtype="float32"))
print(f"embed done {E.shape} wall={t_emb:.1f}s", flush=True)
os.makedirs(os.path.dirname(A.out), exist_ok=True)
np.save(A.out, E)
timing = dict(cells=int(E.shape[0]), dim=int(E.shape[1]), device=DEV, batch_size=BS,
              embed_wall_s=round(t_emb, 1), cells_per_s=round(E.shape[0] / t_emb, 1),
              model=MODEL, h5ad=A.h5ad, out=A.out, ts=time.strftime("%F %T"))
json.dump(timing, open(A.timelog, "w"), indent=1)
print("EMBED_DONE", A.out, json.dumps(timing), flush=True)