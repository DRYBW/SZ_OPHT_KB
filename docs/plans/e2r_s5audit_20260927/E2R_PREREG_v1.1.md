# E2R_PREREG_v1.1 — §2 标题解析算法修订版（其余各节与 v1.0 全文一致，不重复印）

修订时间：2026-09-27 09:2x（v1.0 于 09:13:53 sha 落纸；本修订发生在**任何逐对判读产出（data/e2r_pair_verdicts.tsv 等）生成之前**，
仅基于 6 个标题的方法学试点探针——试点发现 v1.0 §2-B/C 两步存在实现级缺陷，判读结果零生成，故无事后换尺问题。探针证据：
ledgers/api/A_*/B_*/C_*（v1.0 原查询返回，保留不删）。

## v1.0 §2 缺陷诊断（机械事实）
1. norm() 用 `[^a-z0-9]` 剥字符导致变音符丢失：Müller→mller、hiPSC 连字符拆词，短语查询与索引 token 不一致 → 命中恒 0。
2. B 步用"去停用词后前10实词"拼短语——Lucene 短语要求索引 token 连续，删 "of/in/the" 直接破坏连续性 → 命中恒 0。
（实测：v1.0 三步对 2 条真实存在（EuropePMC 可检到 MED 记录）的截断标题全部判 unresolvable。）

## v1.1 §2（替换 v1.0 §2，冻结如下）
预处理 fold(s)=NFKD 去音标转 ASCII；norm(s)=fold 后小写、非字母数字转空格、连续空白折叠。
前缀互含匹配 prefix_ok(存储题T, 候选题C)：norm 全等，或 min(len)≥25 且一方为另一方前缀。
候选记录须 source=MED 且带 pmid 才算可核（v1.0 同）。四步依序，命中即停：
- A：`TITLE:"<fold(T) 全串>"` → prefix_ok 过滤（截断标题 A 步天然失配，由 B 兜）。
- B：取 fold(T) 空格分词；若 len(T)≥118 判"截断存储"，弃最后半个词；取前 16 词原序（含停用词）拼 `TITLE:"<短语>"`。
- C：`TITLE:"w1" AND "w2" ...`——标题实词（长度>3、去停用词、原序前 12 个）交集查询，字段限 TITLE。
- D：同 C 词集但去字段限制并加 `AND SOURCE:MED`。
四步皆空 → unresolvable。空串标题直接 unresolvable 不发 API。每步原始返回落 ledgers/api/<step>_<md5(norm(T))前16>.json。
其余：§0/§1/§3-§9 与 v1.0 逐字同文；§6 验证闸、§7 判读矩阵数字线不动。
