#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step R1 — re-take the registry rows the change touches, from live bytes.

The registry's own rule (VERIFY_CONTRACT §5, and every prior row that says "sha/bytes/mtime re-taken
from live bytes in the same commit") is that a registered artefact's byte columns are re-taken by the
commit that changes it. Four rows are touched here:

  L1-11M  mcp_server/eyekb_core.py            (behaviour: the stage literal is resolved, not guessed)
  L6-06   README.md                           (documentation: the table + the paragraph)
  L6-36   tests/probe_tool_panel_identity.py  (the probe now spells the documented signatures)
  L6-37   tests/fixtures/tool_panel_baseline.json (deliberate re-record; argued in the note)

Nothing else about the rows is touched: layer, item_id, name, category, path, version, authority,
change_gate, freeze_gate, regression_gate, state, surface all keep their bytes; the note column gains
one appended sentence saying what changed and who changed it.

Usage: <py> reg_retake.py [--registry docs/W3_PIPELINE_REGISTRY.tsv] [--write]
Without --write it only prints the readout.
"""
import argparse
import hashlib
import pathlib
import time

RETAKES = {
    "L1-11M": ("mcp_server/eyekb_core.py",
               "2026-10-22 shipped-surface card t_19831068: development_stage is resolved instead of "
               "guessed (an unrecognised literal -- organoid included -- reaches the unknown tier and "
               "carries a stage_literal block; no literal can fall through to the adult baseline). "
               "Behaviour is unchanged for every documented literal: the twelve-call panel is "
               "byte-identical with no stage literal supplied. sha/bytes/mtime re-taken in the same commit."),
    "L6-06": ("README.md",
              "2026-10-22 shipped-surface card t_19831068: the exact-signature table and a paragraph state "
              "the resolved-literal rule (which values reach which tier, and that an unrecognised value is "
              "answered as unknown with a stage_literal block). sha/bytes/mtime re-taken in the same commit."),
    "L6-36": ("tests/probe_tool_panel_identity.py",
              "2026-10-22 shipped-surface card t_19831068: the panel now spells the documented signatures "
              "(scope, a string detail, the required cell_type), a refused call is a FAILURE instead of an "
              "anchor, and the run's interpreter provenance is recorded and compared as an advisory. "
              "sha/bytes/mtime re-taken in the same commit."),
    "L6-37": ("tests/fixtures/tool_panel_baseline.json",
              "2026-10-22 shipped-surface card t_19831068: deliberate re-record, argued not silently green-ed. "
              "The old recording was not reproducible on this machine for two separate measured reasons -- "
              "four of its twelve calls were refused on arguments the tool never accepted (their text embeds "
              "the validator's own version, so it cannot be an anchor), and one answer had genuinely moved "
              "before this card started (explain_annotation 'Mueller cell', citations[].tissues populated in "
              "c4d04d9, never re-recorded). Both are attributed call by call in "
              "docs/plans/shipped_surface_20261022/REPORT.md. Re-recorded with the documented spellings, no "
              "refusals, plus the interpreter provenance block. sha/bytes/mtime re-taken in the same commit."),
}


def sha256_of(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="docs/W3_PIPELINE_REGISTRY.tsv")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    reg = pathlib.Path(a.registry)
    raw = reg.read_text(encoding="utf-8")
    lines = raw.split("\n")
    hdr = lines[0].split("\t")
    if len(hdr) != 17:
        raise SystemExit(f"unexpected header width {len(hdr)}")
    i_sha, i_bytes, i_mtime, i_note, i_id = 10, 11, 12, 15, 1

    seen, out = {}, []
    for ln in lines:
        if not ln.strip():
            out.append(ln)
            continue
        f = ln.split("\t")
        if len(f) != 17 or f[i_id] not in RETAKES:
            out.append(ln)
            continue
        item_id = f[i_id]
        path, note = RETAKES[item_id]
        if f[4] != path:
            raise SystemExit(f"{item_id}: registry path {f[4]!r} != expected {path!r}")
        p = pathlib.Path(path)
        if not p.is_file():
            raise SystemExit(f"{item_id}: {path} not on disk")
        new_sha, new_bytes = sha256_of(p), str(p.stat().st_size)
        new_mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime))
        seen[item_id] = (f[i_sha][:16], new_sha[:16], f[i_bytes], new_bytes, f[i_mtime], new_mtime)
        if note not in f[i_note]:
            f[i_note] = (f[i_note] + " | " + note).strip(" |")
        f[i_sha], f[i_bytes], f[i_mtime] = new_sha, new_bytes, new_mtime
        out.append("\t".join(f))

    if set(seen) != set(RETAKES):
        raise SystemExit(f"rows not all found: {sorted(set(RETAKES) - set(seen))}")

    print(f"{'item_id':<8} {'sha before':<16} {'sha after':<16} {'bytes before':>12} {'bytes after':>11}  mtime")
    for k in sorted(seen):
        b_sha, a_sha, b_by, a_by, b_mt, a_mt = seen[k]
        print(f"{k:<8} {b_sha:<16} {a_sha:<16} {b_by:>12} {a_by:>11}  {b_mt} -> {a_mt}")

    new_raw = "\n".join(out)
    if a.write:
        if new_raw == raw:
            print("no byte change (already re-taken)")
        else:
            reg.write_text(new_raw, encoding="utf-8")
            print(f"wrote {reg}  sha256={sha256_of(reg)}  bytes={reg.stat().st_size}")
    else:
        print("(read-only run; pass --write to update)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())