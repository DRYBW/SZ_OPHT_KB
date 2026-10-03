# EXPECTED_COMPOSITION_v1_cell_suspension_v1 (Side-mounted · Unwired · OB-3 NOT_READY)

> Card t_93eb78a8 | Generated 2026-09-30 02:40 | Rule=PHASE0_INVENTORY_COMPV1X v1.0 FINAL + astra xhigh adjudication | Inherited v1 sha=fb13d529101e2741…

> ⛔ wiring=OFF; sole adjudication caliber = R1A + LOSO fold surfaces; pooled/RC6/E7/Q3merge are sensitivity or disclosure only, never usable as acceptance claims.

## 1. Primary Criteria Results (R1A, LOSO folds / Q4=RC4 old routing / Q5b=RC1 unchanged)

| dataset         | variant                                     | layer          |   n |   flagged |   rate | verdict   |
|:----------------|:--------------------------------------------|:---------------|----:|----------:|-------:|:----------|
| Q1_Lukowski2019 | PRIMARY R1A LOSO-fold                       | RC5_LOSO(n=10) |  10 |         2 |     20 | PASS      |
| Q2_GSE155288    | PRIMARY R1A LOSO-fold                       | RC5_LOSO(n=9)  |  10 |         3 |     30 | TRIGGER   |
| Q3_GSE137537    | PRIMARY R1A LOSO-fold                       | RC5_LOSO(n=7)  |  10 |         2 |     20 | PASS      |
| Q4_GSE148077    | PRIMARY R1A (routing unchanged, legacy ref) | RC4            |  10 |         4 |     40 | TRIGGER   |
| Q5b             | PRIMARY R1A (routing unchanged, legacy ref) | RC1            |  10 |         4 |     40 | TRIGGER   |


Total across five sets (descriptive)=15/50=30.0% (per-set adjudication unchanged by total). COMPV1 baseline R1A={4.0,6.0,5.0,4.0,4.0}→this card's primary metric={2,3,2,4,4}: Platform axis correction=Q1 -2.0 flag, Q2 -3.0 flag, Q3 -3.0 flag.

## 2. RC5 Tentative Full Surface (pooled13, delivery body)


| Class | A Interval | B Interval | Donor Median % | IQR | n_units |
|---|---|---|---|---|---|

| Rod | [35,59] | [28,59] | 36.07 | [35.23, 58.12] | 13 |
| Cone | [0,3] | [0,7] | 1.31 | [0.68, 2.7] | 13 |
| BC | [10,33] | [10,33] | 16.37 | [10.06, 32.85] | 13 |
| AC | [1,3] | [1,28] | 1.84 | [1.2, 2.6] | 13 |
| HC | [0,1] | [0,8] | 0.56 | [0.0, 0.77] | 13 |
| RGC | [0,2] | [0,15] | 0.87 | [0.33, 1.36] | 13 |
| MG | [13,30] | [3,30] | 23.18 | [13.98, 29.36] | 13 |
| Astro | [0,1] | [0,2] | 0.04 | [0.0, 0.22] | 13 |
| Micro | [0,2] | [0,2] | 0.61 | [0.38, 1.11] | 13 |
| RPE | [0,0] | [0,1] | 0.0 | [0.0, 0.0] | 13 |

## 3. LOSO Adjudication Folds (Intervals given by fold surface; each fold has only two studies—passing gate ≠ cross-study validation)

- **LOSO_Q1_Lukowski2019**: n_units=10 studies=2 donors=5; A: Rod[30,49], BC[10,34], MG[22,32], RGC[0,2]
- **LOSO_Q2_GSE155288**: n_units=9 studies=2 donors=6; A: Rod[35,59], BC[8,17], MG[5,29], RGC[0,2]
- **LOSO_Q3_GSE137537**: n_units=7 studies=2 donors=5; A: Rod[30,59], BC[16,34], MG[4,27], RGC[0,1]

## 4. Residual Trigger Row-by-Row Attribution → See JSON residual_xtab_primary / ledgers/compv1x_xtab_primary.tsv

## 5. Coverage Gaps → See JSON coverage_gaps (second study of sorted suspension, GSE203499 annotation artifact, foveola axis, cross-study protocol heterogeneity)
