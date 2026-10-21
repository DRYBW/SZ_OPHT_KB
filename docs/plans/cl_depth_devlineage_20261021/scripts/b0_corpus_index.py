#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""b0_corpus_index.py - index the shipped corpus for the two questions this wave asks.

Question 1 (Task A): for a candidate child term the ontology offers us, does our own corpus
state that term? -> out/CORPUS_TERM_INDEX.tsv

Question 2 (Task B): along a developmental edge, are the markers we would claim actually
stated by papers we hold, and where? -> out/CORPUS_GENE_INDEX.tsv

Sources (all local, nothing downloaded):
  * corpus      /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet
                (+ papers.jsonl for the paper-level identity: journal, year, tissue, species)
  * ontology    the file named in out/ONT_NAV_v1.json
  * our labels  out/ONT_LABELMAP_V2.tsv, kb/markers/markers_v9_dev_retina.json (dev panels)

Match rules (deliberately narrow - a false "this paper states the term" is worse than a miss):
  * a term matches only as a whole phrase, word-bounded, case-insensitive, hyphens/underscores
    and whitespace collapsing accounted for; single-token terms are refused (>= 2 tokens);
  * a gene matches only as a standalone token of >= 2 characters, dashes allowed, case-sensitive
    uppercase form (the corpus is English prose; a lowercase 'ac' is not the gene AC).

Every hit is written with its locator so a reader can open the paper and look: paper_id
(PubMed id), the section string, and the chunk row index.

Stdlib + pyarrow only, read-only, zero network.
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
CHUNKS = os.path.join(CORPUS, "chunks.parquet")
PAPERS = os.path.join(CORPUS, "papers.jsonl")
DEV_PANEL = "/mnt/D/EyeKB/kb/markers/markers_v9_dev_retina.json"
MAX_EXAMPLES = 3


def regex_for(phrase: str):
    """Phrase -> whole-phrase, word-bounded regex (hyphen/underscore/space tolerant)."""
    parts = [re.escape(p) for p in re.split(r"[\s\-_]+", phrase.strip()) if p]
    if not parts:
        return None
    body = r"[\s\-_]+".join(parts)
    return re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])", re.IGNORECASE)


def queries_from_ontology(ont: Ontology, fourway: str):
    """Term queries: every CL term used as a counterpart in the four-way table, plus the
    developmental labels of our own dev panels."""
    terms = {}
    with open(fourway, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for side in ("their_cl", "ours_cl"):
                cid = r.get(side) or ""
                if cid:
                    lab = r.get(side + "_label") or ont.label(cid)
                    if lab:
                        terms.setdefault(cid, set()).add(lab)
    panel_terms = {}
    dev = json.load(open(DEV_PANEL, encoding="utf-8")).get("markers", {})
    for lab in dev:
        panel_terms[lab] = "dev_panel_label"
    return terms, panel_terms


def main() -> int:
    nav = json.load(open(os.path.join(WAVE, "out", "ONT_NAV_v1.json"), encoding="utf-8"))
    ont = Ontology(nav["primary_path"])
    fourway = os.path.join(WAVE, "out", "GRANULARITY_FOURWAY_721.tsv")
    cl_terms, dev_labels = queries_from_ontology(ont, fourway)

    # Build the phrase -> key table. Preferred name of the term, plus its exact synonyms
    # (a synonym match is recorded as such, so the strength of the support stays visible).
    phrase_table = []
    for cid, labels in sorted(cl_terms.items()):
        names = []
        if ont.label(cid):
            names.append((ont.label(cid), "preferred_name"))
        syn_pool = [(syn, scope) for syn, scope in ont.terms[cid].synonyms
                    if scope in ("EXACT", "RELATED")
                    and len(re.split(r"[\s\-_]+", syn.strip())) >= 2]
        syn_pool.sort(key=lambda s: (0 if s[1] == "EXACT" else 1, -len(s[0])))
        for syn, scope in syn_pool[:4]:          # cap: keeps the scan honest and bounded
            names.append((syn, "synonym_" + scope.lower()))
        for lab in labels:
            names.append((lab, "label_as_written"))
        seen = set()
        for phrase, kind in names:
            key = re.sub(r"\s+", " ", phrase.strip().lower())
            if key in seen or len(re.split(r"[\s\-_]+", key)) < 2:
                continue
            seen.add(key)
            phrase_table.append({"key": cid, "phrase": phrase.strip(), "kind": kind,
                                 "regex": regex_for(phrase)})
    for lab in sorted(dev_labels):
        phrase_table.append({"key": "dev_label:" + lab, "phrase": lab.replace("_", " "),
                             "kind": "dev_panel_label", "regex": regex_for(lab.replace("_", " "))})
    print(f"term queries: {len(phrase_table)} phrases over "
          f"{len(set(p['key'] for p in phrase_table))} keys")

    # Gene set: everything our marker libraries ship for the classes involved (dev + adult).
    gene_set = set()
    for fname in ("markers_v9_dev_retina.json", "markers_v8_dev_retina.json",
                  "markers_v4.1_clean.json", "markers_v5_retina_interneuron.json",
                  "markers_v6_retina_repair.json", "markers_membrane_v1.json",
                  "markers_v10_antseg_increment.json", "markers_v11_lensiris_increment.json"):
        for d in ("/mnt/D/EyeKB/kb/markers", "/home/ubuntu/EYEKB_REPO/kb/markers"):
            p = os.path.join(d, fname)
            if os.path.isfile(p):
                payload = json.load(open(p, encoding="utf-8"))
                panel = payload.get("markers") or {}
                for genes in panel.values():
                    if isinstance(genes, list):
                        gene_set.update(str(g).upper() for g in genes if isinstance(g, str))
                for ent in (payload.get("entries") or []):
                    if isinstance(ent, dict):
                        gene_set.update(str(g).upper() for g in (ent.get("markers") or []))
                break
    gene_set = {g for g in gene_set if re.fullmatch(r"[A-Z][A-Z0-9\-]{1,14}", g)}
    print(f"gene queries: {len(gene_set)} symbols")

    token_re = re.compile(r"[A-Za-z][A-Za-z0-9\-]{1,14}")
    word_re = re.compile(r"[a-z0-9]+")

    # Prefilter: running every phrase regex on every chunk is hopeless (hundreds of phrases x
    # 245k chunks). Instead index the phrases by their most specific token and only run the
    # regex on chunks where that token occurs. The regex still decides the match, so the
    # prefilter can only cost recall if a token is written differently - which the regex would
    # not have matched either.
    trigger_index = collections.defaultdict(list)
    for q in phrase_table:
        toks = [t for t in word_re.findall(q["phrase"].lower()) if len(t) > 2]
        if not toks:
            continue
        trigger = max(toks, key=len)
        trigger_index[trigger].append(q)
    print(f"prefilter: {len(trigger_index)} trigger tokens over {len(phrase_table)} phrases")

    term_hits = collections.defaultdict(lambda: {"n_chunks": 0, "papers": set(), "examples": []})
    gene_hits = collections.defaultdict(lambda: {"n_chunks": 0, "papers": set(), "examples": [],
                                                 "cell_types": collections.Counter()})
    n_chunks = 0
    pf = pq.ParquetFile(CHUNKS)
    for batch in pf.iter_batches(batch_size=20000,
                                 columns=["paper_id", "section", "chunk_type", "text",
                                          "cell_type_mentioned", "marker_genes"]):
        cols = batch.to_pydict()
        for i in range(batch.num_rows):
            n_chunks += 1
            text = cols["text"][i] or ""
            pid = cols["paper_id"][i]
            section = (cols["section"][i] or "")[:120]
            lower_tokens = set(word_re.findall(text.lower()))
            for trigger in (lower_tokens & trigger_index.keys()):
                for q in trigger_index[trigger]:
                    if q["regex"].search(text):
                        rec = term_hits[(q["key"], q["phrase"], q["kind"])]
                        rec["n_chunks"] += 1
                        rec["papers"].add(pid)
                        if len(rec["examples"]) < MAX_EXAMPLES:
                            rec["examples"].append({"paper_id": pid, "section": section,
                                                    "chunk_type": cols["chunk_type"][i]})
            toks = {t.upper() for t in token_re.findall(text)}
            for g in toks & gene_set:
                rec = gene_hits[g]
                rec["n_chunks"] += 1
                rec["papers"].add(pid)
                for ct in (cols["cell_type_mentioned"][i] or []):
                    rec["cell_types"][ct] += 1
                if len(rec["examples"]) < MAX_EXAMPLES:
                    rec["examples"].append({"paper_id": pid, "section": section,
                                            "cell_type_mentioned":
                                                (cols["cell_type_mentioned"][i] or [])[:4]})
        print(f"  scanned {n_chunks} chunks", flush=True)

    # paper identity for the locators
    papers = {}
    with open(PAPERS, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            papers[d.get("paper_id")] = d
    print(f"scanned {n_chunks} chunks; papers with metadata: {len(papers)}")

    tp = os.path.join(WAVE, "out", "CORPUS_TERM_INDEX.tsv")
    with open(tp, "w", encoding="utf-8") as f:
        f.write("term_key\tcl_label_from_file\tquery_phrase\tmatch_kind\tn_chunks\tn_papers\t"
                "example_paper_ids\texample_locators\n")
        for (key, phrase, kind), rec in sorted(term_hits.items()):
            pids = sorted(rec["papers"])
            f.write(f"{key}\t{ont.label(key) or ''}\t{phrase}\t{kind}\t{rec['n_chunks']}\t"
                    f"{len(pids)}\t{','.join(pids[:5])}\t"
                    f"{' | '.join(e['paper_id'] + ' @ ' + e['section'] for e in rec['examples'])}\n")
    print(f"wrote {tp}  ({len(term_hits)} term rows)")

    gp = os.path.join(WAVE, "out", "CORPUS_GENE_INDEX.tsv")
    with open(gp, "w", encoding="utf-8") as f:
        f.write("gene\tn_chunks\tn_papers\ttop_cell_types\texample_locators\n")
        for g in sorted(gene_hits):
            rec = gene_hits[g]
            tops = ";".join(f"{k}:{v}" for k, v in rec["cell_types"].most_common(4))
            f.write(f"{g}\t{rec['n_chunks']}\t{len(rec['papers'])}\t{tops}\t"
                    f"{' | '.join(e['paper_id'] + ' @ ' + e['section'] for e in rec['examples'])}\n")
    print(f"wrote {gp}  ({len(gene_hits)} genes with at least one corpus hit)")

    meta = {"generated_by": "scripts/b0_corpus_index.py", "corpus": CORPUS,
            "n_chunks_scanned": n_chunks, "n_papers_metadata": len(papers),
            "n_term_phrases": len(phrase_table), "n_genes_queried": len(gene_set),
            "n_genes_with_hits": len(gene_hits),
            "genes_without_any_corpus_hit": sorted(gene_set - set(gene_hits)),
            "term_rows": len(term_hits), "term_keys": len(set(k[0] for k in term_hits)),
            "term_keys_without_hits": sorted(set(p["key"] for p in phrase_table) - set(k[0] for k in term_hits))}
    mp = os.path.join(WAVE, "out", "CORPUS_INDEX_META.json")
    json.dump(meta, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {mp}")
    print(f"  term keys with no corpus hit: {len(meta['term_keys_without_hits'])}")
    print(f"  genes with no corpus hit    : {len(meta['genes_without_any_corpus_hit'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())