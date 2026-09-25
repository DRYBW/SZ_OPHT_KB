# 发育轴逐行披露表 (KB2c t_be336eee — 红线2: 禁静默)

> schema: eyekb-stage-disclosure/1.0 | 生成: 2026-09-23 | 生成器: build_baselines.py (KB1v2 t_16c3e020; KB2c 发育轴单列 t_be336eee)
> adult 主档 = donor_age>=18y (裁定 Q2); 下表列出每个 filled 条的全部非 adult 供者单元。
> 实测: 4 个 h5ad 源胎儿期核数=0 —— 红线条面'含胎儿 donor'实为 newborn/儿童/青少年混入, 已全部剔出主档。

## retina (主档 organism_stage=adult)
| 被剔供者 | organism_stage | UBERON 原值 | 核数 | 规则 |
|---|---|---|---|---|
| `BCM_23_0131` | developing | 16-year-old stage | 26,671 | 数字年龄 16y vs 阈值 18y |
| `BCM_22_0769` | developing | 11-year-old stage | 20,466 | 数字年龄 11y vs 阈值 18y |
| `MMD_23_21999` | developing | 17-year-old stage | 12,347 | 数字年龄 17y vs 阈值 18y |
| `MMD_23_21623` | developing | 15-year-old stage | 11,892 | 数字年龄 15y vs 阈值 18y |
| `MMD_23_17738` | developing | 10-year-old stage | 10,625 | 数字年龄 10y vs 阈值 18y |
| `MMD_23_20181` | developing | 16-year-old stage | 9,012 | 数字年龄 16y vs 阈值 18y |
| `MMD_23_22486` | developing | 3-year-old stage | 8,925 | 数字年龄 3y vs 阈值 18y |

## ocular_surface (主档 organism_stage=adult)
| 被剔供者 | organism_stage | UBERON 原值 | 核数 | 规则 |
|---|---|---|---|---|
| `BCM_22_0496` | developing | 2-year-old stage | 27,157 | 数字年龄 2y vs 阈值 18y |
| `BCM_22_0698` | developing | newborn stage (0-28 days) | 25,018 | newborn/infant 产后早期→developing (裁定 Q2) |
| `BCM_22_0485` | developing | 1-year-old stage | 23,364 | 数字年龄 1y vs 阈值 18y |
| `BCM_22_0769` | developing | 11-year-old stage | 22,308 | 数字年龄 11y vs 阈值 18y |
| `BCM_21_0999` | developing | 10-year-old stage | 15,667 | 数字年龄 10y vs 阈值 18y |
| `shi_donor1` | developing | 13-year-old stage | 8,281 | 数字年龄 13y vs 阈值 18y |
| `chen_donor1` | developing | postnatal stage | 6,249 | postnatal→developing (裁定 Q1 映射) |
| `chen_donor2` | developing | postnatal stage | 4,301 | postnatal→developing (裁定 Q1 映射) |
| `BCM_23_0131` | developing | 16-year-old stage | 2,245 | 数字年龄 16y vs 阈值 18y |

## optic_nerve (主档 organism_stage=adult)
| 被剔供者 | organism_stage | UBERON 原值 | 核数 | 规则 |
|---|---|---|---|---|
| `MMD_23_17738` | developing | 10-year-old stage | 18,998 | 数字年龄 10y vs 阈值 18y |
| `BCM_22_0698` | developing | newborn stage (0-28 days) | 15,177 | newborn/infant 产后早期→developing (裁定 Q2) |
| `BCM_23_0491` | developing | 16-year-old stage | 14,845 | 数字年龄 16y vs 阈值 18y |
| `MMD_23_22486` | developing | 3-year-old stage | 13,748 | 数字年龄 3y vs 阈值 18y |
| `MMD_23_21623` | developing | 15-year-old stage | 13,317 | 数字年龄 15y vs 阈值 18y |
| `BCM_23_0131` | developing | 16-year-old stage | 10,136 | 数字年龄 16y vs 阈值 18y |
| `MMD_23_21999` | developing | 17-year-old stage | 8,175 | 数字年龄 17y vs 阈值 18y |
| `BCM_22_0769` | developing | 11-year-old stage | 3,443 | 数字年龄 11y vs 阈值 18y |
| `MMD_23_20181` | developing | 16-year-old stage | 2,231 | 数字年龄 16y vs 阈值 18y |

## trabecular_meshwork (主档 organism_stage=adult)

## ciliary_body (主档 organism_stage=adult)
| 被剔供者 | organism_stage | UBERON 原值 | 核数 | 规则 |
|---|---|---|---|---|
| `BCM_23_0491` | developing | 16-year-old stage | 19,530 | 数字年龄 16y vs 阈值 18y |
| `MMD_23_21999` | developing | 17-year-old stage | 17,548 | 数字年龄 17y vs 阈值 18y |
| `MMD_23_20181` | developing | 16-year-old stage | 12,531 | 数字年龄 16y vs 阈值 18y |
| `MMD_23_21623` | developing | 15-year-old stage | 11,508 | 数字年龄 15y vs 阈值 18y |

## RPE (主档 organism_stage=unknown)
- unknown 披露: GSE158629 cells_meta (全 4 donor) — 无年龄列 → 禁静默归 adult (红线2); 文献级: GEO: 'RPE cells were isolated from four adult human donor eyes'

