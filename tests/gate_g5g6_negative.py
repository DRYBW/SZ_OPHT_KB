#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_g5g6_negative.py - G5/G6 negative battery (minimal mutation of the real artefacts -> assert
rejection with the expected check code)

Contract (negative-case discipline carried over from W3_NORM/R1 `tests/run_negative_tests.py`):
  · Positive control: an unmutated copy of the real artefacts must give rc=0 (otherwise the gate itself is untrustworthy);
  · Negative case: every class must give rc!=0 **and hit the expected check code** (a bare "overall FAIL" is not accepted);
  · Extra failures beyond the target code are recorded as unexpected_extra_failures - neither hidden nor
    treated as a failure of the case.

Mutations act only on **copies** under fixtures/: the real artefacts in the repo (ledger / gate inventory /
instance / human checklist / entry) stay byte-identical.

G5 cases: P0 positive control / N1 missing file (C04) / N2 digest drift (C05) / N3 unregistered load (C07) /
N4 expired certification (C08) / N5 stale dispensation (C06)
G6 cases: P0 positive control / N1 empty required cell (R1) / N2 anchorless evidence (R2) / N3 gains only (R5) /
         N4 no sha (R6) / N5 escape hatch without a switch (R7) / N6 default-ON change not registered as a gate
         precondition (R8) / N7 no threshold action (R2-CONCRETE) / N8 checklist-to-rule mapping gap (MAP)

Usage: python3 tests/gate_g5g6_negative.py [--out DIR] [--json OUT.json]
Exit codes: 0 = everything as expected; 1 = at least one case off expectation.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"


def sh(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(p: Path, txt: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")
    return p


def mutate(src: Path, dst: Path, old: str, new: str) -> Path:
    t = sh(src)
    n = t.count(old)
    assert n == 1, f"mutation target not unique in {src.name}: {n} matches for {old[:40]!r}"
    return write(dst, t.replace(old, new))


def run_gate(script: Path, args: list, cwd: Path = ROOT) -> tuple:
    """Return (rc, failing_codes, stdout_tail)."""
    cmd = [sys.executable, str(script)] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    codes = []
    for a in args:
        if a.startswith("--json="):
            jp = Path(a.split("=", 1)[1])
            if jp.exists():
                try:
                    codes = [c["code"] for c in json.loads(jp.read_text(encoding="utf-8"))["checks"]
                             if c["status"] == "FAIL"]
                except Exception:                                  # noqa: BLE001
                    codes = ["<json-unreadable>"]
    return r.returncode, codes, (r.stdout + r.stderr)[-600:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(FIX))
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    fixtures = Path(a.out)

    reg = ROOT / "docs" / "W3_PIPELINE_REGISTRY.tsv"
    inv = ROOT / "docs" / "GATE_INVENTORY_G5G6.tsv"
    led = ROOT / "tests" / "fixtures" / "g5" / "snapshot_drift_ledger.tsv"
    ent = ROOT / "tests" / "run_gates.sh"
    inst = ROOT / "docs" / "CHANGE_CONTROL_G6_INSTANCE.tsv"
    tmpl = ROOT / "docs" / "CHANGE_CONTROL_G6_TEMPLATE.tsv"
    chk = ROOT / "docs" / "W3_CHANGE_CONTROL_CHECKLIST.md"
    g5 = ROOT / "tests" / "gate_registry.py"
    g6 = ROOT / "tests" / "gate_change_control.py"
    missing = [str(p) for p in (reg, inv, led, ent, inst, tmpl, chk, g5, g6) if not p.exists()]
    if missing:
        print(json.dumps({"verdict": "FAIL", "error": f"inputs missing: {missing}"}, ensure_ascii=False))
        return 1

    g5m = fixtures / "g5" / "mutants"
    g6m = fixtures / "g6" / "mutants"
    tmp = fixtures / "_tmp"
    for d in (g5m, g6m, tmp):
        d.mkdir(parents=True, exist_ok=True)

    # ---------- copies of the real artefacts (positive control + negative-case mothers) ----------
    reg0 = write(g5m / "registry_copy.tsv", sh(reg))
    inv0 = write(g5m / "gate_inventory_copy.tsv", sh(inv))
    led0 = write(g5m / "snapshot_drift_ledger_copy.tsv", sh(led))
    ent0 = write(g5m / "run_gates_copy.sh", sh(ent))
    inst0 = write(g6m / "instance_copy.tsv", sh(inst))
    tmpl0 = write(g6m / "template_copy.tsv", sh(tmpl))
    chk0 = write(g6m / "checklist_copy.md", sh(chk))

    def jout(tag: str) -> str:
        return f"--json={tmp / (tag + '.json')}"

    cases = []

    def add(gate: str, cid: str, mutation: str, expected: list, rc: int, codes: list, tail: str) -> None:
        ok = (rc == 0 and not codes) if not expected else (rc != 0 and any(c in codes for c in expected))
        extra = [c for c in codes if c not in expected]
        cases.append({"gate": gate, "id": cid, "mutation": mutation,
                      "expected_codes": expected or ["<none: positive control>"],
                      "rc": rc, "failing_codes": codes, "unexpected_extra_failures": extra,
                      "verdict": "PASS(as expected)" if ok else "FAIL(off expectation)", "ok": ok,
                      "stdout_tail": tail if not ok else ""})

    # G5 mutations are always located by row x column (never by whole-file replacement): parse the copy,
    # change one cell, write it back.
    def tsv_rows(txt: str) -> tuple:
        lines = [ln for ln in txt.splitlines() if ln and not ln.startswith("#")]
        hdr = lines[0].split("\t")
        return hdr, [ln.split("\t") for ln in lines[1:]]

    def tsv_write(path: Path, hdr: list, body: list) -> Path:
        return write(path, "\n".join(["\t".join(hdr)] + ["\t".join(r) for r in body]) + "\n")

    def cell_edit(txt: str, idcol: str, rid: str, col: str, value: str, path: Path) -> Path:
        hdr, body = tsv_rows(txt)
        ci, ri = hdr.index(col), hdr.index(idcol)
        hit = 0
        for r in body:
            if r[ri] == rid:
                r[ci] = value
                hit += 1
        assert hit == 1, f"cell_edit target not unique: {rid}.{col} -> {hit}"
        return tsv_write(path, hdr, body)

    # ================= G5 =================
    rc, codes, tail = run_gate(g5, ["--registry", str(reg0), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_p0")])
    add("G5", "P0_POSITIVE_CONTROL", "positive control: unmutated copy of the real artefacts", [], rc, codes, tail)

    regN1 = cell_edit(sh(reg0), "item_id", "L6-04", "path", "/tmp/NO_SUCH_GATE_FILE_G5.py",
                      g5m / "N1_missing_file_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN1), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n1")])
    add("G5", "N1_MISSING_FILE", "ledger L6-04 path -> non-existent path (missing file)", ["G5-C04"], rc, codes, tail)

    regN2 = cell_edit(sh(reg0), "item_id", "L6-04", "sha256", "0" * 64,
                      g5m / "N2_sha_drift_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN2), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n2")])
    add("G5", "N2_SHA_DRIFT", "ledger L6-04 sha256 -> all zeros (digest drift, not covered by the drift ledger)", ["G5-C05"], rc, codes, tail)

    entN3 = mutate(ent0, g5m / "N3_unregistered_entry.sh",
                   'run_gate "G6 gate_change_control (eight machine rules)" \\\n  python3 tests/gate_change_control.py',
                   'run_gate "G6 gate_change_control (eight machine rules)" \\\n  python3 tests/gate_change_control.py\nrun_gate "probe" \\\n  python3 tests/gate_unregistered_probe.py')
    rc, codes, tail = run_gate(g5, ["--registry", str(reg0), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(entN3), jout("g5_n3")])
    add("G5", "N3_UNREG_LOAD", "entry gains a line invoking an unregistered script (unregistered load)", ["G5-C07"], rc, codes, tail)

    regN4 = cell_edit(sh(reg0), "item_id", "L1-22", "notes",
                      "expiry clause: the declared expiry date (2026-10-01) requires a PI decision to flip or extend (original declaration 2026-10-19)",
                      g5m / "N4_expired_cert_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN4), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n4")])
    add("G5", "N4_CERT_EXPIRED", "ledger L1-22 declared expiry date 2026-10-19 -> 2026-10-01 (earlier than as_of)",
        ["G5-C08"], rc, codes, tail)

    regN6 = cell_edit(sh(reg0), "item_id", "L0-06", "change_gate", "TBD",
                      g5m / "N6_owner_placeholder_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN6), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n6")])
    add("G5", "N6_OWNER_PLACEHOLDER", "ledger L0-06 change_gate -> TBD (placeholder owner)", ["G5-C03"], rc, codes, tail)

    # N5: re-point a ledger entry at a row that is no longer drifted (live sha == registered sha), so the
    # dispensation has lost its reason to exist. C06 must flag a stale dispensation; C05 will additionally fail
    # because the originally drifted row loses its dispensation (recorded as an extra failure, as-is).
    led_rows = [ln.split("\t") for ln in sh(led0).splitlines() if ln and not ln.startswith("#")]
    lh, lrows = led_rows[0], led_rows[1:]
    rhdr, rbody = tsv_rows(sh(reg0))
    stable = next(r for r in rbody if r[rhdr.index("item_id")] == "L6-04")
    lrows2 = []
    for r in lrows:
        r = list(r)
        if r[lh.index("item_id")] == "L6-13":
            r[lh.index("item_id")] = "L6-04"                   # point at a row that is not drifted
            r[lh.index("registered_sha256")] = stable[rhdr.index("sha256")]
            r[lh.index("observed_sha256")] = stable[rhdr.index("sha256")]
            r[lh.index("cause")] = "TEST_STALE_DISPENSATION"
        lrows2.append(r)
    ledN5 = write(g5m / "N5_stale_ledger.tsv", "\n".join(["\t".join(lh)] + ["\t".join(r) for r in lrows2]) + "\n")
    rc, codes, tail = run_gate(g5, ["--registry", str(reg0), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(ledN5), "--entry", str(ent0), jout("g5_n5")])
    add("G5", "N5_LEDGER_STALE", "ledger entry re-pointed at a non-drifted row (stale dispensation, C06)",
        ["G5-C06"], rc, codes, tail)

    # N7: a repo-surface row registered with an ABSOLUTE path that exists on this machine.
    # The old gate would read it as fine (the file is there); the portability rule must reject it,
    # because the absolute prefix only resolves on the maintainer's machine.
    regN7 = cell_edit(sh(reg0), "item_id", "L6-04", "path",
                      str(ROOT / "tests" / "verify_repro.py"),
                      g5m / "N7_repo_row_absolute_path_registry.tsv")
    rc, codes, tail = run_gate(g5, ["--registry", str(regN7), "--gate-inventory", str(inv0),
                                    "--drift-ledger", str(led0), "--entry", str(ent0), jout("g5_n7")])
    add("G5", "N7_REPO_ROW_ABSOLUTE_PATH",
        "repo-surface row registered with an absolute path that does exist (portability rule, C04)",
        ["G5-C04"], rc, codes, tail)

    # ================= G6 =================
    rc, codes, tail = run_gate(g6, ["--instance", str(inst0), "--template", str(tmpl0),
                                    "--checklist", str(chk0), jout("g6_p0")])
    add("G6", "P0_POSITIVE_CONTROL", "positive control: unmutated copy of the real artefacts", [], rc, codes, tail)

    row = [ln for ln in sh(inst0).splitlines() if ln and not ln.startswith("#")]
    hdr, body = row[0].split("\t"), [ln.split("\t") for ln in row[1:]]
    idx = {c: i for i, c in enumerate(hdr)}
    b2 = [list(r) for r in body]
    b2[0][idx["E4"]] = ""
    iN1 = write(g6m / "N1_required_instance.tsv", "\n".join(["\t".join(hdr)] + ["\t".join(r) for r in b2]) + "\n")
    rc, codes, tail = run_gate(g6, ["--instance", str(iN1), "--template", str(tmpl0),
                                    "--checklist", str(chk0), jout("g6_n1")])
    add("G6", "N1_REQUIRED_EMPTY", "E4 emptied (required cell missing)", ["G6-R1"], rc, codes, tail)

    def edit(body_rows, cell, value, ev=None):
        b = [list(r) for r in body_rows]
        b[0][idx[cell]] = value
        if ev is not None:
            b[0][idx[cell + "_evidence"]] = ev
        return b

    def emit(tag, b):
        p = write(g6m / tag, "\n".join(["\t".join(hdr)] + ["\t".join(r) for r in b]) + "\n")
        return run_gate(g6, ["--instance", str(p), "--template", str(tmpl0),
                             "--checklist", str(chk0), jout(tag.replace(".tsv", ""))])

    rc, codes, tail = emit("N2_no_anchor_instance.tsv", edit(body, "Q2", "layer to fix = first-cause layer", "see report"))
    add("G6", "N2_EVIDENCE_NO_ANCHOR", "Q2_evidence -> \"see report\" (no resolvable anchor)", ["G6-R2"], rc, codes, tail)

    bN3 = edit(body, "Q3", "post-change expectation: the readouts improve as intended and the change is accepted.")
    rc, codes, tail = emit("N3_gains_only_instance.tsv", bN3)
    add("G6", "N3_ROLLBACK_TERM_REMOVED", "Q3 with the rollback/negative term removed (gains only)", ["G6-R5"], rc, codes, tail)

    bN4 = [list(r) for r in body]
    bN4[0][idx["Q4"]] = "criteria pre-registered: G5 eight checks + G6 eight rules, frozen before the run."
    bN4[0][idx["Q4_evidence"]] = "criteria section in /home/ubuntu/EYEKB_REPO/docs/VERIFY_CONTRACT_G5G6.md (on disk)"
    rc, codes, tail = emit("N4_no_sha_instance.tsv", bN4)
    add("G6", "N4_PREREG_NO_SHA", "Q4/Q4_evidence with the sha anchor removed", ["G6-R6"], rc, codes, tail)

    bN5 = [list(r) for r in body]
    bN5[0][idx["Q5"]] = "escape hatch: the gates added here are not wired into any default path; the existing escape hatches are unchanged."
    bN5[0][idx["Q5_evidence"]] = "see /home/ubuntu/EYEKB_REPO/docs/GATE_INVENTORY_G5G6.tsv (gate inventory)"
    rc, codes, tail = emit("N5_no_switch_instance.tsv", bN5)
    add("G6", "N5_ESCAPE_NO_SWITCH", "Q5 with the switch name removed (EYEKB_*)", ["G6-R7"], rc, codes, tail)

    bN6 = [list(r) for r in body]
    bN6[0][idx["M3"]] = bN6[0][idx["M3"]] + " this change includes a default ON behaviour change (EYEKB_CN_REWRITE semantics)."
    bN6[0][idx["M3_evidence"]] = bN6[0][idx["M3_evidence"]] + " see tests/G4_EXPECTED.json rc=0"
    rc, codes, tail = emit("N6_default_on_instance.tsv", bN6)
    add("G6", "N6_PRECOND_UNREGISTERED", "M3 declares a default-ON behaviour change without registering a gate precondition (VERIFY_CONTRACT)",
        ["G6-R8"], rc, codes, tail)

    bN7 = [list(r) for r in body]
    bN7[0][idx["M3"]] = "regression gate: ran it, it passed."
    bN7[0][idx["M3_evidence"]] = "see /home/ubuntu/EYEKB_REPO/docs/W3_CHANGE_CONTROL_CHECKLIST.md (human-readable checklist)"
    rc, codes, tail = emit("N7_no_threshold_instance.tsv", bN7)
    add("G6", "N7_NO_THRESHOLD_ACTION", "M3 says only \"ran it, it passed\" - no command and no expected readout (the mirror image of format-only checking)",
        ["G6-R2-CONCRETE"], rc, codes, tail)

    chk_lines = sh(chk0).splitlines(True)
    drop = [i for i, ln in enumerate(chk_lines) if ln.startswith("| 14 |")]
    assert len(drop) == 1, f"checklist row 14 not uniquely located: {drop}"
    chkN8 = write(g6m / "N8_map_checklist.md", "".join(chk_lines[:drop[0]] + chk_lines[drop[0] + 1:]))
    rc, codes, tail = run_gate(g6, ["--instance", str(inst0), "--template", str(tmpl0),
                                    "--checklist", str(chkN8), jout("g6_n8")])
    add("G6", "N8_CHECKLIST_MAP_GAP", "human checklist section 5 with row 14 dropped (rule-to-checklist mapping gap)", ["G6-MAP"], rc, codes, tail)

    n_ok = sum(1 for c in cases if c["ok"])
    res = {"card": "t_9dce4923 (G5G6 repo gates)", "harness": str(Path(__file__).resolve()),
           "method": "minimal mutation of the real artefacts (copies under fixtures only; repo artefacts untouched) -> run the gate -> assert rc!=0 with the expected check code",
           "contract": "the positive control must pass (otherwise the gate is untrustworthy); every negative case must be rejected with its target code; extra failures are recorded as-is",
           "n_cases": len(cases), "n_ok": n_ok, "all_as_expected": n_ok == len(cases),
           "fixtures_dir": str(fixtures), "results": cases,
           "by_gate": {g: {"n": sum(1 for c in cases if c["gate"] == g),
                           "ok": sum(1 for c in cases if c["gate"] == g and c["ok"])}
                       for g in ("G5", "G6")}}
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in cases:
        print(f"  [{'OK ' if c['ok'] else 'BAD'}] {c['gate']} {c['id']:<26} rc={c['rc']} "
              f"codes={c['failing_codes']} expect={c['expected_codes']}")
    print(f"G5G6 negative battery: {n_ok}/{len(cases)} as expected -> "
          f"{'PASS' if n_ok == len(cases) else 'FAIL'}")
    return 0 if n_ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())