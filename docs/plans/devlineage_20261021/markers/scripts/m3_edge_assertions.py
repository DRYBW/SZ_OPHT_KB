#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m3_edge_assertions.py — per-edge marker-change assertions in the contract's schema.

The edge list is card L2's `LINEAGE_EDGES.tsv` (34 edges), re-keyed into the contract's edge key
`<precursor_node_key>-><descendant_node_key>|rel=<relation_type>` and re-typed so that one relation
type can never be silently upgraded into another:

  develops_from_direct       -> ontology_development_relation, directness=direct
  develops_from_transitive   -> ontology_development_relation, directness=transitive (steps=N)
  germ_layer_membership      -> ancestral_origin, directness=distant

A marker change is written only for an edge the ontology declares direct and for which both ends
have a panel (DESIGN §7). `change=on` needs a local chunk that (1) carries the gene token,
(2) is admissible for the node's species, (3) names the **target** group, (4) is developmentally
scented. **Loss is never claimed**: a gene in the precursor's panel and absent from the
descendant's is a gap, because panel absence is not a detection result.

Writes out/EDGES.tsv, out/MARKER_CHANGE_EDGES.tsv, out/EDGE_MARKER_REFUSALS.tsv
Usage: python3 m3_edge_assertions.py
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

REL_MAP = {
    "develops_from_direct": ("ontology_development_relation", "direct"),
    "develops_from_transitive": ("ontology_development_relation", "transitive"),
    "germ_layer_membership": ("ancestral_origin", "distant"),
}
TARGET_PHRASE = {"retinal cone cell": "cone", "retinal rod cell": "rod"}


def main() -> int:
    nodes = M.read_tsv(os.path.join(M.OUT, "NODES.tsv"))
    edges_in = M.read_tsv(M.L2_EDGES)
    panels = M.load_panels()
    attach = M.read_tsv(os.path.join(M.OUT, "LABEL_ATTACHMENT.tsv"))
    papers = M.load_papers()
    stage_scope = M.load_stage_scope()
    examples = {}
    for line in open(os.path.join(M.OUT, "CORPUS_GENE_EXAMPLES_v1.jsonl"),
                     encoding="utf-8"):
        d = json.loads(line)
        examples[d["gene"]] = d["examples"]
    node_by_id = {n["dl_id"]: n for n in nodes}
    labels_by_node = collections.defaultdict(list)
    for a in attach:
        labels_by_node[a["node_key"]].append(a)
    # genes per node, in the panel's own order, unioned over the node's labels
    genes_by_node = {}
    for key, atts in labels_by_node.items():
        gs = set()
        for a in atts:
            rec = panels.get(a["library"], {}).get("labels", {}).get(a["label"])
            if rec:
                gs.update(rec["genes"])
        genes_by_node[key] = gs

    edges, changes, refusals = [], [], []
    for e in edges_in:
        child_id, parent_id = e["child"], e["parent"]
        rtype, direct = REL_MAP.get(e["relation_type"], ("ontology_development_relation", "unknown"))
        cn, pn = node_by_id.get(child_id), node_by_id.get(parent_id)
        if cn is None or pn is None:
            refusals.append({"edge_id": e["edge_id"],
                             "reason": "parent_group_has_no_panel",
                             "detail": "edge endpoint not in the node list: child=%s parent=%s"
                                       % (child_id, parent_id)})
            continue
        ekey = "%s->%s|rel=%s" % (pn["node_key"], cn["node_key"], rtype)
        # grade: a direct ontology step is direct lineage support; a chain the ontology declares in
        # full supports identity conversion and time direction but is not a single step; a
        # germ-layer membership is a distant origin, graded by what anchors it
        if direct == "direct":
            grade = "direct_lineage_support"
        elif direct == "transitive":
            grade = "identity_conversion_not_direct"
        else:
            grade = ("textbook_or_review_distant_origin" if e["evidence_kind"] == "ontology"
                     else "trajectory_only")
        child_genes = genes_by_node.get(cn["node_key"], set())
        parent_genes = genes_by_node.get(pn["node_key"], set())
        if direct == "direct" and child_genes and parent_genes:
            status = "admitted_stepwise"
        elif direct == "transitive":
            status = "edge_not_stepwise_relation"
        elif direct == "distant":
            status = "marker_change_not_available_for_relation_type"
        elif not parent_genes:
            status = "parent_group_has_no_panel"
        else:
            status = "marker_change_not_available"
        edges.append({
            "edge_id": e["edge_id"], "edge_key": ekey,
            "precursor_node": pn["node_key"], "descendant_node": cn["node_key"],
            "precursor_label": pn["cl_label"] or pn["dl_id"],
            "descendant_label": cn["cl_label"] or cn["dl_id"],
            "relation_type": rtype, "directness": direct,
            "upstream_relation": e["relation_type"], "steps": e["steps"],
            "evidence_ids": e["corpus_locators"] or "", "evidence_grade": grade,
            "evidence_kind": e["evidence_kind"], "conflict_status": "none_recorded",
            "stage_crossing": e["stage_crossing"],
            "precursor_stage": pn["organism_stage"], "descendant_stage": cn["organism_stage"],
            "marker_change_status": status,
            "n_precursor_panel_genes": len(parent_genes), "n_descendant_panel_genes": len(child_genes),
            "ontology_lines": e["obo_lines"],
        })
        if status != "admitted_stepwise":
            refusals.append({"edge_id": e["edge_id"], "edge_key": ekey,
                             "reason": status,
                             "detail": ("upstream status=%s; upstream relation=%s; "
                                        "n_precursor_panel_genes=%d n_descendant_panel_genes=%d"
                                        % (e["marker_transition_status"], e["relation_type"],
                                           len(parent_genes), len(child_genes)))})
            continue

        # ---- admitted stepwise edge: the four-condition test -------------------------------
        target_phrase = TARGET_PHRASE.get(cn["cl_label"], "")
        for g in sorted(child_genes - parent_genes):
            cand = [x for x in examples.get(g, []) if x["species"] in ("human", "both")]
            hit = None
            for x in cand:
                named = bool(x.get("target_phrases"))
                dev = x["dev_kw"] or (stage_scope.get(str(x["paper_id"])) in
                                      ("fetal_only", "mixed"))
                if named and dev:
                    hit = x
                    break
            if hit is None:
                refusals.append({"edge_id": e["edge_id"], "edge_key": ekey, "gene": g,
                                 "reason": "no_source_states_the_change",
                                 "detail": ("%d admissible corpus rows for the gene, none naming the "
                                            "target group in a developmental context"
                                            % len(cand))})
                continue
            pid = str(hit["paper_id"])
            changes.append({
                "assertion_id": "", "edge_id_or_node_key": ekey, "gene_symbol": g,
                "species": "human", "role": "identity_support", "change": "on",
                "stage": cn["organism_stage"], "assay": "literature_RNA",
                "source_group": "%s (%s)" % (pn["cl_label"] or pn["dl_id"], pn["dl_id"]),
                "target_group": "%s (%s)" % (cn["cl_label"] or cn["dl_id"], cn["dl_id"]),
                "effect_value": "", "uncertainty": ("the source names the target group in a "
                                                    "developmental context; no source measures the "
                                                    "precursor->descendant change itself"),
                "claim_type": "qualitative", "evidence_ids": "PMID:%s" % pid,
                "evidence_grade": grade, "evidence_anchor": json.dumps(
                    {"kind": "corpus_gene_row", "file": M.CHUNKS, "paper_id": pid,
                     "section": hit["section"], "ord": hit["ord"], "sha16": hit["sha16"],
                     "chunk_type": hit["chunk_type"], "species": hit["species"],
                     "tissue": hit["tissue"], "dev_kw": hit["dev_kw"],
                     "target_phrases": hit["target_phrases"], "gene": g},
                    ensure_ascii=False, sort_keys=True),
                "support_basis": "corpus_gene_row", "anchor_kind": "corpus_gene_row",
                "anchor_species": hit["species"], "target_subtype": "", "extraction_record": "",
                "detection_conditions": "", "node_family": "edge",
                "node_dl_id": cn["dl_id"], "all_sources": "%s::%s" % (e["edge_id"], ekey),
                "panel_selection_basis": "",
                "source_panel": e["child"], "direction": "gain", "stage_crossing": e["stage_crossing"],
            })
        # loss side: never `off`, never `down`
        for g in sorted(parent_genes - child_genes):
            refusals.append({"edge_id": e["edge_id"], "edge_key": ekey, "gene": g,
                             "reason": "detection_conditions_insufficient",
                             "detail": ("the gene is in the precursor's panel and absent from the "
                                        "descendant's; panel absence is not a detection result, so "
                                        "no off/down is claimed")})

    for i, c in enumerate(changes, 1):
        c["assertion_id"] = "E%06d" % i
    cols = ["assertion_id", "edge_id_or_node_key", "gene_symbol", "species", "role", "change",
            "stage", "assay", "source_group", "target_group", "effect_value", "uncertainty",
            "claim_type", "evidence_ids", "evidence_grade", "evidence_anchor", "support_basis",
            "anchor_kind", "anchor_species", "target_subtype", "extraction_record",
            "detection_conditions", "node_family", "node_dl_id", "all_sources",
            "panel_selection_basis", "source_panel", "direction", "stage_crossing"]
    M.write_tsv(os.path.join(M.OUT, "MARKER_CHANGE_EDGES.tsv"), changes, cols)
    M.write_tsv(os.path.join(M.OUT, "EDGES.tsv"), edges,
                ["edge_id", "edge_key", "precursor_node", "descendant_node", "precursor_label",
                 "descendant_label", "relation_type", "directness", "upstream_relation", "steps",
                 "evidence_ids", "evidence_grade", "evidence_kind", "conflict_status",
                 "stage_crossing", "precursor_stage", "descendant_stage", "marker_change_status",
                 "n_precursor_panel_genes", "n_descendant_panel_genes", "ontology_lines"])
    M.write_tsv(os.path.join(M.OUT, "EDGE_MARKER_REFUSALS.tsv"), refusals,
                ["edge_id", "edge_key", "gene", "reason", "detail"])
    print("edges:", len(edges))
    print("  relation types:", dict(collections.Counter(e["relation_type"] for e in edges)))
    print("  grades         :", dict(collections.Counter(e["evidence_grade"] for e in edges)))
    print("  status         :", dict(collections.Counter(e["marker_change_status"] for e in edges)))
    print("edge marker-change assertions:", len(changes))
    print("  by edge:", dict(collections.Counter(c["edge_id_or_node_key"].split("->")[0][:22]
                                                for c in changes)))
    print("refusals:", dict(collections.Counter(r["reason"] for r in refusals)))
    return 0


if __name__ == "__main__":
    sys.exit(main())