# 判读层先验条目模板 (TEMPLATE — 结构冻结 2026-09-23, 卡 t_39182aa2)

> 用途: 新增组织/疾病先验条目一律按本模板出件。机读真源 = 同名 `.json`
> (`schema: eyekb-prior/1.0`); `.md` 由 `/mnt/D/EyeKB/scripts/priors/build_priors.py`
> 自动渲染, **手改 MD 无效会被覆盖**。改内容 = 改脚本内策展数据 + 重跑。

## 目录布局 (冻结)

```
kb/priors/
├── TEMPLATE.md                    ← 本文件
├── composition/                   ← K1 组成基线 (species_tissue.md/json)
│   ├── human_retina.{md,json}
│   └── human_pdr_membrane.{md,json}
└── disease/                       ← K2 疾病条目 (disease_name.{md,json})
    └── proliferative_DR.{md,json}
```

## JSON 结构 (必填字段)

| 字段 | 说明 |
|---|---|
| `schema` | `eyekb-prior/1.0` |
| `entry_id` | 与文件名一致 |
| `species` / `tissue` / `disease` | disease 条目可给 `tissue_scope` 多组织端 |
| `frozen_date` / `card` | 出件日期与来源任务卡 |
| `sources[]` | **每条一个 sid**; 必须有 `pmid`(文献) 或 `path`(数据集/本地库) 之一 —— 红线8: 无出处条目禁入 |
| `evidence_grades{}` | 本条目用到的等级口径 |
| `major_classes[]` 或 `major_compartments[]` | 主表; 每行含 `evidence` + `source_ids[]` |
| `states[]` / `myeloid_states[]` | **两级结构: 细胞类型 × 状态** (如 Macrophage: foam_DAM_LAM), 防"状态当新类型"致库膨胀 |
| `unexpected_flags[]` / `contamination_flags[]` / `flags{}` | 判读旗定义 |
| `signatures{}` | marker 面板, 带溯源说明 |
| `caveats[]` | 已知限制与解读纪律 (含"先验≠真理"声明) |
| `_computed{}` | A 级数字的复算结果快照 (回归比对基准) |

## 证据等级 (冻结口径)

- **A** = 本地实测复算 —— 本实验室管线从原始对象重算 (必须带文件路径 + 细胞数 + 计算脚本)
- **B** = 文献原文直接报告 —— 原文段落明确给出 (摘要无精确 % 时只支持定性表述, 不得引成数字)
- **C** = 跨研究经验区间 / 模型证据外推 —— 由 A 级源数据分布或多研究共识推得, 方法在条目内写明
- **D** = 综述/背景叙述 —— 仅支持定性描述与旗标语义, 不支持任何数值预期

## 判读纪律 (所有条目继承)

1. 先验只做**对照与 QC 旗** (expected / unexpected / contamination-suspect), **禁止替代或修改注释打分** (红线12 继承: RAG 禁入打分)。
2. 先验与数据打架 → 输出"打架清单"**上报 PI**, 禁止改数据凑先验、禁止改先验凑数据 (红线9)。
3. 比例区间受**建库设计**影响 (分选/富集/取材区域) —— 判"异常"前必须先查数据集建库策略 (见 human_retina caveats 1–3)。
4. 公开数据自注释本身可能不准 (PI 明示) —— 一切条目是带等级先验, 非真值。

## 新增条目流程

1. 在 `build_priors.py` 加策展数据 + (若含 A 级) 复算函数与漂移断言
2. 跑 `/home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/scripts/priors/build_priors.py`
3. 跑 `check_priors_consistency.py` (JSON↔MD↔工具 三方一致) 与 MCP 黄金回归
4. WIKI 检索索引登记新条目链接 (K5 机制)
