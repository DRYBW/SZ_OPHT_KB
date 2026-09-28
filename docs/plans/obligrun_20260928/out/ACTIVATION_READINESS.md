# ACTIVATION_READINESS — KB9 k9_ocs 激活就绪建议票（t_c145db7c run142，2026-09-28）

**性质：建议票。本卡零接线零激活零默认切换；OB-5 永久门归 PI 另批，本文件不构成任何激活动作或承诺。**

overlay=_k9_ocs_rules_overlay_v1.json obligations_before_activation 逐门状态（义务 run 当期实测）：

| 义务 | 状态 | 当期证据 |
|---|---|---|
| OB-1 历史 ON 态门 AV2-5(c) | 清 | out/OB1_ledger.tsv + ADD1 A4（v2.1 差异仅 2 lit 行，31 簇逐字节零漂移） |
| OB-2 A07 投票前诊断表首跑 | 清 | out/pre_vote_diagnostics_v21.tsv（硬断言 33/33；57/57 零漂移含未涉簇对照） |
| OB-3 22 视网膜簇 Arm1/Arm2 完整 ranking 一致性 | 清 | out/OB3_consistency.tsv 22/22（案 A ranking 零动，继承有效） |
| OB-4 lit 逐条同源排除筛查留档 | 清 | out/OB4_lit_screening_v21.md 0 残留（v2.1 净化面）+ v1 命中两行剔除台账 |
| OB-5 激活 | **未做——永久归 PI 另批** | 不在本卡范围（BRIEF/PREREG/RULING 三件一致） |

球门（票规 v2 C2b，当期 99 新票，v2.1 面）：
- **P1 = 26/33 ≥ 24/33 → 达标**（C2b 定名 28/33；未达 7 簇集中于 Fibroblasts/Pericytes 谱系带：5 无名 + 2 named-but-wrong[SMC←Pericytes、Keratocytes←Fibroblasts]）
- **P2 strict = 0/33 ≤ 1/33 → 达标**（any 并报 0/33）
- P3 kb 空率 13/33 照旧记录（不入门）

判读：§10-6 义务门全清且球门达标——**建议票：可送 PI 批激活**。
随票限制（PI 决策必读）：①开发集同源，本球门=工程验收非独立验证（注册包 §0/§2）；②C2b coarse:X 入数语义跃迁（协议 §4）；③chen_* 三 study source paper 未解析的筛查残余限制；④激活后下游（REPOSYNC3 前置盘点项）已登记。
