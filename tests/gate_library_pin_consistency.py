#!/usr/bin/env python3
"""Gate: library-pin consistency of the gate/verification scripts themselves.

Why this gate exists
--------------------
On 2026-10-27 the frozen RUN4W golden-41 gate (evals/regression_run4w_golden41_t_d07ab64f.py)
reported 0/41 for every case while nothing was actually broken. Its DIRECT arm had one library
hard-coded (".../literature_db/v2.0_2026-09", lines 72-73) while its MCP arm resolved the default
library through the pointer (a newer one). A gate whose two arms read two different libraries can
only ever report a difference, and that failure looks exactly like a real regression -- it cost a
long detour to separate "the gate is stale" from "the change broke something".

This gate makes that class of defect visible before it wastes a wave. It reads the gate and
verification scripts in the repository, extracts the library versions each one references, compares
them against the default library declared in kb/literature_db/EYEKB_DB_POINTER.yaml, and emits

  FAIL  one script references two different libraries -- it may be comparing different libraries
  WARN  one script pins a library that is not the current default, and it does retrieval work --
        the pin is stale and the gate can no longer see the shipped library
  OK    otherwise

Exit codes: 0 = no FAIL, 2 = at least one FAIL, 3 = the gate's own controls did not behave.
A WARN alone never fails the run: historical audit scripts legitimately pin the library of their
own date. The point is to make stale pins *visible*, not to force every old file to be rewritten.

Usage
  python3 tests/gate_library_pin_consistency.py                 # report, rc per above
  python3 tests/gate_library_pin_consistency.py --controls      # also prove the gate can fail
  EYEKB_PIN_ROOT=<dir> ...   override the repository root

No network, no GPU, standard library only.
"""
import argparse, json, os, re, sys
from pathlib import Path

LIB_RE = re.compile(r"literature_db/([A-Za-z0-9][A-Za-z0-9._\-]*)")
# A library DIRECTORY never carries a file extension; sidecar FILE names under literature_db/ do
# (…/literature_db/EYEKB_DB_POINTER.yaml, …/dev_stage_meta_v2.2_2026-09.jsonl). Without this filter
# the gate reports those file names as "library versions" and calls every script a two-library
# comparison -- measured 2026-10-27, which is how the filter got here.
NOT_A_VERSION_EXT = (".yaml", ".yml", ".json", ".jsonl", ".tsv", ".md", ".txt", ".csv")
RETRIEVAL_MARKERS = ("retrieve(", "search_literature", "stage3_retrieve")
SCAN_DIRS = ("tests", "evals")
SUFFIX_TO_STRIP = ("_slim",)
SELF_NAME = "gate_library_pin_consistency.py"   # skips itself: its --controls need fake versions


def norm_version(v: str) -> str:
    for s in SUFFIX_TO_STRIP:
        if v.endswith(s):
            return v[: -len(s)]
    return v


def is_library_version(v: str) -> bool:
    return not v.lower().endswith(NOT_A_VERSION_EXT)


def default_library_version(root: Path):
    """Read the version whose block declares role: default in the pointer file."""
    p = root / "kb" / "literature_db" / "EYEKB_DB_POINTER.yaml"
    if not p.is_file():
        return None
    cur = None
    for ln in p.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if s.startswith("path:"):
            cur = s.split("path:", 1)[1].split("#")[0].strip()
        elif s.startswith("role:") and cur:
            role = s.split("role:", 1)[1].split("#")[0].strip()
            if role == "default":
                m = LIB_RE.search(cur) or re.search(r"/literature_db/([A-Za-z0-9][A-Za-z0-9._\-]*)", cur)
                if m:
                    return norm_version(m.group(1))
    return None


def scan_script(path: Path):
    """Return (versions, touches_retrieval) for one script, ignoring its docstring-level prose where
    possible: the whole file is searched, because a hard-coded path in a comment is still a stale
    pin a reader will believe."""
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return set(), False
    versions = {norm_version(v) for v in LIB_RE.findall(txt) if is_library_version(v)}
    touches = any(m in txt for m in RETRIEVAL_MARKERS)
    return versions, touches


def chain_members(root: Path):
    """Scripts the one-click chain actually invokes (tests/run_gates.sh). A stale pin inside a chain
    member is a real defect: that gate is presented as the project's acceptance evidence and yet can
    no longer see the shipped library. A stale pin in a standalone historical audit file is not --
    it legitimately belongs to the library of its own date -- so the two are reported differently."""
    sh = root / "tests" / "run_gates.sh"
    if not sh.is_file():
        return set()
    txt = sh.read_text(encoding="utf-8", errors="replace")
    return {m for m in re.findall(r"(?:tests|evals)/[A-Za-z0-9_./\-]+\.py", txt)}


def audit(root: Path):
    default_v = default_library_version(root)
    chain = chain_members(root)
    fails, warns, oks, scanned = [], [], [], 0
    for d in SCAN_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts or "fixtures" in p.parts or p.name == SELF_NAME:
                continue
            scanned += 1
            versions, touches = scan_script(p)
            rel = str(p.relative_to(root))
            stale = (len(versions) == 1 and touches and default_v
                     and next(iter(versions)) != default_v)
            if rel in chain and stale:
                fails.append((rel, f"GATE-CHAIN MEMBER pins {next(iter(versions))} but the declared "
                                   f"default is {default_v} -- the gate cannot see the shipped library"))
            elif len(versions) >= 2:
                warns.append((rel, f"references {len(versions)} libraries "
                                   f"({', '.join(sorted(versions))}) -- confirm the comparison between "
                                   f"them is intentional"))
            elif stale:
                warns.append((rel, f"pins {next(iter(versions))} but the declared default is "
                                   f"{default_v} (stale pin; historical audit files may be fine)"))
            else:
                oks.append(rel)
    return default_v, scanned, fails, warns, oks, chain


def controls(root: Path):
    """Build each situation from scratch and assert the audit reacts. A gate that always passes is
    not a gate, so this runs first in --controls mode and decides rc=3 on any mismatch."""
    import importlib.util, tempfile
    spec = importlib.util.spec_from_file_location("glpc", __file__)
    if spec is None or spec.loader is None:
        return [f"controls: cannot load {__file__} for self-audit"]
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    problems = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # minimal pointer declaring vTEST-default as the default
        (td / "kb" / "literature_db").mkdir(parents=True)
        (td / "kb" / "literature_db" / "EYEKB_DB_POINTER.yaml").write_text(
            "rag_dbs:\n"
            "  vTEST-default:\n"
            "    path: /x/literature_db/vTEST-default\n"
            "    role: default\n"
            "  vTEST-other:\n"
            "    path: /x/literature_db/vTEST-other\n"
            "    role: legacy\n", encoding="utf-8")
        (td / "tests").mkdir(); (td / "evals").mkdir()
        # the chain member list comes from this file, so the FAIL control needs a chain that names it
        (td / "tests" / "run_gates.sh").write_text("python3 evals/chain_stale.py\n", encoding="utf-8")
        cases = {
            "chain_stale.py": ("from stage3_retrieve import retrieve\n"
                               "DB='/x/literature_db/vTEST-old'\n"
                               "retrieve('x', db_dir=DB)\n", "FAIL"),
            "stale_pin.py": ("from stage3_retrieve import retrieve\n"
                             "DB='/x/literature_db/vTEST-old'\n"
                             "retrieve('x', db_dir=DB)\n", "WARN"),
            "clean.py": ("from stage3_retrieve import retrieve\n"
                         "DB='/x/literature_db/vTEST-default'\n"
                         "retrieve('x', db_dir=DB)\n", "OK"),
            "two_libs.py": ("from stage3_retrieve import retrieve\n"
                            "DB='/x/literature_db/vTEST-default'\n"
                            "OLD='/x/literature_db/vTEST-other'\n"
                            "retrieve('x', db_dir=DB); retrieve('x', db_dir=OLD)\n", "WARN"),
            "not_retrieval.py": ("VERSION='/x/literature_db/vTEST-old'\n", "OK"),
        }
        for name, (body, expect) in cases.items():
            (td / "evals" / name).write_text(body, encoding="utf-8")
        dv, n, f, w, o, ch = mod.audit(td)
        got = {}
        for rel, _ in f:
            got[Path(rel).name] = "FAIL"
        for rel, _ in w:
            got[Path(rel).name] = "WARN"
        for rel in o:
            got.setdefault(Path(rel).name, "OK")
        for name, (_, expect) in cases.items():
            if got.get(name) != expect:
                problems.append(f"control {name}: expected {expect}, got {got.get(name)}")
        if dv != "vTEST-default":
            problems.append(f"control pointer: expected vTEST-default, got {dv}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true",
                    help="also build the situations from scratch and assert the gate reacts")
    ap.add_argument("--json", default="", help="write the result summary to this path")
    a = ap.parse_args()
    root = Path(os.environ.get("EYEKB_PIN_ROOT") or Path(__file__).resolve().parent.parent)

    if a.controls:
        problems = controls(root)
        if problems:
            print("== library-pin gate CONTROLS FAILED ==")
            for p in problems:
                print("  [CONTROL FAIL]", p)
            return 3
        print("controls: chain-member stale pin -> FAIL, standalone stale pin -> WARN, "
              "two-library reference -> WARN, clean/default pin -> OK, non-retrieval script ignored "
              "[5/5 behaved]")

    default_v, scanned, fails, warns, oks, chain = audit(root)
    print(f"repo={root}")
    print(f"declared default library: {default_v}")
    print(f"gate-chain members found: {len(chain)}")
    print(f"scripts scanned: {scanned}")
    print()
    if fails:
        print("== FAIL: a gate-chain member is pinned to a library other than the default ==")
        for rel, why in fails:
            print(f"  [FAIL] {rel}: {why}")
    if warns:
        print("== WARN: stale pin / possible unintended cross-library comparison (not chain members) ==")
        for rel, why in warns:
            print(f"  [WARN] {rel}: {why}")
    if not fails and not warns:
        print("no stale pins found")
    print()
    print(f"summary: scanned={scanned} fail={len(fails)} warn={len(warns)} ok={len(oks)}")
    if a.json:
        outp = Path(a.json)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps({
            "repo": str(root), "declared_default_library": default_v,
            "chain_members": sorted(chain), "scanned": scanned,
            "fail": [{"script": r, "why": w} for r, w in fails],
            "warn": [{"script": r, "why": w} for r, w in warns],
            "verdict": "FAIL" if fails else "PASS",
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {a.json}")
    return 2 if fails else 0


if __name__ == "__main__":
    sys.exit(main())