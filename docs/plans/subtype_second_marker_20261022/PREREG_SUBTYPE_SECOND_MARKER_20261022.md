# PRE-REGISTRATION — a second discriminating marker for the 26 thin subtype panels (literature only; registered default OFF)

Date: 2026-10-22 · Card: `t_7509a1a2` (SUBTYPE-2M) · board `pi-briefing`
Upstream acceptance criteria: `plans/subtype_markers_20261022/BRIEF_SUBTYPE_SECOND_MARKER_20261022.md`
Frozen wave under extension: `plans/consensus_subtype_20261022/` (report + ruler + result)

## 0. Disclosure — what was read before this document was frozen

Ordering matters, so it is stated rather than implied.

Read **before** writing this file (all of it frozen upstream material or file-system reconnaissance, none
of it gene-level content from our own volumes):

| # | Read | Why | Was it a measurement of a result? |
|---|---|---|---|
| R1 | `plans/consensus_subtype_20261022/{REPORT.md, PREREG_CONSENSUS_SUBTYPE_20261022.md, SUPERSEDED_LOGS_20261022.md}`, `out/SUBTYPE_SEPARATION.json/.tsv`, `out/SUBTYPE_OBSERVABILITY_rows.json`, `out/G1..G3*.json`, `out/_marker_genes.json`, `scripts/c2_observability.py`, `scripts/c3_separation.py` | the frozen result, the ruler, and the literature entries | no — these are the inputs the card names |
| R2 | the corpus schema: column names of `chunks.parquet`; the distinct vocabulary of its `cell_type_mentioned` column (31 values) and of its `marker_genes` column (40 values); the number of chunks mentioning each in-scope subtype name | to write a **runnable** name-matching rule (the corpus's structured cell-type field is parent-level only — `BC`/`AC`/`HC` — so subtype evidence has to come from text) | **partly**: it establishes that the corpus has 15 / 7 / 7 / … chunks per subtype name. No gene was looked at, no volume was read, no separation was computed. |
| R3 | the machine's literature holdings inventory (`rag/literature_db/v2.6-dev_2026-10/`, `kb/vk_literature_index/`, `kb/textbook_layer/`) | to fix which corpora count as "literature already held on this machine" | no |
| R4 | the house pattern for a registered-but-OFF increment (`docs/plans/noregr_20261022/`, `kb/markers/markers_v13_onfibro_increment.json`, `mcp_server/eyekb_core.py`) | to register the increment the way this repository does | no |

Read **after** this file is on disk: the corpus text at gene level, the seven volumes, the ruler's
re-run, the flip table. **No threshold in this document was chosen after seeing a gene-level result.**
The only pre-frozen number that was *seen* before writing is the count of name-mentioning chunks (R2);
it is reported here so the reader can judge that choice, and it is not used to set any threshold.

## 1. The question, and what "answer" means

The frozen wave scored 56 subtype-by-volume rows (`separated` 12 / `not_separated` 36 /
`insufficient_evidence` 8). **26 of the 36 `not_separated` rows fail for one reason: exactly one
marker clears the pre-registered gate and no second one does** — e.g. flat midget bipolar `GRIK1`
AUC 0.81 with `VSX2` at 0.47, where `VSX2` is expressed in every bipolar cell. The panel is one gene
thick.

This card asks: for each such subtype, can **literature** supply a second defining marker that is
measurable in these volumes, and does the panel then clear its own pre-registered gate?

## 2. The in-scope set (26 rows / 16 subtypes), pinned mechanically

Selection rule (applied to the frozen `out/SUBTYPE_SEPARATION.json`, sha256 recorded by `m0`):
`result == "not_separated"` **and** `reason` starts with `1 marker(s) cleared the gate`. That rule
yields exactly 26 rows and 16 distinct subtypes; the row set is enumerated below so a re-run can be
diffed against it rather than re-derived.

| volume | subtype | n_cells | the one marker that cleared | the marker(s) that did not |
|---|---|---|---|---|
| CX01_retina_snRNA | flat midget bipolar cell (FMB) | 3225 | GRIK1 0.81 | VSX2 0.47 |
| CX01_retina_snRNA | diffuse bipolar 2 (DB2) | 3225 | GRIK1 0.90 | VSX2 0.52 |
| CX01_retina_snRNA | diffuse bipolar 3a (DB3a) | 3225 | GRIK1 0.76 | VSX2 0.42 |
| CX01_retina_snRNA | diffuse bipolar 3b (DB3b) | 3225 | GRIK1 0.89 | VSX2 0.52 |
| CX01_retina_snRNA | diffuse bipolar 4 (DB4) | 3225 | GRM6 0.81 | VSX2 0.40 |
| CX01_retina_snRNA | diffuse bipolar 6 (DB6) | 3225 | GRM6 0.74 | SCGN 0.50 |
| CX01_retina_snRNA | blue-cone bipolar cell (BB) | 2931 | GRM6 0.72 | VSX2 0.58 |
| CX01_retina_snRNA | giant bipolar cell (GB) | 3225 | UTRN 0.91 | — (single-marker panel) |
| CX01_retina_snRNA | H1 horizontal cell | 3225 | LHX1 0.76 | SPP1 0.44 |
| CX01_retina_snRNA | H2 horizontal cell | 3225 | ISL1 0.71 | SPP1 0.56 |
| CX03_retina_multiome | ON cone bipolar cell (ON BC) | 2617 | TRPM1 0.73 | GRM6 0.69, ISL1 0.53, ST18 0.57 |
| CX03_retina_multiome | OFF cone bipolar cell (OFF BC) | 3936 | GRIK1 0.99 | FEZF2 0.60, LHX3 0.52 |
| CX04_cowan_fovea | rod bipolar cell (RBC) | 1016 | PRKCA 0.90 | TRPM1 0.56, VSTM2B 0.69 |
| CX04_cowan_organoid | OFF cone bipolar cell (OFF BC) | 686 | GRIK1 0.75 | FEZF2 0.62, LHX3 0.58 |
| CX04_cowan_periphery | OFF cone bipolar cell (OFF BC) | 1470 | GRIK1 0.85 | FEZF2 0.68, LHX3 0.57 |
| PRE_GSE268630 | invaginating midget bipolar cell (IMB) | 1466 | GRM6 0.79 | VSX2 0.38 |
| PRE_GSE268630 | flat midget bipolar cell (FMB) | 3571 | GRIK1 0.78 | VSX2 0.46 |
| PRE_GSE268630 | diffuse bipolar 2 (DB2) | 2371 | GRIK1 0.82 | VSX2 0.51 |
| PRE_GSE268630 | diffuse bipolar 3b (DB3b) | 2704 | GRIK1 0.76 | VSX2 0.60 |
| PRE_GSE268630 | diffuse bipolar 4 (DB4) | 291 | GRM6 0.89 | VSX2 0.52 |
| PRE_GSE268630 | diffuse bipolar 6 (DB6) | 429 | GRM6 0.89 | SCGN 0.50 |
| PRE_GSE268630 | H1 horizontal cell | 477 | LHX1 0.79 | SPP1 0.58 |
| PRE_GSE268630 | H2 horizontal cell | 928 | ISL1 0.72 | SPP1 0.52 |
| PRE_OA-D001 | starburst (cholinergic) amacrine cell | 986 | SLC5A7 0.91 | SLC18A3 0.69, CHAT 0.67 |
| PRE_OA-D001 | H2 horizontal cell | 1858 | ISL1 0.73 | SPP1 0.70 |
| PRE_OA-D001 | parasol retinal ganglion cell | 446 | SPP1 0.85 | RBPMS2 0.62, CHRNA2 0.66, CA8 0.51 |

The 16 distinct subtypes are the **in-scope subtypes**. A gene is proposed for a subtype, not for a
row; whether a row can move is decided by whether the proposal is measurable *in that volume* (§5).

**Not in scope** (deliberately): the 12 already-`separated` rows, the 8 `insufficient_evidence` rows,
and the 2 `not_separated` rows that fail with **zero** markers clearing the gate. Adding a second
marker to a zero-marker panel is a different (and much weaker) claim, and the card scopes this wave
to the one-gene-thick pattern.

## 3. Name forms — declared before mining

The corpus's structured `cell_type_mentioned` field stops at parent level (`BC`, `AC`, `HC`, `RGC`),
so subtype evidence must be taken from chunk **text**. The name forms below are the literature's own
names (from the frozen 94-entry list) and their ordinary abbreviations. They are fixed now.

| # | in-scope subtype | name forms (case-insensitive) used to put a chunk in the subtype's context |
|---|---|---|
| 1 | flat midget bipolar cell (FMB, OFF midget bipolar) | `flat midget bipolar`, `OFF midget bipolar`, `FMB`, `midget bipolar` |
| 2 | invaginating midget bipolar cell (IMB, ON midget bipolar) | `invaginating midget bipolar`, `ON midget bipolar`, `IMB`, `midget bipolar` |
| 3 | diffuse bipolar 2 (DB2) | `diffuse bipolar 2`, `DB2` |
| 4 | diffuse bipolar 3a (DB3a) | `diffuse bipolar 3a`, `DB3a` |
| 5 | diffuse bipolar 3b (DB3b) | `diffuse bipolar 3b`, `DB3b` |
| 6 | diffuse bipolar 4 (DB4) | `diffuse bipolar 4`, `DB4` |
| 7 | diffuse bipolar 6 (DB6) | `diffuse bipolar 6`, `DB6` |
| 8 | giant bipolar cell (GB) | `giant bipolar` |
| 9 | blue-cone bipolar cell (BB, S-cone ON bipolar) | `blue-cone bipolar`, `blue cone bipolar`, `S-cone ON bipolar` |
| 10 | H1 horizontal cell | `H1 horizontal` |
| 11 | H2 horizontal cell | `H2 horizontal`, `HII horizontal`, `horizontal cell H2` |
| 12 | ON cone bipolar cell (ON BC) | `ON cone bipolar`, `ON bipolar cell` |
| 13 | OFF cone bipolar cell (OFF BC) | `OFF cone bipolar`, `OFF bipolar cell` |
| 14 | rod bipolar cell (RBC, ON rod bipolar) | `rod bipolar` |
| 15 | starburst (cholinergic) amacrine cell | `starburst`, `cholinergic amacrine` |
| 16 | parasol retinal ganglion cell | `parasol` |

Deliberate exclusions from this table, because they are a **different axis** or a **parent standing in
for a child**: bare `BB`, `RBC`, `GB`, `H1`, `H2`, `DB` (ambiguous acronyms); `bipolar cell`,
`cone bipolar`, `horizontal cell`, `amacrine cell`, `retinal ganglion cell` (parent level — the frozen
wave already refuses parent labels as evidence, and this wave inherits that refusal).

## 4. Candidate generation — literature only, three declared channels

A candidate is a **gene symbol**. Generation never looks at our own volumes.

* **Channel A — the project literature corpus** `rag/literature_db/v2.6-dev_2026-10/chunks.parquet`
  (the superset lineage used by the immediately preceding wave; 244,877 chunks / 3,902 papers;
  sha256 recorded by `m0`). A chunk is *in the subtype's context* when any name form of §3 occurs in
  its `text`. A gene symbol `g` is *co-mentioned* for that subtype when `g` and a name form occur in
  the **same sentence** of the same chunk (`[.!?]`-delimited span, snippet ≤ 320 chars, kept verbatim).
* **Channel B — the sources the frozen wave already fetched.** Each entry of `out/G1..G3*.json`
  carries `sources[]` with an `id` (PMID/DOI), a `url_fetched` and a `what_it_supports` statement.
  A gene symbol appearing in the same `;`-delimited clause as a declared name form is a candidate.
  This channel reuses the *already-fetched* literature and requires no new source.
* **Channel C — the rest of the literature held on this machine**: `kb/vk_literature_index/*.md` and
  `kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl`, same sentence-level co-mention rule as channel A.

Symbol extraction: uppercase tokens `\b[A-Z][A-Z0-9]{1,13}\b`, kept only if the token is in the
**assay/volume gene vocabulary** (`plans/antseg_fill_20261020/out/gene_vocab.json`, 42,267 symbols) —
i.e. a symbol the material can express at all. This is a vocabulary filter, not an expression filter:
no volume is read to generate candidates.

## 5. Admission rule (fixed now)

Let `P(g, S)` = the set of distinct papers in which gene `g` is sentence-co-mentioned with subtype `S`
(channels A+C), and `A(g, S)` = the channel-B clause hits (paper ids from the frozen sources).

| id | rule |
|---|---|
| **L1** | `g` clears L1 for `S` iff **`|P(g,S)| ≥ 2`** (two distinct papers — the same "two independent sources" bar the frozen C1 wave uses), **or** `g` is named in a channel-B clause of an already-fetched source together with `S`'s name form. |
| **L2** | `g` ∈ the assay gene vocabulary (42,267 symbols). |
| **L3** | `g` is **not** already one of `S`'s `defining_markers` in the frozen 94-entry list. (Duplicate = nothing added.) |
| **L4** | `g` is **not** a pan-family symbol: if `g` clears L1 for **≥ 3 distinct in-scope subtypes**, it is rejected for all of them. Rationale, and it is a literature-side rule: a symbol the literature attaches to three or more sibling subtypes is not a discriminator between them — this is exactly the failure mode `VSX2` exhibits, and the rule must be able to reproduce it mechanically rather than by inspection. |
| **L5** | cap: at most **K = 2** added candidates per subtype, ranked by `(|P| desc, |A| desc, symbol asc)`. The cap bounds the multiple-testing burden the unchanged ruler carries: BH is applied across the subtype's marker set, so the set grows from the frozen panel by at most 2. |

The **frozen panel is augmented, never replaced**: the re-measurement uses the union
(frozen `_markers_all` ∪ admitted candidates). A candidate rejected by L4 can therefore never remove
the marker that already cleared the gate.

## 6. Measurability (technical precondition, declared)

For a row `(volume V, subtype S)` with a candidate `g`:

| id | rule |
|---|---|
| **M1** | `g` occurs in `V`'s `var/_index` (the ruler skips a gene that is not in the file — this is its existing behaviour, unchanged). |
| **M2** | detection floor: in `V`, `g` is detected (`X > 0`) in **≥ 5 %** of all cells of `V`. A gene below the floor is recorded `not_measurable_here` for that row. |

Both are technical floors, not differential tests: no comparison between the subtype's cells and the
sibling cells is used to decide measurability. A subtype whose every admitted candidate is
unmeasurable **in every volume where its rows sit** is recorded `NOT_AVAILABLE` / `not_measurable`,
and that is a legitimate result (BRIEF §2).

## 7. The re-measurement — same ruler, same code, same thresholds

* The ruler is the frozen `plans/consensus_subtype_20261022/scripts/c3_separation.py`, **run unmodified**
  (`sha256` recorded by `m0`), invoked as
  `python3 scripts/c3_separation.py --observability <my augmented rows> --out <my out dir>`.
* The augmented rows file = the frozen `out/SUBTYPE_OBSERVABILITY_rows.json` with `_markers_all`
  extended by the admitted candidates for in-scope subtypes. Every other field of every row is
  byte-preserved; the frozen file itself is never written.
* **No threshold moves.** AUC ≥ 0.70, BH-FDR < 0.05, ≥ 2 markers, ≥ 30 cells, the explicit
  parent/sibling map, the per-class-cap detector and the S-PRIOR check are all the ruler's own and are
  inherited by running its own file.
* Acceptance criterion for a flip: the ruler's own `result` for that `(volume, subtype)` row changes
  `not_separated` → `separated`, with the augmented `marker_detail` naming **≥ 2** markers that cleared.
  Rows that do not flip keep their `not_separated` verdict and are reported as such.
* **The zero-marker / already-separated / insufficient_evidence rows must not move.** If any of the
  38 out-of-scope rows changes verdict, that is a defect of my augmentation and is reported as a FAIL,
  not as a result.

## 8. The honesty rules for a flip (BRIEF §4, "one marker tested twice")

Each flipped row is classified, with the raw numbers printed:

| id | what is reported |
|---|---|
| **H1** | the markers that cleared the gate, with AUC and q, and which of them are added candidates |
| **H2** | for every clearing marker, the literature claim ids behind it (channel A paper ids / channel B source ids); `two_independent_claims` iff the two clearing markers share **no** paper id, else `shared_source` |
| **H3** | the observed pairwise Spearman ρ between the two clearing markers across the cells of that comparison, as a disclosure (never a selection criterion); flagged `high_coexpression` at \|ρ\| ≥ 0.6 |
| **H4** | transcription-factor/paralog collisions: if the added marker and an existing clearing marker share the symbol stem (trailing digits/letters stripped, e.g. `GRM6`/`GRM7`, `GRIK1`/`GRIK3`, `OPN1SW`/`OPN1MW`) they are flagged `same_symbol_family` |
| **H5** | a flip counts as **corroborated** only when H2 = `two_independent_claims`; every other flip is reported as **`flip_flagged`** with its flag name. The wave's headline count is *both* numbers, never the raw count alone. |

## 9. The increment is a candidate library, registered default OFF with an empty whitelist

* New file `kb/markers/markers_v14_subtype_second_increment.json`, one entry per in-scope subtype,
  each named by the Cell Ontology label of the term it carries from the frozen snapshot
  `releases/2026-06-08` (the CL ids are the ones the frozen 94-entry list already verified as
  resolvable: 0 missing).
* Registration on the shipped surface follows the house pattern for a registered-but-OFF increment:
  a `MARKER_LIBS` line, `SUBTYPE_DEFAULT_LIBS = ()` (empty **by design**, so no env switch can inject
  it), its own predicate, and the accepted-library error string gains the name.
* **No `*_DEFAULT_LIBS` tuple of any other wave is touched.** Nothing is activated on the default
  route; the default `all` route is byte-identical, and that is **measured** over the recorded query
  set (721 cluster windows + the class/species battery + the repo's legacy tool-panel probe), not
  asserted.
* The library is consumed by this wave only through an explicit `--observability` argument to the
  ruler. It is not merged into `all` by any switch.

## 10. Red lines and resources

* Cell Ontology: every class name resolves against the frozen snapshot; no fabricated term.
* Every cited source resolves (PMID/DOI from the corpus `paper_id`/`doi` columns and the frozen
  `sources[].id`); unresolvable anchors are reported as unresolvable.
* Zero downloads, zero network (audit hook: load receipts > 0, EVENT lines = 0).
* English for anything that mirrors into the repository. Every number carries its command.
  NOT_RUN is never a pass.
* Frozen material is read-only: `plans/consensus_subtype_20261022/**` is never modified, and its
  `REPORT.md` is never rewritten.
* Resource discipline (WORKSTATION_RULES 2026-09-30): one volume read measured at **5.30 GiB peak RSS /
  18 s** (`scripts/m0b_rss_probe.py CX01_retina_snRNA`, the largest in-scope volume) ⇒ heavy steps run
  under `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G`, concurrency ≤ 4,
  `free -g` recorded before and after, heartbeat every 30 min with the available reading, nothing new
  started below 40 GiB available.
* Commit locally; **DO NOT PUSH**; the commit hash is reported.

## 11. Deliverables

1. this pre-registration (`/mnt/D/EyeKB/plans/subtype_second_marker_20261022/`, mirrored in the repo);
2. `out/SUBTYPE_SECOND_MARKER_LIT.{json,tsv}` — every candidate with its paper count, snippets, and
   the L1–L5 decision, *including the rejected ones*;
3. `kb/markers/markers_v14_subtype_second_increment.json` — the candidate library (default OFF);
4. `out/SUBTYPE_SECOND_MARKER_PANEL.json` — admitted panel + the per-volume measurability table;
5. `out/SUBTYPE_SEPARATION_AUGMENTED.{json,tsv}` — the re-measurement by the unmodified ruler;
6. `out/FLIPS.{json,tsv}` — per row before/after with the marker evidence and the H1–H5 classification;
7. `out/DEFAULT_FACE.json` — the default-face byte-identity measurement;
8. `out/MANIFEST.sha256`, `out/GATE.json`, `ledgers/net_audit.log`, `logs/chain.log`;
9. `REPORT.md` — English, in this wave's own directory (the frozen wave's `REPORT.md` is untouched);
10. one row in `docs/W3_PIPELINE_REGISTRY.tsv` for the new library.

## 12. What this wave may NOT claim

The reading is **in-sample**: the panel is measured on the same seven volumes that produced the
question. A flip therefore shows that a literature-sourced second marker exists and is measurable —
it is **not** an accuracy claim about the annotator, and it is not evidence that the subtype is "found".
No subtype enters any shipped vocabulary by this wave.