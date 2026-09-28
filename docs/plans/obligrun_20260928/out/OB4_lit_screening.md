# OB4_lit_screening — lit 逐条同源排除筛查留档（t_c145db7c，注册包 §9）

- 筛查对象：正式票面全部 lit 命中 64 条 / 12 唯一 PMID（含 8 冻结簇 RUN5 代整行 lit——同受 §9 排除规则约束）。
- 排除对象定义（注册包 §9 逐字）：直接陈述本评价 33 簇（D002 author 标注）类属归属的文献及其片段（含 Q6 truth 来源标注论文及其补充表）；判定标准=片段文本是否含"簇/细胞群→作者标签"指派关系（标题级初筛+片段级复核两级）。
- 观看列表（D002 study 层全集，obs.study×GSM 直读）：9 study 标签 = chakravarti_GSE218123 / chen_cornea / chen_limbus / chen_pub_GSE153515 / chen_sclera / dickman_GSE186433 / lako_adult_GSE155683 / li_GSE147979 / shi_GSE157474。评测池 100k 细胞构成：6 个 GSM 直读 study 20,429 细胞 + chen_cornea/limbus/sclera 无 GSM 前缀 79,571 细胞（无 accession，本地不可解析其 source paper——登记残余限制，见文末）。

## 逐条判定汇总

| PMID | 标题级初筛 | 片段级复核 | 判定 |
|---|---|---|---|
| 34381080 | Molecular characteristics and spatial distribution of adult  | 非 D002 source；片段指派命中=5；D002 accession 提及=[] | 保留 |
| 36163311 | A single-cell transcriptomic atlas of the human ciliary body | 非 D002 source；片段指派命中=8；D002 accession 提及=[] | 保留 |
| 36712326 | Single cell RNA-seq of human cornea organoids identifies cel | **Q6 truth 来源标注论文**；片段指派命中=2；D002 accession 提及=['GSE218123'] | **同源排除** |
| 37156914 | Multimodal spatiotemporal phenotyping of human retinal organ | 非 D002 source；片段指派命中=10；D002 accession 提及=[] | 保留 |
| 37389178 | Identification of BST2 as a conjunctival epithelial stem/pro | 非 D002 source；片段指派命中=2；D002 accession 提及=[] | 保留 |
| 37443842 | Single-Cell RNA Sequencing: Opportunities and Challenges for | 非 D002 source；片段指派命中=6；D002 accession 提及=[] | 保留 |
| 38177186 | The single-cell transcriptomic atlas and RORA-mediated 3D ep | 非 D002 source；片段指派命中=2；D002 accession 提及=['GSE155683'] | 保留 |
| 39422453 | Transcriptomic profiling of Schlemm’s canal cells reveals a  | 非 D002 source；片段指派命中=3；D002 accession 提及=[] | 保留 |
| 40402520 | Distinct Transcriptomic Profiles of Cultured Anterior and Po | 非 D002 source；片段指派命中=0；D002 accession 提及=[] | 保留 |
| 40576432 | Single-Cell RNA Sequencing of Rabbit Sclera at Different Dev | 非 D002 source；片段指派命中=3；D002 accession 提及=[] | 保留 |
| 40882639 | Single-cell transcriptome and surfaceome profiling of the ad | 非 D002 source；片段指派命中=2；D002 accession 提及=[] | 保留 |
| 41309590 | Neuroectoderm-derived iris muscle characterization at the si | 非 D002 source；片段指派命中=2；D002 accession 提及=[] | 保留 |

## 排除动作（逐条）
- **剔除**：Q6::11（变化簇-KB9重建）lit 行 ct=Endo PMID=36712326 —— chakravarti_GSE218123（Maiti et al. PNAS Nexus 2022，通讯 Chakravarti；Data Availability 自存 GSE218123=GEO 系列题名逐字一致；D002 obs.study 直读 chakravarti_GSE218123 GSM6735065… 4,388 评测细胞）。该论文含 Endothelium 类群指派段落（Results > Endothelial cell types…），其作者标注即 D002/Q6 对 chakravarti cells 的 truth 标签来源；票面渲染行"Endo|PMID:36712326|…identifies cell fates…"= 对 truth=Endothelium 簇（Q6::7/Q6::11）的来源标签回证通道（E1 "lit 背答案"机制实例）。
- **剔除**：Q6::7（变化簇-KB9重建）lit 行 ct=Endo PMID=36712326 —— chakravarti_GSE218123（Maiti et al. PNAS Nexus 2022，通讯 Chakravarti；Data Availability 自存 GSE218123=GEO 系列题名逐字一致；D002 obs.study 直读 chakravarti_GSE218123 GSM6735065… 4,388 评测细胞）。该论文含 Endothelium 类群指派段落（Results > Endothelial cell types…），其作者标注即 D002/Q6 对 chakravarti cells 的 truth 标签来源；票面渲染行"Endo|PMID:36712326|…identifies cell fates…"= 对 truth=Endothelium 簇（Q6::7/Q6::11）的来源标签回证通道（E1 "lit 背答案"机制实例）。

## 披露项（保留但登记）
- 38177186（Li M et al. Nat Commun 2024）：Data availability 明示输入数据下载自 GSE155683（=lako_adult D002 构成研究）、自存 GSE249150（非 D002）。**非 truth 来源论文**（lako 标签定义于 GSE155683 原发表），属第三方再分析；其片段对 GSE155683 细胞群的自有再注释≠D002 所用 author 标签。保留，登记"再分析关系"。
- 37443842（Cells 2023 综述）：无自存数据；可能转述各 study 结果（间接）。无 33 簇指派证据，保留。
- 39422453（Schlemm canal）：自存 GSE272434/GSE271132，非 D002 构成；保留。

## 残余限制（如实登记）
- chen_cornea / chen_limbus / chen_sclera（评测池 79,571 细胞主体）obs 无 accession、无 GSM 前缀，本地证据层无法解析其 source paper；已核 12 命中 PMID 的作者/题名/自存声明均不匹配 chen 系（34381080=Ligocki/Fuchs；37389178=Kitao/Takayanagi；38177186=Li M）。若 chen 系来源论文后续获权威 accession 映射，需重跑本筛查（登记为下游项）。
- 本 run 票面 lit 字段仅存 pmid/year/title[:90]（KB9 建面包实现事实），"片段级"复核在语料 chunk 层执行；渲染给判读席的文本面=title 行——对 Q6 truth 来源论文按 §9 括注（"含 Q6 truth 来源标注论文及其补充表"）类别级排除，不依赖单条片段文本。

## 结论
- 判定：**2 条命中"同源排除"（PMID 36712326 × Q6::7/Q6::11 两行）→ 冻结票面含未排除的 truth 来源 lit = 票面污染事件**。
- 按 PREREG §6/§7：票面作废条件命中 → block 上报，作废留痕，不重跑粉饰；正式三席票未开跑（票预算消耗 0/150）。
