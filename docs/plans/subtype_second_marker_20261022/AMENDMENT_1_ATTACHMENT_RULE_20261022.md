# AMENDMENT 1 to PREREG_SUBTYPE_SECOND_MARKER_20261022.md — the candidate-attachment rule

Date 2026-10-22, card `t_7509a1a2`. Written **after** the first mining pass (`m1_mine_lit.py`) and
**before** the second pass (`m1b_mine_lit_v2.py`). Pass 1's output is preserved byte-for-byte as
`out/SUPERSEDED_m1_mine_lit_p1.{json,tsv}` and is reported as superseded, exactly as the frozen wave
handles its own superseded logs.

## Why an amendment, and why this is not a moved goalpost

PREREG §4 defined a candidate as a **same-sentence co-mention** of a gene symbol and a name form.
Pass 1 shows that rule does not implement the object it claims to measure: it cannot tell *"this gene
is a marker OF the subtype"* from *"this gene is named somewhere in the same sentence"*. Three
verbatim pass-1 examples (all admitted, molecule and subtype in one sentence):

| admitted for | gene | the sentence that admitted it | what it actually is |
|---|---|---|---|
| OFF cone bipolar cell | `NR2E3` | "…including `NRL` and `NR2E3` in rods, `THRB` and `LHX4` in cones, … `FEZF2` and `LHX3` in OFF bipolar cells, and `ISL1` and `ST18` in ON bipolar cells" | a **rod** transcription factor, named 3 clauses away |
| starburst amacrine cell | `VIP` | "Several displaced ACs such as starburst, `CRH`+, `VIP`+, nGnG, and nNOS+ types have been identified…" | a **different** amacrine type in a comma list |
| rod bipolar cell | `HP` | "…**H**eparin-binding epidermal growth factor…" / "…reversed by **HP** in aged retinas" | not a gene symbol in that context at all |

The defect is **construct validity of the generation rule**, not the acceptance gate. The gate
(AUC ≥ 0.70, BH-FDR < 0.05, ≥ 2 markers, the sibling map, the per-class-cap detector) is **not
touched by this amendment** and is still applied by the frozen ruler unmodified. Both readings are
computed and reported; pass 1 is never deleted.

## The amended rule (one amendment; no further changes after it)

Replacing PREREG §4's sentence-level co-mention:

1. **Clause resolution.** A chunk's text is split on `[.!?]`; a span longer than 400 characters is
   split further on `;`. The resulting spans are the *clauses*. (Pass 1 additionally dropped every
   span longer than 2,000 characters — which silently discarded the single most informative sentences
   in the corpus, the cluster-by-cluster enumeration sentences. That guard is removed.)
2. **Attachment (proximity).** Inside one clause, a gene symbol is attached to subtype `S` only if the
   character distance between the symbol and the nearest occurrence of one of `S`'s §3 name forms is
   **≤ 80 characters**.
3. **Predicate.** The clause must also contain at least one marker/expression predicate
   (case-insensitive): `marker`, `express`, `enrich`, `specific`, `label`, `detect`, `identif`,
   `distinguish`, `immunoreactiv`, `transcript`, `antibod`, `stain`, `positive`.
4. **L1 relaxed to one attached statement.** `g` clears L1 for `S` iff there is **at least one**
   attached, predicate-bearing co-mention (≥ 1 paper). Rationale, stated up front: the frozen wave's
   "two independent sources" bar classifies whether a *subtype* is field consensus; a *marker
   attribution* is a factual statement one paper can make. The paper count stays in the record, is
   used for ranking, and a stricter reading (`papers ≥ 2`) is computed alongside so the report can
   carry both numbers. Its consequence — a flip whose two clearing markers come from one paper — is
   caught by the H2/H5 independence classification, which was pre-registered before any flip existed.
5. **Channel C restricted.** `kb/vk_literature_index/*.md` is a **bibliographic index** (titles +
   identifiers), not a statement source; it is removed from candidate **generation** and kept only as
   a name-resolution listing. `kb/textbook_layer/TEXTBOOK_ITEMS_v1.jsonl` (verbatim quotes) stays.
6. **Channel B unchanged** (clause-level co-mention inside an already-fetched source statement).

Rules L2 (assay vocabulary), L3 (not already in the frozen panel), L4 (a symbol attached to ≥ 3
in-scope subtypes is not a discriminator) and L5 (cap K = 2, ranked by paper count then channel-B
then symbol) are unchanged, as is everything in PREREG §5–§12 — including the measurability floor
(§6), the re-measurement contract (§7) and the honesty classification (§8).

## Declaration

This is the **only** amendment. Thresholds in the ruler are untouched; the acceptance criterion for a
flip is untouched; nothing in the in-scope set is touched. Pass 2's output is what the report's
headline uses; pass 1 is reported as superseded with its counts. No further tuning of the mining rule
follows this document, whatever pass 2 returns — a subtype for which pass 2 admits nothing is reported
`NOT_AVAILABLE`, which the BRIEF names as a legitimate result.