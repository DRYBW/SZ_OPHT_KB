#!/usr/bin/env python3
"""Measure citation verification before/after, by the same strict full-text rule.

BEFORE = the citation list produced by the label + gene-anchored corpus searches.
AFTER  = the citation list after the full-text gene index is wired in.
Both are scored with the same rule (does the cited paper's text contain a panel gene of the
entry), so the comparison isolates the wiring change, not a redefinition of "verified".
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REG = HERE.parent / "LINK_REGISTRY_v1.jsonl"
IDX = HERE.parent / "out" / "GENE_PAPER_INDEX_v1.tsv"


def load_idx():
    gidx = {}
    with IDX.open(encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(head):
                continue
            gidx.setdefault(p[1], set()).add(p[0])
    return gidx


def load_rows(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if "error" not in r and r.get("source_kind") == "marker_library"]


def score(rows, gidx):
    n_cit = n_ver = 0
    entries_with = 0
    distinct = set()
    for r in rows:
        panel = {g.upper() for g in (r.get("genes_top") or [])}
        hit_any = False
        for c in r["citations"]:
            n_cit += 1
            distinct.add(c["pmid"])
            if gidx.get(c["pmid"], set()) & panel:
                n_ver += 1
                hit_any = True
        entries_with += int(hit_any)
    return dict(entries=len(rows), citation_rows=n_cit, distinct_papers=len(distinct),
                verified_rows=n_ver, verified_pct=round(100 * n_ver / max(n_cit, 1), 1),
                entries_with_verified=entries_with,
                entries_with_verified_pct=round(100 * entries_with / max(len(rows), 1), 1))


def main():
    gidx = load_idx()
    before = load_rows(sys.argv[1])
    after = load_rows(REG)
    b = score(before, gidx)
    a = score(after, gidx)
    out = {"rule": "cited paper's full text contains >=1 of the entry's top-8 panel genes, "
                   "word-boundary symbol match",
           "before": b, "after": a}
    print(json.dumps(out, indent=2))
    d = HERE.parent / "out" / "CITATION_VERIFICATION_v1.json"
    d.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("written:", d)


if __name__ == "__main__":
    main()