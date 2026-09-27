# 脱敏双扫描报告(增量) — 2026-09-28 KB9REG-EXEC t_4bb75b26

范围：本卡同步面 = kb/markers(2 新件)+mcp_server(2 改件)+docs/wiki(4 改件)+docs/plans/kb9_ocs_20260927(BRIEF/exec/ols 补回证)。
规则三元组=project-github-export 现行清单，与 2026-09-27 REPOSYNC 报告同源（R01–R16 代号沿用）；本报告不复现任何渠道商/裁决商/端点串。

## 本卡面命中（已按标签替换）

- `docs/plans/kb9_ocs_20260927/BRIEF_KB9REG_EXEC.md`: R08=1
- `docs/plans/kb9_ocs_20260927/exec/out/postdiff_selfproof.json`: R08=1
- `docs/plans/kb9_ocs_20260927/exec/out/pre_change_baseline_kb9reg.json`: R08=19
- `docs/plans/kb9_ocs_20260927/exec/scripts/exec2_build_overlay.py`: R08=3
- `docs/plans/kb9_ocs_20260927/exec/scripts/exec3_postdiff_selfproof.py`: R08=2
- `docs/plans/kb9_ocs_20260927/exec/scripts/exec4_golden41_copy.py`: R08=2
- `docs/plans/kb9_ocs_20260927/exec/scripts/exec6_repo_mirror.py`: R12=3; R08=2; R05=1; R04=2; R06=4
- `docs/plans/kb9_ocs_20260927/exec/scripts/exec6_repo_mirror_v2.py`: R04=1; R06=1
- `docs/wiki/体系盘点_MCP-RAG-Wiki-Skill_20260924.md`: R08=3; R01=1
- `docs/wiki/决策记录.md`: R12=1; R08=1
- `docs/wiki/数据资产.md`: R12=1
- `kb/markers/_k9_ocs_rules_overlay_v1.json`: R08=32
- `kb/markers/markers_k9_ocs_increment.json`: R08=1
- `mcp_server/eyekb_core.py`: R08=4
- `mcp_server/server.py`: R08=2

## ⚠ 存量发现（登记，不擅动——处置归协调者/PI）

- kb/ 与 mcp_server/ 历史件 **42 文件**存在 R08(REVIEWER_LLM)/R12(AGENT_ROLE) 形态命中，合计 3570 处。根因=2026-09-27 REPOSYNC 的扫描 DIRS 未含 kb/，kb/mcp 按线上字节 1:1 镜像（当时对账 104/104 MATCH 即此口径）→ 相应字样已随该轮 push 存在于远端。
- docs/ 历史面另有 0 文件命中（多为判读层原文引用，上轮按『数值证据面不触碰』口径放行）。
- 处置选项（协调者定）：①对 kb/面补 apply 脱敏→对账表改标 DESENS（仓与线上字节分歧，需 PI 认可语义）；②维持字节镜像+接受字样暴露（这些词是否敏感属 PI 判断，R08/R12 是内部协作称谓而非密钥）；③改线上原件措辞=触发基线字节变更，禁。
- 本卡产物（仓内）的 external_review 字段值因替换与线上权威原件不同，对账表逐件标 DESENS；线上原件 sha 见 exec/out/SHA_NEW_AND_MODIFIED.txt。

## 文件名扫描
- 本卡新增面 0 命中（无需改名）。
