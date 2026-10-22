#!/usr/bin/env python3
"""Field 7: independent, non-evaluation material on this machine (Annex A9).

A local expression file is a candidate iff it is not under the evaluation tree and its path carries no
evaluation cohort alias. Each candidate is opened backed='r' and its obs string columns are scanned; every
distinct label is resolved to a Cell Ontology id through the fixed snapshot (preferred name or synonym).

A file that cannot be opened is reported NOT_RUN with its path and is never counted as a negative.
Read-only, no network, no download.
"""
import collections
import glob
import json
import os
import sys

import anndata as ad

sys.path.insert(0, "/mnt/D/EyeKB/plans/holefill_v12_20261021")
import cl_nav  # noqa: E402

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
OBO = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"

ROOTS = ["/mnt/D/OcularKB", "/mnt/D/EyeKB"]
EXCLUDE_SUBSTR = ["/plans/oss_check_20261019/", "/subdivision_readiness_20261022/"]
ALIASES = ["CX01", "CX02", "CX03", "CX04", "CX07", "CX08", "CX09", "CX10", "CX11", "CX12",
           "CX13", "CX14", "CX15", "CX16", "CX17", "PRE_OA-D001", "PRE_OA-D002", "PRE_OA-D004",
           "PRE_OA-D068", "GSE199013", "GSE268630", "OA-D001", "OA-D002", "OA-D004", "OA-D068"]

MAXDEPTH = 7


def is_candidate(path):
    if any(s in path for s in EXCLUDE_SUBSTR):
        return False
    for a in ALIASES:
        if a in path:
            return False
    return True


def main():
    obo = cl_nav.load(OBO)
    lab2id, syn2id = obo["label2id"], obo["synonym2id"]

    files = []
    for root in ROOTS:
        for dp, dn, fn in os.walk(root):
            if dp[len(root):].count("/") > MAXDEPTH:
                dn[:] = []
                continue
            dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
            for f in fn:
                if f.endswith(".h5ad"):
                    p = os.path.join(dp, f)
                    if is_candidate(p):
                        files.append(p)
    files.sort()
    print(f"candidate non-evaluation .h5ad files: {len(files)}", flush=True)

    inv, notrun = {}, []
    for i, p in enumerate(files, 1):
        rec = {"path": p}
        try:
            rec["bytes"] = os.path.getsize(p)
            a = ad.read_h5ad(p, backed="r")
            rec["n_obs"] = int(a.n_obs)
            rec["n_vars"] = int(a.n_vars)
            cols = [c for c in a.obs.columns if str(a.obs[c].dtype) in ("object", "category", "string")]
            ids, labels = set(), set()
            for c in cols:
                try:
                    vals = a.obs[c].astype(str).unique().tolist()
                except Exception:
                    continue
                for v in vals:
                    k = str(v).strip().lower()
                    if not k or len(k) > 80:
                        continue
                    cid = lab2id.get(k) or syn2id.get(k)
                    if cid:
                        ids.add(cid)
                        labels.add(str(v))
            a.file.close()
            rec["obs_string_columns"] = cols
            rec["n_labels_resolved"] = len(labels)
            rec["resolved_cl_ids"] = sorted(ids)
            rec["resolved_labels"] = sorted(labels)[:200]
        except Exception as e:
            rec["error"] = str(e)[:200]
            notrun.append(p)
        inv[p] = rec
        if i % 25 == 0 or i == len(files):
            print(f"   [{i}/{len(files)}] resolved={rec.get('n_labels_resolved')} "
                  f"errors={len(notrun)}", flush=True)

    doc = {"roots": ROOTS, "excluded_substrings": EXCLUDE_SUBSTR, "excluded_aliases": ALIASES,
           "n_candidates": len(files), "n_opened": len(files) - len(notrun),
           "n_not_run": len(notrun), "not_run_paths": notrun,
           "datasets": inv,
           "note": "files that could not be opened are NOT_RUN and are never counted as negatives"}
    json.dump(doc, open(f"{OUT}/M_non_evaluation_material.json", "w"), ensure_ascii=False, indent=1)
    print(f"opened={len(files)-len(notrun)}  not_run={len(notrun)}")
    print("wrote", f"{OUT}/M_non_evaluation_material.json")


if __name__ == "__main__":
    main()