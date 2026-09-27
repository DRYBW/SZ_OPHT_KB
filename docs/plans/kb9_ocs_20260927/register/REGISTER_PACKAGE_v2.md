# KB9 眼表词条注册申请包 v2（重装件 · 过 REVIEWER_LLM 二审前版本）

版本：reg-v2.2-20260927（v2.0 经二审 xhigh REVISE→v2.1；v2.1 经三审 xhigh REVISE（A09/A12/A13 闭合，A06/A19+话术 1/2/4/7 偏差）→本版按最小修订清单 1–5 逐项闭合；审件=round2/、round3/） ｜ 出件卡：t_62bb0dfe（BRIEF_KB9REG，D10 放行）｜ 底件：kb9_ocs_20260927/build/ + KB9_BUILD_REPORT.md（22/33 FAIL / 0/33 PASS 口径原样继承，未改一字数字）
上游裁决：recheck/RECHECK_REPLY_20260927.md（REVIEWER_LLM xhigh，prompt sha 3072…52d274d）+ RECHECK_ACTIONS.md（接受 14 / 待 PI 5）｜ 放行件：USER_DIRECTIVE_20260927_scoring_wave.md 追加二 D10
状态行：**过外审待 PI 批注册**（2026-09-27 REVIEWER_LLM xhigh 第五轮签发 ACCEPTED：可送 PI 批注册；本轮签发不等于 PI 批准注册，亦不授权执行/接线/激活。本包为申请文本，未注册、未接线、未激活——零 kb/ 写、零 mcp_server/ 写、零生产路径触碰；批不批、何时接线均归 PI）。审链登记=register/ROUNDTWO_VERDICT_20260927.md。

## 0. 标题页定位限定声明（A01，标题页级，随一切下游文本强制携带）
本包所辖词条与证据装配规则，属**开发集（D002 眼表 578K，作者标签参与规则开发）上的定向修复 + 回归检查**：
- 规则开发消费了 D002 作者分组标签（R2/R3 屏蔽表源自 author_class_markers_data.tsv top60 口径；R1 适用范围依据 D002 标签体系；新词条参考池=作者类池）。文件提前冻结可防后选，不消除标签依赖（REVIEWER_LLM §1）。
- 自检 P1=22/33（球门 ≥24 未达，FAIL 如实报）与 P2=0/33（≤1/33 达）均为**该开发集上的工程验收结果，不构成独立验证的性能增益**；24/33 不可作有依据的预测（A16 模板见 §7）。
- 红线操作定义（D10 已落定文本，A02 关闭引用）：**判读/取证侧允许标签派生的适用性/屏蔽规则（注册与报告须自带"开发集自检"限定声明）；判分/裁定侧禁食标签派生证据；离线审计 SOP 为唯一例外且限 W2 边界。** 本包全部产物按此定义归位：词条+屏蔽规则=判读/取证侧，随件携带本限定声明。

## 1. 注册物清单（申请正文）
| # | 注册物 | 载体 | 依据条款 |
|---|---|---|---|
| R-1 | 新词条 4 条：Melanocyte（CL:0000148）/ Schwann（CL:0002573）/ Conj_epithelium_suprabasal（CL:1000432 借父条+layer_descriptor）/ Limbus_Sclera_fibroblast_C1（CL:0000057 挂父条+subtype），均 applicability=ocular_surface_only | build/markers_k9_ocs_increment.json（未改动） | §2 准入判据 + SUPRABASAL_RECHECK.md |
| R-2 | R1 组织适用性规则（改为逐条 ID—适用范围表驱动，弃"来源文件整批排除"语义） | register/A06_R1_ITEM_SCOPE_TABLE.tsv（30 条排除项逐条生物学依据 + 4 新条反向 scope） | §3 |
| R-3 | R2/R3 对称共享基因屏蔽表（眼表面证据装配层） | out/kb9_shared_gene_shield.tsv（283 条数据记录：kept 225 / R2R3_shield_block 28 / R1_drop 30；含表头共 284 行）+ kb9_face_effective_genesets.json | §3、§4 |
| R-4 | 装配规则 v2（top3 准入、候选不足、加载位置、平票、保真门双态） | 本包 §4（AV2-1..5，冻结文本） | A05/A12 |
| R-5 | crosswalk 扩展表（投票前已冻结；既有名称映射零改动） | build/KB9_CROSSWALK_ext.tsv（6 行，逐行 provenance）+ 冻结件 work_t_d1ca11b0/KB_Q6_crosswalk.tsv | §5 |
| R-6 | 投票前诊断表输出规格（注册条款：下一波及一切激活后 run 的强制输出件） | 本包 §6（spec） | A07 |
| R-7 | agg 参考池×D002 study/donor 重叠登记表 | register/A03_OVERLAP_REGISTRY.tsv（实算） | §2 |
申请分两案（归 PI 选择，本包不预设）：**案 A**=仅注册 R-1 中 Melanocyte+Schwann 两词条（仅补词条，不施加 R2/R3 屏蔽规则；填补 Melanocytes/Schwann 两类零词条的结构缺口——回退与票面含义受案 A 限制条款约束）；**案 B**=全量（R-1 全部 + R-2/R-3 屏蔽规则）。两案共同前提=本包 §0 限定声明随件生效；激活均需另卡 + 同球门重测通过（face v2.1=eval_only 红线沿用）。
案 B 实测票面：P1 22/33（FAIL，G−L=4−3=1<3，见 §7）/ P2 0/33（接管清零，Q6::11/Q6::3 型接管不复现）。案 A（不含屏蔽）**尚未单独运行票面评测**。不施加屏蔽规则不保证零回退；新增候选仍可能改变 top3、提示内容及最终判读。补齐原先缺失的候选类别仅改善结构可达性，不等于已经实现正确分类或达到 P1 球门。其证据目前仅到词条准入与火灾审计层，如实登记，不得声称"已测"。

## 2. agg 参考池 × D002 study/donor 重叠登记（A03 实算件）
计算件 register/scripts/a03_overlap_calc.py（只读 agg_kb6b_v1.npz + D002 obs + evalset/clustering/Q6_clusters.tsv；npz 池层与 h5ad 逐格一致，评测面 100,000 barcode 全部命中 D002）。要点：
| 词条池 | 池细胞 | 评测 33 簇内细胞 | 池 study 数 | 评测内 study | 池 donor(study×donor 对) | 评测内 donor |
|---|---|---|---|---|---|---|
| Melanocyte（Melanocytes 作者池） | 7,209 | 1,230 | 9 | 9 | 46 | 46 |
| Schwann（Schwann_M∪Schwann_N） | 6,059 | 977 | 7 | 7 | 48 | 48 |
| Conj_epithelium_suprabasal | 7,264 | 1,278 | 9 | 6 | 36 | 25 |
| Limbus_Sclera_fibroblast_C1 | 33,033 | 5,714 | 9 | 9 | 67 | 62 |
**结论（登记为事实，采二审强制话术）**：四个参考池的细胞均取自 D002，因此参考池与本次评价在数据来源上完全同源；这不表示全部参考池细胞、study 或 study×donor 对均进入了评价面，各层面的实际交集以 §2 表为准。本包不存在独立供体验证，P1/P2 仅为开发集工程验收结果。案 A 未单独运行判读票面，不得推定其 P1/P2 结果。suprabasal 池 96.9% 细胞来自 chen_limbus（供体集中度另披露）。

## 3. R1 条目—组织适用范围表（A06：逐条生物学依据，文件降为实现索引）
全表如下内联（载体 register/A06_R1_ITEM_SCOPE_TABLE.tsv；34 行=30 排除条目+4 新条反向 scope；生成件 scripts/a06_scope_table.py 由遮蔽表 R1 行与词条库消歧逻辑机械导出，条目 ID 与实跑消歧键一致；细胞身份=库内基因锚+冻结 crosswalk 别名注双证：**MG=Müller 胶质（RLBP1/GLUL/SOX9/S100B）、Astro=星形胶质（GFAP/AQP4/SLC1A3）、Micro=microglia（C1QB）**——消解二审所指身份混写；排除依据=组织解剖学+细胞谱系，不以"作者词表缺席"作生物学不存在证明）：

| entry_id | class | owner_file_firstload | all_files_carrying_class | scope | bio_reason | dup_handling | impl_note |
|---|---|---|---|---|---|---|---|
| Rod | Rod | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 视杆光感受器：组织解剖学上仅存在于视网膜神经层（marker 身份锚 RHO/NRL/NR2E3），角膜/limbus/巩膜/结膜无此细胞层，该条 scope=retina_only：眼表面材料证据装配不计入其 kb_marker_ranking（对命中来源不作穷尽断言） | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| Cone | Cone | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 同 Rod（视锥光感受器，仅视网膜外神经层） | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| BC | BC | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 双极细胞：视网膜内神经元，仅存在于视网膜内神经层，眼表面组织无该层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| AC | AC | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 无长突细胞：视网膜内神经元，同上 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| HC | HC | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 水平细胞：视网膜内神经元，同上 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| RGC | RGC | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 神经节细胞：视网膜输出神经元，胞体位于视网膜神经节细胞层（眼球后极），角膜/limbus/巩膜/结膜 portal 取材范围不含该层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| MG | MG | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=Müller 胶质（v4.1 基因锚 RLBP1/GLUL/SOX9/S100B；冻结 crosswalk 别名注=Müller glia 视网膜特有）：视网膜专属巨胶质，眼表面组织无 Müller 细胞 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| Astro | Astro | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=星形胶质（v4.1 基因锚 GFAP/AQP4/SLC1A3；冻结 crosswalk 别名注=astrocyte 视网膜/中枢）：视网膜内星形胶质，与眼表面组织学细胞群不同实体；RUN5 实证 Q6::13/22/16 被 MG|Astro 接管即此二类 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| Micro | Micro | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=microglia（v4.1 基因锚 C1QB 等小胶质标志）：CNS 常驻巨噬谱系词条；眼表面髓系信号由 Macrophages/Monocytes 词条承载（其 kept 行为见遮蔽表），本条在眼表面装配中不计入排名 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| RPE | RPE | markers_v4.1_clean.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 视网膜色素上皮（基因锚 BEST1/RPE65 类/LRAT/RDH5/MITF）：单层色素上皮位于视网膜侧，与角膜/结膜上皮不同胚胎起源（神经外胚层诱导 vs 表面外胚层），组织解剖学上不在眼表面 portal 取材层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::Rod | Rod | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 视杆光感受器：组织解剖学上仅存在于视网膜神经层（marker 身份锚 RHO/NRL/NR2E3），角膜/limbus/巩膜/结膜无此细胞层，该条 scope=retina_only：眼表面材料证据装配不计入其 kb_marker_ranking（对命中来源不作穷尽断言） | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::Cone | Cone | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 同 Rod（视锥光感受器，仅视网膜外神经层） | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::BC | BC | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 双极细胞：视网膜内神经元，仅存在于视网膜内神经层，眼表面组织无该层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::AC | AC | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 无长突细胞：视网膜内神经元，同上 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::HC | HC | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 水平细胞：视网膜内神经元，同上 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::RGC | RGC | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 神经节细胞：视网膜输出神经元，胞体位于视网膜神经节细胞层（眼球后极），角膜/limbus/巩膜/结膜 portal 取材范围不含该层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::MG | MG | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=Müller 胶质（v4.1 基因锚 RLBP1/GLUL/SOX9/S100B；冻结 crosswalk 别名注=Müller glia 视网膜特有）：视网膜专属巨胶质，眼表面组织无 Müller 细胞 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::Astro | Astro | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=星形胶质（v4.1 基因锚 GFAP/AQP4/SLC1A3；冻结 crosswalk 别名注=astrocyte 视网膜/中枢）：视网膜内星形胶质，与眼表面组织学细胞群不同实体；RUN5 实证 Q6::13/22/16 被 MG|Astro 接管即此二类 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::Micro | Micro | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=microglia（v4.1 基因锚 C1QB 等小胶质标志）：CNS 常驻巨噬谱系词条；眼表面髓系信号由 Macrophages/Monocytes 词条承载（其 kept 行为见遮蔽表），本条在眼表面装配中不计入排名 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_interneuron::RPE | RPE | markers_v5_retina_interneuron.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 视网膜色素上皮（基因锚 BEST1/RPE65 类/LRAT/RDH5/MITF）：单层色素上皮位于视网膜侧，与角膜/结膜上皮不同胚胎起源（神经外胚层诱导 vs 表面外胚层），组织解剖学上不在眼表面 portal 取材层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::Rod | Rod | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 视杆光感受器：组织解剖学上仅存在于视网膜神经层（marker 身份锚 RHO/NRL/NR2E3），角膜/limbus/巩膜/结膜无此细胞层，该条 scope=retina_only：眼表面材料证据装配不计入其 kb_marker_ranking（对命中来源不作穷尽断言） | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::Cone | Cone | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 同 Rod（视锥光感受器，仅视网膜外神经层） | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::BC | BC | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 双极细胞：视网膜内神经元，仅存在于视网膜内神经层，眼表面组织无该层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::AC | AC | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 无长突细胞：视网膜内神经元，同上 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::HC | HC | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 水平细胞：视网膜内神经元，同上 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::RGC | RGC | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 神经节细胞：视网膜输出神经元，胞体位于视网膜神经节细胞层（眼球后极），角膜/limbus/巩膜/结膜 portal 取材范围不含该层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::MG | MG | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=Müller 胶质（v4.1 基因锚 RLBP1/GLUL/SOX9/S100B；冻结 crosswalk 别名注=Müller glia 视网膜特有）：视网膜专属巨胶质，眼表面组织无 Müller 细胞 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::Astro | Astro | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=星形胶质（v4.1 基因锚 GFAP/AQP4/SLC1A3；冻结 crosswalk 别名注=astrocyte 视网膜/中枢）：视网膜内星形胶质，与眼表面组织学细胞群不同实体；RUN5 实证 Q6::13/22/16 被 MG|Astro 接管即此二类 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::Micro | Micro | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 细胞身份=microglia（v4.1 基因锚 C1QB 等小胶质标志）：CNS 常驻巨噬谱系词条；眼表面髓系信号由 Macrophages/Monocytes 词条承载（其 kept 行为见遮蔽表），本条在眼表面装配中不计入排名 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| retina_v6::RPE | RPE | markers_v6_retina_repair.json | markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json | retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking | 视网膜色素上皮（基因锚 BEST1/RPE65 类/LRAT/RDH5/MITF）：单层色素上皮位于视网膜侧，与角膜/结膜上皮不同胚胎起源（神经外胚层诱导 vs 表面外胚层），组织解剖学上不在眼表面 portal 取材层 | 跨文件重复条目 3 份 (markers_v4.1_clean.json|markers_v5_retina_interneuron.json|markers_v6_retina_repair.json)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份） | 排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据） |
| Melanocyte (KB9 build) | Melanocyte | markers_k9_ocs_increment.json (build) | build only（未注册） | ocular_surface_only → 视网膜材料不计入（R1 镜像；火灾审计格二规则臂实证泄漏 0） | 眼表黑色素细胞词条 marker（TRPM1 等）在视网膜双极/杆体语境有真表达（火灾审计无规则臂实测 2/22 簇泄漏），须适用性隔离 | 单文件条目 | 注册后禁全库默认态混用（BUILD_REPORT §4 口径） |
| Schwann (KB9 build) | Schwann | markers_k9_ocs_increment.json (build) | build only（未注册） | ocular_surface_only → 视网膜材料不计入 | MPZ/SCN7A 等在有髓神经相关组织共享；视网膜节细胞轴突段（视神经头）语境存在误入风险 | 单文件条目 | 同上 |
| Conj_epithelium_suprabasal (KB9 build) | Conj_epithelium_suprabasal | markers_k9_ocs_increment.json (build) | build only（未注册） | ocular_surface_only → 视网膜材料不计入 | S100A8/9 髓系共享表达（见 recheck/判件），适用性隔离为前提 | 单文件条目 | 去留待 PI（A15 子项判件 register/SUPRABASAL_RECHECK.md） |
| Limbus_Sclera_fibroblast_C1 (KB9 build) | Limbus_Sclera_fibroblast_C1 | markers_k9_ocs_increment.json (build) | build only（未注册） | ocular_surface_only → 视网膜材料不计入 | DPT/LEPR/LAMA2 为眼表间质域；防泛间质回渗视网膜簇 | 单文件条目 | 同上 |

规则语义从"来源文件 ∈ 三视网膜文件者整批剔除"改为**逐条目 scope 判定**：
- 视网膜神经元 6 类（Rod/Cone/BC/AC/HC/RGC）与 Astro：scope=retina_only 的判定依据=组织解剖取材范围+条目细胞身份（下表 bio_reason 列，基因锚+crosswalk 别名注双证）；规则仅陈述"眼表面装配不计入排名"，**对命中来源不作穷尽断言**（共表达/环境残留为可能成因示例，非判定前提）。
- 身份统一口径（表内外一致，旧合并表述作废）：**MG=Müller 胶质（RLBP1/GLUL/SOX9/S100B）；Astro=星形胶质（GFAP/AQP4/SLC1A3）；Micro=microglia（C1QB）**。眼表面髓系信号由 Macrophages/Monocytes 词条承载（其 kept 行为见遮蔽表），MG/Micro/Astro 不计入眼表面装配不削减该通道；RUN5 实证 Q6::13/22/16 被 MG|Astro 接管=视网膜胶质类型进入眼表簇的跨组织误标。
- RPE：视网膜色素上皮，不在角膜/limbus/巩膜面板；与结膜/角膜上皮不同谱系。
- **REVIEWER_LLM 关切的"视网膜文件中的通用免疫/血管类不必然只适用视网膜"落地**：本表证明三文件内**不存在**被整批排除的通用免疫/血管类——被排除的 10 类逐条均为上列生物学专属类；v5/v6 文件与 v4.1 的 10 类同名重复条目逐条目独立登记、处置一致（整组同退，无保留份，dup_handling 列）。
- 反向条目：4 新条 scope=ocular_surface_only（视网膜材料不计入），依据=火灾审计格二实测（无规则臂泄漏 2/22：TRPM1→视网膜双极/杆体语境、S100A8/9 共现；规则臂泄漏 0）。注册后禁全库默认态混用。

## 4. 证据装配规则 v2 冻结文本（A05 + A12；KB9 实跑 C 臂语义的显式化+新规则）
- **AV2-1（top3 准入）**：屏蔽后 n_shared=0 的类别**不得进入** kb_marker_ranking/top3。实现语义=得分仅对 n>0 构建（k9_query 实测口径，G1 保真 33/33 全等）。
- **AV2-2（候选不足）**：有效候选（n_shared>0）少于 3 时**如实输出不足三席，禁止靠加载顺序补齐**第四/五候选。
- **AV2-3（加载位置冻结）**：本包新条（R-1 四条）加载位置=库序尾部追加（retina→membrane→retina_interneuron→retina_v6→face_v6→**k9**），冻结入注册文本；后续加条一律尾部追加+登记，禁插位。
- **AV2-4（平票规则冻结）**：ranking 按 n_shared 降序；**同分平票按条目插入序（先加载者在前）**，排序稳定性（stable sort）保证确定性复现。此冻结的已知后果须呈报：同分时新条让位于旧条（REVIEWER_LLM"新条持续输给旧条"风险的处置=显式冻结该行为，而非隐式加载序漂移；若 PI 欲改平票语义——如同分并列输出或转弃权——属规则变更，须新版本注册，不在本包生效范围）。
- **AV2-5（保真门三态与历史 ON 对账义务，A12 重写）**：(a) OFF 历史态门——RUN5 冻结证据面 ranking 复刻，KB9 实测 G0=33/33；该门对账对象=RUN5 存档票的**输入面**（存档票=对该冻结面投票）。
- (b) 现役 ON 态门——自实现 matcher 对**当前**生产 query_marker 逐簇全等，KB9 实测 G1=33/33；仅证明装配复刻当前生产语义。
- (c) **历史 ON 态门（本包未完成，登记为下游强制项）**——"与 RUN5 存档票对应的 ON 状态"须把复用票时刻的库版本、装配参数、ranking 与 RUN5 run 当时的完整请求/存档快照逐字段对账；KB9 无 RUN5 时刻完整请求留档，且库态此后已变（Q6::21/29 回退=KB7 条激活之库态变化实证，out/kb9_attribution.json 对照臂），**G1 不得写成历史 ON 保真已证**；任何复用存档票的后续 run 须先建此门（含批组成快照）。
- 屏蔽表生产纪律不变：逐类逐基因机械计算（禁手工挑基因），冻结件 author_class_markers_data.tsv 口径（KB 无关，同 h5ad HVG4000 mean-diff top60）；"任一其他类 top60"的删除条件与"不进入其他类 top60 不证明特异"的不对称性登记为本包残留限制（REVIEWER_LLM §2），下一波 A07 诊断表逐条呈现实证面。

## 5. Keratocytes→评价词表映射冻结声明（A09）
- 冻结映射：**Keratocytes（含 face_v6::Keratocytes 消歧名）→ 九类评价词表之 Fibroblasts**（crosswalk 行 matched_leaf=keratocyte∈Fibroblasts，provenance=alias；KB9_CROSSWALK_ext.tsv 先于投票落盘，既有名称映射零改动）。
- 由此定义的"其它 truth 类"（R3 屏蔽判据）=折叠域之外的 8 类。**该冻结的直接推论与实跑一致**：KERA 在 Fibroblasts top60 属同折叠域，**不构成屏蔽依据**——C 臂实测 KERA/NNMT 眼表面保留、ALDH3A1 屏蔽（其对侧 top60 命中于 Epithelium 折叠域），BUILD_REPORT §2 同口径。"KERA 必被屏蔽"的旧预期在本包正式作废（REVIEWER_LLM §3 指出的定义缺口由此关闭）。
- 折叠≠生物学等同登记：九大类聚合 marker 不充分解决角膜/巩膜纤维细分与上皮分层关系；评价词表合并关系与生物学亚型关系在词条 scope（§3 表）分开记录。
- **全候选类别映射快照（A09 完整化，运行时解析序=frozen crosswalk 优先→k4 内置扩展仅在其为空时生效；38 候选全列，未映射/多重映射处置显式）**：

| kb_candidate | fold_9class | provenance | carrier_runtime |
|---|---|---|---|
| APC_MHCII_high | Immune Cells | alias | frozen(t_d1ca11b0) |
| Astro | (空=不参与R3屏蔽) | no_counterpart | frozen(t_d1ca11b0) |
| Conj_epithelium_basal | Epithelium | KB9_ext | k4_ext(运行时生效) |
| Conj_epithelium_superficial | Epithelium | KB9_ext | k4_ext(运行时生效) |
| Conj_epithelium_suprabasal | Epithelium | KB9_new:CL:1000432 借父条+layer | k4_ext(运行时生效) |
| Corneal Endothelium | Corneal Endothelium | KB9_ext:名=truth 名 | k4_ext(运行时生效) |
| Endo | Endothelium | KB9_ext:KB 缩写=endothelial cell=super_map 叶 | k4_ext(运行时生效) |
| Endo_Patho | Endothelium | KB9_ext:血管内皮病理态 | k4_ext(运行时生效) |
| Fibroblast | Fibroblasts | alias | frozen(t_d1ca11b0) |
| Granulocyte | Immune Cells | KB9_ext | k4_ext(运行时生效) |
| Keratocytes | Fibroblasts | alias | frozen(t_d1ca11b0) |
| Limbus_Sclera_fibroblast_C1 | Fibroblasts | KB9_new:CL:0000057 | k4_ext(运行时生效) |
| MG | (空=不参与R3屏蔽) | no_counterpart | frozen(t_d1ca11b0) |
| Mac_DAM_LAM | Immune Cells | alias | frozen(t_d1ca11b0) |
| Mac_Tissue | Immune Cells | KB9_ext:组织巨噬 | k4_ext(运行时生效) |
| Mast | Immune Cells | x | k4_ext(运行时生效) |
| Melanocyte | Melanocytes | KB9_new:CL:0000148 | k4_ext(运行时生效) |
| Microglia | Immune Cells | KB9_ext:小胶质=免疫叶 | k4_ext(运行时生效) |
| Mono_Classical | Immune Cells | alias | frozen(t_d1ca11b0) |
| Mono_Nonclassical | Immune Cells | alias | frozen(t_d1ca11b0) |
| Myofibroblast | Fibroblasts|Smooth Muscle Cells | ambiguous | frozen(t_d1ca11b0) |
| Pericyte | Pericytes | alias | frozen(t_d1ca11b0) |
| Proliferating | (空=不参与R3屏蔽) | KB9_ext:状态类不折叠(不参与屏蔽) | k4_ext(显式空) |
| RPE | Epithelium | alias | frozen(t_d1ca11b0) |
| SMC | Smooth Muscle Cells | alias | frozen(t_d1ca11b0) |
| Schwann | Schwann Cells | KB9_new:CL:0002573 | k4_ext(运行时生效) |
| T | Immune Cells | alias | frozen(t_d1ca11b0) |
| cDC1 | Immune Cells | KB9_ext | k4_ext(运行时生效) |
| cDC2 | Immune Cells | KB9_ext | k4_ext(运行时生效) |
| face_v6::Fibroblast | Fibroblasts | KB9_ext | k4_ext(运行时生效) |
| face_v6::Keratocytes | Fibroblasts | KB9_ext:keratocyte 叶∈Fibroblasts | k4_ext(运行时生效) |
| face_v6::Myofibroblast | Fibroblasts|Smooth Muscle Cells | KB9_ext:ambiguous 照原链 | k4_ext(运行时生效) |
| face_v6::Pericyte | Pericytes | KB9_ext | k4_ext(运行时生效) |
| face_v6::SMC | Smooth Muscle Cells | KB9_ext | k4_ext(运行时生效) |
| pDC | Immune Cells | alias | frozen(t_d1ca11b0) |
| B | (空=不参与R3屏蔽) | UNMAPPED:不参与屏蔽(如实登记) | runtime_unmapped |
| NK | (空=不参与R3屏蔽) | UNMAPPED:不参与屏蔽(如实登记) | runtime_unmapped |
| Plasma | (空=不参与R3屏蔽) | UNMAPPED:不参与屏蔽(如实登记) | runtime_unmapped |

  处置规则：`ambiguous`（如 Myofibroblast→Fibroblasts|Smooth Muscle Cells）照原链双折叠不猜；`no_counterpart` 类**运行时判空=不参与 R3 屏蔽**（MG/Astro/Rod 等视网膜类实际由 R1 scope 表整条退出装配，空折叠对其无作用面）；`Proliferating`=状态类显式不折叠；`UNMAPPED`（B/NK/Plasma）=运行时如实登记不参与屏蔽（v2.0 缺口：此三行此前未展示）。各候选"其它 truth 类"=九类评价词表 − 该候选折叠集。

## 6. 投票前诊断表输出规格（A07，强制件——注册即约束下游 run）
每 run 投票前生成并冻结落盘（run 目录 `pre_vote_diagnostics.tsv`），列定义：
`cluster_id | entry_id | raw_hit_genes(分号列) | n_raw | shielded_hit_genes | n_shielded | n_remaining(=n_raw−n_shielded) | rank_pre_shield | rank_post_shield | top3_flag_post | immune_support_flag(该簇免疫候选在屏蔽后是否仍有 n_remaining>0 及是否进入 top3；指定对照簇=Q6::8/Q6::26 型真免疫簇逐簇单列)`
配套条款：诊断表**只呈现实证面，不参与计分**；票面与诊断表不一致=run 作废；"证据被掏空"型回退（KB9 实证：Q6::26 因 R2 掏空 APC 头部致一席转 coarse→tie）必须在诊断表内可指认。本包不含重跑（执行归下一波，随 PI 批注册一并裁定范围）。

## 7. 可达性算术模板（A16，注册进下一波预注册必写条款）
- 记 G=原错→修复正确簇数，L=原对→新增回退簇数，基线 P1₀：则 **P1' = P1₀ + G − L**，达标要求 G−L ≥ (球门−P1₀)。KB9 实况演算：P1₀=21（RUN5），G=4（Q6::2/13/15/22），L=3（Q6::26 + 2 例库态激活回退 Q6::21/29），P1'=21+4−3=22 <24——FAIL 与算术自洽，如实报。
- 下一波预注册须**逐簇分列 RUN5 各簇 P1 态与 P2 态两列，禁混算**（KB7 预期代价表"残余十簇混算 P1/P2"含不可达上限风险：若十簇全为 P1 miss 且预期保留，上限 23/33<24；若其中 Q6::24 仅 P2 违规，则上限恰 24/33 且要求其余零回退）。
- "至少净修复三个"是**目标非预测**；无逐簇候选替代关系不得给翻转概率排序。P2 无余量：既有一例违规保留时，其余簇必须零新增 strict 违规；"属预期"不构成 >1/33 豁免。

## 8. 措辞修订清单（A15 措辞部分 + A17 + A18 + A19；同文落地于 KB9_BUILD_REPORT.md 文末 EDITORIAL_NOTE）
1. **"换判据域"表述自注册文本作废**（A15）：本包不使用该措辞；PREREG §1.1 原文因冻结纪律不回改。其"仅在换判据域或补外部证据时才允许成条"条款的现时解释收窄为：**所报三 core 基因统计值满足判件列示的 §1.2 数值门槛，且既有输出可复现；实现完整符合冻结判据及逐基因文献支持关系不由该复算代签**（判件 v2.1 判语 1）。R2/R3 屏蔽（排名计分层）不构成准入变更通道（REVIEWER_LLM §5）；条之去留归 PI。
2. **pericyte/SMC**（A17）：改"在当前数据、特征选择、证据装配与判读协议下**未能稳定区分**"；禁"生物学不可分"表述（共享 marker 与既有失败不能证明生物学不可分）。Q6::24 位保留为 miss 归因于上述限定口径。
3. **弃权/tie 七位**（A17 后半）：登记为**待检验的失败机制假设**（协议性保守弃权归因），新增证据可能改变弃权行为，投票后不得仅凭仍 miss 自动确认旧归因。
4. **混合面审计正名**（A18）：性质=**适用性规则实现验证 + 回归检查**，非新条独立组织特异性证明（规则本身禁止进入故视网膜簇新条零进入=实现验证）；补查项 Arm1/Arm2 于 22 视网膜簇**完整 ranking 一致性**（排序/去重/加载序副作用）登记为下一波强制输出，本包未跑。
5. **OLS 通道降格如实表述**（A19）：OLS 回证=**词条级命名/CL 身份证据**，非逐基因 marker 证据；OLS/PMID/data_driven 三通道**不构成三个独立支持来源**（逐基因支持=文献实际表达关系 + 数据统计，二者与 D002 同源面按 §0 限定）。KB9 的 OLS 红线拦截实证（假号 CL:0000134/0000049 被回函拒）保留为命名卫生证据，不外推。
6. **本次注册条款补全（A19 三缺口）**：①每词条最少合格核心基因数 **MINCORE=3**（自本次注册生效；事实注：KB9 实跑四新条 core 数=10/4/3/3，均不低于 3，但此非当时预注册门槛），不足=不成条并诚实登记阴性；②§1.2"其余 9 互斥组"对应分组=G 层十互斥组（Keratocytes/Fibroblast-stroma/Pericytes/Epithelium/Endothelium/Immune/Melanocytes/Schwann/SMC/CornealEndo）中**排除该条父组后的 9 组**（KB9 k1 实跑枚举=此集合）；③低于 MINPOOL=500 免否决比较对象**逐词条对应登记**（载体 register/A19_MINPOOL_EXEMPT_BY_ENTRY.tsv；小池对象父组归属由 agg 供体对齐实算：B Cells→Fibroblast-stroma、Monocytes→Epithelium、Corneal_Endo→Keratocytes，各词条适用域不同，非全局一概清单）：

| entry_id | parent_group | comparator | level | pool | applies_to_entry | exempt_link |
|---|---|---|---|---|---|---|
| Melanocyte | Melanocytes | CornealEndo | group | 432 | 适用（在本条火灾域 9 组内） | lfc 否决与 cons 参考均不纳入；fire_audit small-record 行留痕 |
| Melanocyte | Melanocytes | B Cells | author_sibling(全局小池) | 212 | 不适用（其父组归属=Fibroblast-stroma≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Melanocyte | Melanocytes | Monocytes | author_sibling(全局小池) | 253 | 不适用（其父组归属=Epithelium≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Melanocyte | Melanocytes | Corneal_Endo | author_sibling(全局小池) | 432 | 不适用（其父组归属=Keratocytes≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Melanocyte | Melanocytes | (组级：火灾域 9 组中 8 组 pool≥500 实际参与否决) | group(active) | -1 | 适用 | 对照行：证明比较域实际执行 |
| Schwann | Schwann | CornealEndo | group | 432 | 适用（在本条火灾域 9 组内） | lfc 否决与 cons 参考均不纳入；fire_audit small-record 行留痕 |
| Schwann | Schwann | B Cells | author_sibling(全局小池) | 212 | 不适用（其父组归属=Fibroblast-stroma≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Schwann | Schwann | Monocytes | author_sibling(全局小池) | 253 | 不适用（其父组归属=Epithelium≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Schwann | Schwann | Corneal_Endo | author_sibling(全局小池) | 432 | 不适用（其父组归属=Keratocytes≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Schwann | Schwann | (组级：火灾域 9 组中 8 组 pool≥500 实际参与否决) | group(active) | -1 | 适用 | 对照行：证明比较域实际执行 |
| Conj_epithelium_suprabasal | Epithelium | CornealEndo | group | 432 | 适用（在本条火灾域 9 组内） | lfc 否决与 cons 参考均不纳入；fire_audit small-record 行留痕 |
| Conj_epithelium_suprabasal | Epithelium | Monocytes | author_sibling | 253 | 适用（同父兄弟域内） | 记录不否决（lfc 与 cons 均不纳入） |
| Conj_epithelium_suprabasal | Epithelium | B Cells | author_sibling(全局小池) | 212 | 不适用（其父组归属=Fibroblast-stroma≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Conj_epithelium_suprabasal | Epithelium | Corneal_Endo | author_sibling(全局小池) | 432 | 不适用（其父组归属=Keratocytes≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Conj_epithelium_suprabasal | Epithelium | (组级：火灾域 9 组中 8 组 pool≥500 实际参与否决) | group(active) | -1 | 适用 | 对照行：证明比较域实际执行 |
| Limbus_Sclera_fibroblast_C1 | Fibroblast-stroma | CornealEndo | group | 432 | 适用（在本条火灾域 9 组内） | lfc 否决与 cons 参考均不纳入；fire_audit small-record 行留痕 |
| Limbus_Sclera_fibroblast_C1 | Fibroblast-stroma | B Cells | author_sibling | 212 | 适用（同父兄弟域内） | 记录不否决（lfc 与 cons 均不纳入） |
| Limbus_Sclera_fibroblast_C1 | Fibroblast-stroma | Monocytes | author_sibling(全局小池) | 253 | 不适用（其父组归属=Epithelium≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Limbus_Sclera_fibroblast_C1 | Fibroblast-stroma | Corneal_Endo | author_sibling(全局小池) | 432 | 不适用（其父组归属=Keratocytes≠本条父组，本不在本条比较域） | 不计作已实施比较后的豁免 |
| Limbus_Sclera_fibroblast_C1 | Fibroblast-stroma | (组级：火灾域 9 组中 8 组 pool≥500 实际参与否决) | group(active) | -1 | 适用 | 对照行：证明比较域实际执行 |

TOPN=12 仅为进入上限。**强制话术：低于 MINPOOL 或因其他资格条件未进入否决计算的比较对象，均须逐项登记，不得计作特异性检验通过。MINCORE=3 是本次注册明确的条款，自本次注册生效；不得将其追认为原 KB9 build 前已经冻结的预注册门槛，既有结果不据此改判。**

## 9. 组批语义与字段依赖检查（A13）
- **组批事实**：判读 runner 为 5 簇/请求共享单 prompt（k6_annotator.py，RUN5 同参）。KB9 实跑=25 变化簇按 5/批重组（批组成≠RUN5 33 簇原批），8 不变簇复用 RUN5 存档票——**混合票集=缓存式系统的一次验收输出**；跨时点/跨后端环境/批上下文差异使该集**不构成全量当期复测，亦不足以将增益独立归因于词条本体**（A11 表述限定，落 EDITORIAL_NOTE）。
- **缓存等同性冻结规则（强制话术全文）**：输入是否不变，以模型实际接收的完整请求为单位判断，包括全部消息、共享批内各簇内容及顺序、实际文献片段与顺序。单簇字段不变不等于完整请求不变；完整请求发生变化时，不得将旧票描述为对应新请求的判读结果。混合缓存票可以按已披露边界报告，但不因此成为当期全量复测或同时段配对结果。按此规则，KB9 的 8 复用簇票一律标注为**缓存混合结果**（其输入面=RUN5 冻结面，本包仅在 (a) 门对账意义上使用之）。
- **gene_hits 依赖检查**：本面实跑结果=33/33 行 gene_hits 全空（无旁路通道），故"原样搬运"在本面为无害；**条款（下一波起强制）**：任何字段原样搬运前须过依赖检查——gene_hits 不得含被排名排除条目的类别/基因旁路信息；tissue_composition_ref 属 **author 标签派生**（9 类占比），KB9 判读 prompt 仅渲染 top_genes/kb_gene_hits/kb_celltype_ranking/lit 四字段（k6_annotator.py build_prompt 实证，tc_ref 未入判读输入），该事实登记入本包。**tissue_composition_ref 含作者标签派生的类别占比，属于可能直接提供类别答案的信息。本次申请不授权将其加入判读请求；D10 对标签派生适用性及屏蔽规则的许可，不自动扩展至该字段，开发集限定声明不能替代新增输入的单独裁定。**
- **lit 重建与同源排除（可审核规则，A13 补）**：变化簇 lit 按 kb2_mcp_v2 同参 top_k=4 重建并整体入面文件冻结（build/face_q6_k9/），实际返回文献/片段/顺序可复核。排除对象=**直接陈述本评价 33 簇（D002 author 标注）类属归属的文献及其片段**（含 Q6 truth 来源标注论文及其补充表）；判定标准=片段文本是否含"簇/细胞群→作者标签"指派关系（标题级初筛+片段级复核两级）；记录义务=每次 lit 重建落盘筛查记录（命中列表/判定/剔除动作）至 run 目录。**本轮 KB9 实跑状态如实登记：检索按类别术语构造、结果随面冻结，但未落逐条同源排除筛查留档——列为下游 run 强制义务，本包不声称已完成。**
- **crosswalk 投票前冻结**：扩展表先于投票落盘（§1 时间线），既有名称映射未改动；若后续修改旧名映射，RUN5 基线须按相同映射重核算（本包未触发）。

## 10. 残留限制节（注册文件必携带，随 §0 声明同页）
1. 开发集同源（§2 实算）：规则、词条、评测同一 D002 study/donor 宇宙，P1/P2=工程验收非独立验证；案 A 无独立票面证据。
2. R2/R3 屏蔽为**非对称删除规则**：top60 共现提示跨谱系/状态/环境 RNA 效应，非判别价值否定；"不进入其他类 top60"不证明特异（REVIEWER_LLM §2），真免疫证据保留依赖 A07 诊断表实证而非规则保证。
3. 混合票集统计边界（§9/A11）。
4. 屏蔽副作用：kb 空率 27%→39%（BUILD_REPORT P3 行原样，如实报）。
5. **suprabasal 生物学限制（强制话术）**：S100A8/S100A9 的髓系及炎性共享表达、参考池 96.9% 细胞来自 chen_limbus、供体一致性仅在可算域内成立，均是条目去留需考虑的证据限制。通过当前统计门槛不等于已证明结膜 suprabasal 特异性；本轮未观察到免疫簇被该条接管，也不构成机制保证。当前可确认的范围为：所报三基因统计值未触发已列 §1.2 数值否决门槛（详见 SUPRABASAL_RECHECK.md）。
6. **本轮未完成义务总表（强制话术 8）**：本轮未完成 22 个视网膜簇 Arm1/Arm2 的完整 ranking 一致性补查，亦未以新注册的投票前诊断表完成下游 run 验收，且历史 ON 态门（AV2-5(c)）与逐条同源排除筛查记录（§9）未落。注册条款的确立不等于这些检查已经通过，适用性规则造成的新条零进入也不证明 marker 具有独立组织特异性。
7. A19 三缺口已在 §8-6 补全；其余未闭合缺口=待 PI 项（§11）。

## 11. 未执行—归 PI 节（A04/A08/A10/A14/A15 子项；禁夹带，本包零执行）
| # | 事项 | 背景一句话 | 选项 | 建议 |
|---|---|---|---|---|
| A04 | 独立眼表验证线 | 外部眼表参考数据定规则→在未参与开发的 study/donor 上冻结评价 | 立项（或含 >1GB 下载，走下载审批铁律另行批准）/ 不立 | 若批注册，先以小体量外部集起步 |
| A08 | Q6::8/26 共识保持列独立验收条件 | 球门增项（不能只看总体 P1） | 下一波加门 / 不加 | 加——与 A07 诊断表天然配套 |
| A10 | 谱系支持 marker 旁挂表替代设计 | REVIEWER_LLM 自明为**非等价替代设计**，表源须外部证据禁 Q6 truth 反推 | 采纳改路线 / 维持现规则 | 维持现规则注册，旁挂表留作研究选项（PI 09-27 D12 已裁"不采"，本行仅登记） |
| A14 | Arm1/Arm2 同时段配对重投（藏臂+固定组批） | 资源/API 成本决策，与 A08 同包 | 全量配对重投 / 至少变化簇双臂同投 / 不重投 | 与 A08 一并入下一波预算裁定 |
| A15 子项 | suprabasal 条去留 | 判件 v2.1 已出：三 core 统计值满足 §1.2 数值门槛且输出可复现、实现合规与文献通道不由复算代签（判语 1 收窄版）；KB7"0 全过"不能作为正确执行判据后的否定结论（判语 2 收窄版，含反事实逐目标归因）+ 髓系共享口径披露 | 保留注册 / 降"待验证候选"不入本轮 / 撤条 | 归 PI；本包 R-1 含该条=按 BUILD_REPORT 原申请状态，PI 若选降级/撤条则 R-1/案 B 组成随之缩 |
| A02 | ~~待 PI~~ | **已落定**：D10 按建议措辞关闭（引文见 §0），本表列此行仅为对账 RECHECK_ACTIONS 原 5 项待 PI 清单 | — | — |

## 12. 包组成与台账
register/ 文件：REGISTER_PACKAGE_v2.md（本件 v2.1）/ A03_OVERLAP_REGISTRY.tsv / A06_R1_ITEM_SCOPE_TABLE.tsv / A09_VOCAB_MAPPING_SNAPSHOT.tsv / A19_MINPOOL_EXEMPT_REGISTRY.tsv / A19_MINPOOL_EXEMPT_BY_ENTRY.tsv / SUPRABASAL_RECHECK.md（v2，含反事实复算）/ SUPRABASAL_RECHECK_EVIDENCE.txt / recheck_kb7_cf/*（反事实件输出） / REGISTER_SHA_MANIFEST.txt（输入只读 sha 台账+新产物 sha）/ scripts/{a03_overlap_calc.py, a06_scope_table.py, sb12_recheck.py, kb7_w2_sandbox.py} / recheck_run/out/*（§1.2 复算件，逐字节=落盘件）/ recheck_kb7/out/*（KB7 原样重放件，逐字节=KB7 发布件）/ round2/（REVIEWER_LLM 二审送审件+回稿登记）。
build/ 与 out/ 与 kb/ 全部只读未触碰（对账见 REGISTER_SHA_MANIFEST.txt）；KB9_BUILD_REPORT.md 仅文末追加 EDITORIAL_NOTE（数字与裁决零改动，追加前后 sha 入账）。
