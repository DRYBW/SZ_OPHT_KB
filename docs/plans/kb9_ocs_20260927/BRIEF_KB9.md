# BRIEF_KB9 — 眼表词条缺口建设（build 隔离版，PI 放行 20260927，队列源于 09-26 拍板"KB9 入队列"）

## 上游与继承（先读，逐条核对）
- 放行件+裁决继承清单：/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md
- CL 命名规范：/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260924_cell_ontology_naming.md（CL id 必挂、OLS 回证、禁凭记忆写号——该规范首跑即拦下假号，红线照守）
- 缺口证据（三度独立坐实，路径以 /mnt/D/OcularKB/WIKI/INDEX.md 当日条与下列件为准）：
  - plans/evalset/RUN5_FACE_prereg.md 及 RUN5 收口件（P1 21/33 归因约 9 簇为词条缺口）
  - plans/evidence_scoring_20260926/E1_VERDICT.md §1 F-OCS 段（Melanocytes/Schwann 零词条结构不可达；上皮 12 簇中 3 簇被 Fibroblasts/Immune 词条接管）
  - plans/e2_decontam_20260926/E2_VERDICT.md §1 F-OCS 行（39.39% 同因复现）
- 方法先例（只读）：kb/ 眼表现役词条文件结构、KB7 红词条修订与邻域火灾审计做法（plans/kb7wire_20260925/ 及其引用的 REVCAND/audit 件，路径读该目录自定）、KB6b 间质家族四红条教训（INDEX 09-25 凌晨条所指件）、HC-LITRE 文献三通道审法（plans/hc_letre_20260925/）

## 建设范围（词条增量+修复，全在 build/ 隔离区）
1. 零词条补建：Melanocytes（眼表源）、Schwann cells，及 RUN5/E1 点名缺口（结膜分层剩余细分、角膜成纤维细胞细分）。
2. 接管修复：泛免疫词条（Mac_*/Mono_*/APC_MHCII）与泛间质词条在眼表面上的适用性审查——给出限定/豁免修订候选（如词条 applicability 字段注记），使 Q6::11/Q6::3 型接管不复现。
3. Keratocytes 交叉信号（Q6::20 已知案）处置候选。

## 任务与自检（预注册先落纸）
- 每条新词/修订：CL id + OLS 原始回证落 ledgers/（OLS 回证件命名照 kb5v3 先例）；逐基因文献链 EuropePMC/PubMed 可核（PMID 落盘），证据不足=弱证据弃用如实登记（HC-LITRE 诚实阴性先例），禁凑数。
- 自检（build 侧，不触生产）：Q6 眼表 33 簇面离线复测——**球门与 RUN5 完全一致不降**（P1 命中 >=24/33 主靶；P2 词条污染实证 <=1/33），判读席复用三席存档票与既有 runner 模式（若需新判读票则用盘上已冻结 runner 与通道，成本超限即 block 上报，不自行加钱）。达不达标如实报，禁调阈值凑命中；不达标=按"预期代价表"列残余 miss 归因。
- 火灾审计：眼表 33 簇 + 视网膜抽 22 簇混合面做邻域交叉核对（KB7 方法），防再造 Q6::24。

## 交付
- build/ 词条增量文件（人读 JSON + 结构对齐现役眼表件）＋ KB9_BUILD_REPORT.md（词条清单/OLS 与 PMID 台账/自检数字/残余缺口/注册申请节）——**注册、接线、激活一律不做**，报告里的"注册申请"等 PI 批。

## 领地与红线
- 全部产物只落 /mnt/D/EyeKB/plans/kb9_ocs_20260927/；kb/、mcp_server/、evalset 冻结卷全程只读 + sha 台账。
- 并行卡避让：勿写 e2r_s5audit_20260927/、e3_rescue_20260927/、panel_pmid_20260927/。
- 零下载大数据（文献摘要级 API 检索可以）；下载若超 1GB 立即停卡上报。
- 完成或遇阻必须调 kanban_complete/kanban_block 落卡；中间产物全保留。
- 工作目录：/mnt/D/EyeKB/plans/kb9_ocs_20260927/（自建）
