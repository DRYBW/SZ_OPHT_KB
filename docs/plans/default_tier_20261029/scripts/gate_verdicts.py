#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the gate chain this card claims and write out/GATE_VERDICTS.json from the runs themselves.

Nothing here is typed from memory: each entry is the command, the exit code the subprocess actually
returned, and the lines of its output that carry the verdict. A gate this card does not own (G4) is
recorded with the mismatch count it reports, not with the word PASS or FAIL.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(CARD, "..", "..", ".."))
OUT = os.path.join(CARD, "out")
PY = os.environ.get("UX_PY", sys.executable)

GATES = [
    ("card_criteria", [PY, os.path.join(CARD, "verify_default_tier.py")],
     r"(criteria pass)"),
    ("g6_change_control", [PY, os.path.join(REPO, "tests", "gate_change_control.py")],
     r"^\[g6\]"),
    ("g5_switch_coverage", [PY, os.path.join(REPO, "tests", "gate_switch_coverage.py")],
     r"^\s+R1 |^\s+R2 "),
    ("g5g6_negative_battery", [PY, os.path.join(REPO, "tests", "gate_g5g6_negative.py")],
     r"negative battery|^\[BAD\]"),
    ("g4_verify_pipeline", [PY, os.path.join(REPO, "tests", "verify_pipeline.py")],
     r"^G4 |^FAIL "),
    ("legacy_tool_panel", [PY, os.path.join(REPO, "tests", "probe_tool_panel_identity.py"),
                           "--baseline", os.path.join(REPO, "tests", "fixtures",
                                                      "tool_panel_baseline.json")],
     r"IDENTITY |legacy_panel|different: "),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    report = {"written_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "gates": {}}
    for name, cmd, pat in GATES:
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        rx = re.compile(pat)
        lines = [ln.strip() for ln in (proc.stdout + proc.stderr).splitlines() if rx.search(ln)]
        report["gates"][name] = {
            "command": " ".join(os.path.relpath(c, REPO) if c.startswith(REPO) else c for c in cmd),
            "rc": proc.returncode,
            "verdict_lines": lines[:12],
        }
        print(f"{name:26s} rc={proc.returncode}  {lines[0] if lines else ''}"[:160])
    with open(os.path.join(OUT, "GATE_VERDICTS.json"), "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return 0


sys.exit(main())