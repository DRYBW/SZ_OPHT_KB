# 组成参考 (发育期): 人胎视网膜 fetal_developing (作者/portal 标签聚合, KB3 独立条)

> schema: `eyekb-baseline-development/1.0` | entry_id: `baseline_human_retina__fetal_developing__kb3` | 状态: development_annotated_aggregate | **development_stage=fetal_developing** | 生成: 2026-09-24 | 卡片: t_5425a7ca
> ⚠ KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。
> 本文件由 `/mnt/D/EyeKB/scripts/baselines/kb3_build_dev_entries.py` 从素材 `plans/kb3_evidence/fetal_agg_20260924.json` 渲染 —— 改内容改聚合脚本+素材, 手改 MD 会被覆盖。

**性质**: 发育期**组成参考**条目: 数字=数据集作者/CELLxGENE portal 已发布细胞标签的**直接计数聚合**, 非现役成人引擎推断 (引擎对 fetal 必须弃权, E4/E5 OOD_严格 冻结件); 供者级 median/IQR 口径未建 (fetal 参考管线任务未启动, KB2c 裁定 Q5), 本条为标签分布级参考。

**用途口径**: 胎/发育期视网膜材料的身份参考 + OOD 行为对照锚 (E5 同源数据); 不得当组成达标线; 不得与 adult 主档互为参照 (PI 红线); 禁入一切打分 (Astra T2 全域继承)。

## 锚点与可得性核实 (KB3 纪律3: 无据不建)

| 锚点 | 角色 | 细胞 | 层级 | 盘上证据 |
|---|---|---|---|---|
| GSE268630 | portal 主锚 | 226,506 (14 donor) | 11w2d–23w4d 全胎期 | gse268630_cellxgene.h5ad 实测 (本仓 E5 冻结件同文件) |
| GSE138002 | 作者标签副锚 | Final 118,555 (胎层 88,013) | Hgw9–Hgw27 实测 (任务书 GW9-19 偏窄) | Final_barcodes.csv.gz umap2_CellType |
| GSE234963 | **只立数据卡** | 176,849 (24 样本) | ~7.5–21 PCW | obs 无标签列 实测 → 组成待回填 |

## 发育期标签分布 — GSE268630 (portal majorclass, 全池直计)

| majorclass | % | n_cells |
|---|---|---|
| PRPC | 23.17 | 52,479 |
| RGC | 18.54 | 41,984 |
| Rod | 16.85 | 38,167 |
| AC | 11.65 | 26,384 |
| NRPC | 9.31 | 21,087 |
| BC | 9.27 | 20,996 |
| HC | 4.21 | 9,532 |
| Cone | 4.12 | 9,324 |
| MG | 2.89 | 6,553 |

> 部位面: macula lutea 119,111 / peripheral 100,532 / 未标 6,863; PRPC/NRPC 为发育专有无成人对应 —— **禁映射进成人 10 类词表**。

## 发育期标签分布 — GSE138002 胎网层 (作者 umap2_CellType)

| celltype | % |  | 样本面 | Hgw9–Hgw27 (17 unit) |
|---|---|---|---|---|
| RPCs | 34.49 | | | |
| Rods | 14.65 | | | |
| Amacrine Cells | 12.45 | | | |
| Retinal Ganglion Cells | 10.18 | | | |
| Horizontal Cells | 7.39 | | | |
| Bipolar Cells | 6.8 | | | |
| Cones | 5.05 | | | |
| Neurogenic Cells | 3.77 | | | |
| BC/Photo_Precurs | 2.86 | | | |
| AC/HC_Precurs | 1.97 | | | |
| Muller Glia | 0.39 | | | |

## 新生层 (GSE138002 Hpnd8) — development_stage=postnatal_neonatal (第三值在此有据)

- Rods: 66.47%
- Bipolar Cells: 30.47%
- Muller Glia: 0.83%
- Horizontal Cells: 0.79%
- Amacrine Cells: 0.62%
- RPCs: 0.56%
- Cones: 0.27%

## 排除层 (禁并入, 只登记)

- **Adult 面** (11,618 细胞): 成人对照材料 → 发育条不纳; 亦非 D001 体系, 不单建 adult 条 (隔离记录)。
- **类器官 Days 面** (11,542 细胞, ['24_Day', '30_Day', '42_Day', '59_Day']): organoid→unknown+旗标 (裁定 Q1)。

## 跨源口径声明

两锚点词表不同 (portal majorclass 9 类 vs 作者 12+ 类) —— 本条并列展示, 不合成单一分布 (Astra T6 不合成口径的发育轴继承)。

⚑ **现役判读引擎=成人域, 对本条材料必须弃权; 本条数字不得被用作引擎对 fetal 输出'对错'的评分基准 (E5 仅行为描述)。**
⚑ 供者级区间口径未建 (fetal 管线另批), 引用时须带本旗。

## caveats
- 标签分布=发表注释的转录组面; GSE268630 同时含 multiome ATAC 面 GSM 矩阵 (未并入本条)。
- GSE138002 'Final' 为作者清洗后集合 (118,555/全 138,672), All_barcodes 面无标签列, 聚合以 Final 为准。
- 本条=发育期**独立文件**; KB2c 概念条 fetal_development_transitions 仍是入口占位, 二者并存: 概念条答'有哪些候选', 本条答'胎视网膜标签分布实测是什么'。

身份签名: `{"baseline_human_retina__fetal_developing__kb3": "sha256:4c5056b77d1c5e59c7ed5a5cb204f29b14f06eb22078a5e366c120201349d846"}`
