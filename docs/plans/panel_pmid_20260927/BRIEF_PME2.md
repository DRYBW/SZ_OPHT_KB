# BRIEF_PME2 — 面板证据链补录第二批（103 键，PI 锁定中等档口径，放行 D7）

## 上游与继承
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加一 D7；第一批账见 /mnt/D/EyeKB/plans/panel_pmid_20260927/PME_NOTE.md
- **口径由 PI 锁定**："expressed in <该细胞类型>"算 membership 型支持=中等档为现行正式口径（批注写进产出件头）；类特异严格档不再议为默认，若未来收紧须全库对称重判并另卡。
- 输入：out/batch2_backlog.tsv（50 weak + 53 none）；第一批 sidecar/引擎/账件只读复用（copy 进本卡目录，禁改一批原件）；E2R 告诫继承：pmid_context 共现通道不用于补录。

## 任务
1. weak 50 键优先救回：第二检索式（类同义词/蛋白别名表——**若开别名必须全类对称**，别名表落盘可审计）+ sort=CITED 遍复用；none 53 键中挑 v6 repair 统计派生基因再扫一遍摘要级文献，查无维持 none 如实登记（诚实阴性，禁软证据升档）。
2. 产出 evidence_chain_supplement_v2.json（旁挂，v1 与 kb/ 面板字节不动）+ PME2_NOTE.md：终态 strong/weak/none 增量账、救回清单逐键证据句、残余 none 定性（"真缺文献"vs"摘要级不可核"两态）。
3. 汇总"两批合计可核链覆盖"最终读数（对照 E2 567 对基账本），供未来评测口径修订引用；**不改 E2 任何数字**。

## 领地与红线
- 只写 /mnt/D/EyeKB/plans/panel_pmid_20260927/batch2/；kb/、E2/E2R 目录只读+sha 台账；零 LLM 判读、摘要级检索零全文下载；完成或遇阻必须落卡，分批落盘留痕。
