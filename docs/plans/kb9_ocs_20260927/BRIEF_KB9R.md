# BRIEF_KB9R — KB9 设计决策复核补送（REVIEWER_LLM 主、qwen3.8max 降级 PI 预授权）

## 上游与继承
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加一 D6a（含 PI 原话"REVIEWER_LLM 可以临时给 qwen3.8max"）
- 送审件（现成）：/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/REVIEWER_LLMrecheck_prompt.txt（四问：R1-R3 屏蔽规则/混合票复用/KB7 分歧处置/可达性）；KB9 上次 503×5 留痕在同目录 REVIEWER_LLMrecheck_*.txt
- 继承：KB9 自检 P1 FAIL/P2 PASS 结论不因本卡改判——本卡只裁**设计决策**（若评审抓到实质设计缺陷，处置等 PI）

## 任务
1. 通道优先级：REVIEWER_LLM（LLM_CHANNEL站，AGENT_ROLE 现有发送器/cycler；先 pgrep 确认无人在跑再发）。503/连败即降级 **qwen3.8max**（LLM_CHANNEL通道，长输出必带 enable_thinking:false）。
2. 回稿验收：稳定+含逐问裁决；**回稿头部登记"裁定模型=<实际名> + 时间 + prompt sha"**——降级件不得写成 REVIEWER_LLM 裁决。
3. 落盘 /mnt/D/EyeKB/plans/kb9_ocs_20260927/recheck/（新目录，不覆盖原目录既有件）；若评审提出必修/建议项，出 RECHECK_ACTIONS.md 逐条列"接受/待 PI/不适用+理由"，执行归后续卡。
4. 完成或遇阻必须落卡。领地：只写 recheck/ 目录；kb/、面板、评测冻结件只读；零下载。
