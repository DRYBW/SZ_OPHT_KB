# pipeline/ — 批量注释证据入口

把 README《标准分析流程》的阶段 A（步骤 1–3）与阶段 B（步骤 4–7）接到你自己的
数据集上：**输入一份单细胞数据，输出逐簇的证据报告与待人工裁决清单**。
这就是"开放即可用"缺的那一口——此前五工具证据服务、九步 SOP、示例脚本都在仓里，
但"拿自己的数据逐簇批量跑五工具"的入口脚本没有随仓发布。

## 跑起来

```bash
# 形态一：.h5ad（X 为原始计数；obs 需能区分样本）
python pipeline/run_pipeline.py --input data.h5ad --species human --tissue retina \
    --group-col treatment --out results/run1

# 形态二：10X 三件套目录（目录本身=单样本；含多份三件套子目录的父目录=多样本）
python pipeline/run_pipeline.py --input 10x_dir/ --species human --tissue retina \
    --sample-group "S1=control;S2=case" --out results/run2

# 形态三：不指定物种/组织——由 S0 样本预判门自动判定并回填（默认行为）
python pipeline/run_pipeline.py --input data.h5ad --out results/run4

# 输入是 Ensembl ID 而没带符号列时：
python pipeline/run_pipeline.py --input data.h5ad --species human --tissue retina \
    --ensg-map ensg2symbol.tsv --out results/run3
```

参数要点：`--species`（`human|mouse|auto`，默认 `auto`）与 `--tissue`（词典已知组织，
`--list-tissues` 打印清单，如 `retina`、`fibrovascular_membrane`、`ocular_surface`…，
默认 `auto`）——auto 时由 S0 门自动判定；显式给定视为人工覆盖（报告中留痕
`s0_overridden_by_user`）。`--group-col` / `--sample-group` 提供分组信息，
疾病背景先验比对才会启用。对输入的完整要求见仓根 README《输入与输出》一节。

## S0 样本预判门（默认启用；本批=shadow 不阻断）

阶段 A 之前先过 S0：三证据（基因 ID 构成 / symbol 惯例与 marker 互打 / 组成打分）
自动判定物种 × 组织，六条硬门（物种矛盾、组织分差不足、域外、深度不足、
疑似胎儿期材料等）任一命中即记 abstain。**Phase 1=shadow：弃权不阻断运行**——
落 `s0_gate_report.json` + `REPORT_ABSTAIN.md`（记录件）后照常执行；阻断式硬门
为 Phase 3（WIRE-2 另批）能力，经 `EYEKB_S0_ENFORCE=1` 切换后 abstain 才停止
（fail-closed）。弃权是合法读数，与逐簇 abstain 同理。
判过门后触发 known-claims 结构化消费（`pipeline/pitfalls/`，见其 README）：
本格适用条目的**风险旗标**渲染进证据报告头段（仅结构化表，无自由文本）与
`decisions_template.csv` 的 `pitfall_risk_flags` / `pitfall_review_required`
两列（人工裁决参考；**不自动改写分级/票面**，自动具名/降级变化恒=0；
answer_dependency≠none 的条目判读后才开放）。
整体回退：环境变量 `EYEKB_S0_GATE=0` 恢复接线前的纯人工参数行为
（此时 `--species/--tissue` 必填；不产任何 S0/旗标件，用于无网基线对比）。阈值覆盖 `--s0-thr <json>`。

## 产出（全部落 --out）

| 文件 | 内容 |
|---|---|
| `stage_a/processed.h5ad` | QC 过滤、归一化、批次校正（≥2 样本时 Harmony）、doublet 标记、Leiden 聚类后的矩阵 |
| `stage_a/figures/` | 质控图：线粒体比例、基因检出数、doublet 评分、UMAP 校正前后 |
| `stage_a/cluster_markers.csv` | 每簇 Wilcoxon top30 基因 |
| `annotation_evidence_report.json` / `.md` | 每簇五字段：top 基因 / `query_marker` 候选与得分 / `get_tissue_composition` 对照（越界旗标）/ `get_disease_prior` 比对（有分组才启用）/ `search_literature` 片段+PMID；外加机械置信度分级 |
| `decisions_template.csv` | 每簇一行，`decision`（accept/modify/abstain）与 `proposed_label` 列**留空交研究者填写** |
| `mcp_calls.jsonl` | 全部证据服务调用留痕（工具、参数、成败、耗时） |
| `s0_gate_report.json` | （S0 门启用时）三证据全读数+门因+override 留痕 |
| `REPORT_ABSTAIN.md` | （仅弃权时）停手报人件——此时阶段 A/B 未执行 |
| `pitfalls_attention.json` / `pitfall_override_audit.jsonl` | （S0 门启用时）本格注意清单机读件 + 覆盖建议逐条审计（裁决书 T5.3 机制） |

## 三条纪律

1. **默认零 LLM。** 五工具是本地机械检索，出证据不出结论。`--llm-assist`
   开关只调用用户自备通道（读 `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`
   环境变量），默认关闭，且开启后也只生成参考叙述，不改变任何簇的分级；
   仓内不含任何真实 key / URL。
2. **弃权是合法输出。** 报告里的置信度分级（`evidence_consistent` /
   `mixed_or_insufficient` / `needs_review`）是**预注册机械 QC 旗**——每条触发规则
   （`no_named_marker_candidates`、`composition_outside_baseline_range` 等）都写进
   报告可逐簇核对；它不是注释结论，脚本也不会把 needs_review 写成确定标签。
   decisions_template.csv 的裁决列永远由人来填。
3. **不含自动打分。** 与 `mcp_server/` 服务级红线一致：证据不得转成
   module score / 标签加权 / 候选排序分 / 复合 QC 分。

## 跨物种提示（服务端治理，pipeline 不绕过）

`query_marker` 的 B5 跨物种治理对鼠源基因输入会清空具名排名
（`no_named_ranking_for="mouse_input"`，候选转入 `unranked_candidates`）。
这些簇会被机器旗标为 `needs_review` / `mixed_or_insufficient` 并原样呈现
unranked 候选，由研究者判读——这是设计行为，不是 bug。

## 依赖

`requirements.txt` 锁了本目录实测版本（Python ≥ 3.11，CPU 即可）。
文献检索的向量模型获取方式与降级规则同仓根 README《5 分钟跑通》；
不装模型时 `search_literature` 走词法匹配并在报告中标注降级，其余四工具不受影响。

## 已知边界

- 阶段 A 默认阈值（min_genes=200、MT≤20%、doublet 预期率 0.06、res=1.0）沿用仓内
  实测流程，全部有命令行开关；没有自动调参。
- 10X 三件套形态不带分组信息，请用 `--sample-group "样本目录名=组名;…"` 显式给出。
- 疾病先验比对是"证据摘录"：报告呈现先验条目对该簇候选细胞类型的原文提及与
  簇级分组占比，不给"一致/不一致"的自动判定词。
