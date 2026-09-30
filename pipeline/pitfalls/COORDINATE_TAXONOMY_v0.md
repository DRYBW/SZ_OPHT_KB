# COORDINATE_TAXONOMY_v0.md — 物种×组织×assay 受控词表与新旧坐标映射（WIRE-P1 前置件）

**状态**: PROPOSED v0（2026-09-30，WIRE-P1 迁移批产出）——已知问题条目的归属表**以本件为准**；
本件登记的待裁定项由维护者/PI 定盘后升 v1。词表未覆盖的坐标一律 UNMAPPED，不得自动注入。
依据：架构评审裁决书（Astra 正式审 T1/T2）「正式矩阵的组织词表尚未统一，需先解决」
「17 面/12 组织/6 skeleton 口径冲突先修」。

## 1. 口径冲突的事实核对（"17 vs 12"）

| 数字 | 实际所指 | 核对结果 |
|---|---|---|
| 「17 面」 | `kb/baselines/*.json` 的**文件数** | 17 = 12 个组织面 + 5 个元/变体件（`baselines.json` 索引、`_STAGE_DISCLOSURE`、`_marker_repair_retina_v6`、`fetal_development_transitions`、`retina__fetal_developing` 发育变体）。**17 不是组织轴长度** |
| 「12 组织」(设计稿 §2.1) | 交叉网提案的组织页清单 | retina, cornea, trabecular_meshwork, sclera, choroid, ciliary_body, lens, vitreous, optic_nerve, lacrimal, conjunctiva, pdr_membrane |
| 「12 基线面」(实测) | `kb/baselines` 的组织面条目 | retina, RPE, ciliary_body, optic_nerve, ocular_surface, trabecular_meshwork, lacrimal_gland, choroid, conjunctiva, iris, lens, sclera |
| 「6 skeleton」 | 无供体级组成数据的基线面 | choroid, conjunctiva, iris, lens, sclera（status=skeleton_mapping_backfilled）+ lacrimal_gland（observed_single_study_pilot，无供体级区间）——组成对照不参与打分，≠无风险≠无 marker（评审停令 6） |

**两个「12」不是同一个 12**：基线面含 RPE/iris/ocular_surface（超级类）而无 cornea/vitreous/pdr_membrane；
设计组织轴反之。冲突面逐个登记如下，v1 定案前**禁按任何一方批量建格**。

## 2. 物种轴（受控词表）

| canonical id | 状态 | 备注 |
|---|---|---|
| `human` | ACTIVE（证据在册） | 六格迁移中的 5 格 |
| `mouse` | ACTIVE（证据在册） | 六格迁移中的 1 格 |
| `rat` / `macaque` / `rabbit` / `zebrafish` | RESERVED（设计词表在册，无证据） | S0 样本预判对 rat 现为域外弃权；进 UNEXPLORED，不得建知识格 |

物种惯例差异（大小写/MT 前缀/ID 体系）作为受控观察登记于条目 scope.preparation/assay 之外的
nomenclature 模式条目，不另立轴。

## 3. 组织轴（canonical id 提案 = 基线面 ∪ 设计组织的最小合并集）

canonical id 优先沿用 `kb/baselines` 面名（不改动现有知识层主键）；设计轴独有的补入；
映射与冲突逐行登记：

| # | canonical tissue_id | 基线面映射 | 设计稿映射 | 数据面状态 | 冲突/缺失登记 |
|---|---|---|---|---|---|
| 1 | `retina` | retina.json | retina | 组成 filled | 区域轴（fovea/macula/peripheral）未建——条目 KC-B1-human-retina-08 引用；登记为缺失子轴 |
| 2 | `RPE` | RPE.json | （无） | filled | 设计 12 缺 RPE——v1 建议补入（眼病主角，类目服从生物学） |
| 3 | `ciliary_body` | ciliary_body.json | ciliary_body | filled | 一致 |
| 4 | `optic_nerve` | optic_nerve.json | optic_nerve | filled | 一致 |
| 5 | `trabecular_meshwork` | trabecular_meshwork.json | trabecular_meshwork | filled | 一致 |
| 6 | `lacrimal_gland` | lacrimal_gland.json | lacrimal | pilot（无供体级区间） | 命名统一取基线面名 lacrimal_gland |
| 7 | `choroid` | choroid.json | choroid | skeleton | 组成面板建设队列（risk_notice 与 panel_gap 两独立对象，评审 T5） |
| 8 | `conjunctiva` | conjunctiva.json | conjunctiva | skeleton | 同上 |
| 9 | `iris` | iris.json | （无） | skeleton | 设计 12 缺 iris；保留基线面名 |
| 10 | `lens` | lens.json | lens | skeleton | 组成缺 |
| 11 | `sclera` | sclera.json | sclera | skeleton | 组成缺 |
| 12 | `ocular_surface` | ocular_surface.json | （cornea 的位置） | filled | **冲突①**：基线是超级类（角膜/角膜缘/巩膜混池，见条目 KC-B1-human-cornea-04），设计按 cornea 立轴。v0 裁定：cornea 作为独立 canonical（六格证据在 cornea 名下），同时在 ocular_surface 面挂指针；"角膜组成对照必须锁取材域" 为强制缓解 |
| 13 | `cornea` | （经 ocular_surface 间接） | cornea | 经超级类 | 见冲突① |
| 14 | `vitreous` | （无组成面） | vitreous | **组成面缺失** | **冲突②**：无正常参照是领域事实（条目 KC-B1-human-vitreous-03 自证）；v0 裁定：坐标合法、面板状态=missing（不是 skeleton——正常玻璃体近无细胞，"健康组成面"可能永远不成立），建格转 panel_gap 评估 |
| 15 | `pdr_membrane` | （组成在 priors/composition/human_pdr_membrane.json；疾病先验 priors/disease/PDR__fibrovascular_membrane.json；服务词典名 fibrovascular_membrane） | pdr_membrane | 有 priors 无 baselines 面 | **冲突③**：三处命名并存（pdr_membrane / fibrovascular_membrane / 无面）。v0 裁定：canonical=`fibrovascular_membrane`（现役服务词典名，MCP 消费用）；六格坐标系内部别名 `pdr_membrane` 保留为 provenance 名，拉页层做别名映射；"疾病材料对照健康器官组成"禁止（条目 KC-B1-human-pdr_membrane-03） |

stage（发育阶段）为**正交轴**，不占组织轴位：`adult | fetal | developing`（源 `retina__fetal_developing`
与 `fetal_development_transitions`、`_STAGE_DISCLOSURE`）；S0 疑似胎儿硬门消费此轴。

## 4. assay 轴（受控词表）

| canonical assay_id | 备注 |
|---|---|
| `scRNA` | 细胞悬液单细胞 |
| `snRNA` | 核悬液（条目 KC-B1-human-retina-07 平台轴的左端） |
| `spatial` | 空间转录组（鼠侧解离不敏感证据路线，KC-B1-mouse-retina-08） |
| —— | **缺失登记**：`bulk`（S0 主账含 GSE160306/179568 bulk 件，现词表不可表达；v1 待裁定补入。本批涉及 bulk 观察的条目 scope.assay 一律留空=不限，不得私加词） |

preparation 词表（最小提案，条目 scope.preparation 用）：
`enzymatic_dissociation`、`short_dissociation_cold_protease`、`nuclear_extraction`、
`surgical_stripped_membrane`、`excised_whole_mount`、`vitrectomy_cassette_wash`、
`blunt_strip_TM`、`cultured_cell_line`、`paired_donor_tissue`。
不在词表内的制备描述 → 条目按 UNMAPPED_SCOPE 处理或留空并登记，不得自造词注入。

disease_or_treatment 词表（最小提案）：
`PDR`、`RRD`、`diabetic_retinopathy_nonPNR`、`glaucoma_TM`、`aging`、`anti_VEGT_treated`、`none_healthy`。
冲突登记：`anti_VEGT_treated` 治疗轴在册但**无治疗记录是六格普遍元数据缺口**（不硬凑）。

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

## 6. 迁移映射（六格坐标系 → canonical）

| 六格文件系坐标 | canonical 坐标 | 说明 |
|---|---|---|
| human__retina | human×retina | 直通 |
| mouse__retina | mouse×retina | 直通 |
| human__pdr_membrane | human×fibrovascular_membrane | 别名映射（冲突③） |
| human__trabecular_meshwork | human×trabecular_meshwork | 直通 |
| human__cornea | human×cornea | 冲突①裁定后合法 |
| human__vitreous | human×vitreous | 冲突②：坐标合法、组成面 missing 登记 |
