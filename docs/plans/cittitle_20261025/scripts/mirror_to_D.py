#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mirror_to_D.py — CITTITLE (card t_d8e7f2d4): copy the delivered tree to the construction-site
mirror under the campaign directory, and verify every copied file by sha256.

The repository copy is the primary (delivery authority, docs/VERIFY_CONTRACT.md §5.1); this mirror
exists so the coordinator's campaign directory `/mnt/D/EyeKB/plans/consistency_20261024/` holds the
same artefacts beside BRIEF_CITTITLE_20261025.md, as the sibling cards did. Copies are byte-verified
in both directions; nothing is moved and nothing on the source side is modified.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

SRC = Path("/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025")
DST = Path("/mnt/D/EyeKB/plans/consistency_20261024/cittitle_out")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    n = 0
    bad = []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(SRC)
        dst = DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        a, b = sha(p), sha(dst)
        n += 1
        if a != b:
            bad.append((str(rel), a, b))
        print(f"{a[:16]}  {'OK ' if a == b else 'BAD'}  {rel}")
    print(f"\nmirrored {n} files to {DST}; sha mismatches: {len(bad)}")
    if bad:
        print(bad)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())