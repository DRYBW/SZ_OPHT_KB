# Amendment 2: one criterion failed, and the change it invalidated

The first implementation made 30 the default for the whole pipeline. Criterion C5 as written in
`CARD.md` then measured this (G4 fixture volume, 11 clusters, `out/STAGEB_DIFFERENTIAL.json`):

| reading | pre-change | default 30 |
|---|---|---|
| query genes per cluster | 10 | 30, in 11 of 11 clusters |
| library candidate payload, per cluster, canonical JSON | — | **identical in 11 of 11** |
| normalized evidence report | `5b193d183a9c…` | `838178d22015…` |
| MCP calls | 38 | 41 |

**C5 fails as written**: the panel widened, the candidate field did not move. The criterion
expected the library answer to change, and it does not.

## Why it does not move, and what that means

The library ranks the cluster's genes and takes the top candidate. Going from 10 genes to 30 adds
genes that are, by rank, worse markers for whatever the library already found; on this volume they
produced no new candidate. The +8.15 pp measured in `wide30_panel_20261029` belongs to the *judge*
reading a wider panel, not to the library's ranking. And the judge is off by default — the shipped
default path calls no model.

So the implementation in force after `CARD.md` would have cost three extra MCP calls and a larger
report on every default run, to buy a gain that only exists on a path most runs never take.

## What the change is now

The width follows the caller:

| state | budget |
|---|---|
| explicit `--top-genes-n` | that value, always |
| `EYEKB_L2_BUDGET=1/true/on/yes` | 30 |
| `EYEKB_L2_BUDGET=0/false/off/no/""` | 10 (rollback) |
| unknown token | 10, one warning |
| unset, judged path (`--adjudicate` / `EYEKB_ADJUDICATE=1`) | **30** |
| unset, plain path | 10 — unchanged |

This is what "the judged layer defaults to 30 genes" means in a system whose default path is
model-free. Default output stays byte-identical, and the measured gain lands exactly where it was
measured.

## Revised criteria

| id | criterion |
|---|---|
| **C5a** | plain path, variable unset: the run is byte-identical to the pre-change run (payload per cluster and normalized report), i.e. C4 keeps holding after the redirection |
| **C5b** | judged path, variable unset, no channel configured: every cluster's evidence panel is 30 genes, and the library candidate payload is still identical to the pre-change run (the judge adds no library answer) |
| **C5c** | the rollback still wins: `EYEKB_L2_BUDGET=0` on the judged path gives 10 and reproduces the pre-change output |

## On changing a criterion after seeing a number

Recorded plainly, because the alternative is worse. C5 was written to predict that widening the
panel would change the library answer; the measurement says otherwise, and the number that refuted
it is in `out/STAGEB_DIFFERENTIAL.json` with its date. The original criterion stays visible in
`CARD.md`, unedited, so the prediction and its refutation can both be read. This is not a
threshold relaxed until something passed: the change itself was narrowed, and the narrowing costs
nothing that was measured.

One thing is *not* measured here and is not claimed: that a 30-gene panel helps a judge that
abstains less. The 25-volume reading says the accuracy over committed answers held (81.70 →
82.20 %), and it stays an observation on volumes this line has already used.