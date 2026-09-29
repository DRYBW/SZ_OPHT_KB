# DECISION_TABLE_composition_gates — 组成敏感门实测勾选表（D-2 / D-3）

- 卡：t_db0c8206（DISC_QANT）｜ 2026-09-28 ｜ 任务书：BRIEF_DISC_QANT.md（=本卡唯一任务书）
- 性质：**决策依据件**。全程只读冻结票面与评测卷；球门与票规零移动、协议零改；两门翻转/位移仅作敏感性观察，**不作因果结论、不作"注释有误"判定**；阈值只出建议档，**勾哪档由 PI 拍板，本卡不代拍**。
- 两门若当时上线的"会旗标什么"按双口径（冻结票面 + 评估卷）都算，见下。

---

## D-2 供体翻否杠杆门（leave-one-donor-out）

票规 v2 C2b 逐字复刻冻结实现（o10_verdict_t_c145db7c.py），票不重投；truth 按冻结口径（super_map 折叠 + EXCL 剔除 + n≥10 + 并列判未定取严）逐 donor 删除后重算。输入：Q6_clusters.tsv（50 donors）× 票面 v2.1 三席 99 票 × RUN5 冻结三席票。

### 实测数字（双口径）

| 口径 | 被计 hit 单元 | 单 donor 删除即翻否单元 | 翻否率 | 翻否类型 |
|---|---|---|---|---|
| ① 冻结票面 v2.1（oblig 99 票，P1=26/33） | 26 | **2** | **7.7%** | 2 例均 shrink_out（删除后 truth 池<10 细胞判未定）；label 翻转 0 例 |
| ② 评估卷（RUN5 冻结票按 C2b 复算，P1=25/33） | 25 | **1** | **4.0%** | shrink_out 1 例；label 翻转 0 例 |

翻中杠杆点（两口径重合）：
- **Q6::30**（126 细胞，Epithelium）— 删 `li_donor72`（占 92.9%）即翻否；仅票面①口径为 hit。
- **Q6::33**（1,339 细胞，Fibroblasts）— 删 `BCM_22_0698`（占 99.4%）即翻否；两口径皆 hit。
- 其余 24/24 个 hit 单元：删除任一 donor 均不翻。两口径共测 1,653 个 簇×donor 组合，仅上述 3 行翻否，1,650 行中性。

面板级单 donor LOO（整卷删该 donor 再全量重算）：票面①最坏 P1 26→25，评估卷②最坏 25→24 —— **≥24/33 球门在任一 donor 删除下均不破线**（②擦线 24=24，如实登记）。

对照基线：D1 线 S13 = 5/7（71.4%）连续估计量单 donor 翻号。本门实测 7.7%/4.0% 与 S13 **口径不同形不可直接比**：本门是分类判定（hit 等式），翻否集中暴露于"小单元×极高主导 donor"形态，label 翻转路径在 truth_frac≥0.99 的 hit 集上结构性难触发。方向结论：**票面/评估卷的 hit 判定整体供体稳健；真实杠杆=两个近单供体单元（92.9%/99.4%），与 S13"杠杆 donor"同型。**

### D-2 勾选表（阈值等 PI 勾，不代拍）

| 档 | 建议规则 | 冻结票面①实测旗标 | 评估卷②实测旗标 | 勾选 |
|---|---|---|---|---|
| T1（最严） | 任一单 donor 删除即翻否 → 旗标该单元降级"供体敏感" | 2/26 单元（Q6::30、Q6::33） | 1/25 单元（Q6::33） | ☐ |
| T1b（外科手术式） | 主导 donor 份额≥50% 且删除翻否才旗标 | 2/26（实测与 T1 旗标集完全重合——翻否的全部是份额≥90% 单元） | 1/25（重合） | ☐ |
| T2（面板警戒） | 单元翻否率≥20% 才整卷升级警戒 | 未触发（7.7%<20%）→ 0 单元 | 未触发（4.0%<20%）→ 0 单元 | ☐ |
| T3（最松） | 仅记录不门控（杠杆 donor 对入台账） | 台账 2 对（li_donor72@Q6::30、BCM_22_0698@Q6::33） | 台账 1 对 | ☐ |

勾 T1/T1b 附注：两档在本数据上**旗标集相同**，差异只在未来出现"中份额 donor 翻转"时 T1 先于 T1b 报警。勾 T2 附注：按实测，任何单 donor 都删不破 ≥24/33 球门——T2 对本类票面无牙齿。

---

## D-3 深度匹配 ranking 位移门

现行口径逐字复刻（mean-diff@HVG4000，kb2_digest2.py FAST 分支 / step2b2 author-class 口径）；处理组=按 n_genes/total_counts 十分位分位对齐重抽类细胞（瓶颈法，seed 冻结=20260928，R=50 抽）；对照=全样重算；同规模均匀随机抽样作噪声基线。**位移只作深度混杂证据，不判词条对错。**

锚点：retina 面板（markers_local_lib 在 kb/baselines/retina.json）→ Q3_137537（真 counts 层，n_genes 轴+total_counts 轴双跑互证）、Q4_148077（n_genes 非零代理）；ocular_surface 面板（9 类，基线 json 无 markers_local_lib）→ Q6_sub100k（nFeature_RNA 真值）。其余 9 个面板盘上无带类标签 counts 锚点 → 登记不可算（不编数）。

### 实测数字

| 统计量 | 实测 |
|---|---|
| 可算行（面板×类×锚点） | **18/39** |
| 全分位对齐不可行行（N'=0，深度分布缺低分位支持） | **16 行**（Q4 10 类中 7 类不可对齐[仅 AC/MG 可算]；Q3 的 Cone/HC/RGC/Micro×两轴；Q6 Corneal Endothelium）|
| 样本过少行（<10 细胞） | 5 行 |
| Kendall τ（全 HVG4000 打分向量，中位） | 整体 **0.80**（区间 0.58–0.94；大类 0.85–0.94，小类/深度偏斜类 0.58–0.84） |
| top5 位移≥1（中位） | **11/18 行** |
| top10 位移≥3（中位） | **0/18 行**（最大中位 top10 位移=2，Q6 Fibroblasts/Immune） |
| 位移超噪声基线（matched 中位 top10 位移 > 随机抽同规模噪声） | **6/18 行**（BC@Q3 两轴、AC@Q4、Fibroblasts@Q6、Immune@Q6、Melanocytes@Q6） |
| 现役清单（markers_local_lib）在 top10 的存活率 control→matched | 0–0.6；仅 AC@Q4 0.4→0.2 因深度对齐下降（其余不变） |

方向读数（观察句式，非判定）：整体排序在深度对齐后大体保持（τ 中位 0.80，无一触发 top10≥3）；位移集中在头部少数行，且多数行的 matched 位移不超出纯抽样噪声——**深度特异位移证据成立但幅度有限（6/18 行超噪声）**。16 行"全分位不可对齐"本身是最强的深度失配存在性信号（这些类深度分布缺全局低分位支持，重抽不可行）。

### D-3 勾选表

| 档 | 建议规则（上线时旗标对象） | 实测旗标数 | 勾选 |
|---|---|---|---|
| B1 | top5 任一位移（中位≥1）即旗标该行 | **11/18 行**（注：其中 5 行位移不超噪声基线——若按"超噪声"收紧则 6/18） | ☐ |
| B2 | top10 ≥3 位移才旗标 | **0/18 行**（本档无牙齿） | ☐ |
| B3 | 仅高表达基因位移才旗标 | **11/18 行**（11 行的 top5 位移基因全部是高表达档，与 B1 集合重合） | ☐ |
| B4 | "全分位深度对齐不可行"单独成旗（存在性门，不看位移幅度） | **16/39 行** | ☐ |

B1/B3 在本数据上旗标集相同（位移基因全落高表达档）；B4 与 B1–B3 正交可叠加。

---

## 盲区声明（口径限制与低估/高估方向）

**D-2：**
1. 票不重投（本卡禁 API/禁动票预算）：翻否只重算 hit 等式的 truth 侧；若输入面（簇 top_genes/成员）随 donor 删除联动重投，旗标只会更多不会更少 → **实测 7.7%/4.0% 是下界**。
2. 翻否两例均 shrink_out、label 翻转 0 例：hit 单元 truth_frac 普遍 ≥0.99，单 donor 删除结构上难翻 label——分类门与 S13 连续估计门的暴露面形态不同，对照时须带此注。
3. 并列 tie 判未定为取严口径；实测 strict/loose 两口径旗标数一致（tie 未触发）；冻结代码本身取 value_counts.index[0]。
4. 评估卷 C2b 复算 P1=25 ≠ 历史裁决 21：差异来自票规代际（C2b 计 coarse、grade 不限），与 donor 无关；历史 RUN5 裁决冻结不动，本表为"若此门当时上线"的叠加模拟。
5. donor 为标签列直读（shi_donor1 等）；pooled 样本（dickman_Cornea07/08）按一个"供体"单元计。
6. P2 门（词条反污染）未做 donor-LOO——任务书 D-2 定义为"被计 hit 的单元"，P2 违例集为空（0/33）无翻面空间。

**D-3：**
1. HVG 基因集冻结=全样对照集 → 位移不含 HVG 选择方差；若逐重抽重选 HVG，位移只增不减 → **位移被低估**。
2. 复算口径=digest FAST（HVG4000 seurat + mean−全池均值）；KB7 W2 火灾审计分（词条修复链）口径不同且 D001 构建池不在本卡领地，未复跑——本卡量的是"票面/评估卷 top_genes 管线"的位移，不是词条发布审计链的位移。
3. 瓶颈式全分位对齐苛刻：任一深度桶无类细胞即"不可对齐"——16 行登记为不可算而非零位移；若改支撑截断对齐能给出数字，但会把失配伪装成小位移（本轮不做，PI 如要另卡）。
4. 可算行 retention 0.3%–49%（小样本臂噪声放大）→ **按 B1 原样计数会高估深度特异效应；按"超噪声"判会低估**（分层抽样方差本就低于均匀抽样）。两个方向均已登记，matched/noise 双列在表可供任意收紧。
5. 深度轴：Q3=真 counts 双轴（n_genes/total_counts 互证，Rod/BC/AC/MG 方向一致）；Q4=无 counts 层用 logcpm 非零数代理 n_genes；Q6=nFeature_RNA（portal 保留列，真值）。CPM 归一后 total UMI 不可恢复——Q4 的 total_counts 轴本轮**不可算**（如实登记，非零位移）。
6. markers_local_lib 存活率仅作语境：该清单产自 D001/HRCA 面板，与 Q3/Q4/Q6 评估卷本就不同构建池——低存活≠词条错（不判定）。
7. 两分句口径取严：D-2 取 strict；D-3 三档均用逐行"中位位移"（分布见 SHIFT_draws.tsv 901 行）。

**两门共性**：全部结论限于盘上冻结件（Q6::33 票面/评估卷 + retina/ocular_surface 面板）；不外推到其他组织面板；"旗标=提示复核"，不等于注释错误或词条错误。本表未接线、未激活——接线与激活另卡另批。

---

## 文件清单与复现

- 本表：`DECISION_TABLE_composition_gates.md`（唯一决策依据件）
- D-2 表：`out/LEVERAGE_table_units.tsv`（1,653 行：口径×hit单元×donor×翻否）、`out/LEVERAGE_summary.tsv`（51 行）、`out/PANEL_LOO_donors.tsv`（100 行=50 donor×2 口径）、`out/q1_stats.json`
- D-3 表：`out/SHIFT_table_panels.tsv`（39 行=面板×类×锚点）、`out/SHIFT_draws.tsv`（900 逐抽：top5/top10 位移+τ）、`out/q2_stats.json`
- 脚本：`scripts/q1_leverage_t_db0c8206.py`、`scripts/q2_depthshift_t_db0c8206.py`（seed=20260928；C2b/truth/mean-diff 三处口径均逐字复刻冻结实现并先跑自测断言；q1 复算 P1 与冻结 verdict.json 逐簇一致断言 PASS 后方出数）
- 日志：`logs/q1.log`、`logs/q2.log`、`logs/q2.rc`（=0）
- 复现：`<CONDA_ROOT>/envs/scrnaseq/bin/python scripts/q1_leverage_t_db0c8206.py`；q2 需 `systemd-run --user --property=MemoryMax=16G` 包裹（100k×35k h5ad 驻留）
- 输入冻结件（全程只读，未动一字节）：`obligrun_20260928/{face/kb9_face_v2.1.jsonl, out/ANN_{A,B,C}_oblig.jsonl, out/oblig_verdict.json}`、`evalset/{clustering/Q6_clusters.tsv, defs/Q6_def.json, data/Q3_137537_logcpm.h5ad, data/Q4_148077_logcpm.h5ad, data/Q6_sub100k.h5ad, annotation/ANN_{A,B,C}_run5.jsonl, work_t_d1ca11b0/Q6_truth_map.tsv}`、`kb/baselines/retina.json`、`rp_project/m3/s2/ensg_symbol_map.json`
