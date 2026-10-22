#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m0 -- freeze the inputs of this wave by content (sha256), and pin the in-scope row set.

Everything downstream quotes a number that came from one of these files; the manifest is what makes
"which bytes" answerable.  Also re-derives the in-scope set mechanically (the rule is in PREREG §2)
and asserts it is exactly 26 rows / 16 subtypes, so a drifting upstream result is caught here rather
than discovered in the report.

Writes out/INPUT_MANIFEST.json.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10"
REPO = "/home/ubuntu/EYEKB_REPO"

INPUTS = [
    (os.path.join(CONS, "REPORT.md"), "the frozen wave's report (read-only, never rewritten)"),
    (os.path.join(CONS, "PREREG_CONSENSUS_SUBTYPE_20261022.md"), "the frozen pre-registration (thresholds)"),
    (os.path.join(CONS, "SUPERSEDED_LOGS_20261022.md"), "which logs back the report"),
    (os.path.join(CONS, "scripts", "c3_separation.py"), "THE RULER -- run unmodified"),
    (os.path.join(CONS, "scripts", "c2_observability.py"), "the observability pass (re-run for reference)"),
    (os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json"), "the frozen 56-row result"),
    (os.path.join(CONS, "out", "SUBTYPE_SEPARATION.tsv"), "the frozen 56-row result (tabular)"),
    (os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json"), "the frozen rows fed to the ruler"),
    (os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY.tsv"), "the frozen budget table"),
    (os.path.join(CONS, "out", "_marker_genes.json"), "the frozen gene list the ruler tests"),
    (os.path.join(CONS, "out", "G1_photoreceptor_bipolar.json"), "the 94-entry literature list (ch 1)"),
    (os.path.join(CONS, "out", "G2_amacrine_horizontal_rgc.json"), "the 94-entry literature list (ch 2)"),
    (os.path.join(CONS, "out", "G3_glia_vascular_support.json"), "the 94-entry literature list (ch 3)"),
    (os.path.join(CORPUS, "chunks.parquet"), "channel A: the literature corpus (v2.6-dev)"),
    (os.path.join(CORPUS, "papers.jsonl"), "channel A: paper records (PMID/DOI resolution)"),
    (os.path.join(CORPUS, "manifest.yaml"), "channel A: corpus provenance"),
    ("/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json", "the assay gene vocabulary (L2)"),
    (os.path.join(REPO, "kb", "ontology", "cl", "releases", "2026-06-08", "cl-base.obo"),
     "the frozen Cell Ontology snapshot"),
    (os.path.join(REPO, "kb", "markers", "markers_cl_alignment_v2_unified.json"), "KB class -> CL map"),
    (os.path.join(REPO, "mcp_server", "eyekb_core.py"), "the shipped service core (pre-change sha)"),
    (os.path.join(REPO, "tests", "probe_tool_panel_identity.py"), "the legacy tool-panel identity probe"),
    (os.path.join(REPO, "tests", "fixtures", "tool_panel_baseline.json"), "the probe's recorded baseline"),
    (os.path.join(WAVE, "PREREG_SUBTYPE_SECOND_MARKER_20261022.md"), "THIS WAVE's pre-registration"),
]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    missing = []
    for p, role in INPUTS:
        if not os.path.exists(p):
            missing.append({"path": p, "role": role})
            continue
        rows.append({"path": p, "role": role, "bytes": os.path.getsize(p), "sha256": sha256_file(p)})

    # the in-scope set, re-derived mechanically from the frozen result
    sep = json.load(open(os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json"), encoding="utf-8"))
    scope = [r for r in sep if r["result"] == "not_separated"
             and str(r.get("reason", "")).startswith("1 marker(s) cleared the gate")]
    subtypes = sorted({r["subtype"] for r in scope})
    volumes = sorted({r["volume"] for r in scope})
    assert len(sep) == 56 and len(scope) == 26 and len(subtypes) == 16, \
        "in-scope set drifted: rows=%d scope=%d subtypes=%d" % (len(sep), len(scope), len(subtypes))

    doc = {"probe": "m0_freeze_inputs.py", "wave": WAVE,
           "n_inputs": len(rows), "inputs": rows, "missing_inputs": missing,
           "in_scope_rule": "result == not_separated AND reason.startswith('1 marker(s) cleared the gate')",
           "in_scope_rows": [{"volume": r["volume"], "subtype": r["subtype"], "n_cells": r["n_cells"],
                              "reason": r["reason"]} for r in scope],
           "in_scope_n_rows": len(scope), "in_scope_n_subtypes": len(subtypes),
           "in_scope_subtypes": subtypes, "in_scope_volumes": volumes,
           "out_of_scope_rows": len(sep) - len(scope)}
    json.dump(doc, open(os.path.join(OUT, "INPUT_MANIFEST.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("inputs frozen: %d (missing %d)" % (len(rows), len(missing)))
    print("in-scope rows=%d subtypes=%d volumes=%s" % (len(scope), len(subtypes), volumes))
    for m in missing:
        print("  MISSING", m["path"])
    for s in subtypes:
        print("   subtype:", s)
    print("wrote", os.path.join(OUT, "INPUT_MANIFEST.json"))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())