#!/usr/bin/env python3
"""FAIRX4A / step 00 — recon only (no scoring, no writes to official artifacts).

Reads:
  X4A input h5ad (gold/x4a_input.h5ad) obs
  HRA006282_optic_nerve.h5ad obs (adult posterior-segment reference candidate)
Produces:
  out/RECON_reference_candidate.json  — donor/cell accounting + class counts after
                                        (a) excluding the 19 X4A donors, (b) keeping donor_age>=18
Read-only on all inputs. Prints every number it writes.
"""
import json, os, re, collections
import anndata as ad

P = "/mnt/D/EyeKB/plans/toolbenchmark_20261010_x4clean"
WORK = "/mnt/D/EyeKB/plans/fairex4a_20261024"
HRA = "/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad"

# --- X4A donors (from the frozen gold volume, obs column donor_id) ---
x = ad.read_h5ad(f"{P}/gold/x4a_input.h5ad", backed="r")
x4a_donors = sorted(x.obs["donor_id"].astype(str).unique().tolist())
x4a_ct = collections.Counter(x.obs["cell_type"].astype(str))
x4a_tissue = collections.Counter(x.obs["tissue"].astype(str))
x4a_ids = set(map(str, x.obs_names))
print("X4A cells", x.n_obs, "donors", len(x4a_donors), x4a_donors)
print("X4A tissues", dict(x4a_tissue))

# --- HRA006282 obs ---
h = ad.read_h5ad(HRA, backed="r")
o = h.obs
d = o["donor_id"].astype(str)

def yrs(s):
    m = re.match(r"\s*(\d+)\s*year", str(s))
    return int(m.group(1)) if m else None

age_n = [yrs(s) for s in o["donor_age"].astype(str)]
unparsed = collections.Counter(str(s) for s, a in zip(o["donor_age"].astype(str), age_n) if a is None)

overlap_cells = d.isin(x4a_donors)
print("HRA cells on X4A donors:", int(overlap_cells.sum()))
print("HRA donors on X4A donors:", sorted(d[overlap_cells.values].unique()))

# exact cell-id overlap (belt and braces)
h_ids_sample = set(map(str, o.index[:200000]))
print("cell-id overlap (HRA first 200k vs X4A):", len(h_ids_sample & x4a_ids))
print("X4A cell ids containing 'ODON':", sum(1 for i in list(x4a_ids)[:5000] if "ODON" in i), "/5000")

keep = (not_overlap := ~overlap_cells.values) & [a is not None and a >= 18 for a in age_n]
import numpy as np
keep = np.asarray(not_overlap, dtype=bool) & np.asarray([a is not None and a >= 18 for a in age_n], dtype=bool)
print("reference candidate cells (donor-disjoint & adult>=18):", int(keep.sum()),
      "donors", o.loc[keep, "donor_id"].nunique())
ct = o.loc[keep, "cell_type"].astype(str)
print("reference candidate cell_type counts:")
for k, v in ct.value_counts().items():
    print(f"  {v:7d} {k}")

out = {
    "x4a": {"n_cells": int(x.n_obs), "donors": x4a_donors,
            "cell_type_counts": dict(x4a_ct), "tissue_counts": dict(x4a_tissue)},
    "hra006282": {
        "path": HRA, "n_cells": int(h.n_obs),
        "n_donors_total": int(o["donor_id"].nunique()),
        "cells_on_x4a_donors": int(overlap_cells.sum()),
        "donors_on_x4a_donors": sorted(d[overlap_cells.values].unique().tolist()),
        "unparsed_donor_age": dict(unparsed),
        "candidate_n_cells": int(keep.sum()),
        "candidate_n_donors": int(o.loc[keep, "donor_id"].nunique()),
        "candidate_cell_type_counts": dict(ct.value_counts()),
        "candidate_source": dict(o.loc[keep, "source"].astype(str).value_counts()),
        "candidate_institute": dict(o.loc[keep, "institute"].astype(str).value_counts()),
        "candidate_tissue": dict(o.loc[keep, "tissue"].astype(str).value_counts()),
        "candidate_assay": dict(o.loc[keep, "assay"].astype(str).value_counts()),
        "candidate_suspension": dict(o.loc[keep, "suspension_type"].astype(str).value_counts()),
        "donor_age_min": int(min(a for a, k in zip(age_n, keep) if k)),
        "donor_age_max": int(max(a for a, k in zip(age_n, keep) if k)),
    },
    "cellid_overlap_first200k": len(h_ids_sample & x4a_ids),
}
os.makedirs(f"{WORK}/out", exist_ok=True)
with open(f"{WORK}/out/RECON_reference_candidate.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("WROTE", f"{WORK}/out/RECON_reference_candidate.json")
