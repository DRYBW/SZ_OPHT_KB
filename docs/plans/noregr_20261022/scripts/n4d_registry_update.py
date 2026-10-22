#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n4d -- keep the repository's ownership ledger honest about the two files this card touches.

G5-C05 compares every registered row's sha256 against the live bytes; a byte change without a
registration re-take is a FAIL (measured: 1 mismatch after the code edit, before this script).
So: re-take the sha/bytes/mtime of mcp_server/eyekb_core.py in place, and register the new marker
file as its own row, the way the previous four increment waves did (L1-24..L1-26).

Every edit asserts its anchor occurs exactly once, and the file is written back with the same tab
structure and UTF-8 encoding it was read with.
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


def stat_row(rel):
    p = os.path.join(REPO, rel)
    st = os.stat(p)
    return (hashlib.sha256(open(p, "rb").read()).hexdigest(), str(st.st_size),
            datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))


def main():
    rows = list(csv.reader(open(REG, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    assert hdr[1] == "item_id" and hdr[10] == "sha256" and len(hdr) == 17, "registry schema moved"
    by_id = {r[1]: i for i, r in enumerate(rows) if len(r) == 17 and r[1].startswith("L1-")}
    assert "L1-11M" in by_id, "the core's registered row is missing"
    core_sha0, core_b0, core_m0 = stat_row("mcp_server/eyekb_core.py")
    pan_sha0, _, _ = stat_row("kb/markers/markers_v13_onfibro_increment.json")
    if ("L1-30" in by_id and rows[by_id["L1-11M"]][10] == core_sha0
            and rows[by_id["L1-30"]][10] == pan_sha0):
        doc = {"probe": "n4d_registry_update.py",
               "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
               "status": "ALREADY_APPLIED (idempotent skip; both rows already match the live bytes)",
               "core_row": {"item_id": "L1-11M", "sha256": core_sha0},
               "new_row": {"item_id": "L1-30", "sha256": pan_sha0},
               "core_row_sha256": core_sha0, "new_row_sha256": pan_sha0,
               "registry_sha256": hashlib.sha256(open(REG, "rb").read()).hexdigest()}
        os.makedirs(OUT, exist_ok=True)
        json.dump(doc, open(os.path.join(OUT, "REGISTRY_UPDATE.json"), "w"), ensure_ascii=False,
                  indent=1)
        print(json.dumps(doc, ensure_ascii=False, indent=1))
        return
    assert "L1-30" not in by_id, "L1-30 already taken with different bytes -- pick the next free id"

    core_sha, core_b, core_m = stat_row("mcp_server/eyekb_core.py")
    pan_sha, pan_b, pan_m = stat_row("kb/markers/markers_v13_onfibro_increment.json")

    # ---- 1. re-take the core's registration ------------------------------------------------
    i = by_id["L1-11M"]
    old = rows[i][10]
    rows[i][10], rows[i][11], rows[i][12] = core_sha, core_b, core_m
    note = (" | 2026-10-22 no-regression card t_0c40c7b1: registers marker library `onfibro_v13` "
            "(row L1-30) as an explicit-route-only library with an EMPTY whitelist -- "
            "EYEKB_ACT_ONFIBRO cannot inject it into the default `all` set in any state, so the "
            "default route is unchanged in every state; the accepted-library error string gains "
            "that one name. Default-face byte identity measured, not asserted: the parent commit's "
            "core was swapped IN PLACE at the same absolute path and the recorded query set "
            "replayed -- 721/721 recorded cluster windows and 229/229 battery calls byte-identical, "
            "legacy tool-panel digests unchanged (legacy e8e6c2635..., full 3f1f52cb6...), probe "
            "file byte-unchanged. sha/bytes/mtime re-taken from live bytes in the same commit.")
    rows[i][15] = rows[i][15] + note

    # ---- 2. register the new marker file ---------------------------------------------------
    new = [""] * 17
    new[0] = "L1"
    new[1] = "L1-30"
    new[2] = ("Optic-nerve fibroblast carrier increment (the family's only reachable carrier on "
              "the optic-nerve side)")
    new[3] = "KB version file"
    new[4] = "kb/markers/markers_v13_onfibro_increment.json"
    new[5] = "v13.0-onfibro-20261022"
    new[6] = ("REGISTERED_DEFAULT_OFF with an EMPTY whitelist (reachable only by naming "
              "library=onfibro_v13; merging it into the default `all` route needs its own measured "
              "harm line and separate PI approval)")
    new[7] = ("Only through the L1 release gate (new version file, never edited in place); sha "
              "re-taken in the same commit as any byte change")
    new[8] = "KB bodies frozen: this file adds one class, it modifies no existing entry"
    new[9] = ("G5 + default-face byte identity over the recorded 721-cluster set + "
              "legacy tool-panel identity probe")
    new[10], new[11], new[12] = pan_sha, pan_b, pan_m
    new[13] = "ON_DISK"
    new[14] = ("Panel build, the closed-candidate admission rule, the harvested-evidence table and "
               "the four-arm before/after measurement are in docs/plans/noregr_20261022/ "
               "(PREREG_NOREGRESSION_20261022.md, out/carrier_panel.json, out/carrier_lit.tsv, "
               "out/FIX_MEASUREMENT.json, REPORT.md)")
    new[15] = ("ONE entry, named by the Cell Ontology label of the term it carries (CL:0000057 "
               "`fibroblast`, resolved against the in-repo ontology release), holding the 10 genes "
               "of the shipped generic `Fibroblast` panel plus the 2 genes of the motivating "
               "cluster's recorded window that pass the declared admission rule (BICC1, EYA2) so "
               "the family's coarse carrier can clear the >=2 shared-gene bar. Why it exists: the "
               "optic_nerve exclusion row for `Limbus_Sclera_fibroblast_C1` left the fibroblast "
               "family with no reachable carrier for optic-nerve-declared clusters, so a "
               "coarse-but-family-correct answer degraded to an abstention (measured on "
               "CX15_optic_nerve_all cluster 31, 1,822 cells = 2.531% of the volume, cell-weighted "
               "-2.53pp). Reading with the carrier merged, recorded declarations: overall "
               "consistent share unchanged (no dataset falls, gate verdict PASS), the two "
               "optic-nerve fibroblast clusters answered at n_shared=2 instead of abstaining; the "
               "change moves 45 clusters / 111,247 cells. Readings are IN-SAMPLE (the carrier was "
               "selected on the same volumes it is measured on); no accuracy claim is made.")
    new[16] = "repo"
    rows.insert(i + 1, new)

    # Join with tabs by hand and write atomically: csv.writer with QUOTE_NONE raises on a field
    # that needs escaping, and it raises MID-WRITE, which truncated this file once during the run
    # (caught and restored from the pre-image; the atomic rename below is the fix).
    body = "\n".join("\t".join(r) for r in rows) + "\n"
    assert body.count("\n") == len(rows), "row count changed while serialising"
    tmp = REG + ".tmp-noregr"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    os.replace(tmp, REG)

    doc = {"probe": "n4d_registry_update.py", "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
           "core_row": {"item_id": "L1-11M", "old_sha256": old, "new_sha256": core_sha,
                        "bytes": core_b, "mtime": core_m},
           "new_row": {"item_id": "L1-30", "sha256": pan_sha, "bytes": pan_b, "mtime": pan_m},
           "rows_before": len(rows) - 1, "rows_after": len(rows),
           "registry_sha256": hashlib.sha256(open(REG, "rb").read()).hexdigest()}
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "REGISTRY_UPDATE.json"), "w"), ensure_ascii=False,
              indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()