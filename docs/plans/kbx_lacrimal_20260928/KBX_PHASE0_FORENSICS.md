# KBX Phase-0 审计发现 — 泪腺词条疗效首考不可按 BRIEF_KBX 执行（缺 ground-truth 真值）

- 审计卡: t_0fb07fd6 | 审计人: AGENT_ROLE | 日期: 2026-09-28
- 任务书: /mnt/D/EyeKB/plans/kbx_lacrimal_20260928/BRIEF_KBX.md
- 放行件: /mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260928_eyekb_improve_wave.md D13
- 状态: **遇阻落卡**（零写生产/零 kb 写/零下载，仅只读审计；本件与 p0_inspect.py 是唯一落盘物）

## 结论（先行）

BRIEF_KBX 第 1 步要求"**h5ad 作者标签→Leiden 聚类…真值=作者标签众数+纯度>=0.8 门**"，
即判读矩阵 P1/P2/P3 三门全部依赖**逐细胞作者细胞类型真值标签**来打分。
**该真值标签在本数据集不存在**（GEO 从未沉积、非 OA 无法补、raw 无簇标签文件）。
因此 KBX 作为"盲注+对答案疗效首考"**无法按书执行**——没有答案可判分。

强行替代（用 KB8 自建聚类当"真值"）= 循环论证：泪腺三词条的 core 基因本就来自 KB8 同一套聚类面板打分
（kb8_panel_scores_tissue.tsv 的 ACINAR/DUCT/MYOEPITH 列=词条基因 z 均值），
用同源聚类当真值给词条判分 → P2"词条污染"门恒不可区分"词条错 vs 覆盖缺口"，违反 BRIEF 第 6 行的考试设计初衷。

## 证据（全部实测，只读）

1. **h5ad 无细胞类型标签列**（sha256 `5e6d753d0c10d1c5ac23e50b5b0150741ce0341654ad65cd68a2a72368a73399`，
   `/mnt/D/OcularKB/data/GSE164403/GSE164403_annotated.h5ad`，3,071×39,009）
   obs 全列 = `sample_id, source_type, gsm, patient_number, author_sort, culture_condition, passage_number,
   day_in_culture, total_counts, n_genes_by_counts, pct_counts_mt, author_empty_well` —— **无任何 cell_type / cluster / label 列**。
   唯一像"注释"的是 `author_sort`，取值 = {All 1,152 / Epcam+ 371 / Epcam+/Ngfr+ 10 / NA 1,535 / empty 3}，
   这是 **FACS 分选策略标签（SORT-seq 分选），不是细胞类型标签**。

2. **组装报告 + uns 显式声明无作者标签**：`GSE164403_assemble_report.json` → `author_cell_type_available: false`；
   h5ad `uns['author_cell_type_available']=False`，`uns['author_cell_type_note']` 原文：
   "GEO 沉积的 cell 级 metadata 只含 PatientNumber/Sort（组织）与 CultureCondition/…（类器官），
   **不含作者 cell-type 簇标签**；论文自报 18 簇须另取（论文补充材料或自行聚类）"。

3. **raw 仅 4 件，无一含簇标签**：`metadataTissue.csv.gz`(CellName/PatientNumber/Sort)、
   `metadataOrganoids.csv.gz`(CellName/PatientNumber/CultureCondition/Passage/Day)、
   `tissuecells.csv.gz`/`organoidcells.csv.gz`(gene×cell 计数矩阵)。GEO 无 supplementary 簇标签文件。

4. **KB8 登记件 §3 早已裁定**：`REGISTRY_ENTRY_Q10_GSE164403.md`——
   "作者 cell-type 标签：**未沉积**…论文自报 18 簇：Cell Stem Cell **非 OA**（EuropePMC isOpenAccess=N，无 PMC 全文）…
   ⇒ 本数据集细胞类型参考系 = KB8 本卡**自建聚类**…**非作者标签**，引用须带此口径"；
   §6 评估层"如 RUN 系列要用 Q10，须先由 **PI 裁定 + 单独预注册**（本登记不构成入卷）"。

5. **WIKI/数据资产.md §7.2/§7.3** 同口径：作者 cell-type 标签列 = "❌ **未沉积**（论文自报 18 簇）"；缺口"作者 cell-type 簇标签未沉积 ⇒ 词条层需另取"。

## 待 PI 裁定的解决路径（三选一，KBX 不能自决替代真值）

- **O1 取回论文 18 簇作者标签**：向 Clevers 组/Cell Stem Cell 补充材料索取或从可获取全文解析逐簇细胞类型映射（可能需 PI 批准少量下载/文献获取）。拿到后真值=该映射→KBX 按书可执行。最干净，但依赖外部可得性。
- **O2 PI 指定外部独立真值参考系**：例如用与泪腺词条**无基因交集**的外部权威 marker 面板（如 CellMarker/PanglaoDB 泪腺条目，或 Human Protein Atlas）为每簇定真值；须先验证这些面板在本平台可检出腺泡/导管/肌上皮（KB8 已实测腺泡程序近乎不可检出 PRSS1 2.3 CPM/CTRB1 6.1 → 即便 oracle 也无法命名腺泡，P2 归因仍受限）。
- **O3 改 KBX 为"无真值"设计**（放弃 P1/P2 疗效门）：仅做"三词条 core 在哪些组织簇以何特异性开火 + 跨簇火灾观察"的定性 sanity，明确不产出注册资格判定（=不满足 BRIEF 第 4 步交付）。此为改考卷性质，需 PI 确认后才不算擅改球门。

## 落卡

只读审计，未建卷、未跑聚类、未发任何 LLM 票、未写 kb/mcp/evalset。kanban_block 待 PI 选 O1/O2/O3。
