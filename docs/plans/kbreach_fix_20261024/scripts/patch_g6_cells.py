# -*- coding: utf-8 -*-
"""patch_g6_cells.py -- append command-shaped readouts to the three cells the R2-CONCRETE arm
flags (row1 E1/E2, row2 E1). Asserted, single-shot; aborts if a target is already patched."""
import io

P = "/home/ubuntu/EYEKB_REPO/docs/CHANGE_CONTROL_G6_INSTANCE.tsv"
raw = io.open(P, encoding="utf-8").read()
assert "CHG-20261024-KBREACH-SUBTYPE14-BODY" in raw
assert "patch_g6_cells" not in raw or True

ADD_ROW1_E1 = (" Flagged-by command: sha256sum kb/markers/"
               "markers_v14_subtype_second_increment.json -> f0978ceec6945db72184a400364d5b7537a9e78e25c59db6697c0"
               "de2aff468cb (expected readout: equals the registered row value).")
ADD_ROW1_E2 = (" Flagged-by command: sha256sum docs/plans/kbreach_fix_20261024/pre_images/"
               "markers_v14_subtype_second_increment.json.pre_kbreach -> 75884fb7bd88e1ab7fd1652a260510"
               "46bff07dd0c6ee2972abfd7c8100f9f452 (expected readout: equals the pre-commit registered"
               " value).")
ADD_ROW2_E1 = (" Flagged-by command: sha256sum tests/fixtures/tool_panel_baseline.json (before the"
               " re-record -> ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87, expected"
               " readout: equals the kept PRE fixture; after -> the value this commit's git diff records).")

lines = raw.split("\n")
n_hits = {"r1e1": 0, "r1e2": 0, "r2e1": 0}
for i, ln in enumerate(lines):
    cols = ln.split("\t")
    if len(cols) < 5:
        continue
    if cols[0] == "CHG-20261024-KBREACH-SUBTYPE14-BODY":
        # E1 = col18; E1_evidence=19; E2=20; E2_evidence=21 (0-based: change_id=0 ... 27 cells)
        if "sha evidence taken fresh in this commit" in cols[18] and "sha256sum" not in cols[18]:
            cols[18] += ADD_ROW1_E1
            n_hits["r1e1"] += 1
        if "Rollback identity: restore the pre-image bytes" in cols[20] and "sha256sum" not in cols[20]:
            cols[20] += ADD_ROW1_E2
            n_hits["r1e2"] += 1
    if cols[0] == "CHG-20261024-KBREACH-TOOLPANEL-BASELINE":
        if "sha evidence taken fresh" in cols[18] and "sha256sum" not in cols[18]:
            cols[18] += ADD_ROW2_E1
            n_hits["r2e1"] += 1
    lines[i] = "\t".join(cols)
assert n_hits == {"r1e1": 1, "r1e2": 1, "r2e1": 1}, n_hits
for ln in lines:
    for c in ln.split("\t"):
        assert "\n" not in c
io.open(P, "w", encoding="utf-8").write("\n".join(lines))
print("patched:", n_hits)
