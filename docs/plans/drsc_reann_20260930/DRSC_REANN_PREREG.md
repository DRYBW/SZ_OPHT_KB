# DRSC_REANN_PREREG — drsc 现栈重注一致性测试 预注册（判据先于执行冻结；落笔 2026-09-30，卡 t_3dd4caaf）

## 0. 定性与红线（写死，先于一切）
- 旧参考 = redo_v2 anno_v2 签字件（自家共识 + 人工签字，2026-09-28 SIGNOFF），**非作者级外部真值**。
- 本测 = **一致性/漂移回归**（现役栈对旧好结果是否稳健），**不是正确率评测**。
- 产物措辞只准：一致率 / 翻转清单 / 漂移 / 归因。禁用：准确率 / 验证为真 / 质量证明。
- 分歧簇 = 送 PI 复核候选清单，不自动判任一方错。
- 本 PREREG 与 out/cluster_roster.tsv = 协调者侧件，含真值列，**不进判读员可见面**。

## 1. 冻结输入（sha256 见 out/inputs.sha256，起跑前锚定）
| 件 | 路径 | sha256[:16] |
|---|---|---|
| 数据（backed 只读） | /mnt/D/DR_GEO/dr-sc/redo_v2/data/main_annotated.h5ad (267,192×36,601; X=CP10K log1p; var_names=symbol 全唯一) | a9d47f24614d0d69 |
| 签字件 | SIGNOFF_labels_20260928.md | 01f0f06e39bc5aea |
| 旧共识表 | tables/annotation_three_source_consensus.csv | 30f6cb57dd2fe000 |
| 现役服务 | /mnt/D/EyeKB/mcp_server/server.py (0.7-k9act, 默认面含 k9_ocs) | 805e78578bfb80b6 |
| 引擎 | /mnt/D/OcularKB/models/v2_prod/v2_prod_model.pkl (dict: scaler/lr/hvg_idx/common_genes=21932/classes=10) | d38af373462dc0bf |
| 判读指令冻结件 | evalset/annotation/ANNOT_INSTRUCTIONS.md（仅复用其规则段，词表段按 §4 适配，适配件=scripts/ANNOT_INSTRUCTIONS_drsc_reann.md） | 3318177471f254ef |
对账断言（Phase-0 已跑，scripts/p0_roster.py）：leiden 32 簇全覆盖；anno_v2 众数 vs consensus final_label **32/32 零不一致**；总细胞 267,192 ✓。

## 2. 旧分级冻结集（SIGNOFF + REGRADE_VERIFY_REPORT §4/§7，见 out/cluster_roster.tsv old_grade 列）
- **high = 29 簇**：majority-3-A+B+C 21 簇 {0,1,2,3,4,5,6,8,9,10,11,13,14,16,17,18,20,22,23,27,29} ∪ SIGNOFF 升 high 8 簇 {12,15,19,21,24,25,26,28}。
- provisional = {7}；dissent = {30}；marker-only = {31}。

## 3. 预期分歧豁免组（先行登记，不计"意外漂移"头条；任务书点名 + 同口径机械扩展）
- E-a：簇 **7**（provisional MG/Astro 骑墙，引用限定"胶质谱系混合候选"）。
- E-b：簇 **31**（Endo——HRCA/引擎均无内皮类的参考缺类伪影在案，SIGNOFF 引用注意①）。
- E-c：Rod 质量轴簇 = 任务书点名 {4,8,11} ∪ 同口径扩展 {0,6}（quality_axis ∈ {Rod-quality(high-mito), Rod-quality(low-MALAT1)} 的全部簇；REGRADE §6 报告同态"Rod 质量轴簇投票发散=降解预期"）。冻结集 = **{0,4,6,8,11}**。
- E-d：**RPE 相关**——任一侧具名 RPE 而另一侧非 RPE 的分歧整对豁免（旧体系 v2 无 RPE 簇；HRCA 面板仅 863 RPE 细胞，RPE 结论本体系不可给，SIGNOFF 引用注意④）。
- 特判（非豁免组，机械必要性）：簇 **30** final=dissent 无固定真名 → **不入 strict/谱系一致率分母**（无可对照参考标签），单列送复核清单。dissent 定性不变（SIGNOFF 引用注意②），kNN 92.9% AC 仅记录。
- 头条一致率分母 = 32 − {豁免组 ∪ {30}} 中"该侧有有效共识名"的簇；豁免组与无共识簇全部单列并报。

## 4. 词表 crosswalk（冻结；D11 硬条款——票面名过本 crosswalk 归一）
### 4.1 参考词表（anno_v2/SIGNOFF 用词）
Rod, Cone, BC, AC, HC, RGC, MG(=Müller glia), Astro, Micro(=小胶质), Endo；dissent（非细胞类型，不参与名比对）。
### 4.2 引擎 10 类 ↔ 参考（classes_ 实测 AC/Astro/BC/Cone/HC/MG/Micro/RGC/RPE/Rod）
**10/10 同名直映**（MG= Müller 双侧同义，RENAME_H 先例）；引擎无 Endo/Pericyte → 簇 31 引擎错配属 E-b 豁免。
### 4.3 判读席词表（本任务适配面，dr-sc=成人人类视网膜）
允许具名 = 参考 10 词 {Rod,Cone,BC,AC,HC,RGC,MG,Astro,Micro,Endo} + {RPE, Pericyte}（库内合法词，命中即单列；RPE 冲突走 E-d，Pericyte 走 §4.5 谱系"vascular"）；或 `coarse:<上述词>`；或 `undetermined`。
票面归一（机械，先于计票）：大小写/空格规范化；同义映射 {Microglia→Micro, Müller glia/Müller glial→MG, Astrocyte→Astro, endothelial/vascular endothelial→Endo, amacrine cell→AC, bipolar cell→BC, horizontal cell→HC, retinal ganglion cell→RGC, pericyte→Pericyte}；盘外残余名 = off_vocab 旗单列（不自动判错，进 §7 归因的"词表"桶）。
### 4.4 谱系级（coarse-grained）分层映射（冻结）
photoreceptor={Rod,Cone}；interneuron={BC,AC,HC}；macroglia={MG,Astro}；microglia={Micro}；projection={RGC}；RPE={RPE}；vascular={Endo,Pericyte}；undetermined/无共识=**无谱系**（任一侧无谱系 → 谱系口径记"不可比"，非 match 非 mismatch，簇级单列）。
### 4.5 "方向性认错大类" 定义（FAIL 档计数单位）
两侧均具名（strict 可判）且 strict 不一致 **且** 谱系层不一致。谱系一致仅细名不一致（如 Rod↔Cone、MG↔Astro）= 粒度墙桶，不算认错大类。

## 5. 执行链冻结
### 5.1 digest 证据面（scripts/digest_drsc.py）
- 分群=obs.leiden 冻结 32 簇，**禁重新聚类**；证据面构造物理剔除 anno_v2/anno_v2_flag/quality_axis/p1/tau/leiden_base/leiden_r05 列（只读 leiden/sample/group/donor/n_genes/pct_mito/pct_malat1）。
- top genes：`sc.tl.rank_genes_groups(a,'leiden',method='wilcoxon',reference='rest',n_genes=30)` on X=CP10K log1p 全 36,601 基因（现行口径 = pipeline/stage_a_processing.py:305；n_genes=30 取任务书"top30"）。
- top_genes 双列 schema：var 本体=symbol → top_genes=原 ID 列、top_genes_sym=同值旁列（ENSG 解码不适用，如实记录"无 ENSG 需解码"，RUN2 教训条款核查通过）。
- 五字段（stage_b_evidence.py 逻辑逐字沿用，输入换本冻结面）：①query_marker(top10 symbol)；②基线组成对照 get_tissue_composition(species=human,tissue=retina) 簇级 fraction vs donor 区间；③疾病先验 = group 列三组比例 {nonDM=NC, DM, DR} + get_disease_prior(disease='DR',tissue='retina')（实测命中 PDR__fibrovascular_membrane 条目；nonDM/DM 库内无条目不查，如实登记）；④lit = top-3 候选 search_literature（物种 human 组织 retina top_k=4）；⑤confidence = stage_b grade_cluster 机械三值分级（非结论）。
- **双态臂**：ON 臂 = 默认环境（EYEKB_ACT_K9 未设=现役含 k9）；OFF 臂 = 采集进程 env EYEKB_ACT_K9=0（eyekb_core 每调用读取）。两臂除服务端 k9 面外**其余逐字同参**；MCP 调用留痕 mcp_calls_{on,off}.jsonl。
- SLIM 判读面（scripts/slim_drsc.py，kb2_slim 逻辑）：cluster_id=drsc::<k>、member=drsc、material={species:human,tissue:retina,material:"成人视网膜 DR 队列(snRNA)，分组 nonDM/DM/DR",dev:adult}、n_cells、qc=簇中位 {n_genes,pct_mito,pct_malat1}、top_genes(20)/sym、kb_marker_ranking(5)、gene_hits(8)、tissue_composition_ref、disease_prior 摘要 {group_fractions_pct, DR mentions(≤4)}、lit(每类 2 条 pmid/yr/t)。两臂各出一份 SLIM，**面内零真值列**（结构断言：SLIM 文本不含 anno_v2/豁免组信息/报告内容）。
### 5.2 判读臂 E2（scripts/run_annotator_drsc_reann.py = run4r 逐字复用改路径/前缀）
- 三席跨厂商（run4r 同款）：A=qwen3.8-max、B=glm-5.1、C=deepseek-v3.2（bailian 通道，2026-09-30 三席冒烟全通）。温度 0.2；qwen 系 enable_thinking:false；5 簇/包断点续跑；prompt 模板 run4r 逐字，instr 段=§4.3 适配件；输出前缀 ANN_{A,B,C}_drsc_reann_{on,off}.jsonl，落本领地 out/，禁触历史产物。
- **票规版本声明（D11 硬条款）：v2=C2b**（PROTOCOL_VOTING_v2_C2b.md §1 逐字：定名票任意 grade 计数；coarse:X 计入 X 法定人数；≥2 席同名即定名；平票残余 S1 破平禁用维持无名；undetermined/缺票不入数）。计票实现 = 参考实现 tiep_20260927/scripts/t1_revote.py rule_c2(count_coarse=True) 等价自写件（scoring/score_drsc.py 内实现 + 单测断言）。
- 每簇产出 consensus_name + consensus_basis（票构成：具名/coarse 来源、grade 分布）+ 无共识(弃权/tie/split3) 单列。
- ON/OFF 两臂各自三席各跑一遍（同一席两臂=无状态 API 独立调用，prompt 不含臂标识，无跨读泄漏路径）。
### 5.3 引擎臂 E1（scripts/e1_engine.py，systemd-run MemoryMax=16G）
- 流程：var symbol ∩ common_genes(21932) → 按 hvg_idx 取 2000 列 → scaler.transform → lr.predict/predict_proba 分块(20k 细胞/块)。
- 簇级主判 = 细胞 argmax 众数（平票取平均 proba 高者）；并报平均 proba argmax（若两口径分歧如实双列）。
- 引擎 10 类按 §4.2 直映；Endo 缺类=E-b 豁免注记。
### 5.4 评分（scripts/score_drsc.py → CONSISTENCY_TABLE.tsv + DRSC_REANN_DISAGREE_attrib.tsv）
- 三方逐簇对照：anno_v2(final, 签字后分级) × E2-ON consensus × E2-OFF consensus × E1。
- **头条一致率**：E2-ON vs anno_v2，strict 与谱系两口径同时给，判读按取严（strict 为主）。弃权/无共识单列（合法，不计错，出分母）。
- **激活位移**：E2-ON vs E2-OFF 逐簇共识名差集 + 两臂各自一致率之差。
- 归因四桶（对每个 strict 不一致簇，顺序判定）：①词表/面版本位移（ON≠OFF 或 off_vocab 名上位或 E-d RPE 对）②粒度墙（谱系一致细名不一致）③判读方差（三席票 split/coarse 混、basis 弱）④意外漂移（豁免组外、old high、谱系认错大类）——仅④需向 PI 解释。
- E1 vs 旧参考一致率作三方对照报（同样双口径），不参与 FAIL 判格主判。

## 6. 判读矩阵（预注册四格，任务书逐字）
1. 一致率高（≥80% strict，除豁免组）且意外漂移=0 → 现役系统对旧好结果稳健，"内容多了质量降"疑虑在本参照上否定。
2. 一致率中等且漂移集中在预期版本敏感组（黑素/眼表类新词上位、免疫细分位移）→ 归因成立，列逐簇清单报 PI。
3. 意外漂移 ≥3 簇（旧 high、非豁免组、方向性认错大类）→ 质量回归 FAIL 档，冻结新增内容波次，出逐簇取证报告。
4. 判读臂跑不满/污染（泄盲）→ 如实 block，不硬考。

## 7. 纪律（任务书承接 + 领地细化）
- 唯一可写=/mnt/D/EyeKB/plans/drsc_reann_test_20260930/{out,scripts,logs}；**禁写** /mnt/D/DR_GEO/**、kb/、mcp_server/、evalset/**、plans/其他目录；冻结件不回改。
- 判读员禁见：anno_v2 列、digest 构造脚本真值分支、旧 REPORT/REGRADE/SIGNOFF、对方席判读件、本 PREREG。协调者验收只查结构不读票面内容。
- copy 不 move；禁下载；禁外部检索（本地 MCP/库检索合法）；重计算 systemd-run MemoryMax=16G；产物 sha 台账 MANIFEST；心跳带 available；完成或遇阻必须落卡。
- 报告头条数字必须 strict/谱系两口径同时给（取严）。

—— PREREG 完，本文件 sha 落纸（DRSC_REANN_PREREG.md.sha256）后方可起跑 §5。
