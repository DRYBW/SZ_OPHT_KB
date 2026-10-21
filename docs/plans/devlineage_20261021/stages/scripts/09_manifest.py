#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 8 — MANIFEST.sha256 over the delivered bytes.

Deliberately excluded, each with the reason written into the manifest as a `#` comment line
(`sha256sum -c` ignores comment lines, so the exclusions stay visible without breaking the check):

  * MANIFEST.sha256 itself — a record cannot contain its own hash;
  * logs/*.log — run logs; any re-run rewrites them, so hashing them would make the manifest fail
    for a reason that has nothing to do with the delivered artefacts;
  * out/GATE_READOUT.md, out/GATE_READOUT.json, out/STAGE_LITERAL_SURFACE.tsv — rewritten by the
    gate/verification step, i.e. by the one command a reviewer is expected to re-run. Their
    sha256 at delivery time is recorded in MANIFEST_SCOPE_NOTE.md instead.

Everything else — every table, every raw response, every script, every report — is hashed.
"""
import hashlib
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_FILES = {"MANIFEST.sha256"}
DERIVED = {"out/GATE_READOUT.md", "out/GATE_READOUT.json", "out/STAGE_LITERAL_SURFACE.tsv"}
MANIFEST = HERE / "MANIFEST.sha256"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    files = []
    for p in sorted(HERE.rglob("*")):
        if not p.is_file() or any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        rel = str(p.relative_to(HERE))
        if rel in EXCLUDE_FILES or rel.startswith("logs/") or rel in DERIVED:
            continue
        files.append((rel, sha(p)))

    derived_shas = {d: (sha(HERE / d) if (HERE / d).is_file() else "") for d in sorted(DERIVED)}
    note = ["# MANIFEST scope note — V3 stage axis (card t_aa1b7f12)", "",
            f"# covered files: {len(files)}", "",
            "# Excluded from the hash list, with the reason:",
            "#   MANIFEST.sha256                a record cannot contain its own hash",
            "#   logs/*.log                     rewritten by any re-run; hashing them would fail the",
            "#                                  check for reasons unrelated to the delivered artefacts",
            "#   out/GATE_READOUT.md            rewritten by the gate/verification step (the one command",
            "#   out/GATE_READOUT.json          a reviewer is expected to re-run)",
            "#   out/STAGE_LITERAL_SURFACE.tsv  same reason",
            "#",
            "# sha256 of the excluded derived files at delivery time:",
            ]
    for k, v in derived_shas.items():
        note.append(f"#   {k}  {v}")
    note += ["#",
             "# Verification:  cd <this directory> && sha256sum -c MANIFEST.sha256",
             "# Expected: every line 'OK', exit code 0.",
             ""]
    (HERE / "MANIFEST_SCOPE_NOTE.md").write_text("\n".join(note), encoding="utf-8")

    lines = ["# " + l for l in note if l.startswith("# ")] + [""]
    lines += [f"{h}  {rel}" for rel, h in files]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")

    res = subprocess.run(["sha256sum", "-c", "MANIFEST.sha256"], cwd=HERE, capture_output=True, text=True)
    ok = sum(1 for l in res.stdout.splitlines() if l.endswith(": OK"))
    verified = sum(1 for l in res.stdout.splitlines() if ": " in l)
    print(f"manifest: {len(files)} files hashed, verified {ok}/{verified}, rc={res.returncode}")
    if res.returncode != 0:
        print(res.stdout[-2000:])
        print(res.stderr[-2000:])


if __name__ == "__main__":
    main()