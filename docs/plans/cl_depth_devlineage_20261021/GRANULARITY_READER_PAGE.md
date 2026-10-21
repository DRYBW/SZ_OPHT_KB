# What our classes are, relative to the literature

Reader page for the granularity side of the card. Everything below is recomputed from
`out/GRANULARITY_FOURWAY_721.tsv`, which is produced by `scripts/a2_fourway_721.py` and re-judged by
`scripts/gate_ontology_nav.py` rule A4. The ontology is the local release the card names,
`releases/2026-06-08`.

## Why a lookup table was not enough

Our class `Endo` names CL:0000115 (endothelial cell). The literature in the same clusters writes
`endothelial cell of artery` (CL:1000413). No lookup table can call that a disagreement, and no
hand-written exception list survives contact with the next dataset: the ontology already knows the
answer, in three steps:

```
CL:1000413 endothelial cell of artery
  -> CL:0000071  blood vessel endothelial cell
  -> CL:0002139  endothelial cell of vascular tree
  -> CL:0000115  endothelial cell          <- our term
```

A judge that only compares a term with its direct parent sees three unrelated terms here. The
ancestor closure sees one cell type named at two granularities. That is the whole point of
`scripts/ont_nav.py`.

## The five verdicts, over the 721 recorded clusters

Source: `out/GRANULARITY_FOURWAY_721.tsv` (721 rows, 1,495,330 cells). Command:

```bash
python3 scripts/a2_fourway_721.py            # writes the table and the summary
python3 scripts/gate_ontology_nav.py         # A4 re-derives every row from the ontology
```

| verdict | meaning | clusters | cells | share of cells |
|---|---|---:|---:|---:|
| `same_term` | the identical CL term under a different name | 212 | 480,120 | 32.1% |
| `we_are_coarser` | our term is an ancestor of theirs | 150 | 342,552 | 22.9% |
| `we_are_finer` | their term is an ancestor of ours | 15 | 36,090 | 2.4% |
| `true_mismatch` | neither is an ancestor of the other | 151 | 268,391 | 17.9% |
| `no_mapping` | one side carries no CL term (see below) | 193 | 368,177 | 24.6% |

`no_mapping` is not one thing. On this recording all of it is on our side, and it splits into:

* **180 clusters / 347,690 cells - we abstained.** No candidate at all. Abstention is a legal
  outcome in this project and is excluded from accuracy-style rates.
* **13 clusters / 20,487 cells - we answered with a class that has no CL term.** This is our own
  naming debt (`APC_MHCII_high`, `Proliferating`), and it is the kind of debt that should be paid
  rather than filed under abstention.

## The reading the external tester used, and what it was measuring

The family-level regex (the reading that produced his 8.0%) scores **41.73%** agreement on this
same recording - 297 clusters / 624,029 cells - a number our recomputation reproduces exactly,
which is what makes the two implementations comparable at all.

| reading | agreement |
|---|---:|
| family-level regex | 41.73% of cells |
| ontology, identical term only | 32.11% of cells / 42.60% of the 1,127,153 judged cells |
| ontology, identical term + granularity | 57.43% of cells |

For the mass his regex called **inconsistent** (222 clusters / 451,272 cells = 30.2%), the
decomposition is:

| what it really is | cells | share of all cells | share of the inconsistent mass |
|---|---:|---:|---:|
| pure naming (same CL term) | 49,109 | 3.3% | 10.9% |
| granularity (we coarser or finer) | 131,487 | 8.8% | 29.1% |
| survives as a real disagreement | 217,976 | 14.6% | 48.3% |
| no mapping on one side | 52,700 | 3.5% | 11.7% |

So of the disagreement mass, **two fifths is vocabulary and granularity, not recognition error** -
and the rest is the part worth working on.

## Reconciliation with his published table

His report lists 13 pairs, 43 clusters, 119,672 cells, which he reads as the same cell under
ontology authority. His per-cluster file for that arm is not on this machine, so the comparison
below is on the same (our class, their label) pairs, against our local recording:

| our class | their label | his cells | our cells | clusters | our verdict | path |
|---|---|---:|---:|---:|---|---|
| Endo | blood vessel endothelial cell | 23,948 | 23,948 | 7 | coarser | CL:0000071 -> CL:0002139 -> CL:0000115 |
| Mac_Tissue | macrophage | 23,468 | 23,468 | 6 | same term | - |
| BC | rod bipolar cell | 19,682 | 23,484 | 8 | coarser | CL:0000751 -> CL:0000749 -> CL:0000748 |
| Endo | endothelial cell | 18,780 | 20,155 | 11 | same term | - |
| Endo | fenestrated endothelial cell | 9,456 | 9,456 | 3 | coarser | CL:0000666 -> CL:0000115 |
| Endo | endothelial cell of artery | 6,987 | 6,987 | 1 | coarser | CL:1000413 -> CL:0000071 -> CL:0002139 -> CL:0000115 |
| Endo | endothelial cell of venule | 5,261 | 5,261 | 1 | coarser | CL:1000414 -> CL:0000071 -> CL:0002139 -> CL:0000115 |
| NK | natural killer cell | 4,378 | 4,378 | 1 | same term | - |
| BC | OFFx cell | 4,062 | 4,062 | 3 | coarser | CL:4033036 -> CL:0000750 -> CL:0000748 |
| BC | ON-blue cone bipolar cell | 2,837 | 2,837 | 1 | coarser | CL:4033019 -> CL:0000749 -> CL:0000748 |
| Astro | glial cell | 492 | 492 | 1 | finer | CL:0000127 -> CL:0000126 -> CL:0000125 |
| Endo | endothelial cell of vascular tree | 205 | 205 | 1 | coarser | CL:0002139 -> CL:0000115 |
| SMC | smooth muscle cell | 116 | 1,967 | 2 | same term | - |
| **total** | | **119,672** | **126,700** | **46** | | |

Our verdict agrees with his relation for all 13 pairs (coarser / finer / same cell), including the
one where the direction is ours-finer (`Astro` vs `glial cell`). The cell totals differ by +7,028
(+5.9%), concentrated in three pairs - `BC` vs rod bipolar cell (+3,802), `Endo` vs endothelial
cell (+1,375), `SMC` (+1,851) - because his table is the post-update arm (2026-10-21) and our local
recording is the 2026-10-20 production arm. We cannot recompute his arm here: his per-cluster file
for that rerun is not on this machine. Across the whole recording, the equivalent mass on our arm
is **60 clusters / 180,596 cells (12.1% of all cells)**, i.e. larger than his 43/119,672 on his arm
for the same reason.

## Where our classes are systematically coarse: the candidate list

`out/CHILD_TERM_CANDIDATES.tsv` - 56 pairs, 342,552 cells involved, 25 with corpus support. The
head of the list:

| our class | our CL | child CL | child term read from the file | depth | clusters | cells | corpus support |
|---|---|---|---|---:|---:|---:|---|
| SMC | CL:0000192 | CL:1000443 | ciliary muscle cell | 1 | 5 | 26,532 | states the term (1 chunk / 1 paper) |
| Endo | CL:0000115 | CL:0000071 | blood vessel endothelial cell | 1 | 7 | 23,948 | states the term (5 / 4) |
| BC | CL:0000748 | CL:0000751 | rod bipolar cell | 1 | 8 | 23,484 | states the term (76 / 5) |
| AC | CL:0000561 | CL:4030028 | glycinergic amacrine cell | 1 | 13 | 15,718 | states the term (3 / 3) |
| AC | CL:0000561 | CL:4030027 | GABAergic amacrine cell | 1 | 13 | 14,442 | states the term (8 / 5) |
| Fibroblast | CL:0000057 | CL:0002363 | keratocyte | 1 | 3 | 11,836 | synonym only (42 / 8) |
| HC | CL:0000745 | CL:0004217 | H1 horizontal cell | 1 | 3 | 11,275 | states the term (11 / 6) |
| Schwann | CL:0002573 | CL:0002376 | non-myelinating Schwann cell | 1 | 3 | 10,914 | no corpus hit |
| Endo | CL:0000115 | CL:0000666 | fenestrated endothelial cell | 1 | 3 | 9,456 | no corpus hit |
| RGC | CL:0000740 | CL:4033047 | OFF midget ganglion cell | 1 | 1 | 9,022 | states the term (4 / 3) |

Two readings worth keeping:

* **12 of the 56 pairs are multi-hop** (our term is two or more `is_a` steps above theirs), 52,566
  cells in total. A direct-parent comparison would score every one of them as a mismatch.
* **31 of the 56 have no corpus support at all.** Most are the fine retinal bipolar and horizontal
  subtypes (`diffuse bipolar 1/2/3b`, `invaginating midget bipolar`, `H2 horizontal cell`). Our
  corpus does not use those names; adopting them would need the naming to come from somewhere, and
  that is a decision for a later card, not a silent import here.

Nothing in this card adopts a child term. The list is decision input: each row carries the CL id
read from the file, the file line, the recorded cell counts, and where our corpus does (or does
not) use the term.