# PIPELINE_COMPLETED — 九步批注入口打包进仓（收尾件）

日期：2026-09-29 ｜ 卡：t_ba57ca24 ｜ 执行：pi-chief ｜ staging 仓：`/home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928`

## commit 清单（本地已提交，**未 push**——按任务书交协调者复核后代推）

| commit | 层 | 内容 |
|---|---|---|
| `cef5c03b623b612bd41390cf15e9acd60c1959f5` | 代码 | `pipeline/`（run_pipeline.py 入口、stage_a_processing.py、stage_b_evidence.py、llm_assist.py、requirements.txt、README.md）+ 仓根 README《批量注释（pipeline/）》节与组织结构行 |
| `a0a85bb` | 证据 | `docs/plans/pipeline_pub_20260929/`（BRIEF 逐字节副本、GATES.md、T3 sha 台账 PRE/POST、四形态冒烟输出全套、日志、fixture 构造脚本） |
| 本件所在 commit | 收尾 | PIPELINE_COMPLETED.md |

父提交链：`cef5c03` 基于 `02daf01`（执行期间协调者侧另有 README 提交落地，线性可快进）。

## 交付物 → 任务书对照

- **输入两形态**：10X 三件套目录（单份=单样本；父目录多份=多样本，重复 barcode 自动唯一化）或 `.h5ad`；命令行强制 `--species human|mouse --tissue <词典已知组织>`（`--list-tissues` 可枚举），可选 `--sample-group/--group-col` 分组。✅
- **阶段 A**：Scanpy/Harmony/Scrublet（提炼自仓内实测锚点 `docs/plans/figure_uplift_20260928/scripts/v2_o1o3...py`），输出 processed.h5ad + 质控图（线粒体/基因检出/doublet/UMAP 前后）。✅
- **阶段 B**：复制改写 `kb2_mcp_v2.py`（原文件未动）→ stdio 拉起仓内 `mcp_server/server.py` 逐簇采五工具；evalset 冻结卷绑定全部解除。✅
- **输出**：`annotation_evidence_report.json/.md`（每簇 top 基因/query_marker 候选得分/get_tissue_composition 越界旗标/get_disease_prior 原文提及（有分组才启用）/search_literature 片段+PMID/三分级）+ `decisions_template.csv`（accept/modify/abstain 三值列全空）+ 质控图。✅
- **纪律红线**：默认零 LLM（断网语义实测通过）；弃权合法（T1c 真实 ENSG 未映射输入 15/15 needs_review 实证）；无任何自动打分/定标逻辑（分级=预注册机械旗，触发规则逐条写进报告）。✅

## 六门结果（详见 GATES.md）

T1 冒烟（h5ad+三件套两形态×四变体）PASS ｜ T2 黄金 41 复跑 41/41 逐位 PASS ｜ T3 密钥扫描零真实值 + 生产盘 kb/mcp_server 125 件 sha 前后全等 PASS（附 calllog 追加写生产日志一项如实登记，见 GATES-T3）｜ T4 零 LLM 断言语义 PASS ｜ T5 README 新增节（黑话扫描 0）PASS ｜ T6 中间产物全保留 PASS（病人来源数据件按仓隐私规不入库、留盘，登记 GATES-T6）。

## 遗留给协调者的三件事

1. **代推**：本地 3 个 commit（禁 push 红线），复核 GATES.md 后推送。
2. **建议另卡**：`mcp_server/calllog.py` 的 `TRACE_DIR` 硬编码 `/mnt/D/EyeKB/logs/mcp_trace`——在任何 stdio 拉起 server 的机器上都会尝试追加写该绝对路径。本卡禁改 mcp_server/ 故仅登记；公开用户机器该路径不存在时 calllog 自带兜底不影响服务，但 env 可覆盖路径是更干净的长期方案。
3. **口径确认**：T6 的".gitignore 只排除 >50MB 数据件"与仓既有"病人衍生数据永不入库"规则存在字面冲突，本卡取隐私优先（未动 .gitignore，用路径排除法），GATES-T6 有记录，如裁定不同可低成本补交小体积 fixture。
