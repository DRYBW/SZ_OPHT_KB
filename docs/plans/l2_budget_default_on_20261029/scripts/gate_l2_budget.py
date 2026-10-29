#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Criteria C1, C2, C3 and C6 of plans/l2_budget_default_on_20261029 (as amended by
AMENDMENT_2: the width follows the judged path, not the whole pipeline).

Run from the repository root:
  python3 docs/plans/l2_budget_default_on_20261029/scripts/gate_l2_budget.py
Exit 0 only when every criterion holds.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))
sys.path.insert(0, os.path.join(REPO, "pipeline"))

fails = []


def check(name, got, want):
    ok = got == want
    print("  %s  %-52s got=%r want=%r" % ("PASS" if ok else "FAIL", name, got, want))
    if not ok:
        fails.append(name)


def module(env_value):
    """Fresh import so the once-per-process warning state resets."""
    sys.modules.pop("l2_budget", None)
    if env_value is None:
        os.environ.pop("EYEKB_L2_BUDGET", None)
    else:
        os.environ["EYEKB_L2_BUDGET"] = env_value
    import l2_budget
    return l2_budget


print("== C1 the width follows the caller ==")
cases = [
    (None, False, 10, "unset, plain path  -> shipped default unchanged"),
    (None, True, 30, "unset, judged path -> 30 (this card)"),
    ("1", False, 30, "env ON, plain path -> 30"),
    ("true", True, 30, "env ON, judged path -> 30"),
    ("0", True, 10, "env OFF beats the judged path -> 10 (rollback)"),
    ("off", False, 10, "env OFF, plain path -> 10"),
    ("", False, 10, "empty value -> 10"),
]
for token, judge, want, label in cases:
    check(label, module(token).resolve(None, judge=judge), want)

print("== C2 an explicit value is never rewritten ==")
for token, judge in [(None, True), (None, False), ("0", True), ("1", False)]:
    check("resolve(12, judge=%s) with env=%r" % (judge, token),
          module(token).resolve(12, judge=judge), 12)

print("== C3 unknown token: fail-closed to legacy, one warning ==")
check("unknown token -> 10 (judged path too)", module("banana").resolve(None, judge=True), 10)
out = subprocess.run(
    [sys.executable, "-c",
     "import os,sys; sys.path.insert(0,%r); os.environ['EYEKB_L2_BUDGET']='banana';\n"
     "import l2_budget as L; print(L.resolve(None, judge=True)); print(L.resolve(7, judge=True))"
     % os.path.join(REPO, "pipeline")],
    capture_output=True, text=True)
check("unknown token -> warnings per process", out.stderr.count("WARNING"), 1)
check("unknown token -> explicit still honoured", out.stdout.split()[1], "7")

print("== C6 change surface ==")
diff = subprocess.run(["git", "-C", REPO, "diff", "--name-only", "HEAD"],
                      capture_output=True, text=True)
prod = sorted(p for p in diff.stdout.split() if not p.startswith("docs/"))
check("production files changed", prod,
      ["pipeline/l2_budget.py", "pipeline/run_pipeline.py", "pipeline/stage_b_evidence.py"])

print()
if fails:
    print("FAILURES: %d -> %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("ALL PASS: C1 / C2 / C3 / C6 hold.")