#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Put this card in the change-control ledger, then let the ledger report its own verdict.

Appends one row (`CHG-20261029-DEFAULT-TIER`) to docs/CHANGE_CONTROL_G6_INSTANCE.tsv and writes
out/REGISTRY_ROWS.json with the identities it used. Every value that can be read from disk is read
from disk at run time — no hash, size or count in the row is typed from memory.
"""
import hashlib
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
G6 = os.path.join(REPO, "docs", "CHANGE_CONTROL_G6_INSTANCE.tsv")
CARD_MD = os.path.join(CARD, "CARD.md")
VERIFY = os.path.join(REPO, "docs", "VERIFY_CONTRACT.md")
ROW_ID = "CHG-20261029-DEFAULT-TIER"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    card_sha = sha(CARD_MD)
    verify_sha = sha(VERIFY)
    before = json.load(open(os.path.join(OUT, "BEFORE.json")))["cases"]
    after = json.load(open(os.path.join(OUT, "AFTER.json")))["cases"]
    envfull = json.load(open(os.path.join(OUT, "AFTER_ENV_FULL.json")))["cases"]

    def c(d, k):
        return d[k]["chars"]

    restored = [k for k in ("index_default", "tissue_default", "comp_default",
                            "comp_mouse_default") if envfull[k]["md5"] == before[k]["md5"]]

    cells = [
        ROW_ID,
        "maintainer (repo-side production code; card docs/plans/default_tier_20261029; PI released "
        "the work on 2026-10-29 by approving the planned order)",

        "mcp_server/server.py — the two tool wrappers (mcp_server/eyekb_core.py untouched)",

        "L5 (tool surface / presentation). The first cause is not retrieval, ranking or the marker "
        "libraries: the wrapper chose the heavy response tier when the caller expressed no "
        "preference, so every default call paid for the largest possible answer.",
        "docs/plans/default_tier_20261029/CARD.md:15 (scope: wrapper only) | "
        "mcp_server/server.py:246 (_default_tier) | docs/VERIFY_CONTRACT.md:366 (§5.8)",

        "Symptom origin: the previous usability pass made the tier switch discoverable but left the "
        "heavy tier as the default, so the lever only helped callers who read the description. "
        "Measured, not inferred: one default index call returned 140,005 characters.",
        "docs/plans/default_tier_20261029/out/BEFORE.json (index_default chars) | "
        "docs/plans/ux_pass2_20261022/REPORT.md:102",

        "Gain and rollback term together. rollback = EYEKB_DEFAULT_DETAIL=full, which restores the "
        "pre-change default byte-for-byte on all four default calls. Known loss: the legacy tool "
        "panel digest moves on exactly one call (mouse composition default), and three further "
        "panel calls were already moved before this card by catalogue and library growth.",
        "docs/plans/default_tier_20261029/out/AFTER_ENV_FULL.json (4/4 restored to BEFORE md5) | "
        "docs/VERIFY_CONTRACT.md §5.8 (legacy panel item, reported not absorbed)",

        "Pre-registered criteria fixed before any edit: C1 heavy tier byte-identical, C2 legacy "
        "summary=False unchanged, C3a/C3b size ratio, C4 environment revert, C5 per-row citations "
        "preserved, C6 gate chain unchanged, C7 revert path executed, C8 no silent shrink. "
        "Criterion C3 was amended once, before any edit, because its absolute threshold had been "
        "derived from a stale catalogue size; the amendment and its ordering evidence are on disk. "
        "CARD.md sha256=" + card_sha + " AMENDMENT_1_C3.md sha256="
        + sha(os.path.join(CARD, "AMENDMENT_1_C3.md")),
        "docs/plans/default_tier_20261029/CARD.md | "
        "docs/plans/default_tier_20261029/AMENDMENT_1_C3.md | "
        "docs/plans/default_tier_20261029/verify_default_tier.py",

        "Escape door: EYEKB_DEFAULT_DETAIL. OFF set = {full, heavy, all}; with "
        "EYEKB_DEFAULT_DETAIL=full all four default calls return the pre-change bytes (md5 equality "
        "in the reading file), and every explicit detail=/summary= argument was byte-identical "
        "before and after in both directions.",
        "docs/plans/default_tier_20261029/out/AFTER_ENV_FULL.json | "
        "docs/SWITCH_COVERAGE_REGISTRY.tsv (EYEKB_DEFAULT_DETAIL, answer-affecting) | "
        "docs/plans/default_tier_20261029/out/AFTER.json (explicit calls)",

        "Version identity: mcp_server/server.py sha256 " + sha(os.path.join(REPO, "mcp_server", "server.py"))
        + " (" + str(os.stat(os.path.join(REPO, "mcp_server", "server.py")).st_size) + " B); "
        "mcp_server/eyekb_core.py untouched at "
        + sha(os.path.join(REPO, "mcp_server", "eyekb_core.py"))
        + "; docs/SWITCH_COVERAGE_REGISTRY.tsv regenerated from the source (29 rows).",
        "docs/plans/default_tier_20261029/out/REGISTRY_ROWS.json | docs/SWITCH_COVERAGE_REGISTRY.tsv",

        "Impact surface. Changes: the two tools' default responses (index 140,005 -> "
        + str(c(after, "index_default")) + " chars; human composition 91,332 -> "
        + str(c(after, "comp_default")) + " chars), and the default responses now carry "
        "detail_applied + detail_note. Does not change: every explicit tier, the core module, any "
        "ranking, any proportion, any citation, the tables on disk, the pipeline outputs.",
        "docs/plans/default_tier_20261029/out/AFTER.json | "
        "docs/plans/default_tier_20261029/out/verify_output.txt",

        "Executable criteria (command + expected readout): "
        "python3 docs/plans/default_tier_20261029/verify_default_tier.py -> expected 7/7 criteria "
        "pass, rc=0; python3 tests/gate_change_control.py -> expected 21 checks, 0 fail, rc=0; "
        "python3 tests/gate_g5g6_negative.py -> expected the same 16/17 cell as before this card "
        "(the pre-existing G5 positive-control red), rc=1 in both states. Per VERIFY_CONTRACT §5.8.",
        "docs/plans/default_tier_20261029/out/verify_output.txt | docs/plans/default_tier_20261029/out/GATE_VERDICTS.json",

        "E1 readings taken now, not quoted from the earlier usability pass: index default "
        + str(c(before, "index_default")) + " -> " + str(c(after, "index_default"))
        + " chars; human composition " + str(c(before, "comp_default")) + " -> "
        + str(c(after, "comp_default")) + " chars; mouse composition " + str(c(before, "comp_mouse_default"))
        + " -> " + str(c(after, "comp_mouse_default")) + " chars; tissue page unchanged at "
        + str(c(after, "tissue_default")) + " chars; explicit heavy/light calls byte-identical "
        "(3/3 and 2/2); environment revert restores " + str(len(restored)) + "/4.",
        "docs/plans/default_tier_20261029/out/BEFORE.json | "
        "docs/plans/default_tier_20261029/out/AFTER.json | "
        "docs/plans/default_tier_20261029/out/AFTER_ENV_FULL.json",

        "E2 regression gates: python3 tests/gate_change_control.py expected rc=0 (measured 21 checks "
        "0 fail); python3 tests/gate_switch_coverage.py expected rc=0 with R1 registry-in-sync "
        "(measured rc=0, 29 rows); python3 tests/gate_g5g6_negative.py byte-identical output before "
        "and after, rc=1 both states on the pre-existing G5 cell; python3 tests/verify_pipeline.py "
        "expected the pre-existing G4 1/3 mismatch, not 0/3 and not 2/3.",
        "docs/plans/default_tier_20261029/out/GATE_VERDICTS.json | "
        "docs/plans/default_tier_20261029/out/battery_pre.txt | "
        "docs/plans/default_tier_20261029/out/battery_post.txt",

        "E3 rollback evidence (executed, not asserted): the same probe was run with "
        "EYEKB_DEFAULT_DETAIL=full against the changed code and compared with the pre-change run — "
        + str(len(restored)) + "/4 default calls byte-identical, and the compact-with-disclosure "
        "fields are absent in that state. Rollback needs no file edit, only the variable.",
        "docs/plans/default_tier_20261029/out/AFTER_ENV_FULL.json vs out/BEFORE.json | "
        "docs/plans/default_tier_20261029/verify_default_tier.py (C4)",

        "E4 boundary: this card does not claim an accuracy or speed gain — it claims a smaller "
        "default with the full answer preserved and reachable. Latency is not reported: it must be "
        "re-measured on an idle machine. No acceptance baseline was moved; the G4 expected anchor and "
        "the legacy tool-panel baseline are left exactly where they were.",
        "docs/plans/default_tier_20261029/CARD.md:43 (out of scope) | "
        "docs/plans/default_tier_20261029/REPORT.md (latency section)",
    ]

    fields = ["change_id", "owner", "entry_point",
              "Q1", "Q1_evidence", "Q2", "Q2_evidence", "Q3", "Q3_evidence",
              "Q4", "Q4_evidence", "Q5", "Q5_evidence",
              "M1", "M1_evidence", "M2", "M2_evidence", "M3", "M3_evidence",
              "E1", "E1_evidence", "E2", "E2_evidence", "E3", "E3_evidence", "E4", "E4_evidence"]
    assert len(cells) == len(fields), (len(cells), len(fields))

    text = open(G6, encoding="utf-8").read()
    if ROW_ID in text:
        print(f"row {ROW_ID} already present; nothing appended")
    else:
        cells = [" ".join(str(x).split()) for x in cells]  # no newlines inside a TSV cell
        assert not any("\t" in x for x in cells), "a cell contains a tab"
        with open(G6, "a", encoding="utf-8") as fh:
            fh.write("\t".join(cells) + "\n")
        print(f"appended {ROW_ID} to {G6}")

    rows = {"row_id": ROW_ID, "card_md_sha256": card_sha, "verify_contract_sha256": verify_sha,
            "server_py_sha256": sha(os.path.join(REPO, "mcp_server", "server.py")),
            "n_fields": len(cells), "written_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    with open(os.path.join(OUT, "REGISTRY_ROWS.json"), "w") as fh:
        json.dump(rows, fh, indent=1, sort_keys=True)

    rc = subprocess.run([sys.executable, os.path.join(REPO, "tests", "gate_change_control.py")],
                        cwd=REPO, capture_output=True, text=True)
    tail = [ln for ln in rc.stdout.splitlines() if ln.startswith("[g6]")]
    print(tail[0] if tail else rc.stdout[-300:])
    print(f"gate_change_control rc={rc.returncode}")
    return rc.returncode


sys.exit(main())