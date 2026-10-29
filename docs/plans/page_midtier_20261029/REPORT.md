# A middle tier for a single page

Executed 2026-10-29. Card: `CARD.md` (criteria fixed before any edit), `AMENDMENT_2_C4_C6.md`
(written **after** the first measurement — a specification correction and one recorded miss, plainly
labelled as such).

**Read this first: the strict verdict is 5/7, not 7/7.** Two pre-registered criteria missed. Both are
explained below with the numbers that caused them, and neither was tuned away.

**Owner ruling (2026-10-29, after reading this report): take the maximum benefit, then close.**
The two misses were mis-specified criteria, not working defects: C4's absolute 2,500-character bound
is not adopted (the outline keeps all of its information at 2,663 characters), and C6's catalogue
carve-out is the behaviour `VERIFY_CONTRACT` §5.8 already registered. The 5/7 verdict above stays on
the record unchanged. See `AMENDMENT_3_RULING_AND_CLOSURE.md`.

## 1. The gap this closes

The previous card fixed the catalogue and then named its own leftover: a single page has nothing
between one row and the whole document. Measured on this tree: `tissue-cornea` is 41,562 characters
of text, `topic-models` is 191,143, `INCLUSIONS_RECENT` is 200,447. Reading any of them meant pulling
all of it into the caller's context.

## 2. What a caller can ask for now

| request | returns | on `tissue:cornea` |
|---|---|---|
| *(nothing — default)* | outline, if the page is over 20,000 characters | **1,482** chars |
| `detail="outline"` | front matter, heading tree with per-section lines/chars/paper counts, year histogram | 1,482 |
| `detail="slice"` + `offset`/`limit` | consecutive verbatim lines, with `next_offset`/`eof` | 100 lines ≈ 17,857 response chars |
| `detail="full"` | the page text, exactly as shipped | 41,930 |

The outline states its own counting rule (`chars_taken_as`) so a reader can recompute every number
instead of trusting it.

## 3. Why there is no structured one-row-per-paper view

Because I measured it before building it. One regex for the standard paper line
(`- PMID… (YYYY) Title — *Journal* [species] tags=… v=…`) round-trips **1,697 of 7,493** paper lines
across the tree. `INDEX.md` and several others use different shapes. A structured view would have
silently dropped three quarters of the corpus, so the mid tier is built on **verbatim slicing**
instead — which cannot drop anything, and whose losslessness is measurable rather than asserted.

## 4. Losslessness, measured on every page

29 of 29 pages were walked in slices and rebuilt:

| reading | result |
|---|---|
| pages walked | 29/29 (enumerated from the service's own inventory, not a hand-written list) |
| slice step | 37 lines, or 997 on the two pages over 60,000 characters so the walk stays cheap |
| rebuild | **29/29 byte-identical** (`"\n".join(all slices)` md5 == page text md5) |
| outline numbers | re-derived by an independent second implementation inside the probe, on all 29 pages: **0 field mismatches** |
| reachability | 29/29 answer a default request, an outline request and a slice request |

## 5. Size, honestly

| page | text chars | outline chars | saving |
|---|---|---|---|
| `topic:models` | 191,143 | 1,467 | 130× |
| `INCLUSIONS_RECENT` | 200,447 | 2,663 | 75× |
| `tissue:cornea` | 41,562 | 1,482 | 28× |
| `topic:dr-diabetic-retinopathy` | 21,258 | 1,519 | **14×** ← the worst case |
| `index:INDEX` | 138,993 | 4,267 | 33× (not the default; the catalogue keeps its inventory) |

The worst saving is 14×, on the biggest page that is still small enough to be near the threshold. Four
short pages (1,518–15,273 characters) keep their full text by the same rule.

## 6. The two misses

**C4 — the absolute bound.** C4 said the outline would be ≤ 2,500 characters on the largest page. I
assumed the largest page was `models`; it is `INCLUSIONS_RECENT` (200,447), and its outline is
**2,663** — 163 over. I did not shrink the outline afterwards: the only ways under the bound were to
drop per-section sizes, drop the year histogram, or truncate heading lists, and all three trade
information for a number I guessed before measuring. The ratio reading is in the table above.

**C6 — the wording.** C6 said every page over 20,000 characters defaults to an outline, and that
`EYEKB_DEFAULT_DETAIL=full` restores the pre-change default on every page. One page does not obey it:
the catalogue, which defaults to the **inventory** view set by the previous card. So C6 reads 28/29.
Under the corrected wording — "every page except the catalogue" — both halves hold **28/28**. The code
was not changed to fit the correction; `AMENDMENT_2_C4_C6.md` records the ordering and the sha.

## 7. Gate chain and attribution

`out/GATE_VERDICTS.json` holds the commands, exit codes and verdict lines as returned.

| gate | rc | reading |
|---|---|---|
| card criteria | 1 | **5/7** (the two misses above; three restated readings printed after the verdict) |
| G6 change control | 0 | 21 checks, 0 fail, 16 recorded changes |
| G5 switch coverage | 0 | R1 registry in sync, 29 rows — this card adds **no** new switch |
| G5/G6 negative battery | 1 | byte-identical output to the previous run; same single pre-existing BAD cell |
| G4 `verify_pipeline.py` | 1 | pre-existing 1/3 mismatch, same two hashes |

Legacy tool-panel identity: red before this card on four calls (catalogue, mouse composition, two
`search_literature`), red after it on five. **Exactly one call is this card's**: 
`get_kb_page:{"scope":"topic","name":"vascular"}` — a 39,018-character page that now defaults to its
outline. `legacy_panel` `95952b46…` → `c58d2411…`; `full_panel` `794b871f…` → `6899652e…`. The fixture
is again **not** re-recorded, so the accumulated drift stays visible.

## 8. Rollback

`EYEKB_DEFAULT_DETAIL=full` — the variable the previous card registered — puts every non-catalogue
page back on its full text: 28/28 pages return their pre-change default bytes, measured against
`out/BEFORE.json`. The two new views keep working in that state, because they are requested, not
defaulted.

## 9. What this does not do, and the one product consequence

* A caller that reads a long page and asks for nothing now gets its **structure**, not the paper
  list. That is the deliberate change; one argument returns the list, and one variable reverts the
  default. If that trade is wrong for the way the tool is used, `EYEKB_DEFAULT_DETAIL=full` undoes it
  without a code change.
* No latency claim: it must be measured on an idle machine.
* No claim about annotation accuracy; nothing here touches a score.
* No section addressing by heading name: headings are unique in all 29 pages today, and nothing
  enforces that, so the addressable unit is the line offset.

## Reproduction

```
cd /home/ubuntu/EYEKB_REPO
python docs/plans/page_midtier_20261029/verify_page_tiers.py          # expect 5/7 and rc=1
python docs/plans/page_midtier_20261029/scripts/gate_verdicts.py      # rewrites GATE_VERDICTS.json
EYEKB_REPO_ROOT=/home/ubuntu/EYEKB_REPO UX_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python \
  python docs/plans/page_midtier_20261029/probe_page_tiers.py --label after \
  --out docs/plans/page_midtier_20261029/out/AFTER.json
```

The pre-change readings in `out/BEFORE.json` were taken by stashing `mcp_server/server.py` to the
parent commit and running the same probe, so both sides come from the same instrument.

`out/BEFORE.json` stores no page bodies. Before this card a request for an outline fell through to
the full page text, and keeping a 200,000-character page body under an `outline` key would have made
the reading file misdescribe what it held — and made it 1.7 MB for no evidential gain. The fields it
is actually read for (characters, md5, default-view characters) are unchanged by that trimming: the
the verifier prints the same 5/7 and the same numbers before and after it.

## Closure

Closed 2026-10-29 by owner ruling ("take the maximum benefit, then close it out"), recorded in
`AMENDMENT_3_RULING_AND_CLOSURE.md`. What that changed: nothing in the code, nothing in the readings,
nothing in any gate — the 5/7 verdict and the two named misses stay exactly as measured. What it
settled: the absolute character bound in C4 is not an acceptance criterion (the outline keeps its
information), and the catalogue keeps the default §5.8 registered for it.

Left open, named rather than buried:

* The delivered mirror `/mnt/D/EyeKB` was **not** synced. Its `mcp_server/server.py` is
  `394d4d91…`, which matches no revision in this repository, so a straight copy would overwrite
  mirror-only changes. It needs a three-way diff, which is its own card.
* Latency is still unmeasured; it requires an idle machine.
* The legacy tool-panel fixture is still not re-recorded, so its accumulated drift stays visible: five
  calls differ, only one of them this card's.