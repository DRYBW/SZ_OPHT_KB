# BRIEF_RAGFIX2 — 门③追补轮 v2.5：16 基因白名单核验重组装 + rag 库 v2.4.1 增量 + 门③复算（D21）

> 补缺声明：本任务书为执行卡 t_6848d3de（RAGFIX2）正文所指向的任务书路径，建卡时协调者未落盘该件。
> 由执行方 AGENT_ROLE 依 ①卡体一句话规格 ②RAGFIX_DECISION_1.md（P1=B 批 v2.5 追加轮，PI 授权落定）
> ③RAGFIX_NOTE.md §5/§9（REVIEWER_LLM 裁决）逐字重建并冻结于本件，2026-09-28。除本件外对 rag_fix_20260928
> 目录零写入（该目录为前卡 t_d0bea5a6 领地，只读）。

## 1. 目的
RAGFIX（t_d0bea5a6）门③ A 档 92 基因覆盖消除 67/92=72.8% <80% FAIL；残差 25 单元归因三分：
①16 单元=was_S2_ctx_mismatch 基因，RAGGAP 必补表从未配过候选论文（清单组装口径缺口）；
②8 单元仅备选 104 覆盖（前卡红线不下）；③1 单元 LILRB2（撤证设计，诚实留空）。
PI 拍板=P1 选项 B（REVIEWER_LLM 同向）：批准 v2.5 追加轮。本卡补 ①：对 16 基因重跑候选检索 →
逐篇题录-PMID 核验白名单（防重蹈 KB6/KB9 eutils 共现建链 PMID 错位误引）→ 白名单闭集下载入库
v2.4.1 → 门③原口径复算。②的 8 单元与备选 104 面本卡**不碰**（PI 批不批备选面是另一决策）；
③LILRB2 维持 none。

## 2. 目标与验收线
1. 16 基因（ATP8B4/CALD1/CDH8/CST1/CST4/FAM135A/FBXL7/FCER1G/GPR143/GRM5/LMOD1/LRRTM3/
   MUC7/PTPRK/SAMSN1/SHISA6，ctx 见 out/GATE3_residual_units.tsv）逐基因候选检索台账 +
   白名单（逐篇三条件核验记录，落卡前冻结为闭集）。
2. 白名单闭集下载入库 **literature_db/v2.4.1_2026-09**：v2.4 全部 230,426 chunks 字节不动
   原样继承（零重算）+ 增量 chunks（chunker/embedding 与 v2.4 完全同源）。
3. 门③复算：**原分母 92、原阈值 80%、原判据逐字**（scripts/gate3_coverage.py 同构，只扩
   "新增论文"面=closed64 ∪ RA2 白名单、"闭集"面=64∪白名单）。输出数**不降**（≥67，单调性
   断言）；≥74/92=80% 记 PASS，未达则如实记 FAIL + 逐单元诚实归因（真缺文献基因维持 none）。
   **不追认 v2.4 已过门③；不移动球门。**
4. 前置断言（67 项已计入证据有效性复核，REVIEWER_LLM 裁决点 3）：chunks_ra_raw.jsonl
   sha256==43d02db66b9a3f235ff4f1b5beaafbc9ba5338aef53a4e26896649ff66a10196（开算前+收尾双核）；
   v2.4 目录四件 sha 对 ledgers/SHA_DELIVERABLES_20260928.txt 复核零漂移。
5. 产出 RAGFIX2_NOTE.md：检索账/白名单核验账/下载账（逐 PMID 成败+体积）/v2.4.1 构建账/
   门③复算表/残差诚实归因/仓重同步登记。

## 3. 方法（冻结判据）
### 3.1 题录核验三条件（逐篇，白名单台账必录）
- **C1 题录含断言词**（题录=EPMC core 题录+摘要，判"该文确在讨论 该基因×该眼语境"，三档任一）:
  a) 基因 symbol 词边界出现于标题；或 b) 登记别名/家族词出现于标题 ∧ 语境词族词出现于标题
  （别名表冻结：CST1/CST4→cystatin；MUC7→mucin；FCER1G→FceRI/Fc epsilon/IgE receptor；
  GRM5→mGluR5/metabotropic glutamate receptor；GPR143→OA1；CALD1→caldesmon；
  LMOD1→leiomodin；其余仅 symbol）；或 c) 基因 symbol ∧ 语境词族同现于标题+摘要且为
  断言语境（记录命中句入台账）。
  链路口例外：kb 词条自身 cited_pmids，标题与断言语义一致（如 cystatins in lacrimal gland）
  → 记 chain_verified，回填 kb 引用链（这正是 RAGFIX §4 要救的"note 真文在、PMID 错位"反面——
  错位者不得入）。
- **C2 PMID 可核**：EPMC EXT_ID:<pm> AND SRC:MED 单篇回查命中，标题逐字一致（台账存快照）。
- **C3 非 HRCA 自引 ∧ 防重蹈**：∉HRCA_EXCL={41578023(HRCA Li et al Nat Genet 2026),
  32555229, 34691611, 37388908, 32946783, 39117640}（kb/baselines/retina.md 锚定文献面）；
  ∉v2.4 papers.jsonl 在库 paper_id（在库=重复，gate 永不兑现且 merge 冲突）；∉closed_set(64)。
### 3.2 检索口径（与 RAGGAP s5 同源可比）
EPMC REST search：`"<SYM>" AND <CTX词族> AND SPECIES:"HUMAN"` pageSize=75（词族逐字=
RAGGAP s5 CONTEXT 表：retina=(retina OR retinal OR photoreceptor OR macula OR "retinal pigment")
/ face=(cornea OR corneal OR conjunctiva OR conjunctival OR "ocular surface" OR limbal)
/ lacrimal=(lacrimal OR tear OR "dry eye" OR meibomian) / kb9=(ocular OR eye OR conjunctiva OR
cornea OR "ocular surface")）。无 symbol 标题命中的基因补跑别名查询同口径。0.5s/请求限速、
直连 ProxyHandler({})。**禁裸用 eutils 通道回填**（KBCHAIN 告诫）；eutils 仅按 ra_fetch 先例作
EPMC 未收录 PMID 的摘要补录，台账标 source。
### 3.3 可兑现性预检（gate③ 字面判据=新论文 chunk 文本词边界提及 gene ∨ cited∩闭集有chunks）
- OA=Y ∧ PMCID → 全文路（下载后必须复核 token 实存于 chunks，台账记 text_hit，不中则
  该篇不宣称消除，如仍为 kb cited 则 chain 路兑现）；
- 非 OA → 仅当摘要含 symbol token（text 路）或本单元走 chain 路，否则不入围（避免无效下载）；
- 每基因首选 1 篇（优先级：kb自引已核 > 标题含symbol的OA全文 > 别名词OA全文 > 摘要路）；
  第 2 篇仅当首选下载后复核失败时替补。白名单总量目标 ≤20 篇，**下载体积硬上限 6MB**——
  超限即停，剩余缺口回挂报批（DECISION_1 红线：锁定≤6MB，超限或替换重新报批）。
### 3.4 v2.4.1 构建（管线逐行同构前卡，禁自创口径）
ra2_fetch.py→ra2_parse_chunk.py→gate 前 token 复核→ra2_merge.py：v2.4 parquet
230,426 行原样 + RA2 增量（sentence_transformers bge-large-en-v1.5 cpu fp32 normalize=True，
pipeline_env，systemd-run -p MemoryMax=20G）；papers.jsonl=v2.4 行原样（n_chunks 重算口径同
ra_merge）+ RA2 新行（source_version=v2.4.1-ra2, admission_lane=ragfix2_v25_whitelist）；
manifest.yaml 注记继承 sha 台账+闭集+核验账。EYEKB_DB_POINTER.yaml 追加 v2.4.1 块
（前缀逐字不变校验，default=v2.0 不动，仿 pointer_register.py）。
### 3.5 门③复算 + 回归旁证
gate3_coverage_v25.py（3.2 断言前置）；gate2_retina_v24.py 克隆对 v2.4.1 复测（停车线=用例级
不劣化 <8/10）；gate① off 态=服务端默认库 v2.0 不受新目录影响，以 sha 台账+指针前缀校验代证
（如预算允许可重跑 runner 加严，非硬项）。

## 4. 注意事项（已知坑与边界）
- chunk 文本**不含标题**（v2.4 实证口径）：标题含 symbol ≠ 门③兑现；abstract-only 且摘要无
  token → text 路不兑现（前卡 §5 归因②教训）。
- 预期诚实报：FAM135A/SHISA6/LRRTM3/ATP8B4/FBXL7/SAMSN1 等低眼命中基因大概率无合格候选，
  维持"真缺文献"none 是合法结果，不得为凑数放宽 C1（移动球门=违规）。
- 8 个仅备选 104 单元（C8ORF76/COL19A1/CPNE5/FAM107B/SLC24A3/SSR4/XCR1/ZNF804B）不在本卡范围；
  LILRB2 维持撤证留空。检索到的论文若同时覆盖这些基因只算副产品，不宣称单元消除。
- 领地：写=本目录补 BRIEF_RAGFIX2.md（仅此一件）+ plans/rag_fix2_v25_20260928/ 全目录 +
  literature_db/v2.4.1_2026-09 + EYEKB_DB_POINTER.yaml 追加块；**禁写** kb_chain_audit_20260928/
  （另卡领地）；只读面=v2.0–v2.4 库、kb/markers 面板核心、mcp_server/、evals/、rag_gap_20260928/。
- 零清单外下载；不绕付费墙（fullTextXML 403/404 即 abstract-only 入账）；>1GB 条款远未触发
  （预算 ≤6MB，DECISION_1 已批）。
- 动 kb/指针面 → 登记 REPO_RESYNC2 不 push（前卡先例）。
- EPMC 偶发 500/残缺 JSON：重试口径同 ra_fetch（hitCount 缺失视为失败）。

## 5. 交付物与落盘
- out/RA2_candidate_ledger.tsv（全候选×三条件判定）+ out/RA2_WHITELIST.{md,tsv}（闭集+锁定体积）
- out/closed_set_ra2_pmids.txt；work/（xml、ra2_selected.jsonl、ra2_availability.tsv、
  chunks_ra2_raw.jsonl）
- 库：/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.1_2026-09/ 四件
- out/GATE3_COVERAGE_v25.json + out/GATE3_residual_units_v25.tsv + out/GATE2_RETINA_v241.json
- ledgers/（SHA_PRE / SHA_POST / SHA_DELIVERABLES 双时点）；RAGFIX2_NOTE.md；REPO_RESYNC2 登记
- 心跳：阶段边界（检索完/白名单锁定/下载完/v2.4.1 落盘/门复算完）落卡；24h 回传，48h 升级。

⚠ 收尾落卡断言：退出前 ① 逐条 stat 核对任务书承诺的交付物已落盘（盘上文件才是证据，会话记忆不算）；② kanban_complete 与 kanban_block 二选一必调——做完→complete；卡住→block 列缺项；半做完→complete 已完项 + kanban_create 后续卡；只给最终文本不落卡 = rc=0 协议违规（pi-briefing 板 09-10~09-25 实证 15 例）。
