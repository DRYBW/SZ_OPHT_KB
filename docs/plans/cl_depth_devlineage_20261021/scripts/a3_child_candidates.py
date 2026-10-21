#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""a3_child_candidates.py - the decision-ready list of finer terms the ontology offers us.

Where our class is systematically coarser than the literature (verdict `we_are_coarser` in the
four-way table), the ontology tells us exactly which child term the author was using. This
script aggregates those pairs and attaches the support a decision needs:

  * ontology side   the child CL id, its preferred name read from the ontology file, the
                    is_a path from the author's term up to our own, and the file lines
  * data side       how many recorded clusters / cells carry that author term
  * corpus side     whether our own corpus states the child term (preferred name or synonym),
                    with paper ids and locators, from out/CORPUS_TERM_INDEX.tsv

Nothing is adopted here. The list is input for a separate activation decision, and a candidate
with no corpus support is reported as a gap rather than quietly dropped.

Outputs: out/CHILD_TERM_CANDIDATES.tsv, out/CHILD_TERM_CANDIDATES.json
"""
from __future__ import annotations

import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ont_nav import Ontology, WE_COARSER, WE_FINER  # noqa: E402


def load_term_index(path):
    idx = collections.defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            idx[r["term_key"]].append(r)
    return idx


def main() -> int:
    nav = json.load(open(os.path.join(WAVE, "out", "ONT_NAV_v1.json"), encoding="utf-8"))
    ont = Ontology(nav["primary_path"])
    fourway = os.path.join(WAVE, "out", "GRANULARITY_FOURWAY_721.tsv")
    rows = list(csv.DictReader(open(fourway, encoding="utf-8"), delimiter="\t"))
    term_index = load_term_index(os.path.join(WAVE, "out", "CORPUS_TERM_INDEX.tsv"))

    groups = collections.OrderedDict()
    for r in rows:
        if r["verdict"] != WE_COARSER:
            continue
        key = (r["ours_cl"], r["their_cl"])
        g = groups.setdefault(key, {"ours_cl": r["ours_cl"], "ours_cl_label": r["ours_cl_label"],
                                    "our_labels": set(), "child_cl": r["their_cl"],
                                    "child_label": r["their_cl_label"],
                                    "author_labels": set(), "clusters": 0, "cells": 0,
                                    "volumes": collections.Counter(),
                                    "family_inconsistent_clusters": 0,
                                    "path": r["relation_path"]})
        g["our_labels"].add(r["ours_label"])
        g["author_labels"].add(r["their_label"])
        g["clusters"] += 1
        g["cells"] += int(r["n_cells"])
        g["volumes"][r["vol"]] += int(r["n_cells"])
        if "不一致" in r["family_verdict"]:
            g["family_inconsistent_clusters"] += 1

    cam_rows = []
    for (ours_cl, child_cl), g in sorted(groups.items(), key=lambda kv: -kv[1]["cells"]):
        support = term_index.get(child_cl, [])
        best = None
        for s in sorted(support, key=lambda s: (0 if s["match_kind"] == "preferred_name" else 1,
                                                -int(s["n_chunks"]))):
            best = s if best is None else best
            if s["match_kind"] == "preferred_name":
                best = s
                break
        n_chunks = sum(int(s["n_chunks"]) for s in support)
        n_papers = len({p for s in support for p in s["example_paper_ids"].split(",") if p})
        if not support:
            status = "no_corpus_hit"
        elif any(s["match_kind"] == "preferred_name" for s in support):
            status = "corpus_states_the_term"
        else:
            status = "corpus_states_a_synonym_only"
        cam_rows.append({
            "ours_cl": ours_cl, "ours_cl_label": g["ours_cl_label"],
            "our_labels": ",".join(sorted(g["our_labels"])),
            "child_cl": child_cl, "child_cl_label": g["child_label"],
            "is_a_depth": max(len(g["path"].split(" -> ")) - 2, 1),
            "is_a_path": g["path"],
            "clusters": g["clusters"], "cells": g["cells"],
            "clusters_the_family_regex_called_inconsistent": g["family_inconsistent_clusters"],
            "top_volumes": ";".join(f"{v}:{c}" for v, c in g["volumes"].most_common(3)),
            "author_label_examples": ";".join(sorted(g["author_labels"])[:3]),
            "corpus_support_status": status,
            "corpus_n_chunks": n_chunks, "corpus_n_papers": n_papers,
            "corpus_best_phrase": (best or {}).get("query_phrase", ""),
            "corpus_best_phrase_kind": (best or {}).get("match_kind", ""),
            "corpus_locator_examples": (best or {}).get("example_locators", ""),
            "child_obo_line": ont.trace_line(child_cl) or "",
        })

    out_tsv = os.path.join(WAVE, "out", "CHILD_TERM_CANDIDATES.tsv")
    with open(out_tsv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cam_rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(cam_rows)
    print(f"wrote {out_tsv}  ({len(cam_rows)} candidates)")

    finer = collections.Counter()
    finer_cells = collections.Counter()
    for r in rows:
        if r["verdict"] == WE_FINER:
            finer[(r["ours_cl"], r["their_cl"])] += 1
            finer_cells[(r["ours_cl"], r["their_cl"])] += int(r["n_cells"])
    print("\n=== child terms the ontology offers us (we are coarser than the literature) ===")
    print(f"{'our class':<16}{'our CL':<14}{'child CL':<14}{'child term':<34}"
          f"{'depth':>5}{'clusters':>9}{'cells':>9}  corpus")
    for r in cam_rows[:25]:
        print(f"{r['our_labels'][:15]:<16}{r['ours_cl']:<14}{r['child_cl']:<14}"
              f"{r['child_cl_label'][:33]:<34}{r['is_a_depth']:>5}{r['clusters']:>9}"
              f"{r['cells']:>9}  {r['corpus_support_status']} "
              f"({r['corpus_n_chunks']} chunks/{r['corpus_n_papers']} papers)")
    tot_cells = sum(r["cells"] for r in cam_rows)
    with_support = sum(1 for r in cam_rows if r["corpus_support_status"] != "no_corpus_hit")
    print(f"  candidates: {len(cam_rows)}  cells involved: {tot_cells}  "
          f"with corpus support: {with_support}/{len(cam_rows)}")

    print("\n=== the opposite direction (we are finer than the literature) ===")
    for (a, b), n in finer.most_common(10):
        print(f"  {ont.label(a)} ({a}) vs {ont.label(b)} ({b}): "
              f"{n} clusters / {finer_cells[(a, b)]} cells")

    summary = {"generated_by": "scripts/a3_child_candidates.py",
               "ontology": {"path": nav["primary_path"], "release": nav["primary"]["release"]},
               "n_candidates": len(cam_rows),
               "cells_involved": tot_cells,
               "with_corpus_support": with_support,
               "without_corpus_support": len(cam_rows) - with_support,
               "candidates": cam_rows,
               "we_are_finer_pairs": [{"ours_cl": a, "ours_label": ont.label(a),
                                       "their_cl": b, "their_label": ont.label(b),
                                       "clusters": n, "cells": finer_cells[(a, b)]}
                                      for (a, b), n in finer.most_common()],
               "note": "no term is adopted in this card; adoption is a separate decision"}
    sp = os.path.join(WAVE, "out", "CHILD_TERM_CANDIDATES.json")
    json.dump(summary, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {sp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())