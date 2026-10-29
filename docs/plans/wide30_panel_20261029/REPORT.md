# Evidence panel width: 10 genes versus 30 genes

Executed 2026-10-29. Adjudication channel: an external OpenAI-compatible endpoint
configured through `OPENAI_*` environment variables, K=3 majority vote, thinking on,
25 volumes / 764 clusters. Endpoint and model identifier are recorded in the
evaluation workspace, not in this repository. **Only the evidence panel width
differs** between the two arms — same channel, same seed handling, same scorer, same
frozen crosswalk.

Artefacts: `JUDGE_SCORE_judge_prod_think_feimao.json` (10 genes, `ev/`) and
`JUDGE_SCORE_judge_prod_think_wide30.json` (30 genes, `ev_wide/`). Runs: 75/75 files,
2,292 cluster-calls, 2 call errors (two single clusters), 0 out-of-set labels.

## 1. Headline, official scorer denominator

Cell-weighted over `scored_cells` = 995,557, using the scorer's own per-volume
`coverage` / `top1_acc` / `macro_f1` fields.

| arm | coverage | top-1 accuracy | macro-F1 |
|---|---|---|---|
| 10 genes | 68.04 % | 66.91 % | 68.90 |
| **30 genes** | **75.38 %** | **75.06 %** | **75.01** |
| delta | **+7.34 pp** | **+8.15 pp** | **+6.11** |

Calibration: the 10-gene arm's 66.91 % reproduces `CHANNEL_COMPARE.json`
`human/new.acc_all` = 0.6691471 on the all-volume denominator, so this table is on the
same footing as the earlier channel comparison.

## 2. Where the gain comes from (cluster-equal counts)

These counts are **not** cell-weighted. Do not mix them with §1.

The 223 clusters that abstained at 10 genes:

| outcome at 30 genes | clusters | cells |
|---|---|---|
| now correct | **58** | 86,231 |
| now answered wrong | 26 | 26,452 |
| still abstained | 139 | 186,059 |

The 541 clusters that already answered at 10 genes:

| outcome at 30 genes | clusters |
|---|---|
| unchanged | 523 |
| fixed (narrow wrong → wide right) | 8 |
| **broken** (narrow right → wide wrong) | **10** |

So widening the panel moves 70 clusters out of abstention, 58 of them into a correct
answer, and costs 10 clusters that were previously right. Net +56 correct clusters.

**The honest cost is those 10.** They are listed in `WIDE30_VS_NARROW.json` under
`per_cluster` with `bucket == "now answered wrong"` and in
`answered_arm_change.broken`, and can be inspected cluster by cluster.

## 3. Why this is not "more guessing"

If widening the panel simply made the model commit more often, accuracy over committed
answers would fall. It does not: the cluster-level figure moves 81.70 % → 82.20 % over
the same clusters. The extra coverage is bought from clusters where the narrow panel
had no usable candidate at all, not by lowering the bar on the ones that already had
one.

## 4. Two wrong numbers I produced first, and why they are wrong

Recorded because both were plausible and both would have been reported as fact:

| attempt | value | why wrong |
|---|---|---|
| cluster-equal, all 764 | 56.54 % → 63.87 % | equal weight per cluster; the official table is cell-weighted, so small clusters dominate differently |
| cluster cells, all 764 | 60.71 % → 68.02 % | used every cluster's `n_cells` as the denominator; the official denominator is `scored_cells` = 995,557, which excludes 167,011 gap/unmapped cells |

Only the scorer's own fields reconcile with the previously published 66.91 %. The
lesson is the one already on record: **do not re-derive a published metric with a new
denominator and compare it to the old number.**

## 5. What this supports

The 30-gene panel is already computed and on disk; using it in the adjudication layer
costs no extra model time beyond the run itself and gains **+8.15 pp** top-1 accuracy
and **+7.34 pp** coverage. That is the largest single measured lever in this line so
far, and it is a data-side change, not a model change.

## Reproduction

```
cd docs/plans/wide30_panel_20261029/scripts
python compare_wide30.py          # cluster-level decomposition
python verify_wide30.py           # 18 assertions, exit 0
```

Both scripts read their inputs from `../out/` and take the workspace root from
`WIDE30_ROOT` (default: this plan directory). They also import `score_judge`, the
scorer that folds author vocabulary and KB vocabulary onto one family key; that module
and the per-cluster truth tables live in the evaluation workspace, not in this
repository. Point `WIDE30_ROOT` at a workspace that contains `score_judge.py` and
`score_corpus.py` to re-run them.

`out/WIDE30_OFFICIAL.json` holds both calibers side by side, with the cluster-level
block explicitly labelled as not cell-weighted. `out/JUDGE_SCORE_judge_prod_think_*.json`
are the two scored artefacts the scripts read, included so the numbers can be
recomputed without re-calling the model.