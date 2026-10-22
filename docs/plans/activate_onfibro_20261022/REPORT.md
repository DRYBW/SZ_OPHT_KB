# Activation report -- the optic-nerve fibroblast carrier (`onfibro_v13`) on the default route

Card: `t_42df17c2` (L7 ACTIVATE onfibro_v13 on the default route) · board `pi-briefing` · 2026-10-22
Pre-registration: `PREREG_ACTIVATION_ONFIBRO_20261022.md` (sha256 `44698e523715262684ed20d88ce69fc4e1e701e2dada10b358dafae12f190c50`, written and on disk before any measurement of the flipped state -- see `out/PREIMAGE.json` for the ordering record).
Interpreter: `/usr/bin/python3` for this wave's scripts (stdlib only); `/home/ubuntu/training-venv/bin/python3` for the repository's G3/G7 precondition and the tool-panel probe; the pipeline gate pins its own contract interpreter.
Zero network, zero downloads: `ledgers/net_audit.log` carries 689 hook load receipts and zero connecting/HTTP event lines (`out/GATE.json` M11).

Everything below is reproducible with one command:

```bash
cd /home/ubuntu/EYEKB_REPO/docs/plans/activate_onfibro_20261022
bash scripts/run_all.sh --with-commit      # measure + re-register + gates + manifest + gate
bash scripts/m4_clone_check.sh             # the clean-clone chain at the commit under test
```

---

## 0. One-line answers

1. **The activation is measured, not assumed.** Over the recorded 28 volumes / 721 clusters / 1495330 cells, cell-weighted, the flip raises the overall `consistent` share by **+1.692pp** (recorded declarations), **+1.618pp** (the external tester's re-declarations) and **+1.496pp** on the default route itself; **no dataset's share falls** on any of the three, and **no cell moves down a grade** (`harm cells = 0`).
2. **The kill switch restores the pre-flip default byte-for-byte.** With the flip in place, `EYEKB_ACT_ONFIBRO=0` reproduces the parent commit's core output on **721/721** recorded cluster windows and **229/229** battery calls, raw and canonical, at the SAME absolute path.
3. **The change is the only change, and it is fully attributed**: 721 of 721 cluster queries move in bytes under the new default; 45 of them move at the RANKING level (the same 45 clusters the predecessor wave measured through the injected arm), 676 move only in the disclosure fields, and **0 are unexplained**.
4. **One compatibility-contract item, reported and not absorbed**: the legacy five-tool panel digest moved (`e8e6c26351cd9a1d42fa2e7cb6a83f23` -> `47e42230a8f7256b4ae9a78d4ff628d3`) on two `query_marker` calls whose **rankings are unchanged**; the baseline fixture was **not** re-recorded, so the panel probe is red at this commit by design (the decision is the owner's).
5. **One frozen identity anchor moved and was re-anchored with the reason recorded and the pre-image kept**: G4's `decisions_template.csv` and normalized evidence report. Three runs with the activation in place agree with each other, and a run with the switch OFF reproduces the previous anchors byte-for-byte -- so the movement is the activation, not the machine.
6. **The repository's own gate chain (G3..G8) is green in the author tree and again inside a clean clone** of the commit under test (`out/CLEAN_CLONE_CHECK.json`).
7. **The reading is IN-SAMPLE.** The carrier was selected on these same volumes: this is a harm-line reading of one measured drop and its repair, **not a validation, not an independent test, and not an accuracy claim**. The carrier is a family-level (coarse) answer and it clears the >=2 shared-gene bar only at the bar.

---

## 1. What was activated, exactly

| item | before | after |
|---|---|---|
| `ONFIBRO_DEFAULT_LIBS` | `()` | `("onfibro_v13",)` |
| core file sha256 | `3dadbbbaf2631da0f48760beb95278f5fabd675e6108282c9080fae67a61d736` | `e74c73c6c2ef04d19b94edd69cfb414bc38104b29c2d054a5e711ad03e781079` |
| core file bytes | 114098 | 115058 |
| the carrier file | `kb/markers/markers_v13_onfibro_increment.json`, byte-unchanged |

The flip is 21 added / 10 removed lines, all inside the declared ONFIBRO region (lines 358-386 after the edit); the only whitelist that changed is `ONFIBRO_DEFAULT_LIBS` ({'ONFIBRO_DEFAULT_LIBS': ['()', '("onfibro_v13",)']}); the module compiles and reports `('onfibro_v13',) / unset-> True / zero-> False / off-> False` with `EYEKB_ACT_ONFIBRO` unset/`1` and `False` for `0`/`off`.

The pre-flip bytes are kept as a pre-image (`pre_images/eyekb_core.py.pre_activation`, sha256 `3dadbbbaf2631da0f48760beb95278f5fabd675e6108282c9080fae67a61d736`), verified identical to the parent commit's blob (`out/DEFAULT_FACE.json: parent_core_equals_kept_preimage = True`).

## 2. The kill switch: `EYEKB_ACT_ONFIBRO=0` restores the pre-flip default byte-for-byte

Measured by swapping the parent commit's core IN PLACE at the same absolute path and replaying the recorded query set, then restoring the flipped file (sha re-verified: `restored == snapshot = True`).

| arm | mode | queries | raw bytes identical | canonical identical | differing raw |
|---|---|---:|---|---|---:|
| KILL vs PARENT | clusters | 721 | True | True | 0 |
| KILL vs PARENT | battery | 229 | True | True | 0 |

Combined digests for the record: clusters raw `53b045972102086ac085a5649bd8859e` (parent) = `53b045972102086ac085a5649bd8859e` (kill); battery raw `56fd4a1c0c451f39e5d630869fae327a` (parent) = `56fd4a1c0c451f39e5d630869fae327a` (kill).

## 3. The measurement

Instrument: the predecessor wave's harness, reused byte-for-byte (`docs/plans/noregr_20261022/scripts/n3_harness.py` + `wave_common.py`; pre-image sha256 of the harness files is recorded in every harness run). One declared extension: `wave_common.SWITCHES` gained the name `EYEKB_ACT_ONFIBRO`, because the newest service switch was not in the hygiene tuple and an arm's value could have leaked into the next arm; no rule, ruler, grade or threshold was changed.

| run | change | verdict | changed clusters | changed cells | overall consistent |
|---|---|---|---:|---:|---:|
| F1 the flip (recorded declarations) | kill switch OFF -> default ON | **PASS** | 45 | 111247 | 40.852% -> **42.544%** (+1.692pp) |
| F2 the flip (tester re-declarations) | kill switch OFF -> default ON | **PASS** | 45 | 111247 | 41.061% -> **42.679%** (+1.618pp) |
| F3 control: OFF + measurement-only injection | kill switch OFF -> default ON | **PASS** | 45 | 111247 | 40.852% -> **42.544%** (+1.692pp) |
| default route (no `tissue` argument) | kill switch OFF -> default ON | **PASS** | 12 | - | 41.732% -> **43.228%** (+1.496pp) |

Cross-checks (all in `out/FLIP_MEASUREMENT.json`):

* the flipped default reproduces the measurement-only injection arm cluster by cluster: **721/721 identical** rankings;
* the kill-switch arm reproduces the predecessor wave's R2 *before* arm exactly, and F1/F2 reproduce its R2/R3 *after* arms (`cross_wave_identity`, all three `identical = True`) -- the pre-flip state has not drifted since that wave;
* ruler self-check against the recording's own `pred_family` column: 542 agree / 0 differ.

### 3.1 Per-dataset, cell-weighted (recorded declarations)

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
| CX12_ocular_surface_snRNA | 21 | 37264 | 35.997 | 35.997 | +0.000 |
| CX13_central_cornea | 16 | 35890 | 6.629 | 6.629 | +0.000 |
| CX13_ciliary_body | 17 | 32282 | 21.495 | 21.495 | +0.000 |
| CX13_iris | 17 | 55990 | 18.646 | 18.646 | +0.000 |
| CX13_lens | 11 | 13538 | 0.0 | 0.0 | +0.000 |
| CX16_tabula_sapiens_eye | 36 | 31808 | 18.052 | 18.052 | +0.000 |
| CX17_mouse_retina_all | 36 | 71751 | 0.0 | 0.0 | +0.000 |
| PRE_GSE268630 | 36 | 59276 | 71.705 | 71.705 | +0.000 |
| PRE_OA-D001 | 32 | 62649 | 74.97 | 74.97 | +0.000 |
| PRE_OA-D002 | 19 | 69411 | 35.879 | 35.879 | +0.000 |
| PRE_OA-D004 | 21 | 81867 | 44.765 | 44.765 | +0.000 |
| PRE_OA-D068 | 20 | 63773 | 53.785 | 53.785 | +0.000 |
| CX13_TM_corneal_scleral | 29 | 51414 | 38.999 | 41.306 | +2.307 |
| CX15_optic_nerve_all | 46 | 71997 | 41.873 | 44.403 | +2.530 |
| CX08_RPE_choroid_snRNA | 18 | 70474 | 31.834 | 37.314 | +5.480 |
| PRE_GSE199013 | 38 | 42473 | 36.859 | 43.376 | +6.517 |
| CX11_posterior_eye_atlas | 20 | 54697 | 21.16 | 32.483 | +11.323 |
| CX14_TM_ciliary_snRNA | 17 | 78110 | 34.716 | 46.839 | +12.123 |

Cells moved, by grade transition (recorded declarations): {"inconsistent->consistent": 3954, "mixed->consistent": 21346}

### 3.2 Every moved cluster, with its truth label and its before/after answer

Kinds: `carrier-gain` = the carrier entry becomes the top-1 answer; `rank-shift` = the top-1 is unchanged and only the candidate list moved; `unexpected` = the top-1 changed to something that is not the carrier entry (none). `intended repair` = a carrier-gain cluster whose reference family is `fibro`.

| volume | cluster | cells | truth (ref cell type / family) | before | after | kind | intended |
|---|---|---:|---|---|---|---|---|
| PRE_OA-D004 | 3 | 10201 | fibroblast / fibro | Fibroblast (2) | Fibroblast (2) | rank-shift | no |
| CX14_TM_ciliary_snRNA | 1 | 9469 | fibroblast / fibro | None (None) | onfibro_v13::Fibroblast (1) | carrier-gain | yes |
| CX10_hiPSC_RPE | 0 | 6299 | retinal pigment epithelial cell / rpe | RPE (2) | RPE (2) | rank-shift | no |
| CX13_TM_corneal_scleral | 12 | 5988 | fibroblast / fibro | Fibroblast (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| CX08_RPE_choroid_scRNA | 0 | 5670 | fibroblast / fibro | Pericyte (2) | Pericyte (2) | rank-shift | no |
| CX12_ocular_surface_snRNA | 4 | 5657 | keratocyte / fibro | Fibroblast (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| PRE_OA-D004 | 14 | 5144 | non-pigmented ciliary epithelial cell / rpe | non-pigmented ciliary epithelial cell (3) | non-pigmented ciliary epithelial cell (3) | rank-shift | no |
| CX11_posterior_eye_atlas | 12 | 5089 | fibroblast / fibro | None (None) | onfibro_v13::Fibroblast (1) | carrier-gain | yes |
| CX13_central_cornea | 10 | 4802 | corneal endothelial cell / endo | corneal endothelial cell (4) | corneal endothelial cell (4) | rank-shift | no |
| PRE_OA-D002 | 9 | 4363 | fibroblast / fibro | Pericyte (2) | Pericyte (2) | rank-shift | no |
| CX10_hiPSC_RPE | 17 | 4008 | retinal pigment epithelial cell / rpe | Fibroblast (5) | Fibroblast (5) | rank-shift | no |
| CX08_RPE_choroid_snRNA | 1 | 3862 | fibroblast / fibro | None (None) | onfibro_v13::Fibroblast (1) | carrier-gain | yes |
| CX13_ciliary_body | 5 | 3464 | fibroblast / fibro | Fibroblast (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| PRE_OA-D002 | 11 | 3447 | keratocyte / fibro | Fibroblast (4) | Fibroblast (4) | rank-shift | no |
| CX10_hiPSC_RPE | 7 | 3323 | retinal pigment epithelial cell / rpe | Fibroblast (2) | Fibroblast (2) | rank-shift | no |
| PRE_OA-D004 | 4 | 3158 | trabecular meshwork cell / tm | trabecular meshwork cell (6) | trabecular meshwork cell (6) | rank-shift | no |
| PRE_GSE199013 | 4 | 2768 | fibroblast / fibro | Pericyte (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| PRE_OA-D002 | 10 | 2732 | keratocyte / fibro | Fibroblast (3) | Fibroblast (3) | rank-shift | no |
| CX10_hiPSC_RPE | 16 | 2632 | retinal pigment epithelial cell / rpe | Myofibroblast (3) | Myofibroblast (3) | rank-shift | no |
| CX16_tabula_sapiens_eye | 0 | 2426 | fibroblast / fibro | Pericyte (2) | Pericyte (2) | rank-shift | no |
| CX15_optic_nerve_all | 31 | 1822 | fibroblast / fibro | None (None) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| CX10_hiPSC_RPE | 6 | 1202 | retinal pigment epithelial cell / rpe | Fibroblast (2) | Fibroblast (2) | rank-shift | no |
| CX13_TM_corneal_scleral | 8 | 1186 | fibroblast / fibro | Pericyte (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| PRE_OA-D004 | 2 | 1158 | pigmented ciliary epithelial cell / rpe | Pericyte (1) | Pericyte (1) | rank-shift | no |
| CX11_posterior_eye_atlas | 4 | 1104 | fibroblast / fibro | None (None) | onfibro_v13::Fibroblast (1) | carrier-gain | yes |
| CX13_central_cornea | 5 | 1093 | fibroblast / fibro | Fibroblast (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| PRE_GSE199013 | 30 | 1085 | fibroblast / fibro | Fibroblast (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| CX10_hiPSC_RPE | 18 | 965 | retinal pigment epithelial cell / rpe | Myofibroblast (2) | Myofibroblast (2) | rank-shift | no |
| PRE_OA-D001 | 30 | 929 | retinal pigment epithelial cell / rpe | RPE (2) | RPE (2) | rank-shift | no |
| PRE_GSE199013 | 14 | 852 | non-pigmented ciliary epithelial cell / rpe | non-pigmented ciliary epithelial cell (5) | non-pigmented ciliary epithelial cell (5) | rank-shift | no |
| PRE_GSE199013 | 6 | 745 | fibroblast / fibro | Limbus_Sclera_fibroblast_C1 (2) | Limbus_Sclera_fibroblast_C1 (2) | rank-shift | no |
| CX13_TM_corneal_scleral | 23 | 740 | endothelial cell / endo | Endo (1) | Endo (1) | rank-shift | no |
| PRE_OA-D068 | 12 | 698 | Mueller cell / mg | Astro (2) | Astro (2) | rank-shift | no |
| CX16_tabula_sapiens_eye | 8 | 542 | conjunctival epithelial cell / cornea_epi | Fibroblast (1) | Fibroblast (1) | rank-shift | no |
| CX13_TM_corneal_scleral | 11 | 440 | fibroblast / fibro | Fibroblast (1) | onfibro_v13::Fibroblast (2) | carrier-gain | yes |
| CX09_voigt_RPE_choroid | 6 | 434 | fibroblast / fibro | Fibroblast (1) | Fibroblast (1) | rank-shift | no |
| CX13_iris | 8 | 376 | pigmented epithelial cell / rpe | SMC (1) | SMC (1) | rank-shift | no |
| CX09_voigt_RPE_choroid | 13 | 353 | fibroblast / fibro | Fibroblast (1) | Fibroblast (1) | rank-shift | no |
| CX04_cowan_fovea | 23 | 253 | fibroblast / fibro | Pericyte (2) | Pericyte (2) | rank-shift | no |
| CX13_TM_corneal_scleral | 25 | 178 | fibroblast / fibro | Fibroblast (1) | Fibroblast (1) | rank-shift | no |
| PRE_OA-D004 | 19 | 157 | fibroblast / fibro | trabecular meshwork cell (4) | trabecular meshwork cell (4) | rank-shift | no |
| CX09_voigt_RPE_choroid | 12 | 156 | retinal pigment epithelial cell / rpe | RPE (2) | RPE (2) | rank-shift | no |
| CX10_hiPSC_RPE | 24 | 155 | retinal pigment epithelial cell / rpe | Fibroblast (3) | Fibroblast (3) | rank-shift | no |
| CX16_tabula_sapiens_eye | 9 | 96 | retinal pigment epithelial cell / rpe | MG (1) | MG (1) | rank-shift | no |
| CX16_tabula_sapiens_eye | 34 | 26 | Mueller cell / mg | Mac_Tissue (2) | Mac_Tissue (2) | rank-shift | no |

Kind census: {"carrier-gain": 13, "rank-shift": 32}; takeovers on another family: 0; unexpected: 0; harm cells: 0.

The motivating cluster, for the record: `CX15_optic_nerve_all` c31, 1822 cells, truth `fibroblast` (family `fibro`), `None`(None) -> **`onfibro_v13::Fibroblast`(2)**, grade `mixed` -> `consistent`, Cell Ontology `abstain` -> `same_cl`.

## 4. The delta is the intended movement -- and the compatibility item

Byte movement and ranking movement are different claims and are reported separately:

| arm | queries | bytes moved | ranking moved | bytes moved with ranking unchanged | unexplained |
|---|---:|---:|---:|---:|---:|
| clusters | 721 | 721 | 45 | 676 | 0 |
| battery | 229 | 228 | 0 | 228 | 0 |

What the moved bytes are (`out/FIELD_DIFF.json`, per JSON path): **`celltype_ranking`, `gene_to_celltypes`, `provenance`, `soft_flags`**. The ranking surface moves on the clusters above; the disclosure fields (`provenance/files`, `provenance/conflicts`, `soft_flags/notes`) move on every response that carries them, because they now name the carrier's file and entries -- which is the intended consequence of the library being a member of the route, not a movement of an answer.

**Compatibility-contract item (reported, not absorbed).** The repository's own tool-panel identity probe, run under both cores:

| panel | parent (pre-flip) | flip (activated) | unchanged |
|---|---|---|---|
| legacy five-tool | `e8e6c26351cd9a1d42fa2e7cb6a83f23` | `47e42230a8f7256b4ae9a78d4ff628d3` | False |
| full six-tool | `3f1f52cb62915f5ad2801962aa523d36` | `f97ff8ad2507f4d69a0e6e57406c2de1` | False |

The probe's own per-call attribution: IDENTITY FAIL: legacy_panel, full_panel moved.; different: query_marker:{"cell_type": "MG"}; different: query_marker:{"genes": ["TMEM119", "CX3CR1", "P2RY12", "C1QA", "SALL1", "CSF1R", "AIF1"]}.
The two calls that moved are `query_marker` calls on the default route; their **rankings are unchanged** (their response diff is confined to `provenance` and `soft_flags`, see `out/FIELD_DIFF.json`: `genes:legacy_panel_microglia` has 2 differing paths, `celltype:MG` has 2). The probe file itself is byte-unchanged against the parent commit. **The baseline fixture was not re-recorded**: re-recording it is the owner's decision, so the movement stays visible as `tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json` reporting `IDENTITY FAIL` at this commit. No gate of the one-click chain (G3..G8) invokes the probe, so the chain is unaffected.

## 5. The frozen identity anchor that moved: G4

`python3 tests/verify_pipeline.py` reported **2/3 mismatch** with the activation in place (`tests/verify_pipeline.py` itself untouched). Re-anchored with the reason recorded and the pre-image kept, and with a causal control:

| reading | value |
|---|---|
| mode (re-anchor / verify) | verify |
| anchors that moved | annotation_evidence_report.md__normalized, decisions_template.csv |
| three runs with the activation in place | identical to each other: **True**
| one run with `EYEKB_ACT_ONFIBRO=0` | reproduces the PREVIOUS anchors byte-for-byte: **True**
| pre-flip expectation kept as | `tests/G4_EXPECTED_PRE-ONFIBRO.json` (sha256 `987190b1eb351bb6fab134afbf0684699a03a64e7c68837c04e924a979d648cd`)
| new expectation | `tests/G4_EXPECTED.json` (sha256 `9f7b4be6d8eeb2888fb9b3df6dd18ac7d1db7bfdaf9bfcc1d90f60efcff6c820`)
| `tests/verify_pipeline.py` after the re-anchor | rc=0 (3/3 PASS)

The criterion is unchanged -- the same three anchors, byte-for-byte, under the same pinned contract interpreter. Only the values they must equal were re-taken from the shipped default, which is what a frozen identity anchor of the default route means; the OFF-state control is what proves the movement belongs to this change and not to the machine.

## 6. Re-registration, in the same commit

| surface | what changed |
|---|---|
| `GATE_INVENTORY_G2_VERIFY_CONTRACT` | {"before": "354403dae664c6584cd9e4123547cf812528905dd87e9d747f481fe75f40fc40", "after": "354403dae664c6584cd9e4123547cf812528905dd87e9d747f481fe75f40fc40", "re_taken": false} |
| `L1-11M` | {"before": {"sha256": "e74c73c6c2ef04d19b94edd69cfb414bc38104b29c2d054a5e711ad03e781079", "bytes": "115058"}, "after": {"sha256": "e74c73c6c2ef04d19b94edd69cfb414bc38104b29c2d054a5e711ad03e781079", "bytes": "115058", "mt |
| `L1-30` | {"file_sha256_live": "852f1ff7ee36d173d49303e6d6e6090212bbbdb6ece3e08a9f227f3bce6cf9cd", "registered_sha256": "852f1ff7ee36d173d49303e6d6e6090212bbbdb6ece3e08a9f227f3bce6cf9cd", "file_bytes_unchanged": true, "authority_b |
| `L5-11` | {"before": {"sha256": "9f7b4be6d8eeb2888fb9b3df6dd18ac7d1db7bfdaf9bfcc1d90f60efcff6c820", "bytes": "5696"}, "after": {"sha256": "9f7b4be6d8eeb2888fb9b3df6dd18ac7d1db7bfdaf9bfcc1d90f60efcff6c820", "bytes": "5696", "mtime" |
| `L6-01` | {"before": {"sha256": "354403dae664c6584cd9e4123547cf812528905dd87e9d747f481fe75f40fc40", "bytes": "23643"}, "after": {"sha256": "354403dae664c6584cd9e4123547cf812528905dd87e9d747f481fe75f40fc40", "bytes": "23643", "mtim |
| `L6-37` | {"sha256": "ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87", "live_sha256": "ce6416126252663ff8be794fe985500a284876c3d15b2420359656c1bb4afd87", "re_recorded": false} |
| `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` | new 27-column instance row `CHG-20261022-ONFIBRO-ACTIVATION` (instance sha256 `1eeac36d252f03bd9c02f1b63d6c82e784c2f6262627a72fe152ab5700c534cb`) |
| `docs/RELEASE_IDENTITY.json` + `docs/RELEASE_MANIFEST_v1.json` | re-taken against the staged tree in the same commit (`scripts/release_identity.py --take --source index`, then `--check`) |
| `docs/W3_MANIFEST.sha256` | re-frozen LAST, after the registry's final bytes existed |
| `docs/VERIFY_CONTRACT.md` | §5.5 registers the default-ON behaviour as a gate precondition (the G6 rule R8 requirement), including the compatibility item |

The carrier's own file is byte-unchanged, so its row keeps its sha; the row's authority text now reads: ACTIVATED 2026-10-22 on the default `all` route by PI decision (activation card t_42df17c2, verbatim authority "载体并进默认路由"); registered as an ACTIVATION, not an audit pass. Kill switch EYEKB_ACT_ONFIBRO=0 restores the pre-flip default byte-for-byte (measured). Rollback = restore the empty whitelist.

## 7. Gates

**Author tree, repository chain** (`out/REPO_GATES.log`): G3 verify_repro 41/41, G4 three byte anchors (re-anchored, 3/3), G5 registry, G6 change control, G7 ontology layer, G8 ontology portability -- `gates=6 failed=0 (CHAIN PASS)`.

**This wave's gate** (16 checks, `out/GATE.json`): verdict **PASS**, failed = [].

**Clean clone** (`out/CLEAN_CLONE_CHECK.json`): commit under test `6cdf7ae`; repository chain inside the clone rc=0; wave gate inside the clone verdict PASS; author-vs-clone fidelity 112 files compared, 0 differing; overall **PASS**.

## 8. Incidents, corrections and what is NOT claimed

1. **`G4` failed before it was re-anchored**, and the first `G5` run failed on a row this card had invalidated (`docs/VERIFY_CONTRACT.md` in the gate inventory) plus the G4 expectation row `L5-11`. Both are recoverable registrations rather than criterion changes; the criteria were not weakened, and the G4 re-anchor carries its own control (section 5).
2. **The predecessor wave's "the default route is byte-identical in every state" is now false by construction** -- that was true while the whitelist was empty. With the carrier on the route, every response that carries the provenance/soft-flag disclosure fields moves; the report says so rather than quoting the old sentence.
3. **The compatibility item is unresolved.** Baseline not re-recorded (deliberate); owner decision pending between "re-record with attribution" (the repo's own rule for an intended digest move) and "narrow the disclosure for libraries that contribute no candidate".
4. **Not claimed:** no accuracy improvement is claimed and no validation is reported; the reading is in-sample on the volumes the carrier was selected on. The carrier is a coarse family-level answer and it clears the >=2 shared-gene bar only at the bar; the two admitted window genes carry 3 and 2 corpus chunks respectively (the predecessor wave's disclosure stands).
5. **Not pushed.** The commit is local; the coordinator pushes after verification. The exact hash is recorded in `out/CLEAN_CLONE_CHECK.json` (`commit` / `clone_of_commit`), which is the artefact the clone step writes -- so this report cannot disagree with the commit it describes.

## 9. Where each number comes from

| reading | command | artefact |
|---|---|---|
| pre-image and ordering | `python3 scripts/l0_preimage.py` | `out/PREIMAGE.json` |
| the flip and its diff census | `python3 scripts/l1_flip_apply.py` | `out/FLIP.json` |
| four-arm measurement | `python3 scripts/l2_flip_measure.py` | `out/FLIP_MEASUREMENT.json` |
| kill switch, delta census, tool panel | `python3 scripts/l3_default_face.py` | `out/DEFAULT_FACE.json` |
| what moved, per JSON path | `python3 scripts/l3c_field_diff.py` | `out/FIELD_DIFF.json` |
| G4 re-anchor and its control | `python3 scripts/g4_reanchor.py` | `out/G4_REANCHOR.json` |
| the precondition registration | `python3 scripts/l5_verify_contract.py` | `out/VERIFY_CONTRACT_UPDATE.json` |
| the registry re-takes | `python3 scripts/l4_registry_rows.py` | `out/REGISTRY_UPDATE.json` |
| the change-control row | `python3 scripts/l6_g6_row.py` | `out/G6_ROW.json` |
| the repository chain | `bash tests/run_gates.sh` (inside the clean clone too) | `out/REPO_GATES.log` |
| manifest, gate, clone check | `scripts/m2_manifest.py`, `scripts/m1_gate.py`, `scripts/m4_clone_check.sh` | `out/MANIFEST.sha256`, `out/GATE.json`, `out/CLEAN_CLONE_CHECK.json` |

English for everything that mirrors into the repository; every number carries the command that produced it; `NOT_RUN` and missing preconditions are never reported as pass.
