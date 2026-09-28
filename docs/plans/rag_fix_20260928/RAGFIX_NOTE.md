# RAGFIX_NOTE — RAG 补文献执行（A档65篇 v2.4 增量 + C档索引旁挂 + LILRB2 误引修复，D19）

卡: t_d0bea5a6 ｜ 任务书: 本目录 BRIEF_RAGFIX.md ｜ 放行: USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加二 D19
执行日: 2026-09-27/28 ｜ 状态: **交付物全部落盘 + 门①② PASS + 门③ 72.8%<80% FAIL；外部裁定（REVIEWER_LLM）=整体验收 FAIL、建议选项 B；卡已 block 待 PI 拍板**

## 0. 一句话
RAGGAP 报批清单"必补"表 65 行 = 64 篇闭集全部入库（1 行 ⛔=LILRB2 误引 PMID 不入库走勘误件），
建成 v2.4_2026-09（v2.3 全量继承零重算 + 9,772 新 chunks），C 档 830 行两路径旁挂完成，
LILRB2 撤证 + 抽 20 既有链复核（**6/20 确诊误引**，只登记未扩修），回归三门①②过、③未过且根因清楚。

## 1. 下载账（逐 PMID 台账 = work/ra_availability.tsv）
- 闭集 = out/closed_set_pmids.txt（64 PMID，与 TIER_A_approval_list.md 必补表 ☐ 行一一对应；⛔41349939 排除）
- 全部走 EPMC 元数据+fullTextXML；OA 全文成功 **55 篇**；abstract-only **9 篇**
  （3 篇无 PMCID：16395610/26173177/42777860；6 篇 fullTextXML 持续 HTTP 500 两次重试+预检均拒：
  33929509/38914302/41026912/41853890/42173563/42508771——题录在、正文不可得，未绕付费墙）
- 总下载体积 **13.9 MB**（预算 ≤85MB 的 16%；>1GB 免批条款远未触发，且 D19 已批）
- 特例 42777860（KB8 LACRT 链）：EPMC 于执行日已收录 MED 题录（RAGGAP 09-27 时点未收录），
  按管线规则 abstract-only 入库；通道注记登记于勘误件 channel_notes。
- 备选 104 篇：本轮未下（任务书红线），清单留账（out/GATE3_FOLLOWUP_candidate_table.md 另附残差追加候选）。

## 2. v2.4 构建账
| 项 | 值 |
|---|---|
| chunks | 230,426 = 220,654(v2.3 原样继承) + 9,772(RA 增量) |
| unique papers | 3,749 = 3,685 + 64 |
| papers.jsonl 行 | 3,764（含历史 15 个 0-chunk ghost，自 v2.3 原样继承） |
| abstract-only | n_papers_fulltext_absent 233→242（+9=本增量 abstract-only 数，逐篇 fulltext_status 登记） |
| embedding | bge-large-en-v1.5 cpu fp32 normalize=True（与 v2.2/v2.3 增量同模型同精度） |
| chunker | stage2a_parse_xml_v2 + stage2b_chunk_v2 零改动复用（口径与现役一致，manifest chunker_provenance 注记） |
| lane | admission_lane=raggap_tier_a_eyekb（非检索式准入，PI 勾选闭集） |
| 冻结面 | v2.0-2.3 全部字节零改动（ledgers/SHA_PRE→SHA_POST ALL MATCH）；evalset/mcp_server 未触 |
| 产物 | /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09/{chunks.parquet(1022.2MB), papers.jsonl, build_stats.json, manifest.yaml} |

## 3. 索引账（C 档 830 行两路径旁挂，零重建零改正文）
- **路径1 链回填**：kb/markers/_raggap_c_linkbackfill_v1.json（INERT 默认 OFF，下划线前缀不入
  MARKER_LIBS/加载 glob，仿 k9 overlay 先例）。830 行逐行带候选库内 PMID + 在库状态核验
  （strong 610/mid 220；全部行 ≥1 候选可证 in_corpus）。应用规则写入件内，激活另需 PI 批。
  行级明细=out/C_path1_rows_detail.tsv。
- **路径2 面板字段扩展**：不动 panels_v5.json/v2.4 parquet；输出 chunk 级扩展共现旁挂表
  out/C_path2_panel_expansion.tsv（row_idx→extra_genes，402 词条基因 × 230,426 chunks
  词边界扫描）+ 汇总 out/C_path2_summary.json。实测：13,225 chunk 获得扩展共现；
  402 词条基因=353 个有面板外扩展共现 + 40 个本就是 QA 面板基因（定义上不计 extra）
  + 9 个零共现（C8ORF76/COL19A1/CPNE5/CYTH4/LILRB2/MFSD4A/SCGB1D1/SSR4/ZNF804B）
  ——其中 CYTH4/MFSD4A 即 B 档固有稀缺基因（互证），SCGB1D1/LILRB2 属泪腺/撤证线，
  其余为门③残差同源基因。
- 附属器语境（TIER_C 第3条）：泪腺 7 行属 A 档问题，本轮已随闭集下载入库 3 篇泪腺文献
  （16395610/26173177/42777860 abstract-only + SCGB2A1 等），残差见 §5。

## 4. 勘误账（kb 侧=旁挂勘误件，面板核心字节零改动）
- **LILRB2 撤证**：kb/markers/_raggap_errata_v1.json（INERT）。PMID:41349939 经 EPMC 逐字复核
  = "Urinary exosomes...urinary tract infection"（Clinica chimica acta），与视网膜 MG 语境无关，
  自 retina_v6/microglia_repair LILRB2 链撤证；原件 .bak + 双 sha 台账（ledgers/SHA_ERRATA_double.txt，
  recheck sha==PRE）。不自动补链（候选替代待 KB6 线复核）。
- **抽 20 既有链复核**（seed=20260928 预注册，总体 55 实例）：
  - 机械档：CONSISTENT 9 / UNCLEAR 1 / MISMATCH 10；
  - 人工升级判读（题录+摘要实读）：**CONFIRMED_MISQUOTE 6（30%）**+ SUSPECT 1（无摘要 letter，
    题录级不可判）+ CONTEXT_OK 1 + CONSISTENT 11 + UNCLEAR 1。
  - **系统性模式**：4/6 确诊链的 note 本身描述着一篇真实存在的眼科文献（如"人穹窿部结膜干细胞富集区"），
    但 PMID 指向完全无关论文（乳腺癌真实世界研究/SIADH 药物警戒/法医亲缘算法…）
    = KB6/KB9 时代 eutils 共现建链通道的 **PMID 错位**，非凭空捏造。
  - 找回候选：KRT19→PMID:25722207 高可信候选（题逐字匹配 note 描述）；AQP5/OR51E2/SCGB3A1 未找回。
  - 6+1 条误引链全量登记（文件+json path+gene+实际题录），**未修**（任务书红线=只登记不扩范围修）。
- 新误引率结论：既有链误引不是孤例（LILRB2 型），抽样 30% 确诊 → KB6/KB9 建链通道的
  "eutils 共现即链"步骤需要系统性回炉（建议另卡，见 §7）。

## 5. 回归三门（预注册判据逐字执行）
| 门 | 判据 | 结果 |
|---|---|---|
| ① 黄金 41/41 off 全等 | MCP-vs-direct 41 用例 strip_sidecar 全等 | **41/41 PASS**；top-5 PMID 与冻结 20260924 版逐字全等（0 漂移）。克隆 runner 附带的 9 项接线契约中 all_list_plus10 FAIL=09-24 版快照期望过期（其后 KB8 泪腺+KB9 k9 等合法注册使 all_list 33→60），本卡写集不在服务端读集内（sha 台账佐证）。补验（REVIEWER_LLM Q5 要求）：契约两分句分别核——超集关系 set(pre)⊆current TRUE、retina_interneuron::10 行为关系 TRUE，仅绝对计数期望 43 过期（现 60）|
| ② 严格 retina gate | 不低于是 v2.1 基线 8/10（退化=停车） | **PASS：8/10 用例级不劣化 + 10/10 gate 级**，与 v2.1 完全同形态（劣化点同为 RPE 4/4、Astrocyte 4/4，= 池扩大后 top-100 窗口槽位漂移，QA_V21 既有归因不变） |
| ③ A 档 92 基因覆盖消除 | ≥80% | **FAIL：67/92 = 72.8%**（行级 168/232 = 72.4%）。残差 25 单元归因：①**16 个**是 was_S2_ctx_mismatch 型（RAGGAP 把它们按语境判据重裁入 A，但"必补表每基因保 1 篇"的配文只覆盖了原始 S3 基因集，**这 16 基因从未在报批清单任何一行挂过候选论文**=清单组装口径缺口）②8 个仅备选 104 覆盖（任务书不下）③1 个=LILRB2（撤证设计，诚实留空）。逐单元明细=out/GATE3_residual_units.tsv；16 基因的追加候选（含 EPMC 眼命中数与 OA 状态）=out/GATE3_FOLLOWUP_candidate_table.md |
- 门③判据未达不是语料质量问题，残差 25 单元的根因三分（互斥口径）：
  ①**16 个**=RAGGAP 必补表从未给这些基因配过候选论文（语境错配重裁型基因，清单组装口径缺口）；
  ②**8 个**=仅备选 104 覆盖（任务书不下），其中 SLC24A3/XCR1 两单元的必补论文恰是 abstract-only
  （41026912/42173563，OA=N），摘要不含符号 → R2 全文级收益在摘要级入库下不可兑现（备选第二篇均 OA=Y 可补）；
  ③**1 个**=LILRB2（撤证设计，诚实留空）。
  全文级(OA=Y)必补论文所配单元 18/18 兑现；未兑现的 2 单元（SLC24A3/XCR1）均为 abstract-only 必补篇。
- 追加轮预估：16 基因×top 候选（多为 OA=Y 全文，估 ~10-15 篇 ≤5MB）+ 已含备选 8 单元勾 1-2 篇
  → 消除率可达 ~90%+；**需 PI 批新闭集**（本卡红线：清单外一篇不下）。

## 6. 红线遵守与仓同步
- v2.1/2.2/2.3 库、kb 面板核心、mcp_server、在跑六卡目录：全程只读，收尾 sha 复核 ALL MATCH（§2）。
- 下载仅限闭集 64 篇；13.9MB 在 D19 已批 ≤85MB 内；未绕任何付费墙（6 篇 500 拒取按 abstract-only 入账）。
- 分批落盘：work/（原始件+台账）+ out/（门结果+旁挂明细）+ ledgers/（三段 sha）+ kb/（2 个 INERT 旁挂件）+ 指针追加。
- **⚠ 仓需重同步（登记，本卡未 push）**：本卡动了 kb/ 面——新增 kb/markers/_raggap_errata_v1.json、
  kb/markers/_raggap_c_linkbackfill_v1.json，EYEKB_DB_POINTER.yaml 追加 v2.4 块（前缀逐字不变校验通过）。
  由协调者按 REPOSYNC 管线（exec6 镜像+脱敏扫描）择机重同步；另 ocularkb/rag/literature_db/v2.4_2026-09
  属 OcularKB 侧冻结库（不在 EyeKB 仓），rag_snapshots 面是否收 v2.4 由同步执行卡裁定。
- 交付件 sha 台账：ledgers/SHA_DELIVERABLES_20260928.txt；全链脚本 scripts/ra_fetch.py → ra_parse_chunk.py
  → ra_merge.py → gate1/2/3 → c_sidecar.py → errata_lilrb2.py → sample20 → pointer_register（可重跑，判据在码）。

## 7. 建议后续（不自动执行，交 PI/协调者）
1. **门③裁定**：批准 16+8 单元追加闭集（候选表 §5 / out/GATE3_FOLLOWUP_candidate_table.md，≤~5MB 量级）
   → 另卡 v2.5 增量；或接受 72.8% 并显式记录口径收窄。
2. **KB6/KB9 链回炉卡**：抽 20 已证 30% 误引率 → 建议全量复核两代增量文件的全部 55 条 pmid 链
   （population 已知，工作量=题录级逐条+note 语义对账；KRT19→25722207 找回先例表明多数可救）。
3. **C 档旁挂件激活**：链回填+面板扩展均为 INERT，激活前义务 run（评测/判读消费方按路径读）待 PI 排期。
4. MCP default 切库（v2.0→v2.4）沿 v2.2/v2.3 先例：本卡未动，待用户拍板。

## 8. 产物索引
| 件 | 路径 |
|---|---|
| v2.4 库 | /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4_2026-09/ |
| 下载台账 | work/ra_availability.tsv（64 行）+ work/xml/（55 XML）+ work/ra_fetch.log |
| 增量 chunks | work/chunks_ra_raw.jsonl（9,772）+ ra_chunks_per_paper.json + ra_ftstatus.json |
| C 旁挂 | kb/markers/_raggap_c_linkbackfill_v1.json + out/C_path1_rows_detail.tsv + out/C_path2_panel_expansion.tsv(+summary.json) |
| 勘误 | kb/markers/_raggap_errata_v1.json + out/PMID_CHAIN_SAMPLE20_FINAL_ADJUDICATION.json + work/markers_v6_retina_repair.json.bak_pre_ragfix |
| 门 | out/GOLDEN41_OFFSTATE_ragfix.{json,md} + out/GATE2_RETINA_v24.json + out/GATE3_COVERAGE_v24.json + out/GATE3_residual_units.tsv + out/GATE3_FOLLOWUP_candidate_table.{md,json} |
| sha | ledgers/SHA_PRE_inputs_20260928.txt / SHA_POST_verify_20260928.txt / SHA_ERRATA_double.txt / SHA_DELIVERABLES_20260928.txt |
| 指针 | kb/literature_db/EYEKB_DB_POINTER.yaml（v2.4 块追加，default=v2.0 未动） |

## 9. 裁定记录（2026-09-28，外部独立裁决）
- 送审：out/PROMPT_GATE3_ADJUDICATION.md → LLM_CHANNEL REVIEWER_LLM（thinking=xhigh，156s），回函归档
  out/REVIEWER_LLMGATE3_ADJUDICATION_reply.md。**总判定：FAIL（卡级整体验收）+ 建议选项 B。**
- REVIEWER_LLM 要点（全部采纳入收口口径）：
  1. 门③ FAIL 主因=上游清单与覆盖目标错配，但"闭集内不可达"**不作断言**——本卡未逐一排除
     同篇可获取全文未取得/解析遗漏/规则漏检（别名匹配未做），故不写"已证明不可达"；
  2. 80% 线、92 单元分母、事前判据**保持不动**（判据不移动=合规）；语境核验增强（防"提及≠支持"）
     留给 v2.5 预注册，不属事后改门；
  3. 追加授权=**逐篇题录-PMID 核验后的白名单**（非"top 候选 ~20 篇"粗边界），锁定目标单元/获取形态/
     篇数/≤6MB 上限，超限或替换重新报批；v2.5 用原分母阈值重跑三门并复核已计入 67 项证据有效性；
     **追加获批不追认 v2.4 已过门③**；获批前 v2.4 按 A 态暂存（frozen read-only，已注册指针未激活）；
  4. Q4 补验（本卡实跑，scripts/REVIEWER_LLMfollowup_probes.py）：7 条确诊/存疑误引 PMID 与门①41 用例
     top-5 交集=∅、与闭集交集=∅ → 门①②③结论不受旧误引链污染；旧链作为 kb 词条面的下游风险
     已由勘误件 sample20_findings 全量登记（追踪义务转 KB6/KB9 回炉卡）；
  5. Q5 补验：all_list_plus10 失效仅绝对计数半句（超集关系+retina_interneuron::10 两半句均 TRUE），
     "契约过期=非本卡"免责成立为条件形态；契约 8/9 失败记录如实保留，另行修订归 t_d07ab64f 系套件维护。
- 交 PI 拍板项（本卡 block 事由）：
  **P1** 选项 A=接受 72.8% 为 D19 闭集终态（门③永久记 FAIL，后续另论）/ **选项 B=批准 v2.5 追加轮**
  （另卡先产逐篇核验白名单→你批→建 v2.5→原门重跑）——REVIEWER_LLM 与本卡均建议 B。
  **P2** KB6/KB9 证据链回炉卡立项（30% 确诊误引率，55 条总体全量题录级复核+错位找回）。
  **P3** C 档两旁挂件与 v2.4 激活排期（含义务 run，默认 OFF 态不变）。
