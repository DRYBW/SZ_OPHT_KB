#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_corpus_scan.py - one pass over the local corpus, looking for *asserted* lineage relations.

The corpus is the only local source that can repair a decapitated branch, and the only honest use of
it is to find sentences that actually assert a relation between a covered class and a precursor -
not sentences that merely mention both. So the scan is deliberately narrow:

  * a single pass, streamed in record batches (the 1 GB embedding column is never read);
  * a chunk is looked at only when it carries a lineage verb at all;
  * a phrase matches only as a whole phrase (>= 2 tokens, word-bounded, `_`/`-`/space tolerant);
    single-token library labels such as `Rod` or `MG` are refused, because in English prose `rod`
    and `mg` mean other things far more often than they mean a cell type;
  * a relation is recorded only when both phrases and the verb sit in one sentence, and the
    direction comes from the verb, not from the order of the words.

Direction rules, both recorded in the row:
  origin      "<descendant> ... derived from|develops from|arises from|originates from|comes from
              ... <precursor>"    -> subject before the verb is the descendant
  production  "<precursor> ... gives rise to|differentiates into ...  <descendant>" -> the subject
              before the verb is the precursor

Every hit keeps its locator: PubMed id, section, the parquet row index of the chunk, and the sentence
itself. A second streaming pass then re-reads the recorded row index + sha256 and verifies the quote
is really there, so "resolvable anchor" is a measured property, not a claim.

Outputs: out/CORPUS_ASSERTIONS_RAW.tsv, out/CORPUS_ASSERTION_ANCHORS.tsv,
         out/CORPUS_SCAN_META.json, out/PEER_WEAK_ROW_CHUNKS.tsv
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402

CORPUS = C.CORPUS
CHUNKS = C.CHUNKS
MAX_EXAMPLES = 3
READ_COLS = ["row_idx", "paper_id", "section", "text"]

# ---- lineage verbs, with the direction they imply -------------------------------------------
ORIGIN_VERBS = r"(?:derived|derive|derives|develop|develops|developed|developing|arise|arises|arising|originate|originates|originating|come|comes|coming|descend|descends|generated|generate)"
ORIGIN = re.compile(r"(?<![A-Za-z])" + ORIGIN_VERBS + r"\s+(?:from|of)(?![A-Za-z])", re.IGNORECASE)
PRODUCTION = re.compile(
    r"(?<![A-Za-z])(?:gives?\s+rise\s+to|giving\s+rise\s+to|differentiates?\s+into|"
    r"differentiating\s+into|differentiated\s+into|evolves?\s+into)(?![A-Za-z])", re.IGNORECASE)
ANY_VERB = re.compile(r"(?<![A-Za-z])(?:" + ORIGIN_VERBS + r"\s+(?:from|of)|gives?\s+rise\s+to|"
                      r"giving\s+rise\s+to|differentiates?\s+into|differentiating\s+into|"
                      r"differentiated\s+into|evolves?\s+into)(?![A-Za-z])", re.IGNORECASE)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

META = {}


# A single-token phrase is refused unless it is long enough to be a cell noun and is not one of
# the words that carry another everyday meaning in English prose. `Rod`, `MG`, `AC`, `B` stay out
# (the peer refused them for the same reason); `macrophage`, `fibroblast`, `granulocyte`,
# `melanocyte`, `pericyte`, `keratocyte` stay in, because several covered classes carry exactly
# those single-token names and refusing them would gut the repair scan.
SINGLE_TOKEN_MIN = 6
SINGLE_TOKEN_STOP = {"plasma", "proliferating", "pigmented", "anterior", "secondary", "transit",
                     "muscle", "endothelial", "epithelial", "photoreceptor", "progenitor",
                     "precursor", "ganglion", "bipolar", "horizontal", "amacrine", "stem",
                     "cells", "human", "mouse", "retina", "cornea", "iris", "lens"}


def _plural_suffix(phrase: str) -> str:
    """Corpus prose writes plurals. A phrase that does not already end in `s` may match with one.

    Without this the scan misses `retinal progenitor cells`, `Muller glia`, `rods` and most other
    running text, which is how the first version of this scan found only 14 ordered pairs.
    """
    return "" if phrase.strip().lower().endswith("s") else "s?"


def phrase_regex(phrase: str):
    """Whole-phrase, word-bounded, plural tolerant, with an explicit single-token policy."""
    parts = [re.escape(p) for p in re.split(r"[\s_\-]+", phrase.strip()) if p]
    if len(parts) < 2:
        return None
    return (r"(?<![A-Za-z0-9])" + r"[\s_\-]+".join(parts) + _plural_suffix(phrase)
            + r"(?![A-Za-z0-9])")


def phrase_regex_or_reason(phrase: str, display: str):
    """(regex, refusal_reason) - a single-token phrase is judged, not blanket-refused."""
    rx = phrase_regex(phrase)
    if rx:
        return rx, ""
    toks = [p for p in re.split(r"[\s_\-]+", phrase.strip()) if p]
    if len(toks) != 1:
        return None, "empty phrase"
    tokn = C.norm(display)
    if len(tokn) < SINGLE_TOKEN_MIN:
        return None, f"single token shorter than {SINGLE_TOKEN_MIN} characters"
    if tokn in SINGLE_TOKEN_STOP:
        return None, "single token on the everyday-meaning stop list"
    return (r"(?<![A-Za-z0-9])" + re.escape(display.strip()) + _plural_suffix(display)
            + r"(?![A-Za-z0-9])"), ""


# The corpus writes Mueller/Muller/Müller both ways; the ontology file spells it `Mueller cell`.
SPELLING_VARIANTS = {
    "Mueller cell": ["muller cell", "Müller cell", "mueller glia", "muller glia", "Müller glia"],
    "retinal pigment epithelial cell": ["retinal pigment epithelium cell"],
    "retinal progenitor cell": ["retina progenitor cell"],
}


def build_phrases():
    """Every phrase the scan may match, keyed by its normalised form -> provenance."""
    nodes = C.read_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"))
    lab = C.load_label_map()
    dev3 = C.read_tsv(C.DEV3_TERMS)
    phrases, refused = {}, []
    def add(text, source, ident, kind):
        rx, reason = phrase_regex_or_reason(text, text)
        if not rx:
            refused.append((text, source, ident, reason))
            return
        key = C.norm(text)
        rec = phrases.setdefault(key, {"display": text, "regex": rx, "sources": set(),
                                       "ids": set(), "kind": kind})
        rec["sources"].add(source)
        rec["ids"].add(ident)
    for n in nodes:
        if n["cl_id"]:
            add(n["cl_label"], "node_cl_label", n["node_id"], n["kind"])
            for v in SPELLING_VARIANTS.get(n["cl_label"], []):
                add(v, "spelling_variant", n["node_id"], n["kind"])
            for l in [x for x in n["our_labels"].split(",") if x]:
                add(l, "our_label", n["node_id"], n["kind"])
        else:
            add(n["cl_label"], "in_house_label", n["node_id"], n["kind"])
    for label, r in lab.items():
        add(label, "library_label", r["cl_id"] or f"NO_MATCH:{label}", "library_label")
    for r in dev3:
        add(r["label"], "dev3_candidate_term", r["cl_id"], "ontology_candidate")
    return nodes, phrases, refused


def build_matcher():
    """(nodes, phrases, refused, combined_regex, norm->phrase). Shared with s6 so the peer's cited
    chunks are re-examined with exactly the matcher that produced the scan."""
    nodes, phrases, refused = build_phrases()
    ordered = sorted(phrases.values(), key=lambda r: -len(r["display"]))
    combined = re.compile("(?<![A-Za-z0-9])(?:" + "|".join(r["regex"] for r in ordered)
                          + r")(?![A-Za-z0-9])", re.IGNORECASE)
    norm2rec = {C.norm(r["display"]): r for r in ordered}
    return nodes, phrases, refused, combined, norm2rec


def match_sentence(sent, combined, norm2rec):
    """Every phrase of the matcher that occurs in one sentence, with its span."""
    hits = []
    for m in combined.finditer(sent):
        got = m.group(0)
        rec = norm2rec.get(C.norm(got))
        if rec is None and got.endswith(("s", "S")):
            rec = norm2rec.get(C.norm(got[:-1]))
        if rec is None:
            continue
        hits.append((m.start(), m.end(), rec))
    return hits


def main() -> int:
    import pyarrow.parquet as pq

    nodes, phrases, refused, combined, norm2rec = build_matcher()
    node_by_id = {n["node_id"]: n for n in nodes}
    print(f"phrases matched: {len(phrases)} (refused: {len(refused)})")
    print(f"  refused examples: {sorted({(t, r) for t, _s, _i, r in refused})[:6]}")

    peer_weak = [r for r in C.read_tsv(os.path.join(C.FIRSTPASS_GERM))
                 if r["tier"] == "corpus_cooccurrence_weak"]
    weak_keys = [(r["cl_id"], r["layer_cl"], r["cl_label"]) for r in peer_weak]

    pairs = {}                     # (prec_key, desc_key) -> record
    n_chunks_seen = n_chunks_scanned = n_sentences = 0
    n_single_phrase_sentences = n_multi_phrase_sentences = 0
    pf = pq.ParquetFile(CHUNKS)
    # The corpus carries a `row_idx` column but it is NULL for some rows (measured), so the
    # canonical anchor for a chunk is its position in the stream, with the parquet value recorded
    # beside it when present, plus the chunk's sha256 as the content identity.
    pos = 0
    for batch in pf.iter_batches(batch_size=4096, columns=READ_COLS):
        rows = batch.to_pylist()
        for r in rows:
            pos += 1
            n_chunks_seen += 1
            text = r.get("text") or ""
            if not ANY_VERB.search(text):
                continue
            n_chunks_scanned += 1
            for sent in SENT_SPLIT.split(text):
                if len(sent) > 1200 or not ANY_VERB.search(sent):
                    continue
                n_sentences += 1
                hits = match_sentence(sent, combined, norm2rec)
                if len(hits) < 2:
                    n_single_phrase_sentences += 1
                    continue
                n_multi_phrase_sentences += 1
                for vm in list(ANY_VERB.finditer(sent)):
                    prod = bool(PRODUCTION.match(sent, vm.start()))
                    before = [h for h in hits if h[1] <= vm.start()]
                    after = [h for h in hits if h[0] >= vm.end()]
                    if not before or not after:
                        continue
                    a = max(before, key=lambda h: h[1])
                    b = min(after, key=lambda h: h[0])
                    if prod:
                        prec, desc, rule = a[2], b[2], "production_subject_is_precursor"
                    else:
                        desc, prec, rule = a[2], b[2], "origin_subject_is_descendant"
                    if C.norm(prec["display"]) == C.norm(desc["display"]):
                        continue                         # the same phrase twice in one sentence
                    if prec["ids"] and prec["ids"] == desc["ids"]:
                        continue                         # two labels of one and the same node
                    key = (C.norm(prec["display"]), C.norm(desc["display"]))
                    rec = pairs.setdefault(key, {
                        "precursor_phrase": prec["display"], "descendant_phrase": desc["display"],
                        "precursor_ids": set(), "descendant_ids": set(), "sources": set(),
                        "direction_rule": set(), "verb": set(), "n_chunks": 0, "n_papers": 0,
                        "papers": set(), "examples": []})
                    rec["precursor_ids"] |= prec["ids"]
                    rec["descendant_ids"] |= desc["ids"]
                    rec["sources"] |= prec["sources"] | desc["sources"]
                    rec["direction_rule"].add(rule)
                    rec["verb"].add(vm.group(0).lower())
                    rec["n_chunks"] += 1
                    rec["papers"].add(str(r["paper_id"]))
                    if len(rec["examples"]) < MAX_EXAMPLES:
                        rec["examples"].append({
                            "pmid": str(r["paper_id"]), "section": (r.get("section") or "")[:180],
                            "stream_pos": pos, "parquet_row_idx": r.get("row_idx") or "",
                            "sentence": re.sub(r"\s+", " ", sent)[:400],
                            "chunk_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]})

    for rec in pairs.values():
        rec["n_papers"] = len(rec["papers"])
    # a pair whose reverse is also asserted is a direction conflict: neither side may be admitted
    # from this evidence alone, and the register says so instead of picking a winner.
    rev = {}
    for (pk, dk), rec in pairs.items():
        if (dk, pk) in pairs:
            rec["direction_conflict"] = "yes"
            rev[pk + "|" + dk] = "yes"
        else:
            rec["direction_conflict"] = "no"

    # ---- write the raw assertion table ---------------------------------------------------------
    rows = []
    for (pk, dk), rec in sorted(pairs.items()):
        rows.append({
            "precursor_phrase": rec["precursor_phrase"], "descendant_phrase": rec["descendant_phrase"],
            "precursor_ids": ",".join(sorted(rec["precursor_ids"])),
            "descendant_ids": ",".join(sorted(rec["descendant_ids"])),
            "phrase_sources": ",".join(sorted(rec["sources"])),
            "direction_rules": ",".join(sorted(rec["direction_rule"])),
            "verbs": ",".join(sorted(rec["verb"])),
            "n_chunks": rec["n_chunks"], "n_papers": rec["n_papers"],
            "direction_conflict": rec["direction_conflict"],
            "example_pmids": ",".join(sorted(rec["papers"])[:5]),
        })
    C.write_tsv(os.path.join(C.OUT, "CORPUS_ASSERTIONS_RAW.tsv"), rows,
                ["precursor_phrase", "descendant_phrase", "precursor_ids", "descendant_ids",
                 "phrase_sources", "direction_rules", "verbs", "n_chunks", "n_papers",
                 "direction_conflict", "example_pmids"])
    ex = []
    for (pk, dk), rec in sorted(pairs.items()):
        for e in rec["examples"]:
            ex.append({"precursor_phrase": rec["precursor_phrase"],
                       "descendant_phrase": rec["descendant_phrase"], **e})
    C.write_tsv(os.path.join(C.OUT, "CORPUS_ASSERTION_EXAMPLES.tsv"), ex,
                ["precursor_phrase", "descendant_phrase", "pmid", "section", "stream_pos",
                 "parquet_row_idx", "sentence", "chunk_sha256"])

    # ---- second streaming pass: verify every recorded anchor --------------------------------
    want = {}
    for (pk, dk), rec in sorted(pairs.items()):
        for e in rec["examples"]:
            want.setdefault(e["stream_pos"], []).append((pk, dk, e["chunk_sha256"], e["pmid"]))
    verified, bad, pos = [], [], 0
    for batch in pf.iter_batches(batch_size=4096, columns=READ_COLS):
        for r in batch.to_pylist():
            pos += 1
            if pos not in want:
                continue
            h = hashlib.sha256((r.get("text") or "").encode("utf-8")).hexdigest()[:16]
            for pk, dk, want_h, pmid in want[pos]:
                ok = (h == want_h and str(r["paper_id"]) == pmid)
                verified.append({"stream_pos": pos, "parquet_row_idx": r.get("row_idx") or "",
                                 "pmid": pmid, "chunk_sha256": h,
                                 "recording_matches_the_corpus": "yes" if ok else "no"})
                if not ok:
                    bad.append(f"stream_pos {pos}: {h} vs recorded {want_h}")
    C.write_tsv(os.path.join(C.OUT, "CORPUS_ASSERTION_ANCHORS.tsv"), verified,
                ["stream_pos", "parquet_row_idx", "pmid", "chunk_sha256",
                 "recording_matches_the_corpus"])

    # ---- the peer's weak co-occurrence rows: dump the chunks they cited ---------------------
    cited = set()
    for r in peer_weak:
        for loc in r["corpus_locators"].split(" | "):
            if " @ " in loc:
                cited.add((loc.split(" @ ")[0].strip(), loc.split(" @ ")[1].strip()[:60]))
    dump, pos = [], 0
    for batch in pf.iter_batches(batch_size=4096, columns=READ_COLS):
        for r in batch.to_pylist():
            pos += 1
            pid = str(r["paper_id"])
            sec = (r.get("section") or "")[:60]
            if (pid, sec) in cited:
                text = r.get("text") or ""
                dump.append({"peer_row_class_cl": "", "pmid": pid,
                             "section": (r.get("section") or "")[:180],
                             "stream_pos": pos, "parquet_row_idx": r.get("row_idx") or "",
                             "carries_a_lineage_verb": "yes" if ANY_VERB.search(text) else "no",
                             "text": re.sub(r"\s+", " ", text)[:1200]})
    # attach the peer row each chunk belongs to
    for d in dump:
        for r in peer_weak:
            if f"{d['pmid']} @ " in r["corpus_locators"]:
                d["peer_row_class_cl"] = r["cl_id"]
                break
    C.write_tsv(os.path.join(C.OUT, "PEER_WEAK_ROW_CHUNKS.tsv"), dump,
                ["peer_row_class_cl", "pmid", "section", "stream_pos", "parquet_row_idx",
                 "carries_a_lineage_verb", "text"])

    meta = {"generated_by": "scripts/s5_corpus_scan.py", "corpus": CORPUS,
            "chunks_in_corpus": n_chunks_seen, "chunks_carrying_a_lineage_verb": n_chunks_scanned,
            "sentences_examined": n_sentences,
            "sentences_with_one_phrase_only": n_single_phrase_sentences,
            "sentences_with_two_or_more_phrases": n_multi_phrase_sentences, "phrases_matched": len(phrases),
            "phrases_refused_single_token": len(refused),
            "refused_examples": sorted({f"{t} [{r}]" for t, _s, _i, r in refused})[:12],
            "ordered_pairs_found": len(pairs),
            "pairs_with_a_direction_conflict": sum(1 for r in pairs.values()
                                                  if r["direction_conflict"] == "yes"), "examples_recorded": len(ex),
            "examples_verified": sum(1 for v in verified if v["recording_matches_the_corpus"] == "yes"),
            "examples_failed_verification": bad,
            "peer_weak_rows": len(peer_weak), "peer_weak_chunks_dumped": len(dump),
            "outputs": {"raw": os.path.join(C.OUT, "CORPUS_ASSERTIONS_RAW.tsv"),
                        "examples": os.path.join(C.OUT, "CORPUS_ASSERTION_EXAMPLES.tsv"),
                        "anchors": os.path.join(C.OUT, "CORPUS_ASSERTION_ANCHORS.tsv"),
                        "peer_weak_chunks": os.path.join(C.OUT, "PEER_WEAK_ROW_CHUNKS.tsv")}}
    C.write_json(os.path.join(C.OUT, "CORPUS_SCAN_META.json"), meta)
    print(json.dumps({k: v for k, v in meta.items() if k != "refused_examples"}, ensure_ascii=False,
                     indent=1)[:1400])
    return 0


if __name__ == "__main__":
    sys.exit(main())