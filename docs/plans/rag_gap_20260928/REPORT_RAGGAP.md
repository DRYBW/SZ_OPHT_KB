# REPORT_RAGGAP — 全 KB 词条 × RAG v2.1 语料覆盖盘点（D18，零下载）

日期: 2026-09-27 ｜ 卡: t_922cdfa0 ｜ 任务书: 本目录 BRIEF_RAGGAP.md
状态: **盘点完成，产出即停——零下载、零重建，等 PI 勾 TIER_A_approval_list.md**

## 0. 一句话结论

**"RAG 无需扩容"只对了一半：** 词条行层面 77%（830/1074）的"缺口"确实只是索引旁挂（C 档，不补语料）；
但存在一个**集中的真扩容面**——神经元亚型锚层（retina AC/BC/HC 扩展基因）+ 泪腺附属器整线 + 膜库免疫亚群，
去重后 **65 篇必补一手论文**（净，已扣 v2.2/v2.3 吸收的 5 篇），估总容量 ≤~35 MB，**>1GB 单独批条款不触发**。

## 1. 方法与口径（预注册判据）

- 词条面 = 现役 KB 全部 marker 库：retina v4.1/v5(+prov)/v6_repair(blocks)、membrane_v1(+prov)、face_v6、lacrimal_v6(KB8)、kb9(build 件 4 新条；已实证 D17 注册件 kb/markers/markers_k9_ocs_increment.json 与 build 件基因/PMID 全等，口径不受注册时点影响)——**1074 个 词条×基因 行 / 402 去重基因**（:prov 溯源层并入统计）。
- 语料面 = **RAG v2.1**（220,375 chunks / 3,674 有 chunk 论文 + 15 ghost，manifest sha 台账见 ledgers/）。
- 支撑层级（行级）：
  - S1 chain_covered：词条引用的 PMID 在库且有 chunk；
  - S2 gene_in_corpus：链 PMID 不在库，但该基因被 ≥1 篇在库论文 chunk 文本提及（词边界 token 匹配）；
  - S3：两者皆无 = 语料真缺口；
  - S0_not_a_gene：状态标签伪基因（修正 panels 误抽后为 0 行，见 §6 已修 bug）。
- 分档判据（HC-LITRE 教训固化，只有"人+眼组织词族"计数算数，全库命中不算）：
  - **A 档** = R1 库外引用链可证在 EPMC（6/7 存在）∪ R2 无链基因眼语境命中 >5；
  - **B 档** = R3 命中 1–5（固有稀缺）∪ R4 命中 0；
  - **C 档** = 已有库内覆盖、仅证据链未链接/索引字段缺 = 纯工程旁挂；其中"提及但语境错配"（C_ctx_mismatch, 74 行）按 A/B 判据重裁——全部转 A（无一转 B），即错配行是真缺口而非索引问题。

## 2. 覆盖矩阵总览

| 档 | 行数 | 占比 | 含义 |
|---|---|---|---|
| COVERED (S1) | 6 | 0.6% | 链 PMID 在库（KERA/ALDH3A1/NNMT/SLC4A11 via 34741068；SLC5A7 via 33393903） |
| C（旁挂即修） | 830 | 77.3% | 基因有库内支撑、链未链接（C_strong 610 / C_mid 220） |
| A（真扩容面） | 232 | 21.6% | 去重 92 个基因×语境 / 65 篇必补 + 104 篇备选候选 |
| B（固有稀缺） | 6 | 0.6% | 去重 3 基因：CYTH4(4)、HIGD1B(4)、MFSD4A(5×多库) |

### 词条级要点（全表 coverage_matrix.tsv / tier_FINAL.tsv）

1. **链级覆盖近乎为零（0.6%）是结构性的**：历轮词条（KB4~KB9）的逐基因链是"本地 RAG + eutils/EPMC 摘要语境校验"建的，
   校验用的 PMID 大多**没进库**（尤其 2024-2026 新文献与附属器文献）——不是检索退化，是当初设计就没让链与库同源。
   这是 C 档 830 行的主根源：**库内其实有货，链没指过去**。
2. **S3 真缺口分布高度集中**（164 行 → 68 基因）：retina_v5/v6 的 AC(64)/BC(53)/HC(58) 亚型锚基因、
   membrane 免疫亚群 pDC/NK/T/Plasma/Microglia（~30 行）、**lacrimal_v6 全部 7 行**。
   v4.1 十类核心、face/kb9 眼表条几乎全在 C 档——**核心词条不缺语料**。
3. **泪腺=整线结构性缺口**：v2.1 库 lacrimal/tear 组织标签 0（V4 附属器"只查量不入库"设计决定），
   KB8 词条链引的 2021-2026 泪液组学文献全部库外。补不补=PI 对附属器线的取舍，不是盘点能定的。
4. v2.2（+7 篇 d0_targeted）/v2.3（+4 篇角膜）增量与本轮 A 候选交叉比对：**5 篇已被吸收**（清单已标"免补"）。

## 3. 对任务书第 4 条的诚实回答

C 档在**行数上确为主（77%）**——对核心 10 类 + 眼表词条，结论"RAG 无需扩容、只需补索引旁挂"成立（TIER_C_index_backlog.md 两条零重建路径）。
但**词条行占比 ≠ 缺口重要性**：A 档 232 行集中在亚型锚层/附属器/免疫亚群——恰恰是注释分辨率最需要文献支撑的地方。
故不给"无需扩容"的 blanket 结论，给"**核心不扩、亚型线定向小补 65 篇**"的中间答案，由 PI 按清单勾选裁决。

## 4. 交付物索引

| 文件 | 内容 |
|---|---|
| coverage_matrix.tsv | 1074 行全矩阵（逐 库×词条×基因，链/库内支撑/文本提及数） |
| tier_FINAL.tsv | 同上 + 终档（COVERED/C/A/B + tier_note） |
| TIER_A_approval_list.md | **报批主件**：65 必补 + 104 备选，PMID/年份/OA/收益词条/勾选框 |
| TIER_B_rarity_register.md | 3 基因稀缺登记（含 EPMC 命中数），禁列补 |
| TIER_C_index_backlog.md + tier_C_backlog_detail.tsv | 830 行旁挂工程清单（两条零重建路径+逐行候选链接 PMID） |
| out/ | 全部中间件（corpus_gene_index / corpus_text_gene / epmc_* / s2_ctx_rows / RAGGAP_STATS.json）与日志 |
| scripts/ | s1~s7 全链可重跑（判据在码） |
| ledgers/ | 输入 sha 台账 + 交付件 sha 台账 |

## 5. 局限（如实）

- 词边界 token 匹配是元数据级近似：基因提及≠该文献支持该基因作该语境 marker；C_strong 回填前需逐行语境抽检（工程量在 C 清单里）。
- A 候选=EPMC 检索词族 top 命中，个别相关性差（如 40971959 为斑马鱼论文漏入——词族过滤不严格的实证），PI 勾选时复核。
- 单篇体积无法零下载实测（EPMC fullTextXML chunked 流式无 Content-Length、拒绝 Range），清单用 ≤0.5 MB/篇经验上界；执行获批后按实际管线复测。
- B 档判定基于 EPMC 命中数阈值（1-5），是操作化定义不是绝对真理；MFSD4A/CYTH4/HIGD1B 若将来出现眼科单细胞文献可翻案。
- 本次口径为任务书指定的 v2.1；MCP 默认库仍是 v2.0（DB 指针），若 PI 后续切库，A/B/C 分档会平移（v2.2/v2.3 吸收 5 篇即此效应的一角）。

## 6. 执行中发现并已修复的自身 bug（防复犯）

1. papers.jsonl 个别 title 含换行/制表符 → TSV 破行（s1 已加 `' '.join(split())` 清洗）。
2. EPMC 过滤语法 `"Homo sapiens"[Organism]` 在 REST search 返回假 0 → 首轮大量假 B_none；改 `SPECIES:"HUMAN"` 重跑（HC-LITRE 教训的镜像：**检索式失效会把"可补"错算成"稀缺"，反之亦然**）。
3. membrane `panels` 容器是"面板→类名"映射被误当基因列表 → 剔除后 402 真基因。

## 6.4 顺带发现的上游词条缺陷（本卡领地外，只报告不修）

retina_v6/microglia_repair 词条 LILRB2 的证据链引用 PMID:41349939，EPMC 逐字复核=
"Urinary exosomes: Emerging biomarkers for urinary tract infection"（泌尿科论文，与视网膜小胶质无关）——
**疑似建卡轮次 PMID 手误/错引**。建议另卡（KB6/microglia_repair 线）核修该链；A 档清单已标 ⛔ 不列补。

另：KB8 LACRT 链的 PMID:42777860 为 2026-09-23 刚上线文献（Ocul Surf），EPMC MEDLINE 尚未收录、
NCBI eutils 实证存在——不是假引，补录通道需走 PubMed 源而非 EPMC。

## 7. 红线遵守

零下载（全程仅 EPMC/HEAD 元数据查询与本地只读扫描）；零 LLM 判读；零重建；RAG 库/kb 只读——
输入 sha 前后台账见 ledgers/SHA_READONLY_inputs.txt（papers.jsonl/manifest 逐字未动）。
