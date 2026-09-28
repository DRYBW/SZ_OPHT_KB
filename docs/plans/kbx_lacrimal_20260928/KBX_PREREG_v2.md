# KBX_PREREG v2 — 泪腺词条疗效首考判据件（票规声明=v2/C2b；判据先于执行冻结，2026-09-28）

- 卡：t_0fb07fd6（D13）｜ 任务书：BRIEF_KBX.md（sha af6a93b0…）｜ 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md D13
- 裁定继承：**KBX_RULING_1.md（sha c159f5fe…）**——O2 外部文献参考系为主档、合格锚定簇<8 自动降 O3；
  判分三门+120 票上限+C2b 票规不动。
- **外部预审（冻结前设计裁决，非看结果调门）**：REVIEWER_LLM（LLM_CHANNEL REVIEWER_LLM，reasoning=xhigh）对 v2 草案回函
  `REVISE_FIRST`（REVIEWER_LLM/A_KBX_PREREG2_REPLY.cycle1_preserved.md），本定稿逐条吸收其 Q1-Q8/S1-S4 裁定与
  可粘贴 §1.2 文本；三门阈值、票规、<8 降档结构未动。
- **票规版本声明（D11 硬条款）：本 run 适用 v2=C2b**（PROTOCOL_VOTING_v2_C2b.md sha 06a00ea9…；本卡=该票规首个正式适用 run）。
- 红线继承：泪腺 A3 维持**不注册不接线**；本卡=纯离线考试；产出=注册申请资格判定**建议**；
  kb/、mcp_server/、evalset 只读+sha 台账；零数据下载（EuropePMC REST=文献元数据检索，逐请求留原始返回）。

## §1 参考系 = 外部文献 marker 面板（禁 KB 派生；语境门=REVIEWER_LLM 可粘贴文本逐字采纳）

§1.2 外部文献面板语境门（冻结文本）：
> 每个候选基因仅可依据独立于 KB、KB8 面板和本 run 聚类结果的外部文献建立参考证据。Europe PMC 查询、返回内容、
> 命中位置和筛选理由逐基因原样保存；同一 PMID 仅计一次。主证据必须同时满足：物种为人；组织语境明确指向
> lacrimal gland 或同义泪腺语境；基因 token 位于题名或摘要；文献语义指向细胞类型、marker、单细胞/转录组定位
> 或组织细胞表达，而非仅疾病关联、体液蛋白存在性或一般组织检测。
> lacrimal sac、dacryocyst、canalicul、meibom、nasolacrimal、泪囊、泪道及其同义语境不视为泪腺语境；仅涉及泪液、
> 唾液、Sjogren 或其他疾病蛋白组而未提供泪腺细胞类型定位的记录，不得作为主 marker 证据。gland 单独出现不足以
> 证明泪腺，必须由题名/摘要中的泪腺语境确认。
> Tier1（主证据）：至少一条记录同时满足：基因精确 token 出现在题名或摘要；泪腺语境出现在题名或摘要；且题名/摘要
> 具有细胞类型/marker/单细胞/转录组定位/免疫组化/原位杂交或等价细胞表达语义。Tier1 基因进入该群主面板。
> Tier2（降级证据）：仅在无 Tier1 时考虑：>=2 个不同 PMID、每 PMID 题名含泪腺语境（同上排除）、基因 token 题名/摘要
> 可见、>=1 条含 marker 语义、无泪囊/泪道/纯疾病体液的排他语境。Tier2 只进预登记**敏感性面板**，不参与主面板
> 分数、0.7 门、首二次比值与主锚定；附录单独报告，禁用于替换主分析。
> 每参考群主面板 Tier1 有效基因数 >= MIN_T1=3，否则该群标记 panel_unavailable（禁由 1-2 基因构成 0.7 锚定）。
> 所有群使用完全相同的检索、排除与证据分级规则；终面板在判据件冻结后不得增删；不足致合格锚定簇<8 时依 §8 降档。

操作化（确定性规则，实现 scripts/kbx_p1c_panel_build_v2.py，逐字冻结）：
- 分层检索：Q_A=`"<GENE>" AND "lacrimal gland" AND (marker OR "cell type" OR "single-cell" OR scRNA OR transcriptom OR immunohistochemistry OR "in situ")`；
  Q_B=`"<GENE>" AND "lacrimal gland"`；resultType=core pageSize=8；原始返回 ledgers/eurpmc2/。
- token 判定：基因=定界大小写不敏感精确 token；语境=regex `lacrim|lacrimation|tear[- ]?duct`；
  排除=regex `lacrimal sac|dacryocyst|canalicul|meibom|lacrimal canals?|nasolacrimal|lacrimal drainage`；
  marker 语义=regex `marker|cell[- ]type|single[- ]cell|sc[- ]?rna|transcriptom|immunohistochem|in situ|expression profil`。
- 候选矩阵（领域知识列举，先于任何检索落纸）：ledgers/KBX_PANEL_CANDIDATES_V2.tsv 首列群名+基因列，
  七群=ACINAR/DUCT/MYOEPITH/IMMUNE/ENDO/NEUROGLIA/STROMA。
- **平台排除预登记规则（独立性披露，REVIEWER_LLM Q8#13）**：LYZ/LTF 依"泪液超富集蛋白×SORT-seq 板法 ambient 先验"
  在候选侧排除（登记于候选表 tier=EXCLUDED-PLATFORM）；该规则基于文库构建方法学公开事实（泪液蛋白洗脱污染），
  不引用 KB8 结论、不依赖本 run 任何计算结果。
- 可用性过滤：面板基因以 h5ad var symbol 空间（sha 5e6d753d…）为准；不在 var 的登记 unavailable 并从群分母剔除。
- 终表：ledgers/KBX_PANEL_FINAL.tsv + ledgers/KBX_PANEL_MAIN_groups.json（Tier1 主面板，群→基因）。

## §2 建卷

1. 输入：/mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad（sha 5e6d753d…，只读）；排除 author_empty_well==True。
2. **两池分别聚类，永不混池**。定量考试分母=组织池唯一（P1/P2/注册资格判定只读组织池）；
   类器官池=预注册独立拓扑附录（O3 性质观察档：面板分数表+锚定判定全列出，**不发席位票、不进任何疗效数字**）——
   REVIEWER_LLM Q1 裁定（体外导管样程序与体内词条装配能力不可共分母）。
3. 参数族（冻结）：normalize_total(1e4)+log1p → HVG seurat 2000 → PCA 50（random_state=20260928）→
   neighbors 15 → leiden flavor=igraph resolution=1.0 random_state=20260928；scanpy 1.12.2（版本入台账）。
4. **主档唯一性+敏感性网格（REVIEWER_LLM Q7）**：主结论只来自 res=1.0；预注册敏感性档 {0.8, 1.2}（同 seed、全管线独立重跑、
   仅报告锚定数/构成稳定性），**禁从网格挑档救主考试**；网格结果永不进 P1/P2。
5. 题面=组织池 n_cells>=30 簇；3×N<=120 断言；若 N>40 按 n_cells 降序截断 top40（BRIEF 冻结条款，预计不触发）。
6. 簇独立性披露（REVIEWER_LLM Q8#10）：逐锚定簇 donor/sort 构成列进逐簇表；某 donor 独占 >=2 分母簇时 VERDICT 加外推限制旗。

## §3 打分与检测一致性门（RULING"纯度"一词的操作化更名，REVIEWER_LLM Q3）

1. 每基因细胞检测率：d(c,gene) = 簇 c 内 CP10K>=5 的细胞占比（CP10K=counts normalize_total(1e4)，未取 log；
   DET_FLOOR=5 与 KB2 W2 CPM_FLOOR=5 同数值独立实现，属打分侧先验常数）。
2. 群分数 = 群内 Tier1 available 基因 d(c,gene) 的**等权截尾均值**（>=4 基因去最高最低各 1；==3 取中位；<3 群不可用）。
   该分数称**检测一致性分**——不得再称"纯度"；RULING 的"纯度>=0.7"在本卡即"最高群检测一致性分>=0.7"。
3. **锚定门（冻结）**：top=argmax；锚定 ⇔ 一致性分(top)>=0.7 ∧ (次高==0 ∨ top>=2×次高) ∧ 无并列最高 ∧ n_cells>=30。
   描述性列（不参与判定）：细胞级 top-group 一致率（每细胞 argmax 群投票众数占比）。
4. **ambient 机械过滤（先于群分数，冻结定义）**：对 Tier1 available 面板基因，用组织池 n>=30 各簇的
   池内伪 bulk CPM（簇 counts 求和÷池总计数×1e6），log2(CPM+1) 跨簇 CV<=0.3 且中位 CPM>=2000 → 该基因出打分
   （含全部簇值，零值保留；计算簇集=题面簇；>=4 簇才执行）。出局名单 out/kbx_ambient_excluded.json 先于锚定落盘。
5. 未锚簇=附列（组织池附列仍入题面投票、只进 P3；类器官全为附录）。逐簇表 out/kbx_cluster_table_raw.tsv
   （全分辨率档；主档列标注）。
6. **考试有效性前置条件（REVIEWER_LLM Q5 修正采纳，新增名目、不并入原降档条款）**：进入投票前断言
   ① 合格锚定簇（锚定∧无泄漏旗）>=8；② 最大参考群占分母 <=40%；③ 无任一群占分母 >50%（与②冗余留档）。
   任一不满足 → 不发席位票，按 O3/不可判处理（P1/P2 定量结论禁发）；前置条件数字先落 ledgers/KBX_ANCHOR_COUNT.txt。

## §4 防循环硬项（泄漏重叠表，RULING 逐群）

1. KB 泪腺 core 集（只读 markers_v6_lacrimal_increment.json sha 4e7e001a…）：
   {LACRT,SCGB1D1,SCGB2A1,CST4,CST1,MUC7}∪{PRR27}∪{}=7 基因。
2. 群重叠=|Tier1 available 面板 ∩ core7|/|Tier1 available 面板|；>0.5 → 泄漏旗：该群锚定簇不计入 P1/P2 分母
   （票仍投、只作参考与 P3）；out/kbx_leak_overlap.tsv 逐群落盘。
3. 泄漏旗致分母=0 → 无 P1 数字，走 §3.6/§8（fail-closed，禁除零假通过）。

## §5 词表与 crosswalk（先于投票冻结）

1. LG 词表（判读员可用原样词）：
   被测词条名 Lacrimal_secretory_tearcell｜Lacrimal_duct_epithelial｜Lacrimal_myoepithelial；
   参考通用名 Acinar_cell｜Ductal_cell｜Myoepithelial_cell｜Immune_cell｜Endothelial_cell｜Neuroglial_cell｜Stromal_cell；
   另允 coarse:<词表名或谱系上位名>/undetermined。
2. 冻结 crosswalk=out/KBX_LG_CROSSWALK.tsv（seat_name→reference_group+provenance 逐行；ambiguous/泛化名
   Smooth_muscle_cell、Glandular_epithelium、Neuron=no_counterpart 不猜；**coarse:X 的 X 先过 crosswalk 再决定计票**——
   no_counterpart 记 abstention_no_counterpart（P3 独立桶，不算词条/模型错误），词表名按映射计）。
3. 归一顺序=norm_identity（沿 t1_revote 实现）→crosswalk。

## §6 证据面（实验侧复刻 face 工具链；copy 不 move，禁 import 生产写路径）

1. 面件 face/EV_DIGEST_SLIM_kbx.jsonl 仅组织池题面簇；字段：cluster_id/member='LG'/material{TIS pool}/
   n_cells/qc(median n_genes|median pct_mt)/sorts/donors/top_genes(wilcoxon vs 池内其余 前20)/
   digest_pool(前60)/kb_gene_hits+kb_celltype_ranking（三词条×digest_pool，n_shared 降序、同分字母序、0 不入、
   top5；实现=run7rg v6_ranking 语义本地副本）。
2. 本面**无 lit 行、无组成参考、无 pred_hint**（E1 反"lit 背答案垫高"；KB2 红线 baselines 禁入打分）。
3. 判读 prompt=冻结件 ANNOT_INSTRUCTIONS.md（sha 33181774…）原文 + KBX_PROMPT_APPEND.txt（frozen，含
   **肌上皮空 core 结构性限制先验披露**，REVIEWER_LLM Q4 采纳文本）+ 证据卡。
4. 构建自检：digest_pool<=60、window<=20、ranking 仅三词条、题面 n>=30。

## §7 三席盲注与判分

1. 席位（BRIEF 冻结不动）：A=qwen3.8-max｜B=glm-5.1｜C=deepseek-v3.2；LLM_CHANNEL 通道、T=0.2、max_tokens=3500、
   CHUNK=5/批、3 重试、enable_thinking=false（qwen 系）；起跑前冒烟探针×3 → logs/seat_smoke.txt。
   通道 429/配额失败=block 上报，禁加席加量。
2. 票数=3×题面簇数 ≤120。
3. **裁决=C2b**：t1_revote.py（sha d321e793…）`rule_c2(bs, count_coarse=True)` 本地副本逐字语义；
   定名票任意 grade 入数；coarse:X 计入 X（X 先过 crosswalk，见 §5.2）；>=2 席同名定名；残余平票维持无名
   （tie/split3/abstain3 记录）；禁 S1 破平。判分实现自测：4 个构造样例逐断言 PASS 后才跑真票。
4. **P1**：合格锚定簇∧无泄漏旗集合 S：|{c∈S: xwalk(consensus)==truth}|/|S| **>=0.60**。
   阈值论证（BRIEF 要求）：泪腺全新组织无历史基线，60%=工程可用下限；参照成熟序列（视网膜 RUN4-r 68.2%、
   眼表 19/22）取略低档；60% 线自设、与历史考试不可比。
   报告义务（REVIEWER_LLM Q8#9）：原始分子/分母+Clopper-Pearson 精确 CI+多数类地板（=分母内最大群占比）逐值并报，
   禁只报百分比；CI 与地板只作披露不改门。
5. **P2 词条污染**：**分析集与 P1 同一集合 S**（REVIEWER_LLM Q8#8 明确化）：consensus∈三词条名 ∧ xwalk(consensus)!=truth 的簇数 **<=1**。
6. **P3 归因表**：全题面逐簇：票面三票、共识、truth、命中/错/弃权/tie、归因桶=
   {词条误导(P2计)|覆盖缺口|票弃权结构|解析混合|技术旗|abstention_no_counterpart|empty_core_no_display_channel}；
   附列未锚簇分数与不可锚原因。诚实阴性合法。

## §8 降档条款（RULING §4 逐字）

建卷后、投票前判定：合格锚定簇 <8（或 §3.6 前置条件不满足）→ 自动转 O3：不发任何票，
仅出定性 sanity（三词条 core×参考群表达域命中拓扑+逐簇面板分数表），明写"不构成疗效数字"，
泪腺定量首考挂"待新数据"账；注册资格判定=不可判。锚定数字先落 ledgers/KBX_ANCHOR_COUNT.txt 再分支。

## §9 交付与领地

只写 /mnt/D/EyeKB/plans/kbx_lacrimal_20260928/；kb/、mcp_server/、evalset 只读；执行前后复验
ledgers/SHA_UPSTREAM_PRE.txt 零写入。交付：本件+sha｜ledgers/（面板两表+原始返回+锚计数）｜face/｜annotation/｜
scoring/｜out/（逐簇表、泄漏表、crosswalk、KBX_VERDICT.md）｜scripts/｜logs/；完成或遇阻必须落卡，分批落盘；
球门落纸后禁回调。

## §10 诚实性与已知限制（先于执行披露）

1. 腺泡酶原程序在 SORT-seq 板法数据预期近乎不可检出（PRSS1/CTRB1 类；Phase-0 取证实测）——ACINAR 锚定预期
   部分失效，P3 按"覆盖缺口"记，不得记"词条错"。
2. 类器官池不进任何定量分母（§2.2）；其拓扑观察只作附录。
3. 本卡真值=外部文献面板映射，非作者标签——与历史 RUN 系列考试**不可比分**；60% 线为自设工程线。
4. 词条展示通道（kb_gene_hits）与真值通道（§3 检测一致性）严格分离：前者永不进真值侧计算，后者永不进判读员可见面。
5. 肌上皮空 core 结构性限制（§6.3 附判读披露，REVIEWER_LLM Q4）：该词条无正向展示通道，其命中/误导数字与非空 core
   词条不可作公平性比较；不可锚时归覆盖缺口。
6. LYZ/LTF 平台排除为预登记方法学先验（§1），非 KB8 结论搬运；独立性限制如文披露。
7. Tier2 敏感性面板存在（附录）；任何 Tier2 基因不得进主分析——若终判有人主张启用，属球门回调，禁。
