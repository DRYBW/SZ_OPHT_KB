# EUTILS_ATTRIBUTION — eutils/建链通道缺陷取证归因（KBCHAIN 任务 4）

卡 t_3a35a2cc ｜ 数据 = out/MISQUOTE_MECHANISM.tsv + out/LEDGER_XREF.tsv + ledgers/recs_merged.json
判读人 = AGENT_ROLE（人工升级判读，逐条理由见 out/FINAL_adjudications.tsv）

## 1. 确诊误引 20 条的共同事实：**全部 off-ledger（建链当日零痕迹）**
20/20 确诊错配的 PMID 都不在 KB7 当日任何检索账本里（kb7_lit_hits.tsv、efetch_kb7/* PMIDS 行、
W4b 台账、k9 PMID_LEDGER、epmc_raw_v2）。对照：
- **KB9 新条链 21 条全检误引 0%**——该代建链把每次 EPMC 查询的**原始响应**留了账（ledgers/epmc_raw_v2/38 件 +
  PMID_LEDGER.tsv 逐条 query/candidates/titles），PMID 从留账响应里选取，天然可回溯。
- **E2R 白名单 169 链（100 对）全检误引 0%**（95%CI 上界 2.2%）——题名与 PMID 成对存储，
  本卡 round-trip 复核（EXT_ID 题录 vs 存储题名）全过（1 例假阴性=HTML 标记残留，人工修正）。

结论：**误引不是"eutils 检索本身给出错号"，而是"检索结果→决策表的手抄转录环节无 round-trip 校验"**。
KB7-W4/W4b 把"esearch top-5 → efetch 摘要块 → best 文本"记了账，但**摘要块与其 PMID 的对应关系从未落表**
（kb7_w4b_eutils.py 只存 `best=blocks[?][:300]` 文本，不存块↔id 映射；`es_*.json` 写入行被 `if False` 短路禁用），
决策表 kb7_decisions.json 的 PMID 列系事后转录，转录出错不可检出。

## 2. 四型机制分型（MISQUOTE_MECHANISM.tsv 量化；注：PMID 前 2 位为年代段无区分度，A 型阈值取公共前缀≥3）
| 型 | 判据 | 条数 | 典型例 |
|---|---|---|---|
| A 数字变异型 | 错号与当日合法 idlist 某号**最长公共前缀≥3**（尾数变异，变异号恰为另一真实文献） | 8 | COX4I2 35929074→3592**0172**(前4同)；PRSS56 29529029→295**61967**；MFRP 40249779→402**28796**；VIP 38066110→380**87179**；TAL1 28671693→286**96901**；OLR1 40140148→401**53135**；ITGAX 41683913→416**65199**；GPR179 42106701→421**24641** |
| A′ 弱同形 | 前缀=2 且账本含与 W4b"best 块"文本对应的号 | 2 | UCHL1（W4b best=块3 Dev Dyn 2014 = 24339342，记录 24449362）；HMGCS2（38857822→38749583） |
| B 搬运替换型 | note 与当日账本某**真实题录文本呼应≥3 词**，但记录 PMID 为另一号 | 4 | OR51E2：note≈账本命中 29249973"β-ionone Regulates RPE Cell…"（W4a+W4b 双账在案），记录号 36167259=食品化学精油封装；FDCSP：note"Corneal and Conjunctival expression profiles"呼应 42589107，记录号=35021166（物理文）；LCN2/CXCL17 同型 |
| C 裸回填无账型 | 无前缀同形且无 note 账本呼应（face 时代"本地 human×N"通道，检索过程整体无留账） | 6 | KRT19 38528295（真文可由题面找回=25722207，RAGFIX 成果）；AQP5 35590283；KRT13 33503899；SCGB3A1 37381815；CLIC6 39385205；CHAT 41037735 |

补充指纹：**同一错号跨链复用**——35021166（CuI 物理论文）同时挂在 LCN2 和 FDCSP 两条链上 =
一次转录污染成对传播，非独立检索错误。

## 3. eutils 通道记录面缺陷（C1 定义必须双通道）
- **PMID:28696901（TAL1 错号）**：NCBI esummary 返回**空题录记录**（title/journal 全空），efetch 无正文，
  EPMC 无 MED 记录 = "可解析但无内容"的残损号——单看 eutils 会误判"合法"。
- 全库 2,877 号通道分布：eutils+EPMC 双通道 2,874；仅 eutils 3（28696901 残损、42124641=预印本
  （EPMC SRC:MED 不收录 PPR-only）、42777860=RAGFIX 曾称"EPMC 已收录 MED 题录"而本卡实测 EPMC 仍无——
  **通道状态会漂移**）。仅 EPMC 0。
- **v5 时代 pmid_context 存储缺陷（120 实例）复现确认**：记录字段只有 (query,n_hits,top_titles)，
  从未存 PMID——引用不可机检，E2R 已定性；本卡将 120 条登记为 NOT_CHECKABLE 不入误引分母。

## 4. 给 RAGFIX2 / 未来建库卡的修复建议（告诫实证化）
1. **禁裸用 eutils 通道回填**：任何 esearch/efetch 结果转写为引用链，必须携带该次查询的**原始响应留账**
   （仿 KB9 epmc_raw_v2 格式），且落链时做 **round-trip 校验**：把写入的 PMID 重新题录解析，
   与留账题名逐词比对，不一致即拒绝写入。KB9/E2R 两面的 0% 实测支持该规程有效。
2. **摘要块↔PMID 映射强制落表**：efetch 多 id 摘要必须按 id 分块存储（retmode=xml 逐 PMID 解析），
   禁止"取第 k 块文本 + 记第 j 个 id"的分离转录。
3. **本地/RAG 检索通道（face 时代 human×N 型）同样强制留账**，否则事后不可审计（本卡 C 型 6 条无法找回原文）。
4. **C1 可解析判据用双通道**：eutils esummary 标题非空 **或** EPMC SRC:MED 有记录；仅单通道命中者打
   channel_note（预印本/残损记录/通道漂移三种亚型本卡各有实例）。
5. 检索式加物种与组织约束（k9 Melanocyte 线教训）：query `GENE AND (melanocyte|melanoma|...)` 无
   human/ocular 限定时，题录级合法但语境级不特异——本卡 8 条 k9 链因此降 weak（非误引，证据强度问题）。
