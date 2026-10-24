# Instrument limit — the frozen noregr harness's ancestor closure drops the release's qualified `is_a` edges

Registered 2026-10-24 by card t_c19cd667 (KB-REACH), fixing item 3 of the card brief: the
qualified-`is_a` closure gap measured by card t_fabddb85 (§6.3) is either fixed behind a declared
switch or registered as a stated instrument limit. **This document registers it as an instrument
limit**; the frozen harness's bytes are NOT changed — `docs/plans/noregr_20261022/scripts/`
wave_common.py is pinned by that wave's own `out/MANIFEST.json`/`out/MANIFEST.sha256` and reused
byte-for-byte by several later cards' recorded readings, so editing it (even behind a default-OFF
switch) would break the comparability those pins exist to guarantee.

## 1. The defect, one line + the exact parse site

`wave_common.Rulers._load_obo` reads each `is_a` value as `v.split("!")[0].strip()`, which keeps
the trailing OBO qualifier — e.g. `is_a: CL:0000192 {is_inferred="true"}` — attached to the parent
id. Such parents never match a real term id, so **the qualified edges never enter the harness's
ancestor closure**; its `anc()`, `related()` and `cl_grade()` under-read coarser/finer relations and
report granularity differences as `truly_inconsistent`.

Site: `docs/plans/noregr_20261022/scripts/wave_common.py`, function `Rulers._load_obo`, the
`elif k == "is_a":` branch (`cur.setdefault("is_a", []).append(v.split("!")[0].strip())`).

## 2. Measured counts (this tree, re-derived 2026-10-24 — no number carried over by trust)

Pinned release `kb/ontology/cl/releases/2026-06-08/cl-base.obo` (sha256
`c6274fb65cdf740b983a06b74cb678814249d7f8e580c2ec9de54bf204a2b1c7`, line-parse by `scripts/r1_reproduce.py` D3 block:

| caliber | lines |
|---|---|
| all `is_a` lines in the release | 4880 |
| carrying any `{...}` qualifier after the id (the card brief's 686) | **686** |
| of which `{is_inferred="true"}` | 679 |
| carrying an `evidence=...` qualifier instead | 7 |

Every one of the 686 qualified lines is read into the closure with its qualifier attached by the
frozen parse, i.e. all of them drop out of the closure at once.

## 3. Effect on the recorded 721-cluster set, measured twice

Top source A = the service replay (the CLOSURE_INSTRUMENT_DIFFERENCE caliber of t_fabddb85:
`W.replay(calls, {"EYEKB_ACT_CL56": "1"}, label="kbreach_sens_before")`), four-way grades:

| grade | harness ruler | corrected ruler |
|---|---|---|
| kb_coarser | 116 | 129 |
| same_cl | 244 | 244 |
| kb_finer | 5 | 18 |
| truly_inconsistent | 176 | 150 |
| abstain | 165 | 165 |
| unmappable_pred | 15 | 15 |

Changed clusters (harness -> corrected): **26 of 721**; direction split:
truly_inconsistent -> kb_coarser = 13, truly_inconsistent -> kb_finer = 13.

Because `Rulers.related()` uses the same closure, the family-level (R_fam) verdict moves too:
consistent 297 -> 297, related 88 -> 102, inconsistent 171 -> 157, mixed 165 -> 165; **14 clusters are graded `inconsistent` by the harness and `related` by a qualifier-stripping closure** — every card that reused this harness under-reports relatedness by exactly this amount.
All 14 family-level moves are one-directional (harness `inconsistent` -> corrected `related`).

Top source B = the recorded ledger's own `pred_top1` column (no service call), as a second opinion:
27 of 721 clusters change under the two rulers (distribution: harness abstain=179, kb_coarser=116, kb_finer=3, same_cl=207, truly_inconsistent=203, unmappable_pred=13; corrected abstain=179, kb_coarser=131, kb_finer=15, same_cl=207, truly_inconsistent=176, unmappable_pred=13). The B counts differ from A because the ledger's recorded top labels predate the current shipped service state; A is the caliber the CL-56 wave recorded and is the one quoted below.

## 4. The 26 affected clusters (top source A, full list)

| # | volume | cluster | pred_top1 | truth | harness grade | corrected grade |
|---|---|---|---|---|---|---|
| 1 | CX08_RPE_choroid_scRNA | 1 | SMC | blood vessel smooth muscle cell | truly_inconsistent | kb_coarser |
| 2 | CX08_RPE_choroid_scRNA | 9 | Mono_Classical | monocyte | truly_inconsistent | kb_finer |
| 3 | CX08_RPE_choroid_scRNA | 17 | Endo | endothelial cell of arteriole | truly_inconsistent | kb_coarser |
| 4 | CX08_RPE_choroid_snRNA | 4 | SMC | vascular associated smooth muscle cell | truly_inconsistent | kb_coarser |
| 5 | CX08_RPE_choroid_snRNA | 9 | T | helper T cell | truly_inconsistent | kb_coarser |
| 6 | CX08_RPE_choroid_snRNA | 16 | Endo | vein endothelial cell | truly_inconsistent | kb_coarser |
| 7 | CX09_voigt_RPE_choroid | 0 | Microglia | macrophage | truly_inconsistent | kb_finer |
| 8 | CX12_ocular_surface_snRNA | 2 | Mac_Tissue | myeloid leukocyte | truly_inconsistent | kb_finer |
| 9 | CX12_ocular_surface_snRNA | 6 | T | lymphocyte | truly_inconsistent | kb_finer |
| 10 | CX12_ocular_surface_snRNA | 18 | ciliary muscle cell | smooth muscle cell | truly_inconsistent | kb_finer |
| 11 | CX13_TM_corneal_scleral | 16 | SMC | ciliary muscle cell | truly_inconsistent | kb_coarser |
| 12 | CX13_TM_corneal_scleral | 19 | T | lymphocyte | truly_inconsistent | kb_finer |
| 13 | CX13_ciliary_body | 14 | T | lymphocyte | truly_inconsistent | kb_finer |
| 14 | CX13_iris | 7 | SMC | smooth muscle cell of sphincter of pupil | truly_inconsistent | kb_coarser |
| 15 | CX14_TM_ciliary_snRNA | 10 | T | lymphocyte | truly_inconsistent | kb_finer |
| 16 | CX16_tabula_sapiens_eye | 3 | Microglia | myeloid leukocyte | truly_inconsistent | kb_finer |
| 17 | CX16_tabula_sapiens_eye | 4 | T | CD8-positive, alpha-beta T cell | truly_inconsistent | kb_coarser |
| 18 | CX16_tabula_sapiens_eye | 5 | T | CD4-positive, alpha-beta T cell | truly_inconsistent | kb_coarser |
| 19 | CX16_tabula_sapiens_eye | 19 | Endo | retinal blood vessel endothelial cell | truly_inconsistent | kb_coarser |
| 20 | PRE_GSE199013 | 9 | T | lymphocyte | truly_inconsistent | kb_finer |
| 21 | PRE_GSE199013 | 12 | T | lymphocyte | truly_inconsistent | kb_finer |
| 22 | PRE_GSE199013 | 32 | SMC | smooth muscle cell of sphincter of pupil | truly_inconsistent | kb_coarser |
| 23 | PRE_OA-D002 | 3 | Endo | endothelial cell of lymphatic vessel | truly_inconsistent | kb_coarser |
| 24 | PRE_OA-D004 | 5 | T | lymphocyte | truly_inconsistent | kb_finer |
| 25 | PRE_OA-D004 | 7 | SMC | ciliary muscle cell | truly_inconsistent | kb_coarser |
| 26 | PRE_OA-D004 | 20 | T | lymphocyte | truly_inconsistent | kb_finer |

## 5. Why the harness is not edited (and what future waves must do)

1. The harness's scripts are pinned by `docs/plans/noregr_20261022/out/MANIFEST.json` and
   `out/MANIFEST.sha256` (entry `scripts/wave_common.py`); several later cards' recorded readings
   state comparability with that ruler. Any byte edit — including a declared switch — invalidates
   those pins and forces every consumer to re-run; that is a coordination decision this card does
   not own.
2. Until the closure is fixed at the harness, any wave that grades Cell-Ontology relations here
   MUST state both readings (harness ruler + a qualifier-stripped second ruler, e.g. the
   `ont_closure_probe.py` implementation this measurement reused) and must not cite a relatedness
   deficit computed on the harness closure alone when the affected terms carry qualified `is_a`
   parents. The re-derivation entry points:

   - `/usr/bin/python3 scripts/r3_closure.py` (this wave: two top sources, both rulers, full lists)
   - `/usr/bin/python3 /mnt/D/EyeKB/plans/cl56_adopt_20261022/scripts/ont_closure_probe.py` (the
     corrected-closure implementation, zero-write)

3. Recorded readings made BEFORE this registration remain comparable among themselves — all of
   them carry the same harness-side under-count. Nothing delivered earlier changes value; the cost
   is that `related` was under-counted by up to 14 clusters on this recorded set.

## 6. Verification this file follows (bytes, commands)

- re-derivation: `/usr/bin/python3 scripts/r3_closure.py` -> out/R3_CLOSURE_READING.json
  (committed mirror: docs/plans/kbreach_fix_20261024/out/R3_CLOSURE_READING.json)
- pre-fix release parse: `/usr/bin/python3 scripts/r1_reproduce.py` -> out/R1_REPRODUCE.json
  (D3 block: 4880 / 686 / 679 counts with the obo sha256 above)
- the harness import in both scripts resolves to the frozen path above and is byte-identical to
  the repo mirror (`docs/plans/noregr_20261022/scripts/wave_common.py`, sha256
  f8226dc4aefc799ace536b66748ece67494826031c21242b6e25b44389f37863).
