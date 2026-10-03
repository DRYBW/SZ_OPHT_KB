# Developmental Axis Row-by-Row Disclosure Table (KB2c t_be336eee — Red Line 2: Silent omission prohibited)

> schema: eyekb-stage-disclosure/1.0 | Generated: 2026-09-23 | Generator: build_baselines.py (KB1v2 t_16c3e020; KB2c developmental axis single column t_be336eee)
> Adult main archive = donor_age>=18y (Adjudication Q2); The table below lists all non-adult donor units for each filled entry.
> Measured: Fetal nucleus count in 4 h5ad sources = 0 —— The red-line lexical surface 'contains fetal donors' actually refers to mixed newborn/child/adolescent samples, which have been entirely excluded from the main archive.

## retina (Main archive organism_stage=adult)
| Excluded Donor | organism_stage | UBERON Original Value | Nucleus Count | Rule |
|---|---|---|---|---|
| `BCM_23_0131` | developing | 16-year-old stage | 26,671 | Numeric age 16y vs threshold 18y |
| `BCM_22_0769` | developing | 11-year-old stage | 20,466 | Numeric age 11y vs threshold 18y |
| `MMD_23_21999` | developing | 17-year-old stage | 12,347 | Numeric age 17y vs threshold 18y |
| `MMD_23_21623` | developing | 15-year-old stage | 11,892 | Numeric age 15y vs threshold 18y |
| `MMD_23_17738` | developing | 10-year-old stage | 10,625 | Numeric age 10y vs threshold 18y |
| `MMD_23_20181` | developing | 16-year-old stage | 9,012 | Numeric age 16y vs threshold 18y |
| `MMD_23_22486` | developing | 3-year-old stage | 8,925 | Numeric age 3y vs threshold 18y |

## ocular_surface (Main archive organism_stage=adult)
| Excluded Donor | organism_stage | UBERON Original Value | Nucleus Count | Rule |
|---|---|---|---|---|
| `BCM_22_0496` | developing | 2-year-old stage | 27,157 | Numeric age 2y vs threshold 18y |
| `BCM_22_0698` | developing | newborn stage (0-28 days) | 25,018 | Newborn/infant early postnatal → developing (Adjudication Q2) |
| `BCM_22_0485` | developing | 1-year-old stage | 23,364 | Numeric age 1y vs threshold 18y |
| `BCM_22_0769` | developing | 11-year-old stage | 22,308 | Numeric age 11y vs threshold 18y |
| `BCM_21_0999` | developing | 10-year-old stage | 15,667 | Numeric age 10y vs threshold 18y |
| `shi_donor1` | developing | 13-year-old stage | 8,281 | Numeric age 13y vs threshold 18y |
| `chen_donor1` | developing | postnatal stage | 6,249 | Postnatal → developing (Adjudication Q1 mapping) |
| `chen_donor2` | developing | postnatal stage | 4,301 | Postnatal → developing (Adjudication Q1 mapping) |
| `BCM_23_0131` | developing | 16-year-old stage | 2,245 | Numeric age 16y vs threshold 18y |

## optic_nerve (Main archive organism_stage=adult)
| Excluded Donor | organism_stage | UBERON Original Value | Nucleus Count | Rule |
|---|---|---|---|---|
| `MMD_23_17738` | developing | 10-year-old stage | 18,998 | Numeric age 10y vs threshold 18y |
| `BCM_22_0698` | developing | newborn stage (0-28 days) | 15,177 | Newborn/infant early postnatal → developing (Adjudication Q2) |
| `BCM_23_0491` | developing | 16-year-old stage | 14,845 | Numeric age 16y vs threshold 18y |
| `MMD_23_22486` | developing | 3-year-old stage | 13,748 | Numeric age 3y vs threshold 18y |
| `MMD_23_21623` | developing | 15-year-old stage | 13,317 | Numeric age 15y vs threshold 18y |
| `BCM_23_0131` | developing | 16-year-old stage | 10,136 | Numeric age 16y vs threshold 18y |
| `MMD_23_21999` | developing | 17-year-old stage | 8,175 | Numeric age 17y vs threshold 18y |
| `BCM_22_0769` | developing | 11-year-old stage | 3,443 | Numeric age 11y vs threshold 18y |
| `MMD_23_20181` | developing | 16-year-old stage | 2,231 | Numeric age 16y vs threshold 18y |

## trabecular_meshwork (Main record organism_stage=adult)

## ciliary_body (Main record organism_stage=adult)
| Excluded Donor | organism_stage | UBERON Original Value | Nucleus Count | Rule |
|---|---|---|---|---|
| `BCM_23_0491` | developing | 16-year-old stage | 19,530 | Numeric age 16y vs threshold 18y |
| `MMD_23_21999` | developing | 17-year-old stage | 17,548 | Numeric age 17y vs threshold 18y |
| `MMD_23_20181` | developing | 16-year-old stage | 12,531 | Numeric age 16y vs threshold 18y |
| `MMD_23_21623` | developing | 15-year-old stage | 11,508 | Numeric age 15y vs threshold 18y |

## RPE (Main record organism_stage=unknown)
- unknown disclosure: GSE158629 cells_meta (all 4 donors) — no age column → silent assignment to adult prohibited (Red Line 2); Literature level: GEO: 'RPE cells were isolated from four adult human donor eyes'

