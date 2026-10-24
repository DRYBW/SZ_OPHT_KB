# -*- coding: utf-8 -*-
"""show_registry_row.py -- print W3_PIPELINE_REGISTRY.tsv header + row L1-31, cell by cell."""
import csv

P = "/home/ubuntu/EYEKB_REPO/docs/W3_PIPELINE_REGISTRY.tsv"
rows = list(csv.reader(open(P, encoding="utf-8"), delimiter="\t"))
hdr = None
for i, r in enumerate(rows):
    if r and not r[0].startswith("#"):
        hdr = r
        print("header line %d, %d cols" % (i + 1, len(r)))
        break
for j, r in enumerate(rows):
    if len(r) > 1 and r[1] == "L1-31":
        print("row line %d, %d cols" % (j + 1, len(r)))
        for h, v in zip(hdr, r):
            print("== %s: %s" % (h, str(v)[:300]))
        break
