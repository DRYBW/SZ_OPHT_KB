# CITTITLE — 反事实证明：改前 / 改后（口径并报，禁只报高的那个）

卡 `t_d8e7f2d4`　单位 = 冻结 registry 中**去重被引论文**（分母 825）；引用记录 3993 条。

| 口径 | 规范化 | 改前对上 | 改前率 | 改后对上 | 改后率 | 增量 |
|---|---|---|---|---|---|---|
| A_strict_full_equality | N1_raw | 247 | 29.94% | 825 | 100.0% | +578 |
| A_strict_full_equality | N2_display_stripped | 248 | 30.06% | 825 | 100.0% | +577 |
| B_prefix40 | N1_raw | 369 | 44.73% | 825 | 100.0% | +456 |
| B_prefix40 | N2_display_stripped | 370 | 44.85% | 825 | 100.0% | +455 |

## 逐条原因（改前未对上，按口径展开）

- **A_strict_full_equality / N1_raw**：未对上 578 条 —— `TITLE_EMPTY_CITED` 455、`TITLE_CAPPED_120` 122、`TITLE_DISPLAY_ARTIFACT` 1
- **A_strict_full_equality / N2_display_stripped**：未对上 577 条 —— `TITLE_EMPTY_CITED` 455、`TITLE_CAPPED_120` 122
- **B_prefix40 / N1_raw**：未对上 456 条 —— `TITLE_EMPTY_CITED` 455、`TITLE_CAPPED_120` 1
- **B_prefix40 / N2_display_stripped**：未对上 455 条 —— `TITLE_EMPTY_CITED` 455

## 非圆形证据（关键：改后 100% 是同源回填的构造结果，不构成「两库一致」的证据）

| 交叉语料 | 口径 | 臂 | 对上/分母 | 率 |
|---|---|---|---|---|
| v2.4.2_2026-09 | A_strict_full_equality | pre | 247/825 | 29.94% |
| v2.4.2_2026-09 | A_strict_full_equality | post_from_primary | 825/825 | 100.0% |
| v2.4.2_2026-09 | B_prefix40 | pre | 369/825 | 44.73% |
| v2.4.2_2026-09 | B_prefix40 | post_from_primary | 825/825 | 100.0% |
| v2.4.2_2026-09 | A_strict_full_equality_N2 | pre | 248/825 | 30.06% |
| v2.4.2_2026-09 | A_strict_full_equality_N2 | post_from_primary | 825/825 | 100.0% |
| v2.4.2_2026-09 | B_prefix40_N2 | pre | 370/825 | 44.85% |
| v2.4.2_2026-09 | B_prefix40_N2 | post_from_primary | 825/825 | 100.0% |
| v2.6-dev_2026-10 | A_strict_full_equality | pre | 247/825 | 29.94% |
| v2.6-dev_2026-10 | A_strict_full_equality | post_from_primary | 825/825 | 100.0% |
| v2.6-dev_2026-10 | B_prefix40 | pre | 369/825 | 44.73% |
| v2.6-dev_2026-10 | B_prefix40 | post_from_primary | 825/825 | 100.0% |
| v2.6-dev_2026-10 | A_strict_full_equality_N2 | pre | 248/825 | 30.06% |
| v2.6-dev_2026-10 | A_strict_full_equality_N2 | post_from_primary | 825/825 | 100.0% |
| v2.6-dev_2026-10 | B_prefix40_N2 | pre | 370/825 | 44.85% |
| v2.6-dev_2026-10 | B_prefix40_N2 | post_from_primary | 825/825 | 100.0% |

## 同 join 的旁证控制（若 pmid↔paper_id 接错，这里必然先塌）

- 期刊一致：820/825
- 年份一致：825/825
- 改前**本来就完整**的题名（非空、非 120）与语料严格全等：243/243
- 改前**被截断**的题名在 40 字前缀口径下与语料相等：115/115

## 记录级归因（改前缺陷形态，逐条计数）

- EMPTY: 2429
- FULL_OK: 1053
- CAPPED_120: 509
- GENUINE_120: 2

## 后修未对上（0 行；空表 = 无行可登，不是静默丢弃）

