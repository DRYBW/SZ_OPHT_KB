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
