# Design — the marker layer of the developmental lineage (card V2)

This document fixes, before any artefact is built, the four things a reader needs in order to
disagree with the delivered layer: how a node is keyed, what an evidence anchor is and which
anchors are admissible, how the three roles are separated mechanically, and how a gap is
classified. It builds strictly against `../DATA_CONTRACT_devlineage_v1.md`; the one place the
contract's fields are genuinely insufficient is raised in section 6 rather than forked.

## 1. Scope and the sources that are actually local

The layer is assembled from what is on this machine. No download, no network, no read of the
evaluation side.

| source | role in this layer | what it can carry |
|---|---|---|
| `plans/cl_depth_devlineage_20261021/out/` (card L2, landmarked on disk) | the node list, the edge list, the ontology closure, the corpus term/gene index | scaffold; superseded where noted |
| `kb/markers/markers_*.json` (12 shipped panel files) | identity panels per class | gene lists **with per-gene provenance where the panel states one** |
| `kb/link_registry/LINK_REGISTRY_v1.jsonl` (161 rows) | citation spine | per entry, the PMIDs whose **own full text** contains the entry's genes, with a chunk locator |
| corpus `…/literature_db/v2.6-dev_2026-10/` (`chunks.parquet` 244,877 rows + `papers.jsonl`) | full text on disk | a resolvable row locator per gene, plus paper species / tissue / full-text flag |
| `kb/textbook_layer/` (81 items, page anchors) | origin statements only | **never** gene-level evidence (the layer's own ban) |
| `kb/literature_db/role_flag_devline_2026-10*.jsonl` | anti-circularity | papers that must not be cited as anchors |

The evaluation side is a **negative** input: the 28 recorded evaluation volume names, the working
tree `oss_check_20261019`, the dev-exam substrate `GSE268630` and its paper `39117640` are excluded
by construction and re-checked by the gate.

## 2. Node key (contract §Node key, instantiated)

```
dl:<canonical_cl_id>|sp=<species>|ts=<tissue_context>|st=<organism_stage>|es=<experimental_system>
```

* the 52 covered classes keep their CL id exactly as read from
  `downloads/cl.obo` (release `releases/2026-06-08`, sha256 `7e19b4ae…`) by card L2 — no id is
  typed from memory and none is re-derived here;
* the 8 germ-layer anchors keep their CL id too (the ontology does carry them) but are marked
  `kind=germ_layer` and never appear in cell candidate ranking;
* `sp`: `human` for a covered class, because the panel that carries the class declares a
  human derivation (each assertion states which panel field says so); `unknown` for a germ-layer
  anchor, which is a generic ontology concept and carries no species claim of its own. **A class
  whose only evidence turns out to be non-human is not silently changed to human — see §4.**
* `ts`: the tissue context of the label's own panel, taken from the panel's own scope text
  (`scope_tissues`, `tissue`, or the panel's declared realm), never invented. `unknown` where the
  panel does not say.
* `st`: the contract's four-level axis `{fetal, adult, developing, unknown}`. A class enters
  `adult` only when the shipped adult baseline declares it as an adult key; `developing` only when
  the ontology's own text says so (L2's `stage_scope`); **everything else is `unknown`** — the
  ontology's `adult_or_unspecified` is *not* adult, and this layer never defaults it.
* `es`: `unknown` everywhere. The shipped panels describe tissue-derived atlases and no panel
  field asserts organoid / iPSC / culture for a lineage node, so claiming one would be invention.
  Disclosed as a raised item in §6.

## 3. Evidence anchor — what counts

An assertion is admitted only with an anchor that a reader can re-open on this machine today. The
gate re-resolves every anchor, so the anchor is a promise the gate keeps.

| `support_basis` | anchor object | strength |
|---|---|---|
| `link_registry_gene_verified` | `kb/link_registry/LINK_REGISTRY_v1.jsonl` row id + PMID + the registry's own `evidence_locator`, where the registry already proved the gene occurs in that paper's full text (`genes_in_text`) | strongest available locally |
| `corpus_gene_row` | corpus `chunks.parquet` `row_idx` + `paper_id` + `section`, re-checked by reading that row and re-applying the strict gene-token rule | strong |
| `panel_provenance_stated` | the panel file, the class, the gene, and the panel's own per-gene evidence record of type `canonical` / `pmid…` / literature | moderate |
| `panel_entry_basis_unstated` | the panel file, the class and the gene only — the gene is shipped but the panel states no per-gene basis | weakest, and counted as such |

**Inadmissible anchors — these produce a gap row, never an assertion:**

* any provenance whose evidence id is a panel's own `data_driven` derivation on an evaluation
  volume (`OA-D001`, `OA-D002`, `OA-D004`, `OA-D068`, `GSE268630`, `GSE199013`) — this is the
  circularity red line, and it bites: the retina interneuron panels were built on author
  annotation of `OA-D001`, so their data-driven genes are excluded here while their
  canonical/PMID genes are kept;
* a corpus row whose paper is the dev-exam paper `39117640`;
* a corpus row whose paper species is not the node's species context (see §4);
* a chunk with `full_text_available = 0` used as if it were full-text evidence.

## 4. Species and stage are never stitched

Nodes are human-context. A panel gene whose only local anchor is mouse-only is **not** written as
a human identity marker; it becomes a gap row with reason `different_species_not_stitchable`, and
the count is reported. A paper tagged `species = both` is admissible (it carries human material).
No assertion spans two species, and no assertion spans two stages: an edge assertion names a
`source_group` and a `target_group`, and both must carry the same species and stage as the
assertion itself.

## 5. The three roles, separated mechanically

`identity_support` / `subtype_discriminator` / `state_warning`. One role per assertion. The
assignment is a function of two already-frozen local facts and nothing else:

1. **state programs first.** `kb/markers/_concept_kind_sidecar_v1.json` declares five shipped
   concepts as `state_program` (a pathological endothelial axis, a disease macrophage axis and
   three proliferation axes), and `markers_v6_retina_repair.json` moves `P2RY12` and `SALL1` to
   "state anchor". Every gene that reaches a node through such a label becomes `state_warning` on
   that node — the identity node keeps its identity genes and the state programme is not allowed
   to impersonate them.
2. **then granularity.** For a node's label, the label's CL id is compared to the node's CL id
   using the ontology closure (card L2's `ont_nav.py`, reused, not rewritten):
   * same term → `identity_support`;
   * label term is a **descendant** of the node term (i.e. the label names a partition of the
     node) → `subtype_discriminator`, with `target_subtype` naming the partition. This is where
     `Endo_Capillary` / `Endo_Venous` stop being written as endothelial identity;
   * label term is an **ancestor** of the node term, or unmapped → `identity_support` (a class
     stated at the node's own granularity, or the in-house class itself).
3. **plus the panel's own subtype layer.** `markers_v6_retina_repair.json` carries an explicit
   `subtype_anchor_layer` (genes moved off the flat core because they only hold for one bipolar
   subtype, e.g. `TENM3`→FMB, `RELN`→IMB). Those genes are `subtype_discriminator` on the parent
   class with the subtype named, never `identity_support`.

A gene on a library's own prohibition list (`markers_v6_retina_repair.json` `bans`) is not
written into that library's sets at all; it becomes a gap row with reason
`prohibited_by_library_ban`.

## 6. Raised contract issues (raised, not forked)

1. **The four evidence grades are edge-centric.** They answer *how strong is the lineage step*;
   they do not answer *how strong is an identity claim*. This layer therefore leaves
   `evidence_grade` empty on node-level identity assertions and fills the anchor object instead,
   and the gate refuses any `evidence_grade` outside the declared four values while requiring
   `evidence_grade` on every edge assertion. Filling node rows with a declared value that does not
   mean what it says would be worse than an empty field with a stated reason.
2. **`assay` has no declared vocabulary.** Declared here as a closed set with the RNA/protein
   split the contract demands: `scRNA`, `literature_RNA`, `literature_protein`, `textbook`,
   `unspecified`. The gate refuses a mixed assay on one row.
3. **`experimental_system` is unobservable in the shipped panels.** Every node therefore carries
   `es=unknown`, and the report says so rather than guessing `in_vivo` for tissue atlases.
4. **A per-gene extraction record has no home in the schema.** `effect_value` is filled only when
   a source states a number *and* an extraction record exists; since the corpus mining in this
   card never reads numbers out of prose, **no assertion in this layer carries an `effect_value`**
   and every edge assertion is `claim_type=qualitative`. That is the honest reading of "never
   fabricate a fold change", not a missing step.

## 7. Marker change along an edge — the admission test

Only an edge whose relation is declared direct by the ontology can carry a stepwise change; a
transitive chain and a germ-layer membership cannot, and are recorded as
`marker_change_not_available` with a reason.

For an admitted edge `P → C`, a gene `g` in the child's panel and absent from the parent's is
written as `change=on` **only if** a local chunk satisfies all of:

1. `g` occurs in the chunk text as a standalone token under the strict rule;
2. the chunk's paper species is admissible for the node's species context;
3. the chunk names the **target** group (the descendant's ontology label, or the descendant in the
   chunk's own `cell_type_mentioned` list);
4. the chunk's paper is developmentally scoped (the dev-stage sidecar says fetal/mixed) or the
   chunk text carries a developmental keyword.

Otherwise the gene is a gap row: `no_source_states_the_change`.

**Loss is never claimed.** A gene in the parent's panel and absent from the child's is *not*
written as `down` or `off`: panel absence is not a detection result. Those rows go to the gap
register with reason `detection_conditions_insufficient`, which is the mechanical form of
"not mentioned is not `off`".

## 8. Gap reasons (closed vocabulary)

`no_source_in_corpus` · `source_exists_not_full_text` ·
`review_citation_unverifiable_locally` · `different_species_not_stitchable` ·
`different_stage_not_stitchable` · `evidence_only_from_evaluation_volume` ·
`prohibited_by_library_ban` · `node_has_no_panel_and_no_source` ·
`parent_group_has_no_panel` · `edge_not_stepwise_relation` ·
`marker_change_not_available_for_relation_type` · `no_source_states_the_change` ·
`detection_conditions_insufficient` · `state_program_without_identity_node` ·
`panel_entry_basis_unstated` · `panel_selected_from_evaluation_report`

Two of these are about *refusing* material rather than lacking it: a gene whose only basis is an
evaluation volume, and a whole panel whose own scope text says it was built to fill the holes the
evaluation run reported (`markers_v12_holefill_increment.json`, refused and registered rather than
consumed). A refusal is recorded, never silent.

## 9. The gate

Twelve named checks, each with a pass/fail count, each re-reading disk rather than trusting a
build. Details and the readout format are in `out/GATE_READOUT.md`; the checks are listed in
`scripts/m5_gate.py`. The default-behaviour check is the recorded production query set
(`golden_721`), replayed and compared to the recorded ranking — argued nowhere, replayed once.