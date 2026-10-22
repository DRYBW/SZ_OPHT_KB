#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m1 -- propose a second discriminating marker per in-scope subtype, FROM LITERATURE ONLY.

Three declared channels (PREREG section 4):

  A. the project literature corpus (v2.6-dev), sentence-level co-mention of a name form and a gene
     symbol that the material can express at all (assay vocabulary);
  B. the sources the frozen wave ALREADY FETCHED -- the `sources[].what_it_supports` statements of
     out/G1..G3*.json, clause-level co-mention;
  C. the rest of the literature held on this machine (kb/vk_literature_index/*.md,
     kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl), same sentence rule as A.

No volume is opened here: candidate generation never looks at our own expression.  The assay
vocabulary is a *vocabulary* filter (42,267 symbols the material can name at all), not an expression
filter.

Writes out/SUBTYPE_SECOND_MARKER_LIT.json and .tsv -- every candidate, including the rejected ones.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(WAVE, "out")
CONS = "/mnt/D/EyeKB/plans/consensus_subtype_20261022"
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet"
VOCAB = "/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json"
REPO = "/home/ubuntu/EYEKB_REPO"

# PREREG section 3, verbatim: name forms per in-scope subtype.
NAME_FORMS = {
    "flat midget bipolar cell (FMB, OFF midget bipolar)":
        [r"flat midget bipolar", r"OFF midget bipolar", r"\bFMB\b", r"midget bipolar"],
    "invaginating midget bipolar cell (IMB, ON midget bipolar)":
        [r"invaginating midget bipolar", r"ON midget bipolar", r"\bIMB\b", r"midget bipolar"],
    "diffuse bipolar 2 (DB2)": [r"diffuse bipolar 2", r"\bDB2\b"],
    "diffuse bipolar 3a (DB3a)": [r"diffuse bipolar 3a", r"\bDB3a\b"],
    "diffuse bipolar 3b (DB3b)": [r"diffuse bipolar 3b", r"\bDB3b\b"],
    "diffuse bipolar 4 (DB4)": [r"diffuse bipolar 4", r"\bDB4\b"],
    "diffuse bipolar 6 (DB6)": [r"diffuse bipolar 6", r"\bDB6\b"],
    "giant bipolar cell (GB)": [r"giant bipolar"],
    "blue-cone bipolar cell (BB, S-cone ON bipolar)":
        [r"blue-cone bipolar", r"blue cone bipolar", r"S-cone ON bipolar"],
    "H1 horizontal cell": [r"H1 horizontal"],
    "H2 horizontal cell": [r"H2 horizontal", r"HII horizontal", r"horizontal cell H2"],
    "ON cone bipolar cell (ON BC)": [r"ON cone bipolar", r"ON bipolar cell"],
    "OFF cone bipolar cell (OFF BC)": [r"OFF cone bipolar", r"OFF bipolar cell"],
    "rod bipolar cell (RBC, ON rod bipolar)": [r"rod bipolar"],
    "starburst (cholinergic) amacrine cell": [r"starburst", r"cholinergic amacrine"],
    "parasol retinal ganglion cell": [r"parasol"],
}
K_CAP = 2          # PREREG L5
PAN_FAMILY_MIN = 3  # PREREG L4

TOKEN = re.compile(r"\b[A-Z][A-Z0-9]{1,13}\b")
SENT = re.compile(r"(?<=[.!?])\s+")
CLAUSE = re.compile(r";")
MAX_SENT = 2000
SNIPPETS_PER_GENE = 3


def sentences(text):
    for s in SENT.split(text or ""):
        if 20 <= len(s) <= MAX_SENT:
            yield s


def main():
    vocab = set(json.load(open(VOCAB)))
    obs = json.load(open(os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json"), encoding="utf-8"))
    frozen_panel = {r["subtype"]: set(r.get("_markers_all") or []) for r in obs}
    scope_subtypes = sorted(NAME_FORMS)
    for s in scope_subtypes:
        assert s in frozen_panel, "in-scope subtype not in the frozen observability rows: %s" % s

    rx = {s: [re.compile(p, re.I) for p in NAME_FORMS[s]] for s in scope_subtypes}
    any_rx = re.compile("|".join("(?:%s)" % p for s in scope_subtypes for p in NAME_FORMS[s]), re.I)

    # ---------------------------------------------------------------- channel A
    import pyarrow.parquet as pq
    f = pq.ParquetFile(CORPUS)
    A = collections.defaultdict(lambda: collections.defaultdict(set))     # subtype -> gene -> {paper}
    Aex = collections.defaultdict(list)                                    # (subtype,gene) -> snippets
    ctx_papers = collections.defaultdict(set)
    ctx_chunks = collections.Counter()
    n_chunks = n_ctx = 0
    papers = set()
    for b in f.iter_batches(batch_size=2000,
                            columns=["paper_id", "pmcid", "doi", "title", "year", "text"]):
        tids = b.column("paper_id").to_pylist()
        pmcs = b.column("pmcid").to_pylist()
        dois = b.column("doi").to_pylist()
        tits = b.column("title").to_pylist()
        txts = b.column("text").to_pylist()
        for pid, pmc, doi, tit, tx in zip(tids, pmcs, dois, tits, txts):
            n_chunks += 1
            papers.add(str(pid))
            body = tx or ""
            if not any_rx.search(body):
                continue
            n_ctx += 1
            for sent in sentences(body):
                for s in scope_subtypes:
                    if not any(r.search(sent) for r in rx[s]):
                        continue
                    ctx_chunks[s] += 1
                    ctx_papers[s].add(str(pid))
                    for tok in set(TOKEN.findall(sent)):
                        if tok not in vocab:
                            continue
                        A[s][tok].add(str(pid))
                        e = Aex[(s, tok)]
                        if len(e) < SNIPPETS_PER_GENE:
                            e.append({"paper_id": str(pid), "pmcid": str(pmc), "doi": str(doi),
                                      "title": str(tit or "")[:140], "snippet": sent.strip()[:320]})

    # ---------------------------------------------------------------- channel B
    B = collections.defaultdict(lambda: collections.defaultdict(set))
    Bex = collections.defaultdict(list)
    for fn in ("G1_photoreceptor_bipolar.json", "G2_amacrine_horizontal_rgc.json",
               "G3_glia_vascular_support.json"):
        for e in json.load(open(os.path.join(CONS, "out", fn), encoding="utf-8")):
            s = e["subtype_name"]
            if s not in NAME_FORMS:
                continue
            for src in (e.get("sources") or []):
                stmt = str(src.get("what_it_supports") or "")
                for cl in CLAUSE.split(stmt):
                    if not any(r.search(cl) for r in rx[s]):
                        continue
                    sid = str(src.get("id") or "")
                    for tok in set(TOKEN.findall(cl)):
                        if tok not in vocab:
                            continue
                        B[s][tok].add(sid)
                        x = Bex[(s, tok)]
                        if len(x) < SNIPPETS_PER_GENE:
                            x.append({"source_id": sid, "url": str(src.get("url_fetched") or ""),
                                      "snippet": cl.strip()[:320]})

    # ---------------------------------------------------------------- channel C
    C = collections.defaultdict(lambda: collections.defaultdict(set))
    Cex = collections.defaultdict(list)
    ctexts = []
    vkdir = os.path.join(REPO, "kb", "vk_literature_index")
    if os.path.isdir(vkdir):
        for fn in sorted(os.listdir(vkdir)):
            if fn.endswith(".md"):
                ctexts.append(("kb/vk_literature_index/%s" % fn,
                               open(os.path.join(vkdir, fn), encoding="utf-8", errors="replace").read()))
    tb = os.path.join(REPO, "kb", "textbook_layer", "TEXTBOOK_ITEMS_v1.jsonl")
    if os.path.isfile(tb):
        for i, line in enumerate(open(tb, encoding="utf-8", errors="replace")):
            try:
                j = json.loads(line)
            except Exception:
                continue
            ctexts.append(("kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl:%d" % (i + 1),
                           " ".join(str(j.get(k) or "") for k in ("term", "quote", "topic"))))
    for srcid, body in ctexts:
        if not any_rx.search(body):
            continue
        for sent in sentences(body):
            for s in scope_subtypes:
                if not any(r.search(sent) for r in rx[s]):
                    continue
                for tok in set(TOKEN.findall(sent)):
                    if tok not in vocab:
                        continue
                    C[s][tok].add(srcid)
                    e = Cex[(s, tok)]
                    if len(e) < SNIPPETS_PER_GENE:
                        e.append({"source": srcid, "snippet": sent.strip()[:320]})

    # ---------------------------------------------------------------- L1..L5
    p_pass = collections.Counter()
    for s in scope_subtypes:
        for g in set(list(A[s]) + list(C[s])):
            if len(A[s].get(g, ())) + len(C[s].get(g, ())) >= 2:
                p_pass[g] += 1
    for s in scope_subtypes:
        for g in list(B[s]):
            p_pass.setdefault(g, 0)

    rows = []
    for s in scope_subtypes:
        genes = sorted(set(list(A[s]) + list(B[s]) + list(C[s])))
        for g in genes:
            pa = sorted(A[s].get(g, ()))
            pb = sorted(B[s].get(g, ()))
            pc = sorted(C[s].get(g, ()))
            l1 = (len(pa) + len(pc)) >= 2 or len(pb) >= 1
            l2 = g in vocab
            l3 = g not in frozen_panel[s]
            l4 = not (p_pass.get(g, 0) >= PAN_FAMILY_MIN)
            rows.append({"subtype": s, "gene": g,
                         "channel_a_papers": pa, "channel_a_n": len(pa),
                         "channel_b_sources": pb, "channel_b_n": len(pb),
                         "channel_c_sources": pc, "channel_c_n": len(pc),
                         "papers_total": len(pa) + len(pc),
                         "already_in_frozen_panel": not l3,
                         "subtypes_l1_passing": p_pass.get(g, 0),
                         "L1_lit": l1, "L2_assay_vocab": l2, "L3_not_duplicate": l3, "L4_not_pan_family": l4,
                         "admitted": bool(l1 and l2 and l3 and l4),
                         "snippets": (Aex.get((s, g), []) + Bex.get((s, g), []) + Cex.get((s, g), []))[:3]})

    # L5: raking + cap
    by_sub = collections.defaultdict(list)
    for r in rows:
        if r["admitted"]:
            by_sub[r["subtype"]].append(r)
    for s, lst in by_sub.items():
        lst.sort(key=lambda r: (-r["papers_total"], -r["channel_b_n"], r["gene"]))
        for i, r in enumerate(lst):
            r["rank_l5"] = i + 1
            r["kept_l5"] = i < K_CAP
    for r in rows:
        r.setdefault("rank_l5", None)
        r.setdefault("kept_l5", False)

    doc = {"probe": "m1_mine_lit.py",
           "corpus": CORPUS, "corpus_sha256": None,
           "vocab_size": len(vocab), "k_cap": K_CAP, "pan_family_min": PAN_FAMILY_MIN,
           "corpus_stats": {"chunks_scanned": n_chunks, "papers": len(papers), "chunks_in_context": n_ctx},
           "context_per_subtype": {s: {"chunks": ctx_chunks.get(s, 0), "papers": len(ctx_papers.get(s, ()))}
                                   for s in scope_subtypes},
           "n_rows": len(rows), "n_admitted_before_cap": sum(1 for r in rows if r["admitted"]),
           "n_kept": sum(1 for r in rows if r["kept_l5"]),
           "rows": rows}
    os.makedirs(OUT, exist_ok=True)
    json.dump(doc, open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.tsv"), "w", encoding="utf-8") as fh:
        cols = ["subtype", "gene", "channel_a_n", "channel_b_n", "channel_c_n", "papers_total",
                "subtypes_l1_passing", "already_in_frozen_panel", "L1_lit", "L2_assay_vocab",
                "L3_not_duplicate", "L4_not_pan_family", "admitted", "rank_l5", "kept_l5"]
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

    print("[corpus] chunks=%d papers=%d chunks_in_context=%d" % (n_chunks, len(papers), n_ctx))
    for s in scope_subtypes:
        kept = [r["gene"] for r in rows if r["subtype"] == s and r["kept_l5"]]
        allpass = [r["gene"] for r in rows if r["subtype"] == s and r["admitted"]]
        print("  %-58s ctx_chunks=%-5d ctx_papers=%-4d admitted=%-12s kept=%s"
              % (s, ctx_chunks.get(s, 0), len(ctx_papers.get(s, ())), allpass, kept))
    print("rows=%d admitted=%d kept=%d" % (len(rows), sum(1 for r in rows if r["admitted"]),
                                           sum(1 for r in rows if r["kept_l5"])))
    print("wrote", os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())