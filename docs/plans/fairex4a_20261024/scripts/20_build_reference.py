#!/usr/bin/env python3
"""STEP 7 — build the B-arm reference index's cell set (PREREG §3.3, frozen rules).

Source : HRA006282_optic_nerve.h5ad  (on disk, zero downloads)
Matrix : raw/X  (CELLxGENE raw counts, float32 storing integers — verified int-like,
         max 318, per-cell totals 647..10,706).  NOT X (X is log1p-normalised; using it
         would break the "identical instrument" requirement against the raw-count query pool).
Filter : donor-disjoint vs X4A's 19 donors  AND  donor_age >= 18
Labels : mapped to the gold's own 16 cell types (PREREG §3.3 map/drop rules)
Sample : per gold class cap 12,500, seed 20261024, rare classes take all
Genes  : the exact 5,000 HVG symbols from work/hvg5000_genes.txt, SAME ORDER as the query
         (identical gene list => identical collator gene_ids order; absent genes zero-filled)
Output : work/ref_hra006282.h5ad (cells x 5000), work/ref_build_ledger.json
"""
import os, sys, json, time, gzip
import numpy as np, h5py, scipy.sparse as sp
import anndata as ad

REF = "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad"
X4A = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean/gold/x4a_input.h5ad"
W = "/mnt/D/EyeKB/plans/fairex4a_20261024/work"
os.makedirs(W, exist_ok=True)
SEED, CAP, CHUNK = 20261024, 12500, 40000
S2 = os.environ.get("FAIRX4A_S2", "0") == "1"          # Müller-cell sensitivity arm (PREREG §3.2)
SUF = "_S2" if S2 else ""
t0 = time.time()

# ---- gold 16 ct -> lineage (from the frozen MAP_X4A_fine2super_v1.tsv) ----
GOLD_MAP = {}
with open("/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean/gold/MAP_X4A_fine2super_v1.tsv") as fh:
    hdr = fh.readline().rstrip("\n").split("\t")
    for ln in fh:
        r = dict(zip(hdr, ln.rstrip("\n").split("\t")))
        GOLD_MAP[r["fine_label"]] = r["super_label"]
GOLD_CT = sorted(GOLD_MAP)
assert len(GOLD_CT) == 16, len(GOLD_CT)

# ---- reference label map (PREREG §3.3, frozen; evidence per row) ----
MAP = {
    "oligodendrocyte": ("map", "oligodendrocyte"),
    "astrocyte": ("map", "astrocyte"),
    "retinal astrocyte": ("map", "astrocyte"),
    "oligodendrocyte precursor cell": ("map", "oligodendrocyte precursor cell"),
    "fibroblast": ("map", "fibroblast"),
    "microglial cell": ("map", "microglial cell"),
    "macrophage": ("map", "macrophage"),
    "blood vessel endothelial cell": ("map", "endothelial cell"),
    "capillary endothelial cell": ("map", "endothelial cell"),
    "endothelial cell of venule": ("map", "endothelial cell"),
    "fenestrated endothelial cell": ("map", "endothelial cell"),
    "endothelial cell": ("map", "endothelial cell"),
    "pericyte": ("map", "pericyte"),
    "vascular associated smooth muscle cell": ("map", "vascular associated smooth muscle cell"),
    "retinal pigment epithelial cell": ("map", "pigmented epithelial cell"),
    "pigmented epithelial cell": ("map", "pigmented epithelial cell"),
    "melanocyte": ("map", "melanocyte"),
    "T cell": ("map", "T cell"),
    "B cell": ("map", "B cell"),
    "natural killer cell": ("map", "natural killer cell"),
    "non-myelinating Schwann cell": ("map", "Schwann cell"),
    "myelinating Schwann cell": ("map", "myelinating Schwann cell"),
    "Mueller cell": ("drop", None),   # main arm; S2 arm maps it (see below)
}
if S2:
    MAP["Mueller cell"] = ("map", "astrocyte")   # PREREG §3.2 S2 sensitivity arm
EVID = {
    "map": "CL identity: same CL class or an explicit CL subtype of the gold's own class (PREREG §3.3)",
    "drop": "not among the gold's 16 classes: retinal neuron / photoreceptor / bipolar / amacrine / horizontal / RGC / RPC / other lineage (adipocyte, mast, dendritic). PREREG §3.3 drop = 'answer space = the gold ontology'.",
}
if S2:
    EVID["map"] = EVID["map"] + "  S2 arm additionally carries the R5 judgement: Mueller cell -> astrocyte."

def h5_cat(f, grp, col):
    g = f[grp + "/" + col] if isinstance(f[grp + "/" + col], h5py.Group) else None
    if g is not None:
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
        codes = g["codes"][:]
        out = np.array(cats, dtype=object)[codes]
        return out
    arr = f[grp + "/" + col][:]
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in arr], dtype=object)

# ---- obs ----
q = ad.read_h5ad(X4A, backed="r")
q_don = set(map(str, q.obs["donor_id"].astype(str).unique()))
q_cells = set(map(str, q.obs_names))
del q
with h5py.File(REF, "r") as f:
    don = h5_cat(f, "obs", "donor_id")
    age = h5_cat(f, "obs", "donor_age")
    ctv = h5_cat(f, "obs", "cell_type")
    src = h5_cat(f, "obs", "source") if "source" in f["obs"] else np.array(["?"] * len(don), dtype=object)
    ref_cell_ids = np.array([x.decode() if isinstance(x, bytes) else str(x)
                             for x in f["obs"]["_index"][:]], dtype=object)
    ref_var_index = np.array([x.decode() if isinstance(x, bytes) else str(x)
                              for x in f["var"]["_index"][:]], dtype=object)
    fn = f["var/feature_name"]
    ref_symbols = np.array([x.decode() if isinstance(x, bytes) else str(x)
                            for x in fn["categories"][:]], dtype=object)[fn["codes"][:]]
    n_ref_cells = len(don)

# age parser (>=18 adult gate)
def age_years(v):
    s = str(v).strip().lower()
    if s in ("", "nan", "unknown", "not reported", "none"):
        return None
    num_s, _, unit = s.partition(" ")
    num_s = num_s.lstrip("><~").strip()
    try:
        n = float(num_s)
    except ValueError:
        return None
    if unit.startswith("day") or unit.startswith("hour"):
        return n / 365.25
    if unit.startswith("week"):
        return n / 52.0
    if unit.startswith("month"):
        return n / 12.0
    if unit.startswith("year") or unit == "":
        return n
    return None

ages = np.array([age_years(a) for a in age], dtype=float)
don_disj = ~np.isin(don, list(q_don))
adult = np.isfinite(ages) & (ages >= 18)
cand = don_disj & adult

# cell-id intersection with X4A (must be 0)
inter = len(set(ref_cell_ids) & q_cells)

# ---- label mapping ----
led = {"ref_path": REF, "matrix": "raw/X (raw counts)", "seed": SEED, "cap": CAP,
       "n_ref_cells": int(n_ref_cells), "n_ref_donors_total": int(len(set(map(str, don)))),
       "x4a_donors": sorted(q_don), "cell_id_intersection_with_x4a": int(inter),
       "candidate_mask": {"n_cells": int(cand.sum()),
                          "n_donors": int(len(set(map(str, don[cand])))),
                          "donors": sorted(set(map(str, don[cand]))),
                          "sources": {str(k): int(v) for k, v in
                                      zip(*np.unique(src[cand], return_counts=True))},
                          "n_age_unparsed_in_ref": int(np.isnan(ages).sum()),
                          "n_age_unparsed_donor_disjoint": int((np.isnan(ages) & don_disj).sum())},
       "gold_16_classes": GOLD_CT}
rows = []
for lab, n in zip(*np.unique(ctv[cand], return_counts=True)):
    dec, tgt = MAP.get(str(lab), ("drop", None))
    rows.append(dict(ref_label=str(lab), n_candidate_cells=int(n), decision=dec,
                     gold_celltype=tgt or "", gold_lineage=GOLD_MAP.get(tgt, "") if tgt else "",
                     evidence=EVID[dec]))
led["label_map"] = sorted(rows, key=lambda r: (r["decision"], -r["n_candidate_cells"]))
led["n_ref_labels_seen"] = len(rows)
led["n_labels_mapped"] = int(sum(1 for r in rows if r["decision"] == "map"))
led["n_labels_dropped"] = int(sum(1 for r in rows if r["decision"] == "drop"))
led["dropped_cells"] = int(sum(r["n_candidate_cells"] for r in rows if r["decision"] == "drop"))

# ---- balanced sample over mapped labels ----
rng = np.random.default_rng([SEED, 2 if S2 else 1])
sel_idx, per_class = [], {}
cand_idx = np.where(cand)[0]
for lab in sorted({r["ref_label"] for r in rows if r["decision"] == "map"}):
    idx = cand_idx[ctv[cand_idx] == lab]
    if len(idx) > CAP:
        idx = np.sort(rng.choice(idx, CAP, replace=False))
    per_class[lab] = dict(n_candidate=int((ctv[cand_idx] == lab).sum()),
                          n_sampled=int(len(idx)), gold_celltype=MAP[lab][1])
    sel_idx.append(idx)
sel = np.sort(np.concatenate(sel_idx))
sel = sel[np.isin(ctv[sel], [k for k, v in MAP.items() if v[0] == "map"])]
# reject label collisions: a cell whose ref_label decision==drop must not be selected
assert all(MAP[str(l)][0] == "map" for l in ctv[sel]), "drop-label cell slipped into the sample"
led["per_class_sampled"] = per_class
led["n_sampled_cells"] = int(len(sel))
led["n_sampled_donors"] = int(len(set(map(str, don[sel]))))
print("sampled", len(sel), "of candidate", int(cand.sum()), flush=True)

# ---- gene alignment: the EXACT 5000 HVG symbols, same order as the query ----
hvg = [l.strip() for l in open(f"{W}/hvg5000_genes.txt") if l.strip()]
assert len(hvg) == 5000
sym2col = {}
for j, s in enumerate(ref_symbols):
    sym2col.setdefault(s, j)
src_cols = np.array([sym2col.get(g, -1) for g in hvg], dtype=np.int64)
n_matched = int((src_cols >= 0).sum())
n_ref_var = int(ref_symbols.shape[0])
col_map = np.full(n_ref_var, -1, dtype=np.int64)          # ref column -> position in the 5000-gene order
col_map[src_cols[src_cols >= 0]] = np.arange(5000, dtype=np.int64)[src_cols >= 0]
assert (col_map[src_cols[src_cols >= 0]] >= 0).all() and int((col_map >= 0).sum()) == n_matched
led["gene_space"] = {"n_hvg": 5000, "n_matched_in_reference": n_matched,
                     "n_zero_filled": int(5000 - n_matched),
                     "alignment": "reference matrix has the same 5,000 symbols in the same order as the query; "
                                  "genes the reference does not measure are zero-filled so the collator sees an "
                                  "identical gene_ids array"}
print("gene match", n_matched, "/5000", flush=True)

# ---- stream raw/X, keep selected rows, re-map to the 5000-column order ----
out_rows, out_data, out_ind = [], [], []
with h5py.File(REF, "r") as f:
    ip = f["raw/X/indptr"][:]
    data = f["raw/X/data"]; ind = f["raw/X/indices"]
    pos = {int(r): k for k, r in enumerate(sel)}
    for c0 in range(0, n_ref_cells, CHUNK):
        c1 = min(c0 + CHUNK, n_ref_cells)
        a, b = int(ip[c0]), int(ip[c1])
        s0 = int(np.searchsorted(sel, c0)); s1 = int(np.searchsorted(sel, c1))
        want = sel[s0:s1]
        if len(want) == 0:
            continue
        d = data[a:b]; ii = ind[a:b]
        local_ip = ip[c0:c1 + 1] - a
        loc = want - c0
        # build csr for the requested rows only; global output row ids = positions in `sel`
        starts = local_ip[loc]; ends = local_ip[loc + 1]
        lens = ends - starts
        rows_rep = np.repeat(np.arange(s0, s1), lens)
        parts_d = [d[s:e] for s, e in zip(starts, ends)]
        parts_i = [ii[s:e] for s, e in zip(starts, ends)]
        dd = np.concatenate(parts_d); jj = np.concatenate(parts_i)
        keep = col_map[jj] >= 0
        rows_rep = rows_rep[keep]
        dd = dd[keep]; jj = col_map[jj[keep]].astype(np.int32)
        out_rows.append(rows_rep.astype(np.int32)); out_data.append(dd.astype(np.float32)); out_ind.append(jj)
        print(f"  chunk {c0}-{c1}: kept {len(want)} rows, nnz {len(dd)}  ({time.time()-t0:.0f}s)", flush=True)

rows_rep = np.concatenate(out_rows); dd = np.concatenate(out_data); jj = np.concatenate(out_ind)
n_out = len(sel)
order = np.lexsort((jj, rows_rep))
rows_rep, dd, jj = rows_rep[order], dd[order], jj[order]
indptr = np.zeros(n_out + 1, dtype=np.int64)
np.add.at(indptr, rows_rep + 1, 1)
indptr = np.cumsum(indptr)
X = sp.csr_matrix((dd, jj, indptr), shape=(n_out, 5000))
_nz = np.diff(X.indptr)
assert int((_nz == 0).sum()) == 0, f"{int((_nz==0).sum())} all-zero reference rows — row mapping broken"
_nzmed = float(np.median(_nz))
print(f"ref nnz/cell: min={_nz.min()} median={_nzmed} max={_nz.max()} sum={X.nnz}", flush=True)
obs = {"ref_label": ctv[sel].astype(str), "ref_gold_ct": np.array([MAP[str(l)][1] for l in ctv[sel]]),
       "ref_lineage": np.array([GOLD_MAP[MAP[str(l)][1]] for l in ctv[sel]]),
       "ref_donor": don[sel].astype(str), "ref_age_y": ages[sel], "ref_source": src[sel].astype(str)}
A = ad.AnnData(X=X, obs=obs)
A.var_names = hvg
A.write_h5ad(f"{W}/ref_hra006282{SUF}.h5ad", compression="gzip")
led["out"] = {"shape": [int(A.shape[0]), int(A.shape[1])], "nnz": int(X.nnz),
              "per_cell_nonzero_median": _nzmed,
              "per_cell_nonzero_min": int(_nz.min()), "per_cell_nonzero_max": int(_nz.max()),
              "wall_s": round(time.time() - t0, 1), "ts": time.strftime("%F %T")}
led["out_class_counts"] = {str(k): int(v) for k, v in zip(*np.unique(A.obs["ref_gold_ct"], return_counts=True))}
led["out_lineage_counts"] = {str(k): int(v) for k, v in zip(*np.unique(A.obs["ref_lineage"], return_counts=True))}
led["s2_arm"] = S2
json.dump(led, open(f"{W}/ref_build_ledger{SUF}.json", "w"), ensure_ascii=False, indent=1)
print("REF_BUILD_OK", json.dumps(led["out"]), flush=True)
print("class counts:", json.dumps(led["out_class_counts"]), flush=True)