#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s8_gate_scaffold.py - the machine check on the scaffold. Fail-closed (rc 0 = PASS, rc 2 = FAIL).

Rules required by the card, plus the pins this card needs to stand on:

  G1  KEY_PARSE          every node key parses against the contract grammar; every edge key parses
                         and agrees with the row's own precursor/descendant fields; ids unique
  G2  REL_VOCAB          every relation type is one of the contract's four; no confirmed row is a
                         trajectory-only row
  G3  STAGE_AXIS         every stage is from the four-level axis; every `adult` node names a
                         baseline that really declares an adult stage (re-read from disk); every
                         `developing` node re-derives from the ontology text or from a library
                         label; nothing defaults to adult
  G4  ANCHOR_RESOLVABLE  every confirmed edge's citations re-walk against the ontology file; every
                         derived row names its rule; every rejected row's corpus locator resolves to
                         a paper this machine ships
  G5  NO_TYPE_UPGRADE    no ancestral_origin or trajectory_association edge carries
                         direct_lineage_support
  G6  ACYCLIC_CONTEXT    no cycle inside one context's forward-differentiation subgraph, and no
                         self edge anywhere
  G7  CONFIRMED_EQ_ADMITTED  {admission=confirmed} == {grade in the admitted set}, and the
                         confirmed-view file equals the confirmed subset of the full edge set
  G8  NO_EVAL_LEAK       the scaffold artefacts carry no reference to the evaluation recording
                         (the file that reads it is named and excluded)
  G9  UPSTREAM_PIN       the consumed artefacts are byte-identical to the hashes this card recorded
  G10 REPLAY_MANIFEST    every artefact matches the manifest, the replay ledger is green, and no
                         pending repair proposal is present in the confirmed edge set

Usage: python3 scripts/s8_gate_scaffold.py [--json out/GATE_SCAFFOLD.json]
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402
from ont_nav import Ontology  # noqa: E402

PINNED_ONTO_NAV_SHA = "4eac5092a16a48a08f72b24e56665c9740b5203ef18259260da9ea005574c456"
PINNED_OBO_SHA = "7e19b4aef8e7fe7720b0c4474c6a5b8713c904ea9ab7b7d5d96f2cb28b8fc51f"
RULE_VOCAB = {"R-NATIVE", "R-ANCHOR-1", "R-ANCHOR-2", "R-ANCHOR-3", "RE-EXAMINE-1"}
# the only files allowed to mention the evaluation recording, each with its reason
LEAK_EXEMPT = {
    "AFTERFACT_RECORDING_COVERAGE.tsv": "the asymmetric coverage reading, by design the only one",
    "AFTERFACT_SUMMARY.json": "the asymmetric coverage reading, by design the only one",
}
ARTEFACTS = ["SCAFFOLD_NODES.tsv", "SCAFFOLD_EDGES.tsv", "SCAFFOLD_EDGES_CONFIRMED.tsv",
             "SCAFFOLD_EDGES_NOT_ADMITTED.tsv", "PENDING_ASSERTIONS.tsv",
             "DECAPITATED_BRANCHES.tsv", "COVERAGE_DENOMINATOR.tsv", "ANCHOR_COVERAGE.tsv",
             "RPC_AXIS.tsv", "PEER_WEAK_ROW_RECHECK.tsv", "CORPUS_ASSERTIONS_RAW.tsv",
             "CORPUS_ASSERTION_EXAMPLES.tsv", "CORPUS_ASSERTION_ANCHORS.tsv",
             "TEXTBOOK_REPAIR_CANDIDATES.tsv", "NODES_SUMMARY.json", "EDGES_SUMMARY.json",
             "PENDING_SUMMARY.json", "DECAPITATED_SUMMARY.json", "COVERAGE_DENOMINATOR.json",
             "CORPUS_SCAN_META.json", "FIRSTPASS_RECONCILIATION.tsv", "CORPUS_PAIRS_UNUSED.tsv",
             "CORPUS_EDGE_CONFIRMATIONS.tsv", "PEER_WEAK_ROW_CHUNKS.tsv"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def read(path):
    return C.read_tsv(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(C.OUT, "GATE_SCAFFOLD.json"))
    a = ap.parse_args()
    checks = []

    def rec(code, ok, detail, offenders=None):
        checks.append({"code": code, "status": "PASS" if ok else "FAIL", "detail": detail,
                       "n_offenders": len(offenders or []), "offenders": (offenders or [])[:20]})

    ont = Ontology(C.ONT_OBO)
    nav = json.load(open(C.ONT_NAV, encoding="utf-8"))
    anchors = {x["cl_id"]: x["key"] for x in nav["germ_layer_anchors"] if x["cl_id"]}
    nodes = read(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    conf = read(os.path.join(C.OUT, "SCAFFOLD_EDGES_CONFIRMED.tsv"))
    full = read(os.path.join(C.OUT, "SCAFFOLD_EDGES.tsv"))
    pending = read(os.path.join(C.OUT, "PENDING_ASSERTIONS.tsv"))
    register = read(os.path.join(C.OUT, "DECAPITATED_BRANCHES.tsv"))
    node_keys = {n["node_key"] for n in nodes}

    # ---- G1
    bad1 = []
    for n in nodes:
        try:
            fields = C.parse_node_key(n["node_key"])
        except ValueError as e:
            bad1.append(f"{n['node_id']}: {e}")
            continue
        if fields["st"] != n["stage"]:
            bad1.append(f"{n['node_id']}: key stage {fields['st']} != stage column {n['stage']}")
        if n["cl_id"] and fields["cl"] != n["cl_id"]:
            bad1.append(f"{n['node_id']}: key cl {fields['cl']} != cl_id column")
        if not n["cl_id"] and not fields["cl"].startswith("NO_MATCH:"):
            bad1.append(f"{n['node_id']}: a concept without a CL id must use the NO_MATCH prefix")
    n_keyless = 0
    for e in full:
        if not e["edge_key"]:
            # a rejected row about a phrase we do not enumerate may have no contract key, but it
            # must say so and it must be a rejected row - never a confirmed edge
            ks = e.get("key_status", "")
            if e["admission"] == "rejected" and ks and ks != "contract_keys_present":
                n_keyless += 1
            else:
                bad1.append(f"{e['edge_id']}: no edge key and no declared reason")
            continue
        try:
            k = C.parse_edge_key(e["edge_key"])
        except ValueError as ex:
            bad1.append(f"{e['edge_id']}: {ex}")
            continue
        if k["precursor"] != e["precursor_node"] or k["descendant"] != e["descendant_node"]:
            bad1.append(f"{e['edge_id']}: key endpoints disagree with the columns")
        if k["rel"] != e["relation_type"]:
            bad1.append(f"{e['edge_id']}: key relation {k['rel']} != column {e['relation_type']}")
        for side in ("precursor_node", "descendant_node"):
            if e[side] and e[side] not in node_keys:
                bad1.append(f"{e['edge_id']}: {side} is not a node key")
    for e in conf:
        try:
            k = C.parse_edge_key(e["edge_key"])
            if k["precursor"] not in node_keys or k["descendant"] not in node_keys:
                bad1.append(f"{e['edge_id']}: confirmed edge endpoint missing from the node set")
        except ValueError as ex:
            bad1.append(f"{e['edge_id']}: {ex}")
    dup = [k for k, v in collections.Counter(n["node_key"] for n in nodes).items() if v > 1]
    if dup:
        bad1.append(f"duplicate node keys: {dup[:5]}")
    dup = [k for k, v in collections.Counter(e["edge_id"] for e in full).items() if v > 1]
    if dup:
        bad1.append(f"duplicate edge ids: {dup[:5]}")
    rec("G1 KEY_PARSE", not bad1,
        f"node keys={len(nodes)} parsed, edge keys={len(full) - n_keyless} parsed, "
        f"rejected rows with a declared key reason={n_keyless}, confirmed={len(conf)}", bad1)

    # ---- G2
    bad2 = []
    for e in full:
        if e["relation_type"] not in C.REL_TYPES:
            bad2.append(f"{e['edge_id']}: relation {e['relation_type']!r} outside the vocabulary")
        if e["evidence_grade"] not in C.GRADES:
            bad2.append(f"{e['edge_id']}: grade {e['evidence_grade']!r} outside the vocabulary")
        if e["admission"] not in C.ADMISSION:
            bad2.append(f"{e['edge_id']}: admission {e['admission']!r} unknown")
    for e in conf:
        if e["relation_type"] == "trajectory_association":
            bad2.append(f"{e['edge_id']}: a trajectory-only row may not be confirmed")
    rec("G2 REL_VOCAB", not bad2,
        f"rows={len(full)} relation_types={sorted({e['relation_type'] for e in full})}", bad2)

    # ---- G3
    bad3 = []
    label_of = {n["node_id"]: n["cl_label"] for n in nodes}
    our_of = {n["node_id"]: n["our_labels"] for n in nodes}
    stage_cnt = collections.Counter()
    for n in nodes:
        stage_cnt[n["stage"]] += 1
        if n["stage"] not in C.STAGES:
            bad3.append(f"{n['node_id']}: stage {n['stage']!r} outside the four-level axis")
            continue
        b = n["stage_basis"]
        if n["stage"] == "adult":
            if not b.startswith("baseline:"):
                bad3.append(f"{n['node_id']}: adult with no baseline basis ({b})")
                continue
            fn = b[len("baseline:"):].split("#")[0]
            p = os.path.join(C.BASELINE_DIR, fn)
            if not os.path.isfile(p):
                bad3.append(f"{n['node_id']}: adult basis names a missing baseline {fn}")
                continue
            d = json.load(open(p, encoding="utf-8"))
            st = str(d.get("development_stage") or d.get("organism_stage") or "")
            if not st.lower().startswith("adult"):
                bad3.append(f"{n['node_id']}: baseline {fn} declares stage {st!r}, not adult")
        elif n["stage"] == "developing":
            if "anchor_role=" in b:
                if anchors.get(n["cl_id"]) != b.split("anchor_role=")[-1]:
                    bad3.append(f"{n['node_id']}: anchor role does not re-derive")
            elif b.startswith("ontology:"):
                cid = n["cl_id"]
                blob = f"{ont.label(cid) or ''} {ont.terms[cid].definition or ''}" \
                    if cid in ont.terms else ""
                want = b.split("#dev_word=")[-1]
                if C.dev_word_in(blob) != want:
                    bad3.append(f"{n['node_id']}: developing basis {want!r} does not re-derive "
                                f"(recomputed {C.dev_word_in(blob)!r})")
            elif b.startswith("label_dev_word:"):
                want = b.split(":", 1)[1]
                if C.dev_word_in_label(our_of[n["node_id"]]) != want:
                    bad3.append(f"{n['node_id']}: label dev word {want!r} does not re-derive")
            else:
                bad3.append(f"{n['node_id']}: developing with an unrecognised basis {b}")
        elif n["stage"] == "unknown":
            if b not in ("no_local_stage_declaration", "not_in_our_libraries_no_es_declared",
                         "no_baseline_declares_this_class"):
                bad3.append(f"{n['node_id']}: unknown stage carrying a positive basis {b}")
    rec("G3 STAGE_AXIS", not bad3,
        f"stages={dict(stage_cnt)} adult_with_a_verified_basis="
        f"{stage_cnt['adult']} unknown_never_defaulted_to_adult=yes", bad3)

    # ---- G4
    bad4 = []
    paper_ids = set()
    with open(C.PAPERS, encoding="utf-8") as f:
        for line in f:
            try:
                paper_ids.add(json.loads(line)["paper_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    for e in conf:
        if e["derivation_rule"] not in RULE_VOCAB:
            bad4.append(f"{e['edge_id']}: derivation rule {e['derivation_rule']!r} unknown")
        lines = {int(x) for x in e["obo_lines"].split(",") if x.strip()}
        if not lines:
            bad4.append(f"{e['edge_id']}: confirmed edge with no ontology line")
            continue
        chain = [x.strip() for x in e["chain_precursor_to_descendant"].split("->")]
        want = set()
        ok_chain = len(chain) >= 2
        for u, v in zip(chain, chain[1:]):          # u is the precursor/ancestor of v
            if u not in ont.terms or v not in ont.terms:
                ok_chain = False
                break
            want |= {ln for t, ln in ont.terms[v].dev_lines if t == u}
            want |= {ln for t, ln in ont.terms[v].is_a_lines if t == u}
        for ln in lines:
            if ln not in want:
                bad4.append(f"{e['edge_id']}: cited line {ln} is not a hop of the recorded chain")
        if not ok_chain:
            bad4.append(f"{e['edge_id']}: chain does not re-walk: {e['chain_precursor_to_descendant'][:90]}")
        if e["derivation"] == "derived_rule" and not e["derivation_note"]:
            bad4.append(f"{e['edge_id']}: derived rule with no explanation in the row")
    n_rej_papers = 0
    for e in full:
        if e["admission"] == "rejected":
            pids = [x.split(":")[-1] for x in e["evidence_ids"].split(",") if ":" in x]
            pids = [p for p in pids if p]
            if not pids or not any(p in paper_ids for p in pids):
                bad4.append(f"{e['edge_id']}: rejected row with no resolvable corpus locator")
            else:
                n_rej_papers += 1
    n_pend_anchors = 0
    for p in pending:
        if p["source_type"] == "textbook_layer":
            if not p["anchor_section"]:
                bad4.append(f"{p['pending_id']}: textbook proposal without a page anchor")
            else:
                n_pend_anchors += 1
        else:
            if not p["anchor_pmid"] or p["anchor_pmid"] not in paper_ids or not p["anchor_quote"]:
                bad4.append(f"{p['pending_id']}: proposal whose paper anchor does not resolve")
            else:
                n_pend_anchors += 1
    rec("G4 ANCHOR_RESOLVABLE", not bad4,
        f"confirmed edges re-walked={len(conf)} rejected_rows_with_a_resolving_locator="
        f"{n_rej_papers} pending_proposals_with_a_resolving_anchor={n_pend_anchors}", bad4)

    # ---- G5
    bad5 = []
    for e in full:
        if e["relation_type"] in ("ancestral_origin", "trajectory_association") \
                and e["evidence_grade"] == "direct_lineage_support":
            bad5.append(f"{e['edge_id']}: {e['relation_type']} labelled direct lineage")
    rec("G5 NO_TYPE_UPGRADE", not bad5,
        f"rows checked={len(full)} "
        f"direct_lineage_typed={sum(1 for e in full if e['relation_type'] == 'direct_lineage')}", bad5)

    # ---- G6
    def cycles(edges, ctx_key):
        adj = collections.defaultdict(lambda: collections.defaultdict(set))
        for e in edges:
            if e["relation_type"] in ("ontology_development_relation", "direct_lineage"):
                try:
                    k = C.parse_node_key(e["precursor_node"])
                except ValueError:
                    continue
                adj[ctx_key(k)][e["precursor_node"]].add(e["descendant_node"])
        state, found = {}, []

        def dfs(u, ctx):
            state[(ctx, u)] = 1
            for v in adj[ctx].get(u, ()):
                s = state.get((ctx, v), 0)
                if s == 1:
                    found.append(f"{ctx}: cycle through {u} -> {v}")
                elif s == 0:
                    dfs(v, ctx)
            state[(ctx, u)] = 2
        for ctx in list(adj):
            for u in list(adj[ctx]):
                if state.get((ctx, u), 0) == 0:
                    dfs(u, ctx)
        return found

    bad6 = cycles(conf, lambda k: f"sp={k['sp']}|ts={k['ts']}|es={k['es']}")
    bad6 += [f"{e['edge_id']}: self edge" for e in full
             if e["precursor_node"] and e["precursor_node"] == e["descendant_node"]]
    rec("G6 ACYCLIC_CONTEXT", not bad6,
        f"contexts checked={len({(C.parse_node_key(e['precursor_node'])['sp'], C.parse_node_key(e['precursor_node'])['ts'], C.parse_node_key(e['precursor_node'])['es']) for e in conf if e['relation_type'] in ('ontology_development_relation', 'direct_lineage')})}",
        bad6)

    # ---- G7
    bad7 = []
    conf_set = {e["edge_id"] for e in conf}
    admitted = {e["edge_id"] for e in full
                if e["evidence_grade"] in C.ADMITTED_GRADES}
    marked = {e["edge_id"] for e in full if e["admission"] == "confirmed"}
    if admitted != marked:
        bad7.append(f"confirmed markers and admitted grades disagree: "
                    f"only-marked={sorted(marked - admitted)[:5]} original={sorted(admitted - marked)[:5]}")
    if marked != conf_set:
        bad7.append(f"the confirmed view file is not the confirmed subset of the full edge set: "
                    f"missing={sorted(marked - conf_set)[:5]} extra={sorted(conf_set - marked)[:5]}")
    rec("G7 CONFIRMED_EQ_ADMITTED", not bad7,
        f"confirmed={len(conf_set)} admitted_grade_rows={len(admitted)} "
        f"full_edge_set_rows={len(full)}", bad7)

    # ---- G8
    bad8 = []
    tokens = C.eval_volume_tokens()
    for name in ARTEFACTS:
        p = os.path.join(C.OUT, name)
        if not os.path.isfile(p):
            bad8.append(f"{name} missing")
            continue
        if name in LEAK_EXEMPT:
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        hits = [t for t in tokens if t in txt]
        if hits:
            bad8.append(f"{name}: references the evaluation recording: {hits[:5]}")
    rep = os.path.join(C.SCAFFOLD, "REPORT.md")
    if os.path.isfile(rep):
        txt = open(rep, encoding="utf-8", errors="replace").read()
        hits = [t for t in tokens if t in txt]
        if hits:
            bad8.append(f"REPORT.md: references the evaluation recording: {hits[:5]}")
    rec("G8 NO_EVAL_LEAK", not bad8,
        f"forbidden tokens checked={len(tokens)} over {len(ARTEFACTS)} artefacts "
        f"(exempt, by design: {sorted(LEAK_EXEMPT)})", bad8)

    # ---- G9
    bad9 = []
    if sha256(os.path.join(HERE, "ont_nav.py")) != PINNED_ONTO_NAV_SHA:
        bad9.append("the vendored ontology navigation module is not the pinned copy")
    if sha256(C.ONT_OBO) != PINNED_OBO_SHA:
        bad9.append("the ontology file is not the pinned release")
    pin = os.path.join(C.LEDGERS, "UPSTREAM_SHA256.tsv")
    if not os.path.isfile(pin):
        bad9.append("the upstream hash ledger is missing")
    else:
        n = 0
        for r in read(pin):
            if not os.path.isfile(r["path"]):
                bad9.append(f"{r['path']}: consumed file is gone")
                continue
            if sha256(r["path"]) != r["sha256"]:
                bad9.append(f"{r['path']}: has changed since this card read it")
            else:
                n += 1
        rec_detail_upstream = f"re-verified {n}/{len(read(pin))} consumed files"
    rec("G9 UPSTREAM_PIN", not bad9,
        f"ontology sha pinned, navigation module sha pinned, {rec_detail_upstream if not bad9 else 'see offenders'}",
        bad9)

    # ---- G10
    bad10 = []
    man = os.path.join(C.OUT, "MANIFEST.sha256")
    n_man = 0
    if not os.path.isfile(man):
        bad10.append("MANIFEST.sha256 is missing")
    else:
        for line in open(man, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            h, rel = line.split("  ", 1)
            p = os.path.join(C.SCAFFOLD, rel)
            if not os.path.isfile(p):
                bad10.append(f"{rel}: in the manifest but not on disk")
            elif sha256(p) != h:
                bad10.append(f"{rel}: sha256 drifted from the manifest")
            else:
                n_man += 1
    rep_led = os.path.join(C.LEDGERS, "REPLAY.txt")
    if not os.path.isfile(rep_led) or "REPLAY_PASS" not in open(rep_led, encoding="utf-8").read():
        bad10.append("ledgers/REPLAY.txt is missing or not green")
    graph_pairs = {(e["precursor_node"], e["descendant_node"]) for e in conf}
    for p in pending:
        if p["descendant_node_key"] and p["descendant_node_key"] in {x for pair in graph_pairs for x in pair}:
            if p["proposed_precursor"] and p["proposed_precursor"].startswith("dl:"):
                bad10.append(f"{p['pending_id']}: a pending proposal is present in the confirmed graph")
    rec("G10 REPLAY_MANIFEST", not bad10,
        f"manifest entries verified={n_man} replay_ledger=green pending_vs_graph_overlap=0", bad10)

    verdict = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    res = {"gate": "SCAFFOLD", "verdict": verdict,
           "ontology": {"path": C.ONT_OBO, "sha256": PINNED_OBO_SHA},
           "counts": {"nodes": len(nodes), "confirmed_edges": len(conf),
                      "full_edge_set_rows": len(full), "pending_assertions": len(pending),
                      "register_rows": len(register)},
           "n_checks": len(checks), "n_fail": sum(1 for c in checks if c["status"] == "FAIL"),
           "checks": checks}
    json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[gate scaffold] {verdict}  rules={len(checks)} fail={res['n_fail']}")
    for c in checks:
        print(f"  {c['status']} {c['code']:<22} {c['detail']}")
        for o in c["offenders"][:5]:
            print(f"      - {o}")
    print(f"wrote {a.json}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())