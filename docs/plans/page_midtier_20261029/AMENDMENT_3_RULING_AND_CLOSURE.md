# Amendment 3 — owner ruling on C4/C6, and closure of the card

Written 2026-10-29, after the owner read the card report and the two missed criteria.

## The ruling

The owner's instruction, translated from Chinese and recorded in substance: **take the maximum
benefit; then close it out.**

Concretely, that settles the two open readings in `AMENDMENT_2_C4_C6.md`:

| crit | pre-registered form | outcome under the ruling |
|---|---|---|
| C4 | outline ≤ 2,500 characters on the largest page | **The absolute bound is not adopted as an acceptance criterion.** The outline stays at **2,663** characters on `topic:INCLUSIONS_RECENT` (200,447-char page). No information was removed to reach a number guessed before measurement. The operative reading is the ratio, measured 14.0× (worst) to 130× (best) over the 24 pages that flip. |
| C6 | threshold rule on every page + environment revert | **The catalogue keeps its registered default** (inventory, 4,324 chars) per `VERIFY_CONTRACT` §5.8, which the previous card registered. The threshold rule holds **28/28** non-catalogue pages; `EYEKB_DEFAULT_DETAIL=full` restores **28/28**. |

This is an owner decision about what the card should have asked for, **not** a re-run and **not** a
threshold edited after the fact. Nothing in `verify_page_tiers.py` was changed to make a cell flip:
it still prints **5/7** and still exits 1, and the change-control row still carries **5/7**. The record
of the two misses stands as written.

## What changed on disk for this amendment

* This file.
* `REPORT.md` — a ruling line at the top and a closure section at the end. The body, the tables and
  every reading above it are untouched.
* `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` — the `CHG-20261029-PAGE-MIDTIER` row keeps its `5/7`
  verdict; an owner-ruling sentence with an anchor is appended to its boundary cell so a reader of the
  ledger alone cannot mistake the two misses for open defects.
* **No change to** `mcp_server/server.py`, `mcp_server/eyekb_core.py`, any probe, any reading file or
  any gate. Version identity at closure is the same as at commit `8131825`.
  `server.py` sha256 `20e5f0c8fc22e4aea16f7159db62dffe445198b751c3f29e5ae54c1dc4bbf766`.

## Why the ruling does not weaken the record

The two misses were about *how the card wrote its criteria*, not about whether the tier works. The
three load-bearing properties are the ones a reader should check independently, and all three pass:

* C2 — outline numbers re-derived by a second implementation on 29 pages, 0 field mismatches.
* C3 — 29/29 pages rebuilt byte-identically from slices.
* C5 — 29/29 pages reachable in all three views.

A future card that wants a hard character bound on outlines should derive it from the tree
(`index:INDEX` has the largest outline anywhere at 4,267 characters, on a page that does not default
to the outline), not pick a round number first.

## Closure state

| item | state |
|---|---|
| Default behaviour on long pages | outline at or above 20,000 characters; full text on request |
| Revert | `EYEKB_DEFAULT_DETAIL=full` — 28/28 non-catalogue pages return pre-change bytes; no code edit |
| New switches | none (`EYEKB_DEFAULT_DETAIL` was registered by the previous card; registry 29 rows, R1 in sync) |
| Acceptance baselines moved | none — G4 anchor and legacy tool-panel fixture untouched |
| Delivered mirror `/mnt/D/EyeKB` | **not synced by this card, on purpose** — see below |

### The delivered mirror is deliberately left alone

`/mnt/D/EyeKB/mcp_server/server.py` is sha256 `394d4d91aad7ffc10151df8813da719fc1df525d645f1988ff2f88b66eb9ea9a`,
which equals **no** revision of the file in this repository (this card's parent `961a286` has
`1253be5e…`, this card `20e5f0c8…`). Copying the repo file over it would overwrite changes that exist
only in the mirror. Sync therefore requires a three-way diff first, and that is a separate card. This
is recorded here rather than silently skipped.