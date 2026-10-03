#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB interpretation-layer prior-entry builder (KB1, card t_39182aa2, 2026-09-23)

Responsibilities:
  1. **Real-time recomputation** of Grade A numbers from raw data sources (HRCA h5ad majorclass counts; GSE165784 v2 Track B
     cluster_composition_B.csv), reconciled with frozen values (drift triggers error and rejects output).
  2. Assembler reads JSON (kb/priors/**/*.json, single source of truth).
  3. Render human-readable MD from JSON (kb/priors/**/*.md) — MD tables match JSON field-by-field,
     K4 golden regression validates accordingly (tool return ↔ JSON ↔ MD).

Discipline (BRIEF_KB1_PRIOR_LAYER_20260923):
  - Every expectation must include a source (PMID/dataset + evidence level); entries without sources are prohibited (Red Line 8)
  - Priors serve only as controls and QC flags; prohibited from scoring (inheriting Red Line 12)
  - two-level structure: cell type × state, preventing state inflation into new types
Evidence level:
  A = Local empirical recomputation (this pipeline, with file paths + cell counts)
  B = Directly reported in original literature (read original paragraph; only supports qualitative description if abstract lacks precise %)
  C = Empirical range across multiple studies (derived from cross-study distribution of Grade A source data, method noted within entry)
Run:
  /home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/scripts/priors/build_priors.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

EYEKB = Path("/mnt/D/EyeKB")
PRIORS = EYEKB / "kb" / "priors"
HRCA_H5AD = "/mnt/D/OcularKB/data/HRCA_cellxgene/HRCA_allcells_annotated.h5ad"
GSE_DIR = EYEKB / "plans" / "demo_gse165784" / "proc" / "v2"
FROZEN_DATE = "2026-09-23"
CARD = "t_39182aa2"

MARKER_LIB = json.load(open(EYEKB / "kb/markers/markers_v4.1_clean.json"))
MEMB_LIB = json.load(open(EYEKB / "kb/markers/markers_membrane_v1.json"))


def h5ad_col(obs, name):
    c = obs[name]
    if isinstance(c, h5py.Dataset):
        return c[:]
    codes = c["codes"][:]
    cats = [x.decode() for x in c["categories"][:]]
    return np.array([cats[i] if i >= 0 else "NA" for i in codes], dtype=object)


# ------------------------------------------------------------------ A-level recalculation
def recompute_hrca():
    """HRCA CELLxGENE edition: recomputation of majorclass/cell_type over 3.17M cells.
    Returns {pooled: {...}, per_study: {...}}; studies grouped by sample-id prefix."""
    f = h5py.File(HRCA_H5AD, "r")
    obs = f["obs"]
    mc = np.array([str(x) for x in h5ad_col(obs, "majorclass")])
    sid = [str(x) for x in h5ad_col(obs, "sampleid")]
    f.close()

    def grp(s):
        for pref, name in [("Chen_a", "Chen_a"), ("Chen_b", "Chen_b_GSE226108"),
                           ("Chen_c", "Chen_c_GSE247157"), ("Chen_rgc", "Chen_rgc_TARGETED"),
                           ("MMD", "MMD"), ("BCM", "BCM"), ("A23", "other"), ("GSM", "Shekhar_legacy")]:
            if s.startswith(pref):
                return name
        return "other"

    total = len(mc)
    pooled = Counter(mc)
    # Whole retina pooled (excluding RGC-targeted enrichment study Chen_rgc — its 46% RGC is by design, not tissue baseline)
    wc = Counter(m for m, s in zip(mc, sid) if grp(s) != "Chen_rgc_TARGETED")
    t2 = sum(wc.values())
    per_study = {}
    gs = [grp(s) for s in sid]
    by = {}
    for m, g in zip(mc, gs):
        by.setdefault(g, Counter())[m] += 1
    for g, c in by.items():
        tot = sum(c.values())
        per_study[g] = {"n": tot, **{k: round(100 * v / tot, 2) for k, v in c.items()}}
    return {"total": total,
            "pooled_all": {k: [v, round(100 * v / total, 2)] for k, v in pooled.items()},
            "pooled_whole_retina": {"n": t2, **{k: round(100 * v / t2, 2) for k, v in wc.items()}},
            "per_study": per_study}


def recompute_gse165784():
    """GSE165784 v2 Track B (harmonypy integration track): per-cluster compartment recomputation,
    in two scopes: all samples and PDR-only."""
    df = pd.read_csv(GSE_DIR / "cluster_composition_B.csv")
    comp_of = {0: "myeloid", 1: "myeloid", 2: "myeloid", 3: "myeloid", 4: "myeloid",
               5: "myeloid", 6: "myeloid", 7: "stromal_myofibro", 8: "stromal_pericyte",
               9: "lymphoid_T", 10: "myeloid", 11: "proliferating", 12: "glial_candidate",
               13: "myeloid", 14: "lymphoid_plasma", 15: "endothelial", 16: "myeloid"}
    df["cluster"] = df["leiden_B"].astype(int)
    df["comp"] = df["cluster"].map(comp_of)
    pdr_cols = [c for c in df.columns if ("PDR" in c)]
    df["pdr"] = df[pdr_cols].sum(axis=1)
    n_all, n_pdr = int(df["n"].sum()), int(df["pdr"].sum())
    ca = df.groupby("comp")["n"].sum()
    cp = df.groupby("comp")["pdr"].sum()
    return {"n_all": n_all, "n_pdr": n_pdr,
            "comp_all": {k: [int(v), round(100 * v / n_all, 2)] for k, v in ca.items()},
            "comp_pdr": {k: [int(v), round(100 * v / n_pdr, 2)] for k, v in cp.items()}}


# ------------------------------------------------------------------ Curated content
RETINA_CLASSES = [
    # (class, English name, expected typical range %, enrichment exception notes, local library marker)
    ("Rod", "Rod photoreceptors", [28, 46], None),
    ("Cone", "Cone photoreceptors", [1.5, 7], None),
    ("BC", "Bipolar cells", [12, 33], None),
    ("AC", "Amacrine cells", [8, 28], None),
    ("HC", "Horizontal cells", [1, 8], None),
    ("RGC", "Ganglion cells", [3, 15],
     "RGC-targeted studies (Chen_rgc pooled 46.2%, Shekhar_legacy 43.6%) use sorting/enrichment designs; high proportion ≠ abnormality"),
    ("MG", "Müller glia", [3, 12], None),
    ("Astrocyte", "Astrocytes", [0.1, 1.5], None),
    ("Microglia", "Microglia", [0.05, 0.8], None),
    ("RPE", "Retinal pigment epithelium", [0, 1.0],
     "High RPE proportion in neural retina sections suggests RPE/choroid contamination (not native neural retina components)"),
]

HRCA_SOURCES = [
    {"sid": "HRCA317M", "kind": "dataset", "pmid": "41578023",
     "label": "HRCA CELLxGENE merged version 3,177,310 cells (10 majorclass, all normal, 6 studies/104 donors, fovea~periphery)",
     "path": HRCA_H5AD, "computation": f"Card {CARD} obs.majorclass recomputation (build_priors.py recompute_hrca)"},
    {"sid": "HRCA_PAPER", "kind": "paper", "pmid": "41578023",
     "label": "Li et al., Single-cell atlas of the transcriptome and chromatin accessibility in the human retina. Nat Genet 2026 (full version ~3.9M cells, 123 RNA classes)"},
    {"sid": "FOVEA_PERIPH", "kind": "paper", "pmid": "32555229",
     "label": "Cell Atlas of the Human Fovea and Peripheral Retina (2020) — shared types between central fovea/periphery but regional differences in proportions and expression"},
    {"sid": "AGING_ATLAS", "kind": "paper", "pmid": "34691611",
     "label": "A single-cell transcriptome atlas of the aging human and macaque retina (2021)"},
    {"sid": "MULTIOMICS_ATLAS", "kind": "paper", "pmid": "37388908",
     "label": "A multi-omics atlas of the human retina at single-cell resolution (2023)"},
    {"sid": "RETINA_ORGANOIDS", "kind": "paper", "pmid": "32946783",
     "label": "Cell Types of the Human Retina and Its Organoids at Single-Cell Resolution (2020)"},
    {"sid": "DEV_DUAL", "kind": "paper", "pmid": "39117640",
     "label": "Single cell dual-omic atlas of the human developing retina (2024) — developmental stage includes progenitors, adult baseline not applicable"},
    {"sid": "RETLIB41", "kind": "kb", "label": "Local marker library markers_v4.1_clean.json v4.1-clean-P0.4",
     "path": str(EYEKB / "kb/markers/markers_v4.1_clean.json")},
]

PDR_SOURCES = [
    {"sid": "GSE165784V2", "kind": "dataset",
     "label": "GSE165784 human PDR fibrovascular membrane+RRD membrane scRNA, v2 integration track Track B (harmonypy, 17 clusters, 10,069 cells; PDR-only 7,142)",
     "pmid": "35061025", "path": str(GSE_DIR / "cluster_composition_B.csv"),
     "computation": f"Card {CARD} recomputation (build_priors.py recompute_gse165784)"},
    {"sid": "PDR_HU2022", "kind": "paper", "pmid": "35061025",
     "label": "Hu et al. Single-Cell Transcriptomics Reveals Novel Role of Microglia in Fibrovascular Membrane of PDR. Diabetes 2022 (GSE165784 original)"},
    {"sid": "PDR_JCI2023", "kind": "paper", "pmid": "37917183",
     "label": "Single-cell transcriptomics analysis of PDR fibrovascular membranes. JCI Insight 2023"},
    {"sid": "PDR_SOX15", "kind": "paper", "pmid": "42601615",
     "label": "Human single-cell atlas of PDR reveals a SOX15-overexpressing stromal population. J Transl Med 2026"},
   {"sid": "PDR_MKI67MG", "kind": "paper", "pmid": "40069725",
     "label": "Single-cell analysis identifies MKI67+ microglia as drivers of neovascularization in PDR. J Transl Med 2025"},
    {"sid": "PDR_NICHE", "kind": "paper", "pmid": "40562775",
     "label": "Metabolic reprogramming of the neovascular niche promotes regenerative angiogenesis in proliferative retinopathies. Nat Commun 2025"},
    {"sid": "PRRX1", "kind": "paper", "pmid": "41230906", "in_lib": True,
     "label": "PRRX1 Orchestrates Pericyte-Myofibroblast Transition in Pathological Retinal Fibrosis. IOVS 2025 (in library)"},
    {"sid": "RAB5IF", "kind": "paper", "pmid": "41390488", "in_lib": True,
     "label": "Endothelial RAB5IF is required for pathological and developmental retinal angiogenesis. Nat Commun 2025 (in library)"},
    {"sid": "VITREOUS_T", "kind": "paper", "pmid": "39220810",
     "label": "Liquid Biopsy for PDR: Single-Cell Transcriptomics of Human Vitreous. Ophthalmol Sci 2024 — PDR vitreous T cells 91.6% (control tissue: vitreous≠membrane)"},
    {"sid": "MEMLIB", "kind": "kb", "label": "Local membrane marker library markers_membrane_v1.json v1-membrane-20260923 (gene-by-gene provenance)",
     "path": str(EYEKB / "kb/markers/markers_membrane_v1.json")},
    {"sid": "MULLER_REDD1", "kind": "paper", "pmid": "35167652", "in_lib": True,
     "label": "Müller Glial Expression of REDD1 Is Required for Retinal Neurodegeneration... Diabetes 2022 (in library; reactive glia background)"},
    {"sid": "GLIA_RDG", "kind": "paper", "pmid": "32069977", "in_lib": True,
     "label": "scRNA-seq in Human Retinal Degeneration Reveals Distinct Glial Cell Populations. Cells 2020 (in library; human retinal degeneration glial states)"},
    {"sid": "DR_RETINA_SC", "kind": "paper", "pmid": "34006945", "in_lib": True,
     "label": "In-depth transcriptomic analysis of human retina reveals molecular mechanisms underlying DR. Sci Rep 2021 (in library)"},
    {"sid": "MG_EARLY_DR", "kind": "paper", "pmid": "38409074", "in_lib": True,
     "label": "scRNA-seq reveals roles of unique retinal microglia types in early DR. DMS 2024 (in library)"},
    {"sid": "TIPCELL_DEV", "kind": "paper", "pmid": "34273276", "in_lib": True,
     "label": "Specialized endothelial tip cells guide neuroretina vascularization and blood-retina-barrier formation. Nat Commun 2021 (in library; tip/stalk biological origin, development/model evidence→PDR extrapolation Grade C)"},
]

# Myeloid 15 subcluster state layer (Grade A, source=GSE165784 v2 O2 subclustering 8,547 cells/15 subclusters)
MYE_STATES = [
    ("Macrophage:homeostatic-like", "Tissue-resident macrophages SELENOP/MRC1/FOLR2/STAB1/CD163", "B13+mye sub7", [7.0], [9.6], "A"),
    ("Macrophage:foam_DAM_LAM", "Foamy/lipid phagolysosomal GPNMB/LIPA/PLD3/CTSD/TREM2/SPP1", "B5+sub10/sub12", [10.0], [14.0], "A"),
    ("Macrophage:MHCII-high_APC", "High MHC-II antigen presentation HLA-DR/DQ/CD74 (merged B1/B3/B4)", "B1+B3+B4", [25.5], [28.7], "A"),
    ("Macrophage:inflammatory_heme", "Inflammation/heme stress HMOX1/CCL3/CXCL8", "B2+sub8", [10.7], [13.2], "A"),
    ("Monocyte:classical_blood", "Peripheral blood classical monocytes FCN1/LYZ/VCAN/S100A8/9 (primary flag for blood contamination)", "B10+sub14", [6.8], [9.5], "A"),
    ("Monocyte:nonclassical", "Non-classical FCGR3A+/CD14-low", "B4", [8.2], [9.0], "A"),
    ("Microglia:homeostatic", "Resident microglia P2RY12/TMEM119/CX3CR1 at low proportions; difficult to distinguish from macrophages in membrane specimens", "B0 partial", None, None, "B"),
    ("Macrophage:RRD_stress", "High MT/hypoxic stress state in RRD specimens (S100A8/9/NUPR1/FABP5/MMP9) — not PDR-specific", "B0+B6+sub0/1/2/11", [21.7], [3.9], "A"),
]


def build_human_retina(hr):
    pooled = hr["pooled_all"]
    ps = hr["per_study"]
    studies_nonTargeted = [g for g in ps if g not in ("Chen_rgc_TARGETED",)]
    MK_ALIAS = {"Astrocyte": "Astro", "Microglia": "Micro"}
    entries = []
    for cls, cn, rng, note in RETINA_CLASSES:
        spread = [ps[g].get(cls, 0.0) for g in studies_nonTargeted]
        e = {"class": cls, "label_cn": cn,
             "pct_hrca317m": pooled[cls][1], "n_cells": pooled[cls][0],
             "expected_range_pct": rng,
             "per_study_spread_pct": [round(min(spread), 2), round(max(spread), 2)],
             "markers_local_lib": MARKER_LIB["markers"].get(MK_ALIAS.get(cls, cls), []),
             "evidence": "A",
             "source_ids": ["HRCA317M", "RETLIB41"],
             "grade_b_anchors": ["HRCA_PAPER", "FOVEA_PERIPH", "AGING_ATLAS", "MULTIOMICS_ATLAS"]}
        if note:
            e["enrichment_note"] = note
        entries.append(e)
    fine = {
        "denominator_note": "cell_type column subdivision covers only finely annotated cells within this majorclass; % represents subtype/intra-class annotated cell counts",
        "BC": {"basis": "BC subtype annotated cells", "top": [
            ["flat midget bipolar cell", 20.9], ["invaginating midget", 15.4],
            ["rod bipolar cell", 14.7], ["diffuse bipolar 2", 9.9], ["DB1", 7.3], ["DB4", 7.1],
            ["DB3b", 5.1], ["giant bipolar (GB)", 3.7], ["DB3a", 3.2], ["DB6", 2.7]]},
        "AC": {"basis": "AC annotated cells", "top": [
            ["GABAergic amacrine", 63.5], ["glycinergic amacrine", 23.0],
            ["amacrine (unclassified)", 10.0], ["starburst amacrine", 3.5]]},
        "RGC": {"basis": "RGC annotated cells", "top": [
            ["OFF midget GC", 50.2], ["ON midget GC", 38.0], ["retinal ganglion cell (untyped)", 7.8],
            ["OFF parasol", 2.5], ["ON parasol", 1.5]]},
        "HC": {"basis": "HC annotated cells", "top": [["H1", 85.2], ["H2", 14.8]]},
        "Cone": {"basis": "Cone annotated cells", "top": [["retinal cone cell", 93.3], ["S cone", 6.7]]},
    }
    states = [
        {"cell_type": "Microglia", "state": "homeostatic",
         "markers": ["P2RY12", "TMEM119", "CX3CR1", "IRF8", "C1QA/B", "TYROBP", "AIF1", "SALL1", "HEXB"],
         "evidence": "A+B", "source_ids": ["RETLIB41", "MEMLIB"],
         "note": "retina library legacy_v4 + AUC candidate merge; extremely low proportion in normal retina (HRCA 0.15%)"},
        {"cell_type": "Müller glia", "state": "homeostatic",
         "markers": ["RLBP1", "GLUL", "SOX9", "S100B", "VIM", "AQP4(low)"],
         "evidence": "A", "source_ids": ["RETLIB41", "HRCA317M"]},
        {"cell_type": "RPE", "state": "homeostatic",
         "markers": ["BEST1", "RPE65", "LRAT", "RDH5", "MITF", "TTR"],
         "evidence": "A", "source_ids": ["RETLIB41", "HRCA317M"],
         "note": "RPE should be near zero in neural retina specimens; presence triggers RPE/choroid contamination flag"},
        {"cell_type": "Astrocyte", "state": "homeostatic (perivascular)",
         "markers": ["GFAP", "AQP4", "SLC1A3", "S100B"],
         "evidence": "A", "source_ids": ["RETLIB41", "HRCA317M"],
         "note": "GFAP upregulation = reactive gliosis flag, see disease entries"},
    ]
    caveats = [
        "Single-sample proportions are strongly influenced by sampling/sorting design (NeuN± nuclear sorting, RGC enrichment, fovea vs peripheral, lobe vs macular): "
        "Cross-study spread (basis for C-level interval derivation) = min~max of pooled data from 6 groups: Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy; RGC-targeted groups excluded.",
        "HRCA 10-class vocabulary excludes endothelial/pericytes (neuroretinal integration does not include vascular classes). True whole retina contains low proportions of vascular components; "
        "Presence of small Endo/Pericyte clusters in annotated data is normal vasculature; do not apply contamination flag (contrast with disease entries).",
        "High RGC proportions in enriched samples (e.g., Chen_rgc 46.2% RGC, Shekhar legacy 43.6%) are by design; the dataset construction strategy must be checked before flagging as 'abnormal'.",
        "Abundant mast cells/eosinophils",
        "Single-sample proportions strongly influenced by sampling/sorting design (NeuN± nucleus sorting, RGC enrichment, fovea vs periphery, lobe vs macular): cross-study spread (basis for C-grade interval derivation) = min~max of pooled data from Chen_a/Chen_b/Chen_c/MMD/BCM/Shekhar_legacy 6 groups, excluding RGC-targeted groups.",
    ]
    return {
        "schema": "eyekb-prior/1.0", "entry_id": "human_retina",
        "title": "Composition baseline: Human (normal) neural retina cell composition",
        "species": "human", "tissue": "retina", "disease": None,
        "frozen_date": FROZEN_DATE, "card": CARD,
        "evidence_grades": {"A": "Local empirical recomputation (with path)", "B": "Direct report from original literature",
                            "C": "Empirical intervals derived from cross-study distribution of Grade A source data"},
        "sources": HRCA_SOURCES,
        "major_classes": entries,
        "fine_types": fine,
        "states": states,
        "caveats": caveats,
        "flags": {
            "expected_low_but_present": ["Microglia (0.05~0.8%)", "RPE (≈0, >1% indicates contamination)", "Astrocyte (0.1~1.5%)"],
            "contamination_suspect": ["High-MT photoreceptor debris zone (dissociation stress, see disease entries)",
                                       "Peripheral blood myeloid large cluster (FCN1/LYZ) — blood residue flag for whole-retina specimens"],
            "unexpected": ["Progenitor/PCNA+ large cluster (adult retina)", "Abundant mast cells/eosinophils"],
        },
        "_computed": {"total_cells": hr["total"],
                      "pooled_whole_retina_excl_targeted": hr["pooled_whole_retina"],
                      "per_study": ps},
    }


def build_human_pdr(hg):
    ca, cp = hg["comp_all"], hg["comp_pdr"]
    n_all, n_pdr = hg["n_all"], hg["n_pdr"]
    comp_entries = [
        ("myeloid", "Myeloid total (macrophage/monocyte/DC/pDC, Track B cluster assignment)", 79.5,
         "Myeloid dominance in PDR membranes is a literature consensus (B: PDR_HU2022/PDR_JCI2023) and consistent with local empirical data (A)",
         ["GSE165784V2", "PDR_HU2022", "PDR_JCI2023"]),
        ("stromal_myofibro", "Myofibroblasts (COL1A1/COL1A2/ACTA2/TAGLN/POSTN/PRRX1)", 4.4,
         "Fibrous components constitute the primary naming entity of membrane specimens; pericyte-to-myofibroblast transition is driven by PRRX1 (B)",
         ["GSE165784V2", "PRRX1", "MEMLIB"]),
        ("stromal_pericyte", "Pericytes (RGS5/PDGFRB/NOTCH3/PRRX1)", 3.5,
         "Vascular wall cells, forming the 'fibrovascular' triad with endothelial cells", ["GSE165784V2", "PRRX1", "MEMLIB"]),
        ("endothelial", "Endothelial cells (CLDN5/VWF/PECAM1; pathological states PLVAP/DLL4/NDUFA4L2)", 3.8,
         "Proliferative vascular tip; tip/stalk sub-state evidence primarily derives from developmental/OIR models (C-level extrapolation)",
         ["GSE165784V2", "TIPCELL_DEV", "RAB5IF", "MEMLIB"]),
        ("lymphoid_T", "T cells (CD3D/CD2/CD69 activation)", 4.7,
         "Present in membrane specimens; distinguish tissue-end from vitreous fluid (T 91.6%)", ["GSE165784V2", "VITREOUS_T"]),
        ("lymphoid_plasma", "Plasma cells (MZB1/JCHAIN/IGHG1)", 0.8, "Presence at low proportion aligns with expectations", ["GSE165784V2"]),
        ("proliferating", "Proliferating cluster (MKI67/TOP2A/CENPF; mixed origin)", 1.7,
         "Proliferation ratio under PDR-only criteria is lower than whole-sample (RRD stress myeloid contribution significant); MKI67+ microglia drive neovascularization (B: PDR_MKI67MG)",
         ["GSE165784V2", "PDR_MKI67MG"]),
        ("glial_candidate", "Glial candidates (Müller/reactive glial scar; CRYAB/CLU, RLBP1 absent)", 1.6,
         "Fibrotic membranes contain glial scar components (B: GLIA_RDG/MULLER_REDD1); however, incomplete markers for this cluster → flag ambiguity, avoid hard labeling",
         ["GSE165784V2", "GLIA_RDG", "MULLER_REDD1"]),
    ]
    rows = [{"compartment": k, "label_cn": cn, "pct_pdr_only": pct, "pct_all_samples": ca[k][1],
             "n_pdr": cp[k][0], "evidence": "A (quantitative) + B (qualitative)", "note": note, "source_ids": sids}
            for k, cn, pct, note, sids in comp_entries]
    states = [{"cell_type": ct, "state": st, "markers_desc": md, "clusters": cl,
               "pct_all_samples": pa, "pct_pdr_only": pp, "evidence": ev,
               "source_ids": ["GSE165784V2", "MEMLIB"] + (["PDR_HU2022"] if "Microglia" in ct else [])}
              for ct, st, cl, pa, pp, ev, md in
              [(a[0], a[1], a[2], a[3], a[4], a[5], None) for a in []]]  # placeholder
    states = []
    for name, desc, clusters, pa, pp, ev in MYE_STATES:
        ct, st = name.split(":", 1)
        states.append({"cell_type": ct, "state": st, "markers_desc": desc, "clusters": clusters,
                       "pct_all_samples": pa, "pct_pdr_only": pp, "evidence": ev,
                       "source_ids": ["GSE165784V2", "MEMLIB", "PDR_HU2022"]})
    return {
        "schema": "eyekb-prior/1.0", "entry_id": "human_pdr_membrane",
        "title": "Composition baseline: human PDR fibrovascular membrane",
        "species": "human", "tissue": "fibrovascular_membrane", "disease": "proliferative diabetic retinopathy",
        "frozen_date": FROZEN_DATE, "card": CARD,
        "evidence_grades": {"A": "Local empirical recomputation (with path)", "B": "Direct report from original literature", "C": "Cross-study empirical range"},
        "sources": PDR_SOURCES,
        "major_compartments": rows,
        "myeloid_states": states,
        "caveats": [
            "GSE165784 = PDR membrane + RRD(rhegmatogenous retinal detachment) membrane mixed dataset; RRD accounts for 29.1% of cells."
            "PDR-specific readings use PDR-only scope (n=7,142); stress states in B0/B6/sub0/1/2/11 are driven by RRD samples, not PDR biology (v2 draft audit trail).",
            "Membrane specimens ≠ whole retina: Absence of independent clusters for Rod/BC/AC/HC neurons is expected; do not flag as unexpected.",
            "Large inter-donor variability in n=1~2 PDR donors; proportion intervals only provide 'order-of-magnitude' precision; no second internally computed PDR membrane dataset available for cross-validation within the library (B-level literature anchors did not provide precise %).",
            "PI reminder: Self-annotation in public PDR data may be inaccurate — B-level entries serve only for qualitative direction; numerical adjudication relies on A-level local recalculation.",
        ],
        "flags": {
            "expected": ["Myeloid dominance (70~85%)", "Endothelial + Pericyte + Myofibroblast triad", "Foamy/DAM-LAM macrophages", "High MHC-II APCs", "Minor T/plasma cell presence"],
            "unexpected": ["Large retinal neuronal cluster (>5% → specimen likely contains retinal body, conflicting with 'membrane' designation)",
                            "Progenitor/organoid features (should not be present in membrane specimens)",
                            "Large RPE cluster (>3% → suspect non-membrane tissue or sampling included RPE-choroid)"],
            "contamination_suspect": ["Blood-derived myeloid lineage (FCN1/LYZ/S100A8 high classical monocytes) — residual blood in surgical specimens; interpret proportions with caution",
                                       "Platelet gene signals (PF4/PPBP)", "Contamination by dominant vitreous T-cell component (compare VITREOUS_T: Vitreous T 91.6%)"],
        },
        "_computed": {"n_all": n_all, "n_pdr": n_pdr,
                      "comp_all": ca, "comp_pdr": cp},
    }


def build_disease_pdr(hg):
    """K2 disease entry seeds: proliferative diabetic retinopathy (across three tissue ends: membrane/vitreous/adjacent retina)"""
    return {
        "schema": "eyekb-prior/1.0", "entry_id": "proliferative_DR",
        "title": "Disease prior: Proliferative diabetic retinopathy (PDR)",
        "disease": "proliferative diabetic retinopathy",
        "tissue_scope": ["fibrovascular_membrane", "vitreous", "retina_adjacent"],
        "species": "human", "frozen_date": FROZEN_DATE, "card": CARD,
        "evidence_grades": {"A": "Local empirical recalculation", "B": "Direct report from original literature", "C": "Model/developmental evidence extrapolation", "D": "Review background (qualitative only)"},
        "sources": PDR_SOURCES,
        "expected_cell_state_matrix": [
            {"tissue": "fibrovascular_membrane",
             "expected": [
                 "Macrophages: tissue-resident (SELENOP/FOLR2) + recruited classical monocytes (FCN1/LYZ) + foamy DAM-LAM (GPNMB/TREM2/SPP1) + MHC-II-high APCs + heme-associated stress (HMOX1)",
                 "Endothelial: pathological state (PLVAP/NDUFA4L2/HIF1A/ICAM1/VCAM1) + tip/stalk sub-states (DLL4; Grade C extrapolated from TIPCELL_DEV/RAB5IF)",
                 "Pericyte→Myofibroblast continuous transition (PRRX1-driven, B: PRRX1)",
                 "Stromal: High extracellular matrix COL1A1/COL3A1/FN1",
                 "Lymphoid: T cells (CD69 activated), low plasma cell proportion",
                 "Proliferating: MKI67+ population present (including MKI67+ microglia, B: PDR_MKI67MG)",
                 "Glial: Müller/reactive glial scar components (GFAP↑, B: GLIA_RDG)"],
             "evidence": "A+B", "source_ids": ["GSE165784V2", "PDR_HU2022", "PDR_JCI2023", "PRRX1", "PDR_MKI67MG", "GLIA_RDG", "TIPCELL_DEV", "RAB5IF"]},
            {"tissue": "vitreous",
             "expected": ["Absolute T cell dominance (91.6%, B: VITREOUS_T), neutrophils nearly absent",
                          "Interpretation: Vitreous and membrane specimen compositions are entirely different — tissue origin must be distinguished first"],
             "evidence": "B", "source_ids": ["VITREOUS_T"]},
            {"tissue": "retina_adjacent",
             "expected": ["Early-mid DR retina: Microglial state changes without large-scale myeloid influx (B: MG_EARLY_DR/DR_RETINA_SC)",
                          "Müller glia reactivity (REDD1/gliosis, B: MULLER_REDD1)",
                          "Neuron proportion does not significantly increase due to PDR itself — membrane ≠ retina"],
             "evidence": "B", "source_ids": ["MG_EARLY_DR", "DR_RETINA_SC", "MULLER_REDD1"]},
        ],
        "unexpected_flags": [
            {"flag": "Large clusters of retinal neurons (Rod/Cone/BC/AC/HC)", "when": "Membrane specimen >5%", "action": "Flag: Specimen suspected to contain retina proper, report to PI"},
            {"flag": "High background of photoreceptor outer segments/lysis fragments (excluding HBA)", "when": "Diffuse mitochondrial+ROS stress signature", "action": "Dissociation stress flag, no disease flag"},
            {"flag": "Progenitor/organoid features", "when": "Any clinical membrane specimen", "action": "Suspected sample mixture/annotation error, flag and escalate"},
            {"flag": "Mast cell/eosinophil enrichment clusters", "when": "Allergic background", "action": "unexpected-report"},
        ],
        "contamination_flags": [
            {"flag": "Peripheral blood (classical monocytes FCN1/LYZ/S100A8/9 + platelets PF4/PPBP + neutrophils FCGR3B/CSF3R)",
             "meaning": "Blood influx in surgical specimens — myeloid count interpretation must first deduct blood-derived components (B: GSE165784 v2 B10/sub14 Grade A measured)"},
            {"flag": "RPE/choroidal pigmented components (BEST1/RPE65/TYR+melanin)",
             "meaning": "Penetrating sampling/concurrent rhegmatogenous detachment procedures"},
            {"flag": "Vitreous-derived T dominance (control 91.6%)",
             "meaning": "Residual liquid-phase components in vitrectomy specimens"},
        ],
        "signatures": {
            "tissue_resident_mac": ["SELENOP", "MRC1", "FOLR2", "CD163", "STAB1", "VSIG4", "CD5L"],
            "recruited_monocyte": ["FCN1", "VCAN", "S100A8", "S100A9", "CD14", "SELL", "S100A12"],
            "foam_DAM_LAM": ["GPNMB", "LIPA", "CTSD", "LGMN", "PLD3", "TREM2", "SPP1", "APOE", "MMP9"],
            "heme_stress_mac": ["HMOX1", "FTL", "FTH1", "CD163"],
            "MHCII_high_APC": ["HLA-DRA", "HLA-DRB1", "CD74", "HLA-DQA1", "HLA-DPB1"],
            "patho_endothelial": ["PLVAP", "NDUFA4L2", "HIF1A", "ICAM1", "VCAM1", "DLL4", "ESM1"],
            "pericyte_to_myofibro": ["PRRX1", "ACTA2", "TAGLN", "POSTN", "COL1A1", "COL1A2", "CTHRC1", "TIMP1"],
            "reactive_glia": ["GFAP", "VIM", "CRYAB", "CLU", "TIMP1"],
            "blood_platelet": ["PPBP", "PF4"],
            "signature_source": "markers_membrane_v1.json (canonical/data_driven/pmid_context tri-state provenance) + v2 measured clusters",
        },
        "caveats": [
            "Tip/stalk endothelial sub-states: limited direct single-cell evidence from human PDR membranes (DLL4+ tip biology mostly derived from development/OIR); marked Grade C — expected presence but no interval defined for proportions.",
            "Composition differences between PDR and RRD membranes lack sufficient independent controls — any 'disease-specific cluster' determination must undergo disease-endpoint comparison before being written (lesson from v2 draft RRD stratification).",
            "PI: PDR annotation itself may be inaccurate → this prior serves as a control and QC flag, not ground truth; when conflicting with data, output a 'prior-vs-data conflict list' for escalation.",
        ],
    }


# ------------------------------------------------------------------ MD rendering
def render_md(entry):
    L = [f"# {entry['title']}", "",
         f"> schema: `{entry['schema']}` | entry_id: `{entry['entry_id']}` | Frozen: {entry['frozen_date']} | Source card: {entry['card']}",
         "> This file is automatically rendered by `/mnt/D/EyeKB/scripts/priors/build_priors.py` from the same-named .json —— To modify content, edit JSON+script; manual MD edits will be overwritten.",
         "> **Reading Discipline**: This entry is a prior and QC flag, prohibited in scoring; if conflicting with data → report via flag, do not force fit.",
         ""]
    eg = entry.get("evidence_grades", {})
    if eg:
        L += ["## Evidence grade definitions", ""] + [f"- **{k}**: {v}" for k, v in eg.items()] + [""]
    if entry.get("disease") and "major_compartments" not in entry and "expected_cell_state_matrix" in entry:
        L += ["## Expected Cell×Status Matrix (by tissue end)", ""]
        for blk in entry["expected_cell_state_matrix"]:
            L += [f"### {blk['tissue']}  [{blk['evidence']}]", ""]
            L += [f"- {e}" for e in blk["expected"]] + [""]
        for sec in ("unexpected_flags", "contamination_flags"):
            L += [f"## {'Unexpected flags' if 'unexpected' in sec else 'Contamination flags'}", ""]
            for fl in entry[sec]:
                L += [f"- **{fl['flag']}**" + (f" — {fl['when']}" if "when" in fl else "") + f" → {fl['action'] if 'action' in fl else fl['meaning']}"]
            L += [""]
        L += ["## Signature Axes (marker panels)", ""]
        for k, v in entry["signatures"].items():
            if k == "signature_source":
                continue
            L += [f"- `{k}`: {', '.join(v)}"]
        L += ["", f"*Signature provenance: {entry['signatures'].get('signature_source','')}*", ""]
    elif "major_classes" in entry:
        L += ["## Main table: Cell type × proportion interval", "",
              "| Cell type | Chinese name | HRCA measured % | Expected interval % | Cross-study spread % | Local library marker | Evidence | Notes |",
              "|---|---|---|---|---|---|---|---|"]
        for e in entry["major_classes"]:
            L.append("| {class} | {label_cn} | {pct_hrca317m} | {rng} | {sp} | {mk} | {ev} | {nt} |".format(
                rng=f"{e['expected_range_pct'][0]}–{e['expected_range_pct'][1]}",
                sp=f"{e['per_study_spread_pct'][0]}–{e['per_study_spread_pct'][1]}",
                mk=", ".join(e["markers_local_lib"][:5]), ev=e["evidence"],
                nt=e.get("enrichment_note", "—"), **e))
        L += [""]
        ft = entry.get("fine_types", {})
        if ft:
            L += ["## Subtype layer (annotated cell proportion % within class)", "", f"*{ft.get('denominator_note','')}*", ""]
            for k, v in ft.items():
                if k == "denominator_note":
                    continue
                L += [f"- **{k}** ({v['basis']}): " + "; ".join(f"{n} {p}%" for n, p in v["top"])]
            L += [""]
        if entry.get("states"):
            L += ["## State layer (cell type × state)", "", "| Cell type | State | Marker | Evidence | Notes |", "|---|---|---|---|---|"]
            for s in entry["states"]:
                mk = ", ".join(s.get("markers") or [s.get("markers_desc", "")])
                L += [f"| {s['cell_type']} | {s['state']} | {mk} | {s['evidence']} | {s.get('note','—')} |"]
            L += [""]
    elif "major_compartments" in entry:
        L += ["## Main Table: Compartment × Proportion", "",
              "| Compartment | PDR-only% | Total Sample% | Cell Count (PDR) | Evidence | Description |", "|---|---|---|---|---|---|"]
        for e in entry["major_compartments"]:
            L += [f"| {e['compartment']} ({e['label_cn']}) | {e['pct_pdr_only']} | {e['pct_all_samples']} | {e['n_pdr']:,} | {e['evidence']} | {e['note']} |"]
        L += [""]
        if entry.get("myeloid_states"):
            L += ["## Myeloid State Layer", "", "| Cell Type | State | Signature/Description | Cluster | Total Sample% | PDR-only% | Evidence |", "|---|---|---|---|---|---|---|"]
            for s in entry["myeloid_states"]:
                pa = s["pct_all_samples"][0] if s["pct_all_samples"] else "—"
                pp = s["pct_pdr_only"][0] if s["pct_pdr_only"] else "—"
                L += [f"| {s['cell_type']} | {s['state']} | {s['markers_desc']} | {s['clusters']} | {pa} | {pp} | {s['evidence']} |"]
            L += [""]
    fl = entry.get("flags", {})
    if fl:
        L += ["## Flag semantics", ""]
        for key, title in [("expected", "Expected"), ("expected_low_but_present", "Expected but low proportion"),
                           ("unexpected", "Unexpected (→ unexpected flag)"),
                           ("contamination_suspect", "Contamination suspicion (→ contamination-suspect flag)")]:
            if fl.get(key):
                L += [f"**{title}**:", ""] + [f"- {x}" for x in fl[key]] + [""]
    L += ["## Notes", ""] + [f"{i+1}. {c}" for i, c in enumerate(entry.get("caveats", []))] + [""]
    L += ["## Source List", "", "| sid | Type | Grade clue | Label |", "|---|---|---|---|"]
    for s in entry["sources"]:
        src = s.get("pmid") or s.get("path", "")
        L += [f"| `{s['sid']}` | {s['kind']} | {src} | {s['label']} |"]
    L += [""]
    return "\n".join(L)


def main():
    hr = recompute_hrca()
    hg = recompute_gse165784()
    # Drift guard: Grade A numbers compared against frozen baseline
    assert hr["total"] == 3177310, hr["total"]
    assert hg["n_all"] == 10069 and hg["n_pdr"] == 7142, (hg["n_all"], hg["n_pdr"])
    assert abs(hg["comp_all"]["myeloid"][1] - 82.28) < 0.01, hg["comp_all"]["myeloid"]
    entries = {
        PRIORS / "composition" / "human_retina": build_human_retina(hr),
        PRIORS / "composition" / "human_pdr_membrane": build_human_pdr(hg),
        PRIORS / "disease" / "proliferative_DR": build_disease_pdr(hg),
    }
    for base, e in entries.items():
        base.parent.mkdir(parents=True, exist_ok=True)
        base.with_suffix(".json").write_text(
            json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        base.with_suffix(".md").write_text(render_md(e), encoding="utf-8")
        print("WROTE", base.with_suffix(".json"))
        print("WROTE", base.with_suffix(".md"))
    print("drift-check PASS | HRCA", hr["total"], "| GSE165784", hg["n_all"])


if __name__ == "__main__":
    sys.exit(main())
