#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m2 -- measurability of the admitted candidates in each in-scope volume (PREREG section 6).

M1: the symbol occurs in the volume's var/_index.
M2: detection floor -- the symbol is detected (X > 0) in >= 5 % of ALL cells of that volume.

Technical floors only: no comparison between the subtype's cells and the sibling cells is read here,
so nothing in this step can favour a gene that "looks good".  Each volume is read once, exactly the
way the ruler reads it (full CSR), and only the candidate columns are kept.

Writes out/SUBTYPE_SECOND_MARKER_MEASURABILITY.json and a per-row view out/..._MEASURABILITY.tsv.
"""
import json
import os
import resource
import sys
import time

import h5py
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
WORKDIR = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/workdir"
VOLUMES = ["CX01_retina_snRNA", "CX03_retina_multiome", "CX04_cowan_fovea", "CX04_cowan_organoid",
           "CX04_cowan_periphery", "PRE_GSE268630", "PRE_OA-D001", "PRE_OA-D068"]
FLOOR = 0.05


def measure(vol, genes):
    path = os.path.join(WORKDIR, vol, "input.h5ad")
    if not os.path.isfile(path):
        return {"volume": vol, "error": "no input.h5ad"}
    out = {"volume": vol, "genes": {}}
    with h5py.File(path, "r") as f:
        idx = np.array([x.decode() if isinstance(x, bytes) else str(x)
                        for x in f["var"]["_index"][:]], dtype=object)
        pos = {}
        for g in genes:
            hit = np.where(idx == g)[0]
            if hit.size:
                pos[g] = int(hit[0])
        out["n_genes_in_file"] = int(len(idx))
        out["n_candidates_in_var_index"] = len(pos)
        X = f["X"]
        if isinstance(X, h5py.Group):
            shape = tuple(int(x) for x in X.attrs["shape"])
            mat = sp.csr_matrix((X["data"][:], X["indices"][:], X["indptr"][:]), shape=shape)
            n_cells = shape[0]
            if pos:
                cols = [pos[g] for g in sorted(pos)]
                blk = np.asarray(mat.tocsc()[:, cols].todense())
                for i, g in enumerate(sorted(pos)):
                    col = blk[:, i]
                    out["genes"][g] = {"in_var_index": True,
                                       "detected_frac": round(float((col > 0).mean()), 5),
                                       "above_floor": bool((col > 0).mean() >= FLOOR)}
            del mat
            if pos:
                del blk
        else:
            raise SystemExit("dense X not supported")
        out["n_cells"] = int(n_cells)
    return out


def main():
    lit = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), encoding="utf-8"))
    genes = sorted({r["gene"] for r in lit["rows"] if r["admitted"]})
    print("candidates to measure:", len(genes))
    res = {"probe": "m2_measurability.py", "floor": FLOOR, "volumes": {}, "n_candidates": len(genes)}
    for vol in VOLUMES:
        t0 = time.time()
        d = measure(vol, genes)
        d["wall_s"] = round(time.time() - t0, 1)
        d["peak_rss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        res["volumes"][vol] = d
        print("  [vol] %-24s cells=%-7s candidates_in_var_index=%s wall=%ss peak_rss=%.2fG"
              % (vol, d.get("n_cells"), d.get("n_candidates_in_var_index"), d.get("wall_s"),
                 d["peak_rss_kb"] / 1048576.0), flush=True)
    json.dump(res, open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_MEASURABILITY.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)

    # per (subtype, kept candidate, volume-with-a-row) view
    sep = json.load(open("/mnt/D/EyeKB/plans/consensus_subtype_20261022/out/SUBTYPE_SEPARATION.json",
                         encoding="utf-8"))
    scope_rows = [r for r in sep if r["result"] == "not_separated"
                  and str(r.get("reason", "")).startswith("1 marker(s) cleared the gate")]
    kept = {}
    for r in lit["rows"]:
        if r["kept_l5"]:
            kept.setdefault(r["subtype"], []).append(r)
    lines = ["subtype\tgene\tvolume\tin_var_index\tdetected_frac\tabove_floor\tverdict"]
    for row in scope_rows:
        s, vol = row["subtype"], row["volume"]
        for r in kept.get(s, []):
            g = r["gene"]
            rec = (res["volumes"].get(vol, {}).get("genes") or {}).get(g)
            if rec is None:
                if (res["volumes"].get(vol, {}).get("error")):
                    v = "volume_unreadable"
                else:
                    v = "not_measurable_not_in_var_index"
                lines.append("%s\t%s\t%s\tFalse\t\t\t%s" % (s, g, vol, v))
            else:
                v = "measurable" if rec["above_floor"] else "not_measurable_below_floor"
                lines.append("%s\t%s\t%s\tTrue\t%s\t%s\t%s"
                             % (s, g, vol, rec["detected_frac"], rec["above_floor"], v))
    with open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_MEASURABILITY.tsv"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote MEASURABILITY json/tsv; rows=%d" % (len(lines) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())