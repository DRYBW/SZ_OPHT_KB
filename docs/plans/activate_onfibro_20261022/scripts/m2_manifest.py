#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m2 -- manifest of this wave's artefacts (out/MANIFEST.json + out/MANIFEST.sha256).

Taken after every artefact is written and before the gate, so a drifting artefact is the gate's job
rather than a human's. `ledgers/` and `logs/` are runtime output that the chain rewrites while it
runs; they are excluded from the manifest on purpose (and the exclusion is stated in the manifest
itself rather than left implicit). The MANIFEST files themselves are excluded, because a record
cannot contain its own hash.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
EXCLUDE_PREFIX = ("./ledgers/", "ledgers/", "./logs/", "logs/", "./out/MANIFEST")
EXCLUDE_SUFFIX = (".pyc",)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    files = []
    for root, dirs, names in os.walk(WAVE):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, WAVE)
            if rel.startswith(("ledgers/", "logs/")) or rel.endswith(EXCLUDE_SUFFIX) \
                    or rel.startswith("out/MANIFEST"):
                continue
            files.append({"rel": rel, "bytes": os.path.getsize(p), "sha256": sha256(p)})
    files.sort(key=lambda e: e["rel"])
    doc = {"probe": "m2_manifest.py", "wave": "docs/plans/activate_onfibro_20261022",
           "n_files": len(files), "files": files,
           "excluded": ["ledgers/**", "logs/**", "out/MANIFEST.json", "out/MANIFEST.sha256"],
           "exclusion_reason": ("ledgers/ and logs/ are runtime output that this chain rewrites "
                                "while it runs; the manifest files cannot contain their own hash"),
           "verify": "python3 docs/plans/activate_onfibro_20261022/scripts/m2_manifest.py --check"}
    json.dump(doc, open(os.path.join(OUT, "MANIFEST.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
        f.write("# docs/plans/activate_onfibro_20261022 -- every artefact of this wave\n")
        f.write("# verify (from this directory): sha256sum -c out/MANIFEST.sha256\n")
        for e in files:
            f.write("%s  %s\n" % (e["sha256"], e["rel"]))
    print("manifest: %d files" % len(files))
    return 0


def check():
    doc = json.load(open(os.path.join(OUT, "MANIFEST.json")))
    bad = [e["rel"] for e in doc["files"]
           if not os.path.exists(os.path.join(WAVE, e["rel"]))
           or sha256(os.path.join(WAVE, e["rel"])) != e["sha256"]]
    print("manifest check: files=%d drifting=%d %s" % (len(doc["files"]), len(bad), bad[:8]))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(check() if "--check" in sys.argv else main())