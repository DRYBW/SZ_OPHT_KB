# USER_DIRECTIVE 2026-09-24: KB entry additions to use Cell Ontology as the naming reference (PI instruction)

## Meaning of the original words
PI (2026-09-24 MSG_PLATFORM): "for the added entries you can refer to celloncology" — i.e. Cell Ontology (OBO CL, the international standard ontology of cell types).

## Norms (effective from this document)
1. **Naming alignment for new entries**: when adding cell-type entries at the KB entry layer (vocabulary names in markers_v*, concept entries EYEKBC-*),
   one must look up the corresponding term in Cell Ontology (http://purl.obolibrary.org/obo/cl.owl) and
   record the `cl_id` (e.g. CL:0000304 photoreceptor rod cell) + official label + definition summary.
2. **Synonym mapping**: author labels / community aliases (BC/bipolar cell/Retinal bipolar cells…) hang under CL terms as an alias table;
   the vocabulary in reading prompts and the truth mappings (defs/maps_Q*.json) converge step by step toward the CL aliases, reducing "same thing, different name" matching failures.
3. **No-conflict clause**: for ophthalmic-specific positions with no corresponding CL term (e.g. concrete BC subtypes DB1/DB2/FMB if CL has no entry),
   coin the name following CL's naming conventions and mark `cl_id: NO_MATCH`; force-fitting an approximate term is prohibited.
4. **Panel gene ontology untouched**: CL alignment is an increment at the entry/naming layer and does not change the already-accepted gene sets of markers_v5;
   the existing v5 entries (incl. keratocyte and the interneuron generic) get a one-time CL back-annotation (a sidecar alignment file; bump the version, no in-place edits).
5. Adnexa ingestion (lacrimal/meibomian etc., pending items) follows the same norms.

## Landing
- Execution card: KB5-v3 gap-entry additions (evidence gathering for the three clusters Q3::13/Q5b::13/Q5b::43) + CL back-alignment of the v5/keratocyte entries;
  the task brief must cite this document.
- CL data acquisition: downloading cl.owl / cl.obo goes through official OBO or EBI (size <50MB, within the approval-free line); take only the retina-related branches + the full id-label index.
