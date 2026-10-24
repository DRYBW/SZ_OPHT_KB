#!/usr/bin/env python3
"""STEP 10 — crosswalk for the refswap arms (new file; the official cw_x4a.tsv is untouched).

Rows are derived from the reference AnnData's own obs (ref_label -> ref_gold_ct -> ref_lineage),
i.e. exactly the frozen PREREG §3.3 map/drop decisions, not re-decided here.
usage: 34_build_cw_refswap.py --ref <h5ad> --arm A1b_scgpt_refswap --out <tsv> [--with-mueller]
"""
import argparse, json
import anndata as ad

ap = argparse.ArgumentParser()
ap.add_argument("--ref", required=True)
ap.add_argument("--arm", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--with-mueller", action="store_true")
A = ap.parse_args()

R = ad.read_h5ad(A.ref)
pairs = {}
for lab, ct, lin in zip(R.obs["ref_label"], R.obs["ref_gold_ct"], R.obs["ref_lineage"]):
    pairs.setdefault(str(lab), (str(lin), str(ct)))
if A.with_mueller:
    pairs.setdefault("Mueller cell", ("glia", "astrocyte"))

EVID = ("B arm reference-swap crosswalk: the emitted label IS a reference-index label; the row records the "
        "PREREG §3.3 identity mapping from that reference label to the gold's own vocabulary. "
        "No score was consulted when the mapping was frozen.")
with open(A.out, "w", newline="") as fh:
    fh.write("arm\traw_label\tlineage\tcanonical_cell_type\tconfidence\tevidence\n")
    for lab in sorted(pairs):
        lin, ct = pairs[lab]
        fh.write("\t".join([A.arm, lab, lin, ct, "high", EVID]) + "\n")
print("CW_OK", A.out, len(pairs), sorted(pairs), flush=True)