#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""c1_benchmark_gapcheck.py - the asymmetric, after-the-fact gap check (Task B companion).

This file is NOT an input to the lineage. The lineage was built from the ontology, our marker
library and the corpus; only afterwards is it read against the recorded 721-cluster table, which
is the direction the brief allows ("the benchmark may only be used afterwards, asymmetrically, to
look for gaps"). Nothing here feeds back into LINEAGE_*.tsv, and gate B6 re-checks that those
files carry no reference to the evaluation side.

Two readings:
  * coverage   for every class node of the lineage, does the recorded table contain clusters our
               current library answered with that class? (a class with zero clusters is a class
               nobody is using yet)
  * gaps       for every class the recorded table did use, is it a node of the lineage? (a class
               in use but absent from the lineage is a missing origin, not a missing label)

Output: out/GAPCHECK_LINEAGE_vs_BENCHMARK.tsv
"""
from __future__ import annotations

import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)


def main() -> int:
    nodes = list(csv.DictReader(open(os.path.join(WAVE, "out", "LINEAGE_NODES.tsv"),
                                     encoding="utf-8"), delimiter="\t"))
    fw = list(csv.DictReader(open(os.path.join(WAVE, "out", "GRANULARITY_FOURWAY_721.tsv"),
                                  encoding="utf-8"), delimiter="\t"))
    lab2cl = {r["label"]: (r["cl_id"] or "")
              for r in csv.DictReader(open(os.path.join(WAVE, "out", "ONT_LABELMAP_V2.tsv"),
                                           encoding="utf-8"), delimiter="\t")}

    used = collections.defaultdict(lambda: {"clusters": 0, "cells": 0})
    for r in fw:
        lab = r["ours_label"] or ""
        cid = lab2cl.get(lab, "")
        rec = used[cid or ("unmapped:" + lab)]
        rec["clusters"] += 1
        rec["cells"] += int(r["n_cells"])

    rows = []
    node_cls = {n["cl_id"] for n in nodes if n["kind"] == "library_class"}
    for n in sorted(nodes, key=lambda x: x["cl_id"]):
        if n["kind"] != "library_class":
            continue
        u = used.get(n["cl_id"], {"clusters": 0, "cells": 0})
        rows.append({"side": "lineage_node", "cl_id": n["cl_id"], "cl_label": n["cl_label"],
                     "our_labels": n["our_labels"], "stage_scope": n["stage_scope"],
                     "recorded_clusters": u["clusters"], "recorded_cells": u["cells"],
                     "note": "class the library ships; clusters recorded against it"
                             if u["clusters"] else "shipped but never the top candidate in the "
                                                   "recorded table"})
    for cid, u in sorted(used.items()):
        if cid in node_cls:
            continue
        rows.append({"side": "recorded_class", "cl_id": cid.replace("unmapped:", ""),
                     "cl_label": cid if cid.startswith("unmapped:") else "",
                     "our_labels": cid.replace("unmapped:", ""), "stage_scope": "",
                     "recorded_clusters": u["clusters"], "recorded_cells": u["cells"],
                     "note": "used by the recorded table but not a lineage node "
                             "(no CL term, or not in the library label map)"})
    out = os.path.join(WAVE, "out", "GAPCHECK_LINEAGE_vs_BENCHMARK.tsv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    n_unused = sum(1 for r in rows if r["side"] == "lineage_node" and r["recorded_clusters"] == 0)
    n_extra = sum(1 for r in rows if r["side"] == "recorded_class")
    print(f"wrote {out}  ({len(rows)} rows)")
    print(f"  lineage library-class nodes: {len(node_cls)}; of them never a top candidate: {n_unused}")
    print(f"  classes used in the recorded table but not lineage nodes: {n_extra}")
    for r in sorted([r for r in rows if r['side'] == 'recorded_class'],
                    key=lambda r: -r["recorded_clusters"])[:10]:
        print(f"    {r['our_labels'] or r['cl_id']:<32}{r['recorded_clusters']:>4} clusters "
              f"{r['recorded_cells']:>8} cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())