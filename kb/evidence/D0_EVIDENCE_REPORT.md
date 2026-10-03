# D0 Evidence Model Starter Batch — Coverage Report (v1.0, 2026-09-24)

Task Card: t_1e783e43 ｜ Task Brief: `D0_EVIDENCE_BRIEF.md` ｜ Template: `EVIDENCE_MODEL_TEMPLATE_v1.0.md`
Entry File: `d0_claims_v1.jsonl` (35 entries) ｜ Validation Script: `scripts/verify_d0_claims.py`

## 1. Verbatim Literal Validation Results (Primary Acceptance Gate)

- Independent rerun (directly reading frozen library `literature_db/v2.2_2026-09/chunks.parquet`, independent of this card's intermediate products):
  **checked 35 claims, 35 pass, 0 fail → 100% PASS**
- Validation items: Enum legality (five/four categories) / kb_target whitelist / verbatim ≤50 words and is a **literal substring** of any chunk for the corresponding pmid (including original spacing and case quirks) / limitation non-empty / citations for abstract-only papers must come from abstract chunks.
- **"Failed Validation" Section: No failed entries.** (During the process, 3 entries were previously corrected at the script level due to >50 words or incomplete truncation—D0C-011/015/017/019/021/030 were rewritten according to "continuous trimming/fragmentation" rules and fully re-extracted/re-validated, no manually typed text entered the products.)

## 2. Coverage Statistics (Entries per Paper, Red Line Compliance: All ≤8 and ≥3)

| pmid | Paper | Intake | Count |
|---|---|---|---|
| 35061025 | Hu 2022 Diabetes (GSE165784 original, microglia) | abstract_only | 5 (D0C-001..005) |
| 41578023 | HRCA Dual-Modal Reference Atlas | abstract_only | 3 (D0C-006..008) |
| 37917183 | JCI Insight 2023 AEBP1 Pericyte-Myofibroblast | full_text | 5 (D0C-009..013) |
| 39220810 | Ophthalmol Sci 2024 Vitreous T Cells | full_text | 5 (D0C-014..018) |
| 40069725 | J Transl Med 2025 MKI67+ microglia | full_text | 6 (D0C-019..024) |
| 40562775 | Nat Commun 2025 Sirt3/FAO metabolic niche | full_text | 5 (D0C-025..029) |
| 42601615 | J Transl Med 2026 SOX15 PDR atlas | full_text | 6 (D0C-030..035) |

Total 35 entries, covering all seven D0 papers (list and exceptions=`data_d0/d0_admission.json`).

### inclusion_reason distribution
core_reference 20 ｜ background 9 ｜ data_anchor 4 ｜ contradicting_evidence 1 ｜ method_anchor 1 (**all five categories have actual entries used**) 

### claim_relation distribution
supports 21 ｜ qualifies 7 ｜ context_only 6 ｜ refutes 1

### kb_target distribution (11 attachment points)
- `PDR__fibrovascular_membrane` 9 ｜ `human_pdr_membrane`(root) 4 ｜ `proliferative_DR` 6 ｜ `GSE165784V2` 3 ｜ `baseline_human_retina` 3
- Concept-level: `human_pdr_membrane#myeloid` 2, `#myeloid_states` 3, `#myeloid_states.foam_DAM_LAM` 2, `#major_compartments` 1, `#stromal_pericyte+stromal_myofibro` 1, `#stromal_myofibro` 1
- Full coverage of three main lines: **retina baseline** (HRCA 3 entries), **PDR membrane demo** (membrane composition/myeloid states/stromal states 14 entries), **GSE165784 data anchor** (original literature 5 entries + independent re-analysis 2 entries + third-party citation 2 entries anchoring the same accession).

## 3. Abstract-only limitation list (full_text_available=0)

| pmid | Impact | Entry-level disposition |
|---|---|---|
| 35061025 | No PMCID/OA failure → only abstract citable; sample n, cluster count, and quantitative criteria for "microglia major" cannot be verified from the library core | D0C-001..005 all marked as abstract-only in limitations; provenance.chunk_type=abstract |
| 41578023 | HRCA 3.9M cells/125 donors/130+ types are all self-reported in the abstract; fine-grained composition tables are not in the library | D0C-006..008 same as above |

The two papers contribute 8 entries (accounting for 22.9%) as abstract-level evidence—permitted by the task brief, but **must not** serve as the basis for any Grade A numerical adjudication (consistent with the `human_pdr_membrane` card caveat "Grade B literature anchors do not provide precise %").

## 4. Literature tensions exposed in this batch (value points of the evidence model, registered for reference)

1. **Microglia vs Macrophage identity dispute (same GSE165784 data)**: 35061025 claims microglia are dominant and defines a GPNMB+ subpopulation (D0C-002/003); 37917183 empirically refutes this stating "none of the inflammatory cells expressed microglia markers (TMEM119/P2RY12)" (D0C-011, the only refutes in this batch); 40069725 uses panels like SELENOP/MRC1/GPNMB to label the same population as microglia (D0C-021/022 method_anchor)—our Track B labels these states as Macrophage. → The **direction (myeloid dominance) for `human_pdr_membrane#myeloid*` is stable, while the identity term (microglia vs macrophage) is panel-dependent**, consistent with existing caveats.
2. **Three distinct sampling contexts**: FVM digested membrane (GSE165784 series) ≠ vitreous fluid wash (39220810, T cells 91.6%, D0C-014 qualifies) ≠ PDR donor retina proper (42601615, D0C-030/033). Any "membrane composition" reading must not be extrapolated to the other two compartments.
3. 42601615 relays Hu 2022 "mesenchymal 8.2%" (D0C-034) as a third-party metric, serving only as provenance without independent re-derivation.

## 5. Red-line compliance statement

- Did not touch `evalset/`, did not modify v2.1/v2.2 library files or the `d0_admission.json` body, did not write to `kb/baselines` or `kb/markers` (only read-only references to their entry_id as kb_target).
- Did not expand across the entire library: filtered only 196 D0 chunks by pmid.
- Claims are 100% script-extracted from chunk original text, with zero external knowledge supplementation.
- All intermediate products retained (see §6).

## 6. Product and traceability list

Formal products (`/mnt/D/EyeKB/kb/evidence/`):
- `EVIDENCE_MODEL_TEMPLATE_v1.0.md` — Three-field specification v1.0 (one positive and one negative example each)
- `d0_claims_v1.jsonl` — First batch of 35 entries
- `D0_EVIDENCE_REPORT.md` — This report
- `scripts/verify_d0_claims.py` — Independent lexical verification (rerunnable, exit code serves as gate)
- `scripts/extract_claims.py` — Probe-style extraction script (all 35 entries generated via this)
- `scripts/build_and_validate.py` — draft→jsonl assembly + intra-batch validation
- `SHA256SUMS.txt` — Product hash anchoring

Intermediate products (workspace `~/.hermes/kanban/boards/pi-briefing/workspaces/t_1e783e43/`, not deleted):
`d0_chunks.parquet` / `d0_chunks.json` (196 chunk filtered set), `paper_*.txt` (seven separate texts), `d0_claims_draft.json`, `validation_result.json`, `coverage_stats.json`
