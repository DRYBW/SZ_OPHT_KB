"""Machine-readable schema for a tissue knowledge-base plugin.

Every rule here is a *machine gate*, not a convention.  A plugin that violates
any rule fails `kbkit validate`.  The point of the kit is that the discipline
is executable rather than aspirational.

Design rules encoded below (and why each exists):

R1  Every marker gene carries a DIRECTION.  A gene that goes up in a cell type
    and a gene that goes down are different evidence; collapsing them into one
    unsigned list makes the ranking ill-posed and makes ties arbitrary.

R2  Every knowledge item carries PROVENANCE (a PMID, or a dataset accession).
    Items that cannot answer "where did this come from" are not admissible.

R3  `organism_stage` is a first-class axis alongside species and tissue.
    Fetal / developing / adult are NOT interchangeable even for the same tissue.

R4  Composition baselines are reported as per-donor RANGES, never point
    estimates.  Two independent donors are not "a proportion".

R5  Disease context is expressed as  cell type x state , never as a new cell
    type.  A state (proliferating, inflammatory, foam-like) is not a lineage.

R6  Only per-cell author-level annotated public datasets may serve as
    evaluation ground truth.  Sorted-pool labels and our own consensus labels
    do NOT qualify (using them would be circular).
"""

from __future__ import annotations

SCHEMA_VERSION = "1.0"

# ── controlled vocabularies ───────────────────────────────────────────────────
SPECIES = {"human", "mouse", "rat", "macaque", "zebrafish", "other"}
ORGANISM_STAGE = {"fetal", "developing", "adult", "unknown"}
DIRECTION = {"+", "-"}
EVIDENCE_LEVEL = {"A", "B", "C"}          # A = primary/author-level, B = secondary, C = inferred
SAMPLING_MATERIAL = {
    "retina", "vitreous", "membrane", "rpe_choroid", "cornea", "conjunctiva",
    "limbus", "optic_nerve", "iris", "lens", "tear", "aqueous", "other",
}
ASSAY = {"scRNA", "snRNA", "multiome", "spatial", "bulk", "other"}
ANNOTATION_LEVEL = {
    "per_cell_author",   # ONLY level admissible as evaluation ground truth
    "per_cell_consensus",  # our own call -> evaluation would be circular
    "per_cluster_author",
    "sorted_pool",       # not cells
    "none",
}
INCLUSION_REASON = {
    "composition_baseline",
    "disease_cell_composition",
    "state_signature",
    "method_reference",
    "disease_mechanism_background",
    "developmental_composition",
}

# ── entity schemas ────────────────────────────────────────────────────────────
# Each spec: field -> (required, kind, note)

COMMON = {
    "entry_id":        (True,  "str", "stable id; never renamed in place"),
    "schema_version":  (True,  "str", "must equal SCHEMA_VERSION at build time"),
    "species":         (True,  "enum", "SPECIES"),
    "tissue":          (True,  "str",  "free text tissue name (eye: see SAMPLING_MATERIAL)"),
    "organism_stage":  (True,  "enum", "ORGANISM_STAGE — R3; must not be inferred silently"),
}

MARKER_ENTRY = dict(COMMON, **{
    "cell_type":       (True,  "str",  "canonical name"),
    "cl_id":           (True,  "str",  "Cell Ontology term, or NO_MATCH (never a near term)"),
    "genes":           (True,  "list", "list of GENE items — R1/R2"),
    "version":         (True,  "str",  "entry version"),
    "discipline_note": (False, "str",  "e.g. what this entry may NOT be cited for"),
})

GENE = {
    "gene":          (True,  "str",  "HGNC-style symbol (canonical case)"),
    "direction":     (True,  "enum", "DIRECTION — R1"),
    "provenance":    (True,  "dict", "R2: {'pmid': '...'} or {'dataset': 'GSE...'}"),
    "evidence_level":(True,  "enum", "EVIDENCE_LEVEL"),
    "context":       (False, "str",  "condition under which the direction holds"),
    "panel":         (False, "enum", "'core' or 'extended'"),
}

BASELINE_ENTRY = dict(COMMON, **{
    "sampling_material":   (True,  "enum", "SAMPLING_MATERIAL — same material as the data, not a proxy"),
    "disease_stage":       (True,  "str",  "e.g. 'control', 'PDR', 'NPDR'"),
    "treatment_background":(True,  "str",  "e.g. 'none', 'anti-VEGF pre-op <=7d' — must not be pooled"),
    "assay":               (True,  "enum", "ASSAY"),
    "enrichment_step":     (True,  "str",  "e.g. 'CD31+ selection', 'none'"),
    "n_donors":            (True,  "int",  "donor count; proportions are per-donor — R4"),
    "cells":               (True,  "list", "list of COMPOSITION items"),
})

COMPOSITION = {
    "cell_type":    (True,  "str",  ""),
    "proportion":   (True,  "range", "[lo, hi] — R4; a point estimate is rejected"),
    "pmid":         (True,  "str",  "R2"),
    "evidence_level":(True, "enum", "EVIDENCE_LEVEL"),
}

DISEASE_ENTRY = dict(COMMON, **{
    "disease":          (True,  "str",  ""),
    "context":          (True,  "str",  "what this disease does to the tissue"),
    "cells":            (True,  "list", "list of TYPE x STATE items — R5"),
    "unexpected_flags": (False, "list", "signatures that should raise a flag, not a label"),
    "contamination_flags": (False, "list", "e.g. blood, pigment, ambient RNA"),
})

TYPE_STATE = {
    "cell_type": (True, "str",  ""),
    "state":     (True, "str",  "state label, NOT a lineage — R5"),
    "signature": (False, "list", "genes; each with direction+provenance like GENE"),
    "pmid":      (True, "str",  "R2"),
}

REGISTRY_ENTRY = {
    "dataset_id":       (True,  "str",  ""),
    "accession":        (True,  "str",  "GEO/ArrayExpress/etc."),
    "species":          (True,  "enum", "SPECIES"),
    "tissue":           (True,  "str",  ""),
    "organism_stage":   (True,  "enum", "ORGANISM_STAGE"),
    "annotation_level": (True,  "enum", "ANNOTATION_LEVEL — R6; only per_cell_author is admissible"),
    "n_cells":          (False, "int",  ""),
    "n_donors":         (False, "int",  ""),
    "source":           (True,  "str",  "paper / portal + how obtained"),
    "notes":            (False, "str",  ""),
}

PLUGIN_YAML = {
    "name":            (True, "str",  "plugin name"),
    "tissue":          (True, "str",  ""),
    "species":         (True, "list", "species covered"),
    "schema_version":  (True, "str",  "must equal SCHEMA_VERSION"),
    "plugin_version":  (True, "str",  "semantic version"),
    "build_lock":      (True, "dict", "pinned inputs (see DESIGN §8.3)"),
    "axes":            (True, "dict", "declared axes: species / tissue / organism_stage"),
    "contact":         (False, "str", ""),
    "licence":         (True, "str",  "plugin licence"),
}

SCHEMAS = {
    "markers":   MARKER_ENTRY,
    "baselines": BASELINE_ENTRY,
    "disease":   DISEASE_ENTRY,
    "registry":  REGISTRY_ENTRY,
}

REQUIRED_FILES = ["plugin.yaml", "markers", "baselines", "disease", "ontology",
                  "registry.yaml", "query_templates.yaml", "extensions"]
