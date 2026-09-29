# USER_DIRECTIVE 2026-09-24：Q2 真值主口径切换（PI "ok" 确认，项目维护方代录）

## 决定
自本件起，涉及 Q2 (GSE155288) 真值的对外数字，**主口径=truth_corrected**（truthfix_v1 派生列）：
- RUN3 头条以 errata v1.1 α 口径为准：n=197，A(qwen3.8-max)=60.9%，B(glm-5.1)=70.05%
- v1.0（作者原始真值）件全部保留为历史档案，引用时须标注"含已知作者错标簇 C18/C19"
- Q2::18 定性=作者错标（真值为 Rod 程序细胞）；Q2::19=doublet-suspect 逐出真值计分区

## 连带
1. RUN4 及后续所有 RUN 的 Q2 相关判读/裁决一律走 corrected 口径（RUN4_PREREG.md 的 errata 追加段已含靶单 23→22）。
2. 对外叙事（M1 论文/科会图）引用 GSE155288 时须带标签质量注记（11 类粗注释含错标簇，见审计件 v1.1）。
3. 盲区线结案数字（真杆判 BC=0.004%）本身已用 corrected 口径，不受影响。

## 状态
- PI 语义：2026-09-24 对"建议切 truth_corrected"回复 ok（MSG_PLATFORM）
- 生效：即时
- 撤销条件：GSE155288 作者发布修订版 ident 且通过我方复核时，重新评估口径
