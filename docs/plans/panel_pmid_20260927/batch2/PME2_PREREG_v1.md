# PME2_PREREG_v1 — 面板证据链补录第二批预注册（跑数前落纸）

卡：t_95cbb3ec（EyeKB-PME2）。放行件：USER_DIRECTIVE_20260927_scoring_wave.md 追加一 D7。
任务书：BRIEF_PME2.md。**本文件 sha 先于任何检索请求落 ledgers/sha_prereg.txt。**

## 0. 口径头（PI 锁定，2026-09-27 D7）
- **"expressed in <该细胞类型>" 算 membership 型支持 = 中等档，为现行正式口径**（marker 词表含
  express，与第一批 PREREG §4 一致；类特异严格档不再议为默认，若未来收紧须全库对称重判并另卡）。
- 判读矩阵 row1 义务继承第一批（PME_NOTE.md §第二批清单）。
- E2R 告诫继承：**pmid_context 共现通道不用于补录**（本卡零引用 pmid_context 字段/通道）。

## 1. 输入与领地
- 对象：out/batch2_backlog.tsv 的 103 个非 strong 键（50 weak + 53 none；class|gene 键级）。
  其中 v6 repair 统计派生基因（第一批账 grade=none 者）按任务书要求纳入复扫，
  但第二检索式对 **全部 103 键统一施加**（对称性优先于选择性，防"挑键开后门"）。
- 第一批 sidecar/引擎/账件已 copy 至 in_b1_snapshot/（sha 与一批原件逐一同值，见 sha_pre.txt）；
  一批原件、kb/、E2/E2R/E3 目录：**只读**，PRE/POST sha 台账 ledgers/sha_pre.txt（81 条）/ sha_post.txt。
- 全部产物只落 batch2/。零 LLM 判读（分级=规则引擎；worker 自审仅对升档证据句过目做降级修正，
  逐条留痕 ledgers/audit_fixes_v2.tsv，原始引擎判定不掩——与第一批 §PREREG 同构）。
- 摘要级检索零全文下载；请求量 ~103×2 遍 + UniProt 别名核查 <600 次，远低于 1GB 停卡线。

## 2. 第二检索式 = 类同义词扩展 + 基因蛋白别名（规则机械、全表对称）

### 2.1 类同义词扩展表（全部 29 类逐一列，"—" = 无新增；扩词仅限类名的词汇变体，禁引入新生物学概念）
| 类 | 新增查询短语 / doc_re 扩展 |
|---|---|
| Rod | "rod outer segment" |
| Cone | "cone outer segment" |
| BC | "rod bipolar cell" / "cone bipolar cell" / "ON bipolar" / "OFF bipolar" |
| AC | "amacrine cell" / "amacrine neuron" / "retinal amacrine" |
| HC | "retinal horizontal cell" |
| RGC | "retinal ganglion neuron" |
| MG | "muller glial cell" / "retinal muller" |
| Astro / Microglia / Endo / Endo_Patho / Pericyte / Fibroblast / Myofibroblast / Mono_Classical / Mono_Nonclassical / Mac_Tissue / cDC1 / cDC2 / pDC / T / NK / B / Plasma / Granulocyte / Proliferating / APC_MHCII_high | —（APC 类使用第一批 A5 修正后的去循环 doc_re，属继承非新增） |
| SMC | doc_re 增 `smooth\s+muscle`（membership 语境，DES/MYL9/TPM1 常写作 smooth muscle actin 而非 cell） |
| Mac_DAM_LAM | doc_re 增 `\bLAM\b[^.]{0,60}macrophage`（对称于已有 DAM 形） |

### 2.2 基因别名表（对 103 键的全部 unique 基因统一施加，同端点同参数）
- 来源：UniProt REST（rest.uniprot.org，human + reviewed:true，fields=accession,genes,protein_name）。
  取：① gene synonyms（entry.genes[].synonyms[].value，仅取 primaryGeneName==目标基因的条目）；
  ② 蛋白名 RecName 的 Full 与 Short 字段。逐条留档 ledgers/raw_uniprot/<GENE>.json（含 URL），可审计。
- 机械过滤（全表统一，禁逐键手工增删）：
  F1 长度 ≥4 字符；F2 字符集 `^[A-Za-z0-9][A-Za-z0-9 ,.'/()-]*$`；
  F3 符号形别名（`^[A-Z][A-Z0-9-]{2,}$`）须过冲突核查：UniProt `gene_exact:<alias> AND human AND reviewed`
     返回条目主符号 ≠ 目标基因 → 弃用；
  F4 别名同时是本面板 103 键另一基因的主符号/已留别名 → 双方弃用（内部冲突）；
  F5 含 "putative/uncharacterized/hypothetical" 的名称弃用。
- 别名表落盘 data/alias_gene_v2.tsv（gene, alias, source[uniprot_syn|uniprot_recname_full|uniprot_recname_short], kept[0/1], drop_reason, url），
  留弃全登记，可复核。

### 2.3 检索与分级
- 查询：`(类短语∪扩展短语) AND (GENE OR "别名1" OR "别名2" ...) AND (SRC:MED)`；
  多词别名加双引号做短语匹配。
- 双遍复用（继承 A1）：遍1 relevance；非 strong 再跑遍2 sort=CITED。逐键 raw 留 ledgers/raw2/<类>__<基因>.json。
- 分级规则 = 第一批 PREREG §4 原文，仅 G、C 的定义扩展为：
  G' = 句含 `基因符号 OR 任一保留别名`（词边界、大小写不敏感；CS_GENES 集合继承）；
  C' = 句含扩展后 doc_re；M 不变（marker 词表一字不加）。
  strong/weak/none 判据结构与第一批完全同构（单句 G'∧C'∧M / 文档级 G'∧C' / 查无）。
- **禁软证据升档**：升 strong 必须有可复核证据句；"none 维持诚实阴性"合法。

## 3. 终态合并与两批合计读数
- 键级 combined_final = max(一批 final_grade, 二批 final_grade)，序 strong>weak>none；
  两批 grade、二批自审修正、来源通道（route1/route2）全字段并记，不掩任何原判。
- 行级（338）按 (class,gene) 回填 combined_final → 两批合计可核链覆盖终读：
  **可核强链 = E2 基线文件内可核 30 + 两批合计 strong 行数；/567 对**。
- 残余 none 定性（两态，机械判据）：四遍（批1两遍+批2两遍）总候选 hit 数=0 → "真缺文献"；
  >0 但无文档级 G'∧C' 共现 → "摘要级不可核"（断言可能在全文/图注）。逐键登记。
- E2 任何数字不改；对照件仅引用 E2_VERDICT §B 面板侧基账（30/199/338）。

## 4. 红线（重申）
- 只写 batch2/；E2/E2R/kb/、一批原件字节不动（POST sha 断言）。
- 零 LLM 判读调用；零全文下载；pmid_context 通道零使用。
- 完成或遇阻必须落卡；分批落盘留痕。

---
## 修正补记（先于跑数）
- **A1' sort 参数修正（2026-09-27 12:5x，发现于一键冒烟）**：一批引擎沿用 `&sort=CITED` 裸形，实测被 EBI 全线
  503 拒（`sort=PCT`/`CITED_AND_PCT`/小写同灭）；官方文档正确格式为 `sort=CITED desc`（或 query 后缀 `sort_cited:y`），
  实测 200 且按引用量降序返回。**取证连带发现：一批 ledgers/raw/ 全部 84 个触发二遍的键 raw2 皆 null（error2=503）——
  一批 A1"双遍"实际从未生效，其账=单遍 relevance 口径**。一批数字不改（登记于 PME2_NOTE 事实节），
  二批起二遍以修正格式真实执行。双遍语义本身不变（继承一批 A1）。
