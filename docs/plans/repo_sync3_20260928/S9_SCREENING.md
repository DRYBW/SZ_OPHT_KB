# S9_SCREENING — v2.4/v2.4.1/v2.4.2 语料 × registry truth 来源同源筛查（前置盘点）

- 卡：t_09e9a4a3 REPOSYNC3 · T8 ｜ 日期=2026-09-28 ｜ 依据=OBLIGRUN_RULING_1 追溯登记（"§9 永久机制由每次重建落盘同源筛查列承接，落 REPOSYNC3 前置盘点"）
- 性质：**只盘点不修库**（票面层排除机制沿 RULING_1 案 A 现行有效；语料层本轮不重建）。
- 筛查体与规则=注册包 §9 冻结件逐字复用（标题级观看列表 + 片段级 own-deposit/指派复核；正则=o4/o7 同源件），血缘=票面 v2.1 lineage registry（`docs/plans/obligrun_20260928/out/FACE_V21_ledger.tsv` 注释行）。脚本=`scripts/t8_s9_screening.py`，机读件=`out/t8_s9_hits.tsv`+`out/t8_s9_stats.json`。

## 一、watchlist（registry truth 来源，机械可判部分）

| study | source_pmid | 证据链 |
|---|---|---|
| chakravarti_GSE218123 | 36712326 | OB-4 v1 三重证据链件（GEO 题名逐字一致+Data Availability 自存+obs.study 直读） |
| lako_adult_GSE155683 | 33865984 | 外部解析补登记（Collin J, Ocul Surf 2021；eutils 只读） |
| 其余 7 study（shi_GSE157474/chen_pub_GSE153515/li_GSE147979/dickman_GSE186433/chen_cornea/chen_limbus/chen_sclera） | None（题名零匹配/无 accession） | 残余限制沿 v1 披露——机械筛查不可判，如实登记不虚构 |

## 二、命中清单（核心发现：两 truth 来源论文在三版语料均全文在库）

| 语料版本 | PMID 36712326 | PMID 33865984 |
|---|---|---|
| v2.4_2026-09 | **在库** 26 chunks；own-deposit 声明段命中 GSE218123；指派句式 2 处 | **在库** 64 chunks；own-deposit GSE155683；指派句式 14 处 |
| v2.4.1_2026-09 | 在库（全量继承零重算，同字节） | 在库（同） |
| v2.4.2_2026-09 | 在库（同） | 在库（同） |

覆盖面账：票面 v2.1 全 33 簇 lit 行现存 11 unique PMID，**11/11 在三版语料均存在全文行**（=检索侧对任一 lit 行可召回其原文 chunk，通名文献属预期；其中 watchlist 命中=上述 2 行）。

跨版本存在矩阵（补测，供口径完整性）：36712326 自 **v2.0（现役默认库）即在库**；33865984 自 v2.1 入库；v2.2–v2.4.2 均继承。=该暴露面并非 v2.4.x 增量引入，而是历史语料基座既有属性。

RAGFIX3 增量面：ra3 准入 103 篇 × watchlist 交集 = **0**（本波新增未扩大同源暴露；且 ra3 四检含"非 HRCA 自引"项）。v2.4.2 papers.jsonl 行数 3884（含历史 0-chunk ghost 15，指针 unique_papers=3869 口径）。

## 三、判定

1. **语料层存在同源全文 = 已披露的结构性暴露面**，非新发缺陷：注册包的循环性防线本就落在**票面层**（§9 两级筛查逐条剔除，RULING_1 案 A 净化面 v2.1 命中集恰 2 行已剔、机械复算全等）+ **判读协议层**（ANNOTATION_PROTOCOL v1.3 消费规则）。检索召回原文≠判读采信——下游席位若引用 watchlist 论文片段作 identity 依据，属协议违规而非语料缺陷。
2. 义务条款承接：本件=OB-4"每次重建落盘同源筛查列"的首次落盘盘点；未来任何语料重建（含 PI 拍板 default 切换波）必须随建随落同名筛查列，watchlist 命中增量>0 即升级上报（禁静默并入）。
3. 不可判残余（7 study 无 source_pmid）：机制盲区沿 v1 披露；若 A04 独立验证线立项，血缘登记先行补齐。
4. 本盘点**未改动任何语料/注册包/票面文件**；线上只读，命中处置=登记。

*REPOSYNC3 T8 产出（2026-09-28）。命中行逐字源=out/t8_s9_hits.tsv；机读统计=out/t8_s9_stats.json；筛查脚本可复跑（依赖 pandas/pyarrow 只读）。*
