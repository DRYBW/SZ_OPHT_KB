# Uplift measurement: the two shipped changes, re-measured on the tree as it stands

Measured u1_uplift.py on the recorded query set: **28 volumes, 721 clusters, 1,495,330 cells**.
Each arm replays the same recorded queries through the live router with a declared switch
overlay; the routing layer and the grading ruler are imported read-only from
`docs/plans/noregr_20261022`. Nothing outside this directory is written.

Reading of the grades: `consistent` the candidate resolves to the same Cell Ontology class as
the reference label; `related` a coarser or finer class in the same lineage; `inconsistent` a
class outside the reference lineage; `mixed` no single reading for the cluster.

## 1. Headline

| arm | what it isolates | consistent before % | consistent after % | delta pp | clusters gained | clusters moved | cells moved | gate verdict |
|---|---|---|---|---|---|---|---|---|
| C2 | C2 tissue-scope narrowing alone | 40.980 | 41.061 | +0.081 | +2 | 91 | 158,160 | PASS_ATTRIBUTED |
| C1 | C1 carrier library on/off | 41.061 | 42.679 | +1.618 | +6 | 45 | 111,247 | PASS |
| C0 | C0 pre-narrowing baseline -> today's default | 40.980 | 42.679 | +1.699 | +8 | 126 | 258,425 | PASS |

The `before` value of C0 is the arm with **both** switches off, i.e. the state before the
tissue-scope narrowing and before the carrier. C2 holds the carrier off in both arms so that
the narrowing is measured on its own; C1 flips only the carrier on the narrowed tree.
C2 and C1 add up to C0 in the `consistent` share, which is the check that the decomposition
is complete.

## 2. Per-volume detail

### C2 tissue-scope narrowing alone, carrier held OFF on both arms

Before arm `{"env": {"EYEKB_TISSUE_SCOPE": "0", "EYEKB_ACT_ONFIBRO": "0"}}`, after arm `{"env": {"EYEKB_TISSUE_SCOPE": "1", "EYEKB_ACT_ONFIBRO": "0"}}`.

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---|---|---|---|---|
| consistent | 40.980 | 41.061 | +0.081 | 291 | 293 |
| related | 16.785 | 17.232 | +0.447 | 84 | 89 |
| inconsistent | 21.774 | 19.219 | -2.555 | 193 | 164 |
| mixed | 20.461 | 22.488 | +2.027 | 153 | 175 |

Volumes whose `consistent` share moved (5 of 28):

| volume | before % | after % | delta pp |
|---|---|---|---|
| CX11_posterior_eye_atlas | 23.179 | 26.830 | +3.651 |
| CX13_central_cornea | 5.116 | 6.629 | +1.513 |
| CX12_ocular_surface_snRNA | 34.612 | 35.997 | +1.385 |
| CX13_TM_corneal_scleral | 39.036 | 38.999 | -0.037 |
| CX15_optic_nerve_all | 44.403 | 41.873 | -2.530 |

Largest movers by cluster:

| volume | cluster | cells | reference type | before top | after top | grade |
|---|---|---|---|---|---|---|
| PRE_OA-D002 | 12 | 4,512 | lymphocyte | retina_interneuron::BC | None | inconsistent -> mixed |
| CX13_ciliary_body | 0 | 3,800 | pigmented ciliary epithelial cell | retina_interneuron::HC | None | inconsistent -> mixed |
| CX11_posterior_eye_atlas | 0 | 3,609 | oligodendrocyte | retina_interneuron::BC | None | inconsistent -> mixed |
| PRE_GSE199013 | 8 | 3,115 | ciliary muscle cell | retina_interneuron::AC | ciliary muscle cell | inconsistent -> related |
| PRE_GSE199013 | 21 | 2,843 | macrophage | Astro | None | inconsistent -> mixed |
| CX11_posterior_eye_atlas | 1 | 2,663 | oligodendrocyte | retina_interneuron::BC | None | inconsistent -> mixed |
| CX14_TM_ciliary_snRNA | 11 | 2,497 | myelinating Schwann cell | retina_interneuron::BC | None | inconsistent -> mixed |
| CX11_posterior_eye_atlas | 2 | 2,387 | oligodendrocyte precursor cell | retina_interneuron::AC | None | inconsistent -> mixed |

### C1 carrier library on/off, today's tree (single variable)

Before arm `{"env": {"EYEKB_ACT_ONFIBRO": "0"}}`, after arm `{"env": {"EYEKB_ACT_ONFIBRO": "1"}}`.

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---|---|---|---|---|
| consistent | 41.061 | 42.679 | +1.618 | 293 | 299 |
| related | 17.232 | 17.232 | +0.000 | 89 | 89 |
| inconsistent | 19.219 | 18.955 | -0.264 | 164 | 162 |
| mixed | 22.488 | 21.134 | -1.354 | 175 | 171 |

Volumes whose `consistent` share moved (6 of 28):

| volume | before % | after % | delta pp |
|---|---|---|---|
| CX14_TM_ciliary_snRNA | 34.716 | 46.839 | +12.123 |
| CX11_posterior_eye_atlas | 26.830 | 36.134 | +9.304 |
| PRE_GSE199013 | 36.859 | 43.376 | +6.517 |
| CX08_RPE_choroid_snRNA | 31.834 | 37.314 | +5.480 |
| CX15_optic_nerve_all | 41.873 | 44.403 | +2.530 |
| CX13_TM_corneal_scleral | 38.999 | 41.306 | +2.307 |

Largest movers by cluster:

| volume | cluster | cells | reference type | before top | after top | grade |
|---|---|---|---|---|---|---|
| CX14_TM_ciliary_snRNA | 1 | 9,469 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |
| CX13_TM_corneal_scleral | 12 | 5,988 | fibroblast | Fibroblast | onfibro_v13::Fibroblast | consistent -> consistent |
| CX12_ocular_surface_snRNA | 4 | 5,657 | keratocyte | Fibroblast | onfibro_v13::Fibroblast | consistent -> consistent |
| CX11_posterior_eye_atlas | 12 | 5,089 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |
| CX08_RPE_choroid_snRNA | 1 | 3,862 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |
| CX13_ciliary_body | 5 | 3,464 | fibroblast | Fibroblast | onfibro_v13::Fibroblast | consistent -> consistent |
| PRE_GSE199013 | 4 | 2,768 | fibroblast | Pericyte | onfibro_v13::Fibroblast | inconsistent -> consistent |
| CX15_optic_nerve_all | 31 | 1,822 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |

### C0 pre-narrowing baseline -> today's default

Before arm `{"env": {"EYEKB_TISSUE_SCOPE": "0", "EYEKB_ACT_ONFIBRO": "0"}}`, after arm `{"env": {"EYEKB_TISSUE_SCOPE": "1", "EYEKB_ACT_ONFIBRO": "1"}}`.

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---|---|---|---|---|
| consistent | 40.980 | 42.679 | +1.699 | 291 | 299 |
| related | 16.785 | 17.232 | +0.447 | 84 | 89 |
| inconsistent | 21.774 | 18.955 | -2.819 | 193 | 162 |
| mixed | 20.461 | 21.134 | +0.673 | 153 | 171 |

Volumes whose `consistent` share moved (7 of 28):

| volume | before % | after % | delta pp |
|---|---|---|---|
| CX11_posterior_eye_atlas | 23.179 | 36.134 | +12.955 |
| CX14_TM_ciliary_snRNA | 34.716 | 46.839 | +12.123 |
| PRE_GSE199013 | 36.859 | 43.376 | +6.517 |
| CX08_RPE_choroid_snRNA | 31.834 | 37.314 | +5.480 |
| CX13_TM_corneal_scleral | 39.036 | 41.306 | +2.270 |
| CX13_central_cornea | 5.116 | 6.629 | +1.513 |
| CX12_ocular_surface_snRNA | 34.612 | 35.997 | +1.385 |

Largest movers by cluster:

| volume | cluster | cells | reference type | before top | after top | grade |
|---|---|---|---|---|---|---|
| CX14_TM_ciliary_snRNA | 1 | 9,469 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |
| CX13_TM_corneal_scleral | 12 | 5,988 | fibroblast | Fibroblast | onfibro_v13::Fibroblast | consistent -> consistent |
| CX12_ocular_surface_snRNA | 4 | 5,657 | keratocyte | Fibroblast | onfibro_v13::Fibroblast | consistent -> consistent |
| CX11_posterior_eye_atlas | 12 | 5,089 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |
| PRE_OA-D002 | 12 | 4,512 | lymphocyte | retina_interneuron::BC | None | inconsistent -> mixed |
| CX08_RPE_choroid_snRNA | 1 | 3,862 | fibroblast | None | onfibro_v13::Fibroblast | mixed -> consistent |
| CX13_ciliary_body | 0 | 3,800 | pigmented ciliary epithelial cell | retina_interneuron::HC | None | inconsistent -> mixed |
| CX11_posterior_eye_atlas | 0 | 3,609 | oligodendrocyte | retina_interneuron::BC | None | inconsistent -> mixed |

## 3. What the aggregate hides

- **C2**: 2 cluster(s) left `consistent`, 4 entered it, and 22 cluster(s) (30,304 cells) were
  left with no named candidate at all.
  - left `consistent`: CX15_optic_nerve_all cluster 31, 1,822 cells, reference `fibroblast`; candidate `Limbus_Sclera_fibroblast_C1` -> `None`,
    graded consistent -> mixed with CL reading `same_cl` -> `abstain`.
  - left `consistent`: CX13_TM_corneal_scleral cluster 3, 1,430 cells, reference `conjunctival epithelial cell`; candidate `Conj_epithelium_basal` -> `conjunctival epithelial cell`,
    graded consistent -> inconsistent with CL reading `same_cl` -> `unmappable_pred`.
- **C1**: 0 cluster(s) left `consistent`, 6 entered it, and 0 cluster(s) (0 cells) were
  left with no named candidate at all.
- **C0**: 1 cluster(s) left `consistent`, 9 entered it, and 21 cluster(s) (28,482 cells) were
  left with no named candidate at all.
  - left `consistent`: CX13_TM_corneal_scleral cluster 3, 1,430 cells, reference `conjunctival epithelial cell`; candidate `Conj_epithelium_basal` -> `conjunctival epithelial cell`,
    graded consistent -> inconsistent with CL reading `same_cl` -> `unmappable_pred`.

## 4. Attribution of every fall

A fall in any volume's cell-weighted `consistent` share may not be reported as complete unless
it is attributed, in the artefact, to a named cluster, a named cause and a named row or panel.

- **C2** (verdict PASS_ATTRIBUTED):
  - `CX13_TM_corneal_scleral` -0.037 pp (39.036% -> 38.999%): cluster 3 (1,430 cells, reference cell type = conjunctival epithelial cell); cause: the narrowing moves the top candidate to a label string supplied by a library the knowledge base does not own; the label is `conjunctival epithelial cell`, which is the reference string augmented exactly, but the grading layer cannot resolve it to a CL id (after_cl = unmappable_pred) whereas the previous label `Conj_epithelium_basal` did resolve (before_cl = same_cl). The ranking did not degrade: this is a mapping-layer artefact of the ruler, counted here rather than hidden; row/panel: the label-to-CL knowledge source used by the predicate side of the ruler (not the marker panel)
  - `CX15_optic_nerve_all` -2.530 pp (44.403% -> 41.873%): cluster 31 (1,822 cells, reference cell type = fibroblast, family = fibro); cause: the optic-nerve declaration excludes the class `Limbus_Sclera_fibroblast_C1`, which was the only reachable carrier for the fibro family in that tissue (before: n_ranked = 1, n_shared = 1, grade consistent / same_cl; after: n_ranked = 0, no candidate, grade mixed / abstain); row/panel: the optic_nerve record's `excluded_classes` row for `Limbus_Sclera_fibroblast_C1` in the tissue crosswalk (`eyekb_core._tissue_crosswalk()`)
- **C1**: no volume's `consistent` share fell (verdict PASS).
- **C0**: no volume's `consistent` share fell (verdict PASS).

## 5. Limits of this measurement

1. **In-sample.** The carrier library was selected on these same volumes, so these readings
   describe the recorded set, not held-out data. They are not an accuracy estimate.
2. **The reference labels are a consensus, not an independent truth set.** The grades report
   agreement with those labels; they do not certify that a call is biologically correct.
3. **`consistent` is a mapping-dependent grade.** One cluster in C2 leaves `consistent` while
   its new candidate string is *identical* to the reference string, because the grading layer
   cannot resolve that label to a Cell Ontology id (`unmappable_pred`). Counted, not hidden.
4. **The window lever is not in these arms.** The production default recall window stays at 10;
   the 30-window variant is a separate arm and is not part of any number above.
5. **The harness's per-dataset `cells_lost` block is global, not per-dataset** -- in the frozen
   harness the same transition counts are repeated under each dropped volume. Read the
   per-cluster table for cluster-level detail; the harness was not edited.
6. **Switch handling.** `scripts/switch_coverage/arm_hygiene.py` derives the switch list from
   the source and `preflight()` refuses to run a comparison whose arms are not in different
   states; `tests/gate_switch_coverage.py` enforces the same rule over every report on disk.

## 6. Re-deriving these numbers

```
cd <repo-root>/docs/plans/uplift_20261022   # this wave, relative to the repository root
export PYTHONHASHSEED=0 NR_NET_AUDIT_LOG=$PWD/logs/net_audit.log
/usr/bin/python3 scripts/u1_uplift.py        # writes out/UPLIFT_MEASUREMENT.json
/usr/bin/python3 scripts/u2_report.py        # writes this file
/usr/bin/python3 tests/gate_switch_coverage.py   # switch coverage and arm hygiene
```

The harness's own pre-image travels inside the measurement document, so any reported number can
be traced back to the harness revision that produced it.
