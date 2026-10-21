#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 5 — before/after table for the development_stage surface, with the negative column.

Reads two dumps produced by a1_dump_panel.py (one taken in a clean tree at the pre-change commit,
one taken in the working tree after the fix) and prints, per (species, tissue, literal):

  pre / post   the entry the server chose, its organism_stage, and whether the response is
               byte-identical to the same pair's adult response
  delta        .  = byte-identical before and after
               C  = changed (the literal is now resolved rather than falling through)

The negative direction is part of the table, not an afterthought: two literals that used to produce
one response now produce that response plus a disclosure block, and the literals that used to borrow
the adult baseline no longer do. Both are printed with their byte counts.

Usage: <py> c2_stage_surface.py --before PRE.json --after POST.json --out TABLE.tsv
"""
import argparse
import json
import pathlib

PAIRS = [("human", "retina"), ("human", "RPE"), ("mouse", "retina")]


def load(p):
    d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    rows = {}
    for k, v in d.items():
        if k.startswith("_") or v.get("surface") != "literal":
            continue
        a = v["args"]
        rows[(a["species"], a["tissue"], a["development_stage"])] = v
    adult = {(sp, ti): r["md5"] for (sp, ti, lit), r in rows.items() if lit == "adult"}
    return rows, adult


def describe(v, adult_md5):
    p = v.get("payload") or {}
    entry = p.get("entry_id") or p.get("mode") or ""
    stage = p.get("organism_stage")
    stage = stage if isinstance(stage, str) else ""
    flag = (p.get("stage_literal") or {}).get("flag", "")
    return {"entry": entry, "stage": stage, "flag": flag,
            "md5": v["md5"], "bytes": v["bytes"],
            "same_as_adult": "Y" if v["md5"] == adult_md5 else "N"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pre, pre_adult = load(a.before)
    post, post_adult = load(a.after)

    lines = ["species\ttissue\tliteral\tpre_entry\tpre_stage\tpre_flag\tpre_eq_adult\tpre_md5\t"
             "post_entry\tpost_stage\tpost_flag\tpost_eq_adult\tpost_md5\tdelta\tbytes_delta"]
    changed = []
    for key in sorted(set(pre) | set(post)):
        sp, ti, lit = key
        d_pre = describe(pre[key], pre_adult.get((sp, ti))) if key in pre else None
        d_post = describe(post[key], post_adult.get((sp, ti))) if key in post else None
        if d_pre and d_post:
            delta = "." if d_pre["md5"] == d_post["md5"] else "C"
            bd = d_post["bytes"] - d_pre["bytes"]
        else:
            delta, bd = "?", "?"
        if delta == "C" or (d_pre and d_post and d_pre["same_as_adult"] != d_post["same_as_adult"]):
            changed.append((sp, ti, lit, d_pre, d_post))
        lines.append("\t".join(str(x) for x in (
            sp, ti, lit or "empty",
            d_pre["entry"] if d_pre else "", d_pre["stage"] if d_pre else "",
            d_pre["flag"] if d_pre else "", d_pre["same_as_adult"] if d_pre else "",
            d_pre["md5"] if d_pre else "",
            d_post["entry"] if d_post else "", d_post["stage"] if d_post else "",
            d_post["flag"] if d_post else "", d_post["same_as_adult"] if d_post else "",
            d_post["md5"] if d_post else "", delta, bd)))
    pathlib.Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"table -> {a.out}  rows={len(lines) - 1}")
    print()
    print(f"{'species':<7} {'tissue':<7} {'literal':<20} {'pre':<34} {'post':<34} {'eq_adult':<10} "
          f"{'dBytes'}")
    for sp, ti, lit, d_pre, d_post in changed:
        print(f"{sp:<7} {ti:<7} {(lit or 'empty'):<20} "
              f"{(d_pre['entry'] + ' ' + d_pre['flag'])[:33]:<34} "
              f"{(d_post['entry'] + ' ' + d_post['flag'])[:33]:<34} "
              f"{d_pre['same_as_adult'] + '->' + d_post['same_as_adult']:<10} "
              f"{d_post['bytes'] - d_pre['bytes']:+d}")
    print()
    print(f"changed rows: {len(changed)} of {len(lines) - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())