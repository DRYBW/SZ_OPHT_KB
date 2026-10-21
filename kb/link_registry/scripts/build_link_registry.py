#!/usr/bin/env python3
"""Build the cross-layer link registry (the "neuron" table) for EyeKB.

One row per knowledge entry, carrying the five fields that define a live link:

    kb_entry (markers library + class)  <->  wiki_page
    <->  pmids (in-corpus citations from the current RAG default library)
    <->  mcp_route (the exact tool call that reaches it)
    <->  skill_trigger (the skill that documents how to consume it)

Rows are written to out/LINK_REGISTRY_v1.jsonl plus a coverage summary.
No network access: citations come only from the local RAG corpus.
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


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def wiki_index():
    """Map normalised cell-type tokens -> wiki page file that mentions them."""
    idx = {}
    for p in sorted(KB.glob("**/*.md")):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = p.relative_to(KB)
        txt_l = txt.lower()
        idx[rel] = txt_l
    return idx


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
    wiki = wiki_index()
    books = book_index()
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
                        "title": (hit.get("title") or "")[:120],
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
            cites.sort(key=lambda c: (not c["gene_match"], -(c.get("relevance") or 0)))
            n_gene = sum(1 for c in cites if c["gene_match"])
            # --- wiki link ----------------------------------------------
            # Two-tier matcher: strict (whole normalised label) and loose (each underscore-separated
            # word of >=5 chars). A loose hit counts as "mentioned" but is flagged, because a naming
            # variant (Mono_Classical vs "monocyte") is a real link while a substring accident is not.
            strict_tok = _norm(cls)
            loose_toks = [t for t in (_norm(w) for w in re.split(r"[_\s]+", cls)) if len(t) >= 5]
            hits, loose_only = [], []
            for rel, txt in wiki.items():
                if strict_tok and strict_tok in txt:
                    hits.append(str(rel))
                elif any(t in txt for t in loose_toks):
                    loose_only.append(str(rel))
            if not hits and loose_only:
                hits = loose_only[:4]
                wiki_match_kind = "loose"
            elif hits:
                wiki_match_kind = "strict"
            else:
                wiki_match_kind = "absent"
            # --- book anchors -------------------------------------------
            anchors = []
            for key in (cls, cls.replace("_", " ")):
                anchors += books.get(key, [])
            rows.append({
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
                "book_anchors": anchors[:4],
                "mcp_route": f"query_marker(cell_type='{cls}', library='{name}')",
                "skill_trigger": "knowledge-guided-cell-annotation",
            })
    with (HERE.parent / "LINK_REGISTRY_v1.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    ok = [r for r in rows if r.get("n_pmids") and r.get("n_wiki_pages")]
    dead = [r for r in rows if not r.get("n_pmids") or not r.get("n_wiki_pages")]
    print(f"entries={len(rows)} fully_linked={len(ok)} broken_or_partial={len(dead)}")
    for r in dead[:25]:
        print("  gap:", r.get("entry_id"), "pmids=", r.get("n_pmids"),
              "wiki=", r.get("n_wiki_pages"))


if __name__ == "__main__":
    main()