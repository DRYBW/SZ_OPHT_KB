# Disease × Tissue/Material × Developmental Stage Matrix (Thin-Layer Architecture Overview)

> schema: eyekb-disease-matrix/1.1 | Generated: 2026-09-23 | Card: t_be336eee | Generator: build_disease_v2.py (KB1v2 t_16c3e020)
> General ophthalmology architecture (PI 2026-09-23): Disease entries = Thin layers overlaid on tissue baselines (kb/baselines/); **Batch expansion paused** (Astra T6) — First validate reading benefits with one PDR membrane cell (PRIOR_DIFF), then incrementally expand by sample entry.
> **KB2c Developmental Axis (Adjudication Q3)**: Cell key = (disease, material, organism_stage) three keys; Current network all cells = adult; Developmental/fetal samples do not enter adult disease cells (PI directive: 'Even a single tissue is incorrect').

| Disease | Tissue/Material Cell | Developmental Stage | development_axis (KB3) | Status | Description |
|---|---|---|---|---|---|
| PDR | fibrovascular_membrane | adult | **FILLED (Example Cell)** | PDR__fibrovascular_membrane.md |
| PDR | vitreous | adult | **placeholder** | Qualitative anchor exists (B: PMID 39220810, T 91.6%); Independent entry below minimum usability threshold — temporarily recorded in example cell cross_material_note |
| PDR | retina_adjacent | adult | **placeholder** | Grade B literature anchor (MG_EARLY_DR/DR_RETINA_SC/MULLER_REDD1) |
| NPDR/DME | retina | adult | **placeholder** | Different materials from different PDR stages, must not be merged (T6: do not synthesize a single composition baseline) |
| nAMD/GA | RPE_choroid | adult | **placeholder** | Tissue-side RPE/choroid baseline is currently skeletal → backfill W1 skeleton before addressing disease cells |
| RRD | subretinal/ERM membrane | adult | **placeholder** | GSE165784 RRD-ERM n=1 —— Single sample can only report 'observed in this sample', no universal entry created (T3) |
| ERM (idiopathic) | membrane | adult | **placeholder** | Same material as PDR membrane but different disease — reuse concept ID, establish separate cell |
| glaucoma | optic_nerve_RGC | adult | **placeholder** | Tissue-side optic_nerve skeleton mapping backfilled (HRA006282 locally computable) |
| keratoconus | cornea | adult | **placeholder** | Tissue-side ocular_surface baseline filled → lowest evidence threshold for this cell |
| Fuchs/endothelial decompensation | corneal_endothelium | adult | **placeholder** | D002 endothelial layer has only 404 cells, expand tissue baseline first |
| uveitis (intermediate) | vitreous | adult | **placeholder** | Shares material concept with PDR__vitreous |
| cataract | lens | adult | **placeholder** | Tissue-side lens skeleton = LEC domain adjudication |

## Architecture Rules

1. Decouple tissue baselines from disease entries: Disease cells do not repeat tissue proportions, only write expected/flags/signatures for Disease×Material (identity+status two levels).
2. Same disease different materials = different cells (PDR membrane ≠ PDR vitreous ≠ adjacent retina; Astra T2 sampling material anchoring).
3. Same material different diseases not merged (PDR membrane and idiopathic ERM membrane reuse concept ID but separate cells; T6).
4. Cell opening threshold = minimum usability standard for entries (see example cells), no specific evidence does not create subtype cells alone (T4/P4).
5. Each cell links to: Tissue baseline file ↔ RAG reason-tag (evidence_meta sidecar) ↔ Literature index page ↔ Concept table (W5 four-way link).
6. **Development axis listed separately (KB2c)**: Cell keys include organism_stage; Adult disease cells only accept adult materials, developmental stage disease samples (e.g., pediatric ROP membrane) establish new cells separately, prohibited from merging into adult cells (PI red line).

## KB3 Development Axis Reserved Cells (t_5425a7ca — establish cells only, do not fill content)

| Disease | Material Cell | development_axis | Status |
|---|---|---|---|
| ROP (Retinopathy of Prematurity) | developing_retina_vascular | **fetal_neonatal** | RESERVED —— Developmental axis vascular proliferative disease, never pooled/cross-referenced with PDR adult cells; Prerequisite for filling = developmental data/literature anchors + passing adjudication |

> Placeholder implementation for Architecture Rule 6: Adult cell array rows=12 remains unchanged (regression lock), reserved cells use independent key development_axis_reservations (dual lock).
