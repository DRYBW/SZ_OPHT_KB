# KBGOV_PREREG_v1.1 — query_marker 跨物种 ranking 治理候选：证据层机械 A/B 预注册

- 卡：t_ea865be1 ｜ 任务书：BRIEF_KBGOV.md ｜ 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md D14
- 性质：**候选设计 + 离线证据层验证，零实装**。禁改 eyekb_core.py/server.py/kb/（sha 在 ledgers/INPUT_SHA_PRE.txt，POST 复核逐字节全等）。
- 纪律继承（逐字禁再犯）：BTEST §4/§7.2（Q7::52/58 鼠簇 AC 伪影经自由查询回流——判读卡撤行修在渲染层，工具路径不经过）；RUN7RG R2 伤害账（kb_ranking=AC(1) 带偏，FACE_V2 预注册 §5 盲区 4"大写惯例匹配非 1:1 ortholog 无回证"实证兑现）；E3 §1（弃权带回捞具名错行 5×Q7 跨物种簇 Q7::11/15/21/22/61 + 2×弱命中）；RUN7RG §6（Q2::22 误导源在 GLUL/VIM/CLU 共表达基因先验，删词条仍回 MG）；FACEV21 拆弹 3A/Q7/RPE（规则层修复先例，本卡把 (b) Q7 撤行从卡片层下沉库侧）；E2 §4B（567 (库,类,基因) 对定性，人面板对 HRCA 系=自参照件）。
- 复刻纪律（E2R/E3 先例）：实验侧复刻 query_marker genes-mode 排序逻辑，**禁 import 生产码**；复刻件对服务端 calllog 留痕做逐行序对账（G0 门），不过即中止。
- 时序红线：v1.0 sha=33119b7d 落纸先于复刻跑数与 G0；v1.1 为**跑数前输入装配修正**（仅 §1 输入列定义，球门/判据/规则形态零改动，修正理由=ENSG/symbol 双列实证 158/290），v1.1 sha 先于校准冻结与 B 断言。球门落纸后禁再回调。
- v1.0 原件与 sha 保留：KBGOV_PREREG_v1.0.md(.sha256)。

## §1 输入件与判据分母（冻结）

1. **病灶集 L（9 件，canonical 输入复原自冻结票档/面）**：
   - 鼠源 7 簇：Q7::52、Q7::58（输入=run7rg 面 `digest_pool` 全 25 基因，frozen EV_DIGEST_SLIM_run7rg.jsonl）；Q7::11、Q7::15、Q7::21、Q7::22、Q7::61（输入=v3full SLIM `top_genes_sym[:20]`，出处=E3 §1 具名错行 5 簇名单，即 BRIEF 点名件）。
   - 人源 1 簇：Q2::22（输入=v3full SLIM `top_genes_sym[:20]`；G3 靶——MG 经 {GLUL,VIM} 具名顶前）。
   - 登记不判 1 簇：Q5b::35（BTEST lost-4 之一，归因=grade 判序漂移，**归 D16/GRADE 卡管**，本卡不设病灶判据；但其 A→B 排名若变动**计入回归位移账**）。
   - 保真副列（不作主判）：席位原始入参（toolcalls run1_{A,B,C}，含大小写变体与增删基因）在 A 下重放，验证与 calllog 留痕响应等值。
2. **回归集 R**：RUN3 v3full SLIM 290 簇中 **231 个人源簇，剔除 Q2::22 后 = 230 簇** 为"零位移"门分母，逐簇输入=v3full SLIM `top_genes_sym[:20]`（v1.1 修正：top_genes 列 158/290 簇为 ENSG ID 形态，席位所见为双列且其 marker 检索实以 symbol 列为准，canonical 一律取 top_genes_sym；缺失列=0 簇已验证）；鼠源 59 簇（全部 Q7）不入位移门分母（属治理对象），其位移单列"鼠侧账"。truth 连接件=run3_object_B_table_v1.1.tsv（可用处标"正确名伤亡"）。
3. 物种词表（全部本地零网络）：HUMSYM=Homo_sapiens.gene_info.gz Symbol∪Synonyms（大写形态）；MOUSYM=mus_musculus.104.gtf.gz gene_name（大小写双形态）；ORTH11=mouse_model 冻结件 human2mouse_1to1_symbols.json（12,313 对，Ensembl compara 104）。

## §2 复刻件与 G0 验证门（先于一切 A/B）

复刻 = eyekb_core.query_marker(genes-mode) v1.0 语义的实验侧重写：库装载序 retina(v4.1)→membrane→retina_interneuron→retina_v6→face_v6（face_v6/lacrimal 归一派生按生产 `_load_marker_dbs` 原文复刻）；类名 upper 冲突消歧 `库名::类名` 别名（首现保正名）；输入 `strip().upper()`；`n_shared=Σ[命中基因]`；排序=按 -n_shared 的**稳定排序**（同分保 markers 插入序=库装载序）；n=0 类不进。**不含** soft_flags 注记（calllog 证实不改排序，其 flag 单列记录）。
- **G0 门**：对 calls_2026-09-27.jsonl 内全部 `tag=btest_d9 ∧ tool=query_marker ∧ mode=genes` 行（library=all、act_v6_on=true 留痕态），复刻 ranking 类序 vs `resp.ranking_classes_top` 逐行对账，**错行=0 才放行**；同时含 09-26 文件内 library=all 的 genes-mode 行（若 tag 匹配口径不同则如实报窗口）。锚点必核单列：Q7::52 席A 19 基因查询→`[Pericyte, Fibroblast, retina_interneuron::AC, retina_v6::AC]`；Q2::22→`[MG, Astro, retina_interneuron::MG, retina_interneuron::Astro, Fibroblast, retina_v6::Astro]`。
- 注：A 基线 = **现库**（v6 激活态）复刻响应；v3full 面内 kb_marker_ranking 为 09-24 旧库态，只作历史参考列，不作 A 定义。

## §3 治理规则候选（形态先冻结，数值参数由 §4 校准件定，校准先于 B 跑）

**G1 输入物种判定层**（对 genes-mode 入参，逐基因三信号 → 簇级判定）：
- 信号 s1 形态：`title_frac` = 名单中"首字母大写含小写体"MGI 惯例基因的占比；`msp_hits` = 鼠特异命名模式命中数（`^Gm\d+$`、`.*Rik$`）。
- 信号 s2 词表：`m_only` = upper 归一后 ∉HUMSYM ∧ ∈MOUSYM 的基因数（鼠独有符号）；`h_only` = ∉MOUSSYM ∧ ∈HUMSYM。
- 信号 s3 同源：命中面板基因逐一走 ORTH11 回证（人 symbol→鼠 symbol），无回证=不可具名证据（修 FACE_V2 §5 盲区 4）。
- 判定（冻结形态）：`mouse_confirmed` ⇔ title_frac ≥ T ∧ (msp_hits ≥ 1 ∨ m_only ≥ 1)；`mouse_suspected` ⇔ title_frac ≥ T ∧ 无佐证；其余 `human_assumed`。T 由 §4 校准冻结。
- 响应三档（各出示例，进 CANDIDATE 正文）：**V-a 显式 species 标注**（排名不动，响应加 `input_species`+逐条 `cross_species_hit` 证据字段）；**V-b 降级具名**（confirmed 输入：类候选保留具名 ⇔ n_shared ≥ 2 ∧ 全部共享基因 s3 回证通过 ∧ 共享集⊄AMBIG；不合格者移出具名排名入 `unranked_candidates`；suspected 仅 V-a）；**V-c 拒答**（confirmed 输入具名排名清空+指引 `no_named_ranking_for='mouse_input'`；suspected 仅 V-a）。
- 已知限制（如实落纸，不回避）：纯 MGI 大小写惯例、无鼠独有/模式基因的鼠源名单（如 Q7::61）只靠 s1 信号——若 T 之下仍有真人源名单以 title 惯例上送，将被误标/误杀；本数据 231 人源簇 title_frac≤0.05、59 鼠源簇≥0.95，分隔带内无样本，边界外推是本卡不可证事项，实装申请书须携带此限制。

**G2 跨物种 ranking 过滤** = G1 判定为鼠源时的人面板具名条件（V-b/V-c 档；参考 FACEV21 拆弹 (b) 撤行但下沉库侧、条件化而非一刀切）。

**G3 假命中防线（人源侧，只管共表达歧义，不管 grade——grade 归 D16）**：
- AMBIG = 冻结锚集 {GLUL, VIM, CLU}（出处=BTEST §4/RUN7RG §6 点名件；**不用**面板跨类出现率自扩——预演显示出现率无法与 ISL1/GAD1/S100B 等正当共享 marker 分离，自扩=过杀放大器）。
- 触发：类条目 n_shared ≥ 1 ∧ 其共享基因 ⊆ AMBIG → `no_naming_claim` 标记（歧义基因堆数不构成特异性；锚案 Q2::22 MG 经 {GLUL,VIM} n=2 顶前）。BRIEF 字面 n_shared=1 案（Calb1/Grin3a 型）为 ⊆AMBIG 之特例，一并覆盖；但 Calb1/Grin3a 类基因**不入** AMBIG（其病灶在鼠源输入，G1/G2 管辖）。
- Q3::11/Q4::8 型（人源 ONECUT2 单基因入 AC——v4.1 AC 面板内容错位）：**不属 G3 管辖**，属面板内容修复线（KB5-v3 口径），本卡如实登记为"未覆盖病灶"，禁为过病灶而扩 AMBIG。

**B 变体组合（可组合矩阵）**：
- B1=V-a + G3(flag-only，序不变)：非破坏，具名资格标注。
- B2=V-b + G3(removal)：破坏性；B3=V-c + G3(removal)：最严。三档共同底线：凡 confirmed/suspected 鼠源输出条目一律带 species 注记（纵深防御）。

## §4 校准（零 LLM，先于 B 跑，产物冻结）

- T：以 §1 名单标注（59 鼠/231 人）的 title_frac 分布取最大间隙分隔点；校准件 `data/kbgov_g1_calibration.json`（含两侧极值、间隙、选定 T）+ sha；落纸后才跑 B。
- 词表提取件 `data/kbgov_vocab_stats.json`（HUMSYM/MOUSYM/ORTH11 规模与命中样例）+ sha。

## §5 机械断言（A/B 对账表口径）

对每个输入件（病灶集 8 + 回归集 230 + 鼠侧 59）：A=§2 复刻现库 ranking；B_x=规则叠加后 ranking/标注。
1. **病灶清零/物种化（逐簇判词）**：
   - 鼠源 7 簇：A 中凡具名 top 条目（如 AC/HC/BC/Pericyte/Fibroblast）在 B1 下必须带显式 species 注记（=显式物种化达成）；B2/B3 下必须丧失具名资格（移除或降级为 unranked/拒答）=清零。逐簇记 `cleared|species_qualified|NOT`。
   - Q2::22：B1 下 MG 条目 `no_naming_claim=true`；B2/B3 下 MG 移出具名排名。伪影=现库响应中 MG 具名顶前（§2 锚点留痕）。
   - A 基线锚定断言：Q7::52 canonical 池 A 响应 top 必须含 AC 具名条目；Q2::22 A top1=MG——不达即复刻失真，全线中止回查（这是"BTEST §7.2 修复须下沉库侧"的机械复述）。
2. **回归零位移门（逐变体）**：位移定义=人源簇的**具名类序**（entry 类名序列与次序；flag-only 变体设计上序不变则记 0）A vs B 不等；逐条列 `out/kbgov_regression_shift.tsv`（cluster_id、A序、B序、触发规则、truth、是否正确名伤亡）。位移率 >5%（>11/230）→ 该变体判**过杀回炉**；(0,5%]→逐条归因后方可入围；=0 满分。鼠侧 59 位移单列不入门。
3. **正确名伤亡红线**（独立于百分比）：truth 已知且 A top1 正确、B 将其剥夺/改序 = 伤亡；任一变体出现伤亡必须在 CANDIDATE 中显式账目化，禁以"≤5% 容差"掩盖。
4. **过杀账**：位移/伤亡逐条 + 规则归因（G1 误判？G2 条件？G3 连带？）+ 修法建议。

## §6 产出与落点

- `KBGOV_CANDIDATE.md`（规则文本=可原样装进 eyekb_core 的粒度；A/B 对账表；过杀账；实装申请书草案：三段式=①注册（规则件+验证账入 kb/priors 或 plans 注册线）②OFF 态接线（eyekb_core 加分支 env 默认 OFF，pre/post 等价证明路径照抄 t_5d5853c9 激活纪律）③激活另批——全部待 PI，本卡零接线零生产写）。
- 机读件：`data/kbgov_ab_lesion.tsv`、`out/kbgov_regression_shift.tsv`、`out/kbgov_ab_metrics.json`、`ledgers/INPUT_SHA_POST.txt`、`ledgers/kbgov_replica_vs_calllog.tsv`、`logs/`。
- 脚本入 `scripts/`（复刻件、校准件、A/B runner、账目件生成），全部只读输入+本目录写。

## §7 红线自查清单（收尾落卡断言之盘上证据）

零 LLM（全线无席位/模型调用）；零网络（词表/ortholog/GTF 全本地）；零生产写（eyekb_core.py/server.py/kb/ 只读，POST sha 全等）；禁 import 生产码（复刻件独立实现，G0 对账锚 calllog 留痕）；产物只落本目录；完成或遇阻必须落卡。
