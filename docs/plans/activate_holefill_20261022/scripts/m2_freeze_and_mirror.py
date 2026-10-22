#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m2 -- freeze this wave's own artefacts, and mirror the wave to the plan/delivery tree.

The repository holds the committed wave; `/mnt/D/EyeKB/plans/activate_holefill_20261022` is what the
laboratory reads on the data volume, and it is verified rather than trusted (every file is compared by
sha256 after the copy). Writes MANIFEST.sha256 in canonical `sha256sum` format and out/MIRROR_CHECK.json.

  python3 scripts/m2_freeze_and_mirror.py            # freeze + mirror + verify
  python3 scripts/m2_freeze_and_mirror.py --check    # verify an existing manifest
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
DEST = "/mnt/D/EyeKB/plans/activate_holefill_20261022"
MANIFEST = os.path.join(WAVE, "MANIFEST.sha256")
SKIP_DIRS = {"__pycache__"}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files():
    out = []
    for root, dirs, names in os.walk(WAVE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, WAVE)
            if rel in ("MANIFEST.sha256", "out/MIRROR_CHECK.json"):
                continue
            out.append(rel)
    return sorted(out)


def write_manifest():
    lines = ["%s  %s" % (sha256_file(os.path.join(WAVE, r)), r) for r in files()]
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("# docs/plans/activate_holefill_20261022 -- every artefact of this wave\n")
        f.write("\n".join(lines) + "\n")
    return len(lines)


def check_manifest():
    bad = []
    n = 0
    for line in open(MANIFEST, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        want, rel = line.split("  ", 1)
        n += 1
        got = sha256_file(os.path.join(WAVE, rel))
        if got != want:
            bad.append(rel)
    return n, bad


def mirror():
    os.makedirs(DEST, exist_ok=True)
    copied, compared, differing = 0, 0, []
    for rel in files():
        src, dst = os.path.join(WAVE, rel), os.path.join(DEST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        compared += 1
        if sha256_file(src) != sha256_file(dst):
            differing.append(rel)
    for extra in ("MANIFEST.sha256",):
        shutil.copy2(os.path.join(WAVE, extra), os.path.join(DEST, extra))
    return copied, compared, differing


def main():
    if "--check" in sys.argv:
        n, bad = check_manifest()
        print("manifest lines:", n, "| differing:", len(bad), bad[:5])
        return 0 if not bad else 1
    n = write_manifest()
    copied, compared, differing = mirror()
    doc = {"probe": "m2_freeze_and_mirror.py",
           "manifest": "docs/plans/activate_holefill_20261022/MANIFEST.sha256",
           "manifest_lines": n, "manifest_sha256": sha256_file(MANIFEST),
           "mirror": {"source": WAVE, "destination": DEST, "files_copied": copied,
                      "files_compared": compared, "files_differing": len(differing),
                      "differing": differing[:10],
                      "excluded": ["__pycache__/**", "MANIFEST.sha256 (copied last, not compared)",
                                   "out/MIRROR_CHECK.json (this file)"]},
           "verdict": "PASS" if not differing else "FAIL"}
    with open(os.path.join(WAVE, "out", "MIRROR_CHECK.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    n2, bad = check_manifest()
    print("manifest lines:", n, "| re-checked:", n2, "| differing:", len(bad))
    print("mirrored files:", copied, "| compared:", compared, "| differing:", len(differing))
    print("manifest sha256:", doc["manifest_sha256"])
    print("verdict:", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" and not bad else 1


if __name__ == "__main__":
    sys.exit(main())