#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m4b -- attribution-quality check on the clauses that drove the flips.

The pre-registered classification (PREREG section 8) asks whether two clearing markers come from
independent claims.  It does not ask whether the claim is *about* the subtype -- that is what the
clause actually says, and it is worth printing in full, untruncated, because a clause can name a gene
and a subtype and still not assert that the gene marks that subtype (a passing mention, e.g. a
fovea-vs-periphery contrast that lists DB4 inside a list).

This script re-reads the corpus, resolves the FULL untruncated sentence and clause for every
flip-driving added gene, and writes them verbatim into out/ATTRIBUTION_CHECK.json.  It is a
disclosure added after the measurement: it is NOT part of the pre-registered verdict, and the report
carries both.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
SENT = re.compile(r"(?<=[.!?])\s+")
CLAUSE = re.compile(r";")
# PREREG section 3 name forms, exactly as the mining pass used them
NAME_FORMS = {
    "diffuse bipolar 2 (DB2)": [r"diffuse bipolar 2", r"\bDB2\b"],
    "diffuse bipolar 3a (DB3a)": [r"diffuse bipolar 3a", r"\bDB3a\b"],
    "diffuse bipolar 3b (DB3b)": [r"diffuse bipolar 3b", r"\bDB3b\b"],
    "diffuse bipolar 4 (DB4)": [r"diffuse bipolar 4", r"\bDB4\b"],
    "diffuse bipolar 6 (DB6)": [r"diffuse bipolar 6", r"\bDB6\b"],
    "flat midget bipolar cell (FMB, OFF midget bipolar)": [r"flat midget bipolar", r"OFF midget bipolar",
                                                           r"\bFMB\b", r"midget bipolar"],
    "invaginating midget bipolar cell (IMB, ON midget bipolar)": [r"invaginating midget bipolar",
                                                                  r"ON midget bipolar", r"\bIMB\b",
                                                                  r"midget bipolar"],
    "blue-cone bipolar cell (BB, S-cone ON bipolar)": [r"blue-cone bipolar", r"blue cone bipolar",
                                                       r"S-cone ON bipolar"],
    "giant bipolar cell (GB)": [r"giant bipolar"],
    "H1 horizontal cell": [r"H1 horizontal"],
    "H2 horizontal cell": [r"H2 horizontal", r"HII horizontal", r"horizontal cell H2"],
    "ON cone bipolar cell (ON BC)": [r"ON cone bipolar", r"ON bipolar cell"],
    "OFF cone bipolar cell (OFF BC)": [r"OFF cone bipolar", r"OFF bipolar cell"],
    "rod bipolar cell (RBC, ON rod bipolar)": [r"rod bipolar"],
    "starburst (cholinergic) amacrine cell": [r"starburst", r"cholinergic amacrine"],
    "parasol retinal ganglion cell": [r"parasol"],
}


def clauses(text):
    for s in SENT.split(text or ""):
        if len(s) <= 400:
            yield s
        else:
            for c in CLAUSE.split(s):
                yield c


def main():
    flips = json.load(open(os.path.join(OUT, "FLIPS.json"), encoding="utf-8"))["flips"]
    lit = json.load(open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), encoding="utf-8"))
    pairs = []          # (paper_id, gene, subtype)
    for f in flips:
        for g in f["clearing_added"]:
            for r in lit["rows"]:
                if r["subtype"] == f["subtype"] and r["gene"] == g:
                    for s in r["snippets"]:
                        if s.get("paper_id"):
                            pairs.append((str(s["paper_id"]), g, f["subtype"]))
    pairs = sorted(set(pairs))
    need = {p[0] for p in pairs}
    print("flip-driving claims to resolve in full:", len(pairs), "papers:", sorted(need))

    texts = {pid: [] for pid in need}
    import pyarrow.parquet as pq
    f = pq.ParquetFile(CORPUS)
    for b in f.iter_batches(batch_size=2000, columns=["paper_id", "text"]):
        for pid, tx in zip(b.column("paper_id").to_pylist(), b.column("text").to_pylist()):
            if str(pid) in texts:
                texts[str(pid)].append(tx or "")

    entries = []
    for pid, g, sub in pairs:
        rxs = [re.compile(p, re.I) for p in NAME_FORMS.get(sub, [])]
        best = None
        for tx in texts.get(pid, []):
            for c in clauses(tx):
                if g not in c:
                    continue
                if any(r.search(c) for r in rxs):
                    best = c.strip()
                    break
            if best:
                break
        entries.append({"paper_id": pid, "gene": g, "subtype": sub, "resolved": bool(best),
                        "full_clause": (best or "")[:600],
                        "truncated_in_mining_record": bool(best and len(best) > 300)})

    doc = {"probe": "m4b_verify_claims.py",
           "note": "full, untruncated clause for every flip-driving added gene; a disclosure added "
                   "after the measurement, NOT part of the pre-registered verdict",
           "n_entries": len(entries), "entries": entries}
    json.dump(doc, open(os.path.join(OUT, "ATTRIBUTION_CHECK.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for e in entries:
        print("=" * 100)
        print(e["paper_id"], "|", e["gene"], "|", e["subtype"], "| resolved:", e["resolved"])
        print("   ", e["full_clause"])
    print("wrote", os.path.join(OUT, "ATTRIBUTION_CHECK.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())