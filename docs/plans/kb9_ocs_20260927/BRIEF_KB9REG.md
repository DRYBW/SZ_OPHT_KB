# BRIEF_KB9REG — KB9 注册包 v2 重装 + REVIEWER_LLM 二审（D10，PI 09-27 放行）

## 上游与继承
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加二 D10（含 A02 红线操作定义落定文本，注册包必须引用）
- 复核裁决源：/mnt/D/EyeKB/plans/kb9_ocs_20260927/recheck/RECHECK_REPLY_20260927.md（REVIEWER_LLM xhigh，prompt sha 3072…5274d）+ RECHECK_ACTIONS.md 19 条处置表
- 底件：kb9_ocs_20260927/build/（词条+屏蔽表）+ KB9_BUILD_REPORT.md（P1 22/33 FAIL/P2 0/33 不动）

## 任务
1. **注册包 v2**（register/ 新目录，build/ 与 kb/ 均不动）：REVIEWER_LLM 接受项逐条落实成文——① 开发集定位限定声明（A01，标题页级）② agg 参考池×D002 study/donor 重叠登记表（A03）③ 装配规则 v2 文本：n_shared=0 不入 top3、有效候选<3 不加载顺序补齐、新条加载位置+平票规则冻结（A05）④ R1 逐条 ID-组织适用范围表含跨文件重复条目处置（A06）⑤ 投票前诊断表输出规格（A07）⑥ Keratocytes→评价词表映射冻结声明（A09）⑦ 组批语义+gene_hits 依赖检查条款（A13）⑧ 可达性算术模板 G-L>=3（A16）⑨ 措辞修订：pericyte/SMC"当前方法下未能稳定区分"、混合面审计正名、OLS=词条级命名证据（A17/A18/A19）⑩ 删除"换判据域"表述（A15 措辞部分）。待 PI 项（A04/A08/A10/A14/A15 子项）单列"未执行-归 PI"节，禁夹带。
2. **BUILD_REPORT 表述层补记**：文末 append EDITORIAL_NOTE（A11 混合票=缓存式自检定位、A13 解释性局限登记、A17/A18 措辞限定），**数字与裁决零改动**。suprabasal 条复核（A15 子项）：按 §1.2 冻结准入复算一遍出判件（只判不改，去留归 PI）。
3. **REVIEWER_LLM 二审**：prompt=注册包全文 verbatim+逐条对照 REVIEWER_LLM 上轮意见的"闭合位置+原文摘录"（信息差铁律），请求逐条【闭合/未闭合】+签发文本；LLM_CHANNEL通道（AGENT_ROLE 现成发送器，先 pgrep 防撞），503 连败则降级 qwen3.8max（LLM_CHANNEL，登记实际裁定模型，PI 预授权沿用）。回稿 ACCEPTED 备份+通道释放。
4. 二审若 PASS：注册申请状态="过外审待 PI 批注册"（批不批、何时接线仍归 PI，本卡零接线零 kb/ 写）。

## 纪律
- 产物只落 kb9_ocs_20260927/register/；全部输入只读+sha 台账；零 LLM 判读（二审送审除外）；完成或遇阻必须落卡。
