#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s4_decapitated_branches.py - the decapitated-branch register.

Where a chain exists, the graph carries it. This file is the other half of the honest answer: every
branch where no local source supplies a chain, named with its class identifiers, the cell mass
involved where our own baselines record it, the exact point where the chain stops, and the kind of
evidence that would repair it.

Populations, all recomputed from the delivered artefact files:
  covered_class_without_origin     52 covered classes - 8 that an anchor reaches = 44
  anchor_without_any_covered_class the coarsest level: an anchor no covered class reaches
  in_house_concept_without_term    the library concepts the ontology cannot name at all
  axis_rollup                      the retinal progenitor axis, summarised in one row

Outputs: out/DECAPITATED_BRANCHES.tsv, out/DECAPITATED_SUMMARY.json
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402
from ont_nav import Ontology  # noqa: E402

COLS = ["branch_id", "branch_kind", "cl_id", "cl_label", "our_labels", "ontology_status",
        "ontology_line", "stage", "evidence_tier", "break_kind", "chain_top_term",
        "chain_top_label", "chain_top_line", "cell_mass", "cell_mass_basis", "rpc_axis",
        "evidence_required", "repair_route", "notes"]


def main() -> int:
    ont = Ontology(C.ONT_OBO)
    nav = json.load(open(C.ONT_NAV, encoding="utf-8"))
    anchors = {a["cl_id"]: a["key"] for a in nav["germ_layer_anchors"] if a["cl_id"]}
    nodes = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    edges = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    lab = C.load_label_map()
    peer_germ = C.read_tsv(C.FIRSTPASS_GERM)
    peer_tier = collections.defaultdict(set)
    for r in peer_germ:
        peer_tier[r["cl_id"]].add(r["tier"])
    peer_unresolved = {r["cl_id"] for r in C.read_tsv(C.FIRSTPASS_UNRESOLVED)}
    rpc_rows = {r["cl_id"]: r["rpc_axis"] for r in C.read_tsv(os.path.join(C.OUT, "RPC_AXIS.tsv"))}
    d1 = {r["cl_id"]: r for r in C.read_tsv(C.D1_TABLE)}

    key2id = {n["node_key"]: n["node_id"] for n in nodes}
    a1 = [n for n in nodes if n["library_ring"] == "A1"]
    a1set = {n["node_id"] for n in a1}

    anchored = set()
    for e in edges:
        d = key2id[e["descendant_node"]]
        if d in a1set and (e["relation_type"] == "ancestral_origin"
                           or e["precursor_kind"] == "origin_anchor"):
            anchored.add(d)

    def closure_info(cid):
        """(top term, steps, path) of this class's develops_from closure, or None."""
        out, frontier = {}, [(p, 1, [cid, p]) for p, _ln in ont.terms[cid].dev_lines]
        while frontier:
            p, d, path = frontier.pop()
            if p in out and out[p][0] <= d:
                continue
            out[p] = (d, path)
            for q, _ln in ont.terms[p].dev_lines if p in ont.terms else []:
                frontier.append((q, d + 1, path + [q]))
        if not out:
            return None
        top = sorted(out.items(), key=lambda kv: (-kv[1][0], kv[0]))[0][0]
        return top, out[top][0], out[top][1]

    EV_NO_STEP = ("a developmental claim in a source we can anchor locally (a paper we hold, or a "
                  "textbook page) that names this class and its precursor, admitted through the "
                  "pending-assertion route; an upstream ontology statement would also repair it but "
                  "is not ours to write. A corpus co-occurrence is not sufficient.")
    EV_STOPS = ("the chain exists but stops before a germ layer: the term it stops at must be "
                "linked to an anchor (an ontology statement) or an anchored source must connect "
                "the class upward; admitting the local claim alone proves a step, not an origin.")
    EV_ANCHOR = ("any covered class reaching this anchor. Needs the covered classes that belong to "
                 "this branch to carry an admitted chain, or the anchor itself to be linked by an "
                 "ontology statement; the corpus rows we hold only co-mention it.")
    EV_NOTERM = ("an ontology term for the concept (the granularity work already lists candidate "
                 "child terms), or an in-house lineage assertion with a local anchor. Until one of "
                 "the two exists the concept cannot sit on an ontology-backed chain.")

    rows = []
    n = 0
    for node in sorted(a1, key=lambda x: x["node_id"]):
        cid = node["node_id"]
        if cid in anchored:
            continue
        n += 1
        info = closure_info(cid)
        tier = ("corpus_cooccurrence_only" if "corpus_cooccurrence_weak" in peer_tier.get(cid, ())
                else ("no_local_evidence" if cid in peer_unresolved else "unclassified"))
        if info is None:
            break_kind, top, top_d, top_path = "no_develops_from_statement_at_all", "", "", ""
            ev = EV_NO_STEP
        else:
            top, top_d, top_path = info
            break_kind = "closure_does_not_reach_any_origin_anchor"
            ev = EV_STOPS
        rows.append({
            "branch_id": "", "branch_kind": "covered_class_without_origin", "cl_id": cid,
            "cl_label": node["cl_label"], "our_labels": node["our_labels"],
            "ontology_status": "mapped", "ontology_line": node["obo_line"], "stage": node["stage"],
            "evidence_tier": tier, "break_kind": break_kind,
            "chain_top_term": top, "chain_top_label": ont.label(top) if top else "",
            "chain_top_line": ont.trace_line(top) if top else "",
            "cell_mass": node["cell_mass_share_pct"] or "unknown",
            "cell_mass_basis": node["cell_mass_basis"],
            "rpc_axis": rpc_rows.get(cid, ""),
            "evidence_required": ev,
            "repair_route": ("pending_assertion_if_an_anchored_source_asserts_it; otherwise "
                             "requires_an_upstream_ontology_statement"),
            "notes": (f"peer tier: {'/'.join(sorted(peer_tier.get(cid, {'unresolved'})))}; "
                      f"chain top: {ont.label(top) if top else 'none'}"
                      f"{' (' + str(top_d) + ' step(s))' if top else ''}"
                      + (f"; D1 chain_break_at={d1[cid]['chain_break_at'].split(':')[-1]}"
                         if cid in d1 else ""))})
    # anchors nothing reaches
    reach = collections.Counter()
    for e in edges:
        prec = e["precursor_node"].split("|")[0][3:]
        if prec in anchors:
            reach[prec] += 1
    for aid, akey in sorted(anchors.items()):
        if reach.get(aid):
            continue
        n += 1
        rows.append({
            "branch_id": "", "branch_kind": "anchor_without_any_covered_class", "cl_id": aid,
            "cl_label": ont.label(aid), "our_labels": "", "ontology_status": "mapped",
            "ontology_line": ont.trace_line(aid), "stage": "developing",
            "evidence_tier": "n/a_anchor", "break_kind": "no_covered_class_reaches_this_anchor",
            "chain_top_term": "", "chain_top_label": "", "chain_top_line": "",
            "cell_mass": "unknown", "cell_mass_basis": "anchor_concept", "rpc_axis": "",
            "evidence_required": EV_ANCHOR,
            "repair_route": "requires_a_chain_from_a_covered_class_or_an_upstream_ontology_statement",
            "notes": ("the anchor itself is in the node set with its ontology line; what is missing "
                      "is any covered class connected to it")})
    # in-house concepts the ontology cannot name
    for node in sorted((x for x in nodes if x["library_ring"] == "A2"), key=lambda x: x["node_id"]):
        n += 1
        rows.append({
            "branch_id": "", "branch_kind": "in_house_concept_without_ontology_term",
            "cl_id": "", "cl_label": node["cl_label"], "our_labels": node["our_labels"],
            "ontology_status": "no_match", "ontology_line": "", "stage": node["stage"],
            "evidence_tier": "n/a_no_ontology_term",
            "break_kind": "concept_has_no_ontology_counterpart_at_all",
            "chain_top_term": "", "chain_top_label": "", "chain_top_line": "",
            "cell_mass": node["cell_mass_share_pct"] or "unknown",
            "cell_mass_basis": node["cell_mass_basis"],
            "rpc_axis": "", "evidence_required": EV_NOTERM,
            "repair_route": "adopt_a_term_or_record_an_in_house_assertion_with_a_local_anchor",
            "notes": (node["stage_note"] or "")})
    # retinal progenitor axis roll-up
    n += 1
    retinal = [r for r in C.read_tsv(os.path.join(C.OUT, "RPC_AXIS.tsv"))]
    off = [r["cl_label"] for r in retinal if r["rpc_axis"] == "does_not_reach_the_rpc"]
    rows.append({
        "branch_id": "", "branch_kind": "axis_rollup", "cl_id": "CL:0002672",
        "cl_label": "retinal progenitor cell axis", "our_labels": "",
        "ontology_status": "mapped", "ontology_line": ont.trace_line("CL:0002672"),
        "stage": "developing", "evidence_tier": "rollup",
        "break_kind": "axis_carries_photoreceptors_only",
        "chain_top_term": "", "chain_top_label": "", "chain_top_line": "",
        "cell_mass": "unknown", "cell_mass_basis": "rollup_row", "rpc_axis": "",
        "evidence_required": ("for each retinal class off the axis: an anchored source naming its "
                              "precursor (the ontology says nothing at all for them)"),
        "repair_route": "pending_assertions_per_class",
        "notes": (f"{sum(1 for r in retinal if r['rpc_axis'] == 'reaches_the_rpc')} of "
                  f"{len(retinal)} covered classes reach the retinal progenitor cell; "
                  f"{len(off)} do not: " + ", ".join(off[:12]) + ("..." if len(off) > 12 else ""))})
    for i, r in enumerate(rows, 1):
        r["branch_id"] = f"BR{i:03d}"
    C.write_tsv(os.path.join(C.OUT, "DECAPITATED_BRANCHES.tsv"), rows, COLS)
    summ = {"generated_by": "scripts/s4_decapitated_branches.py",
            "rows": len(rows),
            "by_branch_kind": C.counts(r["branch_kind"] for r in rows),
            "by_break_kind": C.counts(r["break_kind"] for r in rows),
            "by_evidence_tier": C.counts(r["evidence_tier"] for r in rows),
            "covered_classes_without_origin": len(anchored) and
                sum(1 for r in rows if r["branch_kind"] == "covered_class_without_origin"),
            "with_cell_mass_known": sum(1 for r in rows if r["cell_mass"] != "unknown"),
            "outputs": {"register": os.path.join(C.OUT, "DECAPITATED_BRANCHES.tsv")}}
    C.write_json(os.path.join(C.OUT, "DECAPITATED_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())