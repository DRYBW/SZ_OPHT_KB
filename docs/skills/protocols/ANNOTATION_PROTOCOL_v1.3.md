# Annotation Protocol v1.2 (EyeKB reading layer · freeze first, then compare)

> Version: v1.3 | Generated: 2026-09-28 | Card: t_e0f94d4f (H1M3-GRADE reading-sequence anchor implementation · directive addendum V, queue ②)
> Supersession: v1.2 (2026-09-27, t_03808fff) and v1.1 (2026-09-23, t_16c3e020) **stay in place as historical frozen artifacts**; this version = copy, not move (convention); body §0–§8 is as-is identical to v1.2; the sole addition = **§9 reading-sequence anchor (H1) clause** (H1-M3 implementation, per /mnt/D/EyeKB/plans/grade_anchor_20260928/GRADE_ANCHOR.md §3–§5 + USER_DIRECTIVE_20260928 addendum V, PI whole-chain authorization; effectiveness regime in §9.4).
> Historical version line (retained): v1.1 | generated 2026-09-23 | card t_16c3e020 (KB1v2-W3); v1.1's supersession record (v1.0 = BRIEF_KB1 K6 design draft, t_39182aa2 superseded before completion and never in force; implemented per BRIEF_KB1v2 W3 + REVIEWER_LLMANNOTATION_GUIDANCE_v1.md T1/T2/T3) is governed by the v1.1 original.
> Scope: consumers of the five EyeKB MCP tools (the OcularKB engine, T-ATLAS, the DR/RP lines, and any agent's human-in-the-loop annotation sessions).
> Red-line invariant (rewritten as "evidence-consumption discipline v2" by PI decision 2026-09-26, USER_DIRECTIVE_20260926_redline_rewrite.md): reading-layer evidence may be consumed freely (a core of this system's design); **the scoring/adjudication side MUST NOT consume evidence from the same source as the readings** (the extended REVIEWER_LLM T3 wording is in §0; historical frozen artifacts remain in force as worded at their freeze time).

## 0. Red lines (service-level, written into the MCP server docs and response bodies)

No signature, proportion range, or expectation list from RAG/baseline/disease entries **may be** converted into:
module scores, label weighting, confidence bonuses, candidate-ranking scores, or composite QC scores.
Literature may support human reading; disease rules produce only unscored context flags. Neither may slip into automated discrimination pipelines.
(The extended T3 wording of the Claude5 frozen ruling is fully inherited; REVIEWER_LLM noted "not entering the score ≠ having no influence", hence the sequencing control added in §1.)

## 1. Freeze first, then compare — four-stage process (REVIEWER_LLM T3)

| Stage | What to do | Frozen artifact | Prohibited |
|---|---|---|---|
| ① Data first | Mask the disease-group information that can be masked (retain essential metadata such as species and **actual sampled material**); complete technical QC, candidate identities, alternative explanations, and undetermined items | data version + label version + evidence record (hashes/timestamps of the three artifacts recorded in the audit file) | `get_disease_prior` MUST NOT be called in this stage; `get_tissue_composition` may be queried only by the actual sampled material — cross-material citation via "the disease occurs in this organ" is not allowed |
| ② Disease comparison | Present the disease entries and generate **context consistency/conflict flags only** (expected / unexpected / contamination-suspect); supplement citations | flag list + citation-verification record | Labels MUST NOT be changed |
| ③ Review changes | Any label modification MUST state: newly found data evidence + why the original candidate no longer holds | change audit table (old label → new label → new evidence → rejection reason) | **"Better fits disease expectations" alone MUST NOT serve as a modification reason** |
| ④ PI adjudication | Retain pre-/post-modification labels, rationale, and still-unresolved issues; finalize after the PI decides | adjudication record (including "insufficient evidence" as a legitimate conclusion) | The PI must not become the sole source of truth (T7, third step) |

## 2. Four-way disposition of unexpected findings (REVIEWER_LLM T3; no mixing of queues)

| Queue | Semantics | Destination |
|---|---|---|
| `out_of_baseline_coverage` | Beyond baseline coverage (baseline is a skeleton / range not estimable / material mismatch) | Record → evaluate baseline expansion (backfill the W1 skeleton mapping) |
| `conflicts_with_literature` | Conflicts with existing literature | Per-item citation verification + escalate the "priors-vs-data conflict list" to the PI |
| `technical_suspect` | Technically suspect (doublets/ambient RNA/low quality/stress/batch) | Enter the §3 technical-credibility gate review queue |
| `candidate_biology` | Candidate biological phenomenon | Follow the fixed T3 disposition chain: confirm the observation (coordinated expression within single cells? driven by a few outlier cells?) → exclude technical causes → identity-and-state qualification (cell cycle ≠ angiogenesis) → clinical context → independent validation (other donors/cohorts/spatial localization) |

An identity outside the list triggers only the `out_of_baseline_coverage` flag and **MUST NOT be force-retagged to a listed identity** (T2).

## 3. Three acceptance gates (REVIEWER_LLM T1 table embedded as-is) + three-way disposition

| Acceptance target | What to check | How the result is used |
|---|---|---|
| Identity evidence | Supporting evidence for the candidate identity, counter-evidence, distinctions from adjacent candidates; the applicability domain and uncertainty of the reference mapping | Decide whether the cluster can be labeled at broad-class level, at fine-subtype level, or must be kept undetermined |
| Population resolution | Whether mutually exclusive lineage programs are mixed at the single-cell level; whether identity boundaries persist after resampling, neighbor-parameter, and resolution changes | Decide to keep the current level, continue analysis, or report unresolved |
| Technical credibility | Doublets, ambient RNA, low quality, donor/batch effects, structural changes introduced by integration, and covariates such as the cell cycle | Judge whether labels or fine subdivisions may be driven by technical factors |

Implementation rules (T1 key adjustments, fixed item by item):
- The doublet rate is a **technical metric, not a resolution metric**; calibrate per library/donor × cell broad class × label level — do not judge all clusters with one global fixed threshold; re-check with independent clues such as lineage mixing and expression complexity.
- Marker consistency before/after integration is only one of the required checks; also check whether integration eliminated donor splitting and whether it wrongly merged distinct identities. More thorough batch mixing is by itself not evidence of success.
- Resolution stability evaluates the **identity conclusion**, not the stability of cluster IDs/cluster counts.
- UMAP distance, silhouette, and batch-mixing metrics MUST NOT be set as standalone pass gates (supporting diagnostics only).
- Threshold-calibration procedure: first define the allowed error types and acceptance metrics → select thresholds on a development set → validate on independent donors/cohorts → freeze; a new test set MUST NOT be tuned while inspecting results. **Report jointly: accepted-label error rate, coverage, abstention rate, per-class recall, and cross-donor stability** — to prevent inflating accuracy through mass abstention. No calibration data exist yet → all concrete thresholds remain "pending calibration" (EVAL_Rubric_v1.md).

**split-or-report three-way disposition (replaces the old "split by default")**: for a population judged inseparable, choose in order —
① evidence supports splitting → split; ② no evidence for splitting → **keep the coarser label**; ③ the population shows continuous structure (e.g. pericyte→myofibroblast transition, MG→macrophage activation) → **report the continuous/unresolved population**.
"Split" is not the default remediation; forcing continuous states apart manufactures new subtypes out of sequencing depth/donor effects.

## 4. Composition-baseline usage rules (REVIEWER_LLM T2; corresponds to kb/baselines/)

1. Select the baseline by the **actual sampled material** (PDR membrane ≠ healthy retina ≠ vitreous; the primary anchor for GSE165784 = same-material PDR membrane data).
2. Proportions are **donor-level conditional reference distributions** (median/IQR/range across donors), not targets that must be met;
   pooled global values suffer the large-donor leverage problem and are for comparative display only.
3. Baseline priority: same species, same material, comparable developmental stage → same material, closely related disease → same material, other disease/non-pathological → anatomy-related atlases/literature (downgraded reference; annotate the mismatches).
4. "Range not estimable" is legitimate; missing proportion data MUST NOT block annotation of a new tissue.
5. Proportions reflect "the cell composition captured under a specific experimental workflow", not an unbiased ground truth of the tissue.
6. Layers differing in enrichment/sorting/platform (scRNA vs snRNA) **MUST NOT be mixed** (e.g. the D001 NeuN+ layer vs the naive layer).

## 5. Identity hierarchy × state axes (REVIEWER_LLM T4; corresponds to disease-entry schema eyekb-disease/1.1)

- For each annotated object, store separately: identity hierarchy (broad class / fine subtype / deepest supportable level), state axes (proliferation/inflammation/ECM remodeling etc., may coexist), context (species/material/disease/applicability conditions), and evidence with uncertainty.
- "A macrophage population with an ECM-remodeling state" > inventing a new "disease-specific macrophage type"; do not force-binarize continuous states.
- Concept merging follows expression programs/lineages/context only (the concept-ID mapping in `kb/priors/concepts.tsv`), never lexical similarity; similar names do not merge automatically, and different names do not split automatically.
- When provenance evidence (e.g. microglial vs monocyte-derived) supports only transcriptional similarity, cap the conclusion at the transcriptional-similarity level.

## 6. Single-sample and control discipline (REVIEWER_LLM T3 case rules; project-wide)

- A single sample (e.g. RRD n=1) may be reported only as "observed in this sample…"; it MUST NOT be declared a general feature of the disease, and no cross-disease enrichment conclusions may be built on it; RRD is a different pathological state, **not a healthy negative control**.
- "A marker is missing" MUST NOT be mechanically treated as counter-evidence (dropout/depth/disease-driven expression change); a mixed cluster must not be judged from mean expression alone.
- Blinded-baseline declaration: artifacts that have already gone through membrane-related knowledge augmentation (e.g. the GSE165784 v2 draft) **MUST NOT be claimed** to be fully prior-free blinded baselines; they may serve only as "rules-off" baselines. Estimating the effect of knowledge exposure requires a new blinded-review design or new data.

## 7. Session trail (auditability)

Every annotation session must record: tools called + parameters + response summaries (mcp_calls*.jsonl), the hashes of the three frozen artifacts, the flag list,
the change audit table, and the PI adjudication record. Wiki pages carry version numbers (T5: literature links alone are insufficient for audit).

## 8. Voting-rule version declaration (added in v1.2, 2026-09-27; cites the decision document)

The vote-counting rule for multi-seat reading consensus has been upgraded by PI decision (USER_DIRECTIVE_20260927_scoring_wave addendum II, D11):

- **Decision document (sole authoritative definition source)**: /mnt/D/OcularKB/WIKI/PROTOCOL_VOTING_v2_C2b.md
  - v1 = **C4** (current baseline): naming ballots with grade∈{A,B} are counted; ≥2 seats with the same name establish the name; UNDET/coarse:/grade C are all discarded.
  - v2 = **C2b** (quorum + coarse ballots counted): naming ballots of any grade are counted; coarse:X counts toward label X's quorum; ≥2 seats with the same name establish the name; residual ties keep the cluster unnamed (S1 tie-breaking disabled).
- **Every run's preregistration MUST declare the applicable voting-rule version** (write one of `v1=C4` or `v2=C2b` into the PREREG); no declaration = no freeze, no start.
- **Effective scope**: v2 binds only runs preregistered after the decision document's sign-off date (2026-09-27); historical frozen adjudications are never retroactively altered.
- **Transition clause**: D9 B-test = primary reading on C4 + C2b computed mechanically in parallel (zero extra seat ballots), for that one run only; it sets no dual-primary-reading precedent.
- Runner-fork inventory (list only, no changes): /mnt/D/EyeKB/plans/proto_v2_20260927/RUNNER_WATCHLIST.md.
- This section does not conflict with §0–§7: the §0 red-line invariant (the scoring/adjudication side must not consume reading-side same-source evidence) applies equally to both voting-rule versions.

## 9. Reading-sequence anchor H1 (added in v1.3, 2026-09-28; implementation card t_e0f94d4f, preregistration PREREG_H1M3 sha 14fc3f8f…)

Nine-epoch counterfactual evidence (GRADE_ANCHOR §2/§4): the dominant form of reading-seat grade drift is **systematic over-conservatism that loses correct names**
(25 of the 28 named∧C ballots had hidden name == truth, 89.3%), not noise filtering; this clause cures grade-semantics drift with a protocol floor.

**9.1 Clause text (protocol floor)**: a named ballot (identity = a concrete label, not coarse:X/undetermined) MUST carry **grade≥B**;
"named∧grade-C" is an **illegal ballot shape**. Protocol intent: C = indistinguishable → the only legitimate outputs are a coarse call (coarse:<name>) or abstention (undetermined);
if you can name it = adjacent candidates have been excluded → at least B. If a seat insists on C while the ballot is named, the runner handles it per the §9.3 mode.

**9.2 Tiers (each run's preregistration MUST declare)**: whether the grade floor B is applied to named∧C ballots is decided by the tier predicate —
tier family `none / S / M / M2 / M3 / X` (predicates as-is = the GRADE_ANCHOR §3 table; the three gates fields are seat self-reports,
and trusting gate self-reports is at the same assumption level as trusting grade self-reports under C2b). **The recommended tier implemented in this version = H1-M3: `identity_evidence=pass ∨ resolution=pass`
→ floor to B** ("named + at least one discriminating gate passed = at least B"; the technical gate does not participate in the anchoring — isomorphic to the 3A no-demotion prohibition).
Named∧C ballots that pass no gate are **not raised** (the §9.5 inflation case is blocked exactly this way). Each run's PREREG MUST declare
`H1_tier: none|S|M|M2|M3|X` and `H1_mode: A|B`; no declaration = no freeze, no start (a hard clause alongside the §8 voting-rule version declaration).

**9.3 Disposition modes (declare one of the two in the PREREG)**:
- **Mode A (strong) = reject and re-vote**: named∧C ballots are never accepted; that seat's ballot for that cluster is voided and re-voted (re-votes count against the ballot budget);
- **Mode B (weak; the implementation tier of this wave's two-gate validation) = automatic flooring**: tier gate passed → the effective grade is set to B and an `anchor_applied` flag is recorded
  (per ballot, in the reading record table); gate not passed → keep C and record a `namedC_noanchor` flag (the ballot's original text is untouched; it is counted under the current voting rule after registration).
Per-run preregistered gate metrics RECOMMENDED to be pinned (following GRADE_ANCHOR §5.4): Mode A = named∧C stock remaining after acceptance = 0; Mode B = anchor_applied counts
with a case-by-case ledger of flips-to-correct / new errors; **the R1/R2/stability gates do not move** — the grade anchor's net effect is reported separately as a "flips-to-correct ledger" to prevent attribution confusion.

**9.4 Effective boundary (prospective effect, same regime as C2b)**: this clause binds only runs preregistered **after the sign-off date (2026-09-28)**;
historical frozen readings and published adjudications (RUN2-RUN7RG/FACEV21/KB9/BTEST/OBLIGRUN current-period 26/33 etc.) are **never retroactively altered**.
This clause governs grade ordering semantics and **does not rewrite the counting semantics of the approved voting rules**: under v1=C4 a non-raised named∧C was not counted anyway;
under v2=C2b named ballots of any grade are counted as-is (anchor document §4 "absorbability": flooring does not change NAMED/COARSE ballot shapes → the C2b consensus structure is identical;
non-tie/non-abstain handling stays as-is as in C2b). H1 and C2b are complementary, not conflicting — H1 cures grade-semantics drift; C2b cures coarse-ballot counting.

**9.5 H1-X disposition note (the grade-inflation case; X is banned as a tier)**: the pure-consistency anchor H1-X (raise every named∧C) produced, in the nine-epoch counterfactuals,
**the single empirical inflation case RUN5 Q6::31**: seat B's `Pericytes∧C` (identity_evidence=unresolved ∧ resolution=unresolved)
and seat C's `Pericytes∧B` — two wrong-name ballots, once the C-floor was counted — **mutually corroborated into a false majority**, flipping "unnamed" into "wrongly named" (new errors +1;
mechanism = the two-wrong-names corroborating-each-other hallucination). H1-M3's "at least one discriminating gate passed" condition blocks exactly this case (that ballot passed neither gate → not raised).
Therefore the **X tier is banned as a preregistration tier for new runs**; if pure-consistency-anchor semantics are needed, they MUST be preregistered together with the H3 flag (§9.7) shadow before deliberation may be allowed.

**9.6 Implementation components and validation trail (registered in this document)**: runner naming-chain component
`/mnt/D/EyeKB/plans/grade_h1m3impl_20260928/scripts/h1m3_runner_t_e0f94d4f.py` (ballot-shape parsing = as-is semantics of the C2b decision document §5
reference implementation; flooring/rejection = this clause §9.3; C4/C2b counting untouched). Two validation gates:
**G1 recomputation gate PASS** — 9 archives (RUN4-r/RUN7RG/FACEV21/BTEST-run1/2/RUN5/RUN6A/RUN6B/KB9) replayed through the component under H1-M3, **exactly equal
to the GRADE_ANCHOR reference document on every epoch** (raised 24 / hidden-name correct 22/24 = 91.7% / flips-to-correct 7 / new errors 0 / regressions 0;
out/g1_verdict.json); **G2 regression gate PASS** — OBLIGRUN v2 ballots, 99 votes: the C2b primary-column baseline reproduced 26/33, cluster-by-cluster 33/33 exact equality;
the C2b∘M3 sensitivity column 26/33, delta=0 (the absorbability prediction re-confirmed on the current-period new ballots; named∧C 13 votes = raised 11 / not raised 2;
out/g2_ballot_flags.tsv; all 13 hidden names are correct names — a re-confirmation of the drift pattern); the C4 reference column 18→23/33 (+5 clusters, registered, not gated).
Wiring this clause into the two production ballot-validation implementations under kb/ and mcp_server/ is in territory this document must not touch — the **component + clause are handed to REPOSYNC3 for same-source adoption**
(following GRADE_ANCHOR §5.2 "align the two kb/mcp implementations before implementing").

**9.7 Standby companion items (not implemented in this document; boundary statement)**: H2 inter-seat calibration soft prompt (adding the annotation-evidence-report tail sentence into the frozen artifact = an activation-class action, report separately to the PI);
H3 single-seat C-rate threshold-exceedance flag (A4 review layer, shadow first — record the flag only, no wiring); the counter-example teaching line in ANNOT_INSTRUCTIONS.md §grade-levels
(the Q5b::35 run1 seat-A ballot shape — kb/ territory, writes forbidden; registered for hand-off to REPOSYNC3).

**9.8 Red-line invariant**: the §0 red line (the scoring/adjudication side must not consume reading-side same-source evidence) applies equally to all H1 tiers — the anchor's decision inputs are the ballot's
self-report fields only (identity/grade/gates); zero label derivation, zero scoring-side inputs, zero new ballots.
