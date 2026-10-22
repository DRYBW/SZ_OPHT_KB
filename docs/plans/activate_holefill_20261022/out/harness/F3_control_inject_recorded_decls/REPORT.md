# Regression-harness report -- F3 control: the measurement-only injection arm

Declared change: measurement-only: the OFF core with holefill_v12 injected into `all`

Before arm: `{"env": {"EYEKB_ACT_HOLEFILL": "0"}}`
After arm:  `{"env": {"EYEKB_ACT_HOLEFILL": "0"}, "inject": ["holefill_v12"]}`

Recorded set: 721 clusters / 1495330 cells / 28 volumes

## Ruling: **FAIL**

a change may not be reported as complete while any dataset's cell-weighted consistent share has fallen, unless the drop is attributed to a named cluster + named cause + named row/panel

Unattributed falls: CX01_retina_snRNA, CX02_adult_retina, CX03_retina_multiome, CX04_cowan_fovea, CX04_cowan_organoid, CX04_cowan_periphery, CX09_voigt_RPE_choroid, CX10_hiPSC_RPE, CX12_ocular_surface_snRNA, CX13_central_cornea, PRE_GSE268630, PRE_OA-D001, PRE_OA-D068

- **CX01_retina_snRNA** consistent 70.110% -> 69.238% (-0.872pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX02_adult_retina** consistent 72.376% -> 57.278% (-15.098pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX03_retina_multiome** consistent 36.842% -> 27.695% (-9.147pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX04_cowan_fovea** consistent 67.772% -> 57.758% (-10.014pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX04_cowan_organoid** consistent 90.134% -> 58.435% (-31.699pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX04_cowan_periphery** consistent 54.239% -> 13.140% (-41.099pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX09_voigt_RPE_choroid** consistent 74.310% -> 70.006% (-4.304pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX10_hiPSC_RPE** consistent 11.475% -> 0.000% (-11.475pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX12_ocular_surface_snRNA** consistent 35.997% -> 34.612% (-1.385pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **CX13_central_cornea** consistent 6.629% -> 4.592% (-2.037pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_GSE268630** consistent 71.705% -> 66.519% (-5.186pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_OA-D001** consistent 74.970% -> 66.089% (-8.881pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)
- **PRE_OA-D068** consistent 53.785% -> 37.047% (-16.738pp)  UNATTRIBUTED (missing: cluster, cause, row_or_panel)

## Overall, cell-weighted

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---:|---:|---:|---:|---:|
| consistent | 42.544 | 39.230 | -3.314 | 297 | 283 |
| related | 16.936 | 13.030 | -3.906 | 88 | 71 |
| inconsistent | 19.843 | 32.568 | +12.725 | 171 | 235 |
| mixed | 20.676 | 15.172 | -5.504 | 165 | 132 |

## Per dataset

| dataset | clusters | cells | before consistent % | after consistent % | delta pp |
|---|---:|---:|---:|---:|---:|
| CX04_cowan_periphery | 33 | 34702 | 54.239 | 13.14 | -41.099 |
| CX04_cowan_organoid | 15 | 43847 | 90.134 | 58.435 | -31.699 |
| PRE_OA-D068 | 20 | 63773 | 53.785 | 37.047 | -16.738 |
| CX02_adult_retina | 48 | 85452 | 72.376 | 57.278 | -15.098 |
| CX10_hiPSC_RPE | 25 | 54894 | 11.475 | 0.0 | -11.475 |
| CX04_cowan_fovea | 25 | 19753 | 67.772 | 57.758 | -10.014 |
| CX03_retina_multiome | 31 | 51591 | 36.842 | 27.695 | -9.147 |
| PRE_OA-D001 | 32 | 62649 | 74.97 | 66.089 | -8.881 |
| PRE_GSE268630 | 36 | 59276 | 71.705 | 66.519 | -5.186 |
| CX09_voigt_RPE_choroid | 16 | 3624 | 74.31 | 70.006 | -4.304 |
| CX13_central_cornea | 16 | 35890 | 6.629 | 4.592 | -2.037 |
| CX12_ocular_surface_snRNA | 21 | 37264 | 35.997 | 34.612 | -1.385 |
| CX01_retina_snRNA | 37 | 97015 | 70.11 | 69.238 | -0.872 |
| CX07_iPSC_organoid_POAG | 21 | 46275 | 6.788 | 6.788 | +0.000 |
| CX13_ciliary_body | 17 | 32282 | 21.495 | 21.495 | +0.000 |
| CX13_iris | 17 | 55990 | 18.646 | 18.646 | +0.000 |
| CX13_lens | 11 | 13538 | 0.0 | 0.0 | +0.000 |
| CX14_TM_ciliary_snRNA | 17 | 78110 | 46.839 | 46.839 | +0.000 |
| CX15_optic_nerve_all | 46 | 71997 | 44.403 | 44.403 | +0.000 |
| CX16_tabula_sapiens_eye | 36 | 31808 | 18.052 | 18.052 | +0.000 |
| CX17_mouse_retina_all | 36 | 71751 | 0.0 | 0.0 | +0.000 |
| PRE_OA-D004 | 21 | 81867 | 44.765 | 46.108 | +1.343 |
| CX13_TM_corneal_scleral | 29 | 51414 | 41.306 | 44.326 | +3.020 |
| CX08_RPE_choroid_snRNA | 18 | 70474 | 37.314 | 42.555 | +5.241 |
| PRE_GSE199013 | 38 | 42473 | 43.376 | 50.069 | +6.693 |
| CX08_RPE_choroid_scRNA | 20 | 73513 | 36.63 | 44.448 | +7.818 |
| PRE_OA-D002 | 19 | 69411 | 35.879 | 44.777 | +8.898 |
| CX11_posterior_eye_atlas | 20 | 54697 | 32.483 | 41.52 | +9.037 |

## Cells moved, by grade transition

| transition | clusters | cells |
|---|---:|---:|
| mixed->inconsistent | 31 | 79450 |
| consistent->inconsistent | 22 | 75632 |
| related->inconsistent | 12 | 41374 |
| related->consistent | 5 | 17035 |
| inconsistent->consistent | 1 | 6176 |
| mixed->consistent | 2 | 2855 |

## Clusters whose ranking moved (255 clusters / 636656 cells)

| volume | cluster | n_cells | tissue | before | after | grade |
|---|---|---:|---|---|---|---|
| CX02_adult_retina | 4 | 12902 | retina | Rod (1) | retinal rod cell (3) | consistent -> inconsistent |
| CX02_adult_retina | 2 | 11504 | retina | MG (1) | MG (1) | related -> related |
| PRE_OA-D068 | 8 | 11348 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX01_retina_snRNA | 11 | 9022 | retina | RGC (1) | RGC (1) | consistent -> consistent |
| CX04_cowan_organoid | 3 | 8557 | retina | Rod (2) | retinal rod cell (4) | consistent -> inconsistent |
| CX03_retina_multiome | 7 | 8308 | retina | None (None) | retinal rod cell (2) | mixed -> inconsistent |
| CX03_retina_multiome | 12 | 7918 | retina | None (None) | retinal rod cell (1) | mixed -> inconsistent |
| CX13_iris | 11 | 7817 | iris | trabecular meshwork cell (3) | trabecular meshwork cell (3) | inconsistent -> inconsistent |
| CX13_iris | 4 | 7697 | iris | None (None) | endothelial cell of vascular tree (1) | mixed -> inconsistent |
| CX08_RPE_choroid_snRNA | 16 | 7584 | rpe | Endo (1) | Endo (1) | inconsistent -> inconsistent |
| PRE_OA-D004 | 10 | 7296 | trabecular_meshwork | Endo (4) | endothelial cell (5) | related -> inconsistent |
| CX14_TM_ciliary_snRNA | 6 | 7215 | trabecular_meshwork | Endo (3) | endothelial cell (4) | related -> inconsistent |
| CX13_iris | 9 | 7148 | iris | SMC (2) | SMC (2) | inconsistent -> inconsistent |
| CX08_RPE_choroid_snRNA | 15 | 6987 | rpe | Endo (1) | Endo (1) | related -> related |
| PRE_OA-D004 | 15 | 6736 | trabecular_meshwork | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 7 | 6705 | trabecular_meshwork | pigmented ciliary epithelial cell (4) | pigmented ciliary epithelial cell (4) | related -> related |
| PRE_OA-D004 | 0 | 6579 | trabecular_meshwork | Pericyte (3) | Pericyte (3) | consistent -> consistent |
| PRE_OA-D068 | 4 | 6577 | retina | Rod (2) | retinal rod cell (3) | consistent -> inconsistent |
| PRE_OA-D004 | 11 | 6521 | trabecular_meshwork | Schwann (2) | Schwann (2) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 5 | 6501 | trabecular_meshwork | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 9 | 6433 | trabecular_meshwork | Mac_Tissue (2) | Mac_Tissue (2) | related -> related |
| CX14_TM_ciliary_snRNA | 0 | 6414 | trabecular_meshwork | Pericyte (1) | Pericyte (1) | consistent -> consistent |
| CX10_hiPSC_RPE | 0 | 6299 | rpe | RPE (2) | retinal pigment epithelial cell (3) | consistent -> inconsistent |
| CX11_posterior_eye_atlas | 16 | 6257 | optic_nerve | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| PRE_OA-D002 | 5 | 6176 | ocular_surface | APC_MHCII_high (2) | macrophage (3) | inconsistent -> consistent |
| CX04_cowan_periphery | 7 | 6085 | retina | Rod (2) | retinal rod cell (3) | consistent -> inconsistent |
| CX13_iris | 3 | 6003 | iris | Melanocyte (2) | Melanocyte (2) | consistent -> consistent |
| CX10_hiPSC_RPE | 3 | 5993 | rpe | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 12 | 5988 | trabecular_meshwork | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX08_RPE_choroid_scRNA | 2 | 5950 | rpe | Pericyte (3) | Pericyte (3) | consistent -> consistent |
| CX08_RPE_choroid_scRNA | 8 | 5747 | rpe | Mac_Tissue (3) | macrophage (6) | related -> consistent |
| PRE_OA-D001 | 3 | 5564 | retina | Rod (1) | retinal rod cell (3) | consistent -> inconsistent |
| CX08_RPE_choroid_scRNA | 3 | 5505 | rpe | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| PRE_OA-D004 | 9 | 5460 | trabecular_meshwork | APC_MHCII_high (3) | APC_MHCII_high (3) | inconsistent -> inconsistent |
| CX07_iPSC_organoid_POAG | 8 | 5369 | retina | Melanocyte (1) | Melanocyte (1) | inconsistent -> inconsistent |
| CX08_RPE_choroid_scRNA | 17 | 5334 | rpe | Endo (2) | endothelial cell (3) | inconsistent -> inconsistent |
| PRE_OA-D004 | 8 | 5310 | trabecular_meshwork | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX08_RPE_choroid_scRNA | 15 | 5291 | rpe | retina_interneuron::BC (2) | retina_interneuron::BC (2) | inconsistent -> inconsistent |
| CX08_RPE_choroid_scRNA | 7 | 5261 | rpe | Endo (1) | Endo (1) | related -> related |
| PRE_OA-D068 | 6 | 5191 | retina | AC (1) | AC (1) | consistent -> consistent |
| CX04_cowan_organoid | 12 | 5187 | retina | MG (1) | MG (1) | consistent -> consistent |
| PRE_OA-D004 | 14 | 5144 | trabecular_meshwork | non-pigmented ciliary epithelial cell (3) | capillary endothelial cell (2) | related -> inconsistent |
| PRE_OA-D068 | 7 | 5021 | retina | None (None) | retinal pigment epithelial cell (1) | mixed -> inconsistent |
| PRE_OA-D002 | 8 | 4981 | ocular_surface | Melanocyte (5) | Melanocyte (5) | consistent -> consistent |
| CX08_RPE_choroid_scRNA | 9 | 4974 | rpe | Mono_Classical (3) | Mono_Classical (3) | consistent -> consistent |
| CX11_posterior_eye_atlas | 6 | 4943 | optic_nerve | Mac_Tissue (4) | macrophage (5) | related -> consistent |
| PRE_OA-D002 | 7 | 4940 | ocular_surface | Endo (1) | endothelial cell (2) | related -> inconsistent |
| CX13_central_cornea | 10 | 4802 | ocular_surface | corneal endothelial cell (4) | corneal endothelial cell (4) | related -> related |
| CX03_retina_multiome | 9 | 4746 | retina | None (None) | retinal rod cell (2) | mixed -> inconsistent |
| CX08_RPE_choroid_snRNA | 4 | 4743 | rpe | SMC (2) | SMC (2) | inconsistent -> inconsistent |
| CX03_retina_multiome | 11 | 4719 | retina | Rod (1) | retinal rod cell (4) | consistent -> inconsistent |
| CX04_cowan_organoid | 4 | 4558 | retina | Rod (3) | retinal rod cell (4) | consistent -> inconsistent |
| PRE_OA-D001 | 2 | 4488 | retina | MG (2) | MG (2) | consistent -> consistent |
| CX04_cowan_periphery | 3 | 4416 | retina | None (None) | macrophage (1) | mixed -> inconsistent |
| PRE_OA-D068 | 5 | 4397 | retina | Melanocyte (1) | Melanocyte (1) | inconsistent -> inconsistent |
| PRE_OA-D002 | 9 | 4363 | ocular_surface | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| PRE_OA-D068 | 10 | 4194 | retina | retina_interneuron::HC (2) | retina_interneuron::HC (2) | inconsistent -> inconsistent |
| PRE_OA-D002 | 6 | 4129 | ocular_surface | Endo (5) | endothelial cell (6) | related -> inconsistent |
| PRE_OA-D068 | 19 | 4097 | retina | Rod (2) | retinal rod cell (4) | consistent -> inconsistent |
| PRE_GSE268630 | 3 | 3998 | retina | Rod (1) | Rod (1) | consistent -> consistent |
| PRE_GSE268630 | 5 | 3997 | retina | None (None) | retinal rod cell (1) | mixed -> inconsistent |
| CX15_optic_nerve_all | 21 | 3933 | optic_nerve | Endo (2) | Endo (2) | related -> related |
| PRE_OA-D002 | 3 | 3921 | ocular_surface | Endo (2) | Endo (2) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 8 | 3902 | retina | Rod (3) | retinal rod cell (6) | consistent -> inconsistent |
| CX04_cowan_fovea | 16 | 3897 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX08_RPE_choroid_snRNA | 3 | 3889 | rpe | RGC (1) | endothelial cell of artery (2) | inconsistent -> inconsistent |
| CX13_iris | 5 | 3851 | iris | Melanocyte (1) | Melanocyte (1) | consistent -> consistent |
| CX13_ciliary_body | 1 | 3844 | ciliary_body | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX15_optic_nerve_all | 12 | 3810 | optic_nerve | RGC (1) | endothelial cell of artery (2) | inconsistent -> inconsistent |
| CX03_retina_multiome | 8 | 3799 | retina | None (None) | retinal rod cell (2) | mixed -> inconsistent |
| CX03_retina_multiome | 5 | 3781 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX02_adult_retina | 3 | 3763 | retina | None (None) | retinal rod cell (2) | mixed -> inconsistent |
| CX15_optic_nerve_all | 20 | 3722 | optic_nerve | Endo (3) | endothelial cell (4) | related -> inconsistent |
| CX08_RPE_choroid_snRNA | 6 | 3715 | rpe | RPE (1) | RPE (1) | consistent -> consistent |
| CX13_iris | 6 | 3703 | iris | pDC (1) | pDC (1) | inconsistent -> inconsistent |
| CX08_RPE_choroid_snRNA | 11 | 3693 | rpe | Mac_Tissue (4) | macrophage (5) | related -> consistent |
| CX16_tabula_sapiens_eye | 12 | 3692 | retina | Mono_Classical (2) | Mono_Classical (2) | inconsistent -> inconsistent |
| PRE_OA-D004 | 13 | 3615 | trabecular_meshwork | MG (2) | MG (2) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 0 | 3609 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| CX13_ciliary_body | 5 | 3464 | ciliary_body | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX04_cowan_organoid | 9 | 3458 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX08_RPE_choroid_snRNA | 14 | 3258 | rpe | Endo (1) | Endo (1) | related -> related |
| CX01_retina_snRNA | 9 | 3234 | retina | MG (1) | MG (1) | consistent -> consistent |
| CX01_retina_snRNA | 13 | 3228 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX01_retina_snRNA | 27 | 3223 | retina | None (None) | retinal rod cell (2) | mixed -> inconsistent |
| CX01_retina_snRNA | 34 | 3188 | retina | Astro (1) | Astro (1) | inconsistent -> inconsistent |
| CX07_iPSC_organoid_POAG | 3 | 3141 | retina | RPE (1) | RPE (1) | consistent -> consistent |
| PRE_GSE268630 | 24 | 3102 | retina | retina_interneuron::HC (4) | retina_interneuron::HC (4) | consistent -> consistent |
| CX10_hiPSC_RPE | 8 | 3091 | rpe | None (None) | vein endothelial cell (1) | mixed -> inconsistent |
| PRE_GSE268630 | 14 | 3074 | retina | RGC (1) | blood vessel endothelial cell (2) | consistent -> inconsistent |
| PRE_OA-D001 | 25 | 3035 | retina | APC_MHCII_high (2) | macrophage (3) | inconsistent -> inconsistent |
| PRE_GSE199013 | 20 | 3033 | ocular_surface | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX13_lens | 6 | 2964 | lens | retina_interneuron::AC (1) | retina_interneuron::AC (1) | inconsistent -> inconsistent |
| PRE_GSE268630 | 12 | 2899 | retina | RGC (2) | RGC (2) | consistent -> consistent |
| PRE_GSE268630 | 21 | 2886 | retina | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 15 | 2868 | optic_nerve | Endo (2) | endothelial cell (4) | related -> inconsistent |
| PRE_GSE199013 | 21 | 2843 | ocular_surface | None (None) | macrophage (1) | mixed -> consistent |
| PRE_OA-D004 | 1 | 2815 | trabecular_meshwork | APC_MHCII_high (3) | APC_MHCII_high (3) | inconsistent -> inconsistent |
| CX10_hiPSC_RPE | 4 | 2690 | rpe | None (None) | endothelial cell (1) | mixed -> inconsistent |
| CX03_retina_multiome | 10 | 2625 | retina | cDC1 (1) | retinal rod cell (3) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 14 | 2502 | ocular_surface | Endo (2) | Endo (2) | related -> related |
| CX08_RPE_choroid_scRNA | 10 | 2476 | rpe | Endo (3) | blood vessel endothelial cell (4) | related -> inconsistent |
| CX13_lens | 7 | 2385 | lens | None (None) | capillary endothelial cell (1) | mixed -> inconsistent |
| PRE_OA-D001 | 23 | 2349 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| PRE_GSE268630 | 1 | 2331 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| PRE_OA-D001 | 10 | 2316 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX10_hiPSC_RPE | 2 | 2289 | rpe | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 18 | 2276 | trabecular_meshwork | Endo (2) | Endo (2) | related -> related |
| CX13_TM_corneal_scleral | 1 | 2268 | trabecular_meshwork | progenitor cell (6) | progenitor cell (6) | consistent -> consistent |
| CX11_posterior_eye_atlas | 13 | 2260 | optic_nerve | RGC (1) | endothelial cell of artery (2) | inconsistent -> inconsistent |
| PRE_GSE268630 | 20 | 2192 | retina | None (None) | endothelial cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 4 | 2107 | retina | MG (1) | macrophage (2) | consistent -> inconsistent |
| CX11_posterior_eye_atlas | 19 | 2076 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 10 | 2043 | optic_nerve | Endo (2) | Endo (2) | related -> related |
| CX15_optic_nerve_all | 39 | 1994 | optic_nerve | MG (1) | retinal pigment epithelial cell (3) | inconsistent -> inconsistent |
| CX03_retina_multiome | 1 | 1979 | retina | None (None) | macrophage (1) | mixed -> inconsistent |
| CX04_cowan_organoid | 2 | 1952 | retina | AC (1) | AC (1) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 15 | 1922 | optic_nerve | None (None) | retinal rod cell (3) | mixed -> inconsistent |
| CX04_cowan_fovea | 0 | 1894 | retina | Rod (3) | retinal rod cell (5) | consistent -> inconsistent |
| CX15_optic_nerve_all | 23 | 1884 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 40 | 1859 | optic_nerve | retina_interneuron::HC (1) | retina_interneuron::HC (1) | inconsistent -> inconsistent |
| PRE_GSE268630 | 6 | 1839 | retina | retina_interneuron::AC (1) | retina_interneuron::AC (1) | inconsistent -> inconsistent |
| CX13_iris | 2 | 1790 | iris | None (None) | retinal rod cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 9 | 1784 | retina | Rod (2) | retinal rod cell (5) | consistent -> inconsistent |
| CX07_iPSC_organoid_POAG | 10 | 1767 | retina | None (None) | retinal pigment epithelial cell (1) | mixed -> inconsistent |
| CX13_ciliary_body | 4 | 1766 | ciliary_body | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| PRE_GSE268630 | 13 | 1738 | retina | RGC (2) | RGC (2) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 19 | 1671 | retina | Endo (3) | endothelial cell (4) | inconsistent -> inconsistent |
| CX07_iPSC_organoid_POAG | 9 | 1659 | retina | AC (1) | retinal pigment epithelial cell (2) | inconsistent -> inconsistent |
| CX07_iPSC_organoid_POAG | 2 | 1609 | retina | None (None) | macrophage (1) | mixed -> inconsistent |
| CX13_TM_corneal_scleral | 24 | 1553 | trabecular_meshwork | Mac_Tissue (1) | macrophage (2) | related -> consistent |
| CX04_cowan_periphery | 28 | 1535 | retina | None (None) | capillary endothelial cell (1) | mixed -> inconsistent |
| CX02_adult_retina | 14 | 1526 | retina | Endo (1) | Endo (1) | inconsistent -> inconsistent |
| CX13_central_cornea | 4 | 1461 | ocular_surface | corneal epithelial cell (2) | capillary endothelial cell (1) | related -> inconsistent |
| CX13_ciliary_body | 13 | 1457 | ciliary_body | Astro (1) | Astro (1) | inconsistent -> inconsistent |
| CX04_cowan_organoid | 1 | 1435 | retina | None (None) | retinal pigment epithelial cell (1) | mixed -> inconsistent |
| CX13_TM_corneal_scleral | 3 | 1430 | trabecular_meshwork | conjunctival epithelial cell (3) | conjunctival epithelial cell (3) | inconsistent -> inconsistent |
| PRE_GSE268630 | 4 | 1404 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| PRE_OA-D004 | 7 | 1369 | trabecular_meshwork | SMC (1) | SMC (1) | inconsistent -> inconsistent |
| PRE_GSE199013 | 23 | 1357 | ocular_surface | Endo (3) | endothelial cell (4) | related -> inconsistent |
| CX16_tabula_sapiens_eye | 3 | 1341 | retina | Microglia (3) | Microglia (3) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 2 | 1333 | ocular_surface | Mac_Tissue (1) | Mac_Tissue (1) | inconsistent -> inconsistent |
| CX01_retina_snRNA | 6 | 1306 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX12_ocular_surface_snRNA | 8 | 1263 | ocular_surface | Limbus_Sclera_fibroblast_C1 (2) | Limbus_Sclera_fibroblast_C1 (2) | consistent -> consistent |
| CX13_TM_corneal_scleral | 14 | 1261 | trabecular_meshwork | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 6 | 1236 | retina | APC_MHCII_high (4) | APC_MHCII_high (4) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 15 | 1227 | retina | Mono_Classical (1) | Mono_Classical (1) | inconsistent -> inconsistent |
| CX13_ciliary_body | 10 | 1208 | ciliary_body | Melanocyte (2) | Melanocyte (2) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 28 | 1208 | retina | cDC1 (1) | cDC1 (1) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 17 | 1196 | optic_nerve | Endo (1) | Endo (1) | related -> related |
| CX07_iPSC_organoid_POAG | 14 | 1189 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 8 | 1186 | trabecular_meshwork | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 16 | 1175 | retina | Mono_Classical (1) | Mono_Classical (1) | inconsistent -> inconsistent |
| PRE_OA-D004 | 2 | 1158 | trabecular_meshwork | Pericyte (1) | Pericyte (1) | inconsistent -> inconsistent |
| CX04_cowan_organoid | 11 | 1142 | retina | MG (1) | MG (1) | consistent -> consistent |
| PRE_OA-D004 | 17 | 1099 | trabecular_meshwork | Mac_Tissue (3) | macrophage (6) | related -> consistent |
| PRE_OA-D001 | 13 | 1053 | retina | pDC (1) | pDC (1) | inconsistent -> inconsistent |
| PRE_GSE268630 | 8 | 1045 | retina | Astro (1) | Astro (1) | inconsistent -> inconsistent |
| CX13_central_cornea | 3 | 1006 | ocular_surface | Keratocytes (1) | Keratocytes (1) | inconsistent -> inconsistent |
| PRE_GSE199013 | 0 | 975 | ocular_surface | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX10_hiPSC_RPE | 18 | 965 | rpe | Myofibroblast (2) | Myofibroblast (2) | inconsistent -> inconsistent |
| PRE_OA-D001 | 30 | 929 | retina | RPE (2) | RPE (2) | consistent -> consistent |
| CX04_cowan_periphery | 11 | 873 | retina | None (None) | retinal blood vessel endothelial cell (1) | mixed -> inconsistent |
| CX10_hiPSC_RPE | 9 | 841 | rpe | None (None) | vein endothelial cell (1) | mixed -> inconsistent |
| CX12_ocular_surface_snRNA | 12 | 819 | ocular_surface | Endo (1) | Endo (1) | related -> related |
| CX01_retina_snRNA | 35 | 811 | retina | RPE (2) | retinal pigment epithelial cell (3) | consistent -> inconsistent |
| CX04_cowan_organoid | 5 | 784 | retina | Rod (2) | retinal rod cell (3) | consistent -> inconsistent |
| PRE_OA-D001 | 31 | 767 | retina | RPE (1) | RPE (1) | consistent -> consistent |
| PRE_GSE268630 | 25 | 755 | retina | retina_interneuron::AC (3) | retina_interneuron::AC (3) | consistent -> consistent |
| PRE_GSE199013 | 6 | 745 | ocular_surface | Limbus_Sclera_fibroblast_C1 (2) | Limbus_Sclera_fibroblast_C1 (2) | consistent -> consistent |
| CX13_central_cornea | 13 | 743 | ocular_surface | progenitor cell (2) | macrophage (1) | consistent -> inconsistent |
| CX13_TM_corneal_scleral | 23 | 740 | trabecular_meshwork | Endo (1) | Endo (1) | related -> related |
| PRE_OA-D068 | 12 | 698 | retina | Astro (2) | Astro (2) | inconsistent -> inconsistent |
| PRE_OA-D068 | 11 | 695 | retina | MG (1) | macrophage (2) | inconsistent -> inconsistent |
| CX03_retina_multiome | 27 | 693 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| PRE_GSE199013 | 36 | 690 | ocular_surface | Endo (1) | Endo (1) | related -> related |
| PRE_OA-D002 | 17 | 685 | ocular_surface | oligodendrocyte (3) | oligodendrocyte (3) | inconsistent -> inconsistent |
| CX04_cowan_organoid | 10 | 637 | retina | None (None) | macrophage (1) | mixed -> inconsistent |
| CX07_iPSC_organoid_POAG | 7 | 616 | retina | None (None) | capillary endothelial cell (1) | mixed -> inconsistent |
| CX04_cowan_periphery | 24 | 592 | retina | None (None) | retinal pigment epithelial cell (1) | mixed -> inconsistent |
| PRE_GSE199013 | 17 | 588 | ocular_surface | Pericyte (1) | Pericyte (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 7 | 582 | retina | Rod (3) | retinal rod cell (5) | related -> inconsistent |
| CX01_retina_snRNA | 2 | 569 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX12_ocular_surface_snRNA | 16 | 516 | ocular_surface | Pericyte (1) | endothelial cell of artery (2) | consistent -> inconsistent |
| PRE_GSE268630 | 35 | 515 | retina | retina_interneuron::HC (3) | retina_interneuron::HC (3) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 2 | 513 | rpe | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 17 | 511 | retina | Myofibroblast (5) | Myofibroblast (5) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 20 | 503 | trabecular_meshwork | Pericyte (2) | Pericyte (2) | consistent -> consistent |
| CX15_optic_nerve_all | 30 | 496 | optic_nerve | retina_interneuron::BC (1) | retina_interneuron::BC (1) | inconsistent -> inconsistent |
| PRE_OA-D001 | 8 | 493 | retina | Rod (3) | retinal rod cell (6) | inconsistent -> inconsistent |
| CX02_adult_retina | 46 | 485 | retina | retina_interneuron::AC (2) | retina_interneuron::AC (2) | consistent -> consistent |
| CX03_retina_multiome | 0 | 484 | retina | RGC (2) | RGC (2) | consistent -> consistent |
| CX04_cowan_periphery | 5 | 480 | retina | APC_MHCII_high (5) | APC_MHCII_high (5) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 3 | 470 | rpe | Schwann (1) | Schwann (1) | consistent -> consistent |
| PRE_OA-D068 | 16 | 428 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 10 | 384 | retina | Rod (2) | retinal rod cell (3) | consistent -> inconsistent |
| CX13_iris | 8 | 376 | iris | SMC (1) | SMC (1) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 21 | 372 | trabecular_meshwork | Endo (1) | Endo (1) | related -> related |
| CX07_iPSC_organoid_POAG | 17 | 369 | retina | RPE (1) | RPE (1) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 13 | 353 | rpe | Fibroblast (1) | Fibroblast (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 2 | 331 | retina | Melanocyte (6) | Melanocyte (6) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 1 | 313 | retina | Mono_Classical (1) | Mono_Classical (1) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 20 | 312 | ocular_surface | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| PRE_OA-D001 | 1 | 308 | retina | MG (3) | MG (3) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 33 | 284 | retina | Mono_Classical (2) | Mono_Classical (2) | inconsistent -> inconsistent |
| CX04_cowan_fovea | 20 | 280 | retina | Pericyte (3) | Pericyte (3) | inconsistent -> inconsistent |
| CX08_RPE_choroid_scRNA | 5 | 274 | rpe | MG (2) | MG (2) | inconsistent -> inconsistent |
| PRE_GSE268630 | 29 | 273 | retina | None (None) | retinal rod cell (2) | mixed -> inconsistent |
| CX16_tabula_sapiens_eye | 21 | 272 | retina | retina_interneuron::AC (1) | retina_interneuron::AC (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 30 | 205 | retina | Endo (2) | Endo (2) | related -> related |
| CX04_cowan_periphery | 1 | 186 | retina | RPE (3) | RPE (3) | consistent -> consistent |
| CX13_ciliary_body | 15 | 184 | ciliary_body | Endo (2) | endothelial cell (3) | related -> inconsistent |
| CX13_TM_corneal_scleral | 25 | 178 | trabecular_meshwork | Fibroblast (1) | Fibroblast (1) | consistent -> consistent |
| CX04_cowan_fovea | 19 | 173 | retina | APC_MHCII_high (4) | macrophage (5) | inconsistent -> inconsistent |
| CX04_cowan_organoid | 14 | 170 | retina | None (None) | endothelial cell of artery (1) | mixed -> inconsistent |
| CX04_cowan_fovea | 22 | 168 | retina | APC_MHCII_high (2) | APC_MHCII_high (2) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 27 | 168 | retina | Astro (1) | Astro (1) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 7 | 168 | rpe | Endo (3) | Endo (3) | related -> related |
| CX03_retina_multiome | 20 | 159 | retina | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX04_cowan_fovea | 24 | 159 | retina | APC_MHCII_high (1) | APC_MHCII_high (1) | inconsistent -> inconsistent |
| CX04_cowan_periphery | 0 | 157 | retina | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| PRE_OA-D004 | 19 | 157 | trabecular_meshwork | trabecular meshwork cell (4) | trabecular meshwork cell (4) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 0 | 156 | rpe | Microglia (3) | Microglia (3) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 12 | 156 | rpe | RPE (2) | retinal pigment epithelial cell (4) | consistent -> inconsistent |
| CX02_adult_retina | 23 | 139 | retina | APC_MHCII_high (2) | APC_MHCII_high (2) | inconsistent -> inconsistent |
| CX04_cowan_fovea | 17 | 138 | retina | Astro (1) | Astro (1) | consistent -> consistent |
| CX04_cowan_organoid | 0 | 132 | retina | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent |
| PRE_OA-D068 | 13 | 126 | retina | AC (1) | AC (1) | consistent -> consistent |
| CX04_cowan_periphery | 23 | 120 | retina | retina_interneuron::BC (2) | retina_interneuron::BC (2) | consistent -> consistent |
| CX03_retina_multiome | 15 | 118 | retina | APC_MHCII_high (1) | APC_MHCII_high (1) | inconsistent -> inconsistent |
| CX01_retina_snRNA | 30 | 109 | retina | RGC (1) | RGC (1) | consistent -> consistent |
| CX13_ciliary_body | 16 | 102 | ciliary_body | Pericyte (1) | Pericyte (1) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 9 | 96 | rpe | APC_MHCII_high (4) | APC_MHCII_high (4) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 9 | 96 | retina | MG (1) | retinal pigment epithelial cell (2) | inconsistent -> inconsistent |
| CX03_retina_multiome | 24 | 93 | retina | AC (1) | AC (1) | consistent -> consistent |
| CX04_cowan_periphery | 29 | 88 | retina | Pericyte (3) | Pericyte (3) | consistent -> consistent |
| CX13_lens | 10 | 88 | lens | None (None) | macrophage (2) | mixed -> inconsistent |
| CX09_voigt_RPE_choroid | 10 | 86 | rpe | Pericyte (1) | Pericyte (1) | inconsistent -> inconsistent |
| CX04_cowan_fovea | 18 | 84 | retina | RPE (3) | retinal pigment epithelial cell (4) | consistent -> inconsistent |
| CX02_adult_retina | 47 | 77 | retina | retina_v6::RPE (3) | retina_v6::RPE (3) | inconsistent -> inconsistent |
| PRE_GSE199013 | 2 | 60 | ocular_surface | pigmented ciliary epithelial cell (4) | pigmented ciliary epithelial cell (4) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 45 | 55 | optic_nerve | None (None) | retinal rod cell (1) | mixed -> inconsistent |
| PRE_GSE199013 | 1 | 54 | ocular_surface | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 15 | 47 | rpe | Granulocyte (1) | macrophage (2) | inconsistent -> inconsistent |
| CX01_retina_snRNA | 36 | 35 | retina | RPE (2) | retinal pigment epithelial cell (3) | consistent -> inconsistent |
| PRE_GSE199013 | 15 | 34 | ocular_surface | non-pigmented ciliary epithelial cell (3) | non-pigmented ciliary epithelial cell (3) | related -> related |
| CX09_voigt_RPE_choroid | 14 | 30 | rpe | MG (1) | MG (1) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 34 | 26 | retina | Mac_Tissue (2) | Mac_Tissue (2) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 25 | 22 | optic_nerve | None (None) | retinal rod cell (1) | mixed -> inconsistent |
| CX16_tabula_sapiens_eye | 13 | 19 | retina | Mono_Classical (2) | macrophage (4) | inconsistent -> inconsistent |
| CX08_RPE_choroid_scRNA | 16 | 17 | rpe | Melanocyte (2) | Melanocyte (2) | inconsistent -> inconsistent |
| PRE_GSE199013 | 18 | 15 | ocular_surface | pigmented ciliary epithelial cell (2) | retinal rod cell (1) | inconsistent -> inconsistent |
| CX08_RPE_choroid_scRNA | 19 | 13 | rpe | pDC (1) | pDC (1) | inconsistent -> inconsistent |
| CX13_central_cornea | 15 | 12 | ocular_surface | None (None) | endothelial cell (1) | mixed -> consistent |
| CX16_tabula_sapiens_eye | 24 | 11 | retina | Mono_Classical (1) | macrophage (2) | inconsistent -> inconsistent |

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
