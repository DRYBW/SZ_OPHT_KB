# PRE_REG_kbchain v1.0 — KBCHAIN 全库引用链误引审计预注册（先落纸后执行）

卡: t_3a35a2cc ｜ 任务书: BRIEF_KBCHAIN.md ｜ 执行: AGENT_ROLE ｜ 日期: 2026-09-28
红线继承: 只写本目录；kb/、其余 plans 只读；零生产写；零 LLM 判读（判级=纯机械词面规则）；
网络=EPMC/eutils 题录级，零全文。

## 0. 链（chain）定义
链 = kb 断言层「词条(细胞类×基因)→文献(PMID 或可反解题名)」的引用链接实例。
实例(instance)级计数；同一 PMID 挂多个词条 = 多个实例（文献层去重仅用于取数省流）。

## 1. 总体框（population frame）
| 框 | 内容 | 处置 |
|---|---|---|
| F1 (S1) | KB6/KB9 建链期 evidence 链：kb/markers/markers_v6_retina_repair.json、markers_v6_face_increment.json、markers_v6_lacrimal_increment.json、markers_k9_ocs_increment.json 内 {type:pmid} 证据实例（与 RAGFIX 抽 20 同一定义，population=55，排除已撤证 41349939；另补 note 内嵌 PMID，见 §2 抽取规则 R3） | 全检 |
| F2 (S1) | E2R S5b 白名单 100 对（e2r_whitelist_S5b.json）：(lib::cls::gene)→resolved_pmid 题名反解链 | 全检 |
| F3 (S2) | 其余词条级历史链：markers_membrane_v1.json provenance pmid_context（626 实例/15 唯一 PMID，semantics=类级语境非逐基因引用）；markers_v5_retina_interneuron.json 与 F1 各文件的 note 内嵌 PMID（R3）；kb/priors/**、kb/baselines/**、kb/literature_db/KBADD_KERATOCYTE_NOTES_20260924.md 的 PMID 提及实例 | 全检（机械档）；15% 分层样本做预注册口径估计 |
| F4 (S2) | kb/vk_literature_index/*.md 题录索引条目（PMID+存储题名成对，~7,493 实例/2,740 唯一 PMID）——索引表面，单列报告，不与断言链混算 | 全检（机械档）；15% 分层样本做预注册口径估计 |
| 排除 | v5 非白名单 20 对（top_titles 全空，E2R 已定性"不可核"，无 PMID 可核）；_ 前缀 INERT 旁挂件（_raggap_errata/_raggap_c_linkbackfill/_k9_ocs_rules_overlay）；kb/literature_db/*.jsonl 语料准入面（RAG 库自身，非词条断言链，KB1v2/RAGFIX 已治理）；RAG v2.4 增量（RAGFIX 本轮已逐篇核验）；REVCAND_KB6_v2.tsv（候选基因清单本身无 PMID，其产出的链=F1） | 登记不入抽样框 |

## 2. 链抽取规则（机械，可重跑）
- R1 evidence 对象：dict 含 gene(str) + evidence(list)，e.type=='pmid' 且 id 匹配 /PMID[:=]?\s*(\d{6,8})/ → 实例(file,path,gene,pmid,note)
- R2 provenance 对象：provenance[cell][gene] 列表内 type∈{pmid_context} 且 id 含 PMID → 实例（class 语境链，gene 仅为挂载点）
- R3 note/文本内嵌：任何字符串值中 /PMID[:=]?(\d{6,8})/ 命中，且 (path,id) 未被 R1/R2 捕获 → 实例；gene/class 取最近祖先键。scope/version 等叙述字段同样扫描（文件头版本串中的日期数字不匹配 6-8 位纯数字窗口的误命中由黑名单字段 {version,created,prereg_sha,card} 排除；created/scope 例外允许命中，因其含真实引用）
- R4 vk 索引行：/PMID(\d{6,8}) \((\d{4})\) (.+?) — \*(.+?)\*/(\[.*?\])/ 逐行 → 实例(topic_page,pmid,stored_title,stored_journal,stored_year,species)
- R5 E2R 对：whitelist key=lib::cls::gene，join pcx_pairs(title1/title2)+title_resolution(resolved_pmid,matched_title)；链=（cls,gene 断言)→resolved_pmid

## 3. 三判据与判级（全部词面机械，零 LLM）
- C1 可解析：批量 NCBI eutils esummary（主通道，每请求≤180 id）；EPMC EXT_ID SRC:MED（副通道，C1 失败者复核）。两通道均无记录 → C1 FAIL。仅 EPMC 无/仅 eutils 无 → 通道差异注记（供 §5 归因）。
- C2 标题基因词面：gene 符号在题名（\b 词边界，大小写不敏感）；R2/R4 类语境/索引链 C2 不适用（N/A，预注册豁免）。
- C3 断言语境相符（词族表冻结如下）：
  - EYE = /retin|ocular|eye|lens|corne|glaucoma|cataract|uvea|macula|photoreceptor|ganglion|microglia|m[ü]ller|amacrine|bipolar cell|RPE|vitreous|sclera|choroid|conjunctiv|lacrimal|tear/i
  - CLASS = 按链的 class 术语表（沿用 kb7_w4b CLASSES 的 11 类词族；Melanocyte/ConjEpithelium 等 k9 类补入对应词族）
  - NOTE 呼应 = note≥15 字符时，note 与题名/期刊内容词（≥4 字符、去停用词）交集≥2 → PASS；note 与题名 0 交集且 note 含具体题名式描述 → DIVERGE 旗标
  - GENERIC = 题名含 /single.cell|atlas|transcriptom|proteom|macrophage|immune|dendritic|review|method|protocol/i
- 判级（good/错配/存疑）：
  - good = C1 ∧ (C2 ∨ EYE ∧ (CLASS ∨ 词条语境为眼) )
  - 错配 = C1 FAIL ∨ (C1 ∧ ¬C2 ∧ ¬EYE ∧ ¬CLASS ∧ ¬GENERIC) ∨ DIVERGE 且 ¬C2∧¬EYE
  - 存疑 = 其余（题在、语境不特异）
- 人工升级判读（允许的"有脑"环节，=复核不是生成）：所有 错配+DIVERGE+存疑带note 行，由本卡逐条读题录+note 终判（CONFIRMED_MISQUOTE / CONTEXT_OK / SUSPECT 维持），逐条写理由入表。RAGFIX sample20 的 20 行既有终判作交叉校验对照（本卡独立重判，不抄标签）。

## 4. 分层 15% 抽检（预注册口径，F3/F4）
- seed 冻结 = 20260928（SEED_FREEZE.txt 先落盘）；random.Random(seed)
- 层 = (框×文件/库, 文次年桶[<2020,2020-2022,2023,2024,2025+], 基因/类 top 去重)；层内不放回抽 ceil(0.15×n_layer)，层<7 时至少 1 条；基因维以"先未抽中基因"优先排序实现词面多样性
- 误引率估计 = 抽检样本终判误引数/样本数，Wilson 二项 95%CI（z=1.96）
- 同时报告全量机械档 census rate 作对照（预注册：两者偏离>10pp 时本卡必须解释）

## 5. eutils 通道缺陷归因（任务 4）
对每条 CONFIRMED_MISQUOTE：(a) note 描述文献是否真实存在（EPMC 题面检索）→ 存在=ID 错位型；(b) 错 PMID 是否曾出现在建链期账本合法命中（kb7_lit_hits.tsv、kb7_lit_eutils.tsv、kb9 PMID_LEDGER.tsv、esummary 痕迹）→ 在=搬运截断/错位型；不在=检索串扰型；(c) 通道记录（EPMC 可解/eutils 可解/仅一通道）；结论落 EUTILS_ATTRIBUTION.md，给 RAGFIX2/未来建库"禁裸用 eutils 通道回填"告诫的实证基础。

## 6. 交付物（全部本目录）
- out/CHAIN_INVENTORY.tsv（全链账总表）
- ledgers/（原始返回逐链留账：batches/ 原始响应、raw_eutils.jsonl、raw_epmc_flagged.jsonl、SEED_FREEZE.txt、PREREG_SHA.txt）
- out/S1_RESULTS.tsv / out/S2_F3_RESULTS.tsv / out/S2_F4_results.tsv（逐链判级+终判+理由）
- out/RATE_TABLE.tsv（分档误引率±95%CI）
- out/ERRATUM_CANDIDATES.tsv（撤证候选：处置建议 撤证/换PMID/降weak，只列不动 kb）
- out/EUTILS_ATTRIBUTION.md、KBCHAIN_NOTE.md（总结账）
- scripts/（全部可重跑，判据在码）

## 7. 既有账衔接
起点账 = rag_fix_20260928/out/PMID_CHAIN_SAMPLE20.{tsv,json}+FINAL_ADJUDICATION.json（6 确诊+1 存疑已登记）、kb/markers/_raggap_errata_v1.json（LILRB2 已撤证，41349939 出框）、e2r_s5audit_20260927/out/e2r_quality_findings.tsv + E2R_NOTE（pmid_context 无 PMID 字段等 4 项存储缺陷——本卡复核其是否复现并在 §5 归因）。

---
## 附录 A — 机修记录（E2R v1.1 先例：实现缺陷修正，判据不动；本附录落盘晚于 §1-§7 冻结，特此声明）
执行判读阶段发现三处**提取/比对实现缺陷**（判据语义均未变更）：
1. **F2/F4 round-trip 比对未剥离"YYYY:"年份前缀与 HTML 标记残留**（E2R 存储题名带 `2016:` 前缀，
   E2R 自己在 PREREG v1.2 已做同款剥离；本卡比对函数漏配）→ 修正后 F2 MISMATCH 47→1
   （唯一残留 LAMA3 = `<i>/<sup>` 标记，人工终判 good）。判据"题录逐字全等"未动。
2. **C2 基因词面匹配漏 re.I**（Grm6/GJA10 驼峰题名漏判）→ 修正对齐 RAGFIX 脚本先例（其 gene_in 用 re.I）。
3. **class 上下文提取丢失**（k9 new_terms/face stromal_repair 路径里的类名未传入判级 → 类词族无法评估）
   → 从 path 恢复类上下文。类词族表本身（§3 冻结自 kb7_w4b CLASSES + k9 补集）未改。
已知词表盲区（不改冻结词表，人工档兜底）：EYE 词表缺 myopia/uveitis/meibomian/keratocyte(刊名) 类词族，
相关行由人工升级判读改判并在 FINAL_adjudications.tsv 留理由。**教训回写归因件 §4：词表下次冻结须补
ophthalmology|myopia|uveitis|meibomian|keratocyte|retinoschisis。**
