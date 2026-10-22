#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G10 -- switch coverage and arm hygiene for before/after measurements of the recorded set.

Why this gate exists
--------------------
On 2026-10-22 a before/after measurement of the recorded set (28 volumes, 721 clusters, 1,495,330
cells) reported `changed = 0`: the carrier flip looked inert. It was not inert. The frozen harness
`docs/plans/noregr_20261022/scripts/wave_common.py` clears a HARD-CODED tuple of switch names before
each arm, and `EYEKB_ACT_ONFIBRO` was added to the router after that tuple was written. The before
arm set `EYEKB_ACT_ONFIBRO=0`; the after arm, written as the natural `{}` meaning "the tree as
shipped", inherited it, so both arms were the same state and the comparison compared the tree with
itself. The failure mode is silent: a null that is really an artefact of the instrument.

What it enforces
----------------
R1  registry in sync -- docs/SWITCH_COVERAGE_REGISTRY.tsv must equal what the source says today
    (regenerate with scripts/switch_coverage/gen_switch_registry.py). Catches a switch
    added by a later card that nobody classified.
R2  arm hygiene -- for every before/after report on disk, no switch may be set in one arm and not
    the other unless the frozen harness clears it in between. This is the exact rule that the
    2026-10-22 defect broke, and it is a property of the arm pair, not of any single spec.

Both rules are checked against the real tree, and the gate refuses to pass on a scanner that flags
nothing: `--self-test` plants an arm pair that must be caught and a pair that must be accepted, and
requires the R1 check to reject a registry that has drifted by one character.

Nothing here writes outside its --json path; zero network; standard library only.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
AH_DIR = os.path.join(REPO, "scripts", "switch_coverage")
sys.path.insert(0, AH_DIR)
import arm_hygiene as A          # noqa: E402
import gen_switch_registry as G  # noqa: E402

REGISTRY = os.path.join(REPO, "docs", "SWITCH_COVERAGE_REGISTRY.tsv")
SCAN_ROOT = os.path.join(REPO, "docs", "plans")


def registry_text():
    return "\n".join(G.HEADER + G.rows()) + "\n"


def check_r1():
    """The registry on disk must equal the source-derived rows."""
    res = {"rule": "R1 registry in sync with the source", "registry": REGISTRY, "ok": True,
           "detail": "", "switches_in_source": len(A.discover())}
    if not os.path.isfile(REGISTRY):
        res.update(ok=False, detail="registry missing")
        return res
    with open(REGISTRY, encoding="utf-8") as fh:
        on_disk = fh.read()
    want = registry_text()
    if on_disk != want:
        disk_lines = on_disk.splitlines()
        want_lines = want.splitlines()
        diff = []
        for i in range(max(len(disk_lines), len(want_lines))):
            d = disk_lines[i] if i < len(disk_lines) else "<absent>"
            w = want_lines[i] if i < len(want_lines) else "<absent>"
            if d != w:
                diff.append({"line": i + 1, "on_disk": d[:160], "expected": w[:160]})
        res.update(ok=False, detail="registry drifted from the source; regenerate it",
                   drift=diff[:10], n_drift_lines=len(diff))
    return res


def arms_of(path):
    """(name, before env keys, after env keys) for a before/after report, else None."""
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or "before_arm" not in doc or "after_arm" not in doc:
        return None
    b = (doc.get("before_arm") or {}).get("env") or {}
    a = (doc.get("after_arm") or {}).get("env") or {}
    return doc.get("name") or os.path.relpath(path, REPO), sorted(b), sorted(a)


def check_r2(root=SCAN_ROOT):
    """No switch may be set in one arm and not the other unless the harness clears it."""
    res = {"rule": "R2 arm hygiene (no switch set in one arm only, unless the harness clears it)",
           "scanned": 0, "violations": [], "ok": True}
    for path in sorted(glob.glob(os.path.join(root, "**", "*.json"), recursive=True)):
        got = arms_of(path)
        if not got:
            continue
        name, b, a = got
        res["scanned"] += 1
        bad = A.contaminating(b, a)
        if bad:
            res["violations"].append({"report": os.path.relpath(path, REPO), "name": name,
                                      "before_env": b, "after_env": a,
                                      "leaking_switches": bad})
    if res["violations"]:
        res.update(ok=False, detail="%d report(s) compare arms that the frozen harness does not "
                                    "separate on at least one switch" % len(res["violations"]))
    return res


def self_test():
    """R2 must catch a planted leak and accept a clean pair; R1 must reject a drifted registry."""
    out = {"rule": "self-test on synthetic inputs", "ok": True, "cases": []}

    def case(label, fn, want_ok):
        try:
            got = fn()
            ok = got.get("ok", False)
            detail = got.get("detail", "")
        except Exception as exc:                     # noqa: BLE001
            ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
        good = (ok == want_ok)
        out["cases"].append({"case": label, "expected_ok": want_ok, "got_ok": ok,
                             "pass": good, "detail": detail})
        if not good:
            out["ok"] = False

    def planted_leak():
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "REPORT.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump({"name": "planted leak", "before_arm": {"env": {"EYEKB_ACT_ONFIBRO": "0"}},
                           "after_arm": {"env": {}}}, fh)
            return check_r2(tmp)

    def clean_pair():
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "REPORT.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump({"name": "clean pair",
                           "before_arm": {"env": {"EYEKB_ACT_ONFIBRO": "0"}},
                           "after_arm": {"env": {"EYEKB_ACT_ONFIBRO": "1"}}}, fh)
            return check_r2(tmp)

    def harness_cleared_pair():
        """EYEKB_TISSUE_SCOPE set in one arm only is SAFE: the frozen harness clears it."""
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "REPORT.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump({"name": "harness-cleared single-arm setting",
                           "before_arm": {"env": {"EYEKB_TISSUE_SCOPE": "0"}},
                           "after_arm": {"env": {}}}, fh)
            return check_r2(tmp)

    def drifted_registry():
        global REGISTRY
        keep = REGISTRY
        try:
            with tempfile.TemporaryDirectory() as tmp:
                p = os.path.join(tmp, "SWITCH_COVERAGE_REGISTRY.tsv")
                with open(REGISTRY, encoding="utf-8") as fh:
                    body = fh.read()
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(body.replace("EYEKB_TISSUE_SCOPE", "EYEKB_TISSUE_SCOPEX"))
                REGISTRY = p
                return check_r1()
        finally:
            REGISTRY = keep

    case("planted one-arm switch (must be caught)", planted_leak, False)
    case("both arms name the switch (must be accepted)", clean_pair, True)
    case("harness-cleared switch set in one arm (must be accepted)", harness_cleared_pair, True)
    case("registry drifted by one name (must be caught)", drifted_registry, False)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    report = {"gate": "G10 switch coverage and arm hygiene",
              "repo": REPO,
              "harness_switches": list(A.harness_switches()),
              "must_be_set_in_every_arm": list(A.required_explicit())}
    st = self_test()
    report["self_test"] = st
    report["R1"] = check_r1()
    report["R2"] = check_r2()
    report["ok"] = bool(st["ok"] and report["R1"]["ok"] and report["R2"]["ok"])

    print("G10 switch coverage and arm hygiene")
    print("  harness clears: %s" % ", ".join(report["harness_switches"]))
    print("  an arm setting any of these must set it in every arm: %s"
          % ", ".join(report["must_be_set_in_every_arm"]))
    for c in st["cases"]:
        print("  self-test %-58s %s" % (c["case"], "pass" if c["pass"] else "FAIL"))
    print("  R1 %s -- %s" % ("pass" if report["R1"]["ok"] else "FAIL",
                             report["R1"]["detail"] or "registry matches the source"))
    print("  R2 %s -- scanned %d report(s); %d violation(s)"
          % ("pass" if report["R2"]["ok"] else "FAIL", report["R2"]["scanned"],
             len(report["R2"]["violations"])))
    for v in report["R2"]["violations"]:
        print("     %s  leaking=%s" % (v["report"], v["leaking_switches"]))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
        print("  wrote %s" % args.json)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())