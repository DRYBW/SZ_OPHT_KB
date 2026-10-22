#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m3b -- the three-arm ruler run, with the LOCAL copy of the ruler and its patch record.

Arms (all read-only, no threshold in this script):

  C1  frozen rows  x frozen ruler  -> must reproduce the frozen 56-row result (already measured by m3)
  C2  frozen rows  x local ruler   -> must reproduce the frozen result too: this is the proof that the
                                      two-line repair is behaviour-preserving
  A1  augmented rows x local ruler -> the re-measurement the card asks for

Writes out/RULER_PATCH.json, out/ruler_control_local/**, out/ruler_augmented/**,
out/RULER_RUNS.json (updated).
"""
import difflib
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
FROZEN_RULER = os.path.join(CONS, "scripts", "c3_separation.py")
LOCAL_RULER = os.path.join(HERE, "c3_separation_local.py")
FROZEN_ROWS = os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json")
FROZEN_SEP = os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json")
AUG_ROWS = os.path.join(OUT, "SUBTYPE_OBSERVABILITY_rows_augmented.json")
PY = "/usr/bin/python3"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run_ruler(ruler, obs, outdir, log):
    os.makedirs(outdir, exist_ok=True)
    cmd = [PY, ruler, "--observability", obs, "--out", outdir]
    with open(log, "w", encoding="utf-8") as lg:
        p = subprocess.run(cmd, stdout=lg, stderr=subprocess.STDOUT, cwd=os.path.dirname(ruler))
    return {"cmd": " ".join(cmd), "rc": p.returncode, "outdir": outdir, "log": log}


def compare(a_path, b_path):
    a = json.load(open(a_path, encoding="utf-8"))
    b = json.load(open(b_path, encoding="utf-8"))
    if len(a) != len(b):
        return {"n_a": len(a), "n_b": len(b), "identical_verdicts": False,
                "mismatch": "row count differs"}
    bad = [{"i": i, "a": a[i]["volume"] + "|" + a[i]["subtype"], "a_result": a[i]["result"],
            "b_result": b[i]["result"]} for i in range(len(a))
           if (a[i]["volume"], a[i]["subtype"], a[i]["result"]) != (b[i]["volume"], b[i]["subtype"], b[i]["result"])]
    return {"n_a": len(a), "n_b": len(b), "identical_verdicts": not bad, "n_mismatch": len(bad),
            "mismatches": bad[:10]}


def main():
    frz_src = open(FROZEN_RULER, encoding="utf-8").read().splitlines(keepends=True)
    loc_src = open(LOCAL_RULER, encoding="utf-8").read().splitlines(keepends=True)
    diff = "".join(difflib.unified_diff(frz_src, loc_src, fromfile="frozen c3_separation.py",
                                        tofile="local c3_separation_local.py", n=3))
    n_changed = sum(1 for l in diff.splitlines() if l.startswith(("+", "-")) and not l.startswith(("+++", "---")))
    patch = {"probe": "m3b_remeasure_local.py", "frozen_ruler": FROZEN_RULER,
             "frozen_ruler_sha256": sha(FROZEN_RULER), "local_ruler": LOCAL_RULER,
             "local_ruler_sha256": sha(LOCAL_RULER), "n_changed_lines": n_changed,
             "unified_diff": diff,
             "why": "the frozen ruler raises IndexError while REPORTING marker_detail when a marker's "
                    "p-value is None (constant-vs-constant); the local copy re-indexes q through a "
                    "qmap. Thresholds/statistics untouched; the control arm re-run below proves it."}
    json.dump(patch, open(os.path.join(OUT, "RULER_PATCH.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("ruler patch: %d changed diff lines; frozen=%s local=%s"
          % (n_changed, patch["frozen_ruler_sha256"][:12], patch["local_ruler_sha256"][:12]))

    c2 = run_ruler(LOCAL_RULER, FROZEN_ROWS, os.path.join(OUT, "ruler_control_local"),
                   os.path.join(WAVE, "logs", "m3b_control_local.log"))
    a1 = run_ruler(LOCAL_RULER, AUG_ROWS, os.path.join(OUT, "ruler_augmented"),
                   os.path.join(WAVE, "logs", "m3b_augmented.log"))
    c2_cmp = compare(os.path.join(c2["outdir"], "SUBTYPE_SEPARATION.json"), FROZEN_SEP)
    c1_cmp = compare(os.path.join(OUT, "ruler_control", "SUBTYPE_SEPARATION.json"), FROZEN_SEP)
    a1_cmp = compare(os.path.join(a1["outdir"], "SUBTYPE_SEPARATION.json"),
                     os.path.join(OUT, "ruler_control", "SUBTYPE_SEPARATION.json"))

    doc = json.load(open(os.path.join(OUT, "RULER_RUNS.json"), encoding="utf-8"))
    doc.update({"probe": "m3b_remeasure_local.py", "local_ruler_sha256": patch["local_ruler_sha256"],
                "control_frozen_ruler": c1_cmp, "control_local_ruler": c2_cmp,
                "augmented_vs_control": a1_cmp,
                "arm_c2": c2, "arm_a1": a1,
                "n_rows_changed_by_augmentation": a1_cmp.get("n_mismatch")})
    json.dump(doc, open(os.path.join(OUT, "RULER_RUNS.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    tail = open(a1["log"], encoding="utf-8").read().strip().splitlines()[-3:]
    print("C1 frozen ruler x frozen rows  : identical=%s" % c1_cmp["identical_verdicts"])
    print("C2 local ruler  x frozen rows  : identical=%s" % c2_cmp["identical_verdicts"])
    print("A1 local ruler  x augmented    : rc=%d rows_changed=%s" % (a1["rc"], a1_cmp.get("n_mismatch")))
    for l in tail:
        print("   ", l)
    return 0 if (c1_cmp["identical_verdicts"] and c2_cmp["identical_verdicts"] and a1["rc"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())