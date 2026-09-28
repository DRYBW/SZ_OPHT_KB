# PREREG_OBLIGRUN — KB9 k9_ocs §10-6 义务 run + 正式三席票 run 预注册（先 sha 落纸，后执行）

- 卡：t_c145db7c（assignee AGENT_ROLE）｜ 任务书：BRIEF_OBLIGRUN.md（sha 见 ledgers/SHA_PRE_OBLIGRUN.txt）
- 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加四（PI 原话"批准"= §10-6 义务 run 启动放行；**本批准不含激活**，OB-5 永久门维持）
- 义务原文：/mnt/D/EyeKB/kb/markers/_k9_ocs_rules_overlay_v1.json → obligations_before_activation（OB-1..OB-5）
- 登记件（只读）：REGISTER_PACKAGE_v2.md（sha 4810bbe47a7a1fae…，球门 P1≥24/33、P2 strict≤1/33（any 并报）与诊断表列规格以本件为准）
- 本件 sha 入账 ledgers/PREREG_OBLIGRUN_SHA.txt；先落纸再执行；判据不回改。

## 1. 票规版本声明（D11 硬条款，二选一显式声明）

**本 run 适用票规 = v2 C2b**（主档 PROTOCOL_VOTING_v2_C2b.md，sha 06a00ea99c56036d…；向前生效——本预注册晚于落款 2026-09-27，受 v2 约束）。

操作定义（逐字 PROTOCOL_VOTING_v2_C2b §1，参考实现 t1_revote.py sha d321e793144e2795… 之 `rule_c2(bs, count_coarse=True)` + `parse_ballot`）：
1. 定名票（identity 非 undetermined*、非 coarse: 前缀、非缺票）**任意 grade（A/B/C）计入**该标签法定人数；
2. coarse:X 按冒号后标签 X **计入 X 的法定人数**；
3. 定名门：**≥2 席同名即定名**；tie@1 不定名；
4. 平票残余 **S1 破平禁用**，维持无名（tie/split3/abstain3 照旧记录）；
5. undetermined*/缺票不入数。

**票面名过冻结 crosswalk 归一**（协议 §4.3 强制条款）：kb 候选名折叠一律过冻结件 KB_Q6_crosswalk.tsv（sha 274042aa93e9d014…）+ 追加件 KB9_CROSSWALK_ext.tsv（sha 8d82b6191067e983…，6 行 provenance 逐行）；本 run 不改任何旧名映射。ambiguous 照原链双折叠不猜，no_counterpart/UNMAPPED 不参与 R3/P2 折叠判定（判空=不参与）。

## 2. 票面（冻结件，本 run 唯一投票输入）

- 票面定义件：/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_face_arms.json（sha 4b0e11baed0c0820…，33 簇，含 armC_kb9 提案臂 ranking 与 G0/G1 保真记录）。
- 投票执行面：build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl（sha ba76b6ce1af1654e…，33 行，= 变化 25 簇替换 ranking+lit、不变 8 簇整行 RUN5 冻结）→ **copy 不 move** 为 face/EV_DIGEST_SLIM_q6_oblig.jsonl，逐字节校验后 sha 入账。
- 预断言（执行前机械校验，任一失败=不开跑并 block）：
  (a) 33 行 kb_marker_ranking（[{cell_type,n_shared}] 逐项）== kb9_face_arms.json armC_kb9 对应簇 —— 已实证 0 错位（本预注册前只读探针）；
  (b) 每行除 kb_marker_ranking 与 lit 外所有字段与 RUN5 面件 EV_DIGEST_SLIM_q6.jsonl（sha f083dd60ee4e4eb9…）逐字段相等（"仅重算 ranking+变化簇 lit 重建"声明核验，属 OB-1 对账一部分）；
  (c) 行序=RUN5 面件行序（批组成与 RUN5 一致，见 §5）。

## 3. 球门（不降，P2 口径回归注册包）

- **P1：C2b 定名且 consensus==truth（Q6 九类折叠，truth 对账断言=k8 逐字复刻：Q6_clusters.tsv 现算 vs Q6_truth_map.tsv 不符即中止）≥ 24/33**。禁调阈值凑命中。
- **P2 strict：违规 ≤1/33；any 口径并报**。违规判据逐字=k8_verdict.py `p2[...]['violation']`（consensus 存在且 ≠truth 且 consensus ∈ kb ranking 折叠类 且 truth-marker top10 重叠 ≥3）。C2b 新增定名簇自动进 P2 污染检查（协议 §4.2，撞 kb 名单即计）。
- P3（kb 空率）照旧记录不入门。
- 历史 C4 P1=22/33 FAIL 记录不回改（out/kb9_verdict.json 为冻结历史值；本 run 单独成节互引）。

## 4. 判读三席与通道

- 席次=RUN5/KB9 同三席同参：A=qwen3.8-max、B=glm-5.1、C=deepseek-v3.2；通道=LLM_CHANNEL（base_url/key 扫 ~/.hermes/profiles/AGENT_ROLE/config.yaml，与冻结 runner 同取法）。
- 参数逐字继承 run_annotator_run5.py/k6_annotator.py：temperature 0.2、max_tokens 3500、CHUNK=5、prompt=冻结 ANNOT_INSTRUCTIONS.md（sha 3318177471f254ef…）原文 + RUN5 卡片渲染（top_genes20 symbol(ENSG)/gene_hits/kb_celltype_ranking/lit；tissue_composition_ref 不入判读输入，注册包 §9 纪律沿用）。
- **enable_thinking:false**：PI 原话"三席同参必带"。执行序：投票前对三模型各做一次**非票面 ping 探针**（零票面内容，不产票、不计入票预算但登记日志）验证该参数逐模型可接受；探针结果逐模型登记 logs/seat_probe_*.json。若某席 API 拒收该参数：该席如实登记为通道约束（qwen 席必带；其余席带参=报错则降为不带并登记偏差），不视为球门失败。
- 通道 429/配额失败=block 上报，禁自行加钱换通道（KB9_PREREG §3 沿用）。

## 5. 票预算

- 名义票=33 簇 × 3 席 = **99 票**；**上限 150 票**（每收到一张计入面档的票=1 票，重试批次中模型返回的票同样计数）。
- 脚本硬计数器：累计计数将超 150 时**立即停止一切后续请求并 block 上报**（禁"再试一批"）。
- 批组成快照：CHUNK=5 按面件行序 → 7 批（5,5,5,5,5,5,3），与 RUN5 原批完全一致（逐批 cluster_id 清单落 logs/batch_composition.json，OB-1 消费）。

## 6. 四义务定义与验收线（OB-1..OB-4，逐项产表）

- **OB-1（AV2-5(c) 历史 ON 态门）**：产 out/OB1_ledger.tsv。逐簇×逐字段对账 RUN5 面件 vs 本 run 票面（11 字段：cluster_id/member/material/n_cells/qc/top_genes/top_genes_sym/gene_hits/kb_marker_ranking/lit/tissue_composition_ref），+ 批组成快照、指令 sha、runner 参数、库版本注记五类全局字段。漂移逐条登记并判"清/不清"。
  判读口径（先于执行写死）：本 run **零复用存档票**（33 簇全量新票），AV2-5(c)"复用存档票的后续 run 须先建此门"之触发条件不成立，但其对账义务照做：
  (a) 8 不变簇输入面=RUN5 冻结面逐字节可对账 → 该部分"清"；
  (b) 25 变化簇字段漂移限于 kb_marker_ranking+lit（提案内容本身，非失真）→ 登记后"清"；若漂移越出该两字段=不清（上报）；
  (c) RUN5 时刻完整请求原文未逐字节留档（可核验事实）——以"runner sha + 面件 sha + 指令 sha 三件钉定的确定性重渲染"为替代取证形态，如实登记为保真等级注记（G1≠历史 ON 保真，注册包 §4(c) 原文随件携带）；
  (d) 库态 RUN5→今之变化（KB7/face_v6 激活致 Q6::21/4/5/28/29 ranking 位移，kb9_attribution.json 对照臂）登记为历史事实项，本 run 不据旧票声称当期复测。
  OB-1 判"清"=（a）（b）（c）（d）全部如实落表且（b）无越界漂移。
- **OB-2（A07 投票前诊断表首跑）**：产 out/pre_vote_diagnostics.tsv，列规格逐字注册包 §6：
  `cluster_id | entry_id | raw_hit_genes(分号列) | n_raw | shielded_hit_genes | n_shielded | n_remaining(=n_raw−n_shielded) | rank_pre_shield | rank_post_shield | top3_flag_post | immune_support_flag`
  行=每簇 × 每候选 entry（pre/post 任一排名出现的并集）。pre_shield 臂=ON+k9+R1（无 R2/R3 屏蔽）全 ranking；post_shield 臂=C 臂（ON+k9+R1+屏蔽，face_effective_genes 口径，sha 锚 kb9_face_effective_genesets.json）全 ranking；raw=entry 库原基因集，shielded_hit_genes=命中 cluster top10 且被 blocked 的基因。immune_support_flag：折叠入 Immune Cells 的候选，屏蔽后 n_remaining>0 且是否进 top3；Q6::8/Q6::26 逐簇单列（指定对照簇）。
  **硬断言（先于投票）：post_shield top3 与票面 kb_marker_ranking 逐簇全等；不一致=run 作废（block 留痕不重跑粉饰）。**
  Q6::26 型掏空回退在表内可指认（n_shielded>0 且 rank 位移/跌出 top3），逐条登记。
  诊断表只呈现实证面，不参与计分（注册包 §6 原文）。
- **OB-3（22 视网膜簇 Arm1/Arm2 完整 ranking 一致性补查）**：产 out/OB3_consistency.tsv。
  样本=KB9_PREREG §4 冻结抽样规则逐字重导（EV_DIGEST_SLIM_v3full.jsonl sha 8df1e5f6a887bada…；Q1/Q2/Q3/Q4/Q5b/Q7/Q8 各按 n_cells 降序 top3 + Q9 top1 = 22，断言簇清单与 k7 产物行集一致）。
  完整 ranking（截断前全列表，非 top3）三臂：Arm1=ON 五库+k9 合并注入；Arm2=Arm1 按 R1 镜像剔除 k9 face-only 条（K9_NAMES 精确名 + 消歧前缀键 `k9_build::*` 双查——**dedup 碰撞即漏网**，逐项核）；native=query_marker ON 原生（对照 G1 语义）。
  逐项检查：①非 k9 条目在两臂间相对次序与 n_shared 全等（排序稳定性/AV2-4 平票插入序副作用）；②top3 与 k7 存档 ranking_no_rules / ranking_with_rules 可重放对账；③k9 名与既有库类名碰撞致消歧键泄漏（去重副作用）；④同分组（n_shared tie）成员在两臂次序一致（加载序副作用）；⑤Arm2 中 k9 零进入（泄漏断言）。
  每簇一行判定"清/不清"；22/22 清=OB-3 清，任一不清=如实登记并计入 NOT_READY。
- **OB-4（lit 逐条同源排除筛查留档）**：产 out/OB4_lit_screening.md（+ out/OB4_lit_hits.tsv 机读面）。
  筛查对象=本 run 票面全部 lit 命中条目（探针实测 64 条/12 唯一 PMID，含 8 不变簇的 RUN5 代整行冻结 lit——同受注册包 §9 排除规则约束）。
  排除对象定义（注册包 §9 逐字）：直接陈述本评价 33 簇（D002 author 标注）类属归属的文献及其片段（含 Q6 truth 来源标注论文及其补充表）。
  两级筛查：①标题级初筛=12 PMID × 观看列表（D002 study 层标签全集：shi/chen/li/chakravarti/dickman(GSE186433)/BCM/Atlanta/LEI/数字码供体系；+ Q6 truth 来源论文）逐一判归属；②片段级复核=对命中 PMID 取本地语料（v2.0_2026-09 chunks，只读；papers.jsonl sha 入账）全文片段扫"簇/细胞群→作者标签"指派关系模式（含 D002 accession/供体名与标签指派同段共现）。
  逐条落盘：命中列表（簇|cell_type|PMID|判定依据）→ 判定（同源排除/保留）→ 剔除动作（若判排除：票面即须剔除该 lit=面污染事件，按判读矩阵走 block/作废留痕；若全保留：0 剔除登记）。
  **本 run 不重建 lit**（面已冻结，重建=改面，红线禁止）；筛查记录义务在"每次 lit 重建落盘"——本 run 消费的最后一次重建=KB9 build，故对重建产物执行补筛查并留档，即关闭 OB-4 于本 run 范围。
- OB-5=永久门归 PI 另批，本 run 不动。

## 7. 判读矩阵（if-then 写死）

- IF OB-1..OB-4 全"清" AND P1≥24/33 AND P2 strict≤1/33 → VERDICT=**READY**：产 out/ACTIVATION_READINESS.md（逐门数字+建议票"可送 PI 批激活"）；**不激活**（OB-5 归 PI 另批；本 run 零接线零激活零默认切换）。
- ELSE → VERDICT=**NOT_READY**：逐门如实报；禁改写历史 C4 记录；禁"将激活/接近激活"式措辞；泛化"提升 X%"禁。
- IF 诊断表与票面不一致 OR 票面作废条件命中 OR 票预算超限 OR 通道配额失败 → **block 上报**，作废留痕不重跑粉饰。

## 8. 红线（随执行强制）

零接线零激活零默认切换；kb/、mcp_server/、evalset/、注册包、_k9_ocs_rules_overlay_v1.json、lit 语料只读；PRE sha 台账（ledgers/SHA_PRE_OBLIGRUN.txt，60 件）执行完毕后 POST 复验零写入；历史冻结件不回改，新结果单独成节互引文件名；产物全落本卡 plans/obligrun_20260928/（copy 不 move）；中间产物（脚本/日志/票面原始 jsonl）全保留；脚本命名 *_t_c145db7c 另立不复用。

## 9. 执行序（sha 落纸后）

1. 票面 copy+逐字节校验（face/EV_DIGEST_SLIM_q6_oblig.jsonl）
2. OB-1 → OB-2（含硬断言）→ OB-3 → OB-4（投票前完成，全"清"或不清均先落表——不清仍继续投票取球门数字，判读矩阵如实合成；但 OB-2 面不一致=作废停卡）
3. 三席 enable_thinking:false 参数探针（非票面，零票）
4. 正式三席票 run（99 票名义，硬计数器 ≤150）
5. C2b 裁决（fork t1_revote rule_c2 + k8 truth 对账/P2 判据逐字）
6. VERDICT_OBLIGRUN.md + ACTIVATION_READINESS.md（若 READY）+ POST sha 台账
7. kanban_complete（或按矩阵 block）
