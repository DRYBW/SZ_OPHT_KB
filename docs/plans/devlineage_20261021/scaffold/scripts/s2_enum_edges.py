#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s2_enum_edges.py - the enumerated edge set, typed with the contract's four relation types.

Two families enter the confirmed graph, and nothing else does:

  ontology_development_relation  a statement the local ontology itself declares (`develops_from`,
                                 RO:0002202). Its own semantics are kept in `source_relation` /
                                 `source_relation_direction`, so a `develops_from` line and a
                                 forward differentiation arrow can never be confused.
  ancestral_origin               an origin claim that spans more than one step, or that needs the
                                 ontology's own `is_a` bridge to reach a germ-layer anchor. Every
                                 such row names its rule (`derivation_rule`) because it is a derived
                                 rule, not a native ontology attribute.

Rule R-ANCHOR, stated once and applied mechanically. For a library class C, let closure(C) be every
term reachable from C by at least one `develops_from` step. An anchor A is an origin of C when:

  R-ANCHOR-1  A is itself in closure(C)                         -> a pure chain of k steps
  R-ANCHOR-2  some T in closure(C) has A among its direct       -> k steps + one is_a hop
              `is_a` statements
  R-ANCHOR-3  some T in closure(C) has A among its transitive   -> k steps + m is_a hops, the
              `is_a` ancestors (the closure the ontology card      bridge path cited hop by hop
              already computes and audits at gate A3)

A class with no `develops_from` step at all gets no origin edge: `is_a` alone is a taxonomic
statement, not a developmental one, and using it as one would be exactly the common-sense arrow this
card forbids. Equal-cost candidates are resolved by fewest steps, then by rule order, so the output
is deterministic.

Grades. Every confirmed edge is graded `identity_conversion_not_direct`: the source states the time
direction and the identity conversion, and it is not direct-lineage proof. `direct_lineage_support`
is claimed by nothing in this graph - no local artefact gives direct lineage evidence - and what
would be needed to claim it is in the repair register, not here. The alternative reading (a native
one-step `develops_from` as `direct_lineage_support`) is available to any reader from the
`directness` column, so the conservative choice hides nothing. The other two grades are used by the
not-admitted rows and the pending repair table written by s6.

Outputs: out/SCAFFOLD_EDGES_CONFIRMED.tsv, out/FIRSTPASS_RECONCILIATION.tsv, out/EDGES_SUMMARY.json
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402
from ont_nav import Ontology, DEVELOPS_FROM  # noqa: E402

EDGE_COLS = [
    "edge_id", "edge_key", "precursor_node", "descendant_node", "relation_type", "directness",
    "evidence_ids", "evidence_grade", "conflict_status", "marker_change_ids",
    "derivation", "derivation_rule", "derivation_note", "chain_precursor_to_descendant", "steps",
    "obo_lines", "source_relation", "source_relation_direction", "grade_basis",
    "admission", "admission_rule", "precursor_label", "descendant_label",
    "precursor_kind", "descendant_kind", "anchor_kind", "first_pass_edge_ids", "notes",
]


def main() -> int:
    ont = Ontology(C.ONT_OBO)
    nav = json.load(open(C.ONT_NAV, encoding="utf-8"))
    anchors = {a["cl_id"]: a["key"] for a in nav["germ_layer_anchors"] if a["cl_id"]}
    nodes = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    key_of = {n["node_id"]: n["node_key"] for n in nodes}
    kind_of = {n["node_id"]: n["kind"] for n in nodes}
    label_of = {n["node_id"]: n["cl_label"] for n in nodes}
    materialized = {n["node_id"] for n in nodes if n["cl_id"]}
    a1 = [n["node_id"] for n in nodes if n["library_ring"] == "A1"]

    # ---------------------------------------------------------------- family 1: native statements
    edges, dangling = [], []
    for d in sorted(materialized):
        for p, ln in ont.terms[d].dev_lines:
            if p not in materialized:
                dangling.append(f"{d}<-{p}@{ln}")
                continue
            edges.append(_row(p, d, "ontology_development_relation", "direct",
                              f"obo:{ln}", [ln], "native_ontology_attribute", "R-NATIVE",
                              "the ontology itself declares this single develops_from step",
                              [p, d], 1, kind_of, label_of, key_of))
    print(f"native develops_from steps among the enumerated nodes: {len(edges)} "
          f"(dangling endpoints outside the node set: {len(dangling)} {dangling[:3]})")

    # ---------------------------------------------------------------- family 2: derived origins
    derived, rule_counts = [], collections.Counter()
    ring_a_with_closure = []
    for cid in sorted(a1):
        chain = _dev_closure(ont, cid)
        if chain:
            ring_a_with_closure.append(cid)
        for aid, akey in sorted(anchors.items()):
            cands = []
            if aid in chain:
                steps, path, lines = chain[aid]
                if steps == 1:
                    continue                      # already a native edge; not a second row
                cands.append(("R-ANCHOR-1", f"chain:{steps}_steps", steps, path, lines,
                              f"pure develops_from chain of {steps} steps to the anchor "
                              f"({akey}); more than one step, so it must not pose as a single step",
                              [cid] + path[1:]))
            else:
                for tid, (steps, path, lines) in sorted(chain.items()):
                    bridge = [ln for t, ln in ont.terms[tid].is_a_lines if t == aid]
                    if bridge:
                        cands.append(("R-ANCHOR-2", f"chain:{steps}_steps_with_is_a_bridge", steps,
                                      path, lines + bridge,
                                      f"{steps} develops_from step(s), then the ontology's own is_a "
                                      f"hop {label_of.get(tid, ont.label(tid))} is_a "
                                      f"{ont.label(aid)}",
                                      [cid] + path[1:] + [aid]))
                for tid, (steps, path, lines) in sorted(chain.items()):
                    if aid in ont.ancestors_cl(tid):
                        ipath = ont._path(tid, aid)
                        hop_lines, ok = [], True
                        for u, v in zip(ipath, ipath[1:]):
                            lns = [ln for t, ln in ont.terms[u].is_a_lines if t == v]
                            if not lns:
                                ok = False
                                break
                            hop_lines += lns
                        if ok and len(ipath) > 1:
                            cands.append(("R-ANCHOR-3",
                                          f"chain:{steps}_steps_with_is_a_path:{len(ipath) - 1}_hops",
                                          steps, path, lines + hop_lines,
                                          f"{steps} develops_from step(s), then the ontology's own "
                                          f"is_a closure: " + " is_a ".join(
                                              ont.label(x) or x for x in ipath),
                                          [cid] + path[1:] + ipath[1:]))
            if not cands:
                continue
            rule, directness, steps, path, lines, note, chainv = sorted(
                cands, key=lambda x: (len(x[6]), x[0]))[0]
            # every row's chain is written precursor-first, the same direction as its edge key
            chainv = list(reversed(chainv))
            rule_counts[rule] += 1
            derived.append(_row(aid, cid, "ancestral_origin", directness,
                                "obo:" + "+".join(str(x) for x in lines), lines,
                                "derived_rule", rule, note, chainv, steps,
                                kind_of, label_of, key_of,
                                anchor_kind=f"{akey}|{rule}"))
    print(f"derived origin edges: {len(derived)} {dict(rule_counts)};  ring-A classes with a "
          f"develops_from closure: {len(ring_a_with_closure)} of {len(a1)}")

    # ---------------------------------------------------------------- assemble, id, dedupe
    seen, allrows = set(), []
    for r in edges + derived:
        k = (r["precursor_node"], r["descendant_node"])
        if k in seen:
            continue
        seen.add(k)
        allrows.append(r)
    allrows.sort(key=lambda r: (r["descendant_node"], r["precursor_node"], r["relation_type"]))
    for i, r in enumerate(allrows, 1):
        r["edge_id"] = f"S{i:04d}"
    C.write_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"), allrows, EDGE_COLS)

    # ---------------------------------------------------------------- reconciliation with the peer
    rec = reconcile(C.read_tsv(C.FIRSTPASS_EDGES), allrows)
    C.write_tsv(os.path.join(C.OUT, "FIRSTPASS_RECONCILIATION.tsv"), rec,
                ["first_pass_edge_id", "first_pass_pair", "first_pass_relation_type",
                 "first_pass_evidence", "outcome", "scaffold_edge_id", "scaffold_relation_type",
                 "why"])

    desc_with_origin = {r["descendant_node"] for r in allrows}
    anchored_desc = {r["descendant_node"] for r in allrows if r["relation_type"] == "ancestral_origin"
                     or kind_of.get([k for k, v in key_of.items() if v == r["precursor_node"]][0])
                     == "origin_anchor"}
    by_anchor = collections.Counter((r["anchor_kind"] or "none").split("|")[0]
                                    for r in allrows if r["anchor_kind"])
    summ = {
        "generated_by": "scripts/s2_enum_edges.py",
        "confirmed_edges": len(allrows),
        "by_relation_type": C.counts(r["relation_type"] for r in allrows),
        "by_evidence_grade": C.counts(r["evidence_grade"] for r in allrows),
        "by_directness": C.counts(r["directness"] for r in allrows),
        "by_derivation": C.counts(r["derivation"] for r in allrows),
        "by_derivation_rule": C.counts(r["derivation_rule"] for r in allrows),
        "by_admission": C.counts(r["admission"] for r in allrows),
        "edges_by_anchor": dict(by_anchor),
        "native_dangling_endpoints": len(dangling),
        "dangling_detail": dangling,
        "ring_a_classes": len(a1),
        "ring_a_classes_with_a_develops_from_closure": len(ring_a_with_closure),
        "ring_a_classes_with_no_develops_from_step_at_all": len(a1) - len(ring_a_with_closure),
        "ring_a_classes_with_any_inbound_edge":
            sum(1 for cid in a1 if key_of[cid] in desc_with_origin),
        "ring_a_classes_with_an_anchored_origin_edge":
            sum(1 for cid in a1 if key_of[cid] in anchored_desc),
        "ring_a_classes_without_any_anchored_origin": sorted(
            label_of[cid] for cid in a1 if key_of[cid] not in anchored_desc),
        "note_on_grade": ("confirmed edges are graded identity_conversion_not_direct only; no local "
                          "artefact supports direct_lineage_support, so none is claimed"),
        "reconciliation": C.counts(r["outcome"] for r in rec),
        "outputs": {"confirmed": os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"),
                    "reconciliation": os.path.join(C.OUT, "FIRSTPASS_RECONCILIATION.tsv")},
    }
    C.write_json(os.path.join(C.OUT, "EDGES_SUMMARY.json"), summ)
    print(json.dumps({k: v for k, v in summ.items()
                      if k not in ("ring_a_classes_without_any_anchored_origin",)},
                     ensure_ascii=False,
                     indent=1))
    print(f"ring-A classes with an anchored origin edge: "
          f"{summ['ring_a_classes_with_an_anchored_origin_edge']} of {len(a1)}; without: "
          f"{len(summ['ring_a_classes_without_any_anchored_origin'])}")
    return 0


def _dev_closure(ont, cid):
    """id -> (steps, path, lines) for every term reachable from cid by >=1 develops_from step."""
    out, frontier = {}, [(p, 1, [cid, p], [ln]) for p, ln in ont.terms[cid].dev_lines]
    while frontier:
        p, d, path, lines = frontier.pop()
        if p in out and out[p][0] <= d:
            continue
        out[p] = (d, path, lines)
        for q, ln in ont.terms[p].dev_lines if p in ont.terms else []:
            frontier.append((q, d + 1, path + [q], lines + [ln]))
    return out


def _row(prec, desc, rel, directness, evidence_ids, lines, derivation, rule, note, chain, steps,
         kind_of, label_of, key_of, anchor_kind=None):
    return {
        "edge_id": "", "edge_key": C.build_edge_key(key_of[prec], key_of[desc], rel),
        "precursor_node": key_of[prec], "descendant_node": key_of[desc], "relation_type": rel,
        "directness": directness, "evidence_ids": evidence_ids,
        "evidence_grade": "identity_conversion_not_direct",
        "conflict_status": "none", "marker_change_ids": "",
        "derivation": derivation, "derivation_rule": rule, "derivation_note": note,
        "chain_precursor_to_descendant": " -> ".join(chain), "steps": steps,
        "obo_lines": ",".join(str(x) for x in lines),
        "source_relation": DEVELOPS_FROM, "source_relation_direction": "develops_from (child->parent)",
        "grade_basis": ("curated_ontology_statement: time direction and identity conversion are "
                        "stated, direct lineage proof is not"),
        "admission": "confirmed", "admission_rule": "evidence grade is in the contract's admitted set",
        "precursor_label": label_of.get(prec, ""), "descendant_label": label_of.get(desc, ""),
        "precursor_kind": kind_of.get(prec, ""), "descendant_kind": kind_of.get(desc, ""),
        "anchor_kind": anchor_kind or ("" if kind_of.get(prec) != "origin_anchor" else "direct"),
        "first_pass_edge_ids": "", "notes": "",
    }


def reconcile(peer_edges, mine) -> list:
    """Say what happened to every edge the first pass delivered. Nothing is silently dropped."""
    out = []
    peer_pair = collections.defaultdict(list)
    for r in peer_edges:
        peer_pair[(r["parent"], r["child"])].append(r)
    for (prec, desc), rows in sorted(peer_pair.items()):
        got = [r for r in mine
               if r["precursor_node"].split("|")[0] == f"dl:{prec}"
               and r["descendant_node"].split("|")[0] == f"dl:{desc}"]
        relation = rows[0]["relation_type"]
        evidence = "ontology" if rows[0]["evidence_kind"] == "ontology" else "corpus_cooccurrence"
        if got:
            r = sorted(got, key=lambda x: (len(x["chain_precursor_to_descendant"]), x["edge_id"]))[0]
            two = len(rows) > 1
            out.append({"first_pass_edge_id": ",".join(r2["edge_id"] for r2 in rows),
                        "first_pass_pair": f"{prec} <- {desc}",
                        "first_pass_relation_type": relation,
                        "first_pass_evidence": evidence,
                        "outcome": ("merged: the peer wrote this ordered pair twice under two "
                                    "relation names" if two else
                                    "re-typed into the contract vocabulary; the ordered pair is "
                                    "emitted exactly once"),
                        "scaffold_edge_id": r["edge_id"],
                        "scaffold_relation_type": r["relation_type"],
                        "why": ("native single develops_from step -> ontology_development_relation "
                                "(directness=direct); more than one step, or an is_a bridge to a "
                                "germ-layer anchor -> ancestral_origin with the rule named in the "
                                "row" if r["relation_type"] != "ontology_development_relation" else
                                "the peer's develops_from_direct and germ_layer_membership rows "
                                "describe the same single step; one row per ordered pair")})
        else:
            out.append({"first_pass_edge_id": ",".join(r2["edge_id"] for r2 in rows),
                        "first_pass_pair": f"{prec} <- {desc}",
                        "first_pass_relation_type": relation,
                        "first_pass_evidence": evidence,
                        "outcome": "not admitted; re-examined against the corpus in s6",
                        "scaffold_edge_id": "", "scaffold_relation_type": "",
                        "why": ("corpus co-occurrence only: the contract does not admit "
                                "co-occurrence as a lineage edge; where the cited chunk really "
                                "asserts a relation the pair is carried into "
                                "PENDING_ASSERTIONS.tsv (repair proposal), otherwise it is kept as "
                                "a rejected row with its reason")})
    return out


if __name__ == "__main__":
    sys.exit(main())