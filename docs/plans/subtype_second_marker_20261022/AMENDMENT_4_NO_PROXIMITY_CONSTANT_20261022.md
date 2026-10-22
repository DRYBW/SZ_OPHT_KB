# AMENDMENT 4 (FINAL for the attachment rule) — dropping the arbitrary proximity constant

Date 2026-10-22, card `t_7509a1a2`. Written **after** pass 4 (`m1d_mine_lit_v4.py`, AD1+AD2+AD3) and
**before** pass 5 (`m1e_mine_lit_v5.py`). Pass 4's artefacts are preserved as `out/SUPERSEDED_pass4/**`.

AMENDMENT 3 declared itself the last amendment. The pass-4 log forced one more structural change, and
that is stated plainly rather than quietly: shipping the pass-4 panel would mean shipping a panel
whose incompleteness is already known, with the counter-evidence in hand. The change below is
**structural**, not a fitted constant, and it makes the rule *shorter*.

## The defect, with the verbatim evidence

The 80-character proximity window is arbitrary, and this literature writes marker assignments in a
style it systematically rejects: the gene's full name is spelled out, then the symbol in parentheses,
which pushes the symbol past 80 characters from the subtype name. Measured, from the same sentence
that passes 2–4 already rely on:

| gene | segment (PMID 37794584) | distance | pass 4 |
|---|---|---|---|
| `LMO4` | "DB4 bipolar cells were identified based on expression of LIM domain only protein 4 ( LMO4" | **87** > 80 | rejected although the sentence assigns it to DB4 |
| `DNER` | "and DB6 bipolar cells were characterized using Delta and Notch-like epidermal growth factor-related receptor ( DNER" | **~104** > 80 | rejected although the sentence assigns it to DB6 |

Consequence: pass 4 admits **no** candidate for `diffuse bipolar 6 (DB6)` at all and loses the
literature's own DB4 marker, while the sentence says so explicitly. A window that rejects the
literature's most explicit assignment style is the wrong instrument.

## The amended rule (FINAL for the attachment rule)

Remove the proximity constant. Attachment becomes purely structural, using the segment unit AD2
introduced:

> A gene symbol inside a segment attaches to the in-scope subtype `S` when (i) the segment contains a
> marker/expression predicate (AD1 rule 3 + AD3), and (ii) the segment names **exactly one** in-scope
> subtype, namely `S`. A segment that names two or more in-scope subtypes attaches nothing — the
> ambiguity is left unresolved rather than guessed.

Worked examples on the sentence above: `GSG1`→DB2, `CALB1`→DB3a, `LMO4`→DB4, `DNER`→DB6 (each
segment names exactly one in-scope subtype), while `TTR`'s segment ("…foveal than peripheral bipolar
type DB3b and DB4") names two and therefore attaches to neither — the passing mention that pass 2
wrongly turned into a DB4 marker is now dropped by construction.

Everything else is unchanged: L1–L5 (including K = 2 and the L4 pan-family rejection), the
measurability floor, the acceptance gate, the re-measurement contract and the H1–H5 honesty
classification.

## Finality and the robustness reading

**No further change to the attachment rule follows this document, whatever pass 5 returns.** All five
passes stay on disk. Because the amendments moved candidates in both directions, the report's headline
is the **robust** set: a `(volume, subtype)` row counts as robust when it flips under **both** the AD1
rule (pass 2) and the pass-5 rule — two independently-derived attachment rules. Rows that flip under
only one rule are reported as *rule-dependent*, with the rule named.