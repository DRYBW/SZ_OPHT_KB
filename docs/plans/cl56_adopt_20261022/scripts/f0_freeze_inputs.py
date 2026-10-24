# -*- coding: utf-8 -*-
"""f0_freeze_inputs.py -- read-only freeze of every input the CL-56 adoption wave reads.

Writes out/INPUT_MANIFEST.json: for each input, its absolute path, role, size, mtime and sha256.
Nothing is modified. Zero network. Run before the pre-registration document is written so that the
document can name every input by its hash.

Run: /usr/bin/python3 f0_freeze_inputs.py
"""
import hashlib
import json
import os
import time

REPO = "/home/ubuntu/EYEKB_REPO"
OSS = "/mnt/D/EyeKB/plans/oss_check_20261019"
CLD = "/mnt/D/EyeKB/plans/cl_depth_devlineage_20261021"
SUB = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
NRE = "/mnt/D/EyeKB/plans/noregr_20261022"
ANT = "/mnt/D/EyeKB/plans/antseg_fill_20261020"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")


def sha256_file(path, cap=None):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
            n += len(chunk)
            if cap and n >= cap:
                return h.hexdigest() + "+PARTIAL(%d)" % n
    return h.hexdigest()


def rec(rows, path, role, hash_file=True):
    p = path if os.path.isabs(path) else os.path.join(REPO, path)
    e = {"path": p, "role": role, "exists": os.path.exists(p)}
    if e["exists"]:
        st = os.stat(p)
        e["bytes"] = st.st_size
        e["mtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
        e["sha256"] = sha256_file(p) if (hash_file and st.st_size < (3 << 30)) else "NOT_HASHED(large)"
    rows.append(e)
    return e


def main():
    rows = []
    # the recorded set (the measurement ruler's own inputs)
    rec(rows, OSS + "/ledger_v1/ledger_cluster_level.tsv", "I2 recorded reference labels + n_cells, one row per cluster")
    reports = []
    for vol in sorted(os.listdir(OSS + "/dl/results")):
        p = os.path.join(OSS, "dl", "results", vol, "annotation_evidence_report.json")
        if os.path.exists(p):
            reports.append(rec(rows, p, "I1 recorded per-cluster query window (volume %s)" % vol))
    # the harness (reused unedited)
    rec(rows, NRE + "/scripts/wave_common.py", "I7 harness: rulers + replay engine + acceptance gate")
    rec(rows, NRE + "/scripts/n3_harness.py", "I7 harness driver")
    rec(rows, NRE + "/PREREG_NOREGRESSION_20261022.md", "I7 the harness's own pre-registration (rulers, floor)")
    # the wave that produced the candidates
    rec(rows, CLD + "/out/CHILD_TERM_CANDIDATES.json", "I8 the 56 (parent, child) candidates with corpus support")
    rec(rows, CLD + "/out/CHILD_TERM_CANDIDATES.tsv", "I8 same, tabular")
    rec(rows, CLD + "/out/GRANULARITY_FOURWAY_721.tsv", "I8 per-cluster four-way relation reading (721 rows)")
    rec(rows, CLD + "/out/ONT_CLOSURE_is_a.tsv", "I8 the audited is_a closure")
    rec(rows, CLD + "/out/ONT_LABELMAP_V2.tsv", "I8 our label -> CL map with provenance")
    rec(rows, CLD + "/REPORT.md", "I8 the wave report (gate A 9 rules / 0 failures)")
    rec(rows, CLD + "/scripts/ont_nav.py", "I8 the ontology navigation module (closure, relation)")
    # the pre-registered floor wave
    rec(rows, SUB + "/out/pair_table.json", "I9 the 923 (parent, child) readiness rows: tiers + discriminating genes")
    rec(rows, SUB + "/out/pair_table.tsv", "I9 same, tabular")
    rec(rows, SUB + "/out/cost_table.json", "I9 demand / gain / keep / loss per pair")
    rec(rows, SUB + "/PREREG_SUBDIVISION_READINESS_20261022.md", "I9 the pre-registered floors (T-GENES/T-OBS/T-STATE)")
    rec(rows, SUB + "/PREREG_ANNEX_A_OPERATIONS_20261022.md", "I9 the operational annex")
    # the shipped tree
    rec(rows, "mcp_server/eyekb_core.py", "I3 the shipped service core (the file the wiring edits)")
    rec(rows, "kb/markers/markers_cl_alignment_v2_unified.json", "I6 the KB label -> CL map (the naming layer)")
    rec(rows, "kb/ontology/cl/releases/2026-06-08/cl-base.obo", "I6 the frozen Cell Ontology snapshot")
    rec(rows, "kb/baselines/_tissue_class_crosswalk_v1.json", "I5 the tissue exclusion table (untouched)")
    rec(rows, "kb/markers/markers_v10_antseg_increment.json", "I4 a shipped increment carrying child-term entries (reference)")
    rec(rows, "kb/markers/markers_v14_subtype_second_increment.json", "I4 a shipped increment carrying child-term entries (reference)")
    rec(rows, "docs/W3_MANIFEST.sha256", "the repository manifest (re-taken last)")
    rec(rows, "docs/RELEASE_IDENTITY.json", "the release identity record")
    # the corpus and the assay vocabulary (used only for the panel source's vocabulary floor)
    rec(rows, ANT + "/out/gene_vocab.json", "I10 the assay gene vocabulary (the panel's measurability floor)")
    rec(rows, "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet",
        "I11 the served in-repo literature corpus (not re-mined by this wave; identity only)", hash_file=False)

    doc = {"generated_by": "plans/cl56_adopt_20261022/scripts/f0_freeze_inputs.py",
           "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
           "n_volume_reports": len(reports), "inputs": rows}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "INPUT_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=str)
    bad = [r for r in rows if not r["exists"]]
    print("frozen inputs: %d (%d volume reports); missing: %d" % (len(rows), len(reports), len(bad)))
    for r in bad:
        print("  MISSING", r["path"])
    print("wrote out/INPUT_MANIFEST.json")


if __name__ == "__main__":
    main()