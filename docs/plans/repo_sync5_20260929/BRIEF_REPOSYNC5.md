# BRIEF_REPOSYNC5 — 第五轮仓同步（追加八预授权，push 归协调者）

## 目标
staging 仓 <STAGING_REPO>（HEAD=1febfee，远端 main=a0ad857）对齐 09-28 晚—09-29 新产物，跑全部八门，产出一个**可快进 push 的 commit**。**本卡禁止 push**——push 由协调者在授权窗执行。

## 基线（协调者盘上重建，勿再猜）
- 远端 main 头 = a0ad857（REPOSYNC4）；staging 领先 1 commit（1febfee Release 回执）
- 新产物清单（已核实存在）：
  - kb/composition/：EXPECTED_COMPOSITION_v0.{json,md} + COMP_SELFFLAG_20260928.md + SHA256SUMS.txt + scripts/ 三件（进 kb 层镜像；文献+registry 派生，无患者数据）
  - plans/：drsc_disc_quant_20260928/{BRIEF,DECISION_TABLE_composition_gates.md,out/ 表件}、seurat_probe_20260928/{BRIEF,SEURATPROBE_REPORT_v1.0.md,three_numbers.json 等表件}、comp_prior_20260928/{BRIEF_DISC_COMP.md,BRIEF_DISC_COMPV1.md}、obligrun_20260928/（若 REPOSYNC3/4 未收齐则补）、QUEUE_20260929.md
  - WIKI：USER_DIRECTIVE_20260928 追加八节（**mask 版**：涉凭据/内部路径描述化）、当前状态/INDEX 增量
  - skills 镜像：gpu-exclusive-maint-toctou 09-29 更新（Xid79 遥测判供电路径+flock 教训）——若仓内有该镜像则同步，无则登记不造
- worker 建卡后第一步自行 mtime 横扫（-newermt "2026-09-28 12:00"）补漏，漏收不算失职、多收（患者数据类）算失职

## 八门（全 PASS 才算完，逐门结果落 REPOSYNC5_COMPLETED.md）
T1 结构门：新增文件全部落对应层目录，无越层
T2 冻结面零触碰：evalset 票面/registry 基线/生产 kb markers 现役件 sha 前后全等
T3 v4 幂等脱敏扫描 scan=0
T4 **T7 自家数据 token 扫描 HARD=0**（〔样本编号前缀〕/〔项目号前缀〕/〔共病项目代号〕/患者样本号 token 正则，永久门）
T5 黄金 41：仓内 tests/verify_repro.py 用锁环境重跑 PASS 41/41（数据源=Release 预置件已在本地 <WORKER_HOME>/RAG_SLIM_V242，勿重新下载）
T6 新鲜克隆自证：git clone file:// 到 /tmp 干净目录，仓内脚本可跑
T7 directive/WIKI mask 版逐件人查（凭据字面量、内部绝对路径、微信 bot 账号 id 类）
T8 commit 拓扑：staging 领先远端恰 1 个新 commit（1febfee 之后叠一个），git log --oneline 可快进

## 纪律
- **禁 push、禁动 Release/资产、禁改 1febfee 及更早 commit**（不改历史）
- copy 不 move；线上 /mnt/D 原件零改动
- 大文件不收：>50MB 产物只收清单/摘要（如 SEURATPROBE data/ 的 mtx/rds 不进仓，报告+表+manifest 进）
- 公开数据集供体号（BCM_22_*/shi_* 等 GEO 级）允许（仓内既有先例）；患者样本号（〔患者样本号范围形态〕/〔样本编号前缀〕**/〔项目号前缀〕**）绝对禁
- 完成或受阻必须调 kanban_complete/kanban_block 落卡；分步落盘+comment 留痕
- 资源：零下载、CPU、systemd-run MemoryMax=8G、h5ad 相关用 scrnaseq env

## 交付
- staging 新 commit（消息含 REPOSYNC5 前缀+内容清单）
- docs/plans/repo_sync5_20260929/REPOSYNC5_COMPLETED.md（八门逐条 PASS/FAIL+证据）
- 落卡 result=一句话+commit sha
- **领地隔离**：COMPV1（t_37a35220）在跑，其产物 kb/composition/ 内 *v1* 命名件与 plans/comp_prior_v1_20260929/ 属进行中状态——**本卡一律不收**（mtime 横扫命中也跳过并登记'待下轮'），只收 v0 与已收口卡产物


> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked（类别描述化，非患者数据语义零改动）。线上原件留机器侧；逐件登记=docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv。本注为同步卡处置留痕，不改变 PI 条款/通报的规范语义。


> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked（类别描述化，非患者数据语义零改动）。线上原件留机器侧；逐件登记=docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv。本注为同步卡处置留痕，不改变 PI 条款/通报的规范语义。


> 〔仓面注〕本文件涉自家标识 token 字面已按 T7 永久门 masked（类别描述化，非患者数据语义零改动）。线上原件留机器侧；逐件登记=docs/plans/repo_sync5_20260929/ledgers/T7_EXCLUSIONS_RS5.tsv。本注为同步卡处置留痕，不改变 PI 条款/通报的规范语义。
