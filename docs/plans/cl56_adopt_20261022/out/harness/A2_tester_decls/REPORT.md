# Regression-harness report -- A2 same adoption under the external tester's re-declarations

Declared change: as A1, with CX16 and CX11 re-pointed to ocular_surface

Before arm: `{"env": {"EYEKB_ACT_CL56": "1"}}`
After arm:  `{"env": {"EYEKB_ACT_CL56": "1"}, "inject": ["cl56_v15"]}`

Recorded set: 721 clusters / 1495330 cells / 28 volumes

## Ruling: **FAIL**

a change may not be reported as complete while any dataset's cell-weighted consistent share has fallen, unless the drop is attributed to a named cluster + named cause + named row/panel

Unattributed falls: CX02_adult_retina, CX03_retina_multiome, CX04_cowan_fovea, CX04_cowan_organoid, CX04_cowan_periphery, CX12_ocular_surface_snRNA, CX13_TM_corneal_scleral, CX13_central_cornea, PRE_GSE199013, PRE_OA-D001, PRE_OA-D002, PRE_OA-D068

- **CX02_adult_retina** consistent 72.376% -> 57.278% (-15.098pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX03_retina_multiome** consistent 36.842% -> 27.695% (-9.147pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX04_cowan_fovea** consistent 67.772% -> 56.720% (-11.052pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX04_cowan_organoid** consistent 90.134% -> 60.127% (-30.007pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX04_cowan_periphery** consistent 54.239% -> 37.269% (-16.970pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX12_ocular_surface_snRNA** consistent 35.997% -> 20.816% (-15.181pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX13_TM_corneal_scleral** consistent 41.306% -> 40.450% (-0.856pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX13_central_cornea** consistent 6.629% -> 6.386% (-0.243pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_GSE199013** consistent 43.376% -> 40.821% (-2.555pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_OA-D001** consistent 74.970% -> 66.089% (-8.881pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_OA-D002** consistent 35.879% -> 30.913% (-4.966pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_OA-D068** consistent 53.785% -> 18.923% (-34.862pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)

## Overall, cell-weighted

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---:|---:|---:|---:|---:|
| consistent | 42.679 | 37.506 | -5.173 | 299 | 278 |
| related | 17.232 | 18.250 | +1.018 | 89 | 92 |
| inconsistent | 18.955 | 28.739 | +9.784 | 162 | 227 |
| mixed | 21.134 | 15.505 | -5.629 | 171 | 124 |

## Per dataset

| dataset | clusters | cells | before consistent % | after consistent % | delta pp |
|---|---:|---:|---:|---:|---:|
| PRE_OA-D068 | 20 | 63773 | 53.785 | 18.923 | -34.862 |
| CX04_cowan_organoid | 15 | 43847 | 90.134 | 60.127 | -30.007 |
| CX04_cowan_periphery | 33 | 34702 | 54.239 | 37.269 | -16.970 |
| CX12_ocular_surface_snRNA | 21 | 37264 | 35.997 | 20.816 | -15.181 |
| CX02_adult_retina | 48 | 85452 | 72.376 | 57.278 | -15.098 |
| CX04_cowan_fovea | 25 | 19753 | 67.772 | 56.72 | -11.052 |
| CX03_retina_multiome | 31 | 51591 | 36.842 | 27.695 | -9.147 |
| PRE_OA-D001 | 32 | 62649 | 74.97 | 66.089 | -8.881 |
| PRE_OA-D002 | 19 | 69411 | 35.879 | 30.913 | -4.966 |
| PRE_GSE199013 | 38 | 42473 | 43.376 | 40.821 | -2.555 |
| CX13_TM_corneal_scleral | 29 | 51414 | 41.306 | 40.45 | -0.856 |
| CX13_central_cornea | 16 | 35890 | 6.629 | 6.386 | -0.243 |
| CX01_retina_snRNA | 37 | 97015 | 70.11 | 70.11 | +0.000 |
| CX07_iPSC_organoid_POAG | 21 | 46275 | 6.788 | 6.788 | +0.000 |
| CX08_RPE_choroid_scRNA | 20 | 73513 | 36.63 | 36.63 | +0.000 |
| CX08_RPE_choroid_snRNA | 18 | 70474 | 37.314 | 37.314 | +0.000 |
| CX09_voigt_RPE_choroid | 16 | 3624 | 74.31 | 74.31 | +0.000 |
| CX10_hiPSC_RPE | 25 | 54894 | 11.475 | 11.475 | +0.000 |
| CX11_posterior_eye_atlas | 20 | 54697 | 36.134 | 36.134 | +0.000 |
| CX13_ciliary_body | 17 | 32282 | 21.495 | 21.495 | +0.000 |
| CX13_iris | 17 | 55990 | 18.646 | 18.646 | +0.000 |
| CX13_lens | 11 | 13538 | 0.0 | 0.0 | +0.000 |
| CX14_TM_ciliary_snRNA | 17 | 78110 | 46.839 | 46.839 | +0.000 |
| CX15_optic_nerve_all | 46 | 71997 | 44.403 | 44.403 | +0.000 |
| CX16_tabula_sapiens_eye | 36 | 31808 | 18.112 | 18.112 | +0.000 |
| CX17_mouse_retina_all | 36 | 71751 | 0.0 | 0.0 | +0.000 |
| PRE_GSE268630 | 36 | 59276 | 71.705 | 71.705 | +0.000 |
| PRE_OA-D004 | 21 | 81867 | 44.765 | 44.765 | +0.000 |

## Cells moved, by grade transition

| transition | clusters | cells |
|---|---:|---:|
| mixed->inconsistent | 46 | 83895 |
| consistent->inconsistent | 17 | 66646 |
| inconsistent->related | 4 | 12394 |
| consistent->related | 5 | 11722 |
| related->inconsistent | 7 | 9164 |
| inconsistent->consistent | 1 | 1006 |
| mixed->related | 1 | 273 |

## Clusters whose ranking moved (311 clusters / 681726 cells)

| volume | cluster | n_cells | tissue | before | after | grade |
|---|---|---:|---|---|---|---|
| CX02_adult_retina | 4 | 12902 | retina | Rod (1) | S cone cell (4) | consistent -> inconsistent |
| PRE_OA-D068 | 8 | 11348 | retina | MG (1) | rod bipolar cell (2) | consistent -> inconsistent |
| PRE_OA-D004 | 3 | 10201 | trabecular_meshwork | Fibroblast (2) | Fibroblast (2) | consistent -> consistent |
| CX04_cowan_organoid | 3 | 8557 | retina | Rod (2) | rod bipolar cell (3) | consistent -> inconsistent |
| CX03_retina_multiome | 7 | 8308 | retina | None (None) | S cone cell (1) | mixed -> inconsistent |
| CX03_retina_multiome | 12 | 7918 | retina | None (None) | S cone cell (2) | mixed -> inconsistent |
| CX13_iris | 9 | 7148 | iris | SMC (2) | SMC (2) | inconsistent -> inconsistent |
| PRE_OA-D004 | 15 | 6736 | trabecular_meshwork | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| PRE_OA-D068 | 0 | 6661 | retina | RGC (1) | rod bipolar cell (2) | consistent -> inconsistent |
| PRE_OA-D004 | 0 | 6579 | trabecular_meshwork | Pericyte (3) | Pericyte (3) | consistent -> consistent |
| PRE_OA-D068 | 4 | 6577 | retina | Rod (2) | Rod (2) | consistent -> consistent |
| CX02_adult_retina | 24 | 6530 | retina | retina_interneuron::HC (7) | retina_interneuron::HC (7) | consistent -> consistent |
| PRE_OA-D004 | 11 | 6521 | trabecular_meshwork | Schwann (2) | Schwann (2) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 5 | 6501 | trabecular_meshwork | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX10_hiPSC_RPE | 0 | 6299 | rpe | RPE (2) | RPE (2) | consistent -> consistent |
| CX11_posterior_eye_atlas | 16 | 6257 | ocular_surface | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| PRE_OA-D002 | 5 | 6176 | ocular_surface | APC_MHCII_high (2) | APC_MHCII_high (2) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 7 | 6085 | retina | Rod (2) | Rod (2) | consistent -> consistent |
| CX13_TM_corneal_scleral | 12 | 5988 | trabecular_meshwork | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX02_adult_retina | 0 | 5932 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| PRE_OA-D001 | 12 | 5737 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| CX08_RPE_choroid_scRNA | 0 | 5670 | rpe | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 4 | 5657 | ocular_surface | onfibro_v13::Fibroblast (2) | keratocyte (5) | consistent -> related |
| PRE_OA-D001 | 22 | 5633 | retina | retina_v6::RGC (2) | retina_v6::RGC (2) | consistent -> consistent |
| CX04_cowan_organoid | 7 | 5606 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| PRE_OA-D001 | 3 | 5564 | retina | Rod (1) | S cone cell (3) | consistent -> inconsistent |
| PRE_OA-D001 | 4 | 5562 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | related -> related |
| PRE_OA-D002 | 15 | 5503 | ocular_surface | Myofibroblast (5) | Myofibroblast (5) | inconsistent -> inconsistent |
| PRE_OA-D001 | 18 | 5435 | retina | retina_interneuron::HC (6) | retina_interneuron::HC (6) | consistent -> consistent |
| CX04_cowan_organoid | 8 | 5320 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| PRE_OA-D004 | 8 | 5310 | trabecular_meshwork | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX08_RPE_choroid_scRNA | 15 | 5291 | rpe | retina_interneuron::BC (2) | retina_interneuron::BC (2) | inconsistent -> inconsistent |
| PRE_OA-D068 | 6 | 5191 | retina | AC (1) | AC (1) | consistent -> consistent |
| CX04_cowan_organoid | 12 | 5187 | retina | MG (1) | MG (1) | consistent -> consistent |
| PRE_OA-D004 | 14 | 5144 | trabecular_meshwork | non-pigmented ciliary epithelial cell (3) | non-pigmented ciliary epithelial cell (3) | related -> related |
| CX07_iPSC_organoid_POAG | 4 | 5133 | retina | BC (1) | rod bipolar cell (2) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 12 | 5089 | ocular_surface | onfibro_v13::Fibroblast (1) | onfibro_v13::Fibroblast (1) | consistent -> consistent |
| PRE_OA-D068 | 7 | 5021 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_OA-D004 | 6 | 5001 | trabecular_meshwork | Myofibroblast (5) | Myofibroblast (5) | inconsistent -> inconsistent |
| PRE_OA-D002 | 8 | 4981 | ocular_surface | Melanocyte (5) | Melanocyte (5) | consistent -> consistent |
| PRE_OA-D002 | 2 | 4970 | ocular_surface | progenitor cell (5) | progenitor cell (5) | related -> related |
| CX08_RPE_choroid_scRNA | 1 | 4872 | rpe | SMC (5) | SMC (5) | inconsistent -> inconsistent |
| CX02_adult_retina | 16 | 4822 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| CX13_central_cornea | 10 | 4802 | ocular_surface | corneal endothelial cell (4) | corneal endothelial cell (4) | related -> related |
| CX03_retina_multiome | 9 | 4746 | retina | None (None) | S cone cell (3) | mixed -> inconsistent |
| CX08_RPE_choroid_snRNA | 4 | 4743 | rpe | SMC (2) | SMC (2) | inconsistent -> inconsistent |
| CX03_retina_multiome | 11 | 4719 | retina | Rod (1) | S cone cell (4) | consistent -> inconsistent |
| CX04_cowan_organoid | 4 | 4558 | retina | Rod (3) | Rod (3) | consistent -> consistent |
| PRE_OA-D001 | 2 | 4488 | retina | MG (2) | MG (2) | consistent -> consistent |
| CX04_cowan_periphery | 3 | 4416 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_OA-D068 | 5 | 4397 | retina | Melanocyte (1) | S cone cell (2) | inconsistent -> related |
| PRE_OA-D002 | 9 | 4363 | ocular_surface | Pericyte (2) | keratocyte (3) | inconsistent -> related |
| CX04_cowan_periphery | 17 | 4194 | retina | BC (1) | BC (1) | related -> related |
| PRE_OA-D068 | 10 | 4194 | retina | retina_interneuron::HC (2) | retina_interneuron::HC (2) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 0 | 4114 | ocular_surface | corneal endothelial cell (3) | keratocyte (2) | related -> inconsistent |
| PRE_OA-D068 | 19 | 4097 | retina | Rod (2) | S cone cell (3) | consistent -> inconsistent |
| CX10_hiPSC_RPE | 17 | 4008 | rpe | Fibroblast (5) | Fibroblast (5) | inconsistent -> inconsistent |
| PRE_GSE268630 | 3 | 3998 | retina | Rod (1) | Rod (1) | consistent -> consistent |
| PRE_GSE268630 | 5 | 3997 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 8 | 3902 | retina | Rod (3) | rod bipolar cell (4) | consistent -> inconsistent |
| CX04_cowan_fovea | 16 | 3897 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX03_retina_multiome | 8 | 3799 | retina | None (None) | S cone cell (3) | mixed -> inconsistent |
| CX03_retina_multiome | 5 | 3781 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX02_adult_retina | 3 | 3763 | retina | None (None) | S cone cell (4) | mixed -> inconsistent |
| CX08_RPE_choroid_snRNA | 6 | 3715 | rpe | RPE (1) | RPE (1) | consistent -> consistent |
| CX02_adult_retina | 18 | 3645 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX08_RPE_choroid_snRNA | 10 | 3596 | rpe | Melanocyte (2) | Melanocyte (2) | consistent -> consistent |
| PRE_OA-D001 | 7 | 3577 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| PRE_OA-D068 | 14 | 3515 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | inconsistent -> inconsistent |
| CX13_ciliary_body | 5 | 3464 | ciliary_body | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX04_cowan_organoid | 9 | 3458 | retina | MG (1) | rod bipolar cell (2) | consistent -> inconsistent |
| PRE_OA-D002 | 11 | 3447 | ocular_surface | Fibroblast (4) | keratocyte (6) | consistent -> related |
| CX02_adult_retina | 9 | 3413 | retina | retina_interneuron::BC (5) | retina_interneuron::BC (5) | consistent -> consistent |
| CX10_hiPSC_RPE | 7 | 3323 | rpe | Fibroblast (2) | keratocyte (3) | inconsistent -> inconsistent |
| PRE_GSE268630 | 28 | 3300 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX01_retina_snRNA | 29 | 3296 | retina | retina_interneuron::HC (7) | retina_interneuron::HC (7) | consistent -> consistent |
| CX01_retina_snRNA | 15 | 3276 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX01_retina_snRNA | 17 | 3266 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX01_retina_snRNA | 23 | 3250 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | related -> related |
| CX01_retina_snRNA | 9 | 3234 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX01_retina_snRNA | 18 | 3233 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX01_retina_snRNA | 32 | 3233 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| CX01_retina_snRNA | 13 | 3228 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX01_retina_snRNA | 24 | 3228 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX01_retina_snRNA | 20 | 3226 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX01_retina_snRNA | 22 | 3225 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX01_retina_snRNA | 16 | 3223 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX01_retina_snRNA | 27 | 3223 | retina | None (None) | S cone cell (4) | mixed -> inconsistent |
| CX01_retina_snRNA | 31 | 3210 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| CX12_ocular_surface_snRNA | 7 | 3194 | ocular_surface | progenitor cell (5) | progenitor cell (5) | related -> related |
| PRE_OA-D004 | 4 | 3158 | trabecular_meshwork | trabecular meshwork cell (6) | trabecular meshwork cell (6) | related -> related |
| CX01_retina_snRNA | 33 | 3142 | retina | retina_interneuron::HC (4) | retina_interneuron::HC (4) | consistent -> consistent |
| CX07_iPSC_organoid_POAG | 3 | 3141 | retina | RPE (1) | RPE (1) | consistent -> consistent |
| PRE_GSE268630 | 24 | 3102 | retina | retina_interneuron::HC (4) | retina_interneuron::HC (4) | consistent -> consistent |
| CX10_hiPSC_RPE | 8 | 3091 | rpe | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_OA-D068 | 17 | 3077 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | inconsistent -> inconsistent |
| PRE_GSE199013 | 20 | 3033 | ocular_surface | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX13_lens | 6 | 2964 | lens | retina_interneuron::AC (1) | retina_interneuron::AC (1) | inconsistent -> inconsistent |
| PRE_GSE268630 | 21 | 2886 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 15 | 2868 | ocular_surface | Endo (2) | Endo (2) | related -> related |
| CX04_cowan_organoid | 13 | 2844 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX01_retina_snRNA | 14 | 2837 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | related -> related |
| PRE_GSE199013 | 4 | 2768 | ocular_surface | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| PRE_OA-D002 | 10 | 2732 | ocular_surface | Fibroblast (3) | Fibroblast (3) | consistent -> consistent |
| CX10_hiPSC_RPE | 16 | 2632 | rpe | Myofibroblast (3) | keratocyte (5) | inconsistent -> inconsistent |
| CX03_retina_multiome | 10 | 2625 | retina | cDC1 (1) | S cone cell (4) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 16 | 2544 | optic_nerve | retina_interneuron::HC (5) | retina_interneuron::HC (5) | consistent -> consistent |
| CX07_iPSC_organoid_POAG | 13 | 2523 | retina | None (None) | keratocyte (1) | mixed -> inconsistent |
| CX14_TM_ciliary_snRNA | 11 | 2497 | trabecular_meshwork | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX16_tabula_sapiens_eye | 0 | 2426 | ocular_surface | Pericyte (2) | keratocyte (3) | inconsistent -> related |
| CX03_retina_multiome | 6 | 2401 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | related -> related |
| PRE_GSE199013 | 24 | 2400 | ocular_surface | Granulocyte (1) | Granulocyte (1) | consistent -> consistent |
| CX02_adult_retina | 7 | 2398 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| PRE_GSE268630 | 16 | 2355 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| PRE_OA-D001 | 23 | 2349 | retina | MG (1) | rod bipolar cell (2) | inconsistent -> inconsistent |
| PRE_GSE268630 | 1 | 2331 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX10_hiPSC_RPE | 2 | 2289 | rpe | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 9 | 2274 | optic_nerve | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX13_TM_corneal_scleral | 1 | 2268 | trabecular_meshwork | progenitor cell (6) | progenitor cell (6) | consistent -> consistent |
| CX15_optic_nerve_all | 41 | 2224 | optic_nerve | Cone (1) | Cone (1) | consistent -> consistent |
| PRE_GSE268630 | 20 | 2192 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX15_optic_nerve_all | 29 | 2158 | optic_nerve | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 4 | 2107 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX10_hiPSC_RPE | 19 | 2098 | rpe | None (None) | keratocyte (1) | mixed -> inconsistent |
| CX04_cowan_organoid | 6 | 2065 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| CX15_optic_nerve_all | 39 | 1994 | optic_nerve | MG (1) | rod bipolar cell (2) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 2 | 1966 | optic_nerve | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX04_cowan_organoid | 2 | 1952 | retina | AC (1) | AC (1) | inconsistent -> inconsistent |
| CX10_hiPSC_RPE | 11 | 1944 | rpe | Schwann (1) | Schwann (1) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 3 | 1943 | optic_nerve | retina_interneuron::BC (2) | retina_interneuron::BC (2) | related -> related |
| CX15_optic_nerve_all | 15 | 1922 | optic_nerve | None (None) | S cone cell (5) | mixed -> inconsistent |
| CX15_optic_nerve_all | 0 | 1915 | optic_nerve | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX15_optic_nerve_all | 6 | 1913 | optic_nerve | retina_interneuron::BC (5) | retina_interneuron::BC (5) | consistent -> consistent |
| CX04_cowan_fovea | 11 | 1897 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_fovea | 0 | 1894 | retina | Rod (3) | S cone cell (4) | consistent -> inconsistent |
| PRE_GSE199013 | 29 | 1864 | ocular_surface | corneal endothelial cell (3) | keratocyte (2) | related -> inconsistent |
| CX07_iPSC_organoid_POAG | 19 | 1857 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| PRE_GSE268630 | 6 | 1839 | retina | retina_interneuron::AC (1) | retina_interneuron::AC (1) | inconsistent -> inconsistent |
| PRE_OA-D001 | 19 | 1811 | retina | retina_interneuron::HC (3) | retina_interneuron::HC (3) | consistent -> consistent |
| PRE_OA-D001 | 5 | 1809 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX15_optic_nerve_all | 4 | 1806 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX13_iris | 2 | 1790 | iris | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 9 | 1784 | retina | Rod (2) | S cone cell (4) | consistent -> inconsistent |
| CX07_iPSC_organoid_POAG | 10 | 1767 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_GSE268630 | 10 | 1716 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX13_TM_corneal_scleral | 9 | 1712 | trabecular_meshwork | Melanocyte (2) | Melanocyte (2) | consistent -> consistent |
| CX12_ocular_surface_snRNA | 13 | 1685 | ocular_surface | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| PRE_GSE268630 | 23 | 1668 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX07_iPSC_organoid_POAG | 9 | 1659 | retina | AC (1) | AC (1) | inconsistent -> inconsistent |
| CX02_adult_retina | 12 | 1589 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| PRE_GSE268630 | 31 | 1547 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX04_cowan_periphery | 28 | 1535 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX02_adult_retina | 13 | 1524 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX15_optic_nerve_all | 33 | 1515 | optic_nerve | retina_interneuron::AC (5) | retina_interneuron::AC (5) | consistent -> consistent |
| CX10_hiPSC_RPE | 12 | 1500 | rpe | None (None) | keratocyte (1) | mixed -> inconsistent |
| CX13_central_cornea | 4 | 1461 | ocular_surface | corneal epithelial cell (2) | rod bipolar cell (1) | related -> inconsistent |
| CX13_TM_corneal_scleral | 5 | 1452 | trabecular_meshwork | Granulocyte (1) | Granulocyte (1) | consistent -> consistent |
| PRE_GSE268630 | 27 | 1440 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX04_cowan_organoid | 1 | 1435 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_fovea | 1 | 1375 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| PRE_OA-D004 | 7 | 1369 | trabecular_meshwork | SMC (1) | SMC (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 32 | 1356 | retina | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| PRE_OA-D001 | 11 | 1356 | retina | retina_interneuron::BC (5) | retina_interneuron::BC (5) | consistent -> consistent |
| CX03_retina_multiome | 19 | 1341 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| PRE_GSE268630 | 9 | 1292 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | related -> related |
| CX08_RPE_choroid_snRNA | 17 | 1288 | rpe | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| CX04_cowan_fovea | 5 | 1282 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX13_TM_corneal_scleral | 14 | 1261 | trabecular_meshwork | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX13_ciliary_body | 10 | 1208 | ciliary_body | Melanocyte (2) | Melanocyte (2) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 28 | 1208 | ocular_surface | cDC1 (1) | S cone cell (2) | inconsistent -> related |
| CX10_hiPSC_RPE | 6 | 1202 | rpe | Fibroblast (2) | keratocyte (3) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 12 | 1200 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| CX07_iPSC_organoid_POAG | 14 | 1189 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 8 | 1186 | trabecular_meshwork | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX02_adult_retina | 17 | 1183 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| PRE_OA-D004 | 2 | 1158 | trabecular_meshwork | Pericyte (1) | Pericyte (1) | inconsistent -> inconsistent |
| CX04_cowan_organoid | 11 | 1142 | retina | MG (1) | rod bipolar cell (2) | consistent -> inconsistent |
| CX04_cowan_periphery | 21 | 1101 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX13_central_cornea | 5 | 1093 | ocular_surface | onfibro_v13::Fibroblast (2) | keratocyte (4) | consistent -> related |
| PRE_GSE199013 | 30 | 1085 | ocular_surface | onfibro_v13::Fibroblast (2) | keratocyte (5) | consistent -> related |
| PRE_OA-D001 | 0 | 1064 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_GSE199013 | 34 | 1057 | ocular_surface | progenitor cell (5) | progenitor cell (5) | consistent -> consistent |
| PRE_GSE268630 | 8 | 1045 | retina | Astro (1) | Astro (1) | inconsistent -> inconsistent |
| CX04_cowan_fovea | 7 | 1040 | retina | BC (1) | BC (1) | related -> related |
| PRE_GSE268630 | 19 | 1038 | retina | retina_interneuron::HC (3) | retina_interneuron::HC (3) | consistent -> consistent |
| CX15_optic_nerve_all | 7 | 1024 | optic_nerve | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| PRE_GSE268630 | 2 | 1019 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX13_central_cornea | 3 | 1006 | ocular_surface | Keratocytes (1) | keratocyte (2) | inconsistent -> consistent |
| PRE_OA-D001 | 29 | 1005 | retina | retina_interneuron::AC (4) | retina_interneuron::AC (4) | consistent -> consistent |
| PRE_OA-D068 | 1 | 983 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX10_hiPSC_RPE | 18 | 965 | rpe | Myofibroblast (2) | Myofibroblast (2) | inconsistent -> inconsistent |
| CX02_adult_retina | 15 | 964 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX13_TM_corneal_scleral | 6 | 955 | trabecular_meshwork | corneal endothelial cell (3) | keratocyte (2) | related -> inconsistent |
| CX03_retina_multiome | 16 | 948 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX02_adult_retina | 1 | 945 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX15_optic_nerve_all | 19 | 942 | optic_nerve | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| PRE_OA-D001 | 30 | 929 | retina | RPE (2) | RPE (2) | consistent -> consistent |
| CX03_retina_multiome | 13 | 916 | retina | retina_interneuron::HC (6) | retina_interneuron::HC (6) | consistent -> consistent |
| CX13_central_cornea | 2 | 886 | ocular_surface | None (None) | keratocyte (1) | mixed -> inconsistent |
| CX10_hiPSC_RPE | 21 | 884 | rpe | Schwann (1) | Schwann (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 11 | 873 | retina | None (None) | S cone cell (1) | mixed -> inconsistent |
| CX02_adult_retina | 6 | 869 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| PRE_OA-D001 | 24 | 852 | retina | retina_interneuron::BC (6) | retina_interneuron::BC (6) | consistent -> consistent |
| CX02_adult_retina | 19 | 848 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX10_hiPSC_RPE | 9 | 841 | rpe | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX01_retina_snRNA | 35 | 811 | retina | RPE (2) | RPE (2) | consistent -> consistent |
| CX03_retina_multiome | 21 | 808 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX02_adult_retina | 26 | 785 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_organoid | 5 | 784 | retina | Rod (2) | Rod (2) | consistent -> consistent |
| CX02_adult_retina | 20 | 754 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX13_central_cornea | 13 | 743 | ocular_surface | progenitor cell (2) | keratocyte (1) | consistent -> consistent |
| CX13_TM_corneal_scleral | 23 | 740 | trabecular_meshwork | Endo (1) | Endo (1) | related -> related |
| PRE_OA-D001 | 21 | 727 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| PRE_GSE199013 | 32 | 716 | ocular_surface | SMC (2) | SMC (2) | inconsistent -> inconsistent |
| PRE_OA-D068 | 12 | 698 | retina | Astro (2) | Astro (2) | inconsistent -> inconsistent |
| PRE_OA-D068 | 11 | 695 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 22 | 647 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX04_cowan_organoid | 10 | 637 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX07_iPSC_organoid_POAG | 7 | 616 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX03_retina_multiome | 26 | 595 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX04_cowan_periphery | 24 | 592 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX16_tabula_sapiens_eye | 7 | 582 | ocular_surface | None (None) | rod bipolar cell (4) | mixed -> inconsistent |
| CX03_retina_multiome | 18 | 561 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| PRE_OA-D001 | 14 | 554 | retina | AC (1) | AC (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 22 | 546 | ocular_surface | basal cell (3) | keratocyte (2) | inconsistent -> inconsistent |
| PRE_GSE268630 | 35 | 515 | retina | retina_interneuron::HC (3) | retina_interneuron::HC (3) | consistent -> consistent |
| PRE_OA-D001 | 27 | 515 | retina | RGC (2) | RGC (2) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 2 | 513 | rpe | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 17 | 511 | ocular_surface | Myofibroblast (5) | Myofibroblast (5) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 30 | 496 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| PRE_OA-D001 | 8 | 493 | retina | Rod (3) | S cone cell (5) | inconsistent -> inconsistent |
| CX03_retina_multiome | 0 | 484 | retina | RGC (2) | RGC (2) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 3 | 470 | rpe | Schwann (1) | Schwann (1) | consistent -> consistent |
| PRE_OA-D002 | 13 | 468 | ocular_surface | corneal endothelial cell (3) | keratocyte (2) | related -> inconsistent |
| CX03_retina_multiome | 4 | 459 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX13_TM_corneal_scleral | 11 | 440 | trabecular_meshwork | onfibro_v13::Fibroblast (2) | keratocyte (5) | consistent -> related |
| CX04_cowan_fovea | 6 | 439 | retina | BC (1) | BC (1) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 6 | 434 | rpe | Fibroblast (1) | Fibroblast (1) | consistent -> consistent |
| CX02_adult_retina | 35 | 430 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX04_cowan_periphery | 16 | 430 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| PRE_OA-D068 | 16 | 428 | retina | MG (1) | rod bipolar cell (2) | inconsistent -> inconsistent |
| PRE_GSE268630 | 30 | 426 | retina | retina_interneuron::BC (5) | retina_interneuron::BC (5) | consistent -> consistent |
| CX02_adult_retina | 5 | 423 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| PRE_GSE268630 | 22 | 419 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 23 | 413 | ocular_surface | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent |
| CX10_hiPSC_RPE | 23 | 411 | rpe | Melanocyte (2) | Melanocyte (2) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 10 | 384 | retina | Rod (2) | Rod (2) | consistent -> consistent |
| CX13_iris | 8 | 376 | iris | SMC (1) | SMC (1) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 5 | 365 | rpe | Limbus_Sclera_fibroblast_C1 (1) | Limbus_Sclera_fibroblast_C1 (1) | consistent -> consistent |
| CX04_cowan_fovea | 8 | 357 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX04_cowan_fovea | 4 | 349 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 2 | 331 | ocular_surface | Melanocyte (6) | Melanocyte (6) | inconsistent -> inconsistent |
| CX02_adult_retina | 8 | 329 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX15_optic_nerve_all | 44 | 325 | optic_nerve | retina_v6::RGC (2) | retina_v6::RGC (2) | consistent -> consistent |
| PRE_OA-D001 | 17 | 316 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX12_ocular_surface_snRNA | 20 | 312 | ocular_surface | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| PRE_OA-D001 | 1 | 308 | retina | MG (3) | MG (3) | inconsistent -> inconsistent |
| PRE_OA-D068 | 18 | 307 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 15 | 305 | ocular_surface | None (None) | keratocyte (1) | mixed -> inconsistent |
| PRE_OA-D068 | 2 | 300 | retina | retina_v6::RGC (1) | retina_v6::RGC (1) | consistent -> consistent |
| CX13_TM_corneal_scleral | 22 | 289 | trabecular_meshwork | goblet cell (2) | keratocyte (1) | related -> inconsistent |
| PRE_GSE199013 | 35 | 289 | ocular_surface | None (None) | keratocyte (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 15 | 282 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX03_retina_multiome | 28 | 273 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| PRE_GSE268630 | 29 | 273 | retina | None (None) | S cone cell (2) | mixed -> related |
| CX16_tabula_sapiens_eye | 21 | 272 | ocular_surface | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 14 | 261 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX03_retina_multiome | 22 | 255 | retina | Cone (1) | Cone (1) | consistent -> consistent |
| CX04_cowan_fovea | 23 | 253 | retina | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| PRE_OA-D001 | 28 | 250 | retina | retina_v6::RGC (4) | retina_v6::RGC (4) | consistent -> consistent |
| CX02_adult_retina | 22 | 229 | retina | retina_interneuron::BC (4) | retina_interneuron::BC (4) | consistent -> consistent |
| CX03_retina_multiome | 14 | 217 | retina | retina_interneuron::HC (4) | retina_interneuron::HC (4) | consistent -> consistent |
| CX03_retina_multiome | 25 | 210 | retina | retina_interneuron::BC (3) | retina_interneuron::BC (3) | consistent -> consistent |
| CX04_cowan_fovea | 10 | 196 | retina | AC (2) | AC (2) | consistent -> consistent |
| CX15_optic_nerve_all | 36 | 193 | optic_nerve | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX04_cowan_periphery | 1 | 186 | retina | RPE (3) | RPE (3) | consistent -> consistent |
| PRE_OA-D001 | 26 | 179 | retina | Cone (2) | Cone (2) | consistent -> consistent |
| CX13_TM_corneal_scleral | 25 | 178 | trabecular_meshwork | Fibroblast (1) | Fibroblast (1) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 4 | 177 | rpe | SMC (5) | SMC (5) | consistent -> consistent |
| CX04_cowan_fovea | 19 | 173 | retina | APC_MHCII_high (4) | APC_MHCII_high (4) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 27 | 168 | retina | Astro (1) | rod bipolar cell (2) | consistent -> inconsistent |
| CX03_retina_multiome | 20 | 159 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 0 | 157 | retina | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| PRE_OA-D004 | 19 | 157 | trabecular_meshwork | trabecular meshwork cell (4) | trabecular meshwork cell (4) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 12 | 156 | rpe | RPE (2) | RPE (2) | consistent -> consistent |
| CX10_hiPSC_RPE | 24 | 155 | rpe | Fibroblast (3) | Fibroblast (3) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 26 | 153 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX04_cowan_fovea | 2 | 151 | retina | HC (1) | rod bipolar cell (2) | consistent -> inconsistent |
| CX04_cowan_fovea | 17 | 138 | retina | Astro (1) | rod bipolar cell (2) | consistent -> inconsistent |
| CX04_cowan_fovea | 9 | 126 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_OA-D068 | 13 | 126 | retina | AC (1) | rod bipolar cell (2) | consistent -> inconsistent |
| CX04_cowan_periphery | 23 | 120 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 9 | 96 | ocular_surface | Fibroblast (1) | Fibroblast (1) | inconsistent -> inconsistent |
| CX03_retina_multiome | 24 | 93 | retina | AC (1) | AC (1) | consistent -> consistent |
| CX04_cowan_fovea | 18 | 84 | retina | RPE (3) | RPE (3) | consistent -> consistent |
| CX02_adult_retina | 47 | 77 | retina | retina_v6::RPE (3) | retina_v6::RPE (3) | inconsistent -> inconsistent |
| PRE_GSE199013 | 26 | 77 | ocular_surface | Granulocyte (1) | Granulocyte (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 19 | 72 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| PRE_GSE199013 | 13 | 70 | ocular_surface | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX15_optic_nerve_all | 45 | 55 | optic_nerve | None (None) | S cone cell (1) | mixed -> inconsistent |
| CX09_voigt_RPE_choroid | 15 | 47 | rpe | Granulocyte (1) | Granulocyte (1) | inconsistent -> inconsistent |
| CX01_retina_snRNA | 36 | 35 | retina | RPE (2) | RPE (2) | consistent -> consistent |
| CX04_cowan_periphery | 25 | 35 | retina | RGC (1) | rod bipolar cell (2) | consistent -> inconsistent |
| CX04_cowan_fovea | 13 | 26 | retina | None (None) | rod bipolar cell (1) | mixed -> inconsistent |
| CX13_TM_corneal_scleral | 26 | 23 | trabecular_meshwork | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX15_optic_nerve_all | 14 | 22 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | consistent -> consistent |
| CX01_retina_snRNA | 26 | 17 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX08_RPE_choroid_scRNA | 19 | 13 | rpe | pDC (1) | keratocyte (2) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 35 | 13 | ocular_surface | None (None) | keratocyte (1) | mixed -> inconsistent |
| PRE_GSE199013 | 37 | 13 | ocular_surface | corneal endothelial cell (3) | keratocyte (2) | related -> inconsistent |
| CX03_retina_multiome | 17 | 11 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |

## Harness pre-image

```json
{
 "role": "the harness's own pre-image: every number it reports is re-derivable from these files plus the frozen inputs",
 "files": [
  {
   "path": "scripts/n3_harness.py",
   "sha256": "9f55a8ccbd20219615b660218ac2ac7ba8602242ea62c51bb98adcec0bedb807",
   "bytes": 15673
  },
  {
   "path": "scripts/wave_common.py",
   "sha256": "f8226dc4aefc799ace536b66748ece67494826031c21242b6e25b44389f37863",
   "bytes": 18547
  }
 ],
 "inputs": {
  "input_manifest_sha256": "d2f1211613f0bbd6da6b5a21c179b8cadd0a9bca5678bfa524b56c619348dc61",
  "recordings_sha256": {
   "annotation_evidence_report.json": "325b0592893cb90a739f464ed560b05bd2cd395ccee1a46fe72df036447aa18c"
  },
  "fixed_sha256": {
   "ledger_cluster_level.tsv": "9e2a0844ad639e0ba0ed6cccfa3ca7f109cde98d4f91568621cd0e4df85b1427",
   "kb_family_crosswalk_v2.json": "c704b3a5dc5d5dbf024b6cb101356a4c23eacd9978bba0393c07e81d550e64f8",
   "_tissue_class_crosswalk_v1.json": "a06a753af39700541962bf5dc03472635e024130b3f297d57bc1ac2802a5682d",
   "markers_cl_alignment_v2_unified.json": "48051cdae915b82e6e7812da9b98f93b41f51c5fac14bdb370bd5ccdb969a0a1",
   "cl-base.obo": "c6274fb65cdf740b983a06b74cb678814249d7f8e580c2ec9de54bf204a2b1c7",
   "markers_v10_antseg_increment.json": "c488fc26b615e57addd1d0828b20293d07fb3a7a92baedca5d32a528bc597f47",
   "eyekb_core.py": "3dadbbbaf2631da0f48760beb95278f5fabd675e6108282c9080fae67a61d736",
   "markers_membrane_v1.json": "c4268a6e0655f6d89f913289766f3edc062f116a82a983abbfccd7cee54198d1",
   "markers_k9_ocs_increment.json": "139b622082f80a6c3962b7a2532dc8c3fed8a87a92154ccd98491ef4f2540a71",
   "markers_v12_holefill_increment.json": "a9bb4feb86e61360215a403baef74f8eb661fad5d7158de32940c54f52a8475f",
   "probe_tool_panel_identity.py": "bcf619b252a248bd64de00c3d61cd64d4c39dde9dff864d8b3694ed2de666370",
   "probe_opticnerve_scope_ab.py": "f84301d6c41c366a1402a00c90e319a06d99982f8b5684573ed703bdeaa0f500",
   "FINDING_OPTIC_NERVE_REGRESSION_20261022.md": "92ea5d44c7a97925bdad54c586da5dd23ec0e7cd31c1f27e5502290d5cbe0311",
   "GATE_A3.json": "5b77be8f1cc2a657e08ce022d6ca1e2e76062f11b22930603deffd9adab027dc",
   "gate_a3_no_collateral.py": "e3e1c6c279a65c63acb72c4558fb5b9dc30871d99f7e55575aaca4fe9bdb94d4",
   "REPORT_TISSUE_SCOPE_v2.0_DEFAULT_ON.md": "a7d5f157f3e8355c12cd2e01e3c310e84ded7d1e9b855d6538d4791813812f88",
   "PREREG_TISSUE_SCOPE_20261020.md": "1b8983ac117da4a275e91ee8bfc86b56e7889af97aa3eefd9a49984a3f3f339c",
   "cross_dataset_summary.csv": "2f90ca79ec1abd14698ebc9dd06659f45013bdca1e5e475b637da1d9f0160e81",
   "EyeKB更新后重评_20261021.md": "069bd08f5dedb076ed649449d031ab8f5ee939611bb18d604c1a29a4dedf00cf"
  }
 }
}
```
