#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_lineage.py - machine check on the developmental lineage layer (Task B).

Fail-closed (rc 0 = PASS, rc 2 = FAIL). Every rule prints its offenders by name.

Rules
  B1 NODE_TERM    every node's CL term resolves in the ontology file, with its file line, and the
                  recorded label equals the file's own name
  B2 INBOUND      every non-root node has at least one inbound relation, every edge's endpoints
                  exist as nodes, every edge carries evidence (an ontology line, or a corpus
                  locator whose paper resolves in the corpus this machine ships), and the number
                  of roots equals what the disclosure accounts for (germ anchors + classes with
                  no local developmental evidence) -- a silently disconnected node cannot hide
  B3 ACYCLIC      the develops_from graph has no cycle and no self edge
  B4 STAGE_AXIS   stage flags are well formed, the stage_crossing flag agrees with its two
                  endpoints, and no node on the developing side of the axis appears in an adult
                  baseline entry of this repository
  B5 MARKER_TRACE every marker row is either corpus-backed with a resolvable paper id, or
                  declared as having no corpus hit -- a claim without a locator fails
  B6 NO_EVAL_LEAK the lineage artefacts contain no reference to the evaluation volumes and no
                  reference to the evaluation working tree (the lineage is a knowledge artefact,
                  not a benchmark derivative)
  B7 REPLAY       the lineage artefacts match the delivered manifest and the replay ledger is green

Usage: python3 scripts/gate_lineage.py [--json out/GATE_B.json]
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ont_nav import Ontology  # noqa: E402

PAPERS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl"
BASELINE_DIR = "/mnt/D/EyeKB/kb/baselines"
MANIFEST = "out/MANIFEST.sha256"
REPLAY_LEDGER = "ledgers/REPLAY.txt"
LINEAGE_FILES = ("LINEAGE_NODES.tsv", "LINEAGE_EDGES.tsv", "LINEAGE_GERM_LAYER.tsv",
                 "LINEAGE_MARKER_TRANSITIONS.tsv", "LINEAGE_UNRESOLVED_DEVELOPMENT.tsv",
                 "LINEAGE_SUMMARY.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def adult_baseline_keys():
    keys = set()
    for p in sorted(glob.glob(os.path.join(BASELINE_DIR, "*.json"))):
        if os.path.basename(p).startswith("_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        stage = str(d.get("development_stage") or d.get("organism_stage") or "")
        if "fetal" in os.path.basename(p) or "developing" in stage or stage == "fetal":
            continue
        for field in ("donor_level_main", "pooled_adult_only_main",
                      "donor_level_adult_pool_contrast", "pooled_adult_pool_contrast"):
            v = d.get(field)
            if isinstance(v, dict):
                keys |= {norm(k) for k in v}
        for mc in (d.get("major_classes") or []):
            if isinstance(mc, dict) and mc.get("class"):
                keys.add(norm(mc["class"]))
        for st in (d.get("states") or []):
            if isinstance(st, dict) and st.get("cell_type"):
                keys.add(norm(st["cell_type"]))
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(WAVE, "out", "GATE_B.json"))
    a = ap.parse_args()
    checks = []

    def rec(code, ok, detail, offenders=None):
        checks.append({"code": code, "status": "PASS" if ok else "FAIL", "detail": detail,
                       "n_offenders": len(offenders or []), "offenders": (offenders or [])[:25]})

    summ = json.load(open(os.path.join(WAVE, "out", "LINEAGE_SUMMARY.json"), encoding="utf-8"))
    ont = Ontology(summ["ontology"]["path"])
    nodes = read_tsv(os.path.join(WAVE, "out", "LINEAGE_NODES.tsv"))
    edges = read_tsv(os.path.join(WAVE, "out", "LINEAGE_EDGES.tsv"))
    germ = read_tsv(os.path.join(WAVE, "out", "LINEAGE_GERM_LAYER.tsv"))
    markers = read_tsv(os.path.join(WAVE, "out", "LINEAGE_MARKER_TRANSITIONS.tsv"))
    unresolved = read_tsv(os.path.join(WAVE, "out", "LINEAGE_UNRESOLVED_DEVELOPMENT.tsv"))

    # B1
    bad1 = []
    for n in nodes:
        cid = n["cl_id"]
        if cid not in ont.terms:
            bad1.append(f"{n['node_id']}: {cid} not in the ontology file")
            continue
        if not n["obo_line"]:
            bad1.append(f"{cid}: no file line")
        if n["cl_label"] != ont.label(cid):
            bad1.append(f"{cid}: label '{n['cl_label']}' != file name '{ont.label(cid)}'")
        if not ont.trace_line(cid):
            bad1.append(f"{cid}: trace_line returned nothing")
    rec("B1 NODE_TERM", not bad1, f"nodes={len(nodes)}", bad1)

    # B2
    node_ids = {n["cl_id"] for n in nodes}
    paper_ids = set()
    with open(PAPERS, encoding="utf-8") as f:
        for line in f:
            try:
                paper_ids.add(json.loads(line)["paper_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    inbound = {}
    bad2 = []
    for e in edges:
        for side in ("child", "parent"):
            if e[side] not in node_ids:
                bad2.append(f"{e['edge_id']}: {side} {e[side]} is not a node")
        inbound[e["child"]] = inbound.get(e["child"], 0) + 1
        if e["child"] == e["parent"]:
            bad2.append(f"{e['edge_id']}: self edge")
        has_ontology = bool(e["obo_lines"].strip())
        has_corpus = False
        if e.get("corpus_locators"):
            for loc in e["corpus_locators"].split(" | "):
                pid = loc.split(" @ ")[0].strip()
                if pid in paper_ids:
                    has_corpus = True
                    break
        if e["evidence_kind"] == "corpus_cooccurrence" and not has_corpus:
            bad2.append(f"{e['edge_id']}: co-occurrence evidence with no resolvable paper id")
        if not has_ontology and not has_corpus:
            bad2.append(f"{e['edge_id']}: no evidence (no ontology line, no corpus locator)")
    roots = [n["cl_id"] for n in nodes if n["root"] == "yes"]
    for n in nodes:
        if n["root"] == "no" and inbound.get(n["cl_id"], 0) == 0:
            bad2.append(f"{n['cl_id']}: marked non-root but has no inbound edge")
        if n["root"] == "yes" and inbound.get(n["cl_id"], 0) > 0:
            bad2.append(f"{n['cl_id']}: marked root but has {inbound[n['cl_id']]} inbound edges")
    expected_roots = summ["roots_expected_from_disclosure"]
    if len(roots) != expected_roots:
        bad2.append(f"roots {len(roots)} != accounted roots {expected_roots} "
                    f"(germ anchors + classes with no local evidence)")
    if len(unresolved) != summ["unresolved_classes"]:
        bad2.append(f"unresolved rows {len(unresolved)} != summary {summ['unresolved_classes']}")
    rec("B2 INBOUND", not bad2,
        f"edges={len(edges)} roots={len(roots)} (accounted {expected_roots})", bad2)

    # B3
    adj = {}
    bad3 = []
    for e in edges:
        if e["relation_type"].startswith("develops_from"):
            adj.setdefault(e["child"], set()).add(e["parent"])
    state = {}

    def dfs(u):
        state[u] = 1
        for v in adj.get(u, ()):
            if state.get(v) == 1:
                bad3.append(f"cycle through {u} -> {v}")
            elif state.get(v, 0) == 0:
                dfs(v)
        state[u] = 2

    for u in list(adj):
        if state.get(u, 0) == 0:
            dfs(u)
    rec("B3 ACYCLIC", not bad3, f"develops_from nodes={len(adj)} edges="
                                f"{sum(len(v) for v in adj.values())}", bad3)

    # B4
    bad4 = []
    bl = adult_baseline_keys()
    for n in nodes:
        if n["stage_scope"] not in ("developing", "adult_or_unspecified"):
            bad4.append(f"{n['cl_id']}: unknown stage_scope {n['stage_scope']}")
        if n["stage_scope"] == "developing":
            labels = [x for x in n["our_labels"].split(",") if x] + [n["cl_label"]]
            hit = [l for l in labels if norm(l) in bl]
            if hit:
                bad4.append(f"{n['cl_id']}: developing node listed in an adult baseline as {hit}")
    for e in edges:
        want = "yes" if e["child_stage"] != e["parent_stage"] else "no"
        if e["stage_crossing"] != want:
            bad4.append(f"{e['edge_id']}: stage_crossing={e['stage_crossing']} but stages are "
                        f"{e['child_stage']}/{e['parent_stage']}")
        if e["relation_type"] == "germ_layer_membership" and e["tier"] == "unresolved":
            bad4.append(f"{e['edge_id']}: membership edge on an unresolved class")
    rec("B4 STAGE_AXIS", not bad4,
        f"developing nodes={sum(1 for n in nodes if n['stage_scope'] == 'developing')} "
        f"stage-crossing edges={sum(1 for e in edges if e['stage_crossing'] == 'yes')} "
        f"adult-baseline keys checked={len(bl)}", bad4)

    # B5
    bad5 = []
    for m in markers:
        st = m["support_status"]
        if st == "corpus_supported":
            if int(m["corpus_n_chunks"]) <= 0 or int(m["corpus_n_papers"]) <= 0:
                bad5.append(f"{m['edge_id']} {m['gene']}: supported but zero counts")
            if not m["corpus_locators"]:
                bad5.append(f"{m['edge_id']} {m['gene']}: supported but no locator")
            else:
                ok = any(loc.split(" @ ")[0].strip() in paper_ids
                         for loc in m["corpus_locators"].split(" | "))
                if not ok:
                    bad5.append(f"{m['edge_id']} {m['gene']}: no locator resolves in the corpus")
        elif st == "no_corpus_hit":
            if m["corpus_locators"]:
                bad5.append(f"{m['edge_id']} {m['gene']}: declared no hit but carries a locator")
        else:
            bad5.append(f"{m['edge_id']} {m['gene']}: unknown support status {st}")
    rec("B5 MARKER_TRACE", not bad5,
        f"marker rows={len(markers)} corpus-supported="
        f"{sum(1 for m in markers if m['support_status'] == 'corpus_supported')}", bad5)

    # B6
    bad6 = []
    fw = os.path.join(WAVE, "out", "GRANULARITY_FOURWAY_721.tsv")
    vols = set()
    if os.path.isfile(fw):
        for r in read_tsv(fw):
            vols.add(r["vol"])
    forbidden = sorted(vols) + ["oss_check_20261019"]
    for name in LINEAGE_FILES:
        p = os.path.join(WAVE, "out", name)
        if not os.path.isfile(p):
            bad6.append(f"{name} missing")
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        hits = [t for t in forbidden if t in txt]
        if hits:
            bad6.append(f"{name}: references the evaluation side: {hits[:5]}")
    if summ["inputs"].get("evaluation_volumes_used"):
        bad6.append("summary declares evaluation volumes as lineage inputs")
    for name in LINEAGE_FILES:
        p = os.path.join(WAVE, "out", name)
        if os.path.isfile(p) and "oss_check" in open(p, encoding="utf-8",
                                                     errors="replace").read():
            bad6.append(f"{name}: references the evaluation working tree")
    rec("B6 NO_EVAL_LEAK", not bad6,
        f"forbidden tokens checked={len(forbidden)} over {len(LINEAGE_FILES)} files", bad6)

    # B7
    bad7 = []
    man_p = os.path.join(WAVE, MANIFEST)
    if not os.path.isfile(man_p):
        bad7.append(f"manifest missing: {MANIFEST}")
    else:
        want = {}
        for line in open(man_p, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                want[parts[1].lstrip("*")] = parts[0]
        for name in LINEAGE_FILES:
            rel = os.path.join("out", name)
            if rel not in want:
                bad7.append(f"{rel} is not in the manifest")
            elif sha256(os.path.join(WAVE, rel)) != want[rel]:
                bad7.append(f"{rel}: sha256 differs from the manifest")
    rep_p = os.path.join(WAVE, REPLAY_LEDGER)
    if not os.path.isfile(rep_p) or "REPLAY_PASS" not in open(rep_p, encoding="utf-8").read():
        bad7.append(f"replay ledger missing or not green: {REPLAY_LEDGER}")
    rec("B7 REPLAY", not bad7, f"manifest entries={len(want) if os.path.isfile(man_p) else 0}", bad7)

    verdict = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    res = {"gate": "B", "name": "developmental lineage", "verdict": verdict,
           "ontology": summ["ontology"],
           "rules": {"B1": "node term resolves + file line", "B2": "inbound relation + evidence",
                     "B3": "acyclic", "B4": "organism-stage axis not collapsed",
                     "B5": "marker transition traceability", "B6": "no evaluation-volume input",
                     "B7": "manifest + replay"},
           "n_checks": len(checks), "n_fail": sum(1 for c in checks if c["status"] == "FAIL"),
           "checks": checks}
    json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[gate B] {verdict}  rules={len(checks)} fail={res['n_fail']}")
    for c in checks:
        print(f"  {c['status']} {c['code']:<16} {c['detail']}")
        for o in c["offenders"][:6]:
            print(f"      - {o}")
    print(f"wrote {a.json}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())