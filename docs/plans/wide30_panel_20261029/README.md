# Wide evidence panel: 30 genes versus 10 genes

This directory records one measurement: how much the adjudication layer gains when the
evidence panel it is given grows from 10 genes to 30 genes per cluster. Nothing else
changes between the two arms.

- `REPORT.md` - the reading, both denominators, the cluster-level decomposition, and the
  two wrong numbers that were produced first and rejected.
- `out/WIDE30_OFFICIAL.json` - both calibers side by side.
- `out/WIDE30_VS_NARROW.json` - per-cluster table (write target of `compare_wide30.py`).
- `out/JUDGE_SCORE_judge_prod_think_feimao.json`, `out/JUDGE_SCORE_judge_prod_think_wide30.json`
  - the two scored artefacts the scripts read, so the numbers can be recomputed without
  calling a model again.
- `scripts/compare_wide30.py`, `scripts/verify_wide30.py` - the decomposition and an
  assertion pass over every printed relationship.

## Redaction

The committed copies of the two scored artefacts have the per-volume `model` field
replaced with `external-model`. That is a metadata field only; every score, count and
label is unchanged, and the reproduction below still regenerates
`WIDE30_VS_NARROW.json` byte for byte (sha256 `bf02d431...`). The identifier of the model
that produced the readings is kept in the evaluation workspace, not in this repository,
so that no model name or endpoint is shipped with the code.

Source artefacts before redaction:

| file | sha256 |
|---|---|
| `JUDGE_SCORE_judge_prod_think_feimao.json` | `b2b494285ec00737e9a7623e693c41d3bec9ac611b6ef9b7ae89dbc3d7351b2b` |
| `JUDGE_SCORE_judge_prod_think_wide30.json` | `4c9a37eef4befecd277125d5d89d541b1ac3ccf9397b4d5461f5f6256bf7b406` |

## Running it here

The scripts import `score_judge`, the module that folds author vocabulary and knowledge
base vocabulary onto one family key. That module and the per-cluster truth tables belong
to the evaluation workspace and are not part of this repository, so the scripts say so
and stop rather than guessing:

```
$ python scripts/verify_wide30.py
score_judge.py is not part of this repository copy. Point WIDE30_ROOT at an
evaluation workspace that contains score_judge.py and score_corpus.py, ...
```

With a workspace that has them:

```
WIDE30_ROOT=/path/to/workspace python scripts/verify_wide30.py
```

Data are read from `<WIDE30_ROOT>/out/` when that directory exists, otherwise from
`<WIDE30_ROOT>/` itself.