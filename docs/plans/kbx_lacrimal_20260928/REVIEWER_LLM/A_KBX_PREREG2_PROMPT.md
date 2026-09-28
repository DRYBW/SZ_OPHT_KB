# REVIEWER_LLM 预审请求 — KBX 泪腺词条疗效首考 PREREG v2（判据件冻结前预审）

## 角色与任务
你是生信评审强模型。下面是一份"词条疗效首考"预注册判据件草案（尚未冻结 sha）。
请逐节审：找出会让考试**失真、不可判、或结论被高估/低估**的设计缺陷，并对"待审点"逐条给裁定。
输出格式：
1. 逐条回答 Q1-Q8（每条：裁定=采纳/修正/否决 + 一句理由 + 若修正给具体方案）
2. 其它实质缺陷（按严重度排序，编号 P0=阻断冻结 / P1=必须改文 / P2=建议）
3. 终裁行：`FREEZE_OK` 或 `REVISE_FIRST`
不要泛泛套话；只提有操作后果的问题。禁止建议放宽/收紧已裁定的三门阈值本身（那是裁定件与任务书定的）。

## 背景（全部事实，无隐瞒）
- 项目：EyeKB 词条知识库。被测对象=KB8 发布的泪腺三词条：
  Lacrimal_secretory_tearcell core={LACRT,SCGB1D1,SCGB2A1,CST4,CST1,MUC7}（CL:0000315）；
  Lacrimal_duct_epithelial core={PRR27}（无 CL，OLS 实证泪腺无专条）；
  Lacrimal_myoepithelial core=**[]**（警示条：13 候选基因全数邻域火灾，无一幸存）。
  腺泡酶原词条=照实缺口弃用（PRSS1 2.3/CTRB1 6.1 CPM 全池不可检出）。
- 数据：GSE164403（人泪腺组织+类器官 SORT-seq 384孔板，3,071×39,009，唯一人泪腺本体图谱，非 OA）。
  **无逐细胞作者类型标签**（obs 只有 FACS 分选池标签 author_sort）——原任务书"真值=作者标签众数"前提不成立，已裁定改道。
- 裁定件 KBX_RULING_1（有约束力）：O2 外部文献 marker 参考系为主档（≥6 群：腺泡/导管/肌上皮/免疫/内皮/神经，
  每群每基因挂可核 PMID，EuropePMC 复核留原始返回；禁参考 KB 任何词条/KB8 面板/自建聚类派生）；
  Leiden→簇按外部面板打分→参考锚定簇（纯度>=0.7 ∧ 首二次得分比>=2x）；锚不住=附列不计分母；
  防循环硬项=外部面板基因×KB 泪腺 core 逐群重叠>50% 打泄漏旗、该群得分不计 P1 分母；
  三席盲注+120 票上限+C2b 票规+判分三门（P1>=60%、P2<=1、P3 归因表）全部不动；
  合格锚定簇<8 → 自动降 O3 定性档（不发票，只出拓扑 sanity，明写"不构成疗效数字"，定量首考挂待新数据账）。
- 用 KB8 自建聚类当真值=循环（词条 core 即来自那套聚类面板打分），已被 Phase-0 取证驳回。
- 票规 v2/C2b：定名票任意 grade 计数、coarse:X 计入 X 法定人数、≥2 席同名定名、残余平票维持无名。
  本 run=该票规首个正式适用 run（向前生效条款）。
- 历史同构考试的参照数字：视网膜热点系列 R1 15/22（68.2%）；眼表 Q6 系列 19/22。全新组织无基线。
- 前轮教训（E1，同类考试曾出过的问题）：证据面附"本地文献库检索证据（lit 行）"时，lit 与被测词条同源，
  把判读席"背答案垫高"（表面高分实为同源泄漏）⇒ 本 run 证据面不含 lit。
- KB2 红线：baselines 观察档禁当达标线/禁入打分 ⇒ 本 run 证据面不含组织组成参考分布。
- 面板抓取实测（PREREG 规则执行前的原始数字）：88 候选基因，Tier1（基因 token 同现于 title/abstract 且语境 token 同现）仅 3 PASS；
  Tier2（该基因×lacrimal×人 query 有 title 含语境 token 的命中且 hitCount>=2）预计能过一批，但 Tier2 证据强度弱于 Tier1（token 可能匹配在全文某处）。
- 类器官池 1,535 细胞：体外重建=导管样程序（论文自述 organoids recapitulate lacrimal ducts）；无免疫/内皮/神经细胞。
  KB8 scope 明文：类器官侧只作导管参考、禁产体内基线。KB8 曾按两池分别聚类（参数族沿 KB2：HVG2000/PCA50/nn15/leiden igraph res1.0，seed 不同卡不同）。
- 面板七群打分=簇级 pseudobulk CPM 检测分数率（CPM>=5 的面板基因占比），锚定门=最高群检测率>=0.7 ∧ >=2×次高群。
  注意：各群面板基因数不等（预计 ACINAR~15、DUCT~10、MYOEPITH~5、IMMUNE~10、ENDO~6、NEUROGLIA~6、STROMA~6），
  检测分数率天然偏向基因数多的群（多基因群更容易堆出 0.7）。

## 待审点
Q1 两池都入题面（合并读=全题面、主读=组织池小计），还是只组织池入题面？类器官簇的参考群名是体内语义硬套。
Q2 Tier2 文献语境门会不会放进"假语境"基因污染面板打分？若保留，是否要加护栏（如 Tier2 基因只作次级/不进 0.7 主门分子分母，或 Tier2 基因数占比过高整群降级）？
Q3 "纯度>=0.7"操作化为**最高群检测分数率>=0.7**（裁定原文的"纯度"一词在作者标签不存在时的最贴近实现）——采纳/否决/替代方案？（替代候选：簇内 top 群基因表达细胞占比、或 max z-score 占比归一）
Q4 肌上皮警示条 core=[] 使 kb_gene_hits 通道永不亮，但词表含其名、判读席可自由投它。P2 操作化（共识=词条名∧crosswalk 群≠真）对肌上皮=判读员凭通名知识乱枪打中的计数——这个"考试对 core=[] 词条无展示通道"的结构性缺陷是否要在 PREREG §10 先于执行披露？给建议写法。
Q5 P1 60% 线 vs 多数类地板：P1 分母=合格锚定簇（数量小且构成未知），若最大群占比>=51%，地板与 60% 线几乎重合，"命中 60%"就无意义。草案写了"60% 线须高于地板+9pp 才记'超地板'（仅披露不改门）"。这个披露是否足够？是否应加"合格锚定簇>=8 且最大群占比<=40%"作为考试有效性前置条件（不满足即按降档处理）？注意裁定只写了 <8 降档，没写构成偏斜降档——若你判需要，我会以"考试有效性前置条件"名义加（不触三门阈值本身）。
Q6 C2b 的 coarse:X 计票：X 也过 crosswalk 才有意义（判读员投 coarse:Ductal_cell 计入 Ductal_cell→DUCT）。若 X 是词表外泛名（coarse:epithelium）计入后 crosswalk no_counterpart → 该票等于定向弃权。这个处理 OK？
Q7 题面规模：预计组织池 res1.0 出 ~12 簇、n>=30 留 ~10；锚定门后合格锚定簇可能仅 4-8 → 大概率触发 O3 降档、120 票配额用不上。这是数据现实（裁定已预期）。为把"考卷"尽量做厚，除池并入外还有什么合规增量手段（不触裁定：真值必须外部面板；禁 KB 派生）？如 resolution 网格多选一（须预注册且不得看结果挑）？还是维持 res=1.0 单档？
Q8 还有没有其它会失真/不可判/结论被高估的设计缺陷？

# REVIEWER_LLM 预审补件 B — 语境门干跑实证（发给同一评审，接前请求，先读再答）

你前函将收到 88 基因候选矩阵干跑结果（规则草案 §1.2 Tier1∨Tier2 逐字执行，ledgers/eurpmc 原始返回）：

=== FINAL panel by group（干跑） ===
ACINAR: T1=[] | T2=['BPIFA2','DCD','LPO','MUC7','PIP'] | FAIL=19 个（含 PRB1-3/LACRT/PRSS1/CTRB1/STATH/CA6/PRR4/ZG16B/AQP5...）
DUCT:   T1=[] | T2=[] | FAIL=16 个（含 KRT19/CFTR/SOX9/KRT7/PRR27/PIGR/SPP1...全部）
MYOEPITH: T1=['MYH11'] | T2=[] | FAIL=13（含 ACTA2/CNN1/KRT5/KRT14/TP63/TAGLN...）
IMMUNE: T1=['CCL5','CD74'] | T2=['CD3E','CSF1R'] | FAIL=8（含 PTPRC/CD68/MS4A1/NKG7...）
ENDO:   T1=[] | T2=[] | FAIL=7（含 PECAM1/CDH5/VWF/CLDN5...全部）
NEUROGLIA: T1=[] | T2=['S100B'] | FAIL=6（含 PLP1/SOX10/NGFR...）
STROMA: T1=[] | T2=['COL1A1'] | FAIL=6（含 DCN/LUM/PDGFRB...）

Tier2 样本目检：多数 T2 命中来自两篇——PMID 34950038（泪液/唾液蛋白组，SJ 病）与 PMID 35295950（泪囊 chrRNA 疾病研究）；
基因 token 仅在全文索引匹配、abstract 不可见。

## 由此新增的结构性问题（并入你 Q8，也可单列）
S1 照此终判，DUCT 与 ENDO 两群 available=0 → §3 锚定门对这两群永不可能成立；
   七群里可锚的只剩 ACINAR(5 个 T2 全弱源)、IMMUNE(4)、NEUROGLIA(1)、STROMA(1)、MYOEPITH(1) —— 
   合格锚定簇几乎必然 <8 → 100% 触发 O3 降档。考试大概率"无卷可判"。
S2 语境 token 把 "lacrimal sac"（泪囊=引流结构，非泪腺；且疾病材料）算成了泪腺语境——泪囊/泪道文献基因不可作泪腺参考系。
   建议修正：语境 token 收紧为 {lacrim|tear|exocrine} 且 title 含 "lacrimal gland|lacrimal (gland) 语境、排除 lacrimal sac|canalicular|dacryocyst"。你裁。
S3 候选矩阵本身偏"酶原/泪液蛋白"，泛细胞类型 canonical marker（PECAM1/CDH5/PTPRC 等）在"基因×lacrimal"检索下天然吃亏。
   给可操作替代：例如 ①群级锚定=canonical 泛标记走独立语境通道（query 用 "<GENE> AND 'lacrimal gland' AND (marker OR cell type)" 或接受"组织学共识基因无需基因级 PMID、群级挂 1 篇泪腺图谱文献"）——但这要动 RULING"每群每基因挂可核 PMID"的字面；
   ②或者接受"本考卷只有 2-3 群可锚 → 直接按 §8 降档出 O3 定性档"——诚实但等于考试不成立；
   ③或扩大候选矩阵+换检索式（如 "gene AND 'lacrimal gland' single cell"），T2 质量门槛提高（abstract 可见或 2 篇以上不同 PMID）。
   你给出你认为不违裁定精神、又能把考卷做厚到 >=8 锚定簇的最优组合（可组合多措施），并逐条给出你会怎么改 §1。
S4 注意：任何修正仍禁 KB 派生；修正属于"判据冻结前的设计裁决"，不是看结果挑球门——三门阈值与裁定结构不动是你的边界。

请在主回函里对 S1-S4 逐条裁定，并把"面板语境门最终文本"直接写成可粘贴段落。


## PREREG v2 草案全文

——以下为草案全文（与本请求同件拼接）——

# KBX_PREREG v2 — 泪腺词条疗效首考判据件（票规声明=v2/C2b；判据先于执行冻结，2026-09-28）

- 卡：t_0fb07fd6（D13）｜ 任务书：BRIEF_KBX.md（sha af6a93b0…，见 ledgers/SHA_UPSTREAM_PRE.txt）
- 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md D13
- 裁定继承：**KBX_RULING_1.md（sha c159f5fe…）**——Phase-0 取证认定 BRIEF 的"作者标签真值"前提不成立，
  裁定=O2 外部文献参考系为主档、合格锚定簇<8 自动降 O3 定性档；判分三门+120 票上限+C2b 票规不动。
  本件即该裁定的操作化冻结。**本件落纸取 sha 入 ledgers/KBX_PREREG_SHA.txt 之后，才允许面板终判与建卷。**
- **票规版本声明（D11 硬条款）：本 run 适用 v2=C2b**（PROTOCOL_VOTING_v2_C2b.md sha 06a00ea9… 生效范围内，本卡为首个适用正式 run）。
- 红线继承：泪腺 A3 **维持不注册不接线**——本卡=纯离线考试，产出=注册申请资格判定**建议**，不执行注册；
  kb/、mcp_server/、evalset 只读；零下载（EuropePMC REST 文献语境查询=元数据检索，非数据下载，逐请求留原始返回）。

## §1 参考系 = 外部文献 marker 面板（禁 KB 派生）

1. 候选基因仅凭领域知识列出（scripts/kbx_p1_panel_build.py 内嵌候选矩阵，本件附后逐字冻结）；
   生成过程禁查询/抄录 kb/ 任何词条、KB8 面板、自建聚类输出。**唯一例外披露**：KB8 完成报告曾量化
   LYZ/LTF 在本数据集为板法 ambient 超富集——本卡候选侧直接排除 LYZ/LTF 两基因（理由=平台污染先验，
   非循环；本卡亦不读取 KB8 面板基因集）。
2. **语境门（终判规则，先于面板落纸冻结）**：query=`"<GENE>" AND lacrimal AND "Homo sapiens"[Organism]`，
   EuropePMC REST resultType=core pageSize=5，原始返回逐基因留 ledgers/eurpmc/：
   - **Tier1（强）**：任一命中记录 title+abstractText 同时含基因精确 token 与语境 token（lacrim|tear|exocrine|gland）→ PASS，记该 PMID；
   - **Tier2（语境）**：无 Tier1，但存在命中记录 title 含语境 token 且该 query 总 hitCount>=2 → PASS(tier2)，记该 PMID，终表标 tier=context；
   - 其余 → FAIL，照实出局（诚实阴性，禁凑数）。
3. 面板终表 ledgers/KBX_PANEL_FINAL.tsv（逐基因：group|gene|tier|PMID|hits|query|判定）；
   群定义=参考群 **ACINAR/DUCT/MYOEPITH/IMMUNE/ENDO/NEUROGLIA/STROMA 七群**（>=6 达标，RULING §O2.1）。
4. 可用性过滤：面板基因以 h5ad var symbol 空间为准（sha 5e6d753d…）；不在 var 的面板基因不入该群分母（逐群登记 available 数）。

## §2 建卷（机械规则冻结；数据=盘上 GSE164403）

1. 输入：/mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad（sha 5e6d753d0c10…399，3,071×39,009，只读）。
   排除 author_empty_well==True（3 细胞，作者自标）→ 3,068。
2. **两池分别聚类，永不混池**（组织/类器官材料语义不同，池=source_type；类器官侧挂 material=organoid 标注）。
   题面=两池 n_cells>=30 簇之并；预计组织池 10~14 簇、类器官池 5~9 簇。判读主读=组织池小计，合并读=全题面（两口径并报，预注册写死）。
3. 参数族（冻结）：normalize_total(1e4)+log1p → HVG flavor=seurat 2000 → PCA n_comps=50（svd_solver=default, random_state=20260928）
   → neighbors n_neighbors=15 (n_pcs=50) → leiden flavor=igraph **resolution=1.0**、random_state=20260928。
   扫描栈=本机 scanpy 1.12.2（版本入台账）。seed=20260928（本卡新参考系，与 KB8 的 20260925 独立，不读 KB8 聚类产物）。
4. **票上限断言（BRIEF 冻结条款）**：题面簇数 N 须满足 3×N<=120；若 N>40 按 n_cells 降序截断 top40，截断名单落盘。

## §3 打分与锚定门（真值=外部面板映射；RULING 操作化）

1. 簇级 pseudobulk CPM：簇内 counts_int32 求和 ÷ 全矩阵总计数 × 1e6（分母口径=矩阵内基因总计数，披露沿 KB2 统计语义）。
2. 群得分 score(c,g) = 该群 available 面板基因中 CPM>=5 的占比（检测分数率；CPM_FLOOR=5 沿 W2 冻结常量）。
3. **锚定判据（RULING"纯度>=0.7 ∧ 首二次得分比>=2x"的操作化，逐字冻结于此）**：
   - top = argmax_g score(c,g)；second = max_{g≠top} score(c,g)；
   - 锚定 ⇔ score(c,top) >= 0.7 ∧ ( second == 0 ∨ score(c,top) >= 2×second ) ∧ n_cells>=30；
   - 并列最高分（两群同分）→ 不可锚（ratio 门不满足）；
   - 未锚定簇=附列（仍入题面投票、只进 P3 归因，不进 P1 分母）。
4. **ambient 机械过滤（打分侧二次防线）**：面板基因若 簇间 log2(CPM+1) 变异系数 CV<=0.3 且 全簇中位 CPM>=2000
   → 判均匀本底、出该群打分（出局名单逐 run 落盘，先于锚定判定生效，属确定性规则非人工挑选）。
5. 参考锚定簇命名=群名（ACINAR/DUCT/MYOEPITH/IMMUNE/ENDO/NEUROGLIA/STROMA）；逐簇表 out/kbx_cluster_table.tsv
   全列（含未锚簇附列、donor 构成、sort 构成）。

## §4 防循环硬项（泄漏重叠表；RULING 逐群落盘）

1. KB 泪腺 core 集（只读取自 markers_v6_lacrimal_increment.json，sha 4e7e001a…）：
   {LACRT, SCGB1D1, SCGB2A1, CST4, CST1, MUC7}（secretory 6）∪ {PRR27}（duct 1）∪ {}（myoepithelial 警示条空 core）= 7 基因。
2. 逐群 overlap(c)=|该群 available 面板基因 ∩ KB core 7 集| / |该群 available 面板基因|；
   **overlap>0.5 的群=泄漏旗**：其锚定簇不计入 P1 分母（票仍投、只作参考），逐群表 out/kbx_leak_overlap.tsv 落盘。
3. 若泄漏旗致 P1 分母=0 → 不出 P1 数字，按 §8 降档处理（fail-closed，禁除零假通过）。

## §5 判读词表与 crosswalk（先于投票冻结）

1. LG 成员词表（判读员可用原样词，另允 coarse:<词表内或谱系上位名>/undetermined）：
   - 被测词条名：Lacrimal_secretory_tearcell ｜ Lacrimal_duct_epithelial ｜ Lacrimal_myoepithelial
   - 参考通用名：Acinar_cell ｜ Ductal_cell ｜ Myoepithelial_cell ｜ Immune_cell ｜ Endothelial_cell ｜ Neuroglial_cell ｜ Stromal_cell
2. **冻结 crosswalk** out/KBX_LG_CROSSWALK.tsv（词条名/通用名/常见别名 → 参考群；ambiguous 一律 no_counterpart 不猜；
   逐行 provenance；sha 入 ledgers，票规 v2 §4.3 词表漂移条款照此执行）。已知预期 no_counterpart：Smooth_muscle_cell
   （泪腺 mural 域纠缠 KB6b 先例，不折叠）、上皮泛名 glandular_epithelium（非单一群）。
3. 票面名归一顺序=norm_identity（undetermined*/coarse: 前缀处理沿 t1_revote 实现）→ crosswalk 逐词映射（大小写不敏感精确 token）。

## §6 证据面（face；实验侧复刻 face 工具链，copy 不 move，禁 import 生产写路径）

1. 面件 face/EV_DIGEST_SLIM_kbx.jsonl，逐簇行字段：
   cluster_id（TIS::k / ORG::k）｜member='LG'｜material{species=homo, tissue=lacrimal_gland, pool}｜n_cells｜
   qc（簇内 median n_genes_by_counts / pct_counts_mt）｜sort 构成（author_sort 计数）｜donor 构成（patient_number 计数）｜
   top_genes=簇 vs 池内其余 wilcoxon 前 20（symbol）｜digest_pool=wilcoxon 前 60｜
   kb_gene_hits + kb_celltype_ranking=被测三词条×digest_pool（n_shared 降序、同分字母序、0 命中不入、top5/hits≤8 词条——
   实现=run7rg v6_ranking 语义的本地副本，禁 import eyekb 生产写路径）。
2. **本 run 面不含 lit 行、不含 tissue_composition_ref、不含 pred_hint**（偏离 RUN7RG 面，理由=①本地文献库检索链
   与 KB8 证据链同源、E1"lit 背答案垫高"通道不可控；②baselines KB2 红线禁入打分；③首考只测词条装配本身的疗效。
   判读指令文本中 lit 相关段落对本面自然为空，明示"本 run 无 lit 行"）。
3. 面构建自检：digest_pool 长度<=60；词条 ranking 与面板基因重合断言（ACINAR 面板∩secretory core 若含 LACRT/MUC7，
   ranking 展示允许——那是被测对象自身，不是真值通道；真值只用面板+§3 打分）。

## §7 三席盲注与判分

1. 席位（BRIEF 冻结不动）：A=qwen3.8-max ｜ B=glm-5.1 ｜ C=deepseek-v3.2（LLM_CHANNEL 通道，enable_thinking=false（qwen 系），
   T=0.2，max_tokens=3500，CHUNK=5/批，3 重试，断点文件独立）。起跑前三席冒烟探针各 1 次，记录 logs/seat_smoke.txt。
2. prompt 壳=run_annotator_run7rg.py 逐字派生：冻结件 ANNOT_INSTRUCTIONS.md（sha 33181774…）原文 + 本卡 LG 词表与
   "无 lit 行"说明块（frozen 文本，sha 入 ledgers/KBX_PROMPT_APPEND.txt）+ 证据卡。盲态：判读员只看面+指令；
   不看参考群名/真值/对侧票/本判据细节（词表含参考通用名=既有协议惯例，同 Q6 九词表）。
3. 票数=3×题面簇数 ≤120（§2.4 断言）；超=block 上报，禁自行加席加量。通道 429/配额失败=block 上报（沿 KB9 §3 条款）。
4. **C2b 裁决**（参考实现=t1_revote.py sha d321e793… `rule_c2(bs, count_coarse=True)` 本地副本）：
   定名票任意 grade 入数；coarse:X 计入 X 的法定人数（X 过 crosswalk，同§5.3）；>=2 席同名定名；
   残余平票维持无名（tie/split3/abstain3 记录）；undetermined/缺票不入数。禁 S1 破平。
5. 球门（RULING 不动）：
   - **P1**：锚定且无泄漏旗簇中 C2b 共识名 crosswalk 后 ==参考群名 的比例 **>=60%**。
     阈值论证（BRIEF 要求写进本件）：泪腺为全新组织无历史基线，60%=工程可用下限（对照：视网膜热区
     RUN4-r 15/22=68.2%、RUN7RG 系列同带；全新组织首考取略低于成熟序列的工程底线）。
     多数类地板对照=若共识恒预测分母内最大群，命中率=该群占比（逐 run 实算入 VERDICT，60% 线须高于地板+9pp 才记"超地板"，
     否则如实标注"与地板不可分"——地板仅作披露，不改门）。
   - **P2**：锚定簇中 C2b 共识名∈三词条名 且 crosswalk 后 !=参考群名 的簇数 **<=1**（词条误导；tie/弃权不计）。
   - **P3**：逐簇归因表（全题面：共识、群名、命中/错/弃权/tie、错误归因=词条误导|覆盖缺口|票弃权结构|解析混合|技术旗；
     诚实阴性合法；附列未锚簇逐簇列分数与不可锚原因）。
6. 判分实现=scoring/kbx_verdict.py（t1_revote rule_c2 + norm_identity + 本卡 crosswalk 的本地副本，禁 import 生产写路径；
   实现自测=§7.4 规则在 2 个构造样例上逐断言 PASS 后才跑真票）。

## §8 降档条款（RULING §4 逐字）

锚定（§3.3 判定且未被 §4.2 泄漏旗剔除）**合格锚定簇 < 8** → 自动转 O3：不发任何票，
仅出定性 sanity（三词条 core×参考群表达域命中拓扑 + 逐簇面板分数表），明写"不构成疗效数字"，
泪腺定量首考挂"待新数据"账；注册资格判定=不可判（按书报告）。判定发生在建卷后、投票前，
锚定数字先落盘 ledgers/KBX_ANCHOR_COUNT.txt 再分支。

## §9 交付与领地

- 只写 /mnt/D/EyeKB/plans/kbx_lacrimal_20260928/；kb/、mcp_server/、evalset 只读+sha 台账（执行前后各核验一次
  上游件 sha 不变，ledgers/SHA_UPSTREAM_PRE.txt 复验）。
- 交付：KBX_PREREG_v2.md(+sha)｜ledgers/（eurpmc 原始返回、面板终表、PREREG sha、票量记录）｜
  face/｜annotation/｜scoring/｜out/（逐簇表、泄漏重叠表、KBX_VERDICT.md、注册资格判定建议）｜scripts/（全带 kbx_ 前缀）｜logs/。
- 完成或遇阻必须落卡；分批落盘；球门落纸后禁回调。

## §10 诚实性与已知限制（先于执行披露）

1. 腺泡参考群在SORT-seq板法数据中预期近乎不可检出（PRSS1/CTRB1 类酶原；Phase-0 取证实测），
   ACINAR 锚定预期失败或转附列——P3 归因按"覆盖/平台缺口"而非"词条错"记。
2. 类器官簇=体外程序，参考群名按体内语义套用是 RULING §O2 裁定的已知妥协（判读主读=组织池小计即为此设）。
3. 本卡真值非作者标签（外部文献面板映射），与历史 RUN 系列的"作者标签真值"考试**不可直接比分**；60% 线为自设工程线。
4. KB core 与被测词条重叠披露见 §4；词条展示通道（kb_gene_hits）与真值通道（§3 打分）严格分离，
   前者永不进真值侧计算，后者永不进判读员可见面。

