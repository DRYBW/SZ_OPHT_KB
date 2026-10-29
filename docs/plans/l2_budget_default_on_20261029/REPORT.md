# Result: the 30-gene panel follows the judged path

Date 2026-10-29. Card: `CARD.md`, then `AMENDMENT_1.md`, `AMENDMENT_2.md`.
Everything below was measured on this machine; the scripts that produce each number are in
`scripts/`, the raw readings in `out/`.

## 1. What shipped

`pipeline/l2_budget.py` now resolves the per-cluster query budget like this:

| state | budget | note |
|---|---|---|
| explicit `--top-genes-n` | that value | never rewritten, any state |
| `EYEKB_L2_BUDGET=1/true/on/yes` | 30 | door on |
| `EYEKB_L2_BUDGET=0/false/off/no/""` | 10 | rollback |
| unrecognised value | 10 + one warning | fail-closed |
| unset, judged path (`--adjudicate` / `EYEKB_ADJUDICATE=1`) | **30** | this is the change |
| unset, plain path | 10 | unchanged |

Two call sites pass the judged-path flag: `pipeline/stage_b_evidence.py` and
`pipeline/run_pipeline.py`. Nothing else in either file moved.

## 2. Why it is scoped to the judged path and not global

The first implementation made 30 the default everywhere. Criterion C5 then refuted the
prediction behind it, on the G4 fixture volume (11 clusters):

| reading | pre-change | global default 30 |
|---|---|---|
| query genes per cluster | 10 | 30 (11/11 clusters) |
| library candidate payload, per cluster | — | **identical in 11/11** |
| MCP calls | 38 | 41 |
| normalized evidence report | `5b193d18…` | `838178d2…` |

The library's ranking does not move when the panel widens: extra genes ranked below the first
ten produced no new candidate on this volume. So a global flip would have cost three extra
calls and a larger report on every run to buy a gain that only exists on the path where a
model reads the panel — and that path is off by default. The width was therefore attached to
the judged path. The failed prediction is kept in `AMENDMENT_2.md` rather than deleted.

## 3. Criteria, as measured

`scripts/gate_l2_budget.py` — **15 checks, all PASS, rc=0**: seven door-semantics cases
(unset plain 10 / unset judged 30 / env-on 30 in both / env-off beats judged 10 / empty 10),
four explicit-value cases (never rewritten), three unknown-token cases (budget 10, exactly one
warning, explicit still honoured), and the change surface (exactly three production files).

`scripts/stageb_differential.py` — six Stage B runs of the same 11-cluster volume:

| comparison | candidate payload identical | normalized report identical | verdict |
|---|---|---|---|
| C4 rollback (`=0`, first implementation) vs pre | 11/11 | yes | PASS |
| C5 original criterion (global default 30) vs pre | 11/11 | no | **FAIL (refuted)** |
| C5a plain path vs pre | 11/11 | yes | PASS |
| C5b judged path vs pre | 11/11 | no — panel 30 in 11/11 clusters | PASS |
| C5c `=0` on the judged path vs pre | 11/11 | yes | PASS |

The plain path is byte-identical to the pre-change pipeline; the judged path is the same
pipeline with a 30-gene panel and the same library answer.

`scripts/g4_default_differential.py` — criterion C8, the frozen G4 identity anchors:

| state | `stage_a/processed.h5ad` | `decisions_template.csv` | `annotation_evidence_report.md` (normalized) |
|---|---|---|---|
| pre (HEAD code) | `dbc657fa…` | `fe269908…` | `7c225802…` |
| post (this card) | `dbc657fa…` | `fe269908…` | `7c225802…` |
| frozen expectation | `dbc657fa…` | `fe269908…` | `6f795b32…` |

Anchors moved by this change: **none**. Two consecutive post runs were identical.
`AMENDMENT_1.md` expected the evidence report and the decision template to move; with the
narrowed design they do not, and the measurement says so.

The official gate agrees: `tests/verify_pipeline.py` reports the same single mismatch it
reported before this card (`annotation_evidence_report.md` against `6f795b32…`). That red is
pre-existing and this card deliberately did not re-anchor it — re-anchoring would have folded an
unexplained drift into a change that had nothing to do with it.

## 4. Ledgers

`scripts/registry_rows.py` re-took the identity of the three edited files in
`docs/W3_PIPELINE_REGISTRY.tsv` (L2-01, L2-03, L2-11) and appended one change-control row
(`CHG-20261029-L2BUDGET-JUDGEDEFAULT`) to `docs/CHANGE_CONTROL_G6_INSTANCE.tsv`.

| gate | reading | verdict |
|---|---|---|
| `tests/gate_change_control.py` | 15 changes, 21 checks, fail=0 | **PASS** rc=0 |
| `tests/gate_g5g6_negative.py` | 16/17 as expected | unchanged from baseline |
| `tests/verify_pipeline.py` (G4) | 1/3 mismatch, same pair as before this card | unchanged from baseline |

The one negative-battery case that does not match its expectation is the G5 positive control,
which fails on two registered-file digests that were already stale before this card —
`L1-11M:eyekb_core.py` and `L6-47:SWITCH_COVERAGE_REGISTRY.tsv`. Both files are byte-identical
to `HEAD`; the ledger rows are old. Not this change, and not fixed here.

## 5. What is not claimed

The +8.15 pp top-1 and +7.34 pp coverage come from 25 volumes this line has already used, so
they are an observation, not an efficacy verdict; under the standing rule a capability claim
needs volumes that were never seen during design. What this card adds is narrower and firmer:
the judged path now reads the wider panel, the plain path is byte-identical, and the rollback is
one environment variable.

## 6. Reproduce

```
python3 docs/plans/l2_budget_default_on_20261029/scripts/gate_l2_budget.py       # 15 checks
python3 docs/plans/l2_budget_default_on_20261029/scripts/stageb_differential.py # 6 runs on disk
python3 docs/plans/l2_budget_default_on_20261029/scripts/g4_default_differential.py
python3 docs/plans/l2_budget_default_on_20261029/scripts/registry_rows.py      # ledgers + both gates
```

The Stage B runs the differential reads live in `/tmp/l2gate/` and are not shipped with the
repository; the six run directories are rebuilt by the six `stage_b_evidence.py` invocations
described in `AMENDMENT_2.md` (same inputs, one environment difference each). What is shipped is
each run's evidence report and decision template under `out/stageb_runs/<state>/`, so the
normalized-report identity in §3 can be re-derived from the committed bytes without re-running
anything.