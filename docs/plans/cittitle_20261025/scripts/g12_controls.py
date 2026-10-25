#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g12_controls.py — reverse-control battery for G12 (card t_d8e7f2d4).

House rule (G11 precedent, docs/VERIFY_CONTRACT.md §5.6): a gate that has only ever been seen green is
unproven. This script plants each violation shape **on the real tree**, runs the gate, records the rc
and which check named the defect, then restores the file byte-for-byte and verifies the sha came back.

Cases:
  CLEAN             nothing planted                                rc=0
  SOURCE-REGRESSION the builder's retrieval route gets the pre-fix `[:120]` literal back
                                                                   rc=2, G12-C01
  TITLE-DRIFT       one citation's `title_full` is mutated         rc=2, G12-C03
  ANCHOR-BREAK      one citation's pre-existing `journal` is mutated (so the anchor twin no longer
                    inverts to the pre-image)                      rc=2, G12-C05
  COVERAGE-DROP     the last line is dropped from the anchor twin  rc=2, G12-C04
  CORPUS-ABSENT     the corpus is pointed at a missing path        rc=3 (INCONCLUSIVE, not a verdict)

Every case asserts the *expected* check id appears among the failing ones, so a gate that fails for an
unrelated reason does not count as a control passing. Restoration is verified by sha256; a case whose
file does not come back byte-identical makes the whole battery FAIL.

Writes only out/G12_CONTROLS.json and logs/g12_controls.log. Reads/writes nothing else on the tree
except the two files it plants into and restores.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path("/home/ubuntu/EYEKB_REPO")
DELIV = HERE.parent
OUT = DELIV / "out"
LOGS = DELIV / "logs"

BUILDER = ROOT / "kb" / "link_registry" / "scripts" / "build_link_registry.py"
ANCHOR = OUT / "LINK_REGISTRY_v2_cittitle.jsonl"
DROPIN = OUT / "LINK_REGISTRY_v2_cittitle_dropin.jsonl"
GATE = ROOT / "tests" / "gate_cittitle_meta.py"

PREFIX_LITERAL = '"title": (hit.get("title") or "")[:120],'   # trailing comma kept: the
# planted regression must stay syntactically valid, otherwise the builder cannot be imported and the
# case is confounded with a broken build rather than isolated to G12-C01
FIXED_TITLE_LINE = '"title": citation_field(cmeta, pmid, "title", hit.get("title")),'
PLANTED = "MUTATED-PLANTED"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_gate(env_extra=None):
    import os
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run([sys.executable, str(GATE), "--json", "/tmp/g12_control_run.json"],
                       capture_output=True, text=True, cwd=str(ROOT), env=env)
    try:
        data = json.loads(Path("/tmp/g12_control_run.json").read_text(encoding="utf-8"))
        failing = [c["id"] for c in data["checks"] if c["verdict"] != "PASS"]
        finals = {c["id"]: c["verdict"] for c in data["checks"]}
    except Exception:                                                   # noqa: BLE001
        failing, finals = [], {}
    return r.returncode, failing, finals


def main() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    snapshot_dir = DELIV / ".battery_snapshot"
    snapshot_dir.mkdir(exist_ok=True)
    before = {}
    for p in (BUILDER, ANCHOR, DROPIN):
        shutil.copy2(p, snapshot_dir / p.name)
        before[p] = sha(p)

    cases = []

    def record(name, rc, failing, expect_rc, expect_check, note):
        ok = (rc == expect_rc) and (expect_check is None or expect_check in failing)
        cases.append({"case": name, "rc": rc, "expected_rc": expect_rc,
                      "expected_check": expect_check, "failing": failing,
                      "verdict": "PASS" if ok else "FAIL", "note": note})
        print(f"  [{('PASS' if ok else 'FAIL')}] {name:<18} rc={rc} (want {expect_rc}) "
              f"failing={failing} {note}")
        return ok

    def restore(p: Path):
        shutil.copy2(snapshot_dir / p.name, p)
        got = sha(p)
        if got != before[p]:
            raise SystemExit(f"RESTORE FAILED for {p}: {got} != {before[p]}")
        return got

    # ---------------------------------------------------------------- CLEAN
    rc, failing, _ = run_gate()
    record("CLEAN", rc, failing, 0, None, "unmodified tree")

    # ---------------------------------------------------------------- SOURCE-REGRESSION
    src = BUILDER.read_text(encoding="utf-8")
    if src.count(FIXED_TITLE_LINE) != 1:
        raise SystemExit("the fix's retrieval-route line was not found exactly once; battery aborted")
    BUILDER.write_text(src.replace(FIXED_TITLE_LINE, PREFIX_LITERAL), encoding="utf-8")
    rc, failing, _ = run_gate()
    record("SOURCE-REGRESSION", rc, failing, 2, "G12-C01",
           "pre-fix [:120] literal planted back into the builder")
    restore(BUILDER)

    # ---------------------------------------------------------------- TITLE-DRIFT
    lines = ANCHOR.read_text(encoding="utf-8").split("\n")
    row = json.loads(lines[0])
    row["citations"][0]["title_full"] = PLANTED
    lines[0] = json.dumps(row, ensure_ascii=False)
    ANCHOR.write_text("\n".join(lines), encoding="utf-8")
    rc, failing, _ = run_gate()
    record("TITLE-DRIFT", rc, failing, 2, "G12-C03",
           "one citation's title_full mutated: C03 names the drift; C05 and C06 also report the resulting incoherence (the drop-in derives from the twin, the builder reader is the reference the twin was filled from), which is correct consequential detection")
    restore(ANCHOR)

    # ---------------------------------------------------------------- ANCHOR-BREAK
    lines = ANCHOR.read_text(encoding="utf-8").split("\n")
    row = json.loads(lines[0])
    row["citations"][0]["journal"] = PLANTED
    lines[0] = json.dumps(row, ensure_ascii=False)
    ANCHOR.write_text("\n".join(lines), encoding="utf-8")
    rc, failing, _ = run_gate()
    record("ANCHOR-BREAK", rc, failing, 2, "G12-C05",
           "a pre-existing citation key mutated, so the twin no longer inverts to the pre-image")
    restore(ANCHOR)

    # ---------------------------------------------------------------- COVERAGE-DROP
    lines = [ln for ln in ANCHOR.read_text(encoding="utf-8").split("\n") if ln.strip()]
    ANCHOR.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    rc, failing, _ = run_gate()
    record("COVERAGE-DROP", rc, failing, 2, "G12-C04", "last row dropped from the anchor twin")
    restore(ANCHOR)

    # ---------------------------------------------------------------- CORPUS-ABSENT
    rc, failing, _ = run_gate({"EYEKB_G12_CORPUS": "/nonexistent/papers.jsonl"})
    record("CORPUS-ABSENT", rc, failing, 3, "G12-C03",
           "corpus pointed at a missing path: INCONCLUSIVE, not a verdict about the repository")

    # ---------------------------------------------------------------- restore check
    restored = {str(p.relative_to(ROOT)): (sha(p) == before[p]) for p in before}
    all_back = all(restored.values())
    for p in snapshot_dir.iterdir():
        p.unlink()
    snapshot_dir.rmdir()

    summary = {
        "gate": "G12", "script": "tests/gate_cittitle_meta.py",
        "planted_on_the_real_tree_then_restored": True,
        "pre_shas": {str(p.relative_to(ROOT)): v for p, v in before.items()},
        "restored_byte_identical": restored,
        "cases": cases,
        "verdict": "PASS" if (all_back and all(c["verdict"] == "PASS" for c in cases)) else "FAIL",
    }
    (OUT / "G12_CONTROLS.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                           encoding="utf-8")
    (LOGS / "g12_controls.log").write_text(
        "\n".join(f"{c['case']:<18} rc={c['rc']} want={c['expected_rc']} "
                  f"check={c['expected_check']} -> {c['verdict']}" for c in cases)
        + f"\nrestored byte-identical: {restored}\n", encoding="utf-8")
    print(f"\nG12 controls: {summary['verdict']}  (restored byte-identical: {all_back})")
    return 0 if summary["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())