#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_claims.py — six-cell B1 → atomic claim contract (WIRE-P1 deliverable 2 · REV-1/astra finalized)
+ KNOWNISSUES-B2 batch retrieval (B2_ITEMS: assay/preparation/disease axis PATTERN page expansion, KC-B2-001..009)
+ B2 adjudication wave (ARBITRATION_RULING_C1-C14_v1, approved 2026-09-30): Lexicon upgraded to v1 —
  assay axis adds `bulk` (C9 release check); the orthogonal region axis enters the scope syntax (C8, KC-B1-008 addendum
  region_scope annotation regeneration), C12 treatment tri-state registration discipline implemented in vocabulary (claim objects in this batch=0, registered truthfully).

Single source of truth: this script = the sole persistence point for per-claim adjudication table + derivation rules (pages/ and MANIFEST
All are machine-generated artifacts, do not modify manually; to change adjudication, modify this table and rerun. Six-cell manuscript /mnt/D/EyeKB/kb/known_issues/
Read-only, no modifications. Replaces attempt-1's build_pitfalls.py (old qwen contract voided, see REV-1 correction order within card).

Contract (astra T1 atomic claim schema + T3 full enumeration + T6 visibility fields):
  claim_id / scope{species,tissue,assay,preparation,disease_or_treatment}
  failure_mode / observable_signature / risk_level
  mitigation / evidence_source_type / source_check
  home{kind: species|tissue|cell|pattern|unmapped, id}
  visibility / blind_safe / answer_dependency
  status / owner / last_reviewed / links / provenance

Posting rules (REV-1 Correction Order ③):
  - one scope per claim; cross-part tissue non-full coverage/determined by assay·disease·preparation conditions → PATTERN.
  - blind-spot declarations (6) and "Community gap" records (3) = no dimension, no failure signature → **not counted**, 
    Register pages/EXCLUSIONS.json (traceable).
  - Mapping outside the controlled vocabulary (COORDINATE_TAXONOMY_v1.md) → UNMAPPED_SCOPE; automatic injection prohibited.
  - Prohibit bare A/B/C: full enumeration of source types internal_observation|peer_reviewed_literature|
    community_lead; verification status separately recorded in source_check (bibliographic/pointer check passed ≠ claim validity).

Derivation rules (mechanical, no manual tuning):
  answer_dependency=none      → blind_safe=true,  visibility=pre_annotation
  answer_dependency=sample/dataset_specific → blind_safe=false, visibility=post_decision
  source_check: internal_observation → File pointer existence test (locator_verified/unchecked)
                peer_reviewed_literature → locator_verified (eutils bibliographic record verification during B1 construction, audit trail registered)
                community_lead → unchecked (URL existence ≠ claim validity, astra T2 original text)

Usage:
  python build_claims.py            # Rebuild pages/ + MANIFEST
  python build_claims.py --check    # Script-artifact consistency gate (including 100% link resolution)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path("/mnt/D/EyeKB/kb/known_issues")
PAGES = HERE / "pages"

# Six-cell coordinate system → canonical tissue id (COORDINATE_TAXONOMY_v1.md §6, C6/C7 adjudication finalized; only pdr renamed, others pass-through)
TISSUE_CANON = {"retina": "retina", "pdr_membrane": "fibrovascular_membrane",
                "trabecular_meshwork": "trabecular_meshwork", "cornea": "cornea",
                "vitreous": "vitreous"}
CELLS = ["human__retina", "human__pdr_membrane", "mouse__retina",
         "human__trabecular_meshwork", "human__cornea", "human__vitreous"]
CANON_TISSUES = ["retina", "RPE", "ciliary_body", "optic_nerve", "ocular_surface",
                 "trabecular_meshwork", "lacrimal_gland", "choroid", "conjunctiva",
                 "iris", "lens", "sclera", "cornea", "fibrovascular_membrane", "vitreous"]
SPECIES_PAGE = ["human", "mouse"]
# C9 Adjudication (2026-09-30 ruling): bulk added to controlled vocabulary, validation synchronously released; unlisted terms still prohibited from private addition
ASSAY_VOCAB = ["scRNA", "snRNA", "spatial", "bulk"]
# C8 Adjudication: region orthogonal axis (claim-level scope annotation, does not occupy tissue axis position; see COORDINATE_TAXONOMY_v1.md §3.1 for vocabulary)
REGION_VOCAB = ["fovea", "macula_peripheral_mix", "peripheral", "not_recorded"]
EST_BY_GRADE = {"Empirical evidence in Library A": "internal_observation",
                "Tier B bibliographic record PMID": "peer_reviewed_literature",
                "Tier C community experience": "community_lead"}
HIST_GRADE = {"internal_observation": "PIT-E1", "peer_reviewed_literature": "PIT-E2",
              "community_lead": "PIT-E3"}            # for the legend (bare letters forbidden)

# ---------------------------------------------------------------- Item-by-item adjudication table
# key=(cell, b1_order). home=("cell",) defaults to current cell; ("species",sp)/("pattern",pid)/("unmapped",None)
# ad: none|sample_specific|dataset_specific；risk: high|medium|low
# fm/obs: failure mode/observable signature; sc_ex: scope exception axis; why: attribution rationale; note: remarks
V = {}

def v(cell, i, home, ad, risk, fm, obs, why, sc_ex=None, note=""):
    V[(cell, i)] = dict(home=home, ad=ad, risk=risk, fm=fm, obs=obs,
                        why=why, sc=sc_ex or {}, note=note)

# ---- human__retina (14 items → 12 claims + 1 exclusion(declaration) + #11 merge-note→ see EXCL)
HR = "human__retina"
v(HR, 1, ("cell",), "dataset_specific", "high",
  "Reference gap artifact: The 10 majorclass vocabulary lacks an independent endothelial class; vascular clusters are forcibly assigned to microglia by the engine, creating high-confidence false positives.",
  "dr-sc cluster 31: Engine arm Micro share 83.4% vs. Reading arm Endo (E-b registered).",
  "Evidence is only measured within human × retina grid (HRCA vocabulary + current engine combination); no cross-grid dual evidence, so not promoted.")
v(HR, 2, ("cell",), "sample_specific", "high",
  "Degraded/low-quality rod clusters are hijacked into glial naming or collectively abstained (Rod quality axis).",
  "Named assignments for low-depth + high-MT clusters systematically drift between engine and reading.",
  "Photoreceptor quality axis is specific to retina.")
v(HR, 3, ("pattern", "dissociation_stress_transcriptome"), "none", "high",
  "Dissociation-induced stress transcriptome (HSPA1A/FOS/JUN class) floods screen, hijacking evidence window",
  "Cluster top genes dominated by heat shock/IEG class and co-vary with dissociation protocol",
  "Cross-species cross-tissue methodological pitfall: this mitigation self-cites Tier B human/mouse two-lineage dissociation comparison literature (PMID:32487174)",
  sc_ex={"species": ["*"], "tissue": ["*"], "assay": ["scRNA"]})
v(HR, 4, ("pattern", "macroglia_granularity_wall"), "none", "medium",
  "MG↔Astro difficult to distinguish on evidence surface (macroglia granularity wall), dictionary misleading readings have precedent",
  "High-frequency mutual labeling between macroglia two classes; exacerbated in DR reactive gliosis (GFAP↑) scenarios",
  "Wall itself holds across tissues (retina/optic nerve macroglia), evidence surface is human → pattern tagged with dual tissue",
  sc_ex={"species": ["*"], "tissue": ["retina", "optic_nerve"]})
v(HR, 5, ("cell",), "dataset_specific", "medium",
  "Low-depth ambient trap: True BCs contaminated by rod ambient RNA are misread as 'low rod amplitude → bipolar cell' blind spot zone.",
  "Named BCs appear in rod-dominated clusters; without ambient decomposition, misjudgment evidence is inseparable.",
  "Phenomenon limited to retina photoreceptor-dominated materials; cite registered evidence from internal blind spot cards.")
v(HR, 6, ("cell",), "none", "high",
  "The training pool of this system has only 863 cells for the RPE panel; 10-class engine/small panel entries cannot produce RPE conclusions.",
  "RPE class recall collapse/high-confidence misclassification (compared against external purified data).",
  "System applicability domain statement (answer-independent); evidence anchor D001 pool size = fact within grid.",
  note="Manual re-review required for all RPE named assignments in this system until external data or independent panels are promoted.")
v(HR, 7, ("pattern", "platform_nucleus_vs_cell"), "none", "high",
  "snRNA vs scRNA platform axis composition suppresses spectrum: applying nuclear suspension baseline to cell suspension data generates systematic false flags",
  "Cross-design pool-level composition boundary flags trigger frequently; eliminated after stratified routing",
  "Platform axis is a technical attribute independent of species/tissue (vocabulary §4 assay condition-driven)",
  sc_ex={"species": ["*"], "tissue": ["*"], "assay": ["snRNA", "scRNA"]})
v(HR, 8, ("cell",), "sample_specific", "medium",
  "Regional mixing false flag: fovea vs peripheral sampling differences misinterpreted as composition anomalies",
  "Composition proportions of samples from different regions within the same tissue exhibit bimodality",
  "fovea/peripheral are specific to human retinal anatomy; the orthogonal region axis was established with C8 approval (v1 §3.1),"
  "This entry adds a region_scope annotation to mitigate the syntactic executability of 'align control regions first'.",
  sc_ex={"region": ["fovea", "macula_peripheral_mix", "peripheral", "not_recorded"]},
  note="See v1 §3.1 for the four-value semantics of region_scope; not_recorded samples are reported as mixed surfaces, prohibited from being applied as single-surface fovea/peripheral assumptions.")
v(HR, 9, ("pattern", "single_donor_leverage"), "none", "medium",
  "Donor leverage: rare class hits can flip upon deletion of a single donor",
  "Leave-one-donor-out re-computation flip (LODO flip)",
  "General statistical discipline (from composition gate decision table D-2 section, text not limited to grid)",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(HR, 10, ("pattern", "nomenclature_mg_ambiguity"), "none", "high",
  "MG ambiguous abbreviation (Müller glia vs microglia) collides across systems, bare writing in deliverables causes naming ambiguity",
  "Same abbreviation points to different classes in different systems (CL back-check: CL:0000636=Müller cell)",
  "Text explicitly states 'prohibit bare MG in any deliverable' = global delivery discipline",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(HR, 11, ("cell",), "none", "low",
  "Systematic evaluation of dissociation/storage bias is on record; rare class recovery depends on nuclear suspensions—methodological confounders must be deducted before interpreting biological differences.",
  "Differences in rare class recovery rates between scRNA/snRNA are reproducible in literature comparisons of both systems.",
  "B-tier anchor entries: bibliographic evidence for #3/#7 in this cell, scope follows this cell.",
  note="Peer-reviewed anchors; do not automatically generate hard_gate.")
v(HR, 12, ("cell",), "none", "low",
  "Using point values instead of per_study_spread when citing human retinal composition intervals exaggerates certainty.",
  "Interval information is lost when cross-referencing composition point values across studies.",
  "B-tier bibliographic pool anchors this cell; rules limit citations to human retinal composition.")
v(HR, 13, ("cell",), "none", "low",
  "Version drift in online reference mapping tools (Azimuth-like) breaks reproducibility.",
  "Mapping results for the same data are inconsistent across different tool versions.",
  "Community operational tips; tool maintenance is methodological (limited to scRNA mapping paths).",
  sc_ex={"assay": ["scRNA"]}, note="community_lead: verification requirements only, not evidence basis.")

# ---- human__pdr_membrane (10 items → 8 claims + 1 absence + 1 declaration)
PM = "human__pdr_membrane"
v(PM, 1, ("cell",), "dataset_specific", "high",
  "Myeloid proportion suppresses spectrum: membrane samples 79.5-85% myeloid, global clustering suppresses rare classes",
  "Rare class proportion ≈0 in full-pool clustering; reappears after compartment-gated sub-clustering",
  "Proportions are measured from membrane grid (registered GSE165784 series).")
v(PM, 2, ("pattern", "surgical_blood_inflow"), "none", "high",
  "Surgical specimen blood influx: myeloid/platelet/neutrophil signatures mix in; counting myeloid proportions without first reporting blood-lineage vs resident layers = conclusion contamination (platelet/neutrophil anchors near-blood-only; monocyte-layer anchors reach lineage only, blood-vs-recruitment direction needs flag check)",
  "Myeloid splits into two clusters by lineage anchors — blood-lineage side (FCN1/LYZ/S100A8-9, B10/sub14 observed) vs tissue-resident side (SELENOP/MRC1/FOLR2/CD163, B13 observed); anchors cap at lineage layer (blood-contamination vs disease-recruitment aliasing disclosed by priors); PBMC-paired deduction is a conditional rule (no paired blood sample in library yet, forward-looking)",
  "Established across tissues: membrane grid measurement + vitreous strip text explicitly notes 'blood source deduction method same as membrane grid', two grids registered",
  sc_ex={"species": ["human"], "tissue": ["fibrovascular_membrane", "vitreous"]})
v(PM, 3, ("pattern", "disease_material_vs_healthy_baseline"), "none", "high",
  "Disease material ≠ healthy organ: using disease samples against healthy tissue composition as a 'benchmark' misreads material category",
  "Disease material composition naturally deviates from healthy baseline; comparisons outside the three-use protocol (identity reference/background control/QC flag) constitute misuse",
  "Rule solidified into membrane grid protocol by Astra T2, but failure mode itself is generalizable to disease materials",
  sc_ex={"species": ["*"], "tissue": ["*"], "disease_or_treatment": ["PDR"]})
v(PM, 4, ("cell",), "sample_specific", "medium",
  "Tissue-resident macrophages vs. microglia are indistinguishable within the membrane; claims that 'microglia drive neovascularization' require prior proof of residency.",
  "Lack of clustering basis for lineage anchors vs. state anchors leads to cross-sample integration artifacts (merged clusters).",
  "Evidence: measured from membrane grid (B1/B13 registered).")
v(PM, 5, ("cell",), "dataset_specific", "medium",
  "Mixed samples of RRD and PDR alter proportion metrics: proliferative fraction flips depending on metric definition.",
  "Proportion tables calculated separately for two disease definitions yield different results; high-MT clusters vary with sample processing differences.",
  "Disease definition issues limited to membrane grid (PDR/RRD materials).",
  sc_ex={"disease_or_treatment": ["PDR", "RRD"]})
v(PM, 6, ("cell",), "sample_specific", "medium",
  "Cross-lineage merging of proliferative cells (MKI67/TOP2A): cell cycle signature hijacks attribution.",
  "Co-detection of multi-lineage markers within proliferative clusters; DE results on merged clusters cannot be attributed.",
  "Evidence = membrane grid B11 row; suspected general pitfall for cross-lineage merging but lacks evidence in other grids, not promoted (hint recorded).")
v(PM, 7, ("pattern", "chamber_material_distinction"), "none", "high",
  "Composition opposite in different chambers for same disease (PDR vitreous T lineage vs membrane myeloid lineage), citation cross-contamination = conclusion reversal.",
  "PDR vitreous T 91.6% vs membrane myeloid 79.5% dual measurements on record.",
  "Text enumerates three grids of membrane/vitreous/retina with mutual cross-references → cross-tissue limited to human.",
  sc_ex={"species": ["human"], "tissue": ["fibrovascular_membrane", "vitreous", "retina"]})
v(PM, 8, ("cell",), "none", "low",
  "Writing FVM/myeloid claims without literature anchors (method + composition bibliographic pool) renders sources untraceable.",
  "External claims lack PMID anchors.",
  "Tier B bibliographic pool anchored to this cell")

# ---- mouse__retina (10 entries → 9 claims + 1 declaration)
MR = "mouse__retina"
v(MR, 1, ("pattern", "cross_species_panel_id_preflight"), "none", "high",
  "Failure to verify gene ID systems before cross-species paneling → feature space synonymy, panel hit rate drops to zero (0/2000 incident)",
  "panel_present=0; bridge = formal ortholog table + case-insensitive matching enables recovery",
  "Incident occurred in mouse grid; rule text fully generalized (any species, any panel)",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(MR, 2, ("pattern", "symbol_case_ortholog_join"), "none", "high",
  "Gene capitalization convention collisions (human all caps/mouse first letter cap) cause species flag misjudgment and join failures",
  "Before biological interpretation when panel hit rate <50%, first check capitalization/ID system to reset",
  "B5 governance ontology cross-species; full quantification of rule text",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(MR, 3, ("species", "mouse"), "none", "medium",
  "Vendor SingleR mouse-retina reference labels Müller cells as Astrocytes (observed in-library via BMR; vendor conventions not exhaustively audited): cross-system annotation drift",
  "Label category drift for the same cluster between vendor conventions and this lexicon (Müller↔Astro)",
  "General mouse-side annotation convention (text not limited to tissue) → SPECIES/mouse")
v(MR, 4, ("cell",), "none", "medium",
  "Adult mouse RGC single-cell capture rate extremely low (Drop-seq series original limitation): RGC≈0 is preparation domain shift, not biology",
  "snRNA controls can recover RGCs; acute dissociation protocols yield near-zero RGCs",
  "Limited to mouse × retina (RGC capture specific to retinal dissociation), assay=scRNA",
  sc_ex={"assay": ["scRNA"]})
v(MR, 5, ("cell",), "none", "medium",
  "MRCA reference design involves artificial enrichment (sorted targets); extrapolating class proportions to natural enzymatic digestion samples will fail",
  "Training domain BC 46.7% vs. natural composition differs by orders of magnitude; only within-design-layer controls are stable",
  "Reference design layer declaration, anchored to mouse retina reference.")
v(MR, 6, ("cell",), "none", "high",
  "Hard boundary of mouse engine applicability domain: restricted to adult (P28+) retina; vascular/immune states and P<28 are out of domain.",
  "Out-of-domain samples are still forcibly named (precedent for hard labeling outside domain); after passing the developmental axis gate, only flags are issued without renaming.",
  "Self-engine declaration (irrelevant to answer).")
v(MR, 7, ("pattern", "sklearn_proba_column_order"), "none", "medium",
  "sklearn proba column order follows alphabetical order of classes_ rather than custom class order: guessing columns = completely reversed results",
  "Swapping binary classification probability columns systematically reverses discrimination results",
  "'Print classes_ before consuming any sklearn probability output' fully quantified; two collision cases registered",
  sc_ex={"species": ["*"], "tissue": ["*"]})
v(MR, 8, ("cell",), "none", "low",
  "Mouse-side capture bias has methodological literature origins (Drop-seq lineage); use spatial transcriptomics when dissociation-insensitive evidence is required.",
  "Literature two-lineage comparison is reproducible; spatial routes recover classes lost during dissociation.",
  "Tier B bibliographic pool anchored to this cell", sc_ex={"assay": ["scRNA", "spatial"]})
v(MR, 9, ("cell",), "none", "low",
  "Community experience: pitfalls of dissociation stress and doublet tools (operational hint level).",
  "(Community post observation, not locally recalculated)",
  "C-tier content entry; community_lead only requires verification.", sc_ex={"assay": ["scRNA"]},
  note="community_lead")

# ---- human__trabecular_meshwork (8 entries → 6 claims + 1 absence + 1 declaration)
TM = "human__trabecular_meshwork"
v(TM, 1, ("cell",), "none", "high",
  "Lexicon lacks TM-specific classes (TM beam/JCT/SC endothelial rows missing): TM tissues are forcibly assigned to Fibroblast/Ciliary_Muscle/Endothelium.",
  "Top candidates for TM samples all fall into non-TM lexicon classes; 'engine out-of-domain' flag is reproducible.",
  "Lexicon facts of this system, anchored to TM cells.")
v(TM, 2, ("cell",), "none", "medium",
  "Sampling boundary contamination: TM strips include uvea/ciliary body/limbal components, anatomical adjacency determines composition.",
  "Iris sphincter/ciliary muscle signatures appearing in TM samples = normal sampling contamination.",
  "Specific to TM anatomical adjacency.", sc_ex={"preparation": ["blunt_strip_TM"]})
v(TM, 3, ("cell",), "none", "medium",
  "Nuclear suspension platforms lose TM cytoplasmic transcripts (contractile apparatus/ECM-related genes); in-library anchor establishes the 100%-nucleus caliber only.",
  "In-library scRNA comparison anchors are mostly cultured systems — culture state confounds the platform axis, so signature differences cannot be attributed to the nucleus/cell platform alone; cytoplasmic-signature under-read in nucleus data is disclosed with the confound.",
  "Specific to TM + nuclear suspension combination (general platform axis part in platform_nucleus_vs_cell).",
  sc_ex={"assay": ["snRNA"]})
v(TM, 4, ("cell",), "none", "low",
  "Zero-variance rows with [0,0] interval artifacts: false flags in adjacent very-low proportion composition controls.",
  "Baseline rows where donor_range degrades to [0,0] trigger out-of-bounds flags.",
  "Evidence anchor TM Pericyte row; criteria revision pending final decision, no upgrade")
v(TM, 5, ("cell",), "none", "medium",
  "Immortalized cell line phenotypic drift (registration-grade prior, out-of-library): TM literature extensively uses immortalized lines; drift evidence is title-level candidate references, not in-library observation",
  "Immortalized-line context references verified at title level only (full-text not reviewed; candidate anchors PMID:26396484/29847662/40650044 added by 2026-10-06 audit); no drift observation in library — passage/donor-lineage check is a material forensics cue, not a witnessed failure",
  "B-tier out-of-library prior registration limited to TM", sc_ex={"preparation": ["cultured_cell_line"]})
v(TM, 6, ("cell",), "none", "low",
  "Human outflow specialized literature bibliographic pool: anchor for TM/SC subtype vocabulary reconciliation and cross-species homology verification",
  "Cross-species claims are unadjudicable without a vocabulary reconciliation baseline",
  "Tier B bibliographic pool anchored to this cell")

# ---- human__cornea (9 items → 7 claim + 1 declaration… cornea#8 community content accounted)
CO = "human__cornea"
v(CO, 1, ("cell",), "none", "medium",
  "Corneal single-cell material = eye bank donation/transplant endothelial edge fragments (cadaveric material science); the 'normal' label masks material defects",
  "When time-to-fixation and material source are missing, unexpected flags trigger based on the registered checklist",
  "Specific to corneal material science; reporting source + time interval is mandatory mitigation")
v(CO, 2, ("cell",), "none", "medium",
  "Avascular ≠ no vascular signature: limbal/neovascular material contamination produces false endothelial/pericyte clusters",
  "CDH5/PTPRC zero detection = normal corneal gating; NEA/transplant materials show vascular signatures",
  "Specific to cornea (avascular organ)")
v(CO, 3, ("cell",), "dataset_specific", "high",
  "Entry backlash: launching new entries ignites neighborhoods (new Keratocytes entry previously pulled away a 98.7% pure pericyte cluster)",
  "Mini blind validation only proves 'can rescue' but not 'does not ignite neighbors'; post-release neighborhood cluster label drift occurs",
  "release discipline (neighborhood fire audit) belongs to the process layer KB7; the evidence case is anchored to the cornea grid",
  note="Audit rules for curator; failure observations for reading interface")
v(CO, 4, ("cell",), "none", "high",
  "Sampling stratum mixing: pooling ocular surface superclasses (cornea/limbus/sclera...) makes stratum proportions entirely spurious",
  "Whole-mount region composition is dissection-boundary-defined (limbus/conjunctiva inclusion cannot be assumed from the protocol name; no default on disk); applying baselines across regions distorts proportions",
  "D002 superclass structural fact; locking sampling domain is mandatory mitigation")
v(CO, 5, ("pattern", "panbright_epithelial_secreted"), "none", "high",
  "Broad non-specific brightness of epithelial/secretory markers: single-gene classification is compromised by cross-lineage non-specific brightness",
  "Expression rate of out-of-cluster classes > threshold; separable after core combination + non-specific brightness pre-check",
  "Transfer lacrimal gland LACRT lessons to ocular surface = two grid entries with evidence; cross-tissue limited to human",
  sc_ex={"species": ["human"], "tissue": ["cornea", "lacrimal_gland"]})
v(CO, 6, ("cell",), "none", "medium",
  "Single-donor leverage is more extreme in ocular surface: donor eye counts naturally single-digit",
  "In n≤4 donor studies, rare class hits flip upon deletion of a single donor",
  "Specific to corneal material structure (general rule in single_donor_leverage)",
  sc_ex={"preparation": ["paired_donor_tissue"]})
v(CO, 7, ("cell",), "none", "low",
  "Corneal/ocular surface subtype vocabulary must benchmark against atlas literature; culture system citations carry drift declaration",
  "Subtypes undeterminable when vocabulary lacks atlas reconciliation",
  "Tier B bibliographic pool anchored to this cell")
v(CO, 8, ("cell",), "none", "low",
  "Default generic QC/integration rules (empty-droplet, doublet, no-rep statistics) misapplied to low-cell-number corneal materials directly hit empty-drop/contamination mixing; community basis, not corneal empirical",
  "Filtered-matrix low-gene samples = empty-drop/contamination mix band; no-rep statistical-power debate applies to cornea's naturally small n (BioStars #482228/#315869 contexts; locally unrecalculated)",
  "Tier C content clause", note="community_lead")

# ---- human__vitreous (8 items → 6 claim + 1 absence + 1 declaration)
VI = "human__vitreous"
v(VI, 1, ("cell",), "none", "high",
  "Vitreous pitfall primarily concerns 'sample presence and collection contamination' rather than annotation: downgrade if any of the three questions (collection method/control/cell count) cannot be clearly answered",
  "Cassette washing vs. membrane stripping, presence of paired blood/control eye missing from specimen records",
  "General pitfall for this domain (vitreous-specific)", sc_ex={"preparation": ["vitrectomy_cassette_wash"]})
v(VI, 2, ("cell",), "none", "high",
  "Three sources of collection contamination: retinal avulsion fragments (photoreceptors/RPE), membrane tissue inclusion, intraoperative bleeding",
  "Photoreceptor/RPE signature in vitreous samples = collection flag, not new discovery",
  "Vitreous-specific; blood depletion pointer → surgical_blood_inflow")
v(VI, 3, ("cell",), "none", "high",
  "Near-zero cell baseline: no normal-vitreous single-cell composition reference registered (absence in library registration and title-level search — not an existence claim); disease comparisons lack a healthy anchor",
  "Construction-time registration lacks normal vitreous composition entries; 2026-10-06 eutils recheck (vitreous+single-cell) still shows no healthy atlas (hits all disease/protocol contexts); registered-absence wording, existence not asserted",
  "Domain gap fact (basis for vocabulary §3 conflict ② composition aspect missing)")
v(VI, 4, ("cell",), "none", "medium",
  "Low cell count and sequencing depth: proportion of low-quality empty droplets/ambient RNA amplified in sparse cell materials",
  "Left-shifted nFeature distribution per sample + high ambient estimation; rare classes survive after non-ambient gate (expression fraction × doublet joint test)",
  "Vitreous material characteristics (general ambient methodology part in retina ambient entries)")
v(VI, 5, ("pattern", "chamber_material_distinction"), "none", "high",
  "Immune dominant group carries a strong material/chamber component (not purely a disease attribute — material and disease effects may stack): same disease different materials (membrane myeloid vs vitreous T lineage).",
  "Patient-level paired samples can separate chamber effects; averaging class proportions will mask them.",
  "Shares pattern with 'same disease different materials' clause for membrane grid (one scope one claim, subject of this clause = attribution direction).",
  sc_ex={"species": ["human"], "tissue": ["fibrovascular_membrane", "vitreous", "retina"]})
v(VI, 6, ("cell",), "none", "low",
  "Vitreous-side literature protocols + immune control spectrum form bibliographic pool; two neutrophil claims coexist requiring readout method citation",
  "Different readout methods (flow cytometry vs. single-cell) yield contradictory neutrophil conclusions",
  "Tier B bibliographic pool anchored to this cell")

# ---------------------------------------------------------------- Non-entry Registry
EXCLUDED = {
    (HR, 14): ("declaration_not_claim", "Cell blind spot declaration=retrieval audit trail metadata, no failure mode no signature"),
    (PM, 9): ("absence_note", "Community discussion gap registration (no specific failure observations)"),
    (PM, 10): ("declaration_not_claim", "Cell blind spot declaration"),
    (MR, 10): ("declaration_not_claim", "Cell blind spot declaration"),
    (TM, 7): ("absence_note", "Community zero-hit registration"),
    (TM, 8): ("declaration_not_claim", "Cell blind spot declaration"),
    (CO, 9): ("declaration_not_claim", "Cell blind spot declaration"),
    (VI, 7): ("absence_note", "Specific thread not found registration (general pitfall extrapolation has separate entries)"),
    (VI, 8): ("declaration_not_claim", "Cell blind spot declaration"),
}

# ---------------------------------------------------------------- B2 Batch (KNOWNISSUES-B2 existing search items)
# Source=local disk files + registered bibliographic records B-check items (assay/preparation/disease axis priority, astra T1 directed).
# home is always pattern (branch 4 condition-driven), scope.species/tissue=["*"]—does not reference any
# pending adjudication coordinates (C1-C14 approvals unrelated to this batch); slots in vocabulary that cannot be filled (sorting/system/bulk/
# stage terms) left blank and registered in note; self-coined terms prohibited. Status=draft_pending_audit (new items, not migrated;
# audit pipeline same path, see plans/known_issues_b2_20261001/out/audit_pipeline/).
PREP_VOCAB = ["enzymatic_dissociation", "short_dissociation_cold_protease",
              "nuclear_extraction", "surgical_stripped_membrane", "excised_whole_mount",
              "vitrectomy_cassette_wash", "blunt_strip_TM", "cultured_cell_line",
              "paired_donor_tissue"]
DISEASE_VOCAB = ["PDR", "RRD", "diabetic_retinopathy_nonPNR", "glaucoma_TM",
                 "aging", "anti_VEGT_treated", "none_healthy"]
B2_ITEMS = [
    dict(pid="assay_selfreport_wording_drift", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Platform self-reported wording (single-nucleus suspension/cell suspension) inconsistent with actual preparation → nucleus-cell platform axis misattribution: ambient correction and rare-class priors applied inversely based on wrong platform.",
         obs="Case registration: one disk annotation header labeled snRNA-seq, while primary abstract and GEO Series explicitly stated cell suspension (~93,000 cells scale); adjudicated as wording error with audit trail correction (originals not modified); platform reading correction for the same dataset triggered two existing misrecords.",
         mit="Platform entries confirmed face-by-face via primary abstract + GEO series explicit text; annotations/headers serve only as clues; conflict between measured and self-reported → register correction without modifying originals; consumer side must confirm face-by-face once before nucleus-cell axis application.",
         ref="/mnt/D/EyeKB/plans/compv1x_20260930/COMPV1X_REPORT.md Q2 Adjudication Section",
         why="Platform wording errors are universal across tissues (assay axis directly hits own platform labeling error lesson = astra T1 orientation; v0 vocabulary bulk/snRNA mixing risk is homologous)"),
    dict(pid="mixed_prep_protocol_within_dataset", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Mixed sampling/sorting sub-designs within same dataset (unsorted arm pooled with positive/negative immune sorting arms) without metadata characterization → stratification comparability broken, systematic bias in sorted arm composition treated as whole-dataset fact",
         obs="Forensic case: 12 central fovea unsorted samples 55,736 cells + peripheral CD73 depleted/CD90 enriched RGC sorted 29,246 cells (only 2 batches contain sorting), split via cellId prefix + primary method forensics; rules unchanged after pre-registration, split path registered as subsequent option",
         mit="Sample-level preparation strategy forensic table before pooling (cellId prefix/abstract method/sorting marker three columns); composition metrics for non-stratifiable datasets descriptive only, not comparable; pre-registered rules not retroactively changed by forensics, splitting as subsequent option",
         ref="/mnt/D/EyeKB/plans/compv1x_20260930/ledgers/q4_sample_strategy_forensics.tsv full file",
         why="Sub-design mixing = preparation condition driven failure, not exclusive to specific grid (branch 4 → PATTERN)"),
    dict(pid="sorted_suspension_target_absence", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Sorting/plate-based suspensions physically do not carry target cell types → 'zero detection' in re-computation layer misread as biological absence or entry missing, actually a detection channel gap",
         obs="Case: Acinar cell zymogen program independently undetectable in re-computation (PRSS1 all clusters det=0.000, CTRB1≤0.006, PNLIP≈0), sorted suspension does not carry acini + plate-based design — even naming oracle cannot name acini (RULING prediction consistent with re-computation)",
         mit="Before concluding 'cell type absence', pass preparation sensitivity screening (check sorting markers/plate aperture design); if platform does not carry → register as detection gap, prohibit named biological absence",
         ref="/mnt/D/EyeKB/plans/kbx_lacrimal_20260928/KBX_VERDICT.md Section ② Platform/Data Gaps",
         why="Preparation channel gaps are universal across tissues (lacrimal gland as case source, TM/vitreous sorting lines have same-pattern risks)"),
    dict(pid="single_study_pilot_surface_reference", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Treating a 'pilot face' with single study/no donor-level intervals as a composition control reference converts single-batch bias into systematic false flags, with no donor-level confidence bands available for check",
         obs="Status registration evidence: one face status=observed_single_study_pilot (no donor-level intervals); composition control exclusion from scoring criteria already registered (Review Stop Order 6: ≠ no risk ≠ no marker)",
         mit="Automatically attach coverage/panel_gap flags before pilot/single-study faces enter composition controls; composition scoring disabled, description only; panel supplementation candidates converted to construction line work orders",
         ref="/mnt/D/EyeKB/kb/baselines/lacrimal_gland.json status field",
         why="Face status semantic failure is coordinate-independent (any tissue pilot phase same pattern → PATTERN)"),
    dict(pid="fetal_adult_stage_mixing", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Fetal/developmental stage samples mixed into adult tissue reading surface: developmental signatures hijack annotation and age axis, causing developmental cell types to be mislabeled or rare classes flattened under adult vocabulary",
         obs="Evidence grade = risk registration (defensive build + gate smoke; no witnessed mislabel case in library). Independent developmental retina surface (status=development_annotated_aggregate) and transitional components registered precisely due to mixing risk; S0 suspected-fetal hard gate prototype completed smoke test on public sample panel input (structure gate driven)",
         mit="Stage orthogonal axis determination precedes naming (S0 hard gate): fetal/developing suspected samples → abstain/separate list, prohibited strong naming under adult vocabulary; report grouped by stage before reading surface",
         ref="/mnt/D/EyeKB/kb/baselines/retina__fetal_developing.json + /mnt/D/EyeKB/kb/baselines/fetal_development_transitions.json",
         why="Developmental mixing = stage-condition driven (C11 adjudication assigned to PATTERN branch 4, no CELL variant grid created)"),
    dict(pid="demux_ambient_crosscontamination", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=[], assay=[], disease=[],
         fm="Ambient RNA/droplet crosstalk systematically disrupts sample assignment and rare population inference in combinatorial indexing and multi-omics experiments—crosstalk artifacts manifest as 'low-abundance cell types'",
         obs="Bibliographic records: PMID:39975005 and PMID:39989953 (single-nucleus multiome demultiplexing affected by ambient contamination, preprint+republished dual registration), PMID:42779630 (empirical estimation of ambient contamination in combinatorial indexing), PMID:40185305 (mitigation of ambient+doublet effects in tumor single-cell analysis)",
         mit="Pre-demultiplexing ambient forensics (multi-reference mapping/empty droplet controls); report sensitivity of rare class conclusions to ambient correction methods; default downgrade handling for multi-omics components",
         ref="/mnt/D/EyeKB/plans/known_issues_b1_20260930/pubmed_B_verified.json verified key (eutils bibliographic verification audit trail)",
         why="Platform-level assignment failure determined by assay conditions → PATTERN (branch 4)"),
    dict(pid="cross_species_mt_genotype_demux", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=[], assay=["snRNA", "scRNA"], disease=[],
         fm="Demultiplexing/ambient tools dependent on mitochondrial genotype suffer silent bias due to genotype incompatibility when pooling humans-apes and other closely related species; genotype-based attribution fails.",
         obs="Bibliographic record: PMID:40166335 (CellBouncer unified toolkit reveals Hominid Mitochondrial Incompatibilities).",
         mit="Check MT genotype compatibility before cross-species pooling (tool documentation + reference mitochondrial genome version); incompatible → switch to SNP/hashtag attribution; reuse preflight discipline from cross_species_panel_id_preflight for homologous lessons.",
         ref="/mnt/D/EyeKB/plans/known_issues_b1_20260930/pubmed_B_verified.json verified key",
         why="Species × tool interaction failure = condition-driven universal clause (not bound to dispute coordinates)."),
    dict(pid="organoid_developing_reference_mixing", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=["cultured_cell_line"], assay=[], disease=[],
         fm="Organoid/iPSC-derived systems framed with adult tissue: system developmental signatures mistaken for adult cell type evidence, organ-level references further contaminate adult type definitions and training references",
         obs="Bibliography-level anchors only (locator_verified ≠ witnessed failure): PMID:32946783 (Human retina and its organoid atlas), PMID:39117640 (Human developing retina multi-omics atlas), PMID:38942029 (Heterogeneity of hPSC-derived limbal stem cells); no organoid-vs-adult mislabel case observed in library — the rule is preventive, derived from system-axis difference",
         mit="Before naming and training references, distinguish the system axis (organoid/iPSC vs in situ tissue); if no 'system' term is present, leave scope blank and register a gap (to be backfilled after C11/C9 vocabulary expansion); organ-level references must not solely define adult cell types",
         ref="/mnt/D/EyeKB/plans/known_issues_b1_20260930/pubmed_B_verified.json verified key",
         why="System-condition driven (vocabulary currently lacks system axis → note registers gap; do not invent terms)"),
    dict(pid="cross_species_atlas_reference_transfer", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=[], assay=[], disease=[],
         fm="Direct transfer of model species maps/vocabulary to human (or vice versa) as cell type reference: structural and molecular differences exist in homologous tissues, transfer produces 'pseudo-absent/pseudo-present' cell types.",
         obs="Bibliographic records: PMID:32341164 (Human + four model species aqueous humor outflow pathway map, species differences as theme), PMID:35858321 (Human anterior segment map, coexistence of tissue-specific and shared types).",
         mit="List homologous structure comparison table item-by-item before reference transfer (including species-exclusive type lists); citing model species vocabulary must include species axis annotation; same family as symbol_case/panel_id_preflight but different failure surface (reference transfer ≠ ID conflict).",
         ref="/mnt/D/EyeKB/plans/known_issues_b1_20260930/pubmed_B_verified.json verified key",
         why="Cross-species reference condition-driven universal clause (C10 species axis unadjudicated yet PATTERN can be established—no dispute grid built)."),
    # ---- DEEP2 batch 2026-10-06 (PIT-TRIAGE-DEEP2 Task C; quota 21, 20 admitted, 1 slot
    # recorded insufficient_evidence in DEEP2_REPORT; every ref pointer re-verified on disk
    # or eutils-title-verified this session, trails under plans/pit_triage_deep2_20261005/work/) ----
    dict(pid="plate_level_background_secretory_reads", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Plate-based/low-input protocols: plate-level background (thousand-CPM) makes low-expression secretory markers read as false positives — background is a protocol attribute, not lineage expression",
         obs="Lacrimal gland measurement on file: LACRT plate background 1.5-5k CPM, LYZ 0.8-14.9x10^4/LTF 0.5-5.9x10^4 CPM det≈1.0 across groups (T-cell clusters included at 8.5k) — expression rate in unrelated clusters equals target clusters (KB8 ambient-quantification ledger)",
         mit="Register a data_note_ambient positive-read line before positive readings of low-expression entries; positive readings without background quantification downgrade to soft hint; background table and read line shipped together (KB8 hard-wired discipline)",
         ref="/mnt/D/EyeKB/plans/kb8_lacrimal_20260925/KB8_LACRIMAL_COMPLETED.md (ambient quantification, line 30)",
         why="Protocol-condition driven → PATTERN (KB8 lacrimal case; generalizes to all plate-based low-input)"),
    dict(pid="minor_pool_flag_contamination", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Red/green verdicts of minority reference groups are fired by neighbor-class large pools (pool(C)≠pool(O)): verdicts reflect control-pool size, not target group discriminability",
         obs="KB6 audit measurement on file: RPE (n=863) MITF red verdict fired by the large neighbor RGC pool (n=399,605); the target group is too small to fire red — pool mismatch registered in §13-A(3)",
         mit="Minority group (<10k) verdicts must report both pool sizes pool(C)/pool(O); red/green marked unreliable if mismatch exceeds one order of magnitude; conclusions about minority types like RPE must go through independent panels (KC-B1-006 same family, generalization face)",
         ref="/mnt/D/EyeKB/plans/kb6_audit_20260924/AUDIT_KB6_D001_separation_v2.md 13-A(3)",
         why="Verdict-mechanism level failure (coordinate-independent) → PATTERN"),
    dict(pid="cross_species_naive_integration_collapse", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Naive cross-species integration collapses into one heterogeneous mega-cluster plus single-species tiny clusters: the mixed state is an integration failure mode, not cross-species conservation",
         obs="M2 v0.2a failure-control measurement on file: BC 30 clusters = 1 mega-cluster (14,401 cells) + 28 single-species clusters (near-all mouse); RGC 5 clusters trivially mixed, OT ARI -0.002 (M2 pre-registered failure tier)",
         mit="Cross-species integration first passes three-state joint judgment (mixture degree/single-species share/ARI); failure baselines kept on file as controls; success declared only after audited ortholog-space pipeline (M2 three-threshold discipline)",
         ref="/mnt/D/OcularKB/plans/M2_orthotype_20260827/M2_A3_FULL_PREREG.md (failure control L8)",
         why="Species×integration interaction → PATTERN (C10 macaque promotion separate; this rule is coordinate-free)"),
    dict(pid="integration_residual_disease_composition", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Post-integration per-sample composition residual bias is read away: cross-sample cluster merging dilutes disease-cohort differences into the main cluster; merged labels do not eliminate the residual",
         obs="GSE165784 v2 integration measurement on file: single-sample cluster cl0 (99.4%) becomes mixed post-integration (B0 91.6% + B6 70.2%); document registers 'residual RRD bias kept as-is'; state cluster merging evidenced by Jaccard 0.667",
         mit="Post-integration must report per-sample composition tables; cluster labels never substitute per-sample shares; disease-cohort conclusions recomputed on the single-sample track (dual-track retained)",
         ref="/mnt/D/EyeKB/plans/demo_gse165784/ANNOTATION_DRAFT_GSE165784_V2_20260923.md (integration table L12)",
         why="Integration-condition driven → PATTERN (grid item KC-B1-017 generalization face)"),
    dict(pid="vendor_coarsebin_crossclass_mixing", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Vendor coarse bins mix cross-class signal: coarse reference boxes (e.g., vendor Epithelial box) mix non-target epithelium/contamination signals; aligning against coarse boxes yields fake-diff or fake-match deviations",
         obs="BMR agreement measurement on file: vendor Epithelial 2.48% vs model RPE 0.17% with register note 'vendor Epithelial box mixed with non-RPE epithelial/contamination signal'; 13 of 17 vendor coarse bins have no corresponding class and must be treated NA",
         mit="Vendor coarse-bin alignment only to mapping caliber (KC-B1-024 same family); coarse bins without corresponding classes listed NA without extrapolation; coarse-bin deviations first attributed to bin definition before biological reading",
         ref="/mnt/D/EyeKB/plans/mouse_mid_20260925/MOUSE_MID_REPORT.md §3.3",
         why="Reference-granularity condition → PATTERN"),
    dict(pid="governance_gate_convention_false_reject", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Governance gates silently reject legitimate inputs: species/ID convention differences make the gate reject true-type samples (title-case human-origin sends hitting the mouse-suspected branch); false rejections do not enter the result surface",
         obs="KB-GOV B5 implementation on file: 231 human-origin clusters in all-uppercase convention misdetect=0, but the document explicitly registers 'real human title-case sends will be falsely rejected', with T+7 observation window and dual-state probe ledger (off==pre 42/42)",
         mit="Every governance gate ships a false-rejection observation window + dual-state control ledger; false rejections counted and reported separately; if misdetect>0, revert per process, no unilateral caliber change",
         ref="/mnt/D/EyeKB/plans/kbgov_b5impl_20260928/B5IMPL_COMPLETED.md (L37/L45)",
         why="Governance-layer condition → PATTERN (rejection ≠ biological verdict, prevents silent bias)"),
    dict(pid="treatment_record_not_recorded_confound", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=["snRNA"], disease=["anti_VEGT_treated"],
         fm="Missing treatment record is read as untreated (not_recorded ≠ naive): donor/eye-bank metadata has no treatment column, drug exposure history may genuinely exist, and the treatment axis is blind-read",
         obs="Baseline measurement on file: ocular_surface sampling-materials clause 'treatment background: not recorded (eye-bank metadata has no treatment column)' (L28); C12 ruling {treated, naive, not_recorded} three-state discipline in the controlled vocabulary",
         mit="Treatment axis registered three-state; not_recorded must not be used as naive control (C12 mandatory mitigation); treatment-effect comparisons first check metadata treatment-column availability, absent → downgrade to descriptive",
         ref="/mnt/D/EyeKB/kb/baselines/ocular_surface.md (L28) + /mnt/D/EyeKB/plans/known_issues_b2_20261001/out/ARBITRATION_RULING_C1-C14_v1.md (C12)",
         why="C12 landing item: UNMAPPED U12 disposition's 'P23 enters claim once on-disk source surfaced' — source found 2026-10-06 (ocular_surface L28)"),
    dict(pid="eye_bank_donor_material_axis", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Eye-bank ex-vivo material and surgical fresh material mixed into one composition surface: death-to-fixation interval, preservation and surgical context differ systematically; pooling reads preservation effects as tissue biology",
         obs="Baseline measurement on file: ocular surface = eye-bank donor corneoscleral rim (ex-vivo), optic nerve = mixed surgical+eye-bank material (optic_nerve.md L26); material-source+interval reporting duty anchored in ocular_surface sampling-materials clause",
         mit="Composition claims carry material-source words (eye-bank/surgical flap/ex-vivo whole) and intervals; two sources listed separately, never pooled; cross-study comparisons first align material caliber (KC-B1-016 three-usage caliber same family)",
         ref="/mnt/D/EyeKB/kb/baselines/ocular_surface.md (L26-28)",
         why="Material-source condition driven → PATTERN"),
    dict(pid="series_age_metadata_loss_quarantine", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="One GEO series mixes disease/normal/age layers and metadata cannot be completed: the QUARANTINE layer is discarded (8,178/23,178 scale), losing composition comparability — discard volume is a comparability loss not cleanup",
         obs="TG-G2 split measurement on file: GSE210543 23,178 cells into three layers (fetal 8,214 / adult 6,786 / QUARANTINE 8,178 age-unrecoverable); AMD/Unaffected donor codes 4046/4049 disjoint from D002 donor table, both pseudo-independence and age loss registered",
         mit="Series-level splitting (stage/disease layers) precedes composition comparison; QUARANTINE layers not silently discarded; cross-dataset donor ID overlap checked before claiming independence",
         ref="/mnt/D/OcularKB/plans/split_exec_TG-G2_release_20260818.md (L34-57)",
         why="Metadata-condition driven → PATTERN (KC-B2-005 same family; this entry = metadata-loss face)"),
    dict(pid="optic_onh_on_region_conflation", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=["snRNA"], disease=[],
         fm="Optic nerve head (ONH/lamina cribrosa) and optic nerve shaft (ON) have different structure and cell composition: merging into one 'optic nerve' composition surface reads structural region differences as biological composition",
         obs="OA-D003 baseline measurement on file: region components ONH 355,363 nuclei vs ON 604,266 nuclei registered (optic_nerve.md L26, adult-only snRNA primary)",
         mit="Optic nerve claims first lock region words (ONH/ON/mixed); mixed-region composition described only, not benchmarked; sampling boundary recorded; glial composition comparisons stratified by region",
         ref="/mnt/D/EyeKB/kb/baselines/optic_nerve.md (L26)",
         why="Sampling-boundary condition → PATTERN (C3 coordinates legal; the pitfall subject predicted by B1 second-batch list item 2)"),
    dict(pid="doublet_inflated_error_cluster", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Doublets inflate false error clusters: high-doublet-fraction clusters (scrublet score median >0.4 level) are misread as 'class errors' — the failure is doublet composition, not classifier misbehavior for that class",
         obs="T125 crosstab measurement on file: cluster11 n=160 dbl_frac_pct=99.38 score_median 0.4686 — whole error_BC cluster doublet-driven; by contrast cluster10 dbl_frac=0.0% score_median 0.0314 constitutes a different category",
         mit="Error-cluster attribution first passes doublet-score crosstab (T125 style); high-dbl clusters do not drive rule changes; doublet rate reported jointly with rare-class support",
         ref="/mnt/D/OcularKB/plans/M31_T125_ROD_SCRUBLET_CROSSTAB_20260908.json",
         why="QC-condition driven → PATTERN"),
    dict(pid="hidden_lineage_eval_double_dip", est="internal_observation", risk="high",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Public-dataset lineage is invisible: HRCA constituent/pooled donors reappear under different GSE/SUP accessions; nominally independent evaluation sets are actually resub of the training pool",
         obs="ESET declaration measurement on file: 17-species (GSE237204) human barcodes match HRCA at donor level (Hu035516OS↔Hu0355 etc.), GSE265801=HRCA Chen_17_D013=GSE226108 same pool, E-MTAB-7316 HCA constituent barred — all donor-level matches registered",
         mit="External evaluation sets first pass donor/barcode lineage check (not accession-level); resub layers barred from evaluation surfaces; pairwise match ledgers retained",
         ref="/mnt/D/OcularKB/plans/M31_T118_ESET_DECLARATION_20260830.md (L13-16)",
         why="Data-governance condition → PATTERN (evaluation-surface independence duty; does not touch scoring)"),
    dict(pid="query_rewrite_semantic_loss", est="internal_observation", risk="medium",
         ad="none", conf="high", prep=[], assay=[], disease=[],
         fm="Query-rewrite layer structural deletion: whole-sentence replacement rules lose substantive meaning in the rewritten surface (31/66 rows registered), while ON-arm hit improvements mask the meaning loss",
         obs="CN-CHALLENGE-24 measurement on file: G1 pass (strict hit miss=0, OFF 12/24→ON 21/24), G2 FAIL (substantive semantic loss 31 rows: 9 generic-verb bridge rows, 22 structural rows inseparable from whole-sentence-replacement rules), G3 pass (0 reversal)",
         mit="Rewrite layers pass per-row substantive-meaning audits (not just hit rates) before promotion; structural defects patched at the rule layer, not by parameters; ON/OFF control surfaces kept as verdict surfaces",
         ref="/mnt/D/EyeKB/plans/cn_challenge_20261005/out/REPORT_CN_CHALLENGE.md",
         why="Service-surface condition → PATTERN (flag-raising only; service code untouched per territory rules)"),
    dict(pid="pvr_pathologic_migration_flag_conflict", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=["vitrectomy_cassette_wash", "surgical_stripped_membrane"], assay=[], disease=[],
         fm="Retinal pigment/photoreceptor-layer signals in vitreous material have a second disease channel: in PVR contexts pigment-cell migration/proliferation is pathology itself (macrophage-myofibroblast transition registered); reading 'sampling flag only' flags disease body as contamination",
         obs="Bibliography-level anchor: PMID:37686317 (macrophage-myofibroblast transition contributes to myofibroblast formation in PVR, Int J Mol Sci 2023); in-library KC-B1-046 sampling-flag row — PI residual adjudication ruled 2026-10-08 (suggestion ballot adopted: entry body kept + dual-hypothesis addendum in the mitigation cell); cross-reference closure: KC-B1-046 and this row reference each other by id (cards TRIAGE_TABLE residual-1 / PIT-R01)",
         mit="Disease-context words precede reading of pigment-layer signals (first verify PVR/tear context); dual-hypothesis registration (sampling flag and pathology channel reported in the same sentence); specimen records without sampling method still barred from the conclusion pool",
         ref="PMID:37686317 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_candidate_anchors_esummary.json)",
         why="Disease-context condition → PATTERN; takes over the pathology face of KC-B1-046 (PI ruled 2026-10-08: dual-hypothesis addendum adopted, 046 kept; cross-reference closed per PIT-R01; flag-only unchanged)"),
    dict(pid="vitreous_protocol_dependent_yield", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=["vitrectomy_cassette_wash"], assay=[], disease=[],
         fm="Vitreous immune-cell detectable surface is protocol-dependent: cassette washing vs membrane peeling vs flow+single-cell workflow differ in yield and subset retention; cross-protocol composition comparison compares extraction protocols, not biology",
         obs="Bibliography-level anchor: PMID:40382772 (protocol for isolating and characterizing human vitreous immune cell infiltrates by flow cytometry and single-cell transcriptomics, STAR Protoc 2025 — the protocol itself is the research subject)",
         mit="Vitreous composition claims reported per protocol layer (KC-B1-045 three questions extended by a protocol fourth question); cross-protocol comparisons only to pathway layer",
         ref="PMID:40382772 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_candidate_anchors_esummary.json)",
         why="Process-condition → PATTERN"),
    dict(pid="cross_species_aging_reference_transfer", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=[], assay=[], disease=[],
         fm="Aging atlas conclusions transferred directly across species: human and macaque aging retina registered in one atlas while the two-species aging-signature correspondence is an open question; mouse/macaque aging module conclusions cannot be read as human cell-type-specific effects without verification",
         obs="Bibliography-level anchor: PMID:34691611 (a single-cell transcriptome atlas of the aging human and macaque retina, Natl Sci Rev 2021); in-library cross-species integration failure control on file (cross_species_naive_integration_collapse)",
         mit="Cross-species aging claims first build a human-model-species module correspondence table (including failure faces); aging conclusions default to pathway layer; cell-type-specific conclusions verified in the same atlas before transfer",
         ref="PMID:34691611 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_candidate_anchors_esummary.json)",
         why="Species-axis condition → PATTERN (C10 macaque grid promotion separate; this entry registers the transfer rule)"),
    dict(pid="model_species_wound_repop_boundary", est="peer_reviewed_literature", risk="low",
         ad="none", conf="medium", prep=[], assay=[], disease=[],
         fm="Rabbit stromal wound-repopulation model conclusions transferred directly to the human fibrosis window: the registered rabbit non-fibrotic repair pathway differs from human pathological fibrosis; model→human direct read-out is reference-transfer failure",
         obs="Bibliography-level anchor: PMID:41421445 (single cell RNA-seq characterization of non-fibrotic stromal wound repopulation in the rabbit, Exp Eye Res 2026); in-library rabbit×cornea grid = to-be-built (B1 README second-batch item 3)",
         mit="Rabbit-model references first list the non-fibrotic/fibrotic window difference; rabbit material data not admitted to human corneal composition comparison surfaces; grid-build duty transferred to construction line",
         ref="PMID:41421445 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_candidate_anchors_esummary.json)",
         why="Model-species condition → PATTERN (second-batch item 3 'anchored-to-be-built' landing)"),
    dict(pid="batch_integration_overcorrection", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=[], assay=[], disease=[],
         fm="Overcorrection erases true biological variance: batch correction flattens between-group composition differences along with batch effects; post-correction 'uniformity' is falsely read as 'no difference'",
         obs="Bibliography-level anchor: PMID:40158033 (reference-informed evaluation of batch correction for single-cell omics data with overcorrection awareness, Commun Biol 2025); in-library same-case opposite face registered (batch_integration_overcorrection paired with cross_species_naive_integration_collapse)",
         mit="'No difference' conclusions across datasets report correction strength (overcorrection sensitivity); uncorrected-track controls kept (dual-track); disease-effect claims prefer within-dataset stratified analysis",
         ref="PMID:40158033 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_batch_overcorrection_esummary.json)",
         why="Method-condition → PATTERN (opposite failure surface of naive collapse; registered as separate entry)"),
    dict(pid="uveitis_vitreous_evidence_tier_gap", est="peer_reviewed_literature", risk="low",
         ad="none", conf="medium", prep=[], assay=[], disease=[],
         fm="Non-diabetic uveitis vitreous composition has thin single-cell evidence: mediator/proteomic review-layer conclusions are not the composition comparison surface — review conclusions and single-cell composition cannot substitute each other",
         obs="Bibliography-level anchor: PMID:42023421 (immune mediators in birdshot chorioretinopathy: a systematic review, Ocul Immunol Inflamm 2026 — mediator-layer evidence); in-library PVR/uveitis vitreous grid = placeholder (B1 README second-batch item 4)",
         mit="Non-diabetic vitreous composition claims first verify evidence layer (mediator layer ≠ composition layer); composition-layer statements need single-cell support; grid absence registered as build duty",
         ref="PMID:42023421 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_candidate_anchors_esummary.json)",
         why="Evidence-tier condition → PATTERN (second-batch item 4 direct landing)"),
    dict(pid="bulk_composition_backprojection", est="peer_reviewed_literature", risk="medium",
         ad="none", conf="medium", prep=[], assay=["bulk"], disease=[],
         fm="Bulk tissue composition read back to cell-type-specific mechanisms: bulk averaging masks cell-type attribution; deconvolution-vs-single-cell registered differences show bulk conclusions cannot directly read as cell-type evidence",
         obs="Bibliography-level anchor: PMID:42510813 (cell-type deconvolution of equine BALF RNA-seq: a critical comparison with matched single-cell data, Genes 2025 — deconvolution/single-cell truth difference registered in same-subject comparison); in-library U10/C9: bulk assay word legalized by C9 approval, S0 primary ledger includes bulk component",
         mit="Bulk composition conclusions default to pathway/tissue layer; cell-type-specific statements need deconvolution+sensitivity analysis and are labeled inference; when matched single-cell evidence exists, single-cell layer preferred (KC-B2-001 wording-drift same family)",
         ref="PMID:42510813 (title verified 2026-10-06, trail /mnt/D/EyeKB/plans/pit_triage_deep2_20261005/work/eutils_bulk_mean_esummary.json)",
         why="U10/C9 landing: bulk word legalized, P24 'bulk averaging = cell-resolution loss' failure enters claim this round (title-level verified per U10 discipline)"),
]

# ---------------------------------------------------------------- Assembly
def _pointer_exists_in_source(ref):
    """Upgrade from B2: Extract candidate paths from ref string (supports full-width parentheses/+ concatenated footnotes), verify if any exist."""
    toks = re.findall(r"/mnt/\S+", str(ref))
    for t in toks:
        if Path(t).exists():
            return True
        m = re.match(r"^(.*?(?:\.(?:md|json|tsv|csv|h5ad|txt|log|tar|gz|png)))", t)
        if m and Path(m.group(1)).exists():
            return True
    return bool(toks) and False


# ---- Repository Cleaning (Red Line: internal sample IDs prohibited in repository; original working disk files not modified, repository-side build products uniformly pass through this layer)----
# Regex-only rules (no batch-id literals anywhere in repo-side code or artifacts).
_SCRUB_RE = [
    (re.compile("本室 YAS-\\d+ 玻璃体液样本"), "本室玻璃体液样本"),
    (re.compile("In-house YAS-\\d+"), "In-house"),
    (re.compile("YAS-\\d+"), "in-house batch"),
    (re.compile("BMR\\d+"), "in-house mouse dataset"),
]
def _scrub_text(s: str) -> str:
    for pat, rep in _SCRUB_RE:
        s = pat.sub(rep, s)
    return s

_EN_MAP = None

def _en_render(o):
    """English rendering layer for the Chinese working-disk originals (SRC).

    The repo surface is English-only; the six-cell manuscripts under SRC stay
    Chinese (working-disk originals, never rewritten here). Every Chinese
    string pulled from SRC must appear in EN_RENDER_MAP.json (keys byte-exact);
    unknown units fail loudly so regeneration can never silently leak Chinese
    back into pages (same discipline as the WIRE-P1 sanitization-in-generator rule).
    """
    global _EN_MAP
    import json as _json
    if _EN_MAP is None:
        p = Path(__file__).resolve().parent / "EN_RENDER_MAP.json"
        _EN_MAP = _json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    miss = []
    def walk(x):
        if isinstance(x, dict):
            return {walk(k): walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        if isinstance(x, str) and re.search(r"[\u4e00-\u9fff]", x):
            x2 = _scrub_text(x)  # redline scrub BEFORE lookup: sidecar keys are the scrubbed forms
            t = _EN_MAP.get(x2, _EN_MAP.get(x))
            if t is None:
                miss.append(x2[:80])
                return x2
            return _scrub_text(t)
        return _scrub_text(x) if isinstance(x, str) else x
    r = walk(o)
    if miss:
        raise SystemExit("EN_RENDER_MAP missing %d unit(s): %s" % (len(miss), " | ".join(miss[:5])))
    return r


def build():
    claims = []
    seq = 0
    for cell in CELLS:
        src = _en_render(json.load(open(SRC / f"{cell}.json", encoding="utf-8")))
        sp, ti_raw = cell.split("__", 1)
        ti = TISSUE_CANON[ti_raw]
        for i, it in enumerate(src["card"], 1):
            key = (cell, i)
            if key in EXCLUDED:
                continue
            d = V.get(key)
            if d is None:
                raise SystemExit(f"Missing entry {key} in adjudication table—default classification prohibited (astra T4 failure mode warning)")
            seq += 1
            cid = f"KC-B1-{seq:03d}"
            est = EST_BY_GRADE[it["source_grade"]]
            hraw = d["home"]
            hk = hraw[0]
            hi = hraw[1] if len(hraw) > 1 else None
            if hk == "cell":
                hi = f"{sp}__{ti}"
                scope = {"species": [sp], "tissue": [ti]}
            elif hk == "species":
                scope = {"species": [hi], "tissue": ["*"]}
            elif hk == "pattern":
                scope = {"species": ["*"], "tissue": ["*"]}
            else:
                scope = {"species": [], "tissue": []}
            for axis in ("species", "tissue", "assay", "preparation", "disease_or_treatment", "region"):
                if axis in d["sc"]:
                    scope[axis] = d["sc"][axis]
            for axis in ("assay", "preparation", "disease_or_treatment"):
                scope.setdefault(axis, [])
            # Controlled vocabulary mechanical validation (prohibit self-coined terms)
            for t in scope["tissue"]:
                assert t == "*" or t in CANON_TISSUES, f"{cid}: tissue {t} not in controlled vocabulary"
            for s_ in scope["species"]:
                assert s_ == "*" or s_ in SPECIES_PAGE, f"{cid}: species {s_} not in controlled vocabulary"
            for a in scope["assay"]:
                assert a in ASSAY_VOCAB, f"{cid}: assay {a} not in controlled vocabulary (v1 vocab see COORDINATE_TAXONOMY_v1.md §4)"
            for r_ in scope.get("region", []):
                assert r_ in REGION_VOCAB, f"{cid}: region {r_} not in v1 §3.1 region axis vocabulary"
            if est == "internal_observation":
                scv = "locator_verified" if _pointer_exists_in_source(it["source_ref"]) else "unchecked"
            elif est == "peer_reviewed_literature":
                scv = "locator_verified"   # B1 build-time eutils bibliographic check; trail = the search-trail section of the draft README
            else:
                scv = "unchecked"          # URL existence ≠ claim validity (astra T2)
            ad = d["ad"]
            blind = (ad == "none")
            claim = {
                "claim_id": cid,
                "scope": scope,
                "failure_mode": d["fm"],
                "observable_signature": d["obs"],
                "risk_level": d["risk"],
                "mitigation": it["mitigation_or_rule"],
                "evidence_source_type": est,
                "source_check": scv,
                "home": {"kind": hk, "id": hi},
                "visibility": "pre_annotation" if blind else "post_decision",
                "blind_safe": blind,
                "answer_dependency": ad,
                "status": "migrated_draft_pending_audit",
                "owner": "pi-chief (WIRE-P1 migration 2026-09-30)",
                "last_reviewed": None,
                "links": [str(it["source_ref"])],
                "conflicts": [],   # astra T5 conflict-object mount slot (field template: INDEX.legend.conflict_schema)
                "provenance": {
                    "origin_cell": cell, "b1_order": i,
                    "legacy_grade": it["source_grade"],
                    "legacy_code_in_legend": HIST_GRADE[est],
                    "report_confidence": it["confidence"],
                    "home_rationale": d["why"],
                },
            }
            if d["note"]:
                claim["note"] = d["note"]
            claims.append(claim)
    # ---- B2 existing retrieval items (home=pattern, vocabulary validation same rule; status=draft_pending_audit new items)----
    for j, it in enumerate(B2_ITEMS, 1):
        cid = f"KC-B2-{j:03d}"
        est = it["est"]
        assert est in EST_BY_GRADE.values(), f"{cid}: EST enumeration invalid"
        scv = (("locator_verified" if _pointer_exists_in_source(it["ref"]) else "unchecked")
               if est == "internal_observation" else
               ("locator_verified" if est == "peer_reviewed_literature" else "unchecked"))
        for a in it["assay"]:
            assert a in ASSAY_VOCAB, f"{cid}: assay {a} not in controlled vocabulary (v1 §4, bulk legal after C9 approval)"
        for p_ in it["prep"]:
            assert p_ in PREP_VOCAB, f"{cid}: preparation {p_} not in controlled vocabulary"
        for ds in it["disease"]:
            assert ds in DISEASE_VOCAB, f"{cid}: disease {ds} not in controlled vocabulary"
        ad = it["ad"]
        blind = (ad == "none")
        scope = {"species": ["*"], "tissue": ["*"], "assay": list(it["assay"]),
                 "preparation": list(it["prep"]), "disease_or_treatment": list(it["disease"])}
        claim = {
            "claim_id": cid,
            "scope": scope,
            "failure_mode": it["fm"],
            "observable_signature": it["obs"],
            "risk_level": it["risk"],
            "mitigation": it["mit"],
            "evidence_source_type": est,
            "source_check": scv,
            "home": {"kind": "pattern", "id": it["pid"]},
            "visibility": "pre_annotation" if blind else "post_decision",
            "blind_safe": blind,
            "answer_dependency": ad,
            "status": "draft_pending_audit",
            "owner": "pi-chief (KNOWNISSUES-B2 2026-09-30)",
            "last_reviewed": None,
            "links": [str(it["ref"])],
            "conflicts": [],
            "provenance": {
                "origin_cell": "b2_stock_20260930", "b1_order": j,
                "legacy_grade": {"internal_observation": "Empirical evidence in Library A",
                                 "peer_reviewed_literature": "Tier B bibliographic record PMID",
                                 "community_lead": "Tier C community experience"}[est],
                "legacy_code_in_legend": HIST_GRADE[est],
                "report_confidence": it["conf"],
                "home_rationale": it["why"],
            },
        }
        claims.append(claim)
    return claims


# ---------------------------------------------------------------- Page assembly (unique Home+pointer)
def _covers(scope, species, tissue):
    sp_ok = "*" in scope["species"] or species in scope["species"] or not scope["species"]
    ti_ok = "*" in scope["tissue"] or tissue in scope["tissue"] or not scope["tissue"]
    return sp_ok and ti_ok


def pages_of(claims):
    pages = {}
    def page(name):
        return pages.setdefault(name, {
            "schema": "eyekb-known-claims-page/1.0",
            "generated_by": "pipeline/pitfalls/build_claims.py (WIRE-P1 REV-1 + B2)",
            "page_type": name.split("/")[0], "entries": [], "pointers": []})
    by_home = {}
    for c in claims:
        key = c["home"]["id"] if c["home"]["kind"] in ("cell", "species") else \
            (f"patterns/{c['home']['id']}" if c["home"]["kind"] == "pattern" else None)
        if c["home"]["kind"] == "cell":
            fname = f"cells/{key}.json"
        elif c["home"]["kind"] == "species":
            fname = f"species/{c['home']['id']}.json"
        elif c["home"]["kind"] == "pattern":
            fname = f"patterns/{c['home']['id']}.json"
        else:
            fname = "unmapped/UNMAPPED_SCOPE.json"
        page(fname)["entries"].append(c)
        by_home.setdefault(c["claim_id"], fname)
    # Coordinate page pointer: cell pages collect pattern/species coverage bars; species/tissue pages collect pattern coverage bars
    for sp in SPECIES_PAGE:
        page(f"species/{sp}.json")  # guarantee the page exists
    for c in claims:
        if c["home"]["kind"] == "cell":
            continue
        # pattern/species claim → attach pointer to each covered cell page
        covered_cells = []
        for sp in SPECIES_PAGE:
            for tis in (c["scope"]["tissue"] if c["scope"]["tissue"] != ["*"] else CANON_TISSUES):
                cp = f"{sp}__{tis}"
                if _covers(c["scope"], sp, tis):
                    covered_cells.append(cp)
        for cp in covered_cells:
            fn = f"cells/{cp}.json"
            if fn in pages:
                pages[fn]["pointers"].append({
                    "ref_id": c["claim_id"],
                    "context_note": f"scope-hit ({c['evidence_source_type']}/{c['risk_level']}/blind_safe={c['blind_safe']})"})
        for sp in (c["scope"]["species"] if c["scope"]["species"] != ["*"] else SPECIES_PAGE):
            fn = f"species/{sp}.json"
            if c["home"]["kind"] != "species" and fn in pages:
                pages[fn]["pointers"].append({"ref_id": c["claim_id"],
                                              "context_note": "pattern covers species"})
        for tis in (c["scope"]["tissue"] if c["scope"]["tissue"] != ["*"] else CANON_TISSUES):
            fn = f"tissue/{tis}.json"
            pages.setdefault(fn, page(fn))
            if c["home"]["kind"] != "cell":
                pages[fn]["pointers"].append({"ref_id": c["claim_id"],
                                              "context_note": "pattern covers tissue"})
    page("unmapped/UNMAPPED_SCOPE.json")  # always present (0 entries in this batch)
    excl = {"schema": "eyekb-known-claims-exclusions/1.0",
            "reason": "Blind spot declaration/community gap registration=no failure mode no signature, not recorded as claim per REV-1; traceability retained",
            "items": [{"origin_cell": k[0], "b1_order": k[1], "kind": t,
                       "why": w} for k, (t, w) in EXCLUDED.items()]}
    return pages, excl


def write_pages(claims, pages, excl):
    import shutil
    if PAGES.exists():
        shutil.rmtree(PAGES)
    PAGES.mkdir(parents=True)
    for fname, pg in pages.items():
        p = PAGES / fname
        p.parent.mkdir(parents=True, exist_ok=True)
        seen = set()
        pg["entries"] = [e for e in sorted(pg["entries"], key=lambda x: x["claim_id"])
                         if not (e["claim_id"] in seen or seen.add(e["claim_id"]))]
        # pointers deduplication (unique by ref+note)
        pu = {}
        for x in pg["pointers"]:
            pu[(x["ref_id"], x["context_note"])] = x
        pg["pointers"] = [pu[k] for k in sorted(pu)]
        p.write_text(_scrub_text(json.dumps(pg, ensure_ascii=False, indent=1) + "\n"), encoding="utf-8")
    (PAGES / "EXCLUSIONS.json").write_text(_scrub_text(json.dumps(excl, ensure_ascii=False, indent=1) + "\n"),
                                           encoding="utf-8")
    tally = {k: sum(1 for c in claims if c["home"]["kind"] == k)
             for k in ("cell", "species", "tissue", "pattern", "unmapped")}
    hashes = [(str(p.relative_to(PAGES)), hashlib.sha256(p.read_bytes()).hexdigest())
              for p in sorted(PAGES.rglob("*.json"))]
    idx = {"schema": "eyekb-known-claims-index/1.0", "n_claims": len(claims),
           "n_excluded": len(EXCLUDED), "home_tally": tally,
           "claim_ids": sorted(c["claim_id"] for c in claims),
           "pages": dict(hashes),
           "legend": {"evidence_source_type": {
                          "internal_observation": "Internal library empirical evidence (historical archive PIT-E1/original A)",
                          "peer_reviewed_literature": "Peer literature (PIT-E2/original B)",
                          "community_lead": "Community leads (PIT-E3/original C)—prohibited from generating hard_gate/panel_activation/named_label"},
                      "source_check": {"unchecked": "Unverified", "locator_verified": "Pointer/bibliographic record verified",
                                       "claim_curated": "Manual re-review accepted (none in this batch)"},
                      "visibility": {"pre_annotation": "Visible before blind evaluation (structured flags only)",
                                     "post_decision": "Open after reading decision",
                                     "curator_only": "Curators only (not used in this batch)"},
                      "answer_dependency": {"none": "No answer dependency",
                                            "sample_specific": "Sample-specific",
                                            "dataset_specific": "Dataset-specific"},
                      "risk_level": {"high": "Conclusion-level failure/systemic unreliability",
                                     "medium": "Requires downgrade annotation or separate listing",
                                     "low": "Operational hint"},
                      "region_axis": ("v1 §3.1 (C8 approval) orthogonal region annotation: values fovea/macula_peripheral_mix/"
                                      "peripheral/not_recorded; only claims with region_scope annotations where scope contains"
                                      "region key (this batch=KC-B1-008); not_recorded must not be unilaterally applied as fovea/peripheral"),
                      "conflict_schema": ("claim.conflicts appended object fields (astra T5): conflict_id/"
                                          "claim_id/panel_version/decision_record_id/scope/"
                                          "initial_decision/final_decision/rule_applied/reviewer/"
                                          "coordinator_recalculation/timestamp——always empty during shadow phase,"
                                          "Conflicts are written via manual adjudication / Phase 3 voting protocol."),
                      "note": "A/B/C bare letters globally deprecated (T3); historical mappings retained only in legend"}}
    (PAGES / "INDEX.json").write_text(_scrub_text(json.dumps(idx, ensure_ascii=False, indent=1) + "\n"),
                                      encoding="utf-8")
    lines = [f"{h}  pages/{n}" for n, h in hashes]
    lines.append(hashlib.sha256((PAGES / "INDEX.json").read_bytes()).hexdigest() + "  pages/INDEX.json")
    (HERE / "MANIFEST.sha256").write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")
    return idx


def validate(claims, pages):
    ids = [c["claim_id"] for c in claims]
    assert len(ids) == len(set(ids)) == 79, \
        f"claim count={len(set(ids))} (expected 79 = migration batch 50(59−9 excluded)+B2 legacy batch 9+B2 deep-completion batch 20 (2026-10-06 PIT-TRIAGE-DEEP2, quota 21: 20 admitted + 1 insufficient_evidence))"
    homes = {}
    for c in claims:
        assert c["home"]["kind"] in ("cell", "species", "tissue", "pattern", "unmapped")
        assert c["evidence_source_type"] in EST_BY_GRADE.values()
        assert c["source_check"] in ("unchecked", "locator_verified", "claim_curated")
        assert c["answer_dependency"] in ("none", "sample_specific", "dataset_specific")
        assert c["risk_level"] in ("high", "medium", "low")
        assert c["blind_safe"] == (c["answer_dependency"] == "none")
        assert c["failure_mode"] and c["observable_signature"], "Atomic claim missing invalidation mode/signature"
        assert c["owner"] and c["status"], "Missing owner/status"
        homes[c["claim_id"]] = homes.get(c["claim_id"], 0) + 1
    assert all(v_ == 1 for v_ in homes.values()), "Only Home disruption"
    # Link resolution 100%: All pointer ref_id exist in the claim set
    allrefs = set()
    for pg in pages.values():
        for pt in pg["pointers"]:
            allrefs.add(pt["ref_id"])
    dangling = allrefs - set(ids)
    assert not dangling, f"Dangling pointers: {sorted(dangling)[:5]} (Termination condition: 100% link resolution)"
    # No double-write on same page (full content + pointer with same ref)
    for name, pg in pages.items():
        ent = {e["claim_id"] for e in pg["entries"]}
        assert not ent & {p["ref_id"] for p in pg["pointers"]}, f"{name} dual-write"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    claims = build()
    pages, excl = pages_of(claims)
    validate(claims, pages)
    tally = {k: sum(1 for c in claims if c["home"]["kind"] == k)
             for k in ("cell", "species", "tissue", "pattern", "unmapped")}
    print("claims:", len(claims), "excluded:", len(EXCLUDED), "home tally:", tally)
    n_blind = sum(1 for c in claims if c["blind_safe"])
    print(f"blind_safe: {n_blind} / pre_annotation {n_blind}; "
          f"post_decision {len(claims)-n_blind}")
    if a.check:
        import tempfile, shutil as sh
        tmp = Path(tempfile.mkdtemp())
        # Rewrite to temporary directory and perform full diff
        old = {str(p.relative_to(PAGES)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in PAGES.rglob("*.json")}
        gtmp = tmp / "pages"
        gtmp.mkdir()
        gpages = {}
        for name, pg in pages.items():
            gpages[name] = pg
        # Reuse write_pages logic (temporarily swap PAGES global)
        globals()["PAGES"], keep = gtmp, PAGES
        idx = write_pages(claims, pages, excl)
        globals()["PAGES"] = keep
        new = {str(p.relative_to(gtmp)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in gtmp.rglob("*.json")}
        sh.rmtree(tmp)
        drift = [k for k in set(old) | set(new) if old.get(k) != new.get(k)]
        print("CHECK", "PASS" if not drift else f"DRIFT {drift[:6]}")
        return 0 if not drift else 1
    idx = write_pages(claims, pages, excl)
    print("pages written:", len(list(PAGES.rglob('*.json'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
