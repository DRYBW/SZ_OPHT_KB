# RAGFIX3_NOTE — 104 备选批处置 + v2.4.2 增量三门复算（PI 整链授权）

卡: t_b94d0999 ｜ 任务书: /mnt/D/EyeKB/plans/rag_fix3_20260928/BRIEF_RAGFIX3.md ｜
放行: USER_DIRECTIVE_20260928 追加五（PI: 除 >1GB 下载外自主推进）｜ 执行日: 2026-09-28 ｜
状态: **三门齐过——门③ 87/92=94.6% PASS（原分母/原阈值/原判据）+ 门① 41/41 off 全等且 top5 对 ragfix2 基线零漂移 + 门② 8/10 用例级+10/10 gate 级 PASS；7 目标单元兑现 6、C8ORF76 诚实 MISS；副产品新兑现 3（FAM135A/LILRB2/LMOD1）**

## 0. 一句话
对仅备选 104 覆盖的残差单元面做零 LLM 机械四检扫描（104 行→准入 103/拒 1），OA 配文入库
v2.4.2（v2.4.1 全量继承零重算 + 103 篇 11,221 chunks CPU 现算 embedding，19.33MB ≤ 100MB
波次预算，零清单外下载、零付费墙触碰、无 >1GB 拒收项），门③复算 78→87/92，球门零移动，
单调性核 v2.4.1 78 项零倒退；C8ORF76 两候选全文均在库但正文无词边界 token=诚实 MISS 维持残差。

## 1. 扫描账（判读矩阵预注册先于一切计算）
- 判读矩阵 = out/DECISION_MATRIX_RAGFIX3.md，**开算前 sha256 落纸** =
  b3787101187ceba27bdf9357662b6be501b0c6165e1d103015eb979982d80836（ledgers/SHA_DECISION_MATRIX.txt），
  R5 双证据 sha 预注册：chunks_ra_raw==43d02db6… ∧ chunks_ra2_raw==ab941a8a…（收尾复核均 TRUE）。
- 机械四检零 LLM（scripts/ra3_scan.py）：V1 EPMC EXT_ID 单篇回查+标题前缀逐字 ∧ V2 paper_id∪doi
  在库查重 ∧ V3 非 HRCA 自引∪撤证∪closed64∪RA2_17 防双计 ∧ V4 OA 实测（curl -sI HEAD；
  HEAD 无 Content-Length→体积由 GET 实测=预注册注记）。
- 结果: 104 → INTAKE_FULLTEXT 93 + INTAKE_ABS_ONLY 10 + REJECT 1（40171795=RA2 白名单成员，
  防双计）。V1 零拒（104 题录全可核）、V3 零自引命中（104 表组装时已避）、V2 仅 1 例。
- 通道账: EPMC 元数据 91 proxy/12 direct（PORT 优先、失败回退直连=预注册 R1 许可形态，逐条记账）。

## 2. 下载账
- scripts/ra3_fetch.py（同构 ra2_fetch.py）: 93/93 fullTextXML 全部成功，10 篇 abstract-only 入库
  （表内即 OA=N，沿 RA2 先例不绕墙），**累计 19,327,414 B = 19.33MB ≤ 100MB**，无 SKIPPED_CAP、
  无 >1GB 项；零清单外下载。逐 PMID 台账 work/ra3_availability.tsv（含物种人 52/both 13/鼠 15/其他 20/
  未定 3 如实透传——备选表含羊/鱼/蛙等物种混杂，RAGGAP 词族不严格已知形态，不装）。
- 排序=7 目标单元 14 候选在前（先保兑现面），其余 FULLTEXT 在后。

## 3. v2.4.2 构建账
| 项 | 值 |
|---|---|
| chunks | 242,928 = 231,707 (v2.4.1 原样继承零重算) + 11,221 (RA3 增量) |
| unique papers | 3,869 = 3,766 + 103（papers.jsonl 3,884 行=含历史 15 ghost 原样继承） |
| abstract-only | n_papers_fulltext_absent 245→257（+12 = 10 篇 OA=N + 2 篇 XML 正文段缺失：41193841[COL19A1 首选，Nature 文 XML 无 body sec]、42758005；另 PMC13587881 XML 不合规 lxml 报错→abstract-only fallback 如实记 ra3_parse.log） |
| embedding | bge-large-en-v1.5 cpu fp32 normalize=True（与 v2.2/2.3/2.4/2.4.1 增量同模型同精度；**全程禁 GPU 铁律遵守**，systemd-run MemoryMax=20G 隔离运行） |
| chunker | stage2a_parse_xml_v2 + stage2b_chunk_v2 零改动复用（manifest 注记） |
| lane | admission_lane=ragfix3_backup104_scan（机械四检闭集，非检索式准入非 eutils 裸回填） |
| 冻结面 | v2.0–v2.4.1 全部字节零改动（SHA_PRE→SHA_POST 复核 18/19 OK，唯一差异=指针本卡追加块） |
| 零交集断言 | RA3 paper_id ∩ v2.4.1 paper_id = ∅（ra3_merge 落码 assert 通过） |
| 产物 | /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/{chunks.parquet 1076.4MB, papers.jsonl, build_stats.json, manifest.yaml} |

## 4. 门③复算（核心判账，判据逐字未动）
- scripts/gate3_coverage_v3.py：分母 92、阈值 80%、
  text 词边界 token 路 ∨ chain cited∩闭集∧n_chunks>0 路，新增论文面=closed64∪RA2_17∪RA3_103（单调扩面）。
- 结果 **87/92 = 94.6% PASS**（行级 216/232 = 93.1%）。
- RA3 新兑现 9 单元（out/GATE3_new_elim_provenance_v3.tsv 逐单元 PMID 级 provenance）：
  - **目标 7 中 6**：COL19A1（次候选 42428548 兑现，首选 41193841 全文在库但 token 未现——
    "替补顶岗"形态再现）/ FAM107B（38003067+42074142 双候选+载体 34794440）/ SLC24A3
    （36614039+38731230 双候选，**前轮"必补 abstract-only 不可兑现"担忧被备选全文推翻**）/
    SSR4（双候选）/ XCR1（42330349+42724236 双候选+4 载体）/ ZNF804B（41014753 人视网膜空间
    转录组本尊候选兑现+羊文 34529728 等 3 载体）。
  - **副产品 3**（沿 CPNE5 先例如实单列，非本卡目标面）：FAM135A(retina)←41120831（104 表
    TMEM132C 行载体文）、LILRB2(retina)←40868918（LILRA4 行载体文；撤证设计缺口被无关文
    token 路"顺带消除"——**如实标注：此消除非配文意图兑现，kb7 词条 LILRB2 链误引勘误维持**）、
    LMOD1(face)←36207342（CPNE5 行载体文）。
- **C8ORF76(retina) 诚实 MISS**：两候选（37287642/30572641）均 FULLTEXT 入库，但正文词边界无
  "C8ORF76" token（basigin 文献用 BSG/basigin 命名系）→ 维持残差，不造数不放宽。
- 单调性断言 PASS：v2.4.1 已消除 78 单元全部仍消除；双证据 sha 复核 TRUE（43d02db6/ab941a8a）。
- 残差终态 5（out/GATE3_residual_units_v3.tsv）：C8ORF76（诚实 MISS）+ ATP8B4/FBXL7/LRRTM3/
  SHISA6（v2.4.1 六诚实 none 中未被副产品带出的 4 个——104 池对该 4 基因无覆盖，RAGGAP R3
  固有稀缺定性维持）。
- 弱相关如实标注：ZNF804B 兑现载体含羊群遗传学文（34529728）、FAM107B 载体含蛙螈演化文——
  token 路判据下有效，但"眼语境"由各自本尊候选（41014753/42074142）保证，混合载体不装看不见。

## 5. 回归三门全记录
| 门 | 判据 | 结果 |
|---|---|---|
| ① 黄金 41 off 态全等 | 克隆 ragfix2 runner，判据逐字（strip_sidecar MCP-vs-direct，direct 侧 db_dir=v2.0）+ 任务书明令 top5 逐字对 ragfix2 基线 | **41/41 PASS + top5 零漂移（diff=0）**；契约 8/9：all_list_plus10 FAIL=前两轮 REVIEWER_LLM 已裁"绝对计数半句过期"同形态（两分句复证本轮均 TRUE：超集关系 ∧ retina_interneuron::10 计数=10，JSON 内 wiring_contract_plus10_clauses 留证），**非本卡**（本卡 kb/markers 零触碰）out/GOLDEN41_OFFSTATE_ragfix3.{json,md} |
| ② 严格 retina gate | 判据逐字=qa_v21 golden 段克隆，v2.4.2 语料 242,928 chunks，停车线<8/10 | **PASS：8/10 用例级不劣化 + 10/10 gate 级**；劣化点同 RPE/Astrocyte=v2.1/v2.4/v2.4.1 既有形态（逐细胞型 hits 与 v2.4.1 轮完全一致=零新增劣化）out/GATE2_RETINA_v242.json |
| ③ A 档 92 覆盖复算 | 原分母 92/原阈值 80%/原判据逐字，≥ 基线 78 单调性 | **87/92=94.6% PASS**（§4） |

## 6. 红线遵守与仓同步
- v2.0–v2.4.1 库、kb/markers 面板核心、mcp_server、evals/、plans/rag_fix_20260928、
  plans/rag_fix2_v25_20260928、plans/obligrun_20260928（OBLIGRUN 在跑）：全程零写入
  （收尾 sha256sum -c 复核 18/19 OK，唯一差异=本卡指针追加块，前缀逐字节断言通过）。
- 下载 19.33MB ≤ 100MB；任何 >1GB 项无=不收条款未触发；零付费墙；零清单外下载；零 LLM 判读。
- **禁 GPU 全程遵守**：merge/gates 均 CPU（bge fp32 device="cpu"），systemd-run MemoryMax 隔离；
  本卡未持 GPU 租约、未触碰 5090 与 llama-qwen* 单元（执行期间 llama-qwen.service 处
  ExecCondition 拦停态=他方/仲裁器行为，与本卡无关，未干预）。
- MCP/stage3 default=v2.0 未切；Release 六件零触碰；WIKI 六件套未整刷（留痕=指针块+本登记件）。
- **⚠ 仓需重同步（登记，本卡零 push）**：见 REPO_RESYNC3_REQUIRED.md——本卡动 kb 面=
  EYEKB_DB_POINTER.yaml v2.4.2 块追加（pre c7f2e0f7… → final a9072609…）；v2.4.2 库属
  OcularKB 侧冻结库不在 EyeKB 仓。

## 7. 建议后续（不自动执行，交 PI/协调者）
1. **门③终态定格 94.6%**：残差 5 = C8ORF76（token 命名系问题，出路=别名表 BSG/basigin 入判据
   需动球门=另案裁决）+ 4 诚实 none（104 池无覆盖，真缺文献定性维持）。
2. **v2.4.2 激活排期**：default 仍 v2.0 未切（沿先例待拍板）；指针已注册 latest-ragfix3。
3. LILRB2 副产品消除的语义边界已在 §4 标注——若文章叙事需"该单元已配文"，建议表述为
   "无关语境 token 命中"而非"配文兑现"，避免过度声明。
4. RA3 池含 3 例物种 unknown/20 例 other（羊/鱼/蛙/果蝇等）——若 C 档旁挂/生产激活后
   检索质量审计需要，可加"非人/非鼠论文降权"另案（本卡判据不含此逻辑，未擅动）。

## 8. 产物索引（前缀 /mnt/D/EyeKB/plans/rag_fix3_20260928/）
| 件 | 路径 |
|---|---|
| 判读矩阵(预注册) | out/DECISION_MATRIX_RAGFIX3.md + ledgers/SHA_DECISION_MATRIX.txt |
| 扫描台账/闭集 | work/ra3_scan_ledger.tsv + out/closed_set_ra3_{pmids.txt,intake.tsv} + out/RA3_SCAN_SUMMARY.json |
| 下载台账 | work/ra3_availability.tsv + work/ra3_bytes.json + work/xml3/（93 XML 全保留） |
| chunks 中间件 | work/chunks_ra3_raw.jsonl（11,221 行）+ work/ra3_{ftstatus.json,chunks_per_paper.json} |
| 门结果 | out/{GOLDEN41_OFFSTATE_ragfix3.json,.md, GATE2_RETINA_v242.json, GATE3_COVERAGE_v3.json, GATE3_residual_units_v3.tsv, GATE3_new_elim_provenance_v3.tsv} |
| sha 台账 | ledgers/{SHA_PRE_inputs_20260928.txt, SHA_POST_verify_20260928.txt, SHA_DELIVERABLES_20260928.txt} |
| 仓登记 | REPO_RESYNC3_REQUIRED.md |
| 脚本 | scripts/{ra3_scan,ra3_fetch,ra3_parse_chunk,ra3_merge,gate1_golden41_offstate_v3,gate2_retina_v242,gate3_coverage_v3,pointer_register3}.py |
