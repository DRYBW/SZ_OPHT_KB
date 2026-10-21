#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1b — attribute every moved panel digest, and tabulate the stage-literal fall-through.

Reads the dump of step 1 and the recorded baseline, and prints, for each of the twelve panel calls,
the recorded digest, the digest measured at HEAD, whether the two differ, and — for the differing
ones — whether the call was refused on its arguments or answered with different text.

Then prints the stage-literal table: for each (species, tissue, literal), the entry the server
chose, its organism_stage, and whether the response is byte-identical to the adult-baseline
response for the same (species, tissue).

Usage: <py> a2_attribute.py --dump out/PANEL_AT_HEAD.json --baseline tests/fixtures/tool_panel_baseline.json
"""
import argparse
import json
import pathlib

REPO = pathlib.Path("/home/ubuntu/EYEKB_REPO")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", required=True)
    ap.add_argument("--baseline", required=True)
    a = ap.parse_args()

    rows = json.loads(pathlib.Path(a.dump).read_text(encoding="utf-8"))
    base = json.loads(pathlib.Path(a.baseline).read_text(encoding="utf-8"))

    print("=== panel: recorded vs measured at HEAD ===")
    print(f"{'call':<58} {'moved':<6} {'refused':<8} {'recorded':<34} {'measured'}")
    moved_refused, moved_answered, same = 0, 0, 0
    for k, v in sorted((k, v) for k, v in rows.items()
                       if not k.startswith("_") and v["surface"] == "panel"):
        rec = base["calls"].get(k.split("panel::", 1)[1])
        diff = rec != v["md5"]
        if not diff:
            same += 1
        elif v["is_error"]:
            moved_refused += 1
        else:
            moved_answered += 1
        print(f"{k[:57]:<58} {'YES' if diff else '-':<6} "
              f"{'YES' if v['is_error'] else '-':<8} {str(rec):<34} {v['md5']}")
    print(f"  unchanged={same}  moved-refused={moved_refused}  moved-answered={moved_answered}")
    print(f"  recorded tools advertised: {base.get('tools')}")
    print(f"  measured tools advertised: {rows['_tools']}")

    print()
    print("=== stage literal surface (measured) ===")
    print(f"{'species':<8} {'tissue':<8} {'literal':<22} {'is_error':<9} {'entry_id':<44} "
          f"{'organism_stage':<18} {'==adult':<8} bytes")
    adult = {}
    for k, v in rows.items():
        if k.startswith("_") or v["surface"] != "literal":
            continue
        sp, ti, lit = v["args"]["species"], v["args"]["tissue"], v["args"]["development_stage"]
        if lit == "adult":
            adult[(sp, ti)] = v["md5"]
    for k, v in sorted((k, v) for k, v in rows.items()
                       if not k.startswith("_") and v["surface"] == "literal"):
        p = v["payload"] or {}
        sp, ti, lit = v["args"]["species"], v["args"]["tissue"], v["args"]["development_stage"]
        eid = p.get("entry_id") or p.get("mode") or ""
        stage = p.get("organism_stage") if isinstance(p.get("organism_stage"), str) else ""
        ident = "Y" if v["md5"] == adult.get((sp, ti)) else "N"
        print(f"{sp:<8} {ti:<8} {('empty' if lit == '' else lit):<22} "
              f"{'YES' if v['is_error'] else '-':<9} {eid[:43]:<44} {stage[:17]:<18} "
              f"{ident:<8} {v['bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())