#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB KB1v2-W2: disease-entry thin layer (disease × tissue matrix + PDR-membrane example entry + concept-ID mapping)

Scope = BRIEF_KB1v2_20260923.md W2 + ASTRA_ANNOTATION_GUIDANCE_v1.md T4/T6:
  - Disease entry = thin layer overlaid on tissue baseline (disease×tissue matrix); PDR membrane is merely the first example cell
  - Identity hierarchy (major class → fine subtype → deepest supportable level) + multi-state axes (co-existing allowed), prohibit treating each type × state combination as distinct entities
    Combination becomes a new type
  - Each signature includes source + evidence conditions (supports which assertion × condition × comparison target × localization anchor × counterexample)
  - Minimum usability standard for entries: do not create subtype entries without specific evidence
  - Batch expansion deferred (T6): validate D0 utility before scaling; do not merge distinct cells for PDR/RRD/ERM into a single baseline

Inputs (read-only): kb/priors/disease/proliferative_DR.json (legacy KB1 entry, copied not moved, retained as v1 archive)
Output: kb/priors/disease/PDR__fibrovascular_membrane.{json,md}
      kb/priors/disease/_DISEASE_TISSUE_MATRIX.{json,md}
      kb/priors/concepts.tsv
"""
import json
from pathlib import Path

EYEKB = Path("/mnt/D/EyeKB")
DIS_DIR = EYEKB / "kb/priors/disease"
OLD = json.loads((DIS_DIR / "proliferative_DR.json").read_text(encoding="utf-8"))
TODAY = "2026-09-23"
GEN = "build_disease_v2.py (KB1v2 t_16c3e020)"

# ---------------------------------------------------------------- Concept ID mapping
# (concept_id, canonical name, Chinese, synonyms, original naming source, hierarchy, notes)
CONCEPTS = [
    ("EYEKBC-0001", "macrophage_tissue_resident", "Tissue-resident macrophages",
     "resident macrophage; M2-like; homeostatic-like mac",
     "SELENOP+/FOLR2+/MRC1+/CD163+/STAB1+/VSIG4+/CD5L+ (markers_membrane_v1); Hu2022 'microglia-like' nomenclature",
     "identity_major", "Distinction from microglia in EYEKBC-0018 is limited to transcriptional similarity level (Astra T4: transcriptional similarity ≠ proof of developmental origin)"),
    ("EYEKBC-0002", "macrophage_recruited_monocyte", "Recruitment-type classical monocyte/monocyte-derived macrophages",
     "classical monocyte; monocyte-derived macrophage; peripherally derived mac",
     "FCN1+/VCAN+/S100A8/9+/CD14+/SELL+ (membrane v1); GSE165784 B5/B9",
     "identity_major", "Reading of the peripheral blood influx flag must precede 'disease recruitment' conclusions (confounding: surgical blood contamination)"),
    ("EYEKBC-0003", "macrophage_lipid_laden", "Foamy/DAM-LAM macrophages (state axis)",
     "foamy macrophage; lipid-associated macrophage (LAM); disease-associated macrophage",
     "GPNMB+/LIPA+/CTSD+/LGMN+/PLD3+/TREM2+/SPP1+/APOE+/MMP9+; Hu2022 subgroup naming",
     "state_on_macrophage", "State axis overlaid on 0001/0002, does not stand alone as cell type (T4 prevents inflation)"),
    ("EYEKBC-0004", "macrophage_heme_stress", "Heme-stress macrophages (state axis)",
     "erythrophagocytic macro; iron-handling mac",
     "HMOX1+/FTL+/FTH1+ (CD163 co-staining) ; GSE165784 v2 sub14",
     "state_on_macrophage", "High collinearity with hemorrhage contamination flag — reading order: technical first, then status"),
    ("EYEKBC-0005", "mhcii_high_apc", "MHC-II high antigen-presenting state (state axis)",
     "APC-like; migratory dc-like",
     "HLA-DRA/DRB1/CD74/DQA1/DPB1+", "state_on_macrophage_or_dc",
     "DC identity lacks independent specific evidence in membrane specimens → no standalone DC entry created (minimum viable standard)"),
    ("EYEKBC-0006", "endothelial_cell", "Vascular endothelial cells",
     "EC; vascular endothelium", "PECAM1/CDH5/VWF+", "identity_major", ""),
    ("EYEKBC-0007", "endothelial_pathological", "Pathological endothelium (state axis)",
     "tip-like EC; activated EC; hypoxic EC",
     "PLVAP+/NDUFA4L2+/HIF1A+/ICAM1+/VCAM1+/ESM1+; DLL4+ tip substate", "state_on_endothelial",
     "tip/stalk substates = Grade C extrapolation (development/OIR model evidence), no proportion expectation set (Astra T4 state≠type)"),
    ("EYEKBC-0008", "pericyte", "Pericytes", "pericyte; mural cell",
     "RGS5/NOTCH3/PDGFRB+", "identity_major", ""),
    ("EYEKBC-0009", "myofibroblast_transition", "Pericyte-to-myofibroblast transition (continuous axis)",
     "myofibroblast; activated pericyte; PRRX1+ stromal",
     "PRRX1+/ACTA2+/TAGLN+/POSTN+/CTHRC1+ (PRRX1-IOVS2025); SOX15+ stromal (JTM2026)",
     "state_axis_continuous", "Continuous states are not forced into binary positive/negative (T4); boundaries with 0010 fibroblasts often unresolved → allow reporting continuous/unresolved populations (T1 tripartite disposition)"),
    ("EYEKBC-0010", "fibroblast_membrane_stroma", "Membrane fibroblast/stromal cells",
     "fibroblast; stromal cell; COL1A1-high cell",
     "COL1A1/COL3A1/FN1+", "identity_major", ""),
    ("EYEKBC-0011", "muller_glia_reactive", "Reactive Müller glia (state axis)",
     "reactive gliosis; gliotic scar",
     "GFAP+/CRYAB+/CLU+/VIM+/TIMP1+ (GLIA_RDG/MULLER_REDD1 background)", "state_on_muller_glia",
     "Glial components appearing in membrane specimens = expected glial scar composition (Hu2022); homologous to MG identity in retinal specimens"),
    ("EYEKBC-0012", "microglia_homeostatic", "Homeostatic microglia (retina proper)",
     "homeostatic microglia", "P2RY12+/TMEM119+/CX3CR1+/SALL1+", "identity_major",
     "Normal retina 0.14% (D001 donor-level median); Cap for 'microglia-derived' determination in membrane specimens = transcriptional similarity (T4)"),
    ("EYEKBC-0013", "t_cell_activated", "Activated T cells (state axis)",
     "CD69+ T", "CD3D/E+/CD69+", "state_on_t_cell", "Absolute dominance of T in vitreous specimens (B: 39220810)"),
    ("EYEKBC-0014", "platelet_signal", "Platelet signal (contamination/mixed flag)",
     "platelet; megakaryocyte transcript reads", "PPBP+/PF4+", "contamination_flag", ""),
    ("EYEKBC-0015", "neutrophil_signal", "Neutrophil signaling (primarily contamination flags)",
     "PMN; granulocyte", "FCGR3B+/CSF3R+/ELANE+", "contamination_flag",
     "PDR membrane 'neutrophil extracellular trap' disease claim has weak evidence → default to blood contamination flag handling, unless independent evidence exists"),
    ("EYEKBC-0016", "erythrocyte_signal", "Erythrocyte signal (contamination flag)", "RBC contamination", "HBA1/2+/HBB+", "contamination_flag", ""),
    ("EYEKBC-0017", "rpe_contamination", "RPE/pigment epithelium admixture (contamination flag)", "pigment contamination",
     "BEST1+/RPE65+/TYR+/MLANA+", "contamination_flag", "Penetrating sampling / merged rhegmatogenous detachment operation related"),
]

# Signature → Astra T4 evidence conditions (claim type/relation/condition/comparator/localization anchor/negative example constraints)
def sig_evidence():
    base = {
        "tissue_resident_mac": dict(claim_type="identity", relation="Support",
            condition="human, fibrovascular membrane, scRNA", comparator="vs recruited monocytes (FCN1 group)",
            locator="Hu2022 (PMID 35061025) Results section; markers_membrane_v1 canonical layer",
            limits="Insufficient distinction from homeostatic microglia — SELENOP/FOLR2 also found in perivascular macrophages; source assertion capped at transcriptional similarity"),
        "recruited_monocyte": dict(claim_type="identity+contamination", relation="Limitation",
            condition="Same as above", comparator="vs tissue-resident",
            locator="markers_membrane_v1; GSE165784 v2 B5/B9 empirical measurement",
            limits="High FCN1/LYZ expression confounded with surgical blood contamination — single signature cannot determine 'disease recruitment'; must pair with blood-contamination flag check"),
        "foam_DAM_LAM": dict(claim_type="state", relation="Support",
            condition="human PDR membrane; also seen in atherosclerosis LAM (cross-disease)", comparator="vs homeostatic macrophages",
            locator="Hu2022 GPNMB+ subgroup section", limits="LAM signature not PDR-specific; 'foamy' morphological corroboration requires OCT/histology"),
        "heme_stress_mac": dict(claim_type="state", relation="Limitation",
            condition="PDR membrane (hemorrhagic background)", comparator="vs non-stressed macrophages",
            locator="GSE165784 v2 sub14 (Grade A empirical measurement)", limits="HMOX1/FTL also driven by dissociation stress and blood presence — rule out technical factors first"),
        "MHCII_high_APC": dict(claim_type="state", relation="Support",
            condition="human PDR membrane", comparator="vs MHCII-low mac",
            locator="JCI Insight 2023 (PMID 37917183) APC subgroup", limits="High HLA-DR ≠ dendritic cell identity; single-gene CD74 affected by doublets"),
        "patho_endothelial": dict(claim_type="state", relation="Support",
            condition="human PDR membrane + model", comparator="vs quiescent endothelium",
            locator="PLVAP/NDUFA4L2 hypoxia-vascular permeability axis (multiple studies)", limits="Insufficient direct evidence for DLL4 tip state in human membranes (Grade C, developmental extrapolation)"),
        "pericyte_to_myofibro": dict(claim_type="identity+mechanism", relation="Support",
            condition="Retinal fibrosis pathology (including PDR membranes)", comparator="vs quiescent pericytes/quiescent fibroblasts",
            locator="PMID 41230906 (PRRX1-IOVS2025) main figures", limits="Continuous transition spectrum — forced binary classification creates false subtypes (T4); distinguishing 'pericyte-derived' vs 'fibroblast-derived' myofibroblasts requires lineage tracing; transcriptional mixing is indeterminate"),
        "reactive_glia": dict(claim_type="state", relation="Limitation",
            condition="human retina/degeneration contexts", comparator="vs homeostatic MG/Astro",
            locator="PMID 32069977 + 35167652", limits="GFAP upregulation non-specific (trauma/stress/development all present); glial components in membrane specimens consistent with expected glial scar"),
        "blood_platelet": dict(claim_type="technical_artifact", relation="Support",
            condition="Any surgical material", comparator="—",
            locator="markers_membrane_v1 blood-contamination panel", limits="Platelet transcript reads may originate from megakaryocyte contamination or aggregates — use only as flag, not population"),
    }
    return base


# ---------------------------------------------------------------- PDR membrane example entry
def build_pdr_entry():
    e = {
        "schema": "eyekb-disease/1.1",
        "entry_id": "PDR__fibrovascular_membrane",
        "title": "Disease entry (example cell): PDR proliferative stage × fibrovascular membrane (human)",
        "disease": "proliferative diabetic retinopathy (PDR), proliferative stage",
        "tissue": "fibrovascular membrane",
        "tissue_scope": ["fibrovascular_membrane"],
        "species": "human",
        "organism_stage": "adult",
        "development_stage": "adult",  # KB3 (t_5425a7ca) W2: the entry header carries an explicit developmental stage
        "kb3_card": "t_5425a7ca",
        "stage_note": ("KB2c developmental axis (adjudication Q3): disease grid keys include developmental axis —— this grid=adult (proliferative PDR are all adult"
                       "Surgical materials; GSE165784/JCI cohort donors are all adults). Developmental samples excluded from adult disease grid (PI Directive Clause 2);"
                       "If pediatric membrane materials are collected in the future, create a separate entry; do not merge into this one."),
        "frozen_date": TODAY, "card": "t_16c3e020", "supersedes": "proliferative_DR (t_39182aa2, v1 archive)",
        "role": "Matrix example cell = 'one cell' rather than project-centric (PI 2026-09-23 ophthalmology general standard)",
        "matrix_anchor": "_DISEASE_TISSUE_MATRIX.md",
        "context": {
            "Sampling material": "Fibrovascular membrane obtained via vitrectomy combined with membrane peeling (may include internal limiting membrane/epiretinal membrane; "
                       "GSE165784 sample names PDR-ERM and PDR-FM refer to two surgical terms for the same material, both belonging to membrane).",
            "Disease stage": "Proliferative stage (neovascularization/fibrosis phase); non-NPDR/DME stage",
            "Treatment background": "Prior laser/anti-VEGF status is not systematically recorded in source data — marked as unrecorded",
            "Methodological standard": "scRNA-seq cell suspension (non-nuclear); differs from D001 retina nuclear suspension and D002 ocular surface cell suspension standards",
        },
        "usage_scope": ("This entry = context consistency check material (non-whitelist): generates only expected/unexpected/contamination flags, "
                        "Prohibited from scoring; labels must not be forcibly changed to identities within the list (Astra T2)."),
        "sampling_mismatch_warning": {
            "statement": ("**Sampling material mismatch warning (core of Astra T2 adjudication)**: Disease site = retina, but surgical specimen = fibrovascular membrane."
                          "The healthy retinal composition baseline (kb/baselines/retina, D001) is [NOT] applicable as a composition compliance threshold for this membrane specimen — "
                          "Membrane dominated by macrophage/vascular/stromal components; near-zero photoreceptor and other neural retina classes are material properties rather than anomalies."),
            "correct_uses_of_retina_baseline": ["Identity reference (hierarchical judgment of transcriptional similarity between a myeloid cluster and retinal-resident microglia)",
                                               "Background control from adjacent retina specimens (retina_adjacent cell)"],
            "wrong_uses": ["'Threshold compliance' acceptance of cell proportions in membrane specimens", "Judging Rod/Cone absence as a quality defect (check material first!)"],
            "comparable_material_anchor": ("Primary anchor for comparable materials on this card = GSE165784 (PDR membrane, PMID 35061025) + JCI Insight 2023 "
                                           "Independent PDR membrane cohort (PMID 37917183) — same species/material/stage, Astra T2 priority tier 1."),
        },
        # ---- Astra T4 skeleton: identity hierarchy + state axis (do not synthesize new types)
        "identity_hierarchies": [
            {"concept_id": "EYEKBC-0001", "canonical": "macrophage_tissue_resident",
             "supportable_level": "major→subcluster", "note": "Cap for resident/recruited origin determination = transcriptional similarity"},
            {"concept_id": "EYEKBC-0002", "canonical": "macrophage_recruited_monocyte",
             "supportable_level": "major", "note": "Confounded with blood contamination; technical exclusion required first"},
            {"concept_id": "EYEKBC-0006", "canonical": "endothelial_cell",
             "supportable_level": "major→pathologic state", "note": ""},
            {"concept_id": "EYEKBC-0008", "canonical": "pericyte", "supportable_level": "major", "note": ""},
            {"concept_id": "EYEKBC-0010", "canonical": "fibroblast_membrane_stroma",
             "supportable_level": "major", "note": "Continuous with 0009 transition axis; boundary may be unresolved"},
            {"concept_id": "EYEKBC-0011", "canonical": "muller_glia (reactive)",
             "supportable_level": "major+state", "note": "Glial scar components"},
            {"concept_id": "EYEKBC-0013", "canonical": "t_cell", "supportable_level": "major", "note": "Low proportion"},
        ],
        "state_axes": [
            {"axis": "proliferation (MKI67+)", "applies_to": ["endothelial", "stromal", "microglia (reported as exception, Grade B)"],
             "binary_forced": False, "note": "Cell cycle signals ≠ angiogenesis conclusion (T7 Step 4: requires identity + proliferation + spatial three-layer evidence)"},
            {"axis": "hypoxia/patho-activation (HIF1A/PLVAP/NDUFA4L2)", "applies_to": ["endothelial"]},
            {"axis": "ECM remodeling / PMT transition (PRRX1/ACTA2/POSTN/CTHRC1)",
             "applies_to": ["pericyte", "stromal"], "continuous": True},
            {"axis": "lipid_laden/foam (GPNMB/TREM2/SPP1)", "applies_to": ["macrophage"]},
            {"axis": "heme_stress (HMOX1/FTL)", "applies_to": ["macrophage"], "tech_confound": "Hemorrhage + dissociation"},
            {"axis": "MHC-II antigen presentation", "applies_to": ["macrophage"]},
            {"axis": "reactive gliosis (GFAP/CRYAB/CLU)", "applies_to": ["muller_glia", "astrocyte"]},
        ],
        "expected_cell_state_matrix": OLD["expected_cell_state_matrix"][:1] + [
            {"tissue": "__cross_material_note__ (not a cell entry)",
             "expected": ["Vitreous grid reference: T-cell absolute dominance 91.6% (B: VITREOUS_T) —— Belongs to PDR__vitreous grid, "
                          "Before meeting the independent entry threshold, use only as material control",
                          "retina_adjacent cell reference: Microglia state changes in early-moderate DR without large-scale myeloid influx (B: MG_EARLY_DR/DR_RETINA_SC); "
                          "Müller glia reactivity (B: MULLER_REDD1) — belongs to the PDR__retina_adjacent grid"],
             "evidence": "B", "source_ids": ["VITREOUS_T", "MG_EARLY_DR", "DR_RETINA_SC", "MULLER_REDD1"]}],
        "signatures": OLD["signatures"],
        "signature_evidence_T4": sig_evidence(),
        "unexpected_flags": [
            {**f, "disposition_queue_v2": "candidate_biology"} for f in OLD["unexpected_flags"]
        ] + [
            {"flag": "Identities outside baseline/literature lists (e.g., unexpected lymphoid/extramedullary groups)",
             "when": "Any cluster that cannot be assigned to resolved concepts", "action": "unexpected-report",
             "disposition_queue_v2": "out_of_baseline_coverage",
             "note": "Off-list identities trigger flags only; must not be forcibly remapped to on-list identities (T2)"}],
        "unexpected_disposition_queues": {
            "out_of_baseline_coverage": "Exceeds baseline coverage → record and assess for baseline expansion (backfill W1 mapping)",
            "conflicts_with_literature": "Conflicts with existing data → item-by-item citation verification + conflict list reported to PI",
            "technical_suspect": "Technical suspicion (doublets/ambient/stress) → enter T1 technical credibility gate re-review queue",
            "candidate_biology": "Candidate biological phenomenon → follow T3 disposition chain (confirm observation→exclude technical→identity state→clinical context→independent validation)",
        },
        "contamination_flags": OLD["contamination_flags"],
        "minimum_usability_criteria": {
            "statement": ("Minimum usability standard for entries (Astra T4/P4): ① At least one identity or state evidence directly comparable to this material (species + material + disease"
                          "Conditions specified) ② Each signature includes source + evidence conditions ③ No subtype grid created without specific evidence ④ Name merging based solely on expression program/lineage/"
                          "Context, not by lexical similarity (concept ID mapping table) ⑤ Interval unestimable = valid state, does not block entry validity."),
            "gate_for_new_cell": "New grid construction = direct evidence set for this disease×material exists; batch expansion paused (T6), awaiting PRIOR_DIFF control to prove D0 utility",
        },
        "caveats": OLD["caveats"] + [
            "v1.1 (this entry): Rearranged per T4 into two levels: identity hierarchy + state axis; old proliferative_DR.json retained as v1 archive (copy, not move).",
            "Concept ID mapping = initial version (17 concepts); naming across different articles is not automatically merged — merge criteria = expression program/lineage/context (T4).",
        ],
        "sources": OLD["sources"],
        "concept_refs": [c[0] for c in CONCEPTS],
    }
    return e


MATRIX_ROWS = [
    # (disease, tissue/material, status, note)
    ("PDR", "fibrovascular_membrane", "FILLED (example grid)", "PDR__fibrovascular_membrane.md"),
    ("PDR", "vitreous", "placeholder", "Qualitative anchor exists (B: PMID 39220810, T 91.6%); independent entries below minimum usability threshold — temporarily recorded in example grid cross_material_note"),
    ("PDR", "retina_adjacent", "placeholder", "Grade B literature anchors (MG_EARLY_DR/DR_RETINA_SC/MULLER_REDD1)"),
    ("NPDR/DME", "retina", "placeholder", "Different materials across different PDR stages must not be merged (T6: do not synthesize a single composition baseline)"),
    ("nAMD/GA", "RPE_choroid", "placeholder", "Tissue baseline side RPE/choroid currently skeleton → backfill W1 skeleton first before discussing disease grids"),
    ("RRD", "subretinal/ERM membrane", "placeholder", "GSE165784 RRD-ERM n=1 — Single sample may only report 'observed in this sample'; no universal entry created (T3)"),
    ("ERM (idiopathic)", "membrane", "placeholder", "Same material as PDR membrane but different disease — reuse concept ID, establish separate cell"),
    ("glaucoma", "optic_nerve_RGC", "placeholder", "Optic_nerve skeleton on tissue side backfilled with mapping (HRA006282 locally computable)"),
    ("keratoconus", "cornea", "placeholder", "Ocular_surface baseline on tissue side filled → lowest evidence threshold for this cell"),
    ("Fuchs/endothelial decompensation", "corneal_endothelium", "placeholder", "D002 endothelium has only 404 cells; expand baseline side first"),
    ("Uveitis (intermediate type)", "vitreous", "placeholder", "Shares material concept with PDR__vitreous"),
    ("cataract", "lens", "placeholder", "Lens skeleton on tissue side = LEC domain adjudication"),
]


def render_pdr_md(e):
    L = [f"# {e['title']}", "",
         f"> schema: `{e['schema']}` | entry_id: `{e['entry_id']}` | Frozen: {e['frozen_date']} "
         f"| Card: {e['card']} | supersedes: {e['supersedes']} | Developmental stage: **organism_stage={e.get('organism_stage','—')}"
         + (f" | development_stage={e['development_stage']}** (KB3 explicit)" if e.get("development_stage") else "**"),
         f"> Generated by `/mnt/D/EyeKB/scripts/disease/{GEN.split()[0]}`; manual MD edits will be overwritten.", "",
         f"> **Developmental axis**: {e.get('stage_note','')}", "",
         f"**{e['usage_scope']}**", "",
         "## Disease × tissue matrix positioning", "",
         f"This entry is the **first example cell** of the matrix ({e['role']}). Matrix overview: `_DISEASE_TISSUE_MATRIX.md`.", "",
         "## Context (T4)", ""]
    for k, v in e["context"].items():
        L.append(f"- **{k}**: {v}")
    L += ["", "## Sampling material mismatch warning (must read)", "", e["sampling_mismatch_warning"]["statement"], ""]
    L.append("**Correct usage**: " + "; ".join(e["sampling_mismatch_warning"]["correct_uses_of_retina_baseline"]))
    L.append("")
    L.append("**Incorrect usage**: " + "; ".join(e["sampling_mismatch_warning"]["wrong_uses"]))
    L.append("")
    L.append("**Primary anchor for comparable materials**: " + e["sampling_mismatch_warning"]["comparable_material_anchor"])
    L += ["", "## Identity Hierarchy (T4: Hierarchical identity, indicating deepest supportable level per layer)", "",
          "| Concept ID | Canonical Identity | Supportable Level | Notes |", "|---|---|---|---|"]
    for h in e["identity_hierarchies"]:
        L.append(f"| {h['concept_id']} | {h['canonical']} | {h['supportable_level']} | {h['note']} |")
    L += ["", "## State Axes (Co-existing; continuous states not forced into binary classification)", ""]
    for s in e["state_axes"]:
        extra = " [Continuous axis]" if s.get("continuous") else ""
        L.append(f"- **{s['axis']}** → Applies to {', '.join(s['applies_to'])}{extra}"
                 + (f"; ⚠ {s['note']}" if s.get("note") else "")
                 + (f"; technical aliasing: {s['tech_confound']}" if s.get("tech_confound") else ""))
    L += ["", "## Expected Matrix (This Cell)", ""]
    m = e["expected_cell_state_matrix"][0]
    for x in m["expected"]:
        L.append(f"- {x}")
    L.append(f"- Evidence {m['evidence']} | Source: {', '.join(m['source_ids'])}")
    L += ["", "## Cross-material comparison notes (not part of this slot, entries not created)  ", ""]
    for x in e["expected_cell_state_matrix"][1]["expected"]:
        L.append(f"- {x}")
    L += ["", "## Signature × Evidence Conditions (T4: Not just PMID — claim type/conditions/comparison target/localization anchor/counterexample limitations)", "",
          "| Signature | Marker | Claim Type | Relation | Condition | Comparison Target | Localization Anchor | Counterexample/Limitation |",
          "|---|---|---|---|---|---|---|---|"]
    for name, cond in e["signature_evidence_T4"].items():
        mk = ", ".join(e["signatures"].get(name, []))
        L.append(f"| {name} | {mk} | {cond['claim_type']} | {cond['relation']} | {cond['condition']} "
                 f"| {cond['comparator']} | {cond['locator']} | {cond['limits']} |")
    L += ["", "## Unexpected Flags (Including Four-Category Disposition Queue)", "",
          "| Flag | Trigger Condition | Disposition | Queue |", "|---|---|---|---|"]
    for f in e["unexpected_flags"]:
        L.append(f"| {f['flag']} | {f['when']} | {f['action']} | {f['disposition_queue_v2']} |")
    L += ["", "**Cohort semantics**: ", ""]
    for k, v in e["unexpected_disposition_queues"].items():
        L.append(f"- `{k}`: {v}")
    L += ["", "## Contamination Flags", ""]
    for f in e["contamination_flags"]:
        L.append(f"- **{f['flag']}** → {f['meaning']}")
    L += ["", "## Minimum Usability Criteria for Entries", "",
          e["minimum_usability_criteria"]["statement"], "",
          "Threshold for opening new cells: " + e["minimum_usability_criteria"]["gate_for_new_cell"], "",
          "## Notes", ""]
    for i, c in enumerate(e["caveats"], 1):
        L.append(f"{i}. {c}")
    L += ["", "## Source List", "", "| sid | Type | Label |", "|---|---|---|"]
    for s in e["sources"]:
        L.append(f"| `{s['sid']}` | {s.get('kind','')} | {s.get('label','')} |")
    L.append("")
    return "\n".join(L)


def render_matrix_md():
    L = ["# Disease × Tissue/Material × Developmental Stage Matrix (Thin-Layer Architecture Overview)", "",
         f"> schema: eyekb-disease-matrix/1.1 | Generated: {TODAY} | Card: t_be336eee | Generator: {GEN}",
         "> Ophthalmology general architecture (PI 2026-09-23): Disease entries = thin layers overlaid on tissue baselines (kb/baselines/); "
         "**Batch expansion deferred** (Astra T6) — first validate reading benefit (PRIOR_DIFF) using one PDR membrane grid cell, then incrementally expand via sample entry points.",
         "> **KB2c Developmental Axis (Adjudication Q3)**: grid keys=(disease, material, organism_stage) triple key; all current live grids=adult; "
         "Developmental/fetal samples do not enter adult disease grids (PI directive: 'even a single tissue is incorrect').", "",
         "| Disease | Tissue/Material Cell | Developmental Stage | development_axis (KB3) | Status | Description |", "|---|---|---|---|---|---|"]
    for d, t, st, n in MATRIX_ROWS:
        L.append(f"| {d} | {t} | adult | adult | **{st}** | {n} |")
    L += ["", "## KB3 Development Axis Reserved Cells (t_5425a7ca — establish cells only, do not fill content)", "",
          "| Disease | Material Cell | development_axis | Status |",
          "|---|---|---|---|",
          "| ROP (retinopathy of prematurity) | developing_retina_vascular | **fetal_neonatal** | "
          "RESERVED —— developmental axis retinal vascular proliferative disease, never pooled or cross-referenced with adult PDR grid; grid entry prerequisite=developmental data/literature anchor + adjudication |",
          "",
          "> Placeholder implementation of Architecture Rule 6: Adult grid array rows=12 remains fixed (regression lock), reserved slots use independent keys "
          "development_axis_reservations (dual lock).", ""]
    L += ["", "## Architecture Rules", "",
          "1. Decouple tissue baselines from disease entries: Disease cells do not repeat tissue proportions, only write expected/flags/signatures for Disease×Material (identity+status two levels).",
          "2. Same disease different materials = different cells (PDR membrane ≠ PDR vitreous ≠ adjacent retina; Astra T2 sampling material anchoring).",
          "3. Same material different diseases not merged (PDR membrane and idiopathic ERM membrane reuse concept ID but separate cells; T6).",
          "4. Cell opening threshold = minimum usability standard for entries (see example cells), no specific evidence does not create subtype cells alone (T4/P4).",
          "5. Each cell links to: Tissue baseline file ↔ RAG reason-tag (evidence_meta sidecar) ↔ Literature index page ↔ Concept table (W5 four-way link).",
          "6. **Developmental axis separate column (KB2c)**: grid keys include organism_stage; adult disease grids only accept adult materials, "
          "Developmental disease samples (e.g., pediatric ROP membrane) form separate new grids, prohibited from merging into adult grids (PI red line).", ""]
    return "\n".join(L)


def main():
    DIS_DIR.mkdir(parents=True, exist_ok=True)
    e = build_pdr_entry()
    (DIS_DIR / "PDR__fibrovascular_membrane.json").write_text(
        json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIS_DIR / "PDR__fibrovascular_membrane.md").write_text(render_pdr_md(e), encoding="utf-8")
    mx = {"schema": "eyekb-disease-matrix/1.1", "generated": TODAY, "generator": GEN,
          "card": "t_be336eee",
          "stage_axis_note": ("KB2c adjudication Q3: Grid key = (disease, material, organism_stage) triple key."
                              "All current grid entries = adult (all disease/surgical materials are from adults); developmental/fetal samples are excluded from the adult disease grid"
                              "(PI directive clause 2: 'Even a single tissue is incorrect')."),
          "rows": [{"disease": d, "material": t, "status": s, "note": n,
                    "organism_stage": "adult", "development_axis": "adult"}
                   for d, t, s, n in MATRIX_ROWS],
          # ---- KB3 (t_5425a7ca): explicit column for developmental axis + reserved cells (rows==12 regression lock unchanged) ----
          "kb3_note": ("KB3 (t_5425a7ca): Development axis promoted to explicit matrix column development_axis; current 12 grid cells all adult (hardcoded); "
                       "Disease grids on the developmental axis use development_axis_reservations placeholders (to prevent mixing with adult grids, regression double-lock)."),
          "kb3_card": "t_5425a7ca",
          "development_axis_reservations": [{
              "disease": "ROP", "material": "developing_retina_vascular",
              "development_axis": "fetal_neonatal", "organism_stage": "developing",
              "status": "RESERVED (cell established without content)",
              "note": ("Retinopathy of prematurity = developmental-axis vascular proliferative disease (PI red-line associated grid): Strictly separated from adult PDR membrane grid, "
                       "Never merge cells, never serve as mutual references (these fetal/preterm infant entities are incorrect even if from the same tissue as adult counterparts)."
                       "Cell-filling prerequisite = obtain developmental-stage material/literature anchor (e.g., ROP retinal organoid or cadaveric single-cell data—both must first pass"
                       "Discipline for separating the developmental axis; grid-filling actions must pass adjudication and synchronously update regression double-locks (rows/reservations)."),
              "reserved_by": {"card": "t_5425a7ca", "date": "2026-09-24"}}]}
    (DIS_DIR / "_DISEASE_TISSUE_MATRIX.json").write_text(
        json.dumps(mx, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIS_DIR / "_DISEASE_TISSUE_MATRIX.md").write_text(render_matrix_md(), encoding="utf-8")
    ct = Path("/mnt/D/EyeKB/kb/priors/concepts.tsv")
    with open(ct, "w", encoding="utf-8") as f:
        f.write("concept_id\tcanonical_name\tcommon_name\tsynonyms\tsource_namings\tlevel\tnotes\n")
        for row in CONCEPTS:
            f.write("\t".join(row) + "\n")
    print("W2 written:", DIS_DIR / "PDR__fibrovascular_membrane.md", "|", ct)


if __name__ == "__main__":
    main()
