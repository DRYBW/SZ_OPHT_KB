#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m1_nodes.py — instantiate the contract's node key for the lineage this card can actually see.

Two node families, both in the contract's own key format:

  A. the covered classes and germ-layer anchors of card L2's accepted developmental lineage layer
     (`plans/cl_depth_devlineage_20261021/out/LINEAGE_NODES.tsv`, 60 nodes). The contract's own
     `devlineage_20261021/scaffold/` directory has not landed, so the node list is consumed from
     there and the provenance is recorded rather than assumed.

  B. the developmental precursor labels our own dev panels ship and the ontology cannot key
     (`RPC_early`, `NRPC_late`, `Rod_precursor`, `RGC_precursor`, …). The ontology records these as
     NO_MATCH (card DEV-ONT, D2 table: 7 of 10 rows NO_MATCH), and the contract supplies exactly the
     right form for them — `dl:NO_MATCH:<in_house_class_id>|…`. Without these nodes the lineage's
     developmental side would have no markers at all, which is the owner's central ask; they are
     knowledge-layer nodes and never enter cell candidate ranking.

Every field is derived from a named local source, never typed:
  cl_id       read from the ontology file by card L2 (its `obo_line` column re-checked here)
  species     the panel's declared derivation; `unknown` for germ-layer anchors
  tissue      the label's panel scope text / entry tissue field
  stage       {fetal, adult, developing, unknown} — `adult_or_unspecified` is NEVER adult
  es          `unknown` everywhere (no shipped panel asserts an experimental system; see DESIGN §6)

Writes out/NODES.tsv, out/LABEL_ATTACHMENT.tsv, out/NODE_CONTEXT_SOURCES.json
Usage: python3 m1_nodes.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

LIB_CONTEXT = {
    "retina": ("retina", "human", "markers_v4.1_clean.json note: derived from the human retina "
                                  "atlas annotated in HRCA v1"),
    "retina_interneuron": ("retina", "human", "markers_v5 note: HRCA v1 human retina author "
                                                "annotation pairwise DE"),
    "retina_v6": ("retina", "human", "markers_v6 scope: KB7 human retina repair layer"),
    "retina_v7": ("retina", "human", "markers_v7 scope: human retina facet increment"),
    "dev_v8": ("retina", "human", "markers_v8 species=human, organism_stage=fetal/developing"),
    "dev_v9": ("retina", "human", "markers_v9 species=human, organism_stage=fetal/developing"),
    "membrane": ("eye_membrane", "human", "markers_membrane_v1 scope: human eye membrane / vessel / "
                                          "stroma / immune panels (PDR-RRD membrane and general "
                                          "eyeball non-retinal classes)"),
    "face_v6": ("ocular_surface", "human", "markers_v6_face scope: KB7 B1 ocular surface increment"),
    "k9_ocs": ("ocular_surface", "human", "markers_k9_ocs scope: KB9 ocular surface entry gap"),
    "lacrimal_v6": ("lacrimal_gland", "human", "markers_v6_lacrimal scope: KB8 human lacrimal gland "
                                                "entries (GSE164403)"),
        "lensiris_v11": ("lens", "human", "markers_v11_lensiris: entries carry their own CL id and "
                                          "their own per-entry dev_volume; scope_tissues = lens, iris"),
    }
ANTSEG_TISSUE = {
    "lens epithelial cell": "lens", "lens fiber cell": "lens",
    "corneal epithelial cell": "cornea", "corneal endothelial cell": "cornea",
    "basal cell": "cornea", "transit amplifying cell": "cornea",
    "conjunctival epithelial cell": "conjunctiva", "goblet cell": "conjunctiva",
    "trabecular meshwork cell": "trabecular_meshwork",
    "pigmented ciliary epithelial cell": "ciliary_body",
    "non-pigmented ciliary epithelial cell": "ciliary_body",
    "ciliary muscle cell": "ciliary_body", "iris pigment epithelial cell": "iris",
    "progenitor cell": "ocular_surface", "mast cell": "eye", "oligodendrocyte": "optic_nerve",
    # markers_v11 (lens / iris increment) declares its own two tissues and keys its entries by
    # class name; the mapping below is that file's own scope, not an inference
    "anterior lens cell": "lens", "secondary lens fiber": "lens",
    "pigmented epithelial cell": "iris",
}
# a state programme reaches an identity node only where the shipped material says so
STATE_NODE_MAP = {
    "Endo_Patho": "CL:0000115",
    "Mac_DAM_LAM": "CL:0000235",
    "TAC_proliferating": "CL:0009010",
    "Proliferating": "",           # no identity node in the node list -> gap register
    "Retinal_Proliferating": "",   # the cycling state of the retinal progenitor programme -> gap
}
DEV_LIBS = ("dev_v8", "dev_v9")


def label_registry(panels):
    reg = {}
    for lib, p in panels.items():
        for label, rec in p["labels"].items():
            reg.setdefault(label, []).append((lib, rec))
    return reg


def main() -> int:
    panels = M.load_panels()
    reg = label_registry(panels)
    nodes_in = M.read_tsv(M.L2_NODES)
    ont, nav = M.load_ontology()

    nodes, attach, node_key_by_id = [], [], {}

    def emit(node, basis_rows):
        nodes.append(node)
        for b in basis_rows:
            attach.append(b)

    for r in nodes_in:
        cid = r["node_id"]
        kind = r["kind"]
        labels = [x for x in (r["our_labels"] or "").split(",") if x]
        labelled_ok = bool(ont.label(cid))
        if kind == "germ_layer":
            tissue, species, src = "unknown", "unknown", "germ-layer anchor: no panel carries it"
            stage = "developing" if r["stage_scope"] == "developing" else "unknown"
        else:
            adult_keys = [x for x in (r["in_adult_baseline_keys"] or "").split(",") if x]
            stage = ("developing" if r["stage_scope"] == "developing"
                     else ("adult" if adult_keys else "unknown"))
            ctxs = []
            for lab in labels:
                for lib, rec in reg.get(lab, []):
                    if lib in LIB_CONTEXT:
                        ctxs.append((lib,) + LIB_CONTEXT[lib])
                    elif lib == "antseg_v10":
                        ctxs.append((lib, ANTSEG_TISSUE.get(lab, "eye"), "human",
                                     "markers_v10 entry class_name=%s (human anterior-segment "
                                     "scope)" % lab))
            if ctxs:
                lib, tissue, species, src = ctxs[0]
                src = "%s (%s)" % (src, lib)
            else:
                tissue, species, src = "unknown", "unknown", "no panel context recorded"
        key = "dl:%s|sp=%s|ts=%s|st=%s|es=unknown" % (cid, species, tissue, stage)
        node_key_by_id[cid] = key
        emit({"node_key": key, "dl_id": cid, "kind": kind, "cl_label": ont.label(cid) or "",
              "cl_label_from_file": r["cl_label"],
              "cl_label_matches_file": "yes" if ((ont.label(cid) or "") == r["cl_label"]) else "no",
              "obo_line": r["obo_line"], "species": species, "tissue_context": tissue,
              "organism_stage": stage, "experimental_system": "unknown",
              "stage_scope_upstream": r["stage_scope"],
              "adult_baseline_keys": r["in_adult_baseline_keys"],
              "n_panel_genes_upstream": r["n_panel_genes"], "labels": ",".join(labels),
              "panel_files": r["panel_files"], "n_inbound_edges_upstream": r["n_inbound_edges"],
              "context_source": src, "cl_id_in_ontology_file": "yes" if labelled_ok else "no",
              "node_family": "scaffold"}, [])
        for lab in labels:
            for lib, rec in reg.get(lab, []):
                attach.append({"node_key": key, "dl_id": cid, "label": lab, "library": lib,
                               "panel_file": rec["file"], "n_genes": len(rec["genes"]),
                               "concept_kind": rec.get("kind") or "unclassified",
                               "cl_id_in_file": rec.get("cl_id_in_file") or "",
                               "attach_basis": "upstream_label_map",
                               "label_in_link_registry": "%s::%s" % (lib, lab)})

    attached_keys = {(a["library"], a["label"]) for a in attach}

    # --- rule 1: a panel label that declares its own CL id and that id is a node -----------
    for lab, entries in reg.items():
        for lib, rec in entries:
            cid = rec.get("cl_id_in_file") or ""
            if cid and cid in node_key_by_id and (lib, lab) not in attached_keys:
                attach.append({"node_key": node_key_by_id[cid], "dl_id": cid, "label": lab,
                               "library": lib, "panel_file": rec["file"],
                               "n_genes": len(rec["genes"]),
                               "concept_kind": rec.get("kind") or "unclassified",
                               "cl_id_in_file": cid, "attach_basis": "cl_id_declared_in_panel",
                               "label_in_link_registry": "%s::%s" % (lib, lab)})
                attached_keys.add((lib, lab))

    # --- rule 2: a state programme reaches its named identity node ------------------------
    for lab, cid in STATE_NODE_MAP.items():
        if not cid or cid not in node_key_by_id:
            continue
        for lib, rec in reg.get(lab, []):
            if (lib, lab) in attached_keys:
                continue
            attach.append({"node_key": node_key_by_id[cid], "dl_id": cid, "label": lab,
                           "library": lib, "panel_file": rec["file"],
                           "n_genes": len(rec["genes"]),
                           "concept_kind": rec.get("kind") or "unclassified",
                           "cl_id_in_file": rec.get("cl_id_in_file") or "",
                           "attach_basis": "state_program_to_identity_node",
                           "label_in_link_registry": "%s::%s" % (lib, lab)})
            attached_keys.add((lib, lab))

    # --- rule 3: in-house developmental precursor nodes (contract NO_MATCH form) ----------
    dev_labels = {}
    for lib in DEV_LIBS:
        p = panels.get(lib)
        if not p:
            continue
        for lab, rec in p["labels"].items():
            if rec.get("kind") == "state_program":
                continue
            if any((l2, lab) in attached_keys for l2, _ in reg.get(lab, [])):
                continue
            dev_labels.setdefault(lab, []).append((lib, rec))
    for lab, entries in sorted(dev_labels.items()):
        n_genes = sum(len(r["genes"]) for _l, r in entries)
        files = ",".join(sorted({r["file"] for _l, r in entries}))
        key = "dl:NO_MATCH:%s|sp=human|ts=retina|st=developing|es=unknown" % lab
        nodes.append({"node_key": key, "dl_id": "NO_MATCH:%s" % lab,
                      "kind": "in_house_dev_precursor", "cl_label": "",
                      "cl_label_from_file": "", "cl_label_matches_file": "n/a", "obo_line": "",
                      "species": "human", "tissue_context": "retina", "organism_stage": "developing",
                      "experimental_system": "unknown", "stage_scope_upstream": "developing",
                      "adult_baseline_keys": "", "n_panel_genes_upstream": str(n_genes),
                      "labels": lab, "panel_files": files, "n_inbound_edges_upstream": "",
                      "context_source": ("kb/markers dev panels declare species=human, "
                                         "organism_stage=fetal/developing; ontology has no term "
                                         "(card DEV-ONT D2 NO_MATCH) so the contract's NO_MATCH node "
                                         "form applies"),
                      "cl_id_in_ontology_file": "n/a", "node_family": "in_house_dev_precursor"})
        for lib, rec in entries:
            attach.append({"node_key": key, "dl_id": "NO_MATCH:%s" % lab, "label": lab,
                           "library": lib, "panel_file": rec["file"],
                           "n_genes": len(rec["genes"]),
                           "concept_kind": rec.get("kind") or "unclassified",
                           "cl_id_in_file": rec.get("cl_id_in_file") or "",
                           "attach_basis": "contract_NO_MATCH_rule",
                           "label_in_link_registry": "%s::%s" % (lib, lab)})
            attached_keys.add((lib, lab))

    M.write_tsv(os.path.join(M.OUT, "NODES.tsv"), nodes,
                ["node_key", "dl_id", "kind", "cl_label", "cl_label_from_file",
                 "cl_label_matches_file", "obo_line", "species", "tissue_context",
                 "organism_stage", "experimental_system", "stage_scope_upstream",
                 "adult_baseline_keys", "n_panel_genes_upstream", "labels", "panel_files",
                 "n_inbound_edges_upstream", "context_source", "cl_id_in_ontology_file",
                 "node_family"])
    M.write_tsv(os.path.join(M.OUT, "LABEL_ATTACHMENT.tsv"), attach,
                ["node_key", "dl_id", "label", "library", "panel_file", "n_genes",
                 "concept_kind", "cl_id_in_file", "attach_basis", "label_in_link_registry"])

    orphan = []
    for lib, p in panels.items():
        for label, rec in p["labels"].items():
            if (lib, label) not in attached_keys:
                orphan.append({"library": lib, "label": label, "panel_file": rec["file"],
                               "n_genes": len(rec["genes"]),
                               "concept_kind": rec.get("kind") or "unclassified"})
    ctx = {
        "generated_by": "scripts/m1_nodes.py",
        "node_list_source": M.L2_NODES,
        "node_list_provenance": ("card L2's accepted developmental lineage layer; the contract's "
                                 "scaffold/ directory has not landed"),
        "ontology": {"path": nav["primary_path"], "release": nav.get("release"),
                     "sha256": nav.get("sha256")},
        "n_nodes": len(nodes),
        "n_scaffold_nodes": sum(1 for n in nodes if n["node_family"] == "scaffold"),
        "n_in_house_dev_precursor_nodes": sum(1 for n in nodes
                                              if n["node_family"] == "in_house_dev_precursor"),
        "n_germ_layer_anchors": sum(1 for n in nodes if n["kind"] == "germ_layer"),
        "stage_counts": {s: sum(1 for n in nodes if n["organism_stage"] == s) for s in M.STAGES},
        "n_nodes_missing_from_ontology_file": sum(1 for n in nodes
                                                  if n["cl_id_in_ontology_file"] == "no"),
        "n_nodes_stage_from_developing_scope": sum(1 for n in nodes
                                                   if n["organism_stage"] == "developing"),
        "n_labels_attached": len(attach), "n_labels_orphaned": len(orphan),
        "orphan_labels": orphan,
        "node_key_format": ("dl:<canonical_cl_id>|sp=<species>|ts=<tissue_context>|"
                            "st=<organism_stage>|es=<experimental_system>"),
    }
    M.write_json(os.path.join(M.OUT, "NODE_CONTEXT_SOURCES.json"), ctx)
    print(f"nodes={len(nodes)} scaffold={ctx['n_scaffold_nodes']} "
          f"in_house_dev={ctx['n_in_house_dev_precursor_nodes']} germ={ctx['n_germ_layer_anchors']}")
    print(f"stage counts {ctx['stage_counts']}")
    print(f"labels attached={len(attach)} orphaned={len(orphan)}")
    for o in orphan:
        print("   orphan label", o["library"], "::", o["label"], o["concept_kind"], o["n_genes"])
    return 0


if __name__ == "__main__":
    sys.exit(main())