# Card: make the 30-gene query budget the default

Written before any measurement. Criteria below are fixed; results go to `REPORT.md`.

## 0. Decision being executed

`pipeline/l2_budget.py` currently resolves the per-cluster query budget to 10 whenever
`EYEKB_L2_BUDGET` is unset, and to 30 only when the variable is switched on. The registry
row for that module records the reason it was left off: *"default OFF; flipping the
default is a PI-reserved gate, this card does not flip it."*

That gate has now been opened by the project owner, who approved the change after reading
the measurement in `docs/plans/wide30_panel_20261029/REPORT.md` (+8.15 pp top-1 accuracy,
+7.34 pp coverage when the evidence panel grows from 10 to 30 genes). Approval on
2026-10-29, in reply to the note that the default would be switched under a card with a
before/after differential.

## 1. What changes

One file, one function: `pipeline/l2_budget.py`.

| state of `EYEKB_L2_BUDGET` | budget before this card | budget after |
|---|---|---|
| unset | 10 | **30** |
| `1` / `true` / `on` / `yes` | 30 | 30 |
| `0` / `false` / `off` / `no` / empty | 10 | 10 |
| anything else | 10 + one warning | **30** + one warning |

Nothing else moves: no algorithm, no vocabulary, no slot rule, no scoring, no denominator,
no KB version, no adjudication default. An explicit `--top-genes-n` is still never
rewritten, in any state.

Rationale for the unknown-token row: the warning exists so a typo never silently changes
behaviour *relative to the documented default*. With 30 as the documented default, an
unrecognised token now lands on 30 rather than on the legacy value, and still says so.

## 2. Fixed criteria

Measured after the edit, all on this machine, one process at a time.

| id | criterion | fail action |
|---|---|---|
| **C1** | `resolve(None)` is 30 with the variable unset; 30 for each of `1/true/on/yes`; 10 for each of `0/false/off/no`/empty | stop, do not commit |
| **C2** | an explicit value is never rewritten: `resolve(12) == 12` with the variable unset and with it set to `0` | stop |
| **C3** | an unknown token warns exactly once per process and lands on 30 | stop |
| **C4** | rollback works: with `EYEKB_L2_BUDGET=0`, the per-cluster candidate payload of a real pipeline run is identical to the pre-change run (canonical JSON sha256, cluster by cluster) | stop, the change is not revertible |
| **C5** | the new default is real, not just parsed: an end-to-end Stage B run with the variable unset produces 30 query genes per cluster where the volume has them, and its candidate field then differs from the `=0` run | stop |
| **C6** | change surface: exactly one production file differs in `git diff`, plus the registry row and the change-control row | stop |
| **C7** | the +8.15 pp figure stays labelled an observation on volumes already used in this line; no efficacy claim is made here, and no wording in any artefact says the annotation got more accurate | rewrite the artefact |

## 3. Rollback

`EYEKB_L2_BUDGET=0` (or `false` / `off` / `no`) returns the budget to 10 with no code
change. C4 proves that path on real output rather than asserting it.

## 4. Known consequence, not fixed by this card

The Stage B evidence report is an input to the G4 pipeline anchor, which compares a
fixture run against a stored hash. Changing the production default changes that hash by
design. This card records the new hash and leaves the re-anchor to a separate card, since
moving an acceptance baseline is its own change.

## 5. Boundary

No resource cost: the change is a default value; it does not add calls, models, downloads
or GPU work. No new efficacy claim, and the 25-volume corpus remains an observation set,
never an acceptance set for a capability claim.