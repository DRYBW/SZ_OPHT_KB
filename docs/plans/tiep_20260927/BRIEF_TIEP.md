# BRIEF_TIEP — 平票/弃权协议反事实评估（KB9 11 miss 中 8 个协议结构位，PI 放行 D6b）

## 上游与继承
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加一 D6b
- 问题来源：/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_verdict.json 的 missed_modes（tie×8/abstain3×2/majority×1）与 BUILD_REPORT §3 归因；已知案 Q6::30（两席 Epithelium 但第三席 grade C 被现行票规则弃）
- 继承：现行三票多数制协议（RUN4-r 起）**本卡不改**，协议变更勾选归 PI

## 任务（全部盘上票面，零新判读）
1. **盘点**：从 RUN3/RUN4-r/RUN5/FACEV21/KB9 存档票（逐席 grade+label）统计 tie/弃权发生面：各面票数、grade 分布、因破缺规则损失的潜在命中。
2. **反事实重投票**（机械模拟，不重跑 LLM）候选规则并行报：C1 grade 加权票（A=1.0/B=0.8/C=0.4 示例档，档位敏感性 w 网格）；C2 tie 法定人数（≥2 席同标签即定名，第三席粗判不弃全）；C3 tie→证据分 S1 具名破平（复用 E2 decon 规则件，离线用途合规）；C4 维持现状基线。每规则报：净翻正/翻错两面数、对既有已 PASS 结论的改动清单（禁静默改判，全部列出差集）。
3. 产出 TIEP_PROPOSAL.md：规则×数字×风险表+建议档+PI 勾选位；判读纪律=任一规则若使既有 PASS 案翻错，直说。

## 领地与红线
- 只写 /mnt/D/EyeKB/plans/tiep_20260927/（自建）；全部票面/冻结件只读+sha 台账；零 LLM、零网络、零生产写；完成或遇阻必须落卡。
