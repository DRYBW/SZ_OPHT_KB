# Linkage spine — how a knowledge entry stays connected

A knowledge entry is only useful if a reader can follow the trail from a cell-type name to the
papers behind it. This directory holds the link registry that makes that trail explicit, plus the
rule that keeps it from rotting.

## The five links

Every entry carries five fields. A field that is empty is a **dead end**: a reader arrives and
cannot go further.

| field | question it answers | source |
|---|---|---|
| `entry_id` / `library` | which knowledge base does this entry belong to | the marker library the entry lives in |
| `genes_top` / `n_genes` | what identifies this cell type here | the curated marker panel |
| `wiki_pages` | where is this written up for humans | pages under `kb/` |
| `pmids` / `citations` | which papers back it | the literature corpus shipped with this knowledge base |
| `mcp_route` | how does a client fetch it programmatically | `query_marker(...)` / `explain_annotation(...)` |

`book_anchors` is a sixth, optional field: the textbook edition and page the definition comes
from, when the definition is anatomical rather than transcriptional.

## Checking a citation, not just reading it

A citation is only worth something if a reader can open the paper and see the evidence. Each
citation therefore carries `genes_in_text` — the marker genes of that entry which occur in the
cited paper's **own full text** — plus `evidence_locator`, the chunk and section where the first of
them was found, and `evidence_source`, which says whether the paper came from the corpus search or
was found through the gene index.

The index behind this is `out/GENE_PAPER_INDEX_v1.tsv`, built by `scripts/build_gene_paper_index.py`.
It scans every chunk of the shipped corpus and records, per (gene, paper), how often and where the
symbol occurs. The match rule is deliberately narrow: a standalone uppercase token bounded by
non-alphanumerics, dashed and undashed spellings both accepted, no case folding and no substring
matching. A false "this paper mentions our marker" would be worse than a miss, so `AC` is not
allowed to match `RAC1`.

The index is built against the same library the retrieval service resolves as its default
(`EYEKB_DB_DIR`, then the pointer's `role: default` entry), so a citation marked verified is one
`search_literature` can also resolve.

## The rule

`validate_linkage.py` fails whenever any entry has an empty citation list, no page, no route or no
skill entry point, and prints each dead end by name. It also fails when a citation is marked
gene-verified but the shipped index has no row for it — otherwise the flag could be asserted by
hand and nothing would notice. The gate exists because an unwritten page is invisible in review:
the entry still answers queries, so nothing looks broken until a reader tries to check it.

```bash
python3 validate_linkage.py      # exit 0 = every entry is reachable end to end
```

Two further readings ship alongside the gate, because a single number hides the difference between
a written page and a generated one:

- `scripts/audit_link_circularity.py` — how many entries are reachable at all, versus how many are
  reachable **excluding the registry's own rendered appendix**. The appendix lists every label, so
  counting it as an entry's page is circular; the second number is the honest one.
- `scripts/measure_citation_verification.py` — the verified share of citations, before and after the
  gene index is wired in, scored by the same rule on both sides.

## Looking an entry up by its standard name

The registry is keyed by each library's own short name (`MG`, `Rod`, `BC`). A reader who instead
uses the **Cell Ontology** label for the same cell (`Mueller cell`, `retinal rod cell`, `amacrine
cell`) should land on the same record rather than being told the cell type is unknown. The service
resolves that through the alignment pinned in `kb/markers/markers_cl_alignment_v2_unified.json`, and
reports which route matched in `matched_by` (`library name` / `cell ontology label` / `partial
name`). This is a lookup widening only — it does not add, rename or merge any entry.

## Rebuilding

```bash
python3 scripts/build_gene_paper_index.py    # gene -> paper index over the shipped corpus
python3 scripts/build_link_registry.py       # rebuild every row, using that index
python3 scripts/build_citation_appendix.py   # render the reader-facing appendix
python3 validate_linkage.py                  # the gate above
```

Run the index first: the registry consumes it. Citations come only from the local corpus — no
network access, so a rebuild reproduces the same PMIDs on any machine that ships the same library.

## Evidence discipline

The registry is a **disclosure** surface. It reports where an annotation's support comes from; it
must not be used as an input to any score, weighting, ranking or confidence measure. The same
red line that applies to the retrieval service applies here.