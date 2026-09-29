# PHASE0 — COMPV1 可用分层维度盘点 + 分层规则预注册（卡 t_37a35220）

> 本文件在任何旗标重算之前落盘 = v1 分层规则的门先立后算（禁看结果调规则）。
> 依据：任务书 OB-3 "Phase-0 先列可用分层维度再做门"。

## 1. 盘上可用分层维度（实测字段，非设想）

### 1a. retina 面（D001 HRCA，3,177,310 核）
| 维度 | 字段（盘上） | 取值 | 可用性 |
|---|---|---|---|
| 建库/悬液 | `obs.suspension_type` | nucleus 100%（intronic_reads=yes） | ✅ 但**只有核一层**——D001 无任何细胞悬液单元 → 细胞悬液轴 A 级缺层，如实报 |
| 解离 | `obs.suspension_derivation_process` / `suspension_dissociation_reagent` | mechanical+detergent 全图集（NP40 核提取 2,999,939；Shekhar unknown 177,371） | ✅ 但**无酶解vs机械对比层**（全图机械+去污剂）→ 酶解轴无对比度，不建分层 |
| 核分选 | `obs.suspension_enrichment_factors` | na 1,843,277 / NeuN 1,334,033（FACS） | ✅ 主分层维（baselines caveat：NeuN+ 层系统性抬神经元压 MG/Astro/RPE，两层区间禁混用） |
| 取材区域 | `obs.tissue` | peripheral 1,568,477 / macula lutea 1,077,597 / fovea centralis 434,131 / macula lutea proper 97,105 | ✅ 第二分层维 |
| 建库研究 | `obs.study_name` | Chen_a/ancestry/b/c/rgc + Shekhar | ✅ 单元键成分（研究×策略，与 baselines strata 同构） |

### 1b. 设计声明元数据（baselines/retina.json，A 级盘上文本，先于本卡存在）
- `primary_reference_stratum`：主档=排除 Chen_rgc 与各研究 NeuN+ 层、adult-only 113 单元 → v0 区间已是"unsorted 混合区域池"。
- `caveats`：**Chen_rgc 与 Shekhar_GSE237204(legacy) 均为 RGC 靶向设计**（"Shekhar legacy 43.6% 高比例是设计使然"）→ Shekhar naive 单元按设计声明路由进"分选/靶向层"，非本卡新造（文本在 v1 之前已冻结在盘）。
- `富集步骤`（t2）：Chen_rgc 整层 RGC 富集设计。

### 1c. ocular_surface 面（D002）
- `baselines/ocular_surface.json.strata[].tissue_group` 5 层（cornea 29 / corneal endothelium 单独层 2 / limbus 22 / ocular surface region 4 / sclera 10 adult-only 单元），每层带 9 类 donor_level_adult_only（median/IQR/range）→ **OB-2 所需区域分层数值全部盘上现成，A 级**。
- D002 悬液=cell 100%、无分选记录、机械+酶解离（胶原酶 A，时长有梯度但基线未按其分层——本卡不加该维，任务书只要求区域）。

### 1d. 评估成员侧设计元数据（路由依据，全部盘上）
| 成员 | 悬液/平台 | 分选 | 区域 | 证据位置 |
|---|---|---|---|---|
| Q1_Lukowski2019 | **cell**（10x 3'v2） | 无记录 | obs 无区域列；"中央凹取材"=SELFFLAG §3 判读（B 级） | h5ad obs.suspension_type + SELFFLAG |
| Q2_GSE155288 | cell（10x，SELFFLAG 判读） | 无记录 | obs.region = M 36,959 / P 55,426（供者1=M 供者2=P） | h5ad obs.region |
| Q3_GSE137537 | **Smart-seq 全细胞**（低深度） | 无记录 | obs.tissue = MR/PR 混合库 | h5ad obs + 冻结件 §1 平台分层 |
| Q4_GSE148077 | cell（10x） | **CD73/CD90 分选**（神经元表面抗原富集） | fovea（GSM 记录） | EVALSET_FREEZE §0/§1（GSM H1..H11 Fovea/CD73/CD90） |
| Q5b_GSE226108 | nucleus（10x 3'v3） | obs：na 70.1% / NeuN 29.9% | obs：fovea/peripheral/macula proper | h5ad obs 全字段 |

### 1e. OB-1 检索面对象
- `/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/chunks.parquet`（1.1G，含全文 chunks）+ papers.jsonl；
- v0 建台账 `ledgers/mine_ct_pct.json`（pericyte 3 句均非眼表面组成%；goblet 0 句）→ 本卡对 chunks 全量复扫为义务。

## 2. v1 条件层定义（机械，retina）

单元键 = `donor_id × tissue × enrichment`（adult-only：排除 baselines excluded_nonadult_units 7 位供者，KB2c 口径不变）。分布法=供者级（每单元先算 10 类占比再跨单元 median/IQR/range）——与 baselines distribution_method 同式，仅加维度。

区间公式形状不动（任务书红线5）：`low=floor(min(设计层可归因来源))`、`high=ceil(max(...))`、`mid=median`。
来源可归因性（预注册）：priors v1 经验区间与文献 fold 句均为**混合设计**来源（跨研究 pooled / 跨样本极值），只归因"设计无关层"（=v0 行，原样保留零改动）；条件层区间仅由 A 级设计层供者分布构成。条件层支撑门：**单元数≥5，否则回落父层**（机械）。

| 层 ID | 定义 |
|---|---|
| RC1_unsorted_allregion | enrichment=na 且 study∉{Chen_rgc, Shekhar_GSE237204}，全区域 |
| RC2_unsorted_central | RC1 ∪ tissue∈{fovea centralis, macula lutea, macula lutea proper} |
| RC3_unsorted_peripheral | RC1 ∪ tissue=peripheral |
| RC4_sorted_or_targeted | enrichment=NeuN ∪ study∈{Chen_rgc, Shekhar_GSE237204}（设计声明=神经元/RGC 靶向） |

## 3. 成员路由规则（预注册，按成员设计元数据钉，禁按组成数字选层）

| 成员 | 路由层 | 附加披露 |
|---|---|---|
| Q1 | RC1 | platform_mismatch（cell vs 核面）；region=文献判读未达盘上逐细胞字段 → 不落 RC2/RC3 |
| Q2 | RC1 | platform_mismatch；region M+P 混合 → 数据集级走 all-region（供者级 M/P 走 RC2/RC3 作**敏感性附加行**，不改主口径） |
| Q3 | RC1 | platform_mismatch（Smart-seq 全细胞）+ 真值构造轴（Macroglia 签名拆分，见 §6） |
| Q4 | RC4 | platform_mismatch（分选为核悬液 CD73/CD90 细胞——GSM 记录为细胞分选，与 NeuN 核分选同属"靶向设计"层，差异披露） |
| Q5b | RC1 | 主组成 70% naive；样本级（obs.group 12 组→匹配层）全列**敏感性行** |

旗标率定义不变：flagged_rows/面行数（10），数据集级；反向质检 20% 线不变；计入集=Q1..Q5b（Q6 循环参照仅 sanity，Q7/Q8/Q9 域外轴不变）。

## 4. OB-2 规则（眼表 类型×区域）

行=9 类型 × 5 tissue_group（baselines strata 现成分层，A 级）；`low=floor(stratum_iqr_low)`、`high=ceil(stratum_iqr_high)`、`mid=unit_median`（同式加维）。corneal endothelium 单独层 n=404 细胞/2 单元 → 支撑门（≥5 单元）不过 → **回落 any_region 父行**并如实标 `support_gate_fail`（这正是"区间机械规则形不动"的含义：门是机械的，不是拿来凑命中的）。
Q6 重算：Q6_sub100k obs.tissue→5 组映射（机械 UBERON 表：cornea/corneal epithelium/substantia propria of cornea→cornea；corneo-scleral junction→limbus；sclera/tunica fibrosa of eyeball→sclera；ocular surface region→OS region；corneal endothelium→CE 层）+ adult-only（排除 ocular_surface.json excluded_nonadult_units 9 供者）；逐区域组成 vs 该区域行区间；区域样本数 <500 细胞的区域并入 any_region 评估并披露。
禁跨区套用条款进面语义（每行 category_note）。

## 5. OB-1 规则（两行缺 PMID）

在 chunks.parquet 全量扫 `goblet`/`pericyte` 命中句 → 三重过滤：①人 ②正常成人眼表/结膜语境 ③**直接报告组成比例**（% of cells/percentage + 分母可钉）→ 通过者逐字引用+PMID；0 通过则两行维持 null(no_evidence) 并在 V1_VERDICT 声明。禁外网、禁编数。

## 6. 已知残余轴（v1 不解决，如实登记进 VERDICT）
- 悬液平台轴（nucleus vs cell）：面主档无细胞悬液 A 级层 → Q1/Q2/Q3/Q4 平台错配只能披露不能豁免。
- 真值构造轴：Q3 Macroglia→MG/Astro 签名拆分是评估侧真值构造（334 lowconf 敏感性档已冻结），非源研究设计。
- 解离梯度轴：D001 无酶解vs机械对比层。

---

## 附注（同日 11:50，执行后追加，非预注册内容）

计算中发现区间语义分叉：v0 公式是三项包络（donor_iqr ∧ priors ∧ fold_lit），
纯层内 A 级区间（本文件 §2 预注册口径 = **R1A**）本质=中央 50% 带，天然窄于 v0 包络。
按"区间机械规则形不动"的字面另实现 **R1B**（公式逐字保留，仅 donor_iqr 项换成层内值），
**明确标注为后验敏感性变体**：OB-3 目标（<20%）判定只看预注册 R1A；
R1B 只用于残差归因分析。两套语义同时进 v1 件，激活前语义选择列人门（PI）。
（追加理由与时间戳留痕=本附注；两变体结果并排落盘，无回调、无换球门。）
