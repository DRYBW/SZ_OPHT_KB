# GRADE_ANCHOR — 判读席 grade 判序漂移锚分析与 H1 反事实（D16，2026-09-28）

- 卡：t_5522de51 ｜ 任务书：BRIEF_GRADE.md ｜ 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md D16
- 方法边界：纯存档重算（零 LLM、零网络、零新票）；ANNOTATION_PROTOCOL **未改动**（修订件为草案待 PI）；
  历史冻结裁决零回改；票档/协议/evalset 只读，输入 sha 台账 data/SHA_LEDGER_INPUTS.txt（52 件）。

## 0. 总判定（一句话）

判读席 grade 漂移在九档期冻结票面里是**系统性"过度保守丢正确名"**（具名∧C 票 28 张中 25 张隐藏名==truth，89.3%），
不是噪声过滤（降C率与保留票命中率 Spearman -0.171≈无关）；H1 判序锚（推荐档 **H1-M3**）在全部 9 个 archive
反事实重算中 **翻正 7 案 / 新错 0 / 回归 0**，grade 通胀的唯一实证案（H1-X 档 RUN5 Q6::31）被 M3 的
"至少一门判别 pass"条件挡住。是否升为协议条款交 PI 拍板（草案见 §5）。

## §1 矩阵复原与验证

- 复原"席×簇×grade"矩阵：**1,817 票行 / 13 archive / 291 簇**（data/ballot_matrix.tsv），
  覆盖 RUN2/3/3MINI/4/4-r/5/6A/6B/7RG/FACEV21/KB9/BTEST-run1/2（含席位模型映射，META 交叉校验 0 不一致）。
- 七道验证闸门全 PASS（data/verification_gates.json）：
  G1 C4(FACEV21)=已发布 45/45；G2 C4(BTEST run1/run2)=已发布 45/45×2；G3 C2b(FACEV21)=TIEP 发布件 45/45；
  G4 C4(RUN4-r)=run4r_verdict 45/45；G5 C4(RUN7RG)=RG_VERDICT 45/45；G6 C4(RUN5 Q6)=发布表 33/33；
  truth 独立重建（truth_major）vs btest 表 truth 列 45/45 全等。
- 锚点复算对账：重算 R1/R2 = RUN4-r 15/22 & 1/23、RUN7RG 17/22 & 4/23、FACEV21 19/22 & 0/23、
  BTEST-run1 17/22 & 2/23 —— 与 BTEST §3/§6 发布数全等。

## §2 漂移账（量化结果）

### 2.1 各席 grade 分布与漂移（九档期，data/seat_grade_dist.tsv）

| 席位模型 | 平均 C 率（全体票） | 具名票降C率 | 有效票命中率 | 降C隐藏名正确率 |
|---|---|---|---|---|
| deepseek-v3.2（C席） | **0.268** | **0.069** | 0.880 | 14/15 = **93.3%** |
| glm-5.1（B席） | 0.143 | 0.029 | 0.937 | 6/8 = 75.0% |
| qwen3.8-max（A席） | 0.143 | 0.018 | 0.922 | 5/5 = 100% |

- deepseek-v3.2 的 C 率≈另两席 1.9×，而其降C的具名票 93.3% 实为正确名——**弃名不弃错**。
- 时序（data/gradeC_rate_timeseries.tsv）：deepseek C 率 0.222(RUN4-r)→0.273(RUN5)→0.333(RUN6A)→0.356(BTEST-run1)
  →0.440(KB9)，**自由查询/长会话形态下判序漂移加重**；FACEV21 面（卡片层 3A 修后）三席具名∧C=0，
  但 BTEST 自由查询臂同型案复发 5 票——**卡片层修复不外溢到工具/会话层**（与 BTEST §7.2 推论一致）。

### 2.2 BTEST run1/run2 同席成对漂移（data/btest_run_pair_drift.tsv）

| 席 | grade 翻转 | identity 翻转 |
|---|---|---|
| A（qwen） | 0/45 = 0% | 1/45 = 2.2% |
| B（glm） | 4/45 = 8.9% | 6/45 = 13.3% |
| C（deepseek） | **11/45 = 24.4%** | **14/45 = 31.1%** |

C 席是 BTEST §7.3 已指认的最大方差源；grade 维度同样成立（run1 降C 6 票在 run2 收回、5 票新增）。

### 2.3 正确名被降 C 全库扫（Q5b::35 型案，data/correct_name_demoted_C.tsv，27 案）

- 九档期 25 案 + 早期 pilot（RUN3/RUN3MINI）2 案。**其中"单票升回即可翻正"（其余席已有 1 张同真名有效票）7 案**：
  BTEST-run1 A/AC/Q5b::35（病灶原型）、RUN7RG A/Rod/Q5b::2、RUN5 A/Fibroblasts/Q6::13、
  KB9 C 席 Q6::16/26/29/30（Fibroblasts/Immune/Epithelium×2）。
- 其余 18 案降C未伤共识（另两席已 carry majority）或票源不足（tie 无法单票救），已逐案登记 gates/flag/why。
- RUN7RG B/Q7::52 为特殊案：真名 RGC 被降C，但共识已由 AC 伪影 majority 锁定——**grade 锚救不了证据面伪影**，
  与 BTEST §4 归因（库侧 ranking 治理）正交，两案各治各的。

### 2.4 "过度保守 vs 随机噪声"判据

- 降C率 × 保留票命中率：Spearman -0.171（n=27 席×archive 单元）→ 降C不选择性剔除错名；
- 降C隐藏名正确率 89.3%（LLM 九档期）→ 若为过滤噪声应远低于此；
- 结论：**方向上系统性过度保守（丢正确名），执行上带随机性（成对漂移 24-31%）——两者并存，主判过度保守**。
- 边界声明：早期 pilot 期（RUN2/RUN3）pC 0.29-0.40 且隐藏名正确率低（全量具名∧C 含 pilot 时 71.1%），
  判序纪律随证据面 v2/v2.1 演进才收敛到"降C≈误弃"形态；本判据只对九档期现行形态负责。

## §3 锚候选设计（可组合，均可预注册）

### H1 判序锚（协议层硬规则，卡片层 3A 升格）
- **规则文本**：具名票（identity=具体标签，非 coarse:X/undetermined）必须 grade≥B；"具名∧grade-C" 为非法票形，
  runner 应拒收或按判序锚自动下限化——席若坚持 C，必须改投 `coarse:<名>` 或 `undetermined`（协议本意：
  C=不可区分→只能粗判/弃权；能具名=已排除相邻候选→至少 B）。
- **操作化档位（反事实网格，data/variant_totals.json）**：
  | 档 | 判据（对具名∧C票施 grade 下限 B） | 升票 | 隐藏名正确 | 翻正 | 新错 | 回归 |
  |---|---|---|---|---|---|---|
  | H1-S | ie=pass ∧ res=pass ∧ tech∈{pass,na} | 8 | 100% | 3 | 0 | 0 |
  | H1-M | ie≠fail ∧ res≠fail ∧ tech≠fail | 19 | 84% | 6 | **1** | 0 |
  | **H1-M3**★ | **ie=pass ∨ res=pass**（technical 三门口径不参与，3A 同构） | **24** | **91.7%** | **7** | **0** | **0** |
  | H1-M2 | 同 M3 但 tech≠fail | 21 | 90.5% | 6 | 0 | 0 |
  | H1-X | 一律升（纯一致性锚） | 28 | 89.3% | 7 | **1** | 0 |
- **推荐 H1-M3**："具名+至少一门判别门 pass=至少 B"——即任务书"具名+可排除=至少 B"的票面机械翻译
  （identity_evidence/resolution 两门是"可排除"的存档可读代理；technical 门属 3A 禁降级项，不参与判序）。
- 红线合规：判据全部取票面自评字段（identity/grade/gates），零标签派生、零打分侧口径、零新票。
  证据消费纪律 v2 满足。

### H2 席间 grade 校准提示（prompt 层，软提示）
- 面向历史低一致席（deepseek-v3.2）与自由查询长会话：判读卡尾部注入校准句——
  "你给具名票打 C 时，历史统计显示该名字约 9 成是对的；若 identity_evidence 或 resolution 可判 pass，
  必须打 ≥B；否则请改投 coarse:<名> 或 undetermined。"
- 与 MCP 软提示纪律对齐：**只收紧"C 附具名"这一非法票形，不诱导更多 undetermined**（不新增弃权口径）；
  提示文本进预注册冻结件，禁按 run 临时改措辞。
- 定位=H1 的会话层前哨（让席位当场自纠，减少 runner 拒收/下限化次数）。

### H3 单席 C 率超阈值旗（复盘层监控，非生产硬门）
- 口径进 A4 复盘/跟票统计器：每 run 收票后机械计算——
  ①席级全体 C 率 > max(0.30, 2×三席中位数) 触发旗（九档历史命中：仅 deepseek BTEST-run1 0.356/
  run2 0.333/KB9 0.440 触发，qwen/glm 从未越过 0.267）；
  ②具名∧C 出现即记名（任何席 ≥1 票入复盘队列，H1 生效后应为 0——非零=判序锚失效报警）。
- 旗只做复盘与跟票统计，**不作废任何票、不改判读结果**。

## §4 H1 反事实数字（同型案全库，零 LLM）

- **翻正 7 案**（基线 tie/无名 → H1-M3 生效具名，且具名==truth）：
  Q5b::35(AC)、Q5b::2(Rod)、Q6::13(Fibroblasts)、KB9 Q6::16(Fibro)/26(Immune)/29(Epi)/30(Epi)。
  BTEST-run1 R1 17→18/22；RUN7RG R2 4→3/23（Q5b::2 出列）；KB9 具名覆盖 17→21/25。
- **新错 0**（H1-M3/M2/S 档）；H1-X/H1-M 各 1 案：RUN5 Q6::31——两张错误名票（B席 Pericytes∧C +
  C席 Pericytes(B)）在降C票入数后结成假多数，把"无名"翻成"错名"。**通胀机制 = 双错名互相坐实**；
  M3 以"ie=unresolved ∧ res=unresolved → 不升"挡掉该案（B 席票两门皆未 pass）。
- **回归 0**：9 archive × 5 档全部无"对→错/对→无名"案例——下限规则单调，不侵蚀既有正确共识。
- 稳定性门副作用（如实报）：H1-M3/X 生效后 BTEST run1 翻正而 run2 仍无名（A 席 run2 自改为
  coarse:AC ∧C——coarse+gradeC 是协议合法形态，H1 不触发），run1/run2 共识一致率 44→43/45=95.6%，
  **仍过 ≥90% 门**；此差是形态差非新噪声。
- 对已判 BTEST 档位影响：**零**（主判读 run1 C4 R2 仍破 2——伤害簇 Q7::52/58 属证据面伪影，grade 锚不可达；
  R1 17→18 仍<19）。反事实只说明"未来轮次同型案可被救"，不构成任何历史裁决回改。
- C2b 吸收性：C2b 本就计任意 grade 具名票（结构验证 delta=0）——**H1 的增量恰在现行主读 C4**；
  若 PI 日后切 v2=C2b 主档，H1 与 C2b 互补不冲突（H1 治 grade 语义漂移，C2b 治粗票入数）。

## §5 实装路径（草案，全部待 PI，本卡未动协议/生产）

1. **协议件修订草案**（拟新增条款，交 PI 审后按 vN 增量入 ANNOTATION_PROTOCOL v1.3 草案，本卡未写入）：
   - §判序锚："具名票 grade≥B 为协议下限（判序锚 H1，档位=ie∨res 至少一门 pass）；具名∧C 为非法票形。
     runner 收到即拒收回炉（模式 A，强）或按锚自动下限 B 并记 `anchor_applied` 旗（模式 B，弱）；
     每 run 预注册必须声明 H1 档位（none/S/M3/X）与拒收/下限模式。"
   - 生效边界：条款落款后新预注册 run 生效；历史裁决不回改（与 PROTOCOL_VOTING v2 生效条款同构）。
   - 配套：ANNOT_INSTRUCTIONS.md §等级 增一行反例（Q5b::35 run1 席A票面为教学例："仅GRM8弱命中AC…证据不足"
     却具名 AC=非法票形）。
2. **runner 侧**：票面机械校验函数（3 行：kind==NAMED ∧ grade==C ∧ 锚档判据 → 拒收/下限）；
   分叉盘点沿用 proto_v2_20260927/RUNNER_WATCHLIST.md，实装前先对齐 kb/mcp 两处实现（REPOSYNC 后同源）。
3. **H2 软提示**：判读卡尾句入冻结件；H3 旗：A4 复盘口径两行（阈值见 §3-H3），先跑 shadow（只记旗不接线）。
4. **验证轮**：下一个 45 簇视网膜 run 预注册 = C4 + H1-M3（模式 A 或 B 由 PI 定）+ H2 尾句 + H3 shadow，
   预注册门指标建议钉死：具名∧C 票数=0（模式 A）或 anchor_applied 数与翻正/新错逐案账；
   R1/R2/稳定性球门不动（防"换了规则又赢了"的归因混淆——grade 锚的净效应以"翻正案账"单独列报）。
5. **与 KB1 激活线关系**：注册包 v2（D10）各接受项不含判序锚——H1 若实装属协议层变更，走独立预注册，
   不与激活卡混跑。

## §6 诚实边界

- 反事实是**同一批冻结票的重放**，非新读票——H1 生效会改变席位的当场行为（自纠率、票形分布），
  实装轮的真实翻正率只能实测，本档给的是"票形非法存量"上界（9 档期 28 票 / 1817 票 = 1.5%）。
- 新错 0/1 案基于单案证据，统计功效弱；通胀机制（双错名坐实）已被构造出来，故 M3 的门条件与 H3 监控
  是配套必要项而非装饰。
- gates 为席位自评字段，H1-M3 以它为判据=信任门申报——与 C2b 用 grade 申报同级别假设，未引入新信任面。
- KB9 为 25 簇 changed-face 小集，4 案翻正权重从简；主证据为 BTEST/RUN7RG/RUN5 视网膜+眼表九档。
- 早期 pilot（RUN2/3）具名∧C 形态与九档期不同（证据面前 v1 世代），已单列不混入主判据。

## 附录（本目录，产物清单）

- data/SHA_LEDGER_INPUTS.txt（52 件输入 sha 台账）
- data/ballot_matrix.tsv（席×簇×grade 矩阵 1,817 行）
- data/consensus_recomputed.json / data/verification_gates.json（7 闸门）
- data/seat_grade_dist.tsv / gradeC_rate_timeseries.tsv / btest_run_pair_drift.tsv
- data/correct_name_demoted_C.tsv（27 案全列）/ named_gradeC_all.tsv（38 票全列）
- data/seat_corr.json / variant_totals.json / counterfactual_summary.json / counterfactual_promoted.tsv
- scripts/grade_build.py / grade_drift.py / grade_h1_counterfactual.py（重放入口，确定性零 LLM）

*GRADE_ANCHOR v1.0（2026-09-28）；卡 t_5522de51；下一步=§5 草案交 PI 拍板，本卡不动协议不进生产。*
