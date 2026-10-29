# Card: graded abstention output (near-miss column)

Opened 2026-10-22. Owner: default4. Approved by the PI in chat: asked whether
abstentions should be graded rather than reported as a blank, the PI approved in one
word ("ok").

## Why

The abstention analysis of 2026-10-22 (see
`/home/ubuntu/eyekb_indep_validation_20261022/ABSTENTION_ANALYSIS_20261022.md`)
found 205 genuine abstentions in the 25-volume corpus, 269,966 cells. Of those:

* 100 clusters — the library owns the class, this volume's expression never surfaced it
*  35 clusters — the library has no route to the class at all
*  44 clusters — reachable at 30 genes, not at 10
*  26 clusters — the class was in the ranking and the judge still declined

Right now an abstention is one bit of information: `celltype_ranking` is empty and the
caller learns nothing else unless they already know to turn on `EYEKB_ABSTAIN_REASON`.
The PI asked for abstentions to be "split up", i.e. a caller should be able to see
*what was nearly answerable* instead of a blank.

## What changes

One additive key, `abstain_reason.near_miss`, written only when:

1. `EYEKB_ABSTAIN_REASON` is enabled (the existing opt-in, unchanged), and
2. `celltype_ranking` came back empty.

Contents: up to 3 candidates that were demoted **only** by
`state_program_only` or `increment_guard` — the two demotion causes whose meaning is
"the class is right but did not meet the release bar". Each entry carries
`cell_type`, `n_shared`, `shared_genes`, `why`. Sorted by `n_shared` descending.
The key is not written when the list would be empty.

## What does not change

* `celltype_ranking` — still empty on abstention. No answer is invented.
* Scoring — the answer remains `unknown`. No metric moves.
* `tissue_out_of_scope` and `composite_superset` demotions are **never** surfaced in
  `near_miss`. Those two mean "this class is wrong here" (a PI red line: a tissue
  filter that leaks its own exclusions is not a filter). Only "right class, below the
  bar" is surfaced.
* Default bytes — the key is behind the existing opt-in switch, so an unconfigured
  caller sees byte-identical responses.

## Pre-registered acceptance criteria

Fixed before any measurement. Any FAIL means revert, no renegotiation.

| id | criterion | pass condition |
|---|---|---|
| P1 | default route, switch OFF, 764-cluster corpus | 764/764 responses byte-identical (md5), ranking sequences identical |
| P2 | switch ON, `near_miss` list empty | the six pre-existing `abstain_reason` fields byte-identical |
| P3 | switch ON, `near_miss` non-empty | the six pre-existing fields unchanged; only `near_miss` added |
| P4 | red line, per-class scan of every `near_miss` entry | zero entries originating from `tissue_out_of_scope` or `composite_superset` |
| P5 | G4 reproduction hash | unchanged |
| P6 | unit cases: empty score / state_program only / increment_guard | near_miss semantics as defined above, 3/3 |

## Scope discipline

One change, one place: `mcp_server/eyekb_core.py`, inside the existing
`[ABSTAINREASON]` block. No new threshold, no new switch, no whitelist edit, no
touched marker library.

## Reproduction

```
cd /home/ubuntu/EYEKB_REPO/docs/plans/abstain_grade_20261022/scripts
python3 near_miss_measure.py --capture     # on pre-change bytes
# ... apply the change ...
python3 near_miss_measure.py --verify
python3 near_miss_unit.py
```