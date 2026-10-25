# Annotation evidence coverage

How much of this project's annotation carries a source a reader can follow. One row per cluster; a
cluster the system abstained on carries no label, so it carries no citation.

- clusters: **721** over **1,495,330 cells**
- answered (a label was emitted): **541** clusters / **1,147,640** cells
- answered **and** backed by at least one paper: **541** clusters (100.0% of answered) / **1,147,640** cells (100.0% of answered cells)
- answered with a textbook page anchor as well: **368**
- abstained (no label, no citation - by design): **180** clusters

| library the supporting entry comes from | clusters |
|---|---|
| retina | 305 |
| membrane | 180 |
| k9_ocs | 53 |
| face_v6 | 3 |

Rows flagged `config_dependent` change verdict when a knowledge-base switch is flipped; their label in this table is the one the panel recorded, not necessarily the shipped default.

## How checkable is a citation (knowledge-entry level)

A citation counts as checkable when the cited paper's own full text states at least one of the
marker genes of the entry. Same rule applied before and after the full-text index is wired in.

| library | entries | citation rows | rows whose paper states a marker gene | of those, found by the index rather than the label search | entries with at least one checkable citation |
|---|---|---|---|---|---|
| antseg_v10 | 16 | 406 | 303 (75%) | 128 | 16/16 |
| membrane | 23 | 621 | 296 (48%) | 184 | 23/23 |
| retina | 10 | 269 | 178 (66%) | 80 | 10/10 |
| retina_interneuron | 10 | 270 | 173 (64%) | 80 | 10/10 |
| retina_v6 | 10 | 268 | 173 (65%) | 80 | 10/10 |
| k9_ocs | 4 | 105 | 60 (57%) | 32 | 4/4 |
| face_v6 | 7 | 167 | 58 (35%) | 33 | 5/7 |
| **total** | **80** | **2,106** | **1,241 (59%)** | **617** | **78/80** |

Before the index: 1,489 rows, 624 checkable (41.9%), 361 distinct papers, 75/80 entries.
After: 2,106 rows, 1,241 checkable (58.9%), 497 distinct papers, 78/80 entries.
The paper-level detail, with the chunk and section where each marker was found, is in
`ANNOTATION_EVIDENCE_APPENDIX_v1.md` (machine-readable twin: the `.tsv`).

## Registered gaps

- Two marker entries record **no panel at all** in their source library (`face_v6::Fibroblast`,
  `face_v6::Myofibroblast`), so nothing about them can be checked against a paper's text; their 20
  citations each stay at the label level.
- Two entries have no written page independent of this registry's own generated appendix
  (`membrane::cDC1`, `membrane::cDC2`).
- One marker gene of the 312 scanned (MOBP) occurs nowhere in the corpus.

These are disclosure readings. Nothing here feeds a score, a weighting or a ranking.