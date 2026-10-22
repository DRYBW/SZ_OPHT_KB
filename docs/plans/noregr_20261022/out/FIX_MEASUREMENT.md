# Carrier fix -- before/after on the recorded 28 volumes x 721 clusters

Every row below comes from a regression-harness run (n3_harness.py); the harness's pre-image is stored in each run directory.

## G4 verdict: **PASS**

| run | changed clusters | changed cells | overall consistent before | after | delta pp | ruling |
|---|---:|---:|---:|---:|---:|---|
| R1_narrowing_recorded_decls | 85 | 146904 | 41.498 | 40.852 | -0.646 | FAIL |
| R2_fix_recorded_decls | 45 | 111247 | 40.852 | 42.544 | +1.692 | PASS |
| R3_fix_tester_decls | 45 | 111247 | 41.061 | 42.679 | +1.618 | PASS |
| R4_narrowing_plus_fix_tester_decls | 126 | 258425 | 40.980 | 42.679 | +1.699 | PASS |

## The motivating cluster (CX15_optic_nerve_all cluster 31, 1,822 cells, truth `fibroblast`)

| run | before top-1 | n_shared | after top-1 | n_shared | grade |
|---|---|---:|---|---:|---|
| R1_narrowing_recorded_decls | Limbus_Sclera_fibroblast_C1 | 1 | None | None | consistent -> mixed |
| R2_fix_recorded_decls | None | None | onfibro_v13::Fibroblast | 2 | mixed -> consistent |
| R3_fix_tester_decls | None | None | onfibro_v13::Fibroblast | 2 | mixed -> consistent |
| R4_narrowing_plus_fix_tester_decls | Limbus_Sclera_fibroblast_C1 | 1 | onfibro_v13::Fibroblast | 2 | consistent -> consistent |

## Per-dataset consistent-share deltas (pp), the fix runs

### R2_fix_recorded_decls

| dataset | delta pp |
|---|---:|
| CX13_TM_corneal_scleral | +2.307 |
| CX15_optic_nerve_all | +2.530 |
| CX08_RPE_choroid_snRNA | +5.480 |
| PRE_GSE199013 | +6.517 |
| CX11_posterior_eye_atlas | +11.323 |
| CX14_TM_ciliary_snRNA | +12.123 |

### R3_fix_tester_decls

| dataset | delta pp |
|---|---:|
| CX13_TM_corneal_scleral | +2.307 |
| CX15_optic_nerve_all | +2.530 |
| CX08_RPE_choroid_snRNA | +5.480 |
| PRE_GSE199013 | +6.517 |
| CX11_posterior_eye_atlas | +9.304 |
| CX14_TM_ciliary_snRNA | +12.123 |

