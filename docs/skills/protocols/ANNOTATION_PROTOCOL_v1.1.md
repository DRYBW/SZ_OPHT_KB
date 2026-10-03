# Annotation Protocol v1.1 (EyeKB reading layer · freeze first, then compare)

> Version: v1.1 | Generated: 2026-09-23 | Card: t_16c3e020 (KB1v2-W3)
> Supersession: v1.0 (BRIEF_KB1 K6 design draft, t_39182aa2) was superseded before completion and never took effect; this version
> implements BRIEF_KB1v2 W3 + REVIEWER_LLMANNOTATION_GUIDANCE_v1.md T1/T2/T3 directly.
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
