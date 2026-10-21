#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w5_08_manifest.py — the wave's own manifest. Taken last, verified afterwards, never self-hashed.

Coverage: out/ and scripts/ — the artefacts and the code that produced them. ledgers/ holds the
run's own logs (chain.log, the audit log, the manifest check itself), which are written *while*
the chain runs and therefore cannot be listed by a manifest taken in the middle of it; they are
kept and mirrored, just not hash-pinned.

Excluded from out/, and why (a manifest that lists a file the verifier rewrites is a manifest
that fails on its own second run):
  out/MANIFEST.sha256        the list cannot contain its own hash
  out/GATE.json              written by the gate, which runs after the manifest
  out/GATE_READOUT.md        written by the gate
  out/CLEAN_CLONE_CHECK.json written by the clone check, after the manifest
  out/GATE_pass1*.json|md    written inside a clone by the clone check's first pass
  __pycache__/*.pyc          interpreter byproducts
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w5_common as C  # noqa: E402

EXCLUDE = {"out/MANIFEST.sha256", "out/GATE.json", "out/GATE_READOUT.md",
           "out/CLEAN_CLONE_CHECK.json"}
EXCLUDE_PREFIX = ("out/GATE_pass1",)


def main() -> int:
    rows = []
    for d in ("out", "scripts"):
        for root, dirs, files in os.walk(os.path.join(C.WAVE, d)):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for fn in sorted(files):
                if fn.endswith(".pyc"):
                    continue
                rel = os.path.relpath(os.path.join(root, fn), C.WAVE)
                if rel in EXCLUDE or rel.startswith(EXCLUDE_PREFIX):
                    continue
                rows.append((rel, C.sha256(os.path.join(C.WAVE, rel))))
    rows.sort()
    with open(os.path.join(C.OUT, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
        f.write("# sha256 manifest of this wave's artefacts (out/ and scripts/; ledgers/ holds the\n"
                "# run's own logs, which are written while the chain runs)\n"
                "# excluded (a verifier rewrites them): %s\n"
                % ", ".join(sorted(EXCLUDE) + list(EXCLUDE_PREFIX)))
        for rel, h in rows:
            f.write("%s  %s\n" % (h, rel))
    print("manifest entries: %d" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())