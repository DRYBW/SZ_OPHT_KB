# E1_PREREG_v1.0 — 证据入打分对照实验 预注册件（跑数前落纸）

- 卡片：t_a7515c0b｜任务书：BRIEF_E1.md（sha 见 ledgers/sha_ledger_PRE_inputs.txt）
- 批准链：USER_DIRECTIVE_20260926_redline_rewrite.md 追加一（红线 v2 第③条首次激活）
- 本件落纸并 sha 入账之后才允许执行任何命中率/F1 计算（红线④）。
- 机读冻结件：e1_class_map.json（候选类→真值标签映射+并分+破并列规则）、e1_leak_lineage.json（GSE→源论文→语料通道）。二者为本件组成部分，一并落账。

## 0. 输入（全部只读，PRE/POST sha 台账 = ledgers/sha_ledger_{PRE,POST}_inputs.txt）

| 件 | 用途 |
|---|---|
| evalset/digest/EV_DIGEST_SLIM_v3full.jsonl (290 行) | 考卷面：top_genes 双列 + kb_marker_ranking(OFF 时代存档 top3) + lit 面（候选→引用论文） |
| evalset/scoring/run3_object_B_table_v1.1.tsv | 真值（truthfix α 后）+ 双席票（A/B）+ match 列基线 |
| face_v21_20260926/out/per_cluster_flip_table_facev21.tsv | 三席票与共识（45 簇，v2.1 面 = 现役冻结判读存档）；RUN4-r 列作敏感性 |
| evalset/scoring/run5_truth_table.tsv + run5_verdict.json | Q6 三席票与共识（33 簇） |
| kb/markers/*.json（6 库文件） | 证据分原语数据源（直调 eyekb_core 读取，本体零改动） |
| literature_db v2.0_2026-09 papers.jsonl (2713) | 泄漏审计语料成员判定 |

禁项执行：不重跑 LLM（三席全部读存档）；不启停/修改 MCP server（eyekb_core 仅 import 直调，与 MCP 同代码路径=任务书指定原语）；不新增语料；生产判分/共识裁定代码零写入（红线①——本实验全部产物落 plans/evidence_scoring_20260926/，不接线任何 server/core/评分链文件）。

## 1. E1-1 分数构建（操作定义）

对每簇 c（290 全量）：

1. 查询基因 = digest 冻结列 `top_genes_sym`，按构建器原规则取 `(sym or ENSG)` 前 10 个（与 RUN2/RUN3 采集器 kb2_mcp_v2.py L54 逐字同规则；ENSG 未映射串在 query_marker 内自然 0 命中，行为与建卷时一致）。
2. 直调 `eyekb_core.query_marker(genes=上列, library='all')`：
   - **ON 态 = 主口径**（env EYEKB_ACT_V6 未设 → 60 类，现生产面）；
   - **OFF 态 = 敏感性**（env=0 → 43 类）。
   - OFF 态重算结果须与 digest 存档 `kb_marker_ranking`（建卷时 OFF top3）做一致性自检；不一致按库漂移如实登记（不修数）。
3. 候选并类：canonical = 去 `<lib>::` 前缀基名；同 canonical 的别名行 n_shared 取 **max**（不求和，防重复计数）；lit 候选键同规则并入。候选宇宙 = ON 排名键 ∪ lit 键。
4. 三类分数（对每个 (簇, canonical 候选) 对）：
   - **① marker 重合分** = n_shared（原始计数分，任务书指定）；top1 按 (n_shared↓, canonical↑)。
   - **② lit 文献分** = 该候选 lit 条目去重 PMID 数（建卷 top_k=4 封顶）；仅作列报，非主口径（任务书①③主）。
   - **③ 等权合成分** = 0.5·(n_shared/簇内 max) + 0.5·(min(n_papers,4)/4)；top1 按 (合成分↓, n_shared↓, canonical↑)。
   - 并列破缺全部机械化（e1_class_map.json tie_break），禁事后改。
5. 权重网格 w∈{0,0.1,...,1.0}（③ 的推广 `w·norm_m+(1-w)·norm_l`）**全表只作敏感性落盘 out/e1_sensitivity_grid.tsv，不进任何结论**（任务书①）。

主口径声明（防挑好看）：E1-2 的命中对照 **①与③各算各报**；判读矩阵对 ①③ 分别定档；若两口径落在矩阵不同档，裁决=如实报告跨档并整体降为"边界案"交 PI，禁择有利档作单一结论。

## 2. E1-2 真值区对照（评测面与基线）

真值 = run3 v1.1 表 truth 列（truthfix α 后为准，Q2::18/19 修正已含）；命中判定 = 证据 canonical 经 e1_class_map 映射后 == 真值标签；未映射/AMBIG 主口径=miss（分母不豁免）。

| 评测面 | 定义 | n（真值行） | LLM 基线 |
|---|---|---|---|
| **F-RET**（主面） | 成员 ∈ {Q1,Q2,Q3,Q4,Q5b,Q7} 且 truth 非空 | ≈196（α 口径，脚本实算为准） | RUN3 席 A、席 B（单席命中两列）+ **AB 两席共识**（ann_A==ann_B 且均为具体 identity 者记该标签，其余按保守 miss 计满分母；另报"仅共识已定义子集"条件列） |
| **F-OCS** | 成员 Q6 且 truth 非空 | 33 | RUN5 三席共识（存档 consensus 列）+ 单席三票均值；**全程带"判读层参照循环"标注**（D002 同源，只作面板级 sanity） |
| **F-3SEAT** | FACEV21 翻转表 ∩ F-RET（三席面，retina 成员，truth 非空）∪ RUN5 Q6 | 脚本实算 | FACEV21 三席多数票（现役面）；RUN4-r 多数票同表并列报（敏感性） |
| F-DEV | 成员 Q8（发育轴） | 35 | 不进命中率主表（E5 红线：胎/成分离）；只记证据 top1 分布作行为观察 |

- 每面每口径报两列族：**命中**（top1 命中率、top3 覆盖率——真值∈top3 即覆盖）与 **macro-F1**（真值类并集上逐类 P/R/F1，zero_division=0；弃权/无共识按"无类预测"计 FN 不产 FP；证据 top1 空排名按无类预测，同规则对称）。
- 分层：面板（上表）× 真值类（逐类命中表）两层全部落 out/。
- **诚实替代声明（跑数前落纸）**：判读矩阵字面写"三席多数"；290 全量面只有 A/B 两席（C 席从未跑过全量，禁重跑）。故矩阵在 F-RET 上的基线 = AB 两席共识（最接近的合法替代，替代关系此处预先声明，不做事后解释空间）；F-3SEAT 上是字面三席多数。两面都报；档位判定以 **F-RET 为主、F-3SEAT 为副**，两面上升档一致才算稳档。

## 3. E1-3 泄漏审计（先于命中表出，分裂规则预注册）

- 方法：e1_leak_lineage.json 固化成员→源 PMID；逐簇取 lit 引用 PMID 全集；语料成员关系对 papers.jsonl 实测重算。
- 逐簇三态：`evidence_self_reference ∈ {有, 无, 不可判}`：
  - lit 引用为空 → **无**（lit 通道未被消费，marker 通道单列注记）；
  - 成员源论文可解析：被该簇 lit 引用 → **有**；未引用 → **无**；
  - 成员源论文不可解析且 lit 引用非空 → **不可判**。
- marker 通道结构性自参照（Q5b=HRCA 面板派生、Q3/Q4=HRCA constituent、Q6=D002 面板派生）单列 `marker_channel_ref` 记录，**不并入 lit 三态**；主表附加"剔除 marker_channel_ref=强 成员"的敏感性重算列（只列数不改主口径）。
- **主表按 有/无 分列重算命中（=判读矩阵输入列）**；不可判列单报。
- 判读矩阵附加条款（任务书原文执行）：若"有"列命中率 − "无"列 > 10pp，无论档位，结论首行必须写"背答案效应主导"。

## 4. E1-4 无真值区观察（纯描述）

truth 为空的 290−264=26 行（Q9 全部 + 零散不可映射簇）：证据 top1（canonical 与映射后标签两列）vs 面板共识（AB 一致/三席多数，存档）。报一致率+逐例清单；**禁写成命中/正确率**（无真值）。

## 5. E1-5 分歧案例

选例规则（机械）：F-RET∪F-OCS 中 证据①top1 映射标签 与 面板共识标签 均有定义且互斥的簇，按 |n_shared 差| 降序抽 5 例；**Q2::22（基因共表达先验误导案，FACEV21 期 newly_fixed→Astro）为强制必含例**，若其不在前 5 则替换第 5 例并登记。每例陈列：top10 基因、ON 全排名（canonical+n_shared+lit 数）、lit 引用（PMID+年）、各席票+grade+共识、真值、分歧类型注记（验证证据分是否与判读员同坑/不同坑）。

## 6. 判读矩阵执行细则（任务书 §判读矩阵的机械化）

- Δ = 证据 top1 命中率（**扣泄漏列后的"无"列**，分母=该面"无"列真值行）− 基线命中率（同分母重算：基线票也只在"无"列行上计，分母一致才可比）。①③ 各算 Δ。
- 档位：Δ≥+5pp→V1；−5pp<Δ<+5pp→V2；Δ≤−5pp→V3（边界含入：+5pp 整归 V1、−5pp 整归 V3，预先写死）。
- F-RET 主、F-3SEAT 副分别定档；V1 档→按任务书出"生产化提案书（QC 分流/候选缩圈定位）"草案等 PI 批，**不实装**；任何档都不动生产判分链。

## 7. 已知局限（跑前登记）

1. RPE↔Q6"pigmented epithelial"边界取保守不映射（见 class_map basis）。
2. Q7 鼠簇用人源 symbol 大写碰撞 = 生产 ON 面原样行为（facev21 席位协议的"撤 v6 ranking"规则属判读侧，不属库侧，E1 不模拟）。
3. lit 分数只到"引用篇数"粒度（建卷 schema 无片段级证据强度），②③ 的含义受此限。
4. Q4/Q6/Q8 源论文本地不可解析（eutils 不可达）→ 其簇多为"不可判"，泄漏扣减效力受此限，如实声明。
5. OFF 态=重查询的"现役三库"，若 09-24 后库文件有漂移，与 digest 存档自检列报差异。
6. 判读矩阵的"三席多数"在 290 面只能以两席共识执行（§2 替代声明）。

## 8. 产物清单

- 本件 + e1_class_map.json + e1_leak_lineage.json（.sha256 各自落账）
- scripts/e1_collect_scores.py（采集+打分）/ e1_metrics.py（命中/F1/泄漏分裂/分层）/ e1_divergence.py（选例）
- data/e1_scores_ON.tsv / data/e1_scores_OFF.tsv（逐簇×候选全表，保留）
- data/e1_leak_table.tsv（逐簇三态）
- out/e1_truth_region_table.tsv / out/e1_by_class_table.tsv / out/e1_no_truth_agreement.tsv / out/e1_divergence_cases.tsv / out/e1_sensitivity_grid.tsv
- E1_VERDICT.md（最终判读，含档位、跨档声明、提案书与否）
- ledgers/sha_ledger_POST_inputs.txt（收口时全输入复跑 sha + 冻结件零触碰自证）
