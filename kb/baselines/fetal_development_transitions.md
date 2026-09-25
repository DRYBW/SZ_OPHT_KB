# 胎儿/发育期 眼组织 转换态概念条目 (KB2c 裁定 Q5 — 非成人桶分身, 不实算组成)

> schema: `eyekb-baseline-concept/1.0` | entry_id: `fetal_development_transitions` | 生成: 2026-09-23 | 卡片: t_be336eee
> 本文件由 build_baselines.py (KB2c) 生成; 手改会被覆盖。

本条目=概念占位: 登记未来的 fetal/developing 基线候选与其前提, **不是组成基线** —— 胎儿的这些和成人的即使是一个组织也不对 (PI 红线), 禁止把本条目当任何组织的成人桶引用或反向借用。

## 现状事实

- **filled_adult_baselines**: 6
- **fetal_stage_nuclei_in_filled_sources**: 0
- **nonadult_in_filled_sources**: newborn/儿童/青少年供者 (逐行见 _STAGE_DISCLOSURE.md), 已从 adult 主档剔除; 未来 developing 基线的本地素材
- **engine_applicability**: 现役判读引擎 (OcularKB M3 等) 训练/适用域=成人组织 —— 现役引擎不适用 fetal/发育期样本, 对这类材料必须弃权 (评估层 E4=OOD_严格, 指令条款3); 需另建 fetal 参考管线后方可立组成条目

## 候选数据集 (指令条款4 — 全部未入基线)

| accession | 描述 | 发育档 | 本地 | 备注 |
|---|---|---|---|---|
| `GSE268630` | 人胎视网膜 multiome ~22万核 | fetal | True | 指令条款4 首选候选; 入基线前需 fetal 参考管线任务 |
| `GSE137828` | 人胎视网膜 (fetal) | fetal | 待核 | 指令条款4 列名 |
| `GSE137863` | 人胎视网膜发育 (fetal) | fetal | 待核 | 指令条款4 列名 |
| `GSE138002` | 视网膜类器官 | organoid→unknown+旗标 (裁定 Q1) | 待核 | 类器官≠胎儿组织, 也≠成人; 单列 |
| `GSE234963` | 类器官集 | organoid→unknown+旗标 | 待核 | 指令条款4 列名 |
| `GSE235577` | 类器官/多组学 | organoid→unknown+旗标 | 待核 | 08-28 盘点实为 snATAC/多组学 ATAC 组分 — 转换前须重核平台口径 |

**范围外**: 胎儿/发育期组成实算=另批任务 (裁定 Q5); >=60 老年分层=正交 aging 轴, 不在发育轴内。

**使用红线**: 本条目所有候选不得并入任何 adult 条; 引用本条目必须连带'需 fetal 参考管线, 现役引擎不适用'声明。

## KB3 锚点核实 (卡片 t_5425a7ca, 2026-09-24)

> development_stage=**fetal_developing** —— KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。

- **GSE268630** = AVAILABLE_WITH_LABELS: /mnt/D/OcularKB/data/GSE268630/gse268630_cellxgene.h5ad (226,506 细胞, portal 注释含 majorclass/subclass/development_stage/donor_id); GSM 面 25 单样本矩阵在盘
  - 身份纠正: 候选条 desc='multiome ~22万核' 与 portal 面一致; KB3 发育条目实采 portal 转录组注释
- **GSE234963** = AVAILABLE_NO_PUBLISHED_LABELS: 24×h5ad @ /mnt/D/OcularKB/data/backlog_h5ad/ (obs 列=空, 无标签) + RAW.tar @ data/GSE234963/; registry OA-D009: 'Human fetal retinal progenitor scRNA-seq', Fetal ~7.5-21 PCW, 24 samples/13 时间点, 'no standalone GEO label file confirmed'
  - 身份纠正: 候选条 desc='类器官集' 系 KB2c 笔误 —— registry 权威行=胎 RPC (与任务书'人胎 RPC 24 样本'一致); 无公开标签 → 只立数据卡不实算
- **GSE138002** = AVAILABLE_MIXED_CONTENT: data/GSE138002/ 4×suppl (mtx/barcodes/genes); Final_barcodes.csv.gz 118,555 细胞含 umap2_CellType 标签; 样本面=Hgw9-27 胎网 + Hpnd8 新生 + Adult 对照 + 24-59_Day 类器官
  - 身份纠正: 候选条 desc='视网膜类器官' 不完整 —— registry OA-D010 权威标题 'developing human retina AND retinal organoids'; 任务书 '(GW9-19)' 实测胎网面到 GW27; 混内容必须按样本级拆层, Adult/类器官段不进发育条目

结果: retina__fetal_developing 已独立立条目 (GSE268630+GSE138002 标签聚合); GSE234963 只立数据卡。candidates 原数组不动 (逐行口径以本段为准)。

> **KB3 进展 (2026-09-24)**: 首个发育期实数据参考条已独立立档 = `retina__fetal_developing.md` (GSE268630 portal + GSE138002 作者标签聚合; GSE234963 数据卡)。本概念条继续作为候选总表与 MCP fetal 查询入口 —— 两者并存互不覆盖; "需 fetal 参考管线"声明对**引擎判读**仍有效, 本条数字仅为已发布标签分布参考, 非引擎管线产物。
