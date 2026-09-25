# EyeKB 回归套件谱系与替代关系 (2026-09-23 深夜, KB2c 巡检记录)

防止未来扫描器把"过期套件的 FAIL"误读为活回归。当日 KB 快速迭代（一天内 P1→KB1→KB1v2→
KB1v2b→KB2c 五波），部分早期套件的断言已被后继套件合法取代：

| 套件 | 最后状态 | 判读 |
|---|---|---|
| `MCP_REGRESSION_20260923.{json,md}` (19:36) | 41/41 PASS | P1 三工具时代冻结证据，未动 |
| `regression_v2_run.log` (20:48) | 41/41 PASS | P1opt v2 时代冻结日志（早于 sidecar），未动 |
| `REGRESSION_PRIORS_20260923.{json,md}` (21:41) | 当时 PASS | **已被取代**：断言 MCP retina 主行含 `pct_hrca317m`（v1-composition 口径）；KB1v2 起 baseline 条优先，23:35 复跑 KeyError=预期过期，非缺陷 |
| `selftest_tools_v2_20260923.py` | 14/1 | **已被取代**：唯一 FAIL=“list_tools==三工具”（5 工具化自 KB1v2 起合法）|
| `regression_mcp_vs_direct_v2_20260923.py` | 0/41 | **已被取代**：未剥离 KB1v2-W5 sidecar 附加字段（全部差异=`claim_relation`/`inclusion_reasons`/`evidence_context`/`verification_status` only-in-MCP），检索语义本身零漂移——同 41 用例剥离 sidecar 后全等的现行权威证明见下行 |
| `REGRESSION_KB1V2B_20260923.json` (23:32) | **56/56 PASS** | 现役权威①：KB1v2/1v2b 全行为 + search 41 用例(strip_sidecar)全等 + 5 工具契约 |
| `REGRESSION_KB2C_20260923.json` (23:31) | **33/33 PASS** | 现役权威②：发育轴双档/披露对账/分类器表锁/MCP 双轴/fetal 概念隔离 |

处置：过期三件不删除（历史证据），不再单独维护；新断言一律进 KB1V2B/KB2C 两系。
若未来 sidecar 契约或工具数再变，优先扩 KB2C 系。

**KB3 巡检补录 (run 1768, 2026-09-24 08:2x)**: `regression_kb1v2_20260923.py` 亦属**已被取代**
—— 现重跑崩溃于 L100 `tm.get("verdict","")[:40]` (TM 骨架条 verdict 字段系 KB1v2 前形态,
KB2c schema 1.1 骨架重建后不存在; 与 KB3 重渲无关: pre-rerender 备份同样 verdict=None)。
其全部有效断言由 REGRESSION_KB1V2B (56/56, 现役权威①) 承接。崩溃未污染 22:11 历史 JSON。
当日 (09-24) 重跑证据: KB1V2B 56/56 PASS + KB2C 33/33 PASS + KB1V2D 17/17 PASS —
KB3 的 baselines 重渲 (build_baselines.py 崩溃修复+段禁令行入档) 对既有锁定零连带破坏。

**重基线补录 (t_502a23b7, 2026-09-25 16:1x)**: `REGRESSION_KB1V2B_20260923.{py,json}` 的
sidecar 覆盖常量断言 (2713 篇) 因 09-25 晨 t_f3fa8c95 EyeKB-RAG v2.3 角膜引文增补
(evidence_meta_v2.0_2026-09.jsonl 2713→2717 行) 成为预存在失效断言——t_d6f2a0a0 软提示卡
五态同集三态对账确认非其所为 (out/zero_touch_and_failset.json)。按"发布件重基线"纪律出
`regression_kb1v2b_20260925.py` (唯一实质变化=常量 2713→2717，冻结原件零触碰)，重跑
**56/56 PASS**，恢复"56/56"信号纯度；现役权威①自本条起以
`REGRESSION_KB1V2B_20260925.json` 为准，20260923 件降级为历史冻结证据（不删除）。
.bak 前像+sha 台账: `evals/SHA_REBASELINE_2713_2717.txt`。
