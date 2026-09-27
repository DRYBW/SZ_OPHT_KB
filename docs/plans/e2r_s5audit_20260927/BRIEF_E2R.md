# BRIEF_E2R — S5 宽容口径收口核验（E2 尾账，PI 放行 20260927）

## 上游与继承（先读，逐条核对）
- 放行件+裁决继承清单：/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md
- 被收口件：/mnt/D/EyeKB/plans/e2_decontam_20260926/E2_VERDICT.md（§5 S5 行、§7.2、§9 裁决记录）
- 输入（只读）：e2_decontam_20260926/{e2_decon_rules.json, out/e2_panel_water.tsv, out/e2_homology_water.tsv, data/e2_matrix_rows_summary.tsv, scripts/}；kb/markers v5 面板 pmid_context 字段所在文件；RAG papers 语料侧（定位 HRCA 本体论文用于"首条即 HRCA"判定）

## 背景一句话
E2 的 S5 敏感性显示：若 v5 pmid_context(n_hits)（120 对）全算外部证据链，去同源效力几乎全被抵消、Q5b 水分读数从 +32.55pp 塌向 0——但该口径下 PMID 身份不可考。本卡把"可考性"实测出来，给水分账一个三口径区间，W 档不动（否决列 -6.63pp 恒定，E2 §9 已生效）。

## 任务
1. **清单化**：从 E2 产物中提取全部 pmid_context 命中基因对（约 120 对，以 data/ 实际行数为准），逐对列出所引 PMID/top_titles。
2. **身份核验**：逐对经 EuropePMC/PubMed API 验证该 PMID 真实存在、标题期刊可解析、与该基因-细胞类型断言相关性（关键词级判定即可）；单独标记"检索命中标题首条即 HRCA 本体论文（PMID 41578023 或语料内对应件）"的对数。核验原始返回落盘 ledgers/。
3. **S5b 可核验口径重算**：仅"PMID 可核且非 HRCA 自引"认账为外部链，复用 E2 打分脚本复刻逻辑（copy 进本卡目录改参，禁动 E2 原脚本）重算主面与 Q5b 水分账，产出三口径对比表：S1 严格 / S5b 可核验 / S5 全认。
4. **收口件**：E2R_NOTE.md（含对 E2 §7.2 的响应："若 PI 认 S5b，Q5b 水分读数区间为 [X, Y]pp"；禁任何 W 档改判表述），并 append 一行到 out/e2_history_register.tsv 的同源副本（写本卡目录，不回写 E2 目录）。

## 判读矩阵（预注册，机械执行）
| 观测 | 记账 |
|---|---|
| 可核验率 >=50% 且非 HRCA 自引占多 | S5b 口径成立，水分账按区间报，交 PI 决定未来评测是否采 S5b |
| 可核验率 <50% 或大量 PMID 虚构/离题 | S5 定性为"不可核不认"维持 E2 主规则，结案 |
无论哪行：W2 与 E1/E2 裁决零改动；"虚构 PMID"若发现，单列清单（这是 KB 数据质量发现）。

## 领地与红线
- 全部产物只落 /mnt/D/EyeKB/plans/e2r_s5audit_20260927/；kb/、mcp_server/、evalset 冻结卷、evidence_scoring/e2_decontam 两目录全程只读，输入 PRE/POST sha 台账。
- 零 LLM 判读调用、零生产码 import（eyekb_core 不 import，用 E2 复刻件）、零下载（API 检索返回即落盘）。
- 完成或遇阻必须调 kanban_complete/kanban_block 落卡；中间产物全保留。
- 工作目录：/mnt/D/EyeKB/plans/e2r_s5audit_20260927/（自建）
