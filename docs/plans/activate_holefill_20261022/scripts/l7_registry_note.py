#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l7 -- append this card's decision to the library's own registry row (no other registry surface moves).

Why only this row: this card COMMITS NO CORE CHANGE (the acceptance rule ruled NO-GO, so the library
stays default-off), so the service-core registration row (L1-11M) and the release identity are not
re-taken here -- they must be re-taken by whoever lands the working tree's core change. What this card
does owe the ledger is the state of the row it has been deciding about: L1-26 must say that the
activation was measured and refused, with the numbers, and that the library's registration line was
found missing and restored.

Raw-line surgery with `assert count == 1`: the row's file, sha and status columns are untouched, and
only the notes cell grows. Writes out/REGISTRY_NOTE.json.
"""
import hashlib
import json
import os
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs", "W3_PIPELINE_REGISTRY.tsv")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))

NOTE = (
    " | 2026-10-22 activation card t_be11fd4a (ACT-holefill, OWNER-SIGNED decision: the owner was shown "
    "a two-item checklist -- enable the hole-fill library / adopt the Cell-Ontology child-term "
    "candidates -- and answered \"ok\"): the activation was PRE-REGISTERED "
    "(docs/plans/activate_holefill_20261022/PREREG_ACTIVATION_HOLEFILL_20261022.md), measured with the "
    "reused no-regression harness over the recorded 28 volumes / 721 clusters / 1,495,330 cells, and "
    "RULED **NO-GO**: clause (a) failed (the cell-weighted `consistent` share falls overall "
    "-3.314pp and on datasets under all three readings), clause (b) failed (the aggregate "
    "`inconsistent` share RISES +12.725pp recorded declarations / +12.986pp tester declarations "
    "/ +13.063pp default route -- the failure mode named in the L1 precedent), while clause (c) passed "
    "(255 moved clusters, every one attributed, 92 of them the library's own takeovers, zero "
    "unexpected) and clause (d) passed (the OFF state replays the pre-flip default byte-for-byte: "
    "721/721 cluster windows and 229/229 battery calls, raw and canonical). Harm line: 117,006 cells "
    "moved down a grade (7.8%) and 34 clusters graded down. INSTRUMENT FINDING: the frozen KB->CL map "
    "carries the shipped class names only, so 16 of the library's 17 entry names (which are the Cell "
    "Ontology labels themselves) are unresolvable to the judge -- 70 of the 90 takeovers were graded "
    "`unmappable_pred`; re-read with a resolver that falls back to each entry's own cl_id, `same_cl` "
    "rises 39.707% -> 42.261% AND `truly_inconsistent` rises 21.024% -> 24.973% (46 of the 90 "
    "takeovers land on a cluster whose author class is a different class), so clause (b) fails under "
    "BOTH rulers and the refusal is not a labelling artefact. Not activated: this row's "
    "REGISTERED_DEFAULT_OFF state stands, and the library stays reachable by name only. DEFECT FOUND "
    "AND FIXED IN THE WORKING TREE, not committed by this card: commit 0312016 (card t_0c40c7b1) had "
    "dropped this library's MARKER_LIBS entry line as a side effect of appending the next registration "
    "(the append replaced the dictionary's closing line), so `library=\"holefill_v12\"` raised "
    "ValueError while this row claimed it was reachable by name; card t_be11fd4a restored the line and "
    "PROVED the restoration neutral on the shipped default route (721/721 recorded cluster windows and "
    "229/229 battery calls byte-identical, `golden_721` 721/721 both switch arms, explicit-route "
    "resolution restored: out/RESTORE.json). A CONCURRENT card (t_7509a1a2) made the same mistake on "
    "the same file in the same window and found/fixed it in its own script; the working tree's final state (sha be4e91c3...) "
    "carries this card's restoration plus that card's own registration, with this card's activation "
    "wiring removed and the default route byte-identical to the parent commit "
    "(out/COLLISION_AND_CLOSEOUT.json). Every number carries its command in the wave's REPORT.md; the "
    "reading is IN-SAMPLE and carries no accuracy claim.")


def main():
    raw = open(REG, encoding="utf-8").read()
    lines = raw.split("\n")
    hits = [i for i, l in enumerate(lines) if l.split("\t")[1:2] == ["L1-26"]]
    assert len(hits) == 1, "expected exactly one L1-26 row, found %d" % len(hits)
    i = hits[0]
    f = lines[i].split("\t")
    assert len(f) == 17, "row schema moved: %d fields" % len(f)
    doc = {"probe": "l7_registry_note.py", "registry": "docs/W3_PIPELINE_REGISTRY.tsv",
           "row": f[1],
           "registry_sha256_before": hashlib.sha256(raw.encode()).hexdigest(),
           "notes_chars_before": len(f[15]),
           "row_sha_untouched": f[10], "row_bytes_untouched": f[11],
           "note_appended": not f[15].endswith(NOTE)}
    if doc["note_appended"]:
        f[15] = f[15] + NOTE
        lines[i] = "\t".join(f)
        body = "\n".join(lines)
        assert body.count("\n") == raw.count("\n"), "line count changed while serialising"
        tmp = REG + ".tmp-activate"
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
        os.replace(tmp, REG)
    after = open(REG, encoding="utf-8").read()
    doc["registry_sha256_after"] = hashlib.sha256(after.encode()).hexdigest()
    doc["notes_chars_after"] = len(after.split("\n")[i].split("\t")[15])
    doc["only_one_line_changed"] = (
        sum(1 for a, b in zip(raw.split("\n"), after.split("\n")) if a != b) == 1)
    doc["verdict"] = "PASS" if doc["only_one_line_changed"] else "FAIL"
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "REGISTRY_NOTE.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in doc.items() if k != "note_appended"}, ensure_ascii=False)[:900])
    print("verdict:", doc["verdict"])
    return 0 if doc["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())