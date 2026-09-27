# BRIEF_BTEST — RAG 自由查询 A/B 正式验证（D9，PI 09-27 放行）

## 上游与继承（逐条核对后动笔写 PREREG）
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加二 D9+D11；设计蓝本=/mnt/D/EyeKB/plans/rag_anno_usability_20260927/RAG_ANNOTATION_USABILITY.md §B（五要点照抄骨架）
- 基线：FACEV21 19/22∧0/23∧保全 2/2（plans/face_v21_20260926/）、RUN4-r 15/22；红线操作定义=redline_rewrite 追加节（本 run 属判读/取证侧，合规）
- 考卷：FACEV21 冻结面 45 簇（sha c4a47e39… 逐字节复用）；席位 qwen3.8-max/glm-5.1/deepseek-v3.2（LLM_CHANNEL，长输出 enable_thinking:false），T=0.2 同参；工具=MCP 五工具现服务只读使用（禁改 server/kb/面板；calllog 留痕=正常服务副作用）

## 判读矩阵（预注册冻结，写进 PREREG 后再跑）
- **稳定性门（先于对比）**：B 臂全量独立跑 2 次，簇级 C4 定名一致率 ≥90% 方有资格进 A/B 对比；<90% → 判"不判、先治非确定性"，出诊断报告收卡。
- **主判读（C4 票规）**：B 臂 ≥19/22 ∧ R2≤1/23 ∧ 保全双过 → PASS"B 不劣于 A"（再议替代价值，归 PI）；≥15 但 <19 → 部分成立（净损失逐簇归因）；<15 或 R2 破 → B 不达（维持 A 唯一形态）。
- **并列读（零额外票）**：同一批 B 臂票 C2b 机械重算同表并报（D11 过渡条款）；成本列（每簇调用数/时长/token）必录。

## 纪律与红线
- PREREG sha 先落纸（禁球门一字改动，双基线 15/19 写死）；全部输入 PRE/POST sha 台账；evalset/kb/mcp_server 只读；产物只落 /mnt/D/EyeKB/plans/btest_20260927/；B 臂不给 EV_DIGEST（唯一变量=取证方式），逐簇 calllog 非空硬断言；完成或遇阻必须落卡；分批落盘留痕防 crash 重跑（断点续跑清单照 FACEV21 runner 惯例）。
