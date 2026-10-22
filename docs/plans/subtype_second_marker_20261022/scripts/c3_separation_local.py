#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c3_separation.py -- can the material carry each literature-consensus retinal subtype?

LOCAL COPY (card t_7509a1a2, SUBTYPE-2M). Byte-identical to
plans/consensus_subtype_20261022/scripts/c3_separation.py except for ONE two-line repair, recorded
as out/RULER_PATCH.json (unified diff + both sha256 + the reproduction proof):

  the frozen file crashes on any subtype whose marker set contains an entry with p_ = None (the
  degenerate constant-vs-constant case it handles at line 241 by assigning AUC 0.5): the reporting
  comprehension indexes `qs` -- which only holds the non-None p-values -- with the index over ALL
  entries, so the two drift apart and `IndexError` is raised.  The frozen run never contained a
  constant marker in a scored subtype, so the ruler's own result is unaffected; the repair re-indexes
  the q values through a `qmap` built during the same walk, which is equivalent for every entry whose
  p-value exists.  Thresholds, statistics, gates and every other line are untouched, and the frozen
  CONTROL arm is re-run with this copy to prove the frozen 56-row result comes back identically.

The question this answers is NOT "what did our annotator call this cluster". It is the prior one:
for the subtypes the field generally recognises, do the cells we have actually separate from their
nearest sibling on the subtype's own defining markers?

Design (pre-registered in PREREG_CONSENSUS_SUBTYPE_20261022.md, thresholds fixed there)
----------------------------------------------------------------------------------------
* Unit of analysis: a release population = the author-labelled cells of one subtype in one volume.
  Only labels that are the subtype's OWN name count.  A cluster labelled with the generic parent
  (e.g. "amacrine cell") is never used as evidence that a specific amacrine subtype is present --
  being present is not the same as being distinguishable.
* Per marker gene: AUC between the release population's cells and the cells of its SIBLINGS
  (same parent family, different subtype label, same volume).  Mann-Whitney U for the p value,
  Benjamini-Hochberg across the subtype's markers.
* S-GATE: `separated` requires >= 2 defining markers with AUC >= 0.70 at FDR < 0.05.
* S-N: a population below 30 cells cannot be scored.
* S-PRIOR: the observed share of the parent is compared with the share the literature states, where
  the list carries one; a split whose observed share is off by more than 4x either way is reported
  as `not_separated_prior_violation` even when the markers separate.
* Anything below the observability budget is `insufficient_evidence`, never `not_separated`.

Reads the volumes read-only, straight from their h5ad files.  Writes one TSV under --out.
Standard library + numpy/scipy only; no network.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
import h5py
import scipy.sparse as sp
from scipy.stats import mannwhitneyu  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
WORKDIR = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/workdir"
LEDGER_SCRIPTS = "/home/ubuntu/EYEKB_REPO/docs/plans/noregr_20261022/scripts"
MIN_CELLS = 30

# Sibling definition.  The recorded ledger's `ref_family` column groups labels for grading purposes
# and is NOT a parent-type map: it files "rod bipolar cell" under `rod` and "ON-blue cone bipolar
# cell" under `cone`, so using it puts rod bipolar next to rod photoreceptors and turns a trivial
# comparison into an apparent separation.  Siblings are defined here explicitly, as the other
# subtypes of the same parent cell type.
PARENT_OF = {
    "rod bipolar cell": "bipolar", "invaginating midget bipolar cell": "bipolar",
    "flat midget bipolar cell": "bipolar", "diffuse bipolar 1 cell": "bipolar",
    "diffuse bipolar 2 cell": "bipolar", "diffuse bipolar 3a cell": "bipolar",
    "diffuse bipolar 3b cell": "bipolar", "diffuse bipolar 4 cell": "bipolar",
    "diffuse bipolar 6 cell": "bipolar", "giant bipolar cell": "bipolar",
    "OFFx cell": "bipolar", "ON-blue cone bipolar cell": "bipolar",
    "ON-bipolar cell": "bipolar", "OFF-bipolar cell": "bipolar",
    "retinal bipolar neuron": "bipolar",
    "H1 horizontal cell": "horizontal", "H2 horizontal cell": "horizontal",
    "retina horizontal cell": "horizontal",
    "midget ganglion cell of retina": "rgc", "parasol ganglion cell of retina": "rgc",
    "OFF midget ganglion cell": "rgc", "ON parasol ganglion cell": "rgc",
    "OFF parasol ganglion cell": "rgc", "retinal ganglion cell": "rgc",
    "starburst amacrine cell": "amacrine", "amacrine cell": "amacrine",
    "GABAergic amacrine cell": "amacrine", "glycinergic amacrine cell": "amacrine",
    "S cone cell": "cone", "retinal cone cell": "cone",
    "Mueller cell": "mg", "retinal rod cell": "rod",
    "astrocyte": "astro", "microglial cell": "micro",
}

AUC_MIN = 0.70
FDR_MAX = 0.05
SHARE_FACTOR = 4.0

sys.path.insert(0, LEDGER_SCRIPTS)


def read_cat(g, name):
    node = g[name]
    if isinstance(node, h5py.Group):
        cats = [c.decode() if isinstance(c, bytes) else str(c) for c in node["categories"][:]]
        codes = node["codes"][:]
        return np.array([cats[c] if 0 <= c < len(cats) else "" for c in codes], dtype=object)
    arr = node[:]
    if getattr(arr, "dtype", None) is not None and arr.dtype.kind in "SO":
        return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in arr], dtype=object)
    return np.array(arr, dtype=object)


def var_symbols(f):
    """var_names, and a symbol column when the file carries one (some files are ENSG-identified)."""
    var = f["var"]
    idx = None
    keys = set(var.keys())
    if "_index" in keys:
        idx = read_cat(var, "_index").astype(str)
    elif "index" in keys:
        idx = read_cat(var, "index").astype(str)
    sym = None
    for cand in ("symbol", "gene_symbol", "gene_symbols", "feature_name", "gene_name"):
        if cand in keys:
            sym = read_cat(var, cand).astype(str)
            break
    return idx, sym


def values_for(vol, genes_wanted):
    """Per-cell expression for the wanted genes, and the per-cell AUTHOR cell-type label.

    These volumes carry no cluster column -- the clustering happened downstream.  They do carry the
    author's own cell_type labels, which is exactly the release population this test needs: the
    question is about the cells, not about our clustering.
    """
    path = os.path.join(WORKDIR, vol, "input.h5ad")
    if not os.path.isfile(path):
        return None
    with h5py.File(path, "r") as f:
        idx = read_cat(f["var"], "_index").astype(str) if "_index" in f["var"].keys() else None
        if idx is None:
            return None
        pos, found = {}, []
        for g in genes_wanted:
            hit = np.where(idx == g)[0]
            if hit.size:
                pos[g] = int(hit[0]); found.append(g)
        obs = f["obs"]
        lab = None
        for cand in ("cell_type", "author_cell_type"):
            if cand in obs.keys():
                lab = read_cat(obs, cand).astype(str); break
        if lab is None:
            return None
        X = f["X"]
        cols = [pos[g] for g in pos]
        if isinstance(X, h5py.Group):
            mat = sp.csr_matrix((X["data"][:], X["indices"][:], X["indptr"][:]),
                                shape=tuple(int(x) for x in X.attrs["shape"]))
            block = np.asarray(mat.tocsc()[:, cols].todense())
        else:
            block = np.asarray(X[:, cols])
        return ({g: block[:, i].astype(float) for i, g in enumerate(pos)}, lab, found)


def bh(pvals):
    n = len(pvals)
    order = np.argsort(pvals)
    out = np.empty(n)
    prev = 1.0
    for rank, i in enumerate(reversed(order), start=1):
        k = n - rank + 1
        val = min(prev, pvals[i] * n / k)
        out[i] = val
        prev = val
    return out


def auc(a, b):
    if len(a) == 0 or len(b) == 0:
        return None
    u = mannwhitneyu(a, b, alternative="two-sided")
    return float(u.statistic) / (len(a) * len(b))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--observability", default=os.path.join(WAVE, "out", "SUBTYPE_OBSERVABILITY_rows.json"))
    ap.add_argument("--out", default=os.path.join(WAVE, "out"))
    ap.add_argument("--volumes", default="")
    a = ap.parse_args()

    import wave_common as W
    calls = W.load_set()
    obs = json.load(open(a.observability, encoding="utf-8"))

    # release populations = clusters whose OWN author label is the subtype's name
    SUB = [r for r in obs if r["identifiability_verdict"] in ("visible", "marginal") and r["material_reference_label"]]
    parents = {}
    for c in calls:
        parents.setdefault(c["ref_family"], set()).add(c["ref_cell_type"])

    if a.volumes:
        vols = a.volumes.split(",")
    else:
        want_labels = {r["material_reference_label"] for r in SUB}
        vols = sorted({c["vol"] for c in calls
                       if c["tissue"] == "retina" and c.get("species") == "human"
                       and c["ref_cell_type"] in want_labels})
    genes_wanted = sorted({g for r in obs for g in (r.get("_markers_all") or r.get("markers_inside_recorded_window") or [])})
    if not genes_wanted:
        raise SystemExit("no markers to test -- check the observability table")

    rows = []
    by_label = {}
    for r in SUB:
        by_label.setdefault(r["material_reference_label"], []).append(r)
    for vol in vols:
        got = values_for(vol, genes_wanted)
        if got is None:
            print("  [skip] %s: no h5ad / no author label / no var index" % vol, flush=True)
            continue
        expr, lab, found = got
        counts = Counter(lab)
        print("  [vol] %s: %d cells, %d/%d wanted genes present in the file, %d label(s)"
              % (vol, len(lab), len(found), len(genes_wanted), len(counts)), flush=True)
        fam_of = {}
        for c in calls:
            fam_of.setdefault(c["ref_cell_type"], c["ref_family"])
        for r in SUB:
            name = r["material_reference_label"]
            if name is None or name not in counts:
                continue
            n_mine = int(counts[name])
            if n_mine < MIN_CELLS:
                rows.append(dict(volume=vol, subtype=r["subtype"], parent=r["parent"], n_cells=n_mine,
                                 result="insufficient_evidence",
                                 reason="only %d cells carry this label here" % n_mine))
                continue
            par = PARENT_OF.get(name)
            sibs = sorted(k for k in counts if k != name and PARENT_OF.get(k) == par) if par else []
            if not sibs:
                rows.append(dict(volume=vol, subtype=r["subtype"], parent=r["parent"], n_cells=n_mine,
                                 result="insufficient_evidence",
                                 reason="no sibling author label in the same parent family here"))
                continue
            mask_mine = lab == name
            mask_sib = np.isin(lab, sibs)
            if int(mask_sib.sum()) < MIN_CELLS:
                rows.append(dict(volume=vol, subtype=r["subtype"], parent=r["parent"], n_cells=n_mine,
                                 result="insufficient_evidence",
                                 reason="sibling cells fewer than %d" % MIN_CELLS))
                continue
            entries = []
            for m in (r.get("_markers_all") or []):
                g = m
                if g not in expr:
                    continue
                x, y = expr[g][mask_mine], expr[g][mask_sib]
                if np.all(x == x[0]) and np.all(y == y[0]) and x[0] == y[0]:
                    entries.append((g, 0.5, None)); continue
                u = mannwhitneyu(x, y, alternative="two-sided")
                entries.append((g, float(u.statistic) / (len(x) * len(y)), float(u.pvalue)))
            ps = np.array([e[2] for e in entries if e[2] is not None] or [1.0])
            qs = bh(ps)
            passed, qi = [], 0
            qmap = {}
            for ii, (g, a_, p_) in enumerate(entries):
                if p_ is None:
                    continue
                qmap[ii] = float(qs[qi])
                if a_ >= AUC_MIN and qs[qi] < FDR_MAX:
                    passed.append(g)
                qi += 1
            vals = list(counts.values())
            capped = vals.count(max(vals)) >= 3 and max(vals) / max(min(vals), 1) > 3
            share_obs = 100.0 * n_mine / (n_mine + int(mask_sib.sum()))
            share_exp = r.get("expected_share_pct")
            prior_note_extra = ("share not interpretable: this volume is subsampled per class"
                               if capped else "")
            prior_ok = None
            if share_exp and not capped:
                prior_ok = (share_obs / share_exp <= SHARE_FACTOR) and (share_exp / max(share_obs, 1e-9) <= SHARE_FACTOR)
            if not entries:
                result, reason = "insufficient_evidence", "none of this subtype's defining markers is present in the file"
            elif prior_ok is False:
                result, reason = "not_separated_prior_violation", (
                    "observed share %.1f%% against the literature's %s%%" % (share_obs, share_exp))
            elif len(passed) >= 2:
                result, reason = "separated", "markers clearing the gate: %s" % ", ".join(passed)
            else:
                result, reason = "not_separated", ("%d marker(s) cleared the gate; %s"
                    % (len(passed), "; ".join("%s AUC=%.2f" % (g, a_) for g, a_, _ in entries)))
            rows.append(dict(volume=vol, subtype=r["subtype"], parent=r["parent"], n_cells=n_mine,
                             n_sibling_cells=int(mask_sib.sum()), siblings=sibs,
                             observed_share_pct=None if capped else round(share_obs, 2),
                             share_interpretable=not capped, share_note=prior_note_extra,
                             expected_share_pct=share_exp,
                             result=result, reason=reason,
                             marker_detail=[{"gene": e[0], "auc": round(e[1], 3),
                                             "q": None if e[2] is None else qmap[i]}
                                            for i, e in enumerate(entries)]))
    os.makedirs(a.out, exist_ok=True)
    dest = os.path.join(a.out, "SUBTYPE_SEPARATION.tsv")
    cols = ["volume", "subtype", "parent", "n_cells", "n_sibling_cells", "siblings",
            "observed_share_pct", "share_interpretable", "share_note", "expected_share_pct",
            "result", "reason"]
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    json.dump(rows, open(os.path.join(a.out, "SUBTYPE_SEPARATION.json"), "w"), ensure_ascii=False, indent=1)
    print("\nwrote %s" % dest)
    print("rows=%d  %s" % (len(rows), dict(Counter(r["result"] for r in rows))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())