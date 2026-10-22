#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m3 -- re-freeze the W3 manifest's registry line, LAST (after the registry's final bytes exist).

docs/W3_MANIFEST.sha256 carries one checksum line per W3_* artefact plus a comment block recording
each re-freeze. The registry is one of those lines, so editing registry rows invalidates it: this
script re-takes the line from live bytes, records the transition in the comment block the way every
earlier re-freeze did, writes atomically, and verifies the whole manifest with sha256sum semantics
computed here (no shell dependency, so the check is available in the sandbox too).

Usage: python3 m3_w3_manifest.py [--write]
"""
import argparse
import hashlib
import pathlib
import sys

ROOT = pathlib.Path("/home/ubuntu/EYEKB_REPO")
MAN = ROOT / "docs" / "W3_MANIFEST.sha256"
REG_NAME = "W3_PIPELINE_REGISTRY.tsv"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify():
    ok, bad, bads = 0, 0, []
    for ln in MAN.read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        parts = ln.split()
        if len(parts) != 2:
            bads.append("improperly formatted line: %r" % ln)
            bad += 1
            continue
        want, rel = parts
        p = MAN.parent / rel
        if not p.is_file():
            bads.append("%s: missing" % rel)
            bad += 1
        elif sha(p) != want:
            bads.append("%s: FAILED" % rel)
            bad += 1
        else:
            ok += 1
    return ok, bad, bads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    txt = MAN.read_text(encoding="utf-8")
    live = sha(ROOT / "docs" / REG_NAME)
    lines = txt.split("\n")
    old, out = None, []
    for ln in lines:
        if ln.split()[-1:] == [REG_NAME]:
            old = ln.split()[0]
            if old != live:
                out.append("# re-taken 2026-10-22 (activation card t_42df17c2): the registry row was "
                           "re-taken after the activation of `onfibro_v13` on the default route "
                           "(%s -> %s, bytes=%d); the other rows are unchanged."
                           % (old[:16], live[:16], (ROOT / "docs" / REG_NAME).stat().st_size))
            out.append("%s  %s" % (live, REG_NAME))
        else:
            out.append(ln)
    if old is None:
        raise SystemExit("registry line not found in the manifest")
    print("registry sha: %s -> %s  bytes=%d"
          % (old, live, (ROOT / "docs" / REG_NAME).stat().st_size))
    if a.write:
        new_txt = "\n".join(out)
        if new_txt != txt:
            tmp = MAN.with_suffix(".tmp-activate")
            tmp.write_text(new_txt, encoding="utf-8")
            tmp.replace(MAN)
            print("wrote", MAN)
        else:
            print("manifest untouched (registry line already current)")
    ok, bad, bads = verify()
    print("manifest self-check (from docs/): ok=%d bad=%d" % (ok, bad))
    for b in bads:
        print("  ", b)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())