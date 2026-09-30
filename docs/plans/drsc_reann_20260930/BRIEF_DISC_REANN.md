# BRIEF_DISC_REANN_20260930 —— drsc 现栈重注一致性测试（PI 09-30 点名）

## 背景与定位（一句话）
PI 指定：dr-sc（figshare 28228949，DR 单细胞）redo-v2 注释是"之前注释得很好"的旧参考（2026-09-28 签字 high 定级 29 簇），用**现役全套系统**对它再注释一遍，作为整个项目的内容膨胀后的质量回归测试。

**测试定性（红线，写死）**：旧参考=自家共识+人工签字（非作者级外部真值）。本卡=**一致性/漂移回归**，不是正确率评测。产物措辞只准用"一致率/翻转清单/漂移"，禁用"准确率/验证为真/质量证明"句式。分歧簇=送 PI 复核候选清单，不自动判任一方错。本测恰是回答"改动这么多（v6/face v2.1/k9 激活/B5 治理）之后，系统还是不是当年那个好结果"——版本变化引入的合理位移与不该动的位移必须分开归因。

## 输入（全部盘上只读）
- 数据：/mnt/D/DR_GEO/dr-sc/redo_v2/data/main_annotated.h5ad（backed 读；267,192×36,601；obs.leiden 32 簇=冻结分群；**anno_v2/anno_v2_flag/quality_axis/p1/tau 列=真值区，判读侧构建证据面前必须剥离**）
- 旧参考：/mnt/D/DR_GEO/dr-sc/redo_v2/SIGNOFF_labels_20260928.md + tables/annotation_three_source_consensus.csv + REGRADE_VERIFY_REPORT_20260928.md
- 现役服务：/mnt/D/EyeKB/mcp_server/server.py（0.7-k9act，默认面含 k9_ocs=64 类）；env EYEKB_ACT_K9=0 可做 OFF 对照臂
- 引擎：/mnt/D/OcularKB/models/v2_prod/v2_prod_model.pkl（人版 10 类）
- 判读 runner 复用：/mnt/D/EyeKB/plans/evalset/annotation/run_annotator_run4r.py（三席同席同温同 prompt 变体，输出前缀改 drsc_reann，禁覆盖历史产物）
- env：/home/ubuntu/.conda/envs/scrnaseq/bin/python（anndata 0.13.2 可读全站件）

## 执行链（预注册先行）
0. **Phase-0 取证 + PREREG**：簇名册（32×n_cells×anno_v2 final_label×分级）、词表 crosswalk（引擎 10 类↔参考词表、判读具名↔参考词表）规则**先写死落 sha**；预期分歧声明先行登记：簇 7（provisional MG/Astro 骑墙）、簇 31（Endo——HRCA 无内皮类的参考缺类伪影在案）、Rod 质量轴簇（4/8/11）、RPE（面板仅 863 细胞）——这几组分歧不计入"意外漂移"头条。PREREG sha 落纸后才起跑。
1. **证据面 digest**：逐簇 wilcoxon top30（同现行口径）→ 五字段证据（query_marker 命中/基线组成对照/疾病先验[有 group 列：用 NC vs DR 分组]/RAG 文献片段+PMID/置信度）。双态各采一臂：**ON 臂（现役默认面含 k9）为主臂；OFF 臂（EYEKB_ACT_K9=0）为版本归因臂**——两臂之差=本轮激活的净位移（回答 PI 的质量问题最直接的零件）。top_genes 双列 schema（原 ID+sym 旁列）沿用。ENSG 先中性解码再喂库（RUN2 教训）。
2. **判读臂 E2**：三席跨厂商（run4r 同款同温），票规 v2 C2b，每簇输出具名/coarse/弃权+grade；5 簇/包断点续跑，enable_thinking:false。
3. **引擎臂 E1**：v2_prod 逐细胞预测（分块，MemoryMax 托管）→簇级多数+概率汇总（10 类词表，crosswalk 对照）。
4. **评分**：三方对照表（旧签字 × E2 consensus × E1）：exact 一致率（主=strict，谱系级并报取严）、逐簇翻转清单+归因四桶（词表/面版本位移[k9+v6+facev2.1] / 粒度墙 / 判读方差 / 意外漂移——后者才是要向 PI 解释的）、E2 两臂（ON vs OFF）簇级一致率差=激活位移量化。弃权单列（弃权合法，不计错）。

## 判读矩阵（预注册四格）
- 一致率高（≥80% strict 除预期分歧组）且意外漂移=0 → 现役系统对旧好结果稳健，"内容多了质量降"疑虑在本参照上否定；
- 一致率中等且漂移集中在预期版本敏感组（黑素/眼表类新词上位、免疫细分位移）→ 归因成立，列逐簇清单报 PI；
- 意外漂移 ≥3 簇（旧 high、非上述豁免组、方向性认错大类）→ 质量回归 FAIL 档，冻结新增内容波次，出逐簇取证报告；
- 判读臂跑不满/污染（泄盲）→ 如实 block，不硬考。

## 纪律
- 领地：工作目录 /mnt/D/EyeKB/plans/drsc_reann_test_20260930/（唯一可写）。**禁写**：/mnt/D/DR_GEO/**、kb/、mcp_server/、evalset/**、plans/其他目录；冻结件（SIGNOFF/consensus csv）不回改。
- 判读员禁见：anno_v2 列、digest 构造脚本的真值分支、旧 REPORT、对方席判读件。协调者验收只查结构不读票面内容（防泄盲）。
- copy 不 move；禁下载；禁外部检索；心跳带 available；重计算 systemd-run MemoryMax=16G；产物 sha 台账。
- 完成或遇阻必须落卡；报告头条数字必须同时给 strict/谱系两口径（取严）。

## 交付清单
DRSC_REANN_PREREG.md(+sha) / out/digest_{on,off}.jsonl / out/votes_run4r 系三席件 / out/E1_engine_table.tsv / CONSISTENCY_TABLE.tsv / DRSC_REANN_DISAGREE_attrib.tsv / DRSC_REANN_REPORT.md（含：三方对照、一致率两口径、激活位移 ON-OFF 差、豁免组单列、送 PI 复核候选清单）/ MANIFEST sha。
