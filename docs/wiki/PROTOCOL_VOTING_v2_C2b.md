# PROTOCOL_VOTING_v2_C2b — ballot-rules v2 decision document (C2b master file, effective going forward)

- Card: t_03808fff | task brief: /mnt/D/EyeKB/plans/proto_v2_20260927/BRIEF_PROTO.md
- Released by: USER_DIRECTIVE_20260927_scoring_wave.md Supplement 2 **D11** ("Voting protocol v2 = C2b approved as the master rule: effective going forward (from runs pre-registered after this document's sign-off date); historical frozen rulings are not rewritten; D9's run is handled as 'primary read C4 + C2b in parallel'.")
- Rule evidence base: /mnt/D/EyeKB/plans/tiep_20260927/TIEP_PROPOSAL.md (five rules × five surfaces, mechanical counterfactual re-tally, zero LLM; OVERTURN=0 hard validation)
- Signed: 2026-09-27 | nature: decision document (plain text + pointers; this card made zero script changes, zero production writes, zero kb/ writes)

## 1. Operational definition of v2 (C2b, as-is per the TIEP recommended tier)

TIEP §2 as-is:

> **C2b quorum + coarse-count inclusion**: same as C2a, except that coarse:X counts toward the quorum of label X (the wide reading: "the third seat's coarse read is not discarded wholesale").

> **C2a quorum**: naming ballots are counted at any grade; ≥2 seats with the same name = named.

Operational decomposition (exactly equivalent to the reference implementation `t1_revote.py: rule_c2(bs, count_coarse=True)`):

1. **Naming ballots**: a ballot carrying a concrete label (identity not `undetermined*`, not `coarse:`-prefixed, and not a missing ballot) counts toward that label's quorum **at any grade (A/B/C)** — a grade-C naming ballot is not discarded (one of the only two differences from v1=C4, which discards grade C).
2. **coarse:X**: a ballot whose identity carries the `coarse:` prefix counts, via the post-colon label X, **toward the quorum of label X** (wide reading: "the third seat's coarse read is not discarded wholesale") — the other difference from v1=C4, which discards COARSE.
3. **Naming gate**: **≥2 seats with the same name = named**; a single valid ballot (tie@1) does not name.
4. **Residual ties = S1 tie-breaking prohibited, unnamed maintained**: C2b introduces neither S1 evidence tie-breaking (C3a) nor single-ballot confirmation (C3b) — the TIEP checkbox position "adopt C3a/C3b = recommend against" stands; after quorum counting, any residual tie (the most-frequent name has <2 seats) uniformly remains unnamed (the tie/split3/abstain3 patterns are recorded as before).
5. `undetermined*`/missing ballots do not count toward the quorum (same as C4).

Baseline numbers against v1=C4 (TIEP §2.1/§4, KB9 surface): P1 **22→29/33** (+7 flipped correct, 0 flipped wrong, P2=0 passes the gate); the two gates RUN4-r 15/22 and FACEV21 19/22 show zero perturbation (preservation clauses Q4::15∧Q5b::13 unchanged); across five rules × five surfaces **not one existing 'named and correct' conclusion was altered** (OVERTURN=0, hard-validated over the full 204-case difference set). Structural cost (said plainly): coarse:X is a semantic leap — a reader's self-reported low-resolution ballot is counted as a directional ballot; the 7/7 correctness on the KB9 surface is small-sample (n=3) evidence, not a guarantee.

## 2. Effective scope and per-run version declaration (D11 hard clauses)

1. **Effective going forward**: binds only runs pre-registered **after** this document's sign-off date (2026-09-27).
2. **Every run's pre-registration must declare the applicable ballot-rule version**: either `v1=C4` or `v2=C2b`, written explicitly into the PREREG; undeclared = no freezing, no starting.
3. **Historical frozen rulings are never rewritten**: the published numbers of RUN3/RUN4/RUN4-r/RUN5/RUN6-B/RUN7-RG/FACEV21/KB9 remain historical frozen values under the C4 caliber; the TIEP counterfactual re-tally is merely rule-selection evidence and is no basis for re-adjudication. If any rule would flip an existing PASS case into a wrong one, say so plainly; "using the new rules to rewrite the RUN5 conclusions" is itself a gate failure, not an overturn benefit (TIEP §5.1 inherited as-is).

## 3. Transition clause (D9 B-test; the sole exception, one-time)

D9 (RAG free-query A/B formal validation, plans/btest_20260927/) was pre-registered before this document's ballot-rule switch and is handled per the release document: **primary read = the current C4 ballot rules (preserving comparability with the 15/19 baseline); C2b computed mechanically and shown in the same table; zero extra seat ballots** (USER_DIRECTIVE_20260927_scoring_wave Supplement 2 D9 fork decided on the PI's behalf + the BRIEF_BTEST "parallel read" clause). This clause is valid only for D9's run and creates no "dual primary read" precedent; after D9, newly pre-registered runs follow §2.2 single-version declaration.

## 4. Accompanying execution clauses (all three items of the TIEP §4 recommended tier; D11 "hard-coded per the TIEP recommended tier")

1. **Effective-scope clause**: merged into §2 (new pre-registrations + effective scope = from the next run on + history not rewritten).
2. **P2 gate not automatically breached**: clusters newly named under the C2 tier **automatically enter the P2 contamination check** (a hit against the kb roster counts as P2); no gate change needed (measured P2=0 on the KB9 surface).
3. **Independent registration of vocabulary drift**: off-roster names on ballots (Keratocytes/Mac_DAM_LAM/coarse:Stromal etc.) are solved by no tie rule — from v2's effective date, every run's pre-registration must contain a clause **normalizing ballot names through the frozen crosswalk** (the crosswalk is a frozen artifact; its sha registered per run).

## 5. Runner landing points and reference implementation

- Inventory of the current voting implementations (list only, no changes; each run's warmup card forks per this list in the next wave): /mnt/D/EyeKB/plans/proto_v2_20260927/RUNNER_WATCHLIST.md
- C2b reference implementation: /mnt/D/EyeKB/plans/tiep_20260927/scripts/t1_revote.py (sha256 d321e793…) `rule_c2(bs, count_coarse=True)`; the C4 replica = `c4_consensus()` in the same file (the consensus/mode of 156 rows across the four surfaces reconcile row-for-row against the published artifacts: PASS).
- New annotation-protocol version (the in-place v1.1 stays untouched; copy, not move): /mnt/D/EyeKB/plans/ANNOTATION_PROTOCOL_v1.2.md §8.
