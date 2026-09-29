# BRIEF_PIPELINE — 九步批注流程打包进仓（对外"开放即可用"补最后一口）

## 背景与定位（PI 已拍板）
2026-09-29 PI 问"假设是开放的，别人可以下载直接用吗"，协调者实测发现：仓内已有证据服务（5 工具）+SOP+示例脚本，但**"拿自己的数据逐簇批量跑 5 工具"的入口脚本没有随仓发布**（散在 /mnt/D/EyeKB/plans/evalset/scripts/ 生产环境）。PI 原话"要的要的"批准打包。

## 任务：在 staging 仓新建 pipeline/ 目录，交付可一键跑通的批注入口

**输入**：10X 三件套目录（matrix.mtx+barcodes.tsv+genes.tsv）或 .h5ad；命令行必须带 --species human|mouse --tissue <词典已知组织> （+可选 --sample-group 分组标签）。
**输出**（全部落 --out 目录）：
1. 处理后的 .h5ad（含 QC 过滤、归一化、聚类、批次校正标记）
2. annotation_evidence_report.json + .md：每簇一条 = top genes / query_marker 候选与得分 / get_tissue_composition 对照（越界旗标）/ get_disease_prior 一致性（有分组才启用）/ search_literature top 片段+PMID / 置信度分级（evidence_consistent | needs_review | mixed_or_insufficient）
3. 质控图（线粒体比例、基因检出数、doublet、UMAP 前后）
4. decisions_template.csv：每簇一行待人工裁决（accept/modify/abstain 三值列，全空=交研究者）

**纪律红线（写进脚本头部与 README）**：
- 默认路径**零 LLM**——五工具是本地机械检索，出证据不出结论；可选 --llm-assist 开关只调用用户自备通道（示例脚本读 OPENAI_* 环境变量），默认关闭，仓内不写任何真实 key/URL
- 弃权/needs_review 是合法输出；脚本禁把 needs_review 写成确定标签
- 证据消费纪律：产出的报告可给人/判读侧消费；本卡不得新增任何"自动打分/自动定标"逻辑

## 素材来源（复制走，不改生产盘）
- 阶段 A 处理段：docs/plans/figure_uplift_20260928/scripts/（已在仓内，Scanpy/Harmony/Scrublet 实测可用）——提炼成 pipeline/stage_a_processing.py
- 阶段 B 证据采集段：/mnt/D/EyeKB/plans/evalset/scripts/kb2_mcp_v2.py（stdio 起 mcp_server 采 5 工具）与 kb2_digest 系列——**复制到 pipeline/ 后重写为通用输入版**（原脚本绑死 evalset 冻结卷，必须解绑；原文件勿动）
- 工具接口：仓内 mcp_server/server.py（只读复用，禁止修改）

## 验收门（逐条实测，产出 GATES.md 记录命令与输出）
- T1 冒烟端到端：用盘上已有 h5ad（如 /mnt/D/EyeKB/plans/evalset 的冻结卷或仓内小样）取子集（≤2000 细胞、2 样本）走 10X 三件套与 h5ad 两形态各跑一遍 → 报告三件（json/md/csv）齐、每簇五字段非空、needs_review 簇存在证明弃权路径通
- T2 黄金 41 不变：tests/verify_repro.py --db-dir <本地已解语料> 复跑 41/41
- T3 密钥扫描：pipeline/ 与 README 新增段 grep github_pat|ghp_|sk-|Bearer 真实值 = 0；生产盘 /mnt/D/EyeKB/kb 与 mcp_server 目录 sha 台账前后全等（零侵入）
- T4 零 LLM 默认：断网环境语义（不设任何 API 变量）下 T1 全流程可完成
- T5 README：新增"批量注释（pipeline/）"一节（用法三行命令+输入要求回链"输入与输出"节+弃权声明），目录结构表补 pipeline/ 行；沿用现有人话+专业混合文风，禁 agent 黑话（拍板/派卡/波次/收口/判读卡）
- T6 中间产物全保留：pipeline 内脚本/日志/示例输出落 staging 仓，不删除任何试跑产物（.gitignore 只排除 >50MB 数据件）

## 领地与推送
- 可写：/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928/pipeline/ 与 README.md、docs/plans/pipeline_pub_20260929/（本卡工作目录，BRIEF/日志/报告全落此）
- 禁写：/mnt/D/EyeKB 生产盘任何文件（只读复制源除外）、mcp_server/、kb/、tests/、literature_db
- **禁止 git push**——完成后本地 commit（可多个），最后落 PIPELINE_COMPLETED.md（含 commit hash 清单+六门证据路径），由协调者复核后代推

## 落卡纪律
完成调 kanban_complete；遇阻（前提塌方/环境崩）调 kanban_block 并写明三出路。中间产物全部落盘保留。
