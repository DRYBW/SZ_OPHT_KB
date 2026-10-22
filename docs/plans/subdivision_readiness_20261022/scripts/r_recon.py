#!/usr/bin/env python3
"""Recon for the subdivision-readiness wave (2026-10-22).

Read-only, no network. Establishes:
  R1 the 76 dictionary parent rows and their shipped CL ids;
  R2 ontology depth (is_a descendants + how many child NAMES resolve) from the FIXED CL snapshot,
     with the snapshot's sha256 recorded;
  R3 the evaluation-source set: where each of the 28 evaluation volumes came from, and which corpus
     papers carry those accessions (so discovery and evaluation sources can be separated);
  R4 the machine inventory of non-evaluation expression material.

Nothing here proposes a gene or a class name from a reference label.
"""
import collections
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, "/mnt/D/EyeKB/plans/holefill_v12_20261021")
import cl_nav  # noqa: E402

OUT = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022/out"
os.makedirs(OUT, exist_ok=True)

DICT = "/home/ubuntu/EYEKB_REPO/kb/markers/markers_cl_alignment_v2_unified.json"
OBO = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"
VOLS = "/mnt/D/EyeKB/plans/oss_check_20261019/dl/workdir"


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


print("== R0 ontology snapshot ==", flush=True)
obo_sha = sha256(OBO)
d = cl_nav.load(OBO)
print(f"   path   {OBO}")
print(f"   sha256 {obo_sha}")
print(f"   release {d['release']}   terms={len(d['terms'])}")
snap = {"path": OBO, "sha256": obo_sha, "release": d["release"],
        "n_terms": len(d["terms"]), "n_labels_indexed": len(d["label2id"])}
json.dump(snap, open(f"{OUT}/R0_ontology_snapshot.json", "w"), ensure_ascii=False, indent=1)

print("\n== R1+R2 the 76 shipped rows and their ontology depth ==", flush=True)
dic = json.load(open(DICT))
labels = dic["labels"]
terms = d["terms"]
rows = []
for lab, meta in labels.items():
    cid = meta.get("cl_id")
    desc = cl_nav.descendants(cid, OBO) if cid else []
    named = [x for x in desc if (terms.get(x) or {}).get("name")]
    rows.append({
        "class": lab,
        "cl_id": cid,
        "cl_label": meta.get("cl_label"),
        "status": meta.get("status"),
        "qualifier": meta.get("qualifier"),
        "libraries": meta.get("libraries") or [],
        "n_is_a_descendants": len(desc),
        "n_descendant_names_resolve": len(named),
        "descendant_ids": desc,
        "descendant_named": sorted((terms[x]["name"] for x in named)),
    })
rows.sort(key=lambda r: r["class"])
json.dump(rows, open(f"{OUT}/R1R2_parent_depth.json", "w"), ensure_ascii=False, indent=1)
n_no_cl = sum(1 for r in rows if not r["cl_id"])
tot_desc = sum(r["n_is_a_descendants"] for r in rows)
tot_named = sum(r["n_descendant_names_resolve"] for r in rows)
print(f"   rows={len(rows)}  without CL id={n_no_cl}")
print(f"   total is_a descendants={tot_desc}  with a resolvable name={tot_named}")
for r in sorted(rows, key=lambda r: -r["n_is_a_descendants"])[:12]:
    print(f"   {r['class']:34s} {str(r['cl_id']):12s} desc={r['n_is_a_descendants']:4d} named={r['n_descendant_names_resolve']:4d}")

print("\n== R3 volume provenance (the evaluation set) ==", flush=True)
vols = {}
for vp in sorted(glob.glob(f"{VOLS}/*/prep_record.json")):
    vol = vp.split("/")[-2]
    try:
        p = json.load(open(vp))
    except Exception as e:
        vols[vol] = {"error": str(e)[:200]}
        continue
    vols[vol] = {"species": p.get("species"), "tissue": p.get("tissue"),
                 "n_cells": p.get("n_out"), "source": p.get("source"), "id": p.get("id")}
json.dump(vols, open(f"{OUT}/R3_volume_provenance.json", "w"), ensure_ascii=False, indent=1)
for vol, p in sorted(vols.items()):
    print(f"   {vol:28s} {str(p.get('species')):7s} {str(p.get('tissue')):18s} {p.get('n_cells')}")

# accessions / dataset identifiers we can look for in the literature corpus
acc = collections.Counter()
for vol, p in vols.items():
    s = str(p.get("source") or "")
    for m in re.findall(r"(GSE\d{4,7}|E-MTAB-\d+|PRJ[A-Z]{2}\d+|HCA\d+|CxG\d+)", s + " " + vol):
        acc[m] += 1
json.dump(dict(acc), open(f"{OUT}/R3_accessions.json", "w"), ensure_ascii=False, indent=1)
print(f"   accessions recoverable from provenance: {len(acc)} -> {sorted(acc)}")

print("\n== R4 non-evaluation expression material on this machine ==", flush=True)
inv = []
for root in ["/mnt/D/OcularKB", "/mnt/D/EyeKB", "/mnt/data/ZJY", "/home/ubuntu"]:
    if not os.path.isdir(root):
        continue
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count("/")
        if depth > 5:
            dirnames[:] = []
            continue
        dirnames[:] = [x for x in dirnames if x not in (".git", "__pycache__", "node_modules")]
        for fn in filenames:
            if fn.endswith((".h5ad", ".h5", ".rds", ".mtx")):
                fp = os.path.join(dirpath, fn)
                try:
                    sz = os.path.getsize(fp)
                except OSError:
                    continue
                inv.append({"path": fp, "bytes": sz})
                n += 1
    print(f"   {root:20s} {n} files")
inv.sort(key=lambda x: -x["bytes"])
json.dump(inv, open(f"{OUT}/R4_machine_expression_inventory.json", "w"), ensure_ascii=False, indent=1)
print(f"   total {len(inv)} expression-like files, {sum(x['bytes'] for x in inv)/2**30:.1f} GiB")
print("[recon done]", flush=True)