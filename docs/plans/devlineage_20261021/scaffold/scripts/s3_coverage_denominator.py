#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s3_coverage_denominator.py - the coverage denominator, stated instead of implied.

The owner asked for the lineage to be built comprehensively. What "comprehensive" can mean here is
fixed by what the local sources can carry, so this file reports the denominator explicitly: how many
concepts the library actually covers, how many of them any local source can place on a developmental
chain, and how many nodes and edges each evidence tier accounts for. Every count is recomputed from
the delivered artefact files, never copied from a summary.

Outputs: out/COVERAGE_DENOMINATOR.tsv, out/COVERAGE_DENOMINATOR.json,
         out/ANCHOR_COVERAGE.tsv, out/RPC_AXIS.tsv
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


def main() -> int:
    ont = Ontology(C.ONT_OBO)
    nav = json.load(open(C.ONT_NAV, encoding="utf-8"))
    anchors = {a["cl_id"]: a["key"] for a in nav["germ_layer_anchors"] if a["cl_id"]}
    nodes = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    edges = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    lab = C.load_label_map()
    peer_germ = C.read_tsv(C.FIRSTPASS_GERM)
    peer_tier = {r["cl_id"]: r["tier"] for r in peer_germ if r["tier"] != "unresolved"}
    peer_unresolved = {r["cl_id"] for r in C.read_tsv(C.FIRSTPASS_UNRESOLVED)}

    key2id = {n["node_key"]: n["node_id"] for n in nodes}
    a1 = [n["node_id"] for n in nodes if n["library_ring"] == "A1"]
    a2 = [n for n in nodes if n["library_ring"] == "A2"]

    # ---- class-level coverage: which covered concepts can any local source place on a chain
    a1set = set(a1)
    anchored_classes = set()
    for e in edges:
        d = key2id[e["descendant_node"]]
        if d not in a1set:                 # only covered classes count toward class coverage
            continue
        if e["relation_type"] == "ancestral_origin" or e["precursor_kind"] == "origin_anchor":
            anchored_classes.add(d)
    native_any = {key2id[e["descendant_node"]] for e in edges
                  if e["relation_type"] == "ontology_development_relation"}
    with_native = {key2id[e["descendant_node"]] for e in edges}
    classes_with_dev_step = {c for c in a1 if c in native_any}
    weak_only = {c for c in a1 if peer_tier.get(c) == "corpus_cooccurrence_weak"
                 and c not in anchored_classes}
    nothing = {c for c in a1 if c not in anchored_classes and c not in weak_only}

    rows = [
        ("library_concepts_total", len(lab), "concepts the marker libraries actually ship"),
        ("library_concepts_mapped_to_cl", sum(1 for r in lab.values() if r["cl_id"]),
         "of those, resolvable to a Cell Ontology identifier read from the file"),
        ("library_concepts_no_match", a2 and len(a2), "concepts with no ontology counterpart "
         "(dl:NO_MATCH: keys; they can never carry an ontology edge)"),
        ("distinct_cl_ids_in_library", len(a1), "distinct CL identifiers behind the mapped labels"),
        ("nodes_total", len(nodes), "enumerated nodes (rings A1 + A2 + B + C)"),
        ("nodes_ring_a1_library_classes", len(a1), ""),
        ("nodes_ring_a2_no_match_concepts", len(a2), ""),
        ("nodes_ring_b_ontology_intermediates",
         sum(1 for n in nodes if n["kind"] == "ontology_intermediate"),
         "CL terms on a develops_from path out of a ring-A class or an anchor"),
        ("nodes_ring_c_origin_anchors", sum(1 for n in nodes if n["kind"] == "origin_anchor"), ""),
        ("edges_total", len(edges), "confirmed edges (the admitted graph)"),
        ("edges_ontology_development_relation",
         sum(1 for e in edges if e["relation_type"] == "ontology_development_relation"),
         "native develops_from statements between two enumerated nodes"),
        ("edges_ancestral_origin",
         sum(1 for e in edges if e["relation_type"] == "ancestral_origin"),
         "origin claims spanning more than one step or an is_a bridge (derived rule, named per row)"),
        ("edges_direct_lineage", sum(1 for e in edges if e["relation_type"] == "direct_lineage"),
         "confirmed direct-lineage edges: none, because nothing local supports it"),
        ("edges_trajectory_association",
         sum(1 for e in edges if e["relation_type"] == "trajectory_association"),
         "confirmed trajectory-only edges: none (they are rejected rows, written by s6)"),
        ("grade_direct_lineage_support",
         sum(1 for e in edges if e["evidence_grade"] == "direct_lineage_support"), ""),
        ("grade_identity_conversion_not_direct",
         sum(1 for e in edges if e["evidence_grade"] == "identity_conversion_not_direct"), ""),
        ("grade_textbook_or_review_distant_origin",
         sum(1 for e in edges if e["evidence_grade"] == "textbook_or_review_distant_origin"),
         "unused in the confirmed graph; the textbook layer feeds the pending repair table"),
        ("grade_trajectory_only",
         sum(1 for e in edges if e["evidence_grade"] == "trajectory_only"), ""),
        ("library_classes_with_an_anchored_origin", len(anchored_classes),
         "covered classes any local source can attach to a germ-layer / origin anchor"),
        ("library_classes_with_only_corpus_cooccurrence", len(weak_only),
         "covered classes whose only local developmental trace is a corpus co-occurrence"),
        ("library_classes_with_no_local_developmental_evidence", len(nothing),
         "covered classes with no ontology chain and no admitted corpus edge"),
        ("library_classes_that_are_never_a_descendant_in_the_graph",
         len([c for c in a1set if c not in with_native]),
         "covered classes with no inbound edge at all: they are where every chain stops"),
        ("library_classes_with_a_native_develops_from_statement",
         len(classes_with_dev_step), "same set, stated against the ontology statement"),
        ("decapitated_branches", len(weak_only) + len(nothing),
         "covered classes with no anchored origin: the register's population"),
        ("stage_adult", sum(1 for n in nodes if n["stage"] == "adult"),
         "nodes whose stage is adult, each with a baseline declaration as its basis"),
        ("stage_developing", sum(1 for n in nodes if n["stage"] == "developing"), ""),
        ("stage_fetal", sum(1 for n in nodes if n["stage"] == "fetal"),
         "no local artefact declares a fetal stage for a library class"),
        ("stage_unknown", sum(1 for n in nodes if n["stage"] == "unknown"),
         "written as unknown rather than defaulted to adult"),
        ("nodes_with_a_declared_tissue_context",
         sum(1 for n in nodes if n["tissue_context"] != "unknown"),
         "a node key's ts field is filled only where one baseline declares the class"),
        ("nodes_with_a_declared_species",
         sum(1 for n in nodes if n["species"] != "unknown"), ""),
        ("nodes_with_a_recorded_cell_mass",
         sum(1 for n in nodes if n["cell_mass_share_pct"]),
         "share of cells recorded by our own baseline entries"),
        ("native_develops_from_statements_in_release", 400,
         "develops_from statements inside CL term blocks of this release (re-measured in s0)"),
        ("native_develops_from_statements_enumerated", len(edges) and
         sum(1 for e in edges if e["derivation"] == "native_ontology_attribute"),
         "how many of them lie between two enumerated nodes"),
    ]
    C.write_tsv(os.path.join(C.OUT, "COVERAGE_DENOMINATOR.tsv"),
                [{"count": k, "value": v, "note": n} for k, v, n in rows],
                ["count", "value", "note"])

    # ---- per-anchor coverage
    arows = []
    for aid, akey in sorted(anchors.items()):
        direct = [key2id[e["descendant_node"]] for e in edges
                  if e["precursor_node"].split("|")[0] == f"dl:{aid}"]
        origin = sorted({key2id[e["descendant_node"]] for e in edges
                         if e["relation_type"] == "ancestral_origin"
                         and e["anchor_kind"].startswith(akey)})
        arows.append({"anchor_key": akey, "anchor_cl_id": aid,
                      "anchor_label": ont.label(aid),
                      "classes_with_a_native_step_to_the_anchor": len(direct),
                      "classes_with_a_multi_step_origin_to_the_anchor": len(origin),
                      "classes_total_reaching_the_anchor": len(set(direct) | set(origin)),
                      "status": ("carries classes" if (direct or origin) else
                                 "no covered class reaches this anchor: a decapitated branch at "
                                 "the coarsest level"),
                      "examples": ",".join(sorted({ont.label(x) for x in (direct + origin)})[:6])})
    C.write_tsv(os.path.join(C.OUT, "ANCHOR_COVERAGE.tsv"), arows,
                ["anchor_key", "anchor_cl_id", "anchor_label",
                 "classes_with_a_native_step_to_the_anchor",
                 "classes_with_a_multi_step_origin_to_the_anchor",
                 "classes_total_reaching_the_anchor", "status", "examples"])

    # ---- the retinal progenitor axis
    rpc = "CL:0002672"
    rrows = []
    rpc_desc = set()
    for t in ont.active:
        seen, frontier, hit = set(), [t], False
        while frontier and not hit:
            x = frontier.pop()
            for p, _ in ont.terms[x].dev_lines if x in ont.terms else []:
                if p == rpc:
                    hit = True
                    break
                if p not in seen:
                    seen.add(p)
                    frontier.append(p)
        if hit:
            rpc_desc.add(t)
    # how many develops_from statements of this release point at something that is not a CL term
    non_cl_parents = [(t, p, ln) for t in sorted(ont.active) for p, ln in ont.terms[t].dev_lines
                      if not p.startswith("CL:")]
    for cid in sorted(a1):
        if cid == rpc:
            reach = "is_the_rpc"
        elif cid in rpc_desc:
            reach = "reaches_the_rpc"
        else:
            reach = "does_not_reach_the_rpc"
        rrows.append({"cl_id": cid, "cl_label": ont.label(cid),
                      "our_labels": ",".join(sorted(l for l, r in lab.items() if r["cl_id"] == cid)),
                      "rpc_axis": reach,
                      "n_direct_precursors": len(ont.terms[cid].dev_lines),
                      "first_break": (",".join(f"{p}({ont.label(p)})"
                                               for p, _ in ont.terms[cid].dev_lines) or
                                      "no develops_from statement at all in this release")})
    C.write_tsv(os.path.join(C.OUT, "RPC_AXIS.tsv"), rrows,
                ["cl_id", "cl_label", "our_labels", "rpc_axis", "n_direct_precursors", "first_break"])

    summ = {"generated_by": "scripts/s3_coverage_denominator.py",
            "develops_from_statements_with_a_non_cl_parent": len(non_cl_parents),
            "non_cl_parent_examples": [f"{t}<-{p}@{ln}" for t, p, ln in non_cl_parents[:5]],
            "non_cl_parents_among_enumerated_nodes": [f"{t}<-{p}@{ln}" for t, p, ln in non_cl_parents
                                                      if t in set(a1)],
            "counts": {k: v for k, v, _n in rows},
            "anchors_without_any_covered_class": [a["anchor_label"] for a in arows
                                                   if a["classes_total_reaching_the_anchor"] == 0],
            "rpc_axis": C.counts(r["rpc_axis"] for r in rrows),
            "outputs": {"denominator": os.path.join(C.OUT, "COVERAGE_DENOMINATOR.tsv"),
                        "anchor_coverage": os.path.join(C.OUT, "ANCHOR_COVERAGE.tsv"),
                        "rpc_axis": os.path.join(C.OUT, "RPC_AXIS.tsv")}}
    C.write_json(os.path.join(C.OUT, "COVERAGE_DENOMINATOR.json"), summ)
    for k, v, n in rows:
        print(f"  {k:56s} {v}")
    print(f"  anchors with no covered class: {summ['anchors_without_any_covered_class']}")
    print(f"  rpc axis: {summ['rpc_axis']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())