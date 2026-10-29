#!/usr/bin/env python
"""Evaluate the pre-registered criteria of the default-tier card against the three probe runs.

Reads out/BEFORE.json, out/AFTER.json, out/AFTER_ENV_FULL.json and prints one row per criterion
with the readings that decide it. Exits non-zero if any criterion fails, so the result can be used
as a gate rather than as prose.

Usage: python verify_default_tier.py [--dir .]
"""
import argparse
import json
import os
import sys

DEFAULTS = ("index_default", "tissue_default", "comp_default", "comp_mouse_default")


def load(path):
    with open(path) as fh:
        return json.load(fh)["cases"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()

    b = load(os.path.join(args.dir, "out", "BEFORE.json"))
    a = load(os.path.join(args.dir, "out", "AFTER.json"))
    e = load(os.path.join(args.dir, "out", "AFTER_ENV_FULL.json"))

    rows = []

    def add(cid, ok, detail):
        rows.append((cid, "PASS" if ok else "FAIL", detail))

    # C1 — explicit heavy tier is a real escape hatch
    heavy = ("index_detail_full", "tissue_detail_full", "comp_detail_full")
    same = [k for k in heavy if a[k]["md5"] == b[k]["md5"]]
    add("C1", len(same) == len(heavy),
        f"{len(same)}/{len(heavy)} heavy-tier calls byte-identical "
        f"({', '.join(same) if same else 'none'})")

    # C2 — the legacy argument still reaches the heavy tier
    ok = a["index_summary_false"]["md5"] == b["index_default"]["md5"]
    add("C2", ok,
        f"summary=False after {a['index_summary_false']['md5'][:8]} vs old default "
        f"{b['index_default']['md5'][:8]}")

    # C3a / C3b — the new default is substantially lighter (amendment 1 replaced the absolute
    # thresholds with ratios, because the light view grows with the catalogue)
    idx_ratio = b["index_default"]["chars"] / a["index_default"]["chars"]
    add("C3a", idx_ratio >= 20.0,
        f"index {b['index_default']['chars']} -> {a['index_default']['chars']} chars "
        f"({idx_ratio:.1f}x, need >=20x)")
    comp_full_after = a["comp_detail_full"]["chars"]
    comp_ratio = comp_full_after / a["comp_default"]["chars"]
    add("C3b", comp_ratio >= 3.0,
        f"composition {comp_full_after} -> {a['comp_default']['chars']} chars "
        f"({comp_ratio:.2f}x, need >=3x)")

    # C4 — one environment variable restores the old default everywhere
    restored = [k for k in DEFAULTS if e[k]["md5"] == b[k]["md5"]]
    add("C4", len(restored) == len(DEFAULTS),
        f"EYEKB_DEFAULT_DETAIL=full restores {len(restored)}/{len(DEFAULTS)} defaults "
        f"({', '.join(restored)})")

    # C5 — a light tier may not drop per-row citations
    light = a["comp_default"]
    heavy_c = a["comp_detail_full"]
    if light.get("rows") is None:
        add("C5", False, "composition light view returned no rows to check")
    else:
        ok = light["row_citations"] == heavy_c["row_citations"] and light["rows"] == heavy_c["rows"]
        add("C5", ok,
            f"rows {light['rows']}/{heavy_c['rows']}, citations in rows "
            f"{light['row_citations']}/{heavy_c['row_citations']}")

    # C8 — nothing is silent: every default that came back smaller than before must carry both the
    # applied tier and the note that names the way back to the full answer
    silent = []
    for k in DEFAULTS:
        after, before = a[k], b[k]
        shrunk = after.get("chars", 0) < before.get("chars", 0)
        disclosed = bool(after.get("detail_applied")) and bool(after.get("has_detail_note"))
        if shrunk and not disclosed:
            silent.append(k)
    add("C8", not silent,
        f"shrunk defaults without a disclosure: {silent or 'none'}; "
        f"disclosed: " + ", ".join(k for k in DEFAULTS if a[k].get("detail_applied")))

    width = max(len(r[0]) for r in rows)
    fails = 0
    for cid, verdict, detail in rows:
        if verdict == "FAIL":
            fails += 1
        print(f"{cid:<{width}}  {verdict:<4}  {detail}")
    print(f"\n{len(rows) - fails}/{len(rows)} criteria pass")
    return 1 if fails else 0


sys.exit(main())