#!/usr/bin/env python3
"""Build a gene -> paper index over the literature corpus shipped with this knowledge base.

Why this exists
---------------
The corpus carries a per-chunk `marker_genes` column, but it is sparse: it lists a handful of
symbols per chunk, not every gene the chunk mentions. So a citation could only be tagged
"this paper mentions RPE65" when the sparse column happened to record RPE65, and most real
mentions were invisible. A reader checking a report could not tell whether a cited paper
actually discusses the genes the annotation uses.

This script scans the **full text** of every chunk and records, per (gene, paper), where the
symbol occurs. The result is a lookup table: given a panel gene, which papers in this corpus
contain it, in how many chunks, and in which sections.

Matching rule (deliberately strict, because a false "this paper mentions X" is worse than a miss)
-----------------------------------------------------------------------------------------------
An occurrence counts when the gene symbol appears as a standalone uppercase token, delimited by
non-alphanumerics on both sides, in the chunk text. No case folding (gene symbols are written
uppercase), no substring matching, no fuzzy match. A mismatch therefore cannot come from a
substring accident such as `AC` inside `RAC1` or `TTR` inside `ATTR`.

Outputs
-------
  out/GENE_PAPER_INDEX_v1.tsv    gene, paper_id, n_chunks, sections, example_chunk
  out/GENE_PAPER_INDEX_v1.json   provenance + headline counts

No network access. The index is rebuilt from the local corpus, so the same corpus reproduces the
same table on any machine.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out"
REG = HERE.parent / "LINK_REGISTRY_v1.jsonl"


def _repo_root(start):
    p = start
    for _ in range(6):
        if (p / "kb").is_dir() and (p / "mcp_server").is_dir():
            return p
        p = p.parent
    raise SystemExit("repository root not found from " + str(start))


ROOT = _repo_root(HERE)


def corpus_dir():
    """The corpus the retrieval service resolves as its default.

    Resolved through the service's own chain (EYEKB_DB_DIR, then the pointer's role:default entry,
    then the single bundled corpus) rather than by a path written here, so this index always covers
    the same papers the citations were drawn from. An index built over a different library would
    silently verify papers that search_literature cannot resolve, which is exactly the claim the
    appendix makes to a reader.
    """
    env = os.environ.get("EYEKB_DB_DIR")
    if env:
        return Path(env)
    try:
        sys.path.insert(0, str(ROOT / "mcp_server"))
        import eyekb_core as core
        return Path(core._default_db_dir())
    except Exception as exc:                                     # noqa: BLE001
        # Fall back to the repository's own library directory, if it carries exactly one corpus.
        cands = sorted(d for d in (ROOT / "kb" / "literature_db").glob("*")
                       if (d / "chunks.parquet").is_file())
        if len(cands) == 1:
            return cands[0]
        raise SystemExit(f"cannot resolve the corpus (service lookup failed: {exc}); "
                         f"set EYEKB_DB_DIR to the library directory")


CORPUS = corpus_dir() / "chunks.parquet"
PAPERS = CORPUS.parent / "papers.jsonl"

# Standalone uppercase token, non-alphanumeric on both sides, hyphens allowed inside so that
# symbols written with a dash (HLA-DRA, IGHG1-2) are seen as one token. Length >= 2 so
# one-letter symbols cannot collide with roman numerals or amino-acid letters.
TOKEN = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)(?![A-Za-z0-9])")


def _variants(sym):
    """A symbol counts in both its dashed and undashed spelling."""
    up = sym.upper()
    return {up, up.replace("-", "")}


def panel_genes():
    genes = set()
    for line in REG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        for g in r.get("genes_top") or []:
            if isinstance(g, str) and len(g) >= 2:
                genes.add(g.upper())
    return genes


def main():
    try:
        import pyarrow.parquet as pq
    except ImportError:                                          # pragma: no cover
        sys.exit("pyarrow is required to read the corpus parquet")
    if not CORPUS.is_file():
        sys.exit(f"corpus not found: {CORPUS}")

    genes = panel_genes()
    # a token resolves to the canonical panel symbol whether or not it is written with a dash
    lookup = {}
    for g in genes:
        for v in _variants(g):
            lookup.setdefault(v, g)
    print(f"panel genes: {len(genes)} ({len(lookup)} accepted spellings)")

    # gene -> paper_id -> [n_chunks, set(sections), locator, body_hits]
    # `body_hits` counts mentions that sit in a paragraph rather than the abstract, because
    # "the symbol appears in this paper's body text" is the check a reader can actually make.
    hits = {}
    t0 = time.time()
    n_chunks = 0
    ordinal = {}
    pf = pq.ParquetFile(CORPUS)
    for batch in pf.iter_batches(batch_size=4000,
                                 columns=["paper_id", "text", "section", "chunk_type"]):
        pids = batch.column("paper_id").to_pylist()
        txts = batch.column("text").to_pylist()
        secs = batch.column("section").to_pylist()
        cts = batch.column("chunk_type").to_pylist()
        for pid, txt, sec, ct in zip(pids, txts, secs, cts):
            n_chunks += 1
            k = ordinal.get(pid, 0) + 1
            ordinal[pid] = k
            if not txt:
                continue
            found = {lookup[t] for t in set(TOKEN.findall(txt)) if t in lookup}
            for g in found:
                per_gene = hits.setdefault(g, {})
                rec = per_gene.get(pid)
                if rec is None:
                    per_gene[pid] = [1, {sec or ""}, f"{ct}:{k}", int(ct == "paragraph")]
                else:
                    rec[0] += 1
                    rec[3] += int(ct == "paragraph")
                    if len(rec[1]) < 12:
                        rec[1].add(sec or "")
    elapsed = time.time() - t0

    # join paper metadata (journal / year / species / preprint flag)
    meta = {}
    for line in PAPERS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        meta[str(p["paper_id"])] = p

    OUT.mkdir(parents=True, exist_ok=True)
    lines = ["gene\tpaper_id\tjournal\tyear\tspecies\tis_preprint\tn_chunks\tn_body_chunks\tsections\tlocator"]
    n_rows = 0
    papers_hit = set()
    genes_hit = set()
    body_only = 0
    for g in sorted(hits):
        for pid, (n, secs, loc, body) in sorted(hits[g].items(), key=lambda kv: -kv[1][0]):
            m = meta.get(pid, {})
            lines.append("\t".join([
                g, pid, str(m.get("journal", "")), str(m.get("year", "")),
                str(m.get("species", "")), str(m.get("is_preprint", "")),
                str(n), str(body), "|".join(sorted(s for s in secs if s)), loc]))
            n_rows += 1
            papers_hit.add(pid)
            genes_hit.add(g)
            body_only += int(body == 0)
    (OUT / "GENE_PAPER_INDEX_v1.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    stat = {
        "corpus": str(CORPUS),
        "corpus_bytes": CORPUS.stat().st_size,
        "corpus_mtime": int(CORPUS.stat().st_mtime),
        "panel_genes_scanned": len(genes),
        "panel_genes_with_hits": len(genes_hit),
        "genes_without_hits": sorted(genes - genes_hit),
        "papers_with_any_hit": len(papers_hit),
        "index_rows": n_rows,
        "rows_seen_in_abstract_only": body_only,
        "chunks_scanned": n_chunks,
        "match_rule": ("standalone uppercase token, non-alphanumeric delimited, dashed and "
                       "undashed spellings both accepted, no case folding, no substring match"),
        "seconds": round(elapsed, 1),
    }
    (OUT / "GENE_PAPER_INDEX_v1.json").write_text(
        json.dumps(stat, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"chunks {n_chunks} in {elapsed:.1f}s; {len(genes_hit)}/{len(genes)} panel genes found "
          f"in {len(papers_hit)} papers; index rows {n_rows}")
    if stat["genes_without_hits"]:
        print("genes absent from the whole corpus:", ", ".join(stat["genes_without_hits"][:20]))


if __name__ == "__main__":
    main()