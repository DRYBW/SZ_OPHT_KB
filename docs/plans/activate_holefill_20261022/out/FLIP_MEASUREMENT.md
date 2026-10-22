# Flip measurement — `holefill_v12` on the default route (card t_be11fd4a)

Instrument: `docs/plans/noregr_20261022/scripts/n3_harness.py` + `wave_common.py`, reused
unchanged; one declared extension (the switch name `EYEKB_ACT_HOLEFILL` joins the hygiene
tuple). Recorded set: 721 clusters / 1495330 cells / 28 volumes.

## Acceptance (a/b/c measured here; d is `l3`)

| clause | reading | result |
|---|---|---|
| (a) no dataset's consistent share falls | F1 FAIL / F2 FAIL / default FAIL | **FAIL** |
| (b) aggregate inconsistent share does not rise | D_default_route +13.063pp; F1_recorded_decls +12.725pp; F2_tester_decls +12.986pp | **FAIL** |
| (c) every move attributed | 255 moved, kinds {'library-gain': 90, 'rank-shift': 165}, unexpected 0 | ok |

**Verdict on (a)(b)(c): NO-GO**

## Overall, cell-weighted (recorded declarations, F1)

| grade | before % | after % | delta pp |
|---|---:|---:|---:|
| consistent | 42.544 | 39.230 | -3.314 |
| related | 16.936 | 13.030 | -3.906 |
| inconsistent | 19.843 | 32.568 | +12.725 |
| mixed | 20.676 | 15.172 | -5.504 |

## Default route (no tissue argument)

| grade | before % | after % |
|---|---:|---:|
| consistent | 43.228 | 39.853 |
| related | 8.831 | 5.471 |
| inconsistent | 24.205 | 37.268 |
| mixed | 23.736 | 17.408 |

Path changed clusters: 92. Harm cells: 109161.

## Target classes (pre-registered directions)

| class | CL | clusters | exact before | exact after |
|---|---|---:|---:|---:|
| endothelial cell | CL:0000115 | 12 | 10 | 7 |
| macrophage | CL:0000235 | 16 | 6 | 8 |
| retinal pigment epithelial cell | CL:0002586 | 37 | 10 | 5 |
| retinal rod cell | CL:0000604 | 25 | 14 | 1 |

Rod panel: shipped 5 genes clear the >=2 shared-gene bar on 11 of 25 rod-truth clusters;
the increment's 15-gene panel clears it on 21 (+10).

## Moved clusters

| volume | cluster | cells | truth | before | after | grade | kind |
|---|---|---:|---|---|---|---|---|
| CX02_adult_retina | 4 | 12902 | retinal rod cell | Rod (1) | retinal rod cell (3) | consistent -> inconsistent | library-gain |
| CX02_adult_retina | 2 | 11504 | glial cell | MG (1) | MG (1) | related -> related | rank-shift |
| PRE_OA-D068 | 8 | 11348 | Mueller cell | MG (1) | MG (1) | consistent -> consistent | rank-shift |
| CX01_retina_snRNA | 11 | 9022 | OFF midget ganglion cell | RGC (1) | RGC (1) | consistent -> consistent | rank-shift |
| CX04_cowan_organoid | 3 | 8557 | retinal rod cell | Rod (2) | retinal rod cell (4) | consistent -> inconsistent | library-gain |
| CX03_retina_multiome | 7 | 8308 | retinal rod cell | None (None) | retinal rod cell (2) | mixed -> inconsistent | library-gain |
| CX03_retina_multiome | 12 | 7918 | retinal rod cell | None (None) | retinal rod cell (1) | mixed -> inconsistent | library-gain |
| CX13_iris | 11 | 7817 | fibroblast | trabecular meshwork cell (3) | trabecular meshwork cell (3) | inconsistent -> inconsistent | rank-shift |
| CX13_iris | 4 | 7697 | melanocyte | None (None) | endothelial cell of vascular tree (1) | mixed -> inconsistent | library-gain |
| CX08_RPE_choroid_snRNA | 16 | 7584 | vein endothelial cell | Endo (1) | Endo (1) | inconsistent -> inconsistent | rank-shift |
| PRE_OA-D004 | 10 | 7296 | blood vessel endothelial cell | Endo (4) | endothelial cell (5) | related -> inconsistent | library-gain |
| CX14_TM_ciliary_snRNA | 6 | 7215 | blood vessel endothelial cell | Endo (3) | endothelial cell (4) | related -> inconsistent | library-gain |
| CX13_iris | 9 | 7148 | pigmented epithelial cell | SMC (2) | SMC (2) | inconsistent -> inconsistent | rank-shift |
| CX08_RPE_choroid_snRNA | 15 | 6987 | endothelial cell of artery | Endo (1) | Endo (1) | related -> related | rank-shift |
| PRE_OA-D004 | 15 | 6736 | melanocyte | Melanocyte (3) | Melanocyte (3) | consistent -> consistent | rank-shift |
| CX14_TM_ciliary_snRNA | 7 | 6705 | pigmented ciliary epithelial cell | pigmented ciliary epithelial cell (4) | pigmented ciliary epithelial cell (4) | related -> related | rank-shift |
| PRE_OA-D004 | 0 | 6579 | pericyte | Pericyte (3) | Pericyte (3) | consistent -> consistent | rank-shift |
| PRE_OA-D068 | 4 | 6577 | retinal rod cell | Rod (2) | retinal rod cell (3) | consistent -> inconsistent | library-gain |
| PRE_OA-D004 | 11 | 6521 | Schwann cell | Schwann (2) | Schwann (2) | consistent -> consistent | rank-shift |
| CX14_TM_ciliary_snRNA | 5 | 6501 | melanocyte | Melanocyte (4) | Melanocyte (4) | consistent -> consistent | rank-shift |
| CX14_TM_ciliary_snRNA | 9 | 6433 | macrophage | Mac_Tissue (2) | Mac_Tissue (2) | related -> related | rank-shift |
| CX14_TM_ciliary_snRNA | 0 | 6414 | pericyte | Pericyte (1) | Pericyte (1) | consistent -> consistent | rank-shift |
| CX10_hiPSC_RPE | 0 | 6299 | retinal pigment epithelial cell | RPE (2) | retinal pigment epithelial cell (3) | consistent -> inconsistent | library-gain |
| CX11_posterior_eye_atlas | 16 | 6257 | melanocyte | Melanocyte (3) | Melanocyte (3) | consistent -> consistent | rank-shift |
| PRE_OA-D002 | 5 | 6176 | macrophage | APC_MHCII_high (2) | macrophage (3) | inconsistent -> consistent | library-gain |
| CX04_cowan_periphery | 7 | 6085 | retinal rod cell | Rod (2) | retinal rod cell (3) | consistent -> inconsistent | library-gain |
| CX13_iris | 3 | 6003 | melanocyte | Melanocyte (2) | Melanocyte (2) | consistent -> consistent | rank-shift |
| CX10_hiPSC_RPE | 3 | 5993 | retinal pigment epithelial cell | Melanocyte (3) | Melanocyte (3) | inconsistent -> inconsistent | rank-shift |
| CX13_TM_corneal_scleral | 12 | 5988 | fibroblast | onfibro_v13::Fibroblast (2) | onfibro_v13::Fibroblast (2) | consistent -> consistent | rank-shift |
| CX08_RPE_choroid_scRNA | 2 | 5950 | pericyte | Pericyte (3) | Pericyte (3) | consistent -> consistent | rank-shift |
| CX08_RPE_choroid_scRNA | 8 | 5747 | macrophage | Mac_Tissue (3) | macrophage (6) | related -> consistent | library-gain |
| PRE_OA-D001 | 3 | 5564 | retinal rod cell | Rod (1) | retinal rod cell (3) | consistent -> inconsistent | library-gain |
| CX08_RPE_choroid_scRNA | 3 | 5505 | melanocyte | Melanocyte (3) | Melanocyte (3) | consistent -> consistent | rank-shift |
| PRE_OA-D004 | 9 | 5460 | macrophage | APC_MHCII_high (3) | APC_MHCII_high (3) | inconsistent -> inconsistent | rank-shift |
| CX07_iPSC_organoid_POAG | 8 | 5369 | retinal cone cell | Melanocyte (1) | Melanocyte (1) | inconsistent -> inconsistent | rank-shift |
| CX08_RPE_choroid_scRNA | 17 | 5334 | endothelial cell of arteriole | Endo (2) | endothelial cell (3) | inconsistent -> inconsistent | library-gain |
| PRE_OA-D004 | 8 | 5310 | pigmented ciliary epithelial cell | pigmented ciliary epithelial cell (3) | pigmented ciliary epithelial cell (3) | related -> related | rank-shift |
| CX08_RPE_choroid_scRNA | 15 | 5291 | retinal pigment epithelial cell | retina_interneuron::BC (2) | retina_interneuron::BC (2) | inconsistent -> inconsistent | rank-shift |
| CX08_RPE_choroid_scRNA | 7 | 5261 | endothelial cell of venule | Endo (1) | Endo (1) | related -> related | rank-shift |
| PRE_OA-D068 | 6 | 5191 | amacrine cell | AC (1) | AC (1) | consistent -> consistent | rank-shift |
| CX04_cowan_organoid | 12 | 5187 | Mueller cell | MG (1) | MG (1) | consistent -> consistent | rank-shift |
| PRE_OA-D004 | 14 | 5144 | non-pigmented ciliary epithelial cell | non-pigmented ciliary epithelial cell (3) | capillary endothelial cell (2) | related -> inconsistent | library-gain |
| PRE_OA-D068 | 7 | 5021 | retina horizontal cell | None (None) | retinal pigment epithelial cell (1) | mixed -> inconsistent | library-gain |
| PRE_OA-D002 | 8 | 4981 | melanocyte | Melanocyte (5) | Melanocyte (5) | consistent -> consistent | rank-shift |
| CX08_RPE_choroid_scRNA | 9 | 4974 | monocyte | Mono_Classical (3) | Mono_Classical (3) | consistent -> consistent | rank-shift |
| CX11_posterior_eye_atlas | 6 | 4943 | macrophage | Mac_Tissue (4) | macrophage (5) | related -> consistent | library-gain |
| PRE_OA-D002 | 7 | 4940 | endothelial cell | Endo (1) | endothelial cell (2) | related -> inconsistent | library-gain |
| CX13_central_cornea | 10 | 4802 | corneal endothelial cell | corneal endothelial cell (4) | corneal endothelial cell (4) | related -> related | rank-shift |
| CX03_retina_multiome | 9 | 4746 | retinal rod cell | None (None) | retinal rod cell (2) | mixed -> inconsistent | library-gain |
| CX08_RPE_choroid_snRNA | 4 | 4743 | vascular associated smooth muscle cell | SMC (2) | SMC (2) | inconsistent -> inconsistent | rank-shift |
| CX03_retina_multiome | 11 | 4719 | retinal rod cell | Rod (1) | retinal rod cell (4) | consistent -> inconsistent | library-gain |
| CX04_cowan_organoid | 4 | 4558 | retinal rod cell | Rod (3) | retinal rod cell (4) | consistent -> inconsistent | library-gain |
| PRE_OA-D001 | 2 | 4488 | Mueller cell | MG (2) | MG (2) | consistent -> consistent | rank-shift |
| CX04_cowan_periphery | 3 | 4416 | Mueller cell | None (None) | macrophage (1) | mixed -> inconsistent | library-gain |
| PRE_OA-D068 | 5 | 4397 | retinal cone cell | Melanocyte (1) | Melanocyte (1) | inconsistent -> inconsistent | rank-shift |
| PRE_OA-D002 | 9 | 4363 | fibroblast | Pericyte (2) | Pericyte (2) | inconsistent -> inconsistent | rank-shift |
| PRE_OA-D068 | 10 | 4194 | amacrine cell | retina_interneuron::HC (2) | retina_interneuron::HC (2) | inconsistent -> inconsistent | rank-shift |
| PRE_OA-D002 | 6 | 4129 | blood vessel endothelial cell | Endo (5) | endothelial cell (6) | related -> inconsistent | library-gain |
| PRE_OA-D068 | 19 | 4097 | retinal rod cell | Rod (2) | retinal rod cell (4) | consistent -> inconsistent | library-gain |
| PRE_GSE268630 | 3 | 3998 | retinal rod cell | Rod (1) | Rod (1) | consistent -> consistent | rank-shift |

(195 further moved clusters in `FLIP_MEASUREMENT.json`.)

## In-sample disclosure

IN-SAMPLE READING: the library was selected on the same 28 public volumes it is measured on, so this is a coverage/harm reading, not a validation, not an independent test and not an accuracy claim. It is measured at Cell-Ontology level against the author's per-cluster majority label; two of the library's 17 entries (classical / non-classical monocyte) already fail their own pre-registered coverage bar and are carried as FAIL in the library's own record.

