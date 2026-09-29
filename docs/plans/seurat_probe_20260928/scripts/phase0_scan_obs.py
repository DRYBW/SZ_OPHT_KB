#!/usr/bin/env python3
"""Phase-0 pass 1: enumerate h5ad on <STORE>/data, read obs columns + shape via h5py (metadata-only, fast).
Zero writes outside workdir. Read-only on registry data."""
import os, sys, json, traceback
import h5py

DATA = "<STORE>/data"
OUT = "<EYEKB>/plans/seurat_probe_20260928/tables/phase0_h5ad_inventory.tsv"

LABEL_HINTS = ("cell_type", "celltype", "cluster_label", "celltype_original",
               "annotation", "label", "cell_class", "cluster", "subclass", "broad", "class")

def get_shape(f):
    # root attrs shape
    try:
        if "shape" in f.attrs:
            return list(f.attrs["shape"])
    except Exception:
        pass
    for grp in ("X", "layers/X", "raw/X"):
        try:
            p = grp.split("/")
            g = f
            for part in p:
                g = g[part]
            if "shape" in g.attrs:
                return list(g.attrs["shape"])
            if isinstance(g, h5py.Dataset):
                return list(g.shape)  # dense
            if "indptr" in g:
                return [len(g["indptr"]) - 1, int(g.attrs.get("shape", [0, 0])[1])]
        except Exception:
            continue
    return [None, None]

rows = []
for dirpath, dirnames, filenames in os.walk(DATA):
    dirnames.sort()
    for fn in sorted(filenames):
        if not fn.lower().endswith(".h5ad"):
            continue
        p = os.path.join(dirpath, fn)
        rec = {"path": p, "file": fn, "dir": dirpath.replace(DATA + "/", ""), "size_bytes": None,
               "n_obs": None, "n_var": None, "obs_cols": "", "label_like": "", "err": ""}
        try:
            rec["size_bytes"] = os.path.getsize(p)
            with h5py.File(p, "r") as f:
                shp = get_shape(f)
                rec["n_obs"], rec["n_var"] = shp[0], shp[1]
                if "obs" in f:
                    cols = [k for k in f["obs"].keys() if k != "_index"]
                    rec["obs_cols"] = ";".join(cols)
                    lab = [c for c in cols if any(h in c.lower() for h in LABEL_HINTS)]
                    rec["label_like"] = ";".join(lab)
        except Exception as e:
            rec["err"] = f"{type(e).__name__}: {e}"[:200]
        rows.append(rec)
        print(f"[{len(rows)}] {rec['dir']}/{fn} n_obs={rec['n_obs']} label_like={rec['label_like'][:80]} err={rec['err'][:60]}", flush=True)

with open(OUT, "w") as fh:
    fh.write("path\tfile\tdir\tsize_bytes\tn_obs\tn_var\tobs_cols\tlabel_like\terr\n")
    for r in rows:
        fh.write("\t".join(str(r[k]) for k in ["path","file","dir","size_bytes","n_obs","n_var","obs_cols","label_like","err"]) + "\n")
print(f"\nDONE rows={len(rows)} -> {OUT}")
