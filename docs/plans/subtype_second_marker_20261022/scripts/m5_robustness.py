#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m5 -- the robustness reading promised in AMENDMENT_3/4.

A row counts as **robust** when the same `(volume, subtype)` row flips under BOTH the AD1 rule
(pass 2, sentence-level attachment) and the pass-5 rule (structural segment attachment) -- two
independently-derived attachment rules.  A row that flips under only one of them is **rule-dependent**
and carries the name of the rule it depends on.

Writes out/ROBUSTNESS.json / .tsv.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
SUP2 = os.path.join(OUT, "SUPERSEDED_pass2")


def flips_of(sep_path, label):
    rows = json.load(open(sep_path, encoding="utf-8"))
    ctl = json.load(open(os.path.join(OUT, "ruler_control", "SUBTYPE_SEPARATION.json"),
                         encoding="utf-8"))
    ctl_by = {(r["volume"], r["subtype"]): r for r in ctl}
    out = {}
    for r in rows:
        k = (r["volume"], r["subtype"])
        if ctl_by[k]["result"] != r["result"]:
            md = r.get("marker_detail") or []
            added = [d["gene"] for d in md if d["q"] is not None and d["auc"] >= 0.70 and d["q"] < 0.05]
            out[k] = {"rule": label, "after": r["result"], "clearing": added}
    return out


def main():
    p2 = flips_of(os.path.join(SUP2, "ruler_augmented", "SUBTYPE_SEPARATION.json"), "AD1_pass2")
    p5 = flips_of(os.path.join(OUT, "ruler_augmented", "SUBTYPE_SEPARATION.json"), "AD1-4_pass5")
    p2_genes, p5_genes = {}, {}
    for tag, f in (("p2", os.path.join(SUP2, "FLIPS_p2.json")), ("p5", os.path.join(OUT, "FLIPS.json"))):
        if not os.path.isfile(f):
            continue
        for r in json.load(open(f, encoding="utf-8"))["flips"]:
            (p2_genes if tag == "p2" else p5_genes)[(r["volume"], r["subtype"])] = r["clearing_added"]

    keys = sorted(set(p2) | set(p5))
    rows = []
    for k in keys:
        in2, in5 = k in p2, k in p5
        rows.append({"volume": k[0], "subtype": k[1],
                     "flips_pass2_AD1": in2, "flips_pass5_final": in5,
                     "verdict": "robust" if (in2 and in5) else "rule_dependent",
                     "rule_dependent_on": ("" if (in2 and in5) else ("AD1_pass2" if in2 else "final_pass5")),
                     "clearing_added_pass2": p2_genes.get(k, []),
                     "clearing_added_pass5": p5_genes.get(k, [])})
    doc = {"probe": "m5_robustness.py",
           "rule": "robust iff the same (volume, subtype) row flips under both the AD1 rule (pass 2) "
                   "and the pass-5 structural rule",
           "n_pass2_flips": len(p2), "n_pass5_flips": len(p5),
           "n_robust": sum(1 for r in rows if r["verdict"] == "robust"),
           "n_rule_dependent": sum(1 for r in rows if r["verdict"] != "robust"),
           "rows": rows}
    json.dump(doc, open(os.path.join(OUT, "ROBUSTNESS.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "ROBUSTNESS.tsv"), "w", encoding="utf-8") as fh:
        cols = ["volume", "subtype", "flips_pass2_AD1", "flips_pass5_final", "verdict",
                "rule_dependent_on", "clearing_added_pass2", "clearing_added_pass5"]
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join([str(r[c]) if not isinstance(r[c], list) else ",".join(r[c])
                                for c in cols]) + "\n")
    print("pass2 flips=%d pass5 flips=%d robust=%d rule_dependent=%d"
          % (doc["n_pass2_flips"], doc["n_pass5_flips"], doc["n_robust"], doc["n_rule_dependent"]))
    for r in rows:
        print("  %-22s %-56s %-14s pass2=%s%s pass5=%s%s"
              % (r["volume"], r["subtype"], r["verdict"],
                 r["flips_pass2_AD1"], r["clearing_added_pass2"],
                 r["flips_pass5_final"], r["clearing_added_pass5"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())