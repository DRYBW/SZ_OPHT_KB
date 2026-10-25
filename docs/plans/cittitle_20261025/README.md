# cittitle_20261025 — CITTITLE: citation records carry no title; backfill title/doi/pmcid from the corpus

Card: `t_d8e7f2d4` (board `pi-briefing`, executed by `pi-chief`).
Brief: `/mnt/D/EyeKB/plans/consistency_20261024/BRIEF_CITTITLE_20261025.md` (copy: `out/`).
Construction site mirror: `/mnt/D/EyeKB/plans/consistency_20261024/cittitle_out/` (same tree, second copy).
The delivery documents (`README.md`, `REPORT.md`, `out/CITATION_META_SPEC_v1.md`) are English as the
repository requires. `out/CITATION_TITLE_COUNTERFACTUAL_v1.md` and the `reason_text` column of the
`UNMATCHED_*.tsv` files are Chinese on purpose: they reproduce the coordinator's own campaign brief
table format and its per-row reason strings (the LINKKEY card's `UNMATCHED_v1.tsv` does the same).

## One line

Every citation record in the link registry now carries the paper's own **title / doi / pmcid**, joined
from the corpus on `paper_id == pmid`. Before the fix the builder wrote `(hit title)[:120]` on the
retrieval route and `""` on the full-text gene-index route, so 2,429 of the shipped registry's 3,993
citation records had no title at all and 509 carried a 120-character prefix of one — and a title-keyed
audit against the corpus read that as "the two libraries disagree" (strict 247/825 = 29.94%,
prefix-40 369/825 = 44.73%). With the complete titles the same audit is 825/825, and every one of the
2,066 unmatched rows carries a named cause — at paper level 455 papers had no citation-side title,
122 had a clipped one and 1 differed only by display marks, so **zero are a genuine title
difference**. The frozen registry is not rewritten; the repaired registry ships beside it as a new
file that inverts to the frozen bytes exactly.

## What to read, in order

1. `out/CITATION_META_SPEC_v1.md` — the defect with source anchors, the fix, the two registry variants
   and their invariants, the before/after table, the per-row reason breakdown, the three non-circular
   controls, and what this card does **not** claim (the post-fix 100% is same-source by construction).
2. `out/CITATION_TITLE_COUNTERFACTUAL_v1.md` / `.json` — the readings themselves, in both calibers and
   both normalisations, plus the cross-corpus and field-control columns.
3. `out/CITATION_TITLE_LEDGER_v1.tsv` (per citation record, 3,993 rows) and
   `out/CITATION_TITLE_BY_PAPER_v1.tsv` (per cited paper, 825 rows) — the line-level evidence.
4. `out/G12_CONTROLS.json` — the reverse-control battery: six shapes planted on the real tree, the rc
   each produced and which check named it, with every file restored byte-identical.
5. `REPORT.md` — what was done, what was found besides the brief's defect, and what was deliberately
   not done.
6. `out/BACKFILL_META.json` and `out/MANIFEST.sha256` — inputs, join counts, output shas.

## Recompute (one command each)

```bash
cd /home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025
python3 scripts/backfill_citation_meta.py \
    --expect-frozen-sha a04be7711131225129ed6a8f6d3cb08862216c9187307a8a2b663b7bdd15e9cf
python3 scripts/counterfactual_titles.py
python3 scripts/verify_deliverables.py     # 12 checks, 12 PASS, rc=0
python3 scripts/g12_controls.py            # verdict=PASS, restored byte-identical
sha256sum -c out/MANIFEST.sha256           # 11/11 OK

cd /home/ubuntu/EYEKB_REPO
python3 tests/gate_cittitle_meta.py        # G12, rc=0
EYEKB_G3_PY=/home/ubuntu/.conda/envs/pipeline_env/bin/python /bin/bash tests/run_gates.sh
```

`EYEKB_G3_PY` matters here: G3 (dense retrieval anchors) and G7 (ontology gate, which follows the G3
convention) both need an interpreter with the locked dependencies. Under the bare `python3` on this
machine they report rc=3 INCONCLUSIVE and ENV_ERROR respectively — an environment precondition, not a
verdict about the repository.