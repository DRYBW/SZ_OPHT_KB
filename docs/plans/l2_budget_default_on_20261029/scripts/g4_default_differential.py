#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G4 differential for the 30-gene default (criterion C8 of this card).

Answers one question with measurements, not reasoning: when the query budget default moves
from 10 to 30, what happens to the frozen G4 identity anchors, and does turning the door off
bring them back?

States measured on the G4 fixture (`tests/G4_EXPECTED.json` -> fixture + seed, the same probe
the re-anchor cards used):
  pre       old `pipeline/l2_budget.py` (from HEAD), variable unset       -> budget 10
  rollback  new module, EYEKB_L2_BUDGET=0                               -> budget 10
  post      new module, variable unset, twice                            -> budget 30

Readings: `pre` vs `rollback` must be byte-identical (the rollback is real), `post` must be
deterministic across its two runs, and `post` vs `pre` shows which anchors the change moves.
This card does NOT write `tests/G4_EXPECTED.json`. G4 already reported 2/3 before this change,
so re-anchoring here would fold an unexplained pre-existing drift into this card; the numbers
are recorded for whoever resolves that.

Usage: python3 docs/plans/l2_budget_default_on_20261029/scripts/g4_default_differential.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(CARD, "..", "..", ".."))
OUT = os.path.join(CARD, "out")
WORKROOT = os.path.join(OUT, "g4_differential")
MODULE = os.path.join(REPO, "pipeline", "l2_budget.py")
TOUCHED = ["pipeline/l2_budget.py", "pipeline/stage_b_evidence.py", "pipeline/run_pipeline.py"]
KEEP = os.path.join(WORKROOT, "module_new.py")

sys.path.insert(0, os.path.join(REPO, "tests"))
import verify_pipeline as V          # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def clean(text, tail=400):
    noise = ("it/s", "%|", "Batches:", "Loading weights", "Loading SentenceTransformer",
             "JAX version", "INFO ", "DB: ")
    keep = [l for l in (text or "").splitlines() if not any(n in l for n in noise)]
    return "\n".join(keep)[-tail:]


def run(tag, env_extra):
    work = os.path.join(WORKROOT, tag)
    os.makedirs(work, exist_ok=True)
    exp = json.load(open(os.path.join(REPO, "tests", "G4_EXPECTED.json")))
    py, src, pyver, equiv = V.resolve_python()
    cmd = [py, os.path.join(REPO, "pipeline", "run_pipeline.py"), "--out", work,
           "--seed", str(exp["seed"]), "--input", os.path.join(REPO, exp["fixture"]),
           "--species", "human", "--tissue", "fibrovascular_membrane"]
    env = dict(os.environ)
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.pop("EYEKB_L2_BUDGET", None)
    env.update(env_extra)
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=REPO)
    anchors = {}
    for name, fn in (("stage_a/processed.h5ad", V.raw_sha),
                     ("decisions_template.csv", V.raw_sha),
                     ("annotation_evidence_report.md__normalized", V.norm_report_sha)):
        p = os.path.join(work, "annotation_evidence_report.md" if "report" in name else name)
        anchors[name] = fn(__import__("pathlib").Path(p)) if os.path.exists(p) else None
    return {"tag": tag, "rc": r.returncode, "interpreter": [py, src, pyver],
            "env": env_extra, "anchors": anchors, "stderr_tail": clean(r.stderr)}


def main():
    os.makedirs(WORKROOT, exist_ok=True)
    exp = json.load(open(os.path.join(REPO, "tests", "G4_EXPECTED.json")))
    new_module = open(MODULE, "rb").read()
    new_images = {rel: open(os.path.join(REPO, rel), "rb").read() for rel in TOUCHED}
    open(KEEP, "wb").write(new_module)
    doc = {"probe": "g4_default_differential.py",
           "card": "docs/plans/l2_budget_default_on_20261029",
           "frozen_expectation": exp["anchors"],
           "frozen_expectation_sha256": sha(os.path.join(REPO, "tests", "G4_EXPECTED.json")),
           "module_new_sha256": hashlib.sha256(new_module).hexdigest()}
    # The pre-change state needs ALL the files this card touches, not just the module: the new
    # call sites pass a keyword the old module does not accept, so swapping one file produces a
    # TypeError rather than a measurement (learned the hard way on the first attempt).
    pre_images = {}
    try:
        for rel in TOUCHED:
            pre = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + rel],
                                 capture_output=True, check=True).stdout
            pre_images[rel] = pre
            open(os.path.join(REPO, rel), "wb").write(pre)
        doc["pre_sha256"] = {rel: hashlib.sha256(b).hexdigest() for rel, b in pre_images.items()}
        doc["pre"] = run("pre_run1", {})
    finally:
        for rel in TOUCHED:
            open(os.path.join(REPO, rel), "wb").write(new_images[rel])
        doc["restored_sha256"] = {rel: sha(os.path.join(REPO, rel)) for rel in TOUCHED}
    doc["module_restored_sha256"] = sha(MODULE)
    doc["rollback"] = run("rollback_run1", {"EYEKB_L2_BUDGET": "0"})
    doc["post"] = [run("post_run%d" % i, {}) for i in (1, 2)]

    pre_a = doc["pre"]["anchors"]
    doc["post_deterministic"] = (doc["post"][0]["anchors"] == doc["post"][1]["anchors"])
    doc["rollback_reproduces_pre"] = (doc["rollback"]["anchors"] == pre_a)
    doc["post_differs_from_pre"] = (doc["post"][0]["anchors"] != pre_a)
    doc["anchors_moved_by_this_change"] = sorted(
        k for k in pre_a if doc["post"][0]["anchors"][k] != pre_a[k])
    doc["post_matches_frozen_expectation"] = (doc["post"][0]["anchors"] == exp["anchors"])
    doc["pre_matches_frozen_expectation"] = (pre_a == exp["anchors"])
    with open(os.path.join(OUT, "G4_DIFFERENTIAL.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    print("pre anchors     :", {k: (v or "")[:12] for k, v in pre_a.items()})
    print("rollback anchors:", {k: (v or "")[:12] for k, v in doc["rollback"]["anchors"].items()})
    print("post anchors    :", {k: (v or "")[:12] for k, v in doc["post"][0]["anchors"].items()})
    print("frozen expects  :", {k: (v or "")[:12] for k, v in exp["anchors"].items()})
    print("rollback == pre          :", doc["rollback_reproduces_pre"])
    print("post deterministic       :", doc["post_deterministic"])
    print("anchors moved            :", doc["anchors_moved_by_this_change"])
    print("pre == frozen expectation:", doc["pre_matches_frozen_expectation"],
          "(G4's pre-existing red, not caused by this card)")
    ok = doc["rollback_reproduces_pre"] and doc["post_deterministic"]
    print("C8 VERDICT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()