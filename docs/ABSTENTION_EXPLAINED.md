# Abstention: what it means, why it happens, and how to report it

An empty `celltype_ranking` is a first-class result, not a failure. This note explains what the
system knows at that moment, how to get a machine-readable reason, and how to describe abstention
to a reader without overstating or hiding it.

## 1. Why the system abstains at all

The scorer requires positive marker evidence. If none of the query genes appear in any candidate
panel, there is nothing to rank, and returning a best guess would mean returning a class chosen by
tie order rather than by evidence. Measured on the 28-volume evaluation corpus: when abstention is
forced open and a candidate is accepted on a single shared gene, only **34.3%** of the newly
answered cells match the reference label. Abstention is therefore protective; the cost of removing
it is larger than the cost of keeping it.

## 2. Asking for the reason

Set `EYEKB_ABSTAIN_REASON=1` and the response gains one additive key, written only when the ranking
is empty:

```json
"abstain_reason": {
  "cause": "tissue_out_of_scope",
  "causes": ["tissue_out_of_scope"],
  "n_query_genes": 10,
  "n_genes_with_hit": 1,
  "n_scored_classes": 1,
  "demoted": {"composite_superset": 0, "tissue_out_of_scope": 1,
              "increment_guard": 0, "state_program_only": 0, "cl_duplicate_collapse": 0}
}
```

The switch is off by default because writing the key changes response bytes; the frozen
default-face anchor (721 queries, 5,219,369 bytes, per-query identical) is unchanged when the
variable is unset. This was verified after wiring, not assumed.

## 3. The five causes, with measured scale

Counts are cells from the 28-volume evaluation corpus (1,495,330 cells, 721 clusters); 265,954 of
them abstain. Cause is the machine's own declared reason, one per query unless several filters
fired together.

| cause | cells | share | what it means | what to do |
|---|---|---|---|---|
| `no_marker_overlap` | 90,221 | 33.9% | none of the query genes appears in any panel | coverage gap: the vocabulary needs this cell type, or the markers are unusual |
| `tissue_out_of_scope` | 79,798 | 30.0% | a candidate existed but the declared tissue does not contain that class | check the volume's declared tissue; the excluded candidates are listed in `tissue_excluded_candidates` |
| `increment_guard` | 59,631 | 22.4% | a candidate from an increment library lost the incumbency margin | by design: increment entries must out-evidence the baseline, not tie it |
| `multiple` | 33,822 | 12.7% | two or more filters fired together | read `causes`, not `cause` |
| `state_program_only` | 2,482 | 0.9% | only state-program annotations matched, and those are not cell types | expected; see `state_annotations` |

## 4. A second view: is the reference label reachable at all

The taxonomy above is about our filters. A different question is whether the reference class could
have been reached from the query genes. Measured over the same corpus, using each cluster's full
30-gene marker list: **74.69%** reachable within the top ten genes, **13.10%** only within genes
11-30, **12.21%** not reachable at all against the shipped panels. The middle band is what a
fallback widening can address; the last band is a panel-content problem and cannot be fixed by any
ordering or width change.

## 5. How to write it in a report

State abstention as a rate with its causes, never as a single number: "the system returns no answer
for 17.79% of cells; 33.9% of those have no shared marker with any panel, 30.0% fall outside the
declared tissue scope, and 22.4% are held back by the increment guard." Then state the cost of
forcing answers, with the measured 34.3% figure, so a reader can see the trade rather than trust a
claim.

Do not describe abstention as "the model not knowing", and do not describe the tissue-scope share as
an error: in that bucket the best excluded candidate shares one gene in 84,678 of 107,798 cells and
two genes in 20,297, never five or more. The gate is withholding guesses, not answers.

## 6. Limits

These counts come from one evaluation corpus built from 28 public volumes and are stable for that
corpus only; they are not per-query guarantees. A single query can abstain for a reason not in this
table when several guards interact, in which case `cause` reads `multiple` and `causes` lists them.
