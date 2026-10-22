# PRE-REGISTRATION ANNEX A — operationalisations (fixed before any readiness number exists)

Written: 2026-10-22 10:2x CST · companion to `PREREG_SUBDIVISION_READINESS_20261022.md` (thresholds, §2 there, are
frozen and are **not** changed here). This annex fixes only the mechanical operations, so that the operations cannot
be chosen after results are seen. If an operation below turns out to be wrong, the deviation is recorded as a
deviation in the wave REPORT — the threshold is not moved.

## A1 Discovery corpus and evaluation set

| role | artefact |
|---|---|
| discovery (literature) | `/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/chunks.parquet` (3,902 papers / 244,877 chunks) |
| discovery cross-check | `/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/chunks.parquet` (the shipping library) |
| evaluation | the 28 volumes under `/mnt/D/EyeKB/plans/oss_check_20261019/dl/workdir/*/input.h5ad`, 721 recorded clusters |
| fixed ontology | `/mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo`, release `cl/releases/2026-06-08`, sha256 `c6274fb65cdf740b983a06b74cb678814249d7f8e580c2ec9de54bf204a2b1c7` |

**Evaluation-source handles that can be searched for**: the accessions recoverable from the volumes' own derive
records (`GSE199013`, `GSE268630`) plus the 28 volume ids. A discovery paper carrying one of those handles is moved
to the evaluation-source set and excluded from gene/candidate evidence. For the 22 cellxgene-hosted volumes no local
accession handle exists, so their overlap is reported as `NOT_RUN` with the reason — **never as zero**.

## A2 Candidate child names

Per parent, the candidate child names are the **preferred names of its `is_a` descendants** in the fixed snapshot
(652 distinct terms over the 76 parents). Nothing else enters the candidate list. A term that is a descendant of two
shipped parents is evaluated under each parent separately.

## A3 Target context (per parent, read from disk — not typed)

For each library named in the dictionary's `libraries` block, read `kb/markers/<file>` and take the declared
vocabulary from the keys `scope_tissues`, `applicability`, `scope`, `species`, `organism_stage`,
`development_stage`. Tissue tokens are matched against the corpus's own 12-label tissue vocabulary; the key each
tissue token was read from is recorded as provenance. Parent context = union over the parent's libraries. Stage is
`fetal_developing` iff a contributing library declares a fetal/developing stage; otherwise `adult`. System is
`organoid_or_ipsc` iff a contributing library's scope names organoid/iPSC; otherwise `in_vivo`.

## A4 Occurrence in the target context (field 2)

A chunk supports candidate *c* under parent *P* iff the chunk's text contains *c*'s preferred name (case-insensitive,
word-boundary) **and** the chunk's `species` ∈ {human, both} **and** the chunk's `tissue`/`tissue_labels` intersects
*P*'s tissue set. Synonyms are checked only as a secondary channel for names with zero preferred-name hits, reported
separately as `occurrence_via_synonym`.

## A5 Independent sources (field 3)

* `n_indep_studies` = distinct `paper_id` among the chunks covering *c* under *P*; chunk and row counts are recorded
  but are never used as the study count.
* `n_indep_cohorts` = distinct local datasets outside the evaluation set that carry *c*'s term (field 7 scan).
* `n_indep_sources` = `n_indep_studies` + `n_indep_cohorts` (a study and a cohort are distinct units; neither is
  counted twice).
* `has_adjacent_type_contrast` = ≥ 1 source (paper) containing a single chunk in which *c* **and** at least one sibling
  name of the same parent co-occur together with contrast language, from the pre-registered regex
  `differ|distinct|versus|\bvs\b|contrast|discriminat|separate|distinguish|unique to|specific to|unlike|whereas`.

## A6 Genes (field 4)

Cells in the discovery corpus are tokenised with `\b[A-Z][A-Z0-9]{1,13}(?:-[A-Z0-9]{1,6})?\b`; a token counts as a
gene iff it is in the local gene vocabulary `/mnt/D/EyeKB/plans/antseg_fill_20261020/out/gene_vocab.json`
(42,267 symbols — the symbols the shipped panels can measure). The corpus's own `marker_genes` column is used as a
second channel where populated.

* **positive gene of *c*** = a gene seen in ≥ 2 distinct studies inside *c*'s covered chunks (A4 context).
* **parent-shared gene of *P*** = a gene positive for ≥ 2 distinct candidate children of *P*. Removed from every
  child's evidence before any threshold is applied (ruling §C2).
* **nearest sibling of *c*** = the sibling *s* (same *P*) maximising |positive(*c*) ∩ positive(*s)*|; ties broken by
  the smaller `is_a` graph distance, then alphabetically.
* **discriminating positive genes of *c*** = positive(*c*) \ positive(*s*) \ parent-shared(*P*).

## A7 State programme (field 5)

The state reference is built from local material only: the union of (a) the genes of the dictionary's own
proliferation entries (`Proliferating`, `Retinal_Proliferating`, `TAC_proliferating`), (b) the genes recorded in the
disease thin layer `kb/priors/disease/*.json`, and (c) the positive genes of discovery-corpus chunks whose text
matches `cell cycle|mitotic|proliferat|MKI67|TOP2A` for the cell-cycle arm, or a disease/treatment token for the
disease/treatment arm. `state_fraction` = |discriminating positive genes ∩ state reference| / |discriminating positive
genes|. Threshold `T-STATE` (< 0.50) is from the pre-registration and is not changed.

## A8 Observability (field 6)

The interface's current window is the recorded top-10 gene list of each of the 721 clusters; the observable
vocabulary is their union. `n_observable` = |discriminating positive genes ∩ observable vocabulary|. This is a
**probing/regression reading on the fixed 28-volume set**, not validation. Absence from the window is never treated as
evidence that a gene or class does not exist (T-NONEG).

## A9 Independent non-evaluation material (field 7)

A local expression file is a candidate iff (a) it is not under the evaluation tree
`/mnt/D/EyeKB/plans/oss_check_20261019/`, and (b) its path does not contain any evaluation cohort alias
(`CX01`–`CX17`, `PRE_OA-D001/2/4/68`, `GSE199013`, `GSE268630`, `OA-D001/2/4/68`). Each candidate is opened
`backed='r'` and its `obs` string columns are scanned for labels resolving (CL preferred name or synonym) to *c* or
to a descendant of *c*. A file that cannot be opened is reported `NOT_RUN` for that file, with its path, and is never
counted as a negative.

## A10 Cost (card item 6)

Re-measured with the recorded 721-cluster set exactly as holefill §5 defines demand / gain / keep / loss, using the
child panels built under A6 and the parent's shipped panel. Reported as a probing reading against the fixed reference.