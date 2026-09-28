# BRIEF_OBLIGRUN — KB9 k9_ocs §10-6 义务 run（PI 2026-09-28"批准"启动）

上游依据（先全部读）：
- /mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加四节（放行边界与红线）
- /mnt/D/EyeKB/kb/markers/_k9_ocs_rules_overlay_v1.json 的 obligations_before_activation（OB-1..OB-5 原文）
- /mnt/D/EyeKB/plans/kb9_ocs_20260927/register/REGISTER_PACKAGE_v2.md（§6 A07 诊断表列规格、§8-4、§9 lit 同源排除、§10-6 义务表；球门 P1>=24/33 与 P2 口径以注册包为准）
- /mnt/D/OcularKB/WIKI/PROTOCOL_VOTING_v2_C2b.md（票规 v2 主档，向前生效，每 run 预注册声明票规版本）
- 票面=/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_face_arms.json（33 簇）；runner 参考实现=kb9_ocs_20260927/scripts/ 与 kbx_lacrimal_20260928/scripts/（seat/票/裁决脚本命名惯例 *_t_<卡号> 另立不复用）

## 任务（一个 run 内完成，产出落 /mnt/D/EyeKB/plans/obligrun_20260928/）
0. **预注册先行**：PREREG_OBLIGRUN.md 写死票规版本声明（v2 C2b）、球门（P1>=24/33、P2 按注册包）、判读矩阵（见下）、LLM 票预算上限 150——**先 sha 落纸再执行**。
1. **OB-1 AV2-5(c) 历史 ON 态门**：RUN5 时刻完整请求/存档快照逐字段对账（含批组成快照），G1 不等于历史 ON 保真；产出对账表 OB1_ledger，任何字段级漂移如实登记并判"清/不清"。
2. **OB-2 A07 投票前诊断表首跑**：按注册包 §6 列规格产 pre_vote_diagnostics.tsv；票面与诊断表不一致=run 作废（停卡上报）；Q6::26 型掏空回退须可指认。
3. **OB-3 22 视网膜簇 Arm1/Arm2 完整 ranking 一致性补查**：排序/去重/加载序副作用逐项核；产 OB3_consistency.tsv（逐簇判定）。
4. **OB-4 lit 逐条同源排除筛查留档**：命中列表/判定/剔除动作逐条落盘（注册包 §9）；产 OB4_lit_screening.md。
5. **正式三席票 run**：LLM_CHANNEL通道三席同参（channel=key 扫各 profile config.yaml 共用；调用必带 enable_thinking:false），逐簇判读 jsonl 落盘；票规 v2 C2b 计分；上限 150 票，超限立即 block。

## 判读矩阵（预注册，if-then 写死）
- OB-1..4 全"清" 且 P1>=24/33 且 P2 达注册包口径 → VERDICT=**READY**：产 ACTIVATION_READINESS.md（含逐门数字与建议票"可送 PI 批激活"）；**不激活**（OB-5 归 PI 另批）。
- 任一义务"不清" 或 球门不达 → VERDICT=**NOT_READY**：如实逐门报，禁改写历史 C4 记录，禁"将激活/接近激活"式措辞。
- 诊断表不一致/票面作废条件命中 → block 上报，作废留痕不重跑粉饰。

## 纪律红线
零接线零激活零默认切换；kb/、mcp_server/、evalset/、注册包、_k9_ocs_rules_overlay_v1.json 全程只读（产物全落本卡 plans 目录，copy 不 move）；历史冻结件不回改（新结果单独成节+互引文件名）；LLM 票只在第 5 步用；中间产物（脚本/日志/票面原始 jsonl）全保留；泛化"提升 X%"禁；完成或遇阻必须调 kanban_complete/kanban_block 落卡，收尾产 VERDICT_OBLIGRUN.md+sha 台账。
