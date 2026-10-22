#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n4a -- harvest literature evidence for the optic-nerve fibroblast carrier.

The recipe is the one this repository already uses (plans/antseg_fill_20261020/mine_lit.py,
plans/lens_iris_gapfill_20261021/mine_lit.py, plans/holefill_v12_20261021/mine_lit.py): candidate
genes are *proposed* from the local RAG corpus only, and every proposed gene carries the paper
count and up to three example snippets in which the symbol actually occurs.

Difference from those waves: the candidate set here is not open-ended. It is exactly

  * the 10 genes of the motivating cluster's recorded window (CX15_optic_nerve_all cluster 31),
  * the 10 genes of the shipped generic `Fibroblast` panel (kb/markers/markers_membrane_v1.json),
  * the 3 genes of the shipped limbal/scleral fibroblast entry (markers_k9_ocs_increment.json).

Nothing outside those 23 symbols can enter the carrier, so the harvest cannot wander; the corpus is
asked a closed question. Memory discipline: the 1.08 GB parquet is scanned in record batches and
only fibroblast-context rows are materialised (PREREG section on resource discipline).

Writes out/carrier_lit.json and out/carrier_lit.tsv.
"""
import collections
import json
import os
import re
import sys

import pyarrow.dataset as ds

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
VOCAB = "/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json"
REPO = "/home/ubuntu/EYEKB_REPO"

WINDOW = ["BICC1", "MIR99AHG", "RBMS3", "LEPR", "FOXP2", "ADAMTSL3", "MIR100HG", "BNC2", "EYA2",
          "CEMIP"]
PANEL_FIBRO = ["COL1A1", "COL1A2", "COL3A1", "DCN", "LUM", "FBN1", "FN1", "PTGDS", "MMP2", "THY1"]
PANEL_LIMBUS = ["DPT", "LEPR", "LAMA2"]
CANDIDATES = sorted(set(WINDOW) | set(PANEL_FIBRO) | set(PANEL_LIMBUS))

OCULAR = {"retina", "rpe", "choroid", "optic_nerve", "optic nerve", "sclera", "iris", "lens",
          "ciliary_body", "ciliary body", "trabecular_meshwork", "trabecular meshwork",
          "ocular_surface", "ocular surface", "cornea", "conjunctiva", "eye"}
FIBRO = re.compile(r"fibroblast", re.I)
TOKEN = re.compile(r"\b[A-Z][A-Z0-9]{1,13}(?:-[A-Z0-9]{1,6})?\b")


def snippets(text, gene, k=3):
    out = []
    for m in re.finditer(r"[^.!?]{0,200}\b%s\b[^.!?]{0,160}[.!?]" % re.escape(gene), text):
        s = m.group(0).strip()
        if s and len(s) > 40:
            out.append(s[:320])
        if len(out) >= k:
            break
    return out


def main():
    vocab = set(json.load(open(VOCAB)))
    cand = [g for g in CANDIDATES if g in vocab]
    print("[vocab] %d/%d candidates are measurable symbols in the assay"
          % (len(cand), len(CANDIDATES)), flush=True)
    not_in_vocab = sorted(set(CANDIDATES) - set(cand))

    d = ds.dataset(CORPUS)
    cols = ["paper_id", "pmcid", "title", "year", "tissue", "cell_type_mentioned", "text"]
    fib_papers = collections.defaultdict(set)        # gene -> {paper_id} any-tissue fibro context
    eye_papers = collections.defaultdict(set)        # gene -> {paper_id} ocular fibro context
    ex = collections.defaultdict(list)
    n_chunks = n_fibchunks = n_eyefibchunks = 0
    papers = set()

    for batch in d.to_batches(columns=cols, batch_size=4000):
        texts = batch.column("text").to_pylist()
        tids = batch.column("paper_id").to_pylist()
        pmcids = batch.column("pmcid").to_pylist()
        titles = batch.column("title").to_pylist()
        tissues = batch.column("tissue").to_pylist()
        for txt, pid, pmcid, title, tis in zip(texts, tids, pmcids, titles, tissues):
            n_chunks += 1
            papers.add(pid)
            body = txt or ""
            if not FIBRO.search(body):
                continue
            n_fibchunks += 1
            toks = {t for t in TOKEN.findall(body) if t in cand}
            if not toks:
                continue
            tl = str(tis or "").strip().casefold()
            is_eye = any(o in tl for o in OCULAR) or any(o in body[:4000].casefold()
                                                         for o in ("optic nerve", "retina",
                                                                   "sclera", "ocular",
                                                                   "eye"))
            if is_eye:
                n_eyefibchunks += 1
            for g in toks:
                fib_papers[g].add(pid)
                if is_eye:
                    eye_papers[g].add(pid)
                e = ex[g]
                if len(e) < 3 and len(toks) <= 6:
                    for s in snippets(body, g):
                        e.append({"paper_id": str(pid), "pmcid": str(pmcid),
                                  "title": (title or "")[:140], "tissue": tis, "snippet": s})
                        break

    rows = []
    for g in CANDIDATES:
        rows.append({
            "gene": g,
            "in_assay_vocabulary": g in vocab,
            "from_window": g in WINDOW,
            "from_panel_fibroblast": g in PANEL_FIBRO,
            "from_panel_limbus": g in PANEL_LIMBUS,
            "papers_fibroblast_context_any_tissue": len(fib_papers.get(g, ())),
            "papers_fibroblast_context_eye": len(eye_papers.get(g, ())),
            "examples": ex.get(g, [])[:3],
        })
    rows.sort(key=lambda r: -r["papers_fibroblast_context_eye"])

    doc = {"probe": "n4a_mine_carrier.py",
           "corpus": CORPUS,
           "corpus_stats": {"chunks_scanned": n_chunks, "papers": len(papers),
                            "chunks_with_fibroblast": n_fibchunks,
                            "chunks_with_fibroblast_and_eye": n_eyefibchunks},
           "candidate_rule": "closed set = motivating window (10) + shipped generic Fibroblast "
                             "panel (10) + shipped limbal/scleral fibroblast entry (3)",
           "candidates_not_measurable_in_assay": not_in_vocab,
           "rows": rows}
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "carrier_lit.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "carrier_lit.tsv"), "w", encoding="utf-8") as f:
        f.write("gene\tin_assay\tfrom_window\tfrom_panel_fibro\tfrom_panel_limbus\t"
                "papers_fibro_any_tissue\tpapers_fibro_eye\n")
        for r in rows:
            f.write("%s\t%s\t%s\t%s\t%s\t%d\t%d\n"
                    % (r["gene"], r["in_assay_vocabulary"], r["from_window"],
                       r["from_panel_fibroblast"], r["from_panel_limbus"],
                       r["papers_fibroblast_context_any_tissue"],
                       r["papers_fibroblast_context_eye"]))
    print("[corpus] chunks=%d papers=%d fibro_chunks=%d eye_fibro_chunks=%d"
          % (n_chunks, len(papers), n_fibchunks, n_eyefibchunks))
    for r in rows:
        print("   %-10s assay=%-5s window=%-5s fibro_eye=%-4d fibro_any=%-4d"
              % (r["gene"], r["in_assay_vocabulary"], r["from_window"],
                 r["papers_fibroblast_context_eye"], r["papers_fibroblast_context_any_tissue"]))
    if not_in_vocab:
        print("   not measurable in the assay:", not_in_vocab)
    print("wrote", os.path.join(OUT, "carrier_lit.json"))


if __name__ == "__main__":
    main()