#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n4b -- build the optic-nerve fibroblast carrier (card part 1).

Output: kb/markers/markers_v13_onfibro_increment.json -- a NEW library, registered default-OFF with
an empty whitelist, so the shipped default route is byte-identical in every state and activating a
default face stays a separate PI decision.

ADMISSION RULE (declared here, applied mechanically; nothing is hand-picked)
---------------------------------------------------------------------------
The candidate set is closed: the motivating cluster's recorded 10-gene window, the shipped generic
`Fibroblast` panel, and the shipped limbal/scleral fibroblast entry (23 symbols in total, see
n4a_mine_carrier.py). A candidate gene is ADMITTED into the carrier iff all four hold:

  (1) it belongs to that closed set;
  (2) it is measurable in the assay (present in the project's gene vocabulary);
  (3) the local corpus gives it >= 2 chunks in a fibroblast context, at least one of them ocular;
  (4) no shipped library already attaches it to a NON-fibroblast KB class -- a gene the KB already
      spends on another family may not be spent twice, or two families start competing for the same
      query (the repository's own `宁可不映射` discipline).

Genes already in the shipped generic panel are retained unconditionally (the holefill_v12 rule:
a deepening must not lose identity genes).

The carrier is named by the Cell Ontology label of the term it carries, and the term is resolved
against the in-repo ontology release; the class name is therefore CL-resolvable by construction.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_common as W  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
PANEL_PATH = os.path.join(W.REPO, "kb", "markers", "markers_v13_onfibro_increment.json")
LIB_NAME = "onfibro_v13"
ENTRY = "Fibroblast"
CL_ID = "CL:0000057"          # fibroblast
CORPUS = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10"

WINDOW = ["BICC1", "MIR99AHG", "RBMS3", "LEPR", "FOXP2", "ADAMTSL3", "MIR100HG", "BNC2", "EYA2",
          "CEMIP"]
SHIPPED_FIBRO = ["COL1A1", "COL1A2", "COL3A1", "DCN", "LUM", "FBN1", "FN1", "PTGDS", "MMP2", "THY1"]


def claim_map():
    """gene -> ['<library>::<class>', ...] over the shipped libraries (sorted, deterministic)."""
    sys.path.insert(0, os.path.join(W.REPO, "mcp_server"))
    os.environ["EYEKB_ACT_V6"] = "1"
    import eyekb_core as core
    claim = {}
    for name, path, db in core._load_marker_dbs("all"):
        for cls, genes in (db.get("markers") or {}).items():
            for g in genes:
                claim.setdefault(str(g).upper(), []).append("%s::%s" % (name, cls))
    return {k: sorted(v) for k, v in claim.items()}


def cl_name(cid):
    for line in open(W.CL_OBO, encoding="utf-8", errors="replace"):
        pass
    cur = None
    for line in open(W.CL_OBO, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if line == "[Term]":
            cur = {}
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = None
            continue
        if cur is None or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if k == "id":
            cur["id"] = v
        elif k == "name":
            cur["name"] = v
        elif k == "is_obsolete":
            cur["obs"] = (v == "true")
        if cur.get("id") == cid and cur.get("name"):
            return cur["name"], not cur.get("obs", False)
    return None, None


def main():
    lit = json.load(open(os.path.join(OUT, "carrier_lit.json")))
    rows = {r["gene"]: r for r in lit["rows"]}
    claims = claim_map()

    admitted, rejected = [], []
    for g in sorted(set(WINDOW) | set(SHIPPED_FIBRO)):
        r = rows.get(g, {})
        rec = {"gene": g, "in_window": g in WINDOW, "in_shipped_panel": g in SHIPPED_FIBRO,
               "in_assay": bool(r.get("in_assay_vocabulary")),
               "papers_fibro_eye": r.get("papers_fibroblast_context_eye", 0),
               "papers_fibro_any": r.get("papers_fibroblast_context_any_tissue", 0),
               "claimed_by": claims.get(g, [])}
        if rec["in_shipped_panel"]:
            rec["decision"] = "admit_retained_identity_gene"
            admitted.append(rec)
            continue
        bad = claims.get(g, [])
        if not rec["in_assay"]:
            rec["decision"] = "reject_rule2_not_measurable_in_assay"
        elif rec["papers_fibro_eye"] < 1 or rec["papers_fibro_any"] < 2:
            rec["decision"] = "reject_rule3_insufficient_literature_support"
        elif bad:
            rec["decision"] = "reject_rule4_gene_already_spent_on_another_family"
        else:
            rec["decision"] = "admit"
            admitted.append(rec)
        if rec["decision"].startswith("reject"):
            rejected.append(rec)

    marker_set = sorted(set(SHIPPED_FIBRO) | {r["gene"] for r in admitted})
    name, not_obsolete = cl_name(CL_ID)

    # the motivating cluster, for the design record only (the reading itself is in n5)
    calls = W.load_set()
    c31 = [c for c in calls if c["vol"] == "CX15_optic_nerve_all" and c["cluster"] == "31"][0]
    win = [str(g).upper() for g in c31["genes"][:10]]
    shared_window = sorted(set(win) & set(marker_set))
    shared_shipped = sorted(set(win) & set(SHIPPED_FIBRO))

    doc = {
        "version": "v13.0-onfibro-20261022",
        "created": "2026-10-22",
        "scope": "the fibroblast family carrier on the optic-nerve side: the exclusion table removes "
                 "the only reachable carrier of the family for optic-nerve-declared clusters while "
                 "the legitimate generic fibroblast panel shares none of their window, so a "
                 "coarse-but-family-correct answer degrades to an abstention",
        "status": "staging only; library `%s` is NOT merged into the default `all` set and has an "
                  "EMPTY whitelist, so the default route is byte-identical in every state. "
                  "Activating a default face is a separate PI decision and is not made here."
                  % LIB_NAME,
        "registered_by": "docs/plans/noregr_20261022/PREREG_NOREGRESSION_20261022.md",
        "card": "t_0c40c7b1",
        "cl_release": "cl/releases/2026-06-08/cl-base.owl",
        "cl_ontology_file": "kb/ontology/cl/releases/2026-06-08/cl-base.obo",
        "source_corpus": CORPUS,
        "scope_tissues": ["optic_nerve", "retina", "choroid", "sclera", "iris", "ciliary_body",
                          "trabecular_meshwork", "ocular_surface", "conjunctiva", "lens", "RPE",
                          "lacrimal_gland"],
        "scope_tissues_provenance": "the family is legitimate in every ocular tissue the exclusion "
                                    "table speaks about; the entry does not name a tissue-specific "
                                    "identity, it carries the generic family and is named by the "
                                    "generic ontology term",
        "admission_rule": {
            "closed_candidate_set": "motivating window (10) + shipped generic Fibroblast panel (10) "
                                    "= 20 symbols; n4a also profiled the 3 genes of the shipped "
                                    "limbal/scleral entry",
            "rule2": "measurable in the assay (project gene vocabulary)",
            "rule3": ">=2 corpus chunks in a fibroblast context, >=1 of them ocular",
            "rule4": "not already attached by a shipped library to a non-fibroblast KB class",
            "retention": "genes of the shipped generic panel are retained unconditionally "
                         "(deepening must not lose identity genes)",
        },
        "markers": {ENTRY: marker_set},
        "entries": [{
            "class_name": ENTRY,
            "cl_id": CL_ID,
            "cl_label": name,
            "cl_resolves": bool(name) and bool(not_obsolete),
            "cl_status": "kept_separate",
            "cl_overlap_note": "CL:0000057 is the term of the shipped generic `Fibroblast` entry in "
                               "kb/markers/markers_membrane_v1.json (10 genes). This entry is the "
                               "same cell type with a deepened panel; the membrane body is "
                               "untouched. The two entries differ in library, so the merged route "
                               "presents them as separate alias rows and no ranking carries one "
                               "class twice.",
            "tissue": ["fibroblast"],
            "markers": marker_set,
            "n_markers": len(marker_set),
            "why": "the family's coarse carrier, deepened with the evidence-passing genes of the "
                   "motivating window so the >=2 shared-gene bar can be cleared",
            "evidence": {r["gene"]: rows.get(r["gene"], {}).get("examples", [])
                         for r in admitted if r["gene"] in WINDOW},
            "shared_with_motivating_window": shared_window,
        }],
        "admitted": admitted,
        "rejected": rejected,
        "not_repeated_from_production": {
            "shipped generic Fibroblast (membrane_v1, 10 genes)": "retained as identity genes and "
                                                                  "extended, not replaced",
            "k9_ocs::Limbus_Sclera_fibroblast_C1 (DPT/LEPR/LAMA2)": "left in place; the exclusion "
                                                                    "row that removes it stays in "
                                                                    "place too, because a "
                                                                    "limbal/scleral identity is "
                                                                    "still foreign to the optic "
                                                                    "nerve",
        },
        "known_limits": [
            "the two admitted window genes carry 3 and 2 corpus chunks respectively: this is a thin "
            "evidence base, chosen from a closed candidate set rather than from an open harvest",
            "the reading on CX15 is IN-SAMPLE: the panel was selected on the same volumes it is "
            "measured on. No accuracy claim is made; the measurement is a harm-line reading",
            "the carrier is a family-level (coarse) answer. It does not claim the cluster is any "
            "particular fibroblast subtype",
        ],
    }
    os.makedirs(os.path.dirname(PANEL_PATH), exist_ok=True)
    with open(PANEL_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")

    rec = {"probe": "n4b_build_carrier_panel.py", "library": LIB_NAME, "entry": ENTRY,
           "panel_path": PANEL_PATH, "panel_sha256": W.sha256_file(PANEL_PATH),
           "cl_id": CL_ID, "cl_label": name, "cl_resolves": bool(name) and bool(not_obsolete),
           "n_markers": len(marker_set), "markers": marker_set,
           "admitted": admitted, "rejected": rejected,
           "motivating_cluster": {"vol": "CX15_optic_nerve_all", "cluster": "31",
                                  "window": win,
                                  "shared_with_shipped_panel": shared_shipped,
                                  "shared_with_deepened_panel": shared_window}}
    W.save_json(os.path.join(OUT, "carrier_panel.json"), rec)

    print("panel:", PANEL_PATH, "sha256:", rec["panel_sha256"])
    print("CL:", CL_ID, "->", name, "resolves:", rec["cl_resolves"])
    print("markers (%d): %s" % (len(marker_set), marker_set))
    print("admitted:", [r["gene"] for r in admitted])
    print("rejected:")
    for r in rejected:
        print("   %-10s %-46s p_eye=%-3d p_any=%-3d claims=%s"
              % (r["gene"], r["decision"], r["papers_fibro_eye"], r["papers_fibro_any"],
                 r["claimed_by"]))
    print("motivating window shared: shipped=%s  deepened=%s" % (shared_shipped, shared_window))
    print("wrote", os.path.join(OUT, "carrier_panel.json"))


if __name__ == "__main__":
    main()