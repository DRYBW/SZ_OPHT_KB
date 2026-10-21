# Pre-registered tissue declaration rule

Status: **frozen** (2026-10-21). Applies to every comparison in which a cluster's marker genes are
handed to `query_marker` with a tissue argument.

## Why this document exists

The tissue argument changes the answer. On a dataset whose content spans more than one tissue, the
same marker set scored under two different declarations produces two different agreement numbers:
one published evaluation reports 18.1% for a dataset declared `retina` and 42.8% for the same
dataset declared `ocular_surface`, and the same report states that the higher value was chosen
after both were seen. A parameter that can be picked after looking at the result is not a
measurement parameter; it is a degree of freedom that lets the metric be fitted. This document
removes it by fixing, in advance, how the declaration is derived.

## The rule

**R0 — the declaration is derived, not chosen.**
For a dataset *D*, the tissue handed to `query_marker` is the output of one function:

    declare(source_labels(D), crosswalk) -> tissue        # or MIXED_CONTENT

`source_labels(D)` is read from *D*'s own metadata; `crosswalk` is
`kb/baselines/_tissue_source_label_crosswalk_v1.json` (frozen, explicit, withdrawable). The output
is written into the dataset's record before the comparison runs. Nothing else may set the
declaration.

**R1 — the only admissible input is the dataset's own metadata.**
`source_labels(D)` is the set of tissue labels *D* carries in its own cell metadata (for a
CELLxGENE-style object: the distinct values of its tissue column, or its
`tissue_ontology_term_id` values resolved to labels), or the tissue field of the curated registry
row that *D* is delivered under. The comparison result is never an input. If a dataset carries no
tissue label of its own, its declaration is **underdetermined** (see below) and it cannot be
scored as a single-tissue dataset.

**R2 — the mapping is explicit and one row per label.**
Each source label maps to exactly one dictionary name, with its basis recorded. There is no
name-similarity inference and no fuzzy matching. A label that has no row is **unmapped**, and an
unmapped label makes the dataset underdetermined — the rule never guesses a tissue.

**R3 — admissibility, in this order.**
1. one dictionary name for the whole source-label set → that name is the declaration;
2. several names, but a dictionary name whose coverage row covers all of them → the coarsest such
   name is the declaration (fewest covered names wins; ties break alphabetically);
3. otherwise → **`MIXED_CONTENT`**: no single-tissue declaration is admissible. The dataset is
   scored per source-tissue partition (its own labels give the partition), or it is reported as out
   of scope for a single number. If a dataset-level number is reported at all, it is a
   composition-weighted aggregate of the partitions and is labelled as such — never the number a
   single declaration happened to give.

**R4 — a declaration may not move after a number exists.**
Once a comparison number for *D* has been produced under a declaration, that declaration is fixed
for that result. Changing it is an amendment: the previous number is void, both arms are reported
under the amended declaration, and the amendment carries a date, the reason, and the derivation
trace that justifies it. A dataset may be run under a second declaration for diagnosis; that arm
is labelled a diagnostic arm and is excluded from the headline number. A declaration that is
re-derived after the fact and happens to score higher is not an amendment — it is a failed
check. `tests/check_tissue_declaration.py` enforces this by deriving the rule's own outcome and
comparing the declared value against it.

**R5 — every dataset record carries the derivation.**
`dataset_id`, `source_labels`, `declared_tissue`, `declared_from` (the metadata field or the
pre-registration document), `frozen_at` (date or commit), and the derivation outcome. The record
is what makes the declaration auditable without re-running anything.

**R6 — what the service is told, and what it reports back.**
The declared tissue is passed to `query_marker`; the service reports the narrowing it applied and
its reasons (`EYEKB_TISSUE_SCOPE`, `switch_off` / `out_of_scope` style reasons). The service is
not responsible for the declaration and must not infer one: it applies what it is given. This
checker validates the declaration table, not the service.

## Underdetermined cases: what would settle them

| situation | the rule's outcome | what settles it |
|---|---|---|
| a source-label set no dictionary name covers (e.g. a whole-eye dataset with retinal + anterior labels) | `MIXED_CONTENT` | a partition of the comparison by the dataset's own source-tissue labels (per-cell labels make this mechanical); the per-partition numbers are then reportable |
| a dataset whose metadata has no tissue label at all | underdetermined, no single-tissue declaration | the dataset's deposition record or the curation it was delivered under; until then it cannot be a single-tissue datum |
| a source label with no crosswalk row (e.g. `eye`, a composite label) | underdetermined | a reviewed crosswalk row with a stated basis, or a partition as above |
| a dataset whose content and its declared source disagree | the declaration still comes from the metadata; the disagreement is a *finding about the dataset*, recorded, not a licence to redeclare | adjudication by whoever curates the dataset; the comparison reports the disagreement either way |

## Worked illustration (not a measurement of the datasets named)

The two declarations in the report cited above, run through the rule, with the dataset content as
the report describes it:

| dataset (as described) | source labels | rule outcome | is the reported declaration admissible? |
|---|---|---|---|
| a whole-eye dataset with 11 source tissues | `retina`, `lens`, `iris`, `ciliary body`, `cornea`, … | `MIXED_CONTENT` | no — `ocular_surface` covers the corneal/conjunctival surfaces only, so neither `retina` (18.1%) nor `ocular_surface` (42.8%) is a rule-admissible single-tissue declaration; the dataset needs a per-source-tissue partition |
| a posterior-eye atlas declared `ocular_surface` | retinal + optic-nerve labels | `MIXED_CONTENT` | no — same reason |

Illustrative inputs only: these label sets are taken from the cited report's description of the
datasets, not measured here. The rule was written against this repository's tissue dictionary and
the CELLxGENE tissue vocabulary, before any of these datasets were examined, and no row of the
crosswalk was added to move a number.

## Files

| file | role |
|---|---|
| `kb/baselines/_tissue_source_label_crosswalk_v1.json` | the frozen mapping and coverage rows (the rule's only parameter) |
| `tests/check_tissue_declaration.py` | the checker: `--table` judges a declaration table, `--explain 'a;b'` derives a declaration, `--selftest` runs the rule's own cases |
| this document | the rule text (R0–R6), the underdetermined table, the illustration |

Exit codes of the checker: 0 admissible and pre-registered, 1 a row fails (the failure names the
check and the row), 2 usage error, 3 the rule's inputs are not on disk (no judgement is made —
this is what keeps "the crosswalk is missing" from being reported as "the declaration is wrong").