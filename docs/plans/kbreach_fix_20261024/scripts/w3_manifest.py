# -*- coding: utf-8 -*-
"""w3_manifest.py -- re-freeze docs/W3_MANIFEST.sha256: update the registry line's sha from the
live bytes, append a dated header line, keep every other byte (as tested by re-runs of
sha256sum -c). Run LAST among the wave's byte changes (the identity record excludes this file)."""
import hashlib
import io
import os

REPO = "/home/ubuntu/EYEKB_REPO"
REG = os.path.join(REPO, "docs/W3_PIPELINE_REGISTRY.tsv")
MAN = os.path.join(REPO, "docs/W3_MANIFEST.sha256")

raw = io.open(MAN, encoding="utf-8").read()
lines = raw.split("\n")
assert "w3_manifest.py (t_c19cd667)" not in raw, "already frozen by this wave"

reg_sha = hashlib.sha256(io.open(REG, "rb").read()).hexdigest()
reg_bytes = os.path.getsize(REG)

out = []
replaced = 0
old_sha_seen = None
for ln in lines:
    if ln.endswith("W3_PIPELINE_REGISTRY.tsv") and not ln.startswith("#"):
        old_sha = ln.split("  ")[0]
        old_sha_seen = old_sha
        out.append("%s  W3_PIPELINE_REGISTRY.tsv" % reg_sha)
        replaced += 1
        print("registry line: %s -> %s" % (old_sha[:16], reg_sha[:16]))
    else:
        out.append(ln)
assert replaced == 1, replaced
header = ("# re-taken 2026-10-24 (card t_c19cd667, KB-REACH): the registry row L1-31 was re-taken in"
          " the same commit as the subtype_v14 body fix (sha256 %s -> %s, bytes %d); the other rows are"
          " unchanged. Frozen by scripts/w3_manifest.py (t_c19cd667)." % (old_sha_seen, reg_sha, reg_bytes))
assert out and out[0].startswith("# W3-NORM")
out.insert(1, header)
io.open(MAN, "w", encoding="utf-8").write("\n".join(out))

# verify with sha256sum -c from docs/
import subprocess
p = subprocess.run(["sha256sum", "-c", "W3_MANIFEST.sha256"], cwd=os.path.join(REPO, "docs"),
                   capture_output=True, text=True)
ok = [l for l in p.stdout.splitlines() if l.endswith(": OK")]
print("sha256sum -c:", p.returncode, "|", len(ok), "OK lines")
print(p.stdout.strip()[:400])
