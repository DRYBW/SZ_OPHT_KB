# EyeKB Evidence Model Three-Field Template v1.0 (D0 Initial Freeze)

Freeze date: 2026-09-24 ｜ Source card: t_1e783e43 ｜ Upstream task brief: `/mnt/D/EyeKB/kb/evidence/D0_EVIDENCE_BRIEF.md`
Scope: **Claim-level** attachment for RAG/MCP literature evidence. This template is the first version (v1.0), subsequent cards follow it; changing field definitions requires bumping the version and rerunning legacy validation.

## 1. Record structure (JSONL, one claim per line)

```json
{
 "claim_id": "D0C-NNN",
 "pmid": "8-digit number",
 "title": "Paper title (carried over from admission record)",
 "inclusion_reason": "One of five enumerated values",
 "claim_relation": "One of four enumerated values",
 "evidence_context": {
   "kb_target": "KB entry/concept id ('#' suffix allowed for concept reference)",
   "section": "In-text location (original value of chunk section; use chunk_type if empty)",
   "verbatim": "Original claim text (English, ≤50 words, must be a lexical substring of a library chunk)",
   "limitation": "One-sentence applicability boundary for the claim (mandatory, cannot be empty)"
 },
 "provenance": {
   "chunk_type": "abstract|paragraph|table_row (type of chunk hit by extraction)",
   "ingested": "full_text|abstract_only (from d0_admission.json)",
   "extract_mode": "scripted_probe_sentence|scripted_probe_fragment",
   "generated_by": "Producing script identifier"
 }
}
```

## 2. Field Specifications and Filling Rules

### 2.1 `inclusion_reason` (Reason for Inclusion, Five Categories, Frozen Enum)

| Enum Value | Definition | Criteria |
|---|---|---|
| `core_reference` | Primary evidence literature for a KB entry/concept | Removing this entry causes the KB concept to lose its most direct literature support |
| `method_anchor` | Reference point for analysis/processing **methods** (QC thresholds, integration strategies, annotation panels) | Claim content concerns "how it was done," not "what was found" |
| `data_anchor` | Dataset **identity/provenance** anchor (GEO accession, sample composition, original literature binding) | Claim answers "what is this data / where did it come from" |
| `contradicting_evidence` | Claims **opposite in direction** to current KB conclusions | Opposing evidence on the same issue must be retained, not deleted |
| `background` | Contextual/framework statements that do not directly support specific numerical conclusions | Helps readers understand scope/limitations/context |

### 2.2 `claim_relation` (Relation to Target Claim, Four Categories)

| Enum Value | Definition |
|---|---|
| `supports` | Directional statement supporting kb_target |
| `refutes` | Directional statement refuting kb_target or one of its components |
| `qualifies` | Does not change direction but limits conditions/criteria/applicability boundaries |
| `context_only` | Contextual linkage only, does not constitute directional evidence for kb_target |

### 2.3 `evidence_context` (Auditable Context)

- **kb_target**: Only existing KB ids are allowed (prefix whitelist: `baseline_human_retina`, `human_retina`, `human_pdr_membrane`, `PDR__fibrovascular_membrane`, `proliferative_DR`, `GSE165784V2`); `#` can refer to concepts within entries (e.g., `human_pdr_membrane#myeloid_states.foam_DAM_LAM`). Fabricating unregistered ids is prohibited.
- **section**: Take the exact `section` value of the extracted chunk verbatim; substitute with `chunk_type` if empty.
- **verbatim**: English original text ≤50 words; **must be a lexical substring of any chunk for that pmid in v2.2 library** (including original spacing/case quirks, e.g., `MKI67 +  microglia`); extracted by script from chunks, manual typing/modification prohibited. When truncating long sentences, only continuous trimming from start/end is allowed.
- **limitation**: One sentence specifying applicability boundaries—species/tissue criteria (membrane ≠ retina ≠ vitreous fluid), sample size, inference level (annotation/pseudotime/ligand-receptor inference ≠ experimental validation), abstract-only, etc. **Each limitation for abstract-only literature (full_text_available=0) must explicitly note abstract-only.**

## 3. Positive and Negative Examples

### ✅ Positive Example (D0C-011, contradicting_evidence + refutes)
```json
{"claim_id":"D0C-011","pmid":"37917183","inclusion_reason":"contradicting_evidence",
 "claim_relation":"refutes",
 "evidence_context":{"kb_target":"human_pdr_membrane#myeloid",
  "section":"Discussion",
  "verbatim":"none of the inflammatory cells expressed microglia markers, such as  TMEM119  and  P2RY12 , in contrast to recent work that claimed microglial population as a main cell type involved in the fibrovascular membrane formation in PDR, with a subpopulation of microglia presenting fibrogenic properties ( 42 ).",
  "limitation":"Absence-of-evidence on TMEM119/P2RY12 in their own 4-sample dataset (homeostatic microglia markers can be lost upon activation/dissociation); refutes the microglial *identity* label, not the myeloid-dominant composition itself."}}
```
Why positive: Lexical substring is machine-checkable; all five elements present; refutation boundary clearly stated (refutes "identity annotation" not "myeloid proportion"); retains tension with GSE165784 original literature (D0C-002) rather than deleting either side.

### ❌ Negative Example (Prohibited Writing)
```json
{"claim_id":"BAD-001","pmid":"35061025","inclusion_reason":"supporting_evidence",
 "claim_relation":"supports",
 "evidence_context":{"kb_target":"human_pdr_membrane#macrophage_fraction=79.5%",
  "section":"Results",
  "verbatim":"Hu et al. reported that macrophages comprise roughly 80% of the membrane immune infiltrate.",
  "limitation":""}}
```
Why negative (4 violations):
1. `inclusion_reason` uses non-enumerated term (only five categories exist);
2. `verbatim` is a **rewrite/external knowledge addition**, no chunk in library contains this sentence, lexical check will fail;
3. kb_target embeds specific numerical values into id and that granularity concept is unregistered;
4. `limitation` is empty—abstract-only literature (35061025) strictly prohibits entries without defined boundaries.

## 4. Validation Protocol (Same Criteria for Acceptance)

- Independent verification script: `scripts/verify_d0_claims.py` (reads frozen library `chunks.parquet` directly, no dependency on intermediate artifacts), checks per item: valid enum / kb_target whitelist / verbatim ≤50 words and is a lexical surface substring / limitation non-empty / provenance.chunk_type=abstract for abstract-only entries.
- **Pass rate must be 100%**; any failed items are removed from JSONL and **all** registered in the "Failed Verification" section of the current batch report, leaving no untracked omissions.
- Intermediate artifacts (extraction scripts, draft JSON, chunk dump) are retained with the batch and must not be cleaned up.

## 5. Doctrinal Boundaries (following task brief red lines)

- This model covers only the **seven D0 targeted channel papers**; full library rollout belongs to subsequent cards and requires re-review by astra.
- Claims are extracted only from original literature text; **external knowledge supplementation is prohibited**; if extraction fails, extract less, do not pad counts.
- Prohibited actions: modifying `evalset/` (frozen files), altering v2.1/v2.2 library file bodies, writing to `kb/baselines`, `kb/markers` (territory of other cards).
