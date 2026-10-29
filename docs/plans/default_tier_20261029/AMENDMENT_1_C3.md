# Amendment 1 — criterion C3, recorded before any code edit

Recorded 2026-10-29, before `mcp_server/server.py` was touched. Evidence that this ordering
holds: the baseline readings it refers to live in `out/BEFORE.json`, and the file this amendment
constrains still has the hash it had when that baseline was taken —
`server.py` sha256 `eb18dcaf6d3833f9f55f87e111c69e09616f101fd41c0f87d907d828e46c11db`,
`eyekb_core.py` sha256 `f6e199257e068be5c3c65ad1ed959cf6592196aee6e8c754fb8c2d8ece48f3ce`,
repo HEAD `c188085`.

## What was wrong with C3 as written

C3 said: index default ≤ 3,000 characters. That number came from the previous usability pass,
which measured the compact index view at 2,841 characters on 2026-10-22.

The fresh baseline taken today measures that same view at **4,013 characters**. The catalogue has
grown since 2026-10-22 — pages were added, so the compact view grew with them. The literal
threshold would therefore fail for a reason that has nothing to do with this card: the number was
a stale snapshot of a growing object, used as if it were a fixed property of the code.

## Replacement criteria

| id | criterion | pass condition |
|----|-----------|----------------|
| C3a | the index default is substantially lighter | compact index view ≤ 1/20 of the full index (measured, both in the same run) |
| C3b | the composition default is substantially lighter | answer view ≤ 1/3 of the full composition (measured, both in the same run) |
| C3c | the absolute size is reported, not hidden | the report states both absolute character counts and both ratios; no ratio is reported without its absolute pair |

C3a and C3b keep the intent — the new default must be a real size reduction, not a cosmetic one —
while stopping the criterion from depending on a catalogue size that changes for its own reasons.
C3c exists so a future reader cannot see "20×" without seeing "140,005 → 4,013".

## What is not amended

C1, C2, C4, C5, C6, C7, C8 stand exactly as pre-registered. In particular C5 — a light tier may
not drop per-row citations — remains a hard stop on flipping the composition default.