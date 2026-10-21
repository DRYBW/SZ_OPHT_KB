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

## The rule

`validate_linkage.py` fails whenever any entry has an empty citation list, no page, no route or no
skill entry point, and prints each dead end by name. The gate exists because an unwritten page is
invisible in review: the entry still answers queries, so nothing looks broken until a reader tries
to check it. Run it after any content change:

```bash
python3 validate_linkage.py      # exit 0 = every entry is reachable end to end
```

## Rebuilding

```bash
python3 scripts/build_link_registry.py    # rebuild every row from the local knowledge base
python3 scripts/build_citation_appendix.py  # render the reader-facing appendix
python3 validate_linkage.py               # the gate above
```

Citations come only from the local corpus — no network access, so a rebuild reproduces the same
PMIDs on any machine that ships the same library.

## Evidence discipline

The registry is a **disclosure** surface. It reports where an annotation's support comes from; it
must not be used as an input to any score, weighting, ranking or confidence measure. The same
red line that applies to the retrieval service applies here.