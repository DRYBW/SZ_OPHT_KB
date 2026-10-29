# Card: make the light tier the default

Opened 2026-10-29. Executed 2026-10-29.

## Why this card exists

The previous usability pass made the size switch discoverable but left the heavy tier as the
default. A caller who does not read the description still pays 140,005 characters for
`get_kb_page(scope="index")` and 91,332 characters for `get_tissue_composition("human","retina")`
on every call. The switch exists and nobody flips it.

Changing a default moves the shipped response bytes, so it needs its own card, its own
before/after readings and its own revert path. That is this card.

## What is in scope

`mcp_server/server.py` only — the two tool wrappers. `mcp_server/eyekb_core.py` is not touched,
so every core-level caller keeps its current behaviour and the core file hash stays put.

Two independent switches:

* `get_kb_page` default view: page text (140 KB) or page inventory (2.8 KB)
* `get_tissue_composition` default view: full (91 KB) or answer (about 20 KB)

## Pre-registered criteria

Fixed before any edit was made. Any criterion that fails is reported as a failure and the
matching default is not flipped.

| id | criterion | pass condition |
|----|-----------|----------------|
| C1 | explicit heavy tier is a real escape hatch | `detail="full"` on three calls (index page, tissue page, composition) has the same md5 before and after |
| C2 | the legacy argument still reaches the heavy tier | `get_kb_page(scope="index", summary=False)` after the change has the same md5 as the pre-change default |
| C3 | the new default is actually light | index default ≤ 3,000 chars; composition default ≤ 25,000 chars |
| C4 | one environment variable restores the old default everywhere | with `EYEKB_DEFAULT_DETAIL=full`, all four default calls have the same md5 as the pre-change defaults |
| C5 | a light tier may not drop citations | for every row returned in the light views, the count of citations inside that row equals the count in the heavy view; any shortfall must be named in `omitted_fields`, and if it cannot be named the composition default is not flipped |
| C6 | the gate chain does not regress | `verify_pipeline.py` shows the same single mismatch as before; `gate_change_control.py` returns 0; the negative battery keeps its pre-change cell |
| C7 | there is a way back | one of the two revert paths (single-commit revert, environment variable) is executed and shown to restore the pre-change bytes |
| C8 | nothing is silent | every light response carries the applied view and a pointer to how to get the full one |

C4 and C8 both encode the same rule: a smaller default may not hide that it is smaller.

## Out of scope

* the mid tier for a single tissue page (41,920 chars) — needs a design, not a default flip
* latency — must be re-measured on an idle machine, not here
* `search_literature`, `get_disease_prior`, `query_marker` defaults — unchanged by this card