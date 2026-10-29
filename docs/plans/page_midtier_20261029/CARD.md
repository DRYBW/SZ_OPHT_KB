# Card: a mid tier for a single page

Opened 2026-10-29. Executed 2026-10-29.

## Why this card exists

The default-tier card fixed the catalogue: `get_kb_page(scope="index")` returns an inventory. It
left one gap it named in its own out-of-scope section: **a single page has nothing between "one row"
and "the whole page"**. A tissue page is 41,930 characters; the largest page in the tree
(`models.md`) is 191,143 characters. The only way to read one today is to pull the whole thing into
the caller's context.

The earlier usability report proposed no design for this, because size alone is not the problem: a
paper list is genuinely a list, and the reader usually wants part of it.

## What the pages actually look like

Measured on all 29 pages of `kb/vk_literature_index/`:

* 26 of 29 are three-heading pages: `# Literature: <x>`, `## Paper List`, `## Reading Layer Links`.
  The bulk is one line per paper.
* The paper-line format is not uniform across pages. One regex for
  `- PMID… (YYYY) Title — *Journal* [species] tags=… v=…` matches **1,697 of 7,493** paper lines;
  `INDEX.md` and other pages use their own shapes. A structured row view built on that regex would
  silently drop three quarters of the corpus, so this card does **not** build one.
* Headings are unique within every page (0 duplicate heading names in all 29 files), so a section can
  be addressed by name without ambiguity today — but nothing guarantees that tomorrow.

## The design

Two views, both derived from the page text at call time, plus verbatim slicing:

| view | shape | answers |
|---|---|---|
| `outline` | front-matter keys, heading tree with per-section line/char/paper counts, year histogram, drill instructions | "what is in this page and is it worth reading?" |
| `slice` | consecutive verbatim lines, with `total_lines`, `offset`, `limit`, `next_offset`, `eof` | "give me this part of the list" |
| `full` | the page text, exactly as shipped | unchanged |

`slice` is the load-bearing piece: it carries **no parsed structure**, so the union of all slices is
the page, byte for byte. That is a property this card can measure instead of assert, and it is why
the structured-row design was rejected — not because it would be hard, but because on this corpus it
would be lossy.

## Pre-registered criteria

Fixed before any edit. Failure means the matching default does not flip.

| id | criterion | pass condition |
|----|-----------|----------------|
| C1 | the heavy tier is still an escape hatch | `detail="full"` on three pages (tissue cornea, topic vascular, index) has the same md5 before and after |
| C2 | the outline tells the truth | on ≥6 pages spanning 1.5 KB to 191 KB, per-section line counts, character counts and paper counts independently recomputed from the file equal the outline's numbers, and the outline's total equals the file's length |
| C3 | slicing loses nothing | for ≥6 pages, `"\n".join` of every slice taken at a page size that does **not** divide the line count reproduces the page text byte-for-byte (md5 equality) |
| C4 | the new views are small | outline ≤ 2,500 characters on the largest page; a default-size slice ≤ 25,000 characters on any page |
| C5 | no page is left unreachable | all 29 listed pages answer both an outline request and a one-line slice request, 29/29 |
| C6 | the default is a rule, not a mood | pages above 20,000 characters default to outline, pages at or below default to full; `EYEKB_DEFAULT_DETAIL=full` forces the full tier on every page |
| C7 | the gate chain does not regress | `verify_pipeline.py` keeps its pre-existing mismatch count; `gate_change_control.py` returns 0; the negative battery keeps its pre-change cell byte-for-byte |
| C8 | nothing is silent | an implicit outline carries the applied tier, the page size and the one call that returns the text |

## Out of scope

* No structured row view (rejected on measurement, see above).
* No section addressed by heading name: headings are unique today and nothing enforces that, so the
  slice offset is the addressable unit.
* No change to `get_topic`/`get_tissue` routing, to ranking, or to any pipeline output.
* Latency is not reported: it has to be measured on an idle machine.