#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build (or re-verify) the ontology snapshot manifest, and seal the capability registration.

One command rebuilds both, and a re-run returns the same hashes:

    python3 kb/ontology/scripts/build_ont_manifest.py            # verify only (default)
    python3 kb/ontology/scripts/build_ont_manifest.py --take     # re-take the recorded values

What it records
    kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json   the logical address -> repo-relative path ->
                                                     sha256 map the layer resolves through
    kb/ontology/ONT_LAYER_REGISTRY_v1.json           payload_sha256 over its own canonical content,
                                                     with that field excluded (a record cannot
                                                     contain its own hash)

Ordering (this is the part that is easy to get wrong)
    The registry is sealed FIRST, and only then is the manifest's record of the registry's sha256
    taken. Sealing the registry changes its bytes, so a manifest written before the seal records a
    hash that is stale the moment the file is written - the layer would then refuse to answer from a
    perfectly good asset. A re-run with no changes reports VERIFIED.

Discipline
    The repository root is discovered from this file's own location; no absolute path is written.
    Only the three declared assets are hashed. Nothing is downloaded, nothing is written outside
    these two files, and the ontology snapshot itself is never modified: --take only reads it.

Exit codes: 0 = the recorded values match the bytes on disk (or were re-taken);
            1 = a recorded value does not match the bytes on disk (re-take in the same commit);
            3 = the repository could not be located (no claim is made).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

MANIFEST_REL = "kb/ontology/ONTOLOGY_SNAPSHOT_MANIFEST_v1.json"
REGISTRY_REL = "kb/ontology/ONT_LAYER_REGISTRY_v1.json"
SNAPSHOT_REL = "kb/ontology/cl/releases/2026-06-08/cl-base.obo"
ALIGNMENT_REL = "kb/markers/markers_cl_alignment_v2_unified.json"
PAYLOAD_FIELD = "payload_sha256"

ANCHOR_TO_ASSET = {"ont://cl/releases/2026-06-08": SNAPSHOT_REL,
                   f"repo://{REGISTRY_REL}": REGISTRY_REL,
                   f"repo://{ALIGNMENT_REL}": ALIGNMENT_REL}


def repo_root(start: Path) -> Path | None:
    here = start.resolve()
    for d in [here] + list(here.parents):
        if (d / "kb").is_dir() and (d / "mcp_server").is_dir():
            return d
    return None


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def canonical_payload(obj: dict) -> str:
    return json.dumps({k: v for k, v in obj.items() if k != PAYLOAD_FIELD},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--take", action="store_true", help="re-take and write the recorded values")
    a = ap.parse_args()

    root = repo_root(Path(__file__))
    if root is None:
        print("CANNOT RUN: this file is not inside a repository holding kb/ and mcp_server/.")
        return 3

    assets = [SNAPSHOT_REL, REGISTRY_REL, ALIGNMENT_REL]
    for rel in assets:
        if not (root / rel).is_file():
            print(f"FAIL: declared asset absent: {rel}")
            return 1
    live = {rel: {"sha256": sha256_of(root / rel), "bytes": (root / rel).stat().st_size}
            for rel in assets}
    drift = []

    # 1) seal the registry first (its payload hash excludes the field it is written into)
    reg_path = root / REGISTRY_REL
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    want = hashlib.sha256(canonical_payload(reg).encode("utf-8")).hexdigest()
    if reg.get(PAYLOAD_FIELD) != want:
        if a.take:
            reg[PAYLOAD_FIELD] = want
            reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
            back = json.loads(reg_path.read_text(encoding="utf-8"))
            if back.get(PAYLOAD_FIELD) != hashlib.sha256(
                    canonical_payload(back).encode("utf-8")).hexdigest():
                print("FAIL: the sealed registry hash does not survive a re-read.")
                return 1
            live[REGISTRY_REL] = {"sha256": sha256_of(reg_path),
                                  "bytes": reg_path.stat().st_size}
            print(f"sealed registry payload_sha256 = {want}")
        else:
            drift.append(f"{REGISTRY_REL} {PAYLOAD_FIELD}: recorded={reg.get(PAYLOAD_FIELD)} "
                         f"live={want}")

    # 2) then record the manifest's view of the (now final) bytes
    man_path = root / MANIFEST_REL
    man = json.loads(man_path.read_text(encoding="utf-8"))
    for anchor in man.get("anchors", []):
        rel = ANCHOR_TO_ASSET.get(anchor.get("anchor_id"))
        if rel is None:
            print(f"NOTE: manifest anchor not covered by this builder: {anchor.get('anchor_id')}")
            continue
        if anchor.get("path") != rel or anchor.get("sha256") != live[rel]["sha256"]:
            if a.take:
                if anchor.get("sha256") != live[rel]["sha256"]:
                    drift.append(f"{anchor['anchor_id']}: recorded={anchor.get('sha256')} "
                                 f"live={live[rel]['sha256']}")
                anchor["path"] = rel
                anchor["bytes"] = live[rel]["bytes"]
                anchor["sha256"] = live[rel]["sha256"]
            elif anchor.get("sha256") != live[rel]["sha256"]:
                drift.append(f"{anchor['anchor_id']}: recorded={anchor.get('sha256')} "
                             f"live={live[rel]['sha256']}")
    if a.take:
        man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"repo                  {root}")
    for rel in assets:
        print(f"{rel:55s} {live[rel]['bytes']:>10d} bytes  {live[rel]['sha256']}")
    print(f"registry {PAYLOAD_FIELD}  {want}")
    if drift:
        if not a.take:
            print("FAIL: recorded values do not match the bytes on disk:")
            for d in drift:
                print(f"  {d}")
            print("  Re-take in the same commit: python3 kb/ontology/scripts/"
                  "build_ont_manifest.py --take")
            return 1
        print(f"re-taken: {len(drift)} recorded value(s) refreshed")
    print("VERIFIED: the recorded values match the bytes on disk." if not drift
          else "TAKEN: the manifest and registry are sealed to the current bytes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())