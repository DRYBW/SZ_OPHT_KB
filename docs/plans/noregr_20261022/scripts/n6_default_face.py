#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n6 -- the default-face red line (PREREG G5).

Claim under test: the change registered by this card does not alter the default response bytes of
the shipped service.

Method (measurement, not assertion). The parent commit's `mcp_server/eyekb_core.py` is swapped IN
PLACE -- the same absolute path, so every path-carrying field of a response resolves identically and
the only variable is the file's bytes -- and the recorded query set is replayed on the DEFAULT route
(no `tissue` argument, no switch set) in a separate child process. The current file is then swapped
back and the replay repeated. Three readings:

  * `clusters` arm: the 721 recorded cluster gene windows, genes mode, no tissue;
  * `battery` arm: the page listing + cell_type mode for all 76 labelled classes x three species
    arguments -- 229 calls that exercise the non-ranking route too;
  * the repository's own legacy tool-panel identity probe, run under both cores and compared, plus
    a check that the probe file itself is byte-unchanged against the parent commit.

The swap is guarded: the current file's bytes are snapshotted first and restored in a `finally`,
with the sha256 re-verified afterwards.

Writes out/DEFAULT_FACE.json.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
PY = "/usr/bin/python3"
PROBE_PY = "/home/ubuntu/training-venv/bin/python3"
CORE = os.path.join(W.REPO, "mcp_server", "eyekb_core.py")
PROBE = os.path.join(W.REPO, "tests", "probe_tool_panel_identity.py")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sh(cmd, env=None):
    e = dict(os.environ)
    for k in ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_ONFIBRO", "EYEKB_TISSUE_SCOPE",
              "EYEKB_ACT_ANTSEG", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_KB_ANTIUNION",
              "EYEKB_STATE_GUARD", "EYEKB_CL_KEY"):
        e.pop(k, None)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=W.REPO)


def replay(fmode, out_path):
    p = sh([PY, os.path.join(HERE, "n6b_replay_route.py"), fmode, out_path])
    if p.returncode != 0:
        raise SystemExit("replay %s failed: %s" % (fmode, p.stderr[-3000:]))
    return json.load(open(out_path))


def probe():
    p = sh([PROBE_PY, PROBE])
    digests = {}
    for line in p.stdout.splitlines():
        line = line.strip()
        if line.startswith('"legacy_panel"') or line.startswith('"full_panel"'):
            k, v = line.split(":", 1)
            digests[k.strip().strip('"')] = v.strip().strip(',').strip('"')
    return {"rc": p.returncode, "digests": digests,
            "stdout_tail": p.stdout[-2500:], "stderr_tail": p.stderr[-800:]}


def measure(tag, tmp):
    arms = {}
    for fmode in ("clusters", "battery"):
        arms[fmode] = replay(fmode, os.path.join(tmp, "%s_%s.json" % (tag, fmode)))
    return arms, probe()


def main():
    tmp = os.path.join(OUT, "default_face_tmp")
    os.makedirs(tmp, exist_ok=True)
    cur = open(CORE, "rb").read()
    cur_sha = sha(cur)
    head = sh(["git", "-C", W.REPO, "show", "HEAD:mcp_server/eyekb_core.py"])
    if head.returncode != 0:
        raise SystemExit("cannot read the parent commit's core: %s" % head.stderr)
    head_bytes = head.stdout.encode()
    doc = {"probe": "n6_default_face.py", "core_path": "mcp_server/eyekb_core.py",
           "attached_commit": sh(["git", "-C", W.REPO, "rev-parse", "HEAD"]).stdout.strip(),
           "current_core_sha256": cur_sha, "parent_core_sha256": sha(head_bytes)}
    try:
        with open(CORE, "wb") as f:
            f.write(head_bytes)
        os.remove(os.path.join(W.REPO, "mcp_server", "__pycache__", "eyekb_core.cpython-314.pyc")) \
            if os.path.exists(os.path.join(W.REPO, "mcp_server", "__pycache__",
                                           "eyekb_core.cpython-314.pyc")) else None
        doc["parent_core_sha_verified_in_place"] = (
            W.sha256_file(CORE) == sha(head_bytes))
        legacy_arms, legacy_probe = measure("parent", tmp)
    finally:
        with open(CORE, "wb") as f:
            f.write(cur)
        doc["restored_core_sha256"] = W.sha256_file(CORE)
        doc["restored_matches_snapshot"] = (doc["restored_core_sha256"] == cur_sha)
    now_arms, now_probe = measure("current", tmp)

    ok_all = doc["restored_matches_snapshot"] and doc["parent_core_sha_verified_in_place"]
    arms = {}
    for fmode in ("clusters", "battery"):
        a, b = legacy_arms[fmode], now_arms[fmode]
        diff = [k for k in a["hashes"] if a["hashes"].get(k) != b["hashes"].get(k)]
        only_a = [k for k in a["hashes"] if k not in b["hashes"]]
        only_b = [k for k in b["hashes"] if k not in a["hashes"]]
        ident = (not diff) and (not only_a) and (not only_b) \
            and a["combined_md5"] == b["combined_md5"]
        ok_all = ok_all and ident
        arms[fmode] = {"n_queries": a["n"], "identical": ident,
                       "parent_combined_md5": a["combined_md5"],
                       "current_combined_md5": b["combined_md5"],
                       "n_differing": len(diff), "n_only_parent": len(only_a),
                       "n_only_current": len(only_b), "differing": diff[:20]}
    doc["arms"] = arms

    head_probe = sh(["git", "-C", W.REPO, "show", "HEAD:tests/probe_tool_panel_identity.py"])
    probe_unchanged = (head_probe.returncode == 0 and
                       sha(open(PROBE, "rb").read()) == sha(head_probe.stdout.encode()))
    doc["legacy_tool_panel_probe"] = {
        "path": "tests/probe_tool_panel_identity.py",
        "byte_unchanged_vs_parent_commit": bool(probe_unchanged),
        "parent_core_run": {"rc": legacy_probe["rc"], "digests": legacy_probe["digests"]},
        "current_core_run": {"rc": now_probe["rc"], "digests": now_probe["digests"]},
        "digests_identical": legacy_probe["digests"] == now_probe["digests"],
        "stdout_tail": now_probe["stdout_tail"],
    }
    ok_all = ok_all and probe_unchanged and now_probe["rc"] == 0 \
        and legacy_probe["digests"] == now_probe["digests"]
    doc["verdict"] = "PASS" if ok_all else "FAIL"
    W.save_json(os.path.join(OUT, "DEFAULT_FACE.json"), doc)

    print("   core restored == snapshot:", doc["restored_matches_snapshot"],
          " parent core verified in place:", doc["parent_core_sha_verified_in_place"])
    for fmode, d in arms.items():
        print("   %-9s n=%d identical=%s parent_md5=%s current_md5=%s differing=%d"
              % (fmode, d["n_queries"], d["identical"], d["parent_combined_md5"],
                 d["current_combined_md5"], d["n_differing"]))
        for k in d["differing"][:5]:
            print("        DIFF", k)
    print("   tool-panel probe unchanged=%s digests_identical=%s parent=%s current=%s"
          % (probe_unchanged, doc["legacy_tool_panel_probe"]["digests_identical"],
             legacy_probe["digests"], now_probe["digests"]))
    print("   G5 verdict:", doc["verdict"])
    print("wrote", os.path.join(OUT, "DEFAULT_FACE.json"))
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())