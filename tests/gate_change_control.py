#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/gate_change_control.py — G6 gate: change control is machine-checked, not tick-boxed.

Ported from the project-side change-control validator
(`W3_NORM/R1/scripts/validate_change_control.py`, card t_59266f94) into the mirror repo as a
repo-side hard gate. Human-readable checklist = docs/W3_CHANGE_CONTROL_CHECKLIST.md; this
script is its machine counterpart: "five pre-change questions / three mid-change artefacts / four
post-change proofs" become cells + regex, and
a missing or anchorless cell is rc=2.

Eight machine rules (each FAIL names its own rule code, never a bare "G6 FAIL"):
  R1 REQUIRED   the 12 content cells (Q1-Q5 / M1-M3 / E1-E4) + 3 identity cells are non-empty;
                every content cell also carries a `*_evidence` cell
  R2 EVIDENCE   every evidence cell carries a resolvable anchor (existing path / file:line:substr /
                64-hex sha / *.sha256 path / rc=<n> / card t_xxxxxxxx) — a bare conclusion fails;
                and the concrete-action cells must carry a *number*, not prose (see R2-CONCRETE)
  R3 NA         "not applicable" must be rule-numbered (`NA-<n>`) with a reason >= 20 chars that
                names a path that exists
  R4 OUTCOME1   Q1 states the responsibility-layer id (L0-L6) — first-cause layer is declared
  R5 MONOTONE   Q3 states the rollback/negative term (loss|rollback|negative|not monotone); gains
                only = FAIL
  R6 PREREG     Q4 carries a sha anchor (64-hex or a *.sha256 path) for the pre-registered criteria
  R7 ESCAPE     Q5 carries the switch name (EYEKB_*) and an OFF byte-identity statement
  R8 PRECOND    a default-ON behaviour change referenced by M3/E2 must be registered as a gate
                precondition in docs/VERIFY_CONTRACT.md

Structural precondition (not one of the eight rules): G6-MAP — every judgement row of the
human checklist's section 5 table is covered by the rule-to-checklist mapping; a dangling row
number means the machine rules and the human checklist have drifted apart.

The rule "cite concrete thresholds and actions, never stop at format checking" is enforced two ways:
R2 requires a concrete number/rc/sha
anchor (prose without a readout fails), and the R2-CONCRETE arm demands that the regression-gate
cell (M3), the sha-evidence cell (E1) and the rollback-identity cell (E2) each carry an
executable command or an expected readout — a cell that merely says "we ran the gate" fails.

Stdlib only, zero network, zero GPU, read-only. Usage (from repo root):
  python3 tests/gate_change_control.py
  python3 tests/gate_change_control.py --instance docs/CHANGE_CONTROL_G6_INSTANCE.tsv --json OUT.json
Exit codes: 0 = PASS, 2 = FAIL (fail-closed).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IDENTITY = ["change_id", "owner", "entry_point"]
CONTENT = ["Q1", "Q2", "Q3", "Q4", "Q5", "M1", "M2", "M3", "E1", "E2", "E3", "E4"]
PATH_RE = re.compile(r"(?:/[\w\u4e00-\u9f5a.\-]+)+")
SHA_RE = re.compile(r"\b[0-9a-f]{64}\b|\.sha256")
SWITCH_RE = re.compile(r"EYEKB_[A-Z0-9_]+")
NA_RE = re.compile(r"^NA[:：]\s*(NA-\d+)\s*[:：,]?\s*(.{20,})$", re.S)
ANCHOR_EXTRA = re.compile(r"rc=\d|\bt_[0-9a-f]{8}\b|【|\d+/\d+")
FILLED = re.compile(r"[A-Za-z\u4e00-\u9f5a]")

# Rule -> judgement rows of docs/W3_CHANGE_CONTROL_CHECKLIST.md section 5 (human checklist).
# Coverage of rows 1..14 by the union is asserted (G6-MAP).
CHECKLIST_MAP = {"R1": [1, 2, 3, 8, 9, 11, 12, 13, 14],
                 "R2": [1, 10, 11, 13],
                 "R3": [2],
                 "R4": [1],
                 "R5": [4],
                 "R6": [5],
                 "R7": [6],
                 "R8": [7],
                 "R2-CONCRETE": [9, 11, 12]}


def read_rows(p: Path) -> list:
    lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if not ln.startswith("#")]
    if not lines:
        return []
    hdr = lines[0].split("\t")
    return [dict(zip(hdr, ln.split("\t"))) for ln in lines[1:] if ln.strip()]


def checklist_rows(p: Path) -> list:
    """Judgement rows of the checklist's section 5 table (leading integer column)."""
    if not p.exists():
        return []
    txt = p.read_text(encoding="utf-8")
    rows = []
    for m in re.finditer(r"^\|\s*(\d{1,2})\s*\|", txt, re.M):
        rows.append(int(m.group(1)))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", default=str(ROOT / "docs" / "CHANGE_CONTROL_G6_INSTANCE.tsv"))
    ap.add_argument("--template", default=str(ROOT / "docs" / "CHANGE_CONTROL_G6_TEMPLATE.tsv"))
    ap.add_argument("--checklist", default=str(ROOT / "docs" / "W3_CHANGE_CONTROL_CHECKLIST.md"))
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    inst_p = Path(a.instance)
    tmpl_p = Path(a.template)
    chk_p = Path(a.checklist)
    checks, findings = [], []
    verdicts = []

    def rec(code: str, ok: bool, detail: str, offenders=None) -> None:
        short, _, label = code.partition(" ")          # machine code vs human label: code is asserted on, label is for people
        checks.append({"code": short, "label": label, "status": "PASS" if ok else "FAIL", "detail": detail,
                       "n_offenders": len(offenders or []), "offenders": (offenders or [])[:40]})

    def evidence_ok(ev: str) -> bool:
        if not ev:
            return False
        paths = PATH_RE.findall(ev)
        if any(Path(q).exists() for q in paths):
            return True
        return bool(re.search(r"/[\w.\-]+:\d+:", ev)) or bool(SHA_RE.search(ev)) or bool(ANCHOR_EXTRA.search(ev))

    targets = []
    for tag, p in (("instance", inst_p), ("template", tmpl_p)):
        if not p.exists():
            rec("G6-R1 REQUIRED", False, f"{tag} not on disk: {p}", [str(p)])
            targets.append((tag, []))
        else:
            targets.append((tag, read_rows(p)))

    per_change = []
    for tag, rows in targets:
        if not rows:
            verdicts.append(f"{tag}:NO_ROWS")
            continue
        bad_required, bad_evidence, bad_na, bad_q1, bad_q3, bad_q4, bad_q5, bad_conc, bad_pre = \
            [], [], [], [], [], [], [], [], []
        for r in rows:
            rid = f"{tag}:{r.get('change_id', '?')}"
            for c in IDENTITY + CONTENT:
                v = (r.get(c) or "").strip()
                if not v:
                    bad_required.append(f"{rid}.{c} empty (R1)")
                    continue
                if c in IDENTITY:
                    continue
                ev = (r.get(c + "_evidence") or "").strip()
                na = NA_RE.match(v)
                if na:
                    rule, reason = na.group(1), na.group(2)
                    if not any(Path(q).exists() for q in PATH_RE.findall(reason)):
                        bad_na.append(f"{rid}.{c}: NA reason names no existing path ({rule})")
                    continue
                if not ev:
                    bad_evidence.append(f"{rid}.{c}: no evidence cell (R2)")
                elif not evidence_ok(ev):
                    bad_evidence.append(f"{rid}.{c}: evidence has no resolvable anchor (R2): {ev[:60]}")
            if not re.search(r"\bL[0-6]\b", r.get("Q1", "")):
                bad_q1.append(f"{rid}.Q1: no responsibility-layer id L0-L6 (R4)")
            if not re.search(r"(loss|rollback|negative|not monotone)", r.get("Q3", "")):
                bad_q3.append(f"{rid}.Q3: no rollback/negative term (R5) — gains-only is not accepted")
            if not SHA_RE.search((r.get("Q4", "") or "") + (r.get("Q4_evidence", "") or "")):
                bad_q4.append(f"{rid}.Q4: no sha anchor for the pre-registered criteria (R6)")
            if not SWITCH_RE.search(r.get("Q5", "") or "") or not re.search(
                    r"(byte|sha|identical)", (r.get("Q5", "") or "") + (r.get("Q5_evidence", "") or "")):
                bad_q5.append(f"{rid}.Q5: escape door lacks a switch name or an OFF byte-identity statement (R7)")
            # R2-CONCRETE: command/expected readout, not prose
            for c in ("M3", "E1", "E2"):
                cell = (r.get(c, "") or "") + " " + (r.get(c + "_evidence", "") or "")
                if NA_RE.match((r.get(c) or "").strip()):
                    continue
                if not re.search(r"(rc=\d|\d+/\d+|expected|≥|<=|==\s*\d|sha256sum|python3?\s+tests/|bash\s+tests/)", cell):
                    bad_conc.append(f"{rid}.{c}: no executable command / expected readout (R2-CONCRETE)")
            joined = (r.get("M3", "") or "") + (r.get("E2", "") or "") + (r.get("E2_evidence", "") or "")
            if re.search(r"(default\s*on|EYEKB_CN_REWRITE)", joined) and "VERIFY_CONTRACT" not in joined:
                bad_pre.append(f"{rid}: default-ON behaviour change not registered as a gate precondition (R8)")
            per_change.append({"tag": tag, "change_id": r.get("change_id", "?"),
                               "entry_point": r.get("entry_point", ""),
                               "verdict": "FAIL" if any((bad_required, bad_evidence, bad_na, bad_q1,
                                                         bad_q3, bad_q4, bad_q5, bad_conc, bad_pre)) else "PASS"})
        rec("G6-R1 REQUIRED", not bad_required,
            f"[{tag}] empty required cells: {len(bad_required)}", bad_required)
        rec("G6-R2 EVIDENCE", not bad_evidence,
            f"[{tag}] evidence cells without a resolvable anchor: {len(bad_evidence)}", bad_evidence)
        rec("G6-R3 NA", not bad_na, f"[{tag}] rule-numbered NA defects: {len(bad_na)}", bad_na)
        rec("G6-R4 OUTCOME1", not bad_q1, f"[{tag}] Q1 layer-id defects: {len(bad_q1)}", bad_q1)
        rec("G6-R5 MONOTONE", not bad_q3, f"[{tag}] Q3 rollback-term defects: {len(bad_q3)}", bad_q3)
        rec("G6-R6 PREREG", not bad_q4, f"[{tag}] Q4 sha-anchor defects: {len(bad_q4)}", bad_q4)
        rec("G6-R7 ESCAPE", not bad_q5, f"[{tag}] Q5 escape-door defects: {len(bad_q5)}", bad_q5)
        rec("G6-R8 PRECOND", not bad_pre, f"[{tag}] gate-precondition defects: {len(bad_pre)}", bad_pre)
        rec("G6-R2-CONCRETE", not bad_conc,
            f"[{tag}] concrete-action cells without a command/threshold: {len(bad_conc)}", bad_conc)
        verdicts.append(f"{tag}:{'FAIL' if any((bad_required, bad_evidence, bad_na, bad_q1, bad_q3, bad_q4, bad_q5, bad_conc, bad_pre)) else 'PASS'}")

    # G6-MAP (structural precondition: human checklist section 5 <-> machine rules)
    rows_seen = checklist_rows(chk_p)
    expected = set(range(1, 15))
    covered = set()
    for v in CHECKLIST_MAP.values():
        covered |= set(v)
    map_err = []
    if not chk_p.exists():
        map_err.append(f"human checklist not on disk: {chk_p}")
    else:
        if sorted(set(rows_seen)) != sorted(expected):
            map_err.append(f"section-5 judgement rows found={sorted(set(rows_seen))} expected=1..14")
        uncovered = sorted(expected - covered)
        dangling = sorted(covered - set(rows_seen))
        if uncovered:
            map_err.append(f"checklist rows not covered by any machine rule: {uncovered}")
        if dangling:
            map_err.append(f"rule mapping names rows absent from the checklist: {dangling}")
    rec("G6-MAP", not map_err,
        f"checklist rows={len(set(rows_seen))}; covered={len(covered & set(rows_seen))}; problems={len(map_err)}",
        map_err)

    verdict = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    res = {"gate": "G6", "script": str(Path(__file__).resolve()),
           "inputs": {"instance": str(inst_p), "template": str(tmpl_p), "checklist": str(chk_p)},
           "changes": per_change, "verdict": verdict, "n_checks": len(checks),
           "n_fail": sum(1 for c in checks if c["status"] == "FAIL"),
           "rules": {"R1": "15 required cells non-empty", "R2": "evidence anchor + concrete readout",
                     "R3": "NA must be rule-numbered and path-backed", "R4": "Q1 declares L0-L6",
                     "R5": "Q3 declares the rollback term", "R6": "Q4 carries a sha anchor",
                     "R7": "Q5 carries switch name + OFF identity", "R8": "default-ON change registered as gate precondition",
                     "R2-CONCRETE": "M3/E1/E2 must cite a command or an expected readout"},
           "checklist_map": CHECKLIST_MAP, "checks": checks}
    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[g6] changes={len(per_change)} checks={len(checks)} fail={res['n_fail']} verdict={verdict} "
          f"({'; '.join(verdicts)})")
    for c in checks:
        print(f"  {c['status']} {c['code']} {c['label']} :: {c['detail']}")
        for o in c["offenders"][:6]:
            print(f"      - {o}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())