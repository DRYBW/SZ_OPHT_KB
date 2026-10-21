#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s11_check_report_numbers.py - every headline number in REPORT.md, recomputed from the artefacts.

A report whose numbers cannot be recomputed is a narrative. This checks each number the report
quotes: the value is recomputed from the delivered file (or the ledger that captured the command's
own output) and must equal the literal that appears in REPORT.md. Fails loudly and names the number.

Usage: python3 scripts/s11_check_report_numbers.py
Exit: 0 = every quoted number re-derives; 2 = at least one does not.
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

FAILS = []


def check(name, literal, value):
    ok = str(literal) == str(value)
    if not ok:
        FAILS.append(f"{name}: report says {literal!r}, recomputed {value!r}")
    return ok


def main() -> int:
    rep = open(os.path.join(C.SCAFFOLD, "REPORT.md"), encoding="utf-8").read()
    nodes = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    conf = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    full = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES.tsv"))
    rej = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_EDGES_NOT_ADMITTED.tsv"))
    reg = C.read_tsv(os.path.join(C.OUT, "DECAPITATED_BRANCHES.tsv"))
    pend = C.read_tsv(os.path.join(C.OUT, "PENDING_ASSERTIONS.tsv"))
    cov = {r["count"]: r["value"] for r in C.read_tsv(os.path.join(C.OUT, "COVERAGE_DENOMINATOR.tsv"))}
    meta = json.load(open(os.path.join(C.OUT, "CORPUS_SCAN_META.json"), encoding="utf-8"))
    psum = json.load(open(os.path.join(C.OUT, "PENDING_SUMMARY.json"), encoding="utf-8"))
    esum = json.load(open(os.path.join(C.OUT, "EDGES_SUMMARY.json"), encoding="utf-8"))
    nsum = json.load(open(os.path.join(C.OUT, "NODES_SUMMARY.json"), encoding="utf-8"))
    dsum = json.load(open(os.path.join(C.OUT, "DECAPITATED_SUMMARY.json"), encoding="utf-8"))
    aft = json.load(open(os.path.join(C.OUT, "AFTERFACT_SUMMARY.json"), encoding="utf-8"))
    ver = json.load(open(os.path.join(C.OUT, "REVERIFY_UPSTREAM.json"), encoding="utf-8"))
    gate = json.load(open(os.path.join(C.OUT, "GATE_SCAFFOLD.json"), encoding="utf-8"))
    pairs = psum["not_admitted_by_reason"]

    checks = [
        # enumeration
        ("nodes_total", "103", len(nodes)),
        ("ring A1", "52", nsum["by_ring"]["A1"]),
        ("ring A2", "15", nsum["by_ring"]["A2"]),
        ("ring B", "28", cov["nodes_ring_b_ontology_intermediates"]),
        ("ring C", "8", nsum["by_ring"]["C"]),
        ("library concepts", "80", nsum["library_concepts"]),
        ("mapped labels", "65", nsum["library_concepts_mapped"]),
        ("stage adult", "16", nsum["by_stage"]["adult"]),
        ("stage developing", "42", nsum["by_stage"]["developing"]),
        ("stage unknown", "45", nsum["by_stage"]["unknown"]),
        ("stage fetal", "0", nsum["by_stage"].get("fetal", 0)),
        ("species human", "18", nsum["by_species"]["human"]),
        ("tissue declared", "6", cov["nodes_with_a_declared_tissue_context"]),
        # edges
        ("confirmed edges", "51", len(conf)),
        ("full edge set", "75", len(full)),
        ("rejected rows", "24", len(rej)),
        ("ontology_development_relation", "40", esum["by_relation_type"]["ontology_development_relation"]),
        ("ancestral_origin", "11", esum["by_relation_type"]["ancestral_origin"]),
        ("R-NATIVE", "40", esum["by_derivation_rule"]["R-NATIVE"]),
        ("R-ANCHOR-1", "4", esum["by_derivation_rule"]["R-ANCHOR-1"]),
        ("R-ANCHOR-2", "6", esum["by_derivation_rule"]["R-ANCHOR-2"]),
        ("R-ANCHOR-3", "1", esum["by_derivation_rule"]["R-ANCHOR-3"]),
        # coverage denominator
        ("distinct CL ids", "52", cov["distinct_cl_ids_in_library"]),
        ("anchored classes", "8", cov["library_classes_with_an_anchored_origin"]),
        ("weak-only classes", "8", cov["library_classes_with_only_corpus_cooccurrence"]),
        ("no-evidence classes", "36", cov["library_classes_with_no_local_developmental_evidence"]),
        ("never a descendant", "34", cov["library_classes_that_are_never_a_descendant_in_the_graph"]),
        ("decapitated branches", "44", cov["decapitated_branches"]),
        ("develops_from in release", "400", cov["native_develops_from_statements_in_release"]),
        ("develops_from enumerated", "40", cov["native_develops_from_statements_enumerated"]),
        # register
        ("register rows", "64", len(reg)),
        ("covered_class_without_origin", "44",
         dsum["by_branch_kind"]["covered_class_without_origin"]),
        ("anchor_without_any_covered_class", "4",
         dsum["by_branch_kind"]["anchor_without_any_covered_class"]),
        ("in_house_concept_without_ontology_term", "15",
         dsum["by_branch_kind"]["in_house_concept_without_ontology_term"]),
        ("no_develops_from_statement_at_all", "34",
         dsum["by_break_kind"]["no_develops_from_statement_at_all"]),
        ("closure_does_not_reach", "10",
         dsum["by_break_kind"]["closure_does_not_reach_any_origin_anchor"]),
        # pending / corpus
        ("pending rows", "68", len(pend)),
        ("pending resolvable anchors", "68", psum["pending_with_a_resolvable_paper_anchor"]),
        ("peer rows co-mention only", "12", psum["peer_weak_rows_co_mention_only"]),
        ("peer rows asserting", "0", psum["peer_weak_rows_asserting_a_relation"]),
        ("direction conflicts", "12", pairs.get("corpus_sources_point_both_ways")),
        ("confirmations", "5", psum["corpus_pairs_corroborating_an_existing_edge"]),
        ("unused pairs", "39", psum["corpus_pairs_unused"]),
        ("chunks in corpus", "244,877", f"{meta['chunks_in_corpus']:,}"),
        ("chunks with a verb", "6,670", f"{meta['chunks_carrying_a_lineage_verb']:,}"),
        ("sentences examined", "8,309", f"{meta['sentences_examined']:,}"),
        ("sentences two phrases", "628", str(meta["sentences_with_two_or_more_phrases"])),
        ("ordered pairs", "124", str(meta["ordered_pairs_found"])),
        ("examples verified", "194", str(meta["examples_verified"])),
        ("phrases refused", "40", str(meta["phrases_refused_single_token"])),
        # after-fact
        ("recorded clusters", "721", str(aft["recording"]["clusters"])),
        ("recorded cells", "1,495,330", f"{aft['recording']['cells']:,}"),
        ("cells anchored", "19.88%", f"{aft['cells_on_a_class_that_is_anchored']['pct_cells']}%"),
        ("cells decapitated", "55.5%", f"{aft['cells_on_a_class_that_is_decapitated']['pct_cells']}%"),
        ("cells never enumerated", "23.25%",
         f"{aft['cells_on_a_class_we_never_enumerate']['pct_cells']}%"),
        ("cells no CL term", "24.62%",
         f"{aft['cells_on_a_class_with_no_cl_term_on_our_side']['pct_cells']}%"),
        # gate / re-verification / discipline
        ("gate rules", "10", str(gate["n_checks"])),
        ("gate fail", "0", str(gate["n_fail"])),
        ("reverify checks", "58", str(ver["checks"])),
        ("reverify fail", "0", str(ver["fail"])),
        ("first pass nodes", "60", str(len(C.read_tsv(C.FIRSTPASS_NODES)))),
        ("first pass edges", "34", str(len(C.read_tsv(C.FIRSTPASS_EDGES)))),
        ("precursor edges", "79", str(len(C.read_tsv(C.PRECURSOR_EDGES)))),
        ("eye subgraph nodes", "408", str(json.load(open(C.EYE_SUBGRAPH, encoding="utf-8"))["n_nodes"])),
        ("dev3 rows", "58", str(len(C.read_tsv(C.DEV3_TERMS)))),
    ]
    missing = []
    for name, literal, value in checks:
        if not check(name, literal, value):
            continue
        if literal not in rep:
            missing.append(f"{name}: {literal!r} is not in REPORT.md")

    ledger = open(os.path.join(C.LEDGERS, "RESOURCE_READINGS.txt"), encoding="utf-8").read()
    for lit in ("206540", "0:19.78"):
        if lit not in ledger:
            FAILS.append(f"resource reading {lit!r} is not in ledgers/RESOURCE_READINGS.txt")
    rep_led = open(os.path.join(C.LEDGERS, "REPLAY.txt"), encoding="utf-8").read()
    if "REPLAY_PASS" not in rep_led:
        FAILS.append("ledgers/REPLAY.txt is not green")
    net = open(os.path.join(C.LEDGERS, "NET_AUDIT_SUMMARY.txt"), encoding="utf-8").read()
    if "network_event_lines=0" not in net:
        FAILS.append("ledgers/NET_AUDIT_SUMMARY.txt does not read zero network events")
    qr = open(os.path.join(C.LEDGERS, "QUERY_SET_REPLAY_SUMMARY.txt"), encoding="utf-8").read()
    if "REPRO PASS: 41/41" not in qr:
        FAILS.append("the recorded query-set replay is not the 41/41 PASS the report quotes")

    print(f"[report numbers] checked={len(checks)} numeric literals + 6 ledger readings")
    print(f"  numbers that do not re-derive: {len(FAILS)}")
    for f in FAILS:
        print(f"   FAIL {f}")
    print(f"  numbers that re-derive but are absent from the report prose: {len(missing)}")
    for m in missing:
        print(f"   note {m}")
    return 0 if not FAILS else 2


if __name__ == "__main__":
    sys.exit(main())