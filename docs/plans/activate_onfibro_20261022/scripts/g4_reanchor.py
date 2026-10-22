#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g4_reanchor -- re-anchor the G4 three byte anchors for the activated default route, with the
reason recorded, the pre-image kept, and a causal control that separates the activation from
environment drift.

Why this is needed (measured, not assumed): with the carrier on the default route, `tests/verify_pipeline.py`
reports 2/3 mismatch -- `decisions_template.csv` and the normalized `annotation_evidence_report.md`
moved, `stage_a/processed.h5ad` did not. G4 is a frozen identity anchor of the shipped default, so the
task's rule applies: re-anchor with the reason recorded and the pre-image kept, and do not weaken a
criterion to make a gate pass.

What this script does
  1. keeps the pre-flip expectation as tests/G4_EXPECTED_PRE-ONFIBRO.json (bytes untouched otherwise);
  2. runs the pipeline 3x with the activation in place and requires the three anchors to be
     IDENTICAL across the three runs (determinism, the same discipline the X4B-FIX re-anchor used);
  3. runs the pipeline once with EYEKB_ACT_ONFIBRO=0 and requires that run to reproduce the OLD
     anchors byte-for-byte -- the causal control: the movement is the activation, not the machine;
  4. writes the new tests/G4_EXPECTED.json with the updated anchors and a provenance block recording
     the reason, the control reading and the pre-image path;
  5. re-runs tests/verify_pipeline.py so the gate itself reports the verdict (3/3 PASS expected).

Writes out/G4_REANCHOR.json.
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
OUT = os.path.join(WAVE, "out")
EXP = os.path.join(REPO, "tests", "G4_EXPECTED.json")
PRE = os.path.join(REPO, "tests", "G4_EXPECTED_PRE-ONFIBRO.json")
WORKROOT = os.path.join(OUT, "g4_reanchor")
AUDIT_DIR = os.path.join(HERE, "netaudit")
sys.path.insert(0, os.path.join(REPO, "tests"))
import verify_pipeline as V          # noqa: E402  (reuse its hash definitions, do not re-implement)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def clean_chatter(text, head=0, tail=4000):
    """Drop environment chatter (progress bars, loader notes, model-download lines) so the recorded
    readout is reproducible: measured 2026-10-22, the raw tail carried per-run throughput figures and
    made every artefact byte-differ after an identical re-run."""
    noise = ("it/s", "%|", "Batches:", "Loading weights", "Loading SentenceTransformer",
             "JAX version", "INFO ", "DB: ", "Batches")
    keep = [l for l in (text or "").splitlines() if not any(n in l for n in noise)]
    return "\n".join(keep)[-tail:]


def run_pipeline(tag, env_extra):
    work = os.path.join(WORKROOT, tag)
    os.makedirs(work, exist_ok=True)
    exp = json.load(open(EXP))
    py, src, pyver, equiv = V.resolve_python()
    assert py is not None, "no interpreter resolved for the pipeline"
    cmd = [py, os.path.join(REPO, "pipeline", "run_pipeline.py"), "--out", work,
           "--seed", str(exp["seed"]), "--input", os.path.join(REPO, exp["fixture"]),
           "--species", "human", "--tissue", "fibrovascular_membrane"]
    env = dict(os.environ)
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    # pinned PYTHONPATH: only the audit hook's directory, so the worker sandbox's foreign
    # site-packages cannot shadow the contract interpreter's own numpy/pydantic
    env["PYTHONPATH"] = AUDIT_DIR
    env.update(env_extra)
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=REPO)
    anchors = {}
    for name, fn in (("stage_a/processed.h5ad", V.raw_sha),
                     ("decisions_template.csv", V.raw_sha),
                     ("annotation_evidence_report.md__normalized", V.norm_report_sha)):
        p = os.path.join(work, "annotation_evidence_report.md" if "report" in name else name)
        anchors[name] = fn(__import__("pathlib").Path(p)) if os.path.exists(p) else None
    return {"tag": tag, "rc": r.returncode, "interpreter": py, "python": pyver, "work": work,
            "anchors": anchors, "stderr_tail": clean_chatter(r.stderr, tail=600)}


def main():
    os.makedirs(WORKROOT, exist_ok=True)
    cur_exp = json.load(open(EXP))                       # the expectation as it stands now
    pre_exists = os.path.exists(PRE)
    old_anchors = dict((json.load(open(PRE)) if pre_exists else cur_exp)["anchors"])
    mode = "verify" if (pre_exists and cur_exp["anchors"] != old_anchors) else "re-anchor"
    doc = {"probe": "g4_reanchor.py", "mode": mode,
           "expectation": "tests/G4_EXPECTED.json",
           "pre_image": "tests/G4_EXPECTED_PRE-ONFIBRO.json",
           "pre_image_present": pre_exists,
           "old_anchors": old_anchors, "current_anchors": cur_exp["anchors"],
           "fixture_sha256": cur_exp["fixture_sha256"]}

    # 1. pre-image (kept; the old expectation is never edited in place)
    if not pre_exists:
        shutil.copy2(EXP, PRE)
    doc["pre_image_sha256"] = sha(PRE)
    doc["pre_image_holds_the_pre_flip_anchors"] = (json.load(open(PRE))["anchors"] == old_anchors)

    # 2. three runs with the activation in place
    runs_on = [run_pipeline("on_run%d" % i, {}) for i in (1, 2, 3)]
    doc["runs_on"] = runs_on
    stable = all(r["anchors"] == runs_on[0]["anchors"] for r in runs_on)
    doc["three_run_determinism"] = stable
    doc["activated_anchors"] = runs_on[0]["anchors"]

    # 3. causal control: the OFF state must reproduce the PRE-FLIP anchors
    run_off = run_pipeline("off_run1", {"EYEKB_ACT_ONFIBRO": "0"})
    doc["run_off"] = run_off
    doc["off_state_reproduces_pre_flip_anchors"] = (run_off["anchors"] == old_anchors)
    doc["activated_differs_from_pre_flip"] = (runs_on[0]["anchors"] != old_anchors)
    doc["anchors_that_moved"] = sorted(k for k in old_anchors
                                       if runs_on[0]["anchors"][k] != old_anchors[k])

    # 4. write the new expectation (re-anchor mode only)
    if mode == "re-anchor":
        new_exp = dict(cur_exp)
        new_exp["anchors"] = runs_on[0]["anchors"]
        new_exp["anchor_provenance"] = (
            cur_exp.get("anchor_provenance", "") +
            " || RE-ANCHORED 2026-10-22 (activation card t_42df17c2, PI-signed activation of "
            "`onfibro_v13` on the default route): because the shipped default route changed on "
            "purpose, two of the three anchors moved -- %s -- while stage_a/processed.h5ad did not. "
            "Measured: three consecutive runs with the activation in place produced identical "
            "anchors (three_run_determinism=%s), and a run with EYEKB_ACT_ONFIBRO=0 reproduced the "
            "PREVIOUS anchors byte-for-byte (%s), so the movement is the activation and not the "
            "machine. The pre-flip expectation is kept as tests/G4_EXPECTED_PRE-ONFIBRO.json "
            "(sha256 %s). The criterion is unchanged -- the same three anchors, byte-for-byte, under "
            "the same pinned contract interpreter; only the values they must equal were re-taken "
            "from the shipped default, which is what a frozen identity anchor means. Evidence: "
            "docs/plans/activate_onfibro_20261022/out/G4_REANCHOR.json."
            % (", ".join("%s (%s -> %s)" % (k, old_anchors[k][:12], runs_on[0]["anchors"][k][:12])
                         for k in doc["anchors_that_moved"]),
               doc["three_run_determinism"], doc["off_state_reproduces_pre_flip_anchors"],
               doc["pre_image_sha256"]))
        tmp = EXP + ".tmp-activate"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(new_exp, f, ensure_ascii=False, indent=1)
        os.replace(tmp, EXP)
    else:
        prov = cur_exp.get("anchor_provenance", "")
        doc["provenance_records_the_re_anchor"] = ("RE-ANCHORED 2026-10-22" in prov
                                                   and "G4_EXPECTED_PRE-ONFIBRO.json" in prov)
        # in verify mode the expectation must already carry exactly the activated anchors
        doc["expectation_carries_the_activated_anchors"] = (cur_exp["anchors"] == runs_on[0]["anchors"])
    doc["new_expectation_sha256"] = sha(EXP)

    # 5. the gate itself reports the verdict
    genv = dict(os.environ)
    genv["PYTHONPATH"] = AUDIT_DIR
    g = subprocess.run(["/usr/bin/python3", "tests/verify_pipeline.py"], cwd=REPO,
                       capture_output=True, text=True, env=genv)
    doc["verify_pipeline_rc"] = g.returncode
    doc["verify_pipeline_tail"] = g.stdout[-900:]
    common = (doc["pre_image_holds_the_pre_flip_anchors"] and stable and g.returncode == 0)
    if mode == "re-anchor":
        ok = (common and doc["off_state_reproduces_pre_flip_anchors"]
              and doc["activated_differs_from_pre_flip"])
    else:
        ok = (common and doc["off_state_reproduces_pre_flip_anchors"]
              and doc["activated_differs_from_pre_flip"]
              and doc["provenance_records_the_re_anchor"]
              and doc["expectation_carries_the_activated_anchors"])
    doc["verdict"] = "PASS" if ok else "FAIL"
    json.dump(doc, open(os.path.join(OUT, "G4_REANCHOR.json"), "w"), ensure_ascii=False, indent=1)
    print("mode:", mode, "| anchors that moved:", doc["anchors_that_moved"])
    print("three-run determinism:", stable, "| OFF reproduces pre-flip anchors:",
          doc["off_state_reproduces_pre_flip_anchors"], "| activated differs:",
          doc["activated_differs_from_pre_flip"])
    print("verify_pipeline rc:", g.returncode)
    print(g.stdout[-300:])
    print("g4_reanchor verdict:", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())