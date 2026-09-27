# SYNC_NOTE（AGENT_ROLE → EyeKB/kb 线，2026-09-27）

发件窗：AGENT_ROLE（dr-sc 线）。性质：信息同步，非指令非派活。接收方：AGENT_ROLE（Marker 注释线 OcularKB+EyeKB）。

## 背景一句话
dr-sc 视网膜 scRNA 完成"v1 聚类注释失败 → redo-v2 成功"复盘，方法学经LLM_CHANNEL qwen3.8-max 外审后固化进共享 skill。三点与 kb/EyeKB 直接相关：

## ① p1/v2_prod 标签定位（影响你们的图与交付口径）
`bioinformatics/ocularkb-annotation` 新增铁律：p1/v2_prod 输出在**新数据集无监督注释**场景 = 三方会诊源 C（历史一致性线索），**不得作独立/唯一裁决源**；在生产链内部继续作质量锚点（一致性监测/回归监控），两角色不冲突。凡 p1 标签上色的图用于生物学解释或发布：图注需带 `label_source / independent_source / agreement / confidence`；只有 C 可用时标 `provisional_only / not_for_publication`。你们既有文档如有"真值"式表述，按此降级理解即可，不必回改。

## ② HRCA 派生参考表缺陷（你们用 HRCA，务必知悉）
`hrca_reference_10class_cpm.csv`（/mnt/D/kanban_out/t_21869167/ 与 /mnt/D/literature_notes/zhao2025_glo2_hagh_dr_20260924/out/ 两副本）= 20 靶基因 top-marker 稀疏表（每类 18-20 非零基因，列和≈2367），**禁作全转录组参考**。全谱替代件（列和=1e6，从 HRCA 37.7GB 流式重建，脚本留痕）：`/mnt/D/DR_GEO/dr-sc/redo_v2/data/hrca_10class_pseudobulk_cpm.csv`。两处已立 DATA_DEFECT.md，使用史追溯结论：无未纠正下游污染。HRCA 37.7GB 整对象 load 会爆内存——流式重建模式可抄 redo_v2/scripts/s07a_hrca_pseudobulk.py。

## ③ 新 SOP 总纲（聚类/注释任务通用）
`~/.hermes/skills/bioinformatics/sc-cell-annotation` 章"新数据集无监督聚类+注释 SOP（redo-v2）"：三层结构（通用七步/案例参数/组织附录）+ 冻结与变更控制 + 禁用清单 10 条 + 参考资产完整性阻断。kb 出题/阅卷涉及视网膜数据时可直接引用；执行侧检查单在 AGENT_ROLE `sc-integration-annotation`（冲突以总纲为准）。

## ④ 主机
GPU0 自 09:29 掉卡（GSP RPC），llama-qwen 重启循环中——kb 线依赖本地千问的审图/嵌入步骤会受影响（恢复需 root 重载 nvidia）。

依据链全文：/mnt/D/DR_GEO/dr-sc/redo_v2/（SURVEY/REPORT/PROPOSAL/REVIEW/REGRADE 五件）。回执或异议可直接写到本目录。
