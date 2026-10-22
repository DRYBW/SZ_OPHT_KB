#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m4 -- the flip table, with the marker evidence and the pre-registered honesty classification.

For every (volume, subtype) row whose verdict moved, report:

  * which markers cleared the pre-registered gate (AUC >= 0.70, BH q < 0.05) and which of them are
    added candidates rather than frozen panel genes (H1);
  * the literature claim ids behind every clearing marker, and whether the two clearing markers share
    a paper -- `two_independent_claims` vs `shared_source` (H2);
  * the observed Spearman rho between the two clearing markers across the compared cells, a
    disclosure only, flagged at |rho| >= 0.6 (H3);
  * `same_symbol_family` when the added marker and another clearing marker share the symbol stem (H4);
  * the resulting verdict: `corroborated` only when H2 = two_independent_claims (H5).

Also asserts the out-of-scope rows did not move (PREREG section 7).

Writes out/FLIPS.json / .tsv and out/RULER_REPRO_CHECK.json.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

import h5py
import numpy as np
import scipy.sparse as sp
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
WORKDIR = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/workdir"
AUC_MIN, FDR_MAX = 0.70, 0.05
RHO_FLAG = 0.6


def read_cat(g, name):
    node = g[name]
    if isinstance(node, h5py.Group):
        cats = [c.decode() if isinstance(c, bytes) else str(c) for c in node["categories"][:]]
        codes = node["codes"][:]
        return np.array([cats[c] if 0 <= c < len(cats) else "" for c in codes], dtype=object)
    arr = node[:]
    return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in arr], dtype=object)


def expr_for(vol, genes, labels_wanted):
    """gene -> per-cell values, and the author label vector (same reader shape as the ruler)."""
    path = os.path.join(WORKDIR, vol, "input.h5ad")
    with h5py.File(path, "r") as f:
        idx = read_cat(f["var"], "_index").astype(str)
        pos = {}
        for g in genes:
            hit = np.where(idx == g)[0]
            if hit.size:
                pos[g] = int(hit[0])
        obs = f["obs"]
        lab = None
        for cand in ("cell_type", "author_cell_type"):
            if cand in obs.keys():
                lab = read_cat(obs, cand).astype(str)
                break
        X = f["X"]
        cols = [pos[g] for g in pos]
        if isinstance(X, h5py.Group):
            mat = sp.csr_matrix((X["data"][:], X["indices"][:], X["indptr"][:]),
                                shape=tuple(int(x) for x in X.attrs["shape"]))
            block = np.asarray(mat.tocsc()[:, cols].todense()) if cols else np.zeros((0, 0))
        else:
            block = np.asarray(X[:, cols])
        return {g: block[:, i].astype(float) for i, g in enumerate(pos)}, lab


def stem(g):
    m = re.match(r"^([A-Z]+[A-Z0-9]*?)(\d+[A-Z]*)$", g)
    return m.group(1) if m else g


def main():
    frozen = json.load(open(os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json"), encoding="utf-8"))
    ctl = json.load(open(os.path.join(OUT, "ruler_control", "SUBTYPE_SEPARATION.json"), encoding="utf-8"))
    aug = json.load(open(os.path.join(OUT, "ruler_augmented", "SUBTYPE_SEPARATION.json"),
                         encoding="utf-8"))
    lit = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), encoding="utf-8"))
    meas = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_MEASURABILITY.json"),
                          encoding="utf-8"))

    claim = defaultdict(dict)     # subtype -> gene -> [paper ids / source ids]
    kept = defaultdict(list)
    for r in lit["rows"]:
        if r["admitted"]:
            claim[r["subtype"]][r["gene"]] = sorted(set(r["channel_a_papers"] + r["channel_c_sources"]
                                                       + r["channel_b_sources"]))
        if r["kept_l5"]:
            kept[r["subtype"]].append(r["gene"])
    frozen_panel = {}
    for r in json.load(open(os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json"),
                            encoding="utf-8")):
        frozen_panel[r["subtype"]] = set(r.get("_markers_all") or [])

    key = lambda r: (r["volume"], r["subtype"])
    ctl_by, frozen_by = {key(r): r for r in ctl}, {key(r): r for r in frozen}
    aug_by = {key(r): r for r in aug}

    scope_rows = [r for r in frozen if r["result"] == "not_separated"
                  and str(r.get("reason", "")).startswith("1 marker(s) cleared the gate")]
    scope_keys = {key(r) for r in scope_rows}

    moved = [k for k in aug_by if aug_by[k]["result"] != ctl_by[k]["result"]]
    out_of_scope_moved = [k for k in moved if k not in scope_keys]
    flips = []

    # expression for the compared cells, one read per volume
    rows_by_vol = defaultdict(list)
    for k in moved:
        rows_by_vol[k[0]].append(k)
    rho_cache = {}
    for vol, ks in rows_by_vol.items():
        need = sorted({g for k in ks for g in (frozen_panel[aug_by[k]["subtype"]]
                                               | set(kept[aug_by[k]["subtype"]]))})
        expr, lab = expr_for(vol, need, None)
        for k in ks:
            r = aug_by[k]
            name = r["subtype"]
            sibs = r.get("siblings") or []
            mask = lab == _label_for(name, lab)
            if not sibs:
                rho_cache[k] = None
                continue
            maskm = np.isin(lab, [_label_for(s, lab) for s in sibs])
            keep = mask | maskm
            clearing = [d["gene"] for d in (r.get("marker_detail") or [])
                        if d["q"] is not None and d["auc"] >= AUC_MIN and d["q"] < FDR_MAX]
            if len(clearing) >= 2 and all(g in expr for g in clearing[:2]):
                x, y = expr[clearing[0]][keep], expr[clearing[1]][keep]
                try:
                    rho = float(spearmanr(x, y).statistic)
                except Exception:
                    rho = None
                rho_cache[k] = None if rho is None or not np.isfinite(rho) else round(rho, 4)
            else:
                rho_cache[k] = None

    for k in moved:
        r, c = aug_by[k], ctl_by[k]
        name = r["subtype"]
        md = r.get("marker_detail") or []
        clearing = [d for d in md if d["q"] is not None and d["auc"] >= AUC_MIN and d["q"] < FDR_MAX]
        clearing_added = [d["gene"] for d in clearing if d["gene"] not in frozen_panel[name]]
        claims = {d["gene"]: claim[name].get(d["gene"], []) for d in clearing}
        shared = []
        gl = [d["gene"] for d in clearing]
        for i in range(len(gl)):
            for j in range(i + 1, len(gl)):
                inter = sorted(set(claims[gl[i]]) & set(claims[gl[j]]))
                if inter:
                    shared.append({"a": gl[i], "b": gl[j], "shared_claims": inter})
        indep = ("two_independent_claims" if (len(gl) >= 2 and not shared) else
                 ("shared_source" if len(gl) >= 2 else "single_marker_cleared"))
        fam = [{"added": g, "other": h, "stem": stem(g)} for g in clearing_added for h in gl
               if h != g and stem(h) == stem(g)]
        rho = rho_cache.get(k)
        flags = []
        if indep != "two_independent_claims":
            flags.append(indep)
        if rho is not None and abs(rho) >= RHO_FLAG:
            flags.append("high_coexpression")
        if fam:
            flags.append("same_symbol_family")
        # measurability of the added gene that actually cleared (or of the kept set)
        mrow = {g: (meas["volumes"].get(k[0], {}).get("genes") or {}).get(g) for g in
                (clearing_added or kept[name])}
        flips.append({"volume": k[0], "subtype": name, "n_cells": r["n_cells"],
                      "before_result": c["result"], "after_result": r["result"],
                      "before_reason": c["reason"], "after_reason": r["reason"],
                      "clearing_markers": [{"gene": d["gene"], "auc": d["auc"], "q": d["q"],
                                            "added": d["gene"] not in frozen_panel[name],
                                            "claims": claims[d["gene"]]} for d in clearing],
                      "added_genes_in_panel": kept[name],
                      "clearing_added": clearing_added,
                      "independence": indep, "shared_claims": shared,
                      "spearman_clearing_pair": rho,
                      "symbol_family_collisions": fam,
                      "flags": flags,
                      "verdict": "corroborated" if not flags else "flip_flagged",
                      "added_gene_measurability_in_this_volume": mrow})

    repro = {"probe": "m4_flips.py",
             "frozen_rows": len(frozen), "control_rows": len(ctl), "augmented_rows": len(aug),
             "control_reproduces_frozen_verdicts":
                 all(frozen_by[k]["result"] == ctl_by[k]["result"] for k in frozen_by),
             "n_verdict_changes": len(moved),
             "n_in_scope_changes": len([k for k in moved if k in scope_keys]),
             "out_of_scope_moved": [{"volume": k[0], "subtype": k[1], "before": ctl_by[k]["result"],
                                     "after": aug_by[k]["result"]} for k in out_of_scope_moved],
             "out_of_scope_moved_n": len(out_of_scope_moved),
             "before_counts": dict(Counter(r["result"] for r in ctl)),
             "after_counts": dict(Counter(r["result"] for r in aug))}
    json.dump(repro, open(os.path.join(OUT, "RULER_REPRO_CHECK.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"probe": "m4_flips.py", "auc_min": AUC_MIN, "fdr_max": FDR_MAX, "rho_flag": RHO_FLAG,
               "n_flips": len(flips), "flips": flips},
              open(os.path.join(OUT, "FLIPS.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cols = ["volume", "subtype", "n_cells", "before_result", "after_result", "clearing",
            "clearing_added", "independence", "spearman_clearing_pair", "flags", "verdict"]
    with open(os.path.join(OUT, "FLIPS.tsv"), "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for f in flips:
            fh.write("\t".join([
                f["volume"], f["subtype"], str(f["n_cells"]), f["before_result"], f["after_result"],
                ";".join("%s=%.3f/q=%.4g%s" % (m["gene"], m["auc"], m["q"], "*" if m["added"] else "")
                         for m in f["clearing_markers"]),
                ",".join(f["clearing_added"]), f["independence"],
                str(f["spearman_clearing_pair"]), ",".join(f["flags"]), f["verdict"]]) + "\n")

    print("verdict changes: %d (in-scope %d, out-of-scope %d)"
          % (len(moved), len([k for k in moved if k in scope_keys]), len(out_of_scope_moved)))
    print("before:", repro["before_counts"], "-> after:", repro["after_counts"])
    for f in flips:
        print("  %-22s %-58s %s -> %s | added=%s | %s | rho=%s | %s"
              % (f["volume"], f["subtype"], f["before_result"], f["after_result"],
                 f["clearing_added"], f["independence"], f["spearman_clearing_pair"], f["verdict"]))
        print("      clearing:", [(m["gene"], m["auc"], round(m["q"], 5), "ADDED" if m["added"] else "frozen")
                                  for m in f["clearing_markers"]], "flags:", f["flags"])
    print("wrote FLIPS.json/.tsv + RULER_REPRO_CHECK.json")
    return 0 if not out_of_scope_moved else 1


def _label_for(name, lab):
    """the author label of this subtype in this volume = the label whose alias-sense equals name"""
    import json as _j
    ALIAS = {"starburst (cholinergic) amacrine cell": "starburst amacrine cell",
             "midget retinal ganglion cell": "midget ganglion cell of retina",
             "parasol retinal ganglion cell": "parasol ganglion cell of retina",
             "OFF-center retinal ganglion cell (sublamina a)": "OFF midget ganglion cell",
             "ON-center retinal ganglion cell (sublamina b)": "ON parasol ganglion cell",
             "rod bipolar cell (RBC, ON rod bipolar)": "rod bipolar cell",
             "flat midget bipolar cell (FMB, OFF midget bipolar)": "flat midget bipolar cell",
             "invaginating midget bipolar cell (IMB, ON midget bipolar)": "invaginating midget bipolar cell",
             "Retinal astrocyte (pan-retinal resident population)": "retinal astrocyte",
             "S-cone photoreceptor (S cone)": "S cone cell",
             "blue-cone bipolar cell (BB, S-cone ON bipolar)": "ON-blue cone bipolar cell",
             "OFFx bipolar cell (primate outer-stratifying OFF bipolar)": "OFFx cell",
             "giant bipolar cell (GB)": "giant bipolar cell",
             "diffuse bipolar 1 (DB1)": "diffuse bipolar 1 cell",
             "diffuse bipolar 2 (DB2)": "diffuse bipolar 2 cell",
             "diffuse bipolar 3a (DB3a)": "diffuse bipolar 3a cell",
             "diffuse bipolar 3b (DB3b)": "diffuse bipolar 3b cell",
             "diffuse bipolar 4 (DB4)": "diffuse bipolar 4 cell",
             "diffuse bipolar 6 (DB6)": "diffuse bipolar 6 cell",
             "ON cone bipolar cell (ON BC)": "ON-bipolar cell",
             "OFF cone bipolar cell (OFF BC)": "OFF-bipolar cell"}
    tgt = ALIAS.get(name, name)
    return tgt


if __name__ == "__main__":
    sys.exit(main())