# Lineage hygiene: the upstream transition table, the two panel copies, the scaffold re-point, and the evaluation-basis finding

Deliverable of the developmental-lineage hygiene wave, 2026-10-22. Everything below was measured
on this machine; every number has the command that produced it in `ledgers/chain.log` or in the
script that wrote the artefact next to it. No downloads and no network were used: the chain runs
with an audit hook installed (`ledgers/net_audit.log`, receipts > 0 and 0 events). No file under
`kb/` was written; nothing was activated; every intermediate artefact is kept.

Read with:
- `out/GATE_READOUT.md` (the wave's gate, 12 checks)
- `scripts/run_all.sh` (one command rebuilds and judges the whole delivery; chain ~25 s)
- `out/ITEM1_SUMMARY.json`, `out/ITEM1_RECONCILIATION.json`, `out/ITEM3_SUMMARY.json`,
  `out/ITEM2_RECONCILIATION_LEDGER.json`, `out/ITEM4_SUMMARY.json`,
  `out/ITEM4_NONBENCHMARK_FLAG_SPEC.md`, `out/CLEAN_CLONE_CHECK.json`

`out/MANIFEST.sha256` pins `out/` and `scripts/` — every number this report cites. This report
itself is not hash-pinned, on purpose: it states the gate's verdict, and the gate runs after the
manifest. `ledgers/` holds the run's own logs, written while the chain runs, and is kept but not
hash-pinned for the same reason.

Upstream material this wave reads (never copies over): the first-pass developmental lineage layer
(`plans/cl_depth_devlineage_20261021/`), the marker layer (`plans/devlineage_20261021/markers/`),
the scaffold (`plans/devlineage_20261021/scaffold/`), the frozen contract
(`plans/devlineage_20261021/DATA_CONTRACT_devlineage_v1.md`), the shipped panels under `kb/markers/`
in both trees, and the local literature corpus.

---

## Item 1 — the upstream transition-table defect, fixed at the root

**What was wrong.** `plans/cl_depth_devlineage_20261021/scripts/b1_build_lineage.py` emits one row
per gene per edge per direction into `out/LINEAGE_MARKER_TRANSITIONS.tsv`, with a column
`in_child_panel`. That column was the literal string `"yes"` in the source (line 352), so all 90
`loss` rows claimed the child panel contains a gene that a loss row is, by construction,
`parent_genes - child_genes` — i.e. absent from the child panel. The sibling column
`in_parent_panel` was computed honestly all along.

| measurement | before | after |
|---|---|---|
| rows in the table | 100 (10 gain, 90 loss) | 100 (unchanged) |
| distinct values of `in_child_panel` | `{yes}` | `{yes, no}` |
| rows whose value contradicts their own `direction` | 90 | 0 |
| rows whose value changed | — | 90 (`yes`→`no`), 0 the other way |
| columns that changed | — | `in_child_panel` only, 90 cells |

Command: `python3 scripts/w5_01_fix_upstream.py` (idempotent). Evidence:
`out/ITEM1_ROW_CHANGES.tsv` (per row, before/after), `out/pre/LINEAGE_MARKER_TRANSITIONS.tsv.pre_v5`
(the pre-image bytes, sha256 `6f849c05…`), `out/ITEM1_B1_DIFF.txt` (the one-line diff of the
builder).

**The fix is made in the builder, not in the table.** A hand-edited table would be clobbered by
the upstream chain's own replay and would leave the defect in the code. The shadow rebuild proves
this is the only thing that moved: four of the six artefacts the builder writes came back
byte-identical, `LINEAGE_SUMMARY.json` differs only in the output paths it records (normalised and
compared), and exactly one artefact changed *value* — the transition table. On a later run the
rebuild changes nothing at all, which is the stronger statement: the table on disk is exactly what
the builder produces.

**Independent corroboration of the corrected values.** The membership claim is re-derived with a
*different* panel loader (the marker layer's own, plus its label-attachment table) rather than
with the builder that made the table: 100/100 rows agree with the corrected column
(`out/ITEM1_INDEPENDENT_CHECK.tsv`).

**The upstream chain still ends green.** `out/LINEAGE_MARKER_TRANSITIONS.tsv`'s row in
`out/MANIFEST.sha256` moved with it (`out/pre/MANIFEST_LINE_CHANGE.json` records before and after:
`6f849c05…` → `16abc48e…`), and the upstream gates were re-run: lineage gate B **PASS** (0 failed;
its marker-trace check reads `marker rows=100 corpus-supported=100`) and the report-number check
**PASS**. Logs: `logs/item1_upstream_gate_B.txt`, `logs/item1_report_number_check.txt`.

### The weaker grading: measured, adopted at the layer that can carry it, and why not in place

The upstream column `support_status` grades a marker change on "the corpus mentions this gene
anywhere" (`n_chunks > 0`). The marker layer grades it on four conditions at once: the chunk
carries the gene token, its species is admissible for the node, it names the target group, and it
is developmentally scented. This wave applies the marker layer's own rule to the same 100 rows,
from the raw corpus (its own pass, 244,877 chunks, peak 0.307 GiB, 10.1 s, and the same
`m0` rule constants imported rather than copied):

| grading of the same 100 rows | gain (10) | loss (90) |
|---|---|---|
| upstream `support_status` = `corpus_supported` | 10 | 90 |
| four-condition strict, every chunk eligible | 10 | 88 |
| four-condition strict, only the ten rows per gene the marker layer recorded | 10 | 88 |

Two readings, and the second matters: the marker layer's admission test only ever saw its own
best ten rows per gene. Measured here, restricting the strict test to those same ten rows gives
the *same* answer as the full pass (98/100 strict-supported either way), so that restriction is
not binding on this table — it is a bound, not a caveat.

**Reconciliation with the superseding artefact.** `markers/out/MARKER_CHANGE_EDGES.tsv` is the
superseding artefact, and the two now agree exactly where they overlap:

- gain side: the strict test's 10 genes are the superseding artefact's 10 genes, set-for-set
  identical, 10/10 rows agreeing;
- loss side: the superseding artefact writes no loss row at all, by design — it carries all 90 in
  its refusal register with reason `detection_conditions_insufficient`, because panel absence is
  not a detection result. The upstream table's weak column marks those 90 as corpus-supported; the
  strict reading marks 88 of them supported (`AHI1`, on two edges, has no chunk meeting all four).
  The two columns therefore answer different questions on the loss side, and
  `out/TRANSITION_TABLE_RECONCILED.tsv` carries both readings plus the supersession mapping, so
  no silent difference remains between the two transition tables.

**Why the upstream column was not re-purposed in place.** `support_status`'s values are part of
the upstream gate's contract (its check admits exactly `corpus_supported | no_corpus_hit`, and a
`no_corpus_hit` row may not carry a corpus locator). Re-grading that column strictly would either
make the gate reject an unknown status, or force deleting the locators of rows that do have corpus
hits — losing evidence. It would also need chunk-level attributes the upstream index does not
carry (`out/CORPUS_GENE_INDEX.tsv` has gene / counts / locators only). So the stronger grading is
adopted **as the reconciled reading** (`support_status_strict`, `support_status_strict_top10`, the
four per-condition counts and the strict locator, in
`out/TRANSITION_TABLE_RECONCILED.tsv`) and the weak column is retained, labelled, and superseded —
not silently overwritten.

**Residual.** `AHI1` is corpus-supported by the weak rule and refused by the strict rule on two
loss rows; recorded, not resolved, because the loss side claims nothing either way.

---

## Item 2 — the two `kb/markers` copies

**The claim was re-measured, not trusted.** 20 files in total: 16 shared, and all 16 are
byte-identical; 2 exist only in the git tree; 2 only in the data-volume tree
(`out/ITEM2_BYTE_LEDGER.tsv`, one row per file with both sha256 values).

| file | data tree | git tree | why |
|---|---|---|---|
| `markers_v11_lensiris_increment.json` | absent | present | committed in the git tree after the last content copy; the committed release's loader already maps it as `lensiris_v11` |
| `markers_v12_holefill_increment.json` | absent | present | same; mapped as `holefill_v12` |
| `markers_v8_dev_retina.json` | present | absent | never tracked in this repository's history (`git log --all` over that path is empty) |
| `markers_v9_dev_retina.json.v1` | present | absent | a pre-revision copy of a tracked file; no consumer names the `.v1` |

**Which copy is authoritative for the loader — answered by the loader's own rule.** Each tree's
loader resolves `kb/markers` relative to its own package root
(`mcp_server/eyekb_core.py`: `EYEKB_ROOT = Path(__file__).resolve().parents[1]`, `KB = EYEKB_ROOT
/ "kb"`, `MARKER_DIR = KB / "markers"`), and **neither copy has a cross-tree fallback** (searched
both sources). So the copy that is authoritative for a run is the copy inside the tree the service
is started from: the data-volume tree for the running service, the git tree for the release and for
any clone of it. The repository's own convention for this tree pair is the mirror direction —
"copy, not move; the data-volume originals are not modified".

**What the divergence actually does — measured.** The committed release's loader maps **12**
libraries; the data-volume tree's loader maps **10** and is an older revision that does not name
the two increments at all. The two files the data tree lacks are exactly the two the release's
loader names (`out/ITEM2_LOADER_RESOLUTION.json`). Consequence, and it is the sharp one: the
loader guards its panel open with `p.is_file()` (line 1258 of the site copy), so a declared panel
that is missing is **skipped silently** — a `lensiris_v11` or `holefill_v12` query on a tree
without those files would return no markers rather than raise.

**Decision, and where this card stops.** No file is deleted and no existing file's bytes are
touched. The two trees are made set-equal by copying the missing files in, byte-identically, in
the direction the evidence supports (the git side is newer: it carries both the panels and the
loader entries that name them). That execution is **not performed in this card**, because this
card's red lines forbid a `kb/` body change and any activation, and the marker layer's gate
rejects any `kb/` file whose mtime is newer than that card's session start — a write here would
leave an already-green gate red behind it. Instead:

- `out/ITEM2_RECONCILIATION_LEDGER.json` — the decision, its evidence, and both residual items;
- `out/ITEM2_SYNC_KB_MARKERS.sh` — the idempotent executor, **dry run by default** (`--apply` to
  execute, `--no-mirror` to skip the direction that changes the release surface). Its dry run on
  this tree prints: `WOULD v11: repo → data`, `WOULD v12: repo → data`, `WOULD v8: data → repo`.
  Nothing is ever removed, and a copy is skipped when the destination already holds the same bytes.

**Residual (needs a card that may write `kb/`).** (1) `markers_v8_dev_retina.json` is not in the
release, yet the marker layer consumes it (`dev_v8`) and the first-pass lineage builder lists it —
both resolve it only through the data tree, so a fresh clone cannot reproduce that share. (2) The
`.v1` backup should be registered as a non-panel file rather than mirrored or deleted.

---

## Item 3 — the marker layer re-pointed at the scaffold

The frozen contract named `plans/devlineage_20261021/scaffold/` as the node and edge source; that
directory did not exist when the layer was built, so it consumed the first pass's
`LINEAGE_{NODES,EDGES}.tsv`. The scaffold has since landed (103 nodes, 51 confirmed edges, 44
decapitated branches), and this wave re-points the layer at it.

**How.** The builders themselves — the marker layer's own `m1`/`m2`/`m3`/`m4` — are executed
**unmodified**; only the node list and the edge list they are handed change. Two adapter tables
translate the scaffold's published columns into the column contract those builders consume, and
the module-level constants are overridden in place (`M.OUT`, `M.L2_NODES`, `M.L2_EDGES`). Every
translation decision is written out column by column in `out/adapter/COLUMN_MAPPING.tsv`, and
nothing is dropped: 103/103 nodes and 51/51 edges are accounted for, with zero unresolved
endpoints (`out/ITEM3_SUMMARY.json`). The corpus index the marker layer built is scaffolding-neutral
and is carried over byte-identically, so the re-point is a controlled experiment.

**What changed.**

| measurement | before (first pass) | after (scaffold) |
|---|---|---|
| nodes | 70 (60 scaffold + 10 in-house) | 103 (all scaffold; the scaffold's 15 `NO_MATCH` concepts absorb the in-house set) |
| node keys kept unchanged | — | 62 |
| node keys that moved | — | 8 (same class, different key) |
| node assertions | 1,043 | 1,072 |
| assertions resolving under the same key | — | 939 |
| assertions resolving after their node's key moved | — | 102 |
| assertions relocated to another node | — | 2 (`PCNA`, `SOX2`) |
| assertions that fail to resolve | — | **0** |
| nodes with at least one assertion | 59 | 64 |
| nodes with no assertion | 11 | 39 |
| edges | 34 | 51 |
| edge relation types | 9 ontology / 25 ancestral | 40 ontology / 11 ancestral |
| edges admitted stepwise | 2 | 2 |
| marker-change assertions | 10 | 10 |
| gap-register rows | 226 | 266 |

Detail files: `out/ITEM3_NODE_KEY_MOVES.tsv`, `out/ITEM3_ASSERTIONS_MOVED.tsv`,
`out/ITEM3_ASSERTIONS_LOST.tsv`, `out/ITEM3_NODES_WITH_NO_ASSERTION.tsv`,
`out/ITEM3_EDGE_CROSSWALK.tsv`, `out/ITEM3_NEW_MARKER_CHANGES.tsv`.

**Numbers that moved, with the reason.**

1. **The stage axis got more conservative, and 8 node keys moved because of it.** The scaffold
   derives a library class's stage from the class's own declared context, while the first pass
   matched the class name against the repository's baseline files. Measured: 6 nodes moved
   `adult → unknown` (`T cell`, `Endothelial cell`, `Astrocyte`, `B cell`, tear-secreting cell,
   `Schwann cell` — each appears somewhere inside an adult baseline file, but none declares its own
   adult stage), 2 moved `developing → unknown` (`NRPC_early`, `NRPC_late`), and **0 nodes moved to
   adult**; adult nodes 22 → 16. The re-point therefore relaxes nothing: unknown never becomes
   adult, which is what the contract asks for.
2. **The 102 moved assertions are the join moving with those 8 keys**, not evidence moving. The
   2 relocated assertions are the interesting case and they are a correction: the first pass
   attached the state programmes `TAC_proliferating` / `Retinal_Proliferating`'s genes to the
   transit-amplifying-cell *identity* node via an in-code mapping table; the scaffold gives those
   concepts their own nodes, so `PCNA` and `SOX2` now sit on
   `dl:NO_MATCH:TAC_proliferating|…` and `dl:NO_MATCH:Retinal_Proliferating|…` instead. They are
   not lost — the (gene, node) pairs that have no home at all number zero.
3. **Only 16 of the first pass's 34 edge pairs survive**; 35 of the 51 are new. The first pass
   carried 25 `germ_layer_membership` edges derived from corpus co-occurrence, which the scaffold
   re-examined (11 not admitted, 9 re-typed, 7 merged — see its own
   `FIRSTPASS_RECONCILIATION.tsv`) and replaced with 11 ontology-anchored origin edges. The
   marker-change count did **not** move (10), because only two of the new direct edges have a
   panel at both ends; the other 38 direct edges are refused as `parent_group_has_no_panel` (36) or
   `marker_change_not_available` (2). Coverage grew where the scaffold added nodes, not where the
   layer claims marker changes.
4. **64 of the 103 node keys differ from the key strings the scaffold publishes.** The difference
   is systematic and deliberate: the scaffold leaves `sp`/`ts` as `unknown` for most library
   classes, while the contract's key builder derives the declared context from the panels (e.g.
   `…|sp=human|ts=retina|…`). Measured per kind in `out/ITEM3_KEY_SPELLING.tsv`: 28/28 ontology
   intermediates and 8/8 origin anchors match the scaffold string exactly; only 3 of 67 library
   classes do. Adopting the scaffold's strings verbatim would discard declared context and break
   the join with the assertion set that already exists, so the contract key grammar remains the
   authority and every difference is listed.

### The one conflict this re-point exposes, and how it is resolved

The edge builder derives an edge's `evidence_grade` from the relation type it was handed (a direct
ontology step becomes `direct_lineage_support`). The scaffold grades **all 51** of its confirmed
edges `identity_conversion_not_direct`, and says in its own summary that no local artefact supports
`direct_lineage_support`, so none is claimed. Measured: **51/51 edges disagree** — the builder
would write `direct_lineage_support` on 40 and `textbook_or_review_distant_origin` on 11, where
the source says `identity_conversion_not_direct` on all 51 (`out/ITEM3_GRADE_RECONCILIATION.tsv`).

The contract forbids a relation or an evidence grade being upgraded silently, so the source's grade
is made to govern and the builder's value is kept beside it:
`out/repointed/EDGES_RECONCILED.tsv` (51 rows, `evidence_grade` = the source's,
`evidence_grade_builder` retained) and `out/repointed/MARKER_CHANGE_EDGES_RECONCILED.tsv` (the 10
marker-change assertions, whose grade moves from `direct_lineage_support` to
`identity_conversion_not_direct`). **Decision-ready residual:** the grading rule belongs to the
marker layer, and a card that owns it should adopt the source's grade directly rather than rely on
a reconciliation overlay; this wave did not change the rule, because a grading rule is a scientific
statement and this card's mandate is hygiene.

---

## Item 4 — the evaluation-basis finding

75 genes were refused by the marker layer because their only basis is an evaluation volume, and the
hole-fill increment was refused outright because its own scope says it fills the measured coverage
holes of the 28-volume / 721-cluster run. Both refusals are correct under the contract's red line
(never derive a marker or a lineage edge from the evaluation volumes' own queries). The question
this item answers is which shipped panels carry such genes.

**Which panels, and how many.** Measured per panel, three readings distinguished because "basis" is
not one thing — the full table is `out/ITEM4_EVAL_BASIS_BY_PANEL.tsv` and the per-gene detail is
`out/ITEM4_EVAL_BASIS_BY_GENE.tsv`:

| panel | genes | A: refused, evaluation-only basis and no independent evidence | B: admitted, but the entry's own basis is evaluation-only | C: independent or mixed |
|---|---|---|---|---|
| `markers_v9_dev_retina.json` | 149 | **67** | 0 | 82 |
| `markers_v8_dev_retina.json` | 28 | 0 | 0 | 28 |
| `markers_v6_retina_repair.json` | 141 | 0 | 0 | 141 |
| `markers_v10_antseg_increment.json` | 277 | 0 | 0 | 277 |
| `markers_v5_retina_interneuron.json` | 156 | 0 | 0 | 156 |
| `markers_v11_lensiris_increment.json` | 80 | 0 | 0 | 80 |
| `markers_v7_panel_increment.json` | 89 | 0 | 0 | 89 |
| `markers_v4.1_clean.json` | 43 | 0 | 0 | 43 |
| `markers_k9_ocs_increment.json` | 20 | 0 | 0 | 20 |
| `markers_v6_face_increment.json` | 18 | 0 | 0 | 18 |
| `markers_v6_lacrimal_increment.json` | 7 | 0 | 0 | 7 |
| `markers_membrane_v1.json` | 199 | 0 | 0 | 199 |

So the answer is one panel: **`markers_v9_dev_retina.json`, 67 of its 149 genes** (45%). The same
67 genes produce 75 refusal rows in the gap register, because a gene can sit in more than one label
of a panel; the per-panel and per-gene readings reconcile on the gene count (gate check G7).
Reading B is empty: no admitted gene rests on an evaluation-only panel basis. Its sibling panel
`markers_v8_dev_retina.json` ships the same lineage concepts and carries **0** such genes — every
gene it holds has a literature track — which is why the refusal register names `dev_v9` only.

The refused panel `markers_v12_holefill_increment.json` (present in the git tree only): 17 entries,
204 genes, and its own scope names the evaluation run's measured holes. `markers_v11_lensiris_increment.json`:
3 entries, 80 genes, scope = two tissues the project's own coverage declaration names as gaps — not
the benchmark's holes — so it is consumed, and it is the panel whose genes carry no evaluation-only
basis.

**What a non-benchmark flag would need to assert** — the decision-ready specification, in
`out/ITEM4_NONBENCHMARK_FLAG_SPEC.md`:

- **granularity: per entry inside a panel, and per gene inside that entry — not per file.** Measured
  reason: the three readings coexist inside one file (a panel whose declared selection basis is an
  evaluation volume still carries independently-sourced genes; a panel whose basis is independent
  can still carry an evaluation-only entry), so a file-level bit would either condemn or exonerate
  wrongly;
- a **basis class from a closed vocabulary**: `independent_literature |
  independent_in_house_atlas_non_benchmark | evaluation_volume | evaluation_report_holes | unstated`;
- when the class is `evaluation_volume` or `evaluation_report_holes`, the entry must carry an
  **independent anchor per gene** (a PMID or a corpus row) for any gene it wants to be usable for a
  marker or lineage claim — the flag says "this candidate list leaned on the benchmark", not "this
  gene is unusable";
- the **name of the evaluation artefact** it leaned on (volume id / report id), so the exclusion
  list can be re-derived instead of trusted;
- an explicit statement of what the flag does **not** claim (not that the gene is wrong, and not
  any authority to edit a shipped panel);
- **enforcement at the consuming layer**, not by rewriting a shipped panel: the marker layer
  already implements exactly this test for reading A (the four-condition corpus rule item 1
  re-measures); reading B is what is not yet machine-checkable, and it is empty today.

Nothing was activated and no panel body was changed. Status: registered.

---

## Red lines, and how each is answered

| red line | evidence |
|---|---|
| never derive a marker or a lineage edge from the evaluation volumes' own queries | the refusal is preserved and reported (item 4); every anchor this wave writes is a corpus row or a panel entry, and the corpus passes reuse the marker layer's own exclusion list |
| zero downloads, zero network | audit hook over the whole chain and all children: `ledgers/net_audit.log` receipts > 0, events 0; `ledgers/NET_AUDIT_SUMMARY.txt` = `NET_ZERO_PASS` |
| repository-facing text English only | all artefacts and the mirror |
| default behaviour byte-identical, proven by replaying the recorded query set | the recorded 721-query set replays to its recorded ranking: 721 identical, 0 differing (`out/GATE.json` check G9) |
| no `kb/` body change and no activation | `out/ITEM2_BYTE_LEDGER.tsv` re-verified at gate time: both trees' file sets and hashes unchanged by this card (check G6); the executor is a dry run by default; item 4's summary records `activation: none`, `panel_bodies_changed: 0` |
| real measurements only, with commands pasted | `ledgers/chain.log` (every step, with counts), `logs/*.log`, and the resource readings below |
| keep every intermediate artefact | 92 files retained, including pre-images (`out/pre/`), the shadow rebuild (`out/rebuild/`), the adapter tables and their column mapping, and the reconciled views |
| do not push; commit locally and report the hash | mirror committed locally; the hash is recorded in `ledgers/COMMIT.txt` (and in the wave's own report once committed) |
| gate chain green in a clean clone, not only in the author's tree | `out/CLEAN_CLONE_CHECK.json`: the wave's gate re-run *inside* a `git clone` of the commit under test — clone gate PASS, 75 mirrored files compared, 0 differing |

## Resource readings

| step | wall | peak memory |
|---|---|---|
| corpus pass, four-condition regrade over 244,877 chunks | 10.1 s | 0.307 GiB RSS (probe before the run: 0.29 GiB at 100k chunks, so the cap was a guard) |
| probe run (5 batches, 100k chunks) | 4.7 s | 0.29 GiB |
| scaffold re-point, whole layer through four builders | 1.2 s | 48 MB (systemd unit peak) |
| recorded-query replay | 5.8 s | — |
| whole chain (`bash scripts/run_all.sh`) | ~25 s | one process at a time; nothing parallel was needed |

Heavy steps were run under `systemd-run --user -p MemoryMax=… -p MemorySwapMax=2G` with the cap
chosen from the measured RSS, as the brief asks. Available memory during the wave: 198–202 GiB (no
concurrency decision was needed at these sizes).

## Residual and decision-ready items

1. **The grading rule behind the 51/51 edge-grade conflict** (§item 3) — the marker layer should
   adopt the source's grade in its own builder instead of relying on this wave's reconciliation
   overlay. Owner: the marker-layer line.
2. **The two `kb/markers` trees are decided but not yet set-equal** (§item 2) — one command,
   `bash out/ITEM2_SYNC_KB_MARKERS.sh --apply`, run from a card that may write `kb/`; then re-take
   the release identity in the same commit as the mirror direction. Owner: a `kb/`-writing card.
3. **`markers_v8_dev_retina.json` is not in the release** yet is consumed by the layer and by the
   first-pass builder — owner: the repository-sync line.
4. **`AHI1`** is corpus-supported under the weak rule and refused under the strict rule on two loss
   rows (§item 1) — recorded, not resolved: the loss side claims nothing either way.
5. **The marker layer's own admission test only ever saw ten corpus rows per gene.** Measured not to
   bind on this table (both readings agree), but it is a bound worth carrying forward to any larger
   gene set.