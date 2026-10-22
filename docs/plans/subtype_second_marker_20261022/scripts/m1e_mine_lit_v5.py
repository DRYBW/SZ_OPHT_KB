#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m1e -- fifth and FINAL mining pass: STRUCTURAL attachment, no proximity constant.

Implements AMENDMENT_4_NO_PROXIMITY_CONSTANT_20261022.md: a gene symbol attaches to the in-scope
subtype S when the segment carries a marker predicate AND names exactly one in-scope subtype, S.
The 80-character window is gone (it rejected the literature's own "full name then symbol in
parentheses" style: LMO4/DB4 at 87 chars, DNER/DB6 at ~104), and an ambiguous segment that names two
in-scope subtypes now attaches nothing instead of guessing.

Implements AMENDMENT_2 + AMENDMENT_3 + AMENDMENT_4: the attachment unit becomes the comma-level
segment, and a symbol attaches only to the subtype whose name form is nearest inside that segment.
Channels, predicates, L1-L5 and the acceptance gate are unchanged from AD1 / the PREREG.

Writes out/SUBTYPE_SECOND_MARKER_LIT.json / .tsv (pass 3 = the artefact the report's headline uses).
Passes 2-4 are preserved under out/SUPERSEDED_pass2|3|4/.
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
PRED = re.compile(r"marker|express|enrich|specific|label|detect|identif|distinguish|"
                  r"characteriz|discriminat|defined|immunoreactiv|transcript|antibod|stain|"
                  r"positive", re.I)
TOKEN = re.compile(r"\b[A-Z][A-Z0-9]{1,13}\b")
SENT = re.compile(r"(?<=[.!?])\s+")
CLAUSE_SPLIT = re.compile(r";")
COMMA_SPLIT = re.compile(r",")
PROX = 80
COMMA_MAX = 160
K_CAP = 2
PAN_FAMILY_MIN = 3
SNIP = 3


def segments(text):
    """sentence -> ';' -> (if still long) ',' , per AMENDMENT 2 rule 2a."""
    out = []
    for s in SENT.split(text or ""):
        if len(s) < 20:
            continue
        segs = [s] if len(s) <= COMMA_MAX else (CLAUSE_SPLIT.split(s) if len(s) > 400 else [s])
        for c in segs:
            if len(c) <= COMMA_MAX:
                out.append(c)
            else:
                out.extend(x for x in COMMA_SPLIT.split(c) if len(x) >= 20)
    return out


def attach(seg, rxs):
    """{subtype: nearest distance of its name form in this segment} and the name offsets per subtype."""
    spots = {}
    for s, rs in rxs.items():
        offs = [m.start() for r in rs for m in r.finditer(seg)]
        if offs:
            spots[s] = offs
    return spots


def main():
    vocab = set(json.load(open(VOCAB)))
    obs = json.load(open(os.path.join(CONS, "out", "SUBTYPE_OBSERVABILITY_rows.json"), encoding="utf-8"))
    frozen_panel = {r["subtype"]: set(r.get("_markers_all") or []) for r in obs}
    scope = sorted(NAME_FORMS)
    for s in scope:
        assert s in frozen_panel, s
    rxs = {s: [re.compile(p, re.I) for p in NAME_FORMS[s]] for s in scope}
    any_rx = re.compile("|".join("(?:%s)" % p for s in scope for p in NAME_FORMS[s]), re.I)

    A = collections.defaultdict(lambda: collections.defaultdict(set))
    Aex = collections.defaultdict(list)
    ctx_seg = collections.Counter()
    ctx_papers = collections.defaultdict(set)
    n_chunks = n_ctx = n_attached = n_ambiguous = 0
    papers = set()
    import pyarrow.parquet as pq
    f = pq.ParquetFile(CORPUS)
    for b in f.iter_batches(batch_size=2000,
                            columns=["paper_id", "pmcid", "doi", "title", "text"]):
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
            for seg in segments(body):
                if not PRED.search(seg):
                    continue
                spots = attach(seg, rxs)
                if not spots:
                    continue
                for s in spots:
                    ctx_seg[s] += 1
                    ctx_papers[s].add(str(pid))
                if len(spots) != 1:                       # AD4: ambiguity attaches nothing
                    n_ambiguous += 1
                    continue
                s = next(iter(spots))
                for m in TOKEN.finditer(seg):
                    tok = m.group(0)
                    if tok not in vocab:
                        continue
                    best = min(abs(m.start() - x) for x in spots[s])
                    n_attached += 1
                    A[s][tok].add(str(pid))
                    e = Aex[(s, tok)]
                    if len(e) < SNIP:
                        e.append({"paper_id": str(pid), "pmcid": str(pmc), "doi": str(doi),
                                  "title": str(tit or "")[:140], "segment": seg.strip()[:300],
                                  "distance": int(best), "unique_nearest": True})

    # ---------------------------------------------------------------- channel B
    B = collections.defaultdict(lambda: collections.defaultdict(set))
    Bex = collections.defaultdict(list)
    nB_amb = 0
    for fn in ("G1_photoreceptor_bipolar.json", "G2_amacrine_horizontal_rgc.json",
               "G3_glia_vascular_support.json"):
        for e in json.load(open(os.path.join(CONS, "out", fn), encoding="utf-8")):
            s0 = e["subtype_name"]
            if s0 not in NAME_FORMS:
                continue
            for src in (e.get("sources") or []):
                for cl in CLAUSE_SPLIT.split(str(src.get("what_it_supports") or "")):
                    for seg in ([cl] if len(cl) <= COMMA_MAX else
                                [x for x in COMMA_SPLIT.split(cl) if len(x) >= 20]):
                        if not PRED.search(seg):
                            continue
                        spots = attach(seg, rxs)
                        if not spots:
                            continue
                        if len(spots) != 1:              # AD4
                            nB_amb += 1
                            continue
                        sid = str(src.get("id") or "")
                        s1 = next(iter(spots))
                        for m in TOKEN.finditer(seg):
                            tok = m.group(0)
                            if tok not in vocab:
                                continue
                            B[s1][tok].add(sid)
                            x = Bex[(s1, tok)]
                            if len(x) < SNIP:
                                x.append({"source_id": sid, "url": str(src.get("url_fetched") or ""),
                                          "segment": seg.strip()[:300]})

    # ---------------------------------------------------------------- channel C (textbook only)
    C = collections.defaultdict(lambda: collections.defaultdict(set))
    Cex = collections.defaultdict(list)
    tb = os.path.join(REPO, "kb", "textbook_layer", "TEXTBOOK_ITEMS_v1.jsonl")
    if os.path.isfile(tb):
        for i, line in enumerate(open(tb, encoding="utf-8", errors="replace")):
            try:
                j = json.loads(line)
            except Exception:
                continue
            body = " ".join(str(j.get(k) or "") for k in ("term", "quote", "topic"))
            srcid = "kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl:%d" % (i + 1)
            for seg in segments(body):
                if not PRED.search(seg):
                    continue
                spots = attach(seg, rxs)
                if len(spots) != 1:                      # AD4
                    continue
                s1 = next(iter(spots))
                for m in TOKEN.finditer(seg):
                    tok = m.group(0)
                    if tok not in vocab:
                        continue
                    C[s1][tok].add(srcid)
                    e = Cex[(s1, tok)]
                    if len(e) < SNIP:
                        e.append({"source": srcid, "segment": seg.strip()[:300]})

    # ---------------------------------------------------------------- L1..L5
    p_pass = collections.Counter()
    p_pass_strict = collections.Counter()
    for s in scope:
        for g in set(list(A[s]) + list(B[s]) + list(C[s])):
            n = len(A[s].get(g, ())) + len(C[s].get(g, ()))
            if n >= 1 or len(B[s].get(g, ())) >= 1:
                p_pass[g] += 1
            if n >= 2 or len(B[s].get(g, ())) >= 1:
                p_pass_strict[g] += 1

    rows = []
    for s in scope:
        for g in sorted(set(list(A[s]) + list(B[s]) + list(C[s]))):
            pa, pb, pc = sorted(A[s].get(g, ())), sorted(B[s].get(g, ())), sorted(C[s].get(g, ()))
            l1 = (len(pa) + len(pc)) >= 1 or len(pb) >= 1
            l2, l3 = g in vocab, g not in frozen_panel[s]
            l4 = not (p_pass.get(g, 0) >= PAN_FAMILY_MIN)
            rows.append({"subtype": s, "gene": g,
                         "channel_a_papers": pa, "channel_a_n": len(pa),
                         "channel_b_sources": pb, "channel_b_n": len(pb),
                         "channel_c_sources": pc, "channel_c_n": len(pc),
                         "papers_total": len(pa) + len(pc),
                         "l1_strict_papers_ge2": bool(len(pa) + len(pc) >= 2 or len(pb) >= 1),
                         "already_in_frozen_panel": not l3,
                         "subtypes_l1_passing": p_pass.get(g, 0),
                         "subtypes_l1_strict_passing": p_pass_strict.get(g, 0),
                         "L1_lit": l1, "L2_assay_vocab": l2, "L3_not_duplicate": l3,
                         "L4_not_pan_family": l4, "admitted": bool(l1 and l2 and l3 and l4),
                         "snippets": (Aex.get((s, g), []) + Bex.get((s, g), []) + Cex.get((s, g), []))[:3]})

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

    doc = {"probe": "m1e_mine_lit_v5.py",
           "implements": "AMENDMENT_2_ATTACHMENT_UNIT_20261022.md",
           "corpus": CORPUS, "vocab_size": len(vocab), "proximity_chars": None,
           "comma_max": COMMA_MAX, "k_cap": K_CAP, "pan_family_min": PAN_FAMILY_MIN,
           "predicate": PRED.pattern, "attachment": "segment names exactly one in-scope subtype (no proximity constant)",
           "corpus_stats": {"chunks_scanned": n_chunks, "papers": len(papers),
                            "chunks_in_context": n_ctx, "attached_co_mentions": n_attached,
                            "ambiguous_ties_skipped": n_ambiguous, "channel_b_ties_skipped": nB_amb},
           "context_per_subtype": {s: {"segments": ctx_seg.get(s, 0),
                                       "papers": len(ctx_papers.get(s, ()))}
                                   for s in scope},
           "n_rows": len(rows), "n_admitted_before_cap": sum(1 for r in rows if r["admitted"]),
           "n_kept": sum(1 for r in rows if r["kept_l5"]), "rows": rows}
    json.dump(doc, open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.tsv"), "w", encoding="utf-8") as fh:
        cols = ["subtype", "gene", "channel_a_n", "channel_b_n", "channel_c_n", "papers_total",
                "l1_strict_papers_ge2", "subtypes_l1_passing", "subtypes_l1_strict_passing",
                "already_in_frozen_panel", "L1_lit", "L2_assay_vocab", "L3_not_duplicate",
                "L4_not_pan_family", "admitted", "rank_l5", "kept_l5"]
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

    print("[corpus] chunks=%d papers=%d in_context=%d attached=%d ties_skipped=%d"
          % (n_chunks, len(papers), n_ctx, n_attached, n_ambiguous))
    for s in scope:
        kept = [r["gene"] for r in rows if r["subtype"] == s and r["kept_l5"]]
        adm = [(r["gene"], r["papers_total"]) for r in rows if r["subtype"] == s and r["admitted"]]
        print("  %-58s segs=%-5d papers=%-4d admitted=%-40s kept=%s"
              % (s, ctx_seg.get(s, 0), len(ctx_papers.get(s, ())), adm, kept))
    print("rows=%d admitted=%d kept=%d" % (len(rows), sum(1 for r in rows if r["admitted"]),
                                           sum(1 for r in rows if r["kept_l5"])))
    print("wrote", os.path.join(OUT, "SUBTYPE_SECOND_MARKER_LIT.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())