# EyeKB Evidence Model Starter Card Task Brief: D0 Seven-Paper Claim-Level Verification (Three-Field Template + Initial Entries)

## Background and Positioning
One of the project mainlines defined by Astra review is "auditable evidence": RAG/MCP literature evidence cannot rely solely on PMID linkage; it requires **claim-level** relationships and context.
This card = **starter implementation** of the three-field evidence model: only for the D0 targeted channel seven papers (v2.2 library, d0_admission.json contains the list and exception registry),
producing a reusable template + initial entries. **Full library rollout is prohibited** (doctrinal red line).

## Three-Field Definitions (Frozen v1.0 for this card, subsequent cards follow)
1. `inclusion_reason` (reason for inclusion, five-category enum): core_reference / method_anchor / data_anchor / contradicting_evidence / background
2. `claim_relation` (relationship to target claim enum): supports / refutes / qualifies (conditional limitation) / context_only
3. `evidence_context` (auditable context): {kb_target: pointed KB entry/concept id, section: in-text location, verbatim: original claim text (English, ≤50 words), limitation: one-sentence applicability boundary of the claim}

## Tasks
1. Read D0 seven papers' admission materials (v2.2 library chunks: `/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.2_2026-09/`, filter papers.jsonl by pmid; for the two papers with full_text_available=0, use abstract-level evidence only and note in limitation)
2. Extract 3-8 key claims per paper (prioritize those linkable to existing KB entries/concepts: retina baseline, PDR membrane demo, GSE165784 data anchor), fill three-field entries
3. Outputs:
   - `/mnt/D/EyeKB/kb/evidence/EVIDENCE_MODEL_TEMPLATE_v1.0.md` (field specification + filling rules + 1 positive/negative example each)
   - `/mnt/D/EyeKB/kb/evidence/d0_claims_v1.jsonl` (initial entries, each with pmid/kb_target/three fields)
   - `/mnt/D/EyeKB/kb/evidence/D0_EVIDENCE_REPORT.md` (coverage statistics: entries per paper, kb_target distribution, abstract-only limitation list)
4. Self-check: every verbatim must be literally findable in the corresponding chunk text (run a validation script, include results in report); entries not found are deleted without leaving audit trails, listed exhaustively in the report's "Failed Validation" section

## Red Lines
- Do not touch evalset/ (frozen artifacts), do not modify v2.1/v2.2 library files, do not write to kb/baselines and kb/markers (territory of other cards)
- Claims must be extracted only from original literature text; external knowledge supplementation is prohibited; if extraction fails, extract less, do not pad numbers
- Retain all intermediate products; upon completion or obstruction, the card must be finalized

## Acceptance (Executed by Coordinator)
Template field completeness / Entry schema validity / Verbatim literal validation pass rate 100% (all failed items leave audit trails) / All five inclusion_reason categories defined
