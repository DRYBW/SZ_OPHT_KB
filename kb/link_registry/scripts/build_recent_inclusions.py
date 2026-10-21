#!/usr/bin/env python3
"""List the papers in the shipped corpus that no knowledge-base page mentions yet.

The corpus grows with every intake wave; the pages that index it are rebuilt less often, so a paper
can be searchable while being invisible to anyone reading the knowledge base. This script measures
that gap, writes the missing papers into one page grouped by tissue, and reports the count before
and after - so the closing of the gap is a number, not a claim.

Inputs are arguments (no host paths): the corpus's papers.jsonl, the knowledge-base directory to
scan for existing mentions, and the output page path.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

# A corpus paper is identified either by a numeric PubMed id or, for preprints, by a preprint id
# such as PPR_PPR1308284. Both count: what matters is that a reader can find the paper on a page.
ID_RE = re.compile(r"(?:PMID[:\s]*(\d{6,9}))|(PPR_?PPR\d{5,9})")


def mentioned_ids(kb_dir, exclude=None):
    """Identifiers recorded on the knowledge-base pages. The output page itself is excluded, so
    re-running the script measures the same gap instead of finding its own previous output."""
    out = set()
    exclude = Path(exclude).resolve() if exclude else None
    for p in Path(kb_dir).glob("**/*.md"):
        if exclude and p.resolve() == exclude:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in ID_RE.finditer(txt):
            out.add(m.group(1) or m.group(2))
    return out


def id_label(pid):
    return f"PMID {pid}" if str(pid).isdigit() else f"Preprint {pid}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", required=True, help="papers.jsonl of the corpus")
    ap.add_argument("--kb-dir", required=True, help="knowledge-base directory to scan for mentions")
    ap.add_argument("--out", required=True, help="page to write")
    ap.add_argument("--tsv", default="", help="optional full listing as TSV")
    ap.add_argument("--per-tissue-cap", type=int, default=0,
                    help="0 = list every paper; N = cap rows per tissue and state the remainder")
    args = ap.parse_args()

    papers = []
    for line in Path(args.papers).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            papers.append(json.loads(line))
    have = mentioned_ids(args.kb_dir, exclude=args.out)

    missing = []
    for d in papers:
        pid = str(d.get("paper_id") or "")
        if pid and pid not in have:
            tl = d.get("tissues") or []
            missing.append({
                "pmid": pid,
                "year": str(d.get("year") or ""),
                "journal": (d.get("journal") or "").strip(),
                "title": (d.get("title") or "").strip(),
                "tissues": [str(t) for t in tl] if isinstance(tl, list) else [str(tl)],
                "n_chunks": d.get("n_chunks") or 0,
                "is_preprint": int(d.get("is_preprint") or 0),
            })
    missing.sort(key=lambda r: (-int(r["year"] or 0), r["journal"], r["pmid"]))

    by_tissue = defaultdict(list)
    multi = 0
    for r in missing:
        if len(r["tissues"]) > 1:
            multi += 1
        for t in (r["tissues"] or ["unlabelled"]):
            by_tissue[t or "unlabelled"].append(r)

    lines = ["# Papers in the shipped corpus that no page listed yet",
             "",
             "The corpus is updated more often than the pages that index it, so a paper can be searchable "
             "while staying invisible to a reader following the knowledge base. This page closes that gap: "
             "every paper shipped with this knowledge base now appears on some page.",
             "",
             f"- papers in the corpus: **{len(papers)}**",
             f"- identifiers recorded across the knowledge base before: **{len(have)}**",
             f"- papers no page mentioned before this page existed: **{len(missing)}** "
             f"({len(missing)/max(len(papers),1)*100:.1f}% of the corpus)",
             f"- of them, carried by more than one tissue label: {multi}",
             f"- preprints in that set: {sum(1 for r in missing if r['is_preprint'])} "
             f"(identified by a preprint id rather than a PubMed id)",
             "",
             "Full text is retrievable with `search_literature`; the PMID below is what to cite.",
             ""]
    for tissue in sorted(by_tissue, key=lambda t: -len(by_tissue[t])):
        rows = by_tissue[tissue]
        cap = args.per_tissue_cap
        shown = rows if not cap else rows[:cap]
        lines += [f"## {tissue} — {len(rows)} papers", "",
                  "| PMID | year | journal | title |", "|---|---|---|---|"]
        for r in shown:
            title = r["title"].replace("|", "/")[:150]
            lines.append(f"| {id_label(r['pmid'])} | {r['year']} | {r['journal'][:52]} | {title} |")
        if cap and len(rows) > cap:
            lines.append(f"| | | | _{len(rows)-cap} more, in the TSV listing_ |")
        lines.append("")
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.tsv:
        cols = ["pmid", "year", "journal", "title", "tissues", "n_chunks", "is_preprint"]
        with Path(args.tsv).open("w", encoding="utf-8") as fh:
            fh.write("\t".join(cols) + "\n")
            for r in missing:
                fh.write("\t".join([r["pmid"], r["year"], r["journal"], r["title"],
                                    ",".join(r["tissues"]), str(r["n_chunks"]),
                                    str(r["is_preprint"])]) + "\n")

    after = len(mentioned_ids(args.kb_dir))
    print(f"corpus={len(papers)} mentioned_before={len(have)} unlisted={len(missing)} "
          f"tissues={len(by_tissue)} mentioned_after={after}")
    print(f"wrote {args.out}" + (f" and {args.tsv}" if args.tsv else ""))


if __name__ == "__main__":
    main()