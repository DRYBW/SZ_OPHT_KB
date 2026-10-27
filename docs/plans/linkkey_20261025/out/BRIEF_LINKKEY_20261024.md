# LINKKEY — 引用侧与语料侧建立共同连接键（最高优先）

## 为什么要做
引用记录（`kb/link_registry/LINK_REGISTRY_v1.jsonl`）带 `pmid` 但没有 doi；
语料随件（`literature_db/*/papers.jsonl`）带 `paper_id`/`pmcid`(3,680/3,917)/`doi`，**没有 pmid 字段**。
后果：**"哪篇文献被引为证据、哪些文献从未被触达"机器答不出来**。协调者实测：按规范化全标题只能对上 186/803（23.2%），放宽到 40 字前缀 263/803（32.8%）。

## 交付
1. `CONNECT_KEY_v1.tsv`：803 篇被引论文 × 语料条目对照，列 = pmid / 对上所用键（pmid|pmcid|doi|title_norm）/ 语料 paper_id / title / year / journal / 匹配等级（exact|normalized|fuzzy|unmatched）。
2. `UNMATCHED_v1.tsv`：未对上清单 + **逐条原因分类**（标题写法差异 / 语料无此文 / 预印本或全文缺 / 其他），禁止只给总数。
3. `CORPUS_TOUCH_v1.tsv`：语料全部论文分两档 = 「被至少一个条目引为证据」/「未被引用」，各带 pmid 可用性标注。
4. 可复跑脚本 + 哈希清单 + 一段口径说明（对上率是多少、为什么，不许报"100%"）。

## 判据
- 对不上率必须给出；每一行 unmatched 必须有 reason 非空。
- 对上率在两种口径下并报：严格（规范化标题全等）与放宽（前缀/DOI/PMCID），不许只报高的那个。

红线（全部适用）
- 零下载、零 GPU；只读现有盘上件；不 move 只 copy；冻结件不回改。
- 资源纪律：重计算 systemd-run MemoryMax 托管；并行 ≤min(8, cpu/2)；读取必须 backed（禁整文件无界读）。
- 禁 push；本地 commit 即可，commit 由协调者统一推。
- 一致性判据一律"机器可查"：构建/检查时从盘上现读，读到的值与声明值不一致就 FAIL，禁人工解释放行。
- 禁补零、禁静默丢弃：对不上/缺失的条目必须逐条登记原因分类，写进产物。
- worker 自报不算验收：协调者将亲自重跑并逐节点比对。
