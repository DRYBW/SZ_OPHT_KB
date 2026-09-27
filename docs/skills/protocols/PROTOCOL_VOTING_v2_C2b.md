# PROTOCOL_VOTING_v2_C2b — 票规 v2 决策件（C2b 主档，向前生效）

- 卡：t_03808fff ｜ 任务书：/mnt/D/EyeKB/plans/proto_v2_20260927/BRIEF_PROTO.md
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加二 **D11**（"投票协议 v2=C2b 主档批准：向前生效（本协议件落款日之后预注册的 run 起），历史冻结裁决不回改；D9 的 run 按'主读 C4+并列 C2b'处理"）
- 规则实证：/mnt/D/EyeKB/plans/tiep_20260927/TIEP_PROPOSAL.md（五规则×五面机械反事实重投票，零 LLM；OVERTURN=0 硬校验）
- 落款：2026-09-27 ｜ 性质：决策件（纯文本+指针；本卡零脚本改动、零生产写、零 kb/）

## 1. v2 操作定义（C2b，逐字照 TIEP 推荐档）

TIEP §2 逐字：

> **C2b 法定人数+粗判入数**：同 C2a，另 coarse:X 计入标签 X 的法定人数（"第三席粗判不弃全"宽读法）。

> **C2a 法定人数**：定名票任意 grade 计数，≥2 席同名即定名。

操作化分解（与参考实现 `t1_revote.py: rule_c2(bs, count_coarse=True)` 完全等价）：

1. **定名票**：票面携具体标签（identity 非 `undetermined*` 且非 `coarse:` 前缀、非缺票）者，**任意 grade（A/B/C）计入**该标签法定人数——grade C 定名票不弃（与 v1=C4 弃 grade C 的唯一差异之一）。
2. **coarse:X**：identity 以 `coarse:` 为前缀的票，按冒号后标签 X **计入标签 X 的法定人数**（"第三席粗判不弃全"宽读法）——与 v1=C4 弃 COARSE 的另一差异。
3. **定名门**：**≥2 席同名即定名**；仅 1 席有效票（tie@1）不定名。
4. **平票残余=S1 破平禁用，维持无名**：C2b 不引入 S1 证据破平（C3a）或单票确认（C3b）——TIEP 勾选位"采纳 C3a/C3b=建议不采纳"成立；法定人数计票后的残余平票（同名最多者 <2 席）一律维持无名（tie/split3/abstain3 模式照旧记录）。
5. `undetermined*`/缺票不入数（与 C4 相同）。

对照 v1=C4 的基线数字（TIEP §2.1/§4，KB9 面）：P1 **22→29/33**（+7 翻正、0 翻错，P2=0 过门）；RUN4-r 15/22 与 FACEV21 19/22 两门面无任何扰动（保全条款 Q4::15∧Q5b::13 原样）；五规则×五面**无任何一例改动既有"已定名且正确"的结论**（OVERTURN=0，204 差集全量硬校验）。结构代价（直说）：coarse:X 语义跃迁——把判读者自报低分辨率票当定向票入数；KB9 面 7 例全对是小样本（n=3）实证，非保证。

## 2. 生效范围与每 run 版本声明（D11 硬条款）

1. **向前生效**：仅约束本件落款日（2026-09-27）**之后预注册**的 run。
2. **每 run 预注册必须声明适用票规版本**：`v1=C4` 或 `v2=C2b` 二选一显式写进 PREREG；未声明=不得冻结、不得开跑。
3. **历史冻结裁决一律不回改**：RUN3/RUN4/RUN4-r/RUN5/RUN6-B/RUN7-RG/FACEV21/KB9 已发布件数字仍按 C4 口径为历史冻结值；TIEP 反事实重票只是规则选型实证，不构成改判依据。任何规则若使既有 PASS 案翻错，直说；"用新规则回改 RUN5 结论"本身是门失败，不是翻案收益（TIEP §5.1 逐字继承）。

## 3. 过渡条款（D9 B-test，唯一例外且一次性）

D9（RAG 自由查询 A/B 正式验证，plans/btest_20260927/）预注册先于本件票规切换，按放行档处理：**主读=现行 C4 票规（保 15/19 基线可比），C2b 机械另算并列同表，零额外席位票**（USER_DIRECTIVE_20260927_scoring_wave 追加二 D9 分叉代拍 + BRIEF_BTEST"并列读"条款）。本条款仅对 D9 该 run 有效，不构成"双主读"先例；D9 之后新预注册 run 一律按 §2.2 单版本声明。

## 4. 附带执行条款（TIEP §4 推荐档全三条，D11"按 TIEP 推荐档写死"）

1. **生效范围条款**：已并入 §2（新预注册 + 生效范围=下一 run 起 + 历史不回改）。
2. **P2 门不自动破**：C2 档下新增定名簇**自动进 P2 污染检查**（撞 kb 名单即计 P2），无需改门（KB9 面实测 P2=0）。
3. **词表漂移独立登记**：票面盘外名（Keratocytes/Mac_DAM_LAM/coarse:Stromal 等）任何 tie 规则都不解决——自 v2 生效起，各 run 预注册须含**"票面名过冻结 crosswalk 归一"**条款（crosswalk 为冻结件，逐 run 登记 sha）。

## 5. runner 落点与参考实现

- 现行投票实现盘点（只列不改，下一波各 run warmup 卡照单分叉）：/mnt/D/EyeKB/plans/proto_v2_20260927/RUNNER_WATCHLIST.md
- C2b 参考实现：/mnt/D/EyeKB/plans/tiep_20260927/scripts/t1_revote.py（sha256 d321e793…）`rule_c2(bs, count_coarse=True)`；C4 复刻=同文件 `c4_consensus()`（四面 156 行 consensus/mode 与已发布件逐行对账 PASS）。
- 注释协议新版本（原地 v1.1 不动，copy 不 move）：/mnt/D/EyeKB/plans/ANNOTATION_PROTOCOL_v1.2.md §8。
