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
| membrane | 23 | 810 | 485 (60%) | 373 | 23/23 |
| antseg_v10 | 16 | 978 | 875 (89%) | 700 | 16/16 |
| retina | 10 | 616 | 525 (85%) | 427 | 10/10 |
| retina_interneuron | 10 | 551 | 454 (82%) | 361 | 10/10 |
| retina_v6 | 10 | 464 | 369 (80%) | 276 | 10/10 |
| face_v6 | 7 | 172 | 63 (37%) | 38 | 5/7 |
| k9_ocs | 4 | 144 | 99 (69%) | 71 | 4/4 |
| cl56_v15 | 3 | 181 | 160 (88%) | 126 | 3/3 |
| onfibro_v13 | 1 | 77 | 67 (87%) | 57 | 1/1 |
| **total** | **84** | **3993** | **3097 (78%)** | **2429** | **82/84** |

Table re-taken 2026-10-25
(`plans/consistency_20261024/cl56wire_out/scripts/recompute_summary_table.py --registry
kb/link_registry/LINK_REGISTRY_v1.jsonl`), together with the full-text index it is scored against
(330 panel genes / 10,550 rows). The version it replaces was recorded early in the 2026-10-21 wave
and predates that wave's own extended-evidence pass: its row-count columns read 2,106 citation rows
/ 1,241 checkable while the registry it was computed from already carried 3,735 / 2,870. Its entry
columns and this table agree (the 80 entries of the time, 78 of them with a checkable citation). Two
libraries were added after it: `onfibro_v13` (activated on the default route 2026-10-22) and
`cl56_v15` (registered, default-off, so no cluster-level reading moves).

Before the index (read at the 2026-10-21 full-text-index wave): 1,489 rows, 624 checkable (41.9%),
361 distinct papers, 75/80 entries.
After (same wave): 2,106 rows, 1,241 checkable (58.9%), 497 distinct papers, 78/80 entries.
The paper-level detail, with the chunk and section where each marker was found, is in
`ANNOTATION_EVIDENCE_APPENDIX_v1.md` (machine-readable twin: the `.tsv`).

## Registered gaps

- Two marker entries record **no panel at all** in their source library (`face_v6::Fibroblast`,
  `face_v6::Myofibroblast`), so nothing about them can be checked against a paper's text; their 20
  citations each stay at the label level.
- One marker gene of the 330 scanned (MOBP) occurs nowhere in the corpus.
- Re-taken 2026-10-25, same change as the table above: the shipped version of this section still
  named `membrane::cDC1` / `membrane::cDC2` as reachable only through this registry's generated
  appendix; both gained a written page at the 2026-10-21 link-spine close-out, and the current
  reading of `scripts/audit_link_circularity.py` is: 84 marker entries, 84/84 reachable at all,
  84/84 reachable excluding this registry's own rendered appendix, 0 relying on that appendix alone.

These are disclosure readings. Nothing here feeds a score, a weighting or a ranking.
