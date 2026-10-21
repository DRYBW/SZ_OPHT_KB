#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step F2 — re-freeze the W3 manifest row for the registry, in the same commit as the registry edit.

docs/W3_MANIFEST.sha256 carries one line per W3_* artefact plus a comment recording each re-freeze.
The registry is one of those lines, so editing a registry row invalidates it: this script re-takes the
line from live bytes, records the transition in the comment block (the same form every earlier
re-freeze used), and then verifies the whole manifest with `sha256sum -c` semantics computed here (no
shell dependency, so the check is available in the sandbox too).

Usage: <py> f2_manifest_reanchor.py [--write]
"""
import argparse
import hashlib
import pathlib

ROOT = pathlib.Path("/home/ubuntu/EYEKB_REPO")
MAN = ROOT / "docs" / "W3_MANIFEST.sha256"
REG = ROOT / "docs" / "W3_PIPELINE_REGISTRY.tsv"
NOTE_PREFIX = "# re-taken 2026-10-22 (shipped-surface card t_19831068):"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_manifest():
    """(ok, bad) for every checksum line of the manifest, resolved relative to docs/."""
    ok = bad = 0
    bads = []
    for ln in MAN.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        parts = ln.split()
        if len(parts) != 2:
            bads.append(f"improperly formatted line: {ln!r}")
            bad += 1
            continue
        want, rel = parts
        p = MAN.parent / rel
        if not p.is_file():
            bads.append(f"{rel}: missing")
            bad += 1
        elif sha(p) != want:
            bads.append(f"{rel}: FAILED")
            bad += 1
        else:
            ok += 1
    return ok, bad, bads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    txt = MAN.read_text(encoding="utf-8")
    new_sha = sha(REG)
    new_bytes = REG.stat().st_size
    old = None
    lines = txt.split("\n")
    out = []
    for ln in lines:
        if ln.endswith("  W3_PIPELINE_REGISTRY.tsv") or ln.endswith("\tW3_PIPELINE_REGISTRY.tsv"):
            old = ln.split()[0]
            if old != new_sha:
                out.append(f"{NOTE_PREFIX} the registry row was re-taken after the shipped-surface "
                           f"re-take of rows L1-11M / L6-06 / L6-36 / L6-37 "
                           f"({old[:16]} -> {new_sha[:16]}, bytes={new_bytes}); the other rows are "
                           f"unchanged.")
            out.append(f"{new_sha}  W3_PIPELINE_REGISTRY.tsv")
        else:
            out.append(ln)
    if old is None:
        raise SystemExit("registry line not found in the manifest")

    print(f"registry sha: {old} -> {new_sha}  bytes={new_bytes}")
    if a.write:
        if "\n".join(out) != txt:
            MAN.write_text("\n".join(out), encoding="utf-8")
            print(f"wrote {MAN}")
        else:
            print("manifest untouched (registry line already current)")
    ok, bad, bads = verify_manifest()
    print(f"manifest self-check: ok={ok} bad={bad}")
    for b in bads:
        print(f"  {b}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())