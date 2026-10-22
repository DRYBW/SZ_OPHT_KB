# AMENDMENT 3 (FINAL) to PREREG_SUBTYPE_SECOND_MARKER_20261022.md — the predicate list

Date 2026-10-22, card `t_7509a1a2`. Written **after** pass 3 (`m1c_mine_lit_v3.py`, AD2) and **before**
pass 4 (`m1d_mine_lit_v4.py`). Pass 3's artefacts are preserved as `out/SUPERSEDED_pass3/**`.

## The defect, with the verbatim evidence

AD1 rule 3 fixed the predicate list as
`marker|express|enrich|specific|label|detect|identif|distinguish|immunoreactiv|transcript|antibod|stain|positive`.
Pass 3 shows the list omits the single most common *identification* verb in this literature:
**`characteriz*`**. The consequence is measured, not argued: pass 3 admits **zero** candidates for
`diffuse bipolar 6 (DB6)` and loses `CALB1` for DB3a, because the sentence that assigns them uses
"were characterized based on …". Verbatim (PMID 37794584, resolved by `m4b_verify_claims.py`):

> … DB3a bipolar cells were **characterized** based on calbindin 1 (CALB1, cluster 22), DB4 bipolar
> cells were **identified** based on expression of LIM domain only protein 4 (LMO4, cluster 13), and
> DB6 bipolar cells were **characterized** using Delta and Notch-like epidermal growth factor-related
> receptor (DNER, cluster 12).

`identified` and `specific` are in the list, so DB2 (`distinguished`) and DB4 (`identified`) survive;
DB3a and DB6 do not — a gap that is an artefact of the word list, not of the literature.

## The amended rule (FINAL)

The predicate list becomes

`marker | express | enrich | specific | label | detect | identif | distinguish | characteriz |`
`discriminat | defined | immunoreactiv | transcript | antibod | stain | positive`

Nothing else changes: AD2's segment-level unique-nearest attachment stays, as do L1–L5 (including the
K = 2 cap and the L4 pan-family rejection), the measurability floor, the acceptance gate, the
re-measurement contract and the H1–H5 honesty classification.

## Direction of effect, stated in advance, and the robustness statement

AD1 and AD2 **remove** mis-attachments; AD3 **restores** a class of statements that the word list had
silently dropped for a purely lexical reason. Because the three amendments move candidates in
opposite directions, the report carries a **robustness reading**: a flip is called *robust* when the
same `(volume, subtype)` row flips under **both** AD1 (pass 2) and the final rule (pass 4), i.e. under
two differently-derived attachment rules. Rows that flip under only one of them are reported as
*rule-dependent*.

## Finality

This is the last amendment. Whatever pass 4 returns is the headline: no further tuning of the mining
rule follows this document. Subtypes for which pass 4 admits nothing measurable are reported
`NOT_AVAILABLE` / `not_measurable`, which the BRIEF names as a legitimate result.