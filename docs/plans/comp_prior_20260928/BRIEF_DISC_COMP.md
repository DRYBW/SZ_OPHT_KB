# BRIEF_DISC_COMP_20260928 —— drsc 纪律 D-1：EXPECTED_COMPOSITION_v0 组成先验新面（PI 拍板见 directive 追加七B）

## 目标
把"该组织应有哪些细胞+大致比例"从判读员脑子里的隐性知识做成 **kb 新面 v0**：文献派生、逐行溯源、默认 OFF 不接线；自检只出旗标清单不改任何判读。

## 范围（v0 从窄，主检验唯一=面的可构建性与自检旗标率）
- 组织：先做**正常成人视网膜**（基线最厚、registry 标准集可校验）+ **正常成人眼表/角膜-结膜**两页；其余组织留 v1。
- 发育轴纪律：fetal/organoid/非成年条目**不得混入**（organism_stage 轴）；疾病态比例不建（PDR 注释不可靠口径维持）。

## 构建规则（硬）
- 每个细胞类型一行：比例区间（低/中/高，百分数）+ **逐行 PMID**（从 <EYEKB>/kb/vk_literature_index/ 与 INTAKE 台账 392 条里已有的文献证据派生，或盘上已入库 RAG 文献 papers.jsonl 元数据可核者）；
- **禁止从自家聚类/自家 demo 注释派生比例**（循环）；无文献支持的类型行标 "no_evidence" 而非编数；
- 版本化新文件：kb/composition/EXPECTED_COMPOSITION_v0.json + .md 人读版 + build 脚本与台账（逐行来源）。
- 领地：**只允许新建 <EYEKB>/kb/composition/ 目录**；kb/baselines、kb/markers、mcp_server、plans/evalset、obligrun 零触碰（在跑/冻结他卡领地）。

## 自检（只读，出旗标不出结论）
用面去"对账"盘上既有冻结产物：demo GSE165784 共识注释的组成、评估卷里各数据集的细胞组成——计算与先验区间的偏差，列"若此门前线上线会旗标哪些细胞类型/样本"清单+比例分布。**明写：旗标=提示复核，不等于注释错误**；健康公开集若被旗标 >20% 类型，如实报告（说明先验区间太窄，是面的问题不是数据的问题）——此为本卡内建的反向质检。

## 纪律
- 全程 CPU、低内存；产物全保留；完成或受阻落卡。
- 交付清单：EXPECTED_COMPOSITION_v0.json/.md、provenance 台账（逐行 PMID 可解析性自检=题录三判据）、自检旗标报告 COMP_SELFFLAG_20260928.md（含"本面未接线、接线与激活另卡另批"声明）、构建脚本。
