#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step C3 — the acceptance test for the stage-literal gap, run against the shipped bytes.

The card's acceptance line is "either the query path maps an unrecognised/organoid literal to the
unknown tier with a flag, or the docstring is corrected to state the real behaviour". The docstring
now states an unconditional rule, so the rule has to hold for every literal on every pair, not only
for the one literal the card happened to name. This script states it as four assertions and runs
them over the dump of the whole surface:

  A1  a literal that is not a contract tier name (and is not the empty default) carries a
      stage_literal block naming the requested literal and the tier it reached
  A2  that block's flag distinguishes a documented fold (any, postnatal) from an unrecognised
      literal, and the requested literal is echoed verbatim (case included)
  A3  a contract tier name carries no block: "", adult, fetal, developing and unknown answer as
      themselves, so the disclosure is not sprayed onto ordinary calls
  A4  no unrecognised literal is answered with the adult composition: its response is not the
      adult response, and where the two digests do coincide the adult response must not itself be a
      composition answer for that pair (mouse retina has no entry at all - every literal, adult
      included, gets the same "no matching composition entry" error, which lends no adult numbers)

Plus the negative direction, printed rather than summarised: the literal -> entry/stage table for
each pair, and how many responses changed relative to the pre-change dump.

Usage: <py> c3_acceptance.py --after <dump.json> [--before <dump.json>] --out <TABLE.tsv>
"""
import argparse
import json
import pathlib

TIERS = ("", "fetal", "adult", "developing", "unknown")
FOLDED = {"any": "adult", "postnatal": "developing"}


def rows_of(dump):
    out = {}
    for k, v in dump.items():
        if k.startswith("_") or v.get("surface") != "literal":
            continue
        a = v["args"]
        out[(a["species"], a["tissue"], a["development_stage"])] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after", required=True)
    ap.add_argument("--before")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # The server documents one normalisation for the literal (trim, lowercase) before it decides
    # whether the spelling is a contract tier name. The assertions classify the same way; otherwise
    # a padded-but-valid literal (' fetal ') would be graded as an unrecognised one and reported as a
    # product defect that does not exist. Flagged in the report as a criterion note.
    post = json.loads(pathlib.Path(a.after).read_text(encoding="utf-8"))
    pre = json.loads(pathlib.Path(a.before).read_text(encoding="utf-8")) if a.before else None
    rows = rows_of(post)
    pre_rows = rows_of(pre) if pre else {}

    adult = {(sp, ti): r for (sp, ti, lit), r in rows.items() if lit == "adult"}

    lines = ["species\ttissue\tliteral\tentry\torganism_stage\tflag\trequested_echo\ttier\t"
             "same_as_adult\tadult_is_composition\tA1\tA2\tA3\tA4\tchanged"]
    fails = []
    for key in sorted(rows):
        sp, ti, lit = key
        v = rows[key]
        p = v.get("payload") or {}
        block = p.get("stage_literal") or {}
        ad = adult.get((sp, ti))
        ad_p = (ad.get("payload") or {}) if ad else {}
        adult_is_composition = bool(ad_p.get("entry_id"))
        same_as_adult = bool(ad) and v["md5"] == ad["md5"]

        norm = lit.strip().lower()
        folded = norm in FOLDED
        if norm in TIERS:
            a1 = a2 = a4 = "n/a"
            a3 = "PASS" if not block else "FAIL"
            if block:
                fails.append(f"A3 {key}: a contract tier name carries a disclosure block")
        else:
            a3 = "n/a"
            a1 = "PASS" if block and block.get("requested") == lit else "FAIL"
            if a1 == "FAIL":
                fails.append(f"A1 {key}: block={block}")
            want_flag = "stage_literal_folded" if folded else "unrecognised_development_stage_literal"
            want_tier = FOLDED.get(norm, "unknown")
            a2 = ("PASS" if block.get("flag") == want_flag and block.get("tier") == want_tier
                  else "FAIL")
            if a2 == "FAIL":
                fails.append(f"A2 {key}: flag={block.get('flag')!r} tier={block.get('tier')!r}")
            borrows = same_as_adult and adult_is_composition
            a4 = "FAIL" if borrows else "PASS"
            if borrows:
                fails.append(f"A4 {key}: the unrecognised literal is answered with the adult entry")

        changed = "?" if not pre_rows else ("C" if key in pre_rows and
                                            pre_rows[key]["md5"] != v["md5"] else ".")
        lines.append("\t".join(str(x) for x in (
            sp, ti, lit or "empty", (p.get("entry_id") or p.get("mode") or ""),
            p.get("organism_stage") or "", block.get("flag") or "",
            block.get("requested") or "", block.get("tier") or "",
            "Y" if same_as_adult else "N", "Y" if adult_is_composition else "N",
            a1, a2, a3, a4, changed)))

    pathlib.Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print()
    n_lit = sum(1 for r in lines[1:] if r.split("\t")[2] != "empty")
    print(f"rows={len(lines) - 1}  assertions FAIL={len(fails)}")
    for f in fails:
        print(f"  {f}")
    if pre:
        ch = sum(1 for r in lines[1:] if r.split("\t")[-1] == "C")
        print(f"responses that changed versus the pre-change dump: {ch} of {len(lines) - 1}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())