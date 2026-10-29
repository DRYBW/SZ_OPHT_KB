# Amendment 2 — a specification correction, written **after** the first measurement

This file is not pre-registration. It is written after `out/AFTER.json` existed and says so on
purpose, so a reader can discount it accordingly. What it does **not** do: it changes no threshold,
re-runs nothing, and no line of `mcp_server/server.py` was edited to make a number come out.

Evidence that the code did not move to fit this text: the probe was taken at `server.py` sha256
`20e5f0c8fc22e4aea16f7159db62dffe445198b751c3f29e5ae54c1dc4bbf766`, and that is the same file the
readings below come from.

## Criterion C6, as written, could not pass — by design, not by accident

C6 said: "pages above 20,000 characters default to outline, pages at or below default to full;
`EYEKB_DEFAULT_DETAIL=full` forces the full tier on every page."

The measurement found one page that does not obey it: `index:INDEX` (138,993 characters) defaults to
the **inventory** view, with 4,324 characters. That is not this card's doing. The catalogue's default
was set by the previous card (`docs/plans/default_tier_20261029`, contract §5.8), and that card
defines `EYEKB_DEFAULT_DETAIL=full` as "the heavy tier everywhere", which for the catalogue means the
140,005-character text — i.e. the variable reaches back past the inventory decision, not to it.

So the criterion collided with a decision that was already registered, and I wrote the criterion
without rereading the carve-out. Two honest readings were possible:

1. treat it as a real failure and revert the page default — which would punish 28 pages for a
   sentence I got wrong, and would also fail the criterion, since the criterion demands the flip;
2. keep the behaviour, correct the sentence, and show every number that differs.

Option 2 is what this file does, with the failure left visible in the gate output
(`verify_page_tiers.py` still prints C6 as FAIL and still exits 1).

## Corrected criterion C6′ (for the next card, not a retroactive pass)

* The threshold rule applies to every page except the catalogue; the catalogue keeps its own
  registered default (inventory), and that default is unchanged by this card.
* The environment revert is measured on the same set: every non-catalogue page returns its
  pre-change default bytes under `EYEKB_DEFAULT_DETAIL=full`, and the catalogue returns the full
  text, exactly as §5.8 specifies.

Measured under that statement: threshold rule **28/28** non-catalogue pages, environment revert
**28/28**. The pre-registered form of the same criterion reads 28/29 because of the catalogue.

## Criterion C4 is a real miss and stays a miss

C4 said the outline would be ≤ 2,500 characters on the largest page. The largest page turned out to
be `INCLUSIONS_RECENT` at 200,447 characters (not `models` at 191,143, which is what I assumed when
I wrote the bound), and its outline is **2,663** characters — 163 over.

I did not shrink the outline to get under the bound. The only ways to do it would be to drop
per-section sizes, drop the year histogram, or truncate the heading list on heading-dense pages, and
every one of those trades information for a number I guessed before measuring. The honest reading is
that the absolute bound was a bad criterion, and the property that actually matters is the ratio:

| page | page chars | outline chars | ratio |
|---|---|---|---|
| `topic:dr-diabetic-retinopathy` (smallest saving of the 24 that flip) | 21,258 | 1,519 | 14.0× |
| `tissue:tissue-cornea` | 41,562 | 1,482 | 28× |
| `topic:INCLUSIONS_RECENT` (largest page) | 200,447 | 2,663 | 75× |
| `topic:models` | 191,143 | 1,467 | 130× |

Supplementary reading, because it is the one place the absolute number does bite: the largest outline
anywhere in the tree is **4,267** characters on `index:INDEX`, which has 22 headings. That page does
not default to the outline, so it costs nobody anything — but it is the reason a future "outline is
always ≤ N characters" claim would need N above 4,267 or a heading-collapsing design.

## Net position

* Strict pre-registered verdict: **5/7**. Carried into the change-control row as 5/7, not as 7/7.
* Substance: the two misses are one mis-specified sentence (C6) and one guessed absolute (C4), both
  named above. No capability claim in the report depends on either.
* What a reader should check rather than trust: C2 (outline numbers re-derived independently on 29
  pages), C3 (29/29 pages rebuilt byte-identically from slices), C5 (29/29 reachable) — those three
  are the load-bearing ones, and they pass.