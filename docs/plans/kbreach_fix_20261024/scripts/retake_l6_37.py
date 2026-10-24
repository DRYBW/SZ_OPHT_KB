# -*- coding: utf-8 -*-
"""retake_l6_37.py -- re-take registry row L6-37 (tool_panel_baseline.json) from live bytes:
sha256/bytes/mtime columns + a dated notes clause; verify only that line changed."""
import datetime
import hashlib
import io
import os

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs/W3_PIPELINE_REGISTRY.tsv")
FIX = os.path.join(REPO, "tests/fixtures/tool_panel_baseline.json")

st = os.stat(FIX)
sha_now = hashlib.sha256(io.open(FIX, "rb").read()).hexdigest()
bytes_now = st.st_size
mtime_now = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

lines = io.open(REG, encoding="utf-8").read().split("\n")
idx = None
for i, ln in enumerate(lines):
    c = ln.split("\t")
    if len(c) > 10 and c[1] == "L6-37":
        idx = i
        before = c
        break
assert idx is not None, "row L6-37 not found"
print("path col:", before[4] if len(before) > 4 else "?", "| registered sha:", before[10][:16],
      "bytes:", before[11])
assert before[10].startswith("ce641612"), before[10][:16]
NOTE = (" | 2026-10-24 card t_c19cd667 (KB-REACH, change-control row "
        "CHG-20261024-KBREACH-TOOLPANEL-BASELINE): the fixture was re-recorded in that commit because "
        "cards t_42df17c2 (onfibro_v13 default-route activation) had moved the two query_marker "
        "responses' provenance field only (files += onfibro_v13, conflicts += onfibro_v13::Fibroblast; "
        "rankings unchanged, per-call field diff in docs/plans/kbreach_fix_20261024/out/D2_FIELD_"
        "DIFF.json); the device's own instruction (re-record in the commit that owns the change + say "
        "so here) is now discharged. legacy_panel 47e42230a8f7256b4ae9a78d4ff628d3 == the post-"
        "activation digest t_42df17c2 recorded in row L1-11M notes; full_panel "
        "f97ff8ad2507f4d69a0e6e57406c2de1; PRE bytes kept at docs/plans/kbreach_fix_20261024/"
        "pre_images/tool_panel_baseline.json.pre_rerecord (sha256 ce6416126252663ff8be794fe9855"
        "00a284876c3d15b2420359656c1bb4afd87 == this row's previous value). sha/bytes/mtime re-taken "
        "from live bytes in the same commit.")
cols = list(before)
cols[10] = sha_now
cols[11] = str(bytes_now)
cols[12] = mtime_now
cols[14] = cols[14] + NOTE
for x in cols:
    assert "\t" not in x and "\n" not in x
lines[idx] = "\t".join(cols)
io.open(REG, "w", encoding="utf-8").write("\n".join(lines))
lines2 = io.open(REG, encoding="utf-8").read().split("\n")
diffs = [i for i in range(min(len(lines), len(lines2))) if lines2[i] != lines[i]]
print("changed lines:", diffs, "| new sha:", sha_now[:16], "bytes:", bytes_now, "mtime:", mtime_now)
assert diffs == [idx] or diffs == [], diffs
