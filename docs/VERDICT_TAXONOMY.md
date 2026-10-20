# Verdict taxonomy: one definition per cell, two axes

Two different questions get asked about the same annotated cell, and they were being answered by
different scripts with different vocabularies. This file fixes both axes and the rule that keeps
them from being mixed. `tests/check_verdict_taxonomy.py` enforces it on any summary table.

## Axis A - relation between our call and the author's label

Every cell lands in exactly one state. The seven states sum to the cell total.

| state | meaning |
|---|---|
| `same_cl` | our predicted class carries the same Cell Ontology term as the truth |
| `we_finer` | our class is a descendant of the truth term (strictly more specific) |
| `we_coarser` | our class is an ancestor of the truth term (strictly less specific) |
| `kb_lacks_class` | the knowledge base has no class anywhere in the truth lineage |
| `mismatch` | our class and the truth term are in unrelated branches |
| `abstain` | no candidate was returned for the cluster |
| `unmappable` | no Cell Ontology term on one side, so no relation can be computed |

**The disputed boundary lives here.** `mismatch` means "we named a wrong cell type". `kb_lacks_class`
means "we were never able to name it". They are different failures with different fixes, so they are
never added together under one label. A table that reports a single "error rate" without splitting
these two is rejected by the checker.

Rates are cell-weighted unless a table says otherwise in its own `weighting` field. `we_finer` and
`we_coarser` are not errors and never enter an error rate; they are disclosed with their direction
because collapsing them into one number hides which way the granularity runs.

## Axis B - where the truth class stood in our candidate list

Axis B answers "why was this wrong", so it is defined on the whole corpus, not only on the wrong
cells, and its six states also sum to the cell total.

| state | meaning |
|---|---|
| `in_top1` | the truth class was our first choice |
| `same_count_lost` | the truth class was tied with the winner on shared-gene count and lost on ordering |
| `lower_count` | the truth class was admitted but carried fewer shared genes than the winner |
| `not_admitted` | a class in the truth lineage exists in the knowledge base but shares no gene with the query |
| `no_entry` | no class anywhere in the truth lineage exists in the knowledge base |
| `abstain` | no candidate was returned |

Axis B is a diagnostic. It is computed from a frozen candidate cache and must state which width and
which admission rule produced that cache, because the same cluster moves between states when the
panel width changes. Axis B numbers never replace Axis A numbers in a report.

## Why this file exists

On 2026-10-20 two tables in the same body of evidence disagreed by 14,000 cells on one tissue: one
counted `kb_lacks_class` inside `mismatch`, the other listed it separately. Both were internally
consistent; they were answering different questions with the same word. The fix is not a better
number but a fixed vocabulary plus a machine check.

## Rules the checker enforces

A summary table must declare `axis` as `A` or `B`, must carry exactly the state names of that axis,
must sum to its declared cell total, and must not carry a key named `mismatch` that has already had
`kb_lacks_class` folded into it. Optional states may be omitted, but the omission is recorded rather
than silently filled with zero.
