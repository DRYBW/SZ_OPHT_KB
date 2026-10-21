#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s1_enum_nodes.py - the enumerated node set of the developmental scaffold, in contract key form.

Three rings, all of them read from local authority:

  ring A  library_class        the class concepts our marker libraries actually ship: 52 concepts
                               the ontology can name (a CL id read from the file) + the concepts
                               it cannot (`dl:NO_MATCH:<label>` keys, which the contract provides
                               for exactly this case so an in-house concept can never be mistaken
                               for an ontology term)
  ring B  ontology_intermediate every CL term on a `develops_from` path out of a ring-A class, so
                               each ontology step becomes a node instead of a string inside a chain
  ring C  origin_anchor        the germ-layer / origin anchors the repository already resolved

Field provenance is carried per row: `st` (the four-level axis) and the `sp`/`ts`/`es` fields of
the node key each record the artefact they were read from. `unknown` is written wherever nothing
local declares the field - it is never filled with a plausible-looking default, and `adult` is
written only where a repository baseline declares an adult stage for that class.

Outputs: out/SCAFFOLD_NODES.tsv, out/NODES_SUMMARY.json
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scaffold_common as C  # noqa: E402
from ont_nav import Ontology  # noqa: E402

NODE_COLS = [
    "node_id", "node_key", "kind", "cl_id", "cl_label", "obo_line", "ontology_match_status",
    "in_library", "in_cell_ranking", "stage", "stage_basis", "species", "species_basis",
    "tissue_context", "tissue_basis", "tissue_candidates", "experimental_system", "es_basis",
    "our_labels", "n_our_labels", "n_panel_genes", "panel_files", "library_ring", "anchor_role",
    "on_rpc_axis", "chain_to_anchor", "cell_mass_share_pct", "cell_mass_basis", "stage_note",
]


def _is_named_precursor(label: str) -> bool:
    """Our panels also ship precursor concepts whose labels are abbreviations (`NRPC_early`).
    They are developmental by intent but carry no word from the stage word list, so the stage
    stays `unknown` and the reason is recorded here instead of being guessed."""
    return bool(re.search(r"(?<![a-z])(rpc|npc|precursor|proliferat|tac)(?![a-z])", str(label).lower())) \
        or "progenitor" in str(label).lower()


def main() -> int:
    nav = json.load(open(C.ONT_NAV, encoding="utf-8"))
    ont = Ontology(C.ONT_OBO)
    lab = C.load_label_map()
    panels, panel_files = C.load_panels()
    bases = C.load_baselines()

    # ---- label -> CL id, and the concepts the ontology cannot name
    cl_labels = collections.defaultdict(set)
    cl_files = collections.defaultdict(set)
    cl_genes = collections.defaultdict(set)
    nomatch = {}
    for label, r in lab.items():
        cl_files[label] = panel_files.get(label, set())
        cl_genes[label] = panels.get(label, set())
        if r["cl_id"]:
            cl_labels[r["cl_id"]].add(label)
            cl_files[r["cl_id"]] |= panel_files.get(label, set())
            cl_genes[r["cl_id"]] |= panels.get(label, set())
        else:
            nomatch[label] = r["libraries"]
    print(f"library concepts: {len(lab)}  mapped to a CL id: "
          f"{sum(1 for r in lab.values() if r['cl_id'])} -> {len(cl_labels)} distinct CL ids; "
          f"NO_MATCH concepts: {len(nomatch)}")

    # ---- baseline declarations per class (tissue / species / stage / recorded share)
    decl = collections.defaultdict(list)      # cl_id or label -> [(baseline file, info)]
    for fname, info in bases.items():
        for key in info["keys"]:
            decl[C.norm(key)].append((fname, info))
    def declarations(labels):
        out = []
        for l in labels:
            for fname, info in decl.get(C.norm(l), []):
                if (fname, info) not in out:
                    out.append((fname, info))
        return sorted(out, key=lambda x: x[0])

    def stage_of(cl_id, label, lines):
        """The four-level axis, decided by the ontology's own text first, then by a repository
        baseline that declares an adult stage. Nothing else can produce `adult`."""
        blob = ""
        if cl_id and cl_id in ont.terms:
            t = ont.terms[cl_id]
            blob = f"{ont.label(cl_id) or ''} {t.definition or ''}"
            w = C.dev_word_in(blob)
            if w:
                return "developing", f"ontology:{ont.trace_line(cl_id)}#dev_word={w}", w
        else:
            w = C.dev_word_in_label(label)
            if w:
                return "developing", f"label_dev_word:{w}", w
        for fname, info in declarations(lines):
            if str(info["stage"]).lower().startswith("adult"):
                return "adult", f"baseline:{fname}#development_stage=adult", ""
        return "unknown", "no_local_stage_declaration", ""

    def mass_of(labels):
        pts = []
        for fname, info in declarations(labels):
            for l in labels:
                if l in info["shares"]:
                    pts.append((fname, l, info["shares"][l]))
        if not pts:
            return "", "no_baseline_share_recorded"
        pts.sort()
        return ";".join(f"{f}:{l}={v}" for f, l, v in pts), "baseline_major_classes#donor_median_pct"

    rows = []
    # ---- ring A (ring A1: mapped, ring A2: NO_MATCH)
    for cl_id in sorted(cl_labels):
        labels = sorted(cl_labels[cl_id])
        st, basis, _w = stage_of(cl_id, "", labels)
        d = declarations(labels)
        sp = "human" if any(str(i["species"]) == "human" for _, i in d) else "unknown"
        sp_basis = (f"baseline:{d[0][0]}#species=human" if sp == "human" else "no_species_declaration")
        tis = sorted({f[:-5] for f, _ in d})
        ts = tis[0] if len(tis) == 1 else ("unknown" if not tis else "unknown")
        ts_basis = ("baseline:" + d[0][0] + "#unique_declaring_entry" if len(tis) == 1
                    else ("no_baseline_declares_this_class" if not tis
                          else "multiple_declaring_entries"))
        mass, mass_basis = mass_of(labels)
        rows.append({
            "node_id": cl_id, "node_key": C.build_node_key(cl_id, sp, ts, st, "unknown"),
            "kind": "library_class", "cl_id": cl_id, "cl_label": ont.label(cl_id),
            "obo_line": ont.trace_line(cl_id), "ontology_match_status": "mapped",
            "in_library": "yes", "in_cell_ranking": "yes", "stage": st, "stage_basis": basis,
            "species": sp, "species_basis": sp_basis, "tissue_context": ts, "tissue_basis": ts_basis,
            "tissue_candidates": ",".join(tis), "experimental_system": "unknown",
            "es_basis": "no_experimental_system_declaration_on_the_library_side",
            "our_labels": ",".join(labels), "n_our_labels": len(labels),
            "n_panel_genes": len(cl_genes[cl_id]), "panel_files": ",".join(sorted(cl_files[cl_id])),
            "library_ring": "A1", "anchor_role": "", "on_rpc_axis": "",
            "chain_to_anchor": "", "cell_mass_share_pct": mass, "cell_mass_basis": mass_basis})
    for label in sorted(nomatch):
        labels = [label]
        st, basis, _w = stage_of(None, label, labels)
        d = declarations(labels)
        sp = "human" if any(str(i["species"]) == "human" for _, i in d) else "unknown"
        sp_basis = (f"baseline:{d[0][0]}#species=human" if sp == "human" else "no_species_declaration")
        tis = sorted({f[:-5] for f, _ in d})
        ts = tis[0] if len(tis) == 1 else "unknown"
        ts_basis = ("baseline:" + d[0][0] + "#unique_declaring_entry" if len(tis) == 1
                    else ("no_baseline_declares_this_class" if not tis
                          else "multiple_declaring_entries"))
        mass, mass_basis = mass_of(labels)
        rows.append({
            "node_id": f"NO_MATCH:{label}", "node_key": C.build_node_key(f"NO_MATCH:{label}", sp, ts, st, "unknown"),
            "kind": "library_class", "cl_id": "", "cl_label": label,
            "obo_line": "", "ontology_match_status": "no_match",
            "in_library": "yes", "in_cell_ranking": "yes", "stage": st, "stage_basis": basis,
            "species": sp, "species_basis": sp_basis, "tissue_context": ts, "tissue_basis": ts_basis,
            "tissue_candidates": ",".join(tis), "experimental_system": "unknown",
            "es_basis": "no_experimental_system_declaration_on_the_library_side",
            "our_labels": label, "n_our_labels": 1,
            "n_panel_genes": len(panels.get(label, set())),
            "panel_files": ",".join(sorted(panel_files.get(label, set()))),
            "library_ring": "A2", "anchor_role": "", "on_rpc_axis": "",
            "chain_to_anchor": "", "cell_mass_share_pct": mass, "cell_mass_basis": mass_basis,
            "stage_note": ""})
    ring_a = len(rows)

    # ---- ring B: every CL term on a develops_from path out of a ring-A class, and out of an
    # origin anchor (so that no develops_from statement of a node in this graph is left dangling:
    # the hematopoietic stem cell anchor itself develops from two terms, measured).
    closure, b_origin = set(), {}
    def _closure(cid):
        seen, frontier = set(), [(p, 0) for p, _ln in ont.terms[cid].dev_lines]
        while frontier:
            x, d = frontier.pop()
            if x in seen:
                continue
            seen.add(x)
            for p, _ln in ont.terms[x].dev_lines if x in ont.terms else []:
                frontier.append((p, d + 1))
        return seen
    for cl_id in sorted(cl_labels):
        got = _closure(cl_id)
        closure |= got
        for t in got:
            b_origin.setdefault(t, "B1")
    anchor_ids = [a["cl_id"] for a in nav["germ_layer_anchors"] if a["cl_id"]]
    anchor_closure = set()
    for cid in anchor_ids:
        got = _closure(cid)
        closure |= got
        anchor_closure |= got
        for t in got:
            b_origin.setdefault(t, "B2")
    inter = sorted(closure - set(cl_labels) - set(anchor_ids))
    print(f"ring B ontology intermediates: {len(inter)} (develops_from closure of ring A and of the "
          f"anchors = {len(closure)} terms, {len(closure & set(cl_labels))} already ring-A nodes, "
          f"{len(anchor_closure)} reached from an anchor)")
    for cl_id in inter:
        st, basis, _w = stage_of(cl_id, "", [])
        rows.append({
            "node_id": cl_id, "node_key": C.build_node_key(cl_id, "unknown", "unknown", st, "unknown"),
            "kind": "ontology_intermediate", "cl_id": cl_id, "cl_label": ont.label(cl_id),
            "obo_line": ont.trace_line(cl_id), "ontology_match_status": "mapped",
            "in_library": "no", "in_cell_ranking": "no", "stage": st, "stage_basis": basis,
            "species": "unknown", "species_basis": "not_in_our_libraries_no_species_declared",
            "tissue_context": "unknown", "tissue_basis": "no_baseline_declares_this_class",
            "tissue_candidates": "", "experimental_system": "unknown",
            "es_basis": "not_in_our_libraries_no_es_declared",
            "our_labels": "", "n_our_labels": 0, "n_panel_genes": 0, "panel_files": "",
            "library_ring": b_origin.get(cl_id, "B1"), "anchor_role": "", "on_rpc_axis": "",
            "chain_to_anchor": "", "cell_mass_share_pct": "", "cell_mass_basis": "not_in_our_libraries",
            "stage_note": ""})

    # ---- ring C: the origin anchors the repository already resolved (ids read from the file)
    for a in nav["germ_layer_anchors"]:
        cid = a["cl_id"]
        if not cid:
            continue
        rows.append({
            "node_id": cid, "node_key": C.build_node_key(cid, "unknown", "unknown", "developing", "unknown"),
            "kind": "origin_anchor", "cl_id": cid, "cl_label": ont.label(cid),
            "obo_line": ont.trace_line(cid), "ontology_match_status": "mapped",
            "in_library": "no", "in_cell_ranking": "no", "stage": "developing",
            "stage_basis": f"ontology:{ont.trace_line(cid)}#anchor_role={a['key']}",
            "species": "unknown", "species_basis": "anchor_concept_no_species_declared",
            "tissue_context": "unknown", "tissue_basis": "anchor_concept_not_tissue_bound",
            "tissue_candidates": "", "experimental_system": "unknown",
            "es_basis": "anchor_concept_no_es_declared",
            "our_labels": "", "n_our_labels": 0, "n_panel_genes": 0, "panel_files": "",
            "library_ring": "C", "anchor_role": a["key"], "on_rpc_axis": "",
            "chain_to_anchor": "", "cell_mass_share_pct": "", "cell_mass_basis": "anchor_concept",
            "stage_note": ""})

    C.write_tsv(os.path.join(C.OUT, "SCAFFOLD_NODES.tsv"), rows, NODE_COLS)
    summ = {
        "generated_by": "scripts/s1_enum_nodes.py",
        "nodes": len(rows),
        "by_kind": C.counts(r["kind"] for r in rows),
        "by_ring": C.counts(r["library_ring"] for r in rows),
        "by_stage": C.counts(r["stage"] for r in rows),
        "by_stage_basis_prefix": C.counts(r["stage_basis"].split(":")[0] for r in rows),
        "by_species": C.counts(r["species"] for r in rows),
        "by_tissue_context": C.counts(r["tissue_context"] for r in rows),
        "library_concepts": len(lab),
        "library_concepts_mapped": sum(1 for r in lab.values() if r["cl_id"]),
        "library_concepts_no_match": sum(1 for r in lab.values() if not r["cl_id"]),
        "distinct_cl_ids_in_library": len(cl_labels),
        "ontology_intermediates": len(inter),
        "ontology_intermediates_from_anchors": sum(1 for r in rows if r["library_ring"] == "B2"),
        "origin_anchors": sum(1 for r in rows if r["kind"] == "origin_anchor"),
        "nodes_with_cell_mass": sum(1 for r in rows if r["cell_mass_share_pct"]),
        "develops_from_closure_size": len(closure),
        "closure_terms_already_library_classes": len(closure & set(cl_labels)),
        "adult_nodes_and_their_basis": {r["node_id"]: r["stage_basis"]
                                        for r in rows if r["stage"] == "adult"},
        "unknown_stage_nodes": sum(1 for r in rows if r["stage"] == "unknown"),
        "outputs": {"nodes": os.path.join(C.OUT, "SCAFFOLD_NODES.tsv")},
    }
    C.write_json(os.path.join(C.OUT, "NODES_SUMMARY.json"), summ)
    print(json.dumps({k: v for k, v in summ.items()
                      if k not in ("adult_nodes_and_their_basis",)}, ensure_ascii=False, indent=1)[:1800])
    return 0


if __name__ == "__main__":
    sys.exit(main())