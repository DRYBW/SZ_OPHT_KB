# EXPECTED_COMPOSITION_v1_cell_suspension_v1（旁挂·未接线·OB-3 NOT_READY）

> 卡 t_93eb78a8 | 生成 2026-09-30 02:40 | 规则=PHASE0_INVENTORY_COMPV1X v1.0 FINAL + astra xhigh 裁定 | 继承 v1 sha=fb13d529101e2741…

> ⛔ wiring=OFF；判定唯一口径=R1A+LOSO 折面；pooled/RC6/E7/Q3merge 均敏感性或披露，禁作达标声明。

## 1. 主判据结果（R1A, LOSO 折 / Q4=RC4 旧路由 / Q5b=RC1 不变）

| dataset         | variant                                     | layer          |   n |   flagged |   rate | verdict   |
|:----------------|:--------------------------------------------|:---------------|----:|----------:|-------:|:----------|
| Q1_Lukowski2019 | PRIMARY R1A LOSO-fold                       | RC5_LOSO(n=10) |  10 |         2 |     20 | PASS      |
| Q2_GSE155288    | PRIMARY R1A LOSO-fold                       | RC5_LOSO(n=9)  |  10 |         3 |     30 | TRIGGER   |
| Q3_GSE137537    | PRIMARY R1A LOSO-fold                       | RC5_LOSO(n=7)  |  10 |         2 |     20 | PASS      |
| Q4_GSE148077    | PRIMARY R1A (routing unchanged, legacy ref) | RC4            |  10 |         4 |     40 | TRIGGER   |
| Q5b             | PRIMARY R1A (routing unchanged, legacy ref) | RC1            |  10 |         4 |     40 | TRIGGER   |


五集合计(描述性)=15/50=30.0%（逐集判定不因合计改变）。COMPV1 基线 R1A={4.0,6.0,5.0,4.0,4.0}→本卡主口径={2,3,2,4,4}：平台轴修正=Q1 -2.0 旗、Q2 -3.0 旗、Q3 -3.0 旗。

## 2. RC5 暂定全量面（pooled13, 交付本体）


| 类 | A 区间 | B 区间 | 供者中位% | IQR | n_units |
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

## 3. LOSO 判定折（区间由折面给出；每折仅两项研究——过门≠跨研究验证）

- **LOSO_Q1_Lukowski2019**: n_units=10 studies=2 donors=5; A: Rod[30,49], BC[10,34], MG[22,32], RGC[0,2]
- **LOSO_Q2_GSE155288**: n_units=9 studies=2 donors=6; A: Rod[35,59], BC[8,17], MG[5,29], RGC[0,2]
- **LOSO_Q3_GSE137537**: n_units=7 studies=2 donors=5; A: Rod[30,59], BC[16,34], MG[4,27], RGC[0,1]

## 4. 残余触发逐行归因 → 见 JSON residual_xtab_primary / ledgers/compv1x_xtab_primary.tsv

## 5. 覆盖缺口 → 见 JSON coverage_gaps（分选悬液第二研究、GSE203499 注释件、foveola 轴、跨研究方案异质性）
