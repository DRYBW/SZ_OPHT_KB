# Annotation evidence coverage

How much of this project's annotation carries a source a reader can follow. One row per cluster; a cluster the system abstained on carries no label, so it carries no citation.

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

