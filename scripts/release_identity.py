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
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "RELEASE_IDENTITY.json"
RECORD_REL = "docs/RELEASE_IDENTITY.json"
MANIFEST = ROOT / "docs" / "RELEASE_MANIFEST_v1.json"
MANIFEST_REL = "docs/RELEASE_MANIFEST_v1.json"
SCHEMA = "eyekb-release-identity/1.0"
ALGORITHM = "sha256 over sorted lines '<git blob id>  <path>' for every file in the tree"
# The records that cannot contain their own hash, and that therefore sit outside the coverage: the
# identity record, the release manifest, and a card's commit log (a commit's hash depends on the
# listing that includes the file naming it, so it can only be written after the commit).
EXCLUDED = (RECORD_REL, MANIFEST_REL, "docs/plans/l5_ontlayer_20261022/ledgers/COMMIT.txt")
# Layer decomposition. The service surface is the shipped server code; the knowledge surface is the
# shipped knowledge assets. The split is declared here and must not be re-cut silently: two releases
# with the same release_id can then still be told apart by which layer moved.
SERVICE_PREFIXES = ("mcp_server/",)
SERVICE_EXACT = ("scripts/release_identity.py",)
KNOWLEDGE_PREFIXES = ("kb/", "literature_db/")
# Toggles whose observed value belongs to the effective profile. Absent = the release default.
PROFILE_TOGGLES = ("EYEKB_ACT_V6", "EYEKB_ACT_ANTSEG", "EYEKB_KBGOV_B5", "EYEKB_CN_REWRITE",
                   "EYEKB_SPECIES_ROUTE", "EYEKB_ONT_LAYER", "EYEKB_ABSTAIN_REASON",
                   "EYEKB_FALLBACK_WIDEN", "EYEKB_STATE_GUARD", "EYEKB_DB_DIR")
CAPABILITY_REGISTRY = "kb/ontology/ONT_LAYER_REGISTRY_v1.json"
PROTOCOL_LITERAL = re.compile(r'^PROTOCOL_GENERATION\s*=\s*"([^"]+)"', re.M)


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
        if path in EXCLUDED:
            continue
        lines.append(f"{blob}  {path}\n")
        total += size
    digest = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
    return digest[:12], digest, len(lines), total


def layer_digest(entries, prefixes, exact=("*NEVER*",)):
    """Digest of one declared surface, same construction as the release identity so the two are
    comparable. Returns (layer_id, digest, n_files, total_bytes)."""
    lines, total, n = [], 0, 0
    for path, blob, size in entries:
        if path in EXCLUDED:
            continue
        if not (path.startswith(prefixes) or path in exact):
            continue
        lines.append(f"{blob}  {path}\n")
        total += size
        n += 1
    d = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
    return d[:12], d, n, total


def protocol_generation() -> str:
    """The wire-contract label, read from the server that carries it - one source of truth."""
    try:
        txt = (ROOT / "mcp_server" / "server.py").read_text(encoding="utf-8")
        m = PROTOCOL_LITERAL.search(txt)
        return m.group(1) if m else ""
    except Exception:
        return ""


def read_registry_row():
    """The capability registration, as the identity record reports it."""
    try:
        reg = json.loads((ROOT / CAPABILITY_REGISTRY).read_text(encoding="utf-8"))
    except Exception:
        return None
    return {"capability_id": reg.get("capability_id"), "version": reg.get("version"),
            "registered": bool(reg.get("registered")),
            "default_state": reg.get("default_state"),
            "whitelist": reg.get("whitelist"),
            "route_env": reg.get("route_env"),
            "payload_sha256": reg.get("payload_sha256")}


def effective_profile(service_id, knowledge_id, layers):
    """What this run actually used: the observed toggle values, the registered capabilities and
    their state, and the layer identities. Volatile fields (timestamps, commit ids, working
    directory) are deliberately absent, so the same configuration gives the same value."""
    reg = read_registry_row()
    prof = {
        "protocol_generation": protocol_generation(),
        "service_build_id": service_id,
        "knowledge_bundle_id": knowledge_id,
        "toggles": {k: os.environ.get(k) for k in PROFILE_TOGGLES},
        "registered_capabilities": ([{"capability_id": reg["capability_id"],
                                      "state": "OFF" if not reg["whitelist"] else "ROUTED",
                                      "whitelist": reg["whitelist"],
                                      "route_env": reg["route_env"]}] if reg else []),
        "layers": layers,
    }
    blob = json.dumps(prof, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return prof, hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


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
    entries = tree_entries(a.source) or []
    svc_id, svc_dig, svc_n, svc_bytes = layer_digest(entries, SERVICE_PREFIXES, SERVICE_EXACT)
    knw_id, knw_dig, knw_n, knw_bytes = layer_digest(entries, KNOWLEDGE_PREFIXES)
    layers = {"release_id": release_id, "service_build_id": svc_id,
              "knowledge_bundle_id": knw_id}
    prof, profile_id = effective_profile(svc_id, knw_id, layers)
    layers["effective_profile_id"] = profile_id
    print(f"release_id      {release_id}")
    print(f"digest_sha256   {digest}")
    print(f"service_build_id      {svc_id}   ({svc_n} files, {svc_bytes} bytes: mcp_server/ + the "
          f"release tooling)")
    print(f"knowledge_bundle_id   {knw_id}   ({knw_n} files, {knw_bytes} bytes: kb/ + literature_db/)")
    print(f"effective_profile_id  {profile_id}   (observed toggles + registered capabilities; "
          f"volatile fields excluded)")
    print(f"protocol_generation   {protocol_generation()}")
    print(f"source          {a.source}" + (" (the staged tree: what the next commit will contain)"
                                          if a.source == "index" else " (HEAD: what is shipped)"))
    print(f"files           {n_files}  ({total} bytes of blobs)")
    print(f"algorithm       {ALGORITHM}")
    print(f"excluded        {', '.join(EXCLUDED)} (a record cannot contain its own hash)")

    if a.take:
        rec = {"schema": SCHEMA, "release_id": release_id, "digest_sha256": digest,
               "algorithm": ALGORITHM, "source": a.source, "n_files": n_files,
               "total_bytes": total,
               "protocol_generation": protocol_generation(),
               "service_build_id": svc_id, "service_build_id_digest": svc_dig,
               "service_build_id_coverage": {"prefixes": list(SERVICE_PREFIXES),
                                             "exact": list(SERVICE_EXACT),
                                             "n_files": svc_n, "bytes": svc_bytes},
               "knowledge_bundle_id": knw_id, "knowledge_bundle_id_digest": knw_dig,
               "knowledge_bundle_id_coverage": {"prefixes": list(KNOWLEDGE_PREFIXES),
                                                "n_files": knw_n, "bytes": knw_bytes},
               "effective_profile_id": profile_id, "effective_profile": prof,
               "effective_profile_rule": ("the observed toggle values, the registered capabilities "
                                          "and their state, and the layer identities; volatile "
                                          "fields (timestamps, commit ids, working directory) are "
                                          "deliberately absent, so the same configuration gives the "
                                          "same value whatever day it is taken"),
               "layers_note": ("The four layers are separate on purpose: protocol_generation "
                               "describes the wire contract, service_build_id the server code, "
                               "knowledge_bundle_id the shipped knowledge assets, and "
                               "effective_profile_id what actually took effect this run. A caller "
                               "needs the last two together - the resolvable release manifest "
                               "identifier and the configuration that was in force."),
               "taken_at_commit": rev_parse("HEAD"),
               "taken_at_commit_note": ("HEAD when the identity was taken. With --source index the "
                                        "record is taken against the staged tree and ships in the "
                                        "commit that tree becomes; the records are excluded from "
                                        "their own coverage, so the value is unaffected."),
               "coverage": ("every file of the tree (HEAD, or the staged tree with --source index) "
                            "except the identity record and the release manifest"),
               "excluded": list(EXCLUDED),
               "recompute": "python3 scripts/release_identity.py --check"}
        RECORD.parent.mkdir(parents=True, exist_ok=True)
        RECORD.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

        files = [{"path": p, "git_blob": b, "bytes": s} for p, b, s in entries
                 if p not in EXCLUDED]
        man = {"schema": "eyekb-release-manifest/1.0",
               "release_id": release_id, "digest_sha256": digest, "algorithm": ALGORITHM,
               "source": a.source, "n_files": len(files), "total_bytes": sum(f["bytes"] for f in files),
               "layers": {"protocol_generation": protocol_generation(),
                          "service_build_id": svc_id,
                          "knowledge_bundle_id": knw_id,
                          "effective_profile_id": profile_id},
               "excluded": list(EXCLUDED),
               "immutability_note": ("release_id is the sha256 of the canonical listing of exactly "
                                     "the files below, so the value and the manifest cannot drift "
                                     "apart: recompute the listing, recompute the hash, compare. "
                                     "The manifest itself and the identity record are excluded, "
                                     "because a record cannot contain its own hash."),
               "recompute": "python3 scripts/release_identity.py --check",
               "files": files}
        MANIFEST.write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"recorded -> {RECORD_REL} (taken against {a.source})")
        print(f"recorded -> {MANIFEST_REL} ({len(files)} files)")
        return 0

    if a.check:
        rec = read_record()
        if rec is None:
            print(f"FAIL: no readable record at {RECORD_REL}; the shipped tree has no recorded identity.")
            print("  Re-take it in this commit: python3 scripts/release_identity.py --take")
            return 1
        bad = [k for k, v in (("release_id", release_id), ("digest_sha256", digest),
                              ("service_build_id", svc_id),
                              ("knowledge_bundle_id", knw_id),
                              ("effective_profile_id", profile_id)) if rec.get(k) != v]
        if not bad:
            print(f"IDENTITY MATCH: the record matches the shipped bytes ({release_id}); "
                  f"service {svc_id}, knowledge {knw_id}, profile {profile_id}.")
            # the manifest must agree with the record item by item
            try:
                m = json.loads(MANIFEST.read_text(encoding="utf-8"))
                mm = [k for k, v in (("release_id", release_id), ("digest_sha256", digest))
                      if m.get(k) != v]
                listed = hashlib.sha256("".join(f"{f['git_blob']}  {f['path']}\n"
                                                for f in sorted(m.get("files", []),
                                                                key=lambda x: x["path"]))
                                        .encode("utf-8")).hexdigest()
                if mm or listed != digest or m.get("n_files") != n_files:
                    print(f"FAIL: {MANIFEST_REL} is not bound to this release "
                          f"(mismatched fields: {mm or 'none'}; listing digest "
                          f"{listed[:12]} vs {release_id}; files {m.get('n_files')} vs {n_files}).")
                    return 1
                print(f"MANIFEST MATCH: {MANIFEST_REL} lists {n_files} files and its listing "
                      f"recomputes to the recorded release_id.")
            except Exception as e:
                print(f"FAIL: {MANIFEST_REL} unreadable ({type(e).__name__}); the release has no "
                      f"manifest. Re-take it: python3 scripts/release_identity.py --take")
                return 1
            staged = compute("index")
            if staged and staged[0] != release_id:
                print(f"note: the staged tree differs from HEAD (its identity would be {staged[0]}); "
                      "that is a change in progress, not a moved release.")
            return 0
        print(f"FAIL: the record is stale (fields: {', '.join(bad)}). recorded release_id="
              f"{rec.get('release_id')} shipped={release_id} "
              f"(files {rec.get('n_files')} -> {n_files})")
        print("  The rule is that the identity is re-taken in the same commit as the byte change:")
        print("  python3 scripts/release_identity.py --take --source index   # then commit")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())