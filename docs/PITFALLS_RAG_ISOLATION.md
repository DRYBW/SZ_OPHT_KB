# docs/PITFALLS_RAG_ISOLATION.md — known-issues 结构化条目与 RAG 语料的隔离声明

**Status**: BINDING（依据架构评审裁决书签发文本「Prohibited Actions」落档；
2026-09-30 REV-1=astra 正式审定盘版，取代同日上午初版）
**Applies to**: `pipeline/pitfalls/pages/*.json`（原子 claim 契约）、上游 known-issues
原稿（`/mnt/D/EyeKB/kb/known_issues/`，仓外只读件）及其任何文本字段

## 禁令（永久）

1. known-issues（已知问题库）的一切文本——claim 契约的 failure_mode /
   observable_signature / mitigation，以及原稿的 issue / why_it_bites 长文本——
   **永不并入 RAG 语料**。任何 RAG 索引/激活管线（现役 v2.1 与暂存 v2.4.2 及
   后续版本）的构建脚本必须显式排除 `pipeline/pitfalls/` 与 known-issues 原稿
   目录；新增语料来源时须复核本禁令未被稀释。
2. **WIRE 全程锁 RAG v2.1 现役库**：known-issues 交叉网接入不构成任何 RAG
   版本切换/激活理由；暂存 v2.4.2 不得被顺带激活（其自身验收门未全过，激活走
   独立流程）。本批未改任何服务侧/词典侧文件（`mcp_server/`、`kb/`、
   `clients/` git diff=空，验收门 G6 机检）。
3. 样本预判引擎（`pipeline/s0_check.py`）与判读证据面（阶段 A/B 证据采集函数、
   喂给盲评的证据摘要件）**禁读** known-issues 文本。消费=shadow 语义：风险旗标
   与复核要求注入人类阅读面（报告头段旗标表 + decisions 两列），**不自动改写
   分级/票面/具名**（自动具名变化恒=0）；盲评前不注入条目自由文本，
   `answer_dependency≠none` 的条目判读后才开放（run 产物内该文本=REDACTED）。
4. 机检口径（两条，任何接线改动后必复跑）：
   - `plans/wire_p1_20260930/scripts/firewall_grep.py <run目录>`：
     A 层=原稿自然语言指纹 163+ 条 grep 判读证据面 0 命中；
     B 层=post_decision 条目自由文本在任何 run 产物 0 命中（盲评污染扫描）。
   - `pipeline/pitfalls/build_claims.py --check` + `tests/test_s0_gate.py`
     T4-T6：判读面模块 ast 级禁读 + 契约/链接/字段完整 + 无 override/cap 字样。

## 理由

盲评协议与冻结卷是 EyeKB 的核心方法学资产；94.7% 一致性回归的合法性依赖
"判读时只见证据、不见答案侧文本"。known-issues 条目记录具体数据集的已知坑
（含样本级信息），一旦进入检索语料或盲评可见面即构成评测集信息泄漏——
评审终止条件"一次盲评答案泄露=全扩展终止"。

## 例外与出口

无。若未来需要让 known-issues 参与检索，必须另立评审并先修订本声明。
