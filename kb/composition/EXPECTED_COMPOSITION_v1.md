# EXPECTED_COMPOSITION_v1 — Composition Prior Face v1 (conditional stratification; default OFF)

> Card t_37a35220 | Release=USER_DIRECTIVE addition eight | Rule pre-registration=PHASE0_INVENTORY_t_37a35220.md | v0 three items bytes unchanged

> **⛔ unwired; flags = review prompts ≠ annotation errors; activation is forever reserved to the PI.**

## 1. Retina Condition Layer (library/sampling/sorting strategy; unit=donor×tissue×enrichment, adult-only)

| Class | v0 envelope [low, high] | RC1 unsorted whole-region A/B | RC2 unsorted central A/B | RC3 unsorted peripheral A/B | RC4 sorted/targeted A/B |
|---|---|---|---|---|---|
| Rod | [22,58] | [32,66] / [28,66] (n=130) | [17,51] / [17,56] (n=82) | [62,70] / [28,70] (n=48) | [2,27] / [2,56] (n=80) |
| Cone | [1,7] | [2,6] / [1,7] (n=130) | [3,7] / [1,7] (n=82) | [2,4] / [1,7] (n=48) | [0,5] / [0,7] (n=80) |
| BC | [12,33] | [15,30] / [12,33] (n=130) | [21,33] / [12,33] (n=82) | [13,17] / [12,33] (n=48) | [0,18] / [0,33] (n=80) |
| AC | [6,28] | [5,11] / [5,28] (n=130) | [7,12] / [7,28] (n=82) | [4,7] / [4,28] (n=48) | [15,45] / [8,45] (n=80) |
| HC | [1,8] | [1,7] / [1,8] (n=130) | [3,9] / [1,9] (n=82) | [1,2] / [1,8] (n=48) | [0,1] / [0,8] (n=80) |
| RGC | [0,15] | [0,6] / [0,15] (n=130) | [2,9] / [2,15] (n=82) | [0,1] / [0,15] (n=48) | [0,69] / [0,69] (n=80) |
| MG | [3,12] | [6,13] / [3,13] (n=130) | [6,15] / [3,15] (n=82) | [5,10] / [3,12] (n=48) | [0,5] / [0,12] (n=80) |
| Astro | [0,2] | [0,2] / [0,2] (n=130) | [0,2] / [0,2] (n=82) | [0,1] / [0,2] (n=48) | [0,1] / [0,2] (n=80) |
| Micro | [0,1] | [0,1] / [0,1] (n=130) | [0,1] / [0,1] (n=82) | [0,1] / [0,1] (n=48) | [0,1] / [0,1] (n=80) |
| RPE | [0,1] | [0,0] / [0,1] (n=130) | [0,0] / [0,1] (n=82) | [0,0] / [0,1] (n=48) | [0,0] / [0,1] (n=80) |

Note: A = strict donor band (preregistered primary caliber), B = verbatim envelope of the v0 formula (post-hoc sensitivity); A is essentially the central-50% band and inherently narrower than the v0 triple envelope — the semantic choice belongs to the PI.

RC4 members=NeuN+ FACS ∪ Chen_rgc ∪ Shekhar_GSE237204 (baselines existing targeted design declarations on disk).

## 2. OB-3 Stratified Reverse QC Recalculation (20% line unchanged; judgment based only on pre-registered R1A)

| Dataset | Platform | R0 v0 | R1A Stratified (primary) | R1B Envelope (sensitivity) | R2 Unit Mean A | R2 Unit Mean B | R1A Verdict |
|---|---|---|---|---|---|---|---|
| Q1_Lukowski2019 | cell | 4/10=40.0% | 4/10=40.0% | 3/10=30.0% | 4/10=40.0% | 3/10=33.3% | TRIGGER |
| Q2_GSE155288 | cell | 4/10=40.0% | 6/10=60.0% | 4/10=40.0% | 6/10=65.0% | 6/10=60.0% | TRIGGER |
| Q3 | smart-seq cell | 3/10=30.0% | 5/10=50.0% | 3/10=30.0% | 6/10=55.0% | 4/10=40.0% | TRIGGER |
| Q4 | cell+CD73/90 sorted | 2/10=20.0% | 4/10=40.0% | 1/10=10.0% | 5/10=50.0% | 3/10=27.1% | TRIGGER |
| Q5b | nucleus | 0/10=0.0% | 4/10=40.0% | 1/10=10.0% | 4/10=36.9% | 2/10=24.6% | TRIGGER |

**R0 reproduction gate 5/5 PASS (incl. Q5b 0/10). Under R1A, 5/5 all TRIGGER → the OB-3 target <20% is not met; the gap is reported as-is (§4 + V1_VERDICT).**

### Per-row Attribution (PERSISTS=all three rules flagged / NEWFLAG=only strict layer new / RESOLVED=stratification eliminated)

| Dataset | Row | Observed % | v0 | A | B | verdict |
|---|---|---|---|---|---|---|
| Q1_Lukowski2019 | Rod | 62.15 | FLAG | ok | ok | RESOLVED_by_layering |
| Q1_Lukowski2019 | BC | 10.51 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q1_Lukowski2019 | AC | 1.43 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q1_Lukowski2019 | HC | 0.0 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q1_Lukowski2019 | MG | 3.11 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q2_GSE155288 | Rod | 30.01 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q2_GSE155288 | BC | 32.61 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q2_GSE155288 | AC | 2.41 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q2_GSE155288 | HC | 0.69 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q2_GSE155288 | MG | 27.51 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q2_GSE155288 | Micro | 1.83 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q3 | Cone | 1.05 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q3 | AC | 2.47 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q3 | HC | 0.73 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q3 | RGC | 7.54 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q3 | MG | 26.22 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q4 | Rod | 8.32 | FLAG | ok | ok | RESOLVED_by_layering |
| Q4 | BC | 30.25 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q4 | HC | 3.37 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q4 | MG | 23.41 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q4 | Astro | 1.35 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q5b | Rod | 26.12 | ok | FLAG | FLAG | NEWFLAG_under_strict_layer |
| Q5b | AC | 27.4 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q5b | MG | 4.18 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q5b | RPE | 0.02 | ok | FLAG | ok | NEWFLAG_under_strict_layer |

## 3. OB-2 Ocular Surface Type×Region Rows

| Type | cornea | corneal endothelium | corneo-scleral junction | ocular surface region | sclera | v0 mixed row [low, high] |
|---|---|---|---|---|---|---|
| Corneal Endothelium | [0,0] n=29 | gate-fail→v0 | [0,0] n=22 | gate-fail→v0 | [0,0] n=10 | [0,1] |
| Endothelium | [0,2] n=29 | gate-fail→v0 | [5,13] n=22 | gate-fail→v0 | [8,18] n=10 | [0,9] |
| Epithelium | [29,80] n=29 | gate-fail→v0 | [36,68] n=22 | gate-fail→v0 | [0,3] n=10 | [7,71] |
| Fibroblasts | [14,68] n=29 | gate-fail→v0 | [7,38] n=22 | gate-fail→v0 | [34,52] n=10 | [12,45] |
| Immune Cells | [0,2] n=29 | gate-fail→v0 | [0,3] n=22 | gate-fail→v0 | [0,5] n=10 | [0,3] |
| Melanocytes | [0,1] n=29 | gate-fail→v0 | [0,5] n=22 | gate-fail→v0 | [0,6] n=10 | [0,3] |
| Pericytes | [0,1] n=29 | gate-fail→v0 | [2,7] n=22 | gate-fail→v0 | [12,35] n=10 | [0,5] |
| Schwann Cells | [0,0] n=29 | gate-fail→v0 | [0,2] n=22 | gate-fail→v0 | [0,3] n=10 | [0,2] |
| Smooth Muscle Cells | [0,0] n=29 | gate-fail→v0 | [0,0] n=22 | gate-fail→v0 | [0,1] n=10 | [0,1] |

### Q6 (D002 sub100k, adult-only 76,708 cells) Regional Recalculation

| Region | Evaluated Rows | Flags | Details |
|---|---|---|---|
| cornea | 0 | 0 | - |
| corneal endothelium (separate layer, only 404 cells) | 0 | 0 | - |
| corneo-scleral junction (limbus region) | 9 | 1 | Smooth Muscle Cells 0.13% vs [0.0,0.0] FLAG_ABOVE |
| ocular surface region (mixed) | 0 | 0 | - |
| sclera | 9 | 1 | Smooth Muscle Cells 3.1% vs [0.0,1.0] FLAG_ABOVE |
| ANY(v0 mixed, adult-only) | 9 | 1 | Pericytes 5.77% vs [0.0,5.0] FLAG_ABOVE |

v0 mixed row Pericytes flag (6.5%>[0,5]) fully eliminated under regional rows=pure regional mixing pseudo-flag; SMC new flags in limbus/sclera retained honestly (cost and benefit of regional row semantics both on disk).

## 4. OB-1 Search Declaration (two rows missing PMID)

- Search face: full chunks.parquet 242,928 chunks on disk (zero external network) + v0 ledgers cross-reference.
- **Goblet_cell**: 480 chunks hit → 12 windows in ocular surface context → **0 sentences** passed after triple filtering (all numbers were false positives from reagent concentrations/surgical success rates/re-epithelialization area rates) → **maintain null(no_evidence)**.
- **Pericytes**: 2,574 chunks hit → **0 windows** for quantitative ocular surface composition → **maintain null** (Grade A interval rows unchanged).
- Audit trail for all 108 candidate windows: ob1_lit_candidates.tsv.

## 5. Red Lines and Boundary Declarations

- Zero touch on v0 frozen artifacts and evalset/tickets/kb/mcp_server (self-proven via before/after sha ledger logs/SHA_BASELINE_post).
- wiring=OFF: this file enters no runtime path; activation is forever reserved to an explicit PI decision.
- Goals and criteria are not adjusted: The 20% line, donor-level distribution method, support gate (≥5 units), and interval formula shape (including verbatim min/max envelope for B variants) remain fixed; stratification = adding dimensions.
- Prohibition of circular derivation: Regions/enrichments come entirely from D001/D002 portal author annotation lineages + existing design declarations on baselines disk; no data taken from own clustering; Q6=circular reference is sanity check only, not part of adjudication.
- Denominator semantics inherited from v0 (capture event composition reference, not histological ground truth, not compliance threshold); exclusion of fetal/organoid/developing inherited.
