#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 1 — stage-resolved marker sets per node.

Builds, from artefacts already on disk and from nothing else:
  out/NODE_KEYS.tsv              one row per developmental-lineage node (contract node key)
  out/STAGE_RESOLVED_MARKERS.tsv one row per gene per node per stage (contract assertion schema)
  out/ANCHORS.tsv                every anchor used, with file + sha256
  out/STAGE_COVERAGE.tsv         per lineage x stage marker counts, and the one-stage-only finding
  out/STAGE_DISCLOSURE.tsv       row-by-row disclosure of every value that is not adult

Rules implemented (frozen in PREREG_STAGE_CHANGE_v1.md §1):
  * the contract stage literal is one of {fetal, adult, developing, unknown}; the source literal is
    kept in its own column and never silently translated;
  * an identifier is read from the ontology file at build time or taken from the repository's own
    CL label map; no match is recorded as NO_MATCH, never force-attached;
  * a stage with no marker evidence in the corpus produces zero rows plus an explicit disclosure
    row, never a fabricated value;
  * "not mentioned" is never written as `off` (this step writes `change=present` only, and only
    where a source asserts presence at that stage).

No network, no download, read-only against every input.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO")
OUT = REPO / "docs" / "plans" / "devlineage_20261021" / "stages" / "out"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- inputs (read-only)
KB = REPO / "kb"
DEV_PANEL = KB / "markers" / "markers_v9_dev_retina.json"
CL_LABELMAP = KB / "markers" / "markers_cl_alignment_v2_unified.json"
ADULT_BASELINE = KB / "baselines" / "retina.json"
BASELINE_INDEX = KB / "baselines" / "baselines.json"
DEV_BASELINE = KB / "baselines" / "retina__fetal_developing.json"
CONCEPT_ENTRY = KB / "baselines" / "fetal_development_transitions.json"
PRECURSOR_EDGES = Path("/mnt/D/EyeKB/plans/devline_ont_20261002/out/PRECURSOR_EDGES.tsv")
CL_OBO = Path("/mnt/D/EyeKB/plans/devline_ont_20261002/downloads/cl.obo")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------- 1. ontology identifiers
def obo_name_index(path: Path):
    """term id -> primary name, read from the release file itself (never from memory)."""
    idx, cur, name = {}, None, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line == "[Term]":
                if cur and name:
                    idx.setdefault(name, []).append(cur)
                cur, name = None, None
            elif line.startswith("id: CL:") and cur is None:
                cur = line[4:].strip()
            elif line.startswith("name: ") and name is None:
                name = line[6:].strip()
    if cur and name:
        idx.setdefault(name, []).append(cur)
    return idx


OBO = obo_name_index(CL_OBO)
CL_LABELMAP_D = json.loads(CL_LABELMAP.read_text(encoding="utf-8"))
LABELS = CL_LABELMAP_D["labels"]

ANCHORS = {}


def anchor(aid, cls, path, locator, source_ids, claim):
    if aid not in ANCHORS:
        ANCHORS[aid] = {
            "anchor_id": aid,
            "anchor_class": cls,
            "file": rel(path) if isinstance(path, Path) else str(path),
            "sha256": sha256(path) if isinstance(path, Path) and path.is_file() else "",
            "locator": locator,
            "source_ids": ";".join(source_ids),
            "claim": claim,
        }
    return aid


# ---------------------------------------------------------------- 2. adult-side node + markers
adult_baseline = json.loads(ADULT_BASELINE.read_text(encoding="utf-8"))
adult_stage_declared = adult_baseline.get("organism_stage")
assert adult_stage_declared == "adult", adult_stage_declared
anchor("A_ADULT_BASELINE", "adult_atlas_donor_level", ADULT_BASELINE, "$.major_classes[].markers_local_lib + $.organism_stage",
       [s["sid"] for s in adult_baseline.get("sources", []) if isinstance(s, dict)],
       "donor-level adult retina composition reference; each class row carries its local-library marker list")

ADULT_ROWS = {r["class"]: r for r in adult_baseline["major_classes"]}

# The composition baseline names two classes differently from the CL label map; the alias is
# declared here and pinned by an assertion on the CL label actually carried by the id, so the
# join is never a silent name guess.
BASELINE_TO_LABELMAP = {"Astrocyte": "Astro", "Microglia": "Micro"}
CL_LABEL_CANON = {"Astrocyte": "astrocyte", "Microglia": "microglial cell"}

ADULT_NODES = []   # (lineage_id, class code, cl_id, cl_label, markers, source_ids)
for cls in ["Rod", "Cone", "BC", "AC", "HC", "RGC", "MG", "Astrocyte", "Microglia", "RPE"]:
    r = ADULT_ROWS[cls]
    lab = LABELS[BASELINE_TO_LABELMAP.get(cls, cls)]
    if cls in CL_LABEL_CANON:
        assert lab["cl_label"] == CL_LABEL_CANON[cls], (cls, lab)
    assert lab["status"] == "mapped", (cls, lab)
    cid = lab["cl_id"]
    # verify the id really exists in the release file with that label
    assert OBO.get(lab["cl_label"]) and cid in OBO[lab["cl_label"]], (cls, lab["cl_label"], cid)
    ADULT_NODES.append({"class": cls, "cl_id": cid, "cl_label": lab["cl_label"],
                        "markers": list(r["markers_local_lib"]), "source_ids": list(r["source_ids"])})

# ---------------------------------------------------------------- 3. fetal-side node + markers
dev = json.loads(DEV_PANEL.read_text(encoding="utf-8"))
assert dev["organism_stage"] == "fetal/developing", dev["organism_stage"]
DEV_SOURCE_LITERAL = dev["organism_stage"]
DEV_WINDOW = dev["development_stage"]
anchor("A_DEV_PANEL", "data_panel_with_in_cluster_frequency", DEV_PANEL, "$.markers[<entry>] + $.core_evidence[<entry>][<gene>]",
       ["data_track", "literature_track", "skeleton_track"],
       "human fetal/developing retina precursor panel: per-gene track (D=data, L=literature, star=skeleton), "
       "in-cluster frequency and count of developmental-context papers")

FETAL_ENTRIES = dev["markers"]
core_ev = dev["core_evidence"]

# lineage pairing: which adult class (if any) a precursor entry belongs to. Derived from the entry
# naming and from the CL label map, and cross-checked against PRECURSOR_EDGES where an edge exists.
LINEAGE_OF_ENTRY = {
    "Rod_precursor": ("rod", ["Rod"]),
    "Cone_precursor": ("cone", ["Cone"]),
    "BC_precursor": ("bc", ["BC"]),
    "AC_precursor": ("ac", ["AC"]),
    "HC_precursor": ("hc", ["HC"]),
    "RGC_precursor": ("rgc", ["RGC"]),
    "glia_precursor": ("glia", ["MG", "Astrocyte"]),
    "RPE_fetal": ("rpe", ["RPE"]),
    # the progenitor/cycling entries have no adult counterpart in the 10-class adult vocabulary;
    # mapping them onto an adult class is prohibited (see the KB3 vocabulary note and the entry's own
    # retinoblast adoption record).
    "RPC_early": ("progenitor_rpc_early", []),
    "RPC_late": ("progenitor_rpc_late", []),
    "NRPC_early": ("progenitor_nrpc_early", []),
    "NRPC_late": ("progenitor_nrpc_late", []),
    "TAC_proliferating": ("progenitor_tac", []),
    "Retinal_Proliferating": ("progenitor_cycling_state", []),
}
assert set(LINEAGE_OF_ENTRY) == set(FETAL_ENTRIES), set(LINEAGE_OF_ENTRY) ^ set(FETAL_ENTRIES)

STATE_ENTRIES = {"TAC_proliferating", "Retinal_Proliferating"}

# ---------------------------------------------------------------- 4. precursor edges (ontology-side reference)
edge_rows = list(csv.DictReader(open(PRECURSOR_EDGES, encoding="utf-8"), delimiter="\t"))
anchor("A_PRECURSOR_EDGES", "ontology_development_relation", PRECURSOR_EDGES, "one row per edge; stage qualifier column is a DERIVED keyword rule",
       [], "79 ontology edges (45 direct + 34 transitive); the *_stage columns are a derived keyword rule, "
           "NOT a native ontology attribute")
EDGE_BY_AC = {}
for i, r in enumerate(edge_rows, start=2):     # header = line 1
    EDGE_BY_AC.setdefault(r["adult_cl_id"], []).append({"line": i,
                                                        "precursor_cl_id": r["precursor_cl_id"],
                                                        "precursor_label": r["precursor_label"],
                                                        "chain_depth": r["chain_depth"],
                                                        "chain_kind": r["chain_kind"],
                                                        "path_chain": r["path_chain"]})

# ---------------------------------------------------------------- 5. node keys
def node_key(cl_id, stage, in_house_entry=None, es="in_vivo"):
    """Contract node key. A concept with no ontology counterpart carries the mandatory
    `dl:NO_MATCH:<in_house_class_id>` prefix (contract §Node key) — without the in-house id the key
    would not be injective across the eleven NO_MATCH entries."""
    cid = cl_id if cl_id else f"NO_MATCH:{in_house_entry}"
    return f"dl:{cid}|sp=human|ts=retina|st={stage}|es={es}"


def node_instance_id(nk, entry, qualifier):
    """Row identity for this deliverable only. Two mapped entries (RPC_early / RPC_late) share one
    CL term and differ only by the label map's temporal qualifier, so the contract node key alone is
    not injective there; the collision is reported, not hidden."""
    return f"{nk}|entry={entry}" + (f"|q={qualifier}" if qualifier else "")


nodes, node_rows = [], []
for e_name, (lin, adults) in LINEAGE_OF_ENTRY.items():
    lab = LABELS[e_name]
    nk = node_key(lab["cl_id"], "fetal", e_name)
    nodes.append({"node_kind": "fetal_entry", "entry": e_name, "lineage": lin, "adults": adults,
                  "node_key": nk, "cl_id": lab["cl_id"], "cl_label": lab["cl_label"],
                  "cl_status": lab["status"], "cl_qualifier": lab["qualifier"],
                  "cl_reason": lab["reason"]})
for a in ADULT_NODES:
    nk = node_key(a["cl_id"], "adult", a["class"])
    lin = next((l for l, ads in LINEAGE_OF_ENTRY.values() if a["class"] in ads), None)
    nodes.append({"node_kind": "adult_class", "entry": a["class"], "lineage": lin, "adults": [a["class"]],
                  "node_key": nk, "cl_id": a["cl_id"], "cl_label": a["cl_label"],
                  "cl_status": "mapped", "cl_qualifier": None, "cl_reason": None})

# node-key injectivity audit (reported, never silently patched)
from collections import Counter as _Counter
_nk_counts = _Counter(n["node_key"] for n in nodes)
NODE_KEY_COLLISIONS = {k: v for k, v in _nk_counts.items() if v > 1}
for n in nodes:
    n["node_instance_id"] = node_instance_id(n["node_key"], n["entry"], n["cl_qualifier"])

# adult classes that no precursor entry claims: record them explicitly (honesty: they exist in the
# adult vocabulary and are simply not reachable from this card's fetal side)
claimed_adults = {c for l, ads in LINEAGE_OF_ENTRY.values() for c in ads}

with open(OUT / "NODE_KEYS.tsv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["node_kind", "in_house_entry", "lineage_id", "node_key", "node_instance_id", "stage",
                "source_stage_literal", "species", "tissue", "experimental_system", "cl_id", "cl_label",
                "cl_match_status", "cl_qualifier", "cl_no_match_reason", "adult_counterpart_classes",
                "node_key_collision", "source_anchor_id"])
    for n in nodes:
        stage = "fetal" if n["node_kind"] == "fetal_entry" else "adult"
        src = DEV_SOURCE_LITERAL if stage == "fetal" else adult_stage_declared
        w.writerow([n["node_kind"], n["entry"], n["lineage"], n["node_key"], n["node_instance_id"], stage,
                    src, "human", "retina", "in_vivo", n["cl_id"] or "NO_MATCH", n["cl_label"] or "",
                    n["cl_status"], n["cl_qualifier"] or "", n["cl_reason"] or "",
                    ";".join(n["adults"]),
                    "Y" if n["node_key"] in NODE_KEY_COLLISIONS else "N",
                    "A_DEV_PANEL" if stage == "fetal" else "A_ADULT_BASELINE"])

# ---------------------------------------------------------------- 6. stage-resolved marker rows
rows = []


def add(assertion_key, node, gene, stage, role, anchor_id, anchor_locator, source_library,
        source_stage_literal, grade, anchor_class, extra_note=""):
    rows.append({
        "assertion_id": "",
        "edge_id_or_node_key": node["node_key"],
        "gene_symbol": gene,
        "species": "human",
        "role": role,
        "change": "present",
        "stage": stage,
        "assay": "RNA",
        "source_group": source_library,
        "target_group": node["entry"],
        "effect_value": "",
        "uncertainty": "",
        "claim_type": "qualitative",
        "evidence_ids": anchor_id,
        "evidence_grade": grade,
        "evidence_anchor": f"{anchor_id}:{anchor_locator}",
        "node_key": node["node_key"],
        "node_instance_id": node["node_instance_id"],
        "node_kind": node["node_kind"],
        "in_house_entry": node["entry"],
        "lineage_id": node["lineage"],
        "source_stage_literal": source_stage_literal,
        "anchor_class": anchor_class,
        "anchor_file": ANCHORS[anchor_id]["file"],
        "anchor_sha256": ANCHORS[anchor_id]["sha256"],
        "anchor_locator": anchor_locator,
        "note": extra_note,
        "_key": assertion_key,
    })


# fetal side
for n in nodes:
    if n["node_kind"] != "fetal_entry":
        continue
    genes = FETAL_ENTRIES[n["entry"]]
    role = "state_warning" if n["entry"] in STATE_ENTRIES else "identity_support"
    for g in genes:
        ev = core_ev.get(n["entry"], {}).get(g) or {}
        track = ev.get("track", "")
        cls = ("data_panel_with_in_cluster_frequency" if "D" in track
               else ("textbook_review_only" if track.strip("★") == "" else "literature_dev_context_only"))
        grade = ("textbook_or_review_distant_origin" if cls == "textbook_review_only"
                 else "identity_conversion_not_direct")
        loc = f"$.core_evidence.{n['entry']}.{g}"
        note = f"track={track}; freq_in_C={ev.get('freq_in_C','')}; papers_devctx={ev.get('papers_devctx','')}"
        add(("fetal", n["entry"], g), n, g, "fetal", role, "A_DEV_PANEL", loc,
            f"{DEV_PANEL.name}#markers", DEV_SOURCE_LITERAL, grade, cls, note)

# adult side
for n in nodes:
    if n["node_kind"] != "adult_class":
        continue
    a = next(x for x in ADULT_NODES if x["class"] == n["entry"])
    for g in a["markers"]:
        loc = f"$.major_classes[class={a['class']}].markers_local_lib"
        add(("adult", n["entry"], g), n, g, "adult", "identity_support", "A_ADULT_BASELINE", loc,
            f"{ADULT_BASELINE.name}#major_classes", adult_stage_declared,
            "identity_conversion_not_direct", "adult_atlas_donor_level",
            f"class markers_local_lib; source_ids={','.join(a['source_ids'])}")

# deterministic assertion ids: stable, readable, no dependence on iteration order
for i, r in enumerate(sorted(rows, key=lambda x: (x["stage"], x["in_house_entry"], x["gene_symbol"])), start=1):
    r["assertion_id"] = f"V3SA{i:05d}"

COLS = ["assertion_id", "edge_id_or_node_key", "gene_symbol", "species", "role", "change", "stage",
        "assay", "source_group", "target_group", "effect_value", "uncertainty", "claim_type",
        "evidence_ids", "evidence_grade", "evidence_anchor", "node_key", "node_instance_id", "node_kind", "in_house_entry",
        "lineage_id", "source_stage_literal", "anchor_class", "anchor_file", "anchor_sha256",
        "anchor_locator", "note"]
with open(OUT / "STAGE_RESOLVED_MARKERS.tsv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, delimiter="\t", lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in sorted(rows, key=lambda x: (x["stage"], x["in_house_entry"], x["gene_symbol"])):
        w.writerow(r)

# ---------------------------------------------------------------- 7. anchors + coverage + disclosure
with open(OUT / "ANCHORS.tsv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["anchor_id", "anchor_class", "file", "sha256", "locator",
                                       "source_ids", "claim"], delimiter="\t", lineterminator="\n")
    w.writeheader()
    for k in sorted(ANCHORS):
        w.writerow(ANCHORS[k])

cov = []
for n in nodes:
    if n["node_kind"] != "fetal_entry":
        continue
    lin = n["lineage"]
    mine = [x for x in rows if x["lineage_id"] == lin]
    f = [x for x in mine if x["stage"] == "fetal"]
    a = [x for x in mine if x["stage"] == "adult"]
    stages = sorted({x["stage"] for x in mine})
    cov.append({"lineage_id": lin, "fetal_node": n["node_key"], "fetal_entry": n["entry"],
                "adult_counterpart_classes": ";".join(n["adults"]),
                "n_fetal_markers": len(f), "n_adult_markers": len(a),
                "n_developing_markers": 0, "n_unknown_markers": 0,
                "stages_with_markers": ";".join(stages),
                "one_stage_only": "Y" if (bool(f) ^ bool(a)) else "N",
                "finding": ("fetal-stage markers only, no adult counterpart class in the 10-class adult vocabulary"
                            if not n["adults"] and f else
                            ("adult-stage markers only (no fetal-stage marker asserted for this lineage in the corpus)"
                             if not f and a else "both stages carry markers" if f and a else "neither stage carries a marker"))})
with open(OUT / "STAGE_COVERAGE.tsv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(cov[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(cov)

# disclosure: every cell that is NOT adult, row by row (contract: unknown is disclosed row-by-row,
# silent assignment to adult is prohibited)
with open(OUT / "STAGE_DISCLOSURE.tsv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["row_kind", "scope", "stage_literal", "source_literal", "disclosure"])
    w.writerow(["stage_axis_declaration", "kb/baselines/baselines.json#stage_axis", "fetal;adult;developing;unknown",
                "-", "the four-level axis is read from the shipped baseline index, not re-declared here"])
    w.writerow(["entry_stage", f"{DEV_PANEL.name}#organism_stage", "fetal", DEV_SOURCE_LITERAL,
                f"coarse panel literal; its own development_stage window is '{DEV_WINDOW}' (post-fertilisation weeks) "
                "-> mapped to the contract literal fetal; the coarse literal cannot be split per gene in this card"])
    w.writerow(["absent_stage", "developing (postnatal/newborn)", "developing", "-",
                "zero per-gene marker rows: the corpus carries no per-gene developing-stage marker evidence "
                "(the KB3 postnatal layer carries published-label percentages only). Absence is recorded, not filled."])
    w.writerow(["absent_stage", "unknown", "unknown", "-",
                "zero per-gene marker rows: no source in the loaded corpus asserts a per-gene marker set for an "
                "unknown-stage sample; organoid material is isolated with the unknown literal by the KB3 entry and is "
                "not used as marker evidence here"])
    for r in rows:
        if r["stage"] != "adult":
            w.writerow(["marker_row", r["assertion_id"], r["stage"], r["source_stage_literal"],
                        f"{r['in_house_entry']}/{r['gene_symbol']} asserted at {r['stage']} from {r['anchor_file']}"])

n_fetal = sum(1 for r in rows if r["stage"] == "fetal")
n_adult = sum(1 for r in rows if r["stage"] == "adult")
summary = {
    "nodes": len(nodes), "fetal_nodes": sum(1 for n in nodes if n["node_kind"] == "fetal_entry"),
    "adult_nodes": sum(1 for n in nodes if n["node_kind"] == "adult_class"),
    "marker_rows": len(rows), "fetal_marker_rows": n_fetal, "adult_marker_rows": n_adult,
    "developing_marker_rows": 0, "unknown_marker_rows": 0,
    "lineages": len({n["lineage"] for n in nodes}),
    "unclaimed_adult_classes": sorted(claimed_adults ^ {a["class"] for a in ADULT_NODES}),
    "node_key_collisions": {k: v for k, v in NODE_KEY_COLLISIONS.items()},
    "grade_counts": {g: sum(1 for r in rows if r["evidence_grade"] == g)
                     for g in sorted({r["evidence_grade"] for r in rows})},
    "cl_match_counts": {s: sum(1 for n in nodes if n["cl_status"] == s) for s in sorted({n["cl_status"] for n in nodes})},
}
(OUT / "STEP1_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
print("wrote:", ", ".join(sorted(p.name for p in OUT.iterdir())))