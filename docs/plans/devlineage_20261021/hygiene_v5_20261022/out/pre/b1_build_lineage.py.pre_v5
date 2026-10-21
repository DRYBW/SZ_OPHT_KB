#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""b1_build_lineage.py - the developmental lineage layer, built only from local authority.

What the PI asked for: what the mesoderm becomes, what the ectoderm becomes, what the retinal
progenitor cell becomes - and the marker changes that come with each differentiation step.

Where every fact comes from (and nowhere else):
  ontology   the CL release named in out/ONT_NAV_v1.json: `develops_from` (RO:0002202) for the
             edges, `is_a` for germ-layer membership, every id carrying its file line
  library    kb/markers/*.json: the markers we already ship for a class
  corpus     /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10: whether a marker is
             actually stated by a paper we hold, with the paper id and section
  baseline   kb/baselines/*.json: the organism-stage axis, used to check that a developing node
             never sits in an adult baseline and vice versa

Three refusals, enforced by the gate rather than asserted here:
  * the evaluation volumes are NOT an input to this file (a separate, clearly-labelled,
    after-the-fact gap check reads them);
  * stage is never collapsed: every node declares organism_stage, and the gate cross-checks it
    against the repository's own adult/fetal baseline entries;
  * a marker transition is emitted with a corpus locator or it is emitted as `no_corpus_hit`.
    A gap that is counted is a result; a gap that is filled by assertion is not.

Outputs: LINEAGE_NODES.tsv, LINEAGE_EDGES.tsv, LINEAGE_GERM_LAYER.tsv,
         LINEAGE_MARKER_TRANSITIONS.tsv, LINEAGE_UNRESOLVED_DEVELOPMENT.tsv, LINEAGE_SUMMARY.json
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ont_nav import Ontology, DEVELOPS_FROM  # noqa: E402

BASELINE_DIR = "/mnt/D/EyeKB/kb/baselines"
PAPERS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10/papers.jsonl"
MIN_COOCCURRENCE_CHUNKS = 3          # below this a co-occurrence is not even listed as weak

# The word list is the one this repository already uses to tag developmental material
# (the corpus dev-stage tagger and the KB3 stage axis). Matched against the ontology label,
# the definition and our own label; the matched token is recorded so the call is auditable.
DEV_WORDS = ("progenitor", "precursor", "stem cell", "blast", "neuroepithel", "immature",
             "fetal", "embryonic", "transit amplifying", "transit-amplifying", "proliferat")
# Match the words as words. A substring rule would call `fibroblast` a developmental state
# (`blast`) and put a mature cell on the developing side of the axis.
DEV_PATTERNS = [(w, re.compile(r"(?<![a-z])" + w.replace(" ", r"\s+") + r"(?![a-z])"))
                for w in DEV_WORDS]

LIB_DIRS = ("/mnt/D/EyeKB/kb/markers", "/home/ubuntu/EYEKB_REPO/kb/markers")
LIB_FILES = ["markers_v4.1_clean.json", "markers_v5_retina_interneuron.json",
             "markers_v6_retina_repair.json", "markers_v6_face_increment.json",
             "markers_v6_lacrimal_increment.json", "markers_v7_panel_increment.json",
             "markers_k9_ocs_increment.json", "markers_membrane_v1.json",
             "markers_v8_dev_retina.json", "markers_v9_dev_retina.json",
             "markers_v10_antseg_increment.json", "markers_v11_lensiris_increment.json"]
NESTED = ("face_increment", "stromal_repair", "lacrimal_increment")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def load_panels():
    """label -> (genes, source file), plus label -> library."""
    panels, files = {}, {}
    for fname in LIB_FILES:
        path = next((os.path.join(d, fname) for d in LIB_DIRS
                     if os.path.isfile(os.path.join(d, fname))), None)
        if not path:
            continue
        payload = json.load(open(path, encoding="utf-8"))
        lib = fname.replace("markers_", "").replace(".json", "")
        ent = dict(payload.get("markers") or {})
        for k in NESTED:
            v = payload.get(k)
            if isinstance(v, dict):
                ent.update({kk: vv for kk, vv in v.items() if isinstance(vv, dict)})
        for e in (payload.get("entries") or []):
            if isinstance(e, dict) and e.get("class_name"):
                ent.setdefault(e["class_name"], e)
        for label, v in ent.items():
            genes = v if isinstance(v, list) else (v.get("markers") if isinstance(v, dict) else None)
            if genes:
                panels.setdefault(label, set()).update(str(g).upper() for g in genes)
                files.setdefault(label, set()).add(os.path.basename(path))
        for label in ent:
            files.setdefault(label, set()).add(os.path.basename(path))
    return panels, files


def load_baseline_adult_class_keys():
    """Structured class keys of every adult baseline entry in the repository."""
    keys = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(BASELINE_DIR, "*.json"))):
        if os.path.basename(p).startswith("_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        stage = str(d.get("development_stage") or d.get("organism_stage") or "")
        if "fetal" in os.path.basename(p) or "developing" in stage or stage == "fetal":
            continue
        pool = set()
        for field in ("donor_level_main", "pooled_adult_only_main",
                      "donor_level_adult_pool_contrast", "pooled_adult_pool_contrast"):
            v = d.get(field)
            if isinstance(v, dict):
                pool |= {str(k) for k in v}
        for mc in (d.get("major_classes") or []):
            if isinstance(mc, dict) and mc.get("class"):
                pool.add(str(mc["class"]))
        for st in (d.get("states") or []):
            if isinstance(st, dict) and st.get("cell_type"):
                pool.add(str(st["cell_type"]))
        if pool:
            keys[os.path.basename(p)] = pool
    return keys


def corpus_gene_index(path):
    idx = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            idx[r["gene"]] = r
    return idx


def main() -> int:
    nav = json.load(open(os.path.join(WAVE, "out", "ONT_NAV_v1.json"), encoding="utf-8"))
    ont = Ontology(nav["primary_path"])
    anchors = [(a["key"], a["cl_id"], a["queried_name"]) for a in nav["germ_layer_anchors"]
               if a["cl_id"]]

    def chain_ids(info):
        ids = list(info["chain"])
        if ids[-1] != info["layer_cl"]:
            ids.append(info["layer_cl"])
        return ids

    def chain_labels(ids):
        return " -> ".join(ont.label(i) or i for i in ids)

    # ---- label -> CL, with the panels our libraries ship ----
    lab2cl, lab_meta = {}, {}
    with open(os.path.join(WAVE, "out", "ONT_LABELMAP_V2.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            lab2cl[r["label"]] = r["cl_id"] or None
            lab_meta[r["label"]] = r
    panels, panel_files = load_panels()
    cl_panels = collections.defaultdict(set)
    cl_labels = collections.defaultdict(set)
    cl_files = collections.defaultdict(set)
    for lab, cid in lab2cl.items():
        if not cid:
            continue
        cl_labels[cid].add(lab)
        cl_panels[cid] |= panels.get(lab, set())
        cl_files[cid] |= panel_files.get(lab, set())

    # ---- nodes ----
    def stage_of(cid: str):
        """Stage of the node itself, decided by the ontology's own text for that term.

        Our library labels are deliberately NOT an input here: `RPE_fetal` is a state qualifier
        our sidecar already records separately, and letting it decide would move the whole node
        (the adult retinal pigment epithelial cell) onto the developing side of the axis.
        """
        t = ont.terms.get(cid)
        blob = " ".join([str(ont.label(cid) or ""), str(t.definition or "")]).lower()
        for w, pat in DEV_PATTERNS:
            if pat.search(blob):
                return "developing", w
        return "adult_or_unspecified", ""

    def our_label_stage_hints(cid: str):
        hits = []
        for lab in sorted(cl_labels.get(cid, [])):
            for w, pat in DEV_PATTERNS:
                if pat.search(lab.lower()):
                    hits.append(f"{lab}:{w}")
        return ",".join(hits)

    nodes = {}
    for cid in sorted(cl_labels):
        scope, tok = stage_of(cid)
        nodes[cid] = {"node_id": "CL:" + cid.split(":")[1], "kind": "library_class",
                      "cl_id": cid, "cl_label": ont.label(cid), "obo_line": ont.trace_line(cid),
                      "stage_scope": scope, "stage_token": tok,
                      "our_label_stage_hints": our_label_stage_hints(cid),
                      "our_labels": sorted(cl_labels[cid]), "n_panel_genes": len(cl_panels[cid]),
                      "panel_files": sorted(cl_files[cid])}
    for key, cid, name in anchors:
        nodes.setdefault(cid, {"node_id": "CL:" + cid.split(":")[1], "kind": "germ_layer",
                               "cl_id": cid, "cl_label": ont.label(cid),
                               "obo_line": ont.trace_line(cid), "stage_scope": "developing",
                               "stage_token": "germ layer anchor",
                               "our_label_stage_hints": "", "our_labels": [],
                               "n_panel_genes": 0, "panel_files": []})

    # ---- edges: develops_from, direct and through intermediates ----
    edges = []

    def chain_to_anchor(cid: str):
        """develops_from closure, then is_a bridging, to each germ anchor."""
        best = {}
        frontier = [(p, 1, [cid, p], [ln]) for p, ln in ont.terms[cid].dev_lines]
        seen = set()
        while frontier:
            p, d, path, lines = frontier.pop()
            if p in seen:
                continue
            seen.add(p)
            targets = [(p, [])] + [(a, [ln2]) for a, ln2 in ont.terms[p].is_a_lines] if p in ont.terms else [(p, [])]
            for tgt, extra in targets:
                for key, acid, _n in anchors:
                    if tgt == acid and key not in best:
                        best[key] = {"layer_cl": acid, "steps": d, "chain": path,
                                     "dev_lines": list(lines),
                                     "is_a_line": (extra[0] if extra else None)}
            if p in ont.terms:
                for q, ln in ont.terms[p].dev_lines:
                    frontier.append((q, d + 1, path + [q], lines + [ln]))
        return best

    for cid in sorted(cid for cid, n in nodes.items() if n["kind"] == "library_class"):
        for parent, ln in ont.terms[cid].dev_lines:
            if parent in nodes:
                edges.append({"child": cid, "parent": parent,
                              "relation_type": "develops_from_direct",
                              "evidence_kind": "ontology", "obo_lines": [ln],
                              "chain": [cid, parent], "steps": 1})
        # transitive bridges to a germ anchor when no direct edge reaches one
        reach = chain_to_anchor(cid)
        for key, info in sorted(reach.items()):
            if any(e["child"] == cid and nodes[e["parent"]]["kind"] == "germ_layer"
                   for e in edges):
                continue
            edges.append({"child": cid, "parent": info["layer_cl"],
                          "relation_type": "develops_from_transitive",
                          "evidence_kind": "ontology",
                          "obo_lines": info["dev_lines"] + ([info["is_a_line"]] if info["is_a_line"] else []),
                          "chain": chain_ids(info), "steps": info["steps"]})

    # ---- germ layer rows (ontology first, corpus co-occurrence second, else unresolved) ----
    cooc = collections.defaultdict(list)
    with open(os.path.join(WAVE, "out", "CORPUS_GERMLAYER_COOCCURRENCE.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            cooc[r["class_cl"]].append(r)
    germ_rows, unresolved_dev = [], []
    for cid in sorted(cid for cid, n in nodes.items() if n["kind"] == "library_class"):
        reach = chain_to_anchor(cid)
        rows_here = []
        for key, info in sorted(reach.items()):
            rows_here.append({"node_id": nodes[cid]["node_id"], "cl_id": cid,
                              "cl_label": ont.label(cid), "layer_key": key,
                              "layer_cl": info["layer_cl"],
                              "layer_label": ont.label(info["layer_cl"]),
                              "tier": "ontology_chain", "steps": info["steps"],
                              "ontology_chain": " -> ".join(chain_ids(info)),
                              "ontology_chain_labels": chain_labels(chain_ids(info)),
                              "ontology_lines": ",".join(str(x) for x in info["dev_lines"]),
                              "corpus_n_chunks": 0, "corpus_n_papers": 0,
                              "corpus_locators": "", "status": "supported_by_ontology"})
        if not rows_here:
            strong = [r for r in cooc.get(cid, []) if int(r["n_chunks"]) >= MIN_COOCCURRENCE_CHUNKS]
            strong.sort(key=lambda r: -int(r["n_chunks"]))
            # Keep only the two strongest candidate origins per class: a co-occurrence list is
            # noisy by construction (a chunk can mention a cell type and an unrelated germ layer
            # in the same paragraph), so the tail is measured but not carried into the graph.
            for r in strong[:2]:
                rows_here.append({"node_id": nodes[cid]["node_id"], "cl_id": cid,
                                  "cl_label": ont.label(cid), "layer_key": r["layer_key"],
                                  "layer_cl": r["layer_cl"],
                                  "layer_label": ont.label(r["layer_cl"]) or r["layer_key"],
                                  "tier": "corpus_cooccurrence_weak", "steps": "",
                                  "ontology_chain": "", "ontology_lines": "",
                                  "corpus_n_chunks": int(r["n_chunks"]),
                                  "corpus_n_papers": int(r["n_papers"]),
                                  "corpus_locators": r["example_locators"],
                                  "status": "weak_evidence_only"})
        if not rows_here:
            rows_here.append({"node_id": nodes[cid]["node_id"], "cl_id": cid,
                              "cl_label": ont.label(cid), "layer_key": "", "layer_cl": "",
                              "layer_label": "", "tier": "unresolved", "steps": "",
                              "ontology_chain": "", "ontology_lines": "", "corpus_n_chunks": 0,
                              "corpus_n_papers": 0, "corpus_locators": "",
                              "status": "no_local_evidence"})
            unresolved_dev.append({"cl_id": cid, "cl_label": ont.label(cid),
                                   "our_labels": ",".join(sorted(cl_labels[cid])),
                                   "reason": "the ontology carries no develops_from chain to a "
                                             "germ layer, and no corpus term co-occurrence "
                                             f"reaches {MIN_COOCCURRENCE_CHUNKS} chunks"})
        germ_rows.extend(rows_here)

    # ---- germ-layer membership as graph edges, so a reader sees the grouping in the graph too ----
    for r in germ_rows:
        if r["tier"] == "unresolved":
            continue
        edges.append({"child": r["cl_id"], "parent": r["layer_cl"],
                      "relation_type": "germ_layer_membership",
                      "evidence_kind": ("ontology" if r["tier"] == "ontology_chain"
                                        else "corpus_cooccurrence"),
                      "obo_lines": [int(x) for x in r["ontology_lines"].split(",") if x],
                      "chain": r["ontology_chain"].split(" -> ") if r["ontology_chain"] else
                               [r["cl_id"], r["layer_cl"]],
                      "steps": r["steps"] or "",
                      "tier": r["tier"],
                      "corpus_n_chunks": r["corpus_n_chunks"],
                      "corpus_n_papers": r["corpus_n_papers"],
                      "corpus_locators": r["corpus_locators"]})

    # ---- marker transitions along the direct steps ----
    gidx = corpus_gene_index(os.path.join(WAVE, "out", "CORPUS_GENE_INDEX.tsv"))
    marker_rows = []
    for i, e in enumerate(edges):
        e["edge_id"] = f"E{i + 1:03d}"
    for e in edges:
        child_genes, parent_genes = cl_panels.get(e["child"], set()), cl_panels.get(e["parent"], set())
        if e["relation_type"] == "germ_layer_membership":
            e["marker_transition_status"] = "not_applicable_membership"
            e["n_marker_rows"] = e["n_marker_corpus_supported"] = 0
            continue
        if e["relation_type"] != "develops_from_direct":
            e["marker_transition_status"] = "not_stepwise_relation"
            e["n_marker_rows"] = e["n_marker_corpus_supported"] = 0
            continue
        if not child_genes or not parent_genes:
            e["marker_transition_status"] = ("child_panel_absent" if not child_genes
                                             else "parent_panel_absent")
            e["n_marker_rows"] = e["n_marker_corpus_supported"] = 0
            continue
        gain, loss = sorted(child_genes - parent_genes), sorted(parent_genes - child_genes)
        n_sup, n_rows_edge = 0, 0
        for direction, genes in (("gain", gain), ("loss", loss)):
            for g in genes:
                rec = gidx.get(g)
                supported = bool(rec and int(rec["n_chunks"]) > 0)
                if supported:
                    n_sup += 1
                n_rows_edge += 1
                marker_rows.append({"edge_id": e["edge_id"], "direction": direction,
                                    "gene": g,
                                    "in_child_panel": "yes", "in_parent_panel": "yes" if g in parent_genes else "no",
                                    "corpus_n_chunks": int(rec["n_chunks"]) if rec else 0,
                                    "corpus_n_papers": int(rec["n_papers"]) if rec else 0,
                                    "corpus_locators": rec["example_locators"] if rec else "",
                                    "support_status": "corpus_supported" if supported else "no_corpus_hit"})
        e["n_marker_rows"] = n_rows_edge
        e["n_marker_corpus_supported"] = n_sup
        e["marker_transition_status"] = ("has_supported_transition" if n_sup
                                         else "no_supported_transition")

    # ---- write ----
    def write_tsv(name, rows, cols):
        p = os.path.join(WAVE, "out", name)
        with open(p, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore", restval="")
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {p}  ({len(rows)} rows)")
        return p

    # node-level roll-ups
    inbound = collections.Counter()
    for e in edges:
        inbound[e["child"]] += 1
    bl_keys = load_baseline_adult_class_keys()
    bl_all = {norm(k) for pool in bl_keys.values() for k in pool}
    node_rows = []
    for cid, n in sorted(nodes.items()):
        labels = set(n["our_labels"]) | ({n["cl_label"]} if n["cl_label"] else set())
        in_adult = sorted(l for l in labels if norm(l) in bl_all)
        node_rows.append({**n, "our_labels": ",".join(n["our_labels"]),
                          "panel_files": ",".join(n["panel_files"]),
                          "n_inbound_edges": inbound[cid],
                          "germ_layer_tiers": ";".join(
                              f"{r['layer_key']}={r['tier']}" for r in germ_rows
                              if r["cl_id"] == cid and r["tier"] != "unresolved"),
                          "in_adult_baseline_keys": ",".join(in_adult),
                          "root": "yes" if inbound[cid] == 0 else "no"})
    np_ = write_tsv("LINEAGE_NODES.tsv", node_rows,
                    ["node_id", "kind", "cl_id", "cl_label", "obo_line", "stage_scope",
                     "stage_token", "our_label_stage_hints", "our_labels", "n_panel_genes",
                     "panel_files", "n_inbound_edges", "germ_layer_tiers",
                     "in_adult_baseline_keys", "root"])
    edge_rows = []
    for e in edges:
        edge_rows.append({"edge_id": e["edge_id"], "child": e["child"], "parent": e["parent"],
                          "relation_type": e["relation_type"],
                          "tier": e.get("tier", ""),
                          "child_label": ont.label(e["child"]), "parent_label": ont.label(e["parent"]),
                          "chain": " -> ".join(e["chain"]), "steps": e["steps"],
                          "obo_lines": ",".join(str(x) for x in e["obo_lines"] if x),
                          "child_stage": nodes[e["child"]]["stage_scope"],
                          "parent_stage": nodes[e["parent"]]["stage_scope"],
                          "stage_crossing": "yes" if nodes[e["child"]]["stage_scope"]
                                            != nodes[e["parent"]]["stage_scope"] else "no",
                          "evidence_kind": e["evidence_kind"],
                          "corpus_n_chunks": e.get("corpus_n_chunks", ""),
                          "corpus_n_papers": e.get("corpus_n_papers", ""),
                          "corpus_locators": e.get("corpus_locators", ""),
                          "marker_transition_status": e.get("marker_transition_status", ""),
                          "n_marker_rows": e.get("n_marker_rows", 0),
                          "n_marker_corpus_supported": e.get("n_marker_corpus_supported", 0)})
    ep = write_tsv("LINEAGE_EDGES.tsv", edge_rows,
                   ["edge_id", "child", "parent", "relation_type", "tier", "child_label",
                    "parent_label", "chain", "steps", "obo_lines", "child_stage", "parent_stage",
                    "stage_crossing", "evidence_kind", "corpus_n_chunks", "corpus_n_papers",
                    "corpus_locators", "marker_transition_status", "n_marker_rows",
                    "n_marker_corpus_supported"])
    gp = write_tsv("LINEAGE_GERM_LAYER.tsv", germ_rows,
                   ["node_id", "cl_id", "cl_label", "layer_key", "layer_cl", "layer_label",
                    "tier", "steps", "ontology_chain", "ontology_chain_labels", "ontology_lines",
                    "corpus_n_chunks", "corpus_n_papers", "corpus_locators", "status"])
    mp = write_tsv("LINEAGE_MARKER_TRANSITIONS.tsv", marker_rows,
                   ["edge_id", "direction", "gene", "in_child_panel", "in_parent_panel",
                    "corpus_n_chunks", "corpus_n_papers", "corpus_locators", "support_status"])
    up = write_tsv("LINEAGE_UNRESOLVED_DEVELOPMENT.tsv", unresolved_dev,
                   ["cl_id", "cl_label", "our_labels", "reason"])

    tiers = collections.Counter(r["tier"] for r in germ_rows)
    edge_types = collections.Counter(e["relation_type"] for e in edges)
    mk = collections.Counter(r["support_status"] for r in marker_rows)
    summary = {
        "generated_by": "scripts/b1_build_lineage.py",
        "ontology": {"path": nav["primary_path"], "release": nav["primary"]["release"],
                     "sha256": nav["primary"]["sha256"]},
        "inputs": {"label_map": "out/ONT_LABELMAP_V2.tsv",
                   "panels": list(LIB_FILES), "corpus_gene_index": "out/CORPUS_GENE_INDEX.tsv",
                   "corpus_cooccurrence": "out/CORPUS_GERMLAYER_COOCCURRENCE.tsv",
                   "baselines_for_stage_check": sorted(bl_keys),
                   "evaluation_volumes_used": []},
        "nodes": len(node_rows), "roots": sum(1 for r in node_rows if r["root"] == "yes"),
        "roots_expected_from_disclosure":
            (sum(1 for r in node_rows if r["kind"] == "germ_layer") + len(unresolved_dev)),
        "library_class_nodes": sum(1 for r in node_rows if r["kind"] == "library_class"),
        "germ_layer_nodes": sum(1 for r in node_rows if r["kind"] == "germ_layer"),
        "edges": len(edge_rows), "edge_types": dict(edge_types),
        "germ_layer_tiers": dict(tiers),
        "unresolved_classes": len(unresolved_dev),
        "marker_rows": len(marker_rows), "marker_support": dict(mk),
        "edges_with_supported_transition": sum(
            1 for r in edge_rows if r["marker_transition_status"] == "has_supported_transition"),
        "edges_by_transition_status": dict(collections.Counter(
            r["marker_transition_status"] for r in edge_rows)),
        "stage_crossing_edges": sum(1 for r in edge_rows if r["stage_crossing"] == "yes"),
        "developing_nodes_in_adult_baseline": sorted(
            r["cl_id"] for r in node_rows
            if r["stage_scope"] == "developing" and r["in_adult_baseline_keys"]),
        "files": {"nodes": np_, "edges": ep, "germ_layer": gp, "marker_transitions": mp,
                  "unresolved": up},
    }
    sp = os.path.join(WAVE, "out", "LINEAGE_SUMMARY.json")
    json.dump(summary, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote {sp}")

    print("\n=== lineage at a glance ===")
    print(f"  nodes {summary['nodes']} (library classes {summary['library_class_nodes']}, "
          f"germ layers {summary['germ_layer_nodes']}), roots {summary['roots']}")
    print(f"  edges {summary['edges']} {dict(edge_types)}")
    print(f"  germ-layer rows: {dict(tiers)}")
    print(f"  marker rows {len(marker_rows)} {dict(mk)}")
    print(f"  edges with at least one corpus-supported transition: "
          f"{summary['edges_with_supported_transition']}")
    print(f"  classes with no developmental evidence locally: {len(unresolved_dev)}")
    print(f"  developing nodes found in an adult baseline: "
          f"{summary['developing_nodes_in_adult_baseline']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())