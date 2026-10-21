#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_03_repoint.py — ITEM 3: re-point the node-key and edge-key builders at the scaffold.

Why this is needed
    The frozen contract named `plans/devlineage_20261021/scaffold/` as the node/edge source, but
    that directory did not exist when the marker layer was built, so the layer consumed
    `plans/cl_depth_devlineage_20261021/out/LINEAGE_{NODES,EDGES}.tsv` (60 nodes / 34 edges).
    The scaffold has since landed: 103 nodes, 51 confirmed edges, 44 decapitated branches.

How the re-point is done (and what is deliberately NOT done)
    The builders themselves are the marker layer's own m1/m2/m3/m4, executed unmodified — the
    only thing that changes is the node list and the edge list they are handed. Two adapter
    tables translate the scaffold's published columns into the column contract those builders
    consume (the translation is written out column by column, with the reason for each), and the
    module-level constants are then overridden in place:

        M.OUT     -> out/repointed           (this wave's own output directory)
        M.L2_NODES-> out/adapter/NODES_from_scaffold.tsv
        M.L2_EDGES-> out/adapter/EDGES_from_scaffold.tsv

    The contract's key grammar is the authority: the builders derive node and edge keys from the
    panels and the ontology exactly as before. The scaffold's own key *strings* are recorded next
    to the derived ones rather than adopted verbatim, because the scaffold leaves the species and
    tissue context of most library classes as `unknown` (its own key says `sp=unknown|ts=unknown`)
    while the layer's node keys carry the declared context from the panels; adopting the strings
    would discard declared context and break the join with the assertion set that already exists.
    Every node where the two spellings differ is listed in the diff with that reason.

Outputs: out/adapter/*.tsv, out/repointed/*, out/ITEM3_*.{tsv,json}
Usage  : python3 scripts/w5_03_repoint.py
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402

ADAPTER = os.path.join(C.OUT, "adapter")
REPOINT = os.path.join(C.OUT, "repointed")

NODE_COLUMNS = ["node_id", "kind", "cl_label", "obo_line", "stage_scope", "our_labels",
                "n_panel_genes", "panel_files", "n_inbound_edges", "in_adult_baseline_keys"]
NODE_PROVENANCE = ["node_key_in_scaffold", "ontology_match_status", "library_ring",
                   "scaffold_stage", "scaffold_stage_basis", "scaffold_kind", "anchor_role",
                   "n_our_labels", "in_library", "in_cell_ranking"]

EDGE_COLUMNS = ["edge_id", "child", "parent", "relation_type", "tier", "child_label",
                "parent_label", "chain", "steps", "obo_lines", "child_stage", "parent_stage",
                "stage_crossing", "evidence_kind", "corpus_n_chunks", "corpus_n_papers",
                "corpus_locators", "marker_transition_status"]
EDGE_PROVENANCE = ["edge_key_in_scaffold", "scaffold_relation_type", "directness",
                   "evidence_grade", "derivation", "derivation_rule", "first_pass_edge_ids",
                   "precursor_kind", "descendant_kind", "precursor_label", "descendant_label"]


def adapter_ledger():
    """Every translation decision, written out rather than left in the code."""
    return [
        {"column": "node_id", "from": "SCAFFOLD_NODES.node_id",
         "rule": "verbatim; already in the contract's form (CL id, or the mandatory "
                 "NO_MATCH:<in_house_class_id> for the 15 concepts the ontology cannot key)"},
        {"column": "kind", "from": "SCAFFOLD_NODES.kind",
         "rule": "origin_anchor -> germ_layer (the builder's one anchor branch, which forces "
                 "unknown context and never lets an anchor pose as a cell type); library_class "
                 "and ontology_intermediate pass through unchanged"},
        {"column": "cl_label", "from": "SCAFFOLD_NODES.cl_label", "rule": "verbatim"},
        {"column": "obo_line", "from": "SCAFFOLD_NODES.obo_line",
         "rule": "verbatim (empty for the NO_MATCH concepts, which have no ontology line)"},
        {"column": "stage_scope", "from": "SCAFFOLD_NODES.stage + stage_basis",
         "rule": "developing -> developing; adult -> adult_or_unspecified plus the recorded "
                 "baseline key, so the builder still resolves adult through the repository's own "
                 "baseline entries; unknown -> adult_or_unspecified with no baseline key, which "
                 "the builder resolves to unknown. Unknown never becomes adult."},
        {"column": "in_adult_baseline_keys", "from": "SCAFFOLD_NODES.stage_basis",
         "rule": "the baseline entry named by the scaffold's own stage_basis when it is an adult "
                 "baseline (e.g. baseline:retina.json#development_stage=adult); empty otherwise"},
        {"column": "our_labels", "from": "SCAFFOLD_NODES.our_labels", "rule": "verbatim"},
        {"column": "n_panel_genes", "from": "SCAFFOLD_NODES.n_panel_genes", "rule": "verbatim"},
        {"column": "panel_files", "from": "SCAFFOLD_NODES.panel_files", "rule": "verbatim"},
        {"column": "n_inbound_edges", "from": "SCAFFOLD_EDGES_CONFIRMED",
         "rule": "counted from the confirmed edge list (the scaffold table does not carry it)"},
        {"column": "edge_id", "from": "SCAFFOLD_EDGES_CONFIRMED.edge_id",
         "rule": "verbatim (S####), so every re-pointed edge traces to the scaffold row it came "
                 "from; the first-pass ids the scaffold reconciled against are kept in the "
                 "provenance column first_pass_edge_ids"},
        {"column": "child / parent", "from": "SCAFFOLD_EDGES_CONFIRMED.descendant_node / "
                                             "precursor_node",
         "rule": "the contract id parsed out of the endpoint's node_key; child is the descendant "
                 "(the direction develops_from itself uses). Asserted: every parsed id exists in "
                 "the node list."},
        {"column": "relation_type", "from": "SCAFFOLD_EDGES_CONFIRMED.relation_type + directness",
         "rule": "the builder's three-way mapping is preserved rather than bypassed: "
                 "directness=direct -> develops_from_direct; directness=chain:* -> "
                 "develops_from_transitive; relation_type=ancestral_origin -> "
                 "germ_layer_membership. No relation is upgraded: a chain never becomes a step."},
        {"column": "evidence_kind", "from": "SCAFFOLD_EDGES_CONFIRMED.derivation",
         "rule": "native_ontology_attribute and derived_rule(R-ANCHOR-*) both resolve to "
                 "ontology: every one of the 51 rows carries ontology file lines as its "
                 "evidence_ids, and none rests on a corpus co-occurrence"},
        {"column": "steps / obo_lines / chain", "from": "SCAFFOLD_EDGES_CONFIRMED",
         "rule": "verbatim"},
        {"column": "stage_crossing", "from": "SCAFFOLD_EDGES_CONFIRMED endpoint stages",
         "rule": "yes when the two endpoints declare different stages, else no"},
        {"column": "corpus_n_chunks / corpus_n_papers / corpus_locators", "from": "-",
         "rule": "empty: the scaffold admits or refuses an edge on ontology evidence, and the "
                 "corpus numbers that the first-pass table carried were the weak co-occurrence "
                 "counts, not admissions"},
        {"column": "marker_transition_status", "from": "recomputed here from the panels",
         "rule": "a display field of the first pass that the scaffold's edge table does not carry "
                 "and that the edge builder reads when it writes a refusal line. Recomputed with "
                 "the first pass's own definition (panel difference on the gain side, graded by "
                 "whether the corpus has any row for the gene, i.e. the weak grading item 1 of "
                 "this wave re-measures). It is never an admission by itself."},
    ]


def endpoint_id(node_key):
    return node_key.split("|", 1)[0][len("dl:"):]


def main() -> int:
    t0 = time.time()
    summ = {}
    os.makedirs(ADAPTER, exist_ok=True)
    os.makedirs(REPOINT, exist_ok=True)

    scaf_nodes = C.read_tsv(os.path.join(C.SCAF_OUT, "SCAFFOLD_NODES.tsv"))
    scaf_edges = C.read_tsv(os.path.join(C.SCAF_OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    summ["scaffold_nodes_in"] = len(scaf_nodes)
    summ["scaffold_edges_in"] = len(scaf_edges)

    # ---------------------------------------------------------------- node adapter
    inbound = {}
    for e in scaf_edges:
        inbound[endpoint_id(e["descendant_node"])] = inbound.get(
            endpoint_id(e["descendant_node"]), 0) + 1
    node_ids = {r["node_id"] for r in scaf_nodes}
    assert len(node_ids) == len(scaf_nodes), "the scaffold node ids are not unique"

    n_rows, adult_basis, stage_map = [], 0, {}
    for r in scaf_nodes:
        basis = r["stage_basis"] or ""
        if r["stage"] == "developing":
            stage_scope, adult = "developing", ""
        elif r["stage"] == "adult":
            stage_scope, adult = "adult_or_unspecified", (basis or "baseline:unspecified")
            adult_basis += 1
        else:
            stage_scope, adult = "adult_or_unspecified", ""
        stage_map[(r["stage"], basis[:40])] = stage_map.get((r["stage"], basis[:40]), 0) + 1
        row = {
            "node_id": r["node_id"],
            "kind": "germ_layer" if r["kind"] == "origin_anchor" else r["kind"],
            "cl_label": r["cl_label"], "obo_line": r["obo_line"], "stage_scope": stage_scope,
            "our_labels": r["our_labels"], "n_panel_genes": r["n_panel_genes"],
            "panel_files": r["panel_files"], "n_inbound_edges": inbound.get(r["node_id"], 0),
            "in_adult_baseline_keys": adult,
            "node_key_in_scaffold": r["node_key"],
            "ontology_match_status": r["ontology_match_status"], "library_ring": r["library_ring"],
            "scaffold_stage": r["stage"], "scaffold_stage_basis": r["stage_basis"],
            "scaffold_kind": r["kind"], "anchor_role": r["anchor_role"],
            "n_our_labels": r["n_our_labels"], "in_library": r["in_library"],
            "in_cell_ranking": r["in_cell_ranking"],
        }
        n_rows.append(row)
    assert len(n_rows) == len(scaf_nodes), "a scaffold node was dropped in the adapter"
    summ["nodes_adult_with_recorded_baseline"] = adult_basis
    C.write_tsv(os.path.join(ADAPTER, "NODES_from_scaffold.tsv"), n_rows,
                NODE_COLUMNS + NODE_PROVENANCE)
    summ["adapter_node_stage_map"] = {"%s|%s" % k: v for k, v in sorted(stage_map.items())}

    # ---------------------------------------------------------------- corpus artefacts (carried)
    # The corpus index the marker layer built is scaffolding-neutral, so it is carried over
    # byte-identically: that keeps the re-point a controlled experiment — the only thing that
    # changes between the two layers is the node list and the edge list.
    carried = {}
    for name in ("CORPUS_GENE_INDEX_v1.tsv", "CORPUS_GENE_EXAMPLES_v1.jsonl",
                 "CORPUS_GENE_INDEX_v1_META.json"):
        src = os.path.join(C.MK_OUT, name)
        dst = os.path.join(REPOINT, name)
        shutil.copy2(src, dst)
        carried[name] = {"source": src, "sha256": C.sha256(dst)}
    summ["corpus_artefacts_carried_over"] = carried

    M = C.markers_common()
    old = {"OUT": M.OUT, "L2_NODES": M.L2_NODES, "L2_EDGES": M.L2_EDGES}
    M.OUT = REPOINT
    M.L2_NODES = os.path.join(ADAPTER, "NODES_from_scaffold.tsv")
    M.L2_EDGES = os.path.join(ADAPTER, "EDGES_from_scaffold.tsv")
    summ["repoint_override"] = {"M.OUT": M.OUT, "M.L2_NODES": M.L2_NODES, "M.L2_EDGES": M.L2_EDGES,
                                "previous": old}
    import m1_nodes  # noqa: E402
    import m2_node_markers  # noqa: E402
    import m3_edge_assertions  # noqa: E402
    import m4_gap_register  # noqa: E402

    rc = [{"module": "m1_nodes", "rc": m1_nodes.main()}]

    # ---------------------------------------------------------------- edge adapter
    # Built after the node builder has run, because one column the edge builder expects
    # (`marker_transition_status`) is a display field of the first pass that has to be recomputed
    # here: the scaffold's edge table (rightly) does not carry it. It is recomputed with the same
    # definition the first pass used — panel-difference on the gain side, graded by whether the
    # corpus has any row for the gene — and it is a field of the refusal line only, never an
    # admission. Its grading is the weak one, and item 1 of this wave reports exactly that.
    panels = M.load_panels()
    attach = C.read_tsv(os.path.join(REPOINT, "LABEL_ATTACHMENT.tsv"))
    gidx = {r["gene"]: int(r["n_chunks"])
            for r in C.read_tsv(os.path.join(REPOINT, "CORPUS_GENE_INDEX_v1.tsv"))}
    genes_by_id = {}
    for a in attach:
        rec = panels.get(a["library"], {}).get("labels", {}).get(a["label"])
        if rec is None:
            continue
        genes_by_id.setdefault(a["dl_id"], set()).update(rec["genes"])
    label_by_id = {r["node_id"]: r["cl_label"] for r in scaf_nodes}
    stage_by_id = {r["node_id"]: r["stage"] for r in scaf_nodes}
    e_rows, unresolved = [], []
    for e in scaf_edges:
        p_id, d_id = endpoint_id(e["precursor_node"]), endpoint_id(e["descendant_node"])
        for side, sid in (("precursor", p_id), ("descendant", d_id)):
            if sid not in node_ids:
                unresolved.append({"edge_id": e["edge_id"], "side": side, "id": sid})
        if e["relation_type"] == "ancestral_origin":
            rel = "germ_layer_membership"
        elif e["directness"] == "direct":
            rel = "develops_from_direct"
        else:
            rel = "develops_from_transitive"
        if rel == "germ_layer_membership":
            mts = "not_applicable_membership"
        elif rel != "develops_from_direct":
            mts = "not_stepwise_relation"
        else:
            cg, pg = genes_by_id.get(d_id, set()), genes_by_id.get(p_id, set())
            if not cg:
                mts = "child_panel_absent"
            elif not pg:
                mts = "parent_panel_absent"
            else:
                n_sup = sum(1 for g in (cg - pg) if gidx.get(g, 0) > 0)
                mts = "has_supported_transition" if n_sup else "no_supported_transition"
        e_rows.append({
            "edge_id": e["edge_id"], "child": d_id, "parent": p_id, "relation_type": rel,
            "tier": "", "child_label": label_by_id.get(d_id, ""),
            "parent_label": label_by_id.get(p_id, ""),
            "chain": e["chain_precursor_to_descendant"], "steps": e["steps"],
            "obo_lines": e["obo_lines"],
            "child_stage": stage_by_id.get(d_id, ""), "parent_stage": stage_by_id.get(p_id, ""),
            "stage_crossing": "yes" if stage_by_id.get(d_id) != stage_by_id.get(p_id) else "no",
            "evidence_kind": "ontology",
            "corpus_n_chunks": "", "corpus_n_papers": "", "corpus_locators": "",
            "marker_transition_status": mts,
            "edge_key_in_scaffold": e["edge_key"], "scaffold_relation_type": e["relation_type"],
            "directness": e["directness"], "evidence_grade": e["evidence_grade"],
            "derivation": e["derivation"], "derivation_rule": e["derivation_rule"],
            "first_pass_edge_ids": e["first_pass_edge_ids"], "precursor_kind": e["precursor_kind"],
            "descendant_kind": e["descendant_kind"], "precursor_label": e["precursor_label"],
            "descendant_label": e["descendant_label"],
        })
    summ["adapter_edges_unresolved_endpoints"] = unresolved
    assert not unresolved, "an edge endpoint does not exist in the node list"
    assert len(e_rows) == len(scaf_edges), "a scaffold edge was dropped in the adapter"
    C.write_tsv(os.path.join(ADAPTER, "EDGES_from_scaffold.tsv"), e_rows,
                EDGE_COLUMNS + EDGE_PROVENANCE)
    summ["adapter_marker_transition_status"] = {
        v: sum(1 for r in e_rows if r["marker_transition_status"] == v)
        for v in sorted({r["marker_transition_status"] for r in e_rows})}
    C.write_tsv(os.path.join(ADAPTER, "COLUMN_MAPPING.tsv"), adapter_ledger(),
                ["column", "from", "rule"])

    for mod in (m2_node_markers, m3_edge_assertions, m4_gap_register):
        rc.append({"module": mod.__name__, "rc": mod.main()})
    summ["builder_rc"] = rc

    # ---------------------------------------------------------------- the diff
    old_nodes = C.read_tsv(os.path.join(C.MK_OUT, "NODES.tsv"))
    new_nodes = C.read_tsv(os.path.join(REPOINT, "NODES.tsv"))
    old_sets = C.read_tsv(os.path.join(C.MK_OUT, "MARKER_SETS_NODE.tsv"))
    new_sets = C.read_tsv(os.path.join(REPOINT, "MARKER_SETS_NODE.tsv"))
    old_edges = C.read_tsv(os.path.join(C.MK_OUT, "EDGES.tsv"))
    new_edges = C.read_tsv(os.path.join(REPOINT, "EDGES.tsv"))
    old_chg = C.read_tsv(os.path.join(C.MK_OUT, "MARKER_CHANGE_EDGES.tsv"))
    new_chg = C.read_tsv(os.path.join(REPOINT, "MARKER_CHANGE_EDGES.tsv"))
    old_gap = C.read_tsv(os.path.join(C.MK_OUT, "GAP_REGISTER.tsv"))
    new_gap = C.read_tsv(os.path.join(REPOINT, "GAP_REGISTER.tsv"))

    def by_id(rows, key="node_key"):
        return {r[key]: r for r in rows}

    on, nn = by_id(old_nodes), by_id(new_nodes)
    kept = sorted(set(on) & set(nn))
    added = sorted(set(nn) - set(on))
    dropped = sorted(set(on) - set(nn))
    summ["nodes"] = {"old": len(on), "new": len(nn), "kept_by_key": len(kept),
                     "added": len(added), "dropped": len(dropped)}
    # a node whose class is present but under another key = a key move, not a loss
    old_by_id = {}
    for k, v in on.items():
        old_by_id.setdefault(v["dl_id"], []).append(k)
    new_by_id = {}
    for k, v in nn.items():
        new_by_id.setdefault(v["dl_id"], []).append(k)
    moved = []
    for did, ks in old_by_id.items():
        for k in ks:
            if k not in nn and did in new_by_id:
                moved.append({"dl_id": did, "old_key": k, "new_key": new_by_id[did][0],
                              "old_stage": on[k]["organism_stage"],
                              "new_stage": nn[new_by_id[did][0]]["organism_stage"],
                              "old_upstream_stage_scope": on[k]["stage_scope_upstream"],
                              "new_upstream_stage_scope": nn[new_by_id[did][0]][
                                  "stage_scope_upstream"]})
    summ["node_keys_moved"] = len(moved)
    summ["node_keys_moved_detail"] = moved[:40]
    C.write_tsv(os.path.join(C.OUT, "ITEM3_NODE_KEY_MOVES.tsv"), moved,
                ["dl_id", "old_key", "new_key", "old_stage", "new_stage",
                 "old_upstream_stage_scope", "new_upstream_stage_scope"])

    # contract key vs the scaffold's own key string, per node family
    adapter = {r["node_id"]: r for r in C.read_tsv(
        os.path.join(ADAPTER, "NODES_from_scaffold.tsv"))}
    vs = []
    for k, v in nn.items():
        a = adapter.get(v["dl_id"])
        if not a:
            continue
        vs.append({"dl_id": v["dl_id"], "node_family": v["node_family"],
                   "kind_in_scaffold": a["scaffold_kind"],
                   "contract_key": k, "scaffold_key": a["node_key_in_scaffold"],
                   "same": "yes" if k == a["node_key_in_scaffold"] else "no"})
    C.write_tsv(os.path.join(C.OUT, "ITEM3_KEY_SPELLING.tsv"), vs,
                ["dl_id", "node_family", "kind_in_scaffold", "contract_key", "scaffold_key",
                 "same"])
    summ["key_spelling"] = {
        "compared": len(vs),
        "identical": sum(1 for r in vs if r["same"] == "yes"),
        "differing": sum(1 for r in vs if r["same"] == "no"),
        "by_kind": {k: {"compared": sum(1 for r in vs if r["kind_in_scaffold"] == k),
                        "identical": sum(1 for r in vs if r["kind_in_scaffold"] == k
                                         and r["same"] == "yes")}
                    for k in sorted({r["kind_in_scaffold"] for r in vs})},
        "reason": ("the scaffold's own key strings leave sp/ts as unknown for most library "
                   "classes; the contract key builder derives the declared context from the "
                   "panels, which is the spelling the existing assertion set joins on"),
    }

    # assertions: does each previously reported node assertion still resolve in the new layer?
    def node_assertions(rows):
        return {(r["edge_id_or_node_key"], r["gene_symbol"]) for r in rows
                if r["node_family"] in ("scaffold", "in_house_dev_precursor")}
    old_assert = node_assertions(old_sets)
    new_assert = node_assertions(new_sets)
    key_by_class_old = {v["dl_id"]: k for k, v in on.items()}
    key_by_class_new = {v["dl_id"]: k for k, v in nn.items()}
    res = {"same_key": 0, "key_moved": 0, "relocated_to_another_node": 0, "unresolved": 0}
    lost_rows, moved_rows = [], []
    class_by_key_new = {k: v["dl_id"] for k, v in nn.items()}
    for (nk, g) in sorted(old_assert):
        if (nk, g) in new_assert:
            res["same_key"] += 1
            continue
        did = on[nk]["dl_id"]
        nk2 = key_by_class_new.get(did)
        if nk2 and (nk2, g) in new_assert:
            res["key_moved"] += 1
            moved_rows.append({"gene_symbol": g, "dl_id": did, "old_node_key": nk,
                               "new_node_key": nk2})
            continue
        # The gene is gone from that node. Before calling it lost, look for it elsewhere: the
        # scaffold gives several library concepts their own node (the in-house state programmes),
        # so a gene that the first pass attached to an identity node by an in-code mapping table
        # now lives on its own node. That is a relocation and it is reported as one.
        elsewhere = sorted(k for (k2, g2) in new_assert if g2 == g and k2 != nk
                           for k in [k2])
        row = {"gene_symbol": g, "dl_id": did, "old_node_key": nk,
               "new_node_key": nk2 or "(class absent)",
               "elsewhere_in_new_layer": " | ".join(elsewhere[:4]),
               "n_places_elsewhere": len(elsewhere),
               "new_layer_assertions_for_class": sum(1 for (k2, _g) in new_assert
                                                     if k2 == (nk2 or ""))}
        if elsewhere:
            res["relocated_to_another_node"] += 1
            row["resolution"] = "relocated"
            row["relocated_to_class"] = class_by_key_new.get(elsewhere[0], "")
        else:
            res["unresolved"] += 1
            row["resolution"] = "unresolved"
            row["relocated_to_class"] = ""
        lost_rows.append(row)
    summ["node_assertions"] = {"old": len(old_assert), "new": len(new_assert),
                               "resolution": res}
    C.write_tsv(os.path.join(C.OUT, "ITEM3_ASSERTIONS_LOST.tsv"), lost_rows,
                ["gene_symbol", "dl_id", "old_node_key", "new_node_key", "resolution",
                 "relocated_to_class", "elsewhere_in_new_layer", "n_places_elsewhere",
                 "new_layer_assertions_for_class"])

    # the stage axis: which node keys moved because the two node sources declare stage
    # differently, in which direction, and whether any node was moved *to* adult.
    axis = {"adult_to_unknown": 0, "developing_to_unknown": 0, "unknown_to_adult": 0,
            "started_as_moving_to_adult": 0, "other": 0, "moved": len(moved)}
    for m in moved:
        p = (m["old_stage"], m["new_stage"])
        if p == ("adult", "unknown"):
            axis["adult_to_unknown"] += 1
        elif p == ("developing", "unknown"):
            axis["developing_to_unknown"] += 1
        elif m["new_stage"] == "adult":
            axis["started_as_moving_to_adult"] += 1
        else:
            axis["other"] += 1
    axis["nodes_moved_to_adult"] = sum(1 for m in moved if m["new_stage"] == "adult")
    axis["adult_nodes_old"] = sum(1 for r in on.values() if r["organism_stage"] == "adult")
    axis["adult_nodes_new"] = sum(1 for r in nn.values() if r["organism_stage"] == "adult")
    summ["stage_axis"] = axis
    C.write_tsv(os.path.join(C.OUT, "ITEM3_ASSERTIONS_MOVED.tsv"), moved_rows,
                ["gene_symbol", "dl_id", "old_node_key", "new_node_key"])

    # nodes with at least one assertion / with none, old vs new
    old_cov = {k for k, _g in old_assert}
    new_cov = {k for k, _g in new_assert}
    summ["node_coverage"] = {"old_nodes_with_an_assertion": len(old_cov),
                             "new_nodes_with_an_assertion": len(new_cov),
                             "old_nodes_with_no_assertion": len(on) - len(old_cov),
                             "new_nodes_with_no_assertion": len(nn) - len(new_cov)}
    zero_new = sorted(k for k in nn if k not in new_cov)
    C.write_tsv(os.path.join(C.OUT, "ITEM3_NODES_WITH_NO_ASSERTION.tsv"),
                [{"node_key": k, "dl_id": nn[k]["dl_id"], "node_family": nn[k]["node_family"],
                  "labels": nn[k]["labels"]} for k in zero_new],
                ["node_key", "dl_id", "node_family", "labels"])

    # edges
    summ["edges"] = {
        "old": len(old_edges), "new": len(new_edges),
        "old_relation_types": {t: sum(1 for r in old_edges if r["relation_type"] == t)
                               for t in sorted({r["relation_type"] for r in old_edges})},
        "new_relation_types": {t: sum(1 for r in new_edges if r["relation_type"] == t)
                               for t in sorted({r["relation_type"] for r in new_edges})},
        "old_status": {t: sum(1 for r in old_edges if r["marker_change_status"] == t)
                       for t in sorted({r["marker_change_status"] for r in old_edges})},
        "new_status": {t: sum(1 for r in new_edges if r["marker_change_status"] == t)
                       for t in sorted({r["marker_change_status"] for r in new_edges})},
        "old_admitted_stepwise": sum(1 for r in old_edges
                                     if r["marker_change_status"] == "admitted_stepwise"),
        "new_admitted_stepwise": sum(1 for r in new_edges
                                     if r["marker_change_status"] == "admitted_stepwise"),
        "old_marker_change_assertions": len(old_chg),
        "new_marker_change_assertions": len(new_chg),
    }
    # the same ordered pair, old id vs scaffold id (the scaffold reconciled against the first pass)
    old_pairs = {(r["descendant_node"].split("|")[0], r["precursor_node"].split("|")[0],
                  r["relation_type"]) for r in old_edges}
    new_pairs = {(r["descendant_node"].split("|")[0], r["precursor_node"].split("|")[0],
                  r["relation_type"]) for r in new_edges}
    summ["edge_pairs"] = {"old_pairs": len(old_pairs), "new_pairs": len(new_pairs),
                          "old_pairs_also_in_new": len(old_pairs & new_pairs),
                          "new_pairs_not_in_old": len(new_pairs - old_pairs)}
    cross = []
    for e in new_edges:
        d = e["descendant_node"].split("|")[0]
        p = e["precursor_node"].split("|")[0]
        cross.append({"scaffold_edge_id": e["edge_id"], "relation_type": e["relation_type"],
                      "descendant": d, "precursor": p,
                      "in_first_pass_layer": "yes" if (d, p, e["relation_type"]) in old_pairs
                                             else "no",
                      "marker_change_status": e["marker_change_status"]})
    C.write_tsv(os.path.join(C.OUT, "ITEM3_EDGE_CROSSWALK.tsv"), cross,
                ["scaffold_edge_id", "relation_type", "descendant", "precursor",
                 "in_first_pass_layer", "marker_change_status"])

    # edges that gained a marker change: what the new layer now claims, gene by gene
    new_chg_rows = [{"scaffold_edge_id": r["edge_id_or_node_key"].split("->")[0],
                     "edge_key": r["edge_id_or_node_key"], "gene_symbol": r["gene_symbol"],
                     "target_group": r["target_group"], "change": r["change"],
                     "evidence_ids": r["evidence_ids"]} for r in new_chg]
    C.write_tsv(os.path.join(C.OUT, "ITEM3_NEW_MARKER_CHANGES.tsv"), new_chg_rows,
                ["scaffold_edge_id", "edge_key", "gene_symbol", "target_group", "change",
                 "evidence_ids"])
    summ["new_marker_change_genes_per_edge"] = sorted(
        {r["scaffold_edge_id"] for r in new_chg_rows})

    # the gap register moves with the layer
    summ["gap_register"] = {"old_rows": len(old_gap), "new_rows": len(new_gap)}

    # ---------------------------------------------------------------- evidence-grade conflict
    # The edge builder derives the grade from the relation type it was handed (a direct ontology
    # step becomes direct_lineage_support). The scaffold grades every one of its 51 confirmed
    # edges identity_conversion_not_direct and says in its own summary that no local artefact
    # supports direct_lineage_support, so none is claimed. The two cannot both govern, and the
    # contract forbids a silent upgrade, so the source's grade is made to govern and the
    # builder's value is kept next to it as a named conflict rather than quietly overwritten.
    src_grade = {e["edge_id"]: e["evidence_grade"] for e in scaf_edges}
    adap_grade = {r["edge_id"]: r["evidence_grade"]
                  for r in C.read_tsv(os.path.join(ADAPTER, "EDGES_from_scaffold.tsv"))}
    grades, reconciled = [], []
    for r in new_edges:
        sid = r["edge_id"]
        b_g, s_g = r["evidence_grade"], src_grade.get(sid, "")
        grades.append({"scaffold_edge_id": sid, "relation_type": r["relation_type"],
                       "directness": r["directness"],
                       "evidence_grade_builder": b_g, "evidence_grade_source_scaffold": s_g,
                       "agreement": "yes" if b_g == s_g else "no",
                       "governing_grade": s_g})
        row = dict(r)
        row["evidence_grade_builder"] = b_g
        row["evidence_grade"] = s_g
        reconciled.append(row)
    C.write_tsv(os.path.join(C.OUT, "ITEM3_GRADE_RECONCILIATION.tsv"), grades,
                ["scaffold_edge_id", "relation_type", "directness", "evidence_grade_builder",
                 "evidence_grade_source_scaffold", "agreement", "governing_grade"])
    C.write_tsv(os.path.join(C.OUT, "repointed", "EDGES_RECONCILED.tsv"), reconciled,
                list(new_edges[0].keys()) + ["evidence_grade_builder"])
    summ["grade_reconciliation"] = {
        "edges_compared": len(grades),
        "agreement": sum(1 for r in grades if r["agreement"] == "yes"),
        "conflicts": sum(1 for r in grades if r["agreement"] == "no"),
        "builder_values": {v: sum(1 for r in grades if r["evidence_grade_builder"] == v)
                           for v in sorted({r["evidence_grade_builder"] for r in grades})},
        "source_values": {v: sum(1 for r in grades if r["evidence_grade_source_scaffold"] == v)
                          for v in sorted({r["evidence_grade_source_scaffold"] for r in grades})},
        "governing_grade": "the source (scaffold) grade; recorded in EDGES_RECONCILED.tsv",
        "why": ("the builder's rule maps a direct relation to direct_lineage_support, but the "
                "scaffold's own grading says an ontology develops_from statement states time "
                "direction and identity conversion and is not direct lineage proof; the contract "
                "forbids an upgrade, so the source governs and the builder value is kept as a "
                "named conflict for the card that owns the grading rule"),
    }
    # the marker-change assertions inherit the same grading, so they are reconciled the same way
    key_to_edge = {r["edge_key"]: r["edge_id"] for r in new_edges}
    chg_recon = []
    for r in new_chg:
        sid = key_to_edge.get(r["edge_id_or_node_key"], "")
        row = dict(r)
        row["evidence_grade_builder"] = r["evidence_grade"]
        row["evidence_grade"] = src_grade.get(sid, r["evidence_grade"])
        row["scaffold_edge_id"] = sid
        chg_recon.append(row)
    C.write_tsv(os.path.join(C.OUT, "repointed", "MARKER_CHANGE_EDGES_RECONCILED.tsv"),
                chg_recon, list(new_chg[0].keys()) + ["evidence_grade_builder",
                                                      "scaffold_edge_id"])
    summ["marker_change_grade_reconciliation"] = {
        "rows": len(chg_recon),
        "builder_grade": sorted({r["evidence_grade_builder"] for r in chg_recon}),
        "governing_grade": sorted({r["evidence_grade"] for r in chg_recon}),
    }
    summ["seconds"] = round(time.time() - t0, 1)
    C.write_json(os.path.join(C.OUT, "ITEM3_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())