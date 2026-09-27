# PME_NOTE — 面板证据链补录第一批收官（t_f16d4e9f，2026-09-27）

## 一句话结论
E2 定性的 338 对"无记录文献先验"逐对补 EuropePMC 可核外链后，**222/338（65.7%）拿到 strong 级外部链**
（PMID 可解析 + 摘要级句内 基因∧类∧marker 词直接支持），判读矩阵落 **row1：工程缺口第一批关闭过半**；
支持 E2 §6.3 定性——这些行的证据链缺失是**库文件工程问题，非概念问题**（v4.1 八类教科书锚 29/40=72.5% 外部可证）。

## 账（338 行 / 280 unique 类-基因键）
| 层 | strong | weak | none |
|---|---|---|---|
| 行账（判读矩阵口径） | **222（65.68%）** | 62 | 54 |
| 键账（280，审计后终态） | 177 | 50 | 53 |

- 诚实阴性合法：54 行 none 如实登记（如 retina_v6 BC/AC 的通路统计派生基因 BCAT1/HS3ST4/ZNF804B/TACR3/GRM7 等，
  外部文献确无"该基因是该类 marker"级断言——v6 repair 面板的数据驱动派生特征，与 E2 定性一致）。
- v4.1 八类锚：Rod 5/5、Cone 5/5、RGC 5/5、Astro 5/5、BC 3/5、MG 3/5、HC 2/5、AC 1/5（AC/HC 缺口=第二批主攻，
  其 v4.1 五基因多为 sc-atlas 统计派生如 EYA4/SHISA6/SPHKAP/VAT1L/NAALAD2）。
- membrane 免疫系 strong 率最高（Mac_Tissue 14/15、T 10/11、Granulocyte 10/13）；
  最弱=cDC2 1/6、Mono_Nonclassical 2/5、Endo_Patho 3/6（病理态类名本身外部文献少用）。
- 全表 out/pme_accounts.tsv；分类账 out/evidence_chain_supplement_v1.json → counts_by_class。

## 方法与留痕
- 预注册 PME_PREREG_v1.md（跑数前落纸，sha 记 ledgers/sha_pre.txt）；修正 A1-A5 全部先于/独立于选择性改判、对称施加：
  - A1 双遍检索（relevance 非 strong 补 sort=CITED）；A2 rods/cones 裸词护栏；A3 pageSize 50+并发；A4 并发 8；
  - **A5 规则 bug 修复**：APC_MHCII_high 类正则与 HLA-D*/DR* 基因名自循环——去循环后全部 280 键统一重判
    （ledgers/regrade_diff.txt，6 键降档：FCGR1A→none、HLA-DMB/DPA1/DQA1/DQB1→weak、RGS1→none）。
- worker 自审（PREREG §4，零 LLM 判读调用）：191 条 strong 证据句**全部过目**，降级候选逐键看双证据槽，
  终态 14 键 strong→weak（归属错误/机制句非 marker 断言/类词来自他基因或基因全名展开），
  修正与理由见 ledgers/audit_fixes.tsv，原始引擎判定不掩（grade vs final_grade 双列）。
  审计中救回：PDE6B/CSF3R/MPO/PRRX1×2/SSR4/XBP1/PTTG1/TOP2A/SKAP1/LCK/RAMP2/VWF/IRF8(Micro)/IRF7 等 15 键
  （slot2 有合格归属句，不因 slot1 弱句误杀）。
- 逐对检索原始返回全留 ledgers/raw/（280 文件，含 URL+双遍 raw JSON）。
- 与 E2R 领地核对：338 行中 pcx_ext=Y = **0**，两卡清单天然不相交（ledgers/e2r_overlap_check.txt），无让渡。
- 与 E2 分工：E2R 只管 pmid_context 120 对身份核验；本卡只管 338 无记录侧外部链。零重叠零覆盖缺口。

## S1 弃权面可恢复量预估（out/s1_recovery_estimate.tsv；仅预估，未重跑 E2 打分，E2 任何数字未动）
S1−S2 间隙 17.35pp（63.27 vs 45.92，E2_VERDICT §5）。若补录件未来被评测口径认账：
- 结构下界（strong-only 认账）≈ 17.35×222/338 = **11.40pp** 可收敛
- 结构上界（strong+weak 认账）≈ 17.35×284/338 = **14.58pp**
（最乐观线性归因：假设间隙全部正比于 no_record 链覆盖；类组成交互/候选池效应未计，仅供 PI 判断补录价值量级。）

## 红线遵守
- kb/、mcp_server/、E1/E2 目录、e2r/e3/kb9 三卡目录：**字节未动**（ledgers/sha_pre.txt 42+条 vs sha_post.txt 全一致）。
- 零 LLM 判读、零生产码 import、零全文下载（仅摘要级 API JSON，~35MB 量级）。
- sidecar 为旁挂新文件 out/evidence_chain_supplement_v1.json，面板 JSON 零触碰；格式对齐 markers_cl_alignment_v1.json 可回溯要求。

## 已知局限（如实登记）
1. 符号-only 匹配：摘要惯用产物全名（glutamine synthetase↔GLUL、S100B 类钙结合蛋白名）时欠证 → GLUL/S100B 判 weak；
   全类统一不开别名后门（PREREG A3），第二批可考虑人工别名表并全类对称。
2. "expressed in <class>"接受为 membership 型支持（判例 CPNE5→AC）；若 PI 采"类特异/exclusive"严格档，strong 数将显著下降——口径留给 PI。
3. 摘要级单遍语义：部分真 marker 断言在全文/图注中，摘要未含 → none 不等于"外部文献不存在"，仅"摘要级不可核"。

## 第二批清单（判读矩阵 row1 义务）
103 个非 strong 键（50 weak + 53 none）已列 out/batch2_backlog.tsv；weak 优先（补第二检索式/别名表即可救），
none 侧 v6 repair 统计派生基因建议维持诚实 none 并走 KB 线"面板权重降档提案"路径（本卡不执行）。
