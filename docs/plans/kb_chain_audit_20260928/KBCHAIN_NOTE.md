# KBCHAIN_NOTE — 全库引用链误引审计总账（只取证不修，D20）

卡: t_3a35a2cc ｜ 任务书: BRIEF_KBCHAIN.md ｜ 预注册: PRE_REG_kbchain_v1.0.md（sha 见 ledgers/PREREG_SHA.txt）
seed=20260928（ledgers/SEED_FREEZE.txt，先于抽样落盘）｜ 执行日: 2026-09-28
状态: **全检+抽检完成，20 条确诊误引登记，零动 kb**

## 0. 一句话
KB6/KB9 建链期证据链全检 58 条确诊误引 **20 条（34.5%，95%CI 23.6–47.3%）**，全部集中在
**v6 retina_repair（12/13=92.3%）与 face_increment（8/10=80.0%）两份决策表转录链**；
k9 新条（0/21）、KB8 泪腺（0/14）、E2R 白名单（0/169 链）、S2 层全部历史链
（F3 0/120 抽检 + F4 0/1,125 抽检，census 机械档同为 0）——**误引是"KB7 决策表手抄转录"单通道缺陷，
不是全库系统性污染**；RAGFIX 抽 20 的 30% 估计被全检证实并精确定界（20/55 同框口径=36.4%）。

## 1. 分档误引率总表（out/RATE_TABLE.tsv）
| 层 | 框/文件 | n | 确诊误引 | 率 | Wilson 95%CI | 口径 |
|---|---|---|---|---|---|---|
| S1 全检 | F1 合计（v6/k9 evidence 链） | 58 | 20 | 34.5% | [23.6, 47.3] | 人工终判 |
| S1 | markers_v6_retina_repair.json | 13 | 12 | **92.3%** | [66.7, 98.6] | 全检 |
| S1 | markers_v6_face_increment.json | 10 | 8 | **80.0%** | [49.0, 94.3] | 全检 |
| S1 | markers_v6_lacrimal_increment.json | 14 | 0 | 0% | [0, 21.5] | 全检 |
| S1 | markers_k9_ocs_increment.json | 21 | 0 | 0% | [0, 15.5] | 全检 |
| S1 | E2R 白名单（link/pair 级） | 169/100 | 0 | 0% | [0, 2.2]/[0, 3.7] | 全检 round-trip |
| S2 抽检 | F3 词条级历史链（membrane/v5注/priors/baselines，母体 693） | 120 | 0 | 0% | [0, 3.1] | 15% 分层+CI |
| S2 | F3 census 机械档补充 | 693 | 0 | 0% | [0, 0.6] | 全扫 |
| S2 抽检 | F4 vk 题录索引（母体 7,484） | 1,125 | 0 | 0% | [0, 0.3] | 15% 分层+CI |
| S2 | F4 census 机械档补充 | 7,484 | 0 | 0% | [0, 0.1] | 全扫 |
预注册偏离条款（样本 vs census >10pp 须解释）：未触发（两侧同为 0）。
F4 census 7,484 条 = 索引表面 PMID↔存储题名一致性全扫，0 错位——kb 引用链损伤不外溢到 RAG 索引面。

## 2. 确诊误引 20 条（out/ERRATUM_CANDIDATES.tsv，只列不动 kb）
| # | 文件链位 | 基因 | 错 PMID | 实际题录 | 处置建议 |
|---|---|---|---|---|---|
| 1 | face/Pericyte core[3] | COX4I2 | 35920172 | "Letter to the editor"(口颌) | 换→35929074(当日账本唯一命中, 待题验) |
| 2 | face/Conj_basal core[0] | KRT13 | 33503899 | 血管扩张症 miRNA | 撤证/找回 |
| 3 | face/Conj_basal core[2] | AQP5 | 35590283 | SIADH 药物警戒 | 撤证/找回(15557451 物种不符) |
| 4 | face/Conj_basal core[3] | CXCL17 | 33201599 | 景观生态 | 撤证 |
| 5 | face/Conj_basal core[4] | LCN2 | 35021166 | CuI 第一性原理(物理) | 撤证 |
| 6 | face/Conj_basal core[5] | KRT19 | 38528295 | 乳腺癌真实世界 | 换→25722207(RAGFIX 找回, 题逐字匹配) |
| 7 | face/Conj_sup core[0] | SCGB3A1 | 37381815 | 法医亲缘算法 | 撤证 |
| 8 | face/Conj_sup core[1] | FDCSP | 35021166 | CuI 物理文(与#5 同错号) | 撤证/找回(候选 42589107 待题验) |
| 9 | BC[38] | GPR179 | 42124641 | 着床前胚胎生力组学(bioRxiv) | 撤证 |
| 10 | MG[1] | PRSS56 | 29561967 | 儿童口呼吸诊断 | 撤证 |
| 11 | RPE[5] | MFRP | 40228796 | 透析共享决策(护理) | 撤证 |
| 12 | RPE[6] | HMGCS2 | 38749583 | 结肠息肉出血预防 | 撤证 |
| 13 | RPE[7] | CLIC6 | 39385205 | 心肌应变 CMR | 撤证 |
| 14 | RPE[8] | OR51E2 | 36167259 | 精油封装(食品化学) | 换→29249973(双账在案, 待题验) |
| 15 | RGC[5] | UCHL1 | 24449362 | ABO 血型-卒中 | 撤证 |
| 16 | AC 锚[0] | CHAT | 41037735 | 髁突𬌗垫记录 | 撤证 |
| 17 | AC 锚[2] | VIP | 38087179 | 老年住院死亡率 | 撤证 |
| 18 | MG core[8] | TAL1 | 28696901 | 空题录残损记录 | 撤证 |
| 19 | MG core[9] | OLR1 | 40153135 | 流脑疫苗经济学 | 撤证(候选 40140148 待题验) |
| 20 | MG core[10] | ITGAX | 41665199 | ZIO 染色方法学 | 撤证(候选 41683913 待题验) |
机制分型（A 数字变异 8 / A′ 弱同形 2 / B 搬运替换 4 / C 裸回填 6）与全部量化证据见
out/EUTILS_ATTRIBUTION.md + out/MISQUOTE_MECHANISM.tsv。
**下游影响提示**：retina_repair MG/RPE 块是 09-28 v2.4 评测与 R7 GRN 冻结消费的词条面之一；
20 条链中 12 条集中在 retina_repair（其 GPR179/MFRP/HMGCS2/CLIC6/OR51E2/PRSS56/TAL1/OLR1/ITGAX 等
均为标记基因证据位）——撤证不改变数据驱动统计（evidence 仅为文献锚），但**词条级"该基因×该类"
断言的文献支撑在 v6 面大面积归零**，修链执行卡批准后需同步刷新引用面板。
（REVIEWER_LLM Q4 补验已证：7 条确诊/存疑误引与门①41 用例 top-5 交集=∅、与闭集交集=∅ → 评测结论未被污染。）

## 3. k9 与 F2 的"非误引但弱"登记（降 weak 建议，8+ 条）
k9 新条链 0 确诊（PMID 全部 = 当日检索账本合法命中），但 8 条属"基因-类共现真、眼特异性/物种弱"：
TRPM1/PMEL/MLANA/GPR143/DPT/LAMA2(降weak)、SLC24A5(降weak+鸟类物种注记)、CST4(泪腺, 降weak)；
PRR27 建链日无账(仅 RAGFIX 后置合法化)挂"找回待验"。E2R 白名单 38 条 SUSPECT=语境不特异旁证
（与 E2R_NOTE"79% 离题"口径一致），非误引，维持 E2 主规则处置。

## 4. 与起点账交叉验证（out/CROSSCHECK_sample20.tsv）
本卡对 sample20 同 20 链**独立重判**（不抄标签）：一致 19/20。差异 = MLANA（RAGFIX 判 CONSISTENT，
本卡题录级零词面证据降 suspect——全检更严，方向一致不冲突）。升级 2 条：GPR179（UNCLEAR→确诊，
题录=胚胎文异域）、COX4I2（SUSPECT→确诊，当日 idlist 35929074 前 4 位同形=转录变异实锤）。

## 5. 通道缺陷要点（详见 EUTILS_ATTRIBUTION.md）
- 20/20 确诊链**建链当日零账本痕迹**；同框对照：留全账的 KB9=0%、题名-PMID 成对存储的 E2R=0%。
- 根因=KB7-W4/W4b→kb7_decisions.json 的手抄转录**无 round-trip 校验**（W4b 代码不存块↔PMID 映射，
  es_*.json 留账行被 `if False` 禁用；同错号 35021166 成对复用=转录污染传播指纹）。
- eutils 记录缺陷：28696901 "可解析但空题录"（单通道会漏检）；42777860 通道状态漂移
  （RAGFIX 称 EPMC 已收，本卡实测 EPMC 无/eutils 有）→ **C1 判据必须双通道 + 原始留账**。
- v5 pmid_context 无 PMID 字段缺陷复现（120 条 NOT_CHECKABLE 登记）。

## 6. 红线遵守
只写本卡目录；kb/、rag_fix_20260928/、batch_v25/、e2r_s5audit_20260927/ 全程只读——
本卡开工时点未做 PRE 快照，零写证明=只读面关键文件 mtime 全部早于本卡会话起点(09-28 00:53) +
收尾 sha 台账留底（ledgers/SHA_READONLY_verify.txt，含 mtime 列）；零生产写、零 kb 修改、零 LLM 判读
（判级=冻结词面规则，人工环节仅题录级复核且逐条留理由）；网络=EPMC/eutils 题录级 2,877 唯一号
双通道批量（ledgers/batches/ 88 件原始响应全留，unresolved=0）；分批落盘 work→ledgers→out→报告。

## 7. 产物索引（全部 /mnt/D/EyeKB/plans/kb_chain_audit_20260928/）
| 件 | 路径 |
|---|---|
| 预注册+机修补录 | PRE_REG_kbchain_v1.0.md（含附录机修记录）+ ledgers/PREREG_SHA.txt |
| 链账总表 | out/CHAIN_INVENTORY.tsv（8,531 实例：F1 59/F2 169/F3 813/F4 7,490） |
| 判级明细 | out/S1_RESULTS.tsv、S2_F2_RESULTS.tsv、S2_F3_RESULTS.tsv、S2_F4_RESULTS.tsv |
| 人工终判 | out/FINAL_adjudications.tsv（37 行逐条理由）|
| 率表 | out/RATE_TABLE.tsv（分档+Wilson CI） |
| 撤证候选 | out/ERRATUM_CANDIDATES.tsv（20 条，只列不动） |
| 归因 | out/EUTILS_ATTRIBUTION.md、out/MISQUOTE_MECHANISM.tsv、out/LEDGER_XREF.tsv |
| 抽检冻结 | ledgers/SEED_FREEZE.txt、ledgers/SAMPLE_FREEZE.json（23 层）、out/SAMPLE_S2_selection.tsv |
| 交叉验证 | out/CROSSCHECK_sample20.tsv（19/20 一致） |
| 原始题录账 | ledgers/recs_merged.json、raw_eutils_map.json、raw_epmc_map.json、batches/(88 件)、unresolved_pmids.txt(空) |
| 脚本 | scripts/kbc1_inventory.py→kbc2_fetch.py→kbc3_adjudicate.py→kbc6_final→kbc4_rates→kbc7_mechanism（判据在码，可重跑） |
| sha | ledgers/SHA_DELIVERABLES.txt |

## 8. 建议后续（不自动执行，交 PI 看账后批）
1. **修链执行卡**（本卡红线=只列不动）：按 ERRATUM_CANDIDATES.tsv 20 条执行撤证/换号/降weak；
   4 条"换PMID"候选须先逐条题录复验（29249973/35929074/25722207/42589107 等）再写；
   改 kb 走 errata 新文件+双 sha 先例（_raggap_errata_v1.json 同款 INERT→激活两段式）。
2. RAGFIX2/建库卡继承"禁裸用 eutils 回填 + round-trip 强制 + 原始响应留账"三条告诫（EUTILS_ATTRIBUTION.md §4）。
3. v6 面 12/13 归零后 retina_repair 词条的文献支撑缺口 → 与 RAGGAP A 档追加轮（v2.5）合并排产，
   找回时直接用留账通道。
