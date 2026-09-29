# EXPECTED_COMPOSITION_v1 — 组成先验面 v1（条件层化；默认 OFF）

> 卡 t_37a35220 | 放行=USER_DIRECTIVE 追加八 | 规则预注册=PHASE0_INVENTORY_t_37a35220.md | v0 三件字节不动

> **⛔ 未接线；旗标=提示复核≠注释错误；激活永远归 PI。**

## 1. retina 条件层（建库/取材/分选策略；单元=donor×组织×富集，adult-only）

| 类 | v0 包络[低,高] | RC1 未分选全区域 A/B | RC2 未分选中央 A/B | RC3 未分选外周 A/B | RC4 分选/靶向 A/B |
|---|---|---|---|---|---|
| Rod | [22,58] | [32,66] / [28,66] (n=130) | [17,51] / [17,56] (n=82) | [62,70] / [28,70] (n=48) | [2,27] / [2,56] (n=80) |
| Cone | [1,7] | [2,6] / [1,7] (n=130) | [3,7] / [1,7] (n=82) | [2,4] / [1,7] (n=48) | [0,5] / [0,7] (n=80) |
| BC | [12,33] | [15,30] / [12,33] (n=130) | [21,33] / [12,33] (n=82) | [13,17] / [12,33] (n=48) | [0,18] / [0,33] (n=80) |
| AC | [6,28] | [5,11] / [5,28] (n=130) | [7,12] / [7,28] (n=82) | [4,7] / [4,28] (n=48) | [15,45] / [8,45] (n=80) |
| HC | [1,8] | [1,7] / [1,8] (n=130) | [3,9] / [1,9] (n=82) | [1,2] / [1,8] (n=48) | [0,1] / [0,8] (n=80) |
| RGC | [0,15] | [0,6] / [0,15] (n=130) | [2,9] / [2,15] (n=82) | [0,1] / [0,15] (n=48) | [0,69] / [0,69] (n=80) |
| MG | [3,12] | [6,13] / [3,13] (n=130) | [6,15] / [3,15] (n=82) | [5,10] / [3,12] (n=48) | [0,5] / [0,12] (n=80) |
| Astro | [0,2] | [0,2] / [0,2] (n=130) | [0,2] / [0,2] (n=82) | [0,1] / [0,2] (n=48) | [0,1] / [0,2] (n=80) |
| Micro | [0,1] | [0,1] / [0,1] (n=130) | [0,1] / [0,1] (n=82) | [0,1] / [0,1] (n=48) | [0,1] / [0,1] (n=80) |
| RPE | [0,1] | [0,0] / [0,1] (n=130) | [0,0] / [0,1] (n=82) | [0,0] / [0,1] (n=48) | [0,0] / [0,1] (n=80) |

注：A=严格供者带（预注册主口径），B=v0 公式逐字包络（后验敏感性）；A 本质=中央 50% 带，天然窄于 v0 三重包络——语义选择归 PI。

RC4 成员=NeuN+ FACS ∪ Chen_rgc ∪ Shekhar_GSE237204（baselines 盘上既有靶向设计声明）。

## 2. OB-3 分层反向质检复算（20% 线不动；判定只看预注册 R1A）

| 数据集 | 平台 | R0 v0 | R1A 层化(主) | R1B 包络(敏) | R2 单元均 A | R2 单元均 B | R1A 判定 |
|---|---|---|---|---|---|---|---|
| Q1_Lukowski2019 | cell | 4/10=40.0% | 4/10=40.0% | 3/10=30.0% | 4/10=40.0% | 3/10=33.3% | TRIGGER |
| Q2_GSE155288 | cell | 4/10=40.0% | 6/10=60.0% | 4/10=40.0% | 6/10=65.0% | 6/10=60.0% | TRIGGER |
| Q3 | smart-seq cell | 3/10=30.0% | 5/10=50.0% | 3/10=30.0% | 6/10=55.0% | 4/10=40.0% | TRIGGER |
| Q4 | cell+CD73/90分选 | 2/10=20.0% | 4/10=40.0% | 1/10=10.0% | 5/10=50.0% | 3/10=27.1% | TRIGGER |
| Q5b | nucleus | 0/10=0.0% | 4/10=40.0% | 1/10=10.0% | 4/10=36.9% | 2/10=24.6% | TRIGGER |

**R0 复现门 5/5 PASS（含 Q5b 0/10）。R1A 下 5/5 全部 TRIGGER → OB-3 目标 <20% 未达成，如实报缺口（§4+V1_VERDICT）。**

### 逐行归因（PERSISTS=三规则全旗 / NEWFLAG=仅严格层新增 / RESOLVED=层化消除）

| 数据集 | 行 | 观测% | v0 | A | B | verdict |
|---|---|---|---|---|---|---|
| Q1_Lukowski2019 | Rod | 62.15 | FLAG | ok | ok | RESOLVED_by_layering |
| Q1_Lukowski2019 | BC | 10.51 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q1_Lukowski2019 | AC | 1.43 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q1_Lukowski2019 | HC | 0.0 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q1_Lukowski2019 | MG | 3.11 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q2_GSE155288 | Rod | 30.01 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q2_GSE155288 | BC | 32.61 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q2_GSE155288 | AC | 2.41 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q2_GSE155288 | HC | 0.69 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q2_GSE155288 | MG | 27.51 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q2_GSE155288 | Micro | 1.83 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q3 | Cone | 1.05 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q3 | AC | 2.47 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q3 | HC | 0.73 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q3 | RGC | 7.54 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q3 | MG | 26.22 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q4 | Rod | 8.32 | FLAG | ok | ok | RESOLVED_by_layering |
| Q4 | BC | 30.25 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q4 | HC | 3.37 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q4 | MG | 23.41 | FLAG | FLAG | FLAG | PERSISTS_all_rules |
| Q4 | Astro | 1.35 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q5b | Rod | 26.12 | ok | FLAG | FLAG | NEWFLAG_under_strict_layer |
| Q5b | AC | 27.4 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q5b | MG | 4.18 | ok | FLAG | ok | NEWFLAG_under_strict_layer |
| Q5b | RPE | 0.02 | ok | FLAG | ok | NEWFLAG_under_strict_layer |

## 3. OB-2 眼表 类型×区域行

| 类型 | cornea | corneal endothelium | corneo-scleral junction | ocular surface region | sclera | v0 混合行[低,高] |
|---|---|---|---|---|---|---|
| Corneal Endothelium | [0,0] n=29 | gate-fail→v0 | [0,0] n=22 | gate-fail→v0 | [0,0] n=10 | [0,1] |
| Endothelium | [0,2] n=29 | gate-fail→v0 | [5,13] n=22 | gate-fail→v0 | [8,18] n=10 | [0,9] |
| Epithelium | [29,80] n=29 | gate-fail→v0 | [36,68] n=22 | gate-fail→v0 | [0,3] n=10 | [7,71] |
| Fibroblasts | [14,68] n=29 | gate-fail→v0 | [7,38] n=22 | gate-fail→v0 | [34,52] n=10 | [12,45] |
| Immune Cells | [0,2] n=29 | gate-fail→v0 | [0,3] n=22 | gate-fail→v0 | [0,5] n=10 | [0,3] |
| Melanocytes | [0,1] n=29 | gate-fail→v0 | [0,5] n=22 | gate-fail→v0 | [0,6] n=10 | [0,3] |
| Pericytes | [0,1] n=29 | gate-fail→v0 | [2,7] n=22 | gate-fail→v0 | [12,35] n=10 | [0,5] |
| Schwann Cells | [0,0] n=29 | gate-fail→v0 | [0,2] n=22 | gate-fail→v0 | [0,3] n=10 | [0,2] |
| Smooth Muscle Cells | [0,0] n=29 | gate-fail→v0 | [0,0] n=22 | gate-fail→v0 | [0,1] n=10 | [0,1] |

### Q6（D002 sub100k，adult-only 76,708 细胞）分区域重算

| 区域 | 评估行数 | 旗标 | 明细 |
|---|---|---|---|
| cornea | 0 | 0 | - |
| corneal endothelium (单独层, 仅 404 细胞) | 0 | 0 | - |
| corneo-scleral junction (limbus 区) | 9 | 1 | Smooth Muscle Cells 0.13% vs [0.0,0.0] FLAG_ABOVE |
| ocular surface region (混合) | 0 | 0 | - |
| sclera | 9 | 1 | Smooth Muscle Cells 3.1% vs [0.0,1.0] FLAG_ABOVE |
| ANY(v0 mixed, adult-only) | 9 | 1 | Pericytes 5.77% vs [0.0,5.0] FLAG_ABOVE |

v0 混合行的 Pericytes 旗标 (6.5%>[0,5]) 在区域行下全部消除=纯区域混合伪旗；SMC 在 limbus/sclera 新旗如实保留（区域行语义的代价与收益都在盘上）。

## 4. OB-1 检索声明（两行缺 PMID）

- 检索面：盘上 chunks.parquet 242,928 chunks 全量（零外网）+ v0 ledgers 交叉。
- **Goblet_cell**：480 chunks 命中 → 眼表语境 12 窗 → 三重过滤后 **0 句**通过（数字全为试剂浓度/手术成功率/再上皮化面积率假阳性）→ **维持 null(no_evidence)**。
- **Pericytes**：2,574 chunks 命中 → 眼表定量组成 **0 窗** → **维持 null**（A 级区间行不变）。
- 候选全量 108 窗留痕：ob1_lit_candidates.tsv。

## 5. 红线与边界声明

- v0 冻结件与 evalset/票面/kb/mcp_server 零触碰（前后 sha 台账 logs/SHA_BASELINE_post 自证）。
- wiring=OFF：本文件不进任何运行时路径；激活永远归 PI 点名。
- 球门与判据不回调：20% 线、供者级分布法、支撑门（≥5 单元）、区间公式形状（含 B 变体的逐字 min/max 包络）全部形不动；分层=加维度。
- 禁循环派生：区域/富集全部来自 D001/D002 portal 作者注释谱系 + baselines 盘上既有设计声明；未从自家聚类取数；Q6=循环参照仅 sanity 不入判定。
- 分母语义继承 v0（捕获事件构成参考，非组织学真值，非达标线）；fetal/organoid/developing 排除继承。
