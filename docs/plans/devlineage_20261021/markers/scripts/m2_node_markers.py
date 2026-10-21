#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m2_node_markers.py — per-node marker sets with a role and a resolvable anchor per gene.

One row per (node, gene) in the contract's marker-assertion schema. Roles are separated
mechanically (DESIGN §5): a state programme that reaches a node is `state_warning`, a label that
the ontology places strictly under the node term is `subtype_discriminator`, the rest is
`identity_support`. Anchors are chosen from a fixed hierarchy and **every** anchor is re-resolved by
the gate (m5), so an anchor is a promise this script has to keep.

No assertion carries an `effect_value`: nothing in this card reads a number out of prose, so every
row is `claim_type=qualitative` (DESIGN §6.4). No assertion is written for a gene whose only local
evidence is an evaluation volume, nor for a gene whose only evidence is mouse-only against a human
node — those become gap rows.

Writes out/MARKER_SETS_NODE.tsv, out/ANCHORS.jsonl
Usage: python3 m2_node_markers.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mkcommon as M  # noqa: E402

ROLE_PRIORITY = {"identity_support": 0, "subtype_discriminator": 1, "state_warning": 2}
PROTEIN_HINTS = ("protein", "glycoprotein", "immunohistochem", "ihc", "western", "proteomic",
                 "mass spec", "tear fluid", "elisa", "antibody")


def load_examples():
    ex = {}
    path = os.path.join(M.OUT, "CORPUS_GENE_EXAMPLES_v1.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            ex[d["gene"]] = d["examples"]
    return ex


def load_gene_index():
    rows = {}
    for r in M.read_tsv(os.path.join(M.OUT, "CORPUS_GENE_INDEX_v1.tsv")):
        rows[r["gene"]] = r
    return rows


def assay_from_text(text):
    t = (text or "").lower()
    return "literature_protein" if any(h in t for h in PROTEIN_HINTS) else "literature_RNA"


def assay_from_panel_evidence(ev):
    kinds = {e.get("type") for e in ev or []}
    if "canonical" in kinds and len(kinds) == 1:
        return "textbook"
    txt = " ".join(json.dumps(e, ensure_ascii=False) for e in ev or [])
    if any(h in txt.lower() for h in PROTEIN_HINTS):
        return "literature_protein"
    if "data_driven" in kinds:
        return "scRNA"
    if kinds & {"pmid", "pmid_context"}:
        return "literature_RNA"
    return "unspecified"


def main() -> int:
    panels = M.load_panels()
    nodes = M.read_tsv(os.path.join(M.OUT, "NODES.tsv"))
    attach = M.read_tsv(os.path.join(M.OUT, "LABEL_ATTACHMENT.tsv"))
    ont, _nav = M.load_ontology()
    registry = M.load_link_registry()
    gidx = load_gene_index()
    examples = load_examples()
    core_ev, _dev_markers = M.load_dev_core_evidence()
    kind_sidecar = M.load_sidecar_kinds()
    papers_meta = M.load_papers()
    cl_align = M.load_cl_alignment()
    v6_bans = {g.split("/")[0].upper() for g in
               (json.load(open(os.path.join(M.MARKERS_DIR, "markers_v6_retina_repair.json"),
                               encoding="utf-8")).get("bans") or {})}

    by_node = {}
    for a in attach:
        by_node.setdefault(a["node_key"], []).append(a)

    assertions, anchors, refused = [], [], []
    n = 0
    for node in nodes:
        key, cid = node["node_key"], node["dl_id"]
        node_species = node["species"]
        node_genes = {}
        for a in by_node.get(key, []):
            lib, label = a["library"], a["label"]
            rec = panels.get(lib, {}).get("labels", {}).get(label)
            if rec is None:
                continue
            label_cid = ((a["cl_id_in_file"] or cl_align.get(label, "")) or "").strip()
            is_state_program = (a["concept_kind"] == "state_program")
            # is the label a strict partition of the node term?
            label_below_node = False
            if cid.startswith("CL:") and label_cid.startswith("CL:"):
                if label_cid != cid and label_cid in ont.descendants(cid):
                    label_below_node = True
            banned = v6_bans if lib == "retina_v6" else set()
            dev_ce = core_ev.get(label, {}) if lib in ("dev_v8", "dev_v9") else {}
            # The dev panels declare their own two tracks: data (`D`, the dev-exam substrate, i.e.
            # an evaluation volume) and literature (`L`). A gene carried on the data track alone
            # is the evaluation substrate's own signal; the contract forbids deriving a marker from
            # it, so such a gene gets no assertion here whatever else mentions it.
            # genes of the entry: the flat panel plus the panel's own subtype-anchor layer
            # (those genes were moved off the flat core on purpose, so they are not in it)
            gene_list = list(rec["genes"]) + [g for g in (rec.get("subtype_anchor") or {})
                                              if g not in rec["genes"]]
            for g in gene_list:
                if lib in ("dev_v8", "dev_v9"):
                    tk = str((dev_ce.get(g) or {}).get("track") or "")
                    if "D" in tk and "L" not in tk:
                        refused.append({"node_key": key, "gene": g, "library": lib,
                                        "label": label,
                                        "reason": "evidence_only_from_evaluation_volume",
                                        "detail": "the dev panel carries this gene on its data "
                                                  "track only (%s), and that track is the dev-exam "
                                                  "substrate" % tk})
                        continue
                if g in banned:
                    refused.append({"node_key": key, "gene": g, "library": lib, "label": label,
                                    "reason": "prohibited_by_library_ban",
                                    "detail": "gene on %s's own prohibition list" % a["panel_file"]})
                    continue
                # ---- role -------------------------------------------------------------
                role, tgt_sub = "identity_support", ""
                if is_state_program:
                    role = "state_warning"
                elif g in (rec.get("state_anchors") or {}):
                    role, tgt_sub = "state_warning", (rec["state_anchors"][g] or "")
                elif g in (rec.get("subtype_anchor") or {}):
                    role, tgt_sub = "subtype_discriminator", rec["subtype_anchor"][g]
                elif label_below_node:
                    role, tgt_sub = "subtype_discriminator", label
                # ---- anchor -----------------------------------------------------------
                anchor = None
                ev_ids = ""
                reg_row = registry.get("%s::%s" % (lib, label))
                if reg_row:
                    for cit in (reg_row.get("citations") or []):
                        if g in (cit.get("genes_in_text") or []):
                            anchor = {"kind": "link_registry_gene_verified",
                                      "file": M.LINK_REGISTRY,
                                      "entry_id": reg_row.get("entry_id"),
                                      "pmid": str(cit.get("pmid")),
                                      "locator": cit.get("evidence_locator") or "",
                                      "chunk_excerpt": (cit.get("chunk") or "")[:300],
                                      "gene": g}
                            ev_ids = "PMID:%s" % cit.get("pmid")
                            break
                basis = None
                if anchor:
                    basis = "link_registry_gene_verified"
                    assay = assay_from_text(anchor["chunk_excerpt"])
                    # the registry row carries no species; take it from the corpus paper record
                    anchor_species = str((papers_meta.get(str(anchor["pmid"])) or {})
                                         .get("species") or "unknown")
                else:
                    ex = []
                    if g in examples:
                        ex = [e for e in examples[g]
                              if e["species"] in ("human", "both")] or []
                    native = ex[0] if ex else None
                    if native:
                        basis = "corpus_gene_row"
                        assay = "literature_RNA"
                        anchor_species = native["species"]
                        anchor = {"kind": "corpus_gene_row", "file": M.CHUNKS,
                                  "paper_id": str(native["paper_id"]),
                                  "section": native["section"], "ord": native["ord"],
                                  "sha16": native["sha16"], "chunk_type": native["chunk_type"],
                                  "species": native["species"], "tissue": native["tissue"],
                                  "dev_kw": native["dev_kw"], "gene": g}
                        ev_ids = "PMID:%s" % native["paper_id"]
                    else:
                        pev = (rec.get("provenance") or {}).get(g) or \
                              (rec.get("evidence") or {}).get(g) or \
                              ([{"track": dev_ce[g]["track"],
                                "papers_devctx": dev_ce[g].get("papers_devctx")}]
                               if g in dev_ce else None)
                        non_eval = []
                        eval_hit = False
                        for e in (pev or []):
                            blob = json.dumps(e, ensure_ascii=False)
                            if M.is_eval_token(blob):
                                eval_hit = True
                            else:
                                non_eval.append(e)
                        if non_eval:
                            basis = "panel_provenance_stated"
                            assay = assay_from_panel_evidence(non_eval)
                            anchor_species = "human"
                            anchor = {"kind": "panel_provenance_stated",
                                      "file": panels[lib]["path"],
                                      "label": label, "library": lib, "gene": g,
                                      "evidence": non_eval[:3]}
                            ev_ids = ",".join(
                                sorted({str(e.get("id")) for e in non_eval
                                        if str(e.get("id", "")).startswith("PMID")}))[:200]
                        elif eval_hit and not (g in gidx and
                                               int(gidx[g]["n_chunks_human_or_both"]) > 0):
                            refused.append({"node_key": key, "gene": g, "library": lib,
                                            "label": label,
                                            "reason": "evidence_only_from_evaluation_volume",
                                            "detail": "panel per-gene evidence names an evaluation "
                                                      "volume and no independent local row exists"})
                            continue
                        elif g in gidx and int(gidx[g]["n_chunks_mouse_only_terms"]) > 0 and \
                                int(gidx[g]["n_chunks_human_or_both"]) == 0 and \
                                node_species == "human":
                            refused.append({"node_key": key, "gene": g, "library": lib,
                                            "label": label,
                                            "reason": "different_species_not_stitchable",
                                            "detail": "only mouse-species corpus rows exist; the "
                                                      "node is a human context"})
                            continue
                        else:
                            basis = "panel_entry_basis_unstated"
                            assay = "unspecified"
                            anchor_species = "human"
                            anchor = {"kind": "panel_entry_basis_unstated",
                                      "file": panels[lib]["path"],
                                      "label": label, "library": lib, "gene": g}
                prev = node_genes.get(g)
                if prev and ROLE_PRIORITY[prev["role"]] >= ROLE_PRIORITY[role]:
                    prev["sources"].append("%s::%s/%s" % (lib, label, basis))
                    continue
                node_genes[g] = {"role": role, "target_subtype": tgt_sub, "basis": basis,
                                 "anchor": anchor, "assay": assay, "ev_ids": ev_ids,
                                 "anchor_species": anchor_species, "library": lib, "label": label,
                                 "panel_file": a["panel_file"],
                                 "sources": ["%s::%s/%s" % (lib, label, basis)]}

        for g in sorted(node_genes):
            rec = node_genes[g]
            n += 1
            aid = "A%06d" % n
            anchor = rec["anchor"]
            assertions.append({
                "assertion_id": aid, "edge_id_or_node_key": key, "gene_symbol": g,
                "species": node_species, "role": rec["role"], "change": "present",
                "stage": node["organism_stage"], "assay": rec["assay"],
                "source_group": "%s::%s" % (rec["library"], rec["label"]),
                "target_group": node["cl_label"] or node["dl_id"],
                "effect_value": "", "uncertainty": "",
                "claim_type": "qualitative", "evidence_ids": rec["ev_ids"],
                "evidence_grade": "", "evidence_anchor": json.dumps(anchor, ensure_ascii=False,
                                                                   sort_keys=True),
                "support_basis": rec["basis"], "anchor_kind": anchor["kind"],
                "anchor_species": rec["anchor_species"], "target_subtype": rec["target_subtype"],
                "extraction_record": "", "detection_conditions": "",
                "node_family": node["node_family"], "node_dl_id": cid,
                "all_sources": " | ".join(sorted(set(rec["sources"]))),
                "panel_selection_basis": panels.get(rec["library"], {}).get("selection_basis",
                                                                            "unstated"),
            })
            anchors.append({"assertion_id": aid, "gene": g, "anchor": anchor})

    cols = ["assertion_id", "edge_id_or_node_key", "gene_symbol", "species", "role", "change",
            "stage", "assay", "source_group", "target_group", "effect_value", "uncertainty",
            "claim_type", "evidence_ids", "evidence_grade", "evidence_anchor", "support_basis",
            "anchor_kind", "anchor_species", "target_subtype", "extraction_record",
            "detection_conditions", "node_family", "node_dl_id", "all_sources",
            "panel_selection_basis"]
    M.write_tsv(os.path.join(M.OUT, "MARKER_SETS_NODE.tsv"), assertions, cols)
    with open(os.path.join(M.OUT, "ANCHORS.jsonl"), "w", encoding="utf-8") as f:
        for r in anchors:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    import collections
    print("node assertions:", len(assertions))
    print("  roles    :", dict(collections.Counter(a["role"] for a in assertions)))
    print("  basis    :", dict(collections.Counter(a["support_basis"] for a in assertions)))
    print("  assay    :", dict(collections.Counter(a["assay"] for a in assertions)))
    print("  refused  :", dict(collections.Counter(r["reason"] for r in refused)))
    print("  nodes with zero assertions:",
          sum(1 for nd in nodes if nd["node_key"] not in
              {a["edge_id_or_node_key"] for a in assertions}))
    M.write_tsv(os.path.join(M.OUT, "NODE_GENE_REFUSALS.tsv"), refused,
                ["node_key", "gene", "library", "label", "reason", "detail"])
    return 0


if __name__ == "__main__":
    sys.exit(main())