#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m6_manifest.py — freeze the build artefacts.

Written policy, because the manifest is the thing that has to survive a re-run:

  * a manifest list never contains its own hash (a file cannot contain its own digest), so the
    manifest itself is excluded by name;
  * **run-time write-outs are excluded**, and named here so a reader can see what was left out and
    why: the gate's own readouts (`GATE.json`, `GATE_READOUT.md`, `ANCHOR_RESOLUTION.json`) are
    rewritten every time the gate is run, so including them would make the manifest fail every time
    the layer is verified rather than every time the layer is wrong;
  * the acceptance test is therefore "`sha256sum -c` still returns 0 **after** the gate has been
    re-run", which is what run_all.sh checks.

Usage: python3 m6_manifest.py [--check]
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

EXCLUDE = {"MANIFEST.sha256", "GATE.json", "GATE_READOUT.md", "ANCHOR_RESOLUTION.json"}


def main() -> int:
    out = M.OUT
    names = sorted(n for n in os.listdir(out)
                   if not n.startswith(".") and n not in EXCLUDE and os.path.isfile(
                       os.path.join(out, n)))
    mp = os.path.join(out, "MANIFEST.sha256")
    with open(mp, "w", encoding="utf-8") as f:
        f.write("# manifest of the deterministic build artefacts of the marker layer\n")
        f.write("# excluded by policy: %s\n" % ", ".join(sorted(EXCLUDE)))
        f.write("# reason: they are rewritten by the gate on every run, so they are run-time\n")
        f.write("# outputs and not deliverables; the acceptance test is `sha256sum -c` returning 0\n")
        f.write("# after the gate has been re-run.\n")
        for n in names:
            h = hashlib.sha256(open(os.path.join(out, n), "rb").read()).hexdigest()
            f.write("%s  %s\n" % (h, n))
    p = subprocess.run(["sha256sum", "-c", "MANIFEST.sha256"], cwd=out, capture_output=True,
                       text=True)
    ok = [l for l in p.stdout.splitlines() if l.endswith(": OK")]
    bad = [l for l in p.stdout.splitlines() if not l.endswith(": OK")]
    print("manifest entries:", len(names), "| verified OK:", len(ok), "| not OK:", len(bad))
    for l in bad[:10]:
        print("   ", l)
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())