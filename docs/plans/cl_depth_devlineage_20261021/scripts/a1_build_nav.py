#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""a1_build_nav.py - build the navigable ontology artefacts.

Outputs (all under out/):
  ONT_NAV_v1.json          release identity, closure audit, germ-layer anchors resolved
                           from the file, duplicate/typedef disclosure, cross-file check
  ONT_CLOSURE_is_a.tsv     one row per active CL term: id, name, file line, parent count,
                           ancestor-closure size, descendant count
  ONT_LABELMAP_V2.tsv      every label our marker libraries ship -> CL term, with the
                           provenance of that mapping (sidecar / embedded / name match)
                           and the ontology file line the id was read from
  ONT_CROSSFILE_CHECK.json do the two local CL files agree on the terms they share

Every CL identifier written here is read from the ontology file at build time. Nothing is
typed from memory: the label -> CL mapping records the *name* it looked up and the *line*
the id was found on, and the gate (gate_ontology_nav.py) re-verifies both.

Zero network. Stdlib only.
"""
from __future__ import annotations

import collections
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from ont_nav import Ontology, CL_PREFIX, norm_name  # noqa: E402

# Primary ontology file: the card names this one explicitly.
OBO_PRIMARY = "/mnt/D/EyeKB/plans/devline_ont_20261002/downloads/cl.obo"
# Second local CL file, kept because the production judge was built against it; used only
# for a cross-file agreement check, never as a source of ids.
OBO_SECOND = "/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo"

KB_DIRS = ["/mnt/D/EyeKB/kb/markers", "/home/ubuntu/EYEKB_REPO/kb/markers"]
LIB_FILES = [
    "markers_v4.1_clean.json", "markers_v5_retina_interneuron.json",
    "markers_v6_retina_repair.json", "markers_v6_face_increment.json",
    "markers_v6_lacrimal_increment.json", "markers_v7_panel_increment.json",
    "markers_k9_ocs_increment.json", "markers_membrane_v1.json",
    "markers_v8_dev_retina.json", "markers_v9_dev_retina.json",
    "markers_v10_antseg_increment.json", "markers_v11_lensiris_increment.json",
]
SIDECAR = "markers_cl_alignment_v2_unified.json"
# Nested containers that hold class entries inside the increment files.
NESTED = ("face_increment", "stromal_repair", "lacrimal_increment")

# Germ-layer anchors: the *names* are the input; every id is resolved against the file.
GERM_LAYER_NAMES = [
    ("mesoderm", "mesodermal cell"),
    ("ectoderm", "ectodermal cell"),
    ("neural_ectoderm", "neurectodermal cell"),
    ("neural_crest", "neural crest cell"),
    ("surface_ectoderm", "surface ectodermal cell"),
    ("mesenchyme", "mesenchyme cell"),
    ("endoderm", "endodermal cell"),
    ("hematopoietic_stem_cell", "hematopoietic stem cell"),
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def entry_labels(d: dict) -> dict:
    out = {}
    m = d.get("markers")
    if isinstance(m, dict):
        out.update(m)
    for k in NESTED:
        v = d.get(k)
        if isinstance(v, dict):
            out.update({kk: vv for kk, vv in v.items() if isinstance(vv, dict)})
    return out


def find_embedded_cl(obj) -> dict:
    """Collect cl_id / cl_label nested anywhere inside one marker entry."""
    found = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("cl_id", "cl", "cl_iri", "clId") and isinstance(v, str):
                found.setdefault("cl_id", v)
            elif k in ("cl_label", "label") and isinstance(v, str):
                found.setdefault("cl_label", v)
            else:
                sub = find_embedded_cl(v)
                for kk, vv in sub.items():
                    found.setdefault(kk, vv)
    elif isinstance(obj, list):
        for v in obj:
            sub = find_embedded_cl(v)
            for kk, vv in sub.items():
                found.setdefault(kk, vv)
    return found


def collect_labels() -> dict:
    """label -> {libraries, files, embedded cl_id, embedded cl_label}."""
    rows = collections.OrderedDict()
    for fname in LIB_FILES:
        path = next((os.path.join(d, fname) for d in KB_DIRS if os.path.isfile(os.path.join(d, fname))), None)
        if not path:
            rows.setdefault("__missing_files__", set()).add(fname)
            continue
        d = json.load(open(path, encoding="utf-8"))
        lib = fname.replace("markers_", "").replace(".json", "")
        ents = entry_labels(d)
        # v10/v11 keep class entries in `entries` as well; merge when the shape differs.
        for ent in (d.get("entries") or []):
            if isinstance(ent, dict) and ent.get("class_name"):
                ents.setdefault(ent["class_name"], ent)
        for lab, ent in ents.items():
            rec = rows.setdefault(lab, {"libraries": set(), "files": set(),
                                        "embedded_cl_id": None, "embedded_cl_label": None})
            rec["libraries"].add(lib)
            rec["files"].add(path)
            emb = find_embedded_cl(ent)
            if emb.get("cl_id"):
                rec["embedded_cl_id"] = emb["cl_id"]
                rec["embedded_cl_label"] = emb.get("cl_label")
    rows.pop("__missing_files__", None)
    return rows


def main() -> int:
    os.makedirs(os.path.join(WAVE, "out"), exist_ok=True)
    ont = Ontology(OBO_PRIMARY)
    out = {"generated_by": "scripts/a1_build_nav.py",
           "primary": ont.summary(),
           "primary_path": OBO_PRIMARY,
           "closure_audit": ont.closure_is_consistent()}

    print(f"ontology: {OBO_PRIMARY}")
    print(f"  sha256   : {ont.sha256}")
    print(f"  release  : {ont.release}   (format-version {ont.format_version})")
    print(f"  CL terms : {len(ont.terms)} blocks / {len(ont.active)} active / "
          f"{len(ont.terms) - len(ont.active)} obsolete")
    print(f"  CL-namespace typedefs (not cell types): {len(ont.cl_typedefs)}")

    # ---- cross-file agreement (second local CL file) ----
    if os.path.isfile(OBO_SECOND):
        ont2 = Ontology(OBO_SECOND)
        shared = set(ont.terms) & set(ont2.terms)
        name_diff = []
        for tid in sorted(shared):
            a, b = ont.terms[tid].name, ont2.terms[tid].name
            if a != b:
                name_diff.append({"cl_id": tid, "primary": a, "second": b})
        pa, pb = set().union(*[set(ont.terms[t].parents) for t in shared]) if shared else set(), None
        parent_diff = []
        for tid in sorted(shared):
            if sorted(ont.terms[tid].parents) != sorted(ont2.terms[tid].parents):
                parent_diff.append(tid)
        out["second_file"] = {"path": OBO_SECOND, "sha256": ont2.sha256,
                              "release": ont2.release, "n_cl_terms": len(ont2.terms),
                              "n_active": len(ont2.active),
                              "n_shared": len(shared),
                              "only_in_primary": sorted(set(ont.terms) - shared)[:50],
                              "n_only_in_primary": len(set(ont.terms) - shared),
                              "only_in_second": sorted(set(ont2.terms) - shared)[:50],
                              "n_only_in_second": len(set(ont2.terms) - shared),
                              "name_disagreements": name_diff[:50],
                              "n_name_disagreements": len(name_diff),
                              "parent_disagreements": parent_diff[:50],
                              "n_parent_disagreements": len(parent_diff)}
        print(f"second file: {OBO_SECOND}")
        print(f"  release {ont2.release}  terms {len(ont2.terms)}/{len(ont2.active)} active")
        print(f"  shared ids {len(shared)}; name disagreements {len(name_diff)}; "
              f"is_a disagreements {len(parent_diff)}")
    else:
        out["second_file"] = {"path": OBO_SECOND, "missing": True}
        print(f"second file not on disk: {OBO_SECOND}")

    # ---- germ layer anchors resolved from the file ----
    anchors = []
    for key, name in GERM_LAYER_NAMES:
        r = ont.resolve(name)
        anchors.append({"key": key, "queried_name": name, "cl_id": r["cl_id"],
                        "cl_label": r["cl_label"], "method": r["method"],
                        "obo_line": ont.trace_line(r["cl_id"]) if r["cl_id"] else None,
                        "n_descendants": len(ont.descendants(r["cl_id"])) if r["cl_id"] else None})
    out["germ_layer_anchors"] = anchors
    print("germ-layer anchors resolved from the file:")
    for a in anchors:
        print(f"  {a['key']:<24} {a['queried_name']:<24} -> {a['cl_id']} "
              f"{a['cl_label']}  ({a['method']}, descendants={a['n_descendants']})")

    # ---- closure table ----
    cl_path = os.path.join(WAVE, "out", "ONT_CLOSURE_is_a.tsv")
    with open(cl_path, "w", encoding="utf-8") as f:
        f.write("cl_id\tcl_label\tobo_line\tn_parents\tn_ancestors_cl\tn_descendants\n")
        for tid in sorted(ont.active):
            t = ont.terms[tid]
            f.write(f"{tid}\t{t.name}\t{t.line}\t{len(t.parents)}\t"
                    f"{len(ont.ancestors_cl(tid))}\t{len(ont.descendants(tid))}\n")
    print(f"wrote {cl_path}  ({len(ont.active)} rows)")

    # ---- label map with provenance ----
    labels = collect_labels()
    side = json.load(open(os.path.join(KB_DIRS[0], SIDECAR), encoding="utf-8"))
    side_labels = side["labels"]
    rows, unresolved, drift = [], [], []
    for lab in sorted(labels):
        rec = labels[lab]
        cid, method, note = None, None, None
        if lab in side_labels and side_labels[lab].get("cl_id"):
            cid = side_labels[lab]["cl_id"]
            method = "sidecar"
        elif rec.get("embedded_cl_id"):
            cid = rec["embedded_cl_id"]
            method = "embedded_cl_id"
        else:
            # last resort: the label itself, folded onto the ontology by name
            r = ont.resolve(lab)
            cid, method = r["cl_id"], ("name" if r["cl_id"] else "unresolved")
            if not r["cl_id"]:
                r2 = ont.resolve(lab.replace("_", " "))
                if r2["cl_id"]:
                    cid, method = r2["cl_id"], "name_relaxed"
            note = "not covered by the sidecar"
        cl_label = ont.label(cid) if cid else None
        line = ont.trace_line(cid) if cid else None
        # a mapping that points at an id the file does not contain is a defect, not a mapping
        if cid and line is None:
            drift.append({"label": lab, "cl_id": cid, "problem": "id not in ontology file"})
        if cid is None:
            unresolved.append(lab)
        rows.append({"label": lab, "cl_id": cid, "cl_label": cl_label, "method": method,
                     "obo_line": line, "n_libraries": len(rec["libraries"]),
                     "libraries": sorted(rec["libraries"]), "note": note,
                     "sidecar_status": (side_labels.get(lab) or {}).get("status")})
    lm_path = os.path.join(WAVE, "out", "ONT_LABELMAP_V2.tsv")
    with open(lm_path, "w", encoding="utf-8") as f:
        f.write("label\tcl_id\tcl_label\tmapping_method\tobo_line\tn_libraries\tlibraries\t"
                "sidecar_status\tnote\n")
        for r in rows:
            f.write(f"{r['label']}\t{r['cl_id'] or ''}\t{r['cl_label'] or ''}\t{r['method']}\t"
                    f"{r['obo_line'] or ''}\t{r['n_libraries']}\t{','.join(r['libraries'])}\t"
                    f"{r['sidecar_status'] or ''}\t{r['note'] or ''}\n")
    print(f"wrote {lm_path}  ({len(rows)} labels; mapped "
          f"{sum(1 for r in rows if r['cl_id'])}; unresolved {len(unresolved)})")
    if unresolved:
        print(f"  no CL term: {unresolved}")

    out["label_map"] = {
        "n_labels": len(rows),
        "n_mapped": sum(1 for r in rows if r["cl_id"]),
        "n_unresolved": len(unresolved),
        "unresolved": unresolved,
        "n_id_not_in_file": len(drift),
        "id_not_in_file": drift,
        "by_method": dict(collections.Counter(r["method"] for r in rows)),
        "labels_in_libraries_missing_from_sidecar":
            sorted(l for l in labels if l not in side_labels),
    }
    out["files"] = {"closure_tsv": cl_path, "labelmap_tsv": lm_path,
                    "closure_tsv_sha256": sha256(cl_path),
                    "labelmap_tsv_sha256": sha256(lm_path)}
    nav_path = os.path.join(WAVE, "out", "ONT_NAV_v1.json")
    json.dump(out, open(nav_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {nav_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())