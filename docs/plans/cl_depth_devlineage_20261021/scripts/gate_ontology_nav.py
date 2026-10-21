#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_ontology_nav.py - machine check on the ontology navigation deliverables (Task A).

This is the gate the brief asks for: not a rule written down, a rule a machine re-checks.
It is fail-closed (rc 0 = PASS, rc 2 = FAIL) and prints every offender by name.

Rules
  A1 ONT_SOURCE    the ontology file is the one the artefacts claim: sha256 matches, release
                   string present, term counts match
  A2 ID_TRACE      every CL identifier in the delivered artefacts resolves in the ontology file
                   and its recorded label equals the name the file gives that id
  A3 CLOSURE       the ancestor closure agrees with a fixed-point recomputation; no term is its
                   own ancestor
  A4 CLASSIFY      the four-way table is total (one of five verdicts per row), and each verdict
                   is reproduced from the two CL terms by the ontology -- the table cannot drift
                   from the rule; counts and cells reconcile with the recorded input
  A5 CANDIDATES    every candidate child term is a strict descendant of our own term, carries the
                   file line it was read from, and claims corpus support only when a locator exists
  A6 LABELMAP      every mapped label carries the file line of its id and the file's own name;
                   unresolved labels are declared, not silently empty
  A7 CROSSFILE     the two local CL files agree on the terms they share
  A8 NO_MEMORY_ID  no CL identifier anywhere in the delivered artefacts is absent from the file
                   (the "never typed from memory" rule, checked mechanically)
  A9 REPLAY        the artefact manifest matches the files on disk and the replay ledger says the
                   build reproduced itself

Usage: python3 scripts/gate_ontology_nav.py [--json out/GATE_A.json]
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
from ont_nav import Ontology, VERDICTS, NO_MAPPING  # noqa: E402

CL_RE = re.compile(r"\bCL:\d{7}\b")
TEXT_GLOBS = ("out/*.tsv", "out/*.json", "*.md", "scripts/*.py")
MANIFEST = "out/MANIFEST.sha256"
REPLAY_LEDGER = "ledgers/REPLAY.txt"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(WAVE, "out", "GATE_A.json"))
    a = ap.parse_args()

    checks = []

    def rec(code, ok, detail, offenders=None):
        checks.append({"code": code, "status": "PASS" if ok else "FAIL", "detail": detail,
                       "n_offenders": len(offenders or []), "offenders": (offenders or [])[:25]})

    nav_p = os.path.join(WAVE, "out", "ONT_NAV_v1.json")
    nav = json.load(open(nav_p, encoding="utf-8"))
    obo = nav["primary_path"]
    ont = Ontology(obo)

    # A1
    bad = []
    if not os.path.isfile(obo):
        bad.append(f"ontology file missing: {obo}")
    else:
        if sha256(obo) != nav["primary"]["sha256"]:
            bad.append("sha256 of the ontology file differs from the recorded one")
        if not nav["primary"]["release"]:
            bad.append("no release string recorded")
        if len(ont.terms) != nav["primary"]["n_cl_terms_in_file"]:
            bad.append(f"term count {len(ont.terms)} != recorded "
                       f"{nav['primary']['n_cl_terms_in_file']}")
    rec("A1 ONT_SOURCE", not bad, f"ontology={obo} release={nav['primary']['release']} "
                                 f"sha256={nav['primary']['sha256'][:12]}...", bad)

    # A2 / A8 base: which CL ids do the artefacts name, and where
    artefact_ids = {}
    for pat in TEXT_GLOBS:
        for p in sorted(glob.glob(os.path.join(WAVE, pat))):
            if os.path.basename(p) in ("GATE_A.json", "GATE_B.json", "ONT_SELFTEST.json"):
                continue
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for cid in set(CL_RE.findall(txt)):
                artefact_ids.setdefault(cid, set()).add(os.path.relpath(p, WAVE))
    missing = sorted(cid for cid in artefact_ids
                     if cid not in ont.terms and cid not in ont.cl_typedefs)
    typedef_only = sorted(cid for cid in artefact_ids
                          if cid not in ont.terms and cid in ont.cl_typedefs)
    rec("A8 NO_MEMORY_ID", not missing,
        f"distinct CL ids named in artefacts: {len(artefact_ids)}; absent from the ontology file: "
        f"{len(missing)}; CL-namespace relation ids (not cell types, disclosed): {len(typedef_only)}",
        [f"{c} (in {','.join(sorted(artefact_ids[c]))})" for c in missing])

    # A2: label consistency for the specific artefacts that pair an id with a label
    bad2 = []
    for rel, idcol, labcol in (("out/ONT_LABELMAP_V2.tsv", "cl_id", "cl_label"),
                               ("out/LINEAGE_NODES.tsv", "cl_id", "cl_label"),
                               ("out/GRANULARITY_FOURWAY_721.tsv", "ours_cl", "ours_cl_label"),
                               ("out/GRANULARITY_FOURWAY_721.tsv", "their_cl", "their_cl_label")):
        p = os.path.join(WAVE, rel)
        if not os.path.isfile(p):
            bad2.append(f"{rel} missing")
            continue
        for r in read_tsv(p):
            cid, lab = r.get(idcol, ""), r.get(labcol, "")
            if not cid:
                continue
            if cid not in ont.terms:
                bad2.append(f"{rel}: {cid} not in the ontology file")
            elif lab and lab != ont.label(cid):
                bad2.append(f"{rel}: {cid} label '{lab}' != file name '{ont.label(cid)}'")
            elif ont.trace_line(cid) is None:
                bad2.append(f"{rel}: {cid} has no file line")
    rec("A2 ID_TRACE", not bad2, "ids in label/line-pairing artefacts traced to the file", bad2)

    # A3
    c = ont.closure_is_consistent()
    self_anc = [t for t in ont.active if t in ont.ancestors(t)]
    rec("A3 CLOSURE", c["n_bad"] == 0 and not self_anc,
        f"terms={c['n_terms']} mismatched={c['n_bad']} self-ancestors={len(self_anc)}",
        c["bad"] + self_anc)

    # A4
    fw_p = os.path.join(WAVE, "out", "GRANULARITY_FOURWAY_721.tsv")
    rows = read_tsv(fw_p)
    summ = json.load(open(os.path.join(WAVE, "out", "GRANULARITY_SUMMARY.json"), encoding="utf-8"))
    bad4, cells, verdict_counts = [], 0, {}
    for r in rows:
        v = r["verdict"]
        cells += int(r["n_cells"])
        verdict_counts[v] = verdict_counts.get(v, 0) + int(r["n_cells"])
        if v not in VERDICTS:
            bad4.append(f"{r['vol']}|{r['cluster']}: unknown verdict {v}")
            continue
        again = ont.relate(r["ours_cl"] or None, r["their_cl"] or None)["verdict"]
        if again != v:
            bad4.append(f"{r['vol']}|{r['cluster']}: recorded {v} but the ontology says {again} "
                        f"({r['ours_cl']} vs {r['their_cl']})")
    if len(rows) != summ["n_clusters"]:
        bad4.append(f"row count {len(rows)} != summary {summ['n_clusters']}")
    if cells != summ["cells"]:
        bad4.append(f"cell sum {cells} != summary {summ['cells']}")
    for v in VERDICTS:
        if verdict_counts.get(v, 0) != summ["verdicts"][v]["cells"]:
            bad4.append(f"{v}: cells {verdict_counts.get(v, 0)} != summary "
                        f"{summ['verdicts'][v]['cells']}")
    rec("A4 CLASSIFY", not bad4,
        f"rows={len(rows)} cells={cells} verdicts={ {k: v for k, v in sorted(verdict_counts.items())} }",
        bad4)

    # A5
    cand_p = os.path.join(WAVE, "out", "CHILD_TERM_CANDIDATES.tsv")
    bad5 = []
    cands = read_tsv(cand_p)
    for r in cands:
        # our term must sit among the child term's ancestors (that is what "we are coarser" means)
        if r["ours_cl"] not in ont.ancestors(r["child_cl"]):
            bad5.append(f"{r['ours_cl']} is not an ancestor of {r['child_cl']} "
                        f"({r['our_labels']} vs {r['child_cl_label']})")
        if not r["child_obo_line"]:
            bad5.append(f"{r['child_cl']}: no file line recorded")
        if int(r["cells"]) <= 0:
            bad5.append(f"{r['child_cl']}: zero cells")
        st = r["corpus_support_status"]
        if st == "corpus_states_the_term" and not (int(r["corpus_n_chunks"]) > 0
                                                   and r["corpus_locator_examples"]):
            bad5.append(f"{r['child_cl']}: claims corpus support with no locator")
        if st == "no_corpus_hit" and r["corpus_locator_examples"]:
            bad5.append(f"{r['child_cl']}: claims no corpus hit but carries a locator")
        if st not in ("corpus_states_the_term", "corpus_states_a_synonym_only",
                      "no_corpus_hit"):
            bad5.append(f"{r['child_cl']}: unknown support status {st}")
    rec("A5 CANDIDATES", not bad5, f"candidates={len(cands)} "
                                   f"with_support={sum(1 for r in cands if r['corpus_support_status'] != 'no_corpus_hit')}",
        bad5)

    # A6
    lm = read_tsv(os.path.join(WAVE, "out", "ONT_LABELMAP_V2.tsv"))
    bad6 = []
    for r in lm:
        if r["cl_id"]:
            if r["mapping_method"] not in ("sidecar", "embedded_cl_id", "name", "name_relaxed"):
                bad6.append(f"{r['label']}: unknown mapping method {r['mapping_method']}")
            if not r["obo_line"]:
                bad6.append(f"{r['label']}: mapped but no file line")
        else:
            if r["mapping_method"] != "unresolved":
                bad6.append(f"{r['label']}: no id but method {r['mapping_method']}")
            if not (r["sidecar_status"] == "no_match" or r["note"]):
                bad6.append(f"{r['label']}: unresolved with no recorded reason")
    rec("A6 LABELMAP", not bad6, f"labels={len(lm)} mapped={sum(1 for r in lm if r['cl_id'])}", bad6)

    # A7
    sec = nav.get("second_file", {})
    bad7 = []
    if sec.get("missing"):
        bad7.append("second CL file not on disk: the cross-file check could not run")
    else:
        if sec.get("n_name_disagreements"):
            bad7.append(f"name disagreements between the two files: {sec['n_name_disagreements']}")
        if sec.get("n_parent_disagreements"):
            bad7.append(f"is_a disagreements between the two files: "
                        f"{sec['n_parent_disagreements']}")
        if sec.get("n_shared", 0) < 3000:
            bad7.append(f"only {sec.get('n_shared')} shared terms: the comparison is not meaningful")
    rec("A7 CROSSFILE", not bad7,
        f"shared={sec.get('n_shared')} name_diff={sec.get('n_name_disagreements')} "
        f"is_a_diff={sec.get('n_parent_disagreements')}", bad7)

    # A9
    bad9 = []
    man_p = os.path.join(WAVE, MANIFEST)
    if not os.path.isfile(man_p):
        bad9.append(f"manifest missing: {MANIFEST}")
    else:
        for line in open(man_p, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                bad9.append(f"malformed manifest line: {line[:60]}")
                continue
            want, rel = parts[0], parts[1].lstrip("*")
            p = os.path.join(WAVE, rel)
            if not os.path.isfile(p):
                bad9.append(f"manifest names a missing file: {rel}")
            elif sha256(p) != want:
                bad9.append(f"{rel}: sha256 differs from the manifest")
    rep_p = os.path.join(WAVE, REPLAY_LEDGER)
    if not os.path.isfile(rep_p):
        bad9.append(f"replay ledger missing: {REPLAY_LEDGER}")
    else:
        txt = open(rep_p, encoding="utf-8").read()
        if "REPLAY_PASS" not in txt:
            bad9.append("replay ledger does not record REPLAY_PASS")
    rec("A9 REPLAY", not bad9, f"manifest={MANIFEST} ledger={REPLAY_LEDGER}", bad9)

    verdict = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    res = {"gate": "A", "name": "ontology navigation", "verdict": verdict,
           "ontology": {"path": obo, "release": nav["primary"]["release"],
                        "sha256": nav["primary"]["sha256"]},
           "rules": {"A1": "ontology source identity", "A2": "id -> file line + label",
                     "A3": "ancestor closure", "A4": "four-way table reproduces from the ontology",
                     "A5": "child-term candidates", "A6": "label map provenance",
                     "A7": "cross-file agreement", "A8": "no CL id absent from the file",
                     "A9": "artefact manifest + replay ledger"},
           "n_checks": len(checks), "n_fail": sum(1 for c in checks if c["status"] == "FAIL"),
           "checks": checks}
    json.dump(res, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[gate A] {verdict}  rules={len(checks)} fail={res['n_fail']}")
    for c in checks:
        print(f"  {c['status']} {c['code']:<16} {c['detail']}")
        for o in c["offenders"][:6]:
            print(f"      - {o}")
    print(f"wrote {a.json}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())