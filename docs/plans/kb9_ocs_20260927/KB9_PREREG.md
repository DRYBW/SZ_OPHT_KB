# KB9_PREREG — 眼表词条缺口建设预注册（判据先于执行冻结，2026-09-27）

卡：t_6df5b739 ｜ 任务书：BRIEF_KB9.md ｜ 放行：USER_DIRECTIVE_20260927_scoring_wave.md D3
领地：全部产物只落 /mnt/D/EyeKB/plans/kb9_ocs_20260927/；kb/、mcp_server/、evalset 冻结卷只读（PRE sha 台账 ledgers/SHA_PRE_KB9.txt，31 件零缺失）。避让并行卡目录 e2r_s5audit_20260927/、e3_rescue_20260927/、panel_pmid_20260927/。注册/接线/激活一律不做。

## 0. 继承裁决（逐条）
1. E1：表面 +16.8pp 系面板同源+lit 背答案垫高，替代路线关闭；F-OCS 39.39% vs 63.64% 同因=眼表词条覆盖缺口（Melanocytes/Schwann 零词条结构不可达；上皮 12 簇中 3 簇被 Fibroblasts/Immune 词条接管）。
2. E2：W2 生效；打分栈仅离线审计用途，生产零接线。
3. 证据消费纪律 v2：判分/裁定侧禁食同源证据；冻结件不回改。
4. face v2.1=eval_only；本卡一切产物不触生产路径。
5. CL 命名规范：新词条必挂 CL id + OLS by_iri 原始回证落 ledgers/ols_evidence/（照 kb5v3 先例命名 core_<词>_CL_xxxxxxx.json + _parsed.jsonl）；禁凭记忆写号；CL 无对应条（分层细分）按 CL 命名规范自造并注 cl_id: NO_MATCH 或借父条+layer_descriptor（照 KB7 Conj_epithelium_basal 先例，禁硬挂近似 term）。
6. 发布三段式：本卡=建设侧；报告含"注册申请"节等 PI。

## 1. 建设范围与词条判据
### 1.1 零词条补建（新词条名，避免与现库冲突）
- Melanocyte（眼表源，Q6 truth 类 Melanocytes，参考池=agg author 组 Melanocytes；CL:0000134 候选，OLS 回证定号）
- Schwann（Q6 truth 类 Schwann Cells，参考池=author 组 Schwann_M∪Schwann_N 并集；CL:0000049 候选）
- Conj_epithelium_suprabasal（结膜分层剩余细分；KB7 冻结裁定"D002 判据 0 基因全过"在先——本卡仅在换判据域（见 §1.3 R2/R3 后新共享基因屏蔽域）或补外部证据时才允许成条，否则诚实登记弃用）
- 角膜/巩膜成纤维细分（Limbus/Sclera Fibroblasts C1/C2 等）：同 KB7 先例复算；预期大概率仍 0 基因全过（K↔Fib 互逆结构性）→ 诚实阴性登记（HC-LITRE 先例），禁凑数。
### 1.2 核心基因判据（冻结 KB7-W2 常量，只读 agg_kb6b_v1.npz，sha 已入账）
CPM_FLOOR=5, LFC_T=1.0（火灾域全格）, CONS_T=0.75（可算域）, DR=2, MIND=10, SD=study×donor, TOPN=12, MINPOOL=500, BIGPOOL=5000。火灾域=其余 9 互斥组（pool≥500，排除父组）+同父兄弟亚型（pool≥500；<500 记录不否决）。全格表落 out/kb9_fire_audit.tsv（照 kb7_fire_audit_face.tsv 列结构）。
### 1.3 接管修复候选（applicability 修订，词条文件旁挂注记+证据装配规则，不改任何现库基因集）
- R1 组织适用性：material.tissue=='ocular_surface' 的证据装配中，来源文件 ∈ {markers_v4.1_clean.json, markers_v5_retina_interneuron.json, markers_v6_retina_repair.json} 的类（Rod/Cone/BC/AC/HC/RGC/MG/Astro/Micro/RPE/v5 泛型等）不计入 kb_marker_ranking（crosswalk 实证它们多为 no_counterpart 或跨谱系误导，如 Q6::13 之 MG|Astro）。反向同理：KB9 新条 applicability=ocular_surface_only，视网膜材料不计入（火灾审计 §3）。
- R2/R3 共享基因屏蔽（泛免疫/泛间质在眼表面的接管修复）：以冻结件 author_class_markers_data.tsv（KB 无关口径，同 h5ad HVG4000 mean-diff top60）为准——某免疫类基因 g 若出现在任一非 Immune 类 truth 的 top60，则在眼表面证据装配中该基因对免疫类的 n_shared 贡献记 0（R2）；间质类（Fibroblast/Pericyte/SMC/Myofibroblast/Keratocytes）基因 g 若出现在任一其它 truth 类 top60，同法记 0（R3）。目标：Q6::11 型（CD74/HLA→APC_MHCII 接管内皮）、Q6::3 型（S100A8/9→Mono_Classical 接管上皮）、Q6::24 型（mural 通签链）不复现。屏蔽集=逐类逐基因计算落 out/kb9_shared_gene_shield.tsv，禁手工挑基因。
### 1.4 Keratocytes 交叉信号（Q6::20 已知案）处置候选
登记为处置候选（非本轮生效）：face 材料证据中 Keratocytes 名可致 9 词表外定名（Q6::28 C 票），R3 屏蔽后其面贡献归零；词表映射建议（Fibroblasts 折叠域）与 D001 审计盲区（眼表词条做不了视网膜邻类审计）如实写进报告"残留限制"节。

## 2. 逐基因证据链（每 core 基因三通道，不足即弃用/降级并如实登记）
a) OLS：cl_id by_iri 回证（ebi OLS4 API，存原始回函）；b) 文献：EuropePMC/PubMed REST 摘要级检索（禁全文下载；每基因≥1 条可核 PMID，物种=人、组织/细胞类型语境匹配才算 pmid 通道，共现级只记 pmid_context——E2R 教训前置入语义）；c) data_driven：§1.2 npz 全格统计 id 引用。证据不足=弱证据弃用（HC-LITRE 诚实阴性先例），禁凑数。

## 3. 自检（离线复测，build 侧，不触生产）
- 臂定义：Arm1=现役生产库态（retina+membrane+v5+retina_v6+face_v6，ON）纯复算（不投票，只作复现校验与对照）；Arm2=Arm1+KB9 词条增量+R1/R2/R3 装配规则 = KB9 提案包（投票臂）。
- 管线保真门（先于一切投票）：用原库态（retina+membrane+v5，OFF）逐簇复算 face_q6 之 kb_marker_ranking，与冻结件对比——不一致率>0 簇即中止上报（证明装配复刻失真）。
- 面：digest/face_q6/EV_DIGEST_SLIM_q6.jsonl 33 簇；top_genes/gene_hits/tissue_composition_ref 原样搬运，仅重算 kb_marker_ranking（+变化簇 lit 按 kb2_mcp_v2 同参 top_k=4 重建；不变簇整行冻结）。
- 投票：仅证据行有变化（ranking 或 lit 变）的簇重新三席投票（A=qwen3.8-max、B=glm-5.1、C=deepseek-v3.2，LLM_CHANNEL 通道照 run_annotator_run5.py 冻结 runner 同参：温度 0.2、5/批、ANNOT_INSTRUCTIONS 原文、max_tokens 3500、enable_thinking=false 仅 qwen）；无变化簇复用三席存档票。通道 429/配额失败=block 上报，禁自行加钱换通道。
- 裁决：run5_verdict.py 同实现拷贝（同投票规则/同 norm_identity/同 P2 strict&any/同 truth 对账断言），crosswalk 用扩展副本（新增词条名→Q6 词表类映射，逐行注 provenance；ambiguous/no_counterpart 不猜）。
- 球门（与 RUN5 完全一致，不降）：P1 共识==作者标签 ≥24/33；P2 strict 违规 ≤1/33（any 口径并报）。禁调阈值凑命中。
- 预期代价表（不达标时残余 miss 归因锚，先于投票冻结）：①Q6::24——pericyte/SMC 通签生物学不可分（KB6b §3），P2 违规位保留属预期；②Q6::15/28——KERA 在 Fibroblasts top60（super_map 折叠域），R3 屏蔽后仍取决于票是否给定名票（coarse 即弃权）；③Q6::12/16/22/27/30/2/31——弃权/tie 结构位（RUN5 归因③协议性保守弃权），词条侧不可完全修复，若残余照此归因。达 24/33 即 PASS，不达按本表逐簇列残余+归因，如实报。

## 4. 火灾审计（KB7 方法，防再造 Q6::24）
- 格一（新词条全格）：§1.2 口径全格矩阵 out/kb9_fire_audit.tsv——每 core 基因×9 互斥邻组+兄弟亚型，min_lfc_fire、cons、donor 一致全列。
- 格二（混合面邻域交叉）：眼表 33 簇 + 视网膜抽 22 簇（冻结抽样规则：Q1/Q2/Q3/Q4/Q5b/Q7/Q8 各按 n_cells 降序 top3=21 + Q9 top1）；对 Arm2 库态复算 22 视网膜簇 ranking，断言 KB9 新条（applicability=ocular_surface_only）零进入；眼表面同理断言视网膜特有条（R1 剔除项）零进入。全格落 out/kb9_fire_audit_mixedface.tsv。

## 5. 交付与登记
build/markers_k9_ocs_increment.json（人读 JSON，结构对齐 face_v6：version/created/card/prereg_sha/scope/新条 core[{gene,evidence[]}]/applicability 注记/removed_note）；ledgers/ols_evidence_kb9/；ledgers/PMID_LEDGER.tsv（逐基因逐条：基因|通道|PMID|检索式|命中语境|判定）；out/ 全中间件保留；KB9_BUILD_REPORT.md（词条清单/台账指针/自检数字/残余缺口/注册申请节）。
诚实性条款：本件 sha 先于执行入账 ledgers/KB9_PREREG_SHA.txt；判据不回改；投票前后 PRE 触碰核验（31 件复验零写入）。
