#!/usr/bin/env python
"""Evaluate the pre-registered criteria of the page mid-tier card against the three probe runs.

Reads out/BEFORE.json, out/AFTER.json, out/AFTER_ENV_FULL.json. Prints one row per criterion with
the readings that decide it and exits non-zero if any fails, so the result is a gate, not prose.

The outline check recomputes every claimed number from the page text with the probe's own code; the
slice check is the md5 of a page rebuilt from its slices versus the same page fetched whole.
"""
import argparse
import json
import os
import sys

THRESHOLD = 20000


def load(path):
    with open(path) as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    d = args.dir

    b, a, e = (load(os.path.join(d, "out", f)) for f in
               ("BEFORE.json", "AFTER.json", "AFTER_ENV_FULL.json"))

    rows = []

    def add(cid, ok, detail):
        rows.append((cid, "PASS" if ok else "FAIL", detail))

    # C1 — explicit full tier unchanged
    heavy = ("cornea_full", "vascular_full", "index_full")
    same = [k for k in heavy if a["single"][k]["md5"] == b["single"][k]["md5"]]
    add("C1", len(same) == len(heavy),
        f"{len(same)}/{len(heavy)} full-tier responses byte-identical "
        f"({', '.join(same)})")

    # C2 — the outline tells the truth, re-derived independently
    checked, mismatches = 0, []
    for key, page in a["pages"].items():
        o, r = page.get("outline"), page.get("recomputed")
        if not isinstance(o, dict) or not isinstance(r, dict):
            continue
        checked += 1
        for field in ("chars", "lines", "front_matter", "sections", "papers"):
            if o.get(field) != r.get(field):
                mismatches.append(f"{key}.{field}")
    add("C2", checked >= 6 and not mismatches,
        f"{checked} pages re-derived, {len(mismatches)} field mismatches"
        + (f": {mismatches[:4]}" if mismatches else ""))

    # C3 — slicing loses nothing
    walked = [k for k, p in a["pages"].items() if p.get("rebuild_identical") is True]
    broken = [k for k, p in a["pages"].items() if p.get("rebuild_identical") is not True]
    add("C3", len(walked) >= 6 and not broken,
        f"{len(walked)}/{len(a['pages'])} pages rebuilt byte-identically from slices"
        + (f"; broken: {broken[:3]}" if broken else ""))

    # C4 — the new views are small
    biggest_page = max(a["pages"].items(), key=lambda kv: kv[1].get("full_chars", 0))
    outline_chars = biggest_page[1].get("outline_chars", 10 ** 9)
    max_slice = max(p.get("slice_default_chars", 0) for p in a["pages"].values())
    max_outline_any = max(p.get("outline_chars", 0) for p in a["pages"].values())
    add("C4", outline_chars <= 2500 and max_slice <= 25000,
        f"largest page ({biggest_page[0]}, {biggest_page[1].get('full_chars')} chars) outline "
        f"{outline_chars} chars; largest default slice {max_slice} chars; "
        f"[supplementary] largest outline anywhere: {max_outline_any} chars")

    # C5 — no page left unreachable
    n_listed = a.get("n_listed", 0)
    reachable = [k for k, p in a["pages"].items()
                 if p.get("full_chars") and p.get("default_chars") and p.get("slice_default_chars")]
    add("C5", n_listed == len(a["pages"]) == len(reachable),
        f"service lists {n_listed}, probed {len(a['pages'])}, fully reachable {len(reachable)}")

    # C6 — the default is a rule; and one variable restores the old default everywhere
    wrong = []
    for key, p in a["pages"].items():
        if not p.get("full_chars"):
            continue
        big = p["full_chars"] > THRESHOLD
        applied = p.get("default_applied")
        if big and applied != "outline":
            wrong.append(f"{key}=should be outline, got {applied}")
        if not big and applied:
            wrong.append(f"{key}=should stay full, got {applied}")
    env_restored = [k for k in a["pages"] if e["pages"].get(k, {}).get("default_chars")
                    == b["pages"].get(k, {}).get("default_chars")]
    add("C6", not wrong and len(env_restored) == len(b["pages"]),
        f"threshold rule violations: {wrong or 'none'}; EYEKB_DEFAULT_DETAIL=full restores "
        f"{len(env_restored)}/{len(b['pages'])} pages to their pre-change default bytes")

    # C8 — nothing is silent
    silent = [k for k, p in a["pages"].items()
              if p.get("default_applied") == "outline" and not p.get("default_note")]
    add("C8", not silent,
        f"implicit outlines without a disclosure: {silent or 'none'}")

    width = max(len(r[0]) for r in rows)
    fails = 0
    for cid, verdict, detail in rows:
        if verdict == "FAIL":
            fails += 1
        print(f"{cid:<{width}}  {verdict:<4}  {detail}")
    print(f"\n{len(rows) - fails}/{len(rows)} criteria pass (as pre-registered)")

    # ---------------------------------------------------------------------------------------
    # The two pre-registered criteria that missed, restated as ratios. Printed AFTER the strict
    # verdict and clearly separated: these are the readings the misses are made of, not a way to
    # turn them into passes. See POST_MEASUREMENT_RECONCILIATION.md.
    # ---------------------------------------------------------------------------------------
    defaulted = {k: p for k, p in a["pages"].items()
                 if p.get("default_applied") == "outline" and p.get("full_chars")}
    print("\nrestated readings (not verdicts):")
    if defaulted:
        worst = max(defaulted.items(),
                    key=lambda kv: kv[1]["outline_chars"] / kv[1]["full_chars"])
        print(f"  C4 ratio form: {len(defaulted)} pages default to outline; smallest saving "
              f"{worst[0]} {worst[1]['full_chars']} -> {worst[1]['outline_chars']} chars "
              f"({worst[1]['full_chars'] / worst[1]['outline_chars']:.1f}x); largest saving "
              f"{max(defaulted.values(), key=lambda p: p['full_chars'] / p['outline_chars'])['full_chars']}"
              f" chars page -> "
              f"{min(p['outline_chars'] for p in defaulted.values())} chars outline")
    non_index = [k for k in a["pages"] if not k.startswith("index:")]
    rule_ok = [k for k in non_index if a["pages"][k].get("default_applied")
               == ("outline" if a["pages"][k]["full_chars"] > THRESHOLD else None)]
    env_ok = [k for k in non_index
              if e["pages"].get(k, {}).get("default_chars") == b["pages"].get(k, {}).get("default_chars")]
    print(f"  C6 non-index form: threshold rule {len(rule_ok)}/{len(non_index)} pages, "
          f"environment revert {len(env_ok)}/{len(non_index)} pages; the index keeps the inventory "
          f"default (4,324 chars) and returns the 140,005-char text under EYEKB_DEFAULT_DETAIL=full, "
          f"which is VERIFY_CONTRACT 5.8's documented meaning of that variable")
    return 1 if fails else 0


sys.exit(main())