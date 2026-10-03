# EyeKB Panoramic Project Review (late night 2026-09-28, filed by the project maintainer; on handoff, read this file + WIKI/INDEX first)

## In one sentence
The four-layer mirror of the ophthalmic-general "literature knowledge base + evidence service + reading system" is clone-and-run ready, and as of tonight it carries a **homogeneity contract** (results count as system output only when bit-for-bit identical on any machine).

## Status of the four layers
| Layer | Active | On the shelf / in build | Authoritative location |
|---|---|---|---|
| **KB entry layer** | KB1v2-0.6-kbgov5 production code (B5 cross-species governance default ON: mouse-origin queries get named refusals, env-rollbackable; human-origin 230 clusters zero displacement); v6 retina surface + ocular-surface face (k9_ocs 4 entries = case-B sidecar overlay, **default OFF**) | obligation run READY (99 ballots, P1=26/33≥24, ACTIVATION_READINESS.md) | kb/ 104 files, sha record table |
| **RAG literature layer** | MCP default library = **v2.0, 2,713 papers / 174,616 chunks** (the "latest ≠ default" caliber is recorded in the repo README) | **v2.4.2 = 3,869 papers / 242,928 chunks** (gate ③ 94.6%, first break above the 80 line), frozen not activated; fp16-slim release artifact 379MB (three-layer verification 41/41 zero drift) | EYEKB_DB_POINTER.yaml (the sole authoritative source of paper counts) |
| **Wiki knowledge layer** | 15 files + directive chain (Supplement 5 = whole-chain authorization / Supplement 6 = sensitive-data red line / Supplement 7 = Seurat probe + five disciplines) | — | <STORE>/WIKI/ (online) + docs/wiki (repo = masked mirror) |
| **Skill + reading layer** | protocol v1.3 (§9 grading-order anchors effective going forward) + ballot rules v2_C2b + golden 41 + evaluation exams (frozen surfaces); both skill mirrors in the repo | the OBLIGRUN / RAG three-layer acceptance-method sections landed fresh tonight | docs/skills/ + docs/plans/, a 2260-file evidence chain |

## Evaluation and governance lines
- The double-blind reading system: E1/E2 characterized W2, offline audit only (PI final ruling: "not a replacement, an aid"); E3 85.42% limited to the retina SOP; PME three batches 260/338=76.9%.
- The red line = evidence-consumption discipline v2 (legitimate on the annotation/reading side, same-source evidence banned on the scoring side, an automated-scoring stack needs separate PI approval, frozen artifacts are never rewritten).
- KBX external reference frame: GSE164403 in fact has no per-cell author labels (lesson recorded on the card); continue per the O2 external reference frame + anti-circularity gate.
- Mouse edition = the second line's mid tier (mouse_prod_v1, built 09-25); the heavy tier ruled dead (none of MOUSEEXT's 7 candidates is worth >1GB).

## GitHub mirror repository (DRYBW/SZ_OPHT_KB, private repo)
- Character = **the system deliverable itself** (the clone-runnable standard, PI decision 09-27).
- main evolution: e9117cd→b85c006→ea40bea→cf254ab (REPOSYNC1-3) → **a0ad857 (REPOSYNC4: the run-it-in-5-minutes card + the homogeneity contract's three locks — G1 environment lock requirements.repro.txt / G2 data lock Release-preset artifacts as the sole source / G3 acceptance gate verify_repro 41/41 — plus skills increment + the fp16-slim evidence chain) awaiting push**.
- Permanent gates: T7 own-data token scan ([sample-number prefixes]/[project-number prefixes]/drug names/comorbidity codenames etc. — hits are stripped; from the REPOSYNC3 first run HARD=0 it must run on every push); Release assets v2.3, six files frozen, zero movement; v2.4.2-rag-assets (3 slim files) in transit.
- Sensitive surface: patient-derived data / in-house multi-omics / internal codenames never enter the repo (Supplement 6); directive Supplement 6 in-repo = the masked version.

## Running tonight (do not dispatch overlapping work)
| Card / process | Content | Next action |
|---|---|---|
| t_5d18900e SEURATPROBE | registry author-annotated standard-set dual-track probe (install >1GB → stop the card and seek approval; pilot below the bar → NO-GO, fall back to the scanpy single track) | close card → report the three numbers + the second-vote recommendation |
| t_db0c8206 DISC_QANT | donor-rejection leverage + depth-displacement, read-only quantification | close card → checkbox table + three-tier thresholds to the PI |
| t_fa03e1d7 DISC_COMP | EXPECTED_COMPOSITION_v0 composition-prior surface (default OFF) | close card → surface + self-check flag report |
| proc_80f83ff871a1 | GitHub end-to-end run (awaiting the PI's device code 5765-E3BE): push a0ad857 → Release v2.4.2-rag-assets → upload 3 files → publish → server-side verification | success → fresh pull, re-run verify_repro to completion |
| cron | 10-03 09:00 A2 ballot-tracking weekly report; 10-05 09:30 B5 all-uppercase false-rejection T+7 (zero false rejections → all-clear; >0 → recommend switching to B4, awaiting the PI) | automatic |

## Awaiting PI's call (do not start work)
1. **Whether to approve activating the 4 k9_ocs ocular-surface entries** (obligation run READY; the recommendation ballot is in ACTIVATION_READINESS.md; caliber = engineering acceptance, not independent validation).
2. Activating / default-switching the v2.4.x RAG library (same origin as the permanent gate OB-5).
3. Choosing a threshold tier once the DISC_QANT checkbox table returns.
4. Ruling on the "second-vote promotion" once the SEURATPROBE three numbers return.
5. demo review / paper body text (never released).

## Risks and observation items
- B5 false rejection of all-uppercase human gene symbols (a design trade-off; the 10-05 calllog review is the backstop).
- The ra3 ledger's "beneficiary gene" annotations vs. title relevance = observation item (PMID 38003067 frog-paper case, already characterized as non-systemic; token fulfillment ≠ contextual support; contextual spot checks are scheduled before k9 activation).
- Channel pitfalls: the GitHub device-code one-time token (do not kill after TOKEN_OK; it can be recovered from the on-disk file); the oauth endpoint needs -m 35 on slow links; ps/pgrep can hang on this machine — avoid.
- The skills mirror = live files on the machine side; the repo = sanitized snapshot; subsequent iterations continue under "register every change, close the sync card".


> [Repo-surface note] In this file, literal own-identifier tokens have been masked per the T7 permanent gate (categories = sample-number form / project-number form / Chinese drug names / comorbidity-project codename / project English name / stage codename / internal field names / patient sample IDs). The online originals stay on the machine side; the per-file ledger = docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv. This note is a sync-card disposition trail and does not alter the normative meaning of the PI's clauses.
