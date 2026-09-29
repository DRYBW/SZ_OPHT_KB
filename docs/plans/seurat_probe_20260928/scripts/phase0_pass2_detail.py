#!/usr/bin/env python3
"""Phase-0 pass 2: for candidate h5ad, read obs label/stage distributions via h5py category
(codes+categories), detect species from var names, check raw-count availability from X sample.
Read-only. Output JSON table."""
import json, os, sys
import h5py
import numpy as np

W = "<EYEKB>/plans/seurat_probe_20260928"
CANDS = [
    "<STORE>/data/shekhar_annotated/human_homo_sapiens_annotated.h5ad",
    "<STORE>/data/GSE155288/GSE155288_annotated.h5ad",
    "<STORE>/data/GSE137400/lukowski2019_retina.h5ad",
    "<STORE>/data/GSE183320/GSE183320_choroid.h5ad",
    "<STORE>/data/0f7d022a_ocularsurface/9ddcf89a-1329-46a6-b476-d8d3de1f7051.h5ad",
    "<STORE>/data/GSE289703/829524220*" ,  # placeholder replaced below
]
# resolve GSE289703 uuid files explicitly
CANDS = [c for c in CANDS if "*" not in c]
CANDS += [
    "<STORE>/data/GSE289703/68493594-1bde-4b8b-8916-473a10caf035.h5ad",
    "<STORE>/data/GSE289703/469d0939-0439-4255-a9d0-e85a51770d01.h5ad",
    "<STORE>/data/GSE289703/fcf71676-322b-483a-a536-1b5fc61cb476.h5ad",
    "<STORE>/data/GSE226108_cellxgene/GSE226108_56K.h5ad",
    "<STORE>/data/D002_ocularsurface/split/D002_dev_ocularsurface.h5ad",
    "<STORE>/data/GSE265774/query.h5ad",
]

STAGE_HINTS = ("developmental_stage", "age", "stage", "donor", "time", "lifecycle", "embryo", "gestational")
SPECIES_HINTS = ("species", "organism")

def read_cat(f, col):
    """Return value_counts dict for categorical column col."""
    g = f["obs"][col]
    if isinstance(g, h5py.Group):
        codes = g["codes"][:] if "codes" in g else None
        cats = None
        if "categories" in g:
            cats = g["categories"][:]
        if codes is not None and cats is not None:
            cats = [c.decode() if isinstance(c, bytes) else str(c) for c in cats]
            uniq, cnts = np.unique(codes, return_counts=True)
            out = {}
            for u, c in zip(uniq, cnts):
                if u < 0:
                    out["NaN"] = int(c)
                else:
                    out[cats[u]] = int(c)
            return out
    ds = f["obs"][col]
    if isinstance(ds, h5py.Dataset):
        v = ds[:]
        v = [x.decode() if isinstance(x, bytes) else x for x in np.asarray(v).tolist()]
        uniq, cnts = np.unique(v, return_counts=True)
        return {str(u): int(c) for u, c in zip(uniq, cnts)[:40]}
    return {}

def sample_x(f, n=20000):
    """Sample values from X to judge whether raw counts."""
    try:
        if "X" in f:
            X = f["X"]
            if isinstance(X, h5py.Dataset):
                arr = X[:min(50, X.shape[0]), :min(200, X.shape[1])]
                vals = arr[np.isfinite(arr)].ravel()
            else:
                d = X["data"]
                vals = d[:min(n, d.shape[0])]
            if len(vals) == 0:
                return {"err": "empty"}
            nonneg = float((vals >= 0).mean())
            is_int = float(np.allclose(vals, np.round(vals)))
            return {"n": int(len(vals)), "min": float(vals.min()), "max": float(vals.max()),
                    "mean": float(vals.mean()), "frac_int": is_int, "frac_nonneg": nonneg}
    except Exception as e:
        return {"err": str(e)[:120]}
    return {"err": "no X"}

def var_probe(f):
    names = None
    if "var" in f:
        for key in ("_index",):
            if key in f["var"]:
                names = [x.decode() if isinstance(x, bytes) else str(x) for x in f["var"][key][:5]]
    ens = sum(1 for x in names if x.startswith("ENS")) if names else 0
    return {"sample_genes": names, "n_ensg_prefix": ens}

def get_n(f):
    if "shape" in f.attrs:
        return list(f.attrs["shape"])
    X = f.get("X")
    if isinstance(X, h5py.Dataset):
        return list(X.shape)
    if isinstance(X, h5py.Group) and "indptr" in X:
        return [len(X["indptr"]) - 1, int(X.attrs["shape"][1])]
    return [None, None]

results = []
for p in CANDS:
    rec = {"path": p, "exists": os.path.exists(p)}
    if not rec["exists"]:
        results.append(rec); print("MISS", p, flush=True); continue
    try:
        with h5py.File(p, "r") as f:
            n_obs, n_var = get_n(f)
            rec.update({"n_obs": n_obs, "n_var": n_var, "size_MB": round(os.path.getsize(p)/1048576,1)})
            rec["obs_cols"] = sorted([k for k in f["obs"].keys() if k != "_index"])
            rec["layers"] = sorted(list(f["layers"].keys())) if "layers" in f else []
            rec["has_raw"] = "raw" in f
            rec["var_probe"] = var_probe(f)
            rec["X_sample"] = sample_x(f)
            labs = [c for c in rec["obs_cols"] if any(h in c.lower() for h in ("cell_type","celltype","majorclass","cluster_label","shekhar_class","class","label"))]
            dists = {}
            for c in labs[:6]:
                try:
                    vc = read_cat(f, c)
                    dists[c] = {"n_levels": len(vc), "top": dict(sorted(vc.items(), key=lambda kv: -kv[1])[:25])}
                except Exception as e:
                    dists[c] = {"err": str(e)[:100]}
            rec["label_dists"] = dists
            stg = [c for c in rec["obs_cols"] if any(h in c.lower() for h in STAGE_HINTS)]
            sd = {}
            for c in stg[:6]:
                try:
                    vc = read_cat(f, c)
                    sd[c] = dict(sorted(vc.items(), key=lambda kv: -kv[1])[:15]) if len(vc) <= 200 else {"n_levels": len(vc), "sample": list(vc.items())[:15]}
                except Exception as e:
                    sd[c] = {"err": str(e)[:100]}
            rec["stage_dists"] = sd
            spc = [c for c in rec["obs_cols"] if any(h in c.lower() for h in SPECIES_HINTS)]
            rec["species_cols"] = {c: list(read_cat(f, c).items())[:6] for c in spc[:3]} if spc else {}
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {e}"[:200]
    results.append(rec)
    print("OK", p.split('/')[-1], "n_obs=", rec.get("n_obs"), flush=True)

out = f"{W}/tables/phase0_pass2_detail.json"
with open(out, "w") as fh:
    json.dump(results, fh, indent=1, ensure_ascii=False)
print("WROTE", out)
