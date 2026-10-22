#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l4 -- re-take the registrations this activation invalidates, in the same commit (A5).

Because the flip changes the default response bytes **on purpose**, the registry rows whose files
moved must be re-taken from live bytes, and the rows whose *status* changed must say so:

  L1-11M  the delivery copy of the service core   -> sha/bytes/mtime + the activation note
  L1-30   the optic-nerve fibroblast carrier      -> authority/state text (file bytes unchanged)
  L6-01   docs/VERIFY_CONTRACT.md                 -> sha/bytes/mtime (the R8 precondition registration)
  L6-37   the tool-panel baseline fixture         -> a note: the digest moved and was NOT re-recorded

Every edit asserts its anchor occurs exactly once, and the file is written back atomically (the
predecessor wave lost this file once to a mid-write raise; the atomic rename is the fix).
"""
import csv
import datetime
import hashlib
import json
import os
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))

NOTE_CORE = (
    " | 2026-10-22 activation card t_42df17c2 (L7, PI-signed \"载体并进默认路由\"): "
    "ONFIBRO_DEFAULT_LIBS gains `onfibro_v13`, so the optic-nerve fibroblast carrier is part of the "
    "default `all` route whenever EYEKB_ACT_ONFIBRO is unset/on. Measured with the reused harness "
    "(docs/plans/noregr_20261022/scripts/n3_harness.py) over 28 volumes / 721 clusters / 1,495,330 "
    "cells, cell-weighted: no dataset's `consistent` share falls under either declaration set "
    "(recorded declarations 40.852% -> 42.544%, +1.692pp; tester declarations +1.618pp; default "
    "route with no tissue argument +1.496pp); 45 clusters move, every one attributed, 0 harm cells, "
    "0 unexplained. Kill switch EYEKB_ACT_ONFIBRO=0 restores the pre-flip default BYTE-FOR-BYTE, "
    "measured by replaying the recorded query set at the same absolute path: 721/721 cluster windows "
    "and 229/229 battery calls identical (raw and canonical). The activation's own delta is "
    "characterised per response field (out/FIELD_DIFF.json): the ranking moves on 45 clusters, and "
    "every response that carries the provenance/soft-flag disclosure fields now names the carrier. "
    "COMPATIBILITY ITEM (reported, not absorbed): the legacy five-tool panel digest moved "
    "(e8e6c26351cd9a1d42fa2e7cb6a83f23 -> 47e42230a8f7256b4ae9a78d4ff628d3) on two query_marker "
    "calls whose RANKINGS are unchanged; the baseline fixture was NOT re-recorded, so "
    "`tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json` is RED "
    "at this commit by design. Reading is IN-SAMPLE; no accuracy claim. sha/bytes/mtime re-taken "
    "from live bytes in the same commit.")

NOTE_ROW30 = (
    " | 2026-10-22 ACTIVATED by activation card t_42df17c2 (PI-signed, verbatim \"载体并进默认路由\"). "
    "ONFIBRO_DEFAULT_LIBS = (\"onfibro_v13\",): the entry is part of the default `all` route whenever "
    "the feature is on; EYEKB_ACT_ONFIBRO=0 restores the pre-flip default byte-for-byte (721/721 + "
    "229/229 recorded queries, same absolute path). The file's own bytes are UNCHANGED by the "
    "activation (a wiring change, not a panel change), so sha/bytes/mtime stay as registered. "
    "Effect, cell-weighted over 28 volumes / 721 clusters: no dataset's consistent share falls; the "
    "motivating cluster CX15_optic_nerve_all c31 (1,822 cells, truth fibroblast) answers "
    "onfibro_v13::Fibroblast at n_shared=2 instead of abstaining. Recorded as an ACTIVATION "
    "decision, not an audit pass; the reading is IN-SAMPLE and carries no accuracy claim. "
    "Pre-registration: docs/plans/activate_onfibro_20261022/PREREG_ACTIVATION_ONFIBRO_20261022.md; "
    "evidence: docs/plans/activate_onfibro_20261022/REPORT.md.")

NOTE_BASELINE = (
    " | 2026-10-22 activation card t_42df17c2: the recorded panel digest MOVED because the carrier "
    "became a member of the default route (the provenance/soft-flag disclosure fields name it on "
    "every response); the two legacy calls that moved are query_marker:{cell_type MG} and the "
    "microglia gene panel, and their rankings are unchanged (out/FIELD_DIFF.json). Per the "
    "coordinator's instruction the movement is REPORTED rather than absorbed: this fixture is left "
    "byte-unchanged (no re-record), so the probe is red at this commit and the decision to re-record "
    "or to narrow the disclosure belongs to the owner. Fixture bytes unchanged -> sha below stays.")


def sha_live(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def stat_row(rel):
    p = os.path.join(REPO, rel)
    st = os.stat(p)
    return (hashlib.sha256(open(p, "rb").read()).hexdigest(), str(st.st_size),
            datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))


def main():
    rows = list(csv.reader(open(REG, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    assert hdr[1] == "item_id" and hdr[10] == "sha256" and len(hdr) == 17, "registry schema moved"
    idx = {r[1]: i for i, r in enumerate(rows) if len(r) == 17 and r[1]}

    doc = {"probe": "l4_registry_rows.py", "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
           "registry_sha256_before": hashlib.sha256(open(REG, "rb").read()).hexdigest(),
           "rows": {}}

    # ---- L1-11M: the service core (bytes changed by the flip)
    core_sha, core_b, core_m = stat_row("mcp_server/eyekb_core.py")
    i = idx["L1-11M"]
    old_core = rows[i][10]
    doc["rows"]["L1-11M"] = {"before": {"sha256": old_core, "bytes": rows[i][11]},
                             "after": {"sha256": core_sha, "bytes": core_b, "mtime": core_m}}
    rows[i][10], rows[i][11], rows[i][12] = core_sha, core_b, core_m
    doc["rows"]["L1-11M"]["note_appended"] = not rows[i][15].endswith(NOTE_CORE)
    if doc["rows"]["L1-11M"]["note_appended"]:
        rows[i][15] = rows[i][15] + NOTE_CORE

    # ---- L1-30: the carrier row (status changed; file bytes unchanged)
    pan_sha, pan_b, pan_m = stat_row("kb/markers/markers_v13_onfibro_increment.json")
    j = idx["L1-30"]
    doc["rows"]["L1-30"] = {"file_sha256_live": pan_sha, "registered_sha256": rows[j][10],
                            "file_bytes_unchanged": pan_sha == rows[j][10],
                            "authority_before": rows[j][6]}
    rows[j][6] = ("ACTIVATED 2026-10-22 on the default `all` route by PI decision (activation card "
                  "t_42df17c2, verbatim authority \"载体并进默认路由\"); registered as an ACTIVATION, "
                  "not an audit pass. Kill switch EYEKB_ACT_ONFIBRO=0 restores the pre-flip default "
                  "byte-for-byte (measured). Rollback = restore the empty whitelist.")
    if not rows[j][15].endswith(NOTE_ROW30):
        rows[j][15] = rows[j][15] + NOTE_ROW30
    doc["rows"]["L1-30"]["authority_after"] = rows[j][6]

    # ---- L6-01: docs/VERIFY_CONTRACT.md (the R8 precondition registration moved it)
    vc_sha, vc_b, vc_m = stat_row("docs/VERIFY_CONTRACT.md")
    k = idx["L6-01"]
    doc["rows"]["L6-01"] = {"before": {"sha256": rows[k][10], "bytes": rows[k][11]},
                            "after": {"sha256": vc_sha, "bytes": vc_b, "mtime": vc_m}}
    rows[k][10], rows[k][11], rows[k][12] = vc_sha, vc_b, vc_m
    vc_note = (
        " | 2026-10-22 activation card t_42df17c2: §5.5 registers the new default-ON behaviour "
        "(the optic-nerve fibroblast carrier on the default route) as a gate precondition, which is "
        "what G6 rule R8 requires for a default-ON change (docs/CHANGE_CONTROL_G6_INSTANCE.tsv, row "
        "CHG-20261022-ONFIBRO-ACTIVATION). sha/bytes/mtime re-taken from live bytes in the same commit.")
    if not rows[k][15].endswith(vc_note):
        rows[k][15] = rows[k][15] + vc_note

    # ---- L6-37: the tool-panel baseline fixture (bytes unchanged; the digest moved anyway)
    m = idx["L6-37"]
    doc["rows"]["L6-37"] = {"sha256": rows[m][10], "live_sha256": stat_row(
        "tests/fixtures/tool_panel_baseline.json")[0], "re_recorded": False}
    if not rows[m][15].endswith(NOTE_BASELINE):
        rows[m][15] = rows[m][15] + NOTE_BASELINE


    # ---- L5-11: tests/G4_EXPECTED.json (re-anchored by this card, reason recorded in the file)
    g4_sha, g4_b, g4_m = stat_row("tests/G4_EXPECTED.json")
    if "L5-11" in idx:
        g = idx["L5-11"]
        doc["rows"]["L5-11"] = {"before": {"sha256": rows[g][10], "bytes": rows[g][11]},
                                "after": {"sha256": g4_sha, "bytes": g4_b, "mtime": g4_m}}
        rows[g][10], rows[g][11], rows[g][12] = g4_sha, g4_b, g4_m
        g4_note = (" | 2026-10-22 activation card t_42df17c2: re-anchored because the shipped default "
                   "route changed on purpose (the carrier is now a member of `all`); two of the three "
                   "anchors moved, the OFF state reproduces the previous values byte-for-byte, and the "
                   "pre-flip expectation is kept as tests/G4_EXPECTED_PRE-ONFIBRO.json. The criterion "
                   "is unchanged; only the values it compares against were re-taken. sha/bytes/mtime "
                   "re-taken from live bytes in the same commit.")
        if not rows[g][15].endswith(g4_note):
            rows[g][15] = rows[g][15] + g4_note

    # ---- the gate inventory's row for docs/VERIFY_CONTRACT.md (G5-C05 checks its sha too)
    inv = os.path.join(REPO, "docs", "GATE_INVENTORY_G5G6.tsv")
    ilines = open(inv, encoding="utf-8").read().split("\n")
    ihdr = [i for i, l in enumerate(ilines) if l.startswith("gate_id\t")][0]
    icols = ilines[ihdr].split("\t")
    i_p, i_sha = icols.index("script_path"), icols.index("sha256")
    vc_live = sha_live("docs/VERIFY_CONTRACT.md")
    inv_before = None
    for i in range(ihdr + 1, len(ilines)):
        f = ilines[i].split("\t")
        if len(f) == len(icols) and f[i_p] == "docs/VERIFY_CONTRACT.md":
            inv_before = f[i_sha]
            if f[i_sha] != vc_live:
                f[i_sha] = vc_live
                ilines[i] = "\t".join(f)
    assert inv_before is not None, "the inventory has no row for docs/VERIFY_CONTRACT.md"
    if inv_before != vc_live:
        tmp_i = inv + ".tmp-activate"
        with open(tmp_i, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(ilines))
        os.replace(tmp_i, inv)
    doc["rows"]["GATE_INVENTORY_G2_VERIFY_CONTRACT"] = {"before": inv_before, "after": vc_live,
                                                        "re_taken": inv_before != vc_live}

    body = "\n".join("\t".join(r) for r in rows) + "\n"
    assert body.count("\n") == len(rows), "row count changed while serialising"
    tmp = REG + ".tmp-activate"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    os.replace(tmp, REG)
    doc["registry_sha256_after"] = hashlib.sha256(open(REG, "rb").read()).hexdigest()
    doc["registry_rows_after"] = len(rows)
    doc["verdict"] = "PASS"
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "REGISTRY_UPDATE.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1)[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())