# USER_DIRECTIVE_20260926_redline_rewrite — "evidence banned from scoring" red-line rewrite (PI chose option A)

- Decision: 2026-09-26 night; the PI replied "A" = rewrite, not cancel (gist of the PI's words: the red line was originally set for OcularKB's GBDT scoring stack; EyeKB currently has no scoring model and its independent reading purely uses literature markers, so the old clause idled and had the misreading side effect of "not even literature for annotation").
- Superseded old text (Claude5 frozen ruling 2026-08-12): "RAG is for auxiliary citation only; banned from scoring / banned from entering any scoring process."

## New clause: evidence-consumption discipline v2 (currently in force; project-wide unified wording)

1. **Annotation/reading side**: consuming RAG/MCP/literature evidence = **legitimate and the design core** (the three-seat blinded annotation runs on the evidence surface); no restrictions.
2. **Scoring/adjudication side**: ground-truth matching, hit-rate statistics, consensus adjudication, and any automated scoring/confidence-weighting/composite-QC process are **banned from consuming evidence sourced from the reading side** — preventing circular self-validation and evaluation leakage; this is the anchor of the credibility of the RUN-series numbers (19/22, 22/33 etc.).
3. **Precondition clause for activation**: if an automated-scoring stack (GBDT/LLM-judge/confidence score) is ever introduced, clause 2 is the precondition red line; evidence features may enter only with separate PI approval.

## Effective scope

- From now on, the red-line sentence in all task briefs/protocols/evaluation cards uses the new clause (citing this document's path suffices).
- **History is not rewritten**: already-frozen task briefs (plans/BRIEF_*, PROMPT_*), RUN pre-registration documents, and demo drafts keep their wording of the time; citations of the then-current caliber remain valid (evaluation comparability unaffected).
- Landing points already rewritten in this pass: WIKI/RETRIEVAL_INDEX.md, WIKI/KEY_FINDINGS.md, WIKI/DECISION_LOG.md (new row appended), EyeKB/plans/ANNOTATION_PROTOCOL_v1.1.md (inline annotation), skill knowledge-guided-cell-annotation, referenced artifacts of skill research-project-knowledge-hub, the EYEKB_REPO docs mirror (pushed with the commit), and the project maintainer's memory.

## Supplement (same day night; PI as-is: "you can rerun the full dataset once, put the scoring on top, and see whether the annotation overall improves")

= the **first approval** of clause ③ "an automated-scoring stack requires separate PI approval": project **E1, the evidence-into-scoring comparison experiment** is approved to start (full evaluation surface, not a production switch).
- Scope = experiment and quantification; until the experimental conclusions exist, the production scoring chain (ground-truth matching / consensus adjudication) still follows v2 clause ②.
- Pre-registered reading matrix and task brief: /mnt/D/EyeKB/plans/evidence_scoring_20260926/BRIEF_E1.md.

## Supplement 2 (09-26 night; after the E1 results returned, the PI replied "ok" = release all three items along the project maintainer's recommendation ballots)

1. **E1 tier verdict = V2+** (evidence scoring = prefilter + disagreement-flag localization is validated; replacing the reading is not; production wiring not for now) — E1_VERDICT.md stays exactly as the mechanical-execution artifact; this section is the ruling record.
2. **E2 de-same-sourcing retest GO**: task brief /mnt/D/EyeKB/plans/e2_decontam_20260926/BRIEF_E2.md (reading matrix W1/W2/W3 pre-registered; clean effect size + flag operating point + same-source inflation accounting on the evaluation surface).
3. **KB9 ocular-surface entry gaps (Melanocyte/Schwann zero entries, epithelium-immune takeover) enter the build queue**, scheduled together after E2 completes (per the PI's rule: no task dispatch before a decision).

## Supplement 3 (09-27 early hours; E2 completion notified)

E2 mechanical verdict = **W2** (clean Δ+7.66pp fails the flag-operating-point gate + the veto column −6.63pp): the evidence-surface positioning = offline-audit use only, V2+ maintained, the production proposal is closed — **W2 takes effect with no PI action needed**. Two derivative options remain open (non-blocking): ① the S5 permissive caliber (whether EuropePMC context hits count as external links) requires a fresh pre-registration to be recognized; neither caliber reaches W1; ② backfilling PMIDs for the 338 literature-prior genes with no record = a KB construction project item (may be scheduled together with KB9).

## Supplement: operational definition of red line ② (approved by the PI 2026-09-27, USER_DIRECTIVE_20260927_scoring_wave.md Supplement 2 D10)
The executable criterion for "the scoring/adjudication side is banned from consuming same-source evidence": the **reading/evidence-gathering side** may use label-derived applicability/blocking rules (because rule development touched evaluation labels, their effectiveness may only be positioned as "development-set engineering acceptance"; registration and report documents must carry that qualifier, and using them as independent-validation claims is prohibited); the **scoring/adjudication side** bans any label-derived evidence from scoring, confidence weighting, and composite QC judgment; the offline audit SOP (AUDIT_SOP_v1.0) is the sole exception, strictly bounded by the E2 W2 limits (retina surface only, abstention recall only, zero wiring).
