# E2_PREREG_v1.0 — 面板去同源重测 预注册件（跑数前落纸）

- 卡片：t_35d45b74｜任务书：BRIEF_E2.md（sha 见 ledgers/sha_ledger_PRE_inputs.txt）
- 批准链：USER_DIRECTIVE_20260926_redline_rewrite.md 追加二第 2 项（E2 GO，PI 2026-09-26 回 ok）
- 机读规则件：**e2_decon_rules.json**（gene×panel×PMID 矩阵判据，本件组成部分，一并落账）
- 复用冻结件（只读、不改一字）：e1_class_map.json（并类/映射/破并列/AMBIG 口径）、e1_leak_lineage.json（成员→源 PMID）
- 本件与其 sha 入账之后才允许执行任何 decon 命中率/F1/ROC 计算（红线④；只读结构探针 probe1-6 不产判读数字，先于本件登记于此）。

## 0. 输入（全部只读；PRE/POST sha 台账 = ledgers/sha_ledger_{PRE,POST}_inputs.txt，25 件）

E1 全套产物作对照基线；kb/markers 6 库文件派生证据；evalset 冻结卷 run3 v1.1 + FACEV21 翻转表 + RUN5 表（三席票全部读存档，禁重跑 LLM）；papers.jsonl 仅成员判定。**生产代码禁调用声明**：本卡全程不 import、不 exec eyekb_core / mcp_server 任何模块；面板装载与 n_shared 打分逻辑按 eyekb_core.py 现行文本（sha 入账件）**在实验侧复刻**，复刻正确性由 §1 验收闸门用 E1 ON 全表逐行证明。

## 1. 复刻验收闸门（先于一切 decon 数字）

1. 实验侧重建 ON 态 60 类行结构（载入序、face_v6 派生、消歧别名行、基因表大小写归一），逐簇用 digest 冻结 top10 规则重算 raw 排名。
2. 与 data/e1_scores_ON.tsv 逐 (cluster_id, canonical) 对齐：n_shared 与 lit_n 全等才过闸；shared_genes/alias 列允许且仅允许 max-n 平票行序差异（逐处登记，不修数）。
3. 主表关键格复现：F-RET 全部 ① 72.45 / 无泄漏 ① 67.74 / ③ 68.39；矩阵 +16.77 / +3.23 / −23.40；S3 点名单列复现 58.04 / 55.36 / 71.43。任一不过 → 停线排查，禁出 decon 结论。

## 2. E2-1 去同源矩阵（判据 = e2_decon_rules.json，此处为人读版）

- 对每簇判面板污染源：基因级派生旗 hrca_tag（轴={Q3,Q4,Q5b}，HRCA D001 门数据驱动/KB5v2/KB6/REVCAND stats_frozen；v4.1 P0.4 数据驱动 Micro/RPE 集保守并入）与 face_tag（轴={Q6}，kb6b/kb7_w2 D002 门）；mem_tag（GSE165784=Q9 演示集，非真值）撤销 hrca_tag。
- keep 规则（可复算，禁点名单）：S=该 (库,类,基因) 文件内显式基因级 PMID 集（membrane pmid_context 类级语境按其 semantics 原文排除）。簇成员 m：m∈轴 → 需 S∖(B_src(m)∪B_axis(视网膜系)) ≠ ∅；S≠∅ → 需 S∖B_src(m) ≠ ∅（源论文独证基因任何成员处不认外部链）；S=∅ 且 m∉轴 → 保留（无记录文献先验不罚，v4.1 八类/v5v6 继承行；其边界=已知残余，登记 §6-4）。
- B_src = lineage 源 PMID 逐字；B_axis 视网膜系 = {41578023}（HRCA 本体论文）。
- lit 通道：逐簇候选 PMID − B_src(m)；B_src 不可解析成员（Q4/Q6/Q8）登记"lit 不可去污"。
- 产物 data/e2_gene_panel_pmid.tsv = 全矩阵逐行可复算（规则脚本重跑 bit 级一致）。

## 3. E2-2 干净效果量（同分母逐行对照；两口径并列）

- 面：F-RET 196（主）、F-3SEAT 78（副）、F-OCS 33（sanity，循环注记）。
- 重算 ①_decon、③_decon（并类/映射/破并列/AMBIG=miss/弃权=miss 全部沿用 e1_class_map 冻结口径）vs 基线三列（AB 两席共识=主替换基线、最强单席 B、三席多数@F-3SEAT）。
- 口径 c1 保守全分母（共识未定义=miss，E1 延续）与 c2 共识已定义子集（证据与基线同子集）并列全报；out/e2_row_compare.tsv 逐行 raw/decon/基线三态对照。
- **不对称声明（跑前落纸）**：席位票为冻结存档，Q5b/有泄漏行的基线票自身仍含同源/背答案注水（E1 F-A），本卡只清洁证据侧 → 全 196 面 Δ 系统性偏保守（对证据不利方向），如实登记不改设计。
- 头条 Δ 固定：①_decon vs AB共识 @F-RET 全 196 @c1；③ 与其余列全并报；①③ 分档不同 = 跨档边界案交 PI（E1 先例，禁择档）。

## 4. E2-3 预筛/旗标工作点（仅当干净 Δ(①)>0 出 ROC；Δ≤0 走 W3 量化结案）

- 旗标 = ①_decon top1(映射) 与共识(映射) 分歧，扫 θ∈{0..4}（θ=分歧两候选去同源 n 差≥θ），行集=共识已定义（c2 子集），未定义行数单列。
- 结局 = 共识≠truth（真错）。报 sens/spec/prec/flag_rate 全表（F-RET 与 F-3SEAT 同构）。
- "可用工作点" = 特异度≥80% 且灵敏度≥30%（30% 防真空守卫为本卡预注册数字，BRIEF 未定，先落纸后跑数，禁事后调）。
- 预筛第二读法：top3 覆盖率(decon) 报"真值在缩圈 3 候选内"比例（候选宇宙=有分候选数另报，防宇宙塌缩假覆盖）。

## 5. E2-4 判读矩阵绑定（BRIEF 表原样，Δ 定义如上）

| 观测（干净列 = 头条 Δ 定义） | 裁决 |
|---|---|
| Δ>+5pp 且存在可用工作点(§4) | W1：出生产化最小接入提案书（等 PI 批，不实装）；**否决条款**：若 Δ(vs 最强单席 B)<+5pp，W1 封顶降 W2（替代对象是最强基线——E1 F-A 教训预注册化） |
| Δ 0~+5pp 或无可用工作点 | W2：维持 V2+ 定性，提案降级"仅离线审计用" |
| Δ≤0 | W3：结案撤定位，证据面只留引用职能 |

边界含入：+5pp 整归 W1、0 与 −5pp 线不含糊（Δ 恰=0 → W3 行"Δ≤0"）；c1/c2 两口径落不同档 → 边界案交 PI。F-3SEAT 为一致性副证：升档需两面上升（沿用 E1 稳档规则），F-3SEAT 构造面球门不平等声明沿用。

## 6. E2-5 同源水分账（只出表，不改历史冻结件）

- A 簇侧表：成员 {Q3,Q4,Q5b,Q6} + lit 有泄漏 13 行的 raw/decon top1% 与水分 pp + 各成员面板行被剔基因数。
- B 面板侧表：每 (库,类) 行基因的外部链/仅内部派生/无记录三分层占比。
- C 历史登记：E1 已报受垫高数字清单（67.74/68.39、Q5b 43 行 93.0%、F-3SEAT 列、F-OCS 列）+ 本卡修正值 + "供 RUN 系列口径修订输入"声明。
- 已知局限登记：①Q4/Q6/Q8 源论文不可解析→lit 不可去污、Q6 轴仅覆盖 face_v6 面板；②membrane 免疫/血管行派生自 GSE165784（Q9 非真值）判无轴，若该演示集将来进真值需重审；③席位票不可清洁（§3 不对称声明）；④"无记录文献先验"基因（v4.1 八类等）不在文件内建立可核查证据链，S2 严格列给其影响上界；⑤鼠簇人源 symbol 大写碰撞（E1 局限 2 原样）。

## 7. 红线执行

kb/、mcp_server/、evalset、E1 产物零写入（PRE/POST sha 全等自证）；不 import 生产模块、不触网、不新下载、不跑 LLM；全部产物落 /mnt/D/EyeKB/plans/e2_decontam_20260926/（scripts/data/out/ledgers/logs）；中间产物全保留；完成或遇阻必落卡。

## 8. 产物清单（卡面承诺）

- scripts/e2_build_matrix.py（面板复刻+证据矩阵）/ e2_score.py（raw 复刻验收 + decon 打分）/ e2_metrics.py（表/矩阵/ROC/水分账）/ e2_shaledger.py
- data/e2_gene_panel_pmid.tsv / e2_scores_decon_{Q-axis on}.tsv（逐簇×候选全表，含 keep 明细列）/ e2_scores_raw_replica.tsv
- out/e2_verify_replica.tsv / e2_row_compare.tsv / e2_truth_region_table_decon.tsv / e2_metrics.json / e2_flag_operating_points.tsv / e2_homology_water.tsv（A）/ e2_panel_water.tsv（B）/ e2_history_register.tsv（C）/ e2_sensitivity_grid.tsv（S1-S6）
- E2_VERDICT.md（W 档机械执行 + 边界案声明与否 + 水分账摘要）
