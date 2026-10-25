# CITTITLE — citation records carry no title: 缺陷、修法、口径与反事实证明（v1）

卡：`t_d8e7f2d4`（board `pi-briefing`，执行者 `pi-chief`）
brief：`/mnt/D/EyeKB/plans/consistency_20261024/BRIEF_CITTITLE_20261025.md`（副本 `out/`）
交付目录：`/home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025/`
构造现场镜像：`/mnt/D/EyeKB/plans/consistency_20261024/cittitle_out/`（同一套件，盘上两份）

> 一句话：**引用侧的"对上 30%"不是两库分歧，是引用侧自己没落题名。**
> 冻结 registry 的 3,993 条引用记录里 2,429 条题名栏为空、509 条题名是语料全题名的
> 120 字符前缀；825 篇被引论文**全部**在语料里、题名齐全。补出 `title_full/doi/pmcid`
> 三列之后，同一套题名口径下严格对上是 825/825。
> **但 825/825 是同源回填的构造结果，不构成"两库一致"的证据**——非圆形证据在 §4.3。

---

## 1 缺陷本体（源码级，行号现读）

权威树 = `/home/ubuntu/EYEKB_REPO`（LINKKEY 卡 §5 已钉；本卡全部命令只对该树）。

`kb/link_registry/scripts/build_link_registry.py` 在**两条**引用写入路径上写题名：

| # | 位置（改前行号） | 写法 | 后果 |
|---|---|---|---|
| 1 | `:232`（检索路线 `_collect`） | `"title": (hit.get("title") or "")[:120]` | 题名被硬截到 120 字符 |
| 2 | `:299`（全文扫描 gene-index 路线 `_citation`） | `"title": ""` | 题名栏**根本没有值** |

实测（冻结件现读，非引用他人报告）：

| 读数 | 值 |
|---|---|
| registry 行数 / 字节 / sha256 | 165 / 2,498,557 / `a04be7711131225129ed6a8f6d3cb08862216c9187307a8a2b663b7bdd15e9cf` |
| 引用记录总数 | **3,993** |
| 去重被引论文 | **825** |
| 题名栏为空 | **2,429** 条（= `evidence_source = "gene index (full text)"` 的 2,429 条，逐条对齐） |
| 题名长度恰为 120 | **511** 条 = 509 条真截断（是语料全题名的前缀）+ **2 条**语料题名本身恰 120 字 |
| 本来就完整的题名 | **1,053** 条 |
| `doi` / `pmcid` 列 | **0 条**携带（引用侧结构性缺失，LINKKEY 已实测 0/803） |

**语料侧不欠任何东西**：825 篇被引 `pmid` 在**三份语料拷贝**里都能按 `paper_id == pmid`
精确命中（缺席 0）。所以"看起来像两库对不上"完全是引用侧的自伤。

---

## 2 修法（builder 层面，默认路由零改动）

`build_link_registry.py` 新增两件、改两处：

1. `corpus_meta_index()` — 读语料 `papers.jsonl`，建 `paper_id -> {title, doi, pmcid, is_preprint}`。
   解析链与引用自身的来源一致：`EYEKB_DB_DIR` → `mcp_server/eyekb_core._default_db_dir()`
   （指针 `role:default`，**即默认路由**）→ 仓内 G2 slim 库。**只读，不改默认路由。**
2. `citation_field(meta, pmid, key, fallback)` — 取语料字段，取不到才回落到检索 hit 的值。
3. 检索路线题名：改为 `citation_field(cmeta, pmid, "title", hit.get("title"))`（**不再截断**），
   并补 `doi` / `pmcid`。
4. gene-index 路线题名：改为同一函数（**不再写空**），并补 `doi` / `pmcid`。
5. 收尾新增一行读数：`citation titles: records=… distinct_papers=… resolved=… unresolved=…`
   —— 未解析数一律打印，**不许静默留空**。

字段语义（三列，brief 指定）：

| 列 | 语义 | 说明 |
|---|---|---|
| `title` | 论文完整题名（**不截断**） | 修后 builder 与 drop-in 版 registry 用此名 |
| `title_full` | 同上，独立列名 | anchor 版 registry 用此名（`title` 保持冻结字节，见 §3） |
| `doi` / `pmcid` | 语料同名字段原值 | 语料缺则该列 = `""`（本卡实测：825 篇里 doi 缺 0、pmcid 缺 5） |

**已有字段零改动**：`journal` / `year` / `tissues` / `marker_genes` / `gene_match` /
`genes_in_text` / `evidence_locator` / `evidence_source` / `relevance` / `chunk` 等全部原样。

---

## 3 交付件与不变量

| 件 | 字节 | sha256（现取） | 不变量 |
|---|---|---|---|
| `out/LINK_REGISTRY_v2_cittitle.jsonl`（**anchor 版**） | 3,259,193 | `0d49ee04dc0a940d…` | 去掉三列后**逐行逐字节等于**冻结 registry |
| `out/LINK_REGISTRY_v2_cittitle_dropin.jsonl`（**drop-in 版**） | 3,553,292 | `ba5e71b5b19b4a55…` | = anchor 版按 `title := title_full` 逐行导出（**自身不可逆，故不承担字节锚**） |
| `pre_images/LINK_REGISTRY_v1.jsonl.pre_cittitle` | 2,498,557 | `a04be771…` | 冻结件本体，原样保留（**红线：冻结件不回改**） |

- **旧件并排保留 + 哈希留档**：冻结 registry 一字节未改（`a04be771…` 未变），新件是新文件。
- **三列插入位置**：每条形如 `…"title": …, "title_full": …, "doi": …, "pmcid": …, "journal": …`，
  插在 `title` 之后 ⇒ 删除三列即恢复原 key 顺序 ⇒ 反序列化回原行字节。
  这条在 build 与 verify 两条实现路径上**逐行断言**，不是散文声明。
- **两条 registry 变体的用法**：消费方要"读 `title` 就是完整题名" ⇒ 用 drop-in；
  要"与冻结件逐字节可核" ⇒ 用 anchor 版。**两个都不覆盖冻结件**（是否转正属协调者裁决，
  本卡登记为"未转正、不静默推进"）。

---

## 4 反事实证明

### 4.1 改前 / 改后（口径并报，禁只报高的那个）

单位 = **去重被引论文**（分母 825，与 LINKKEY 卡分母口径同族）；upstream 审原件
`LINKKEY_out/UNMATCHED_v1.tsv` 里按 pmid 取"最长非空题名"的规则沿用。

| 口径 | 规范化 | 改前对上 | 改前率 | 改后对上 | 改后率 |
|---|---|---|---|---|---|
| **A 严格**（规范化全等） | N1 原样 | **247 / 825** | **29.94 %** | 825 / 825 | 100.00 % |
| **A 严格** | N2 去展示标记 | **248 / 825** | **30.06 %** | 825 / 825 | 100.00 % |
| **B 放宽**（前 40 字前缀） | N1 原样 | **369 / 825** | **44.73 %** | 825 / 825 | 100.00 % |
| **B 放宽** | N2 去展示标记 | **370 / 825** | **44.85 %** | 825 / 825 | 100.00 % |

- N1 = NFKC + 小写 + 非字母数字折叠空格（LINKKEY 口径）。
- N2 = N1 之前先剥展示标记（HTML 标签 `<i>…</i>`、HTML 实体 `&lt;i&gt;…`、Unicode 破折号
  `‐ – —`、多余空白）。语料 3,884 行里有 41 行题名含实体。
- **改后 100 % 的成色必须说清**：引用侧 `title_full` 是**从同一份语料**按
  `paper_id == pmid` 回填的，再拿它去和这份语料比，**必然 100 %**。这是"修好了键"的读数，
  **不是**"两库一致"的证据。所以才要下面 §4.3。

### 4.2 逐条原因（改前未对上者，按口径展开；每行都有 reason，禁只给总数）

`out/UNMATCHED_PRE_v1.tsv` = **2,066 行**（A/N1 578 + A/N2 577 + B/N1 456 + B/N2 455），
每行 `reason_code` 与 `reason_text` 均非空（机械核对：空值行 0）。

| 口径 | 未对上 | 原因分解 |
|---|---|---|
| A / N1 | 578 | `TITLE_EMPTY_CITED` **455** ＋ `TITLE_CAPPED_120` **122** ＋ `TITLE_DISPLAY_ARTIFACT` **1** |
| A / N2 | 577 | `TITLE_EMPTY_CITED` 455 ＋ `TITLE_CAPPED_120` 122 |
| B / N1 | 456 | `TITLE_EMPTY_CITED` 455 ＋ `TITLE_CAPPED_120` 1（那 1 条即展示标记那条） |
| B / N2 | 455 | `TITLE_EMPTY_CITED` **455**（前 40 字口径下，截断与展示标记都够不着） |

**关键诚实点：`TITLE_OTHER_DIFF`（真正写法差异）在四个口径下都是 0 行。**
也就是说，brief 担心的"两库对不上"在 825 篇里**一例都没有**；全部失配都是引用侧的两处形态缺陷
（外加 1 条纯展示标记）。

改后未对上 = `out/UNMATCHED_POSTFIX_v1.tsv` = **0 行**（空表 = 无行可登，不是静默丢弃）。

记录级账（3,993 条逐条）：`out/CITATION_TITLE_LEDGER_v1.tsv`
列含 `pre_class`（`EMPTY` 2,429 / `CAPPED_120` 509 / `GENUINE_120` 2 / `FULL_OK` 1,053）、
`pre_strict_match`、`post_strict_match`、`doi_present`、`pmcid_present`。
逐篇视图：`out/CITATION_TITLE_BY_PAPER_v1.tsv`（825 行，带 reason_code + 两侧原文）。

### 4.3 非圆形证据（改后 100 % 不算证据，这三样才算）

| # | 控制 | 读数 | 它排除了什么 |
|---|---|---|---|
| ① | **换语料**：用拷贝 1 回填的题名，去和拷贝 2 / 拷贝 3 的题名比 | 三个口径 × 两个拷贝 **全部同数**（A 247 / B 369；N2 下 A 248 / B 370） | 排除"回填出来的题名只在这一份拷贝里成立" |
| ② | **同 join 的字段控制**：期刊一致 / 年份一致 | 年份 **825/825**；期刊 **820/825**——5 条差额**逐条**是 `PPR_*` 预印本（引用侧写 `bioRxiv/medRxiv`，语料该字段为空），不是错配 | 排除"pmid ↔ paper_id 接错了" |
| ③ | **改前本来就完整的题名**（非空、非 120）与语料严格全等 | **243 / 243** | 这批题名是**冻结 builder** 写的、不是本卡写的；它们全对 ⇒ "低对上率"确实只由缺陷造成 |

另：**改前被截断的题名在 40 字前缀口径下与语料相等 = 115 / 115** —— 即那 115 篇确实是
"完整题名的前 120 字"，证明截断是机械截断而非内容不同。

### 4.4 与 brief 数字的对账（口径差异登记，不是任一方错）

brief 写「884 条题名栏为空 / 116 条硬截断 / 2 条预印本 / 1 条题名被改写，1,003 条
全部 reachable_by_pmid=yes」。**这四个数是 LINKKEY 审计件 `UNMATCHED_v1.tsv` 的 reason_code
频次**（该文件 1,003 行 = A 口径 560 行 + B 口径 443 行），不是 registry 侧记录数：

| brief 数 | 来源（现读交叉表） |
|---|---|
| 884 空 | A 口径 442 + B 口径 442 |
| 116 截断 | A 口径 115 + B 口径 1 |
| 2 预印本 / 1 改写 | 均在 A 口径 |

**registry 侧现读是另一组数**（更大）：3,993 条引用记录里 2,429 条为空、509 条真截断
（去重到论文层则是 455 篇空、122 篇"最长题名即截断"）。两组数说的是同一件事的两个粒度，
本卡两组并报，**不把其中一组当作另一组的校验**。另：被引 `PPR_*` id 现读 **5 个**
（LINKKEY 当时 2 个），全部在语料中解析成功。

---

## 5 本卡**不主张**什么（防过度解读）

- ❌ 不主张"两库题名一致率 100 %"。改后 100 % 是同源回填的构造结果（§4.1 末），
  非圆形读数只有 §4.3 那三样。
- ❌ 不主张"引文证据质量"。本卡只回答"题名键能不能用"，不回答"引对了没有"。
- ❌ 不主张"冻结 registry 已修好"。**冻结件一字节未改**；修好的键在新件与 builder 里。
- ❌ 不主张 DOI/PMCID 能独立校验引用身份：那两列也是从同一份语料取的，属同一血缘；
  它们只是"引文可点开"的展示字段，不是第三方核验。
- ❌ 不主张"改前后数字可比于 LINKKEY 的 243/803（30.26 %）与 360/803（44.83 %）"：
  分母不同（825 vs 803，registry 在此期间被 CL56WIRE 重建过）、规范化细则与"同一 pmid
  取哪条题名"的选择也不同，**登记为口径差异**；两组数同量级、同成因。

---

## 6 复跑方式（可复跑脚本 + 哈希清单）

```bash
cd /home/ubuntu/EYEKB_REPO/docs/plans/cittitle_20261025

python3 scripts/backfill_citation_meta.py \
    --expect-frozen-sha a04be7711131225129ed6a8f6d3cb08862216c9187307a8a2b663b7bdd15e9cf
python3 scripts/counterfactual_titles.py     # 反事实证明 + 逐条原因 + 非圆形控制
python3 scripts/verify_deliverables.py       # 独立复算器：12 项，全 PASS 退出 0
python3 scripts/g12_controls.py              # G12 反向控制电池（真树植入→复原→对 sha）

cd /home/ubuntu/EYEKB_REPO
python3 tests/gate_cittitle_meta.py          # G12 单门，rc=0
/bin/bash tests/run_gates.sh                 # 一键链 G3→G12
cd docs/plans/cittitle_20261025 && sha256sum -c out/MANIFEST.sha256
```

`verify_deliverables.py` 是**给协调者亲自重跑并逐节点比对用的**：它不采信本目录任何自述数字，
规范化/截断判定/原因分类/JSON 处理**各自重写一遍**（不 import `cittitle_common.py`），
只从输入件与已落盘表现读复算 **12 项**（输入 sha、行数、字节锚、drop-in 导出、三列齐备、
题名==语料、8 个口径臂重算、unmatched 行/原因合计、逐条账、字段控制、预印本、缺陷现场计数）。

红线遵守：零下载 / 零 GPU / 零网络；只读语料（三份拷贝全部只读，未 move 未改）；
不改默认路由（`EYEKB_DB_DIR`、指针 `role:default`、`search_literature` 全未动）；不 push；
冻结件零回改；全部数字现读现算，未引用旧报告数字。