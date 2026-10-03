# USER_DIRECTIVE 2026-09-25: EyeKB downstream batch release (PI "ok"; recorded on the PI's behalf by the project maintainer AGENT_ROLE)

## Semantics
The PI replied "ok" to the 7 pending items (plain-language checklist) the project maintainer listed. Per the established decision semantics = **authorization of the entire downstream chain**:
items on the checklist marked "recommended" land as recommended; items without a recommendation do not auto-start (see "Deferred").

## Released items (scope of this directive)

| # | Decision | Execution landing |
|---|---|---|
| D1 | Of the KB6 audit, the 17 red entries are **revised per the REVCAND_KB6_v2.tsv revision-candidate table** (rewrite/downgrade/delete per the candidate table's suggestions; per-gene literature gates follow the KB4 six-mandatory format) | card KB7 (merged with D2 B1/D3; one card per territory to prevent double-writing) |
| D2 | Adnexa ingestion: **A1 lacrimal gland + A2 meibomian gland = accept**; A3 orbital fat on hold; A4 extraocular muscle not accepted; **B1 ocular-surface entry increment = do immediately** (folded into the KB7 card) | A1/A2 first get a retrieval-precheck card (zero downloads; produce accession + measured volume + direct-link list, **then seek approval**); download actions need separate approval; automatic execution prohibited |
| D3 | **v6 panel card opened**: the 7 genes of the MG re-export candidates, the RGC watchlist (UCHL1/STMN2/PRPH/SNCG; counter-examples PVALB/PCP4 banned as RGC), the Astro candidates (TNC/CLDN11/MGST1/GYPC), and the ocular-surface stroma surviving anchors (KERA true anchor + COX4I2/PCP4/DCN dual-cohort candidates) enter the pool; each gene passes the literature gate + OLS back-verification, then releases versioned | KB7 card |
| D4 | **Two soft prompts onto MCP**: a) rod-dominant yet judged-BC clusters → review reminder; b) mural family (Pericyte/SMC/Fibroblast/Keratocyte/Myofibroblast) shared-marker crosstalk → review reminder. No hard flags, no scoring changes | soft-prompt card |
| D5 | The Q2 external-evaluation primary caliber = **maintain alpha** (C19 not expelled, A 64%/B 76%, consistent with the current headline caliber of USER_DIRECTIVE_20260924_q2_maincaliber.md); beta is kept in parallel as a sensitivity caliber; any cited number must state its caliber | bookkeeping decision, no computation |

## Deferred (not released; awaiting the PI's call)
- The three exam-paper rule proposals (putting the model distribution on the evidence surface / top20 window truncation / question-surface quality flags) — they touch the face protocol and need a fresh pre-registration; awaiting the checkboxes.
- P1 demo review, mouse annotation model, starting the M1 paper — awaiting the PI's schedule.

## Discipline red lines (inherited, all written into the task briefs)
1. Download-approval iron rule: >1GB requires listing the inventory and getting PI approval first; silent downloads prohibited; approved-for-ingestion != approved-for-download.
2. Zero modification of frozen artifacts: panels get versioned new files; in-place overwriting prohibited; red-entry revisions go through .bak pre-images + a sha record table.
3. All CL IDs must be OLS back-verified (including any identifier in this directive and in task briefs; the executing side must not copy them as-is).
4. Self-check gates are never lowered; tuning thresholds to force hits is prohibited; if not met, report FAIL honestly and do not publish.
5. The runner script must call kanban_complete/kanban_block to land the card upon completion or when blocked (3 prior offenses).
6. All intermediate artifacts (scripts/logs/figures/intermediate tables) are retained; deletion prohibited.

## Status
- PI semantics: 2026-09-25, replied ok to the 7-item plain-language checklist (MSG_PLATFORM)
- Effective: immediately
- D5 was settled by the project maintainer as the current-state default (alpha) per the 09-24 directive; the PI may re-rule to beta at any time.

## Supplement (second wave, same day): PI "no downloads needed — whatever else you can do, do it"
= full release of everything that can progress with zero downloads; three cards dispatched (all read-only/light compute, touching no unauthorized writes):
- t_ (FACEQUANT) on-disk counterfactual quantification of the three exam-paper rule proposals → produce a checkbox sheet for the PI; **this wave does not release the protocol changes themselves**; the proposals still await the PI's checkboxes.
- t_ (MOUSE-PRE) mouse-model prerequisite precheck + three-tier cost-quote design (GSE243413 on disk, zero downloads); **no training, no version build**; GO still awaits the PI seeing the quotes.
- t_ (M1-PREP) M1 materials index + figure skeleton + gap list (read-only + web retrieval); **no body text written**; starting still awaits the PI's call.
Adnexa DNA: the ADNEXA precheck card produces the approval-request list as usual (the list itself is zero-download).

## Supplement 2 (same day 16:4x): adnexa download ruling = "the MB-scale ones are fine, forget the GB ones"
- **Approved (MB-scale, ~140MB total)**: GSE164403 (the only true human lacrimal atlas, 13.9MB, P0), GSE252058 (lacrimal sac disease reference, 93.4MB), GSE174653 (organoid, 7.9MB), GSE17822 (meibomian gland MGD microarray, 10.2MB), GSE288952 (MG cell line, 14.8MB).
- **Not approved this round (GB-scale, stay on hold; do not re-list)**: Tabula Sapiens Eye subset 1.4GB, SRP497138 meibomian scRNA 171.7GB.
- Boundary note: the C-arm line GSE199013 corneal layers 0.1095GB falls within the existing "<1GB approval-free" discipline (already handled by the parallel lines t_d8a41542/t_be247578) and does not conflict with this ruling.
- Wave three launches accordingly: ADNEXA-DOWN (download/ingest the approved items), KB7-WIRE (v6 wired into MCP + soft-prompt consolidated release), HC-LITRE (HC 8 candidates + statistically-strong-literature-weak list re-audit).

## Supplement 3 (same day evening): PI "you can go ahead" = two releases
- **D6 three-proposal checkboxes = per the recommended tiers 1B / 2B / 3A** (1B: model prediction enters the evidence surface only as a ≥0.9 high-confidence hint; 2B: panel hits get priority slots, window stays 20; 3A: purely descriptive question-surface flags, no filtering). Basis document = plans/face_protocol_quant_20260925/FACE_QUANT_FOR_PI.md tail-end checkbox table; checkbox ≠ effective — a fresh pre-registration is still required (the FACE_QUANT red-line statement).
- **D7 mouse mid-tier GO** (rebuild the v1.4-caliber 10-class production model + BMR prospective agreement report-style + light-tier natural coverage; the heavy tier does not start = no GB downloads).
- The KB8 lacrimal-entry card (t_e7ec73ab) launches first and is running; the PREREG-FACEV2 card and the MOUSE-MID card launch with D6/D7.

## Supplement 4 (same day late night): PI "good" = efficacy re-exam chain released (D8)
- **D8 = dual-series re-exam GO**: ① RUN6-B ocular surface, 33 clusters re-tested (within the Q6_VOCAB2 frozen pre-registration framework: v6 ocular-surface entries + evidence surface v2.0 + the two soft prompts measured by ballot tracking on live traffic; baselines = RUN5 21/33 and P2 1/33); ② RUN7-RG retina, 22 hotspot targets re-tested (**fresh pre-registration, sha before run**: v6 repaired entries + face_v2 evidence surface; same targets same gate >=15/22 not lowered by one character; the three-ballot protocol reused as-is from RUN4-r; baseline = RUN4-r 15/22).
- Caliber red line (hard-coded in the pre-registration): this round = efficacy validation, not a go-live declaration — **until the hit-rate-improvement numbers exist, external material must not write "repairs improved X%"**; the original RUN5/RUN4 FAIL files stay archived permanently as controls; the soft-prompt ballot-tracking rate is measured on live traffic for the first time — a trigger rate too high or too low is both reported honestly, no parameter tuning.
- The MCP **activation switch for v6/lacrimal entries is still not part of this document** — after the two series' numbers return, the PI rules on the activation approval.

## Supplement 5 (09-25 late night): PI "keep going" = the three D9 dispositions
- **D9.1 face v2.1 defuse-and-retest = released**: build v2.1 per the three repair points listed by RUN7RG (add a "must not be used as a downgrade basis" directive line to the 3A flag; either withdraw v6 ranking for the cross-species Q7 cluster or add ortholog back-verification; refine the resolution rule order for the RPE×BC conflict), **fresh pre-registration, sha before run**; gates not lowered by one character (R1>=15/22, R2<=1/23). Reading-matrix pre-authorization: both lines pass → produce the "activation proposal pack" (including recommended wording) and **await the PI's activation ruling; no automatic switch**; either line fails → FAIL lands on the card and is escalated; **no self-initiated third re-test round (anti goal-post-moving)**.
- **D9.2 soft-prompt behavioral finding = into M1 materials, not hardened**: the mural note was cited in 23/24 ballots yet all three seats on Q6::24 still judged SMC — "saw and cited it but did not change the judgment" is a protocol-level negative result, kept as M1 discussion-section material (plans/m1_prep_20260925/M1_ADDENDUM_D9_20260926.md); wording upgrades / folding into the voting system are revisited once the v2.1 numbers return.
- **D9.3 gene-prior ambiguity (GLUL/VIM/CLU co-expression) = into M1 materials + logged open**, no standalone card; if the activation proposal is approved, then evaluate opening a "prior layer" research line.
- The GitHub private repo stays ready; **push the moment the PI supplies the fine-grained token** (blocks none of the above).
