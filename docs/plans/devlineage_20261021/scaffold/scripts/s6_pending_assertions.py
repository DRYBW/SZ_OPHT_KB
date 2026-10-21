#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s6_pending_assertions.py - turn the scan into three separate, non-confusable outcome tables.

  PENDING_ASSERTIONS.tsv            literature-repair proposals for the decapitated branches. Each
                                    one carries a resolvable anchor (paper id + section + chunk
                                    position + the sha256-truncated chunk identity + the sentence)
                                    and an evidence grade. **None of them enters the confirmed
                                    graph** - that is the whole point of the contract's rule that a
                                    repair proposal is not an edge.
  SCAFFOLD_EDGES_NOT_ADMITTED.tsv   edge-shaped rows the contract does not admit: the peer's corpus
                                    co-occurrence pairs, re-examined against the very chunks they
                                    cited, plus pairs whose sources point both ways.
  CORPUS_EDGE_CONFIRMATIONS.tsv     a source that asserts a pair already in the confirmed graph.
                                    Recorded as a separate class on purpose: such a source could
                                    support a grade *upgrade*, and this card does not upgrade.

The re-examination of the peer's weak rows is the part that changes a verdict: a co-occurrence row
is only weak if the chunk really only mentions both terms. Each cited chunk is therefore re-read and
its sentences are matched with the same matcher the scan used, in both directions.

Outputs: as above, plus out/SCAFFOLD_EDGES.tsv (the full edge set = confirmed + not admitted) and
         out/PENDING_SUMMARY.json
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402
import s5_corpus_scan as S5  # noqa: E402

PEND_COLS = ["pending_id", "branch_id", "target_kind", "descendant_cl_id", "descendant_label",
             "descendant_node_key", "proposed_precursor", "proposed_precursor_label",
             "proposed_precursor_status", "proposed_relation_type", "evidence_grade",
             "direction_rule", "n_chunks", "n_papers", "support_level",
             "anchor_pmid", "anchor_section", "anchor_stream_pos", "anchor_chunk_sha256",
             "anchor_quote", "source_type", "admission", "note"]


def main() -> int:
    nodes, phrases, refused, combined, norm2rec = S5.build_matcher()
    node_by_id = {n["node_id"]: n for n in nodes}
    nodes_tsv = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    confirmed = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    register = C.read_tsv(os.path.join(C.OUT, "DECAPITATED_BRANCHES.tsv"))
    raw = C.read_tsv(os.path.join(C.OUT, "CORPUS_ASSERTIONS_RAW.tsv"))
    examples = C.read_tsv(os.path.join(C.OUT, "CORPUS_ASSERTION_EXAMPLES.tsv"))
    peer_germ = [r for r in C.read_tsv(C.FIRSTPASS_GERM) if r["tier"] == "corpus_cooccurrence_weak"]
    dev3 = {r["cl_id"]: r["label"] for r in C.read_tsv(C.DEV3_TERMS)}
    node_ids_by_cl = collections.defaultdict(set)
    for n in nodes_tsv:
        if n["cl_id"]:
            node_ids_by_cl[n["cl_id"]].add(n["node_id"])

    # ---- decapitated population and the register row each class owns
    branch_of, reg_row = {}, {}
    for r in register:
        key = r["cl_id"] or f"NO_MATCH:{r['cl_label']}"
        if r["branch_kind"] in ("covered_class_without_origin",
                                "in_house_concept_without_ontology_term"):
            branch_of[key] = r["branch_id"]
            reg_row[r["branch_id"]] = r
    print(f"decapitated population: {len(branch_of)} classes; register rows: {len(register)}")

    ex_by_pair = collections.defaultdict(list)
    for e in examples:
        ex_by_pair[(e["precursor_phrase"], e["descendant_phrase"])].append(e)

    def resolve_ids(cell):
        return set(x for x in (cell or "").split(",") if x)

    pending, not_admitted, confirmations, unused = [], [], [], []
    node_by_id = {n["node_id"]: n for n in nodes_tsv}
    conf_pairs = {(e["precursor_node"].split("|")[0][3:], e["descendant_node"].split("|")[0][3:])
                  for e in confirmed}

    for r in raw:
        pid_, did_ = resolve_ids(r["precursor_ids"]), resolve_ids(r["descendant_ids"])
        targets = sorted(x for x in did_ if x in branch_of)
        is_conf = any((p, d) in conf_pairs for p in pid_ for d in did_)
        conflict = r["direction_conflict"] == "yes"
        if conflict and (targets or is_conf):
            pk, dk, ks = _pair_keys(pid_, did_, node_by_id)
            row = _rejected(r, "corpus_sources_point_both_ways",
                            "the same pair is asserted in both directions by different "
                            "sentences we hold, so neither direction is admitted",
                            node_by_id=node_by_id)
            row["precursor_node"], row["descendant_node"], row["key_status"] = pk, dk, ks
            if pk and dk:
                row["edge_key"] = C.build_edge_key(pk, dk, "trajectory_association")
                row["precursor_kind"] = node_by_id[[i for i in pid_ if i in node_by_id][0]]["kind"]
                row["descendant_kind"] = node_by_id[[i for i in did_ if i in node_by_id][0]]["kind"]
            not_admitted.append(row)
            continue
        if is_conf and not targets:
            ex = ex_by_pair.get((r["precursor_phrase"], r["descendant_phrase"]), [])
            confirmations.append({
                "precursor_phrase": r["precursor_phrase"], "descendant_phrase": r["descendant_phrase"],
                "precursor_ids": r["precursor_ids"], "descendant_ids": r["descendant_ids"],
                "n_chunks": r["n_chunks"], "n_papers": r["n_papers"],
                "example_pmid": ex[0]["pmid"] if ex else "",
                "example_sentence": ex[0]["sentence"] if ex else "",
                "status": "corroborates_an_existing_ontology_edge",
                "note": ("not an upgrade: raising the edge's grade would need a lineage-tracing "
                         "source, and this card does not move a grade on a prose assertion")})
            continue
        if not targets:
            unused.append({"precursor_phrase": r["precursor_phrase"],
                           "descendant_phrase": r["descendant_phrase"],
                           "descendant_ids": r["descendant_ids"], "n_chunks": r["n_chunks"],
                           "reason": "the descendant is not a decapitated covered class, an in-house "
                                     "concept, or a pair already in the confirmed graph"})
            continue
        for tid in targets:
            ex = ex_by_pair.get((r["precursor_phrase"], r["descendant_phrase"]), [])
            prec_ids = sorted(pid_)
            prec_status = ("scaffold_node" if any(x in node_by_id for x in prec_ids)
                           else ("registered_candidate_term" if any(x in dev3 for x in prec_ids)
                                 else "no_ontology_term_on_our_side"))
            prec_label = (node_by_id[prec_ids[0]]["cl_label"] if prec_ids and prec_ids[0] in node_by_id
                          else (dev3.get(prec_ids[0], r["precursor_phrase"]) if prec_ids
                                else r["precursor_phrase"]))
            anchor_ids = {a["cl_id"] for a in json.load(
                open(C.ONT_NAV, encoding="utf-8"))["germ_layer_anchors"] if a["cl_id"]}
            rel = ("ancestral_origin" if (set(prec_ids) & anchor_ids)
                   else ("direct_lineage" if prec_status != "no_ontology_term_on_our_side"
                         else "trajectory_association"))
            pending.append({
                "pending_id": "", "branch_id": branch_of[tid],
                "target_kind": reg_row[branch_of[tid]]["branch_kind"],
                "descendant_cl_id": tid, "descendant_label": reg_row[branch_of[tid]]["cl_label"],
                "descendant_node_key": (node_by_id[tid]["node_key"] if tid in node_by_id else ""),
                "proposed_precursor": ",".join(prec_ids) or r["precursor_phrase"],
                "proposed_precursor_label": prec_label,
                "proposed_precursor_status": prec_status,
                "proposed_relation_type": rel, "evidence_grade": "identity_conversion_not_direct",
                "direction_rule": r["direction_rules"], "n_chunks": r["n_chunks"],
                "n_papers": r["n_papers"],
                "support_level": ("multi_chunk" if int(r["n_chunks"]) > 2 else "single_or_few_chunks"),
                "anchor_pmid": ex[0]["pmid"] if ex else "",
                "anchor_section": ex[0]["section"] if ex else "",
                "anchor_stream_pos": ex[0]["stream_pos"] if ex else "",
                "anchor_chunk_sha256": ex[0]["chunk_sha256"] if ex else "",
                "anchor_quote": ex[0]["sentence"] if ex else "",
                "source_type": "paper_we_hold",
                "admission": "pending_repair_proposal",
                "note": ("a paper asserts the direction and the identity conversion; it is not "
                         "lineage tracing, so the pair stays out of the confirmed graph")})

    # ---- the peer's weak rows, re-examined against the chunks they cited
    dump = C.read_tsv(os.path.join(C.OUT, "PEER_WEAK_ROW_CHUNKS.tsv"))
    by_class = collections.defaultdict(list)
    for d in dump:
        by_class[d["peer_row_class_cl"]].append(d)
    peer_recheck, n_asserted = [], 0
    for r in peer_germ:
        cid = r["cl_id"]
        layer_cl = r["layer_cl"]
        chunks = by_class.get(cid, [])
        found = []
        for d in chunks:
            if d["carries_a_lineage_verb"] != "yes":
                continue
            for sent in S5.SENT_SPLIT.split(d["text"]):
                if not S5.ANY_VERB.search(sent):
                    continue
                hits = S5.match_sentence(sent, combined, norm2rec)
                if not hits:
                    continue
                ids = {x for h in hits for x in h[2]["ids"]}
                if cid in ids and layer_cl in ids:
                    found.append({"pmid": d["pmid"], "section": d["section"],
                                  "stream_pos": d["stream_pos"], "sentence": sent[:400]})
        verdict = ("the_cited_chunks_assert_a_relation" if found
                   else "the_cited_chunks_only_co_mention_the_two_terms")
        if found:
            n_asserted += 1
            for f in found[:1]:
                pending.append({
                    "pending_id": "", "branch_id": branch_of.get(cid, ""),
                    "target_kind": reg_row.get(branch_of.get(cid, ""), {}).get("branch_kind", ""),
                    "descendant_cl_id": cid, "descendant_label": r["cl_label"],
                    "descendant_node_key": (node_by_id[cid]["node_key"] if cid in node_by_id else ""),
                    "proposed_precursor": layer_cl,
                    "proposed_precursor_label": r["layer_label"] or r["layer_key"],
                    "proposed_precursor_status": "scaffold_node",
                    "proposed_relation_type": "ancestral_origin",
                    "evidence_grade": "identity_conversion_not_direct",
                    "direction_rule": "re_examined_peer_locator", "n_chunks": r["corpus_n_chunks"],
                    "n_papers": r["corpus_n_papers"], "support_level": "peer_tier_row_reclassified",
                    "anchor_pmid": f["pmid"], "anchor_section": f["section"],
                    "anchor_stream_pos": f["stream_pos"], "anchor_chunk_sha256": "",
                    "anchor_quote": f["sentence"], "source_type": "paper_we_hold",
                    "admission": "pending_repair_proposal",
                    "note": ("the peer recorded this pair as weak co-occurrence; re-reading the very "
                             "chunks it cited shows a sentence that asserts the relation, so it is "
                             "carried here as a proposal, not into the graph")})
        else:
            layer_keyed = node_by_id.get(layer_cl, {}).get("node_key", "")
            class_keyed = node_by_id.get(cid, {}).get("node_key", "")
            not_admitted.append({
                "edge_id": "", "edge_key": (C.build_edge_key(layer_keyed, class_keyed,
                                                             "trajectory_association")
                                            if layer_keyed and class_keyed else ""),
                "precursor_node": layer_keyed, "descendant_node": class_keyed,
                "key_status": ("contract_keys_present" if layer_keyed and class_keyed
                               else "endpoint_not_an_enumerated_node"),
                "relation_type": "trajectory_association", "directness": "not_a_step",
                "evidence_ids": "corpus:" + ",".join(sorted({d["pmid"] for d in chunks})[:3]),
                "evidence_grade": "trajectory_only", "conflict_status": "none",
                "marker_change_ids": "", "derivation": "peer_artefact_re_examined",
                "derivation_rule": "RE-EXAMINE-1",
                "derivation_note": verdict.replace("_", " "),
                "chain_precursor_to_descendant": f"{layer_cl} ~ {cid}",
                "steps": "", "obo_lines": "", "source_relation": "corpus_cooccurrence",
                "source_relation_direction": "none_asserted",
                "grade_basis": "co_mention_only: no sentence in the cited chunks asserts a relation",
                "admission": "rejected",
                "admission_rule": "the contract does not admit co-occurrence as a lineage edge",
                "precursor_label": r["layer_label"] or r["layer_key"],
                "descendant_label": r["cl_label"],
                "precursor_kind": "origin_anchor", "descendant_kind": "library_class",
                "anchor_kind": r["layer_key"], "first_pass_edge_ids": r["node_id"] and "",
                "notes": (f"peer row: {r['corpus_n_chunks']} chunks / {r['corpus_n_papers']} papers; "
                          f"{len(chunks)} cited chunk(s) re-read; verdict: {verdict}")})
        peer_recheck.append({"class_cl": cid, "class_label": r["cl_label"],
                             "peer_layer_key": r["layer_key"], "peer_n_chunks": r["corpus_n_chunks"],
                             "chunks_re_read": len(chunks),
                             "chunks_carrying_a_lineage_verb":
                                 sum(1 for d in chunks if d["carries_a_lineage_verb"] == "yes"),
                             "verdict": verdict,
                             "asserted_pair_example": (found[0]["sentence"] if found else ""),
                             "asserted_pmid": (found[0]["pmid"] if found else "")})
    C.write_tsv(os.path.join(C.OUT, "PEER_WEAK_ROW_RECHECK.tsv"), peer_recheck,
                ["class_cl", "class_label", "peer_layer_key", "peer_n_chunks", "chunks_re_read",
                 "chunks_carrying_a_lineage_verb", "verdict", "asserted_pair_example",
                 "asserted_pmid"])
    print(f"peer weak rows re-examined: {len(peer_recheck)}; asserting a relation: {n_asserted}")

    # ---- the textbook layer, same treatment
    tb = [json.loads(l) for l in open(C.TEXTBOOK, encoding="utf-8")]
    tb_hits = []
    for item in tb:
        blob = " ".join(str(item.get(k) or "") for k in ("term", "topic", "quote"))
        for sent in S5.SENT_SPLIT.split(blob):
            if not S5.ANY_VERB.search(sent):
                continue
            hits = S5.match_sentence(sent, combined, norm2rec)
            ids = {x for h in hits for x in h[2]["ids"]}
            targets = sorted(x for x in ids if x in branch_of)
            if len(hits) >= 2 and targets:
                tb_hits.append({"item_id": item["item_id"], "book": item["book"],
                                "page": item["page"], "page_anchor": item["page_anchor"],
                                "topic": item["topic"], "quote": item["quote"][:300],
                                "sentence": sent[:300], "matches": ",".join(sorted(ids)),
                                "targets": ",".join(targets)})
    if tb_hits:
        for h in tb_hits:
            for tid in h["targets"].split(","):
                pending.append({
                    "pending_id": "", "branch_id": branch_of.get(tid, ""),
                    "target_kind": reg_row.get(branch_of.get(tid, ""), {}).get("branch_kind", ""),
                    "descendant_cl_id": tid,
                    "descendant_label": reg_row.get(branch_of.get(tid, ""), {}).get("cl_label", ""),
                    "descendant_node_key": (node_by_id[tid]["node_key"] if tid in node_by_id else ""),
                    "proposed_precursor": h["matches"], "proposed_precursor_label": h["matches"],
                    "proposed_precursor_status": "see_matches_column",
                    "proposed_relation_type": "trajectory_association",
                    "evidence_grade": "textbook_or_review_distant_origin",
                    "direction_rule": "textbook_item_sentence", "n_chunks": 1, "n_papers": 1,
                    "support_level": "textbook_item", "anchor_pmid": "",
                    "anchor_section": f"{h['book']} {h['page_anchor']}",
                    "anchor_stream_pos": "", "anchor_chunk_sha256": "",
                    "anchor_quote": h["sentence"], "source_type": "textbook_layer",
                    "admission": "pending_repair_proposal",
                    "note": "textbook/review-grade origin claim; never an edge"})
    C.write_tsv(os.path.join(C.OUT, "TEXTBOOK_REPAIR_CANDIDATES.tsv"), tb_hits,
                ["item_id", "book", "page", "page_anchor", "topic", "quote", "sentence", "matches",
                 "targets"])

    for i, r in enumerate(sorted(pending, key=lambda x: (x["branch_id"], x["descendant_cl_id"],
                                                         x["proposed_precursor"])), 1):
        r["pending_id"] = f"PA{i:04d}"
    C.write_tsv(os.path.join(C.OUT, "PENDING_ASSERTIONS.tsv"), pending, PEND_COLS)
    C.write_tsv(os.path.join(C.OUT, "CORPUS_PAIRS_UNUSED.tsv"), unused,
                ["precursor_phrase", "descendant_phrase", "descendant_ids", "n_chunks", "reason"])
    C.write_tsv(os.path.join(C.OUT, "CORPUS_EDGE_CONFIRMATIONS.tsv"), confirmations,
                ["precursor_phrase", "descendant_phrase", "precursor_ids", "descendant_ids",
                 "n_chunks", "n_papers", "example_pmid", "example_sentence", "status", "note"])

    # ---- not-admitted rows get their own identifiers so the merge stays traceable
    allrows = list(confirmed)
    for i, r in enumerate(sorted(not_admitted, key=lambda x: (x["descendant_label"],
                                                              x["precursor_label"])), 1):
        r["edge_id"] = f"R{i:03d}"
        allrows.append(r)
    cols = list(confirmed[0].keys()) + ["key_status"]
    C.write_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_NOT_ADMITTED.tsv"),
                [r for r in allrows if r["edge_id"].startswith("R")], cols)
    C.write_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES.tsv"), allrows, cols)

    summ = {"generated_by": "scripts/s6_pending_assertions.py",
            "pending_assertions": len(pending),
            "pending_by_target_kind": C.counts(r["target_kind"] for r in pending),
            "pending_by_grade": C.counts(r["evidence_grade"] for r in pending),
            "pending_with_a_resolvable_paper_anchor":
                sum(1 for r in pending if r["anchor_pmid"] and r["anchor_quote"]),
            "pending_from_the_textbook_layer": sum(1 for r in pending
                                                   if r["source_type"] == "textbook_layer"),
            "not_admitted_rows": len(not_admitted),
            "not_admitted_by_reason": C.counts(r["derivation_rule"] for r in not_admitted),
            "confirmed_edges": len(confirmed),
            "full_edge_set_rows": len(allrows),
            "peer_weak_rows_asserting_a_relation": n_asserted,
            "peer_weak_rows_co_mention_only": len(peer_recheck) - n_asserted,
            "corpus_pairs_corroborating_an_existing_edge": len(confirmations),
            "corpus_pairs_unused": len(unused),
            "textbook_items_with_a_developmental_assertion_for_a_decapitated_branch": len(tb_hits),
            "outputs": {"pending": os.path.join(C.OUT, "PENDING_ASSERTIONS.tsv"),
                        "not_admitted": os.path.join(C.OUT, "SCAFFOLD_EDGES_NOT_ADMITTED.tsv"),
                        "full_edge_set": os.path.join(C.OUT, "SCAFFOLD_EDGES.tsv"),
                        "peer_recheck": os.path.join(C.OUT, "PEER_WEAK_ROW_RECHECK.tsv")}}
    C.write_json(os.path.join(C.OUT, "PENDING_SUMMARY.json"), summ)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


def _pair_keys(prec_ids, desc_ids, node_by_id):
    """Node keys for a rejected row when both ends really are nodes in this enumeration.

    A rejected row must still be readable as a pair, so wherever the two phrases resolve to
    enumerated nodes the row carries the contract keys; where an endpoint is only a phrase (a term we
    do not enumerate), the row says so in key_status instead of inventing a key.
    """
    pk = next((node_by_id[i]["node_key"] for i in prec_ids if i in node_by_id), "")
    dk = next((node_by_id[i]["node_key"] for i in desc_ids if i in node_by_id), "")
    if pk and dk:
        return pk, dk, "contract_keys_present"
    return "", "", ("precursor_phrase_is_not_an_enumerated_node" if not pk
                    else "descendant_phrase_is_not_an_enumerated_node")


def _rejected(r, rule, note, node_by_id=None) -> dict:
    return {"edge_id": "", "edge_key": "", "precursor_node": "", "descendant_node": "",
            "key_status": "",
            "relation_type": "trajectory_association", "directness": "not_a_step",
            "evidence_ids": "corpus:" + (r["example_pmids"] or ""),
            "evidence_grade": "trajectory_only", "conflict_status": "conflicting_sources",
            "marker_change_ids": "", "derivation": "corpus_scan_direction_conflict",
            "derivation_rule": rule, "derivation_note": note,
            "chain_precursor_to_descendant": f"{r['precursor_phrase']} ~ {r['descendant_phrase']}",
            "steps": "", "obo_lines": "", "source_relation": "corpus_assertion",
            "source_relation_direction": "both_directions_asserted",
            "grade_basis": "not admitted: the sources disagree on the direction",
            "admission": "rejected",
            "admission_rule": "unexplained conflict is not admitted as a confirmed edge",
            "precursor_label": r["precursor_phrase"], "descendant_label": r["descendant_phrase"],
            "precursor_kind": "", "descendant_kind": "", "anchor_kind": "",
            "first_pass_edge_ids": "",
            "notes": f"{r['n_chunks']} chunks / {r['n_papers']} papers assert the pair both ways"}


if __name__ == "__main__":
    sys.exit(main())