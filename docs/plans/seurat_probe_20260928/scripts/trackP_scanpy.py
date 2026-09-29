#!/usr/bin/env python3
"""Track P (Python current face): scanpy chain HVG->PCA->neighbors15->leiden res1.0
+ kb/marker-face top_genes judgment rule (read-only reuse of EyeKB marker libs).
Same-start rule as Track S: raw counts only. Writes cluster labels + top30 + per-cluster judgment csvs.
Usage: trackP_scanpy.py <dataset: DS1|DS1sub20k|DS2>
"""
import sys, json, hashlib, subprocess
import numpy as np, pandas as pd
import scanpy as sc
import anndata as ad

W = "<EYEKB>/plans/seurat_probe_20260928"
DS_PATHS = {
 "DS1": ("/mnt/OcularKB", None),
}
SOURCES = {
 "DS1": ("h5ad", "<STORE>/data/shekhar_annotated/human_homo_sapiens_annotated.h5ad", "shekhar_class", {}),
 "DS1sub20k": ("mtx", f"{W}/data/DS1sub20k", "truth", {}),
 "DS2": ("h5ad_raw", "<STORE>/data/GSE137400/lukowski2019_retina.h5ad", "author_cell_type", {}),
}
TRUTH_MAP_DS2 = {
 "retinal rod cell type A":"Rod","retinal rod cell type B":"Rod","retinal rod cell type C":"Rod",
 "retinal cone cell":"Cone","retinal bipolar neuron type A":"BC","retinal bipolar neuron type B":"BC",
 "retinal bipolar neuron type C":"BC","retinal bipolar neuron type D":"BC",
 "amacrine cell":"AC","retinal ganglion cell":"RGC","Muller cell":"MG",
 "microglial cell":"Micro","unannotated":None,"unspecified":None}

def read_h5ad_counts(path, labcol, barcode_col=None, use_raw=False, cat_map=None):
    import h5py
    from scipy.sparse import csr_matrix
    def dec(x): return x.decode() if isinstance(x, (bytes, np.bytes_)) else str(x)
    with h5py.File(path, "r") as f:
        root = f["raw"] if use_raw else f
        g = root["X"]
        X = csr_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=tuple(int(x) for x in g.attrs["shape"]))
        v = root["var"]
        if "feature_name" in v and isinstance(v["feature_name"], h5py.Group):
            fn = v["feature_name"]
            fcats = [dec(c) for c in fn["categories"][:]]
            genes = np.array([fcats[i] if i >= 0 else "NA" for i in fn["codes"][:]])
        elif "_index" in v:
            genes = np.array([dec(x) for x in v["_index"][:]])
        else:
            nm = v.attrs["_index"]; nm = dec(nm)
            genes = np.array([dec(x) for x in v[nm][:]])
        gc = f["obs"][labcol]
        if isinstance(gc, h5py.Group):
            cats = [dec(c) for c in gc["categories"][:]]
            lab = np.array(cats)[gc["codes"][:]]
        else:
            lab = np.array([dec(x) for x in gc[:]])
        if barcode_col and barcode_col in f["obs"]:
            cells = np.array([dec(x) for x in f["obs"][barcode_col][:]])
        else:
            nm2 = f["obs"].attrs.get("_index", "_index"); nm2 = dec(nm2)
            ds2 = f["obs"]["_index"] if "_index" in f["obs"] else f["obs"][nm2]
            cells = np.array([dec(x) for x in ds2[:]])
    if cat_map:
        lab = np.array([cat_map.get(x, "EXCL") for x in lab])
    a = ad.AnnData(X.astype("float32"))
    a.var_names = list(genes); a.var_names_make_unique()
    a.obs = pd.DataFrame({"cell": cells, "truth": lab})
    return a

def load(tag):
    kind, path, labcol, _ = SOURCES[tag]
    if kind == "h5ad":
        return read_h5ad_counts(path, labcol, barcode_col="barcode")
    if kind == "h5ad_raw":
        return read_h5ad_counts(path, labcol, use_raw=True, cat_map=TRUTH_MAP_DS2)
    # mtx
    import scipy.io as sio
    M = sio.mmread(f"{path}_counts.mtx").tocsr()  # genes x cells
    genes = open(f"{path}_features.tsv").read().split()
    cells = open(f"{path}_barcodes.tsv").read().split()
    truth = pd.read_csv(f"{path}_truth.tsv", sep="\t")
    a = ad.AnnData(M.T.astype("float32"))
    a.var_names = genes; a.var_names_make_unique()
    a.obs = pd.DataFrame({"cell": cells}); a.obs["truth"] = truth["truth"].values
    return a

def load_marker_libs():
    libs = {}
    sha = {}
    for name, p in [("v4.1", "<EYEKB>/kb/markers/markers_v4.1_clean.json"),
                    ("v6", "<EYEKB>/kb/markers/markers_v6_retina_repair.json")]:
        raw = open(p, "rb").read()
        sha[name] = hashlib.sha256(raw).hexdigest()
        d = json.loads(raw)["markers"]
        libs[name] = {k: [str(g).upper() for g in v] for k, v in d.items()}
    merged = dict(libs["v4.1"]); merged.update(libs["v6"])
    return merged, sha, libs

def judge(top_sets, mk):
    out = []
    for cid, tg in top_sets.items():
        tgu = {g.upper() for g in tg}
        scores = {cls: len(tgu & {g.upper() for g in ms}) for cls, ms in mk.items()}
        best = max(scores.values())
        winners = sorted([c for c, s in scores.items() if s == best])
        out.append({"cluster": cid, "call": winners[0] if best > 0 else "MISS",
                    "n_shared": best, "ties": ";".join(winners if best > 0 else []),
                    "scores": json.dumps(scores)})
    return pd.DataFrame(out)

def main():
    tag = sys.argv[1]
    a = load(tag)
    sc.pp.filter_cells(a, min_genes=0)
    a.layers["counts"] = a.X.copy()
    sc.pp.normalize_total(a, target_sum=1e4); sc.pp.log1p(a)
    sc.pp.highly_variable_genes(a, n_top_genes=2000, flavor="seurat")
    sc.pp.pca(a, n_comps=50, random_state=20260928)
    sc.pp.neighbors(a, n_neighbors=15, use_rep="X_pca", random_state=20260928)
    sc.tl.leiden(a, resolution=1.0, key_added="leiden", flavor="igraph", n_iterations=2, directed=False, random_state=20260928)
    sc.tl.rank_genes_groups(a, "leiden", method="wilcoxon", n_genes=30)
    gr = a.uns["rank_genes_groups"]
    clusters = list(a.obs["leiden"].cat.categories)
    top = {c: [gr["names"][c][i] for i in range(30)] for c in clusters}
    mk, sha, libs = load_marker_libs()
    jd = judge(top, mk)
    jd["top30"] = jd["cluster"].map(lambda c: ";".join(top[c]))
    # truth dominant per cluster
    a.obs["truth_str"] = a.obs["truth"].astype(str)
    dom = (a.obs.groupby(["leiden", "truth_str"], observed=True).size().unstack(fill_value=0))
    dom["truth_dominant"] = dom.idxmax(axis=1)
    jd = jd.merge(dom[["truth_dominant"]].reset_index().rename(columns={"leiden": "cluster"}), on="cluster", how="left")
    jd.to_csv(f"{W}/tables/trackP_{tag}_clusters.csv", index=False)
    a.obs[["cell", "truth", "leiden"]].to_csv(f"{W}/tables/trackP_{tag}_celllabels.csv", index=False)
    json.dump({"tag": tag, "n_cells": int(a.n_obs), "n_clusters": len(clusters),
               "marker_lib_sha256": sha, "marker_union_n_classes": len(mk),
               "classes": sorted(mk.keys()),
               "params": "HVG2000 seurat->PCA50->neighbors15->leiden res1.0 igraph; wilcoxon top30"},
              open(f"{W}/tables/trackP_{tag}_meta.json", "w"), indent=1)
    print("TRACKP_DONE", tag, "clusters=", len(clusters))

if __name__ == "__main__":
    main()
