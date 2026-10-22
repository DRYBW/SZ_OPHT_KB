#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m3 -- build the augmented marker lists and re-measure with the FROZEN RULER, unmodified.

Three things happen here, and the third is the one the card asks for:

  1. CONTROL arm -- the ruler is run on the **frozen** observability rows, into its own directory. It
     must reproduce the frozen 56-row result exactly; if it does not, the environment differs from
     the frozen run and nothing downstream is interpretable. (PREREG section 7.)
  2. The augmented rows file: the frozen rows with `_markers_all` extended by the admitted candidates
     for in-scope subtypes. Everything else is byte-preserved; the frozen file is never written.
  3. AUGMENTED arm -- the same ruler, same thresholds, same volumes, run on the augmented rows.

No threshold lives in this script: AUC/FDR/cell floors are the ruler's own constants, read from
`plans/consensus_subtype_20261022/scripts/c3_separation.py` by executing that file.

Writes out/SUBTYPE_OBSERVABILITY_rows_augmented.json, out/ruler_control/**, out/ruler_augmented/**,
out/RULER_RUNS.json.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
RULER = os.path.join(CONS, "scripts", "c3_separation.py")
FROZEN_ROWS = os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json")
FROZEN_SEP = os.path.join(CONS, "out", "SUBTYPE_SEPARATION.json")
PY = "/usr/bin/python3"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run_ruler(obs_path, outdir, logpath):
    os.makedirs(outdir, exist_ok=True)
    cmd = [PY, RULER, "--observability", obs_path, "--out", outdir]
    with open(logpath, "w", encoding="utf-8") as lg:
        p = subprocess.run(cmd, stdout=lg, stderr=subprocess.STDOUT, cwd=os.path.dirname(RULER))
    tail = open(logpath, encoding="utf-8").read().strip().splitlines()[-1:]
    return {"cmd": " ".join(cmd), "rc": p.returncode, "log": logpath, "tail": tail,
            "result_json": os.path.join(outdir, "SUBTYPE_SEPARATION.json")}


def main():
    lit = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), encoding="utf-8"))
    meas = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_MEASURABILITY.json"),
                          encoding="utf-8"))
    frozen = json.load(open(FROZEN_ROWS, encoding="utf-8"))
    kept = {}
    for r in lit["rows"]:
        if r["kept_l5"]:
            kept.setdefault(r["subtype"], []).append(r["gene"])

    aug = []
    for r in frozen:
        r2 = json.loads(json.dumps(r))            # deep copy; every field preserved
        add = [g for g in kept.get(r["subtype"], []) if g not in (r.get("_markers_all") or [])]
        r2["_frozen_markers_all"] = list(r.get("_markers_all") or [])
        r2["_added_by_subtype2m"] = add
        r2["_markers_all"] = list(r.get("_markers_all") or []) + add
        aug.append(r2)
    # every field other than the three marker fields must be identical to the frozen rows
    for a, b in zip(aug, frozen):
        for k in set(list(a) + list(b)):
            if k in ("_markers_all", "_frozen_markers_all", "_added_by_subtype2m"):
                continue
            assert a.get(k) == b.get(k), "field %s changed for %s" % (k, b.get("subtype"))
    aug_path = os.path.join(OUT, "SUBTYPE_OBSERVABILITY_rows_augmented.json")
    json.dump(aug, open(aug_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    added_total = sum(len(r["_added_by_subtype2m"]) for r in aug)
    print("augmented rows: %d rows, %d rows carry an addition, %d genes added in total"
          % (len(aug), sum(1 for r in aug if r["_added_by_subtype2m"]), added_total))

    ctl = run_ruler(FROZEN_ROWS, os.path.join(OUT, "ruler_control"),
                    os.path.join(WAVE, "logs", "m3_ruler_control.log"))
    aug_run = run_ruler(aug_path, os.path.join(OUT, "ruler_augmented"),
                        os.path.join(WAVE, "logs", "m3_ruler_augmented.log"))

    control_rows = json.load(open(ctl["result_json"], encoding="utf-8"))
    frozen_rows = json.load(open(FROZEN_SEP, encoding="utf-8"))
    same = []
    for a, b in zip(control_rows, frozen_rows):
        same.append(a["volume"] == b["volume"] and a["subtype"] == b["subtype"]
                    and a["result"] == b["result"])
    control_identical = (len(control_rows) == len(frozen_rows) and all(same))

    doc = {"probe": "m3_remeasure.py",
           "ruler": RULER, "ruler_sha256": sha(RULER),
           "frozen_rows_sha256": sha(FROZEN_ROWS), "frozen_sep_sha256": sha(FROZEN_SEP),
           "augmented_rows": aug_path, "augmented_rows_sha256": sha(aug_path),
           "genes_added_total": added_total,
           "added_per_subtype": {s: g for s, g in sorted(kept.items())},
           "control": ctl, "augmented": aug_run,
           "control_reproduces_frozen": control_identical,
           "control_row_mismatches": [{"i": i, "control": control_rows[i]["result"],
                                       "frozen": frozen_rows[i]["result"]}
                                      for i, ok in enumerate(same) if not ok][:10]}
    json.dump(doc, open(os.path.join(OUT, "RULER_RUNS.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("control rc=%d  reproduces frozen result: %s" % (ctl["rc"], control_identical))
    print("control tail:", ctl["tail"])
    print("augmented rc=%d" % aug_run["rc"], "tail:", aug_run["tail"])
    return 0 if (ctl["rc"] == 0 and aug_run["rc"] == 0 and control_identical) else 1


if __name__ == "__main__":
    sys.exit(main())