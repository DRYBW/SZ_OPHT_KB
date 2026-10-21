#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m5_gate.py — the machine-checkable gate for the marker layer.

Thirteen named checks, each re-reading disk rather than trusting the build. Every check reports a
pass/fail count, so "PASS" is a number and not a mood:

  G1  KEY_RESOLVES          every assertion points at a node key or an edge key that exists
  G2  ANCHOR_RESOLVES       every anchor re-opens from disk (corpus row by ordinal + sha, panel
                            entry by file, registry citation by entry + PMID + gene)
  G3  VOCAB                 every controlled field is inside its declared vocabulary
  G4  NO_NUMERIC            no effect_value anywhere without an extraction record that resolves
  G5  RNA_PROTEIN_SPLIT     no single row mixes RNA and protein evidence
  G6  SPECIES_STAGE         no assertion spans a species or stage boundary un-split
  G7  NO_EVAL_INPUT         no delivered data artefact names an evaluation volume or its paper
  G8  GAP_COVERAGE          every zero-evidence node and every edge appears in the register, and
                            every reason is in the declared vocabulary
  G9  NO_OFF_WITHOUT_DETECTION   no `off` / `down` was claimed from panel absence
  G10 REBUILD_REPLAY        the whole chain rebuilds byte-identically into a scratch directory
  G11 NO_FABRICATED_GENE    every gene symbol resolves to a real on-disk source
  G12 GOLDEN721             the recorded production query set replays to its recorded ranking
  G13 KB_UNTOUCHED          nothing under kb/ or the repo's kb/ was written by this card

Usage: python3 m5_gate.py [--no-replay] [--json OUT/GATE.json]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

DATA_ARTEFACTS = ["NODES.tsv", "LABEL_ATTACHMENT.tsv", "MARKER_SETS_NODE.tsv",
                  "MARKER_CHANGE_EDGES.tsv", "EDGES.tsv", "GAP_REGISTER.tsv",
                  "CORPUS_GENE_INDEX_v1.tsv", "NODE_GENE_REFUSALS.tsv",
                  "EDGE_MARKER_REFUSALS.tsv", "ANCHORS.jsonl"]
GOLDEN = "/mnt/D/EyeKB/plans/holefill_v12_20261021/golden_721.py"
GOLDEN_RECORDED = "/mnt/D/EyeKB/plans/holefill_v12_20261021/out/golden_721_BEFORE.json"
SESSION_START = 1792600271  # the card's created_at: anything newer under kb/ is ours, if any


class Gate:
    def __init__(self, outdir):
        self.out = outdir
        self.checks = []

    def add(self, code, name, ok, detail, offenders=()):
        off = list(offenders)
        self.checks.append({"code": code, "name": name, "status": "PASS" if ok else "FAIL",
                            "detail": detail, "n_offenders": len(off), "offenders": off[:12]})
        return ok


def rd(path):
    return M.read_tsv(os.path.join(M.WAVE, "out", path)) if not os.path.isabs(path) else M.read_tsv(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(M.OUT, "GATE.json"))
    ap.add_argument("--no-replay", action="store_true")
    args = ap.parse_args()
    out = M.OUT
    g = Gate(out)

    nodes = M.read_tsv(os.path.join(out, "NODES.tsv"))
    edges = M.read_tsv(os.path.join(out, "EDGES.tsv"))
    nset = M.read_tsv(os.path.join(out, "MARKER_SETS_NODE.tsv"))
    nchg = M.read_tsv(os.path.join(out, "MARKER_CHANGE_EDGES.tsv"))
    gaps = M.read_tsv(os.path.join(out, "GAP_REGISTER.tsv"))
    refusals = M.read_tsv(os.path.join(out, "NODE_GENE_REFUSALS.tsv"))
    allrows = nset + nchg
    node_keys = {n["node_key"] for n in nodes}
    edge_keys = {e["edge_key"] for e in edges}

    # ---- G1 keys ---------------------------------------------------------------------------
    bad = [r["assertion_id"] for r in allrows
           if r["edge_id_or_node_key"] not in node_keys | edge_keys]
    g.add("G1", "KEY_RESOLVES", not bad,
          "assertions=%d node keys=%d edge keys=%d unresolved=%d"
          % (len(allrows), len(node_keys), len(edge_keys), len(bad)), bad)

    # ---- G2 anchors ------------------------------------------------------------------------
    anchors = {}
    for line in open(os.path.join(out, "ANCHORS.jsonl"), encoding="utf-8"):
        d = json.loads(line)
        anchors[d["assertion_id"]] = d
    for r in nchg:
        anchors[r["assertion_id"]] = {"gene": r["gene_symbol"],
                                      "anchor": json.loads(r["evidence_anchor"])}
    registry = M.load_link_registry()
    panels = M.load_panels()
    bad, checked = [], collections.Counter()
    for aid, rec in anchors.items():
        a = rec["anchor"]
        kind = a.get("kind")
        g_ = rec["gene"]
        if kind == "link_registry_gene_verified":
            row = registry.get(a.get("entry_id"))
            ok = bool(row) and any(str(c.get("pmid")) == str(a.get("pmid"))
                                   and g_ in (c.get("genes_in_text") or [])
                                   for c in (row.get("citations") or []))
        elif kind == "corpus_gene_row":
            # defer: verified in one pass below
            ok = True
        elif kind in ("panel_provenance_stated", "panel_entry_basis_unstated"):
            ok = os.path.isfile(a["file"]) and g_ in open(a["file"], encoding="utf-8",
                                                          errors="replace").read()
        else:
            ok = False
        checked[kind] += 1
        if not ok:
            bad.append("%s:%s:%s" % (aid, kind, g_))
    # one pass over the corpus for every corpus-row anchor
    wanted = {}
    for aid, rec in anchors.items():
        a = rec["anchor"]
        if a.get("kind") == "corpus_gene_row":
            wanted[int(a["ord"])] = (aid, rec["gene"], str(a["paper_id"]), a["sha16"])
    verified = collections.Counter()
    if wanted:
        ord_i = 0
        pf = pq.ParquetFile(M.CHUNKS)
        for batch in pf.iter_batches(batch_size=20000,
                                     columns=["paper_id", "text"]):
            d = batch.to_pydict()
            for i in range(batch.num_rows):
                ord_i += 1
                hit = wanted.get(ord_i)
                if not hit:
                    continue
                aid, gene, pid, sha16 = hit
                text = d["text"][i] or ""
                ok = (str(d["paper_id"][i]) == pid
                      and hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] == sha16
                      and gene in {t.upper() for t in re.findall(r"[A-Za-z][A-Za-z0-9\-]{1,14}",
                                                                 text)})
                verified["ok" if ok else "bad"] += 1
                if not ok:
                    bad.append("%s:corpus_row:ord=%d:%s" % (aid, ord_i, gene))
    g.add("G2", "ANCHOR_RESOLVES", not bad,
          "anchors=%d by kind=%s corpus rows re-read=%d ok=%d bad=%d"
          % (len(anchors), dict(checked), len(wanted), verified["ok"], verified["bad"]), bad)
    M.write_json(os.path.join(out, "ANCHOR_RESOLUTION.json"),
                 {"n_anchors": len(anchors), "by_kind": dict(checked),
                  "corpus_rows_reread": len(wanted), "corpus_rows_ok": verified["ok"],
                  "corpus_rows_bad": verified["bad"], "offenders": bad[:50]})

    # ---- G3 vocab --------------------------------------------------------------------------
    bad = []
    for r in nset:
        for field, vocab in (("role", M.ROLES), ("change", M.CHANGES), ("stage", M.STAGES),
                             ("claim_type", M.CLAIM_TYPES), ("species", M.SPECIES_VOCAB),
                             ("assay", M.ASSAYS), ("support_basis", M.SUPPORT_BASIS)):
            if r[field] not in vocab:
                bad.append("%s %s=%r" % (r["assertion_id"], field, r[field]))
        if r["evidence_grade"] and r["evidence_grade"] not in M.EV_GRADES:
            bad.append("%s evidence_grade=%r" % (r["assertion_id"], r["evidence_grade"]))
    for r in nchg:
        for field, vocab in (("role", M.ROLES), ("change", M.CHANGES), ("stage", M.STAGES),
                             ("claim_type", M.CLAIM_TYPES), ("species", M.SPECIES_VOCAB),
                             ("assay", M.ASSAYS), ("support_basis", M.SUPPORT_BASIS),
                             ("evidence_grade", M.EV_GRADES)):
            if r[field] not in vocab:
                bad.append("%s %s=%r" % (r["assertion_id"], field, r[field]))
    for e in edges:
        if e["relation_type"] not in M.RELATION_TYPES:
            bad.append("%s relation_type=%r" % (e["edge_id"], e["relation_type"]))
    g.add("G3", "VOCAB", not bad,
          "fields checked over %d assertions + %d edges; rows with an out-of-vocabulary value=%d"
          % (len(allrows), len(edges), len(bad)), bad)

    # ---- G4 no numeric without an extraction record ----------------------------------------
    bad = []
    for r in allrows:
        if (r["effect_value"] or "").strip():
            er = (r["extraction_record"] or "").strip()
            if not er or not os.path.isfile(er):
                bad.append("%s effect_value=%r" % (r["assertion_id"], r["effect_value"]))
    numeric = sum(1 for r in allrows if (r["effect_value"] or "").strip())
    g.add("G4", "NO_NUMERIC", not bad,
          "assertions with effect_value=%d (all qualitative by design); offenders=%d"
          % (numeric, len(bad)), bad)

    # ---- G5 RNA / protein not merged -------------------------------------------------------
    bad = []
    per_gene = collections.defaultdict(set)
    for r in allrows:
        if "protein" in r["assay"] and "rna" in r["assay"].lower():
            bad.append("%s assay=%r" % (r["assertion_id"], r["assay"]))
        per_gene[(r["edge_id_or_node_key"], r["gene_symbol"])].add(r["assay"])
    n_dual = sum(1 for v in per_gene.values() if any("protein" in x for x in v)
                 and any("rna" in x.lower() for x in v))
    g.add("G5", "RNA_PROTEIN_SPLIT", not bad,
          "assays=%s; (node, gene) pairs carrying both an RNA and a protein row (kept as separate "
          "rows, never merged)=%d" % (dict(collections.Counter(r["assay"] for r in allrows)),
                                      n_dual), bad)

    # ---- G6 species / stage not stitched ---------------------------------------------------
    bad = []
    node_by_key = {n["node_key"]: n for n in nodes}
    for r in nset:
        n = node_by_key[r["edge_id_or_node_key"]]
        if r["species"] != n["species"]:
            bad.append("%s species=%s node=%s" % (r["assertion_id"], r["species"], n["species"]))
        if r["stage"] != n["organism_stage"]:
            bad.append("%s stage=%s node=%s" % (r["assertion_id"], r["stage"],
                                                n["organism_stage"]))
        if r["anchor_species"] not in ("human", "both"):
            bad.append("%s anchor_species=%s" % (r["assertion_id"], r["anchor_species"]))
    for r in nchg:
        if not r["source_group"] or not r["target_group"]:
            bad.append("%s groups not named" % r["assertion_id"])
        if r["stage_crossing"] not in ("yes", "no"):
            bad.append("%s stage_crossing=%r" % (r["assertion_id"], r["stage_crossing"]))
        ends = {node_by_key[e["descendant_node"]]["organism_stage"]
                for e in edges if e["edge_key"] == r["edge_id_or_node_key"]}
        ends |= {node_by_key[e["precursor_node"]]["organism_stage"]
                 for e in edges if e["edge_key"] == r["edge_id_or_node_key"]}
        if ends and r["stage"] not in ends:
            bad.append("%s stage=%s not an endpoint stage %s"
                       % (r["assertion_id"], r["stage"], sorted(ends)))
        if r["species"] not in ("human", "both"):
            bad.append("%s species=%s" % (r["assertion_id"], r["species"]))
    g.add("G6", "SPECIES_STAGE", not bad,
          "node rows carry their node's species and stage; edge rows name source and target group "
          "and disclose stage_crossing; offenders=%d" % len(bad), bad)

    # ---- G7 no evaluation input ------------------------------------------------------------
    forbidden = M.FORBIDDEN_VOLUMES + M.FORBIDDEN_TOKENS
    bad = []
    for name in DATA_ARTEFACTS:
        p = os.path.join(out, name)
        if not os.path.isfile(p):
            bad.append("%s missing" % name)
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        hits = [t for t in forbidden if t in txt]
        if hits:
            bad.append("%s: %s" % (name, hits[:4]))
    g.add("G7", "NO_EVAL_INPUT", not bad,
          "%d forbidden tokens over %d data artefacts; hits=%d"
          % (len(forbidden), len(DATA_ARTEFACTS), len(bad)), bad)

    # ---- G8 gap coverage + vocabulary ------------------------------------------------------
    bad = [r["reason"] for r in gaps if r["reason"] not in M.GAP_REASONS]
    with_assertion = {r["edge_id_or_node_key"] for r in nset}
    for n in nodes:
        if n["node_key"] not in with_assertion:
            if not any(r["scope"] == "node" and r["subject_key"] == n["node_key"] for r in gaps):
                bad.append("node not in register: %s" % n["node_key"])
    edge_subjects = {r["subject_key"] for r in gaps}
    changed = {r["edge_id_or_node_key"] for r in nchg}
    for e in edges:
        if e["edge_key"] not in edge_subjects and e["edge_key"] not in changed:
            bad.append("edge not in register: %s" % e["edge_id"])
    g.add("G8", "GAP_COVERAGE", not bad,
          "gap rows=%d reasons=%d/%d declared; zero-evidence nodes=%d; edges covered=%d/%d"
          % (len(gaps), len({r["reason"] for r in gaps}), len(M.GAP_REASONS),
             sum(1 for r in gaps if r["scope"] == "node"), len(edge_subjects | changed),
             len(edges)), bad)

    # ---- G9 never claim off/down from panel absence ----------------------------------------
    bad = []
    for r in allrows:
        if r["change"] in ("off", "down"):
            if not (r["detection_conditions"] or "").strip():
                bad.append("%s change=%s without detection conditions" % (r["assertion_id"],
                                                                         r["change"]))
    losses = sum(1 for r in gaps if r["reason"] == "detection_conditions_insufficient")
    g.add("G9", "NO_OFF_WITHOUT_DETECTION", not bad,
          "off/down assertions=%d; loss-side genes recorded as a gap instead=%d"
          % (sum(1 for r in allrows if r["change"] in ("off", "down")), losses), bad)

    # ---- G10 rebuild replay -----------------------------------------------------------------
    replay = {"performed": False}
    if not args.no_replay:
        tmp = tempfile.mkdtemp(prefix="mk_replay_")
        env = dict(os.environ, MK_OUTDIR=tmp)
        logs = []
        ok = True
        for s in ("m0_corpus_gene_index.py", "m1_nodes.py", "m2_node_markers.py",
                  "m3_edge_assertions.py", "m4_gap_register.py"):
            p = subprocess.run(["/usr/bin/python3", os.path.join(HERE, s)], env=env,
                               capture_output=True, text=True)
            logs.append("%s rc=%d" % (s, p.returncode))
            if p.returncode:
                ok = False
                logs.append(p.stderr[-400:])
                break
        differs = []
        if ok:
            for name in DATA_ARTEFACTS + ["NODE_CONTEXT_SOURCES.json", "GAP_SUMMARY.json"]:
                a = os.path.join(out, name)
                b = os.path.join(tmp, name)
                if not (os.path.isfile(a) and os.path.isfile(b)):
                    differs.append("%s missing on one side" % name)
                    continue
                ha = hashlib.sha256(open(a, "rb").read()).hexdigest()
                hb = hashlib.sha256(open(b, "rb").read()).hexdigest()
                if ha != hb:
                    differs.append(name)
        replay = {"performed": True, "build_ok": ok, "logs": logs,
                  "artefacts_compared": len(DATA_ARTEFACTS) + 2, "differing": differs}
        shutil.rmtree(tmp, ignore_errors=True)
        g.add("G10", "REBUILD_REPLAY", ok and not differs,
              "chain rebuilt into a scratch dir: %s; artefacts compared=%d differing=%d"
              % ("; ".join(logs), replay["artefacts_compared"], len(differs)), differs)
    else:
        g.add("G10", "REBUILD_REPLAY", True, "skipped by --no-replay", [])

    # ---- G11 no fabricated gene -------------------------------------------------------------
    gidx = {r["gene"] for r in M.read_tsv(os.path.join(out, "CORPUS_GENE_INDEX_v1.tsv"))}
    panel_genes = set()
    for lib, p in panels.items():
        for label, rec in p["labels"].items():
            panel_genes.update(rec["genes"])
            panel_genes.update(rec.get("subtype_anchor") or {})
    bad = [r["assertion_id"] + ":" + r["gene_symbol"] for r in allrows
           if r["gene_symbol"] not in gidx and r["gene_symbol"] not in panel_genes]
    g.add("G11", "NO_FABRICATED_GENE", not bad,
          "gene symbols in assertions=%d; unresolvable to the corpus index or a shipped panel=%d"
          % (len({r["gene_symbol"] for r in allrows}), len(bad)), bad)

    # ---- G12 recorded query set replay -----------------------------------------------------
    golden = {"performed": False}
    if os.path.isfile(GOLDEN) and not args.no_replay:
        gp = os.path.join(tempfile.mkdtemp(prefix="mk_golden_"), "golden_now.json")
        t0 = time.time()
        p = subprocess.run(["/usr/bin/python3", GOLDEN, gp], capture_output=True, text=True,
                           cwd=os.path.dirname(GOLDEN))
        golden["performed"] = True
        golden["rc"] = p.returncode
        golden["seconds"] = round(time.time() - t0, 1)
        golden["stdout_tail"] = (p.stdout or "")[-400:]
        if p.returncode == 0 and os.path.isfile(gp) and os.path.isfile(GOLDEN_RECORDED):
            now = json.load(open(gp))
            shutil.copy2(gp, os.path.join(M.WAVE, "ledgers", "golden_721_now.json"))
            before = json.load(open(GOLDEN_RECORDED))
            golden["now"] = now.get("stats")
            golden["recorded"] = before.get("stats")
            same = (now.get("stats", {}).get("off", {}).get("n")
                    == before.get("stats", {}).get("off", {}).get("n")
                    and now.get("stats", {}).get("off", {}).get("differ") == 0)
            g.add("G12", "GOLDEN721", same,
                  "recorded production queries replayed in %.1fs: n=%s identical=%s differ=%s "
                  "(recorded baseline differ=%s)"
                  % (golden["seconds"],
                     now.get("stats", {}).get("off", {}).get("n"),
                     now.get("stats", {}).get("off", {}).get("identical"),
                     now.get("stats", {}).get("off", {}).get("differ"),
                     before.get("stats", {}).get("off", {}).get("differ")),
                  [] if same else [str(p.stdout)[-300:]])
        else:
            g.add("G12", "GOLDEN721", False,
                  "the replay did not produce a comparable result (rc=%s)" % p.returncode,
                  [(p.stderr or "")[-300:]])
    else:
        g.add("G12", "GOLDEN721", True, "skipped (script absent or --no-replay)", [])

    # ---- G13 kb untouched ------------------------------------------------------------------
    bad, newest = [], 0.0
    for root in (M.MARKERS_DIR, M.MARKERS_DIR_REPO, os.path.join(M.KB, "link_registry"),
                 os.path.join(M.KB, "textbook_layer")):
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                p = os.path.join(dirpath, fn)
                try:
                    mt = os.stat(p).st_mtime
                except OSError:
                    continue
                newest = max(newest, mt)
                if mt >= SESSION_START:
                    bad.append(p)
    g.add("G13", "KB_UNTOUCHED", not bad,
          "kb/ files walked; newest mtime=%s; files written during this card=%d"
          % (time.strftime("%Y-%m-%d %H:%M", time.localtime(newest)), len(bad)), bad)

    verdict = "PASS" if all(c["status"] == "PASS" for c in g.checks) else "FAIL"
    doc = {"gate": "marker layer", "verdict": verdict,
           "n_checks": len(g.checks),
           "n_fail": sum(1 for c in g.checks if c["status"] != "PASS"),
           "counts": {c["code"]: {"status": c["status"], "n_offenders": c["n_offenders"]}
                      for c in g.checks},
           "checks": g.checks, "replay": replay, "golden": golden,
           "ontology": M.load_ontology()[1], "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
           "columns_node": list(nset[0].keys()) if nset else [],
           "columns_edge": list(nchg[0].keys()) if nchg else []}
    M.write_json(args.json, doc)
    lines = ["# Gate readout — marker layer", "",
             "verdict: **%s**  (%d checks, %d failed)" % (verdict, len(g.checks), doc["n_fail"]),
             "", "| check | name | status | n_offenders | detail |", "|---|---|---|---|---|"]
    for c in g.checks:
        lines.append("| %s | %s | %s | %d | %s |" % (c["code"], c["name"], c["status"],
                                                     c["n_offenders"],
                                                     c["detail"].replace("|", "/")))
    if replay.get("performed"):
        lines += ["", "Rebuild replay: %s; artefacts compared=%d, differing=%d."
                  % ("build ok" if replay["build_ok"] else "build FAILED",
                     replay["artefacts_compared"], len(replay["differing"]))]
    if golden.get("performed"):
        lines += ["", "Recorded query set: rc=%s in %.1fs; now %s; recorded %s."
                  % (golden.get("rc"), golden.get("seconds", 0), golden.get("now"),
                     golden.get("recorded"))]
    open(os.path.join(out, "GATE_READOUT.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[2:6]))
    for c in g.checks:
        print("  %-4s %-26s %s  offenders=%d" % (c["code"], c["name"], c["status"],
                                                 c["n_offenders"]))
    print("verdict:", verdict, "->", args.json)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())