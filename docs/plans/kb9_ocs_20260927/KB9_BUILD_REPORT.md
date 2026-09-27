# KB9_BUILD_REPORT — 眼表词条缺口建设（build 隔离版）t_6df5b739

日期：2026-09-27 ｜ 放行：USER_DIRECTIVE_20260927_scoring_wave.md（D3）｜ 预注册：KB9_PREREG.md（sha 47045d9f…，ledgers/KB9_PREREG_SHA.txt，判据先落纸）
领地合规：**零生产写**——kb/、mcp_server/、evalset 冻结卷 31 件 PRE sha 台账复验全 OK（零触碰）；未写 e2r_s5audit/e3_rescue/panel_pmid 三并行卡目录；零大数据下载（仅文献摘要级 API）。**注册、接线、激活一律未做**（§6 注册申请等 PI 批）。

## 1. 新建词条（build/markers_k9_ocs_increment.json，结构对齐 face_v6）
| 词条 | CL id（OLS by_iri 回证 ledgers/ols_evidence_kb9/） | 眼表有效核心基因 | 文献通道（ledgers/PMID_LEDGER.tsv） |
|---|---|---|---|
| Melanocyte | CL:0000148 melanocyte | TRPM1 MLANA TYRP1 PMEL DCT TYR GAPDHS GPR143 SLC24A5 ABCB5（10/10 全绿） | 全 10 条 pmid 级 |
| Schwann | CL:0002573 Schwann cell | MPZ SCN7A SOX2 NRXN1（4） | MPZ/SOX2/NRXN1=pmid；SCN7A=canonical+Q6::17 直证 |
| Conj_epithelium_suprabasal | CL:1000432 借父条+layer_descriptor（KB7 先例） | S100A8 S100A9 KRT4 | S100A8/9=pmid；KRT4=canonical |
| Limbus_Sclera_fibroblast_C1 | CL:0000057 挂父条+subtype | DPT LEPR LAMA2 | pmid（泛纤维语境，非眼科特异，已标注） |

OLS 红线执行实证：候选号 CL:0000134 回函 label=mesenchymal cell、CL:0000049=common myeloid progenitor，**均与凭记忆预期不符被拒**（拒件留痕 ERRATA_*.json），定案号以回函为准——20260924 规范首拦假号条款在 KB9 复现有效。

数据选基全格可审：out/kb9_fire_audit.tsv（Melanocyte/Schwann/Conj_suprabasal/纤维四亚型逐基因×全邻组，KB7-W2 冻结常量未动）。诚实登记：①Limbus/Sclera/C2/Sclera_Fib 三池 donor cons 0 基因全过（纤维细分仅 C1 成立，与 KB7"四细分全零"部分分歧——KB7 断言无盘上件，KB9 以同常量 author 池独立复算，判据未放宽）；②MITF/CDH19/PLP1/MBP/SOX10 等教科书锚数据全绿或不可检但按 TOPN=12 冻结口径不回填（禁择优挑基因）；③文献 weak/context-only 通道弃用清单逐条在 removed_note（8 基因 weak_evidence，照 HC-LITRE 先例）。

## 2. 接管修复候选（applicability 规则，证据装配层，词条基因集本体未改）
- R1 组织适用性：眼表面材料剔除视网膜专属条（MG/Astro/RPE 等——RUN5 实证 Q6::13/22/16 等 6 簇被 MG|Astro 接管）；反向 face-only 条在视网膜材料剔除。
- R2/R3 对称共享基因屏蔽：以冻结件 author_class_markers_data.tsv（KB 无关口径）为据——免疫/间质条基因出现在非本折叠 truth 类 top60 → 眼表面 n_shared 记 0。产出 out/kb9_shared_gene_shield.tsv（逐条 kept/blocked）+ kb9_face_effective_genesets.json。实测要点：CD74/HLA-DRA/HLA-DRB1 被屏（Q6::11 型接管源头）；S100A8/9 被 Mono_Classical 侧屏但 suprabasal 侧保留（该数据集免疫层 top60 由 T/肥大基因主导，数据说话）；mural 链 ACTA2/TAGLN/MYL9/TPM1/TPM2 被屏（Q6::24 型源头）。
- Keratocytes/Q6::20 处置：KERA/NNMT 眼表面保留、ALDH3A1 屏蔽；判读词表折叠建议（Keratocytes→Fibroblasts 域）写入规则文件，**runner 词表未动**（生产侧改动等 PI）。

## 3. 自检 Q6 眼表 33 簇离线复测（球门与 RUN5 完全一致不降）
保真门：①双库态（retina+membrane，即 RUN5 建面配置）复现冻结面 ranking **33/33 逐簇全等**；②自实现 matcher 对 query_marker(ON) 裸配置 33/33 全等。复测面 = 现役生产库 + KB9 新条 + R1/R2/R3（C 臂）；25/33 簇证据变化→三席重投（A=qwen3.8-max B=glm-5.1 C=deepseek-v3.2，LLM_CHANNEL 通道冒烟 3/3 可用，协议照 run_annotator_run5 同参 temp0.2/5批/max_tokens3500），8 簇复用 RUN5 存档票；裁决脚本判据逐字复用 run5_verdict.py，truth 对账断言通过。中途修复披露：首版 C 臂 R1 消歧键 bug 漏放 retina_interneuron::Astro，投票跑 ~3 分钟后发现，SIGTERM 重启（产物作废重跑，首版件未入裁决）。

结果（out/kb9_verdict.json）：
| 线 | 球门 | RUN5 | KB9 C 臂 | 判定 |
|---|---|---|---|---|
| P1 真值命中 | ≥24/33 | 21/33 | **22/33（66.7%）** | **FAIL（差 2）** |
| P2 反污染 | ≤1/33 | 1/33 | **0/33** | PASS（接管清零，任务书"使 Q6::11/Q6::3 型接管不复现"达成） |
| P3 kb 空率 | 观察 | 27% | 39%（屏蔽副作用如实报） | 记录 |

翻转归因（逐簇表 out/kb9_truth_table.tsv）：**+4 命中**：Q6::2（Mono_Classical 接管→结膜分层条 3:0 命中）、Q6::13（MG|Astro 接管清除）、Q6::15、Q6::22（Fibroblast|Myofibroblast 归位）；Q6::11/Q6::3 两型接管面全退场（P2 清零）。**−3 回退**：Q6::26（R2 把 APC 头部掏空后一席转 coarse→tie——屏蔽的免疫簇侧代价）、Q6::21/29（**非 KB9 所致**：其证据变化仅来自现役库态本身（KB7 条激活），对照 kb9_attribution.json 库激活臂）。残余 11 miss 按预注册预期代价表归因：①Q6::24 pericyte/SMC 通签生物学不可分（P2 位保留预期→实测 0 违例优于预期）；②Q6::15/28 折叠域票面摇摆；③Q6::12/16/18/27/30/31 弃权/tie 结构位（协议性保守弃权非词条可修，其中 Q6::30 两席 Epithelium 但 C 席 grade C 被票规则弃——判读协议改进项另卡）。**禁调阈值凑命中：球门原样，如实报 FAIL。**

## 4. 火灾审计（防再造 Q6::24）
格一新条全格：out/kb9_fire_audit.tsv——四新条逐 core 基因×9 互斥邻组+兄弟亚型全绿（否决域）；donor cons 明细 out/kb9_donor_cons.tsv。
格二混合面（33 眼表+22 视网膜抽样，冻结规则=各成员 n_cells top3+Q9 top1）：out/kb9_fire_audit_mixedface.tsv——无规则臂模拟注册即污染面：**k9 条泄漏 2/22 簇（TRPM1→视网膜双极/杆体语境 3 簇 top10、S100A8/9 共现 1 簇）**，坐实 R1 反向适用性的必要性；规则臂（applicability=ocular_surface_only）：**泄漏 0**，眼表面视网膜条违规 0（PASS）。基因级重叠披露：TRPM1/S100A8/S100A9 三基因在视网膜簇 top10 有真表达（非词条错误），靠适用性隔离，注册后禁全库默认态混用。

## 5. 外部评审记录
送审件 out/REVIEWER_LLMrecheck_prompt.txt（R1-R3 屏蔽规则/混合票复用/KB7 分歧处置/可达性四问）发 REVIEWER_LLM 复核——**通道 503×5 连败未获回函**（out/REVIEWER_LLMrecheck_*.txt 留痕）。按任务书"成本超限即上报不自行加钱"未换付费通道；设计决策全部锚定既有冻结件（RUN5 判据/KB7-W2 常量/CL 规范），预注册先行入账，可复核。

## 6. 注册申请（等 PI，本卡未动）
申请注册 build/markers_k9_ocs_increment.json 四新条 + R1/R2/R3 装配规则（mcp 侧以旁挂 library 形式，照 face_v6 先例）。建议分两案：A=仅注 Melanocyte+Schwann（零回退风险，直接修复 Melanocytes/Schwann 两 truth 类结构不可达）；B=全量含屏蔽规则（P2 清零收益+Q6::26 型免疫簇证据变薄代价，P1 净+1 不达门）。激活需另卡+同球门重测通过（face v2.1 eval_only 红线沿用）。

产物索引：scripts/k1-k8（全留档）；out/14 件；ledgers/（SHA_PRE 31 件+OLS 回证+PMID 台账+esummary 34 件+epmc_raw_v2 38 件）；build/（词条 JSON+C 臂面+crosswalk 扩展）。

---

## EDITORIAL_NOTE（2026-09-27，t_62bb0dfe 注册包 v2 配套表述层补记；本节以上原文一字未动，全部数字与裁决零改动）
1. **混合票集定性（A11）**：§3 自检为**缓存式系统验收输出**——25 变化簇重组 5/批重投 + 8 不变簇复用 RUN5 存档票。跨时点票（存档票 vs 新票）混入采样随机性、服务端模型变化与批上下文差异（温度 0.2 同参不保证可重复）；该票面**不构成全量当期 33 簇复测**，§3 翻转归因**不足以将增益独立归因于 KB9 词条本体**（组合效果=词条+装配规则+重建 lit）。
2. **组批语义与字段依赖（A13，解释性局限登记，不重跑）**：RUN5 判读为 5 簇/请求共享单 prompt，KB9 对变化簇子集重组批=未变簇虽沿用存档票、重投簇的批上下文与 RUN5 不同；gene_hits 本面 33/33 全空（原样搬运无害），tissue_composition_ref 属 author 标签派生字段但**未进入判读 prompt**（k6_annotator.py build_prompt 渲染面实证）——依赖检查条款与"lit 重建冻结/同源排除、crosswalk 投票前冻结"见 register/REGISTER_PACKAGE_v2.md §9。
3. **措辞限定（A17/A18）**：§3 残余归因中"Q6::24 pericyte/SMC 通签生物学不可分"读作"**在当前数据、特征选择、证据装配与判读协议下未能稳定区分**"；七个弃权/tie 位读作"待检验的失败机制假设"。§4 混合面审计定性=**适用性规则实现验证+回归检查**（"新条零进入"验证的是规则实现，非新条 marker 的独立组织特异性；Arm1/Arm2 于 22 视网膜簇完整 ranking 一致性补查登记于注册包，未在本报告跑）。§1 OLS 回证=**词条级命名证据**，OLS/PMID/data_driven 三通道不构成三个独立支持来源。§1 Conj_suprabasal 条之依据读作"所报三 core 基因统计值满足判件列示的 §1.2 数值门槛，且既有输出可复现；实现完整符合冻结判据及逐基因文献支持关系不由该复算代签"（原 PREREG §1.1"换判据域"措辞已由 REVIEWER_LLM 判不成立并在注册包作废；判件 v2.1 见 register/SUPRABASAL_RECHECK.md——该条去留归 PI）。
4. **球门不可达算术（A16）**：§3"预期代价表"十簇残余系 P1/P2 混算，存在不可达上限风险；P1'=P1₀+G−L 须逐簇分列 P1/P2 态（模板=register/REGISTER_PACKAGE_v2.md §7）。本报告 22/33 FAIL、0/33 PASS 裁决不因上述任何表述修订改判。
