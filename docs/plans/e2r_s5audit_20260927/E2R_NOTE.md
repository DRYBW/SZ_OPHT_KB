# E2R_NOTE — S5 宽容口径收口核验（E2 尾账，D1 卡）

卡片 t_dc954503｜任务书 BRIEF_E2R.md｜放行依据 USER_DIRECTIVE_20260927_scoring_wave.md
预注册：E2R_PREREG_v1.0（sha 496be21c，09:13:53）→ v1.1（算法实现缺陷机修，09:20:42）→ v1.2（YYYY: 前缀剥离，09:27:15），三版 sha 均先于一切判读产物；v1.1 缺陷缓存 11 行隔离于 data/e2r_title_resolution.v1.1-defective.jsonl.bak，未入任何判读。
**W 档零改动**：W2 生效状态与 E1/E2 裁决原样（复刻件重算 W 门等值断言 PASS：Δ主 +7.66 / ③ +7.66 / 否决列 −6.63 / 无可用工作点 → W2，与 E2 冻结件全等，见 logs/metrics_log.txt）。本件不含任何改判表述。

## 0. 结论（预注册判读矩阵机械执行）
**ROW2 —— S5 定性"不可核不认"维持 E2 主规则，结案。**
三扳机实测：可核验率 83.3%（≥50% ✓）、可核命中非 HRCA 自引占多（100/100 对含至少一个非自引可核 PMID，self_only=0 ✓）、**但离题占比 79%（>50% 触发"大量离题"否决支）**。
一句话：**PMID 身份几乎全部真实可核、无虚构、无自引垄断——但这些"语境命中"的题名 79% 不含基因词也不含细胞类型词，是 EuropePMC 全文共现检索的语境噪音，不构成对"该基因↔该细胞类型"断言的证据链。** E2 §5 主规则按"身份不可核不认"取严格端的立场，在身份实测可核之后依然成立——理由从"身份不可考"更新为"**语境命中与断言不特异**"。

## 1. 身份核验结果（120 对 pmid_context，逐对）
| 项 | 值 | 注 |
|---|---|---|
| 清单 | 120 对 | v5 provenance pcx>0 == E2 矩阵 pcx_ext=Y == 面板在册，三方一致门 PASS |
| PMID 存储 | **0/120** | pmid_context 记录字段只有 (query, n_hits, top_titles)——从未存过任何 PMID（KB 数据质量发现①） |
| 可核验（≥1 题反解出真实 MED+PMID） | 100/120 = 83.3% | 解析出 141 个去重 PMID，全部 EuropePMC MED 记录 |
| 不可核验 | 20/120 | **全部是题字段空存储**（n_hits>0 但 top_titles=[""]），非虚构（发现②） |
| 虚构 PMID | **0** | 未发现任何捏造题名（2 条题 EuropePMC 仅 PPR 预印本记录、无 MED，判不可核非虚构） |
| 自引垄断（全部可核命中均 ∈HRCA 集） | 0 对 | |
| 首条即 HRCA 本体/语料对应件 | 2 对（BC NETO1、BC TENM3） | E2 §5 点名的 NETO1 案例证实；HRCA 集={41578023, 40660409}（本体+语料内预印本对应件，均 kb/literature_db 在册） |
| 关键词级相关（题含基因词或类词） | 21/100 = 21% | 其余 79 对命中题不含断言词=离题（判读矩阵触发支） |

## 2. 三口径水分账（复刻件重算；raw/S1/S5 与 E2 冻结 TSV 逐行零差异，out/e2r_verify_replica.tsv PASS）
主面与 Q5b（out/e2r_three_caliber_table.tsv）：

| 口径 | 认账规则 | F-RET@196① | F-RET无泄漏① | F-3SEAT① | Q5b@43① | Q5b水分pp |
|---|---|---|---|---|---|---|
| raw（不去污） | — | 72.45 | 67.74 | 60.26 | 93.02 | 0.00 |
| **S1 严格（E2 主规则）** | 仅显式逐基因 PMID | **63.27** | 56.77 | 51.28 | 60.47 | **32.55** |
| S5b 可核验 | 题可反解真实 MED+PMID 且非 HRCA 自引（100 对认账） | 71.94 | 67.74 | 60.26 | 93.02 | **0.00** |
| S5b_rel 可核+相关 | S5b ∧ 题含基因/类词（21 对认账） | 63.78 | 57.42 | 52.56 | 62.79 | **30.23** |
| S5 全认 | n_hits>0 即认（120 对） | 71.94 | 67.74 | 60.26 | 93.02 | 0.00 |

- S5b 与 S5 全等的原因（实测定位）：S5 比 S5b 多认的 20 对恰是 20 对空题不可核——其基因未改变任何簇 top1（S5↔S5b 全部差异仅 8 个簇的非 top1 候选 n 值减 1，out 明细见 data/e2r_scores_*）。
- S5b_rel 与 S1 仅差 0.51pp（63.78 vs 63.27）：把"真实+相关"的 21 对计入后水分几乎全保留（30.23pp），**即 E2 主规则的严格端几乎不因"宽容可核语境命中"而动摇**。

## 3. 对 E2 §7.2 的响应（任务书要求句式）
**若 PI 认 S5b（"PMID 可核且非 HRCA 自引"字面口径），Q5b 水分读数区间为 [0.00, 32.55]pp——S5b 落在 0.00pp 端（与 S5 全认同值），S1 主规则在 32.55pp 端；加关键词级相关性门（S5b_rel）则读数 30.23pp，紧贴 S1。**
主面同构：S1 63.27 / S5b 71.94 / S5b_rel 63.78 / S5 71.94（raw 72.45）。
机械判定：可核验率高但离题占多 → 判读矩阵行2 成立——S5 通道"不可核不认"的**结论**不变，**理由**修正为：语境命中不特异（79% 题名与断言无词面关联），且面板连 PMID 与可核题名都未完整存储（20/120 空题）。按预注册：结案，未来评测是否采 S5b 的裁定权在 PI，本卡不代裁、不改 W 档。

## 4. KB 数据质量发现（单列清单 out/e2r_quality_findings.tsv，159 行，供 D4/PME 线输入）
① 120/120 pmid_context 记录无 PMID 字段（只有 query/n_hits/top_titles）——"PMID 身份不可考"是存储结构缺陷而非检索缺陷；
② 20/120 对题字段空（n_hits>0），身份永远不可复核；
③ 42/145 唯一题名带 `YYYY:` 前缀混存、77/120 对题名 120 字符截断——检索友好性差；
④ 2 题 EuropePMC 仅 PPR 预印本无 MED 记录；
⑤ 0 条虚构 PMID（正面结论：v5 建库时 EuropePMC 检索本身没有捏造数据）。
**对 D4（338 对无记录文献补录）的告诫：pmid_context 通道只能给出"共现语境"不能给出"逐断言引用"，补录不应复用此通道。**

## 5. 复现链与红线实证
链：scripts/e2r_extract.py（清单，门0 三方一致）→ e2r_pmid_verify.py（v1.2 算法，147 唯一题 + 三锚 exit-2 门；原始 API 返回 236 件落 ledgers/api/）→ e2r_score.py ALL（raw/S1/S5/S5b/S5b_rel）→ e2r_verify_replica.py（逐行全等闸 PASS）→ e2r_metrics.py（E1 锚 + E2 S1/S5 锚 + Q5b 水分锚 + W 门等值断言全 PASS）→ e2r_closeout.py + e2r_findings_final.py。
复刻件 = E2 脚本拷贝改参（改动逐条留痕 scripts/replica_patch_notes.txt / replica_metrics_notes.txt），E2 原目录零写入。
红线实证：37 输入件 PRE/POST sha 全等（ledgers/sha_ledger_{PRE,POST}_inputs.txt）；零 LLM 判读调用；零生产码 import（eyekb_core 未调用，sha 在台账）；除 EuropePMC REST 检索返回落盘外零下载；全部产物只落本卡目录 /mnt/D/EyeKB/plans/e2r_s5audit_20260927/。

## 6. 产物清单
E2R_NOTE.md（本件）｜E2R_PREREG_v1.0/1.1/1.2.md｜data/e2r_pcx_pairs.{tsv,jsonl}｜data/e2r_title_resolution.jsonl｜data/e2r_pair_verdicts.tsv｜data/e2r_whitelist_S5b.json｜data/e2r_scores_{raw_replica,S1,S5,S5b,S5b_rel}.tsv｜out/e2r_identity_summary.json｜out/e2r_matrix_verdict.json｜out/e2r_three_caliber_table.tsv｜out/e2r_homology_water.tsv｜out/e2r_sensitivity_grid.tsv｜out/e2r_truth_region_table.tsv｜out/e2r_metrics.json｜out/e2r_verify_replica.tsv｜out/e2r_quality_findings.tsv｜out/e2r_history_register.tsv（E2 登记表同源副本+append 一行，未回写 E2）｜out/e2r_flag_operating_points.tsv｜out/e2r_row_compare.tsv｜out/e2r_by_class.tsv｜out/e2r_panel_water_copy.tsv｜ledgers/（sha 台账+API 原始件）｜logs/｜scripts/。
