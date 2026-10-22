#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n7 -- the wave manifest.

Hashed AFTER every artefact is written and BEFORE the gate runs, so a drifting artefact is the
gate's job rather than a human's. Excluded on purpose (and listed in the manifest as excluded, with
the reason): the manifest itself (a file cannot contain its own hash), everything under ledgers/ and
logs/ (runtime files that this chain rewrites while it runs), the gate's own readouts, and
__pycache__.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

EXCLUDE_DIRS = ("ledgers", "logs", "__pycache__")
EXCLUDE_FILES = ("out/MANIFEST.sha256", "out/MANIFEST.json", "out/GATE.json",
                 "out/GATE_READOUT.md", "out/CLEAN_CLONE_CHECK.json")
EXCLUDE_SUFFIX = (".pyc",)


def main():
    files = []
    for root, dirs, names in os.walk(WAVE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for n in sorted(names):
            if n.endswith(EXCLUDE_SUFFIX):
                continue
            p = os.path.join(root, n)
            rel = os.path.relpath(p, WAVE)
            if rel in EXCLUDE_FILES:
                continue
            files.append((rel, W.sha256_file(p), os.path.getsize(p)))
    files.sort()
    lines = ["%s  %s" % (h, rel) for rel, h, s in files]
    with open(os.path.join(OUT, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    doc = {"probe": "n7_manifest.py", "wave": os.path.relpath(WAVE, W.REPO),
           "n_files": len(files), "files": [{"rel": r, "sha256": h, "bytes": s}
                                            for r, h, s in files],
           "excluded_dirs": list(EXCLUDE_DIRS), "excluded_files": list(EXCLUDE_FILES),
           "exclusion_reason": "runtime output of this chain (ledgers/logs/gate readouts) and the "
                               "manifest itself; a file cannot carry its own hash",
           "note": "the sha256 list also exists as out/MANIFEST.sha256 in sha256sum -c format"}
    W.save_json(os.path.join(OUT, "MANIFEST.json"), doc)
    print("manifest: %d files" % len(files))
    print("wrote", os.path.join(OUT, "MANIFEST.sha256"))


if __name__ == "__main__":
    main()