# BRIEF_DISC_COMPV1 — 组成先验分层 v1（治反向质检三义务，追加八预授权）

## 授权与上游
- 放行依据：<STORE>/WIKI/USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加八（PI 常设自主推进令）；v0 口径=同文件追加七 B/D-1。
- 上游件（全部盘上已核实存在）：
  - <EYEKB>/kb/composition/EXPECTED_COMPOSITION_v0.json（activation_obligations 三条 OB-1/2/3；rows_missing_pmid 两行）
  - <EYEKB>/kb/composition/EXPECTED_COMPOSITION_v0.md 与 COMP_SELFFLAG_20260928.md（§3 旗标率表：Q1 40%/Q2 40%/Q3 30% TRIGGER，Q4 20% under，Q5b 0%）
  - <EYEKB>/plans/comp_prior_20260928/BRIEF_DISC_COMP.md（v0 任务书，纪律条款全部继承）
  - kb/baselines（adult-only 供者级主档）、kb/priors/composition/human_retina.json、已入库 RAG literature_db 原文 chunks

## 任务（三义务逐治）
1. **OB-1 缺 PMID 两行**（ocular_surface_normal_adult_human: Pericytes / Goblet_cell）：只在盘上已入库文献 chunks 里找直接报告该比例的原文句；找到→逐字引用+PMID；找不到→维持 null(no_evidence) 并在 V1_VERDICT 声明。**禁编数、禁外网检索下载**。
2. **OB-2 眼表面区域混合超级类**：按 baselines/D002 口径的 tissue_group（角膜/结膜/巩膜等盘上实际字段，worker Phase-0 实测列名后定）分层出区间，行=类型×区域；禁跨区套用条款写进面语义。
3. **OB-3 反向质检触发（核心）**：对 retina 面按**建库/取材/分选策略分层**（如 酶解vs机械、核分选 NeuN±、整眼vs区域取材——以 baselines 元数据盘上实际可用字段为准，Phase-0 先列可用分层维度再做门）重算旗标率。目标=v1 规则下健康公开集 Q1-Q5 旗标率 <20%；**若达不到，如实报"哪些维度残余触发+缺口在哪"，禁改 20% 球门、禁回调判据凑命中**（KB5 防火墙条款：面侧问题报面侧，改判据=另案送 PI）。

## 验收件（全落 <EYEKB>/plans/comp_prior_v1_20260929/，禁写 v0 目录）
- EXPECTED_COMPOSITION_v1.json + v1.md（新目录 kb/composition/ 内 v1 命名版本化，v0 三件字节不动，前后 sha 台账自证）
- 分层反向质检复算表（数据集×面×分层规则→旗标率，逐行可复算）
- V1_VERDICT.md：三义务各自 解决/部分/未解决 + 残余激活缺口 + 激活前剩余人门清单（照实，不含任何激活动作）
- MANIFEST_sha256.txt；脚本带 *_t_<卡号>.py 后缀全部留盘

## 纪律红线
1. 零下载零外网；只用盘上已入库资产。
2. v0 冻结件与 evalset/票面 kb/mcp_server 零触碰；kb/composition/ 只新增 v1 命名文件。
3. wiring=OFF 保持——本卡产物不得进任何运行时路径；激活永远归 PI 点名。
4. 禁循环派生继承（不从自家聚类派比例）；fetal/organoid/developing 排除继承；no_evidence 合法。
5. 球门与判据不回调（20% 线、纯度阈值、区间机械规则形不动；分层是加维度非改标准）。
6. 资源：systemd-run --user -p MemoryMax=16G 托管计算段；心跳带 available；h5ad 用 <CONDA_ROOT>/envs/scrnaseq/bin/python。
7. 完成或受阻必须调 kanban_complete/kanban_block 落卡；分步落盘+comment 留痕。

## 发射门（协调者侧执行，不入 worker 任务书）
- 仅当 SEURATPROBE（t_5d18900e）已收口 且 /proc/loadavg 1min <40 才建卡；两条件任一不满足不发射。
