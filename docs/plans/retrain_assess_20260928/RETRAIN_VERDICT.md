# RETRAIN_VERDICT — "要不要重训"四对象冲击评估（只读，零重训，D22）

- 卡片：t_ed4a3c52 ｜ 执行：AGENT_ROLE ｜ 日期：2026-09-28 ｜ 全程只读，零训练零重建零修改
- 任务书：BRIEF_RETRAIN.md（同目录）
- 复算证据：scripts/verify_retrain_assess_t_ed4a3c52.py（13 项断言全 PASS，原始输出 out/verify_run.log）
- 只读资产 sha 台账：ledgers/SHA_READONLY_ASSETS_20260928.txt（17 件，含 1GB chunks.parquet 独立复算，与并行卡 rag_fix 交付台账逐字符一致）

## 结论一句话

**四个对象全部不需重训。** 模型侧字节零接触（sha 实证）；RAG 侧新 chunk 嵌入已在构建管线内生成
（9,772/9,772 实测零欠账）；唯一遗留 = v6 面板**源文件**内嵌已撤证的错误 PMID（旁挂勘误设计
所致，MCP 运行时不读 errata），列再导出候选交 PI 拍板，本卡不动。

---

## 对象 1：v2_prod（人源 LR-HVG2000）→ 不需重训【输入面零接触】

| 核对项 | 实测 | 证据 |
|---|---|---|
| 模型字节 | sha256 d38af373…6b5c 与 META.json 逐字符一致；目录今日（09-27/28）零文件改动 | verify A1；台账；find -newermt 空 |
| 训练池字节 | HRCA(GSE265774)+GSE148077 数据目录今日零改动；训练脚本未动 | find -newermt 空 |
| 训练池边界（先例账） | IMPACT 卡四路独立证据：META / v2_prod_train.py 源码 / train_donor_registry.json(104 donors) / EVALSET_FREEZE 接触史声明——池外一切（含 GSE155288）均为外部 | models/V2PROD_CONTAMINATION_IMPACT_20260924.md §1 |
| 推理链 | consume_p1.py 只读 ①模型 pkl ②prod_lrhvg/hvg_top2000.json（整目录 mtime Aug 14，今日零改动）——不引用任何 kb/markers/overlay/errata/RAG 路径 | grep 源码 + find |
| 词典独立性（先例案证） | KB5v3 案：MG 词条 4/5 基因零区分度误导三席判读员，**不用词典的 v2_prod 728/728 判对 Astro**（plans/kb5v3_20260924/KB5V3_COMPLETED_20260924.md） | 先例账 |
| k9 overlay | INERT：不在 MARKER_LIBS、不在加载 glob、MCP 不读、默认 OFF；LILRB2 命中 0；且 k9 注册(09-27)晚于 v2_prod 验收(08-24)/切产(09-16) | _k9 overlay status 字段实测 |

**LILRB2 定性（任务书"若在且仅 kb 引用链错，模型不受——分定性"）**：
LILRB2 **在** HVG-2000 特征列（列位 991），Micro 类系数 +0.0166、其余 9 类 −0.0013～−0.0028
（verify A2 实测）。模型对该基因的用法 = 从训练池表达矩阵学得的数值权重，与 kb 词典引用链
**无因果通路**——撤证撤掉的是一条误引 PMID（41349939，泌尿科论文），不改变任何表达值、特征列、
系数。**模型不受，不需重训。**

## 对象 2：mouse_prod_v1（鼠版）→ 不需重训【字节全对 + 输入面无交集】

| 核对项 | 实测 | 证据 |
|---|---|---|
| 字节面 | SHA256SUMS 6/6 OK（model pkl/hvg_panel/META/cells csv/folds/MRCA 源 h5ad）；目录今日零改动（末次 09-25） | verify B1 + find |
| 特征空间独立性（复述） | 面板 2,000/2,000 行全 ENSMUSG（verify B2 实测）；配方自述 "seurat_v3 top2000 batch_key=source 鼠原生重选，**人 D001 面板不移植**"（META.recipe.hvg） | META.json + hvg_panel.csv |
| 与 k9 交集 | k9 = 人源眼表词条，注册于 09-27——**晚于** mouse_prod 建卡日 09-25，时序上不可能进输入；且训练输入=MRCA 官方注释 h5ad+预注册 v1.4 配方+folds.json，全程不读 kb | 各件时间戳 + META.recipe_source |
| 与撤证交集 | 撤证目标=人源 markers_v6_retina_repair.json 的一条 PMID 链；鼠模型不消费该文件（面板为 ENSMUSG 原生重选） | errata target_file 字段 |

## 对象 3：RAG 检索嵌入/索引 → 不需重训，且**无待补编码欠账**【实测对账】

**术语分诊（任务书要求分开写）**：
- 重新**编码**（embedding 生成）= 用冻结预训练编码器 bge-large-en-v1.5 把 chunk 文本变向量——工程动作。
- 重新**训练** = 更新任何模型权重——本项目 RAG 侧**从未微调过编码器**（v2.0→v2.4 全程 CPU fp32
  原样推理），故 RAG 不存在"重训"命题；只有"是否补编码/重建"的工程命题。

| 核对项 | 实测 | 证据 |
|---|---|---|
| build 产物含 embedding | v2.4_2026-09/chunks.parquet（1,022MB）含 embedding 列 | verify 输入 |
| 行数对账 | 230,426 行 = 继承 220,654 + 新增 9,772，按 64 篇闭集 PMID **精确分割验证**（非只看 manifest 声明） | verify C1/C2 |
| 编码欠账 | embedding null=0 / 空数组=0 / 维数全 1024（230,426/230,426）；新 lane **9,772/9,772 全有嵌入** | verify C3/C4/C5 |
| 产物未被事后改动 | chunks.parquet sha256 独立复算 = rag_fix 卡 DELIVERABLES 台账逐字符一致（93125c2e…c9f9） | ledgers/ |
| 独立索引文件 | 无——stage3_retrieve 直读 parquet 内嵌向量（mcp search_literature 透传），故也不存在"重建索引"欠账 | eyekb_core.py:37-58 |
| v2.5 追补 | 在跑（并行卡 t_d0bea5a6，本卡禁写其目录）——**待数据**：落盘后按同两条机械检查（行数对账 + embedding null=0/空=0）复检即可，无需预判任何重训 | RAGFIX2 在跑状态 |

RAG 侧唯一遗留动作（非本卡范围）：MCP/stage3 默认库未切（v2.0 不变，v2.4=latest-raggap 注册
OFF 态）——属服务行为变更，沿先例待用户拍板，与重训无关。

## 对象 4：面板/词条衍生件 → 模型衍生件零涉及；kb 侧列 1 个再导出候选（本卡不动）

- **撤证语义**：LILRB2 在 retina_v6/microglia_repair 的 **core[13] 成员资格保留**，
  存活证据支 canonical + data_driven(REVCAND_KB6_v2::Microglia::rank6)；仅撤 evidence[1]
  的误引 PMID:41349939。撤证件自述 INERT + "面板核心文件字节零改动"（实测成立：面板 mtime 09-25）。
- **扩散面实测**：错误 PMID 41349939 在 kb/clients/mcp 文本面仅 2 处——①面板源文件内嵌 1 处
  （verify D1 计数=1）②errata 本体（登记用，正常）；linkbackfill 830 行零命中（verify D2）；
  其余命中全在 rag_gap 卡的账本/清单文件（留痕，非资产）。
- **实际暴露点**：MCP 运行时 MARKER_LIBS['retina_v6'] 直指面板源文件且**不读 errata**
  （eyekb_core.py:140-144 grep 实证）→ query_marker 现返回仍含已撤证的链。
- **候选处置（交 PI 拍板，二选一）**：
  - **A. 维持旁挂勘误**（现行既定设计，先例=CL 假号 markers_cl_alignment_v1.json：旁挂件+
    源文件只读+.bak 快照+双 sha 台账）——消费 run 自行按路径应用 errata；源文件零改动。
  - **B. KB9b 式源文件再导出**——从 core[13].evidence 删该条（保留 gene 行与成员资格），
    .bak pre-image + sha 台账。若走 GitHub 镜像同步（repo_sync 卡口径：kb/ 100 文件进仓、
    对外 clone 可查），**建议 B 或至少 errata 随面板同包分发**——对外快照里裸源文件带着
    一条泌尿科 PMID 充当"microglial phagocytosis review"，是公开面瑕疵。
- **模型侧衍生件**：v6 面板不是 v2_prod/mouse_prod 任何环节输入（两模型 HVG 均数据侧重选，
  非词典衍生）→ 无论 A/B，**不触发任何模型重训**。

---

## 附页：今日全部变更 × 受影响资产矩阵（供 GitHub 同步卡与 A4 复盘引用）

| # | 今日变更（09-27 夜→09-28） | 落点 | v2_prod | mouse_prod_v1 | RAG 嵌入/索引 | 面板/词条衍生件 |
|---|---|---|---|---|---|---|
| 1 | k9 眼表 4 词条注册（默认 OFF，t_4bb75b26） | kb/markers/markers_k9_ocs_increment.json + _k9_ocs_rules_overlay_v1.json | 无接触（推理链不读 kb；INERT） | 无接触（时序上晚于建卡日） | 无接触（overlay 不入语料） | 无——新文件，非 v6 派生件；**GitHub 同步=随 kb/ 100 文件进仓（默认 OFF 语义要在 README/件内保留）** |
| 2 | LILRB2 撤证 + sample20 误引登记（t_d0bea5a6） | kb/markers/_raggap_errata_v1.json（INERT 旁挂） | 无接触（特征列含 LILRB2 但权重源自表达数据，见对象 1 定性） | 无接触 | 无接触（撤证只影响词典引用链，语料侧该 PMID 本就 ⛔ 不入库） | **受影响=唯一实弹点**：v6 源文件内嵌误链、MCP 不读 errata → 对象 4 候选 A/B 待 PI 拍板 |
| 3 | RAG v2.4 增量 +9,772 chunks/64 篇（t_d0bea5a6） | OcularKB rag/literature_db/v2.4_2026-09（frozen read-only 注册） | 无接触 | 无接触 | **已建成**：嵌入零欠账（实测 C3-C5）；默认 db 未切（行为变更待拍板） | 无 |
| 4 | RAGGAP C 档链回填 830 行（默认 OFF） | kb/markers/_raggap_c_linkbackfill_v1.json（INERT） | 无接触 | 无接触 | 无接触 | 零误引 PMID 命中（verify D2） |
| 5 | v2.5 追补在跑（并行卡） | rag_fix_20260928/（本卡禁写） | 无接触 | 无接触 | **待数据**：落盘后复检行数+embedding 两条即可 | 待其产物再扫一次 41349939/新撤证项 |
| 6 | 误引审计在跑（kb_chain_audit 卡） | kb_chain_audit_20260928/（现仅 BRIEF，本卡禁写） | 无接触 | 无接触 | 无接触 | 审计对象=kb 引用链本身，产出可能扩充对象 4 候选清单 |

**GitHub 同步含义（给同步卡）**：本轮变更中进仓面 = kb/markers 三新件（k9 两件 + errata +
linkbackfill）+ v2.4 指针行；**模型资产（v2_prod/mouse_prod）与 RAG 语料本体字节未动**，
Release 资产/模型文件无重新上传必要；唯对象 4 若 PI 选 B，v6 面板源文件将产生一次真实再导出
（届时同步卡需换该文件并更新对账表）。

## 红线遵守声明

只写 /mnt/D/EyeKB/plans/retrain_assess_20260928/；models/、kb/、rag 库、mcp 全程只读（仅
joblib.load/sha256sum/文本 grep）；kb_chain_audit 与 rag_fix 两并行卡目录零写入（本卡对其目录
的访问全部为只读 grep/ls/读台账）；零训练、零重建、零修改任何生产件。
