# REVIEWER_LLM 预审补件 B — 语境门干跑实证（发给同一评审，接前请求，先读再答）

你前函将收到 88 基因候选矩阵干跑结果（规则草案 §1.2 Tier1∨Tier2 逐字执行，ledgers/eurpmc 原始返回）：

=== FINAL panel by group（干跑） ===
ACINAR: T1=[] | T2=['BPIFA2','DCD','LPO','MUC7','PIP'] | FAIL=19 个（含 PRB1-3/LACRT/PRSS1/CTRB1/STATH/CA6/PRR4/ZG16B/AQP5...）
DUCT:   T1=[] | T2=[] | FAIL=16 个（含 KRT19/CFTR/SOX9/KRT7/PRR27/PIGR/SPP1...全部）
MYOEPITH: T1=['MYH11'] | T2=[] | FAIL=13（含 ACTA2/CNN1/KRT5/KRT14/TP63/TAGLN...）
IMMUNE: T1=['CCL5','CD74'] | T2=['CD3E','CSF1R'] | FAIL=8（含 PTPRC/CD68/MS4A1/NKG7...）
ENDO:   T1=[] | T2=[] | FAIL=7（含 PECAM1/CDH5/VWF/CLDN5...全部）
NEUROGLIA: T1=[] | T2=['S100B'] | FAIL=6（含 PLP1/SOX10/NGFR...）
STROMA: T1=[] | T2=['COL1A1'] | FAIL=6（含 DCN/LUM/PDGFRB...）

Tier2 样本目检：多数 T2 命中来自两篇——PMID 34950038（泪液/唾液蛋白组，SJ 病）与 PMID 35295950（泪囊 chrRNA 疾病研究）；
基因 token 仅在全文索引匹配、abstract 不可见。

## 由此新增的结构性问题（并入你 Q8，也可单列）
S1 照此终判，DUCT 与 ENDO 两群 available=0 → §3 锚定门对这两群永不可能成立；
   七群里可锚的只剩 ACINAR(5 个 T2 全弱源)、IMMUNE(4)、NEUROGLIA(1)、STROMA(1)、MYOEPITH(1) —— 
   合格锚定簇几乎必然 <8 → 100% 触发 O3 降档。考试大概率"无卷可判"。
S2 语境 token 把 "lacrimal sac"（泪囊=引流结构，非泪腺；且疾病材料）算成了泪腺语境——泪囊/泪道文献基因不可作泪腺参考系。
   建议修正：语境 token 收紧为 {lacrim|tear|exocrine} 且 title 含 "lacrimal gland|lacrimal (gland) 语境、排除 lacrimal sac|canalicular|dacryocyst"。你裁。
S3 候选矩阵本身偏"酶原/泪液蛋白"，泛细胞类型 canonical marker（PECAM1/CDH5/PTPRC 等）在"基因×lacrimal"检索下天然吃亏。
   给可操作替代：例如 ①群级锚定=canonical 泛标记走独立语境通道（query 用 "<GENE> AND 'lacrimal gland' AND (marker OR cell type)" 或接受"组织学共识基因无需基因级 PMID、群级挂 1 篇泪腺图谱文献"）——但这要动 RULING"每群每基因挂可核 PMID"的字面；
   ②或者接受"本考卷只有 2-3 群可锚 → 直接按 §8 降档出 O3 定性档"——诚实但等于考试不成立；
   ③或扩大候选矩阵+换检索式（如 "gene AND 'lacrimal gland' single cell"），T2 质量门槛提高（abstract 可见或 2 篇以上不同 PMID）。
   你给出你认为不违裁定精神、又能把考卷做厚到 >=8 锚定簇的最优组合（可组合多措施），并逐条给出你会怎么改 §1。
S4 注意：任何修正仍禁 KB 派生；修正属于"判据冻结前的设计裁决"，不是看结果挑球门——三门阈值与裁定结构不动是你的边界。

请在主回函里对 S1-S4 逐条裁定，并把"面板语境门最终文本"直接写成可粘贴段落。
