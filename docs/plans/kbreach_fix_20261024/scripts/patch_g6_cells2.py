# -*- coding: utf-8 -*-
"""patch_g6_cells2.py -- fix the flagged change-control cells, keyed by header cell NAMES.
Single-shot; every append asserted (count==1 per target); aborts on second run."""
import io

P = "/home/ubuntu/EYEKB_REPO/docs/CHANGE_CONTROL_G6_INSTANCE.tsv"
lines = io.open(P, encoding="utf-8").read().split("\n")
hdr_idx = None
for i, ln in enumerate(lines):
    c = ln.split("\t")
    if len(c) > 3 and c[0] == "change_id":
        hdr_idx = i
        hdr = c
        break
assert hdr_idx is not None
IX = {name: j for j, name in enumerate(hdr)}
assert IX["E1"] == 19 and IX["E2"] == 21 and IX["Q3"] == 7 and IX["Q4"] == 9 and IX["Q5"] == 11, IX

hits = {}


def append_to(cell_owner_rid, cellname, phrase):
    for i in range(hdr_idx + 1, len(lines)):
        cols = lines[i].split("\t")
        if len(cols) < 5:
            continue
        if cols[0] != cell_owner_rid:
            continue
        j = IX[cellname]
        assert phrase[:40] not in cols[j], "already patched: %s.%s" % (cell_owner_rid, cellname)
        cols[j] = cols[j] + phrase
        for x in cols:
            assert "\n" not in x
        lines[i] = "\t".join(cols)
        hits[(cell_owner_rid, cellname)] = hits.get((cell_owner_rid, cellname), 0) + 1


R1 = "CHG-20261024-KBREACH-SUBTYPE14-BODY"
R2 = "CHG-20261024-KBREACH-TOOLPANEL-BASELINE"

append_to(R1, "Q3", (" Negative term carried explicitly: rollback = restore the byte-exact pre-image "
                     "(sha-verified); the replay then reproduces the PRE digests; no switch state gains "
                     "access to the new block."))
append_to(R1, "Q4", (" Frozen-input anchor: the pre-fix bytes this fix starts from, "
                     "sha256 75884fb7bd88e1ab7fd1652a26051046bff07dd0c6ee2972abfd7c8100f9f452, were the "
                     "registered row value before this commit (kept verbatim in the pre-image)."))
append_to(R1, "E1", (" Readout command: sha256sum kb/markers/markers_v14_subtype_second_increment.json "
                     "-> f0978ceec6945db72184a400364d5b7537a9e78e25c59db6697c0de2aff468cb; expected: equals "
                     "the re-taken registry row value."))
append_to(R1, "E2", (" Readout command: sha256sum docs/plans/kbreach_fix_20261024/pre_images/"
                     "markers_v14_subtype_second_increment.json.pre_kbreach -> 75884fb7bd88e1ab7fd1652a2605"
                     "1046bff07dd0c6ee2972abfd7c8100f9f452; expected: equals the pre-commit registered value."))

append_to(R2, "Q3", (" Negative term carried explicitly: rollback = restore the PRE fixture bytes "
                     "(sha-verified); the probe then returns to its recorded RED state "
                     "(IDENTITY FAIL on exactly the two attributed calls, rc=1)."))
append_to(R2, "Q4", (" Frozen-input anchor: the PRE fixture bytes, "
                     "sha256 ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87, equal the "
                     "fixture as recorded at commit 435bb92 and are kept verbatim in the wave pre-image."))
append_to(R2, "Q5", (" No service switch participates in this row; the switch surface nearest the "
                     "drift is EYEKB_ACT_ONFIBRO (the activation whose provenance field the moved calls "
                     "now carry); rollback identity is byte-level: restoring the PRE fixture bytes "
                     "reproduces the recorded RED state exactly."))
append_to(R2, "E1", (" Readout command: sha256sum tests/fixtures/tool_panel_baseline.json; expected: "
                     "the after-value this commit's git diff records (before the re-record it read "
                     "ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87)."))

expect = {(R1, "Q3"): 1, (R1, "Q4"): 1, (R1, "E1"): 1, (R1, "E2"): 1,
          (R2, "Q3"): 1, (R2, "Q4"): 1, (R2, "Q5"): 1, (R2, "E1"): 1}
assert hits == expect, hits
io.open(P, "w", encoding="utf-8").write("\n".join(lines))
print("patched cells:", sorted(str((r, c)) for (r, c) in hits))
