#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB3 W1: render the standalone developmental entry retina__fetal_developing (JSON+MD).

Iron-rule implementation (PI: fetal ≠ adult even in the same tissue):
  - schema=eyekb-baseline-development/1.0 -> MCP _load_priors only accepts adult entries whose schema
    startswith "eyekb-baseline/"; this entry is invisible to adult queries and the no-adult-bucket-
    substitute path is unchanged (_fetal_concept_response).
  - data source = histograms of authors'/portal **published labels** (aggregated by kb3_fetal_agg.py);
    the live adult engine has zero involvement.
  - development_stage=fetal_developing; the 4 sample faces inside GSE138002 are hard-split by sample
    prefix; adult_Adult / organoid_Day segments **do not enter the entry body**, only isolation
    records are kept (organoid per adjudication Q1: unknown + flag).
Material: plans/kb3_evidence/fetal_agg_20260924.json (asserted here; numbers are never hand-copied).
"""
import json
from pathlib import Path

AGG = Path("/mnt/D/EyeKB/plans/kb3_evidence/fetal_agg_20260924.json")
KB = Path("/mnt/D/EyeKB/kb/baselines")
OUT_DIR = KB
PROH = ("KB3 prohibition (PI red line 2026-09-23): developmental-stage data must not enter the adult "
        "baseline statistics pool, and vice versa —— fetal ≠ adult even within the same tissue; "
        "adult/fetal never serve as mutual references.")

agg = json.loads(AGG.read_text(encoding="utf-8"))
A = agg["GSE268630_portal"]
B = agg["GSE138002_final_author_labels"]
C = agg["GSE234963"]

# ---- assertions (material integrity; on failure stop, no half-finished entries) ----
assert A["cells_total"] == sum(A["majorclass_hist"].values()) == 226506, "268630 histogram mismatch"
assert B["cells_final_total"] == 118555
lay = B["layers"]
lay.setdefault("other", {"n_cells": 0, "celltype_pct": {}, "samples": []})
assert sum(v["n_cells"] for v in lay.values()) == B["cells_final_total"], "138002 stratification lost cells"
assert "Hgw9" in lay["fetal_Hgw"]["samples"] and "Hgw27" in lay["fetal_Hgw"]["samples"]
assert set(lay["adult_Adult"]["samples"]) == {"Adult"}
assert all(s.endswith("_Day") for s in lay["organoid_Day"]["samples"])

FETAL = lay["fetal_Hgw"]
POST = lay["postnatal_Hpnd"]
# zero mapping from the fetal vocabulary onto the adult 10-class vocabulary: keep original terms
# (the developmental vocabulary is an independent ontology; translating it = precursor of pooling)
entry = {
    "schema": "eyekb-baseline-development/1.0",
    "entry_id": "baseline_human_retina__fetal_developing__kb3",
    "tissue": "retina",
    "species": "human",
    "title": "Composition reference (developmental stage): human fetal retina fetal_developing (author/portal label aggregation, KB3 standalone entry)",
    "status": "development_annotated_aggregate",
    "generated": "2026-09-24",
    "generator": "kb3_build_dev_entries.py (KB3 t_5425a7ca) ← measured material from kb3_fetal_agg.py",
    "card": "t_5425a7ca",
    "development_stage": "fetal_developing",
    "development_stage_prohibition": PROH,
    "stage_axis": {
        "field": "development_stage",
        "levels": ["adult", "fetal_developing", "postnatal_neonatal",
                   "mixed_not_separable", "unknown"],
        "note": ("KB3 enum (task brief W1). This entry = developmental entry, permanently separated from the adult "
                 "master file (retina.json, organism_stage=adult); citing numbers from this entry to backfill any "
                 "adult entry is forbidden, and vice versa."),
    },
    "nature": ("Developmental-stage **composition reference** entry: the numbers are **direct count aggregations** of "
               "cell labels published by the dataset authors / CELLxGENE portal, not live adult-engine inference "
               "(the engine must abstain on fetal data, E4/E5 OOD_strict frozen items); the donor-level median/IQR "
               "scope is not established (fetal reference pipeline task not started, KB2c adjudication Q5); "
               "this entry is a label-distribution-level reference."),
    "usage_scope": ("Identity reference for fetal/developmental-stage retinal material + OOD behavior control anchor "
                    "(E5 same-source data); must not be treated as a composition pass line; must not serve as mutual "
                    "reference with the adult master file (PI red line); excluded from all scoring (Astra T2, inherited globally)."),
    "evidence_grades": {"A": "direct counts of portal/author published labels (file paths + aggregation script traceable)"},
    "anchors": [
        {"acc": "GSE268630", "role": "primary_portal", "tier": "fetal",
         "file": "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad",
         "cells": 226506, "donors": 14,
         "stage_range": "11w2d–23w4d post-fertilization (portal development_stage 14 levels; full list in "
                        "plans/kb3_evidence/fetal_agg_20260924.json)",
         "tissue_note": "macula lutea 119,111 + peripheral 100,532 + retina (site unlabeled) 6,863",
         "provenance": "CELLxGENE portal annotations (author_cell_type/majorclass columns)"},
        {"acc": "GSE138002", "role": "secondary_author_labels", "tier": "fetal+postnatal mixed face, split",
         "file": "/mnt/D/OcularKB/data/GSE138002/GSE138002_Final_barcodes.csv.gz",
         "cells_final_total": 118555,
         "layer_split": {k: v["n_cells"] for k, v in lay.items()},
         "fetal_layer_cells": FETAL["n_cells"],
         "fetal_layer_samples": FETAL["samples"],
         "stage_range_note": "task brief stated GW9-19; the measured portal Final version contains Hgw9–Hgw27 + Hpnd8 + Adult + organoid Days"
                             " —— mixed content hard-split by sample-face prefix; non-fetal faces stay out of this entry's body",
         "provenance": "author published label column umap2_CellType (GEO suppl Final_barcodes)"},
        {"acc": "GSE234963", "role": "data_card_only", "tier": "fetal_RPC",
         "cells": C["cells"], "registry": C["registry"], "files": C["files"],
         "composition": None,
         "note": "no label columns in obs (measured: all 24x h5ad obs empty) + no standalone GEO label file "
                 "(registry recheck agrees) -> data card only; composition pending the fetal reference pipeline / "
                 "author label acquisition; no evidence, no entry (KB3 discipline 3)."}],
    "portal_majorclass_reference": {
        "cells": A["cells_total"], "donors": A["n_donors"],
        "pct": A["majorclass_pct"], "hist": A["majorclass_hist"],
        "vocabulary_note": "PRPC=photoreceptor progenitor, NRPC=neural retina progenitor —— "
                           "developmental-specific classes with **no adult 10-class counterpart**; mapping into the adult vocabulary is forbidden (ontology separation)."},
    "author_labels_fetal_layer(GSE138002)": {
        "cells": FETAL["n_cells"], "samples": FETAL["samples"],
        "pct_by_celltype": FETAL["celltype_pct"],
        "vocabulary_note": "RPCs/Neurogenic Cells/BC.Photo_Precurs/AC.HC_Precurs and other precursor terms: same rule as above —— never translated into adult vocabulary."},
    "postnatal_neonatal_layer(GSE138002)": {
        "cells": POST["n_cells"], "samples": POST["samples"],
        "pct_by_celltype": POST["celltype_pct"],
        "development_stage": "postnatal_neonatal",
        "note": "separate stratum: neonatal ≠ fetal ≠ adult (the third value of the KB3 enum is evidenced here); never merged with the fetal layer."},
    "excluded_layers": {
        "adult_Adult": {"cells": lay["adult_Adult"]["n_cells"],
                        "disposition": "never merge into this developmental entry (adult control material belongs to the adult-side scope, but the 11.6K cells are not part of the D001 system — no standalone entry; registered in isolation)"},
        "organoid_Day": {"cells": lay["organoid_Day"]["n_cells"], "samples": lay["organoid_Day"]["samples"],
                         "disposition": "organoid -> unknown + flag (KB2c adjudication Q1: organoid ≠ fetal tissue ≠ adult); "
                                        "listed only, never merged into any developmental or adult entry"},
        "other": {"cells": lay["other"]["n_cells"], "disposition": "sample faces not named developmentally -> isolated"}},
    "cross_source_note": ("the two anchors use different vocabularies (portal majorclass 9 classes vs author 12+ classes) —— "
                          "this entry presents them side by side and never synthesizes a single distribution "
                          "(developmental-axis inheritance of the Astra T6 no-synthesis scope)."),
    "flags": {"engine_applicability": "the live interpretation engine = adult domain; it must abstain on this entry's material; "
                                      "the numbers here must not serve as a scoring basis for right/wrong of engine output on fetal "
                                      "(E5 is behavioral description only).",
              "not_donor_level": "donor-level interval scope not established (fetal pipeline is a separate batch); carry this flag when citing."},
    "caveats": [
        "label distribution = the transcriptome face of the published annotations; GSE268630 also contains the multiome ATAC face of GSM matrices (not merged into this entry).",
        "GSE138002 'Final' is the author-curated set (118,555 of 138,672 total); the All_barcodes face has no label column; aggregation follows Final.",
        "this entry = standalone developmental-stage file; the KB2c concept entry fetal_development_transitions remains the entry-point placeholder — both coexist: the concept entry answers 'which candidates exist', this entry answers 'what the measured fetal-retina label distribution is'."],
    "sources": [
        {"sid": "S1", "kind": "portal_dataset", "acc": "GSE268630",
         "path": A and "/mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad"},
        {"sid": "S2", "kind": "geo_supplementary", "acc": "GSE138002",
         "path": "/mnt/D/OcularKB/data/GSE138002/GSE138002_Final_barcodes.csv.gz"},
        {"sid": "S3", "kind": "registry", "row": "OA-D009/OA-D010",
         "path": "/mnt/D/OcularKB/registry/ocular_public_datasets_verified_v1.csv"},
        {"sid": "S4", "kind": "eval_anchor", "note": "E5=Q8_GSE268630 (same data on the eval side, behavior quarantined first; "
                                                     "this entry is its KB-side companion)"},
    ],
    "identity_signature": None,  # computed below after fill (covers only this entry's body; independent of the adult-entry signature scheme)
}


def sha256_obj(obj):
    import hashlib
    return "sha256:" + hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


entry["identity_signature"] = {
    entry["entry_id"]: sha256_obj({k: entry[k] for k in
                                   ("portal_majorclass_reference",
                                    "author_labels_fetal_layer(GSE138002)",
                                    "postnatal_neonatal_layer(GSE138002)", "excluded_layers")})}

(OUT_DIR / "retina__fetal_developing.json").write_text(
    json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------- MD rendering ----------------
L = [f"# {entry['title']}", ""]
L.append(f"> schema: `{entry['schema']}` | entry_id: `{entry['entry_id']}` | status: {entry['status']} "
         f"| **development_stage={entry['development_stage']}** | generated: {entry['generated']} | card: {entry['card']}")
L.append(f"> ⚠ {PROH}")
L.append(f"> This file is rendered by `/mnt/D/EyeKB/scripts/baselines/kb3_build_dev_entries.py` from material "
         f"`plans/kb3_evidence/fetal_agg_20260924.json` —— to change content, edit the aggregation script + material; manual MD edits get overwritten.")
L.append("")
L.append(f"**Nature**: {entry['nature']}")
L.append("")
L.append(f"**Usage scope**: {entry['usage_scope']}")
L.append("")
L.append("## Anchors and availability verification (KB3 discipline 3: no evidence, no entry)")
L.append("")
L.append("| Anchor | Role | Cells | Tier | On-disk evidence |")
L.append("|---|---|---|---|---|")
L.append(f"| GSE268630 | portal primary anchor | {A['cells_total']:,} (14 donor) | 11w2d–23w4d full fetal period | "
         f"gse268630_cellxgene.h5ad measured (same file as this repo's E5 frozen item) |")
L.append(f"| GSE138002 | author-label secondary anchor | Final {B['cells_final_total']:,} (fetal layer {FETAL['n_cells']:,}) | "
         f"Hgw9–Hgw27 measured (task brief's GW9-19 was too narrow) | Final_barcodes.csv.gz umap2_CellType |")
L.append(f"| GSE234963 | **data card only** | 176,849 (24 samples) | ~7.5–21 PCW | no label columns in obs (measured) -> composition pending backfill |")
L.append("")
L.append("## Developmental label distribution — GSE268630 (portal majorclass, whole-pool direct counts)")
L.append("")
L.append("| majorclass | % | n_cells |")
L.append("|---|---|---|")
for k, v in A["majorclass_hist"].items():
    L.append(f"| {k} | {A['majorclass_pct'][k]} | {v:,} |")
L.append("")
L.append(f"> site face: macula lutea 119,111 / peripheral 100,532 / unlabeled 6,863; "
         f"PRPC/NRPC are developmental-specific with no adult counterpart —— **never map into the adult 10-class vocabulary**.")
L.append("")
L.append("## Developmental label distribution — GSE138002 fetal-retina layer (author umap2_CellType)")
L.append("")
L.append("| celltype | % |  | sample face | Hgw9–Hgw27 (17 unit) |")
L.append("|---|---|---|---|---|")
for k, v in FETAL["celltype_pct"].items():
    L.append(f"| {k} | {v} | | | |")
L.append("")
L.append("## Neonatal layer (GSE138002 Hpnd8) — development_stage=postnatal_neonatal (third enum value evidenced here)")
L.append("")
for k, v in POST["celltype_pct"].items():
    L.append(f"- {k}: {v}%")
L.append("")
L.append("## Excluded layers (never merge, registration only)")
L.append("")
L.append(f"- **Adult face** ({lay['adult_Adult']['n_cells']:,} cells): adult control material -> not admitted to the developmental entry; "
         f"also not part of the D001 system, no standalone adult entry (isolation record).")
L.append(f"- **Organoid Days face** ({lay['organoid_Day']['n_cells']:,} cells, "
         f"{sorted(lay['organoid_Day']['samples'])}): organoid -> unknown + flag (adjudication Q1).")
if lay["other"]["n_cells"]:
    L.append(f"- **other face** ({lay['other']['n_cells']} cells): isolated.")
L.append("")
L.append("## Cross-source scope statement")
L.append("")
L.append(entry["cross_source_note"])
L.append("")
L.append(f"⚑ **{entry['flags']['engine_applicability']}**")
L.append(f"⚑ {entry['flags']['not_donor_level']}")
L.append("")
L.append("## caveats")
for c in entry["caveats"]:
    L.append(f"- {c}")
L.append("")
L.append(f"identity signature: `{json.dumps(entry['identity_signature'], ensure_ascii=False)}`")
(OUT_DIR / "retina__fetal_developing.md").write_text("\n".join(L) + "\n", encoding="utf-8")

# ---------------- index registration (baselines.json development_entries key, additive) ----------------
IDX = KB / "baselines.json"
idx = json.loads(IDX.read_text(encoding="utf-8"))
rec = {"entry_id": entry["entry_id"], "file": "retina__fetal_developing.md",
       "tissue": "retina", "development_stage": "fetal_developing",
       "anchors": [c["acc"] for c in entry["anchors"]], "status": entry["status"],
       "schema": entry["schema"], "note": "standalone developmental entry (invisible to MCP adult queries; coexists with the concept entry)"}
ex = [x for x in idx.get("development_entries", []) if x.get("entry_id") != rec["entry_id"]]
idx["development_entries"] = ex + [rec]
IDX.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------- concept-entry pointer (additive tail note, candidates array untouched) ----------------
pm = KB / "fetal_development_transitions.md"
t = pm.read_text(encoding="utf-8")
# mark matches the historical line already present in the live concept MD (frozen input; not renamed)
mark = "KB3 已建首个发育期实数据参考条"
if mark not in t and "KB3 first developmental real-data reference entry" not in t:
    t += ("\n> **KB3 progress (2026-09-24)**: the first developmental real-data reference entry is now filed standalone = `retina__fetal_developing.md` "
          "(aggregation of GSE268630 portal + GSE138002 author labels; GSE234963 data card). This concept entry remains the candidate master table and "
          "the MCP fetal query entry point —— the two coexist without overwriting each other; the \"needs a fetal reference pipeline\" statement "
          "remains valid for **engine interpretation**; the numbers in this entry are published-label distribution references only, not engine-pipeline products.\n")
    pm.write_text(t, encoding="utf-8")
pj = KB / "fetal_development_transitions.json"
d = json.loads(pj.read_text(encoding="utf-8"))
if "kb3_first_entry_pointer" not in d:
    d["kb3_first_entry_pointer"] = {
        "file": "retina__fetal_developing.json", "entry_id": entry["entry_id"],
        "card": "t_5425a7ca", "date": "2026-09-24",
        "note": "concept entry = candidate master table / query entry point; that file = published-label distribution reference entry (first developmental real-data entry). Coexist."}
    pj.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

print("WROTE retina__fetal_developing.json/md + index + concept pointer")
print(json.dumps({"fetal_268630": A["majorclass_pct"],
                  "fetal_138002": FETAL["n_cells"]}, ensure_ascii=False))
