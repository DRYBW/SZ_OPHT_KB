#!/usr/bin/env python3
"""Generate the annotation-evidence appendix: for every knowledge entry, the basis of the
annotation plus the literature it cites.

Input  : out/LINK_REGISTRY_v1.jsonl  (built by build_link_registry.py)
Output : out/ANNOTATION_EVIDENCE_APPENDIX_v1.md   (report-ready, English)
         out/ANNOTATION_EVIDENCE_APPENDIX_v1.tsv  (machine-readable)

Every row answers three questions a reader of the final report will ask:
  1. What identifies this cell type here?      -> key markers + the library the entry lives in
  2. Where does that knowledge come from?      -> curated entry + textbook page anchor
  3. Which papers back it?                     -> PMIDs from the local corpus (journal, year)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out"
REG = HERE.parent / "LINK_REGISTRY_v1.jsonl"

# Which libraries feed the default answer surface vs which are reachable only by explicit routing.
DEFAULT_ON = {"retina", "membrane", "retina_interneuron", "retina_v6", "face_v6", "k9_ocs", "antseg_v10"}


def main():
    rows = [json.loads(l) for l in REG.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if "error" not in r]
    rows.sort(key=lambda r: (r["library"], r["cell_type"]))

    tsv = ["entry_id\tlibrary\troute\tcell_type\tn_genes\tkey_markers\ttextbook_anchor\twiki_pages\t"
           "n_pmids\tn_verified_citations\ttop_citations"]
    lines = ["# Annotation evidence appendix",
             "",
             "Generated from the local knowledge base and the local literature corpus. Every cell-type "
             "entry below carries the three things a reader needs in order to check an annotation: the "
             "markers that identify it, the source the entry came from, and the papers that back it.",
             "",
             f"- entries: **{len(rows)}**",
             f"- distinct papers cited: **{len({c['pmid'] for r in rows for c in r['citations']})}** "
             f"({sum(1 for r in rows for c in r['citations'])} citation rows; "
             f"{sum(1 for r in rows for c in r['citations'] if c.get('gene_match'))} of them state one "
             f"of the marker genes we use in their own text)",
             f"- fully linked (source + page + MCP route + skill): "
             f"**{sum(1 for r in rows if r['n_pmids'] and r['n_wiki_pages'])}**",
             f"- reachable on the default answer surface: "
             f"**{sum(1 for r in rows if r['library'] in DEFAULT_ON)}**",
             "",
             "Citations are drawn from the corpus shipped with this knowledge base, so every PMID below "
             "can be resolved by `search_literature` without network access.",
             "",
             "A citation is marked `states` when the gene symbols of this entry occur in the cited "
             "paper's own full text as standalone words (no substring matches, no case folding). The "
             "location shown is the chunk and section where the first of those symbols was found, so a "
             "reader can open the paper and check. An unmarked citation is a paper about the cell type "
             "whose text does not name our panel genes.",
             ""]

    by_lib = {}
    for r in rows:
        by_lib.setdefault(r["library"], []).append(r)

    for lib, items in by_lib.items():
        route = "default" if lib in DEFAULT_ON else ("textbook layer" if lib == "textbook_t4"
                                                     else "explicit routing only")
        first_col = "term" if lib == "textbook_t4" else "cell type"
        src_col = "source quote" if lib == "textbook_t4" else "key markers"
        lines += [f"## Library `{lib}` ({route}) — {len(items)} entries", "",
                  f"| {first_col} | {src_col} | textbook anchor | wiki page | backing papers |",
                  "|---|---|---|---|---|"]
        for r in items:
            if r.get("source_kind") == "textbook":
                mk = r.get("quote", "")[:110]
            else:
                mk = ", ".join(r["genes_top"][:6])
            anchor = "; ".join(f"{b}, {p}" for b, p in r["book_anchors"][:2]) or "—"
            wiki = ", ".join(r["wiki_pages"][:2]) or "**none**"
            def _c(c):
                if c.get("gene_match"):
                    g = ", ".join(c.get("genes_in_text") or c.get("matched_panel_genes") or [])
                    loc = c.get("evidence_locator") or ""
                    return (f"PMID {c['pmid']} ({c['journal']} {c['year']}) states {g}"
                            + (f" — {loc}" if loc else ""))
                return f"PMID {c['pmid']} ({c['journal']} {c['year']}) — no panel gene in its text"
            if r.get("source_kind") == "textbook":
                cites = "; ".join(f"{b} {p}" for b, p in r.get("book_anchors", [])) or "**none**"
            else:
                cites = "; ".join(_c(c) for c in r["citations"][:3]) or "**none**"
            lines.append(f"| {r['cell_type']} | {mk} | {anchor} | {wiki} | {cites} |")
            tsv.append("\t".join([
                r["entry_id"], r["library"], route, r["cell_type"], str(r["n_genes"]),
                mk, anchor, wiki, str(r["n_pmids"]),
                str(sum(1 for c in r["citations"] if c.get("gene_match"))), cites]))
        lines.append("")

    gaps = [r for r in rows if not r["n_wiki_pages"]]
    unverified = [r for r in rows if r.get("source_kind") == "marker_library" and r["n_pmids"]
                  and not any(c.get("gene_match") for c in r["citations"])]
    no_panel = [r for r in unverified if not (r.get("panel_genes") or [])]
    label_only = [r for r in unverified if r.get("panel_genes")]
    if gaps or label_only or no_panel:
        lines += ["## Known gaps", ""]
        if gaps:
            lines += ["Entries with citations but no written knowledge-base page yet — a reader "
                      "cannot follow the trail further, so these are registered as open items:", ""]
            for r in gaps:
                lines.append(f"- `{r['entry_id']}` — {r['n_pmids']} backing papers, no page")
            lines.append("")
        if label_only:
            lines += ["Entries whose cited papers never name the panel genes in their own text — the "
                      "citations are papers about the cell type, so the trail stops at the label "
                      "rather than the marker:", ""]
            for r in label_only:
                lines.append(f"- `{r['entry_id']}` — {r['n_pmids']} papers, none stating "
                             f"{', '.join(r.get('panel_genes') or [])}")
            lines.append("")
        if no_panel:
            lines += ["Entries that carry no marker panel at all in their source library — nothing "
                      "can be checked against a paper's text until a panel is recorded, so their "
                      "citations stay at the label level:", ""]
            for r in no_panel:
                lines.append(f"- `{r['entry_id']}` — {r['n_pmids']} papers, 0 markers recorded in "
                             f"`{r.get('kb_file')}`")
            lines.append("")

    (OUT / "ANNOTATION_EVIDENCE_APPENDIX_v1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "ANNOTATION_EVIDENCE_APPENDIX_v1.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
    print(f"appendix written: {len(rows)} entries across {len(by_lib)} libraries; "
          f"{len(gaps)} entries without a wiki page")


if __name__ == "__main__":
    main()