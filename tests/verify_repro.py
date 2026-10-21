#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB mirror-repo homogeneity verifier (VERIFY contract G3).
Do the retrieval results produced on this machine match the distribution of the repo's anchors? One command answers.

Usage (from repo root):
  python tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim
Criterion: the top5 PMID sequence of all 41 cases is position-by-position identical to tests/REPRO_EXPECTED.json.
Exit codes: 0=PASS (homogeneous); 1=FAIL (prints per-case diffs and the three-layer triage order);
            3=INCONCLUSIVE (the run could not be evaluated — the anchors are dense-retrieval results and
              this machine fell back to lexical search, so the comparison would be meaningless).
Dependencies = requirements.repro.txt; engine = clients/ocularkb/rag/scripts/stage3_retrieve.py (dual-format branch).

Before comparing anything, this script checks whether the retrieval engine actually ran in its dense
mode. The anchors were produced with BAAI/bge-large-en-v1.5 on CPU; if that model (or the sentence
transformers dependency) is unavailable, the engine silently degrades to lexical search and every
PMID sequence differs. Reporting that as "retrieval drift" sends the reader after a scientific cause
that is not there, so the two outcomes are kept apart: a degraded run is INCONCLUSIVE, not a failure.
"""
import argparse, json, os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-dir", default=os.path.join(ROOT, "literature_db", "v2.4.2_2026-09_slim"))
    ap.add_argument("--expected", default=os.path.join(ROOT, "tests", "REPRO_EXPECTED.json"))
    a = ap.parse_args()

    if not os.path.isdir(a.db_dir):
        print("FAIL: corpus directory not found", a.db_dir)
        print("Triage order: do G2 first — download the prebuilt release from Releases and run sha256sum -c (see README 5-minute quickstart, step 2). Products of a rebuild path do not count (contract G2).")
        return 1

    spec = importlib.util.spec_from_file_location(
        "s3", os.path.join(ROOT, "clients", "ocularkb", "rag", "scripts", "stage3_retrieve.py"))
    s3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s3)

    exp = json.load(open(a.expected, encoding="utf-8"))["results"]
    mis, n, degraded = [], 0, []
    for c in exp:
        r = s3.retrieve(c["cell_type"], species=c.get("species"), top_k=5,
                        tissue=c.get("tissue"), db_dir=a.db_dir)
        if isinstance(r, dict) and r.get("degraded"):
            degraded.append((r.get("retrieval_mode") or "degraded"))
        hits = r["results"] if isinstance(r, dict) and "results" in r else r
        got = [str(h.get("pmid")) for h in hits[:5]]
        n += 1
        if got != [str(p) for p in c["top_pmids"]]:
            mis.append({"case": f'{c["cell_type"]}/{c.get("species")}/{c.get("tissue")}',
                        "expected": c["top_pmids"], "got": got})

    if degraded:
        print(f"REPRO INCONCLUSIVE: {len(degraded)}/{n} cases ran in '{degraded[0]}' mode, "
              "not the dense mode the anchors were built with.")
        print("Nothing about retrieval quality can be read from this run, so no drift is reported.")
        print("Fix the precondition first, then re-run:")
        print("  - install the G1-locked dependencies: pip install -r requirements.repro.txt")
        print("  - make the embedding model discoverable: put bge-large-en-v1.5 under models/, "
              "or set EYEKB_MODEL_DIR to it")
        print("  - or point the gate at the interpreter that already has them: "
              "EYEKB_G3_PY=/path/to/python bash tests/run_gates.sh")
        return 3

    ok = not mis
    print(f"REPRO {'PASS' if ok else 'FAIL'}: {n-len(mis)}/{n} cases with position-by-position identical top5")
    if mis:
        print(json.dumps(mis[:10], ensure_ascii=False, indent=1))
        print("Triage order: does the G2 prebuilt-release sha match -> are G1 dependency versions per requirements.repro.txt -> is the model BAAI/bge-large-en-v1.5.")
        print("Do not adjust criteria or tune parameters to force a pass: the drift itself is the information to report (docs/VERIFY_CONTRACT.md §4).")
    return 0 if ok else 1

sys.exit(main())
