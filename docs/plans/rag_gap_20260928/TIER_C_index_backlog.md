# RAGGAP — C 档索引旁挂工程清单（不需重建、不需新语料）

C 档共 **830** 词条行：基因在 v2.1 库内确有 chunk 提及，但词条证据链未链接库内 PMID（链在库外或纯 canonical）。

修复路径（全部旁挂，零重建）：
1. **链回填**：`tier_C_backlog.tsv` 的 `link_candidate_pmids` 即库内支撑论文——词条 JSON 的 evidence 追加 `{"type":"pmid","id":"PMID:...","in_corpus":true}`（照 KB1v2d 先例，改词条不动 chunks/embedding）。
2. **面板字段**：chunk 级 `marker_genes` 列仅 40 基因（v2.1 只建 QA 面板）——若要让 search_literature 的 marker 共现面覆盖词条基因，扩 `panels_v5.json` 后**只需重算该列元数据**（embedding 零重算，v2.2 先例）。
3. **附属器语境缺口另算**：泪腺语境在库内 0 标签（V4 只查量不入库）——lacrimal 词条的语境支撑属 A 档扩容问题，不在本清单。

| 分级 | 行数 | 含义 |
|---|---|---|
| C_strong | 610 | 语境匹配库内论文 ≥3 篇（回填即得强链） |
| C_mid | 220 | 语境匹配 1-2 篇（回填为弱链，可接受） |
| C_ctx_mismatch→A | 74 | 提及但语境错配 → 已按 EPMC 语境判据转入 A/B 档（无一判 B） |
