#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l0 -- keep the pre-image of the file the flip edits, and freeze what the flip starts from.

Written and run BEFORE the flip (the pre-registration ordering rule of the card: the file on disk
comes first, then the change). It runs AFTER `l0b` (the registration restoration), so the pre-image is
the tree the activation starts from -- which contains the restored `holefill_v12` dictionary entry and
no whitelist member. Writes out/PREIMAGE.json:

  * the bytes and sha256 of `mcp_server/eyekb_core.py` as they stand now, copied to
    pre_images/eyekb_core.py.pre_activation (the pre-registered rollback path);
  * the exact pre-flip text of the two regions the flip rewrites, so the restore is mechanical, and
    how many times each occurs (must be exactly one);
  * the sha256/mtime of this wave's pre-registration, i.e. the ordering proof (pre-reg < outcomes);
  * the git revision the flip starts from (the PARENT reference the default-face device pins) and
    whether the tree was clean apart from this wave;
  * the sha of the pre-restore image that `l0b` kept, so the defect fix's own pre-image is on record
    in the same file that pins the activation's pre-image.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
REPO = "/home/ubuntu/EYEKB_REPO"
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
PRE_DIR = os.path.join(WAVE, "pre_images")
PRE = os.path.join(PRE_DIR, "eyekb_core.py.pre_activation")
PRE_RESTORE = os.path.join(PRE_DIR, "eyekb_core.py.pre_restore")
OUT = os.path.join(WAVE, "out")

BEFORE_R2 = '''    v = (os.environ.get("EYEKB_ACT_ONFIBRO") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _antseg_act_enabled():'''

BEFORE_R3 = '''        if _onfibro_act_enabled():
            names = names + list(ONFIBRO_DEFAULT_LIBS)  # [ONFIBRO] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit'''

REGISTRATION_ENTRY = '"holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json"'


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    p = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    return p.stdout.strip(), p.returncode


def main():
    os.makedirs(PRE_DIR, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    src = open(CORE, encoding="utf-8").read()
    doc = {
        "probe": "l0_preimage.py",
        "core_path": "mcp_server/eyekb_core.py",
        "core_sha256": sha256_file(CORE),
        "core_bytes": os.path.getsize(CORE),
        "core_mtime": subprocess.run(["stat", "-c", "%y", CORE], capture_output=True,
                                     text=True).stdout.strip(),
        "pre_image_path": "docs/plans/activate_holefill_20261022/pre_images/eyekb_core.py.pre_activation",
        "pre_restore_image_path": "docs/plans/activate_holefill_20261022/pre_images/eyekb_core.py.pre_restore",
        "pre_restore_image_sha256": (sha256_file(PRE_RESTORE)
                                     if os.path.exists(PRE_RESTORE) else None),
        "before_comment_region": BEFORE_R2,
        "before_doc_region": BEFORE_R3,
        "before_region_counts": {"whitelist_block_anchor": src.count(BEFORE_R2),
                                 "loader_branch_anchor": src.count(BEFORE_R3)},
        "registration_entry_present": REGISTRATION_ENTRY in src,
        "prereg": "docs/plans/activate_holefill_20261022/PREREG_ACTIVATION_HOLEFILL_20261022.md",
        "prereg_sha256": sha256_file(os.path.join(WAVE, "PREREG_ACTIVATION_HOLEFILL_20261022.md")),
        "prereg_mtime_epoch": os.path.getmtime(
            os.path.join(WAVE, "PREREG_ACTIVATION_HOLEFILL_20261022.md")),
        "base_commit": git("rev-parse", "HEAD")[0],
        "git_status_porcelain": git("status", "--porcelain")[0].splitlines(),
    }
    shutil.copy2(CORE, PRE)
    doc["pre_image_sha256"] = sha256_file(PRE)
    doc["pre_image_bytes"] = os.path.getsize(PRE)
    doc["pre_image_matches_live"] = doc["pre_image_sha256"] == doc["core_sha256"]
    doc["verdict"] = ("PASS" if doc["pre_image_matches_live"]
                      and doc["before_region_counts"] == {"whitelist_block_anchor": 1,
                                                          "loader_branch_anchor": 1}
                      and doc["registration_entry_present"] else "FAIL")
    with open(os.path.join(OUT, "PREIMAGE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("core sha256      :", doc["core_sha256"])
    print("core bytes/mtime :", doc["core_bytes"], doc["core_mtime"])
    print("pre-image        :", doc["pre_image_sha256"], "matches live:", doc["pre_image_matches_live"])
    print("pre-restore image:", doc["pre_restore_image_sha256"])
    print("region counts    :", doc["before_region_counts"],
          "| restored entry present:", doc["registration_entry_present"])
    print("base commit      :", doc["base_commit"])
    print("prereg sha256    :", doc["prereg_sha256"])
    print("l0 verdict       :", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())