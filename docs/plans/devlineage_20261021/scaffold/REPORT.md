# REPORT — developmental scaffold: full enumeration, coverage denominator, decapitated-branch register

Card: **V4 — developmental lineage: full scaffold enumeration, coverage denominator, decapitated-branch
register**. Construction site: `plans/devlineage_20261021/scaffold/`. Executed by `pi-chief`.

Upstream, both binding: the frozen contract
`plans/devlineage_20261021/DATA_CONTRACT_devlineage_v1.md`, then the brief
`plans/devlineage_20261021/BRIEF_V4_SCAFFOLD_EXPANSION_20261021.md`. The first pass's delivery
`plans/cl_depth_devlineage_20261021/` (commit `8492dd3adf1e281f5590e8c144053116613713af`) is treated
as a peer artefact: read, re-derived row by row, and extended — never redone.

---

## 0. The directive this card answers, and what it is not

The owner asked for the developmental lineage to be built **comprehensively**: every lineage
enumerated, each carrying its own markers, each carrying some markers at a given stage.

An earlier external review had limited this block to two pilots. **On scope the owner's directive
overrides that limit — and that override is a directive, not an audit pass.** No quality gate the
review set is relaxed by it: every gate in the contract still binds, every arrest in the sources is
still recorded as an arrest, and nothing below asserts a lineage step that a local source does not
state. What the directive changes is how much I enumerate, not how much I claim.

The marker work and the stage axis belong to the sibling cards (`markers/`, `stages/`). This card
owns the scaffold: nodes, edges, relation typing, the coverage denominator and the register. Every
edge row carries an empty `marker_change_ids` column, which is where the marker layer attaches.

---

## 1. The two numbers that fix what "comprehensive" can mean

Re-measured from the ontology file, not read from any summary (`scripts/s0_reverify_upstream.py`):

```
ontology: /mnt/D/EyeKB/plans/devline_ont_20261002/downloads/cl.obo
  release=releases/2026-06-08 active=3335 dev_statements=400
  develops_from by namespace: {'CL': 400, 'UBERON': 656}
  relation names declared by the release: 241
```

* `develops_from` (RO:0002202) appears **400 times inside CL term blocks**; the integrated release
  carries 1,056 occurrences in total, and the other 656 sit inside UBERON blocks — a count taken
  without reading the file's own block structure reports 1,056 and then mistakes the peer's 400 for
  an error. (My own first count did exactly that; see §9.)
* The release declares 241 relation names and **none of them is `transdifferentiation`**; the string
  does not occur anywhere in the file. The contract's fourth relation is therefore absent from this
  release, and no edge in this card can use it.
* The ontology contains **no gene-name term for a cell type**, so it cannot supply a marker. The
  marker layer's input can therefore only be the literature and our own panels — which is the sibling
  card's problem, and it is stated here only so that "each lineage carries its own markers" is not
  read as something this scaffold could deliver.

So "comprehensive" here means **comprehensively enumerated and exhaustively graded**: the full
denominator, every branch carrying its evidence grade, and every broken branch named with what would
repair it. It cannot mean "every arrow filled", and filling an arrow by common sense is a red line.

---

## 2. The enumeration — nodes

```bash
python3 scripts/s1_enum_nodes.py
```
→ `out/SCAFFOLD_NODES.tsv` (**103** rows), `out/NODES_SUMMARY.json`

| ring | kind | n | what it is |
|---|---|---|---|
| A1 | `library_class` | 52 | the distinct CL terms behind the 65 mapped library labels |
| A2 | `library_class` | 15 | library concepts the ontology cannot name (`dl:NO_MATCH:<label>` keys) |
| B | `ontology_intermediate` | 28 | every CL term on a `develops_from` path out of a ring-A class or an anchor |
| C | `origin_anchor` | 8 | the germ-layer / origin anchors the repository already resolved from the file |

Two extensions over the peer's 60 nodes, both mechanical:

* **The 15 concepts the ontology cannot name are enumerated** rather than dropped. The contract
  provides `dl:NO_MATCH:<in-house id>` for exactly this case, and 11 of those 15 are developmental
  precursor concepts our own developmental panels ship (`Rod_precursor`, `Cone_precursor`,
  `AC_precursor`, `BC_precursor`, `HC_precursor`, `RGC_precursor`, `glia_precursor`, `NRPC_early`,
  `NRPC_late`, `TAC_proliferating`, `TAC_transit_amplifying`). A lineage layer that silently omits
  the concepts our own panels are built around would be reporting a smaller library than exists.
* **The 28 intermediates are materialised as nodes.** The peer recorded them inside a `chain` string;
  a chain inside a string cannot carry an ontology line, a stage or an inbound edge count per term.
  Materialising them is what turns 9 native steps into the 40 §3 counts.

Node keys follow the contract grammar exactly, and every field is sourced or `unknown`:

```
dl:<canonical_cl_id>|sp=<species>|ts=<tissue_context>|st=<organism_stage>|es=<experimental_system>
```

| field | rule actually applied | measured |
|---|---|---|
| `st` | the ontology's own text carries a developmental word → `developing`; else a repository baseline that declares an adult stage → `adult`; else `unknown` | adult 16, developing 42, unknown 45, fetal 0 |
| `sp` | written only where a repository baseline declares the species for that class | human 18, unknown 85 |
| `ts` | written only where exactly one baseline entry declares the class; several declaring entries leave it `unknown` and the candidates are listed in `ts_candidates` | declared 6, unknown 97 |
| `es` | `unknown` everywhere: nothing on the library side declares an experimental system | unknown 103 |

`unknown` is never defaulted to adult, and every `adult` names the baseline that declares it — the
gate re-reads that file and re-derives the call (`G3`). Two of our own vocabulary facts are recorded
instead of being papered over: `RPE_fetal` is a state qualifier on the same CL term and does **not**
move the RPE node onto the developing side, and eight NO_MATCH labels (`NRPC_early`, `NRPC_late`,
`Proliferating`, `Retinal_Proliferating`, …) are named as precursors but carry no word from the stage
word list, so their stage stays `unknown` with the reason in the row's `stage_note`.

---

## 3. The enumeration — edges, typed

```bash
python3 scripts/s2_enum_edges.py
```
→ `out/SCAFFOLD_EDGES_CONFIRMED.tsv` (**51** rows, one per ordered pair, `edge_key` in contract form)

| relation type | n | what it means here |
|---|---|---|
| `ontology_development_relation` | 40 | a step the ontology itself declares (`develops_from`), semantics kept in `source_relation` and `source_relation_direction` |
| `ancestral_origin` | 11 | an origin claim spanning more than one step, or needing the ontology's own `is_a` bridge |
| `direct_lineage` | **0** | nothing local supports it — see the grade policy below |
| `trajectory_association` | 0 in the confirmed graph | the 24 trajectory-only rows are the rejected rows of §6 |

**Rule R-ANCHOR**, applied mechanically, written into every derived row (`derivation_rule`,
`derivation_note`) because it is a derived rule and not a native ontology attribute. For a library
class C, let `closure(C)` be every term reachable from C by at least one `develops_from` step:

| rule | condition | directness written |
|---|---|---|
| R-ANCHOR-1 | the anchor is itself in `closure(C)` | `chain:<k>_steps` (k ≥ 2; k = 1 is a native edge) |
| R-ANCHOR-2 | a term in `closure(C)` has the anchor among its direct `is_a` statements | `chain:<k>_steps_with_is_a_bridge` |
| R-ANCHOR-3 | a term in `closure(C)` has the anchor among its transitive `is_a` ancestors | `chain:<k>_steps_with_is_a_path:<m>_hops` |

A class with **no `develops_from` step at all gets no origin edge**: `is_a` alone is a taxonomic
statement, not a developmental one, and using it as one would be the common-sense arrow this card
forbids. R-ANCHOR-3 is the one place this card goes beyond the peer's rule, and it earns its keep in
a measurable way: it repairs exactly one pair — `corneal endothelial cell` reaches `neural crest cell`
through `migratory cranial neural crest cell → migratory neural crest cell → neural crest cell`, all
three hops being statements of the ontology file. The peer had this pair only as a corpus
co-occurrence, and its cited chunks turn out (§6) to co-mention the two terms without asserting a
relation. The ontology carries it; the corpus does not.

Measured distribution of the 51 confirmed edges:

```
by_derivation_rule: R-NATIVE 40, R-ANCHOR-1 4, R-ANCHOR-2 6, R-ANCHOR-3 1
by_directness:      direct 40, chain:2_steps 2, chain:2_steps_with_is_a_bridge 3,
                    chain:1_steps_with_is_a_bridge 1, chain:1_steps_with_is_a_path:2_hops 1,
                    chain:3_steps 1, chain:3_steps_with_is_a_bridge 1,
                    chain:4_steps 1, chain:4_steps_with_is_a_bridge 1
```

**Grade policy, stated because it is a judgement.** Every confirmed edge is graded
`identity_conversion_not_direct`: the source states the time direction and the identity conversion,
and it is not direct-lineage proof. `direct_lineage_support` is claimed by **nothing** in this graph,
and `textbook_or_review_distant_origin` is used only by the pending repair table. The conservative
reading costs the graph nothing observable — a reader who prefers to call a native one-step
`develops_from` direct-lineage support can do so from the `directness` column, because the
declaration's own semantics are preserved there. The alternative, calling a curated ontology
statement "direct lineage evidence", would be exactly the silent upgrade the contract forbids.

---

## 4. The coverage denominator

```bash
python3 scripts/s3_coverage_denominator.py
```
→ `out/COVERAGE_DENOMINATOR.tsv` (33 counts), `out/ANCHOR_COVERAGE.tsv` (8 rows),
`out/RPC_AXIS.tsv` (52 rows)

```
library_concepts_total                                   80
library_concepts_mapped_to_cl                            65
library_concepts_no_match                                15
distinct_cl_ids_in_library                               52
nodes_total                                              103
edges_total                                              51
library_classes_with_an_anchored_origin                  8
library_classes_with_only_corpus_cooccurrence            8
library_classes_with_no_local_developmental_evidence     36
library_classes_that_are_never_a_descendant_in_the_graph 34
decapitated_branches                                     44
native_develops_from_statements_in_release               400
native_develops_from_statements_enumerated               40
```

Read as a coverage statement: **8 of the 52 covered classes** can be tied to a germ-layer origin by
anything on this machine; **44 cannot**, of which 36 have no local developmental trace at all and 8
have only a corpus co-occurrence. The ontology's 400 `develops_from` statements reduce to 40 between
enumerated nodes, because 360 of them connect terms our library does not cover.

Per-anchor (`out/ANCHOR_COVERAGE.tsv`): `mesoderm` 3 classes, `neural_ectoderm` 4, `ectoderm` 5,
`neural_crest` 2, and **four anchors nothing reaches** — `hematopoietic stem cell`,
`surface ectodermal cell`, `endodermal cell`, `mesenchymal cell`. That last group matters: our library
ships nine haematopoietic and immune classes and three mesenchymal ones, and the ontology's own
`develops_from` graph connects none of them to those anchors.

The retinal progenitor axis (`out/RPC_AXIS.tsv`): of the 52 covered classes, **2 reach** the retinal
progenitor cell (rod, cone), 1 **is** it, and **49 do not** — including every other retinal class
(bipolar, amacrine, horizontal, ganglion, Müller glia, RPE, astrocyte). The one complete retinal
lineage in this release is `neurectodermal cell → retinal progenitor cell → {rod, cone}`.

---

## 5. The decapitated-branch register

```bash
python3 scripts/s4_decapitated_branches.py
```
→ `out/DECAPITATED_BRANCHES.tsv` — the centrepiece, **64** rows

| branch kind | n | contents |
|---|---|---|
| `covered_class_without_origin` | 44 | one row per covered class no anchor reaches |
| `anchor_without_any_covered_class` | 4 | the coarsest break: an anchor no covered class reaches |
| `in_house_concept_without_ontology_term` | 15 | concepts with no ontology counterpart at all |
| `axis_rollup` | 1 | the retinal progenitor axis in one row |

Each row names the class (CL id and our labels, or the `NO_MATCH` concept), the ontology line or the
absence of one, the stage, the peer's evidence tier, the **exact point where the chain stops**
(`break_kind`, `chain_top_term` with its ontology line), the **cell mass where our own baselines
record one** (14 classes carry such a share; 9 register rows quote one), the retinal-axis position,
and the kind of evidence that would repair it. The break kinds measure as:

```
no_develops_from_statement_at_all             34
closure_does_not_reach_any_origin_anchor      10
no_covered_class_reaches_this_anchor           4
concept_has_no_ontology_counterpart_at_all    15
axis_carries_photoreceptors_only               1
```

The 10 `closure_does_not_reach_any_origin_anchor` rows are the interesting middle: those classes *do*
have a chain, it just stops short of an origin. Two examples out of the register:

* `retinal pigment epithelial cell (CL:0002586)` — no `develops_from` statement at all; the ontology
  says nothing about where RPE comes from. Cell mass recorded: present in the retina baseline.
* `B cell (CL:0000236)` — closure exists (2 terms) and reaches no anchor; the haematopoietic anchor
  it belongs to is one of the four nothing reaches.
* `corneal endothelial cell (CL:0000132)` was in this population as a weak-corpus class until
  R-ANCHOR-3 repaired it, and the register records the repair by its absence — which is why the
  peer's 9 weak classes are 8 here.

---

## 6. Literature-repair proposals — and where they are kept

```bash
python3 scripts/s5_corpus_scan.py     # one streaming pass over the local corpus (0.20 GiB peak)
python3 scripts/s6_pending_assertions.py
```

`out/PENDING_ASSERTIONS.tsv` — **68** proposals, every one with a resolvable anchor (paper id,
section, the chunk's position in the corpus stream, a truncated sha256 of the chunk, and the
sentence). **Not one of them is in the confirmed graph**, which is the contract's whole point: a
repair proposal is not an edge. Examples, quoting the sources:

| proposal | source sentence |
|---|---|
| `lens fiber cell ← lens epithelial cell` (16 chunks / 12 papers) | "Lens fiber cells originate from lens epithelial cells through the process of cell differentiation." |
| `Mueller cell ← retinal progenitor cell` (6 / 5) | "…all retinal neurons and the Müller glia (MG) arising from a shared retinal progenitor cell (RPC) population…" |
| `amacrine cell ← retinal progenitor cell` (5 / 5) | "All retinal cell types … are generated from multipoten[t]…" |
| `corneal epithelial cell ← stem cell` (5 / 5) | "…the limbal stem cells at the corneal periphery that can differentiate into corneal epithelial cells…" |
| `macrophage ← monocyte` (40 / 26) | "…human peripheral monocytes were differentiated into inactivated M0 macrophages…" |

The scan is deliberately narrow and its refusals are recorded: one streaming pass, 244,877 chunks, of
which **6,670** carry a lineage verb at all; **8,309** sentences examined; **628** sentences carry
two phrases or more; **124** ordered pairs; **194** example anchors, all **194** re-read in a second
pass and verified byte-for-byte. 40 phrases are refused outright (single tokens such as `Rod`, `MG`,
`AC`, `B`, and everyday-meaning words such as `plasma`, `proliferating`); 161 are matched, including
the `Mueller/Muller/Müller` spelling variants the corpus actually uses.

Three other tables keep the outcomes apart:

* `out/PEER_WEAK_ROW_RECHECK.tsv` — the peer's 12 weak co-occurrence rows, **re-examined against the
  very chunks they cited**. Verdict: **0 of 12 assert a relation; 12 of 12 only co-mention** the two
  terms. The peer's "weak" label is correct, and it is now verified rather than inherited.
* `out/SCAFFOLD_EDGES_NOT_ADMITTED.tsv` — 24 rejected rows: those 12, plus 12 pairs whose sources
  assert them **in both directions** (`fibroblast`/`Myofibroblast`, `Keratocytes`/`fibroblast`,
  `macrophage`/`Microglia`, `stem cell`/`progenitor cell`, …). A pair the sources point both ways on
  is not a step; it is a conflict, and it is carried as `trajectory_association` /
  `trajectory_only` / `admission=rejected` with the reason in the row.
* `out/CORPUS_EDGE_CONFIRMATIONS.tsv` — 5 pairs a paper asserts that are **already** ontology edges
  (e.g. `monocyte → macrophage`). Recorded separately on purpose: such a source could support a grade
  upgrade, and this card does not upgrade a grade on prose. 39 further pairs are recorded in
  `out/CORPUS_PAIRS_UNUSED.tsv` with the reason they were not used.

**The textbook layer carries no developmental assertion for any decapitated branch** —
`out/TEXTBOOK_REPAIR_CANDIDATES.tsv` is empty (0 rows) after matching all 81 items against the same
matcher. That is a measured negative: the textbook layer this repository holds is layer/region
vocabulary, not lineage. It is reported instead of being stretched into a citation.

---

## 7. The machine gate

```bash
python3 scripts/s8_gate_scaffold.py
```
→ `out/GATE_SCAFFOLD.json`, `rc 0`

```
[gate scaffold] PASS  rules=10 fail=0
  PASS G1 KEY_PARSE           node keys=103 parsed, edge keys=75 parsed, rejected rows with a declared key reason=0, confirmed=51
  PASS G2 REL_VOCAB           rows=75 relation_types=['ancestral_origin', 'ontology_development_relation', 'trajectory_association']
  PASS G3 STAGE_AXIS          stages={'adult': 16, 'unknown': 45, 'developing': 42} adult_with_a_verified_basis=16 unknown_never_defaulted_to_adult=yes
  PASS G4 ANCHOR_RESOLVABLE   confirmed edges re-walked=51 rejected_rows_with_a_resolving_locator=24 pending_proposals_with_a_resolving_anchor=68
  PASS G5 NO_TYPE_UPGRADE     rows checked=75 direct_lineage_typed=0
  PASS G6 ACYCLIC_CONTEXT     contexts checked=1
  PASS G7 CONFIRMED_EQ_ADMITTED confirmed=51 admitted_grade_rows=51 full_edge_set_rows=75
  PASS G8 NO_EVAL_LEAK        forbidden tokens checked=29 over 24 artefacts (exempt, by design: ['AFTERFACT_RECORDING_COVERAGE.tsv', 'AFTERFACT_SUMMARY.json'])
  PASS G9 UPSTREAM_PIN        ontology sha pinned, navigation module sha pinned, re-verified 17/17 consumed files
  PASS G10 REPLAY_MANIFEST    manifest entries verified=42 replay_ledger=green pending_vs_graph_overlap=0
```

The rules the card asked for, and how each is mechanical rather than asserted:

* **keys parse** — every node key is re-parsed against the contract grammar and cross-checked against
  the row's own columns; every edge key is re-parsed and its endpoints must exist in the node set.
* **relation types in vocabulary** — and no trajectory-only row is confirmed.
* **stage from the four-level axis, unknown never defaulted to adult** — every `adult` re-reads its
  baseline and requires that file to declare an adult stage; every `developing` re-derives its word
  from the ontology text or from our own label; an `unknown` stage carrying a positive basis is an
  offender.
* **every confirmed edge has a resolvable anchor** — each row's chain is re-walked hop by hop against
  the ontology file and each cited line must be a real statement of that hop; each rejected row's
  corpus locator must resolve to a paper this machine ships; each pending proposal's anchor must
  resolve to a shipped paper with a non-empty quote.
* **no `trajectory_association` or `ancestral_origin` edge labelled direct lineage** — checked over
  the whole edge set, not only the confirmed part.
* **no cycle inside one context's forward-differentiation subgraph** — DFS per context; the context
  count is 1 because this enumeration is class-level (`sp`/`ts`/`es` are `unknown` for most nodes),
  and that is reported rather than dressed up.
* **confirmed-edge count equals admitted-grade count** — as a set equality in both directions
  (`G7`), plus the confirmed view file must equal the confirmed subset of the full edge set.

`G8` is the contract's no-circularity rule: the evaluation recording's own volume identifiers and
working-tree name are searched for in all 24 delivered artefacts and in this report; the only two
files that may mention it are the asymmetric coverage table and its summary, named in the readout.
`G10` additionally checks that no pending proposal appears among the confirmed edges.

---

## 8. Reconciliation with the first pass — added, re-graded, and why

`out/FIRSTPASS_RECONCILIATION.tsv` accounts for **every one** of the peer's 34 edges. Nothing was
dropped silently; the outcome counts are:

```
merged: the peer wrote the same ordered pair twice under two relation names   7
re-typed into the contract vocabulary; the ordered pair is emitted exactly once 9
not admitted; re-examined against the corpus in s6                           11
```

What the peer's 34 edges become: 16 distinct ordered pairs that survive as confirmed edges (the 7
duplicates are pairs written once as `develops_from_*` and once as `germ_layer_membership`), and 11
pairs that the contract does not admit at all. Reconciled against the 27 distinct pairs in the peer's
file (34 rows − 7 duplicates) that is exact: 16 + 11 = 27.

**Re-graded, and why.** The peer typed its edges in a private vocabulary
(`develops_from_direct`, `develops_from_transitive`, `germ_layer_membership`); the contract has four
relation types and forbids a private dialect. The mapping applied, one ordered pair per row:

| peer vocabulary | this card | why |
|---|---|---|
| `develops_from_direct` (a one-step native statement) and the `germ_layer_membership` row that describes the same pair | `ontology_development_relation`, `directness=direct` | it is what the ontology declares, and the declaration's own semantics are preserved in `source_relation*` |
| `develops_from_transitive`, `germ_layer_membership` with `tier=ontology_chain` | `ancestral_origin` with R-ANCHOR-1/2 and the rule named in the row | more than one step, or an `is_a` hop; the contract says such a claim must not pose as a single step |
| the 11 pairs resting on `evidence_kind=corpus_cooccurrence` | not admitted; 12 rejected rows (`trajectory_association` / `trajectory_only`) after re-reading the cited chunks | co-occurrence is not a lineage relation; re-reading showed no sentence asserting one |
| the peer's 9 "weak" classes (12 rows) as a tier | the same 12 rows here, but re-examined and 12/12 confirmed as co-mention-only | the label was right; it is now verified |

**Added.** 40 native steps (the peer's 9 were the subset whose parent was already one of its nodes; the
other 31 were dropped because their parent was not a node, and materialising the intermediates brings
them back); 28 intermediate nodes; 15 `NO_MATCH` concepts; the 4 `ancestral_origin` rows for
`neurectodermal cell`/`ectoderm` on the retinal axis that existed implicitly in the peer's chains;
1 extra origin pair via R-ANCHOR-3; and the whole register/pending/gate apparatus.

**Not changed, and worth saying.** The peer's edges all re-derive from the file
(`out/REVERIFY_UPSTREAM.tsv`, 58 checks, 0 fail), its 36 unresolved classes re-derive as a set, its
13 chain pairs and its 9 weak classes are exactly the ones this card also finds, and its
"9 have only a weak corpus co-occurrence layer" and "36 have zero local developmental evidence"
statements in the brief are reproduced to the class. Two observations about the peer artefact are
recorded rather than treated as errors: 6 of its `germ_layer_membership` rows cite only the
`develops_from` hops and not the `is_a` bridge line they rely on (its `develops_from_transitive` rows
cite it — both conventions are accepted by the re-verification, and this card's rows cite every hop);
and its `steps` column counts `develops_from` hops, excluding the bridge.

---

## 9. Discipline: replay, determinism, zero network, and my own two errors

**Default behaviour, proven by replay.** The card asks for the recorded query set to be replayed and
the difference count reported. The repository records one: `tests/REPRO_EXPECTED.json` (41 recorded
retrieval cases with their expected top-5 PubMed ids) replayed by `tests/verify_repro.py`.

```bash
bash scripts/s9_query_set_replay.sh
```

```
verify_repro_rc=0
REPRO PASS: 41/41 cases with position-by-position identical top5
network_event_lines=0
```

**Difference count 0 of 41.** This card adds a directory under `plans/` and changes nothing in the
repository; the replay is the check that says so in numbers rather than in prose. The run is wrapped
in the same audit hook as the rest of the chain, with the offline flags set so a missing local model
cannot silently become a download; `network_event_lines=0` covers it too.

**Determinism.** Every artefact is built twice and compared byte for byte:
`ledgers/REPLAY.txt` reads `REPLAY_PASS byte-identical on the second build`, 16 artefacts compared
over 7 builds plus the corpus scan. `ledgers/replay_pass1.txt` and `replay_pass2.txt` are kept.

**Zero network.** `ledgers/NET_AUDIT_SUMMARY.txt`: `network_event_lines=0` with hook-install receipts
proving the hook ran, over a chain that includes the corpus scan, the two build passes and the gate.
No download, no fetch, no model pull: the embedding model the replay needs was already on this
machine, and the offline environment flags are set in the script.

**What was re-verified, item by item** (`out/REVERIFY_UPSTREAM.tsv`, 58 checks, 0 fail). Every
consumed artefact was re-derived rather than trusted: the ontology file's sha256, release string, 3,531
term blocks / 3,335 active terms and 400 in-block `develops_from` statements; the navigation
artefact's closure audit and its 8 anchors; the label map's 80 labels / 65 mapped / 52 distinct ids
with every id's file line and label re-read; **all 79 rows** of `PRECURSOR_EDGES.tsv` re-walked hop by
hop; **all 408 nodes** of `cl_eye_subgraph.json` re-resolved against the file; the 58 DEV3 candidate
rows; D1's 32 rows / 22 ids with `n_direct_precursors` and `chain_reaches_RPC` recomputed; D2's 10
rows and D3's 61 rows / 14 ids re-resolved; and the peer's own delivery — 60 nodes, 34 edges, 61
register rows and the 36 unresolved classes re-derived as a set.

**Two errors of mine, kept rather than hidden.** Both were in my own measurement code, both were
caught by making the check re-derive from the artefact instead of trusting a summary, and both are
written into `s0_reverify_upstream.py`'s docstring because the next reader will make them again:

1. the first `develops_from` count was namespace-blind — 1,056 statements over the whole integrated
   release rather than 400 inside CL term blocks — which made the peer's correct 400 look wrong;
2. my first chain walk read `PRECURSOR_EDGES.tsv` in the child→parent direction, so all 34 of its
   transitive rows looked broken while they were fine.

A third, smaller correction belongs here too: the first version of the corpus scan refused every
single-token phrase (the peer's rule for candidate terms), which would have refused `macrophage`,
`fibroblast`, `granulocyte`, `melanocyte`, `pericyte` and `keratocyte` — six covered classes. The
policy is now explicit and recorded per phrase: single tokens are refused below 6 characters or on an
everyday-meaning stop list, and 40 phrases are refused with their reason in
`out/CORPUS_SCAN_META.json`.

**Measured resources**, from `ledgers/RESOURCE_READINGS.txt` (commands and raw output):

```
$ /usr/bin/time -v python3 scripts/s5_corpus_scan.py
  Maximum resident set size (kbytes): 206540        # 0.20 GiB
  Elapsed (wall clock) time (m:ss):   0:19.78
  Percent of CPU this job got:        132%
$ free -g      # before / after the chain
  available: 202 GiB / 202 GiB
```

One process, 0.20 GiB peak, no concurrency needed and none used; the heavy step runs under
`systemd-run --user -p MemoryMax=2G -p MemorySwapMax=2G` (≈10× the measured peak), and the 40 GiB
floor that would have stopped new concurrent work was never approached. This card uses no GPU (no GPU
step exists in it), which matters because the figure server's GPU is held by another workload.

---

## 10. What remains unreachable

Stated plainly, because it is the point of the register:

1. **44 of the 52 covered classes cannot be tied to any origin by anything on this machine** — 36
   with no local evidence at all, 8 with corpus co-occurrence only. A sparse confirmed graph plus this
   register is the correct outcome; a fuller graph would be assumption.
2. **The retinal progenitor axis carries photoreceptors only.** 49 of the 52 covered classes do not
   reach it, including every other retinal class. The corpus proposals in §6 are the only local route
   to those columns, and they are proposals.
3. **Four anchors carry no covered class at all** (haematopoietic stem cell, surface ectodermal cell,
   endodermal cell, mesenchymal cell), which is a break at the coarsest level, not at the leaves.
4. **15 library concepts have no ontology counterpart**, 11 of them developmental precursors our own
   panels are built around. Until a term is adopted upstream or an in-house assertion is anchored,
   those concepts cannot sit on an ontology-backed chain — they are nodes with keys and no edges.
5. **`transdifferentiation` does not exist in this release** (0 relation names, 0 occurrences), so the
   transdifferentiation questions the layer may eventually need cannot be answered from the ontology
   at all.
6. **The ontology cannot supply a marker** — it has no gene-name term for a cell type. "Each lineage
   carrying its own markers" is therefore entirely the sibling marker layer's work, and no amount of
   scaffold enumeration substitutes for it.
7. **The textbook layer this repository holds does not repair any decapitated branch** (0 items with a
   developmental assertion for one). Repair has to come from the papers we hold, and §6 shows what
   that yields: proposals, not edges.
8. **Direction conflicts are real and left unresolved** (12 pairs whose sources assert them both
   ways). Resolving one needs a lineage-tracing source or an explicit upstream statement, not a
   preference.

---

## 11. Reproduction and file map

```bash
cd /mnt/D/EyeKB/plans/devlineage_20261021/scaffold
bash scripts/run_all.sh                    # scan, builds, replay, manifest, gate, network audit
bash scripts/s9_query_set_replay.sh        # the recorded query set: 41/41, difference count 0
bash scripts/s10_resource_readings.sh      # the readings this report quotes
python3 scripts/s8_gate_scaffold.py        # the gate alone (rc 0 = PASS, rc 2 = FAIL)
(cd /mnt/D/EyeKB/plans/devlineage_20261021/scaffold && sha256sum -c out/MANIFEST.sha256)
```

| path | contents |
|---|---|
| `out/SCAFFOLD_NODES.tsv` | the enumerated node set, contract keys, per-field provenance |
| `out/SCAFFOLD_EDGES_CONFIRMED.tsv` | the confirmed graph, one row per ordered pair, graded |
| `out/SCAFFOLD_EDGES.tsv` | the full edge set = confirmed + not admitted (`R###`) |
| `out/SCAFFOLD_EDGES_NOT_ADMITTED.tsv` | the 24 rejected rows with their reasons |
| `out/DECAPITATED_BRANCHES.tsv` | the register: 64 branches, break point, cell mass, repair route |
| `out/PENDING_ASSERTIONS.tsv` | 68 repair proposals with resolvable anchors (never edges) |
| `out/COVERAGE_DENOMINATOR.tsv`, `.json` | the denominator, count by count |
| `out/ANCHOR_COVERAGE.tsv`, `out/RPC_AXIS.tsv` | per-anchor and per-class axis coverage |
| `out/CORPUS_*`, `out/PEER_WEAK_ROW_*`, `out/TEXTBOOK_REPAIR_CANDIDATES.tsv` | the scan, its verified anchors, the peer re-examination, the textbook negative |
| `out/FIRSTPASS_RECONCILIATION.tsv` | what happened to all 34 peer edges |
| `out/REVERIFY_UPSTREAM.tsv`, `.json` | 58 re-verification checks on everything consumed |
| `out/AFTERFACT_RECORDING_COVERAGE.tsv`, `out/AFTERFACT_SUMMARY.json` | the asymmetric coverage reading (the only files allowed to touch the recording) |
| `out/GATE_SCAFFOLD.json`, `out/MANIFEST.sha256` | the verdict and the hashes |
| `ledgers/`, `logs/` | chain log, both replay passes, the query replay, the network audit, resource readings, per-script stdout |

The evaluation recording is read **only** by `scripts/s7_afterfact_coverage.py`, after the graph is
frozen, in the direction the brief allows — as coverage. Its reading, for completeness: of the 721
recorded clusters and 1,495,330 cells, **19.88%** of cells sit on a class this scaffold anchors,
**55.5%** on a class whose branch is decapitated, **23.25%** on a class this enumeration never
reaches, and **24.62%** on a class carrying no CL term on our side. 13 of the decapitated classes in
the recording have at least one pending repair proposal attached. Those numbers are reported here as
coverage, and no edge in this card was derived from them.

Commits for this card (local only, nothing pushed), in order:

| commit | what it holds |
|---|---|
| `2fbe88fe7be944f574a23a75b818c134ffcb2a01` | this wave, first landing of the mirror (62 files) |
| `5c41367e27a1d13da8396a078bd07c0d4e10748a` | the mirror after the last chain run — the revision whose bytes `ledgers/DOC_SHA256.tsv` and `out/MANIFEST.sha256` describe |
| `ac76619107cbc00850bb48a03753335d468c79fb` | the commit that first records this line; a later commit records the table itself |

The mirror is `docs/plans/devlineage_20261021/scaffold/`; the construction site remains
`plans/devlineage_20261021/scaffold/`. Verify either one with `sha256sum -c out/MANIFEST.sha256`
(44 files, all OK) from inside it. Nothing outside that directory was written: `kb/`,
`mcp_server/`, the frozen ontology wave and the first pass's wave are byte-identical to how this card
found them (`G9`, 17/17 consumed files re-hashed).