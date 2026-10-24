# -*- coding: utf-8 -*-
"""final_touches.py -- (1) append the L6-37 re-take to the toolpanel change-control row's M2 cell;
(2) re-freeze W3_MANIFEST.sha256 (idempotent: refresh the registry line, append a one-line header).
Verify-only output; aborts if a target is already patched."""
import hashlib
import io
import os
import subprocess

REPO = "/home/ubuntu/EYEKB_REPO"
G6 = os.path.join(REPO, "docs/CHANGE_CONTROL_G6_INSTANCE.tsv")
MAN = os.path.join(REPO, "docs/W3_MANIFEST.sha256")
REG = os.path.join(REPO, "docs/W3_PIPELINE_REGISTRY.tsv")
FIX = os.path.join(REPO, "tests/fixtures/tool_panel_baseline.json")

# (1) G6 row2 M2 cell
g6 = io.open(G6, encoding="utf-8").read().split("\n")
hit = 0
for i, ln in enumerate(g6):
    c = ln.split("\t")
    if len(c) > 15 and c[0] == "CHG-20261024-KBREACH-TOOLPANEL-BASELINE":
        if "registry row L6-37 re-taken" not in c[15]:
            c[15] += (" Also part of this row's surface: registry row L6-37 (the fixture's own "
                      "registration) re-taken from live bytes in the same commit; W3 manifest re-frozen "
                      "after it.")
            hit += 1
        g6[i] = "\t".join(c)
        break
assert hit == 1, hit
io.open(G6, "w", encoding="utf-8").write("\n".join(g6))
print("G6 row2 M2 patched")

# (2) W3 manifest re-freeze, second pass
raw = io.open(MAN, encoding="utf-8").read()
reg_sha = hashlib.sha256(io.open(REG, "rb").read()).hexdigest()
lines = raw.split("\n")
replaced = 0
for i, ln in enumerate(lines):
    if ln.endswith("W3_PIPELINE_REGISTRY.tsv") and not ln.startswith("#"):
        old = ln.split("  ")[0]
        if old != reg_sha:
            lines[i] = "%s  W3_PIPELINE_REGISTRY.tsv" % reg_sha
            replaced += 1
            print("registry line refreshed: %s -> %s" % (old[:16], reg_sha[:16]))
        break
assert replaced == 1, ("registry line already current" if replaced == 0 else replaced)
anchor = "# re-taken 2026-10-24 (card t_c19cd667, KB-REACH"
extra = None
for i, ln in enumerate(lines):
    if ln.startswith(anchor) and "second pass" in ln:
        extra = i
        break
if extra is None:
    insert_at = next(i for i, ln in enumerate(lines)
                     if ln.startswith(anchor) and "second pass" not in ln) + 1
    lines.insert(insert_at, anchor + ", second pass): registry row L6-37 was re-taken after the"
                              " tool-panel fixture re-record; both passes covered by"
                              " scripts/w3_manifest.py + scripts/final_touches.py (t_c19cd667).")
io.open(MAN, "w", encoding="utf-8").write("\n".join(lines))

p = subprocess.run(["sha256sum", "-c", "W3_MANIFEST.sha256"], cwd=os.path.join(REPO, "docs"),
                   capture_output=True, text=True)
oks = [l for l in p.stdout.splitlines() if l.endswith(": OK")]
print("sha256sum -c rc:", p.returncode, "| OK lines:", len(oks))
