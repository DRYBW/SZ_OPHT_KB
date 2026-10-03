# D8 efficacy-retest twin-series record (night of 2026-09-25; RUN6-B ocular surface + RUN7-RG retina, 22 targets)

## RUN7-RG (t_09ca801c, plans/run7rg_20260926/)
- Preregistration: RUN7RG_PREREG.md sha `2cab65e2…` (sha committed to paper before the build; the 11 read-only inputs re-checked with two sha passes before/after the start — unchanged)
- Surface: 45 clusters (22 targets = RUN4-r's original targets with not one word changed + 23 controls = RUN3 clusters both readers got right), v6 entries + FACE_V2 evidence surface (2B priority placeholder window + 3A flag); three seats = qwen3.8-max/glm-5.1/deepseek-v3.2, temperature 0.2, all rerun from scratch
- Results: **R1=17/22 PASS** (baseline 15/22, +2: Q4::15, Q5b::13 — exactly RUN4-r's three-ballot split residue, the second validation of the attribution prediction; 0 lost); **R2=4/23 FAIL** (≤1 gate breached): Q5b::2 downgraded to abstention triggered by the 3A description flag / Q7::52, Q7::58 pulled toward AC by v6 cross-species ranking noise / Q4::23 a v6 RPE entry hit introduced a new lineage conflict and the cluster collectively abstained
- Q2::22 reverse validation landed on frozen-matrix branch `repair_ineffective_for_cluster`: no consensus in the main run (1 named ballot across three seats); after deleting the entry + hint, 2/3 of the ballots returned to MG instead — the misleading source sits in the gene-set priors (GLUL/VIM/CLU ambiguous co-expression), not only in the entry
- **MCP activation-switch recommendation = negative**; three face v2.1 repair points (new preregistration pending PI): (a) add a "MUST NOT be used as downgrade grounds" instruction line to the 3A flag, or retract the flag; (b) retract the v6 ranking for the Q7 cross-species clusters, or add ortholog back-validation; (c) refine the resolution decision order for RPE×BC conflict clusters; expected to preserve the +2 gain
- Goalpost-move guard: this document does not add protocol re-tests; archived alongside the RUN4-r PASS with per-cluster attribution returned to the PI

## RUN6-B (t_6951c807, plans/run6b_20260926/)
- Framework: Q6_VOCAB2_TRUTH_HIERARCHY_PREREG_v1.0 (sha 800d5db1…, left untouched) + frozen execution config RUN6B_FACE_SPEC.md (sha c9fbda97…) + new-surface sha 206badfa… (FACE_V2 slice + v6 ocular-surface entry-hit layer; production MCP stdio query_marker library=face_v6, 47 live calls with logs kept)
- Same three seats, temperature, and prompts as RUN5 (no swapping seats or models); 33/33×3 with zero missing
- Results: **P1=22/33** (baseline 21/33, Δ+1: entry backfill flipped 4 to correct; C-seat off-lexicon bandwagon votes + granularity ambiguity flipped 3 to lost); **P2=1/33 — pass by a hair** — the violation is still Q6::24; all three seats saw the mural soft prompt yet the SMC takeover was still not blocked
- First test of soft prompts under real traffic (report only, no adjudication): mural triggered 8/33 (all stromal/mural-cell clusters); rod_bc 0/33 (face_v6 has no Rod/BC structure — reported as-is, threshold tuning forbidden); note-visible ballots changed verdict 10/24, at the same level as the note-free control's noise interval; citation rate 23/24 (with a caveat for channel confusion involving granularity notes); full cluster×seat matrix, 99 rows = softflag_followup_table.tsv
- Side output: v6 ocular-surface ranking empty rate 19/33 vs the RUN5 old 43-class surface 9/33 (empty = no misleading priors, but narrow bandwidth); the impact has been booked in the P1 transition ledger

## Status and pending decisions
- Activation stays negative = current policy; awaiting PI: ① release for the face v2.1 defuse-and-retest; ② harden the soft prompts (mandatory review step / folded into voting) or stop there and write the result into the M1 discussion section; ③ open a new line for gene-prior ambiguity, or just book it
- Directive landed in USER_DIRECTIVE_20260925_eyekb_downstream_batch.md addendum 4 (D8); the INDEX late-night 09-25 entry carries the day's 21-card master ledger
