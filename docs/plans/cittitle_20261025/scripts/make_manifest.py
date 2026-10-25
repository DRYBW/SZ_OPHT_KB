#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_manifest.py — CITTITLE (card t_d8e7f2d4): write out/MANIFEST.sha256 over the delivered
artefacts, and nothing else.

Rules that made the earlier waves' manifests rot, applied here:
  * the manifest itself is excluded (a file cannot contain its own hash);
  * run-time files produced by the verifiers are excluded (`out/G12_CONTROLS.json` is rewritten every
    time the reverse-control battery runs; the per-run logs live in logs/, outside this root), so
    `sha256sum -c` stays rc=0 after a re-run of the checks rather than only on the first pass;
  * it is written LAST, after every other delivered byte, and `sha256sum -c` is then run from out/.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out"
MAN = "MANIFEST.sha256"

# Rewritten by a re-run of a check, so it must not be pinned: see the module docstring.
EXCLUDE = {MAN, "G12_CONTROLS.json"}


def main() -> int:
    entries = []
    for p in sorted(OUT.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(OUT))
        if rel in EXCLUDE:
            continue
        entries.append((rel, hashlib.sha256(p.read_bytes()).hexdigest()))
    lines = ["# CITTITLE (card t_d8e7f2d4) — delivered artefacts under out/",
             "# Excluded on purpose: this manifest itself (a file cannot hash itself) and "
             "G12_CONTROLS.json",
             "# (rewritten by every run of scripts/g12_controls.py, so pinning it would make "
             "`sha256sum -c` fail after a re-run",
             "#  of the controls while the artefacts are untouched).",
             "# Verify from THIS directory:  sha256sum -c MANIFEST.sha256",
             ]
    lines += [f"{h}  {rel}" for rel, h in entries]
    (OUT / MAN).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for rel, h in entries:
        print(f"{h[:16]}  {rel}")
    p = subprocess.run(["sha256sum", "-c", MAN], cwd=str(OUT), capture_output=True, text=True)
    ok = [l for l in p.stdout.splitlines() if l.endswith(": OK")]
    bad = [l for l in p.stdout.splitlines() if "FAILED" in l]
    print(f"sha256sum -c: rc={p.returncode} ok={len(ok)}/{len(entries)} failed={len(bad)}")
    if p.returncode != 0:
        print(p.stdout[-500:], p.stderr[-300:])
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())