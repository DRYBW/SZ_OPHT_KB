#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 3b — the timeline: per commit, which panel calls match the recorded baseline.

Reads the dumps written by b1_bisect.sh and prints one row per commit and panel call:
  .   digest equals the recorded baseline
  R   digest moved and the server refused the call (argument validation)
  M   digest moved and the call was answered with different text

Usage: <py> b2_timeline.py --baseline tests/fixtures/tool_panel_baseline.json <dump.json> [<dump.json> ...]
"""
import argparse
import json
import pathlib

PANEL_ORDER = [
    'query_marker:{"cell_type": "RPE", "library": "retina"}',
    'query_marker:{"cell_type": "MG"}',
    'query_marker:{"genes": ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]}',
    'get_tissue_composition:{"detail": true, "species": "human", "tissue": "retina"}',
    'get_tissue_composition:{"species": "mouse", "tissue": "retina"}',
    'get_disease_prior:{"disease": "PDR"}',
    'get_kb_page:{"kind": "topic", "name": "vascular"}',
    'get_kb_page:{"kind": "index"}',
    'search_literature:{"query": "Mueller cell gliosis", "top_k": 3}',
    'search_literature:{"cell_type": "Rod", "top_k": 3}',
    'explain_annotation:{"cell_type": "Rod"}',
    'explain_annotation:{"cell_type": "Mueller cell"}',
]
SHORT = ["qmk RPE", "qmk MG", "qmk genes", "comp detail=bool", "comp mouse", "prior PDR",
         "page kind=topic", "page kind=index", "lit query-only", "lit cell_type",
         "explain Rod", "explain Mueller"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("dumps", nargs="+")
    a = ap.parse_args()
    base = json.loads(pathlib.Path(a.baseline).read_text(encoding="utf-8"))["calls"]

    rows = []
    for d in a.dumps:
        name = pathlib.Path(d).stem.replace("dump_", "")
        data = json.loads(pathlib.Path(d).read_text(encoding="utf-8"))
        by_key = {k.split("panel::", 1)[1]: v for k, v in data.items()
                  if k.startswith("panel::")}
        rows.append((name, by_key))

    hdr = f"{'call':<20}" + "".join(f"{n:>10}" for n, _ in rows)
    print(hdr)
    print("-" * len(hdr))
    for key, label in zip(PANEL_ORDER, SHORT):
        line = f"{label:<20}"
        for _, by_key in rows:
            v = by_key.get(key)
            if v is None:
                line += f"{'?':>10}"
            elif v["md5"] == base.get(key):
                line += f"{'.':>10}"
            elif v["is_error"]:
                line += f"{'R':>10}"
            else:
                line += f"{'M':>10}"
        print(line)
    print()
    print("legend: . = matches the recorded baseline   R = moved, call refused   "
          "M = moved, answered differently")
    print("commits, oldest first: " + ", ".join(n for n, _ in rows))
    print()
    print("=== moved-and-answered calls, in full ===")
    for name, by_key in rows:
        for key, label in zip(PANEL_ORDER, SHORT):
            v = by_key.get(key)
            if v and v["md5"] != base.get(key) and not v["is_error"]:
                print(f"  {name:<10} {label:<20} md5={v['md5']} recorded={base.get(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())