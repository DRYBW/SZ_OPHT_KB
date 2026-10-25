#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""freeze_w3_manifest.py — CITTITLE (card t_d8e7f2d4): re-freeze docs/W3_MANIFEST.sha256.

Same procedure as the earlier waves (the method, not their script): replace the
`W3_PIPELINE_REGISTRY.tsv` line's sha with the live one, insert a dated provenance line under the
file's own header, and leave every other byte alone. Run LAST among this card's byte changes, then
verify with `sha256sum -c` from docs/.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO")
DOCS = REPO / "docs"
REG = DOCS / "W3_PIPELINE_REGISTRY.tsv"
MAN = DOCS / "W3_MANIFEST.sha256"

HEADER = ("# Re-frozen 2026-10-25 (card t_d8e7f2d4, CITTITLE): the registry row was re-taken for the "
          "citation presentation metadata fix (rows L6-01/L6-22 re-taken, L6-53..L6-57 added); the "
          "other rows are unchanged. Frozen by docs/plans/cittitle_20261025/scripts/"
          "freeze_w3_manifest.py.")


def main() -> int:
    reg_sha = hashlib.sha256(REG.read_bytes()).hexdigest()
    reg_bytes = REG.stat().st_size
    txt = MAN.read_text(encoding="utf-8")
    if HEADER in txt:
        print("already frozen by this card; nothing to do")
        return 0
    lines = txt.split("\n")
    out, replaced, old = [], 0, None
    for ln in lines:
        if ln.endswith("W3_PIPELINE_REGISTRY.tsv") and not ln.startswith("#"):
            old = ln.split("  ")[0]
            out.append(f"{reg_sha}  W3_PIPELINE_REGISTRY.tsv")
            replaced += 1
        else:
            out.append(ln)
    assert replaced == 1, f"expected exactly one registry line, replaced {replaced}"
    assert out and out[0].startswith("# W3-NORM"), out[0][:60]
    out.insert(1, HEADER)
    MAN.write_text("\n".join(out), encoding="utf-8")
    print(f"registry line: {old[:16]} -> {reg_sha[:16]} ({reg_bytes} B)")
    p = subprocess.run(["sha256sum", "-c", "W3_MANIFEST.sha256"], cwd=str(DOCS),
                       capture_output=True, text=True)
    ok = [l for l in p.stdout.splitlines() if l.endswith(": OK")]
    print(f"sha256sum -c: rc={p.returncode} ok={len(ok)}")
    print(p.stdout.strip()[:400])
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())