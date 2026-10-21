#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m4_gap_register.py — the gap register, which is a first-class deliverable and not a leftover.

Every node and every edge that carries no evidence appears here by name, with a reason drawn from
the closed vocabulary in DESIGN §8 and with the local material that was actually checked. Three
kinds are distinguished so the register cannot be read as one undifferentiated "missing" pile:

  no_evidence      nothing admissible exists locally; the node or edge is a research agenda item
  thin_evidence    an assertion exists but its support is weak (basis unstated in the panel, a
                   citation that cannot be checked locally, a source whose full text is absent, or
                   a stage or species mismatch that stops it from being stitched)
  refused_evidence material exists but is inadmissible (evaluation-volume-derived, on a library's
                   prohibition list, or from a panel built to fill the benchmark's own holes)

Writes out/GAP_REGISTER.tsv (+ out/GAP_SUMMARY.json)
Usage: python3 m4_gap_register.py
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402


def main() -> int:
    out = M.OUT
    nodes = M.read_tsv(os.path.join(out, "NODES.tsv"))
    attach = M.read_tsv(os.path.join(out, "LABEL_ATTACHMENT.tsv"))
    node_sets = M.read_tsv(os.path.join(out, "MARKER_SETS_NODE.tsv"))
    node_ref = M.read_tsv(os.path.join(out, "NODE_GENE_REFUSALS.tsv"))
    edges = M.read_tsv(os.path.join(out, "EDGES.tsv"))
    edge_changes = M.read_tsv(os.path.join(out, "MARKER_CHANGE_EDGES.tsv"))
    edge_ref = M.read_tsv(os.path.join(out, "EDGE_MARKER_REFUSALS.tsv"))
    gidx = {r["gene"]: r for r in M.read_tsv(os.path.join(out, "CORPUS_GENE_INDEX_v1.tsv"))}
    papers = M.load_papers()
    stage_scope = M.load_stage_scope()
    panels = M.load_panels()
    rows = []

    def add(**kw):
        kw.setdefault("gene", "")
        kw.setdefault("detail", "")
        kw.setdefault("suggested_next_source", "")
        rows.append(kw)

    nodes_with_evidence = {r["edge_id_or_node_key"] for r in node_sets}
    node_by_key = {n["node_key"]: n for n in nodes}
    anchors = {}
    for line in open(os.path.join(out, "ANCHORS.jsonl"), encoding="utf-8"):
        d = json.loads(line)
        anchors[d["assertion_id"]] = d["anchor"]

    # ---- 1. nodes with no assertion at all -------------------------------------------------
    for n in nodes:
        if n["node_key"] in nodes_with_evidence:
            continue
        n_genes = 0
        for a in attach:
            if a["node_key"] == n["node_key"]:
                n_genes += int(a["n_genes"] or 0)
        if n["kind"] == "germ_layer":
            reason, detail = ("node_has_no_panel_and_no_source",
                              "germ-layer anchor; no shipped panel carries it and the marker layer "
                              "does not manufacture one")
        elif n_genes == 0:
            reason, detail = ("node_has_no_panel_and_no_source",
                              "the node is declared by the scaffold but no consumed panel ships a "
                              "gene list for it")
        else:
            reason, detail = ("no_source_in_corpus",
                              "panels ship %d genes but none of them reached an admissible anchor"
                              % n_genes)
        add(scope="node", subject_key=n["node_key"], subject_label=n["cl_label"] or n["dl_id"],
            library="", gap_kind="no_evidence", reason=reason,
            detail=detail + " | stage=%s tissue=%s family=%s"
                            % (n["organism_stage"], n["tissue_context"], n["node_family"]),
            evidence_status="node declared in the scaffold; 0 admissible marker assertions")

    # ---- 2. labels we ship that no node can carry ------------------------------------------
    attached = {(a["library"], a["label"]) for a in attach}
    for lib, p in panels.items():
        for label, rec in p["labels"].items():
            if (lib, label) in attached:
                continue
            kind = rec.get("kind") or "unclassified"
            if kind == "state_program":
                reason = "state_program_without_identity_node"
                detail = ("shipped as a state programme; no identity node exists for it in the node "
                          "list, so it is not written onto one")
            else:
                reason = "no_source_in_corpus"
                detail = ("declared by %s with %d genes; the ontology carries no term our mapping "
                          "resolves to a node" % (p["file"], len(rec["genes"])))
            add(scope="label", subject_key="%s::%s" % (lib, label), subject_label=label,
                library=lib, gap_kind="no_evidence", reason=reason, detail=detail,
                evidence_status="%d genes shipped, 0 attached to a node" % len(rec["genes"]),
                suggested_next_source="an ontology term for this class, or an explicit in-house "
                                      "NO_MATCH node")

    # ---- 3. gene-level refusals carried up from the node build ----------------------------
    for r in node_ref:
        n = node_by_key.get(r["node_key"], {})
        add(scope="gene", subject_key=r["node_key"],
            subject_label=n.get("cl_label") or r["node_key"], library=r["library"], gene=r["gene"],
            gap_kind="refused_evidence", reason=r["reason"], detail=r["detail"],
            evidence_status="present in %s::%s" % (r["library"], r["label"]))

    # ---- 4. thin evidence: an assertion exists but its support is weak --------------------
    for a in node_sets:
        aid = a["assertion_id"]
        gene = a["gene_symbol"]
        idx = gidx.get(gene, {})
        n_all = int(idx.get("n_chunks") or 0)
        n_nofull = int(idx.get("n_chunks_no_full_text") or 0)
        anchor = anchors.get(aid, {})
        if a["support_basis"] == "panel_entry_basis_unstated":
            add(scope="gene", subject_key=a["edge_id_or_node_key"], subject_label=a["target_group"],
                library=a["source_group"].split("::")[0], gene=gene, gap_kind="thin_evidence",
                reason="panel_entry_basis_unstated",
                detail="the gene is shipped in %s but that panel states no per-gene basis and no "
                       "corpus row anchors it" % a["source_group"],
                evidence_status="%d corpus chunks" % n_all)
            continue
        if n_all and n_all == n_nofull:
            add(scope="gene", subject_key=a["edge_id_or_node_key"], subject_label=a["target_group"],
                library=a["source_group"].split("::")[0], gene=gene, gap_kind="thin_evidence",
                reason="source_exists_not_full_text",
                detail="every corpus chunk carrying this gene has full_text_available=0",
                evidence_status="%d chunks, all without full text" % n_all)
            continue
        if a["support_basis"] == "panel_provenance_stated":
            ids = [x for x in (a["evidence_ids"] or "").split(",") if x.startswith("PMID:")]
            have = [x for x in ids if x.split(":", 1)[1] in papers]
            if not ids:
                add(scope="gene", subject_key=a["edge_id_or_node_key"],
                    subject_label=a["target_group"],
                    library=a["source_group"].split("::")[0], gene=gene, gap_kind="thin_evidence",
                    reason="review_citation_unverifiable_locally",
                    detail="the panel states a basis for this gene but carries no paper identifier, "
                           "so the statement cannot be checked against a paper on this machine",
                    evidence_status="panel provenance without a PMID",
                    suggested_next_source="a corpus row, or the paper the panel's note refers to")
                continue
            if ids and not have:
                add(scope="gene", subject_key=a["edge_id_or_node_key"],
                    subject_label=a["target_group"],
                    library=a["source_group"].split("::")[0], gene=gene, gap_kind="thin_evidence",
                    reason="review_citation_unverifiable_locally",
                    detail="the panel's citation for this gene is not in the shipped corpus, so it "
                           "cannot be checked here: %s" % ",".join(ids[:4]),
                    evidence_status="panel provenance only",
                    suggested_next_source="obtain the cited paper, or a corpus row stating it")
                continue
        pid = str(anchor.get("paper_id") or "")
        sc = stage_scope.get(pid) if pid else None
        if sc == "adult_only" and a["stage"] == "developing":
            add(scope="gene", subject_key=a["edge_id_or_node_key"], subject_label=a["target_group"],
                library=a["source_group"].split("::")[0], gene=gene, gap_kind="thin_evidence",
                reason="different_stage_not_stitchable",
                detail="the anchor paper is scoped adult_only and the node is developing; the "
                       "stage mismatch is disclosed rather than stitched",
                evidence_status="PMID %s @ %s" % (pid, anchor.get("section", "")))

    # ---- 5. edges with no marker change ---------------------------------------------------
    changed_edges = {r["edge_id_or_node_key"] for r in edge_changes}
    by_edge_reason = {}
    for r in edge_ref:
        by_edge_reason.setdefault(r["edge_key"] or r["edge_id"], []).append(r)
    for e in edges:
        refs = by_edge_reason.get(e["edge_key"], [])
        gene_refs = [r for r in refs if r.get("gene")]
        edge_refs = [r for r in refs if not r.get("gene")]
        n_changes = len([c for c in edge_changes
                         if c["edge_id_or_node_key"] == e["edge_key"]])
        if e["marker_change_status"] == "admitted_stepwise":
            # the register names every gene of the step, so the "we did not claim a loss" record is
            # as visible as the assertions themselves
            n_detect = sum(1 for r in gene_refs
                           if r["reason"] == "detection_conditions_insufficient")
            n_nostate = sum(1 for r in gene_refs if r["reason"] == "no_source_states_the_change")
            add(scope="edge", subject_key=e["edge_key"],
                subject_label="%s -> %s" % (e["precursor_label"], e["descendant_label"]),
                library="", gap_kind=("no_evidence" if n_detect or n_nostate else "thin_evidence"),
                reason=("detection_conditions_insufficient" if n_detect >= n_nostate
                        else "no_source_states_the_change"),
                detail="admitted stepwise edge: %d marker-change assertions; %d genes did not pass "
                       "the four-condition test, and %d genes present in the precursor panel and "
                       "absent from the descendant panel were NOT written as off/down (panel "
                       "absence is not a detection result)" % (n_changes, n_nostate, n_detect),
                evidence_status="%d marker-change assertions on this edge" % n_changes,
                suggested_next_source="a source that measures the precursor->descendant change")
            for r in sorted(gene_refs, key=lambda x: (x["reason"], x.get("gene", ""))):
                add(scope="gene", subject_key=e["edge_key"], subject_label=r.get("gene", ""),
                    library="", gene=r.get("gene", ""), gap_kind="no_evidence",
                    reason=r["reason"], detail=r["detail"],
                    evidence_status="edge %s" % e["edge_id"])
            continue
        reason = edge_refs[0]["reason"] if edge_refs else "marker_change_not_available"
        detail = edge_refs[0]["detail"] if edge_refs else ""
        add(scope="edge", subject_key=e["edge_key"],
            subject_label="%s -> %s" % (e["precursor_label"], e["descendant_label"]), library="",
            gap_kind="no_evidence", reason=reason,
            detail=detail + " | relation=%s directness=%s stage_crossing=%s"
                            % (e["relation_type"], e["directness"], e["stage_crossing"]),
            evidence_status="edge grade=%s; %d marker-change assertions"
                            % (e["evidence_grade"], 0),
            suggested_next_source=("the contract's own pending-assertion table expects a source that "
                                   "states the step" if e["directness"] == "direct"
                                   else "a direct (stepwise) source; the relation type here cannot "
                                        "carry a marker change by construction"))

    # ---- 6. panels refused outright, with their own words ---------------------------------
    for fname, meta in M.REFUSED_PANELS.items():
        path = M.panel_path(fname)
        n_entries, n_genes = 0, 0
        if os.path.isfile(path):
            d = json.load(open(path, encoding="utf-8"))
            n_entries = len(d.get("markers") or {})
            n_genes = sum(len(v) for v in (d.get("markers") or {}).values()
                          if isinstance(v, list))
        add(scope="panel", subject_key=fname, subject_label="hole-fill increment", library="holefill",
            gap_kind="refused_evidence", reason=meta["reason"],
            detail="%s | the panel's own scope: %s" % (fname, meta["quote"]),
            evidence_status="%d entries / %d genes shipped-but-unused" % (n_entries, n_genes),
            suggested_next_source="a candidate list built without reading the benchmark's holes")

    cols = ["scope", "subject_key", "subject_label", "library", "gene", "gap_kind", "reason",
            "detail", "evidence_status", "suggested_next_source"]
    for i, r in enumerate(rows, 1):
        r["gap_id"] = "G%05d" % i
    M.write_tsv(os.path.join(out, "GAP_REGISTER.tsv"), rows, ["gap_id"] + cols)

    summ = {
        "generated_by": "scripts/m4_gap_register.py",
        "n_gap_rows": len(rows),
        "by_kind": dict(collections.Counter(r["gap_kind"] for r in rows)),
        "by_reason": dict(collections.Counter(r["reason"] for r in rows)),
        "by_scope": dict(collections.Counter(r["scope"] for r in rows)),
        "nodes_total": len(nodes),
        "nodes_with_zero_evidence": sum(1 for r in rows if r["scope"] == "node"),
        "edges_total": len(edges),
        "edges_with_marker_change": len(changed_edges),
        "edges_with_zero_marker_change": sum(1 for r in rows if r["scope"] == "edge"),
        "reasons_declared": list(M.GAP_REASONS),
        "reasons_unused": [x for x in M.GAP_REASONS
                           if x not in {r["reason"] for r in rows}],
    }
    M.write_json(os.path.join(out, "GAP_SUMMARY.json"), summ)
    print("gap rows:", len(rows))
    print("  by kind  :", summ["by_kind"])
    print("  by scope :", summ["by_scope"])
    print("  by reason:", summ["by_reason"])
    print("  declared-but-unused reasons:", summ["reasons_unused"])
    return 0


if __name__ == "__main__":
    sys.exit(main())