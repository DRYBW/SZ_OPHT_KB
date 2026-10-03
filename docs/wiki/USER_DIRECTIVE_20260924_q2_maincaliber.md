# USER_DIRECTIVE 2026-09-24: Q2 ground-truth primary-caliber switch (PI confirmed with "ok"; recorded on the PI's behalf by the project maintainer)

## Decision
From this document, for external numbers involving the Q2 (GSE155288) ground truth, the **primary caliber = truth_corrected** (a derived column of truthfix_v1):
- The RUN3 headline follows the errata v1.1 α caliber: n=197, A(qwen3.8-max)=60.9%, B(glm-5.1)=70.05%
- All v1.0 artifacts (author-original truth) are kept as historical archives; citations must annotate "contains known author mislabel clusters C18/C19"
- Q2::18 is characterized as an author mislabel (true value = a rod-program cell); Q2::19 = doublet-suspect, expelled from the truth-scoring region

## Consequences
1. From RUN4 onward, all Q2-related readings/adjudications in all RUNs go through the corrected caliber (the errata addendum section of RUN4_PREREG.md already reflects targets 23→22).
2. External narratives (the M1 paper / group-meeting figures) citing GSE155288 must carry the label-quality annotation (11-class coarse annotation containing mislabeled clusters; see audit document v1.1).
3. The blind-spot-line closure numbers (true rods judged BC = 0.004%) already used the corrected caliber and are unaffected.

## Status
- PI semantics: 2026-09-24, replied "ok" to the proposal "switch to truth_corrected" (MSG_PLATFORM)
- Effective: immediately
- Revocation condition: when the GSE155288 authors publish a revised ident that passes our re-review, the caliber is re-evaluated
