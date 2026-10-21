#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m0_corpus_gene_index.py — one pass over the shipped corpus, per gene, with resolvable rows.

The only heavy step in this card. It reads every chunk once and records, for each gene our panels
ship:

  * how many chunks and papers contain it as a standalone uppercase token (the strict rule of card
    L2's b0_corpus_index.py, reused so the two passes are comparable);
  * the species split of those chunks (human / mouse / both / unknown) and how many are
    developmentally scented (dev keyword in the text);
  * for a small closed list of cell-type phrases, how many chunks carry the gene AND the phrase;
  * up to N example locators, each carrying the parquet `row_idx` so the gate can re-open the exact
    row and re-check the token. Examples are preferred human/both, paragraph, dev-scented.

Output: out/CORPUS_GENE_INDEX_v1.tsv (+ meta json, + a raw examples jsonl for the anchor object).

Usage: python3 m0_corpus_gene_index.py [--limit-batches N] [--outdir DIR]
Stdlib + pyarrow only, read-only, zero network.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import resource
import sys

import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

MAX_EXAMPLES = 10
TARGET_PHRASES = {
    "rod": "rod",
    "cone": "cone",
    "retinal progenitor cell": "retinal progenitor",
    "progenitor": "progenitor",
    "photoreceptor": "photoreceptor",
}
DEV_KW = re.compile(
    r"\b(development|developmental|differentiat\w*|fetal|foetal|embryonic|progenitor|"
    r"neurogenesis|organogenesis|gestation\w*|postnatal|immature|proliferat\w*|"
    r"precursor|birth|E1[0-9]|P[0-7]\b)\b", re.IGNORECASE)
WORD_RE = re.compile(r"[a-z0-9]+")


def example_rank(e):
    """Lower is better: a human-context, target-naming, developmentally scented paragraph."""
    return (0 if e["species"] in ("human", "both") else 1,
            0 if e.get("target_phrases") else 1,
            0 if e["dev_kw"] else 1,
            0 if e["chunk_type"] == "paragraph" else 1)
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-]{1,14}")


def gene_universe():
    panels = M.load_panels()
    genes = set()
    raw = collections.defaultdict(set)
    for lib, p in panels.items():
        for label, rec in p["labels"].items():
            for g in rec["genes"]:
                genes.add(g)
                raw[g].add(f"{lib}::{label}")
    core, _markers = M.load_dev_core_evidence()
    for label, genes_d in core.items():
        for g in genes_d:
            g = str(g).upper()
            if M.SYMBOL_RE.match(g):
                genes.add(g)
                raw[g].add(f"dev_v9::{label}")
    return genes, raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-batches", type=int, default=0)
    ap.add_argument("--outdir", default=M.OUT)
    args = ap.parse_args()

    genes, raw = gene_universe()
    print(f"gene universe: {len(genes)} symbols from the shipped panels", flush=True)

    role_flags = M.load_role_flags()
    # a paper flagged data_side_only is searchable background but must never be cited as the
    # anchor for a marker (its substrate is the evaluation volume). It is excluded from the
    # example locators; the corpus counts still include it, which is disclosed.
    no_anchor_papers = {str(p) for p, f in role_flags.items() if f == "data_side_only"}
    no_anchor_papers.update(str(t) for t in M.FORBIDDEN_TOKENS if str(t).isdigit())
    print(f"papers excluded from anchor locators: {sorted(no_anchor_papers)}", flush=True)

    hits = collections.defaultdict(lambda: {
        "n_chunks": 0, "papers": set(), "species": collections.Counter(),
        "tissue": collections.Counter(), "n_devkw": 0, "n_fulltext_absent": 0,
        "target": collections.Counter(), "examples": [], "cell_types": collections.Counter()})
    papers_meta = M.load_papers()
    phrases = {k: re.compile(r"(?<![A-Za-z0-9])" + re.escape(v) + r"(?![A-Za-z0-9])", re.I)
               for k, v in TARGET_PHRASES.items()}

    n_chunks = 0
    ord_i = 0
    pf = pq.ParquetFile(M.CHUNKS)
    cols = ["paper_id", "section", "chunk_type", "text", "cell_type_mentioned",
            "species", "tissue", "full_text_available"]
    for b, batch in enumerate(pf.iter_batches(batch_size=20000, columns=cols), 1):
        d = batch.to_pydict()
        for i in range(batch.num_rows):
            n_chunks += 1
            ord_i += 1
            text = d["text"][i] or ""
            toks = {t.upper() for t in TOKEN_RE.findall(text)}
            present = toks & genes
            if not present:
                continue
            pid = d["paper_id"][i]
            section = (d["section"][i] or "")[:120]
            ctype = (d["cell_type_mentioned"][i] or [])
            has_dev = bool(DEV_KW.search(text))
            t_hits = [k for k, rx in phrases.items() if rx.search(text)]
            for g in present:
                rec = hits[g]
                rec["n_chunks"] += 1
                rec["papers"].add(pid)
                rec["species"][d["species"][i] or "unknown"] += 1
                rec["tissue"][d["tissue"][i] or "unknown"] += 1
                if has_dev:
                    rec["n_devkw"] += 1
                if not d["full_text_available"][i]:
                    rec["n_fulltext_absent"] += 1
                for t in t_hits:
                    rec["target"][t] += 1
                for ct in ctype:
                    rec["cell_types"][ct] += 1
                # keep the ten best-ranked examples rather than the first ten: a gene like RHO
                # occurs in 1,397 chunks and the first ten may all be mouse or non-developmental
                if pid in no_anchor_papers:
                    continue
                ex = rec["examples"]
                cand = {
                    "ord": ord_i, "sha16": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
                    "paper_id": pid, "section": section,
                    "chunk_type": d["chunk_type"][i] or "",
                    "species": d["species"][i] or "unknown",
                    "tissue": d["tissue"][i] or "unknown",
                    "dev_kw": has_dev, "target_phrases": t_hits}
                if len(ex) < MAX_EXAMPLES:
                    ex.append(cand)
                else:
                    worst = max(ex, key=example_rank)
                    if example_rank(cand) < example_rank(worst):
                        ex.remove(worst)
                        ex.append(cand)
        if args.limit_batches and b >= args.limit_batches:
            print(f"[probe] stopped after {b} batches ({n_chunks} chunks)", flush=True)
            break
        if b % 5 == 0:
            print(f"  scanned {n_chunks} chunks (maxrss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1048576:.2f} GiB)  [ok={len(hits)}]",
                  flush=True)

    maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576
    print(f"scanned {n_chunks} chunks; genes with at least one hit: {len(hits)}; "
          f"maxrss {maxrss:.2f} GiB")

    # examples were kept by example_rank during the scan; sort again for presentation
    os.makedirs(args.outdir, exist_ok=True)
    rows = []
    examples = {}
    for g in sorted(hits):
        rec = hits[g]
        ex = sorted(rec["examples"], key=example_rank)
        examples[g] = ex
        rows.append({
            "gene": g,
            "n_chunks": rec["n_chunks"],
            "n_papers": len(rec["papers"]),
            "n_chunks_human_or_both": rec["species"].get("human", 0) + rec["species"].get("both", 0),
            "n_chunks_mouse_only_terms": rec["species"].get("mouse", 0),
            "species_split": ";".join(f"{k}:{v}" for k, v in rec["species"].most_common()),
            "n_dev_scented_chunks": rec["n_devkw"],
            "n_chunks_no_full_text": rec["n_fulltext_absent"],
            "target_phrase_counts": ";".join(f"{k}:{v}" for k, v in rec["target"].most_common()),
            "top_cell_types": ";".join(f"{k}:{v}" for k, v in rec["cell_types"].most_common(6)),
            "example_locators": " | ".join(
                f"{e['paper_id']}@{e['section']}#ord{e['ord']}#sha{e['sha16']}" for e in ex[:4]),
        })
    M.write_tsv(os.path.join(args.outdir, "CORPUS_GENE_INDEX_v1.tsv"), rows,
                ["gene", "n_chunks", "n_papers", "n_chunks_human_or_both",
                 "n_chunks_mouse_only_terms", "species_split", "n_dev_scented_chunks",
                 "n_chunks_no_full_text", "target_phrase_counts", "top_cell_types",
                 "example_locators"])
    with open(os.path.join(args.outdir, "CORPUS_GENE_EXAMPLES_v1.jsonl"), "w",
              encoding="utf-8") as f:
        for g in sorted(examples):
            f.write(json.dumps({"gene": g, "examples": examples[g]}, ensure_ascii=False) + "\n")
    # NOTE: the measured peak RSS deliberately does NOT go into the meta file. A resource
    # reading is a property of the run, not of the corpus, and putting it in a frozen artefact
    # made the second build differ from the first (caught by the replay ledger). It is printed
    # instead, so the run log carries it.
    meta = {
        "generated_by": "scripts/m0_corpus_gene_index.py",
        "corpus": M.CORPUS,
        "n_chunks_scanned": n_chunks,
        "n_genes_queried": len(genes),
        "n_genes_with_hits": len(hits),
        "genes_without_any_corpus_hit": sorted(genes - set(hits)),
        "genes_in_panels": {g: sorted(v) for g, v in sorted(raw.items())},
        "target_phrases": TARGET_PHRASES,
        "match_rule": ("standalone uppercase token [A-Za-z][A-Za-z0-9-]{1,14}, case-sensitive; "
                       "same rule as upstream card L2's b0_corpus_index.py"),
    }
    M.write_json(os.path.join(args.outdir, "CORPUS_GENE_INDEX_v1_META.json"), meta)
    print(f"genes with no corpus hit at all: {len(meta['genes_without_any_corpus_hit'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())