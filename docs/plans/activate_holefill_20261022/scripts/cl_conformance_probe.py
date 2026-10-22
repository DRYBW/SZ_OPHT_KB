#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""red-line probe -- every entry name of the library under decision must resolve against the in-repo
Cell Ontology snapshot, with no fabricated term.

Reads the library (I4) and the in-repo release `kb/ontology/cl/releases/2026-06-08/cl-base.obo`,
and for each of the 17 entries compares the entry's declared `cl_id` with the term that carries the
entry's own name. Writes out/CL_CONFORMANCE.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
OUT = os.path.join(WAVE, "out")
OBO = os.path.join(REPO, "kb", "ontology", "cl", "releases", "2026-06-08", "cl-base.obo")


def load_obo(path):
    terms, cur = {}, None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                cur = {}
                continue
            if line.startswith("[") and line.endswith("]"):
                cur = None
                continue
            if cur is None or ":" not in line:
                continue
            k, v = line.split(":", 1)
            v = v.strip()
            if k == "id":
                cur["id"] = v
                terms[v] = cur
            elif k == "name":
                cur["name"] = v
            elif k == "is_obsolete":
                cur["obsolete"] = (v == "true")
    return {k: v for k, v in terms.items() if not v.get("obsolete")}


def main():
    inc = json.load(open(os.path.join(REPO, "kb", "markers",
                                      "markers_v12_holefill_increment.json")))
    terms = load_obo(OBO)
    by_name = {}
    for cid, t in terms.items():
        nm = (t.get("name") or "").strip().casefold()
        if nm:
            by_name.setdefault(nm, cid)
    rows = []
    for e in (inc.get("entries") or []):
        name = str(e.get("class_name") or "")
        cid = e.get("cl_id")
        resolved = by_name.get(name.strip().casefold())
        rows.append({"class_name": name, "declared_cl_id": cid,
                     "term_carrying_that_name": resolved,
                     "declared_matches_the_snapshot": bool(resolved and resolved == cid),
                     "name_present_in_snapshot": resolved is not None})
    entry_names = sorted({r["class_name"] for r in rows})
    marker_names = sorted(inc.get("markers") or {})
    doc = {"probe": "cl_conformance_probe.py",
           "ontology_file": "kb/ontology/cl/releases/2026-06-08/cl-base.obo",
           "ontology_terms": len(terms),
           "library_entries": len(rows), "library_names": len(entry_names),
           "entries": rows,
           "every_entry_name_resolves_to_its_declared_term": all(
               r["declared_matches_the_snapshot"] for r in rows),
           "names_in_markers_not_in_entries": sorted(set(marker_names) - set(entry_names)),
           "fabricated_terms": [r["class_name"] for r in rows if not r["name_present_in_snapshot"]],
           "verdict": ("PASS" if all(r["declared_matches_the_snapshot"] for r in rows) else "FAIL")}
    with open(os.path.join(OUT, "CL_CONFORMANCE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    for r in rows:
        print("%-42s %-12s snapshot=%-12s %s" % (r["class_name"], r["declared_cl_id"],
                                                 r["term_carrying_that_name"],
                                                 "ok" if r["declared_matches_the_snapshot"]
                                                 else "*** MISMATCH"))
    print("entries:", len(rows), "verdict:", doc["verdict"],
          "| fabricated terms:", doc["fabricated_terms"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())