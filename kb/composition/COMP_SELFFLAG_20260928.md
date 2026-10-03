# COMP_SELFFLAG_20260928 — EXPECTED_COMPOSITION_v0 self-check flag report (read-only, outputs flags not conclusions)

> Card t_fa03e1d7 | Input: `EXPECTED_COMPOSITION_v0.json` × frozen on-disk artifacts (kb/baselines, plans/evalset frozen files, demo_gse165784 v2 consensus draft table)
> **⛔ This face is not wired. Flags = prompts for re-review, not annotation errors; wiring and activation require separate cards and approval (PI decision).**

## 0. Method
- Reconciliation targets: Ground truth composition of each member in the evaluation volume (Q1–Q9, ground truth = author-level/portal annotations or mapped_10class; not re-annotation by own clustering) + demo GSE165784 v2 Track B consensus annotation draft (disease material, demonstrating gate behavior).
- flag rules: pct < low → BELOW; pct > high → ABOVE; off-face identities (T / macrophage / fibroblast / progenitor …) → off_face_identity disclosure row; the proportion denominator is all cells of the dataset.
- Built-in reverse quality check clause: If flagged type proportion >20% in healthy public sets → honestly report "face too narrow = issue with the face definition, not the data".
- Out-of-domain axes (excluded from reverse quality check denominator): Q7 mouse (species axis), Q8 fetal (developmental axis), Q6 (same construction source as ocular surface = circular reference), Q9 demo (disease surgical material, usage_scope prohibits use as standard control).

## 1. Summary Flag Rate

| Dataset | Face | Cell Count | Flagged Rows/Face Rows | Flag Rate | Reverse Quality Check |
|---|---|---|---|---|---|
| Q1_Lukowski2019 | retina | 19,694 | 4/10 | 40.0% | TRIGGER(>20%) |
| Q2_GSE155288 | retina | 92,385 | 4/10 | 40.0% | TRIGGER(>20%) |
| Q3 | retina | 20,091 | 3/10 | 30.0% | TRIGGER(>20%) |
| Q4 | retina | 84,982 | 2/10 | 20.0% | under |
| Q5b | retina | 412,419 | 0/10 | 0.0% | under |
| Q7 | retina | 361,022 | 5/10 | 50.0% | not_counted(disease/development/circular) |
| Q8 | retina | 226,506 | 4/10 | 40.0% | not_counted(disease/development/circular) |
| Q6_D002_sub100k | ocular_surface | 100,000 | 1/9 | 11.1% | not_counted(disease/development/circular) |
| Q9_GSE165784_demo_v2 | retina | 10,069 | 7/10 | 70.0% | not_counted(disease/development/circulation) |

## 2. Flag Details (Row-by-Row Dataset × Cell Type)

| Dataset | Row | Observed % | Surface Interval [Low, High] | Status |
|---|---|---|---|---|
| Q1_Lukowski2019 | Rod | 62.15 | [22,58] | FLAG_ABOVE |
| Q1_Lukowski2019 | Cone | 2.96 | [1,7] | in_range |
| Q1_Lukowski2019 | BC | 10.51 | [12,33] | FLAG_BELOW |
| Q1_Lukowski2019 | AC | 1.43 | [6,28] | FLAG_BELOW |
| Q1_Lukowski2019 | HC | 0.0 | [1,8] | FLAG_BELOW |
| Q1_Lukowski2019 | RGC | 0.32 | [0,15] | in_range |
| Q1_Lukowski2019 | MG | 3.11 | [3,12] | in_range |
| Q1_Lukowski2019 | Astro | 0.0 | [0,2] | in_range |
| Q1_Lukowski2019 | Micro | 0.72 | [0,1] | in_range |
| Q1_Lukowski2019 | RPE | 0.0 | [0,1] | in_range |
| Q1_Lukowski2019 | OFF_FACE::OTHER | 18.81 | null(disclosure row) | off_face_identity |
| Q2_GSE155288 | Rod | 30.01 | [22,58] | in_range |
| Q2_GSE155288 | Cone | 2.1 | [1,7] | in_range |
| Q2_GSE155288 | BC | 32.61 | [12,33] | in_range |
| Q2_GSE155288 | AC | 2.41 | [6,28] | FLAG_BELOW |
| Q2_GSE155288 | HC | 0.69 | [1,8] | FLAG_BELOW |
| Q2_GSE155288 | RGC | 0.63 | [0,15] | in_range |
| Q2_GSE155288 | MG | 27.51 | [3,12] | FLAG_ABOVE |
| Q2_GSE155288 | Astro | 0.79 | [0,2] | in_range |
| Q2_GSE155288 | Micro | 1.83 | [0,1] | FLAG_ABOVE |
| Q2_GSE155288 | RPE | 0.0 | [0,1] | in_range |
| Q2_GSE155288 | OFF_FACE::Pericytes | 0.97 | null(disclosure row) | off_face_identity |
| Q2_GSE155288 | OFF_FACE::Endothelium | 0.45 | null(disclosure row) | off_face_identity |
| Q3 | Rod | 45.52 | [22,58] | in_range |
| Q3 | Cone | 1.05 | [1,7] | in_range |
| Q3 | BC | 15.7 | [12,33] | in_range |
| Q3 | AC | 2.47 | [6,28] | FLAG_BELOW |
| Q3 | HC | 0.73 | [1,8] | FLAG_BELOW |
| Q3 | RGC | 7.54 | [0,15] | in_range |
| Q3 | MG | 26.22 | [3,12] | FLAG_ABOVE |
| Q3 | Astro | 0.04 | [0,2] | in_range |
| Q3 | Micro | 0.31 | [0,1] | in_range |
| Q3 | RPE | 0.0 | [0,1] | in_range |
| Q3 | OFF_FACE::Other_mapped | 0.42 | null(disclosure row) | off_face_identity |
| Q4 | Rod | 8.32 | [22,58] | FLAG_BELOW |
| Q4 | Cone | 2.35 | [1,7] | in_range |
| Q4 | BC | 30.25 | [12,33] | in_range |
| Q4 | AC | 16.25 | [6,28] | in_range |
| Q4 | HC | 3.37 | [1,8] | in_range |
| Q4 | RGC | 13.42 | [0,15] | in_range |
| Q4 | MG | 23.41 | [3,12] | FLAG_ABOVE |
| Q4 | Astro | 1.35 | [0,2] | in_range |
| Q4 | Micro | 0.79 | [0,1] | in_range |
| Q4 | RPE | 0.0 | [0,1] | in_range |
| Q4 | OFF_FACE::Other_mapped | 0.48 | null(disclosure row) | off_face_identity |
| Q5b | Rod | 26.12 | [22,58] | in_range |
| Q5b | Cone | 5.64 | [1,7] | in_range |
| Q5b | BC | 25.72 | [12,33] | in_range |
| Q5b | AC | 27.4 | [6,28] | in_range |
| Q5b | HC | 3.56 | [1,8] | in_range |
| Q5b | RGC | 2.82 | [0,15] | in_range |
| Q5b | MG | 4.18 | [3,12] | in_range |
| Q5b | Astro | 0.14 | [0,2] | in_range |
| Q5b | Micro | 0.03 | [0,1] | in_range |
| Q5b | RPE | 0.02 | [0,1] | in_range |
| Q5b | OFF_FACE::glial cell | 4.37 | null(disclosure row) | off_face_identity |
| Q7 | Rod | 9.44 | [22,58] | FLAG_BELOW |
| Q7 | Cone | 1.34 | [1,7] | in_range |
| Q7 | BC | 40.91 | [12,33] | FLAG_ABOVE |
| Q7 | AC | 12.2 | [6,28] | in_range |
| Q7 | HC | 0.06 | [1,8] | FLAG_BELOW |
| Q7 | RGC | 22.59 | [0,15] | FLAG_ABOVE |
| Q7 | MG | 2.27 | [3,12] | FLAG_BELOW |
| Q7 | Astro | 0.0 | [0,2] | in_range |
| Q7 | Micro | 0.45 | [0,1] | in_range |
| Q7 | RPE | 0.11 | [0,1] | in_range |
| Q7 | OFF_FACE::nan | 10.27 | null(disclosure row) | off_face_identity |
| Q7 | OFF_FACE::Endothelial | 0.28 | null(disclosure row) | off_face_identity |
| Q7 | OFF_FACE::Pericyte | 0.08 | null(disclosure row) | off_face_identity |
| Q8 | Rod | 16.85 | [22,58] | FLAG_BELOW |
| Q8 | Cone | 4.12 | [1,7] | in_range |
| Q8 | BC | 9.05 | [12,33] | FLAG_BELOW |
| Q8 | AC | 11.65 | [6,28] | in_range |
| Q8 | HC | 4.21 | [1,8] | in_range |
| Q8 | RGC | 18.54 | [0,15] | FLAG_ABOVE |
| Q8 | MG | 2.89 | [3,12] | FLAG_BELOW |
| Q8 | Astro | 0.0 | [0,2] | in_range |
| Q8 | Micro | 0.0 | [0,1] | in_range |
| Q8 | RPE | 0.0 | [0,1] | in_range |
| Q8 | OFF_FACE::retinal progenitor cell | 32.48 | null(disclosure row) | off_face_identity |
| Q8 | OFF_FACE::OFFx cell | 0.21 | null(disclosure row) | off_face_identity |
| Q6_D002_sub100k | Corneal Endothelium | 0.07 | [0,1] | in_range |
| Q6_D002_sub100k | Endothelium | 5.75 | [0,9] | in_range |
| Q6_D002_sub100k | Epithelium | 43.36 | [7,71] | in_range |
| Q6_D002_sub100k | Fibroblasts | 39.91 | [12,45] | in_range |
| Q6_D002_sub100k | Immune Cells | 1.72 | [0,3] | in_range |
| Q6_D002_sub100k | Melanocytes | 1.23 | [0,3] | in_range |
| Q6_D002_sub100k | Pericytes | 6.5 | [0,5] | FLAG_ABOVE |
| Q6_D002_sub100k | Schwann Cells | 0.98 | [0,2] | in_range |
| Q6_D002_sub100k | Smooth Muscle Cells | 0.48 | [0,1] | in_range |
| Q9_GSE165784_demo_v2 | Rod | 0.0 | [22,58] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | Cone | 0.0 | [1,7] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | BC | 0.0 | [12,33] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | AC | 0.0 | [6,28] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | HC | 0.0 | [1,8] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | RGC | 0.0 | [0,15] | in_range |
| Q9_GSE165784_demo_v2 | MG | 0.0 | [3,12] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | Astro | 0.0 | [0,2] | in_range |
| Q9_GSE165784_demo_v2 | Micro | 17.4 | [0,1] | FLAG_ABOVE |
| Q9_GSE165784_demo_v2 | RPE | 0.0 | [0,1] | in_range |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_Inflam | 10.73 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_DAMLAM | 10.01 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_MHCII | 9.42 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mono_Nonclass | 8.24 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_DC | 7.85 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_Tissue | 7.0 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mono_Classical | 6.82 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_RRD | 4.3 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Myofibroblast | 3.69 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Tcell | 3.52 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Proliferating | 3.12 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Endo_vascular | 2.68 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Pericyte_vascular | 2.48 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::MG(candidate) | 1.62 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Plasma | 0.61 | null(disclosure row) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::pDC | 0.52 | null(disclosure row) | off_face_identity |

## 3. Reverse Quality Control Verification (Built-in Clauses)

- Healthy public datasets included in reverse quality control: Q1/Q2/Q3/Q4/Q5b (total 5, human normal adult retina).
- **Trigger (>20% types flagged): 3 instances —— Q1_Lukowski2019 40.0%; Q2_GSE155288 40.0%; Q3 30.0%**
- Reading (factual, not conclusion): Per built-in clauses, this first indicates that the **v0 interval is too narrow for cross-platform/cross-sampling-region/sorting designs**, a scope issue rather than a data issue. Specific attributions: Q1/Q2 = foveal sampling + scRNA cell suspension (main face archive uses snRNA nuclear suspension; Astra T2 has declared the two metrics are not directly comparable); Q3/Q4 = Macroglia signature splitting criteria + CD73/CD90 sorting design elevating BC/MG and suppressing Rods; Q5b shares origin with main face archive (HRCA internal composition), flag rate 0 represents an **upper bound of circular self-validation, not good generalization**.
- Disposition Recommendation (not auto-approved; submit to PI alongside text when activating separate cards/approvals): Stratify v1 intervals by suspension_type (nuclear/cell) and sampling region (fovea/peripheral/whole retina/sorted); or define the 'prior surface' as a conditional surface with design exemptions.

## 4. Off-Surface Identity Disclosure (Non-flagged, informational)

### Q8 Fetal (Out-of-Domain Axis Behavior Record)
- retinal progenitor cell is the largest class at 73,569/226,506=32.5% (denominator re-reviewed = def.classes total sum = full file) — The adult surface lacks a progenitor row, so all entries fall into off_face_identity; expected behavior of developmental material against the adult surface.

### Top Off-Surface Identity Rows per Dataset
- **Q1_Lukowski2019**: OTHER 18.81%
- **Q2_GSE155288**: Pericytes 0.97%; Endothelium 0.45%
- **Q3**: Other_mapped 0.42%
- **Q4**: Other_mapped 0.48%
- **Q5b**: glial cell 4.37%
- **Q7**: nan 10.27%; Endothelial 0.28%; Pericyte 0.08%
- **Q8**: retinal progenitor cell 32.48%; OFFx cell 0.21%
- **Q9_GSE165784_demo_v2**: Mac_Inflam 10.73%; Mac_DAMLAM 10.01%; Mac_MHCII 9.42%; Mono_Nonclass 8.24%; Mac_DC 7.85%; Mac_Tissue 7.0%; Mono_Classical 6.82%; Mac_RRD 4.3%

## 5. Declaration
- This report outputs only the flag list and proportion distribution; flags ≠ annotation errors; no existing annotations are judged correct or incorrect based on this report.
- this face is unwired, default OFF; wiring and activation require a separate task card and approval batch.
- Reproduction: `python3 scripts/build_expected_composition_v0.py && python3 scripts/selfcheck_comp_v0.py && python3 scripts/gen_md.py` (logs logs/selfcheck_run.log).
