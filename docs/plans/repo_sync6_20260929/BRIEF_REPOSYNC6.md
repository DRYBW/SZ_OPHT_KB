# BRIEF_REPOSYNC6 — 第六轮仓同步（COMPV1 收口产物增补，REPOSYNC5 领地剔除件回收）

日期：2026-09-29 | 派发：AGENT_ROLE-coordinator | 执行：AGENT_ROLE
上游依据：
- docs/plans/repo_sync5_20260929/REPOSYNC5_COMPLETED.md（RS5 收口件，其"领地剔除"节明列本卡回收范围）
- <EYEKB>/plans/comp_prior_v1_20260929/（COMPV1 t_37a35220 收口产物，协调者已抽验：manifest 27/27 sha OK）
- <EYEKB>/kb/composition/EXPECTED_COMPOSITION_v1.{json,md}（v1 分层面，wiring=OFF）
- USER_DIRECTIVE 追加八（常设授权令，docs/plans/WIKI 镜像内）——本卡属授权令范围内机械同步

## 任务（增量同步，第二个 commit）

staging 仓 = <STAGING_REPO>（当前 HEAD=fa4f175，origin/main=a0ad857，本地待推链已含 2 commits）。在 fa4f175 之上新建 1 个 commit，内容：

1. kb/composition/EXPECTED_COMPOSITION_v1.{json,md} 两件入仓（copy 不 move，/mnt/D 原件零改动）。
2. plans/comp_prior_v1_20260929/ 全目录入 docs/plans/comp_prior_v1_20260929/（V1_VERDICT.md、PHASE0_INVENTORY、层化结果 tsv 全部、residual_attribution_xtab、ob1_lit_candidates、os/retina 两 json、retina_strata_units、scripts/ 全部、logs/ 全部、MANIFEST_sha256.txt）。单件 >50MB 不收并登记清单（照 RS5 规矩，预期无此大件）。
3. WIKI 侧 09-29 增补对齐：COMPV1 收口条目若 INDEX/当前状态有本地新行未入仓，一并入（masked 口径照旧：本地绝对路径 pathnorm 到仓内相对形、任何 token 化）。<WORKER_HOME>/QUEUE_常设任务_20260928.md 新增行同步到仓内对应件（docs/plans/QUEUE_20260929.md 或既有件对齐）。
4. 证据目录 docs/plans/repo_sync6_20260929/：BRIEF 本体、gates_summary.json、各门输出、T7_EXCLUSIONS_RS6.tsv、SYNC_NOTE。

## 八门（全部必跑，证据落 docs/plans/repo_sync6_20260929/out/）

T1 领地锁定：只写上述范围；禁碰 evalset/ tests/ mcp_server/ rag_snapshots/ kb 生产码目录；禁 rebase/amend/reset/改历史；禁 push（push 归协调者授权窗）。
T2 冻结面不变：commit 前后对冻结清单逐件 sha 全等（复用 rs5 的冻结清单件）。
T3 脱敏引擎 v4 幂等：对新增内容跑 v4 引擎 scan=0（复用 scripts/ 下 rs5/既有脱敏脚本管线，输出 masked 落盘到暂存路径，禁回写 /mnt/D 原件）。
T4 T7 敏感扫描永久门：HARD=0（ADVISORY 通名可留，沿 PI 口径）；ghp_/github_pat_/gho_/sk- 全模式扫。
T5 黄金 41 复跑：training-venv 锁版 tests/verify_repro.py 41/41（本轮纯数据件不动引擎逻辑，此门为永久门仍须跑，systemd-run MemoryMax=8G 托管）。
T6 新鲜克隆可运行：file:// 克隆本 commit，tracked 文件数对账 + fsck clean。
T7 人查台账：逐新增件列 sha 台账；凭证类字面量一律变量引用、写后 grep 星号自查（教训条款）。
T8 拓扑：恰 1 新 commit，fa4f175 之上线性可快进。

## 纪律

- 中间产物全保留（脚本/日志/台账），全部落盘留证，禁删除。
- 完成或遇阻必须调 kanban_complete/kanban_block 落卡，summary 写明新 commit sha + 八门数字。
- 自报路径必须与实际落盘逐字一致（RS5 后教训：协调者拿你自报路径核账）。
- 遇任何门不过：如实 FAIL 落卡，禁回调球门、禁跳门。


> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked（类别描述化，非患者数据语义零改动）。线上原件留机器侧；逐件登记=docs/plans/repo_sync6_20260929/ledgers/T7_EXCLUSIONS_RS6.tsv。本注为同步卡处置留痕，不改变任务书条款的规范语义。
