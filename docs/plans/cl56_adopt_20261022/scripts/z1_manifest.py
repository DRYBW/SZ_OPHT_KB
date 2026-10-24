# -*- coding: utf-8 -*-
"""z1_manifest.py -- sha256 manifest of this wave's delivered artefacts (the manifest is built LAST).

Exclusions, declared in the file's own header rather than silently skipped:
  * this manifest itself (a file cannot carry its own hash);
  * `logs/` -- per-step stdout, rewritten on every chain run;
  * `ledgers/net_audit.log` -- the audit hook appends to it while the chain runs;
  * `out/default_face_tmp/` -- the byte-identity device's per-arm scratch;
  * `out/CLONE_*` -- the clean-clone gate readouts, written after this manifest.

Also prints the sha256 of the two repository files this card edits, so the reader can tie the wave to the
commit without trusting prose.

Run: /usr/bin/python3 z1_manifest.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
REPO = "/home/ubuntu/EYEKB_REPO"

INCLUDE_DIRS = ("scripts", "out", "pre_images", "discipline", "ledgers")
INCLUDE_FILES = ("PREREG_ADOPT_CL56_20261022.md", "REPORT.md")
EXCLUDE_PREFIX = ("logs/", "out/default_face_tmp/", "out/CLONE_", "ledgers/net_audit.log")
EXCLUDE_EXACT = ("out/MANIFEST.sha256", "out/REPO_SHA_AFTER.json", "out/SCORE_TABLE.json")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    files = []
    for f in INCLUDE_FILES:
        p = os.path.join(WAVE, f)
        if os.path.exists(p):
            files.append(f)
    for d in INCLUDE_DIRS:
        for root, dirs, fns in os.walk(os.path.join(WAVE, d)):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for fn in fns:
                rel = os.path.relpath(os.path.join(root, fn), WAVE).replace(os.sep, "/")
                if rel in EXCLUDE_EXACT or any(rel.startswith(p) for p in EXCLUDE_PREFIX):
                    continue
                files.append(rel)
    files = sorted(set(files))
    header = ["# CL-56 adoption wave (card t_fabddb85, board pi-briefing) -- artefact manifest",
              "# verify with: cd /mnt/D/EyeKB/plans/cl56_adopt_20261022 && sha256sum -c out/MANIFEST.sha256",
              "# excluded on purpose: out/MANIFEST.sha256 (self), logs/ (rewritten per run),",
              "#   ledgers/net_audit.log (appended during the run), out/default_face_tmp/ (device scratch),",
              "#   out/CLONE_* (clean-clone gate readouts, written after this file),\n#   out/REPO_SHA_AFTER.json (written by this script after the file list is computed)"]
    lines = header + ["%s  %s" % (sha(os.path.join(WAVE, f)), f) for f in files]
    with open(os.path.join(OUT, "MANIFEST.sha256"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    repo = {rel: sha(os.path.join(REPO, rel)) for rel in
            ("mcp_server/eyekb_core.py", "kb/markers/markers_v15_cl56_increment.json",
             "kb/markers/markers_cl_alignment_v2_unified.json", "docs/W3_PIPELINE_REGISTRY.tsv",
             "docs/SWITCH_COVERAGE_REGISTRY.tsv", "docs/CHANGE_CONTROL_G6_INSTANCE.tsv",
             "docs/W3_MANIFEST.sha256")}
    json.dump(repo, open(os.path.join(OUT, "REPO_SHA_AFTER.json"), "w"), indent=1)
    print("manifest entries:", len(files))
    print("wrote out/MANIFEST.sha256 (+ out/REPO_SHA_AFTER.json)")


if __name__ == "__main__":
    main()