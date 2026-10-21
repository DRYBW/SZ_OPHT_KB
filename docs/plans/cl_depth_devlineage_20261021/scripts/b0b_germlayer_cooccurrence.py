#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""b0b_germlayer_cooccurrence.py - where does our own corpus state a cell's developmental origin?

The ontology's `develops_from` relation reaches a germ layer for only a handful of the classes
the library covers (the photoreceptor chain through RPC, endothelium through mesoderm, ...). For
the rest, the germ-layer grouping the PI asked for has to come from somewhere, and "somewhere"
cannot be an assertion. This script measures the weaker but checkable alternative: how often a
chunk of our own corpus states the class and the germ layer together, and where.

Strength honesty: co-occurrence inside one chunk is not a developmental claim by itself. Each row
records the counts and up to three locators so the claim can be read; the lineage data marks
these rows `corpus_cooccurrence`, never `ontology_chain`.

Read-only, stdlib + pyarrow, zero network.
"""
from __future__ import annotations

import collections
import csv
import json
import os
import re
import sys

import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ont_nav import Ontology  # noqa: E402

CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10"
CHUNKS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
MAX_EXAMPLES = 3


def phrase_regex(phrase: str):
    parts = [re.escape(p) for p in re.split(r"[\s\-_]+", phrase.strip()) if p]
    if not parts:
        return None
    body = r"[\s\-_]+".join(parts)
    return re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])", re.IGNORECASE)


def main() -> int:
    nav = json.load(open(os.path.join(WAVE, "out", "ONT_NAV_v1.json"), encoding="utf-8"))
    ont = Ontology(nav["primary_path"])

    # class phrases: every CL term our label map maps to, by its name and its own synonym set
    classes = {}
    with open(os.path.join(WAVE, "out", "ONT_LABELMAP_V2.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["cl_id"]:
                classes.setdefault(r["cl_id"], set()).add(r["label"])
    # layer phrases: the anchors resolved in a1, plus their synonyms
    layers = {}
    for a in nav["germ_layer_anchors"]:
        if not a["cl_id"]:
            continue
        phrases = {a["queried_name"], ont.label(a["cl_id"])}
        for syn, scope in ont.terms[a["cl_id"]].synonyms:
            if scope == "EXACT" and len(re.split(r"[\s\-_]+", syn.strip())) >= 1:
                phrases.add(syn)
        layers[a["key"]] = phrases

    phrase_rows = []
    for cid, labs in sorted(classes.items()):
        names = set(labs)
        if ont.label(cid):
            names.add(ont.label(cid))
        for ph in names:
            phrase_rows.append(("class", cid, ph.strip(), phrase_regex(ph)))
    for key, phs in sorted(layers.items()):
        cid = next(a["cl_id"] for a in nav["germ_layer_anchors"] if a["key"] == key)
        for ph in phs:
            phrase_rows.append(("layer", key, ph.strip(), phrase_regex(ph)))
    phrase_rows = [p for p in phrase_rows if p[3] is not None]
    print(f"phrases: {sum(1 for p in phrase_rows if p[0]=='class')} class / "
          f"{sum(1 for p in phrase_rows if p[0]=='layer')} layer")

    word_re = re.compile(r"[a-z0-9]+")
    trigger_index = collections.defaultdict(list)
    for kind, key, ph, rx in phrase_rows:
        toks = [t for t in word_re.findall(ph.lower()) if len(t) > 2]
        if not toks:
            continue
        trigger_index[max(toks, key=len)].append((kind, key, ph, rx))
    print(f"prefilter triggers: {len(trigger_index)}")

    hits = collections.defaultdict(lambda: {"n_chunks": 0, "papers": set(), "examples": []})
    n_chunks = 0
    pf = pq.ParquetFile(CHUNKS)
    for batch in pf.iter_batches(batch_size=20000,
                                 columns=["paper_id", "section", "chunk_type", "text"]):
        cols = batch.to_pydict()
        for i in range(batch.num_rows):
            n_chunks += 1
            text = cols["text"][i] or ""
            lower = set(word_re.findall(text.lower()))
            cls_hit, lay_hit = set(), set()
            for trigger in (lower & trigger_index.keys()):
                for kind, key, ph, rx in trigger_index[trigger]:
                    if rx.search(text):
                        (cls_hit if kind == "class" else lay_hit).add(key)
            if not cls_hit or not lay_hit:
                continue
            pid = cols["paper_id"][i]
            section = (cols["section"][i] or "")[:120]
            for c in cls_hit:
                for l in lay_hit:
                    rec = hits[(c, l)]
                    rec["n_chunks"] += 1
                    rec["papers"].add(pid)
                    if len(rec["examples"]) < MAX_EXAMPLES:
                        rec["examples"].append({"paper_id": pid, "section": section,
                                                "chunk_type": cols["chunk_type"][i]})
    print(f"scanned {n_chunks} chunks; class-layer pairs with at least one chunk: {len(hits)}")

    out = os.path.join(WAVE, "out", "CORPUS_GERMLAYER_COOCCURRENCE.tsv")
    with open(out, "w", encoding="utf-8") as f:
        f.write("class_cl\tclass_label\tlayer_key\tlayer_cl\tn_chunks\tn_papers\t"
                "example_locators\n")
        for (c, l), rec in sorted(hits.items()):
            layer_cl = next(a["cl_id"] for a in nav["germ_layer_anchors"] if a["key"] == l)
            f.write(f"{c}\t{ont.label(c) or ''}\t{l}\t{layer_cl}\t{rec['n_chunks']}\t"
                    f"{len(rec['papers'])}\t"
                    f"{' | '.join(e['paper_id'] + ' @ ' + e['section'] for e in rec['examples'])}\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())