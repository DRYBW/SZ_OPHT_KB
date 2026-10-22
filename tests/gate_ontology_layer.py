#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_ontology_layer.py - G7: the read-only Cell Ontology explanation layer.

What it enforces
    The capability registered in kb/ontology/ONT_LAYER_REGISTRY_v1.json has to prove itself
    mechanically, in a clean clone, without the data-mount evidence root and without network:

      G7-C01 ANCHORS        every logical address in the manifest resolves and its sha256 matches
      G7-C02 SNAPSHOT       the fixed snapshot parses; two independent parses agree; release and
                            hash match the manifest; the `is_a` graph has no cycle
      G7-C03 SEMANTICS      the declared battery over the REAL snapshot: alias/alt_id, both ancestor
                            directions, shared-ancestor-but-unrelated, multiple inheritance,
                            obsolete term with a unique replacement, synonym ambiguity, a blanket
                            ancestor, restriction expressions that must not read as is_a edges
      G7-C04 UNIT-CASES     a synthetic mini-ontology for the states this snapshot does not exhibit
                            (ambiguous replacement, same label twice, a cycle). Labelled synthetic:
                            it is a unit test of the code path, and it is NOT evidence about the
                            snapshot.
      G7-C05 TWO-LAYER       `is_a_relation` and `assessment` are both present on every comparison,
                            and are not the same record
      G7-C06 REGISTRATION    registered = true, default OFF, whitelist empty; with the route unset
                            the server imports no ontology code and advertises no ontology tool;
                            with the route set exactly the named tools appear
      G7-C07 DEFAULT-ROUTE   the frozen replay hashes: the 54 non-identity calls of the recorded
                            request set are byte-identical before and after this change, the tool
                            list is unchanged, and the identity call is the only moved one
      G7-C08 TABLES          three separate tables with a fixed denominator and no blended lenient
                            accuracy; nothing is dropped from a denominator for having no answer
      G7-C09 STOP-LINE       the blanket-ancestor rule holds, ambiguity is never resolved towards a
                            favourable answer, and the stop line is declared

Gate result
    Three states only: PASS (every mandatory check actually executed and passed), FAIL (a rule
    failed, or a mandatory check did not execute), ENV_ERROR (a declared external precondition was
    checked and found absent, so no conclusion can be drawn). A missing shipped asset is never an
    ENV_ERROR: it is a delivery defect and fails. Every check reports should-run / did-run / status,
    and the readout prints the five counts.

Stdlib only, read-only, zero network, zero GPU.

Usage (from the repository root):
    python3 tests/gate_ontology_layer.py [--json out.json]
Exit codes: 0 = PASS, 2 = FAIL, 3 = ENV_ERROR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_server"))

REGISTRY_REL = "kb/ontology/ONT_LAYER_REGISTRY_v1.json"
MANIFEST_REL = "kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json"
CARD_OUT = "docs/plans/l5_ontlayer_20261022/out"
ONT_TOOL_NAMES = ("resolve_term", "get_ancestors", "compare_terms", "explain_class_mapping")

# Battery cases, all read from the shipped snapshot. The expected strings are the ontology's own
# vocabulary, re-derived here; nothing is quoted from a report.
CASE_SAME = ("retinal rod cell", "CL:0000604")
CASE_COARSER = ("CL:0000561", "CL:0004232")
CASE_UNRELATED_WITH_SHARED_ANCESTOR = ("CL:0000561", "CL:4033052")
CASE_ALT_ID = ("CL:0000337", "CL:0000031")
CASE_OBSOLETE_UNIQUE = "CL:0000002"
CASE_AMBIGUOUS_SYNONYM = "mo.6c+ii"
CASE_MULTI_INHERITANCE = "CL:0004222"
CASE_BLANKET = ("CL:0000000", "CL:0000001")
CASE_RESTRICTION = ("CL:0000005", "CL:0000333")
MINI_OBO = """format-version: 1.2
data-version: synthetic/unit-test
ontology: mini
[Term]
id: CL:9000001
name: alpha cell
is_a: CL:9000004
[Term]
id: CL:9000002
name: beta cell
is_obsolete: true
replaced_by: CL:9000001
replaced_by: CL:9000003
[Term]
id: CL:9000003
name: gamma cell
[Term]
id: CL:9000004
name: alpha cell
[Term]
id: CL:9000005
name: delta cell
intersection_of: part_of CL:9000001
[Term]
id: CL:9000006
name: epsilon cell
is_a: CL:9000007
[Term]
id: CL:9000007
name: zeta cell
is_a: CL:9000006
"""


class Ledger:
    def __init__(self):
        self.checks = []

    def rec(self, code, label, mandatory, should_run, did_run, status, detail, offenders=None):
        self.checks.append({"code": code, "label": label, "mandatory": bool(mandatory),
                            "should_run": bool(should_run), "did_run": bool(did_run),
                            "status": status, "detail": detail,
                            "offenders": (offenders or [])[:8]})
        print(f"  {status:9s} {code} {label} :: {detail}")
        for o in (offenders or [])[:6]:
            print(f"      - {o}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    ap.add_argument("--service-python", default=os.environ.get("EYEKB_G7_PY")
                    or os.environ.get("EYEKB_G3_PY") or sys.executable,
                    help="interpreter that can import the service (MCP SDK + its dependencies); "
                         "defaults to EYEKB_G7_PY / EYEKB_G3_PY / this interpreter")
    a = ap.parse_args()
    svc_py = a.service_python
    L = Ledger()
    import ontology_layer as OL

    # ---------------------------------------------------------------- G7-C01 ANCHORS
    anchors = OL.anchor_status()
    bad = [f"{x['anchor']}: {x['status']}" for x in anchors if x["status"] != "RESOLVED"]
    L.rec("G7-C01", "ANCHORS", True, True, True, "PASS" if anchors and not bad else "FAIL",
          f"{len(anchors)} logical address(es), {len(bad)} unresolved", bad)

    # ---------------------------------------------------------------- G7-C02 SNAPSHOT
    snap = OL.layer()
    s1 = snap.summary()
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "second.json"
        p.write_text(json.dumps(s1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        s1_hash = hashlib.sha256(p.read_bytes()).hexdigest()
    ok_snap = (snap.anchor["status"] == "RESOLVED" and not snap.cycles
               and snap.release and snap.terms)
    man = OL.load_manifest()
    ok_man = (man.get("snapshot_release") in (snap.release or "")
              and man.get("parser_version"))
    L.rec("G7-C02", "SNAPSHOT", True, True, True, "PASS" if ok_snap and ok_man else "FAIL",
          f"terms={s1['n_terms_in_file']} active={s1['n_active']} obsolete={s1['n_obsolete']} "
          f"cycles={len(snap.cycles)} release={snap.release!r} summary_sha256={s1_hash[:16]}",
          ([] if ok_snap and ok_man else ["snapshot did not parse, or its release string does not "
                                          "match the manifest, or the graph has a cycle"]))

    # ---------------------------------------------------------------- G7-C03 SEMANTICS
    det, off = [], []
    c = snap.compare_terms(*CASE_SAME)
    det.append(f"same_term={c['verdict']}")
    if not (c["verdict"] == "same_term" and c["is_a_relation"] == "same_canonical_term"):
        off.append(f"{CASE_SAME}: expected same_term, got {c['verdict']}")
    c = snap.compare_terms(*CASE_COARSER)
    det.append(f"coarser={c['verdict']}")
    if not (c["verdict"] == "ours_broader" and c["ancestor_path"] and c["levels_crossed"]):
        off.append(f"{CASE_COARSER}: expected ours_broader with a path, got {c['verdict']}")
    c2 = snap.compare_terms(*reversed(CASE_COARSER))
    det.append(f"finer={c2['verdict']}")
    if c2["verdict"] != "ours_narrower":
        off.append(f"reversed {CASE_COARSER}: expected ours_narrower, got {c2['verdict']}")
    c = snap.compare_terms(*CASE_UNRELATED_WITH_SHARED_ANCESTOR)
    shared = sorted(snap.ancestors_cl(c["ours"]["canonical_id"])
                    .intersection(snap.ancestors_cl(c["theirs"]["canonical_id"])))
    det.append(f"unrelated={c['verdict']} shared_ancestors={len(shared)}")
    if not (c["verdict"] == "not_supported_by_is_a" and shared
            and c["is_a_relation"] == "no_ancestor_relation" and c["unresolved_reason"]):
        off.append(f"{CASE_UNRELATED_WITH_SHARED_ANCESTOR}: a shared ancestor must not be read as "
                   f"equivalence, and the bucket must be not_supported_by_is_a")
    r = snap.resolve_term(CASE_ALT_ID[0])
    det.append(f"alt_id={r['canonical_id']}/{r['resolution_method']}")
    if not (r["canonical_id"] == CASE_ALT_ID[1] and r["resolution_method"] == "alt_id"):
        off.append(f"{CASE_ALT_ID[0]}: expected the alternate identifier to resolve to "
                   f"{CASE_ALT_ID[1]}")
    r = snap.resolve_term(CASE_OBSOLETE_UNIQUE)
    det.append(f"obsolete={r['resolution_status']}/{bool(r['replacement'])}")
    if not (r["resolution_status"].startswith("obsolete") and r["obsolete_status"] == "obsolete"):
        off.append(f"{CASE_OBSOLETE_UNIQUE}: an obsolete term must be reported as obsolete")
    r = snap.resolve_term(CASE_AMBIGUOUS_SYNONYM)
    det.append(f"ambiguous_synonym={r['resolution_status']}")
    if not (r["resolution_status"] == "ambiguous" and r["requires_review"] and r["candidates"]):
        off.append(f"{CASE_AMBIGUOUS_SYNONYM}: an ambiguous synonym must go to review, never be "
                   f"resolved towards one answer")
    g = snap.get_ancestors(CASE_MULTI_INHERITANCE)
    det.append(f"multi_inheritance_parents={len(snap.terms[CASE_MULTI_INHERITANCE].parents)} "
               f"ancestors={g['n_ancestors']}")
    if not (len(snap.terms[CASE_MULTI_INHERITANCE].parents) > 1 and g["n_ancestors"] > 0):
        off.append(f"{CASE_MULTI_INHERITANCE}: multiple inheritance not carried through")
    c = snap.compare_terms(*CASE_BLANKET)
    det.append(f"blanket={c['verdict']}/{c['assessment']['status']}/"
               f"{c['assessment'].get('min_report_granularity_met')}")
    if not (c["verdict"] == "ours_broader"
            and c["assessment"].get("min_report_granularity_met") is False
            and c["assessment"]["status"] == "resolution_limited"):
        off.append(f"{CASE_BLANKET}: a blanket ancestor must not be reported as a usable coarse "
                   f"answer")
    term, tgt = CASE_RESTRICTION
    is_a_anc = tgt in snap.ancestors_cl(term)
    rest = [x for x in snap.terms[term].restrictions if x[1] == tgt]
    det.append(f"restriction_target_is_ancestor={is_a_anc} (restrictions on the term={len(rest)})")
    if is_a_anc or not rest:
        off.append(f"{CASE_RESTRICTION}: an OWL restriction expression was read as an is_a edge, or "
                   f"the case no longer exists in this snapshot")
    L.rec("G7-C03", "SEMANTICS", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det), off)

    # ---------------------------------------------------------------- G7-C04 UNIT-CASES (synthetic)
    off = []
    with tempfile.TemporaryDirectory() as td:
        mini = Path(td) / "mini.obo"
        mini.write_text(MINI_OBO, encoding="utf-8")
        m = OL.OntologySnapshot.__new__(OL.OntologySnapshot)
        m.asset_root = ROOT
        m.anchor = {"anchor": "synthetic://unit", "status": "RESOLVED", "path": "mini.obo",
                    "sha256_actual": hashlib.sha256(MINI_OBO.encode()).hexdigest()}
        m.registry = {}
        m.blanket_threshold = 200
        m.terms, m.active, m.alt_index = {}, set(), {}
        m.n_import_term_blocks, m.imports_declared = 0, []
        m.release = m.format_version = m.ontology_id = None
        m.file_sha256 = m.anchor["sha256_actual"]
        m._anc, m._desc, m._name_index, m._syn_index = {}, {}, {}, {}
        m.n_duplicate_id_blocks, m.cycles = 0, []
        m._parse(mini)
        m._build_indexes()
        m._build_closure()
        r_amb = m.resolve_term("beta cell")
        r_dup = m.resolve_term("alpha cell")
        r_rest = m.get_ancestors("CL:9000005")
        if not (r_amb["resolution_status"] == "ambiguous" and r_amb["requires_review"]):
            off.append("synthetic: an obsolete term with two replacements must go to review")
        if not (r_dup["resolution_status"] == "ambiguous" and len(r_dup["candidates"]) == 2):
            off.append("synthetic: the same label on two terms must be ambiguous, not guessed")
        if any(x["id"] == "CL:9000001" for x in r_rest["ancestors"]):
            off.append("synthetic: a restriction target was read as an is_a ancestor")
        if not m.cycles:
            off.append("synthetic: the planted is_a cycle was not detected")
    L.rec("G7-C04", "UNIT-CASES (synthetic, not evidence about the snapshot)", True, True, True,
          "PASS" if not off else "FAIL",
          "ambiguous replacement / duplicate label / restriction target / planted cycle exercised",
          off)

    # ---------------------------------------------------------------- G7-C05 TWO-LAYER
    off = []
    c = snap.compare_terms(*CASE_UNRELATED_WITH_SHARED_ANCESTOR)
    if "is_a_relation" not in c or "assessment" not in c:
        off.append("a comparison must carry both is_a_relation and assessment")
    elif c["is_a_relation"] == c["verdict"]:
        off.append("is_a_relation and the report bucket are the same string: the two records have "
                   "been collapsed")
    if c["assessment"]["status"] in ("", None):
        off.append("assessment.status is empty")
    ev = snap.compare_terms(*CASE_UNRELATED_WITH_SHARED_ANCESTOR,
                            evidence_source="unit-test source", evidence_assertion="unit-test claim")
    if not (ev["verdict"] == "confirmed_incompatible"
            and ev["incompatibility_evidence"] and ev["incompatibility_evidence"]["recorded"]):
        off.append("confirmed_incompatible was not reached with explicit evidence")
    plain = snap.compare_terms(*CASE_UNRELATED_WITH_SHARED_ANCESTOR)
    if plain["verdict"] != "not_supported_by_is_a":
        off.append("without evidence the same pair must stay not_supported_by_is_a")
    L.rec("G7-C05", "TWO-LAYER", True, True, True, "PASS" if not off else "FAIL",
          f"verdict={c['verdict']} is_a_relation={c['is_a_relation']} "
          f"assessment={c['assessment']['status']} (evidence path -> {ev['verdict']})", off)

    # ---------------------------------------------------------------- G7-C06 REGISTRATION
    off = []
    reg = json.loads((ROOT / REGISTRY_REL).read_text(encoding="utf-8"))
    if not (reg.get("registered") and reg.get("default_state") == "OFF"
            and reg.get("whitelist") == [] and reg.get("route_env") == "EYEKB_ONT_LAYER"):
        off.append(f"{REGISTRY_REL}: registered={reg.get('registered')} "
                   f"state={reg.get('default_state')} whitelist={reg.get('whitelist')}")
    have = []
    for py, route, tag in ((svc_py, "", "default"),
                           (svc_py, "resolve_term,compare_terms", "routed")):
        code = ("import asyncio, json, os, sys\n"
                "sys.path.insert(0, 'mcp_server')\n"
                "import server\n"
                "tools = sorted(t.name for t in asyncio.run(server.app.list_tools()))\n"
                "print(json.dumps({'tools': tools, "
                "'ontology_imported': 'ontology_layer' in sys.modules}))\n")
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env["EYEKB_ONT_LAYER"] = route
        p = subprocess.run([py, "-c", code], cwd=str(ROOT), env=env, capture_output=True, text=True,
                           timeout=300)
        if p.returncode != 0:
            missing = [ln for ln in p.stderr.splitlines() if "ModuleNotFoundError" in ln]
            status = "ENV_ERROR" if missing else "FAIL"
            L.rec("G7-C06", "REGISTRATION", True, True, True, status,
                  f"the service could not be imported for the {tag} state "
                  f"({missing[0].strip() if missing else p.stderr.strip()[-200:]})")
            return _finish(L, a)
        got = json.loads(p.stdout.strip().splitlines()[-1])
        have.append((tag, got))
        if tag == "default":
            if got["ontology_imported"]:
                off.append("with the route unset, the ontology module was imported")
            if any(t in got["tools"] for t in ONT_TOOL_NAMES):
                off.append("with the route unset, an ontology tool was advertised")
        else:
            if not got["ontology_imported"]:
                off.append("with the route set, the ontology module was not imported")
            if sorted(got["tools"]) != sorted(["resolve_term", "compare_terms"] + [
                    t for t in have[0][1]["tools"]]):
                off.append(f"with the route set, the advertised set is {got['tools']}")
    L.rec("G7-C06", "REGISTRATION", True, True, True, "PASS" if not off else "FAIL",
          f"default: {len(have[0][1]['tools'])} tools, ontology imported="
          f"{have[0][1]['ontology_imported']}; routed: +"
          f"{len(have[1][1]['tools']) - len(have[0][1]['tools'])} tools", off)

    # ---------------------------------------------------------------- G7-C07 DEFAULT-ROUTE
    off, det = [], []
    pre_p = ROOT / CARD_OUT / "PRE_REPLAY_HASHES.tsv"
    post_p = ROOT / CARD_OUT / "POST_REPLAY_HASHES.tsv"
    if not (pre_p.is_file() and post_p.is_file()):
        L.rec("G7-C07", "DEFAULT-ROUTE", True, True, False, "FAIL",
              f"the frozen replay hashes are missing ({pre_p.name} / {post_p.name})")
    else:
        def load(p):
            return {r.split("\t")[0]: r.split("\t")[1:] for r in
                    p.read_text(encoding="utf-8").splitlines()[1:] if r.strip()}
        pre, post = load(pre_p), load(post_p)
        moved = [k for k in pre if pre[k][0] != post.get(k, [""])[0]]
        identity = [k for k in moved if k.startswith("get_release_identity")]
        others = [k for k in moved if not k.startswith("get_release_identity")]
        det.append(f"calls={len(pre)} moved={len(moved)} identity_only={len(identity)} "
                   f"others={len(others)}")
        if others:
            off.append(f"calls outside the identity tool moved: {others[:4]}")
        if not identity:
            off.append("the identity call did not move, so the four-layer block is not being "
                       "reported (or the hashes are not from this change)")
        tl_pre = (ROOT / CARD_OUT / "PRE_TOOLS.txt").read_text(encoding="utf-8").split()
        tl_post = (ROOT / CARD_OUT / "POST_TOOLS.txt").read_text(encoding="utf-8").split()
        if tl_pre != tl_post:
            off.append(f"the advertised tool list moved: {tl_pre} -> {tl_post}")
        if any(t.startswith(("resolve_term", "get_ancestors", "compare_terms",
                             "explain_class_mapping")) for t in tl_post):
            off.append("an ontology tool was advertised in the default state")
        L.rec("G7-C07", "DEFAULT-ROUTE", True, True, True, "PASS" if not off else "FAIL",
              "; ".join(det), off)

    # ---------------------------------------------------------------- G7-C08 TABLES
    off, det = [], []
    t1, t2, t3 = (ROOT / CARD_OUT / "TABLE_1_SAME_TERM.tsv",
                  ROOT / CARD_OUT / "TABLE_2_GRANULARITY.tsv",
                  ROOT / CARD_OUT / "TABLE_3_TASK_VALIDITY.tsv")
    rows = {}
    for p in (t1, t2, t3):
        if not p.is_file():
            off.append(f"missing table {p.name}")
            continue
        rows[p.name] = [r.split("\t") for r in p.read_text(encoding="utf-8").splitlines() if r]
    if len(rows) == 3:
        denoms = {rows[t1.name][0].index("denominator_clusters"),
                  rows[t3.name][0].index("denominator_clusters")}
        d1 = rows[t1.name][1][denoms.pop() if len(denoms) == 1 else 3]
        # every declared denominator on both tables must be the same fixed number
        dn = []
        for name, idx in ((t1.name, rows[t1.name][0].index("denominator_clusters")),
                          (t3.name, rows[t3.name][0].index("denominator_clusters"))):
            dn += [r[idx] for r in rows[name][1:]]
        if len(set(dn)) != 1:
            off.append(f"the denominators differ across the tables: {sorted(set(dn))}")
        det.append(f"fixed denominator={sorted(set(dn))} rows={d1}")
        for name, rws in rows.items():
            for h in rws[0]:
                if h.lower() in ("accuracy", "agreement_rate", "lenient_accuracy", "score"):
                    off.append(f"{name}: a blended figure column is present ({h})")
        if not any("counts_as_correct" in r for r in rows[t2.name]):
            off.append("the granularity table does not state which buckets count as correct")
        if any(p.name.upper().find("ACCURACY") >= 0 for p in (t1, t2, t3)):
            off.append("a file named like a blended accuracy table exists")
    if not (ROOT / CARD_OUT / "BUCKET_SUMMARY.json").is_file():
        off.append("BUCKET_SUMMARY.json is missing")
    else:
        bs = json.loads((ROOT / CARD_OUT / "BUCKET_SUMMARY.json").read_text(encoding="utf-8"))
        if not bs["denominator"]["clusters"]:
            off.append("the summary declares no denominator")
        if bs.get("cross_check_against_the_earlier_reading", {}).get("identical") is not True:
            off.append("the recomputation does not agree with the earlier reading")
        det.append(f"buckets={ {k: v['clusters'] for k, v in bs['buckets'].items()} }")
    L.rec("G7-C08", "TABLES", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det) or "tables absent", off)

    # ---------------------------------------------------------------- G7-C09 STOP-LINE
    off, det = [], []
    c = snap.compare_terms(*CASE_BLANKET)
    if c["assessment"].get("min_report_granularity_met") is not False:
        off.append("the blanket-ancestor rule did not take effect")
    det.append(f"blanket_threshold={snap.blanket_threshold} blanket_ancestors={s1['n_blanket_ancestors']}")
    r = snap.resolve_term(CASE_AMBIGUOUS_SYNONYM)
    if sorted(r["candidates"]) != sorted(["CL:0002469", "CL:0002470"]):
        off.append(f"the ambiguity candidates changed: {r['candidates']}")
    if r["canonical_id"] is not None:
        off.append("an ambiguous synonym produced a canonical answer")
    det.append(f"ambiguity kept as review, candidates={len(r['candidates'])}")
    reg_sl = json.loads((ROOT / REGISTRY_REL).read_text(encoding="utf-8")).get("stop_line") or []
    if len(reg_sl) < 4:
        off.append("the stop line is not declared in the registry")
    det.append(f"stop_line items={len(reg_sl)}")
    L.rec("G7-C09", "STOP-LINE", True, True, True, "PASS" if not off else "FAIL",
          "; ".join(det), off)

    return _finish(L, a)


def _finish(L, a) -> int:
    total = len(L.checks)
    did = sum(1 for c in L.checks if c["did_run"])
    npass = sum(1 for c in L.checks if c["status"] == "PASS")
    nfail = sum(1 for c in L.checks if c["status"] == "FAIL")
    nenv = sum(1 for c in L.checks if c["status"] == "ENV_ERROR")
    nnot = sum(1 for c in L.checks if not c["did_run"])
    mandatory_unrun = [c["code"] for c in L.checks if c["mandatory"] and not c["did_run"]]
    if nenv:
        verdict = "ENV_ERROR"
    elif nfail or mandatory_unrun:
        verdict = "FAIL"
    else:
        verdict = "PASS"
    res = {"gate": "G7", "label": "read-only Cell Ontology explanation layer",
           "script": str(Path(__file__).resolve().relative_to(ROOT)),
           "checks": L.checks, "n_checks": total,
           "should_run": total, "did_run": did, "pass": npass, "fail": nfail,
           "not_run": nnot, "env_error": nenv,
           "mandatory_not_run": mandatory_unrun,
           "verdict": verdict,
           "rule": ("a gate does not pass while any mandatory check did not execute; a missing "
                    "shipped asset is a FAIL, never an ENV_ERROR")}
    print(f"[g7] should_run={total} did_run={did} pass={npass} fail={nfail} not_run={nnot} "
          f"env_error={nenv} verdict={verdict}")
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0 if verdict == "PASS" else (3 if verdict == "ENV_ERROR" else 2)


if __name__ == "__main__":
    sys.exit(main())