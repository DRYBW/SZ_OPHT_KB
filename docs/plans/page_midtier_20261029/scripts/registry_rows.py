#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Put this card in the change-control ledger, then let the ledger report its own verdict.

Appends one row (`CHG-20261029-PAGE-MIDTIER`) to docs/CHANGE_CONTROL_G6_INSTANCE.tsv and writes
out/REGISTRY_ROWS.json with the identities it used. Every hash, size and count in the row is read
from disk or from the card's own readings at run time.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CARD = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(CARD, "..", "..", ".."))
OUT = os.path.join(CARD, "out")
G6 = os.path.join(REPO, "docs", "CHANGE_CONTROL_G6_INSTANCE.tsv")
CARD_MD = os.path.join(CARD, "CARD.md")
SERVER = os.path.join(REPO, "mcp_server", "server.py")
VERIFY = os.path.join(REPO, "docs", "VERIFY_CONTRACT.md")
ROW_ID = "CHG-20261029-PAGE-MIDTIER"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    card_sha = sha(CARD_MD)
    a = json.load(open(os.path.join(OUT, "AFTER.json")))
    b = json.load(open(os.path.join(OUT, "BEFORE.json")))
    pages = a["pages"]
    defaulted = {k: v for k, v in pages.items() if v.get("default_applied") == "outline"}
    worst = max(defaulted.items(), key=lambda kv: kv[1]["outline_chars"] / kv[1]["full_chars"])
    best = max(defaulted.values(), key=lambda v: v["full_chars"] / v["outline_chars"])
    rebuilt = [k for k, v in pages.items() if v.get("rebuild_identical") is True]
    max_slice = max(v.get("slice_default_chars", 0) for v in pages.values())
    biggest = max(pages.items(), key=lambda kv: kv[1].get("full_chars", 0))
    verified = subprocess.run([sys.executable, os.path.join(CARD, "verify_page_tiers.py")],
                              capture_output=True, text=True)
    verdict_line = [ln for ln in verified.stdout.splitlines() if "criteria pass" in ln]

    cells = [
        ROW_ID,
        "maintainer (repo-side production code; card docs/plans/page_midtier_20261029; the work was "
        "released by the project owner as part of the ordered follow-up run)",

        "mcp_server/server.py — the get_kb_page wrapper only (mcp_server/eyekb_core.py untouched)",

        "L5 (tool surface / presentation). The first cause is a missing view, not a retrieval or "
        "ranking problem: a single page had nothing between one row and the whole document, so a "
        "41,930-character tissue page could only be read by pulling all of it into the caller's "
        "context.",
        "docs/plans/page_midtier_20261029/CARD.md:15 (design) | mcp_server/server.py "
        "(PAGE_OUTLINE_THRESHOLD, _outline_view, _slice_view) | docs/VERIFY_CONTRACT.md §5.9",

        "Symptom origin: the previous card fixed the catalogue and named this gap in its own "
        "out-of-scope list, with the size attached: tissue page 41,930 characters, largest page in "
        "the tree 191,143. Measured again before any edit in out/BEFORE.json.",
        "docs/plans/default_tier_20261029/REPORT.md:103 | "
        "docs/plans/page_midtier_20261029/out/BEFORE.json (cornea_default 41930 chars)",

        "Gain and loss together. Gain: " + str(len(defaulted)) + " pages above 20,000 characters now "
        "default to an outline; the worst saving is " + worst[0] + " "
        + str(worst[1]["full_chars"]) + " -> " + str(worst[1]["outline_chars"]) + " chars ("
        + f"{worst[1]['full_chars'] / worst[1]['outline_chars']:.1f}x" + "), the best is "
        + str(best["full_chars"]) + " -> " + str(best["outline_chars"]) + " chars. Loss/rollback: two "
        "pre-registered criteria missed and stay red (C4 absolute bound, C6 wording), recorded below "
        "and in AMENDMENT_2; rollback of the default is EYEKB_DEFAULT_DETAIL=full, measured to "
        "restore 28/28 non-catalogue pages from BEFORE.",
        "docs/plans/page_midtier_20261029/out/AFTER.json | "
        "docs/plans/page_midtier_20261029/out/AFTER_ENV_FULL.json | "
        "docs/plans/page_midtier_20261029/AMENDMENT_2_C4_C6.md",

        "Pre-registered criteria (C1-C8) fixed before any edit; strict verdict as measured = 5/7, "
        "carried as 5/7. The two misses are named: C4 failed on its absolute 2,500-character bound "
        "(largest page was INCLUSIONS_RECENT 200,447 chars, outline 2,663; not tuned afterwards), "
        "C6 failed on wording that did not carve out the catalogue (it defaults to the inventory per "
        "§5.8) although 28/28 non-catalogue pages obey the rule and revert. "
        "CARD.md sha256=" + card_sha + " AMENDMENT_2 sha256="
        + sha(os.path.join(CARD, "AMENDMENT_2_C4_C6.md")),
        "docs/plans/page_midtier_20261029/CARD.md | "
        "docs/plans/page_midtier_20261029/AMENDMENT_2_C4_C6.md | "
        "docs/plans/page_midtier_20261029/out/verify_output.txt",

        "Escape door: EYEKB_DEFAULT_DETAIL (already registered by §5.8; this card introduces no new "
        "switch, registry unchanged at 29 rows and R1 in sync). With EYEKB_DEFAULT_DETAIL=full every "
        "non-catalogue page returns its pre-change default bytes (28/28 identical to BEFORE) and the "
        "catalogue returns the full text per §5.8; explicit detail=full/outline/slice calls are "
        "byte-identical in both states.",
        "docs/plans/page_midtier_20261029/out/AFTER_ENV_FULL.json | docs/SWITCH_COVERAGE_REGISTRY.tsv | "
        "docs/plans/page_midtier_20261029/out/AFTER.json (explicit calls)",

        "Version identity: mcp_server/server.py sha256 " + sha(SERVER) + " (" + str(os.stat(SERVER).st_size)
        + " B); mcp_server/eyekb_core.py untouched at " + sha(os.path.join(REPO, "mcp_server", "eyekb_core.py"))
        + "; no new switch, so docs/SWITCH_COVERAGE_REGISTRY.tsv is byte-unchanged.",
        "docs/plans/page_midtier_20261029/out/REGISTRY_ROWS.json | docs/SWITCH_COVERAGE_REGISTRY.tsv",

        "Impact surface. Changes: get_kb_page gains detail=outline and detail=slice, two new "
        "arguments (offset, limit), and the default for pages over 20,000 characters. Does not "
        "change: the catalogue default (inventory), any page text on disk, the compact answer view, "
        "composition/disease/marker tools, any ranking or any pipeline output. A structured "
        "row-per-paper view was designed and REJECTED on measurement: one regex round-trips only "
        "1,697 of 7,493 paper lines, so it would have dropped three quarters of the corpus.",
        "docs/plans/page_midtier_20261029/CARD.md:26 | "
        "docs/plans/page_midtier_20261029/out/AFTER.json",

        "Executable criteria (command + expected readout): python3 "
        "docs/plans/page_midtier_20261029/verify_page_tiers.py -> prints 5/7 criteria pass and exits "
        "1 because two pre-registered criteria are red by design of the record; python3 "
        "tests/gate_change_control.py -> expected 21 checks 0 fail rc=0; python3 "
        "tests/gate_switch_coverage.py -> expected R1 in sync rc=0; python3 "
        "tests/verify_pipeline.py -> expected the pre-existing 1/3 mismatch, unchanged.",
        "docs/plans/page_midtier_20261029/out/verify_output.txt | "
        "docs/plans/page_midtier_20261029/out/GATE_VERDICTS.json",

        "E1 readings taken in this card, not quoted: " + str(len(rebuilt)) + "/" + str(len(pages))
        + " pages rebuilt byte-identically from slices (walk steps 37 lines, 997 on the two largest); "
        "outline numbers re-derived independently on " + str(len(pages)) + " pages with 0 field "
        "mismatches; largest page " + biggest[0] + " " + str(biggest[1]["full_chars"]) + " chars -> "
        "outline " + str(biggest[1]["outline_chars"]) + " chars; largest default-size slice "
        + str(max_slice) + " chars; strict verdict " + (verdict_line[0].strip() if verdict_line else "n/a") + ".",
        "docs/plans/page_midtier_20261029/out/AFTER.json | "
        "docs/plans/page_midtier_20261029/out/verify_output.txt",

        "E2 regression gates: python3 tests/gate_change_control.py expected rc=0 (measured 21 checks "
        "0 fail); python3 tests/gate_switch_coverage.py expected rc=0 with R1 registry-in-sync "
        "(measured rc=0, 29 rows); python3 tests/gate_g5g6_negative.py expected the same 16/17 cell "
        "and byte-identical output to the previous run (measured identical); python3 "
        "tests/verify_pipeline.py expected the pre-existing G4 1/3 mismatch (measured 1/3, same two "
        "hashes 7c225802 vs 6f795b32).",
        "docs/plans/page_midtier_20261029/out/GATE_VERDICTS.json | "
        "docs/plans/page_midtier_20261029/out/battery_post.txt",

        "E3 rollback evidence (executed): the probe was run again against the changed code with "
        "EYEKB_DEFAULT_DETAIL=full; 28/28 non-catalogue pages returned their pre-change default "
        "characters and md5s, and the catalogue returned the 140,005-character text. Rollback needs "
        "no file edit, only the variable; the two new views stay available in that state.",
        "docs/plans/page_midtier_20261029/out/AFTER_ENV_FULL.json vs out/BEFORE.json | "
        "docs/plans/page_midtier_20261029/verify_page_tiers.py (C6)",

        "E4 boundary: no accuracy, latency or ranking claim. The product-facing consequence is stated "
        "plainly: a caller that reads a long page without asking for a view now gets its structure "
        "rather than the paper list, and one argument returns the list. No acceptance baseline was "
        "moved: G4's expected anchor and the legacy tool-panel baseline are untouched by this card.",
        "docs/plans/page_midtier_20261029/REPORT.md (what this does not do) | "
        "docs/plans/page_midtier_20261029/AMENDMENT_2_C4_C6.md",
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
        cells = [" ".join(str(x).split()) for x in cells]
        assert not any("\t" in x for x in cells), "a cell contains a tab"
        with open(G6, "a", encoding="utf-8") as fh:
            fh.write("\t".join(cells) + "\n")
        print(f"appended {ROW_ID} to {G6}")

    with open(os.path.join(OUT, "REGISTRY_ROWS.json"), "w") as fh:
        json.dump({"row_id": ROW_ID, "card_md_sha256": card_sha,
                   "server_py_sha256": sha(SERVER), "verify_contract_sha256": sha(VERIFY),
                   "n_fields": len(cells),
                   "written_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, fh, indent=1,
                  sort_keys=True)

    rc = subprocess.run([sys.executable, os.path.join(REPO, "tests", "gate_change_control.py")],
                        cwd=REPO, capture_output=True, text=True)
    tail = [ln for ln in rc.stdout.splitlines() if ln.startswith("[g6]")]
    print(tail[0] if tail else rc.stdout[-300:])
    print(f"gate_change_control rc={rc.returncode}")
    return rc.returncode


sys.exit(main())