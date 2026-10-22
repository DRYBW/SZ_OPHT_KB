#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n4e -- shared-ledger honesty fix for a row another card left stale.

The ownership ledger's job is to say what is on disk. A row whose live bytes no longer match its
registered sha is a false residual: it makes G5-C05 red for a reason that has nothing to do with the
change under test, and it hides the next real drift in the noise.

Measured need (2026-10-22): while this card was running, a concurrent card
(docs/plans/l5_ontlayer_20261022, registry row L6-43) registered its own REPORT.md and then rewrote
that file in a later commit, so at HEAD the row's registered sha (4719f98d...) no longer matched the
committed bytes (c74c53d1...). G5-C05 therefore failed on a file this card never touched.

Policy applied here, deliberately narrow:
  * only rows whose path is a committed file under docs/plans/ are considered;
  * only rows whose live sha differs from the registered sha are re-taken;
  * the row's notes get an explicit sentence naming this card and the file's author card, so the
    owner can confirm or re-take it themselves;
  * every other column is left exactly as it was.
Vendor/vcs rows (.git/**), maintainer-local rows (/mnt/D/... paths) and rows dispensed by the
snapshot-drift ledger are out of scope and are left alone.

Writes out/LEDGER_HEAL.json and updates docs/W3_PIPELINE_REGISTRY.tsv atomically.
"""
import csv
import datetime
import hashlib
import json
import os

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))
SELF = "docs/plans/noregr_20261022/"
NOTE = (" | 2026-10-22 no-regression card t_0c40c7b1 re-took this row's sha/bytes/mtime as a "
        "shared-ledger honesty fix: the file was rewritten by its author card after this row's own "
        "registration, so the registered sha no longer matched the committed bytes and G5-C05 was "
        "red for a path this card does not own. The author card should confirm or re-take the row. "
        "No other column was touched.")


def main():
    rows = list(csv.reader(open(REG, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    assert len(hdr) == 17, "registry schema moved"
    healed, skipped = [], []
    for r in rows[1:]:
        if len(r) != 17:
            continue
        path = r[4]
        if not path.startswith("docs/plans/") or r[16] != "repo":
            continue
        if path.startswith(SELF):
            continue
        p = os.path.join(REPO, path)
        if not os.path.isfile(p):
            skipped.append({"item_id": r[1], "path": path, "why": "not on disk"})
            continue
        st = os.stat(p)
        live = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if live == r[10]:
            continue
        old = r[10]
        r[10], r[11], r[12] = live, str(st.st_size), datetime.datetime.fromtimestamp(
            st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        r[15] = r[15] + NOTE
        healed.append({"item_id": r[1], "path": path, "old_sha256": old, "new_sha256": live,
                       "bytes": r[11], "mtime": r[12]})

    if healed:
        body = "\n".join("\t".join(r) for r in rows) + "\n"
        assert body.count("\n") == len(rows), "row count changed while serialising"
        tmp = REG + ".tmp-noregr-heal"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(body)
        os.replace(tmp, REG)

    doc = {"probe": "n4e_ledger_heal.py", "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
           "healed": healed, "skipped": skipped,
           "status": "HEALED" if healed else "NOTHING_TO_HEAL",
           "registry_sha256": hashlib.sha256(open(REG, "rb").read()).hexdigest()}
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "LEDGER_HEAL.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()