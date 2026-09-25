# 事故记录 (t_d07ab64f, 2026-09-24 21:46-21:50): 冻结回归件被 import 副作用重跑覆盖

## 事实
- 新黄金回归驱动初版 `import regression_mcp_vs_direct_v2_20260923`（意图复用 build_cases/parse/first_diff）。
- 该冻结脚本**无 `if __name__` 守卫**（模块级 `sys.exit(asyncio.run(main()))`），import 即全量重跑并**重写**
  `MCP_REGRESSION_V2_20260923.{json,md}`（该两件 mtime 变为 09-24 21:49）。

## 影响面界定
- 两件属 SUITE_SUPERSESSION_20260923.md 明文的**"已被取代"历史套件**（0/41，未剥离 sidecar，非现役权威）。
- 重跑**语义零漂移**：verdict=FAIL、n_consistent=0/41、逐用例 top-5 pmid 与差异类型 (`claim_relation` only-in-MCP) 与 09-23 历史态逐行一致（脚本确定性 + 检索层零改动，与 SUPERSESSION 记载一致）。
- 实际损失=逐用例 `secs_mcp` 计时元数据与逐字节形态。**41/41 真 PASS 历史证据在 `regression_v2_run.log`（20:48 冻结，未触碰）**。
- 现役权威套件 REGRESSION_KB1V2B_20260923.json / REGRESSION_KB2C_20260923.json / 其余冻结件：未写、未动。

## 根因与防再犯
1. 根因：import 冻结脚本前未检查模块级副作用。教训入卡。
2. 新驱动改为**自带** build_cases/parse/first_diff 复制品（不再 import 冻结件）。
3. 本件即 errata 落档：覆盖前后语义等价的证明 = 本文件 + SUPERSESSION 表格记载。
