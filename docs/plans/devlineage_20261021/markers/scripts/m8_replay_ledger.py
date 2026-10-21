#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m8_replay_ledger.py — rebuild the chain into a scratch directory and write the replay ledger.

The gate already compares a rebuild internally (check G10). This script exists so the comparison
also lands in `ledgers/` as a durable, quotable artefact: which artefacts were compared, their
hashes on both sides, and whether anything differed.

Usage: python3 m8_replay_ledger.py
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

CHAIN = ["m0_corpus_gene_index.py", "m1_nodes.py", "m2_node_markers.py",
         "m3_edge_assertions.py", "m4_gap_register.py"]


def main() -> int:
    led = os.path.join(M.WAVE, "ledgers")
    os.makedirs(led, exist_ok=True)
    names = []
    for line in open(os.path.join(M.OUT, "MANIFEST.sha256"), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        names.append(line.split("  ", 1)[1].strip())
    tmp = tempfile.mkdtemp(prefix="mk_replay_ledger_")
    env = dict(os.environ, MK_OUTDIR=tmp)
    for s in CHAIN:
        p = subprocess.run(["/usr/bin/python3", os.path.join(HERE, s)], env=env,
                           capture_output=True, text=True)
        if p.returncode:
            print("build failed at", s, p.stderr[-300:])
            shutil.rmtree(tmp, ignore_errors=True)
            return 1
    h1, h2, diff = [], [], []
    for n in names:
        a = hashlib.sha256(open(os.path.join(M.OUT, n), "rb").read()).hexdigest()
        b = hashlib.sha256(open(os.path.join(tmp, n), "rb").read()).hexdigest()
        h1.append("%s  %s" % (a, n))
        h2.append("%s  %s" % (b, n))
        if a != b:
            diff.append(n)
    shutil.rmtree(tmp, ignore_errors=True)
    open(os.path.join(led, "replay_pass1.txt"), "w", encoding="utf-8").write("\n".join(h1) + "\n")
    open(os.path.join(led, "replay_pass2.txt"), "w", encoding="utf-8").write("\n".join(h2) + "\n")
    open(os.path.join(led, "REPLAY.txt"), "w", encoding="utf-8").write(
        "# replay ledger: the whole chain was rebuilt into a scratch directory and every artefact\n"
        "# listed in out/MANIFEST.sha256 was compared byte for byte.\n"
        "artefacts_compared=%d\ndiffering=%d\n%s\n"
        % (len(names), len(diff),
           "REPLAY_PASS byte-identical on the second build" if not diff
           else "REPLAY_FAIL " + ",".join(diff)))
    print("replay: compared %d artefacts, differing %d" % (len(names), len(diff)))
    return 0 if not diff else 1


if __name__ == "__main__":
    sys.exit(main())