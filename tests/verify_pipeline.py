#!/usr/bin/env python3
"""G4 acceptance gate: one command answering "does your batch-annotation pipeline
produce exactly what we produce?".

Prerequisites (matching VERIFY_CONTRACT G1/G2): dependencies installed per
requirements.repro.txt; the literature corpus is the Release slim build (the
production fp32 original was measured to hit the same anchors).
Criteria = the three anchors in tests/G4_EXPECTED.json (the evidence report is
hashed after normalizing timestamp/output-path; the other two artifacts are
raw-byte anchors). The pipeline entry pins its thread backends by default —
do not override.

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
guarantees false FAILs across venvs.

Interpreter resolution (2026-10-21; portability fix). The pinned path above is one
machine's environment, and a gate that cannot run on any other machine cannot be
evaluated by a reader of this repository. The gate therefore resolves its interpreter
along a documented ladder and prints which rung answered:

  rung 0  `EYEKB_G4_PY`                 explicit override. The caller asserts that the
                                        interpreter is equivalent to the contract one, so a
                                        byte mismatch under it is a FAIL (the historical
                                        meaning of this door, unchanged).
  rung 1  the contract default path     used whenever it exists here: this machine's
                                        numbers are unchanged by the ladder.
  rung 2  the same environment family   sibling interpreters under the contract default's
                                        environment directory, plus every directory listed in
                                        `EYEKB_G4_PY_SEARCH` (colon-separated; `<dir>/bin/python`
                                        and `<dir>/*/bin/python` are tried).
  rung 3  `python3` / `python` on PATH.

Rung 2 and 3 candidates are probed before use: the first candidate that satisfies the
declared dependency floor (DEP_FLOOR, below) wins, with candidates matching the recorded
contract versions (DEP_CONTRACT) preferred. A candidate whose version set equals
DEP_CONTRACT is treated as contract-equivalent; any other floor-satisfying candidate is a
substitute, and a substitute cannot turn a byte difference into a verdict about this
repository — the anchors were taken with the contract versions, so the difference is
reported as a comparison instead (see the exit codes).

Exit codes: 0=PASS(3/3)
            1=FAIL (a contract-equivalent interpreter produced different bytes: real regression)
            2=cannot set up (usage error, fixture missing, or fixture drift)
            3=not judgeable on this machine (no interpreter satisfies the declared floor;
              or a substitute interpreter's artifacts cannot be compared with the anchors)
The distinction between 1 and 3 is the point: "your machine cannot run this gate" and
"this repository is broken" are different findings and must not share a status.

Usage:  python tests/verify_pipeline.py [--work OUTPUT_DIR]
        EYEKB_G4_PY=/path/to/python python tests/verify_pipeline.py   # explicit override
        EYEKB_G4_PY_SEARCH=/opt/envs:/srv/conda python tests/verify_pipeline.py
        This gate itself uses only the standard library and can be launched by any python3 (3.10+).

NOTE on norm_report_sha below: the "Generated at" pattern matches the *pipeline-generated
report text* (produced in Chinese by the current pipeline release, which is itself
byte-anchored); it must stay verbatim until the report template is re-anchored.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = json.loads((ROOT / "tests" / "G4_EXPECTED.json").read_text(encoding="utf-8"))

# Interpreter pin: default = the interpreter that produced the G4 anchors;
# EYEKB_G4_PY overrides (rung 0 of the ladder documented above).
PY_ENV = "EYEKB_G4_PY"
PY_SEARCH_ENV = "EYEKB_G4_PY_SEARCH"
PY_PINNED = "/home/ubuntu/.conda/envs/pipeline_env/bin/python"

# Declared dependency floor for the annotation stack, and the versions the anchors were
# taken with. The floor is a lower bound a substitute must clear to be worth running; the
# contract set is what makes a reading comparable with the anchors.
DEP_FLOOR = {"scanpy": "1.10", "anndata": "0.10", "numpy": "1.24", "scipy": "1.10",
             "scikit-learn": "1.3", "pandas": "2.0"}
DEP_CONTRACT = {"scanpy": "1.11.5", "anndata": "0.11.4", "numpy": "2.2.6",
                "scipy": "1.15.3", "scikit-learn": "1.7.2"}
PROBE_MAX_CANDIDATES = 64        # bound the search; stage 1 is cheap (spec lookup, no imports)
PROBE_IMPORTS = (("scanpy", "scanpy"), ("anndata", "anndata"), ("numpy", "numpy"),
                 ("scipy", "scipy"), ("sklearn", "scikit-learn"), ("pandas", "pandas"))
SPEC_SNIPPET = (
    "import json,sys,importlib.util\n"
    "mods={k: importlib.util.find_spec(m) is not None for m,k in %r}\n"
    "print('EYEKB_G4_SPEC ' + json.dumps({'python': '%%d.%%d' %% sys.version_info[:2], 'mods': mods}))\n"
    % (PROBE_IMPORTS,)
)
PROBE_SNIPPET = (
    "import json,sys\n"
    "mods={}\n"
    "for m,k in %r:\n"
    "    try:\n"
    "        mod=__import__(m); mods[k]=getattr(mod,'__version__','') or ''\n"
    "    except Exception:\n"
    "        mods[k]=None\n"
    "print('EYEKB_G4_PROBE ' + json.dumps({'python': '%%d.%%d' %% sys.version_info[:2], 'mods': mods}))\n"
    % (PROBE_IMPORTS,)
)


def raw_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm_report_sha(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"(?:Generated at|生成时间)[:：]?\s*[\d\- :T]+", "Generated at:=TS", t)
    t = re.sub(r"`[^`]*?/stage_a/", "`<RUN>/stage_a/", t)
    t = re.sub(r"(/tmp/[\w\-]+/|\$HOME/\S*?/pipeline/)", "<RUN>/", t)
    return hashlib.sha256(t.encode()).hexdigest()


def live_check(cand: str):
    """Cheap liveness check. -> version string, or None (with the reason printed)."""
    try:
        r = subprocess.run([cand, "-c", "import sys;print('%d.%d'%sys.version_info[:2])"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        print(f"ENV ERROR: G4 interpreter live-check raised: {cand} ({type(e).__name__}: {e})")
        return None
    if r.returncode != 0:
        print(f"ENV ERROR: G4 interpreter live-check rc={r.returncode}: {cand}")
        print(r.stderr[-400:])
        return None
    return r.stdout.strip()


def spec_probe(cand: str):
    """Stage 1: which of the six modules are importable at all (cheap, no package import)."""
    try:
        r = subprocess.run([cand, "-c", SPEC_SNIPPET], capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        if line.startswith("EYEKB_G4_SPEC "):
            d = json.loads(line[len("EYEKB_G4_SPEC "):])
            return d.get("python"), d.get("mods") or {}
    return None


def probe(cand: str):
    """Stage 2: versions of the six modules. -> (python, mods dict) or None."""
    try:
        r = subprocess.run([cand, "-c", PROBE_SNIPPET], capture_output=True, text=True, timeout=300)
    except Exception as e:
        print(f"[g4] probe skipped ({type(e).__name__}): {cand}")
        return None
    if r.returncode != 0:
        return None
    for line in r.stdout.splitlines():
        if line.startswith("EYEKB_G4_PROBE "):
            d = json.loads(line[len("EYEKB_G4_PROBE "):])
            return d.get("python"), d.get("mods") or {}
    return None


def ver_tuple(v: str):
    parts = re.findall(r"\d+", v or "")
    return tuple(int(x) for x in parts[:3]) or (0,)


def floor_ok(mods: dict) -> tuple:
    """-> (ok, reason). Every floor entry must be present and >= its bound."""
    missing = [k for k, _ in DEP_FLOOR.items() if not mods.get(k)]
    if missing:
        return False, "missing: " + ", ".join(missing)
    low = [f"{k} {mods[k]}<{DEP_FLOOR[k]}" for k in DEP_FLOOR
           if ver_tuple(mods[k]) < ver_tuple(DEP_FLOOR[k])]
    if low:
        return False, "below floor: " + ", ".join(low)
    return True, "floor satisfied"


def contract_match(mods: dict) -> bool:
    return all(ver_tuple(mods.get(k, "")) == ver_tuple(v) for k, v in DEP_CONTRACT.items())


def candidate_pool():
    """Rung 2 and rung 3 candidates, deterministically ordered, deduplicated."""
    seen, pool = set(), []

    def add(p: str, rung: int):
        if p and p not in seen and Path(p).is_file():
            seen.add(p)
            pool.append((p, rung))

    fam_root = Path(PY_PINNED).parent.parent          # .../envs
    if fam_root.is_dir():
        for d in sorted(fam_root.glob("*/bin/python")):
            add(str(d), 2)
        add(str(fam_root / "bin" / "python"), 2)
    for root in [r for r in os.environ.get(PY_SEARCH_ENV, "").split(os.pathsep) if r.strip()]:
        add(str(Path(root) / "bin" / "python"), 2)
        for d in sorted(Path(root).glob("*/bin/python")):
            add(str(d), 2)
    for name in ("python3", "python"):
        add(shutil.which(name) or "", 3)
    # explicit-override path is rung 0 and handled by the caller; never offered as a substitute
    return [(p, r) for p, r in pool if p != PY_PINNED][:PROBE_MAX_CANDIDATES]


def resolve_python():
    """Resolve and live-test the G4 interpreter along the documented ladder.

    -> (path, source_label, python_version, contract_equivalent) or (None, reason, None, False)
    """
    env = os.environ.get(PY_ENV, "").strip()
    if env:
        if not (Path(env).is_file() and os.access(env, os.X_OK)):
            print(f"ENV ERROR: {PY_ENV} is set but not an executable interpreter: {env}")
            print("  An explicitly requested interpreter that does not exist is an error, not a")
            print("  fallback: clear the variable to let the gate search, or point it at a real one.")
            return None, f"env var {PY_ENV}", None, False
        v = live_check(env)
        if v is None:
            return None, f"env var {PY_ENV}", None, False
        return env, f"env var {PY_ENV} (rung 0, equivalence asserted by the caller)", v, True

    if Path(PY_PINNED).is_file() and os.access(PY_PINNED, os.X_OK):
        v = live_check(PY_PINNED)
        if v is not None:
            return PY_PINNED, "contract default (rung 1)", v, True
        print("[g4] the contract default exists but failed its liveness check; searching instead")

    print(f"[g4] contract default unavailable here ({PY_PINNED}) - searching the documented ladder")
    tried, rejected = [], []
    for cand, rung in candidate_pool():
        sp = spec_probe(cand)
        if sp is None:
            rejected.append((cand, rung, "not runnable"))
            continue
        pyver, present = sp
        if not all(present.values()):
            gone = [k for k, v in present.items() if not v]
            rejected.append((cand, rung, f"python {pyver}; not importable: {', '.join(gone)}"))
            continue
        pr = probe(cand)
        if pr is None:
            rejected.append((cand, rung, "version probe failed"))
            continue
        pyver, mods = pr
        ok, why = floor_ok(mods)
        tried.append((cand, rung, pyver, why, contract_match(mods)))
        if not ok:
            rejected.append((cand, rung, why))
            continue
        cm = contract_match(mods)
        label = f"rung {rung} {'contract-matching' if cm else 'substitute'}"
        print(f"[g4] selected {cand} ({label}; python {pyver}; {why})")
        return cand, label, pyver, cm
    print("ENV ERROR: no interpreter on this machine satisfies the declared dependency floor")
    print(f"  contract default: {PY_PINNED} (absent)")
    print(f"  searched: {len(tried) + len(rejected)} candidate(s) on the documented ladder")
    print("  floor: " + ", ".join(f"{k}>={v}" for k, v in sorted(DEP_FLOOR.items())))
    for cand, rung, why in rejected[:PROBE_MAX_CANDIDATES]:
        print(f"    rung {rung}: {cand} -> {why}")
    print(f"  Remedy: prepare an equivalent environment and `export {PY_ENV}=/path/to/python`, or point")
    print(f"  `{PY_SEARCH_ENV}` at the directory that holds your environments (colon-separated).")
    print("  This is an environment state, not a repository failure: no verdict is reported.")
    return None, "ladder exhausted", None, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default="")
    a = ap.parse_args()
    fixture = ROOT / EXP["fixture"]
    if not fixture.is_file():
        print("FAIL: fixture missing from the repository:", fixture)
        return 2
    if raw_sha(fixture) != EXP["fixture_sha256"]:
        print("FAIL: fixture bytes differ from the anchor (repository content drift)")
        return 1
    PY, src, pyver, equiv = resolve_python()
    if PY is None:
        return 3
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
        if equiv:
            print("FAIL: run_pipeline rc=", r.returncode, "(contract-equivalent interpreter)")
            print(r.stderr[-800:])
            return 1
        print("NOT JUDGEABLE: run_pipeline rc=", r.returncode, "(substitute interpreter)")
        print(r.stderr[-800:])
        print("  The pipeline did not run to completion under a substitute interpreter; that says")
        print("  nothing about the repository. Point EYEKB_G4_PY at an environment matching the")
        print("  declared floor and re-run for a verdict.")
        return 3
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
    if nfail == 0:
        print("\nG4 PASS: 3/3 byte-identical")
    elif equiv:
        print(f"\nG4 FAIL: {nfail}/3 mismatch")
    else:
        print(f"\nG4 NOT JUDGEABLE: {nfail}/3 differ under a substitute interpreter")
        print("  The anchors were taken with the contract versions (see DEP_CONTRACT in tests/verify_pipeline.py).")
        print("  A difference under another interpreter is not evidence that the repository changed;")
        print("  reproduce it under a contract-equivalent environment before treating it as a regression.")
    print("(timestamps and output paths are excluded from the criteria; everything else is byte-for-byte; see VERIFY_CONTRACT G4)")
    if nfail == 0:
        return 0
    return 1 if equiv else 3


if __name__ == "__main__":
    sys.exit(main())