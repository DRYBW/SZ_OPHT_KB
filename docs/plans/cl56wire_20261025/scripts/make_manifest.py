#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write/verify out/MANIFEST.sha256 over this wave's artefacts.

Run from anywhere:  /usr/bin/python3 scripts/make_manifest.py [--verify]
The manifest lists every artefact of the wave except itself and the append-only build logs are
included (they are frozen once the wave closes; if a builder is re-run, re-run this script).

Excluded on purpose: out/MANIFEST.sha256 (a record cannot contain its own hash) and this script's
own __pycache__.
"""
import hashlib
import sys
from pathlib import Path

WAVE = Path("/mnt/D/EyeKB/plans/consistency_20261024/cl56wire_out")
MAN = WAVE / "out" / "MANIFEST.sha256"
SKIP_DIRS = {"__pycache__", "discipline"}


def files():
    out = []
    for p in sorted(WAVE.rglob("*")):
        if p.is_dir() or p == MAN:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def main():
    if "--verify" in sys.argv:
        import subprocess
        rc = subprocess.run(["sha256sum", "-c", str(MAN)], cwd=WAVE).returncode
        print("manifest verify rc=", rc)
        return rc
    lines = []
    for p in files():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append("%s  %s" % (h, p.relative_to(WAVE)))
    MAN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("manifest:", MAN, len(lines), "files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())