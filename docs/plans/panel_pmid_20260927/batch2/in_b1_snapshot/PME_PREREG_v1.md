# PME_PREREG_v1 — 面板证据链补录第一批预注册（跑数前落纸）

卡：t_f16d4e9f（PME）。放行件：/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md（D4 行）。
任务书：BRIEF_PME.md（本目录）。判读矩阵继承任务书 §判读矩阵，不改。

## 1. 输入与领地
- 对象：E2 data/e2_gene_panel_pmid.tsv 中 explicit_pmids 空 且 axis_members 空 的 338 行（库,类,基因），
  机械提取条件 `NR>1 && $4=="" && $10==""`（= e2_matrix_rows_summary.tsv no_record 列合计 338，双路核对一致）。
- 检索键去重：按 (canonical class, gene) 去重 = 280 键；结果按行回填 338 账。
- 与 E2R 无重叠核对：338 行中 pcx_ext='Y' 行数 = 0（awk 实测，登记 ledgers/e2r_overlap_check.txt）。E2R 的 120 对全部在 external/axis 侧。
- kb/、mcp_server/、E1/E2 目录、e2r/e3/kb9 三卡目录：只读 + PRE/POST sha 台账（ledgers/sha_pre.txt / sha_post.txt）。
- 全部产物只落本目录。零 LLM 判读调用（分级=规则引擎，worker 只自审 strong 行，修正逐条留痕不掩 raw）。

## 2. 检索规则（冻结）
- 端点：Europe PMC REST search。`format=json, resultType=core, pageSize=10, SRC:MED`（仅 PubMed 摘要级；不做全文获取；PMID 可解析为收录前提）。
- 查询：`(类同义词短语 OR ...) AND GENE`，同义词表见 §3（冻结，凭记忆/临时加词禁止）。
- 每键原始返回逐对留档：ledgers/raw/<类>__<基因>.json（含请求 URL）。
- 节流：请求间隔 ≥0.35s；总请求 280，预计 <10 分钟；下载仅摘要级 JSON，量级 <50MB，远低于 1GB 停卡线。

## 3. 类同义词表（canonical class → 查询短语 | 文档级 doc_re 要点）
| 类 | 查询短语 | 备注/护栏 |
|---|---|---|
| Rod | "rod photoreceptor" OR "rod cell" | doc_re 需 rod+photoreceptor/rod cell |
| Cone | "cone photoreceptor" OR "cone cell" | |
| BC | "retinal bipolar cell" OR "bipolar cell" | 护栏：doc 含 bipolar disorder 且无 retina/retinal/photoreceptor/amacrine/inner nuclear → 类判不成立 |
| AC | amacrine | |
| HC | "horizontal cell" | |
| RGC | "retinal ganglion cell" OR RGC | |
| MG | "muller glia" OR "muller cell" OR "Mueller glia" | Müller glia（视网膜）|
| Astro | astrocyte | |
| Microglia | microglia OR microglial | |
| Endo | endothelial cell OR endothelium | |
| Endo_Patho | neovascular endothelial OR tumor endothelial OR endothelial activation | |
| Pericyte | pericyte | |
| SMC | "smooth muscle cell" | |
| Fibroblast | fibroblast | |
| Myofibroblast | myofibroblast | |
| Mono_Classical | "classical monocyte" OR "monocyte subsets" OR "CD14+ monocyte" | 护栏：负向 (?<!non-)classical |
| Mono_Nonclassical | "nonclassical monocyte" OR "patrolling monocyte" | |
| Mac_Tissue | "tissue macrophage" OR "resident macrophage" OR macrophage | 通用 macrophage 语境可入类，strong 仍需句级 marker 词 |
| Mac_DAM_LAM | "disease-associated macrophage" OR "lipid-associated macrophage" | |
| APC_MHCII_high | "MHC class II" OR "antigen-presenting cell" OR HLA-DR | |
| cDC1 | cDC1 OR "type 1 conventional dendritic" OR "cross-presenting dendritic" | |
| cDC2 | cDC2 OR "type 2 conventional dendritic" | |
| pDC | "plasmacytoid dendritic cell" OR pDC | |
| T | "T cell" OR "T lymphocyte" | |
| NK | "natural killer cell" OR "NK cell" | |
| B | "B cell" OR "B lymphocyte" | |
| Plasma | "plasma cell" | |
| Granulocyte | granulocyte OR neutrophil | |
| Proliferating | proliferation OR "proliferating cell" | strong 需句内含基因+proliferat+marker 词（"调控增殖"类句不得升 strong——marker 词表不含 regulat/affect）|

## 4. 分级规则（冻结，逐句机械）
候选 hit = 返回结果中**有 PMID** 的记录（无 PMID 的 PMC-only 记录不认账）。
文本单元 = title 按一句 + abstractText 按 [.?;!]\s 切句。
- G = doc 句含基因符号 `\bGENE\b`（大小写不敏感；覆盖表：CAMP 强制大小写敏感 `\bCAMP\b` 防 cAMP 误配）。
- C = 句含类 doc_re；M = 句含 marker 词 `marker|specific|express|define|label|identif|characteris|signature|hallmark|canonical|positive|stain`。
- **strong**：≥1 候选 hit 存在单句同时满足 G∧C∧M。记录该句（≤2 条 hit）。
- **weak**：非 strong，且 ≥1 候选 hit 文档级 G∧C 共现（或 G∧M 句共现且 C 在文档他处）。记录 PMID+标题，证据句可为空。
- **none**：查无（0 候选 hit 或无任何 G∧C 共现）。**诚实阴性合法**，禁软证据冒充 strong。
- worker 自审：全部 strong 行的证据句逐行过目；判定不成立的改 none/weak，原判定与修正均留 ledgers/strong_selfaudit.tsv，raw 不掩。

## 5. 分批（v4.1 八类教科书强锚优先）
- batch1 = retina 库 8 类（Rod/Cone/BC/AC/HC/RGC/MG/Astro）涉及的 unique 键（71 键）。
- batch2 = retina_interneuron / retina_v6 增量键。
- batch3 = membrane 全部键。
- batch4 = face_v6 增量键（Pericyte/SMC）。
每批落盘留痕；账按 338 行全量。

## 6. 产出
- out/evidence_chain_supplement_v1.json（sidecar 旁挂新文件；kb/ 字节不动；格式对齐 markers_cl_alignment_v1.json 的可回溯要求：directive/prereg sha/method/逐键证据）。
- out/pme_accounts.tsv（338 行逐对账：lib, class, gene, grade, pmids, evidence, raw 文件）。
- out/pme_summary.json（strong/weak/none 计数 + 判读矩阵落点）。
- out/s1_recovery_estimate.tsv（S1 弃权面可恢复量**预估**：结构口径 = 补 strong 后各面板行 no_record 基因获得可核外部链的覆盖比例，对 S1-S2 间隙 17.35pp 的 [lower=strong, upper=strong+weak] 结构区间；**不重跑 E2 打分、不改 E2 任何数字**，仅表格预估）。
- PME_NOTE.md（结论+判读矩阵记账）。

## 7. 判读矩阵（照抄任务书，机械执行）
| 观测 | 记账 |
|---|---|
| strong 覆盖 >=50% 无记录对 | 工程缺口第一批关闭过半，剩余列第二批清单 |
| strong 30-50% | 部分成立，按类拆分列缺口 |
| strong <30% | "无记录先验多不可外部证"定性，反馈 KB 线降档提案（不执行）|
覆盖度按 338 行账（非 280 键）计。

## 8. 修正记录（跑数前落纸；冒烟校准发现，未产生任何正式账）
- **A1（2026-09-27，正式批启动前）**：冒烟 8 键发现两遍召回不足——Rod/RHO（教科书强锚）仅判 weak、Cone/OPN1SW 判 none，
  根因=经典断言句不在 relevance 前 10。修正：每键 pass1(relevance) 若非 strong 追加 pass2(sort=CITED 高引经典)，两遍候选合并判级；
  raw 文件同存双遍（raw1/raw2）逐对留痕。分级规则（§4）不变，仅扩候选池。
- **A2（同批）**：Rod/Cone 类 doc_re 增补裸 'rods/cones' 形，加护栏：句内无 photoreceptor 短语时，文档须含 photorecept|retina 语境才认类。
- **A3（同批，实测延迟后）**：单请求实测 11.4s（本机网络路径），pageSize 10→50 提升候选池（仍 SRC:MED 摘要级、上限 2 遍=≤100 候选/键）；
  并发 4 线程（总请求速率 <0.4/s，远低于滥用线）。**基因匹配维持符号-only、全类统一**——不给个别类开"产物全名别名"后门，
  防测量不公；若视网膜类因 rhodopsin 命名习惯欠证，在 PME_NOTE 登记为已知局限而非改判据。
- **A4（运行工程，非判据）**：实测吞吐 2.7 键/分过低，并发 4→8 worker（仍 <1 req/s）；已完成 12 键经缓存续跑不重复计数。判据/候选池/分级规则零变化。
- 修正后 prereg 新 sha 记入 ledgers/sha_pre.txt 尾注（修正先于跑数，符合"判据先于跑数冻结"）。
