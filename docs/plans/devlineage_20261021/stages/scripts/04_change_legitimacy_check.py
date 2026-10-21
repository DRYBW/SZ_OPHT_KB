#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3 stage axis / step 4 — the change-legitimacy check.

Generates the candidate changes that the locally available materials tempt a reader to write, then
enforces the rule table frozen in PREREG_STAGE_CHANGE_v1.md §3 and reports what it rejected and why.

Rules with no real candidate in this corpus are exercised with explicitly labelled fixture rows,
reported separately and never counted among the real candidates.

Outputs:
  out/CANDIDATE_CHANGES.tsv       every generated candidate (real + fixture), with its columns
  out/CHANGE_REJECTION_LEDGER.tsv one row per rejected candidate with the rules it broke and why
  out/CHANGE_ADMITTED.tsv         the admitted set (header only when the set is empty — reported as such)
  out/RULE_REGISTRY.tsv           the rule table as code, with the count each rule rejected
  out/CHANGE_CHECK_SUMMARY.json   counts
"""
import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = Path("/home/ubuntu/EYEKB_REPO")
OUT = HERE / "out"
KB = REPO / "kb"

GRADES = {"direct_lineage_support", "identity_conversion_not_direct",
          "textbook_or_review_distant_origin", "trajectory_only"}
STAGES = {"fetal", "adult", "developing", "unknown"}

RULES = [
    ("R1", "anchor", "the row carries no evidence anchor, or the anchor file is not on disk"),
    ("R2", "stage provenance", "the stage value comes from a derived keyword column, not from a source that observed the stage"),
    ("R3", "single source", "the two sides of the change come from two different studies/sources (snapshot differ)"),
    ("R4", "species", "the two sides are from different species"),
    ("R5", "assay", "the two sides are from different assays"),
    ("R6", "condition", "the two sides are from different conditions/experimental systems"),
    ("R7", "step count", "the direction would be propagated along a lineage of more than one step"),
    ("R8", "identity / time direction", "start or end identity, or the time direction, is not asserted by the source itself"),
    ("R9", "grade", "the evidence grade is missing or outside the contract's four values"),
    ("R10", "off semantics", "the change is `off` while the source only fails to mention the gene"),
    ("R11", "numeric", "a numeric effect value with no traceable extraction record"),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load():
    markers = list(csv.DictReader(open(OUT / "STAGE_RESOLVED_MARKERS.tsv", encoding="utf-8"), delimiter="\t"))
    nodes = list(csv.DictReader(open(OUT / "NODE_KEYS.tsv", encoding="utf-8"), delimiter="\t"))
    edges = list(csv.DictReader(open("/mnt/D/EyeKB/plans/devline_ont_20261002/out/PRECURSOR_EDGES.tsv",
                                     encoding="utf-8"), delimiter="\t"))
    return markers, nodes, edges


def mouse_labeled_genes():
    """Genes with a structured mouse-labeled evidence node in the shipped marker libraries.

    Only structured `"species": "mouse"` fields are used — free-text mentions of the word mouse are
    deliberately not harvested, so the cross-species family is built from machine-readable evidence.
    """
    out = {}
    for p in sorted((KB / "markers").glob("markers_*.json")):
        try:
            s = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in re.finditer(r'"gene"\s*:\s*"([A-Za-z0-9\-\.]+)"', s):
            gene = m.group(1).upper()
            seg = s[m.end():m.end() + 900]
            if re.search(r'"species"\s*:\s*"mouse"', seg):
                out.setdefault(gene, set()).add(p.name)
    return {g: sorted(v) for g, v in out.items()}


def main():
    markers, nodes, edges = load()
    node_of = {n["in_house_entry"]: n for n in nodes}
    adj = {n["lineage_id"]: n for n in nodes if n["node_kind"] == "fetal_entry"}

    fetal = {}
    adult = {}
    for r in markers:
        (fetal if r["stage"] == "fetal" else adult).setdefault(r["lineage_id"], {})[r["gene_symbol"]] = r

    edge_by_ac = {}
    for i, e in enumerate(edges, start=2):
        edge_by_ac.setdefault(e["adult_cl_id"], []).append((i, e))
    clid_of_class = {n["in_house_entry"]: n["cl_id"] for n in nodes if n["node_kind"] == "adult_class"}

    dev = json.loads((KB / "markers" / "markers_v9_dev_retina.json").read_text(encoding="utf-8"))
    dev_bl = json.loads((KB / "baselines" / "retina__fetal_developing.json").read_text(encoding="utf-8"))
    dev_f = json.loads((KB / "baselines" / "fetal_development_transitions.json").read_text(encoding="utf-8"))
    adult_bl = json.loads((KB / "baselines" / "retina.json").read_text(encoding="utf-8"))
    mouse_genes = mouse_labeled_genes()

    DEV_FILE = "kb/markers/markers_v9_dev_retina.json"
    ADULT_FILE = "kb/baselines/retina.json"

    def edge_ref_for(lin):
        """Reference to the ontology row that declares this pair, if any. The scaffold workstream
        owns edge ids; this card references the on-disk row by precursor->descendant and relation."""
        node = adj.get(lin)
        if not node or not node["adult_counterpart_classes"]:
            return "", "", "", ""
        ac = node["adult_counterpart_classes"].split(";")[0]
        cid = clid_of_class.get(ac, "")
        for line, e in edge_by_ac.get(cid, []):
            if e["precursor_cl_id"] == (node["cl_id"] or ""):
                return (f"PRECURSOR_EDGES.tsv:{line}|{e['precursor_cl_id']}->{e['adult_cl_id']}"
                        f"|rel=ontology_development_relation",
                        node["node_key"], node_of[ac]["node_key"], str(e["chain_depth"]))
        return "", node["node_key"], node_of[ac]["node_key"] if ac in node_of else "", ""

    cands = []

    def add(**kw):
        kw.setdefault("fixture", "N")
        kw.setdefault("stage_provenance", "source_observed")
        kw.setdefault("identity_direction_asserted", "N")
        kw.setdefault("n_steps", 1)
        kw.setdefault("assay_from", "RNA")
        kw.setdefault("assay_to", "RNA")
        kw.setdefault("condition_from", kw.get("source_from", ""))
        kw.setdefault("condition_to", kw.get("source_to", ""))
        kw.setdefault("species_from", "human")
        kw.setdefault("species_to", "human")
        kw.setdefault("effect_value", "")
        kw.setdefault("extraction_record", "")
        kw.setdefault("evidence_grade", "identity_conversion_not_direct")
        kw.setdefault("notes", "")
        cands.append(kw)

    # ---- family 1: within-lineage snapshot differ (fetal panel vs adult atlas)
    for lin, fg in fetal.items():
        ag = adult.get(lin, {})
        eref, pn, dn, depth = edge_ref_for(lin)
        only_f = sorted(set(fg) - set(ag))
        only_a = sorted(set(ag) - set(fg))
        for g in only_f:
            add(family="cross_source_snapshot_differ", lineage_id=lin, edge_ref=eref,
                precursor_node=pn, descendant_node=dn, gene_symbol=g, stage_from="fetal", stage_to="adult",
                change="off", source_from=DEV_FILE, source_to=ADULT_FILE,
                evidence_anchor=f"{DEV_FILE}#markers.{adj[lin]['in_house_entry']}",
                notes="gene asserted at fetal; absent from the adult class's list -> tempts `off in adult`")
        for g in only_a:
            add(family="cross_source_snapshot_differ", lineage_id=lin, edge_ref=eref,
                precursor_node=pn, descendant_node=dn, gene_symbol=g, stage_from="fetal", stage_to="adult",
                change="on", source_from=DEV_FILE, source_to=ADULT_FILE,
                evidence_anchor=f"{ADULT_FILE}#major_classes",
                notes="gene asserted at adult; absent from the fetal entry -> tempts `on in adult`")

    # ---- family 2: cross-entry composition differ (fetal portal labels vs adult donor-level)
    for lin, fg in fetal.items():
        n = adj.get(lin)
        if not n or not n["adult_counterpart_classes"]:
            continue
        cls = n["adult_counterpart_classes"].split(";")[0]
        if cls not in {r["class"] for r in adult_bl["major_classes"]}:
            continue
        add(family="cross_entry_composition_differ", lineage_id=lin, edge_ref="",
            precursor_node=n["node_key"], descendant_node=node_of[cls]["node_key"], gene_symbol="",
            stage_from="fetal", stage_to="adult", change="transient",
            source_from="kb/baselines/retina__fetal_developing.json#portal_majorclass_reference",
            source_to="kb/baselines/retina.json#major_classes",
            evidence_anchor="kb/baselines/retina__fetal_developing.json#portal_majorclass_reference",
            notes=("the two label histograms use different vocabularies (portal PRPC/Rod vs the adult class "
                   "vocabulary) and different studies; the KB3 entry forbids mapping one into the other"))

    # ---- family 3: multi-step propagation along the ontology chain
    for lin, fg in fetal.items():
        n = adj.get(lin)
        if not n or not n["adult_counterpart_classes"]:
            continue
        cls = n["adult_counterpart_classes"].split(";")[0]
        cid = clid_of_class.get(cls, "")
        for line, e in edge_by_ac.get(cid, []):
            if int(e["chain_depth"]) > 1:
                add(family="multistep_propagation", lineage_id=lin,
                    edge_ref=f"PRECURSOR_EDGES.tsv:{line}|{e['precursor_cl_id']}->{e['adult_cl_id']}",
                    precursor_node=n["node_key"], descendant_node=node_of[cls]["node_key"], gene_symbol="",
                    stage_from="fetal", stage_to="adult", change="up",
                    source_from=DEV_FILE, source_to=ADULT_FILE,
                    evidence_anchor=f"{DEV_FILE}#markers", n_steps=int(e["chain_depth"]),
                    notes=f"chain_depth={e['chain_depth']} ({e['chain_kind']}): direction would have to travel "
                          "more than one step")

    # ---- family 4: cross-species stitch (a human stage on one side, mouse-labeled evidence on the other)
    for side_name, side_map in (("fetal", fetal), ("adult", adult)):
        for lin, sg in side_map.items():
            for g, rec in sorted(sg.items()):
                if g in mouse_genes:
                    add(family="cross_species_stitch", lineage_id=lin, edge_ref="",
                        precursor_node=rec["node_key"], descendant_node="", gene_symbol=g,
                        stage_from=side_name,
                        stage_to="adult" if side_name == "fetal" else "fetal", change="present",
                        source_from=rec["anchor_file"] + " (human-side stage assertion)",
                        source_to="kb/markers (mouse-labeled evidence node)",
                        species_to="mouse",
                        evidence_anchor=rec["anchor_file"] + "#" + rec["anchor_locator"],
                        notes=f"mouse-labeled evidence node present in: {','.join(mouse_genes[g])}")

    # ---- family 5: stage taken from the derived keyword column
    for line, e in enumerate(edges, start=2):
        if e["adult_stage"] != "developing":
            continue
        add(family="derived_keyword_stage", lineage_id="", edge_ref=f"PRECURSOR_EDGES.tsv:{line}",
            precursor_node=f"CL:{e['precursor_cl_id']}", descendant_node=f"CL:{e['adult_cl_id']}",
            gene_symbol="", stage_from="unknown", stage_to=e["adult_stage"], change="present",
            source_from="PRECURSOR_EDGES.tsv (derived *_stage column)", source_to="PRECURSOR_EDGES.tsv (derived *_stage column)",
            stage_provenance="derived_keyword",
            evidence_anchor="plans/devline_ont_20261002/out/PRECURSOR_EDGES.tsv",
            notes="the stage qualifier of this row is a derived keyword rule, not a native ontology attribute")

    n_real = len(cands)

    # ---- fixtures: rules with no real candidate in this corpus
    fixtures = [
        dict(family="fixture_R5_assay", lineage_id="rod", edge_ref="", precursor_node="fixture",
             descendant_node="fixture", gene_symbol="RHO", stage_from="fetal", stage_to="adult",
             change="present", source_from="kb/markers (RNA panel)", source_to="a protein-level source",
             assay_to="protein", evidence_anchor="kb/markers/markers_v9_dev_retina.json#markers",
             fixture="Y", notes="rule-firing fixture: the two sides are different assays"),
        dict(family="fixture_R9_grade", lineage_id="rod", edge_ref="", precursor_node="fixture",
             descendant_node="fixture", gene_symbol="RHO", stage_from="fetal", stage_to="adult",
             change="present", source_from="kb/markers (RNA panel)", source_to="kb/markers (RNA panel)",
             evidence_anchor="kb/markers/markers_v9_dev_retina.json#markers",
             evidence_grade="looks_convincing", fixture="Y",
             notes="rule-firing fixture: grade outside the contract vocabulary"),
        dict(family="fixture_R11_numeric", lineage_id="rod", edge_ref="", precursor_node="fixture",
             descendant_node="fixture", gene_symbol="RHO", stage_from="fetal", stage_to="adult",
             change="up", source_from="kb/markers (RNA panel)", source_to="kb/markers (RNA panel)",
             evidence_anchor="kb/markers/markers_v9_dev_retina.json#markers",
             effect_value="2.4", extraction_record="", fixture="Y",
             notes="rule-firing fixture: numeric effect with no extraction record"),
        dict(family="fixture_R8_direction", lineage_id="cone", edge_ref="", precursor_node="fixture",
             descendant_node="fixture", gene_symbol="ARR3", stage_from="fetal", stage_to="adult",
             change="up", source_from="kb/markers (RNA panel)", source_to="kb/markers (RNA panel)",
             evidence_anchor="kb/markers/markers_v9_dev_retina.json#markers",
             identity_direction_asserted="N", fixture="Y",
             notes="rule-firing fixture: no start/end identity or time direction asserted by the source"),
        dict(family="fixture_R4_species", lineage_id="glia", edge_ref="", precursor_node="fixture",
             descendant_node="fixture", gene_symbol="RLBP1", stage_from="fetal", stage_to="adult",
             change="up", source_from="kb/markers (human RNA panel)", source_to="kb/markers (mouse-labeled evidence node)",
             species_to="mouse", evidence_anchor="kb/markers/markers_v9_dev_retina.json#markers",
             fixture="Y", notes="rule-firing fixture: the two sides are from different species"),
        dict(family="fixture_R1_anchor", lineage_id="cone", edge_ref="", precursor_node="fixture",
             descendant_node="fixture", gene_symbol="ARR3", stage_from="fetal", stage_to="adult",
             change="present", source_from="kb/markers (RNA panel)", source_to="kb/markers (RNA panel)",
             evidence_anchor="kb/markers/does_not_exist.json#markers", fixture="Y",
             notes="rule-firing fixture: the anchor does not resolve on disk"),
    ]
    for f in fixtures:
        add(**f)

    # ---- the check
    def anchor_exists(a):
        if not a:
            return False
        head = a.split("#")[0]
        p = Path(head) if head.startswith("/") else REPO / head
        if not p.is_file():
            p = Path("/mnt/D/EyeKB") / head if not head.startswith("/") else p
        return p.is_file()

    rejected, admitted = [], []
    for i, c in enumerate(cands, start=1):
        c["candidate_id"] = f"V3CC{i:05d}"
        broken, why = [], []
        if not anchor_exists(c["evidence_anchor"]):
            broken.append("R1"); why.append("anchor does not resolve on disk")
        if c["stage_provenance"] != "source_observed":
            broken.append("R2"); why.append("stage comes from a derived keyword column")
        if c["source_from"] != c["source_to"]:
            broken.append("R3"); why.append("the two sides are from different sources")
        if c["species_from"] != c["species_to"]:
            broken.append("R4"); why.append(f"species differ ({c['species_from']} vs {c['species_to']})")
        if c["assay_from"] != c["assay_to"]:
            broken.append("R5"); why.append(f"assay differ ({c['assay_from']} vs {c['assay_to']})")
        if c["condition_from"] != c["condition_to"]:
            broken.append("R6"); why.append("condition/experimental system differs between the sides")
        if int(c["n_steps"]) > 1:
            broken.append("R7"); why.append(f"lineage is {c['n_steps']} steps deep")
        if c["identity_direction_asserted"] != "Y":
            broken.append("R8"); why.append("no source-asserted identity and time direction for this change")
        if c["evidence_grade"] not in GRADES:
            broken.append("R9"); why.append(f"grade {c['evidence_grade']!r} outside the contract vocabulary")
        if c["change"] == "off":
            broken.append("R10"); why.append("`off` asserted from absence of mention")
        if c["effect_value"] and not c["extraction_record"]:
            broken.append("R11"); why.append("numeric effect value with no extraction record")
        c["rules_broken"] = ";".join(broken)
        c["primary_rule"] = broken[0] if broken else ""
        c["reason"] = " | ".join(why)
        (rejected if broken else admitted).append(c)

    cols = ["candidate_id", "fixture", "family", "lineage_id", "edge_ref", "precursor_node",
            "descendant_node", "gene_symbol", "species_from", "species_to", "stage_from", "stage_to",
            "change", "assay_from", "assay_to", "source_from", "source_to", "stage_provenance",
            "identity_direction_asserted", "n_steps", "evidence_anchor", "evidence_grade",
            "effect_value", "extraction_record", "rules_broken", "primary_rule", "reason", "notes"]
    with open(OUT / "CANDIDATE_CHANGES.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(cands)

    led_cols = ["candidate_id", "fixture", "family", "lineage_id", "gene_symbol", "stage_from",
                "stage_to", "change", "primary_rule", "rules_broken", "reason", "evidence_anchor"]
    with open(OUT / "CHANGE_REJECTION_LEDGER.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=led_cols, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows([c for c in rejected])

    with open(OUT / "CHANGE_ADMITTED.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(admitted)

    with open(OUT / "RULE_REGISTRY.tsv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["rule_id", "name", "meaning", "n_real_candidates_rejected_by_this_rule",
                    "n_fixture_candidates_rejected_by_this_rule"])
        for rid, name, meaning in RULES:
            w.writerow([rid, name, meaning,
                        sum(1 for c in rejected if c["fixture"] == "N" and rid in c["rules_broken"].split(";")),
                        sum(1 for c in rejected if c["fixture"] == "Y" and rid in c["rules_broken"].split(";"))])

    real = [c for c in cands if c["fixture"] == "N"]
    fix = [c for c in cands if c["fixture"] == "Y"]
    summary = {
        "n_candidates_real": len(real),
        "n_candidates_fixture": len(fix),
        "n_rejected_real": sum(1 for c in rejected if c["fixture"] == "N"),
        "n_rejected_fixture": sum(1 for c in rejected if c["fixture"] == "Y"),
        "n_admitted_real": sum(1 for c in admitted if c["fixture"] == "N"),
        "n_admitted_fixture": sum(1 for c in admitted if c["fixture"] == "Y"),
        "by_family": {f: sum(1 for c in real if c["family"] == f) for f in sorted({c["family"] for c in real})},
        "primary_rule_counts_real": {r: sum(1 for c in rejected if c["fixture"] == "N" and c["primary_rule"] == r)
                                     for r in sorted({c["primary_rule"] for c in rejected if c["fixture"] == "N"})},
        "rules_never_fired_real": [r for r, _, _ in RULES
                                   if not any(r in c["rules_broken"].split(";") for c in rejected if c["fixture"] == "N")],
        "all_rules_fired_by_fixtures": sorted({r for c in rejected if c["fixture"] == "Y"
                                               for r in c["rules_broken"].split(";")}),
        "mouse_labeled_genes_found": len(mouse_genes),
        "input_hashes": {"kb/markers/markers_v9_dev_retina.json": sha256(KB / "markers" / "markers_v9_dev_retina.json"),
                         "kb/baselines/retina.json": sha256(KB / "baselines" / "retina.json"),
                         "kb/baselines/retina__fetal_developing.json": sha256(KB / "baselines" / "retina__fetal_developing.json"),
                         "kb/baselines/fetal_development_transitions.json": sha256(KB / "baselines" / "fetal_development_transitions.json")},
        "graded_contract_stages": sorted(STAGES),
    }
    (OUT / "CHANGE_CHECK_SUMMARY.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()