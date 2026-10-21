# The developmental lineage layer

Reader page for the developmental side of the card. Built by `scripts/b1_build_lineage.py` from the
local ontology release, our own marker libraries, our own corpus and our own baseline entries;
judged by `scripts/gate_lineage.py`.

The PI's question was: what does the mesoderm become, what does the ectoderm become, what does the
retinal progenitor cell become - and what happens to the marker panel along the way? This page
answers it with what the sources actually support, and states the size of the part they do not.

## What the ontology can carry, and what it cannot

The relation is `develops_from` (`RO:0002202`, resolved from the file's own typedef). It is **thin**:
the whole release contains 400 statements of it, and of the 52 classes our library covers only 7
reach a germ-layer anchor through it:

| class | reaches | chain (labels, as read from the file) |
|---|---|---|
| retinal progenitor cell | neural ectoderm, ectoderm | RPC -> neurectodermal cell -> ectodermal cell |
| retinal rod cell | neural ectoderm, ectoderm | rod -> RPC -> neurectodermal cell -> ectodermal cell |
| retinal cone cell | neural ectoderm, ectoderm | cone -> RPC -> neurectodermal cell -> ectodermal cell |
| endothelial cell | mesoderm | endothelial cell -> mesodermal cell |
| microglial cell | mesoderm | microglial cell -> mesodermal cell |
| melanocyte | neural crest, neural ectoderm, ectoderm | melanocyte -> melanoblast -> migratory neural crest cell -> ... |
| oligodendrocyte | neural ectoderm, ectoderm | oligodendrocyte -> oligodendrocyte precursor cell -> ... -> neurectodermal cell |

That is the headline the PI asked for, and it is also the honest limit: **the retinal chain is
complete only for the photoreceptors.** Bipolar cells, amacrine cells, horizontal cells, retinal
ganglion cells, Mueller glia and RPE carry no `develops_from` statement at all in this release, so
the ontology alone cannot say what they come from.

For the classes the ontology cannot reach, the page reports the weaker, clearly-labelled tier: how
often one chunk of our own corpus states the class and a germ-layer term together. Nine classes have
only that, and 36 have neither.

| tier | classes | rows |
|---|---:|---:|
| `ontology_chain` (the ontology says it, with the chain) | 7 | 13 |
| `corpus_cooccurrence_weak` (a chunk states both; **not** a developmental claim on its own) | 9 | 12 |
| `unresolved` (no local evidence) | 36 | 36 |

The weak tier, in full, with counts and locators in `out/LINEAGE_GERM_LAYER.tsv`:

| class | candidate origin | chunks | papers |
|---|---|---:|---:|
| retinal pigment epithelial cell | mesenchyme | 13 | 12 |
| T cell | hematopoietic stem cell | 10 | 5 |
| corneal endothelial cell | neural crest | 7 | 7 |
| fibroblast | mesenchyme | 6 | 5 |
| retinal pigment epithelial cell | neural crest | 5 | 3 |
| fibroblast | neural crest | 4 | 4 |
| retinal ganglion cell | neural crest | 4 | 3 |
| plasma cell | mesenchyme | 4 | 3 |
| B cell | hematopoietic stem cell | 3 | 3 |
| keratocyte | mesenchyme / neural crest | 3 / 3 | 3 / 3 |
| myofibroblast cell | mesenchyme | 3 | 3 |

Read those as leads to check, not as findings. The 36 unresolved classes are listed by name in
`out/LINEAGE_UNRESOLVED_DEVELOPMENT.tsv`; they include the retinal interneurons, Mueller glia, RPE,
the vascular/stromal classes and most of the ocular surface groups. That list is the honest size of
the gap, and it is the specification for whatever supplies developmental literature next.

## The graph

* **60 nodes**: 52 classes our library covers (each with the ontology line and the number of panel
  genes we ship for it - 50 of the 52 have a panel) plus 8 germ-layer anchors
  (mesodermal, ectodermal, neurectodermal, neural crest, surface ectodermal, endodermal,
  mesenchymal, hematopoietic stem cell), every id resolved from the file.
* **34 edges**: 5 `develops_from_direct` (the file's own statements between two of our classes), 4
  `develops_from_transitive` (chains that pass through terms the library does not cover, e.g.
  melanocyte -> melanoblast -> migratory neural crest cell -> neural crest cell), and 25
  `germ_layer_membership` (the grouping, with its tier and evidence on the edge).
* **44 roots**, and that number is accounted for mechanically: 8 germ-layer anchors plus the 36
  classes with no local developmental evidence. Gate B2 fails if the root count ever stops matching
  that disclosure, so a disconnected node cannot hide.

## The marker changes along a differentiation step

`out/LINEAGE_MARKER_TRANSITIONS.tsv` - 100 rows, every one of them corpus-backed with a paper id and
a section. The two steps the ontology supports between two covered classes are RPC -> rod and
RPC -> cone. On the rod step, the panel gains the phototransduction genes and drops the progenitor
set:

| direction | gene | corpus chunks | corpus papers |
|---|---|---:|---:|
| gain | RHO | 1,397 | 490 |
| gain | NRL | 665 | 171 |
| gain | PDE6B | 342 | 141 |
| gain | NR2E3 | 283 | 100 |
| gain | GNAT1 | 174 | 89 |
| loss | PAX6 | 1,525 | 424 |
| loss | GFAP | 1,889 | 542 |
| loss | SOX2 | 790 | 291 |
| loss | OTX2 | 755 | 242 |
| loss | ATOH7 | 602 | 122 |

On the cone step the gains are `OPN1SW` (219 chunks / 87 papers), `OPN1MW` (152 / 74), `GNAT2`
(142 / 74), `PDE6H` (101 / 50), `ARR3` (244 / 98) against the same progenitor loss set.

Two caveats, stated because they matter more than the table does:

1. "gain"/"loss" here is the **difference between two marker panels along an ontology edge**, not a
   measured expression change. It says which genes our library uses to tell the two classes apart
   and that each of them is stated by papers we hold - not that they go up or down.
2. **Only 2 of the 34 edges can carry such a step at all.** Three more are steps where the parent
   has no panel of its own (`parent_panel_absent`: RPC -> neurectodermal cell, endothelial cell ->
   mesodermal cell, microglial cell -> mesodermal cell), and the rest are membership or
   non-stepwise relations. The panel-change-along-the-trajectory idea is therefore delivered where
   the ontology has a trajectory, and reported as a gap everywhere else.

## The stage axis is not collapsed

Developmental stage runs as its own axis in this repository, and this layer respects it:

* every node declares `organism_stage` (`developing` / `adult_or_unspecified`), decided by the
  ontology's own text for that term - with the matching word recorded in `stage_token`. Our own
  state labels are deliberately excluded from that decision, and disclosed separately in
  `our_label_stage_hints` (e.g. our `RPE_fetal` panel label does not move the RPE node to the
  developing side).
* 12 nodes are on the developing side: the 8 germ-layer anchors plus retinal progenitor cell,
  transit amplifying cell, progenitor cell and basal cell.
* gate B4 cross-checks every developing node against the structured class keys of the repository's
  **adult** baseline entries - 78 keys across the adult baseline files - and fails if one appears
  there. Reading: 0 offenders.
* 31 edges cross the stage axis. All of them are membership or develops_from edges, i.e. the axis is
  crossed by a stated developmental relation, never by an equivalence.

## What is not done here

* The lineage does not include the 15 library labels the ontology cannot name (the photoreceptor,
  bipolar, amacrine, horizontal, ganglion and glia precursors, the proliferating states, the
  lacrimal duct epithelium). They cannot be nodes under the gate's rule that every node's CL term
  must resolve; they are listed in `out/ONT_LABELMAP_V2.tsv` with their reason. Handing them a term
  is a decision for the card that owns the library vocabulary, not a side effect of this one.
* No marker in this layer is a claim about expression direction or about a fetal sample.
* `out/GAPCHECK_LINEAGE_vs_BENCHMARK.tsv` is the only file that reads the recorded clusters against
  the lineage, and it runs afterwards, as a gap check: 23 of the 52 class nodes are never the top
  candidate anywhere in the recording, and only two recorded groups have no lineage node - the
  abstentions (180 clusters / 347,690 cells) and `APC_MHCII_high` (13 / 20,487), which is exactly
  the class that carries no CL term.