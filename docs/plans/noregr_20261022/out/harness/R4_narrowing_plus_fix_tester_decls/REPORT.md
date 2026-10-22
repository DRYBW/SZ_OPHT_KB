# Regression-harness report -- R4 narrowing + carrier fix, the tester's final declarations

Declared change: the narrowing with the carrier available

Before arm: `{"env": {"EYEKB_TISSUE_SCOPE": "0"}}`
After arm:  `{"env": {"EYEKB_TISSUE_SCOPE": "1"}, "inject": ["onfibro_v13"]}`

Recorded set: 721 clusters / 1495330 cells / 28 volumes

## Ruling: **PASS**

a change may not be reported as complete while any dataset's cell-weighted consistent share has fallen, unless the drop is attributed to a named cluster + named cause + named row/panel

## Overall, cell-weighted

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---:|---:|---:|---:|---:|
| consistent | 40.980 | 42.679 | +1.699 | 291 | 299 |
| related | 16.785 | 17.232 | +0.447 | 84 | 89 |
| inconsistent | 21.774 | 18.955 | -2.819 | 193 | 162 |
| mixed | 20.461 | 21.134 | +0.673 | 153 | 171 |

## Per dataset

| dataset | clusters | cells | before consistent % | after consistent % | delta pp |
|---|---:|---:|---:|---:|---:|
| CX01_retina_snRNA | 37 | 97015 | 70.11 | 70.11 | +0.000 |
| CX02_adult_retina | 48 | 85452 | 72.376 | 72.376 | +0.000 |
| CX03_retina_multiome | 31 | 51591 | 36.842 | 36.842 | +0.000 |
| CX04_cowan_fovea | 25 | 19753 | 67.772 | 67.772 | +0.000 |
| CX04_cowan_organoid | 15 | 43847 | 90.134 | 90.134 | +0.000 |
| CX04_cowan_periphery | 33 | 34702 | 54.239 | 54.239 | +0.000 |
| CX07_iPSC_organoid_POAG | 21 | 46275 | 6.788 | 6.788 | +0.000 |
| CX08_RPE_choroid_scRNA | 20 | 73513 | 36.63 | 36.63 | +0.000 |
| CX09_voigt_RPE_choroid | 16 | 3624 | 74.31 | 74.31 | +0.000 |
| CX10_hiPSC_RPE | 25 | 54894 | 11.475 | 11.475 | +0.000 |
| CX13_ciliary_body | 17 | 32282 | 21.495 | 21.495 | +0.000 |
| CX13_iris | 17 | 55990 | 18.646 | 18.646 | +0.000 |
| CX13_lens | 11 | 13538 | 0.0 | 0.0 | +0.000 |
| CX15_optic_nerve_all | 46 | 71997 | 44.403 | 44.403 | +0.000 |
| CX16_tabula_sapiens_eye | 36 | 31808 | 18.112 | 18.112 | +0.000 |
| CX17_mouse_retina_all | 36 | 71751 | 0.0 | 0.0 | +0.000 |
| PRE_GSE268630 | 36 | 59276 | 71.705 | 71.705 | +0.000 |
| PRE_OA-D001 | 32 | 62649 | 74.97 | 74.97 | +0.000 |
| PRE_OA-D002 | 19 | 69411 | 35.879 | 35.879 | +0.000 |
| PRE_OA-D004 | 21 | 81867 | 44.765 | 44.765 | +0.000 |
| PRE_OA-D068 | 20 | 63773 | 53.785 | 53.785 | +0.000 |
| CX12_ocular_surface_snRNA | 21 | 37264 | 34.612 | 35.997 | +1.385 |
| CX13_central_cornea | 16 | 35890 | 5.116 | 6.629 | +1.513 |
| CX13_TM_corneal_scleral | 29 | 51414 | 39.036 | 41.306 | +2.270 |
| CX08_RPE_choroid_snRNA | 18 | 70474 | 31.834 | 37.314 | +5.480 |
| PRE_GSE199013 | 38 | 42473 | 36.859 | 43.376 | +6.517 |
| CX14_TM_ciliary_snRNA | 17 | 78110 | 34.716 | 46.839 | +12.123 |
| CX11_posterior_eye_atlas | 20 | 54697 | 23.179 | 36.134 | +12.955 |

## Cells moved, by grade transition

| transition | clusters | cells |
|---|---:|---:|
| inconsistent->mixed | 20 | 27900 |
| mixed->consistent | 3 | 18420 |
| inconsistent->consistent | 6 | 8421 |
| inconsistent->related | 6 | 7260 |
| consistent->inconsistent | 1 | 1430 |
| related->mixed | 1 | 582 |

## Clusters whose ranking moved (126 clusters / 258425 cells)

| volume | cluster | n_cells | tissue | before | after | grade |
|---|---|---:|---|---|---|---|
| PRE_OA-D004 | 3 | 10201 | trabecular_meshwork | Fibroblast (2) | Fibroblast (2) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 1 | 9469 | trabecular_meshwork | None (None) | onfibro_v13::Fibroblast (1) | mixed -> consistent |
| CX13_TM_corneal_scleral | 15 | 7529 | trabecular_meshwork | ciliary muscle cell (3) | ciliary muscle cell (3) | related -> related |
| CX14_TM_ciliary_snRNA | 6 | 7215 | trabecular_meshwork | Endo (3) | Endo (3) | related -> related |
| CX14_TM_ciliary_snRNA | 2 | 7111 | trabecular_meshwork | ciliary muscle cell (3) | ciliary muscle cell (3) | related -> related |
| CX14_TM_ciliary_snRNA | 15 | 6588 | trabecular_meshwork | Schwann (2) | Schwann (2) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 5 | 6501 | trabecular_meshwork | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX13_TM_corneal_scleral | 16 | 6461 | trabecular_meshwork | SMC (1) | SMC (1) | inconsistent -> inconsistent |
| CX10_hiPSC_RPE | 0 | 6299 | rpe | RPE (2) | RPE (2) | consistent -> consistent |
| CX11_posterior_eye_atlas | 16 | 6257 | ocular_surface | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX13_TM_corneal_scleral | 12 | 5988 | trabecular_meshwork | Fibroblast (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX08_RPE_choroid_scRNA | 0 | 5670 | rpe | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 4 | 5657 | ocular_surface | Fibroblast (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| PRE_OA-D004 | 14 | 5144 | trabecular_meshwork | non-pigmented ciliary epithelial cell (3) | non-pigmented ciliary epithelial cell (3) | related -> related |
| CX11_posterior_eye_atlas | 12 | 5089 | ocular_surface | None (None) | onfibro_v13::Fibroblast (1) | mixed -> consistent |
| PRE_OA-D002 | 8 | 4981 | ocular_surface | Melanocyte (5) | Melanocyte (5) | consistent -> consistent |
| CX13_central_cornea | 10 | 4802 | ocular_surface | corneal endothelial cell (4) | corneal endothelial cell (4) | related -> related |
| PRE_OA-D002 | 12 | 4512 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| PRE_OA-D002 | 9 | 4363 | ocular_surface | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 13 | 4258 | trabecular_meshwork | Schwann (2) | Schwann (2) | consistent -> consistent |
| CX13_ciliary_body | 12 | 4062 | ciliary_body | ciliary muscle cell (3) | ciliary muscle cell (3) | related -> related |
| CX10_hiPSC_RPE | 17 | 4008 | rpe | Fibroblast (5) | Fibroblast (5) | inconsistent -> inconsistent |
| PRE_OA-D002 | 3 | 3921 | ocular_surface | Endo (2) | Endo (2) | inconsistent -> inconsistent |
| CX08_RPE_choroid_snRNA | 1 | 3862 | rpe | None (None) | onfibro_v13::Fibroblast (1) | mixed -> consistent |
| CX15_optic_nerve_all | 12 | 3810 | optic_nerve | RGC (1) | RGC (1) | inconsistent -> inconsistent |
| CX13_ciliary_body | 0 | 3800 | ciliary_body | retina_interneuron::HC (1) | None (None) | inconsistent -> mixed |
| CX11_posterior_eye_atlas | 0 | 3609 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| CX13_ciliary_body | 5 | 3464 | ciliary_body | Fibroblast (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| PRE_OA-D002 | 11 | 3447 | ocular_surface | Fibroblast (4) | Fibroblast (4) | consistent -> consistent |
| CX10_hiPSC_RPE | 7 | 3323 | rpe | Fibroblast (2) | Fibroblast (2) | inconsistent -> inconsistent |
| PRE_GSE199013 | 8 | 3115 | ocular_surface | retina_interneuron::AC (1) | ciliary muscle cell (2) | inconsistent -> related |
| PRE_GSE199013 | 11 | 3052 | ocular_surface | Schwann (2) | Schwann (2) | consistent -> consistent |
| PRE_GSE199013 | 20 | 3033 | ocular_surface | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| PRE_GSE199013 | 21 | 2843 | ocular_surface | Astro (1) | None (None) | inconsistent -> mixed |
| PRE_GSE199013 | 4 | 2768 | ocular_surface | Pericyte (1) | onfibro_v13::Fibroblast (2) | inconsistent -> consistent |
| PRE_OA-D002 | 10 | 2732 | ocular_surface | Fibroblast (3) | Fibroblast (3) | consistent -> consistent |
| CX11_posterior_eye_atlas | 1 | 2663 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| CX10_hiPSC_RPE | 16 | 2632 | rpe | Myofibroblast (3) | Myofibroblast (3) | inconsistent -> inconsistent |
| CX14_TM_ciliary_snRNA | 11 | 2497 | trabecular_meshwork | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| CX16_tabula_sapiens_eye | 0 | 2426 | ocular_surface | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 2 | 2387 | ocular_surface | retina_interneuron::AC (1) | None (None) | inconsistent -> mixed |
| CX13_ciliary_body | 3 | 2361 | ciliary_body | pigmented ciliary epithelial cell (5) | pigmented ciliary epithelial cell (5) | related -> related |
| CX11_posterior_eye_atlas | 13 | 2260 | ocular_surface | RGC (1) | Pericyte (1) | inconsistent -> inconsistent |
| PRE_OA-D004 | 18 | 2180 | trabecular_meshwork | retina_interneuron::BC (2) | mast cell (3) | inconsistent -> related |
| CX11_posterior_eye_atlas | 19 | 2076 | ocular_surface | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX11_posterior_eye_atlas | 11 | 1997 | ocular_surface | retina_interneuron::AC (1) | Schwann (1) | inconsistent -> consistent |
| CX13_ciliary_body | 6 | 1865 | ciliary_body | Schwann (2) | Schwann (2) | consistent -> consistent |
| PRE_GSE199013 | 29 | 1864 | ocular_surface | corneal endothelial cell (3) | corneal endothelial cell (3) | related -> related |
| CX12_ocular_surface_snRNA | 18 | 1851 | ocular_surface | ciliary muscle cell (3) | ciliary muscle cell (3) | inconsistent -> inconsistent |
| CX15_optic_nerve_all | 31 | 1822 | optic_nerve | Limbus_Sclera_fibroblast_C1 (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX13_ciliary_body | 4 | 1766 | ciliary_body | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX13_TM_corneal_scleral | 9 | 1712 | trabecular_meshwork | Melanocyte (2) | Melanocyte (2) | consistent -> consistent |
| CX12_ocular_surface_snRNA | 13 | 1685 | ocular_surface | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX13_TM_corneal_scleral | 24 | 1553 | trabecular_meshwork | retina_interneuron::AC (2) | Mac_Tissue (1) | inconsistent -> related |
| CX13_TM_corneal_scleral | 5 | 1452 | trabecular_meshwork | Granulocyte (1) | Granulocyte (1) | consistent -> consistent |
| CX13_TM_corneal_scleral | 3 | 1430 | trabecular_meshwork | Conj_epithelium_basal (2) | conjunctival epithelial cell (3) | consistent -> inconsistent |
| CX13_TM_corneal_scleral | 2 | 1411 | trabecular_meshwork | Conj_epithelium_basal (1) | conjunctival epithelial cell (2) | inconsistent -> consistent |
| PRE_OA-D004 | 7 | 1369 | trabecular_meshwork | RGC (1) | SMC (1) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 2 | 1333 | ocular_surface | Mac_Tissue (1) | Mac_Tissue (1) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 11 | 1318 | ocular_surface | retina_interneuron::AC (1) | None (None) | inconsistent -> mixed |
| CX13_TM_corneal_scleral | 14 | 1261 | trabecular_meshwork | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX10_hiPSC_RPE | 6 | 1202 | rpe | Fibroblast (2) | Fibroblast (2) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 8 | 1186 | trabecular_meshwork | Pericyte (1) | onfibro_v13::Fibroblast (2) | inconsistent -> consistent |
| PRE_OA-D004 | 2 | 1158 | trabecular_meshwork | Pericyte (1) | Pericyte (1) | inconsistent -> inconsistent |
| PRE_GSE199013 | 16 | 1148 | ocular_surface | retina_interneuron::BC (1) | Melanocyte (1) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 4 | 1104 | ocular_surface | Limbus_Sclera_fibroblast_C1 (1) | Limbus_Sclera_fibroblast_C1 (1) | consistent -> consistent |
| CX13_central_cornea | 5 | 1093 | ocular_surface | Fibroblast (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| PRE_GSE199013 | 30 | 1085 | ocular_surface | Fibroblast (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| PRE_GSE199013 | 34 | 1057 | ocular_surface | progenitor cell (5) | progenitor cell (5) | consistent -> consistent |
| CX13_TM_corneal_scleral | 10 | 1018 | trabecular_meshwork | retina_interneuron::AC (1) | None (None) | inconsistent -> mixed |
| PRE_GSE199013 | 33 | 1001 | ocular_surface | retina_interneuron::AC (1) | None (None) | inconsistent -> mixed |
| PRE_GSE199013 | 0 | 975 | ocular_surface | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related |
| CX10_hiPSC_RPE | 18 | 965 | rpe | Myofibroblast (2) | Myofibroblast (2) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 6 | 955 | trabecular_meshwork | corneal endothelial cell (3) | corneal endothelial cell (3) | related -> related |
| PRE_OA-D001 | 30 | 929 | retina | RPE (2) | RPE (2) | consistent -> consistent |
| CX14_TM_ciliary_snRNA | 8 | 910 | trabecular_meshwork | retina_interneuron::BC (2) | None (None) | inconsistent -> mixed |
| PRE_GSE199013 | 14 | 852 | ocular_surface | non-pigmented ciliary epithelial cell (5) | non-pigmented ciliary epithelial cell (5) | related -> related |
| PRE_OA-D002 | 16 | 793 | ocular_surface | mast cell (4) | mast cell (4) | related -> related |
| PRE_GSE199013 | 6 | 745 | ocular_surface | Limbus_Sclera_fibroblast_C1 (2) | Limbus_Sclera_fibroblast_C1 (2) | consistent -> consistent |
| CX13_TM_corneal_scleral | 23 | 740 | trabecular_meshwork | Endo (1) | Endo (1) | related -> related |
| PRE_GSE199013 | 32 | 716 | ocular_surface | SMC (2) | SMC (2) | inconsistent -> inconsistent |
| PRE_OA-D068 | 12 | 698 | retina | Astro (2) | Astro (2) | inconsistent -> inconsistent |
| PRE_GSE199013 | 36 | 690 | ocular_surface | Endo (1) | Endo (1) | related -> related |
| PRE_OA-D002 | 17 | 685 | ocular_surface | MG (2) | oligodendrocyte (3) | inconsistent -> inconsistent |
| PRE_GSE199013 | 17 | 588 | ocular_surface | Pericyte (1) | Pericyte (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 7 | 582 | ocular_surface | Rod (3) | None (None) | related -> mixed |
| CX13_central_cornea | 12 | 543 | ocular_surface | retina_interneuron::BC (1) | basal cell (2) | inconsistent -> consistent |
| CX16_tabula_sapiens_eye | 8 | 542 | ocular_surface | Fibroblast (1) | Fibroblast (1) | inconsistent -> inconsistent |
| CX14_TM_ciliary_snRNA | 12 | 531 | trabecular_meshwork | retina_interneuron::BC (1) | pigmented ciliary epithelial cell (2) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 16 | 516 | ocular_surface | RGC (1) | Pericyte (1) | inconsistent -> consistent |
| CX16_tabula_sapiens_eye | 17 | 511 | ocular_surface | Myofibroblast (5) | Myofibroblast (5) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 20 | 503 | trabecular_meshwork | Pericyte (2) | Pericyte (2) | consistent -> consistent |
| CX13_TM_corneal_scleral | 11 | 440 | trabecular_meshwork | Fibroblast (1) | onfibro_v13::Fibroblast (2) | consistent -> consistent |
| CX09_voigt_RPE_choroid | 6 | 434 | rpe | Fibroblast (1) | Fibroblast (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 23 | 413 | ocular_surface | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent |
| CX13_ciliary_body | 11 | 404 | ciliary_body | retina_interneuron::BC (1) | pigmented ciliary epithelial cell (2) | inconsistent -> inconsistent |
| CX13_iris | 8 | 376 | iris | SMC (1) | SMC (1) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 13 | 353 | rpe | Fibroblast (1) | Fibroblast (1) | consistent -> consistent |
| CX16_tabula_sapiens_eye | 2 | 331 | ocular_surface | Melanocyte (6) | Melanocyte (6) | inconsistent -> inconsistent |
| CX12_ocular_surface_snRNA | 20 | 312 | ocular_surface | Melanocyte (4) | Melanocyte (4) | consistent -> consistent |
| CX13_ciliary_body | 14 | 300 | ciliary_body | T (1) | T (1) | consistent -> consistent |
| CX13_TM_corneal_scleral | 22 | 289 | trabecular_meshwork | retina_interneuron::BC (1) | goblet cell (2) | inconsistent -> related |
| PRE_GSE199013 | 35 | 289 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| CX16_tabula_sapiens_eye | 21 | 272 | ocular_surface | retina_interneuron::AC (1) | None (None) | inconsistent -> mixed |
| CX12_ocular_surface_snRNA | 19 | 265 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| CX04_cowan_fovea | 23 | 253 | retina | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent |
| CX13_central_cornea | 11 | 227 | ocular_surface | retina_interneuron::HC (1) | None (None) | inconsistent -> mixed |
| PRE_OA-D004 | 19 | 157 | trabecular_meshwork | trabecular meshwork cell (4) | trabecular meshwork cell (4) | inconsistent -> inconsistent |
| CX09_voigt_RPE_choroid | 12 | 156 | rpe | RPE (2) | RPE (2) | consistent -> consistent |
| CX10_hiPSC_RPE | 24 | 155 | rpe | Fibroblast (3) | Fibroblast (3) | inconsistent -> inconsistent |
| CX11_posterior_eye_atlas | 8 | 142 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| CX14_TM_ciliary_snRNA | 13 | 100 | trabecular_meshwork | Schwann (2) | Schwann (2) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 9 | 96 | ocular_surface | MG (1) | Fibroblast (1) | inconsistent -> inconsistent |
| CX14_TM_ciliary_snRNA | 14 | 94 | trabecular_meshwork | Schwann (2) | Schwann (2) | inconsistent -> inconsistent |
| PRE_GSE199013 | 13 | 70 | ocular_surface | retina_interneuron::BC (1) | None (None) | inconsistent -> mixed |
| PRE_GSE199013 | 22 | 70 | ocular_surface | retina_interneuron::BC (2) | mast cell (2) | inconsistent -> related |
| CX13_TM_corneal_scleral | 27 | 68 | trabecular_meshwork | Schwann (2) | Schwann (2) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 28 | 53 | trabecular_meshwork | retina_interneuron::BC (2) | mast cell (2) | inconsistent -> related |
| PRE_GSE199013 | 19 | 52 | ocular_surface | retina_interneuron::AC (1) | None (None) | inconsistent -> mixed |
| CX16_tabula_sapiens_eye | 34 | 26 | ocular_surface | Mac_Tissue (2) | Mac_Tissue (2) | inconsistent -> inconsistent |
| CX13_TM_corneal_scleral | 26 | 23 | trabecular_meshwork | Melanocyte (3) | Melanocyte (3) | consistent -> consistent |
| CX13_TM_corneal_scleral | 17 | 16 | trabecular_meshwork | retina_interneuron::BC (1) | pigmented ciliary epithelial cell (2) | inconsistent -> inconsistent |
| PRE_GSE199013 | 18 | 15 | ocular_surface | retina_interneuron::AC (2) | pigmented ciliary epithelial cell (2) | inconsistent -> inconsistent |
| CX16_tabula_sapiens_eye | 20 | 13 | ocular_surface | retina_interneuron::HC (1) | None (None) | inconsistent -> mixed |
| PRE_GSE199013 | 37 | 13 | ocular_surface | corneal endothelial cell (3) | corneal endothelial cell (3) | related -> related |
| CX13_central_cornea | 15 | 12 | ocular_surface | Astro (1) | None (None) | inconsistent -> mixed |

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
