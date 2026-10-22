# AMENDMENT 2 to PREREG_SUBTYPE_SECOND_MARKER_20261022.md — the attachment UNIT

Date 2026-10-22, card `t_7509a1a2`. Written **after** pass 2 (`m1b_mine_lit_v2.py`, AD1) and **before**
pass 3 (`m1c_mine_lit_v3.py`). Pass 2's artefacts are preserved as `out/SUPERSEDED_pass2/**`.

## The defect, with the verbatim evidence

AD1 attached a gene to a subtype when the two occur in the same clause (split on `.`/`!`/`?`, then on
`;`) within 80 characters. That unit is still one delimiter too coarse: the corpus's most useful
sentences are **comma-separated enumerations** that walk a list of subtypes, and a gene whose *full
name* is spelled out before its symbol lands physically nearer the **next** subtype.

The clause that proves it (PMID 37794584, resolved in full by `m4b_verify_claims.py` — pass 2's own
flip-driving evidence):

> "Clusters associated with bipolar cells were further characterized into rod bipolar cells using
> carbonic anhydrase 8 (CA8, cluster 9) as a specific marker, **DB2** bipolar cells were distinguished
> using germ cell-specific gene 1 protein (**GSG1**, cluster 15), **DB3a** bipolar cells were
> characterized based on calbindin 1 (**CALB1**, cluster 22), **DB4** bipolar cells were identified
> based on expression of LIM domain only protein 4 (**LMO4**, cluster 13), and **DB6** bipolar cells
> were characterized using Delta and Notch-like epidermal growth factor-related receptor (**DNER**,
> cluster 12)."

The sentence assigns `GSG1`→DB2, `CALB1`→DB3a, **`LMO4`→DB4**, **`DNER`→DB6**. Pass 2 attached
`LMO4` to **DB6** (24 characters to the right of `LMO4`, 75 to the left to `DB4`) and — because of the
same over-coarse unit — attached `TTR` to DB4 on a clause that is a *fovea-versus-periphery* contrast
("`TTR` expressed at higher levels by foveal than peripheral bipolar type DB3b and DB4"), i.e. a
passing mention rather than a marker statement. One of those two mis-attachments (LMO4→DB6) actually
moved a row.

## The amended rule (FINAL — no further amendments)

2a. **Segment resolution.** A chunk's text is split on `[.!?]`, then on `;`, and a resulting segment
    longer than 160 characters is split further on `,`. The resulting spans are the *segments*.
2b. **Unique nearest assignment.** Inside one segment, a gene symbol is attached to subtype `S` only
    when `S`'s nearest declared §3 name form is (i) present in that segment, (ii) within 80 characters
    of the symbol, and (iii) **the nearest such name form among all 16 in-scope subtypes**. A symbol
    that is equally near two in-scope subtypes is attached to neither.

Everything else is AD1: predicate required (PRED), L1 (≥ 1 attached statement), L2 (assay vocabulary),
L3 (not already in the frozen panel), L4 (≥ 3 in-scope subtypes ⇒ not a discriminator), L5 (cap K = 2,
ranked by paper count, then channel-B, then symbol). The acceptance gate, the measurability floor, the
re-measurement contract and the H1–H5 honesty classification are untouched.

## Direction of effect, stated in advance

Both AD1 and AD2 **remove** mis-attachments; neither adds a candidate nor relaxes a threshold. If pass
3 keeps fewer candidates than pass 2, that is the amendment doing its job, and pass 3 is the headline.
All three passes are reported.