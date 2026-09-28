# VERDICT_OBLIGRUN — KB9 k9_ocs §10-6 义务 run 裁决（t_c145db7c，2026-09-28）

**VERDICT = NOT_READY（票面作废条件命中 → block 上报，作废留痕，不重跑粉饰）**

判读依据=PREREG_OBLIGRUN.md（sha bfd8836d1ef3b83f582325f0636674dd14112d420f505b59b3c2155bed04b52f，先于一切执行落纸）§7 判读矩阵三分支之第三支：
「诊断表不一致/票面作废条件命中 → block 上报，作废留痕不重跑粉饰」。
本 run 未进入正式三席投票（**票预算消耗 0/150**，零 LLM 票产生）。

## 逐门数字

| 门 | 结果 | 证据件 |
|---|---|---|
| OB-1 AV2-5(c) 历史 ON 态门对账 | **清** | out/OB1_ledger.tsv（339 行）：8 不变簇输入面逐字节对账通过；25 变化簇漂移严格限于 kb_marker_ranking+lit 两字段（0 越界）；批组成快照=RUN5 原批（7 批 5,5,5,5,5,5,3）；RUN5 请求原文未逐字节留档→以 runner sha+指令 sha+面件 sha 三件钉定确定性重渲染 21 请求替代（与 RUN5 原 runner build_prompt **逐字节等价 21/21 实证**，logs/requests_reconstructed_run5/）；库态 RUN5→今漂移（library_activation_only=Q6::21/4/5/28/29）如实登记；本 run 零复用存档票，AV2-5(c) 触发条件不成立且对账义务照做 |
| OB-2 A07 投票前诊断表首跑 | **PASS** | out/pre_vote_diagnostics.tsv（57 行，§6 全 11 列）+ out/OB2_notes.md：硬断言 post_shield top3==票面 ranking 33/33 全等（0 不一致）；Q6::8/Q6::26 对照簇逐簇单列；Q6::26 型掏空回退可指认（APC_MHCII_high n_raw=3→n_shielded=3→n_remaining=0 头部掏空；另 Q6::11 APC/pDC、Q6::2/3/30 Mono_Classical、Q6::6/25 Mac_DAM_LAM 共 9 处掏空行登记） |
| OB-3 22 视网膜簇 Arm1/Arm2 完整 ranking 一致性 | **清** | out/OB3_consistency.tsv：22/22 簇 Arm2(R1 镜像)==native ON 全列表逐位相等（次序+n_shared）；Arm1 去 k9 后与 native 同序（stable-sort 无副作用）；top3==query_marker ON（G1 语义扩展至视网膜输入 22/22）；去重碰撞=0（ON 五库与 K9 四名下划线无关，k9_build:: 前缀键零出现）；k9 在 Arm2 零泄漏；k7 存档 top3 重放逐字节对账 22/22。口径注：Arm1 全列表 k9 进入=3 簇（Q4::24/Q7::29/Q9::0），其中 2 簇进 top3，与注册包"泄漏 2/22（top3 口径）"自洽；规则臂泄漏 0 维持 |
| OB-4 lit 逐条同源排除筛查 | **不清（票面作废条件命中）** | out/OB4_lit_hits.tsv（64 条/12 PMID 逐条判定）+ out/OB4_lit_screening.md：命中 1 篇 Q6 truth 来源标注论文——**PMID 36712326（Maiti et al., PNAS Nexus 2022；通讯 Chakravarti；= D002 构成研究 chakravarti_GSE218123 之 source paper，三重证据：论文 Data Availability 自存 GSE218123 + GEO 系列题名与论文题名逐字一致 + D002 obs.study×GSM 直读 4,388 评测细胞）**。其 lit 行进入票面 2 簇（Q6::11、Q6::7，均 truth=Endothelium，lit 行 ct=Endo）；片段级复核实锤其 Results 段含内皮细胞群→标签指派关系（"Endothelial cell types in the cornea and the organoid"）。注册包 §9 排除对象明文"含 Q6 truth 来源标注论文及其补充表"→ 应剔除而未剔除 = 冻结票面含未排除来源标签回证通道（E1"lit 背答案"机制实例） |

## 作废留痕（不粉饰条款执行）

- 票面 EV_DIGEST_SLIM_q6_oblig.jsonl（sha ba76b6ce1af1654e…，=KB9 C 臂冻结面 copy）**按 §9 口径判为受污染票面，不得用于出数**；本 run 依预注册不开跑（不产出"带污染面 P1/P2"这类可被下游误用的数字）。
- 历史 C4 P1=22/33 FAIL（out/kb9_verdict.json）不回改；TIEP C2b 反事实 29/33 不替代本轮当期数字；两者均仅互引。
- 其余 10 篇命中判"保留"（含披露项：38177186=lako GSE155683 再分析非来源论文/own-deposit GSE249150 非 D002；37443842 综述；39422453 自存 GSE272434/271132 非 D002）。
- 残余限制：chen_cornea/chen_limbus/chen_sclera（评测池 79,571/100,000 细胞主体）obs 无 accession/GSM 前缀，本地不可解析 source paper；12 命中 PMID 逐篇作者/题名/自存声明核过均非 chen 系（Ligocki/Kitao/Li M…）。若日后获得 chen 系权威映射须重跑本筛查。

## 领地核验

- 红线领地 kb/、mcp_server/、evalset/、注册包、overlay、lit 语料：POST sha 复验 **60 件 0 写入**（ledgers/SHA_POST_OBLIGRUN.txt）。
- 唯一外部变更=USER_DIRECTIVE_20260928_eyekb_improve_wave.md：指令主档追加（13:40:45 追加五/六；追加四放行文本与本 run 开跑时所读逐行一致）。我 PRE 快照恰在其追加完成前 7 秒，如实登记，非本卡写入。

## 修复路径（归 PI/协调者批准——两案均改变任务书钉定票面，超出本卡权限，故 block）

- **案 A（建议，改动面最小）**：票面 v2.1=C 臂面逐行剔除 2 条 36712326 lit 行（ranking/gene 字段逐字节不动→OB-2 硬断言在新面可重算；lit 字段面级变化仅限 Q6::7/Q6::11 两行）；重跑 OB-4 筛查（应 0 剔除）后按本预注册同参开跑三席 99 票。
- **案 B（管道级修复）**：lit 重建轮——search_literature 管线加装 §9 同源排除过滤器后对 25 变化簇重建 top_k=4（回填下一非来源命中）→ 面 v2 重冻结 + OB-2/OB-4 重跑 + 三席票。改动面大（lit 回填新行本身亦须过筛查），但一次性把"每次重建落盘筛查"的管道义务固化为代码。
- 两案后续=本 PREREG 同球门（P1≥24/33、P2 strict≤1/33、票规 v2 C2b、上限 150 票）正式 run；OB-5 激活永久门不受任何影响，仍归 PI 另批。

产物清单：PREREG_OBLIGRUN.md（+sha）、face/EV_DIGEST_SLIM_q6_oblig.jsonl、out/{OB1_ledger.tsv, pre_vote_diagnostics.tsv, OB2_notes.md, OB3_consistency.tsv, OB4_lit_hits.tsv, OB4_lit_screening.md, OB4_gse_scan.json, VERDICT_OBLIGRUN.md}、ledgers/{SHA_PRE_OBLIGRUN.txt, SHA_POST_OBLIGRUN.txt, PREREG_OBLIGRUN_SHA.txt, FACE_OBLIG_SHA.txt, immune_fold_names.json}、logs/{batch_composition.json, requests_reconstructed_run5/(21+INDEX)}、scripts/o{1,2,3,4}_*_t_c145db7c.py。
