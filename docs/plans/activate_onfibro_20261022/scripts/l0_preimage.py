#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l0 -- keep the pre-image of the file the flip edits, and freeze what the flip starts from.

Written and run BEFORE the flip (the pre-registration ordering rule of the card: the file on disk
comes first, then the change). Writes out/PREIMAGE.json:

  * the bytes and sha256 of `mcp_server/eyekb_core.py` as they stand now, copied to
    pre_images/eyekb_core.py.pre_activation (route 2 of the pre-registered rollback path);
  * the exact pre-flip text of the two regions the flip rewrites, so the restore is mechanical;
  * the sha256/mtime of this wave's pre-registration, i.e. the ordering proof (pre-reg < outcomes);
  * the git revision the flip starts from and whether the tree was clean apart from this wave.
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
OUT = os.path.join(WAVE, "out")

# the two regions the flip rewrites, verbatim as they stand before the flip
BEFORE_COMMENT = """# [ONFIBRO t_0c40c7b1] whitelist for the optic-nerve fibroblast carrier.  EMPTY BY DESIGN: the
# registration is deliberately unreachable from the default `all` set, so this predicate exists to
# make the OFF state explicit and machine-readable rather than to open a route.  Semantics follow
# the ACT-v6 discipline so a future activation wave inherits an obvious shape:
# {0,false,off,no} = OFF; unset/empty/anything else = the value of this switch, which -- with an
# empty whitelist -- still merges nothing.
ONFIBRO_DEFAULT_LIBS = ()
"""
BEFORE_DOC = '''    """env EYEKB_ACT_ONFIBRO in {0,false,off,no} = OFF; unset/anything else = ON.

    ON still injects nothing: ONFIBRO_DEFAULT_LIBS is empty by design (card t_0c40c7b1 red line --
    this registration may not change the default response bytes). The library is reachable by name
    only, and the merged effect is a measurement artefact, not a shipped route.
    """
'''


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
        "pre_image_path": "docs/plans/activate_onfibro_20261022/pre_images/eyekb_core.py.pre_activation",
        "before_comment_region": BEFORE_COMMENT,
        "before_doc_region": BEFORE_DOC,
        "before_region_counts": {"comment": src.count(BEFORE_COMMENT),
                                 "doc": src.count(BEFORE_DOC)},
        "prereg": "docs/plans/activate_onfibro_20261022/PREREG_ACTIVATION_ONFIBRO_20261022.md",
        "prereg_sha256": sha256_file(os.path.join(WAVE, "PREREG_ACTIVATION_ONFIBRO_20261022.md")),
        "prereg_mtime_epoch": os.path.getmtime(
            os.path.join(WAVE, "PREREG_ACTIVATION_ONFIBRO_20261022.md")),
        "base_commit": git("rev-parse", "HEAD")[0],
        "git_status_porcelain": git("status", "--porcelain")[0].splitlines(),
    }
    shutil.copy2(CORE, PRE)
    doc["pre_image_sha256"] = sha256_file(PRE)
    doc["pre_image_bytes"] = os.path.getsize(PRE)
    doc["pre_image_matches_live"] = doc["pre_image_sha256"] == doc["core_sha256"]
    doc["verdict"] = ("PASS" if doc["pre_image_matches_live"]
                      and doc["before_region_counts"] == {"comment": 1, "doc": 1} else "FAIL")
    with open(os.path.join(OUT, "PREIMAGE.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("core sha256      :", doc["core_sha256"])
    print("core bytes/mtime :", doc["core_bytes"], doc["core_mtime"])
    print("pre-image        :", doc["pre_image_sha256"], "matches live:", doc["pre_image_matches_live"])
    print("region counts    :", doc["before_region_counts"])
    print("base commit      :", doc["base_commit"])
    print("prereg sha256    :", doc["prereg_sha256"])
    print("l0 verdict       :", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())