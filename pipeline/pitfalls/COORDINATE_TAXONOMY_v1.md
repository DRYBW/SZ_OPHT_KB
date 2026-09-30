# COORDINATE_TAXONOMY_v1.md — 物种×组织×assay 受控词表与新旧坐标映射（WIRE-P1 前置件 · v1 批复版）

**状态**: RATIFIED v1（2026-09-30 批复；批复件 `plans/known_issues_b2_20261001/out/ARBITRATION_RULING_C1-C14_v1.md`
sha256=aea4b4c592a092f115c78b4ee1ec81ecaf4eea1b9e2453c8ead39615f3b7fb8a；请求件
`ARBITRATION_REQUEST_coordinates_C1-C14.md` sha256=88996f1039042fbdea8a1fd4bd9c6f109cbbc170adbd3e6ca4cffae159dd37a3）。
C1-C14 全部按 v0 取严案批复。已知问题条目的归属表**以本件为准**；词表未覆盖的坐标一律 UNMAPPED，不得自动注入。
依据：架构评审裁决书（Astra 正式审 T1/T2）「正式矩阵的组织词表尚未统一，需先解决」「17 面/12 组织/6 skeleton 口径冲突先修」。

## 1. 口径冲突的事实核对（"17 vs 12"）

| 数字 | 实际所指 | 核对结果 |
|---|---|---|
| 「17 面」 | `kb/baselines/*.json` 的**文件数** | 17 = 12 个组织面 + 5 个元/变体件（`baselines.json` 索引、`_STAGE_DISCLOSURE`、`_marker_repair_retina_v6`、`fetal_development_transitions`、`retina__fetal_developing` 发育变体）。**17 不是组织轴长度** |
| 「12 组织」(设计稿 §2.1) | 交叉网提案的组织页清单 | retina, cornea, trabecular_meshwork, sclera, choroid, ciliary_body, lens, vitreous, optic_nerve, lacrimal, conjunctiva, pdr_membrane |
| 「12 基线面」(实测) | `kb/baselines` 的组织面条目 | retina, RPE, ciliary_body, optic_nerve, ocular_surface, trabecular_meshwork, lacrimal_gland, choroid, conjunctiva, iris, lens, sclera |
| 「6 skeleton」 | 无供体级组成数据的基线面 | choroid, conjunctiva, iris, lens, sclera（status=skeleton_mapping_backfilled）+ lacrimal_gland（observed_single_study_pilot，无供体级区间）——组成对照不参与打分，≠无风险≠无 marker（评审停令 6） |

**两个「12」不是同一个 12**：基线面含 RPE/iris/ocular_surface（超级类）而无 cornea/vitreous/pdr_membrane；
设计轴反之。冲突面逐行登记于 §3，**C1-C14 已批复（2026-09-30）**：canonical 组织轴=15 面，矩阵面积=6×15=90 格全占位（C1/C10），
占位矩阵为机器产物 `pipeline/pitfalls/matrix/MATRIX_GRID.json`（build 重生成，禁手改）；格子激活一律走人工审计门，**不随面积批复激活**。

## 2. 物种轴（受控词表）

| canonical id | 状态 | 备注 |
|---|---|---|
| `human` | ACTIVE（证据在册） | 六格迁移中的 5 格 |
| `mouse` | ACTIVE（证据在册） | 六格迁移中的 1 格 |
| `rat` / `macaque` / `rabbit` / `zebrafish` | RESERVED（设计词表在册，无证据） | C10 批复：RESERVED 物种入矩阵=占位（只能 PLACEHOLDER/UNEXPLORED），**不得建知识格**；升格走"≥3 条有出处坑 + 人工审计门"预注册通道（逐申请批复，禁自控）。macaque×retina 转正不在本批，随二批深补素材另案呈报（素材最厚已登记）。S0 样本预判对 rat 现为域外弃权 |

物种惯例差异（大小写/MT 前缀/ID 体系）作为受控观察登记于条目 scope.preparation/assay 之外的
nomenclature 模式条目，不另立轴（C13 确认项）。

## 3. 组织轴（canonical id 定案 = 基线面 ∪ 设计组织的最小合并集，15 面）

canonical id 优先沿用 `kb/baselines` 面名（不改动现有知识层主键）；设计轴独有的补入；
映射与冲突逐行登记（C1 批复：15 面定案；各行裁定=批复结果）：

| # | canonical tissue_id | 基线面映射 | 设计稿映射 | 数据面状态 | 冲突/裁定登记 |
|---|---|---|---|---|---|
| 1 | `retina` | retina.json | retina | 组成 filled | 区域子轴已立 region 正交轴（§3.1，C8 批复）；条目 KC-B1-human-retina-08 补 region_scope 注记重生成 |
| 2 | `RPE` | RPE.json | （无） | filled | 设计 12 缺 RPE——**C2 批复补入独立面**（眼病主角，类目服从生物学；"少"是 low-support 不是出局） |
| 3 | `ciliary_body` | ciliary_body.json | ciliary_body | filled | 一致 |
| 4 | `optic_nerve` | optic_nerve.json | optic_nerve | filled | 一致 |
| 5 | `trabecular_meshwork` | trabecular_meshwork.json | trabecular_meshwork | filled | 一致 |
| 6 | `lacrimal_gland` | lacrimal_gland.json | lacrimal | pilot（无供体级区间） | **C7 批复：命名统一取基线面名 lacrimal_gland**（设计稿 `lacrimal` 为别名，不另立面） |
| 7 | `choroid` | choroid.json | choroid | skeleton | 组成面板建设队列（risk_notice 与 panel_gap 两独立对象，评审 T5） |
| 8 | `conjunctiva` | conjunctiva.json | conjunctiva | skeleton | 同上 |
| 9 | `iris` | iris.json | （无） | skeleton | **C3 批复保留基线面名**（坐标合法、状态如实 skeleton） |
| 10 | `lens` | lens.json | lens | skeleton | 组成缺 |
| 11 | `sclera` | sclera.json | sclera | skeleton | 组成缺 |
| 12 | `ocular_surface` | ocular_surface.json | （cornea 的位置） | filled | **冲突①（C4 批复）**：cornea 作为独立 canonical（六格证据在 cornea 名下），同时在 ocular_surface 面挂指针；**"角膜组成对照必须锁取材域"为强制缓解**（基线超级类=角膜/角膜缘/巩膜混池，条目 KC-B1-human-cornea-04） |
| 13 | `cornea` | （经 ocular_surface 间接） | cornea | 经超级类 | 见冲突①：C4 批复后 cornea 独立入轴 |
| 14 | `vitreous` | （无组成面） | vitreous | **组成面缺失** | **冲突②（C5 批复）**：坐标合法、面板状态=missing（**不是 skeleton**——正常玻璃体近无细胞，"健康组成面"可能永远不成立）；建格转 panel_gap 评估；不建健康玻璃体组成面板（条目 KC-B1-human-vitreous-03 自证） |
| 15 | `fibrovascular_membrane` | （组成在 priors/composition/human_pdr_membrane.json；疾病先验 priors/disease/PDR__fibrovascular_membrane.json；服务词典名 fibrovascular_membrane） | pdr_membrane | 有 priors 无 baselines 面 | **冲突③（C6 批复）**：canonical=`fibrovascular_membrane`（现役服务词典名，MCP 消费用）；`pdr_membrane` 保留为 provenance 名，拉页层做别名映射（consume.py PULL_TISSUE_ALIAS）；**现役 MCP 服务词典零改动**；登记 panel_gap=缺健康对照语义，禁"疾病材料对照健康器官组成"（C14 批复；条目 KC-B1-human-pdr_membrane-03）；面板补录义务登记≠建面板 |

### 3.1 region 正交轴（C8 批复，2026-09-30）

`region ∈ {fovea, macula_peripheral_mix, peripheral, not_recorded}`——与 species/tissue/stage 正交，
**不另占组织轴位、不建格子维度**。语义=claim 级/样本级 scope 注记轴：
- human×retina 格的高风险条 KC-B1-008（区域混合假旗）的缓解动作"组成对照先对齐区域"以本轴为语法前提——
  本轴立轴后该缓解可执行（此前登记"缺失子轴"，条目引用无落点）；
- 消费侧（S0/判读）按样本 region_scope 分组对照；**`not_recorded` 不得当 `fovea` 或 `peripheral` 套用**
  （登记纪律，同 C12 治疗三态的 not_recorded≠naive 同型）；
- 历史条涉及区域观察的 scope 复位按深补批重生成（本批仅 KC-B1-008 补 region_scope 注记）。

stage（发育阶段）为**正交轴**，不占组织轴位：`adult | fetal | developing`（源 `retina__fetal_developing`
与 `fetal_development_transitions`、`_STAGE_DISCLOSURE`）；S0 疑似胎儿硬门消费此轴。
发育坑归 PATTERN（C11 批复，分支 4；stage 作 claim 级 scope 注记，不建 CELL 变体格）。

## 4. assay 轴（受控词表）

| canonical assay_id | 备注 |
|---|---|
| `scRNA` | 细胞悬液单细胞 |
| `snRNA` | 核悬液（条目 KC-B1-human-retina-07 平台轴的左端） |
| `spatial` | 空间转录组（鼠侧解离不敏感证据路线，KC-B1-mouse-retina-08） |
| `bulk` | **C9 批复补词**（S0 主账含 GSE160306/179568 类 bulk 件；受控词表校验同步放行）。本批涉及 bulk 观察的现存条 scope 复位=按深补批重生成，本批仅放开词表与校验；bulk 均值化类失效另立 PATTERN 候选（P24，题录未核不入账） |

preparation 词表（最小提案，条目 scope.preparation 用）：
`enzymatic_dissociation`、`short_dissociation_cold_protease`、`nuclear_extraction`、
`surgical_stripped_membrane`、`excised_whole_mount`、`vitrectomy_cassette_wash`、
`blunt_strip_TM`、`cultured_cell_line`、`paired_donor_tissue`。
不在词表内的制备描述 → 条目按 UNMAPPED_SCOPE 处理或留空并登记，不得自造词注入。
分选制备族（immuno-sorting 类）扩词提案挂 C9 同批登记（U15），**批复词表以本件为准，未列词不得注入**。

disease_or_treatment 词表（最小提案）：
`PDR`、`RRD`、`diabetic_retinopathy_nonPNR`、`glaucoma_TM`、`aging`、`anti_VEGT_treated`、`none_healthy`。
冲突登记（**C12 批复**）：`anti_VEGT_treated` 词保留在册；治疗状态观察一律按三态登记
`{treated, naive, not_recorded}`，**"not_recorded 不得当 naive"为强制缓解**（六格普遍无治疗记录=
元数据缺口，不硬凑）；P23（治疗记录缺失混池）待盘上源核出后随深补批转 claim。

## 5. 归属裁决树（本批及 B2 一律按此五支执行）

```text
1 单物种全组织            → SPECIES/{species}
2 单组织全物种            → TISSUE/{tissue}
3 单物种×单组织坐标       → CELL/{species}__{tissue}
4 多但非全 或 由 assay/制备/疾病/治疗条件决定 → PATTERN/{pattern_id}
5 映射不进本词表          → UNMAPPED_SCOPE（禁自动注入，仅登记）
```

- 无 GLOBAL 页型：跨物种跨组织的普适规律=第 4 支（assay/方法条件驱动）归 PATTERN。
- 「更具体者优先」只用于确定适用范围，不决定知识真伪；低证据等级条目不得自动覆盖高证据共性（评审 T1）。
- 纯社区经验（community_lead）只能产生线索/verification_task/manual_review_required，
  不得产生 hard_gate/panel_activation/named_label（评审 T2）。
- 格子五态（UNMAPPED/PLACEHOLDER/LEAD_ONLY/EVIDENCE_READY/WORKFLOW_READY）在页面元数据登记；
  六格当前=EVIDENCE_READY（provisional）——≥3 条不同 failure mode 的原子条目且来源定位经
  机械核验（文件指针存在性），**尚未**完成六格人工审计（WORKFLOW_READY 需人工审核，等审计门）。
- 矩阵面积=6 物种×15 canonical 组织=**90 格全占位**（C10 批复；机器产物，零手写）：
  human/mouse×15 计 30 格按五态如实登记，RESERVED 四物种×15 计 60 格一律 PLACEHOLDER/UNEXPLORED。
  **占位≠激活**：本批达标候选=0 的口径维持（C 项批复不改变任何格的激活状态）。

## 6. 迁移映射（六格坐标系 → canonical，C6/C7 批复定案）

| 六格文件系坐标 | canonical 坐标 | 说明 |
|---|---|---|
| human__retina | human×retina | 直通 |
| mouse__retina | mouse×retina | 直通 |
| human__pdr_membrane | human×fibrovascular_membrane | 别名映射（冲突③，C6 批复：canonical=fibrovascular_membrane，pdr_membrane 留 provenance 名） |
| human__trabecular_meshwork | human×trabecular_meshwork | 直通 |
| human__cornea | human×cornea | 冲突①（C4 批复）后合法：cornea 独立 canonical，ocular_surface 挂指针 |
| human__vitreous | human×vitreous | 冲突②（C5 批复）：坐标合法、组成面 missing 登记（非 skeleton） |
