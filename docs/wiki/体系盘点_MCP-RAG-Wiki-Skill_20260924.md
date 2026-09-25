# MCP-RAG-Wiki-Skill 体系盘点与路线图（2026-09-24）

> 维护：协调者 | 性质：体系级现状快照 + 下一步计划（供 PI 拍板优先级）
> 依据：2026-09-24 全链考古（KB2 两轮评测收口后盘点）；上层教义见 skill `knowledge-guided-cell-annotation`。

## 0. 体系一句话

**四层咬合的"眼科单细胞注释知识基础设施"**：Skill（判读纪律/协议）规定怎么判 → MCP（工具层）提供统一取数口 → RAG（文献证据层）供证据+PMID → Wiki（项目中枢）存结论与决策。注释生产走 human-in-loop（AI 草稿+PI 裁决），质量由 KB2 双盲评测环验证。

```
[PI 临床裁决]  ← human-in-loop 闭环顶点（真值在 PI 手里）
     ↕
[Skill] 判读协议：两维度教义/三门/词表/发育轴红线
     ↕
[MCP] eyekb 5工具：query_marker / search_literature / get_tissue_composition
                / get_disease_prior / get_kb_page   （stdio，41/41 黄金回归）
     ↕                    ↘
[RAG] 文献证据库            [知识条目] kb/baselines(11组织+发育轴) + kb/markers
  v2.1→v2.2 09-24 切默认 (220,571 ch)   + 预印本轴(可过滤)/QA 逐 marker 带 PMID
  (v2.2=D0锚文献定向通道; 切换证据 SWITCH_V22_RECORD.md)   + 疾病矩阵(PDR 首格+development_axis; keratocyte 补录 09-24 已收口)
     ↕
[Wiki] 六件套（INDEX/结论速查/数据资产/决策记录/当前状态/检索索引）
     ↕
[KB2 评测环] 双盲判读（RUN1/RUN2 已收口）→ 量化判读一致率 + 自动暴露 KB 缺口（已实证：keratocyte 词表缺口）
```

## 1. 各层现状

### RAG（文献证据层）
- **现役 v2.2_2026-09（检索默认库，09-24 t_27d3ba2c 切换）**：220,571 chunks / 3,681 篇；11 组织 + 预印本轴（可过滤）+ QA 逐 marker 带 PMID；检索 stage3_retrieve_v3 支持 `--tissue/--preprint/--dev-stage`（默认已指 v2.2；黄金回归 10/10 不劣化+D0 可检出自检，证据 scripts/SWITCH_V22_RECORD.md；MCP search_literature 默认仍 v2.0 待拍板另卡）
- **v2.2_2026-09（09-23 深夜建成）**：v2.1 全量继承 + **D0 锚文献定向通道**（7 篇 196 chunks，逐篇例外登记；含 GSE165784 原文 abstract-only）+ `full_text_available` 列
- papers 级 dev_stage sidecar（3,696 行，正则+人工抽验 30）
- **缺口**：① ~~v2.2 未接为检索默认库~~（✅ 09-24 t_27d3ba2c：ocularkb 检索脚本默认已切 v2.2，GSE165784 原文主锚实测 rank-1 可检出；MCP 侧默认切换待用户拍板）② RAG 正主表无 organism_stage 列（现靠 sidecar 过渡）③ REVIEWER_LLM 要求的三字段证据模型（inclusion_reason 五类 + claim_relation + evidence_context）**未落地** ④ 附属器入库待拍板（泪腺 170/睑板腺 220/眼眶脂肪 126/眼外肌 46 OA 篇）

### MCP（工具服务层）
- 5 工具齐；get_tissue_composition 已带 development_stage（adult 主档/adult_pool 对照/fetal 转换态概念条目，KB2c 口径）；41/41 黄金回归；stdio 不开端口（红线保持）
- **缺口**：① query_marker 不认 ENSG（本轮实证，采集器侧双列已修，工具侧保持"调用方传 symbol"现设计，docstring 已写明）② search_literature 的 dev-stage 过滤依赖 RAG sidecar，工具内未透传 ③ 疾病态/膜类 marker 面板仍薄（PDR 膜 demo 实证健康库 0 覆盖，补录进行中）

### Wiki（项目中枢）
- 六件套运转正常；当前状态/结论速查今日已更（引擎现状段过时项已修：v2_prod 维持拍板入账）
- **缺口**：决策记录.md 未收录本日三拍板（v2_prod 维持/双列 schema/keratocyte 补录）——待补

### Skill（程序性知识）
- `knowledge-guided-cell-annotation`（判读体系主 skill）：教义+三层知识条目+REVIEWER_LLM 裁决+发育轴红线+双盲评测运维+pitfalls，KB2 缺陷周期已入 references——**与实际系统同步**
- `celltype-marker-knowledge-base`（marker 取数纪律，2026-08-22，另一 profile）：与主 skill 无互相引用
- **缺口**：主 skill 实例资产节未更新 RUN1/RUN2 评测结果；两 skill 关系未声明

## 2. 跨层断点（按危害排序）

| # | 断点 | 危害 | 修法 |
|---|---|---|---|
| 1 | 三字段证据模型未落地 | "证据可审计"是 REVIEWER_LLM 定的项目主线，现在条目只有 PMID 没有论断级关系（支持/反驳/限定） | D0 关键论断逐条核验起步，禁全库铺开 |
| 2 | ~~RAG v2.2 未接线~~（✅ 09-24 t_27d3ba2c 检索脚本默认已切+回归自检 PASS；MCP 默认切换待拍板另卡） | 评测/demo 引 D0 锚文献（GSE165784 原文）检索不到 | 检索默认库切 v2.2 + 黄金回归自检 |
| 3 | human-in-loop 最后一公里未走通 | demo 只到草稿；"PI 确认→写回 obs→diff 表"定稿闭环未在真实样本走通 | 拿 PDR 膜 demo v2 走一遍（PI 参与 30 分钟级） |
| 4 | organism_stage 正主列未进 RAG | sidecar 是过渡，跨库查询有分叉 | 下次 rebuild 时加列（先拍板） |
| 5 | 双 skill 无关联 | 未来会话可能只加载其一 | 互加 related 声明（分钟级） |
| 6 | 疾病态 marker 面板薄 | PDR 膜类样本本地命中低 | 随疾病谱滚动补（教义既有路线，勿一次性大坑） |

## 3. 下一步计划

### P0（机械性，可立即派）
1. ~~结论速查引擎段过时~~（✅ 本日已修）
2. RAG 检索默认库切 v2.2 + 41/41 回归自检（小卡）（✅ 09-24 t_27d3ba2c 完成：stage3_retrieve_v3 默认切 v2.2，黄金回归 10/10 同口径不劣化 + D0 七篇可检出；证据 scripts/SWITCH_V22_RECORD.md。注：MCP search_literature 默认仍 v2.0，切否涉服务行为变更待用户拍板另卡）
3. keratocyte 补录卡收口验收（t_e1febb8e 在跑）
4. 双 skill 互加关联声明 + 主 skill 实例资产补两轮评测结果（分钟级，协调者直接做）
5. 决策记录.md 补本日三拍板

### P1（1-2 天级，建议下一波）
6. **三字段证据模型落地**：先对 D0 七篇的关键论断逐条核验（inclusion_reason+claim_relation+evidence_context），产出模板后再谈扩量
7. **human-in-loop 定稿闭环首跑**：PDR 膜 demo v2 草稿 → PI 确认/改判 → 写回 obs → v2→v3 diff 表（需要 PI 30 分钟级参与）
8. organism_stage 正列方案拍板（sidecar 转正 vs 维持 sidecar+查询层聚合）

### P2（等拍板）
9. 附属器入库四组织（量级已报）
10. 鼠版注释模型（GSE243413 32.3 万细胞在盘，OWN_MOUSE_DR_DATASET 直接受益）
11. RUN3 方向（扩考卷 / 真人双盲 / 换判读员架构）
12. M1 数据论文组装（注册表/指纹库/验证链齐，缺工作区/图表/正文）

### 明确不做（教义既有红线）
- 疾病层一次性铺宽；人鼠对齐（暂缓）；胎儿桶代答胎儿问题之外的任何捷径；RAG/先验进引擎打分
