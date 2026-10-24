#!/usr/bin/env python3
"""RECON (complete the truncated 00_recon_reference_candidate.py output):
   HRA006282 obs audit -> donor-disjoint + adult candidate -> cell_type counts.
   Read-only. backed='r'. No downloads."""
import json, os, sys
import anndata as ad
import numpy as np

REF = "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad"
OUT = "/mnt/D/EyeKB/plans/fairex4a_20261024/out/RECON_reference_candidate_full.json"
X4A_OBS = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean/gold/x4a_input.h5ad"

a = ad.read_h5ad(REF, backed="r")
obs = a.obs
print("REF shape", a.shape)
print("obs cols", list(obs.columns))
q = ad.read_h5ad(X4A_OBS, backed="r")
qd = set(map(str, q.obs["donor_id"].unique())) if "donor_id" in q.obs.columns else None
print("x4a obs cols", list(q.obs.columns))
if qd is None:
    # find donor-ish col
    for c in q.obs.columns:
        if "donor" in c.lower() or "sample" in c.lower():
            print("  cand donor col", c, q.obs[c].unique()[:25])

rec = {
    "ref_path": REF, "ref_shape": list(a.shape), "obs_columns": list(obs.columns),
    "x4a_donors": sorted(qd) if qd else None,
}
# donor col detection in ref
don_col = None
for c in ["donor_id", "donor", "Donor", "sample", "Sample"]:
    if c in obs.columns:
        don_col = c; break
print("ref donor col:", don_col)
if don_col:
    dv = obs[don_col].astype(str)
    rec["ref_n_donors_total"] = int(dv.nunique())
    on_x4a = dv.isin(qd)
    rec["cells_on_x4a_donors"] = int(on_x4a.sum())
    rec["donors_on_x4a_donors"] = sorted(set(dv[on_x4a].unique()))
    rec["donors_not_on_x4a"] = sorted(set(dv[~on_x4a].unique()))
    rec["n_ref_cells_kept_donor_disjoint"] = int((~on_x4a).sum())

# age
age_col = None
for c in ["donor_age", "age", "Age"]:
    if c in obs.columns:
        age_col = c; break
print("age col:", age_col)
if age_col:
    av = obs[age_col].astype(str)
    rec["age_col"] = age_col
    rec["age_value_counts"] = {str(k): int(v) for k, v in av.value_counts().items()}

ct_col = None
for c in ["cell_type", "CellType", "celltype", "author_cell_type"]:
    if c in obs.columns:
        ct_col = c; break
print("ct col:", ct_col)
rec["ct_col"] = ct_col

# candidate = donor-disjoint + adult
mask = ~obs[don_col].astype(str).isin(qd)
def is_adult(v):
    s = str(v).strip().lower()
    if s in ("", "nan", "unknown", "not reported"): return None
    if s.endswith("day") or s.endswith("days") or s.endswith("week") or s.endswith("weeks") \
       or s.endswith("month") or s.endswith("months") or s.endswith("year") or s.endswith("years") \
       or s.endswith("hour") or s.endswith("hours"):
        num = s.split()[0].replace(">", "").replace("<", "")
        try: n = float(num)
        except ValueError: return None
        if s.endswith("day") or s.endswith("days") or s.endswith("hour") or s.endswith("hours"):
            return n / 365.25
        if s.endswith("week") or s.endswith("weeks"): return n / 52.0
        if s.endswith("month") or s.endswith("months"): return n / 12.0
        return n
    return None
if age_col:
    ages = obs[age_col].astype(str).map(is_adult)
    rec["n_age_unparsed"] = int(ages.isna().sum())
    rec["n_age_unparsed_values"] = {str(k): int(v) for k, v in obs[age_col].astype(str)[ages.isna()].value_counts().items()}
    mask = mask & (ages.notna()) & (ages >= 18)
rec["candidate_n_cells"] = int(mask.sum())
cand_don = obs[don_col].astype(str)[mask]
rec["candidate_n_donors"] = int(cand_don.nunique())
rec["candidate_donors"] = sorted(set(cand_don.unique()))
if ct_col:
    cts = obs[ct_col].astype(str)[mask]
    rec["candidate_cell_type_counts"] = {str(k): int(v) for k, v in cts.value_counts().items()}
# also source / study col
for c in obs.columns:
    if any(k in c.lower() for k in ["source", "study", "dataset", "collection"]):
        rec["col_" + c] = {str(k): int(v) for k, v in obs[c].astype(str)[mask].value_counts().items()}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(rec, open(OUT, "w"), ensure_ascii=False, indent=1)
print("RECON_FULL_OK", OUT)
print(json.dumps({k: rec[k] for k in rec if k.startswith("candidate_")}, ensure_ascii=False)[:3000])