#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mkcommon.py — shared, read-only vocabulary and loaders for the marker layer.

Everything here reads shipped artefacts and never writes into `kb/`. The evaluation side is a
NEGATIVE input: the volume names below are the forbidden set, and any provenance or corpus row
that resolves to one of them is refused as evidence (contract red line: no marker may be derived
from the evaluation volumes' own queries).
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import os
import re
import sys

WAVE = "/mnt/D/EyeKB/plans/devlineage_20261021/markers"
# Every build script writes here. The gate rebuilds the whole chain into a scratch directory by
# exporting MK_OUTDIR and compares hashes, so "it rebuilds byte-identically" is measured, not argued.
OUT = os.environ.get("MK_OUTDIR", os.path.join(WAVE, "out"))
KB = "/mnt/D/EyeKB/kb"
MARKERS_DIR = os.path.join(KB, "markers")
MARKERS_DIR_REPO = "/home/ubuntu/EYEKB_REPO/kb/markers"


def panel_path(basename):
    """The shipped library, preferring the construction site and falling back to the repo copy.

    The two copies are byte-identical for every shared file (checked in the report); the repo copy
    additionally carries two panels the site does not, which card L2 also read from there.
    """
    p = os.path.join(MARKERS_DIR, basename)
    return p if os.path.isfile(p) else os.path.join(MARKERS_DIR_REPO, basename)
LINK_REGISTRY = os.path.join(KB, "link_registry", "LINK_REGISTRY_v1.jsonl")
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10"
CHUNKS = os.path.join(CORPUS, "chunks.parquet")
PAPERS = os.path.join(CORPUS, "papers.jsonl")
TEXTBOOK = os.path.join(KB, "textbook_layer", "TEXTBOOK_ITEMS_v1.jsonl")
SIDECAR_KIND = os.path.join(MARKERS_DIR, "_concept_kind_sidecar_v1.json")
ROLE_FLAG = sorted(glob.glob(os.path.join(KB, "literature_db", "role_flag_devline_2026-10*.jsonl")))
STAGE_SCOPE = os.path.join(KB, "literature_db", "dev_stage_scope_devline_2026-10.jsonl")

# --- upstream card L2 (the scaffold that landed on disk) --------------------------------
L2 = "/mnt/D/EyeKB/plans/cl_depth_devlineage_20261021"
L2_OUT = os.path.join(L2, "out")
L2_NODES = os.path.join(L2_OUT, "LINEAGE_NODES.tsv")
L2_EDGES = os.path.join(L2_OUT, "LINEAGE_EDGES.tsv")
L2_UNRESOLVED = os.path.join(L2_OUT, "LINEAGE_UNRESOLVED_DEVELOPMENT.tsv")
ONT_NAV = os.path.join(L2_OUT, "ONT_NAV_v1.json")
L2_SCRIPTS = os.path.join(L2, "scripts")

# --- evaluation side (forbidden as an input) -------------------------------------------
FORBIDDEN_VOLUMES = [
    "CX01_retina_snRNA", "CX02_adult_retina", "CX03_retina_multiome", "CX04_cowan_fovea",
    "CX04_cowan_organoid", "CX04_cowan_periphery", "CX07_iPSC_organoid_POAG",
    "CX08_RPE_choroid_scRNA", "CX08_RPE_choroid_snRNA", "CX09_voigt_RPE_choroid",
    "CX10_hiPSC_RPE", "CX11_posterior_eye_atlas", "CX12_ocular_surface_snRNA",
    "CX13_TM_corneal_scleral", "CX13_central_cornea", "CX13_ciliary_body", "CX13_iris",
    "CX13_lens", "CX14_TM_ciliary_snRNA", "CX15_optic_nerve_all", "CX16_tabula_sapiens_eye",
    "CX17_mouse_retina_all", "PRE_GSE199013", "PRE_GSE268630", "PRE_OA-D001", "PRE_OA-D002",
    "PRE_OA-D004", "PRE_OA-D068",
]
FORBIDDEN_TOKENS = FORBIDDEN_VOLUMES + [
    "oss_check_20261019",
    "GSE268630", "GSE199013",
    "39117640",                      # the dev-exam substrate's own paper (role_flag data_side_only)
]
# provenance ids that name an evaluation volume under another spelling
EVAL_EVIDENCE_RE = re.compile(
    r"(?:CX\d{2}[_A-Za-z]|PRE_(?:GSE|OA-)|OA-?D0\d{2}|HRCA_D0\d{2}|GSE268630|GSE199013|39117640)",
    re.IGNORECASE)

# --- declared vocabularies (see DESIGN §6) ---------------------------------------------
ROLES = ("identity_support", "subtype_discriminator", "state_warning")
CHANGES = ("up", "down", "on", "off", "transient", "present")
STAGES = ("fetal", "adult", "developing", "unknown")
CLAIM_TYPES = ("quantitative", "qualitative")
SPECIES_VOCAB = ("human", "mouse", "both", "unknown")
ASSAYS = ("scRNA", "literature_RNA", "literature_protein", "textbook", "unspecified")
EXP_SYSTEMS = ("in_vivo", "organoid", "iPSC_derived", "culture", "unknown")
EV_GRADES = ("direct_lineage_support", "identity_conversion_not_direct",
             "textbook_or_review_distant_origin", "trajectory_only")
RELATION_TYPES = ("ontology_development_relation", "direct_lineage", "ancestral_origin",
                  "trajectory_association")
SUPPORT_BASIS = ("link_registry_gene_verified", "corpus_gene_row", "panel_provenance_stated",
                 "panel_entry_basis_unstated")
GAP_REASONS = (
    "no_source_in_corpus", "source_exists_not_full_text",
    "review_citation_unverifiable_locally", "different_species_not_stitchable",
    "different_stage_not_stitchable", "evidence_only_from_evaluation_volume",
    "prohibited_by_library_ban", "node_has_no_panel_and_no_source",
    "parent_group_has_no_panel", "edge_not_stepwise_relation",
    "marker_change_not_available_for_relation_type", "no_source_states_the_change",
    "detection_conditions_insufficient", "state_program_without_identity_node",
    "panel_entry_basis_unstated", "panel_selected_from_evaluation_report",
)

# panel files consumed as the identity candidate pool, with the library key used by the
# shipped link registry (so an anchor can be looked up by entry id)
PANEL_FILES = [
    ("retina", "markers_v4.1_clean.json"),
    ("retina_interneuron", "markers_v5_retina_interneuron.json"),
    ("retina_v6", "markers_v6_retina_repair.json"),
    ("retina_v7", "markers_v7_panel_increment.json"),
    ("dev_v8", "markers_v8_dev_retina.json"),
    ("dev_v9", "markers_v9_dev_retina.json"),
    ("membrane", "markers_membrane_v1.json"),
    ("antseg_v10", "markers_v10_antseg_increment.json"),
    ("lensiris_v11", "markers_v11_lensiris_increment.json"),
    ("face_v6", "markers_v6_face_increment.json"),
    ("k9_ocs", "markers_k9_ocs_increment.json"),
    ("lacrimal_v6", "markers_v6_lacrimal_increment.json"),
]

# A panel is refused outright when its own scope text says it was built to fill the holes the
# evaluation run itself reported: consuming it would make the layer a derivative of the benchmark
# (contract red line). Recorded rather than silently dropped.
REFUSED_PANELS = {
    "markers_v12_holefill_increment.json": {
        "reason": "panel_selected_from_evaluation_report",
        "quote": ("scope: the measured coverage holes of the 28-volume / 721-cluster run — "
                  "vascular endothelium in retina and choroid, macrophage and monocyte separated "
                  "from microglia, retinal rod depth, and the RPE/melanocyte pair"),
    },
}

# How each consumed panel's candidate pool was selected — disclosed on every assertion so a reader
# can discount a set whose selection leaned on an evaluation volume, even when the anchor for the
# individual gene is independent.
SELECTION_BASIS = {
    "retina": "curated_panel_pre_2026 (literature + canonical consensus)",
    "retina_interneuron": "in_house_atlas_eval_volume (HRCA D001 pairwise-DE gate)",
    "retina_v6": "in_house_atlas_eval_volume (HRCA D001 / KB7 repair disposition)",
    "retina_v7": "in_house_atlas_eval_volume (retina facet increment on D001-derived entries)",
    "dev_v8": "developmental_panel_data_plus_literature (data track = the dev-exam substrate)",
    "dev_v9": "developmental_panel_data_plus_literature (data track = the dev-exam substrate)",
    "membrane": "in_house_atlas_non_eval (GSE165784) + canonical consensus",
    "antseg_v10": "in_house_atlas_eval_volume (per-entry dev_volume) + corpus harvest",
    "lensiris_v11": "in_house_atlas_eval_volume (per-entry dev_volume) + corpus harvest",
    "face_v6": "in_house_atlas_eval_volume (D002 ocular surface) + canonical consensus",
    "k9_ocs": "in_house_atlas_eval_volume (D002 ocular surface) + canonical consensus",
    "lacrimal_v6": "in_house_atlas_non_eval (GSE164403 human lacrimal gland)",
}

GENE_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-]{1,14}")
SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9\-]{1,14}$")


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, cols):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def is_eval_token(text):
    """True when a provenance id / volume string names an evaluation volume."""
    if not text:
        return False
    return bool(EVAL_EVIDENCE_RE.search(str(text)))


def load_cl_alignment():
    """label -> cl_id, from the shipped label-map sidecar (76 labels over the libraries).

    This is the repository's own answer to 'which ontology term does this in-house label denote',
    so it is used for the role decision instead of guessing from the label's spelling.
    """
    p = os.path.join(MARKERS_DIR, "markers_cl_alignment_v2_unified.json")
    out = {}
    if os.path.isfile(p):
        d = json.load(open(p, encoding="utf-8"))
        for label, rec in (d.get("labels") or {}).items():
            if rec.get("cl_id"):
                out[label] = rec["cl_id"]
    return out


def load_sidecar_kinds():
    """(panel basename, entry) -> concept_kind."""
    d = json.load(open(SIDECAR_KIND, encoding="utf-8"))
    out = {}
    for fn, ents in (d.get("libs") or {}).items():
        for ent, rec in ents.items():
            out[(fn, ent)] = rec.get("concept_kind")
    return out


def load_link_registry():
    """entry_id -> row (with citations)."""
    rows = {}
    with open(LINK_REGISTRY, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rows[d.get("entry_id")] = d
    return rows


def load_panels():
    """library -> {label: {'genes': [...], 'file': basename, 'provenance': {gene: [rec]},
    'evidence': {gene: [rec]}, 'subtype_anchor': {gene: subtype}, 'kind': concept_kind}}"""
    kinds = load_sidecar_kinds()
    out = {}
    for lib, fname in PANEL_FILES:
        path = panel_path(fname)
        if not os.path.isfile(path):
            continue
        d = json.load(open(path, encoding="utf-8"))
        labels = {}
        prov_root = d.get("provenance") or {}
        for label, genes in (d.get("markers") or {}).items():
            if not isinstance(genes, list):
                continue
            labels.setdefault(label, {"genes": [], "provenance": {}, "evidence": {},
                                      "subtype_anchor": {}})
            rec = labels[label]
            for g in genes:
                g = str(g).upper()
                if not SYMBOL_RE.match(g):
                    continue
                if g not in rec["genes"]:
                    rec["genes"].append(g)
                if isinstance(prov_root.get(label), dict) and g in prov_root[label]:
                    rec["provenance"][g] = prov_root[label][g]
        for ent in (d.get("entries") or []):
            if not isinstance(ent, dict):
                continue
            label = ent.get("class_name")
            if not label:
                continue
            rec = labels.setdefault(label, {"genes": [], "provenance": {}, "evidence": {},
                                            "subtype_anchor": {}})
            rec["cl_id_in_file"] = ent.get("cl_id")
            rec["tissue_in_file"] = ent.get("tissue")
            rec["dev_volume"] = ent.get("dev_volume")
            rec["provenance_note"] = ent.get("provenance")
            for g in (ent.get("markers") or []):
                g = str(g).upper()
                if SYMBOL_RE.match(g) and g not in rec["genes"]:
                    rec["genes"].append(g)
        # per-gene evidence blocks (v6 style, and the face / lacrimal increments). The block
        # keys are label names, except `microglia_repair`, whose own `applies_to` field names the
        # library entries it belongs to; its `state_anchors` is a state list, not identity.
        for key in ("marker_blocks", "stromal_repair", "face_increment",
                    "lacrimal_increment", "new_terms"):
            blk = d.get(key)
            if not isinstance(blk, dict):
                continue
            for label, val in blk.items():
                genes = val.get("core") if isinstance(val, dict) else None
                if genes is None and isinstance(val, list):
                    genes = val
                if not isinstance(genes, list):
                    continue
                rec = labels.setdefault(label, {"genes": [], "provenance": {}, "evidence": {},
                                                "subtype_anchor": {}})
                for item in genes:
                    if isinstance(item, dict) and item.get("gene"):
                        g = str(item["gene"]).upper()
                        rec["evidence"].setdefault(g, []).extend(item.get("evidence") or [])
                        if SYMBOL_RE.match(g) and g not in rec["genes"]:
                            rec["genes"].append(g)
        mr = d.get("microglia_repair")
        if isinstance(mr, dict):
            targets = [t.split("::")[-1] for t in (mr.get("applies_to") or [])]
            label = targets[0] if targets else "Microglia"
            rec = labels.setdefault(label, {"genes": [], "provenance": {}, "evidence": {},
                                            "subtype_anchor": {}})
            rec["applies_to"] = mr.get("applies_to")
            for item in (mr.get("core") or []):
                if isinstance(item, dict) and item.get("gene"):
                    g = str(item["gene"]).upper()
                    rec["evidence"].setdefault(g, []).extend(item.get("evidence") or [])
                    if SYMBOL_RE.match(g) and g not in rec["genes"]:
                        rec["genes"].append(g)
            for item in (mr.get("state_anchors") or []):
                if isinstance(item, dict) and item.get("gene"):
                    g = str(item["gene"]).upper()
                    rec.setdefault("state_anchors", {})[g] = (item.get("anchor_subtype") or
                                                              "state anchor")
                    rec["evidence"].setdefault(g, []).extend(item.get("evidence") or [])
        for label, items in (d.get("subtype_anchor_layer") or {}).items():
            rec = labels.setdefault(label, {"genes": [], "provenance": {}, "evidence": {},
                                            "subtype_anchor": {}})
            for it in items:
                g = str(it.get("gene", "")).upper()
                if g:
                    rec["subtype_anchor"][g] = it.get("anchor_subtype") or ""
        for label in labels:
            labels[label]["kind"] = kinds.get((fname, label))
            labels[label]["file"] = fname
        out[lib] = {"file": fname, "path": path, "labels": labels,
                    "payload_keys": sorted(d.keys()),
                    "scope": d.get("scope") or d.get("applicability") or "",
                    "selection_basis": SELECTION_BASIS.get(lib, "unstated")}
    return out


def load_dev_core_evidence():
    """dev_v9 → {label: {gene: {'track':..., 'freq_in_C':..., 'papers_devctx':...}}}"""
    d = json.load(open(os.path.join(MARKERS_DIR, "markers_v9_dev_retina.json"), encoding="utf-8"))
    return d.get("core_evidence") or {}, (d.get("markers") or {})


def load_papers():
    out = {}
    with open(PAPERS, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[str(d.get("paper_id"))] = d
    return out


def load_role_flags():
    """pmid -> role_flag (data_side_only means: searchable as background, never an anchor)."""
    out = {}
    for path in ROLE_FLAG:
        for line in open(path, encoding="utf-8"):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            pid = d.get("pmid") or d.get("paper_id")
            if pid:
                out[str(pid)] = d.get("role_flag")
    return out


def load_stage_scope():
    """pmid -> dev stage scope value (fetal_only | adult_only | mixed | not_recorded)."""
    out = {}
    if not os.path.isfile(STAGE_SCOPE):
        return out
    for line in open(STAGE_SCOPE, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        pid = d.get("pmid") or d.get("paper_id")
        if pid:
            out[str(pid)] = d.get("dev_stage_final") or d.get("scope") or d.get("value")
    return out


def load_ontology():
    """Reuse card L2's navigator rather than re-implementing ontology parsing."""
    sys.path.insert(0, L2_SCRIPTS)
    import ont_nav  # noqa: E402
    nav = json.load(open(ONT_NAV, encoding="utf-8"))
    return ont_nav.Ontology(nav["primary_path"]), nav