#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s7_afterfact_coverage.py - the only file that reads the evaluation recording, after the graph.

The contract forbids deriving a lineage edge from the evaluation volumes' own queries, and allows
exactly one asymmetric use afterwards: reporting coverage. So this runs last, reads the recorded
per-cluster table the repository already produced, and answers two questions:

  * how much of the recorded cell mass sits on a class the scaffold can place on a chain, and how
    much sits on a class whose branch is decapitated;
  * what the recording contains that the scaffold does not know about at all (classes with no CL
    term on our side, and classes we never enumerate).

Nothing computed here is written back into any scaffold artefact: the nodes, edges, register and
pending tables are all built before this file runs, and the gate proves they carry no reference to
the recording.

Outputs: out/AFTERFACT_RECORDING_COVERAGE.tsv, out/AFTERFACT_SUMMARY.json
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402

COLS = ["cl_id_or_no_match", "label", "recorded_clusters", "recorded_cells",
        "on_software_side", "scaffold_status", "decapitated", "pending_repairs", "note"]


def main() -> int:
    rec = C.read_tsv(C.FIRSTPASS_FOURWAY)
    nodes = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    edges = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    register = C.read_tsv(os.path.join(C.OUT, "DECAPITATED_BRANCHES.tsv"))
    pending = C.read_tsv(os.path.join(C.OUT, "PENDING_ASSERTIONS.tsv"))
    edges_full = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES.tsv"))
    key2id = {n["node_key"]: n["node_id"] for n in nodes}
    a1 = {n["node_id"] for n in nodes if n["library_ring"] == "A1"}
    a2 = {n["cl_label"] for n in nodes if n["library_ring"] == "A2"}
    anchored = set()
    for e in edges:
        d = key2id[e["descendant_node"]]
        if d in a1 and (e["relation_type"] == "ancestral_origin"
                        or e["precursor_kind"] == "origin_anchor"):
            anchored.add(d)
    decap = {r["cl_id"] for r in register if r["branch_kind"] == "covered_class_without_origin"}
    pend_by_target = collections.Counter(r["descendant_cl_id"] for r in pending)
    label_of = {n["node_id"]: n["cl_label"] for n in nodes}

    mass = collections.defaultdict(lambda: {"clusters": 0, "cells": 0})
    for r in rec:
        cid = r["ours_cl"] or f"NO_MATCH:{r['ours_label']}"
        mass[cid]["clusters"] += 1
        try:
            mass[cid]["cells"] += int(r["n_cells"])
        except (TypeError, ValueError):
            pass
    tot_clusters = sum(v["clusters"] for v in mass.values())
    tot_cells = sum(v["cells"] for v in mass.values())

    rows = []
    for cid, v in sorted(mass.items(), key=lambda kv: -kv[1]["cells"]):
        if cid.startswith("CL:"):
            status = ("anchored" if cid in anchored else
                      ("decapitated" if cid in decap else "not_a_covered_class"))
            label = label_of.get(cid, "")
            on_side = "yes" if cid in a1 else "no"
        else:
            status = "no_cl_term_on_our_side"
            label = cid.split(":", 1)[1]
            on_side = "yes" if label in a2 else "no"
        rows.append({"cl_id_or_no_match": cid, "label": label,
                     "recorded_clusters": v["clusters"], "recorded_cells": v["cells"],
                     "on_software_side": on_side, "scaffold_status": status,
                     "decapitated": "yes" if cid in decap else "no",
                     "pending_repairs": pend_by_target.get(cid, 0),
                     "note": ""})
    C.write_tsv(os.path.join(C.OUT, "AFTERFACT_RECORDING_COVERAGE.tsv"), rows, COLS)

    def share(sel):
        c = sum(r["recorded_cells"] for r in rows if sel(r))
        return {"clusters": sum(r["recorded_clusters"] for r in rows if sel(r)), "cells": c,
                "pct_cells": round(100.0 * c / tot_cells, 2) if tot_cells else 0.0}

    summ = {
        "generated_by": "scripts/s7_afterfact_coverage.py",
        "read_after_the_graph_was_frozen": True,
        "recording": {"clusters": tot_clusters, "cells": tot_cells},
        "cells_on_a_class_that_is_anchored": share(lambda r: r["scaffold_status"] == "anchored"),
        "cells_on_a_class_that_is_decapitated": share(lambda r: r["decapitated"] == "yes"),
        "cells_on_a_class_we_never_enumerate": share(lambda r: r["on_software_side"] == "no"),
        "cells_on_a_class_with_no_cl_term_on_our_side":
            share(lambda r: r["scaffold_status"] == "no_cl_term_on_our_side"),
        "classes_in_the_recording": len(rows),
        "decapitated_classes_with_a_pending_repair":
            sum(1 for r in rows if r["decapitated"] == "yes" and r["pending_repairs"]),
        "full_edge_set_rows": len(edges_full),
        "note": ("this file is the only reader of the evaluation recording in this card; the "
                 "scaffold artefacts are frozen before it runs and the gate checks that none of "
                 "them references the recording"),
    }
    C.write_json(os.path.join(C.OUT, "AFTERFACT_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())