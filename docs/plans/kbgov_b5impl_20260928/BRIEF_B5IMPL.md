# BRIEF_B5IMPL — KBGOV 主候选 B5 实装（query_marker 跨物种 ranking 治理，追加五预授权队列①）

依据：/mnt/D/EyeKB/plans/kb_gov_20260928/{KBGOV_CANDIDATE.md, KBGOV_PREREG_v1.1.md}（B5=主候选，机械 A/B 双门证据在案）；USER_DIRECTIVE_20260928 追加五（OBLIGRUN 收口自动接续，落地=接线级修复带回归门+可回退）。

## 改动面（仅 mcp_server/，kb/零触碰）
- query_marker genes-mode 入口按实装书 G1：鼠源输入 confirmed+suspected → 拒答具名（removed/annotated 按候选件 §G1 语义）；AMBIG 共表达证据仅标注不删序。
- **env 开关 EYEKB_KBGOV_B5**：实装后默认 ON；置 0/未设=回退态，回退态响应与 pre 基线**逐字节全等**（A5 式验收件机读自证）。
- 版本注记 server version 递增（0.5-k9reg→0.6-kbgov5），REGISTERED_DEFAULT_OFF 语义（k9_ocs/lacrimal_v6）不得破坏。

## 验收门（全过才算实装成功，任一不过=block 回滚）
1. 病灶门：BTEST Q7::11/15/21/22/52/58/61 七簇 B5 形态**零具名残留**（对照候选件 7/7 口径）。
2. 人源零位移门：calls jsonl 人源 230 簇流量重放 ranking 位移=0.0%（预注册过杀线>5% 语义沿用）。
3. 回归门：黄金 41/41 off 态全等 + 42-probe（off 态）+ G1-G4 套 + tests/probe_repo_mcp 系断言；ON 态三席探针 smoke 通过。
4. 回退门：EYEKB_KBGOV_B5=0 与 pre sha 台账双态对照（B5IMPL_A5_ROLLBACK.tsv）。
5. 留痕：SHA_PRE/POST 全件台账；kb/、evalset/、注册包、overlay、plans/kb_gov_20260928 只读复验零写入。

## 纪律
观察条款：上线后 T+7 calllog 采样（登记 cron 建议项给协调者，不自行建 cron）；异常信号→按回退门操作并落卡。仓面零 push（REPO_RESYNC_B5IMPL.md 登记）。禁 import 实验复刻件——以生产码内实现+复刻件对账双源一致为准。中间产物全保留。完成或遇阻必须调 kanban_complete/kanban_block 落卡。产物目录 /mnt/D/EyeKB/plans/kbgov_b5impl_20260928/。
