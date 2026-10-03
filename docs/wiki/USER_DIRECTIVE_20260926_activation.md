# USER_DIRECTIVE_20260926 — activation decision (v6 retina + face v2.1 + ocular-surface v6 switched into MCP)

- Decision time: 2026-09-26 (PI's as-is reply: "approved", applied to the project maintainer's three-item recommendation list; whole-chain release along the recommendation ballots)
- Basis document: /mnt/D/EyeKB/plans/face_v21_20260926/ACTIVATION_PROPOSAL_v21_DRAFT.md (the PASS artifact of FACEV21 card t_7ae5c3d4)
- Continues: USER_DIRECTIVE_20260925_eyekb_downstream_batch.md Supplements 4/5 (D8 dual-series re-exam + D9.1 defuse retest and reading-matrix pre-authorization) — this document is exactly the pre-authorization honored on the reading-matrix PASS branch

## Decision table

| # | Decision | Execution landing |
|---|---|---|
| A1 | **Approved**: switch v6 retina entries (markers_v6_retina_repair.json) + the FACE_PROTOCOL_V2.1 rendering rules to MCP activation (included in the default all) | activation card (dispatched by this directive) |
| A2 | **Approved + observation clause**: switch v6 ocular-surface entries (markers_v6_face_increment.json) to activation; after activation, one week of ballot-tracking sampling on live traffic — an anomalous trigger rate triggers immediate rollback (following the RUN6-B caliber; no new thresholds) | activation card + a follow-on ballot-tracking sampling card (the project maintainer dispatches it separately after the activation card closes) |
| A3 | **Not switched for now**: the lacrimal increment entries markers_v6_lacrimal_increment.json stay registered-but-inactive (no efficacy numbers); do not wire this round; do not re-report repeatedly | logged, awaiting assessment |
| A4 | One-month efficacy retrospective card: dispatched separately after activation (not in this wave) | deferred |
| A5 | Rollback plan: activation must be built as a switch (env/config level); rollback = restore the default behavior of the three incumbent libraries; the canonical serialization of the sf13-off state being fully equal to the pre_change baseline is the machine-readable acceptance artifact | activation-card acceptance item |

## External-wording release (part unlocked by the decision)

- From this directive, the proposal §III internal-efficacy wording is **approved** for use: "In the three-seat blinded re-test over 22 retinal hotspot targets + 23 control clusters, consensus hits went from 15/22 to 19/22 and control flips from 1 to 0; on the ocular surface, 33 clusters went from 21/33 to 22/33."
- Still prohibited (unchanged): no writing "repairs improved X%" as a generalized performance claim; single-configuration numbers (fixed question surface / frozen three seats / temperature 0.2) must not be extrapolated to the live distribution; post-activation single-seat live reading performance is unvalidated and must be labeled as such.

## Discipline red lines (inherited)

1. Zero touch on the frozen surfaces: existing frozen artifacts under kb/baselines, the v4.1/v5/membrane surfaces, and the evalset frozen products keep their bytes (self-attested with a PRE/POST sha record table).
2. The published v6 entry files themselves must not be modified (sha POST==PRE).
3. This round does not activate lacrimal, does not do the qc_flags case B, and does not change soft-prompt behavior (all three keep their existing calibers).
4. All intermediate artifacts retained; a card must be landed on completion or when blocked.
