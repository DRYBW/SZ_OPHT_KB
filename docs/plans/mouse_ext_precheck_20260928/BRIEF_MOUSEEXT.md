# BRIEF_MOUSEEXT — 鼠版重档外部验证集：零下载预检+报批清单（PI 整链授权，追加五）

放行依据：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加五（>1GB 下载仍需 PI 逐行批=本卡产报批件）。
背景：鼠版中档已建成（plans/mouse_mid_20260925/MOUSE_MID_REPORT.md v2，模型=/mnt/D/OcularKB/models/mouse_prod_v1/）；重档净增价值=真外部带注释验证集；08-26 已知 limitation="外部带注释独立鼠视网膜集稀缺"——本卡把"到底有没有、多大、重不重复"用盘上证据钉死，产行级批准清单交 PI。

## 任务（全程零下载；产出落 /mnt/D/EyeKB/plans/mouse_ext_precheck_20260928/）
1. **候选枚举**（web+GEO/SRA/CELLxGENE/HCA 元数据检索，只查元数据不下正文）：mouse_retina/ocular 带**逐细胞类型作者标签**的独立公开集；重点点名 GSE137400 鼠源本体、GSE81905，并补充检索 2024-2026 新发布（如小鼠眼发育/视网膜新 atlas）。
2. **逐行核四件**：①注释可用性——区分"逐细胞类型标签 vs 分选池标签"（GSE164403 教训：supplementary/assemble_report 实证，不许从标题推断）②体积——curl -sI/supplementary 表 HEAD 实测 ③与 MRCA 训练池包含风险——公共源（Shekhar/Ma/Tran/Yan/Jacobi 等 MRCA 域内 resub 源）逐一比对（accession/供体/barcode 级能核多少核多少，核不了如实标"不可判"）④与 mouse_prod_v1 类目兼容性（10 类映射可覆盖否，发育期样本按 development_stage 轴剔除预判）。
3. **本地已在盘核查**：find /mnt/D/OcularKB/data /mnt/D/DR_GEO /mnt/D/RetinaAging -iname *GSE*，本地已有不列缺口。
4. **产出=行级报批清单 MOUSEEXT_APPROVAL.tsv + 一页说明**：每行=accession/组织构成/细胞数/标签形态实测/实测体积/包含风险/净增价值预判/建议（收-GB 级需勾|不收|不可判待补检）；>1GB 行全部进"等 PI 勾"栏，一行不自动下。
5. **结论段回答**："重档能否补出真第二外部 F1"——以命中清单证据给 可/不可/部分，禁拍脑袋。

## 红线
零下载（元数据与 HEAD 请求除外）；models/mouse_prod_v1、plans/mouse_* 目录只读；不训练不建版；kb/ 只读。完成或遇阻必须调 kanban_complete/kanban_block 落卡。
