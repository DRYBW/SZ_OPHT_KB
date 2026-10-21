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

        <git blob id>  <two spaces>  <repository-relative path>

    over every file the tree contains, sorted by path. The blob ids are content addresses,
    so the value changes when — and only when — the bytes of that tree change, and any clone
    of the same commit computes the same value whatever directory it sits in.

Which tree
    `HEAD` by default: a release is a commit, and the identity has to describe what is
    shipped, not what happens to sit in somebody's working tree. A dirty working tree
    therefore does not move a release's identity — and cannot hide one either. `--source
    index` reads the staged tree instead, which is how the record is taken in the same commit
    as the change: stage everything, take the identity of the staged tree, commit.

Exclusions (deliberate, and the only ones)
    docs/RELEASE_IDENTITY.json   this record cannot contain its own hash

Rule (this repository's discipline, unchanged): the identity is re-taken in the same commit
as any byte change to the tracked tree. A reader can check the claim with one command wherever
the checkout lives.

Usage (from the repository root):
  python3 scripts/release_identity.py                      # the identity of HEAD
  python3 scripts/release_identity.py --source index       # the identity of the staged tree
  python3 scripts/release_identity.py --take [--source …]  # re-take it and write the record
  python3 scripts/release_identity.py --check              # the record vs the shipped bytes

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
ALGORITHM = "sha256 over sorted lines '<git blob id>  <path>' for every file in the tree"


def blob_sizes(oids):
    """Sizes of the given blobs, one stream call to the object store."""
    if not oids:
        return {}
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch-check",
                            "--batch-all-objects" if False else "--buffer"],
                           input="".join(o + "\n" for o in oids), capture_output=True,
                           text=True, timeout=600)
    except Exception:
        return {}
    out = {}
    for line in r.stdout.splitlines():
        f = line.split()
        if len(f) >= 3:
            try:
                out[f[0]] = int(f[2])
            except ValueError:
                pass
    return out


def tree_entries(source: str):
    """Every file of the tree, sorted by path: [(path, blob_id, size)] or None.

    HEAD is read from the commit object; the index (staged tree) is read from `git ls-files -s`.
    Either way the blob ids are content addresses, which is what makes the identity a statement
    about bytes rather than about a working directory.
    """
    if source == "head":
        cmd = ["git", "-C", str(ROOT), "ls-tree", "-r", "-z", "HEAD"]
    else:
        cmd = ["git", "-C", str(ROOT), "ls-files", "-s", "-z"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    pairs = []
    for entry in r.stdout.split(b"\x00"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        f = meta.split()
        # ls-tree:  <mode> blob <object>            ls-files -s: <mode> <object> <stage>
        blob = f[2] if (source == "head" and len(f) >= 3 and f[1] == b"blob") else (
            f[1] if (source == "index" and len(f) >= 3) else None)
        if blob is None or len(blob) < 7:
            continue          # submodule/commit entries, or an unmerged stage entry
        pairs.append((path.decode("utf-8", "replace"), blob.decode()))
    sizes = blob_sizes([b for _, b in pairs])
    return sorted((path, blob, sizes.get(blob, 0)) for path, blob in pairs)


def compute(source: str):
    """-> (release_id, digest, n_files, total_bytes) or None."""
    entries = tree_entries(source)
    if entries is None:
        return None
    lines, total = [], 0
    for path, blob, size in entries:
        if path == RECORD_REL:
            continue
        lines.append(f"{blob}  {path}\n")
        total += size
    digest = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
    return digest[:12], digest, len(lines), total


def read_record():
    if not RECORD.exists():
        return None
    try:
        return json.loads(RECORD.read_text(encoding="utf-8"))
    except Exception:
        return None


def rev_parse(rev: str = "HEAD") -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", rev],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", action="store_true", help="re-take and write the record")
    ap.add_argument("--check", action="store_true", help="compare the record with the shipped bytes")
    ap.add_argument("--source", choices=("head", "index"), default="head",
                    help="which tree the identity describes (default head: a release is a commit)")
    a = ap.parse_args()

    got = compute(a.source)
    if got is None:
        print("CANNOT COMPUTE: this working tree is not a git checkout, or git is unavailable.")
        print("  The release identity is a statement about the shipped tree, so no value can be")
        print("  derived here. This is not a mismatch.")
        return 3
    release_id, digest, n_files, total = got
    print(f"release_id      {release_id}")
    print(f"digest_sha256   {digest}")
    print(f"source          {a.source}" + (" (the staged tree: what the next commit will contain)"
                                          if a.source == "index" else " (HEAD: what is shipped)"))
    print(f"files           {n_files}  ({total} bytes of blobs)")
    print(f"algorithm       {ALGORITHM}")
    print(f"excluded        {RECORD_REL} (a record cannot contain its own hash)")

    if a.take:
        rec = {"schema": SCHEMA, "release_id": release_id, "digest_sha256": digest,
               "algorithm": ALGORITHM, "source": a.source, "n_files": n_files,
               "total_bytes": total,
               "taken_at_commit": rev_parse("HEAD"),
               "taken_at_commit_note": ("HEAD when the identity was taken. With --source index the "
                                        "record is taken against the staged tree and ships in the "
                                        "commit that tree becomes; the record is excluded from its "
                                        "own coverage, so the value is unaffected."),
               "coverage": "every file of the tree (HEAD, or the staged tree with --source index)",
               "excluded": [RECORD_REL],
               "recompute": "python3 scripts/release_identity.py --check"}
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"recorded -> {RECORD_REL} (taken against {a.source})")
        return 0

    if a.check:
        rec = read_record()
        if rec is None:
            print(f"FAIL: no readable record at {RECORD_REL}; the shipped tree has no recorded identity.")
            print("  Re-take it in this commit: python3 scripts/release_identity.py --take")
            return 1
        if rec.get("release_id") == release_id and rec.get("digest_sha256") == digest:
            print(f"IDENTITY MATCH: the record matches the shipped bytes ({release_id}).")
            staged = compute("index")
            if staged and staged[0] != release_id:
                print(f"note: the staged tree differs from HEAD (its identity would be {staged[0]}); "
                      "that is a change in progress, not a moved release.")
            return 0
        print(f"FAIL: the record is stale. recorded={rec.get('release_id')} "
              f"shipped={release_id} (files {rec.get('n_files')} -> {n_files})")
        print("  The rule is that the identity is re-taken in the same commit as the byte change:")
        print("  python3 scripts/release_identity.py --take --source index   # then commit")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())