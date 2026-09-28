# DECISION_MATRIX_RAGFIX3 — 判读矩阵（预注册，开算前 sha 落纸）

卡: t_b94d0999 ｜ 任务书: BRIEF_RAGFIX3.md ｜ 执行日: 2026-09-28
上游基线: v2.4.1 门③ 78/92=84.8% PASS（rag_fix2_v25 口径）；目标面=7 个仅备选104覆盖单元
（C8ORF76/COL19A1/FAM107B/SLC24A3/SSR4/XCR1/ZNF804B 均 retina/membrane ctx，tier_FINAL cited_pmids 实测全空→只能走 text token 路）。

## R0 扫描面与准入判据（零 LLM，机械四检）
扫描面 = TIER_A_approval_list.md 备选表 104 行（已提取 work/backup104_raw.tsv，104 unique PMID）。
逐篇四检（顺序执行，拒绝即止并记原因）：
- V1 题录可核性：EPMC `/search?EXT_ID:{pmid} AND SRC:MED` resultType=core 单篇回查命中
  ∧ 返回标题与表内截断标题前缀一致（沿 ra2_fetch C2 复核判据逐字）。不命中→REJECT_VERIFY；
  标题不符→REJECT_TITLE_MISMATCH。禁 eutils 裸回填（KBCHAIN 告诫）。
- V2 在库查重：pmid ∈ v2.4.1 papers.jsonl paper_id 集 ∨ live DOI ∈ papers.jsonl doi 集（大小写不敏感）
  → REJECT_IN_LIBRARY（防重蹈/防双计）。本地预检已知命中：40171795（=RA2 白名单成员）。
- V3 自引/撤证排除：pmid ∈ HRCA_EXCL={41578023,32555229,34691611,37388908,32946783,39117640}
  ∪ {41349939(LILRB2 撤证 errata)} ∪ closed64 ∪ RA2_17 → REJECT_SELF_CITATION/IN_CLOSEDSET（沿 RA2 三条件之C3）。
- V4 OA 全文可得性与体积：live isOpenAccess/pmcid 记录 + `curl -sI` HEAD fullTextXML 实测可达性。
  **实测注记**：EPMC fullTextXML HEAD 响应无 Content-Length（预注册时已实测），体积判定改以 GET 下载
  实得 xml_bytes 记账（沿 ra2_availability.tsv 先例）；HEAD 状态码照记。
  准入分级：OA=Y∧pmcid∧可达→FULLTEXT；OA=N 或 fullTextXML 403/404/无 pmcid→ABS_ONLY 入库
  （沿 RA2 先例：3 篇 abstract-only 入库，n_papers_fulltext_absent 如实+计数，不绕付费墙）。
入库 = V1∧V2∧V3 全过；V4 只定入库形态（FULLTEXT/ABS_ONLY），不构成拒绝。

## R1 预算与红线（下载面）
- 波次全批预算 ≤100MB（累计 xml_bytes）；超限停车，剩余记 SKIPPED_CAP 如实登记。
- 任何单项 >1GB 不收并登记（GET 实测 size 判定；fullTextXML 语境下理论不可达此量级，条款保留）。
- 抓取走 PORT 代理（mihomo，预注册时 CONNECT 实测 200）；代理失败回退直连并记录通道
  （RA2 直连先例，不视为违令——如实登记通道分布）。0.6s/请求限速+指数退避沿 ra2_fetch 逐字。
- 零清单外下载：下载闭集=扫描账准入集，逐 PMID 台账 work/ra3_availability.tsv。
- 禁碰 GPU（5090=qwen 服务）；embedding 仅 CPU bge-large-en-v1.5 fp32 normalize=True（v2.2/2.3/2.4/2.4.1 同模型同精度）。
- 禁写目录：plans/rag_fix_20260928、plans/rag_fix2_v25_20260928、plans/obligrun_20260928；
  kb/、mcp_server/、evalset/ 只读（唯一例外=EYEKB_DB_POINTER.yaml 追加式 v2.4.2 块，沿 RA2 先例=任务书 §4 明令）。

## R2 入库构建（v2.4.2）
- v2.4.2_2026-09（新建，/mnt/D/OcularKB/ocularkb/rag/literature_db/）= v2.4.1 全量继承零重算
  （231,707 chunks 文本/向量/列逐字节原样，pd.concat 继承段）+ RA3 准入增量 chunks（CPU 现算）。
- chunker = stage2a_parse_xml_v2 + stage2b_chunk_v2 纯函数零改动（ra3_parse_chunk.py 逐行同构 ra2_parse_chunk.py，
  axes=["RA3-TIERA"] 中间字段不入 parquet）。
- 新 paper_id ∩ v2.4.1 paper_id = ∅ 断言（merge 落码）。
- v2.4/v2.4.1 目录字节零改动（SHA_PRE→SHA_POST 复核）。
- papers.jsonl：继承段 n_chunks 刷新沿 ra2_merge 口径；增量 admission_lane=ragfix3_backup104_scan。

## R3 门①（黄金 41 off 态全等）
- runner=克隆 gate1_golden41_offstate_v25.py（判据逐字：strip_sidecar MCP-vs-direct，direct 侧 db_dir=v2.0_2026-09，
  SUITE_SUPERSESSION 现行权威口径）；n_consistent==41 → PASS；任何翻转=停车回滚。
- 附加判据（任务书明令）：top-5 PMID 逐字对 out/GOLDEN41_OFFSTATE_ragfix2.json 基线零漂移（diff=0）。
- 接线契约 9 项如实记录；all_list_plus10 若仍为"绝对计数半句失效"形态→沿 REVIEWER_LLM Q5 两分句复证先例
  （超集关系 ∧ retina_interneuron::10 计数），免责形态非本卡，逐字记录不擅改期望值。

## R4 门②（严格 retina gate，v2.4.2 语料）
- 判据逐字=gate2_retina_v241.py（qa_v21 golden 段）：10 用例 no_degrade =
  (v242_retina_hits >= v10_hits) ∨ (v242_all_hits >= v10_hits)；用例级 ≥8/10 ∧ gate 级(hits≥3/5) 10/10 → PASS。
- 停车线：用例级 <8/10 → FAIL_STOP 落卡上报，不回调判据。
- v10 hits 基线取 qa_v2.json golden_regression 不重算（逐字一致保证）。

## R5 门③（覆盖复算，球门零移动）
- 判据逐字=gate3_coverage_v25.py：分母 92（tier_FINAL tier==A 单元），阈值 80%，
  消除 = gene 符号词边界 token ∈ 任一新论文 chunk 文本（regex 逐字同源），
  或 row cited_pmids ∩ closed 集 ∧ 该文 n_chunks>0（nch 读 v2.4.2 papers.jsonl）。
- 新增论文面 = closed64 ∪ RA2_17 ∪ RA3 准入 PMID 集（单调扩面）。
- 证据有效性复核断言：chunks_ra_raw.jsonl sha==43d02db66b9a3f235ff4f1b5beaafbc9ba5338aef53a4e26896649ff66a10196；
  chunks_ra2_raw.jsonl sha==ab941a8ae3b00b29bc80bbdd359e6dad70b0d7a0eaa1122a9f0d6b3ab9962a53；
  两者任一漂移=停车。
- 单调性断言：v2.4.1 已消除 78 单元（=92 − GATE3_residual_units_v25.tsv 14 单元）全部仍消除，
  违反=停车。RA3 新兑现单元逐一列 provenance（兑现论文 PMID + 该论文相关性/物种注记，副产品如实单列
  沿 CPNE5 先例；弱相关兑现=羊/鱼等非眼语境论文 token 命中者，如实标注不隐瞒）。
- 结果 <80% 亦如实报 FAIL，残差转"诚实 none/设计缺口"清单；禁回调阈值/分母/判据。

## R6 指针与收尾
- EYEKB_DB_POINTER.yaml 纯追加 v2.4.2 块（pre_sha=c7f2e0f7d583cfc56ce8bfb821b0517513e81316e416b55ecd0aa30d1f6e15c7，
  追加后 assert 前缀逐字节不变）；MCP/stage3 default=v2.0 未切；Release 六件零触碰。
- REPO_RESYNC3_REQUIRED.md sha 台账，本卡零 push。
- RAGFIX3_NOTE.md 逐条处置+残差归因+诚实登记；中间产物全保留。

## R7 预期与上限（非承诺）
理论上限 78+7=85/92=92.4%；兑现依赖 token 终裁实然（RA2 教训：T4"正文含 symbol"首选兑现率 4/5，
abstract-only 单元 SLC24A3/XCR1 已知归因不装）。不预设达标——按 R5 实然判。
