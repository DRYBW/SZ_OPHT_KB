#!/usr/bin/env python3
"""G4 acceptance gate: one command answering "does your batch-annotation pipeline
produce exactly what we produce?".

Prerequisites (matching VERIFY_CONTRACT G1/G2): dependencies installed per
requirements.repro.txt; the literature corpus is the Release slim build (the
production fp32 original was measured to hit the same anchors).
Criteria = the three anchors in tests/G4_EXPECTED.json (the evidence report is
hashed after normalizing timestamp/output-path; the other two artifacts are
raw-byte anchors). The pipeline entry pins its thread backends by default — do
not override.

The interpreter is part of the contract (KB10d, 2026-10-01): the interpreter
this gate uses to drive the pipeline is **pinned to pipeline_env** (override via
`EYEKB_G4_PY`, see below); the caller's `sys.executable` is never inherited.
Reason: the bytes of `stage_a/processed.h5ad` depend on the float-writing paths
of anndata/numpy/scipy/sklearn. Measured with identical code and fixture:
pipeline_env (scanpy 1.11.5 / anndata 0.11.4 / numpy 2.2.6 / scipy 1.15.3 /
sklearn 1.7.2) -> anchor `dbc657…`; training-venv (scanpy 1.12.2 / anndata
0.12.19 / numpy 2.4.6) -> `f7a461…`; offline venv (anndata 0.13.2) -> `10cfbe…`
(the differences concentrate in the float32 last bits of X_pca/X_umap/var/dispersions;
the obs/leiden/counts layers are identical). Inheriting the caller's interpreter
guarantees false FAILs across venvs. A missing/non-executable pinned interpreter
is an environment error (rc=2 with the remedy printed) — it never falls back
silently to the current interpreter.

Usage:  python tests/verify_pipeline.py [--work OUTPUT_DIR]
        EYEKB_G4_PY=/path/to/python python tests/verify_pipeline.py   # explicit override
        This gate itself uses only the standard library and can be launched by any python3 (3.10+).
Exit codes: 0=PASS(3/3)   1=FAIL (per-artifact got/expected printed)   2=environment error

NOTE on norm_report_sha below: the "Generated at" pattern matches the *pipeline-generated
report text* (produced in Chinese by the current pipeline release, which is itself
byte-anchored); it must stay verbatim until the report template is re-anchored.
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = json.loads((ROOT / "tests" / "G4_EXPECTED.json").read_text(encoding="utf-8"))

# Interpreter pin: default = the interpreter that produced the G4 anchors;
# EYEKB_G4_PY overrides (the only fallback door).
PY_ENV = "EYEKB_G4_PY"
PY_PINNED = "/home/ubuntu/.conda/envs/pipeline_env/bin/python"


def raw_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm_report_sha(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"(?:Generated at|生成时间)[:：]?\s*[\d\- :T]+", "Generated at:=TS", t)
    t = re.sub(r"`[^`]*?/stage_a/", "`<RUN>/stage_a/", t)
    t = re.sub(r"(/tmp/[\w\-]+/|\$HOME/\S*?/pipeline/)", "<RUN>/", t)
    return hashlib.sha256(t.encode()).hexdigest()


def resolve_python():
    """Resolve and live-test the G4 pipeline interpreter. Returns (path, src, ver); path=None means environment error."""
    env = os.environ.get(PY_ENV, "").strip()
    cand, src = (env, f"env var {PY_ENV}") if env else (PY_PINNED, "contract default")
    if not (Path(cand).is_file() and os.access(cand, os.X_OK)):
        print(f"ENV ERROR: G4 interpreter unavailable (source={src}): {cand}")
        print("  This gate's criteria are anchored to pipeline_env (see docs/VERIFY_CONTRACT.md G4);")
        print("  a missing/non-executable interpreter is an environment error —")
        print("  it never silently switches to the current interpreter, which would guarantee a false FAIL.")
        print(f"  Remedy: prepare an equivalent environment, then `export {PY_ENV}=/path/to/python` and rerun.")
        return None, src, None
    try:
        r = subprocess.run([cand, "-c", "import sys;print('%d.%d'%sys.version_info[:2])"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"ENV ERROR: G4 interpreter live-check raised (source={src}): {cand} ({type(e).__name__}: {e})")
        return None, src, None
    if r.returncode != 0:
        print(f"ENV ERROR: G4 interpreter live-check rc={r.returncode} (source={src}): {cand}")
        print(r.stderr[-400:])
        return None, src, None
    return cand, src, r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="")
    a = ap.parse_args()
    fixture = ROOT / EXP["fixture"]
    if not fixture.is_file():
        print("ENV ERROR: fixture missing:", fixture)
        return 2
    if raw_sha(fixture) != EXP["fixture_sha256"]:
        print("FAIL: fixture bytes differ from the anchor (repository content drift)")
        return 1
    PY, src, pyver = resolve_python()
    if PY is None:
        return 2
    print(f"[g4] interpreter: {PY} (python {pyver}, source: {src})")
    if PY != PY_PINNED:
        print(f"[g4] note: interpreter is not the contract default ({PY_PINNED}) — the G4 anchors")
        print("       come from the default contract environment; differences under a non-default interpreter are not new findings.")
    work = Path(a.work) if a.work else Path(tempfile.mkdtemp(prefix="g4_verify_"))
    cmd = [PY, str(ROOT / "pipeline" / "run_pipeline.py"),
           "--out", str(work), "--seed", EXP["seed"],
           "--input", str(fixture), "--species", "human",
           "--tissue", "fibrovascular_membrane"]
    print("[g4] running pipeline (~1-2 minutes, fully offline)...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ENV ERROR: run_pipeline rc=", r.returncode)
        print(r.stderr[-800:])
        return 2
    checks = [
        ("stage_a/processed.h5ad", lambda p: raw_sha(p)),
        ("decisions_template.csv", lambda p: raw_sha(p)),
        ("annotation_evidence_report.md", lambda p: norm_report_sha(p)),
    ]
    nfail = 0
    for name, fn in checks:
        key = name + ("__normalized" if "report" in name else "")
        target = EXP["anchors"][key]
        got = fn(work / name)
        ok = (got == target)
        nfail += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + key)
        if not ok:
            print("   got:     ", got)
            print("   expected:", target)
    print(f"\nG4 {'PASS: 3/3 byte-identical' if nfail == 0 else f'FAIL: {nfail}/3 mismatch'}")
    print("(timestamps and output paths are excluded from the criteria; everything else is byte-for-byte; see VERIFY_CONTRACT G4)")
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
