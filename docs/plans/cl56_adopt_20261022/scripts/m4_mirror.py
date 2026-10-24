# -*- coding: utf-8 -*-
"""m4_mirror.py -- mirror this wave into the repository's review layer (docs/plans/cl56_adopt_20261022/).

The construction site stays /mnt/D/EyeKB/plans/cl56_adopt_20261022 (where the frozen inputs point); the
repository carries the review copy, which is what the change-control row's anchors resolve against.

Copied: the pre-registration, the report, scripts/, out/ (minus the byte-identity device's scratch),
pre_images/, ledgers/, logs/, discipline/. Nothing outside that directory is written.

Run: /usr/bin/python3 m4_mirror.py
"""
import filecmp
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
REPO = "/home/ubuntu/EYEKB_REPO"
DEST = os.path.join(REPO, "docs", "plans", "cl56_adopt_20261022")
SKIP_DIRS = ("out/default_face_tmp", "__pycache__")
SKIP_FILES = ()          # everything in the wave is mirrored, the scratch directory excepted


def main():
    n, touched = 0, []
    for root, dirs, fns in os.walk(WAVE):
        rel_root = os.path.relpath(root, WAVE).replace(os.sep, "/")
        if rel_root == ".":
            rel_root = ""
        dirs[:] = [d for d in dirs if d != "__pycache__" and
                   (rel_root + "/" + d).lstrip("/") not in
                   [s.split("/", 1)[-1] if "/" in s else s for s in SKIP_DIRS] or True]
        for fn in fns:
            rel = (rel_root + "/" + fn).lstrip("/")
            if any(rel.startswith(s) for s in SKIP_DIRS) or fn in SKIP_FILES:
                continue
            if fn.endswith(".pyc"):
                continue
            src = os.path.join(root, fn)
            dst = os.path.join(DEST, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False):
                continue
            shutil.copy2(src, dst)
            os.chmod(dst, 0o644)
            touched.append(rel)
            n += 1
    print("mirrored %d file(s) into %s" % (n, DEST))
    for t in sorted(touched)[:20]:
        print("   +", t)
    if len(touched) > 20:
        print("   ... %d more" % (len(touched) - 20))


if __name__ == "__main__":
    main()