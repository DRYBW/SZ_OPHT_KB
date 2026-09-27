# E3_PREREG_v1.0 — 弃权带回捞工具正式化预注册（辅助定位验收，2026-09-27）

- 卡：t_7b5a5fb3｜任务书：BRIEF_E3.md｜放行依据：/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md（D2 卡）
- 本件 + 机读件 e3_rules.json 的 sha256 于 ledgers/prereg_sha.txt 落纸，**先于本卡一切跑数**（红线④时序可审计）。
- 判据落纸后不得回调（禁移动球门）。全阴性是合法结论（PI 铁律：证据不足/弃权合法）。

## 0. 对象与定位
把 E2_VERDICT §3 观察性附加数字（AB 弃权 85 行，去同源证据具名 48/对 41=85.4%）正式化为预注册检验。
工具定位=**辅助/仅离线审计**（PI 原话"不是代替，是辅助"）；本卡禁接线、禁生产写、产物仅落本目录。

## 1. 工具规格冻结
- **触发面**：有真值行中，基线共识未定义的行（=判读弃权带）。F-RET 用 AB 两席共识（c2 未定义）；F-3SEAT 用存档三席共识。
- **共识未定义判定**（逐字复刻 E2 口径，e2_metrics.copy.py）：
  - F-RET：`ann_A==ann_B 且均非 undetermined*/coarse:* 前缀` 之外 = 未定义（run3_object_B_table_v1.1.tsv）。
  - F-3SEAT：FACEV21 45 行用 `v21_mode=='majority' 且 v21_consensus 非空非 nan`（per_cluster_flip_table_facev21.tsv）；RUN5 Q6 33 行用 `consensus 非空非 nan`（run5_truth_table.tsv）。
- **输出**：证据分（decon S1 主规则，e2_decon_rules.json sha 34928582 原样只读复用）①top1 具名标签 + 基因依据（n_shared 明细 + shared_genes）。
- **具名/弃权判定**：top1 候选经 e1_class_map.json 冻结映射（面板按簇归属 retina/ocular）得到字符串标签=具名；映射为 AMBIG[...]、无映射条目、或无任何候选=**无具名 top1=弃权**。
- **命中**：具名标签==truth 字符串全等。弃权/AMBIG=miss（沿用 E1/E2 冻结口径，c1 保守分母）。
- 打分实现=实验侧复刻（本卡 scripts/ 内自含，**不 import 生产码 eyekb_core**）；席位票全部读存档，禁重跑 LLM。

## 2. 面一（主门 R1）
- 面=F-RET：run3 表 truth 非空且 member∈{Q1,Q2,Q3,Q4,Q5b,Q7}=196 行；弃权带=E2 口径约 85 行（复现闸钉死，见 §5）。
- **判据（两条都过才 R1 PASS）**：带内具名精确率 ≥80%（具名对/具名数）；带内具名量 ≥40 行（下限防缩到无关痛痒的量）。

## 3. 面二（泛化门 R2）
- 面=F-3SEAT 78 行（FACEV21 retina 45 ∪ RUN5 Q6 33）弃权带复算（E2 观察值：带 14 行/具名 7/对 5）。
- **判据（两条都过才 R2 PASS）**：带内具名 n≥15；具名精确率 ≥70%。
- 如实声明：构造面小分母，R1/R2 球门不平等沿用 E1 声明；本门专测泛化，不过不拖累 R1 记账（判读矩阵 §6）。

## 4. 改良臂（R3）= FACEV21 三拆弹的规则叠加层
规则来源=FACE_PROTOCOL_V2_1_PREREG.md §4(a)(b)(c) 冻结文本。FACEV21 拆弹是**判读卡面规则**；本臂把三条逐一映射为打分侧确定性叠加操作（不 import 生产码，不碰任何席位票），映射设计仅凭规则文本推导，未查询带内结果分布择优（防事后选尺）。

- **3A'（旗禁降级→打分侧透传）**：打分器无 grade/identity 通道，(a) 在打分侧无任何可施加的降级通路——登记为**空操作**（不虚构叠加动作）。
- **Q7'（跨物种撤词条 ranking）**：(b) 撤下 Q7 簇全部 kb_gene_hits/kb_celltype_ranking 行；打分侧具名输出即面板 ranking 的唯一通道 → **成员==Q7 的行改良臂一律不具名**（=弃权）。影响行：F-RET 的 Q7 行 + F-3SEAT 中 flip 表 Q7::簇（8 个）。
- **C'（判序细化→弱命中不配定名，强冲突弃权）**：(c) 原文="两谱系核心共存仅当两谱系同时 n_shared≥2；n_shared≤1 的谱系不构成谱系冲突"。打分侧直译：
  1. 候选按 (n_shared desc, canon asc) 排名取最大 n 层；
  2. 若最大 n≤1（含 lit-only n=0）→ **弱命中行：不具名**（弱命中既不构成冲突也不单独定名——打分器无直证/文献外的定名通道，1:1 破并列=掷硬币，本臂移除之）；
  3. 若最大 n≥2 且最大层唯一 → 具名该候选（映射同 §1）；
  4. 若最大 n≥2 且最大层 ≥2 个候选（真正的"核心共存"冲突）→ **冲突未决：不具名**（判读侧对应 resolution:fail 语义）。
- 改良臂在两个面各复跑一遍（同一 S1 分数表上的后处理层，不重打分、不 import 生产码）。
- **判据**：每面改良臂具名精确率 ≥ 现役臂精确率（具名=0 时该面记 FAIL，未定义不作达标）；且 E1 §5 分歧案例表（out/e1_divergence_cases.tsv，5 例：Q2::22/Q6::11/Q6::3/Q2::14/Q6::20）中 Q2::22 型同坑案例在改良臂下**修复（top1==truth）或如实记录未修复**。
- 改良臂不达标→**现役臂按原样入 SOP**（R3 判词记录之；改良臂数据如实附表，不进任何门）。

## 5. 复现闸（先于判读，不过闸禁出结论，exit 2 中止）
- G0：本卡管线复刻的 S1 逐簇候选分数表与 E2 冻结 data/e2_scores_S1.tsv 全量逐 (cluster_id, cand_canon) 等值（n、lit_n、shared_genes 按集合比；行序差异登记）。
- G1：现役臂带内计数逐值==E2 observation_addendum：F-RET 带 85/具名 48/对 41；F-3SEAT 带 14/具名 7/对 5。
- G2：PRE sha 台账（ledgers/sha_ledger_PRE_inputs.txt，21 件）输入件 POST 复核零触碰。

## 6. 判读矩阵（先冻结后看数）
| R1 | R2 | 记账 |
|---|---|---|
| PASS | PASS | 辅助工具双面成立，SOP 草案交 PI 阅（仍不接线） |
| PASS | FAIL | 限视网膜面成立，SOP 标注泛化边界 |
| FAIL | 任意 | 如实记"观测数字未过正式化检验"，SOP 不产出，E2 观察性附加勘正注记（本卡目录侧登记，不回写 E2 件） |

R3 独立判词（达标/不达标+逐案例状态表），不并入上矩阵；R1 FAIL 时无 SOP，改良臂结果仍如实落表。

## 7. 红线
- 全部产物只落 /mnt/D/EyeKB/plans/e3_rescue_20260927/；kb/、mcp_server/、生产评分链、E1/E2/evalset/face_v21/run7rg 全程只读 + PRE/POST sha 台账。
- 零 LLM 调用、零网络、零生产写；禁重跑席位票；禁移动球门（本件 sha 后判据冻结）。
- E2R 卡并行在跑：勿写 e2r_s5audit_20260927/。
- 完成或遇阻必须落卡（kanban_complete/kanban_block）；中间产物全保留。
