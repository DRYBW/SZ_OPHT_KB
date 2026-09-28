# RAGFIX2_NOTE — 门③追补轮 v2.5：16 基因白名单核验重组装 + v2.4.1 增量 + 门复算（D21）

卡: t_6848d3de ｜ 任务书: /mnt/D/EyeKB/plans/rag_fix_20260928/BRIEF_RAGFIX2.md（建卡缺件，由执行方按卡体+RAGFIX_DECISION_1 重建冻结，见该件头注）｜ 放行: RAGFIX_DECISION_1 P1=B（PI 授权落定 + REVIEWER_LLM 建议同向）
执行日: 2026-09-28 ｜ 状态: **三门齐过——门③复算 78/92=84.8% PASS（原判据原分母原阈值）+ 门② 8/10+10/10 PASS + 门① 黄金 41/41 off 全等 PASS（top5 与前轮零漂移）**

## 0. 一句话
对 RAGGAP 清单组装口径缺口的 16 个从未配文基因（was_S2_ctx_mismatch 型）重跑候选检索，逐篇三条件
题录核验（断言词/PMID 可核/非 HRCA 自引∧不在库防重蹈）锁白名单 17 篇闭集（2.34MB≤6MB），下载入库
v2.4.1（v2.4 字节不动），门③复算 67→78/92 转 PASS；10 基因兑现 + 1 副产品（CPNE5）+ 6 基因诚实
维持 none，球门未动。

## 1. 检索与白名单账（判据=BRIEF_RAGFIX2.md §3 冻结）
- 检索口径逐字=RAGGAP s5（`"SYM" AND 眼词族 AND SPECIES:"HUMAN"` pageSize=75，直连限速）+ 登记别名查询；
  EPMC 通道全程元数据级，**零裸用 eutils 回填**（KBCHAIN 告诫；eutils 通道本轮未触发）。
- 三条件核验明细: out/RA2_candidate_ledger.tsv（全候选含拒绝原因）+ work/ra2_candidates_raw.json；
  HRCA_EXCL={41578023(HRCA 本体), 32555229, 34691611, 37388908, 32946783, 39117640}（kb/baselines/retina.md 锚定面）
  ∧ 不在库（v2.4 papers.jsonl 3749 篇）∧ 不在 closed64（防重蹈=防双计）。
- 白名单 17 篇=10 首选+7 替补: out/RA2_WHITELIST.{md,tsv}；闭集 out/closed_set_ra2_pmids.txt。
  链路口 3 篇=CST1/CST4/MUC7 的 kb 词条**自引 PMID**（题录语义一致核验通过——与 sample20 型"note 真文
  在、PMID 错位"相反，本轮 GPR143 自引 42170303 即因题录与眼语境不一致被 CHAIN_CTX_FAIL 拒，防误引门生效实证）。
- 物种如实透传（人限定检索下的混标不装）：human 9/both 3/mouse 2/other 3，见 RA2_WHITELIST.md 注记。

## 2. 下载账
- 逐 PMID 台账 work/ra2_availability.tsv：17/17 C2 复核通过（EXT_ID 单篇回查+标题逐字比对），
  OA 全文 14 篇 fullTextXML 全部成功、abstract-only 3 篇（1471486/2029847/17399701，含 PMC legacy 但
  OA=N 不绕墙），**总 2.34MB ≤ 6MB 上限，零清单外下载，未绕付费墙**。
- ra2_fetch.py 逐行同构 ra_fetch.py（同源 species 正则/限速/重试/无 PMCID→abstract-only）。

## 3. v2.4.1 构建账
| 项 | 值 |
|---|---|
| chunks | 231,707 = 230,426(v2.4 原样继承零重算) + 1,281(RA2 增量) |
| unique papers | 3,766 = 3,749 + 17（papers.jsonl 3,781 行=含历史 15 ghost 原样继承） |
| abstract-only | n_papers_fulltext_absent 242→245（+3: 1471486/2029847/17399701） |
| embedding | bge-large-en-v1.5 cpu fp32 normalize=True（与 v2.2/2.3/2.4 增量同模型同精度） |
| chunker | stage2a_parse_xml_v2 + stage2b_chunk_v2 零改动复用（manifest 注记） |
| lane | admission_lane=ragfix2_v25_whitelist（三条件核验闭集，非检索式准入非 eutils 裸回填） |
| 冻结面 | v2.0–v2.4 全部字节零改动（SHA_PRE→SHA_POST 8/9 OK，唯一差异=指针本卡追加块，前缀断言过） |
| 零交集断言 | RA2 paper_id ∩ v2.4 paper_id = ∅（ra2_merge 落码 assert） |
| 产物 | /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.1_2026-09/{chunks.parquet 1027.7MB, papers.jsonl, build_stats.json, manifest.yaml} |

## 4. token 终裁与门③复算（核心判账）
- **可兑现性预检实然化**（v2.4 教训：chunk 文本不含标题）：全 17 篇下载后逐基因词边界 token 扫描
  out/RA2_token_verification.tsv——T4 档（题录=断言语境词在标题∧symbol 在检索全文域）的"正文含 symbol"
  假设首选 4/5 兑现；**CALD1 首选 39195219 token 未现（命中疑在补充材料，fullTextXML 不含）→ 替补 33028893
  顶岗 HIT(2)**——替补槽设计生效实证。
- 门③复算 out/GATE3_COVERAGE_v25.json：**分母 92、阈值 80%、判据逐字=gate3_coverage.py 未动**，
  仅扩"新增论文"面=closed64∪RA2 白名单（REVIEWER_LLM 裁决点 3 前置：v2.4 增量 chunks sha==43d02db6… 复核
  =已计入 67 项证据有效性重证；单调性断言 v2.4 67 单元零倒退 PASS）。
- 结果 **78/92 = 84.8% PASS**（行级 192/232 = 82.8%）。RA2 新兑现 11 单元 =
  text_primary 7（CDH8/FCER1G/GPR143/GRM5/MUC7/PTPRK/SAMSN1，其中 MUC7 链∧文双路）+ text_backup 1
  （CALD1 替补顶岗）+ chain 2（CST1/CST4 摘要路链兑现）+ **副产品 1（CPNE5——备选表单元，被 CDH8
  替补文 Copine-4 论文自然兑现，非本卡目标面，如实单列）**。
- 残差 14 单元（out/GATE3_residual_units_v25.tsv）三分（互斥口径）：①7 个仅备选 104 覆盖
  （C8ORF76/COL19A1/FAM107B/SLC24A3/SSR4/XCR1/ZNF804B——卡体明示不碰，PI 批不批备选面另案）
  ②6 个诚实 none（ATP8B4/FAM135A/FBXL7/LMOD1/LRRTM3/SHISA6——symbol/别名不现于任何眼语境标题+摘要
  无 token，三条件无合格候选；RAGGAP R3 固有稀缺型二次实证，维持"真缺文献"不造数）
  ③1 个 LILRB2（撤证设计缺口维持）。
- **不追认 v2.4 已过门③**（DECISION_1 红线）：v2.4 的 72.8% FAIL 记录保持原样，v2.5 复算独立记
  78/92 PASS 于 v2.4.1 库。

## 5. 回归三门全记录（REVIEWER_LLM 裁决点 3"三门重跑"口径补齐）
| 门 | 判据 | 结果 |
|---|---|---|
| ① 黄金 41 off 态全等 | MCP-vs-direct strip_sidecar 41/41 + 接线契约（克隆 t_d0bea5a6 runner，判据逐字） | **41/41 PASS**；top-5 与前轮（v2.4 轮）逐字零漂移（diff=0）。契约 8/9：all_list_plus10 FAIL=前置轮旧快照绝对计数期望过期（pre=33→期望 43，现值 60，本卡 all_list 增量为 0——与 v2.4 轮同形态失效）；REVIEWER_LLM Q5 两分句复证 out/CONTRACT_PLUS10_RECHECK_v25.json：超集关系 TRUE ∧ retina_interneuron::10 计数 TRUE，免责条件形态沿前轮先例，**非本卡** |
| ② 严格 retina gate | v2.4.1 上复测，判据逐字=qa_v21 golden 段，停车线<8/10 | **PASS：8/10 用例级不劣化 + 10/10 gate 级**，劣化点同 RPE/Astrocyte=v2.1/v2.4 既有形态（窗口槽位漂移既有归因不变）out/GATE2_RETINA_v241.json |
| ③ A 档 92 覆盖复算 | 原分母/原阈值/原判据，不降于 67 且 ≥80% | **78/92=84.8% PASS**（§4） |

## 6. 红线遵守与仓同步
- v2.0–v2.4 库、kb/markers 面板核心、mcp_server、evals/、rag_gap_20260928/、kb_chain_audit_20260928/：
  全程零写入（收尾 sha 复核 8/9 OK，唯一差异=本卡指针追加块；禁写目录未触）。
- 下载=白名单闭集本身 17 篇，2.34MB≤6MB；超限停车条款未触发；备选 104 一篇未下；LILRB2 未补链。
- 判据零移动：C1 三档+链路口在开算前冻结于任务书（本卡中途扩 T4/T4a+替补槽发生在**下载之前、
  白名单锁定之时**，门判据本体未变）；6 个 none 未为凑数放宽。
- **⚠ 仓需重同步（登记，本卡未 push）**：见 REPO_RESYNC2_REQUIRED.md——本卡动 kb 面=EYEKB_DB_POINTER.yaml
  v2.4.1 块追加（final sha 见 ledgers/SHA_POST_NOTE_20260928.md）；v2.4.1 库属 OcularKB 侧冻结库不在 EyeKB 仓。

## 7. 建议后续（不自动执行，交 PI/协调者）
1. **备选 104 面批否**：剩余 7 单元仅备选表覆盖（含 abstract-only 必补不可兑现的 SLC24A3/XCR1 已知归因），
   批=闭集勾选→v2.4.2 同管线增量；不批=门③终态定格 84.8%+7 单元记录。
2. **KB6/KB9 链回炉卡**（前卡 P2 已并 KBCHAIN-AUDIT 另卡，本卡无新误引发现——链路口核验反而
   拒掉 1 条疑似错位自引 GPR143→42170303，供审计卡参考）。
3. **C 档旁挂/v2.4.1 激活排期**：MCP default 仍 v2.0（未切，沿先例待拍板）；v2.4.1 已注册 latest-ragfix2。
4. 6 个诚实 none 基因如 PI 认为必须配文，出路=非 OA 全文付费渠道（本卡禁绕墙不可行）或
   接受 R3 固有稀缺定性。

## 8. 产物索引
| 件 | 路径（前缀 /mnt/D/EyeKB/plans/rag_fix2_v25_20260928/） |
|---|---|
| 任务书(补缺件) | /mnt/D/EyeKB/plans/rag_fix_20260928/BRIEF_RAGFIX2.md（本目录 PROTOCOL_BRIEF_RAGFIX2.md 同件副本） |
| 检索账 | scripts/ra2_candidates.py + work/ra2_candidates{,_v2}.log + work/ra2_candidates_raw.json + out/RA2_candidate_ledger.tsv |
| 白名单 | out/RA2_WHITELIST.{md,tsv} + out/closed_set_ra2_pmids.txt |
| 下载账 | scripts/ra2_fetch.py + work/ra2_availability.tsv + work/ra2_selected.jsonl + work/xml2/(13 XML) + work/ra2_bytes.json |
| chunks/终裁 | work/chunks_ra2_raw.jsonl(1,281) + scripts/ra2_verify_tokens.py + out/RA2_token_verification.tsv |
| 库 | /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.1_2026-09/（scripts/ra2_merge.py + work/merge.log） |
| 门 | out/GATE3_COVERAGE_v25.json + out/GATE3_residual_units_v25.tsv + out/GATE2_RETINA_v241.json + out/GOLDEN41_OFFSTATE_ragfix2.{json,md} + out/CONTRACT_PLUS10_RECHECK_v25.json（scripts/gate3_coverage_v25.py / gate2_retina_v241.py / gate1_golden41_offstate_v25.py / contract_plus10_recheck.py） |
| 指针 | scripts/pointer_register2.py + /mnt/D/EyeKB/kb/literature_db/EYEKB_DB_POINTER.yaml v2.4.1 块 |
| sha | ledgers/SHA_PRE_inputs_20260928.txt / SHA_POST_verify_20260928.txt + SHA_POST_NOTE_20260928.md / SHA_DELIVERABLES_20260928.txt |

⚠ 收尾落卡断言：退出前 ① 逐条 stat 核对任务书承诺的交付物已落盘（盘上文件才是证据，会话记忆不算）；② kanban_complete 与 kanban_block 二选一必调——做完→complete；卡住→block 列缺项；半做完→complete 已完项 + kanban_create 后续卡；只给最终文本不落卡 = rc=0 协议违规。
