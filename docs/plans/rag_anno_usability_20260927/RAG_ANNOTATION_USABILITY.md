# RAG_ANNOTATION_USABILITY — "RAG 现在能不能用于单细胞注释"一页判定（D8，2026-09-27）

> 卡 t_21b905a7｜任务书 BRIEF_RAGANNO.md（本目录）｜PI 原话："你看看 rag 现在能不能用于单细胞注释"
> 性质=盘上证据+外部锚文的决定级评估；零新评测、零 LLM 判读调用、零生产写、零下载。

## 总结论（一句话）

**RAG 不是一个开关，是四个开关：A 证据面供体=今天就能用（已激活在跑，但质量挂在词条+拆弹规则上，不在裸检索上）；B 自由查询辅助=需要一步验证（工具在、真实流量=0，本卡只出设计）；C 入打分=禁止（仅离线审计弃权带回捞，且限视网膜面）；D 外部同类=与 A 用/C 禁的分层结论互相印证。**

## 四形态判定表

### A｜证据面供体形态（RAG 语料→lit digest/KB 词条→三席判读）——【今天就能用·现役】

- **现状**：已激活在跑。2026-09-26 21:33 PI 拍板（A1/A2），MCP 默认 library=all 经 EYEKB_ACT_V6 纳入 retina_v6+face_v6（43→60 类精确+17；OFF 态与 pre 基线全等；泪腺硬禁；回退=env=0）——`plans/activation_20260926/ACTIVATION_COMPLETED.md`、`WIKI/USER_DIRECTIVE_20260926_activation.md`。
- **盘上证据（疗效链，verbatim）**：基线 RUN4-r R1'=15/22、R2'=1/23 PASS → RUN7RG **FAIL**（R1 修复线 17/22 过线+2 丢失 0，但 R2 伤害线 **4/23 破 ≤1**）→ FACEV21 三拆弹 **PASS：19/22 ∧ 0/23 ∧ 保全 2/2**——`plans/run7rg_20260926/RUN7RG_COMPLETED.md`、`plans/face_v21_20260926/FACE_PROTOCOL_V2_1_COMPLETED.md`。眼表线 RUN6-B：P1 22/33（Δ+1 净，翻正4/翻丢3）、P2 擦线 PASS(1/33)——`plans/run6b_20260926/RUN6B_COMPLETED.md`。获批内部疗效版措辞："共识命中 15/22→19/22、对照翻错 1→0；眼表 21/33→22/33"（禁泛化"提升 X%"）。
- **判定要写的核心口径：证据面质量依赖词条与拆弹规则，非 RAG 裸检索。** RUN7RG 的 4 伤害簇 3 类副作用全由词条/旗/跨物种 ranking 内容引发（Q5b::2 描述旗被当过滤用、Q7::52/58 被 `kb_celltype_ranking` 首行 AC 带偏、Q4::23 RPE 词条命中引入新谱系冲突集体弃权）；FACEV21 只改三条**规则行**（禁降级/撤 ranking/判序细化）就把同 4 簇伤害归零且增益 0 丢失。词条害人-救人多案同向：救=KB4 keratocyte 条修好 Q6::15（RUN3-mini 5/5，`WIKI/当前状态.md`）、v6 退役歧义基因修好 Q4::15/Q5b::13；害=Q2::22 MG 词条 4/5 基因无区分度误导三席（v2_prod 不用词典反 728/728 判对，KB5v3 案）、Q6::24 眼表基质四词条集体无区分度（KB6b 复核改判）。更深一层：**RUN7RG Q2::22 反向验证=删词条+hint 反更糟（2/3 回 MG）→误导源主要在基因集先验（GLUL/VIM/CLU 歧义共表达），非仅词条**——"喂更好的检索"不必然治好判读。
- **边界**：①19/22 是冻结面离线疗效数字，face v2.1 三拆弹=**eval_only 未接服务面**，线上默认响应不含 Q7 撤行——**禁直接外推线上**（`WIKI/当前状态.md` 风险提示）；②词条覆盖是硬上限：KB9 眼表补条自检 P1 22/33 FAIL（差 2；残余 11 miss 中 8 属 tie/弃权协议结构位非词条可修）→**新条不注册**、Melanocyte/Schwann 零词条=结构不可达、HC 词条缺口=文献面固有稀缺（`plans/kb9_ocs_20260927/KB9_BUILD_REPORT.md`）；③A2 一周跟票观察窗在跑（触发率异常即回退，T+7 周报 cron 2026-10-03，`plans/obs_followup_20260926/`）。

### B｜自由查询辅助形态（判读时按需向 RAG/MCP 提问）——【需要一步验证·只出设计】

- **现状**：工具在、流量零。五工具=query_marker / **search_literature** / get_kb_page / get_tissue_composition / get_disease_prior（`/mnt/D/EyeKB/mcp_server/server.py` L67-145；任务书所称 "query_lit" 即 search_literature，命名差异见口径冲突表）。服务端留痕层 09-26 21:55 上线：`/mnt/D/EyeKB/logs/mcp_trace/calls_2026-09-26.jsonl` 共 16 行、**全部=query_marker 且全部 tag=selftest_probe**；基线日 ON-default-all 真实流量分母=**0**（`plans/obs_followup_20260926/out/BASELINE_20260926.json`）。统计器 obs_stats.py 已口径自检全绿（重算 RUN6-B：mural **8/33**、rod_bc **0/33**、词条名票 **8/8 全 C 席**，与 RUN6-B 实测一字不差）。
- **判定**：**无对照实验=无结论**。RUN 系列三席吃的是**赛前冻结证据面**（EV_DIGEST jsonl，判读中不提问），自由查询形态与 A 形态的差异（按需取证、不可复现性、查询方差）未测——**不可拿 A 的 19/22 外推给 B**。
- **最小预注册设计（草案，执行归 PI，本卡不跑）**：
  1. **问题**：三席判读下"自由查询臂"是否 R1 不劣且 R2 不破（对照=现役固定证据面臂）。
  2. **唯一变量**=取证方式；考卷复用 FACEV21 冻结面 45 簇（sha `c4a47e39…` 逐字节同一张卷）、三席不变（qwen3.8-max/glm-5.1/deepseek-v3.2、T=0.2）、投票规则不变（RUN4-r 三票共识）、球门一字不降（R1≥15/22 ∧ R2≤1/23），双基线=RUN4-r 15/22 与 FACEV21 19/22。
  3. **B 臂定义**：判读卡不给 EV_DIGEST，给五工具会话权限（ON 态 all=60 类）；每簇留痕必须非空（calllog 现成，进程证据自动可审计）——**零新增基建**。
  4. **先于对比的两道稳定性门**（自由查询天然非确定）：B 臂全量重跑 2 次，簇级共识一致率 ≥90% 才有资格进与 A 臂的对比；每簇调用数/时长记成本列。预算=45×3×2 席票≈270 票，量级同一次 FACEV21 重考，零下载零生产写。
  5. **判读矩阵四格**（全阴性合法）：双过→B 可用（再议替代 A）；修过伤破→B 禁；双不过→维持 A；稳定性门不过→不判、先治非确定性。sha 先落纸再跑，禁调阈值。

### C｜打分输入形态（RAG 证据进自动打分/置信加权）——【禁止（仅离线审计例外）·已裁】

- **现状与裁决**：E1 表面优势 +16.87pp 被泄漏审计击穿（有泄漏列 top1 **84.62%** vs 无泄漏列 **67.74%**；Q5b 面板同源 40/44=91%+lit 背答案双通道）→跨档交 PI（`plans/evidence_scoring_20260926/E1_VERDICT.md`）；E2 去同源后干净 Δ=**+7.66pp**（63.27 vs AB 共识 55.61）仍正、但旗标工作点门失败（AB 共识 111 行真错仅 2，θ∈{0..4} 全拦 0/2、误报 2，无"特异≥80%∧灵敏≥30%"工作点）+否决列 **−6.63pp** vs 最强单席 → 机械 W2；**PI 终裁（09-27）：定档 V2+ 且仅"辅助/离线审计"定位，生产判分禁用、提案线正式关闭**（`E1_VERDICT.md` §9、`plans/e2_decontam_20260926/E2_VERDICT.md` §9，原话"不是代替，是辅助""还是有点用的"）。红线 v2②③同步生效（判分/裁定侧禁食判读同源证据；自动打分栈须 PI 另批）——`WIKI/USER_DIRECTIVE_20260926_redline_rewrite.md`。**禁再开。**
- **唯一例外（有正式化数字）**：弃权带回捞离线审计——E3 正式化：R1 **PASS**（F-RET 弃权带 85 行：现役臂具名 48/对 41=精确率 **85.42%**，双判据过）；R2 **FAIL**（F-3SEAT 弃权带仅 14 行<15 体量门→**85.4% 不能外推出视网膜面**）；R3 改良臂两面 100% 但 48→10 塌缩→双层 SOP。`AUDIT_SOP_v1.0.md` 已按 D5 定稿（09-27 12:19），**零接线不变**——`plans/e3_rescue_20260927/E3_VERDICT.md`。

### D｜外部同类对照（2024-2026，锚文 5 篇）——【印证 A 用/C 禁，B 为领域共同空白】

| 锚文 | 要点 | 与我们结论的对照 |
|---|---|---|
| **CellTypeAgent**（arXiv:2505.08844, 2025; PMC12133089） | LLM 初筛候选+CellxGene 数据库**外证投票**定稿，9 数据集/303 类型/36 组织，主打减幻觉 | =我们 A 形态"判读吃证据面+盲注三席"同构；验证层置于模型之外是共识 |
| **CASSIA**（Nat Commun 2025, s41467-025-67084-x） | 点名 GPTCelltype 的 **hyperconfidence/幻觉**缺陷；多智能体+检索推理，970 类型；marker 增益 ~50 个饱和 | 支持"裸 LLM/裸检索不可信、需检索+复核结构"；marker 饱和≈我们面板窗口/命中密度议题 |
| **SOAR**（arXiv:2412.02915; PMC12641614） | 11 数据集×8 LLM×1226 任务基准：**文献丰富组织（PBMC 等）表现显著好、less-studied 组织差** | 与 KB9 眼表零词条、HC 文献稀缺、眼表覆盖弱≈9 簇（RUN5）同向=覆盖决定上限 |
| **AnnDictionary**（Nat Commun 2025, s41467-025-64511-x） | LLM 注释**大类可靠、谱系近邻系统性偏**（basal→epithelial；细胞 vs 类型 15-20pp 差） | =我们 coarse 名/细分名边界与 Q6::24 pericyte/SMC 通签（生物学不可分）同类失效模式 |
| **scAgent**（arXiv:2504.04698, 2025） | planning+memory+30 插件工具 agent，160 类型/35 组织，跨组织通用 | agent 化=我们 MCP 五工具方向；**其评测同样不报"自由查询 vs 固定证据面"对照** |

对照结论：外部无一例外把检索/证据当**输入侧**资产（agent 化、外证投票、多智能体复核），**没有任何主流系统把 RAG 检索结果直接当终裁打分器**——与 E1/E2 的 W2 裁决独立同向；"判读时自由查询是否优于固定证据面"外部也无发表对照=共同空白，我们的 B 设计若做成即是可对外输出的增量点。

## 三档清单

- **今天就能用**：①A 形态——RAG/KB→冻结证据面→三席盲注（现役：60 类 ON 态，回退 env=0；引用疗效必带边界①②③）；②C 的离线审计子集——弃权带回捞 SOP（仅 F-RET 面、仅离线、按需执行，不接线）。
- **需要一步验证**：①B 形态 A/B 预注册（§B 设计，执行归 PI）；②face v2.1 三拆弹接线上外的时机（另卡+同球门，A 形态内迭代）；③A2 跟票 T+7（10-03 cron，例行）。
- **禁止**：①RAG 同源证据进生产判分/置信加权/复合 QC（红线 v2②③+E1/E2 裁决，禁再开）；②把 19/22 外推线上；③把 KB9 未注册新条当可用；④"提升 X%"泛化措辞；⑤自动打分栈生产化未经 PI 另批。

## 口径冲突表（与 WIKI 现行口径）

| # | 事项 | WIKI/任务书口径 | 盘上实证（路径） | 处置 |
|---|---|---|---|---|
| 1 | "query_lit 现役"（BRIEF） | 任务书称 query_lit | server.py 五工具无此名，实为 **search_literature** | 仅命名差异，登记不改 WIKI |
| 2 | "统计器有真实流量数据可查"（BRIEF） | 暗示已有流量 | 留痕 16 行全 selftest、真实分母=0（BASELINE_20260926.json） | 如实改述："流量池已建、自由查询真实流量=0"，B 判定按后者 |
| 3 | 19/22 适用域 | 对外疗效口径已解锁（activation directive） | 同件仍禁外推线上+face v2.1=eval_only | 无冲突，作 A 边界①引用 |

## 来源（全部盘上冻结件）

WIKI：`/mnt/D/OcularKB/WIKI/INDEX.md`（09-24~09-27 条）、`当前状态.md`、`结论速查.md`、`USER_DIRECTIVE_20260926_activation.md`、`USER_DIRECTIVE_20260926_redline_rewrite.md`、`USER_DIRECTIVE_20260927_scoring_wave.md`（D8 放行+追加一）。
Plans（`/mnt/D/EyeKB/plans/` 下）：`run7rg_20260926/RUN7RG_COMPLETED.md`、`face_v21_20260926/FACE_PROTOCOL_V2_1_COMPLETED.md`、`run6b_20260926/RUN6B_COMPLETED.md`、`activation_20260926/ACTIVATION_COMPLETED.md`、`obs_followup_20260926/OBS1_COMPLETED.md+out/BASELINE_20260926.json`、`evidence_scoring_20260926/E1_VERDICT.md`、`e2_decontam_20260926/E2_VERDICT.md`、`e3_rescue_20260927/E3_VERDICT.md+AUDIT_SOP_v1.0.md`、`kb9_ocs_20260927/KB9_BUILD_REPORT.md`、`kb6b_face_20260925/`（改判案）。
代码：`/mnt/D/EyeKB/mcp_server/server.py`（五工具+calllog 留痕）。
外部：arXiv:2505.08844 / Nat Commun 2025 s41467-025-67084-x / arXiv:2412.02915 / Nat Commun 2025 s41467-025-64511-x / arXiv:2504.04698（摘要级检索，无全文下载）。

*卡 t_21b905a7；红线合规：只写本目录、全线只读、零 LLM 判读、零生产写、零下载。*
