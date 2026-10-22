# APPEND RECORD — addendum A on the frozen final report (card t_74ef13aa)

This wave was required to add a subdivision-readiness report to the end of the frozen EyeKB final report
**without changing any pre-existing byte**. This file records that operation in English so the repository
mirror is auditable on its own; the addendum itself is written in the language of the report it was appended
to (Chinese), and stays with that report, outside this repository.

## Target (frozen, not modified)

```
/mnt/D/EyeKB/plans/retina_deep_20261020/REPORT_EyeKB_成果报告_v2.0.md   (v2.0 final, 2026-10-20)
/mnt/D/EyeKB/plans/retina_deep_20261020/REPORT_EyeKB_一页纸_v2.0.md    (one-pager companion)
```

## Result

| property | main report | one-pager |
|---|---|---|
| bytes before | 16,745 | 2,431 |
| sha256 before (== sha256 of the kept pre-image copy) | `63a9f7bd4751df4122a45e89cb0737bbf9dd84a295caeecfdd4b1691703f9a8b` | `4812ca4f4ae573456240611f7e2a6a6bd5ba0010e38eb7f441616cacd77fd6a1` |
| bytes added | 24,401 | 1,106 |
| sha256 after | `efb253f478784e4395eb7d21be83eea960270dad6ef1ca79ba948ba7e26aed4b` | `a80a22f411897e31874350a9a72a5e9ec13c3e6d527b980d8412d350a5b78c5f` |
| prefix `0..N_before` re-hashed after the append | identical to the pre-image | identical to the pre-image |
| line diff | **added 281, removed 0, modified 0** | **added 13, removed 0** |
| pre-image copy kept | `REPORT_EyeKB_成果报告_v2.0.md.pre_addendum` | `REPORT_EyeKB_一页纸_v2.0.md.pre_addendum` |

Machine-readable proofs: `out/append_proof.json`, `out/append_proof_onepager.json`.

## How the addendum is headed

It opens as an appended section with its own version (`v2.0-A1`) and date (2026-10-22), states in the same table
that everything above it is unchanged, names the pre-append sha256 and the pre-image copy, and its **first
paragraph** states that it is a resolution audit and a knowledge asset — **not** a claim of improved accuracy.
Every consistency figure in it is labelled a regression/probing reading on the fixed 28-volume / 721-cluster set,
with the author labels described as a **fixed reference**, never as an automatic gold standard.

## Reproducing the append

```bash
cd /mnt/D/EyeKB/plans/subdivision_readiness_20261022
# the script is idempotent: it refuses to append twice (it looks for the addendum marker)
python3 scripts/m_append.py
# it re-prints the proof: sha before, prefix re-hash, added/removed line counts
```

To re-run from a clean state, restore both files from their `.pre_addendum` copies first — that is exactly what
was done when the operation was corrected for the `blast`-inside-`fibroblast` defect (see
`PREREG_ANNEX_A_AMENDMENTS3_20261022.md`): the frozen files were restored from the pre-images and the addendum was
regenerated, so the "added lines only" claim holds for the final bytes rather than for the superseded ones.