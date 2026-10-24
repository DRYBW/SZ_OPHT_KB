#!/usr/bin/env python3
"""STEP 11d — provenance/homology measurement for the B-arm reference (disclosure, not a control).

Question it answers, with numbers instead of assertion:
  how much of X4A does the collection that supplies the reference actually contain, and how
  close are the two label systems on the SAME cells?
Method: X4A cell ids are "<sample>_<barcode>"; HRA006282 ids are "<donor>_<tissue>_<barcode>".
Match on (donor_id, barcode). X4A's 19 donors are EXCLUDED from the reference, so no query cell
is scored against itself — this file measures annotation-system homology, not cell leakage.
Output: out/REFERENCE_LABEL_HOMOLOGY.json
"""
import json, collections
import numpy as np, anndata as ad

REF = "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad"
X4A = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean/gold/x4a_input.h5ad"
O = "/mnt/D/EyeKB/plans/fairex4a_20261024/out/REFERENCE_LABEL_HOMOLOGY.json"

q = ad.read_h5ad(X4A, backed="r")
qid = [str(x) for x in q.obs_names]
qdon = [str(x) for x in q.obs["donor_id"]]
qct = [str(x) for x in q.obs["cell_type"]]
qauth = [str(x) for x in q.obs["author_label"]] if "author_label" in q.obs else [""] * len(qid)
x4a_donors = set(qdon)

a = ad.read_h5ad(REF, backed="r")
rid = [str(x) for x in a.obs_names]
rdon = [str(x) for x in a.obs["donor_id"]]
rct = [str(x) for x in a.obs["cell_type"]]
rauth = [str(x) for x in a.obs["author_cell_type"]] if "author_cell_type" in a.obs else [""] * len(rid)

# HRA rows on X4A donors -> (donor, barcode) -> label lists
by_don_bar = collections.defaultdict(list)
on_x4a_donors = 0
for i, (d, x) in enumerate(zip(rdon, rid)):
    if d in x4a_donors:
        on_x4a_donors += 1
        parts = x.split("_")
        by_don_bar[(d, parts[-1])].append(i)

bar_x4a = set()
matched = 0
amb = 0
ct_agree = 0
auth_agree = 0
ct_cmp = 0
uniq = 0
for i, (d, x) in enumerate(zip(qdon, qid)):
    bar = x.split("_", 1)[1]
    bar_x4a.add((d, bar))
    hit = by_don_bar.get((d, bar))
    if not hit:
        continue
    matched += 1
    if len(hit) > 1:
        amb += 1
    j = hit[0]
    if len(hit) == 1:
        uniq += 1
    ct_cmp += 1
    ct_agree += int(rct[j] == qct[i])
    if rauth[j] and qauth[i]:
        auth_agree += int(rauth[j] == qauth[i])

res = {
    "reference": REF, "query": X4A,
    "n_x4a_cells": len(qid), "n_x4a_distinct_donor_barcode": len(bar_x4a),
    "n_reference_cells_on_x4a_donors": on_x4a_donors,
    "n_x4a_cells_matched_in_reference_on_same_donor": matched,
    "match_rate_over_cells": round(matched / len(qid), 4),
    "n_matches_ambiguous_within_donor": amb,
    "n_unambiguous_matches": uniq,
    "cell_type_label_identity_on_matched": round(ct_agree / ct_cmp, 4) if ct_cmp else None,
    "author_cell_type_label_identity_on_matched": round(auth_agree / ct_cmp, 4) if ct_cmp else None,
    "note": ("X4A's 19 donors are excluded from the reference, so no query cell is in the reference index. "
             "What this measures is that reference and query come from the SAME CELLxGENE collection "
             "(HRA006282) and carry homologous annotation columns; the refswap reading must be read with that in mind."),
}
json.dump(res, open(O, "w"), ensure_ascii=False, indent=1)
print("HOMOLOGY_OK", json.dumps(res, ensure_ascii=False, indent=1))