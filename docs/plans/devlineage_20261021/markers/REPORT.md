# The marker layer of the developmental lineage — per lineage and per edge, graded

This directory holds the middle clause of the owner's request: **each lineage carries its own
markers**, and **each transition carries a marker-change assertion**, every one of them graded
and every one of them anchored to something a reader can open on this machine. It builds
against the frozen contract `../DATA_CONTRACT_devlineage_v1.md` and the brief
`../BRIEF_V2_MARKER_LAYER_20261021.md`. The design decisions taken before the build are fixed
in `DESIGN_MARKER_LAYER.md`.

The honest headline: **59 nodes carry 1043 graded assertions over 695 distinct genes, 2 of 34
edges can carry a stepwise marker change, and 226 gaps are named explicitly — of which 140 are
genuine absences of evidence and 78 are pieces of evidence this layer refused to use.**

---

## 1. What is in the directory

| file | what it is |
|---|---|
| `out/NODES.tsv` | the node table, one row per node, in the contract's node-key format |
| `out/MARKER_SETS_NODE.tsv` | **the per-node marker sets** — one row per gene per node, with `role`, `change`, `stage`, `assay`, `source_group`, `target_group`, `claim_type`, `evidence_ids`, `evidence_grade`, `evidence_anchor` |
| `out/MARKER_CHANGE_EDGES.tsv` | **the per-edge marker-change assertions**, same schema, `edge_id_or_node_key` carrying the edge key |
| `out/EDGES.tsv` | the edge table: contract edge key, relation type, directness, grade, marker-change status |
| `out/GAP_REGISTER.tsv` | **the gap register**, first-class, one row per node/edge/gene with no admissible evidence, with reason and the material that was actually checked |
| `out/GATE.json`, `out/GATE_READOUT.md` | the machine gate and its readout |
| `out/ANCHOR_RESOLUTION.json` | the anchor re-resolution result the gate produced |
| `out/CORPUS_GENE_INDEX_v1.tsv` | the corpus pass: per gene, counts, species split, and locators with a byte-level anchor |
| `out/MANIFEST.sha256` | the frozen build artefacts |
| `ledgers/` | chain log, replay ledger, manifest check, network audit, resource readings |
| `scripts/` | the build (`m0`–`m4`), the manifest (`m6`), the report (`m7`), the gate (`m5`), and `run_all.sh` |

## 2. Where the markers came from, and what each source is allowed to say

| source | allowed to supply | not allowed |
|---|---|---|
| the shipped marker panels (`kb/markers/*.json`) | the candidate identity panel per class, and a per-gene basis **where the panel states one** | it may not stand in for *lineage* membership, and its evaluation-volume-derived provenance may not be used |
| the local corpus (`literature_db/v2.6-dev_2026-10`, 244,877 chunks) | the anchor: a row whose text carries the gene, with paper id, section, ordinal and text hash | nothing about a paper we do not hold |
| the citation spine (`kb/link_registry/LINK_REGISTRY_v1.jsonl`) | citations the registry already proved contain the entry's genes in the paper's own full text | it is a disclosure surface, never a score |
| the Cell Ontology (`releases/2026-06-08`) | the node identity, the ancestors/descendants used for role separation, the `develops_from` relation | it carries **zero** gene-name terms for cell types, so it supplies no marker at all |
| the textbook layer (81 items, page anchors) | nothing gene-level | its own rule forbids it as expression evidence |

### 2.1 The panels actually consumed, and how each candidate pool was selected

Disclosed because an anchor being independent of the evaluation side does not make a *candidate list* independent of it. Read this column before treating a set as benchmark-clean.

| library | file | read from | entries | genes | how the candidate pool was selected |
|---|---|---|---|---|---|
| `antseg_v10` | markers_v10_antseg_increment.json | construction site | 16 | 396 | in_house_atlas_eval_volume (per-entry dev_volume) + corpus harvest |
| `dev_v8` | markers_v8_dev_retina.json | construction site | 10 | 32 | developmental_panel_data_plus_literature (data track = the dev-exam substrate) |
| `dev_v9` | markers_v9_dev_retina.json | construction site | 14 | 222 | developmental_panel_data_plus_literature (data track = the dev-exam substrate) |
| `face_v6` | markers_v6_face_increment.json | construction site | 7 | 18 | in_house_atlas_eval_volume (D002 ocular surface) + canonical consensus |
| `k9_ocs` | markers_k9_ocs_increment.json | construction site | 4 | 20 | in_house_atlas_eval_volume (D002 ocular surface) + canonical consensus |
| `lacrimal_v6` | markers_v6_lacrimal_increment.json | construction site | 3 | 7 | in_house_atlas_non_eval (GSE164403 human lacrimal gland) |
| `lensiris_v11` | markers_v11_lensiris_increment.json | repo copy | 3 | 88 | in_house_atlas_eval_volume (per-entry dev_volume) + corpus harvest |
| `membrane` | markers_membrane_v1.json | construction site | 23 | 215 | in_house_atlas_non_eval (GSE165784) + canonical consensus |
| `retina` | markers_v4.1_clean.json | construction site | 10 | 47 | curated_panel_pre_2026 (literature + canonical consensus) |
| `retina_interneuron` | markers_v5_retina_interneuron.json | construction site | 10 | 162 | in_house_atlas_eval_volume (HRCA D001 pairwise-DE gate) |
| `retina_v6` | markers_v6_retina_repair.json | construction site | 11 | 141 | in_house_atlas_eval_volume (HRCA D001 / KB7 repair disposition) |
| `retina_v7` | markers_v7_panel_increment.json | construction site | 10 | 95 | in_house_atlas_eval_volume (retina facet increment on D001-derived entries) |

Byte-identity of the two copies was checked for every shared panel file; the repo copy is the
only place `markers_v11_lensiris_increment.json` exists, and card L2 read it from there too.

**A panel refused outright:** `markers_v12_holefill_increment.json` ships in the repository
but is **not consumed**. Its own scope text says it was built to fill *the measured coverage
holes of the 28-volume / 721-cluster run* — i.e. the candidate list is the benchmark's own
output, which the contract forbids as a source of markers. It is registered in the gap
register rather than silently dropped (`panel_selected_from_evaluation_report`).

## 3. Node keys

`dl:<cl_id>|sp=<species>|ts=<tissue_context>|st=<organism_stage>|es=<experimental_system>`

| | count | how it was derived |
|---|---|---|
| nodes | 70 | 52 covered classes + 8 germ-layer anchors from card L2's lineage layer, plus 10 in-house developmental precursor nodes |
| ids resolved from the ontology file | 60 | the id is read from `cl.obo` (`releases/2026-06-08`), never typed |
| stage = `adult` | 22 | only where the shipped adult baseline declares the class |
| stage = `developing` | 22 | only where the ontology's own text or a dev panel says so |
| stage = `unknown` | 26 | `adult_or_unspecified` is **not** adult, and is never defaulted |
| `es` (experimental system) | 70 `unknown` | no shipped panel asserts one for a lineage node; guessing `in_vivo` for a tissue atlas would be invention |

**Why in-house nodes were added.** The ontology has no term for the developmental precursor
labels our own dev panels ship — card DEV-ONT recorded 7 of 10 as `NO_MATCH`. The contract
supplies the right form for exactly that case (`dl:NO_MATCH:<in_house_class_id>|…`), so these
labels get nodes instead of disappearing. Without them the developmental side of the lineage
would have no markers at all, which is the owner's central ask. They are knowledge-layer
nodes and never enter cell candidate ranking:

| node | genes | note |
|---|---|---|
| `AC_precursor` | 18 | markers_v8_dev_retina.json,markers_v9_dev_retina.json |
| `BC_precursor` | 0 | markers_v8_dev_retina.json,markers_v9_dev_retina.json |
| `Cone_precursor` | 25 | markers_v8_dev_retina.json,markers_v9_dev_retina.json |
| `HC_precursor` | 25 | markers_v8_dev_retina.json,markers_v9_dev_retina.json |
| `NRPC_early` | 25 | markers_v9_dev_retina.json |
| `NRPC_late` | 25 | markers_v9_dev_retina.json |
| `RGC_precursor` | 21 | markers_v8_dev_retina.json,markers_v9_dev_retina.json |
| `Rod_precursor` | 25 | markers_v8_dev_retina.json,markers_v9_dev_retina.json |
| `TAC_transit_amplifying` | 2 | markers_v8_dev_retina.json |
| `glia_precursor` | 0 | markers_v9_dev_retina.json |

## 4. Per-node marker sets — 1043 assertions

### 4.1 How each gene got its role

One role per assertion, assigned in this order (DESIGN §5): a **state programme** that
reaches a node is `state_warning`; a gene the panel itself declares as a subtype anchor, or a
label the ontology places strictly *under* the node term, is `subtype_discriminator`; the rest
is `identity_support`.

| role | assertions | what it means here |
|---|---|---|
| `identity_support` | 982 | this is what the type is |
| `subtype_discriminator` | 31 | this separates it from its nearest sibling — includes the panel's own subtype-anchor layer |
| `state_warning` | 30 | this changes with disease, cycle or treatment and must not be read as identity |

The state separation is not cosmetic. `Endo_Patho`, `Mac_DAM_LAM`, `TAC_proliferating` and the
microglial state anchors (`P2RY12`, `SALL1`) are shipped as **state programmes** by the
knowledge base's own concept-kind sidecar; here they are written as `state_warning` on the
identity node they accompany, so a disease endothelial axis can never be read as the
endothelium's identity.

### 4.2 Where the anchor for each gene comes from

| support basis | assertions | what the anchor is |
|---|---|---|
| `link_registry_gene_verified` | 313 | a citation the registry already proved contains the gene in that paper's own full text (`genes_in_text`), with its own locator |
| `corpus_gene_row` | 720 | a corpus row: paper id, section, ordinal and text hash — re-read by the gate |
| `panel_provenance_stated` | 6 | the panel's own per-gene basis (`canonical` / PMID), used only when it is not an evaluation-volume derivation |
| `panel_entry_basis_unstated` | 4 | the gene is shipped in the panel but that panel states no per-gene basis and no corpus row anchors it — the weakest tier, and flagged in the gap register |

Anchor species: {'human': 856, 'both': 187}. **No assertion on a human node is anchored on a mouse-only source** — 
those genes are gap rows instead (§7). Assay split: {'literature_RNA': 1015, 'literature_protein': 23, 'scRNA': 1, 'unspecified': 4} — RNA and protein rows are kept
separate and are never merged on one row.

### 4.3 Every node, with its counts

| node | stage | tissue | identity | subtype | state | genes |
|---|---|---|---|---|---|---|
| `CL:0000037 hematopoietic stem cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0000057 fibroblast` | adult | eye_membrane | 13 | 0 | 0 | 13 |
| `CL:0000084 T cell` | adult | eye_membrane | 11 | 0 | 0 | 11 |
| `CL:0000094 granulocyte` | unknown | eye_membrane | 13 | 0 | 0 | 13 |
| `CL:0000097 mast cell` | adult | eye | 11 | 0 | 0 | 11 |
| `CL:0000114 surface ectodermal cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0000115 endothelial cell` | adult | retina | 17 | 0 | 8 | 25 |
| `CL:0000127 astrocyte` | adult | retina | 6 | 0 | 0 | 6 |
| `CL:0000128 oligodendrocyte` | adult | optic_nerve | 18 | 0 | 0 | 18 |
| `CL:0000129 microglial cell` | adult | retina | 23 | 0 | 0 | 23 |
| `CL:0000132 corneal endothelial cell` | adult | eye_membrane | 22 | 0 | 0 | 22 |
| `CL:0000133 neurectodermal cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0000148 melanocyte` | adult | ocular_surface | 10 | 0 | 0 | 10 |
| `CL:0000160 goblet cell` | unknown | conjunctiva | 20 | 0 | 0 | 20 |
| `CL:0000185 myoepithelial cell` | unknown | lacrimal_gland | 0 | 0 | 0 | 0 |
| `CL:0000186 myofibroblast cell` | unknown | eye_membrane | 12 | 0 | 0 | 12 |
| `CL:0000192 smooth muscle cell` | unknown | retina | 8 | 0 | 0 | 8 |
| `CL:0000221 ectodermal cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0000222 mesodermal cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0000223 endodermal cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0000235 macrophage` | adult | retina | 18 | 0 | 20 | 38 |
| `CL:0000236 B cell` | adult | eye_membrane | 7 | 0 | 0 | 7 |
| `CL:0000315 tear secreting cell` | adult | lacrimal_gland | 6 | 0 | 0 | 6 |
| `CL:0000529 pigmented epithelial cell` | unknown | lens | 30 | 0 | 0 | 30 |
| `CL:0000561 amacrine cell` | adult | retina | 32 | 20 | 0 | 52 |
| `CL:0000573 retinal cone cell` | adult | retina | 5 | 0 | 0 | 5 |
| `CL:0000575 corneal epithelial cell` | unknown | cornea | 30 | 0 | 0 | 30 |
| `CL:0000604 retinal rod cell` | adult | retina | 5 | 0 | 0 | 5 |
| `CL:0000623 natural killer cell` | unknown | eye_membrane | 7 | 0 | 0 | 7 |
| `CL:0000636 Mueller cell` | adult | retina | 6 | 0 | 0 | 6 |
| `CL:0000646 basal cell` | developing | cornea | 30 | 0 | 0 | 30 |
| `CL:0000669 pericyte` | adult | retina | 15 | 0 | 0 | 15 |
| `CL:0000740 retinal ganglion cell` | adult | retina | 6 | 0 | 0 | 6 |
| `CL:0000745 retina horizontal cell` | adult | retina | 29 | 2 | 0 | 31 |
| `CL:0000748 retinal bipolar neuron` | adult | retina | 42 | 9 | 0 | 51 |
| `CL:0000784 plasmacytoid dendritic cel` | unknown | eye_membrane | 9 | 0 | 0 | 9 |
| `CL:0000786 plasma cell` | unknown | eye_membrane | 9 | 0 | 0 | 9 |
| `CL:0000860 classical monocyte` | unknown | eye_membrane | 11 | 0 | 0 | 11 |
| `CL:0000875 non-classical monocyte` | unknown | eye_membrane | 5 | 0 | 0 | 5 |
| `CL:0000990 conventional dendritic cel` | unknown | eye_membrane | 14 | 0 | 0 | 14 |
| `CL:0002144 capillary endothelial cell` | unknown | retina | 4 | 0 | 0 | 4 |
| `CL:0002223 anterior lens cell` | unknown | lens | 28 | 0 | 0 | 28 |
| `CL:0002224 lens epithelial cell` | unknown | lens | 30 | 0 | 0 | 30 |
| `CL:0002225 secondary lens fiber` | unknown | lens | 29 | 0 | 0 | 29 |
| `CL:0002303 pigmented ciliary epitheli` | unknown | ciliary_body | 24 | 0 | 0 | 24 |
| `CL:0002304 non-pigmented ciliary epit` | unknown | ciliary_body | 26 | 0 | 0 | 26 |
| `CL:0002363 keratocyte` | unknown | eye_membrane | 3 | 0 | 0 | 3 |
| `CL:0002367 trabecular meshwork cell` | unknown | trabecular_meshwork | 30 | 0 | 0 | 30 |
| `CL:0002543 vein endothelial cell` | unknown | retina | 4 | 0 | 0 | 4 |
| `CL:0002565 iris pigment epithelial ce` | unknown | iris | 24 | 0 | 0 | 24 |
| `CL:0002573 Schwann cell` | adult | ocular_surface | 4 | 0 | 0 | 4 |
| `CL:0002586 retinal pigment epithelial` | adult | retina | 10 | 0 | 0 | 10 |
| `CL:0002672 retinal progenitor cell` | developing | retina | 45 | 0 | 0 | 45 |
| `CL:0008019 mesenchymal cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0009010 transit amplifying cell` | developing | cornea | 30 | 0 | 2 | 32 |
| `CL:0011004 lens fiber cell` | unknown | lens | 29 | 0 | 0 | 29 |
| `CL:0011012 neural crest cell` | developing | unknown | 0 | 0 | 0 | 0 |
| `CL:0011026 progenitor cell` | developing | ocular_surface | 30 | 0 | 0 | 30 |
| `CL:1000432 conjunctival epithelial ce` | unknown | ocular_surface | 32 | 0 | 0 | 32 |
| `CL:1000443 ciliary muscle cell` | unknown | ciliary_body | 11 | 0 | 0 | 11 |
| `NO_MATCH:AC_precursor` | developing | retina | 3 | 0 | 0 | 3 |
| `NO_MATCH:BC_precursor` | developing | retina | 0 | 0 | 0 | 0 |
| `NO_MATCH:Cone_precursor` | developing | retina | 7 | 0 | 0 | 7 |
| `NO_MATCH:HC_precursor` | developing | retina | 6 | 0 | 0 | 6 |
| `NO_MATCH:NRPC_early` | developing | retina | 18 | 0 | 0 | 18 |
| `NO_MATCH:NRPC_late` | developing | retina | 25 | 0 | 0 | 25 |
| `NO_MATCH:RGC_precursor` | developing | retina | 19 | 0 | 0 | 19 |
| `NO_MATCH:Rod_precursor` | developing | retina | 9 | 0 | 0 | 9 |
| `NO_MATCH:TAC_transit_amplifying` | developing | retina | 2 | 0 | 0 | 2 |
| `NO_MATCH:glia_precursor` | developing | retina | 0 | 0 | 0 | 0 |

## 5. Per-edge marker-change assertions — 10

The edge list is card L2's 34 edges, re-keyed into the contract's edge key and re-typed so
that no relation is silently upgraded into another:

| upstream relation | contract relation type | directness | edges | what it can carry |
|---|---|---|---|---|
-
| `develops_from_direct` | `ontology_development_relation` | direct | 5 | a stepwise marker change, if a source states it |
| `develops_from_transitive` | `ontology_development_relation` | transitive | 4 | a chain the ontology declares in full: time direction and identity conversion, **not** a single step, so no marker change is attributed |
| `germ_layer_membership` | `ancestral_origin` | distant | 25 | a distant origin; it must not pose as a single step |

Evidence grade per edge: {'direct_lineage_support': 5, 'identity_conversion_not_direct': 4, 'trajectory_only': 12, 'textbook_or_review_distant_origin': 13}.
Assertions per evidence grade: node-level identity assertions carry **no** grade by design (the four declared grades are edge-centric — see §10.1), and the 10 edge assertions grade as {'direct_lineage_support': 10}.
Marker-change status per edge: {'parent_group_has_no_panel': 3, 'edge_not_stepwise_relation': 4, 'admitted_stepwise': 2, 'marker_change_not_available_for_relation_type': 25}.

### 5.1 The admission test, and what it admitted

A gene is written as `change=on` for edge `P → C` only when a local chunk (1) carries the
gene token, (2) belongs to a paper whose species fits the node, (3) **names the target
group**, and (4) is developmentally scented. Anything else is a gap row.

| edge | transition | assertions | genes |
|---|---|---|---|
| `retinal progenitor cell → retinal cone cell` | E005 | 5 | ARR3, GNAT2, OPN1MW, OPN1SW, PDE6H |
| `retinal progenitor cell → retinal rod cell` | E007 | 5 | GNAT1, NR2E3, NRL, PDE6B, RHO |

Every one of these 10 rows names a `source_group` (the precursor) and a `target_group` (the
descendant), carries `claim_type=qualitative`, **no `effect_value` at all**, and states in
`uncertainty` what the source does and does not support: it names the target group in a
developmental context; no source on this machine measures the precursor→descendant change
itself.

### 5.2 The loss side is deliberately empty

**90 genes** are present in a precursor's panel and absent from the descendant's. Not one of
them is written as `down` or `off`: panel absence is not a detection result, and
"not mentioned" is not `off`. They are named individually in the gap register with reason
`detection_conditions_insufficient`. This is the mechanical form of the contract's rule, and
it is the reason the confirmed marker-change layer is ten rows and not two hundred.

## 6. All 34 edges, with their status

| edge | precursor | descendant | relation | directness | grade | marker change |
|---|---|---|---|---|---|---|
| E001 | mesodermal cell | endothelial cell | ontology_development_relation | direct | direct_lineage_support | parent_group_has_no_panel |
| E002 | ectodermal cell | oligodendrocyte | ontology_development_relation | transitive | identity_conversion_not_direct | edge_not_stepwise_relation |
| E003 | mesodermal cell | microglial cell | ontology_development_relation | direct | direct_lineage_support | parent_group_has_no_panel |
| E004 | ectodermal cell | melanocyte | ontology_development_relation | transitive | identity_conversion_not_direct | edge_not_stepwise_relation |
| E005 | retinal progenitor cell | retinal cone cell | ontology_development_relation | direct | direct_lineage_support | 5 assertions |
| E006 | ectodermal cell | retinal cone cell | ontology_development_relation | transitive | identity_conversion_not_direct | edge_not_stepwise_relation |
| E007 | retinal progenitor cell | retinal rod cell | ontology_development_relation | direct | direct_lineage_support | 5 assertions |
| E008 | ectodermal cell | retinal rod cell | ontology_development_relation | transitive | identity_conversion_not_direct | edge_not_stepwise_relation |
| E009 | neurectodermal cell | retinal progenitor cell | ontology_development_relation | direct | direct_lineage_support | parent_group_has_no_panel |
| E010 | mesenchymal cell | fibroblast | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E011 | neural crest cell | fibroblast | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E012 | hematopoietic stem cell | T cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E013 | mesodermal cell | endothelial cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E014 | ectodermal cell | oligodendrocyte | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E015 | neurectodermal cell | oligodendrocyte | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E016 | mesodermal cell | microglial cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E017 | neural crest cell | corneal endothelial cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E018 | ectodermal cell | melanocyte | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E019 | neural crest cell | melanocyte | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E020 | neurectodermal cell | melanocyte | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E021 | mesenchymal cell | myofibroblast cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E022 | hematopoietic stem cell | B cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E023 | ectodermal cell | retinal cone cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E024 | neurectodermal cell | retinal cone cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E025 | ectodermal cell | retinal rod cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E026 | neurectodermal cell | retinal rod cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E027 | neural crest cell | retinal ganglion cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E028 | mesenchymal cell | plasma cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E029 | mesenchymal cell | keratocyte | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E030 | neural crest cell | keratocyte | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E031 | mesenchymal cell | retinal pigment epithelial cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E032 | neural crest cell | retinal pigment epithelial cell | ancestral_origin | distant | trajectory_only | marker_change_not_available_for_relation_type |
| E033 | ectodermal cell | retinal progenitor cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |
| E034 | neurectodermal cell | retinal progenitor cell | ancestral_origin | distant | textbook_or_review_distant_origin | marker_change_not_available_for_relation_type |

## 7. What could not be closed

This section is the deliverable as much as the tables above. Numbers first, then the
individual items; the machine-readable form is `out/GAP_REGISTER.tsv` (226 rows).

| gap kind | rows | meaning |
|---|---|---|
| `no_evidence` | 140 | nothing admissible exists locally |
| `refused_evidence` | 78 | material exists but is inadmissible (evaluation-derived, prohibited, or benchmark-holedriven) |
| `thin_evidence` | 8 | an assertion exists but its support is weak and is disclosed as such |

| reason | rows | the closing question this leaves |
|---|---|---|
| `detection_conditions_insufficient` | 92 | a source that measures the gene in the precursor and in the descendant with adequate detection conditions — this is what would let a loss be claimed |
| `evidence_only_from_evaluation_volume` | 75 | an independent source for these genes: they currently enter only through an evaluation volume's own cells or the dev-exam substrate |
| `marker_change_not_available_for_relation_type` | 25 | nothing to close by reading; an ancestral-origin relation cannot carry a single-step marker change by construction |
| `node_has_no_panel_and_no_source` | 11 | a panel, or a source, for this node: it is declared but carries no markers |
| `panel_entry_basis_unstated` | 4 | a per-gene basis for these genes — the panel lists them without saying why |
| `review_citation_unverifiable_locally` | 4 | the paper the panel's note refers to, or a corpus row for the gene |
| `edge_not_stepwise_relation` | 4 | a direct (single-step) source for each link of the chain; the ontology gives only the chain, which cannot be read as one step |
| `state_program_without_identity_node` | 3 | an identity node for this state programme, or a decision that it belongs to another layer |
| `parent_group_has_no_panel` | 3 | a panel for the precursor end: with no precursor genes there is nothing to compare against |
| `no_source_in_corpus` | 2 | a source for these genes/classes; the corpus does not carry them |
| `different_species_not_stitchable` | 2 | a human-context source: the only local evidence is in another species and is therefore not stitched |
| `panel_selected_from_evaluation_report` | 1 | a candidate list built without reading the benchmark's own holes |

### 7.1 The four things a reader should actually take from this

1. **The lineage is a two-step graph, not a tree of markers.** Only rod and cone have a
   complete ontology path (`neurectodermal cell → retinal progenitor cell → rod/cone`), and
   only those two edges can carry a stepwise marker change. The other 32 edges are typed and
   graded, but their marker dynamics are recorded as *not available* rather than narrated.
2. **11 of 70 nodes carry no marker at all**, and the reason is stated for each: 11 are
   germ-layer concepts or classes with no panel, 0 are declared with a panel that reaches no
   admissible anchor.
3. **75 genes were refused because their only basis is an evaluation volume**, and 2 more
   because the only local evidence is in another species. Both numbers are evidence of the
   layer's restraint, not of the corpus's poverty, and both shrink the layer relative to what
   a permissive reading would have produced.
4. **4 assertions rest on a panel entry with no per-gene basis and no corpus row.** They are
   shipped, they are in the tables, and they are also in the gap register — the weakest tier
   is not allowed to look like the strongest.

### 7.2 Gaps that are named but not closed, by name

* **dl:CL:0000037|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0000114|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0000133|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0000185|sp=human|ts=lacrimal_gland|st=unknown|es=unknown** — `node_has_no_panel_and_no_source` — the node is declared by the scaffold but no consumed panel ships a gene list for it | stage=unknown tissue=lacrimal_gland family=scaffold
* **dl:CL:0000221|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0000222|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0000223|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0008019|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:CL:0011012|sp=unknown|ts=unknown|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — germ-layer anchor; no shipped panel carries it and the marker layer does not manufacture one | stage=developing tissue=unknown family=scaffold
* **dl:NO_MATCH:BC_precursor|sp=human|ts=retina|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — the node is declared by the scaffold but no consumed panel ships a gene list for it | stage=developing tissue=retina family=in_house_dev_precursor
* **dl:NO_MATCH:glia_precursor|sp=human|ts=retina|st=developing|es=unknown** — `node_has_no_panel_and_no_source` — the node is declared by the scaffold but no consumed panel ships a gene list for it | stage=developing tissue=retina family=in_house_dev_precursor
* **dev_v8::Retinal_Proliferating** — `state_program_without_identity_node` — shipped as a state programme; no identity node exists for it in the node list, so it is not written onto one
* **dev_v9::Retinal_Proliferating** — `state_program_without_identity_node` — shipped as a state programme; no identity node exists for it in the node list, so it is not written onto one
* **membrane::APC_MHCII_high** — `no_source_in_corpus` — declared by markers_membrane_v1.json with 10 genes; the ontology carries no term our mapping resolves to a node
* **membrane::Proliferating** — `state_program_without_identity_node` — shipped as a state programme; no identity node exists for it in the node list, so it is not written onto one
* **lacrimal_v6::Lacrimal_duct_epithelial** — `no_source_in_corpus` — declared by markers_v6_lacrimal_increment.json with 1 genes; the ontology carries no term our mapping resolves to a node
* **dl:CL:0002225|sp=human|ts=lens|st=unknown|es=unknown** — `different_species_not_stitchable` — only mouse-species corpus rows exist; the node is a human context
* **dl:CL:0011004|sp=human|ts=lens|st=unknown|es=unknown** — `different_species_not_stitchable` — only mouse-species corpus rows exist; the node is a human context
* **markers_v12_holefill_increment.json** — `panel_selected_from_evaluation_report` — markers_v12_holefill_increment.json | the panel's own scope: scope: the measured coverage holes of the 28-volume / 721-cluster run — vascular endothelium in retina and choroid, macrophage and monocyte separated from microglia, retinal rod depth, and the RPE/melanocyte pair

## 8. The gate

`out/GATE.json` is the machine-readable form; `out/GATE_READOUT.md` is the table. Verdict:
**PASS**, 13 checks, 0 failed.

| check | name | status | pass/fail count |
|---|---|---|---|
| G1 | KEY_RESOLVES | PASS | 0 offenders |
| G2 | ANCHOR_RESOLVES | PASS | 0 offenders |
| G3 | VOCAB | PASS | 0 offenders |
| G4 | NO_NUMERIC | PASS | 0 offenders |
| G5 | RNA_PROTEIN_SPLIT | PASS | 0 offenders |
| G6 | SPECIES_STAGE | PASS | 0 offenders |
| G7 | NO_EVAL_INPUT | PASS | 0 offenders |
| G8 | GAP_COVERAGE | PASS | 0 offenders |
| G9 | NO_OFF_WITHOUT_DETECTION | PASS | 0 offenders |
| G10 | REBUILD_REPLAY | PASS | 0 offenders |
| G11 | NO_FABRICATED_GENE | PASS | 0 offenders |
| G12 | GOLDEN721 | PASS | 0 offenders |
| G13 | KB_UNTOUCHED | PASS | 0 offenders |

Two of them are worth naming here because they caught real defects during the build:

* **G2** re-opens every anchor. It failed on its first run for 9 anchors whose panel file
  resolution picked the construction site while the panel only exists in the repo copy — a
  reader following those anchors would have found nothing.
* **G7** found that 9 assertions had been anchored on the dev-exam substrate's own paper.
  The corpus pass now excludes it (and every paper the knowledge base flags
  `data_side_only`) from anchor locators, so the evaluation side cannot leak in through a
  citation.

Anchor re-resolution (G2): 1053 anchors, {'link_registry_gene_verified': 313, 'corpus_gene_row': 730, 'panel_provenance_stated': 6, 'panel_entry_basis_unstated': 4}; 378 corpus rows re-read byte for byte.

## 9. Proofs, with the commands that produced them

**One command builds and judges the whole layer:**

```
systemd-run --user --unit=mk-full --collect -p MemoryMax=6G -p MemorySwapMax=2G \
  --wait --pipe bash /mnt/D/EyeKB/plans/devlineage_20261021/markers/scripts/run_all.sh
```

Measured on the full run: `Service runtime: 43.2s`, `Memory peak: 457.8M` (cgroup), and the
corpus pass alone measured `maxrss 0.33 GiB` for one process over 244,877 chunks — the
concurrency question is answered by there being one process.

**Byte-identical rebuild** (`ledgers/REPLAY.txt`, produced by rebuilding the chain into a
scratch directory and comparing every artefact in the manifest):

```
# replay ledger: the whole chain was rebuilt into a scratch directory and every artefact
# listed in out/MANIFEST.sha256 was compared byte for byte.
artefacts_compared=14
differing=0
REPLAY_PASS byte-identical on the second build
```

**Default behaviour byte-identical**, by replaying the recorded production query set rather
than arguing about it (`ledgers/golden_721_now.json` is written by the replay):

```
python3 /mnt/D/EyeKB/plans/holefill_v12_20261021/golden_721.py
OFF: n=721  identical_to_2026-10-18=721  differ=0  with_composite_demoted=-
```

i.e. 721 of 721 recorded clusters reproduce their recorded ranking, `differ=0`, exactly as
before this card. This layer adds files; it changes no default answer.

**Zero network**, by an audit hook that covers child processes (`ledgers/NET_AUDIT_SUMMARY.txt`):

```
# zero-network audit (audit hook, covers child processes, including this report)
hook_install_lines=20
network_event_lines=0
NET_ZERO_PASS
```

The load-receipt lines are the control: 20 of them prove the hook was installed, so zero
event lines means zero network operations rather than a hook that never ran. No download was
performed and no download was needed: every source named in §2 was already on this machine.

**Nothing under `kb/` was touched** (gate G13): the whole knowledge base was walked and its
newest mtime predates this card. The layer is registered-but-not-activated: it writes only
inside `plans/devlineage_20261021/markers/`, and nothing default reads it.

**Manifest** (`out/MANIFEST.sha256`, 14 entries) verifies after the gate has re-run:

```
$ (cd out && sha256sum -c MANIFEST.sha256) | grep -c ': OK'
14
```

Run-time write-outs are excluded from the manifest on purpose (`GATE.json`,
`GATE_READOUT.md`, `ANCHOR_RESOLUTION.json`): they are rewritten every time the layer is
verified, so including them would make the manifest fail whenever the layer is *checked*
rather than whenever it is *wrong*. The acceptance test is therefore 'sha256sum -c' still
returns 0 after the gate has run', which is what `run_all.sh` checks and what the figure
above shows.

**Independence from the upstream corpus pass.** Card L2 built its own gene index over 8
panels; this card rebuilt it over 773 symbols from 12 panels with the same matcher. The 713
genes the two passes share have **identical chunk counts, 0 differences** — the pass is
reproducible, and the 60 newly covered symbols are the difference the extra panels make.

## 10. Raised contract issues (raised, not forked)

The contract asks to be told when a field is genuinely insufficient rather than forked
privately. Four such points came up; all four are handled additively, so no declared value
changes meaning:

1. **The four evidence grades are edge-centric.** They answer *how strong is the lineage
   step*; they do not answer *how strong is an identity claim*. Node-level identity
   assertions therefore carry **no** `evidence_grade` (the gate refuses any value outside
   the declared four and requires one on every edge assertion) and carry an anchor object
   plus a `support_basis` tier instead. Filling the field with a value that does not mean
   what it says would be worse than an empty field with a stated reason.
2. **`assay` has no declared vocabulary.** Declared here as a closed set with the RNA/protein
   split the contract demands: `scRNA`, `literature_RNA`, `literature_protein`, `textbook`,
   `unspecified`. The gate refuses a mixed assay on one row.
3. **`experimental_system` is unobservable in the shipped panels**, so every node carries
   `es=unknown`. This is a real limitation of the layer and not a placeholder.
4. **A per-gene extraction record has no home in the schema.** `effect_value` is filled only
   when a source states a number *and* an extraction record exists; since the mining in this
   card never reads numbers out of prose, **no assertion carries an `effect_value`** and every
   edge assertion is `claim_type=qualitative`. That is the honest reading of "never
   fabricate a fold change", not a missing step.
5. **One grade name does not fit one of its uses**: `textbook_or_review_distant_origin` is
   also the correct grade for a distant origin the *ontology itself* declares. The anchor
   kind is recorded alongside (`anchor_kind` / `evidence_kind`), so no reader is misled.

## 11. What this layer is not

* It is **not** a complete lineage.** It is a comprehensively enumerated and honestly graded
  one: 34 edges typed, 70 nodes keyed, 59 of them carrying markers, 11 of them named as gaps.
* It is **not** a claim that these markers change along these transitions.** Ten assertions
  say a gene is present in the target group and developmentally scented; none says the
  transition was measured.
* It is **not** independent of the adult library.** Its candidate pools are the shipped
  panels, several of which were selected with an evaluation volume's cells (§2.1). What is
  independent is the *anchor* on every individual assertion; what is not is the size and
  membership of some candidate lists. That distinction is the reason §2.1 exists.
* It is **not** activated.** Nothing default reads `plans/devlineage_20261021/markers/`.

## 12. Reproducing this

```
cd /mnt/D/EyeKB/plans/devlineage_20261021/markers
bash scripts/run_all.sh                 # build + manifest + gate (rebuild replay included)
bash scripts/run_all.sh --no-replay     # skip the two replays
python3 scripts/m7_report.py            # regenerate this report from the artefacts
python3 scripts/m4_gap_register.py      # regenerate the gap register alone
```

Scripts: `m0_corpus_gene_index.py` (corpus pass, the only heavy step) · `m1_nodes.py` (node
keys) · `m2_node_markers.py` (per-node sets) · `m3_edge_assertions.py` (per-edge changes) ·
`m4_gap_register.py` (gap register) · `m5_gate.py` (13 checks) · `m6_manifest.py` ·
`m7_report.py` · `run_all.sh` · `netaudit/sitecustomize.py`.
