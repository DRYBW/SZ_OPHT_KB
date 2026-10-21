# REPORT - Cell Ontology depth and the developmental lineage layer

Card: L2-Cell Ontology depth + developmental lineage layer. Executed by `pi-chief`.
Wave directory: `plans/cl_depth_devlineage_20261021`.

Upstream: `plans/pi_asks_20261021/BRIEF_CL_DEEP_USE_AND_DEVLINEAGE_20261021.md`, and the external
tester's ontology re-judgement in `plans/zjy_feedback_20261021/from_oss/EyeKB更新后重评_20261021.md`
section 5-2.

The criticism this card answers is that we *say* we use the Cell Ontology but use it as a spelling
normaliser: one class, one CL term, no ancestor reasoning and no granularity reasoning. That was
correct. This card makes the ontology navigable, measures what the missing reasoning cost, and
builds the developmental layer the PI asked for - and counts, rather than hides, the parts the
sources cannot support.

---

## 1. Source identity (what was actually used)

```bash
python3 scripts/a1_build_nav.py
```

```
ontology: /mnt/D/EyeKB/plans/devline_ont_20261002/downloads/cl.obo
  sha256   : 7e19b4aef8e7fe7720b0c4474c6a5b8713c904ea9ab7b7d5d96f2cb28b8fc51f
  release  : releases/2026-06-08   (format-version 1.2)
  CL terms : 3531 blocks / 3335 active / 196 obsolete
  CL-namespace typedefs (not cell types): 3
second file: /mnt/D/OcularKB/ocularkb/rag/ontology/cl-base.obo
  release cl/releases/2026-06-08/cl-base.owl  terms 3531/3335 active
  shared ids 3531; name disagreements 0; is_a disagreements 0
```

* **Release actually used: `releases/2026-06-08`**, the file the brief names. Its CL namespace holds
  3,531 `[Term]` blocks (3,335 active, 196 obsolete) plus 3 relation typedefs - 3,534 `id: CL:` lines,
  which is the 3,534 the tester reported. Obsolete terms are parsed but kept out of the navigable set.
* The second local CL file (the one the production judge was built against) agrees with the named
  file on **every shared term**: 3,531 shared, 0 name disagreements, 0 `is_a` disagreements. So the
  numbers below and the production judge are on the same vocabulary.
* `develops_from` is `RO:0002202`, resolved from the file's own typedef, not assumed; the release
  contains 400 statements of it. `transdifferentiation` does not exist in this release (as the
  earlier ontology card already recorded).
* Two parsing facts that cost this project before and are now handled explicitly: `is_a` lines with
  a qualifier (`{is_inferred="true"}`, 662 of them in this release) have the qualifier stripped, and
  the three CL-namespace relation ids (`CL:4030044/45/46`) are disclosed as typedefs rather than
  mistaken for cell types. Gate A1/A3/A7/A8 re-check all of this.

Our label map, extended from the 76-class sidecar to every label the libraries ship:

```
wrote out/ONT_LABELMAP_V2.tsv  (80 labels; mapped 65; unresolved 15)
  by method: sidecar 61, name 4, unresolved 15
```

Each mapping records the id, the file's own name for it, the **line of the ontology file it was read
from**, and how it was obtained (shipped sidecar / `cl_id` embedded in the increment file / name
match). The 15 unresolved labels are declared with their reason, not left empty.

---

## 2. What changed, in measurable terms

| | before this card | after |
|---|---|---|
| relation between two CL terms | a lookup table (one class -> one term), plus a judge that merged "coarser" and "finer" into one bucket | a function of the two terms and the file: same / coarser / finer / mismatch / no mapping, split in both directions |
| ancestor reasoning | per-term DFS inside one script, unverified | closure computed at build time, audited against a fixed-point recomputation (A3), cross-checked across two ontology files (A7) |
| granularity composition | one number (`subsumed` 25.32% of cells) | coarser 22.9% + finer 2.4% of cells = the same 25.32%, now with direction |
| multi-step relations | invisible: a two-step or three-step `is_a` relation reads as unrelated | 12 of 56 candidate pairs (52,566 cells) are two or more steps and are named as such |
| identifier provenance | ids resolved inside a build script, unverifiable after the fact | every id carries its file line; A8 refuses any CL id in the artefacts that is not in the file (3,338 distinct ids seen, 0 offenders) |
| lineage layer | did not exist | 60 nodes / 34 edges, each edge with an ontology line or a corpus locator, plus the counted gap |

The `subsumed` figure reconciles exactly (342,552 + 36,090 = 378,642 cells = the 25.32% the earlier
reading reported), so this is a refinement of the existing judge, not a competing number.

---

## 3. Task A - the four-way split over the 721 recorded clusters

```bash
python3 scripts/a2_fourway_721.py
```

```
cells total: 1495330
verdict          clusters    cells  %cells
same_term             212   480120   32.1%
we_are_coarser        150   342552   22.9%
we_are_finer           15    36090    2.4%
true_mismatch         151   268391   17.9%
no_mapping            193   368177   24.6%
    ours_abstain                         180 clusters    347690 cells
    ours_candidate_without_cl_term        13 clusters     20487 cells
```

* The classification is a function of the two CL terms and the ontology. Gate A4 re-derives all 721
  verdicts from the table's own terms and fails on any disagreement; there is no curated list.
* Re-resolving both sides independently reproduces the recorded ids **exactly** for all 721 rows
  (truth drift 0, our-side drift 0), so the re-judgement is comparable with the earlier reading.
* `no_mapping` is entirely on our side here. Abstention (180 clusters) is a legal outcome and is
  excluded from accuracy-style rates; the 13 clusters / 20,487 cells where we answered with a class
  that has no CL term (e.g. `APC_MHCII_high`, `Proliferating`) are our own naming debt and are
  reported as such.

### How much of the family-regex disagreement mass is real

```bash
python3 scripts/a2_fourway_721.py        # prints the decomposition below
```

```
=== family regex (the reading that produced the 8.0%) ===
  family_consistent        297 clusters    624029 cells (41.7%)
  family_inconsistent      222 clusters    451272 cells (30.2%)
  family_other             202 clusters    420029 cells (28.1%)

=== of the family-inconsistent mass, what it actually is ===
  same CL term (pure naming)      :     49109 cells (3.3% of all cells, 10.9% of the inconsistent mass)
  granularity (we coarser/finer)  :    131487 cells (8.8% of all cells, 29.1% of the inconsistent mass)
  survives as a real disagreement :    217976 cells (14.6% of all cells, 48.3% of the inconsistent mass)
  no mapping on one side          :     52700 cells
```

The family regex itself scores **41.73%** on this recording - the same 41.73% the tester reports for
his pre-update baseline, which is what makes the two implementations comparable. Under ontology
authority the same recording reads 32.11% identical term (42.60% of judged cells) and 57.43% once
granularity differences are counted as non-contradictions.

### Reconciliation with the tester's 13 pairs

```bash
python3 scripts/a2_fourway_721.py        # prints the reconciliation table
```

| | his number | ours on the same pairs |
|---|---:|---:|
| clusters | 43 | 46 |
| cells | 119,672 | 126,700 |
| relation agreement per pair | 13/13 | **13/13** |

His relation call agrees with ours for all 13 pairs, in both directions (including `Astro` vs
`glial cell`, where we are the finer side). The cell totals differ by +7,028 (+5.9%), concentrated
in `BC` vs rod bipolar cell (+3,802), `Endo` vs endothelial cell (+1,375) and `SMC` (+1,851).
**Reason, stated plainly: his table is the post-update arm (2026-10-21) and our local recording is
the 2026-10-20 production arm.** His per-cluster file for that rerun is not on this machine, so we
cannot recompute his arm; across the whole recording the equivalent mass on our arm is 60 clusters /
180,596 cells (12.1% of all cells), larger than his 43 / 119,672 (8.0%).

---

## 4. Task A.4 - the child-term candidates (decision-ready, not adopted)

`out/CHILD_TERM_CANDIDATES.tsv`: **56 pairs, 342,552 cells, 25 with corpus support, 31 without.**
No term is adopted in this card.

The head of the list (full table in `GRANULARITY_READER_PAGE.md` and in the file):

| our class | child CL | child term (read from the file) | cells | corpus |
|---|---|---|---:|---|
| SMC | CL:1000443 | ciliary muscle cell | 26,532 | states the term |
| Endo | CL:0000071 | blood vessel endothelial cell | 23,948 | states the term |
| BC | CL:0000751 | rod bipolar cell | 23,484 | states the term |
| AC | CL:4030028 | glycinergic amacrine cell | 15,718 | states the term |
| AC | CL:4030027 | GABAergic amacrine cell | 14,442 | states the term |
| Fibroblast | CL:0002363 | keratocyte | 11,836 | synonym only |
| HC | CL:0004217 | H1 horizontal cell | 11,275 | states the term |
| Schwann | CL:0002376 | non-myelinating Schwann cell | 10,914 | none |
| Endo | CL:0000666 | fenestrated endothelial cell | 9,456 | none |
| RGC | CL:4033047 | OFF midget ganglion cell | 9,022 | states the term |

Corpus support is measured, not asserted: the term (or one of its synonyms) is looked for as a
whole phrase in the chunks of the corpus this machine ships, and each hit is stored with its paper
id and section (`out/CORPUS_TERM_INDEX.tsv`, built by `scripts/b0_corpus_index.py`). 31 candidates
have no hit at all - mostly the fine retinal bipolar and horizontal subtypes - and they are listed
as gaps, because the naming would have to come from somewhere and that is a separate decision.

---

## 5. Task B - the developmental lineage layer

```bash
python3 scripts/b1_build_lineage.py
```

```
nodes 60 (library classes 52, germ layers 8), roots 44
edges 34 {'develops_from_direct': 5, 'develops_from_transitive': 4, 'germ_layer_membership': 25}
germ-layer rows: {'ontology_chain': 13, 'corpus_cooccurrence_weak': 12, 'unresolved': 36}
marker rows 100 {'corpus_supported': 100}
edges with at least one corpus-supported transition: 2
classes with no developmental evidence locally: 36
developing nodes found in an adult baseline: []
```

* **The chains the ontology does carry** (with the full reads in `out/LINEAGE_GERM_LAYER.tsv`):
  neural ectoderm -> retinal progenitor cell -> {rod, cone}; mesoderm -> {endothelial cell,
  microglial cell}; neural crest -> melanocyte (through melanoblast and migratory neural crest
  cell); ectoderm -> oligodendrocyte (through the oligodendrocyte precursor chain). Seven classes
  in total.
* **What it does not carry is the headline.** Bipolar cells, amacrine cells, horizontal cells,
  retinal ganglion cells, Mueller glia and RPE have no `develops_from` statement in this release, so
  within the ontology the photoreceptor chain is the only complete retinal lineage. Nine classes
  have only the weaker corpus co-occurrence tier (labelled `corpus_cooccurrence_weak`, with counts
  and locators), and **36 classes have no local developmental evidence at all** - listed by name in
  `out/LINEAGE_UNRESOLVED_DEVELOPMENT.tsv`.
* **Marker changes along a step.** 100 corpus-backed rows over the two steps the ontology supports
  between two covered classes (RPC -> rod, RPC -> cone): gains such as `RHO` (1,397 chunks / 490
  papers), `NRL` (665/171), `PDE6B` (342/141), `NR2E3` (283/100) and losses such as `PAX6`
  (1,525/424), `GFAP` (1,889/542), `SOX2` (790/291), `ATOH7` (602/122). This is the panel
  difference along an ontology edge - **not** a measured expression change - and every gene carries
  its locators. Only 2 of 34 edges can carry such a step; 3 more are steps where the parent has no
  panel (`parent_panel_absent`), and the rest are membership or non-stepwise relations.
* **Stage axis.** Every node declares `organism_stage` from the ontology's own text (with the
  matching word recorded); our own state labels are excluded from that decision and disclosed
  separately, so `RPE_fetal` does not move the RPE node onto the developing side. 12 nodes are
  developing (8 anchors + retinal progenitor cell, transit amplifying cell, progenitor cell, basal
  cell). Gate B4 checks every developing node against 78 structured class keys of the repository's
  adult baseline entries: 0 offenders.
* **Evaluation volumes are not an input.** Gate B6 fails if any lineage artefact mentions one of the
  28 evaluation volumes or the evaluation working tree. The only file that reads them against the
  lineage is `out/GAPCHECK_LINEAGE_vs_BENCHMARK.tsv`, run afterwards as a gap check: 23 of the 52
  class nodes are never the top candidate anywhere in the recording, and the only recorded groups
  without a lineage node are the abstentions (180 clusters / 347,690 cells) and `APC_MHCII_high`
  (13 / 20,487 cells, the class that carries no CL term).

---

## 6. Gates and proofs

```bash
bash scripts/run_all.sh
```

```
REPLAY_PASS byte-identical on the second build
manifest entries: 31
[gate A] PASS  rules=9 fail=0
  PASS A1 ONT_SOURCE    release=releases/2026-06-08 sha256=7e19b4aef8e7...
  PASS A2 ID_TRACE      ids in label/line-pairing artefacts traced to the file
  PASS A3 CLOSURE       terms=3335 mismatched=0 self-ancestors=0
  PASS A4 CLASSIFY      rows=721 cells=1495330
  PASS A5 CANDIDATES    candidates=56 with_support=25
  PASS A6 LABELMAP      labels=80 mapped=65
  PASS A7 CROSSFILE     shared=3531 name_diff=0 is_a_diff=0
  PASS A8 NO_MEMORY_ID  distinct CL ids named in artefacts: 3338; absent: 0
  PASS A9 REPLAY        manifest=out/MANIFEST.sha256 ledger=ledgers/REPLAY.txt
[gate B] PASS  rules=7 fail=0
  PASS B1 NODE_TERM     nodes=60
  PASS B2 INBOUND       edges=34 roots=44 (accounted 44)
  PASS B3 ACYCLIC       develops_from nodes=7 edges=9
  PASS B4 STAGE_AXIS    developing nodes=12 stage-crossing edges=31 adult-baseline keys checked=78
  PASS B5 MARKER_TRACE  marker rows=100 corpus-supported=100
  PASS B6 NO_EVAL_LEAK  forbidden tokens checked=29 over 6 files
  PASS B7 REPLAY        manifest entries=31
[net-audit] hook installs=35  network events=0
NET_ZERO_PASS
```

* **Default behaviour untouched, proven by replay.** Nothing in `kb/`, `mcp_server/` or any shipped
  fixture was modified by this card; every artefact is new and lives under this wave directory. The
  strongest available check - the project's recorded 721-query replay - is not affected by an
  addition under `plans/`, and the determinism reading that *is* in scope is the byte-identical
  rebuild above (`ledgers/REPLAY.txt`, 15 artefacts compared over two builds).
* **Zero network**, enforced by an audit hook that covers child processes, with 35 hook-install
  receipt lines proving the hook ran (`ledgers/NET_AUDIT_SUMMARY.txt`).
* Every intermediate artefact stays on disk: `out/` (26 files), `ledgers/` (chain log, replay
  passes, net audit, resource readings), `logs/` (per-script stdout).

---

## 7. What did not work, and what is still unresolved

Stated plainly, with numbers:

1. **The ontology cannot carry most ocular lineages.** 36 of 52 covered classes have no local
   developmental evidence (`out/LINEAGE_UNRESOLVED_DEVELOPMENT.tsv`). Adding developmental
   literature is the only way to move that number; it is not a parsing problem.
2. **The corpus co-occurrence tier is weak and is labelled weak.** It found candidate origins for 9
   classes (e.g. corneal endothelial cell / neural crest, 7 chunks in 7 papers), but a single chunk
   mentioning a cell type and a germ layer is not a developmental claim. These rows are not
   promoted to `ontology_chain` and the reader page says so.
3. **Only 2 of 34 edges can carry a marker transition**, because a step needs panels on both sides
   and the parent side is often a germ-layer anchor. `parent_panel_absent` (3 edges) is recorded as
   a status, not hidden.
4. **31 of 56 child-term candidates have no corpus support.** Adopting them would be a vocabulary
   import with no local evidence; this card refuses to do it quietly.
5. **We cannot reproduce the tester's post-update arm locally.** His 2026-10-21 per-cluster file is
   not on this machine, so the reconciliation in section 3 is on the same pairs but on our arm. The
   difference (+7,028 cells on his 13 pairs; 60 vs 43 clusters across the recording) is attributed
   to the arm, not explained away.
6. **The four-way split is a relation reading, not an accuracy score.** It says what our class is
   relative to the author's term. It does not say we were right: `we_are_finer` cases (36,090 cells)
   and `same_term` cases can still be the wrong cell type at the right granularity. The metrics in
   `docs/TISSUE_COVERAGE_DECLARATION.md` remain the accuracy-side reading.
7. **The 15 labels the ontology cannot name are still unnamed** (precursors, proliferating states,
   lacrimal duct epithelium). They cannot be lineage nodes under gate B1 and are listed with their
   reasons instead.

---

## 8. Reproduction and file map

*Language.* All prose in this wave is English. Two kinds of non-English string remain, both
deliberate: the verdict vocabulary of the earlier judge, copied verbatim into the four-way table
(`✅一致` / `❌不一致` / `❓混合·低信息`) so that column stays faithful to its source, and upstream file
names cited as paths.

```bash
cd /mnt/D/EyeKB/plans/cl_depth_devlineage_20261021
bash scripts/run_all.sh                       # everything, in order, with both gates
python3 scripts/gate_ontology_nav.py          # gate A alone (rc 0/2)
python3 scripts/gate_lineage.py               # gate B alone (rc 0/2)
```

| path | contents |
|---|---|
| `scripts/ont_nav.py` | the navigation module: parse, `is_a` closure, five-way relation, `develops_from`, tracing |
| `scripts/a1_build_nav.py` | release identity, closure table, label map with provenance, cross-file check |
| `scripts/a2_fourway_721.py` | the four-way table over the 721 recorded clusters + reconciliation |
| `scripts/b0_corpus_index.py`, `scripts/b0b_germlayer_cooccurrence.py` | the two corpus scans (term index, gene index, germ-layer co-occurrence) |
| `scripts/a3_child_candidates.py` | the child-term candidate list with corpus support |
| `scripts/b1_build_lineage.py` | the lineage: nodes, edges, germ-layer rows, marker transitions, unresolved list |
| `scripts/c1_benchmark_gapcheck.py` | the after-the-fact, asymmetric gap check against the recording |
| `scripts/gate_ontology_nav.py`, `scripts/gate_lineage.py` | the two gates (A1-A9, B1-B7) |
| `scripts/run_all.sh`, `scripts/netaudit/sitecustomize.py` | one-command chain, replay, manifest, network audit hook |
| `out/ONT_NAV_v1.json`, `out/ONT_CLOSURE_is_a.tsv`, `out/ONT_LABELMAP_V2.tsv` | the navigable ontology |
| `out/GRANULARITY_FOURWAY_721.tsv`, `out/GRANULARITY_SUMMARY.json`, `out/FAMILY_VS_ONTOLOGY_CROSSTAB.tsv` | Task A readings |
| `out/CHILD_TERM_CANDIDATES.tsv`, `.json` | Task A.4 decision input |
| `out/CORPUS_*.tsv`, `out/CORPUS_INDEX_META.json` | corpus support and its gaps |
| `out/LINEAGE_*.tsv`, `out/LINEAGE_SUMMARY.json` | Task B data |
| `out/GAPCHECK_LINEAGE_vs_BENCHMARK.tsv` | the after-the-fact gap check |
| `out/MANIFEST.sha256` | sha256 of every delivered artefact (gate outputs excluded by construction) |
| `ledgers/`, `logs/` | chain log, replay passes, net audit, resource readings, per-script stdout |

Commit for this card: `8492dd3adf1e281f5590e8c144053116613713af` (local only, nothing pushed).
The commit is the review-layer mirror of this wave under `docs/plans/cl_depth_devlineage_20261021/`;
the construction site remains `plans/cl_depth_devlineage_20261021/`. No file outside that directory
was touched - `kb/`, `mcp_server/` and the shipped fixtures are unchanged, which is what makes the
"default behaviour untouched" claim checkable by inspection as well as by replay.