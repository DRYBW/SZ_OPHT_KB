# OBSERVE_NOTE — KB9 案A 激活跟票观察（仿眼表 v6 条款）[t_abfebe59]

状态: **生效**（RULING_KB9ACT_2 核定案S，激活维持；回退作废分支未触发）——跟票窗口 2026-09-30 起算 7 天至 2026-10-07（含），采样口径同 A2 眼表模式。

- 起算日: 2026-09-30（W2 探针捕获日；② 已按案S核定通过，全部行为门绿）
- 窗口: 7 天，至 2026-10-07（含）
- 对象: 生产 MCP query_marker 默认态（library 缺省=all）响应，激活版本 KB1v2-0.7-k9act

## 采样口径（每日）
1. 源: /mnt/D/EyeKB/logs/mcp_trace/calls_*.jsonl 中 tool=query_marker 且入参未设 library 的请求（默认态）；当日无默认态请求=空采，照常登记一行"空采"。
2. 机械核查（可用 scripts/kb9act2_capture_t_abfebe59.py 的 canon sha 口径做日际对比）:
   - 触发A: k9 四条（Melanocyte/Schwann/Conj_epithelium_suprabasal/Limbus_Sclera_fibroblast_C1）在非眼表输入的 ranking **首位/上位**（n_shared 并列组内排名≠尾部）且输入明显为视网膜/脉络膜面板；
   - 触发B: 非 k9 类次序较前一日发生翻转（subsequence 位移）；
   - 触发C: 泪腺名泄漏（cell_types 出现 lacrimal*，或 lacrimal_v6 经 env/入参挤入默认路径）。
3. 任一触发 → 立即回退（调用方进程 env 设 EYEKB_ACT_K9=0，无需改数据，A5 纪律），并回本文件登记触发证据+回退时刻，上报协调者（default4）。

## 已知并观察但不触发的行为（本次 ON 态实测登记）
- 视网膜/鼠源面板输入在 ranking/unranked **尾部**出现 n=1 的 k9 条（TRPM1→Melanocyte ×2 例；炎症/损伤相关基因→Conj_epithelium_suprabasal ×1 例，均在 22 簇回归集内）。这是跨组织真实共表达基因进入默认检索面的激活固有行为，非"上位"，不属触发A；判读侧以 applicability=ocular_surface_only（_k9_ocs_rules_overlay_v1.json，INERT 旁挂，判读 run 直读）消解。
- 所有默认态响应的 provenance.files / soft_flags.trigger.data_snapshot 增加 1 行 k9 文件台账（激活的透明登记，预期变化）。

## 执行归属
建议由巡检 cron 或协调者派发独立观察卡执行；本卡只落口径（禁扩权不自建调度）。窗口结束日回填结论：无触发=转正式在册；有触发=回退+复议。
→ 09-30 协调者（default4）已登记执行件：no_agent 每日巡检 cron c9b829c74c66（09:30 采昨日，脚本 kb9act_daily_check.py，判定逻辑对齐 kb9act_t7_check.py；台账本目录 ledgers/kb9act_daily_log.tsv，state 供触发B日际对比）；另有 10-07 09:00 收口 cron b1dca3ebd5a1。触发即回退+上报，正常静默。
