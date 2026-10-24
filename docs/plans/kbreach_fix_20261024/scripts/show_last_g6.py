# -*- coding: utf-8 -*-
"""show_last_g6.py -- print the last change-control instance row, cell by cell (read-only)."""
import csv
import sys

P = "/home/ubuntu/EYEKB_REPO/docs/CHANGE_CONTROL_G6_INSTANCE.tsv"
rows = list(csv.reader(open(P, encoding="utf-8"), delimiter="\t"))
hdr = None
for r in rows:
    if r and not r[0].startswith("#"):
        hdr = r
        break
last = rows[-1]
print("header cells:", len(hdr), "| last row cells:", len(last))
for h, v in zip(hdr, last):
    print("--- %s: %s" % (h, str(v)[:220]))
