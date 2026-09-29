# PHASE-0 数据集核实表（SEURATPROBE t_5d18900e，2026-09-28 实测）

方法：全盘枚举 `<STORE>/data/` 193 个 h5ad（scripts/phase0_scan_obs.py → tables/phase0_h5ad_inventory.tsv），对 11 个候选逐 obs 列实测取值分布（scripts/phase0_pass2_detail.py → tables/phase0_pass2_detail.json），X/counts 层用抽样 20000 值判整数性（frac_int），物种用 var 索引前缀实测。证据全部落盘。

## 入选（成年眼组织 · 逐细胞作者级注释 · ≤20万细胞 · 有原始 counts）

| # | 数据集 | 文件实测 | 真值列（obs 实测） | 成年证据（obs 实测） | counts 证据（抽样实测） |
|---|--------|----------|--------------------|----------------------|--------------------------|
| DS1 | Shekhar 17 物种视网膜图谱人子集（Hahn & Shekhar，registry OA-D038/GSE237204 谱系，`shekhar_annotated/human_homo_sapiens_annotated.h5ad`） | 180,093 × 60,671（≤20万 ✓）| `shekhar_class` 逐细胞 7 类：RGC 81,085 / Rod 44,903 / AC 37,032 / MG 5,615 / BC 4,856 / HC 4,577 / Cone 2,025；作者级类注释（非分选池） | 图谱=成年脊椎动物视网膜（registry OA-D038 "Healthy / comparative evolution"）；obs 无 fetal 列；RGC 占 45% 与 Hahn 2024 RGC 富集设计一致 | X frac_int=1.0，min=1 max=707 → 原始整数 counts ✓；var 索引=gene symbol（WASH7P…），dup=0 |
| DS2 | Lukowski 2019 成人视网膜图谱（CELLxGENE 导出，盘上位 GSE137400/ 目录，成员身份按文件内容不按目录名） | 19,694 × 36,475 | `author_cell_type` 逐细胞 14 类：rod A/B/C 12,239 / bipolar A–D 2,070 / unannotated 3,248(EXCL) / Müller 612 / cone 583 / AC 281 / microglia 142 / RGC 63 / unspecified 456(EXCL) | `development_stage`：42-year 11,475 + 53-year 6,409 + 80-year 1,810 → 全部成年 ✓ | `raw/X` frac≈整数 counts ✓；var 自带 `feature_name` symbol ✓；has_raw=true |

MG 语义判定（DS1 `MG` = Müller 胶质而非小胶质，实测 per-cell 检出率 scripts/ds1_mg_probe.py）：
- DS1 MG 细胞 4000 抽样：RLBP1=0.423 GLUL=0.689 SLC1A3=0.455 vs C1QA=0.002 C1QB=0.005 CX3CR1=0.001 P2RY12=0.003 TMEM119=0.000 → Müller 确证；全数据集无小胶质类。kb 词条 MG=Müller 同义，直接可比。

## 排除（逐条实测理由）

| 候选 | 排除理由 |
|------|----------|
| GSE165784 / GSE160306 | PI 明令禁拿自家共识注释当答案（追加七A） |
| GSE135133/GSE135167（鼠 Shekhar） | 本地无 h5ad（仅原始矩阵），入 G2 需新下载 → 零下载纪律排除 |
| GSE155288（92,385 obs）| `developmental_stage_class` 列存在 → 发育/fetal 轴数据集，成年纪律排除 |
| GSE226108_*cellxgene（56K） | `cell_type` 单类=amacrine 56,507 + `suspension_enriched_cell_types=neuron` → 神经元富集分选池（AC0–AC29 亚型来自分选群内细分），且属 D001 训练池谱系（记忆 GSE226108⊂HRCA resub）→ 自家同源风险，排除 |
| GSE183320_choroid（30,416） | X frac_int=0（log 归一值）且无 raw/layers → 无原始 counts 起点，G2"同一起点(counts)"不成立，排除 |
| GSE289703 三个 uuid 文件（69K/99K/182K） | 混合供体含 newborn/1-month/11-year 与 "RPE_Fetal" 类；两文件为单谱系分块（纯 RPE 5 亚型 / 纯内皮 5 亚型）→ 违背"标准数据集逐细胞类型标签"本意且成年面需再切供体；GSE289703 构成（多研究拼接 isocor 型）溯源证据弱，排除（候选后备） |
| 0f7d022a_ocularsurface（147,484）| 成年 ✓（24–83 岁实测）author_cell_type 26 类 ✓ has_raw ✓，但为眼表面（角膜/结膜）组织且 D002 谱系 6/9 与 HOSCA 同源（本室 C4 裁定评估侧排除记录）；保留为后备不进本轮（跨引擎对照重点在眼内组织，本轮已足 2 集） |
| train_splits_v2/*、GSE210543_relabeled、GSE265774/query | `relabeled_*`/majorclass = 自家流水线产物（分选池/自家标签），非作者级 → 循环，排除（任务书要点明令） |
| >20 万细胞集（GSE226108_56K×2 文件超门槛等）| 单集 ≤20 万约束 |

## 双轨对照口径
- DS1×DS2 同为人（跨引擎对照同物种内 ✓）；选 2 集 ✓（任务书要求 ≥2）；零新下载 ✓。
- SingleR 参考采用"自建交叉参考"（DS2→注 DS1，DS1→注 DS2），理由：零下载（Monaco/HCA 官方参考在 ExperimentHub 需运行时新下载，违反零下载面）、同物种同组织、两集均为独立作者标注。
