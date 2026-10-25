#!/usr/bin/env python3
"""Build the cross-layer link registry (the "neuron" table) for EyeKB.

One row per knowledge entry, carrying the five fields that define a live link:

    kb_entry (markers library + class)  <->  wiki_page
    <->  pmids (in-corpus citations from the current RAG default library)
    <->  mcp_route (the exact tool call that reaches it)
    <->  skill_trigger (the skill that documents how to consume it)

Rows are written to out/LINK_REGISTRY_v1.jsonl plus a coverage summary.
No network access: citations come only from the local RAG corpus.

Citation records carry the paper's own presentation metadata — `title` (complete, never a
120-character prefix), `doi`, `pmcid` — joined from the corpus on `paper_id == pmid`. Before card
t_d8e7f2d4 (CITTITLE) `title` was `(hit title)[:120]` on the retrieval route and `""` on the
full-text gene-index route, so a title-keyed audit could only ever see ~30% of the citations and
reported it as "the two libraries disagree". Both numbers are re-measured here on every build and
printed; see `citation_field()` / `corpus_meta_index()`.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _repo_root(start):
    """Walk up until the directory that holds both kb/ and mcp_server/."""
    p = start
    for _ in range(6):
        if (p / "kb").is_dir() and (p / "mcp_server").is_dir():
            return p
        p = p.parent
    raise SystemExit("repo root not found from " + str(start))


ROOT = _repo_root(HERE)
MCP = ROOT / "mcp_server"
KB = ROOT / "kb"
OUT = HERE.parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(MCP))

import eyekb_core as core  # noqa: E402

WIKI_DIR = KB / "vk_literature_index"
BOOK_ITEMS = ROOT / "plans" / "devline_book_20261002" / "out" / "BOOK_KB_ITEMS.tsv"

# How many of the strongest gene-index candidates keep the ranked route, and the bar the remaining
# candidates must clear to be admitted as extended evidence. Both are named here so the rule is
# readable in one place and the readout can quote it.
TOP_RANKED = 8          # the highest-evidence candidates, admitted by rank (unchanged behaviour)
STRONG_MIN_GENES = 2    # panel genes that must occur in a paper's BODY text for the extended route

# Libraries the registry wires IN ADDITION to the default answer route.
#
# The registry is a disclosure / wiring surface, not a route. A library registered
# REGISTERED_DEFAULT_OFF has an empty whitelist, so it is not in the default `all` set in any
# state and its entries change no answer; wiring them here is what keeps a name that exists in the
# knowledge base from being a dead end (no wiki page, no route, no citation). Equally, a library
# that is IN the default route is picked up from `core._load_marker_dbs("all")` and must not be
# listed here.
#
# Each name must be a registered `MARKER_LIBS` key whose explicit route
# (`query_marker(cell_type=..., library="<name>")`) actually answers — the wiring proof re-reads
# that against the shipped code rather than trusting this line.
REGISTRY_EXTRA_LIBS = ("cl56_v15",)


def load_paper_tissues():
    """paper_id -> "tissue,tissue" from the shipped corpus metadata.

    Used to refuse an extended citation whose marker genes match but whose organ does not. Returns
    an empty dict when the corpus metadata is unavailable, and the caller then skips the extended
    route entirely rather than admitting uncheckable papers.
    """
    out = {}
    db = os.environ.get("EYEKB_DB_DIR") or str(ROOT / "literature_db" / "v2.4.2_2026-09_slim")
    p = Path(db) / "papers.jsonl"
    if not p.is_file():
        return out
    try:
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                d = json.loads(line)
                pid = str(d.get("paper_id") or d.get("pmid") or "")
                ts = d.get("tissues") or d.get("tissue_labels") or []
                if isinstance(ts, str):
                    ts = [t for t in ts.split(",") if t]
                if pid:
                    out[pid] = ",".join(str(t).strip() for t in ts if str(t).strip())
    except Exception:                                                  # noqa: BLE001
        return {}
    return out


# Presentation metadata a citation record carries about the paper it cites (card t_d8e7f2d4).
CITATION_META_FIELDS = ("title", "doi", "pmcid", "is_preprint")


def corpus_meta_index():
    """paper_id -> {title, doi, pmcid, is_preprint} from the shipped corpus, plus the sources used.

    Why this exists (card t_d8e7f2d4, CITTITLE). A citation record carried `pmid` and a title the
    builder had already cut to 120 characters — or an empty string, for the papers admitted through
    the full-text gene index. Both are defects of THIS file, not of the corpus: every cited paper is
    present in the corpus and the corpus' own `title` field is complete. A title-keyed audit was
    therefore comparing a clipped or blank key against a full one and reading the mismatch as "the
    two libraries disagree".

    The join key is `paper_id == pmid`. That is not an assumption made here: it is the same field
    carried through the chain (corpus build -> retrieval kernel -> this registry) and it is
    re-measured on every build — the caller prints how many cited ids failed to resolve, and any
    non-zero count is visible rather than silently blanking a title.

    Resolution follows the chain the citations themselves come from: EYEKB_DB_DIR, then the
    repository's default-DB resolution (`mcp_server/eyekb_core._default_db_dir()`, i.e. the pointer's
    role:default entry), then the repo-committed G2 slim library. **This function is read-only and
    changes no route** — it resolves the same library the retrieval layer already answers from.
    """
    cands = []
    env = os.environ.get("EYEKB_DB_DIR")
    if env:
        cands.append(Path(env))
    try:
        cands.append(Path(core._default_db_dir()))
    except Exception:                                                  # noqa: BLE001
        pass
    cands.append(ROOT / "literature_db" / "v2.4.2_2026-09_slim")
    out, sources = {}, []
    for db in cands:
        p = Path(db) / "papers.jsonl"
        if not p.is_file():
            continue
        sources.append(str(p))
        try:
            with p.open(encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    d = json.loads(line)
                    pid = str(d.get("paper_id") or d.get("pmid") or "")
                    if not pid:
                        continue
                    out[pid] = {k: ("" if d.get(k) is None else d.get(k))
                                for k in CITATION_META_FIELDS}
        except Exception:                                              # noqa: BLE001
            continue
    return out, sources


def citation_field(meta, pmid, key, fallback=""):
    """One corpus metadata field for a cited paper, with the retrieval hit as the fallback.

    Never returns a truncated value: the point of the CITTITLE fix is that a citation's title is the
    paper's own title, not a 120-character prefix of it. Falls back to `fallback` (the search hit's
    own value) only when the id does not resolve in the corpus — and the caller reports that count.
    """
    v = (meta.get(str(pmid)) or {}).get(key)
    if v in (None, ""):
        v = fallback
    return v if isinstance(v, str) else ("" if v is None else str(v))


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def wiki_index():
    """Map normalised cell-type tokens -> wiki page file that mentions them.

    Two structures are returned: the lower-cased page text (for the strict phrase test) and, per
    page, the set of joins of two and three consecutive word tokens with separators removed. The
    second one exists because the same class is written differently in different places —
    `Mac_DAM_LAM` in the marker library, `Mac_DAMLAM` in a composition table, `Mac DAM/LAM` in
    prose. Those are one class with three spellings, and a link matcher that only knows the first
    reports a page that does discuss the class as absent.
    """
    idx = {}
    spans = {}
    for p in sorted(KB.glob("**/*.md")):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = p.relative_to(KB)
        txt_l = txt.lower()
        idx[rel] = txt_l
        toks = re.split(r"[^a-z0-9]+", txt_l)
        s = set()
        for i in range(len(toks) - 1):
            a = toks[i]
            b = toks[i + 1]
            if a and b:
                s.add(a + b)
                if i + 2 < len(toks) and toks[i + 2]:
                    s.add(a + b + toks[i + 2])
        spans[rel] = s
    return idx, spans


GENE_INDEX = HERE.parent / "out" / "GENE_PAPER_INDEX_v1.tsv"


def gene_index():
    """paper_id -> {gene: {n_chunks, n_body, sections, locator, journal, year, species, ...}}.

    Built by build_gene_paper_index.py, which scans the full text of every chunk in the corpus at
    word boundaries. The corpus' own per-chunk `marker_genes` column is sparse — it records a few
    symbols per chunk, not everything the chunk says — so without this index a citation could not
    be described as "this paper states RPE65" in a way a reader can go and check.
    """
    out = {}
    if not GENE_INDEX.is_file():
        return out
    with GENE_INDEX.open(encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(head):
                continue
            r = dict(zip(head, p))
            out.setdefault(r["paper_id"], {})[r["gene"]] = {
                "n_chunks": int(r["n_chunks"]), "n_body": int(r["n_body_chunks"]),
                "sections": r["sections"], "locator": r["locator"],
                "journal": r["journal"], "year": r["year"],
                "species": r["species"], "is_preprint": r["is_preprint"],
            }
    return out


def book_index():
    """term -> list of (book_edition, page_anchor) from the textbook extraction."""
    out = {}
    if not BOOK_ITEMS.is_file():
        return out
    with BOOK_ITEMS.open(encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(head):
                continue
            r = dict(zip(head, parts))
            kb_term = (r.get("kb_term") or "").strip()
            if not kb_term:
                continue
            for t in re.split(r"[;,]", kb_term):
                t = t.strip()
                if t:
                    out.setdefault(t, []).append(
                        (r.get("book_edition", ""), r.get("chapter_page_anchor", "")))
    return out


def main():
    libs = core._load_marker_dbs("all")
    # Registered default-off libraries wired into the disclosure surface (see REGISTRY_EXTRA_LIBS).
    # Appended after the route's own libraries, so the shipped row order is unchanged and the extra
    # rows land at the end of the marker block.
    have = {n for n, _, _ in libs}
    for extra in REGISTRY_EXTRA_LIBS:
        if extra not in have:
            libs = libs + core._load_marker_dbs(extra)
    wiki, wiki_spans = wiki_index()
    books = book_index()
    gidx = gene_index()
    paper_tissues = load_paper_tissues()
    cmeta, corpus_srcs = corpus_meta_index()
    if not cmeta:
        print("WARNING: citation presentation metadata (title/doi/pmcid) could not be read from any "
              "corpus copy; the gene-index route would then write EMPTY titles and a title-keyed "
              "audit would be unanswerable (card t_d8e7f2d4).")
    else:
        print(f"citation metadata: {len(cmeta)} papers indexed from {corpus_srcs[0]}"
              + (f" ({len(corpus_srcs)} corpus copies read, later ones override earlier ones)"
                 if len(corpus_srcs) > 1 else ""))
    if not gidx:
        print("WARNING: GENE_PAPER_INDEX_v1.tsv missing - citations cannot be verified against "
              "paper full text; run scripts/build_gene_paper_index.py first")
    rows = []
    for name, lib_path, data in libs:
        mk = data.get("markers") if isinstance(data, dict) else None
        if not isinstance(mk, dict):
            continue
        for cls, genes in mk.items():
            if not isinstance(genes, list):
                continue
            genes = [g for g in genes if isinstance(g, str)]
            # --- in-corpus citations -------------------------------------
            # Two passes: the generic label query finds the atlas or review papers that discuss this cell
            # type; a gene-anchored query finds papers that actually mention the marker genes we use
            # to identify it. Hits whose marker_genes intersect our panel are marked as such and
            # ranked first, because "this paper mentions RPE65" is a stronger trail than "this paper
            # is about RPE".
            panel = {g.upper() for g in genes[:6]}
            panel_all = {g.upper() for g in genes[:8]}
            pmids, cites, seen = [], [], set()

            def _collect(hits, gene_match):
                for hit in hits:
                    pmid = str(hit.get("pmid") or hit.get("paper_id") or "")
                    if not pmid or pmid in seen:
                        continue
                    seen.add(pmid)
                    tl = hit.get("tissue_labels") or []
                    mg = [g for g in (hit.get("marker_genes") or [])]
                    overlap = sorted(panel & {str(g).upper() for g in mg})
                    pmids.append(pmid)
                    cites.append({
                        "pmid": pmid,
                        # Was (hit.get("title") or "")[:120] — a 120-character prefix is not a title
                        # and cannot be matched against one (card t_d8e7f2d4). The corpus' own field
                        # is complete; the retrieval hit carries the same string and is used only
                        # when the id fails to resolve, which the caller reports.
                        "title": citation_field(cmeta, pmid, "title", hit.get("title")),
                        "doi": citation_field(cmeta, pmid, "doi"),
                        "pmcid": citation_field(cmeta, pmid, "pmcid"),
                        "journal": hit.get("journal", ""),
                        "year": hit.get("year", ""),
                        "tissues": ",".join(tl) if isinstance(tl, list) else str(tl),
                        "marker_genes": ",".join(mg),
                        "gene_match": bool(overlap) if gene_match else False,
                        "matched_panel_genes": overlap,
                        "relevance": hit.get("relevance_score"),
                        "chunk": (hit.get("snippet") or "")[:200],
                    })

            try:
                res = core.search_literature(cell_type=cls, species="human", top_k=10)
                _collect((res or {}).get("results", []), False)
                q = f"{cls} marker genes {' '.join(genes[:6])}"
                res2 = core.search_literature(cell_type=cls, species="human", top_k=10, query=q)
                _collect((res2 or {}).get("results", []), True)
            except Exception as exc:                                  # noqa: BLE001
                cites = []
                rows.append({"error": f"{cls}: {exc}"})
            # --- full-text verification, then discovery --------------------------
            # GENE_PAPER_INDEX is a word-boundary scan of every chunk in the corpus. It does two
            # things here:
            #   * re-labels each search hit with the genes its paper actually states, the section
            #     they sit in and the chunk locator, so the claim is one a reader can check;
            #   * adds papers the label query never returned, but whose text states the panel
            #     genes, ranked by how many panel genes they contain.
            n_added = 0
            for c in cites:
                per_gene = gidx.get(c["pmid"]) or {}
                present = {k: v for k, v in per_gene.items() if k in panel_all}
                c["genes_in_text"] = sorted(present)
                c["n_genes_in_text"] = len(present)
                c["evidence_source"] = "corpus search"
                if present:
                    top_g, top_meta = max(present.items(), key=lambda kv: kv[1]["n_chunks"])
                    first_sec = [s for s in top_meta["sections"].split("|") if s] or [""]
                    c["gene_match"] = True
                    c["matched_panel_genes"] = sorted(present)
                    c["evidence_locator"] = f"{top_meta['locator']} @ {first_sec[0]}"
                    c["n_chunks_with_gene"] = sum(v["n_chunks"] for v in present.values())
                else:
                    c["gene_match"] = False
                    c["matched_panel_genes"] = []
                    c["evidence_locator"] = ""
                    c["n_chunks_with_gene"] = 0
            cand = {}
            for pid, genes_here in gidx.items():
                if pid in seen:
                    continue
                present = {g: meta for g, meta in genes_here.items() if g in panel_all}
                if not present:
                    continue
                if str(next(iter(present.values()))["species"]).lower() not in {"human", "both"}:
                    continue
                cand[pid] = present
            ranked = sorted(cand.items(),
                            key=lambda kv: (-len(kv[1]),
                                            -sum(m["n_chunks"] for m in kv[1].values()),
                                            kv[0]))

            def _citation(pid, genes_here, tier):
                ordered = sorted(genes_here, key=lambda g: -genes_here[g]["n_chunks"])
                top_meta = genes_here[ordered[0]]
                first_sec = [s for s in top_meta["sections"].split("|") if s] or [""]
                return {
                    "pmid": pid,
                    # Was "" — the gene-index route wrote no title at all, so 2,429 of the registry's
                    # citation records had no title key a reader (or an audit) could use, although the
                    # corpus holds it (card t_d8e7f2d4, CITTITLE).
                    "title": citation_field(cmeta, pid, "title"),
                    "doi": citation_field(cmeta, pid, "doi"),
                    "pmcid": citation_field(cmeta, pid, "pmcid"),
                    "journal": top_meta["journal"],
                    "year": top_meta["year"],
                    "tissues": paper_tissues.get(pid, ""),
                    "marker_genes": "",
                    "gene_match": True,
                    "genes_in_text": ordered,
                    "n_genes_in_text": len(ordered),
                    "matched_panel_genes": ordered,
                    "n_chunks_with_gene": sum(m["n_chunks"] for m in genes_here.values()),
                    "evidence_locator": f"{top_meta['locator']} @ {first_sec[0]}",
                    "evidence_source": "gene index (full text)",
                    "evidence_tier": tier,
                    "species": top_meta["species"],
                    "relevance": None,
                    "chunk": "",
                }

            for pid, genes_here in ranked[:TOP_RANKED]:
                if pid in seen:
                    continue
                seen.add(pid)
                pmids.append(pid)
                cites.append(_citation(pid, genes_here, "top_ranked"))
                n_added += 1

            # --- the rest of the corpus' evidence -------------------------------
            # The papers above are the highest-evidence candidates. Everything below them used to be
            # dropped, which left most of the corpus unreachable from any entry - a paper could state
            # three of an entry's marker genes in its own body text and still not be citable, purely
            # because eight other papers ranked higher. The remaining candidates are admitted here on
            # an explicit bar instead of on rank, and only when the paper is genuinely about the same
            # tissue:
            #
            #   * at least STRONG_MIN_GENES of this entry's panel genes occur in the paper's BODY
            #     text (the index also records abstract-only mentions, which are weaker evidence);
            #   * the paper's own tissue label set intersects the tissues carried by this entry's
            #     search hits, so "same marker genes, different organ" does not attach.
            #
            # Papers admitted this way carry evidence_tier = "panel_genes_2_plus" so a reader can
            # tell them from the ranked set. The rule reads only shipped files and is re-runnable.
            entry_tissues = set()
            for c in cites:
                for t in str(c.get("tissues") or "").split(","):
                    if t.strip():
                        entry_tissues.add(t.strip().lower())
            n_extended = 0
            if not paper_tissues:
                print(f"NOTE: {cls}: corpus paper metadata unavailable, so the extended-evidence "
                      "pass is skipped for this entry (fail-closed rather than unchecked).")
            elif entry_tissues:
                for pid, genes_here in ranked[TOP_RANKED:]:
                    if pid in seen:
                        continue
                    body_genes = {g: m for g, m in genes_here.items() if m["n_body"] > 0}
                    if len(body_genes) < STRONG_MIN_GENES:
                        continue
                    pt = {t.strip().lower() for t in paper_tissues.get(pid, "").split(",") if t.strip()}
                    if not (pt & entry_tissues):
                        continue
                    seen.add(pid)
                    pmids.append(pid)
                    cites.append(_citation(pid, genes_here, "panel_genes_2_plus"))
                    n_extended += 1
            cites.sort(key=lambda c: (not c["gene_match"], -c.get("n_genes_in_text", 0),
                                      -(c.get("relevance") or 0)))
            n_gene = sum(1 for c in cites if c["gene_match"])
            # --- wiki link ----------------------------------------------
            # Two-tier matcher: strict (whole normalised label) and loose (each underscore-separated
            # word of >=5 chars). A loose hit counts as "mentioned" but is flagged, because a naming
            # variant (Mono_Classical vs "monocyte") is a real link while a substring accident is not.
            # Word-boundary matching, because a bare substring test on a short label is noise:
            # "AC" matched any page containing those two letters, which is most of them.
            phrase = cls.replace("_", " ").lower()
            label_norm = _norm(cls)
            strict_re = re.compile(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])")
            loose_res = [re.compile(r"(?<![a-z0-9])" + re.escape(w.lower()) + r"(?![a-z0-9])")
                         for w in re.split(r"[_\s]+", cls) if len(w) >= 5]
            hits, loose_only, variant_only = [], [], []
            for rel, txt in wiki.items():
                if strict_re.search(txt):
                    hits.append(str(rel))
                elif len(label_norm) > 3 and label_norm in wiki_spans.get(rel, ()):
                    variant_only.append(str(rel))
                elif any(rx.search(txt) for rx in loose_res):
                    loose_only.append(str(rel))
            if hits:
                wiki_match_kind = "strict"
            elif variant_only:
                wiki_match_kind = "variant"
            elif loose_only:
                wiki_match_kind = "loose"
            else:
                wiki_match_kind = "absent"
            # Tier order: an exact spelling, then a spelling variant, then a loose word hit. Pages
            # are capped, so a stricter match keeps its slot; nothing that used to be listed is
            # dropped unless a stronger link takes the slot.
            ordered = []
            for src in (hits, variant_only, loose_only):
                for p in src:
                    if p not in ordered:
                        ordered.append(p)
            hits = ordered[:4]
            # --- book anchors -------------------------------------------
            anchors = []
            for key in (cls, cls.replace("_", " ")):
                anchors += books.get(key, [])
            rows.append({
                "source_kind": "marker_library",
                "entry_id": f"{name}::{cls}",
                "library": name,
                "cell_type": cls,
                "n_genes": len(genes),
                "genes_top": genes[:8],
                "kb_file": str(lib_path.relative_to(ROOT)) if str(lib_path).startswith(str(ROOT)) else lib_path.name,
                "wiki_pages": hits[:4],
                "n_wiki_pages": len(hits),
                "wiki_match_kind": wiki_match_kind,
                "pmids": pmids,
                "n_pmids": len(pmids),
                "citations": cites,
                "n_citations": len(cites),
                "n_gene_matched": n_gene,
                "n_gene_index_added": n_added,
                "n_extended_evidence": n_extended,
                "panel_genes": genes[:8],
                "book_anchors": anchors[:4],
                "mcp_route": f"query_marker(cell_type='{cls}', library='{name}')",
                "skill_trigger": "knowledge-guided-cell-annotation",
            })
    # --- textbook layer: structural vocabulary (layers / membranes / regions / pathways) -------
    # These rows carry a book and a page instead of a PMID: the claim they support is anatomical
    # ("where the structure sits"), which no paper in the corpus is being asked to establish.
    tb_path = KB / "textbook_layer" / "TEXTBOOK_ITEMS_v1.jsonl"
    n_book = 0
    if tb_path.is_file():
        for line in tb_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            it = json.loads(line)
            rows.append({
                "source_kind": "textbook",
                "entry_id": f"textbook_t4::{it['term']}",
                "library": "textbook_t4",
                "cell_type": it["term"],
                "kind": it["kind"],
                "n_genes": 0,
                "genes_top": [],
                "kb_file": "kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl",
                "wiki_pages": ["textbook_layer/INDEX.md"],
                "n_wiki_pages": 1,
                "wiki_match_kind": "strict",
                "pmids": [],
                "n_pmids": 0,
                "citations": [],
                "book_anchors": [[it["book"], f"p{it['page']}"]],
                "quote": it["quote"],
                "kb_status": it["kb_status"],
                "mcp_route": f"explain_annotation(cell_type='{it['term']}')",
                "skill_trigger": "knowledge-guided-cell-annotation",
            })
            n_book += 1

    with (HERE.parent / "LINK_REGISTRY_v1.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # CITTITLE re-measurement (card t_d8e7f2d4): a title-keyed audit is only answerable if every
    # citation record carries a non-empty, untruncated title. Both numbers are printed on every build
    # so the defect cannot come back unnoticed.
    cited = {c["pmid"] for r in rows for c in (r.get("citations") or [])}
    n_cit = sum(len(r.get("citations") or []) for r in rows)
    untitled = sorted(p for p in cited if not citation_field(cmeta, p, "title"))
    print(f"citation titles: records={n_cit} distinct_papers={len(cited)} "
          f"resolved={len(cited) - len(untitled)} unresolved={len(untitled)}"
          + (f" UNRESOLVED={untitled[:10]}" if untitled else ""))

    # Same rule as the gate: evidence is a paper OR a textbook page; a page, a route and a skill
    # entry point are always required.
    def _wired(r):
        return (r.get("n_pmids") or r.get("book_anchors")) and r.get("n_wiki_pages") \
            and r.get("mcp_route") and r.get("skill_trigger")

    ok = [r for r in rows if _wired(r)]
    dead = [r for r in rows if not _wired(r)]
    print(f"entries={len(rows)} (marker={len(rows)-n_book}, textbook={n_book}) "
          f"fully_linked={len(ok)} broken_or_partial={len(dead)}")
    for r in dead[:25]:
        print("  gap:", r.get("entry_id"), "pmids=", r.get("n_pmids"),
              "book=", len(r.get("book_anchors") or []), "wiki=", r.get("n_wiki_pages"))


if __name__ == "__main__":
    main()