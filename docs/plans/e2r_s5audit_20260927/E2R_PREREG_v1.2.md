# E2R_PREREG_v1.2 — §2 追加标题预处理（_year 前缀剥离）；其余与 v1.1 逐字一致

发现（机械事实，v1.1 探针期实测）：v5 pmid_context 存储的 top_titles 有两种形态——
①裸题名（103/145 唯一标题）；②`YYYY:题名` 带年份前缀（42/145）。v1.1 四步对②一律 4 发全空判
unresolvable——前缀破坏短语连续性与前缀匹配，属实现级缺陷而非证据缺失。
v1.1 运行在判读产物生成前被我方主动终止（data/e2r_title_resolution.jsonl 仅含 11 条污染缓存，
已更名留档 data/e2r_title_resolution.v1.1-defective.jsonl.bak，不作任何判读输入）。

## v1.2 §2 增补（插入 v1.1 §2 四步之前）
预处理 strip_year(T)：若 T 匹配 `^\d{4}[:：]\s*` → 剥离前缀，记录 year_hint；否则原样。
四步 A/B/C/D、prefix_match、MED+pmid 可核定义、空题规则全部沿用 v1.1 不变，作用对象改为 strip_year(T)。
判读口径不变（§5 四态、§7 判读矩阵数字线不动）。
验证锚（试点实证）：①剥前缀 `Non-coding RNAs in the development of sensory organs and related diseases.`
→ MED 23588489 pubYear=2013；②`MicroRNAs in the Neural Retina.` → MED 24745005 pubYear=2014；
③裸题 NETO1 title1 → 40660409 hrca_self=true（v1.0 已证）。
任一锚不中 → 停工修算法，不出判读。
