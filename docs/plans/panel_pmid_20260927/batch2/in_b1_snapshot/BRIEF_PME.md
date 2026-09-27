# BRIEF_PME — 面板证据链补录第一批（338 对无记录先验，PI 放行 20260927）

## 上游与继承（先读，逐条核对）
- 放行件+裁决继承清单：/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md
- 对象来源：/mnt/D/EyeKB/plans/e2_decontam_20260926/（data/e2_matrix_rows_summary.tsv + out/e2_panel_water.tsv：567 个库-类-基因对中，纯内部派生 199 + 无记录文献先验 338；E2 §6.3 定性"338 对证据链缺失是库文件工程问题非概念问题"，v4.1 八类及其 v5/v6 继承行为重点）
- 方法先例（只读）：plans/hc_letre_20260925/（HC-LITRE 文献三通道审法与诚实阴性纪律）、kb5v3 的 OLS 回证留档命名惯例
- 注意：E2R 卡并行在跑，pmid_context 120 对归它管——本卡只做 338 对"无记录"侧，两卡清单禁重叠（重叠对数如出现，登记后让给 E2R）。

## 任务
1. 从 E2 产物提取 338 对（库,细胞类型,基因）清单，按类分批（v4.1 八类教科书强锚优先：RHO/NRL 类）。
2. 逐对补外部文献链：EuropePMC/PubMed 检索"该基因是/不是该细胞类型 marker"级可核证据，收录标准=PMID 可解析 + 摘要级直接支持（不做全文获取）；每对输出：PMID、标题、hit 摘要一句、分级 strong/weak/none。查无=none 如实登记（诚实阴性），禁软证据冒充 strong。
3. 产出 sidecar：evidence_chain_supplement_v1.json（旁挂新文件，**kb/ 现有一切文件字节不动**，面板 JSON 零触碰），格式对齐 kb 侧 sidecar 先例（如 markers_cl_alignment_v1.json 的可回溯要求）。
4. 汇总账：strong/weak/none 计数 + "S1 弃权面可恢复量"预估（若补录件未来被评测口径认账，E2 S2 下界与 S1 之间 17pp 间隙的可收敛部分），仅出预估表，**不改 E2 任何数字**。

## 判读矩阵（预注册）
| 观测 | 记账 |
|---|---|
| strong 覆盖 >=50% 无记录对 | 工程缺口第一批关闭过半，剩余列第二批清单 |
| strong 30-50% | 部分成立，按类拆分列缺口 |
| strong <30% | "无记录先验多不可外部证"定性，反馈 KB 线：这些行的面板权重应降档（提案，不执行） |

## 领地与红线
- 全部产物只落 /mnt/D/EyeKB/plans/panel_pmid_20260927/；kb/、mcp_server/、E1/E2 目录只读 + sha 台账；禁写 e2r_s5audit_20260927/、e3_rescue_20260927/、kb9_ocs_20260927/。
- 零 LLM 判读调用（检索与判支持度可用规则+worker 自审，逐对留检索原始返回）；下载仅摘要级，>1GB 立即停卡。
- 完成或遇阻必须调 kanban_complete/kanban_block 落卡；中间产物全保留；量大耗不尽时分批落盘 + kanban comment 留痕进度。
- 工作目录：/mnt/D/EyeKB/plans/panel_pmid_20260927/（自建）
