#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_preimage_ref_immutable.py — G9: pre/post-image references must be immutable.

Why this gate exists (observed twice, not hypothesised)
------------------------------------------------------
A "before/after" judgement script compares an old revision of a file against the
current one. If the old revision is fetched with a *relative* git reference
(`git show HEAD:path`, `HEAD~1:path`, `@{1}:path`), then the moment the change
itself is committed `HEAD` IS the new revision: the script silently compares the
new file against itself.

Two field occurrences:
  * 2026-10-22 (carrier-flip card): after its own commit, `git show HEAD:mcp_server/eyekb_core.py`
    became the activated core, so PARENT == FLIP on all 721 queries and
    "changed fields = {}" — yet the wave gate still reported most checks PASS.
  * 2026-10-22 (gene-symbol fix card): the identity judge read its pre-image with
    `git show HEAD:...` *after* the fix had been committed, so "names containing
    '#' before the fix" came out 0 and the judge reported FAIL — for the wrong reason.
    With the reference pinned to the pre-fix commit, the same script reports PASS
    and the before-image fingerprint reproduces (0dcca9d37e92).

Rule
----
A pre/post-image reference must be an immutable commit id (full 40-hex, or an
abbreviation of >= 7 hex, optionally kept in a named constant) or a content hash.
Relative references are forbidden for this purpose.

Scope
-----
Product and tooling code where such judges live: pipeline/, mcp_server/, kb/,
scripts/, tests/ (excluding tests/fixtures/** and build/**). Historical change
records under docs/ are audit originals and are deliberately NOT rewritten or
scanned — this gate is about executable code, not about past records.

Escape hatch
------------
A line may legitimately *mention* the pattern as a human-readable label (e.g. a
report string saying what the old default used to be). Two mechanisms:
  * a reference written inside backticks is prose *about* the hazard, not code
    that performs it, and is skipped;
  * any other legitimate mention must carry the explicit marker `gate-g9: allow`
    so the exemption is a reviewed, greppable decision rather than an accident.

Self-test
---------
The gate also runs its scanner over a synthetic tree containing violating files
(shell-style and argv-style calls, plus a relative ref hidden in a pre-image
constant) and clean files (immutable ids, backticked prose, marked label), and
requires the exact expected split. A scanner that flags nothing must not pass.
A scanner that flags its own prose cannot pass either.

Exit codes: 0 = PASS, 1 = FAIL (violations on the real tree or a failed self-test),
3 = precondition missing (repo root not found).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SCAN_DIRS = ("pipeline", "mcp_server", "kb", "scripts", "tests")
SKIP_DIR_NAMES = {"build", "fixtures", "__pycache__", ".git", ".gate_out"}
SCAN_SUFFIXES = (".py", ".sh", ".bash", ".ipynb", ".md")

# Relative git refs used as a pre/post-image source. Two call shapes are covered:
#   shell style:  git show HEAD:path
#   argv  style:  ["git", "show", "HEAD:path"]
RELATIVE_REF_RE = re.compile(
    r"""(?:git["'\s]*,\s*["']?show["']?\s*,\s*["'](?P<ref_argv>[^"']+)["']
        |git\s+show\s+(?P<ref_shell>[^\s"';|)`]+))""",
    re.VERBOSE,
)
# Also catch the ref written into a constant that feeds a `git show` call.
HEAD_CONST_RE = re.compile(r"""^[A-Z0-9_]*PRE[A-Z0-9_]*\s*=\s*["'](HEAD(?:~\d+)?|@\{[^}]*\})["']""")
ALLOW_MARKER = "gate-g9: allow"
HEX_RE = re.compile(r"^[0-9a-f]{7,40}$")
# Self-exemption: this file necessarily *contains* the hazard patterns, as the
# positive/negative fixtures of its own self-test and as prose about the rule.
# Exempting it does not open a blind spot, because the self-test proves the
# scanner still flags those exact shapes in every other file.
SELF_EXEMPT = {"gate_preimage_ref_immutable.py"}


def _is_prose(line: str, span: tuple[int, int]) -> bool:
    """True when the matched text sits inside backticks (documentation about the hazard)."""
    before = line[: span[0]]
    after = line[span[1]:]
    return before.count("`") % 2 == 1 and after.lstrip().startswith("`")


def _is_relative(ref: str) -> bool:
    ref = ref.strip().rstrip("`").strip()
    if not ref:
        return False
    if ref.startswith("HEAD") or ref.startswith("@"):
        return True
    # `a..b` range forms are relative by construction
    if ".." in ref:
        return True
    base = ref.split(":")[0]
    return not bool(HEX_RE.match(base))


def scan_file(path: Path) -> list[dict]:
    hits: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return hits
    for i, line in enumerate(text.splitlines(), 1):
        if ALLOW_MARKER in line:
            continue
        m = RELATIVE_REF_RE.search(line)
        if m:
            ref = m.group("ref_argv") or m.group("ref_shell") or ""
            if _is_relative(ref) and not _is_prose(line, m.span()):
                hits.append({"file": str(path), "line": i, "kind": "relative-ref-in-git-show",
                             "text": line.strip()[:200]})
                continue
        m2 = HEAD_CONST_RE.match(line.strip())
        if m2 and _is_relative(m2.group(1)):
            hits.append({"file": str(path), "line": i, "kind": "relative-ref-in-preimage-constant",
                         "text": line.strip()[:200]})
    return hits


def scan_tree(root: Path) -> tuple[list[dict], int]:
    hits: list[dict] = []
    n_files = 0
    for d in SCAN_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
                continue
            if any(part in SKIP_DIR_NAMES for part in p.parts):
                continue
            if p.name in SELF_EXEMPT:
                continue
            n_files += 1
            hits.extend(scan_file(p))
    return hits, n_files


def self_test() -> tuple[bool, dict]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        # violating: shell-style relative ref used as pre-image source
        (root / "scripts" / "bad.py").write_text(
            'import subprocess\nsubprocess.run("git show HEAD:pipeline/x.py", shell=True)\n',
            encoding="utf-8")
        # violating: argv-style relative ref used as pre-image source
        (root / "scripts" / "bad_argv.py").write_text(
            'import subprocess\nsubprocess.run(["git", "show", "HEAD~1:pipeline/x.py"])\n',
            encoding="utf-8")
        # violating: relative ref hidden in a pre-image constant
        (root / "scripts" / "bad2.py").write_text('PRE_COMMIT = "HEAD~1"\n', encoding="utf-8")
        # clean: immutable full commit id
        (root / "scripts" / "good.py").write_text(
            'PRE_COMMIT = "0ce0c943ceea71c5591925bf97ed0c2d77f3d2b9"\n'
            'subprocess.run(["git", "show", f"{PRE_COMMIT}:pipeline/x.py"])\n',
            encoding="utf-8")
        # clean: relative ref mentioned as a human-readable label, explicitly allowed
        (root / "scripts" / "label.py").write_text(
            'note = "old default used git show HEAD:core.py"  # gate-g9: allow\n', encoding="utf-8")
        # clean: backticked prose about the hazard
        (root / "scripts" / "prose.py").write_text(
            'PROSE = "the old script used `git show HEAD:core.py` and silently self-compared"\n',
            encoding="utf-8")
        # clean: absolute sha in an argv-style call
        (root / "scripts" / "sha.py").write_text(
            'subprocess.run(["git", "show", "16349f6f373ced7f77aedf40ac97c4b7b93304ce:pipeline/x.py"])\n',
            encoding="utf-8")
        hits, n_files = scan_tree(root)
        flagged = {Path(h["file"]).name for h in hits}
        expected = {"bad.py", "bad_argv.py", "bad2.py"}
        ok = (flagged == expected) and n_files == 7
        return ok, {"n_files": n_files, "flagged": sorted(flagged),
                    "expected": sorted(expected)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=None, help="repo root (default: parent of this file's dir)")
    ap.add_argument("--json", default=None, help="write readout here")
    args = ap.parse_args()

    here = Path(__file__).resolve()
    root = Path(args.repo).resolve() if args.repo else here.parent.parent
    if not (root / "tests").is_dir():
        print(f"[G9] precondition missing: no tests/ under {root}", file=sys.stderr)
        return 3

    print(f"[G9] repo   = {root}")
    print(f"[G9] rule   = pre/post-image references must be immutable (no HEAD / HEAD~N / @{{n}})")

    st_ok, st = self_test()
    print(f"[G9] self-test: scanner over synthetic tree -> flagged={st['flagged']} "
          f"(expected {st['expected']}), files={st['n_files']}  {'OK' if st_ok else 'BROKEN'}")

    hits, n_files = scan_tree(root)
    print(f"[G9] scanned {n_files} file(s) under {', '.join(SCAN_DIRS)}")
    print(f"[G9] self-exempt (declared, contains the gate's own fixtures/prose): {sorted(SELF_EXEMPT)}")
    for h in hits:
        print(f"[G9]   VIOLATION {h['kind']}: {h['file']}:{h['line']}")
        print(f"[G9]     {h['text']}")

    verdict = "PASS" if (st_ok and not hits) else "FAIL"
    print(f"[G9] violations = {len(hits)}")
    print(f"[G9] verdict = {verdict}")

    if args.json:
        Path(args.json).write_text(json.dumps({
            "gate": "G9", "rule": "pre/post-image references must be immutable",
            "scanned_files": n_files, "violations": hits,
            "self_test": {"ok": st_ok, **st},
            "verdict": verdict,
        }, ensure_ascii=False, indent=1), encoding="utf-8")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())