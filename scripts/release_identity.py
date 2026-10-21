#!/usr/bin/env python3
"""Release identity for this service repository.

Why it exists
    A caller has to be able to tell two releases apart. The service reports a protocol
    generation label in its handshake (`KB1v2-...`); that label describes the wire contract,
    not the bytes that are shipped, so it does not move when the knowledge base, the
    pipeline or the service code move. This script derives a *release identity* from the
    shipped bytes themselves.

What the identity is
    release_id = the first 12 hex digits of the sha256 of the canonical listing

        <sha256 of each tracked file>  <two spaces>  <repository-relative path>

    over every file git tracks, sorted by path. So it changes when — and only when — the
    bytes of the shipped tree change, and any clone of the same commit computes the same
    value whatever directory it sits in.

Exclusions (deliberate, and the only ones)
    docs/RELEASE_IDENTITY.json   this record cannot contain its own hash

Rule (this repository's discipline, unchanged): the identity is re-taken in the same commit
as any byte change to the tracked tree. A reader can therefore check the claim with one
command wherever the checkout lives.

Usage (from the repository root):
  python3 scripts/release_identity.py              # print the identity of this working tree
  python3 scripts/release_identity.py --take       # re-take it and write docs/RELEASE_IDENTITY.json
  python3 scripts/release_identity.py --check      # compare the record with the shipped bytes

Exit codes: 0 = identity printed / record matches the shipped bytes
            1 = the record does not match the shipped bytes (re-take it in this commit)
            3 = the identity cannot be computed here (no git, or not a checkout): no claim is made
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "RELEASE_IDENTITY.json"
RECORD_REL = "docs/RELEASE_IDENTITY.json"
SCHEMA = "eyekb-release-identity/1.0"
ALGORITHM = "sha256 over sorted lines '<sha256 of file>  <path>' for every tracked file"


def tracked_paths():
    """Every path git tracks, sorted. None when git cannot answer (then: no claim)."""
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                           capture_output=True, timeout=300)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return sorted(p.decode("utf-8", "replace") for p in r.stdout.split(b"\x00") if p)


def compute(paths):
    """-> (release_id, digest, n_files, total_bytes) or None if a tracked file is unreadable."""
    lines, total = [], 0
    for rel in paths:
        if rel == RECORD_REL:
            continue
        f = ROOT / rel
        try:
            b = f.read_bytes()
        except OSError:
            return None
        total += len(b)
        lines.append(f"{hashlib.sha256(b).hexdigest()}  {rel}\n")
    blob = "".join(lines).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()
    return digest[:12], digest, len(lines), total


def read_record():
    if not RECORD.exists():
        return None
    try:
        return json.loads(RECORD.read_text(encoding="utf-8"))
    except Exception:
        return None


def head_commit():
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", action="store_true", help="re-take and write the record")
    ap.add_argument("--check", action="store_true", help="compare the record with the shipped bytes")
    a = ap.parse_args()

    paths = tracked_paths()
    if not paths:
        print("CANNOT COMPUTE: this working tree is not a git checkout, or git is unavailable.")
        print("  The release identity is a statement about the shipped (tracked) bytes, so no")
        print("  value can be derived here. This is not a mismatch.")
        return 3
    got = compute(paths)
    if got is None:
        print("CANNOT COMPUTE: a tracked file could not be read.")
        return 3
    release_id, digest, n_files, total = got
    print(f"release_id      {release_id}")
    print(f"digest_sha256   {digest}")
    print(f"tracked_files   {n_files}  ({total} bytes)")
    print(f"algorithm       {ALGORITHM}")
    print(f"excluded        {RECORD_REL} (a record cannot contain its own hash)")

    if a.take:
        rec = {"schema": SCHEMA, "release_id": release_id, "digest_sha256": digest,
               "algorithm": ALGORITHM, "n_files": n_files, "total_bytes": total,
               "taken_at_commit": head_commit(),
               "taken_at_commit_note": ("the commit HEAD pointed at when the identity was taken, i.e. "
                                        "the parent of the commit this record ships in: a record cannot "
                                        "name the commit that contains it"),
               "coverage": "every file tracked by git at the commit this record ships in",
               "excluded": [RECORD_REL],
               "recompute": "python3 scripts/release_identity.py --check"}
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"recorded -> {RECORD_REL} (taken_at_commit {rec['taken_at_commit'][:12] or 'unknown'})")
        return 0

    if a.check:
        rec = read_record()
        if rec is None:
            print(f"FAIL: no readable record at {RECORD_REL}; the shipped bytes have no recorded identity.")
            print("  Re-take it in this commit: python3 scripts/release_identity.py --take")
            return 1
        if rec.get("release_id") == release_id and rec.get("digest_sha256") == digest:
            print(f"IDENTITY MATCH: the record matches the shipped bytes ({release_id}).")
            return 0
        print(f"FAIL: the record is stale. recorded={rec.get('release_id')} "
              f"shipped={release_id} (files {rec.get('n_files')} -> {n_files})")
        print("  The rule is that the identity is re-taken in the same commit as the byte change:")
        print("  python3 scripts/release_identity.py --take")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())