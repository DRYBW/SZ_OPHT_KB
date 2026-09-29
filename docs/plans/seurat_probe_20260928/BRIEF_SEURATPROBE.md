# BRIEF_SEURATPROBE_20260928 —— Seurat/SingleR 双轨可行性探针（PI 拍板见 USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加七A）

## 目标
评估"Seurat+SingleR 作为 EyeKB 第二意见引擎"的可行性与增益，产出三数字+GO/NO-GO 建议。本卡不接线、不改任何生产面。

## 判读降级条款（预注册，先于执行）
- G0 装机：conda 新建环境（名 r_seurat_probe，python/R 均在新环境内；**不碰系统 R=/usr/bin/R，不装进任何既有 env**）。conda -c conda-forge/生物channels 装 r-base + Seurat + SingleR。**装机下载量先 du 预估+实测累计，若实测总量 >1GB：立即停卡，写 BLOCK 上报协调者转 PI 报批**（PI 常设门）。
- G1 试点：选一候选集 20k 细胞子集，跑 Seurat 标准链（SCT 或 log 归一 + HVG2000 + PCA + neighbors(k=20) + louvain res=1.0）；判据 RSS<=20G（/usr/bin/time -v 实测）且 端到端 <=15min。任一不达标 -> NO-GO 结案，落 NO_GO_SEURATPROBE.md（数字+失败环节），现行 scanpy 单轨原样继续，本卡结束。
- G2 全量探针（G0+G1 均过才进）：见下。

## 数据面（PI 明令，禁止自作主张换）
真值参照只从 **<STORE>/registry** 选**逐细胞作者级注释**的标凈数据集：
- Phase-0 必做：枚举 registry 目录清单，对每个候选 h5ad/rds 实测 obs 全列名+取值分布，确认存在逐细胞类型标签列（**分选池标签不算**，KB9 教训 GSE164403）；
- 入选：眼组织、成年（fetal/发育轴排除，organism_stage 轴纪律）、单集 <=20 万细胞、人鼠皆可但跨引擎对照同物种内进行；**选 2 个**（不足 2 个如实报缺口并 block，禁放宽到自家共识注释集——GSE165784/GSE160306 demo 面明令禁用当答案）。
- 只用盘上已有件，零新下载（FASTQ/新集一律不下）。

## 探针内容（G2）
同一数据、同一起点（counts）双轨：
- 轨 S（Seurat）：标准链 + 聚类 + **SingleR**（选最贴参考：HumanCellAtlas/Monaco/自建，写明选择理由与版本）
- 轨 P（Python 现行面）：与现管线同参 scanpy 链（HVG->PCA->neighbors15->leiden res1.0），**其"注释"用现有 kb/marker 面 top_genes 判读规则**（只读复用，不改规则）
产出三数字（全部落表）：
1. **跨引擎一致率**：逐细胞标签 ARI/NMI + 簇级混淆矩阵 + 每作者真值类的双轨纯度；
2. **SingleR 增益**：SingleR 标签 vs 作者真值的逐类一致；SingleR vs 轨 P 的改判清单（哪些簇/类被改），每条改判挂文献支持（有 kb 词条/PMID 则引，无则标"无支持，存疑"）；
3. **分歧清单**：双轨不一致且无单一真值裁决的簇列表（这就是未来"送 PI 裁决"的形态与工作量样本）+ 第二票转正 GO/NO-GO 建议（附工作量估计：每卷需 PI 裁几簇）。

## 资源与领地纪律
- 全部 CPU；重步骤 systemd-run --user -p MemoryMax=24G -p MemorySwapMax=2G 托管；心跳每 30min 带 free available 读数，<40G 停新并发落卡。**禁 GPU**（qwen 占用铁律）。
- 领地：工作目录 <EYEKB>/plans/seurat_probe_20260928/（本卡唯一可写）。禁写：kb/、mcp_server/、plans/evalset/、kb/baselines/、OcularKB registry（只读）、literature_db 各版。
- 中间产物（脚本/日志/矩阵/RDS）全部保留；完成或受阻必须调 kanban_complete/kanban_block 落卡。

## 交付清单
Phase-0 数据集核实表（obs 列实测证据）/ G0 装机台账（env 名+包版本+下载体积实测）/ G1 试点 RSS 与耗时数字 / SEURATPROBE_REPORT_v1.0.md（三数字+建议+局限声明）/ 全部表件与脚本原件。
