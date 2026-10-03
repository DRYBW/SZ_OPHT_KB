# PROTOCOL_VOTING_v2_C2b — decision record for voting rule v2 (C2b main file, prospective effect)

- Card: t_03808fff | Task brief: /mnt/D/EyeKB/plans/proto_v2_20260927/BRIEF_PROTO.md
- Authorization: USER_DIRECTIVE_20260927_scoring_wave.md, addendum 2 **D11** ("approval of voting protocol v2 = C2b as the main file: prospective effect (from runs preregistered after this document's sign-off date onward); historical frozen adjudications are never retroactively altered; the D9 run is handled as 'primary reading C4 + parallel C2b'")
- Rule validation: /mnt/D/EyeKB/plans/tiep_20260927/TIEP_PROPOSAL.md (mechanical counterfactual re-voting, 5 rules × 5 evidence surfaces, zero LLM; hard verification of OVERTURN=0)
- Sign-off: 2026-09-27 | Nature: decision record (plain text + pointers; this card makes zero script changes, zero production writes, zero kb/ writes)

## 1. Operational definition of v2 (C2b, as-is from the TIEP recommended tier)

TIEP §2 as-is:

> **C2b quorum + coarse counted**: same as C2a, plus coarse:X is counted toward the quorum of label X (broad reading: "a third-seat coarse call is not a full abstention").

> **C2a quorum**: named ballots count at any grade; ≥2 seats with the same name establishes naming.

Operational decomposition (fully equivalent to the reference implementation `t1_revote.py: rule_c2(bs, count_coarse=True)`):

1. **Named ballots**: a ballot whose ballot face carries a concrete label (identity is not `undetermined*`, not prefixed `coarse:`, and not a missing ballot) is **counted at any grade (A/B/C)** toward that label's quorum — a grade-C named ballot is not an abstention (one of only two differences from v1=C4, which discards grade C).
2. **coarse:X**: a ballot whose identity carries the `coarse:` prefix is **counted toward the quorum of the label X after the colon** (broad reading: "a third-seat coarse call is not a full abstention") — the other difference from v1=C4, which discards COARSE.
3. **Naming gate**: **≥2 seats with the same name establishes naming**; a single valid seat (tie@1) does not name.
4. **Residual ties = S1 tie-break disabled, name withheld**: C2b introduces no S1-evidence tie-break (C3a) and no single-ballot confirmation (C3b) — the TIEP checkbox "adopt C3a/C3b = not recommended" holds; residual ties after quorum counting (most-frequent name has <2 seats) all remain unnamed (tie/split3/abstain3 patterns recorded as before).
5. `undetermined*`/missing ballots are not counted (same as C4).

Baseline comparison against v1=C4 (TIEP §2.1/§4, KB9 evidence surface): P1 **22→29/33** (+7 flipped to correct, 0 flipped to wrong, P2=0 at the gate); no perturbation on the two gate surfaces RUN4-r 15/22 and FACEV21 19/22 (preservation clauses Q4::15∧Q5b::13 intact); across 5 rules × 5 surfaces **not a single existing "named and correct" verdict is altered** (OVERTURN=0, full hard verification of all 204 difference-set ballots). Structural cost (stated plainly): the semantic leap of coarse:X — treating a reader's self-reported low-resolution ballot as a directional vote; the 7-of-7 correct on the KB9 surface is small-sample (n=3) evidence, not a guarantee.

## 2. Scope of effect and per-run rule-version declaration (D11 hard clause)

1. **Prospective effect**: binds only runs preregistered **after** this document's sign-off date (2026-09-27).
2. **Each run's preregistration MUST declare the applicable voting-rule version**: one of `v1=C4` or `v2=C2b`, explicitly written into the PREREG; undeclared = no freeze, no start.
3. **Historical frozen adjudications are never retroactively altered**: the numbers in the published RUN3/RUN4/RUN4-r/RUN5/RUN6-B/RUN7-RG/FACEV21/KB9 deliverables remain historically frozen under the C4 reading; the TIEP counterfactual re-vote is only rule-selection validation and constitutes no grounds for reversal. If any rule would turn an existing PASS case into an error, say so plainly; "using the new rule to retroactively alter RUN5 conclusions" is itself a gate failure, not an adjudication gain (as-is inheritance from TIEP §5.1).

## 3. Transition clause (D9 B-test, the sole exception, one-off)

The D9 preregistration (formal A/B validation of RAG free queries, plans/btest_20260927/) predates this document's rule switch and is handled per the authorization tier: **primary reading = current C4 voting rule (preserving comparability with the 15/19 baseline), C2b computed mechanically in parallel on the same table, zero extra seat ballots** (USER_DIRECTIVE_20260927_scoring_wave addendum 2 — proxy adoption of the D9 fork — plus BRIEF_BTEST's "parallel reading" clause). This clause applies only to that D9 run and sets no "dual primary reading" precedent; runs newly preregistered after D9 all follow the single-version declaration of §2.2.

## 4. Attached execution clauses (all three of the TIEP §4 recommended tier; D11 "hard-coded per the TIEP recommended tier")

1. **Scope-of-effect clause**: folded into §2 (new preregistrations + effect from the next run onward + no retroactive changes to history).
2. **P2 gate not automatically breached**: naming clusters newly added under the C2 tier **automatically enter the P2 contamination check** (a collision with the kb name list counts as P2); no gate modification is needed (KB9-surface measurement: P2=0).
3. **Lexical drift registered separately**: off-panel names on the ballot face (Keratocytes/Mac_DAM_LAM/coarse:Stromal, etc.) are not solved by any tie rule — from v2's effective date onward, each run's preregistration MUST include a **"normalize ballot-face names through the frozen crosswalk"** clause (the crosswalk is a frozen artifact, with its sha registered per run).

## 5. Runner landing points and reference implementation

- Inventory of current voting implementations (listed only, not modified; the warmup card of each run in the next wave forks per this list): /mnt/D/EyeKB/plans/proto_v2_20260927/RUNNER_WATCHLIST.md
- C2b reference implementation: /mnt/D/EyeKB/plans/tiep_20260927/scripts/t1_revote.py (sha256 d321e793…), `rule_c2(bs, count_coarse=True)`; the C4 replica = `c4_consensus()` in the same file (consensus/mode across the four surfaces — 156 rows — reconciled line by line against the published deliverables: PASS).
- New annotation-protocol version (v1.1 left in place, copy not move): /mnt/D/EyeKB/plans/ANNOTATION_PROTOCOL_v1.2.md §8.
