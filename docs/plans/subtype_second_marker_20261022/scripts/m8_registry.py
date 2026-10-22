#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m8 -- keep the repository's ownership ledger honest about the two files this card touches.

G5 compares every registered row's sha256 against the live bytes, so a byte change without a
registration re-take is a FAIL.  Two rows are written:

  * `L1-11M` (mcp_server/eyekb_core.py) -- re-taken from the COMMITTED blob
    (out/COMMITTED_eyekb_core.py = the parent commit + this card's four registration edits), with an
    explicit note that the shared working tree simultaneously carried another card's in-flight
    activation, whose bytes are NOT part of this commit and whose own row the sibling card re-takes;
  * `L1-31` (kb/markers/markers_v14_subtype_second_increment.json) -- the new library, from live bytes.

Every edit asserts its anchor occurs exactly once, and the registry is written back through an atomic
rename (csv.writer with QUOTE_NONE raises mid-write on a field needing escaping and truncated this
file once in an earlier wave).

Writes out/REGISTRY_UPDATE.json.
"""
import csv
import datetime
import hashlib
import json
import os
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
LIB_REL = "kb/markers/markers_v14_subtype_second_increment.json"
CORE_REL = "mcp_server/eyekb_core.py"


def sha_of(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    rows = list(csv.reader(open(REG, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    assert hdr[1] == "item_id" and hdr[10] == "sha256" and len(hdr) == 17, "registry schema moved"
    by_id = {r[1]: i for i, r in enumerate(rows) if len(r) == 17 and r[1].startswith("L1-")}
    assert "L1-11M" in by_id, "the core's registered row is missing"
    nums = [int(k.split("-")[1]) for k in by_id if k.split("-")[1].isdigit()]
    new_id = "L1-%02d" % (max(nums) + 1)
    assert new_id not in by_id, "%s already taken" % new_id

    committed = os.path.join(OUT, "COMMITTED_eyekb_core.py")
    live = os.path.join(REPO, CORE_REL)
    lib = os.path.join(REPO, LIB_REL)
    blob_sha, blob_bytes = sha_of(committed), os.path.getsize(committed)
    live_sha = sha_of(live)
    lib_sha, lib_bytes = sha_of(lib), os.path.getsize(lib)
    lib_mtime = datetime.datetime.fromtimestamp(os.stat(lib).st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    live_mtime = datetime.datetime.fromtimestamp(os.stat(live).st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    dface = json.load(open(os.path.join(OUT, "DEFAULT_FACE.json"), encoding="utf-8"))
    fl = json.load(open(os.path.join(OUT, "FLIPS.json"), encoding="utf-8"))
    rob = json.load(open(os.path.join(OUT, "ROBUSTNESS.json"), encoding="utf-8"))
    panel = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_PANEL.json"), encoding="utf-8"))

    doc = {"probe": "m8_registry.py", "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
           "new_row": new_id, "committed_blob_sha256": blob_sha,
           "live_core_sha256_at_registration": live_sha,
           "live_core_carries_concurrent_edit": live_sha != blob_sha,
           "library_sha256": lib_sha, "library_bytes": lib_bytes}

    if new_id in by_id and rows[by_id[new_id]][10] == lib_sha and rows[by_id["L1-11M"]][10] == blob_sha:
        doc["status"] = "ALREADY_APPLIED (idempotent skip)"
        json.dump(doc, open(os.path.join(OUT, "REGISTRY_UPDATE.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(json.dumps(doc, ensure_ascii=False, indent=1))
        return

    i = by_id["L1-11M"]
    old_sha = rows[i][10]
    rows[i][10], rows[i][11], rows[i][12] = blob_sha, str(blob_bytes), live_mtime
    rows[i][15] = rows[i][15] + (
        " | 2026-10-22 card t_7509a1a2 (SUBTYPE-2M): registers marker library `subtype_v14` "
        "(row %s) as an explicit-route-only library with an EMPTY whitelist -- EYEKB_ACT_SUBTYPE "
        "cannot inject it into the default `all` set in any state; the accepted-library error string "
        "gains that one name. sha registered here is the COMMITTED blob (parent commit + this card's "
        "four edits, bytes=%d); at registration time the shared working tree simultaneously carried "
        "another card's in-flight activation (docs/plans/activate_holefill_20261022/, card t_be11fd4a) "
        "whose bytes are deliberately NOT part of this commit -- the live file's sha then was %s, and "
        "that card re-takes this row in its own commit. Default-face byte identity MEASURED, not "
        "asserted: parent blob vs committed blob imported side by side at the same directory and the "
        "default route replayed over %d calls (721 recorded cluster windows + the class/species "
        "battery) -- 0 differing calls, route composition identical, subtype_v14 absent from `all` in "
        "every switch state (out/DEFAULT_FACE.json)." % (new_id, blob_bytes, live_sha[:16],
                                                         dface["arms"]["n_calls_per_arm"]))

    new = [""] * 17
    new[0] = "L1"
    new[1] = new_id
    new[2] = ("Second-marker increment for the 26 one-gene-thick subtype panels of the frozen "
              "consensus-subtype wave")
    new[3] = "KB version file"
    new[4] = LIB_REL
    new[5] = "v14.0-subtype-second-marker-20261022"
    new[6] = ("REGISTERED_DEFAULT_OFF with an EMPTY whitelist (reachable only by naming "
              "library=subtype_v14; merging it into the default `all` route needs its own measured "
              "harm line and separate PI approval)")
    new[7] = ("Only through the L1 release gate (new version file, never edited in place); sha "
              "re-taken in the same commit as any byte change")
    new[8] = "KB bodies frozen: this file adds 16 subtype entries, it modifies no existing entry"
    new[9] = ("G5 + default-face byte identity over %d calls (parent blob vs committed blob at the "
              "same directory) + explicit route-composition check" % dface["arms"]["n_calls_per_arm"])
    new[10], new[11], new[12] = lib_sha, str(lib_bytes), lib_mtime
    new[13] = "ON_DISK"
    new[14] = ("Panel build, the literature mining passes (five, all on disk), the ruler re-run and "
               "the flip table are in plans/subtype_second_marker_20261022/ "
               "(PREREG_SUBTYPE_SECOND_MARKER_20261022.md + AMENDMENT_1..4, out/SUBTYPE_SECOND_MARKER_LIT.json, "
               "out/SUBTYPE_SECOND_MARKER_PANEL.json, out/FLIPS.json, out/ROBUSTNESS.json, REPORT.md)")
    new[15] = ("16 entries, one per in-scope literature-consensus retinal subtype, each named by the "
               "Cell Ontology label of the term it carries (resolved against the in-repo release "
               "2026-06-08; 16/16 resolve), holding the frozen panel PLUS at most 2 literature-sourced "
               "candidates selected by segment-level attribution against the in-repo literature corpus "
               "(no gene chosen on our own expression; every added gene carries its paper ids and its "
               "per-volume measurability inside the file). Measured effect: %d of the 26 in-scope rows "
               "flip not_separated -> separated (separated 12 -> 20 of 56), %d of them robust across two "
               "independently-derived attachment rules, %d rule-dependent; 0 out-of-scope rows moved. "
               "The reader is IN-SAMPLE (the panel was selected and measured on the same seven volumes); "
               "no accuracy claim is made, and no subtype enters any shipped vocabulary by this wave."
               % (fl["n_flips"], rob["n_robust"], rob["n_rule_dependent"]))
    new[16] = "repo"
    rows.insert(by_id["L1-11M"] + 1, new)

    body = "\n".join("\t".join(r) for r in rows) + "\n"
    assert body.count("\n") == len(rows), "row count changed while serialising"
    tmp = REG + ".tmp-subtype2m"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    os.replace(tmp, REG)

    doc.update({"core_row": {"item_id": "L1-11M", "old_sha256": old_sha, "new_sha256": blob_sha},
                "library_row": {"item_id": new_id, "sha256": lib_sha, "bytes": lib_bytes,
                                "mtime": lib_mtime},
                "rows_before": len(rows) - 1, "rows_after": len(rows),
                "registry_sha256": sha_of(REG),
                "n_entries": len(panel["panel_rows"]),
                "n_flips": fl["n_flips"], "n_robust": rob["n_robust"]})
    json.dump(doc, open(os.path.join(OUT, "REGISTRY_UPDATE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())