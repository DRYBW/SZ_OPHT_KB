# MOUSEEXT 一页说明 — 鼠版重档外部集零下载预检结论

卡：t_f2bd45ce ｜ 执行人：AGENT_ROLE ｜ 日期：2026-09-28
放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加五（PI 整链授权，>1GB 下载仍需逐行勾）
协议：全程零下载——仅 GEO eutils 元数据、FTP suppl 目录清单、filelist.txt、HEAD（Content-Length）与本地盘上实测；零文件体下载。
产物：本文件 + `MOUSEEXT_APPROVAL.tsv`（行级报批清单）+ `scripts/`（探针脚本）+ `evidence/`（原始 JSON/日志/基因交集表）。

## 1. 基线（盘上实锤）

- mouse_prod_v1 十类 = Rod/BC/AC/RGC/MG(Müller)/Cone/Microglia/HC/RPE/Astro（META.json classes）。
- 训练池 = official MRCA（330,930 细胞）按 P28+ 10 类过滤后 270,523 细胞；**9 源 accession 实锤**（MRCA_all_cells_annotated.h5ad obs 逐细胞提取）：
  GSE243413(Chen×3 池=unified atlas 本体)｜Ma 2023(accession 未载)｜**Tran 2019=GSE133382**(aRGC1-10)｜**Yan 2020=GSE149715**｜**Shekhar 2016=GSE81904**(Bipolar1-6,P17)｜Jacobi 2022=GSE201254｜Benhar 2023=GSE199317。
- 本地在盘核查（find /mnt/D/{OcularKB/data,DR_GEO,RetinaAging}，96 目录）：GSE137400 目录**只有人源 lukowski2019_retina.h5ad**（179MB，非鼠本体）；GSE201402/GSE147573 鼠集在盘；RetinaAging GSE325477/478 在盘（主项目域）。

## 2. 三个核心判定（证据见 TSV 与 evidence/）

1. **点名两集 = 训练池母系列，GSM 级实锤**：
   - GSE137400（Tran Neuron2019 SuperSeries,437GSM）**包含**训练源 GSE133382 全部 10 个 GSM（aRGC1-10，10/10 交集）→ 训练池的 33,264 个 RGC 细胞就在这套数据里；其余 392 个 GSM = 同研究分选 RGC/ONC 损伤时序，且 GEO 不载逐细胞类型标签表（supp=仅 count 矩阵）。
   - GSE81905（Shekhar Cell2016 SuperSeries,683GSM）**包含**训练源 GSE81904 全部 6 个 GSM（6/6 交集，P17 FACS Vsx2/Chx10）；余库=按 GSM 标题即 BC 亚型的单细胞库，只覆盖 BC 一个类。
   - 结论：两集非"独立外部"，收之=拿训练细胞/训练域重测自己（循环）。**不收，无需勾下载。**
2. **GSE255520（2024-26 唯一"标签达标"新候选）= 同细胞重测**：4 个 GSM 标题与训练池 GSE243413 sampleid 逐名吻合（10x3_Ms_WT_P40/10x_Retina0426Cd73N/10x_RGC_live_AC…），supp 有逐细胞 class 表但细胞已全在训练池 → 循环。**不收。**
3. **2024-2026 全域检索零真外部全类候选**：GEO `mouse+retina/eye/ocular+single-cell, 2024:2026` 命中 289 条全部扫题+眼相关 156 条逐条判读，外加 snRNA/OIR/退行查询补扫——全部落入：疾病/扰动模型（OIR/RAA/IFNβ/AAV/KO×10+）、单类域（RGC/免疫/MG/杆体）、发育轴（P14/P17/E 期）、或脑眼混合。无任何"健康成体全视网膜+逐细胞作者标签"新集。经典家族补查：Macosko GSE63472 实锤 **P14（发育域）**且标签表不在 GEO；GSE147573 单库无标签。

## 3. 唯一盘上有标签资产：GSE201402（BOP 配套集，已在盘 1.3GB）

盘上实测（RDS 解包直读）：9,383 细胞 raw integer counts + **逐细胞 celltype 列 16 标签**（rod 6716/MG 445[Rlbp1⁺Aqp4⁺ 证实 Müller]/RGC 427/Cone 402/BC1-BC10 共 1076/AC 94/HC 23；Cx3cr1/P2ry12 阴性=无小胶；无 RPE/Astro）。accession 级不在 9 源。
**但**：① 冻结 P6 消费端断言 panel 覆盖 ≥90%，该对象交付件 counts 仅 6,275 基因（BOP 预过滤），**实测覆盖 1005/2000=50.25%** → 按冻结口径不可直接判分；② 仅 7/10 类；③ 单库单供体（F1 置信区间宽）；④ 供体年龄 GEO 未载。
处置=**不可判待补检**（补检路径已列 TSV，均为零/低下载；本卡不执行）。

## 4. 结论段：重档能否补出真第二外部 F1？

**不可（全类口径），证据钉死；存在一个受限的部分口径选项。**
- 命中的"带逐细胞作者标签"公开鼠眼全集共 3 套：GSE137400/GSE81905 = 训练池母系列（GSM 级实锤包含）；GSE255520 = 训练细胞重测（GSM 名级实锤）。→ **公开域内不存在第二个独立、健康成体、十类兼容、带作者逐细胞标签的鼠视网膜集**。08-26 的"稀缺"限定词就此收窄为"不存在"，重档天花板钉死。
- **部分口径**：GSE201402（盘上，零下载）可做 **7 类子集**外部评估——但必须（a）新建"低覆盖口径"评审门（50.25% panel 覆盖下的概率非零扰动，超出 v2 报告"93.2–95.6% panel-incomplete"先例一倍以上，默认按冻结断言拒绝），（b）预注册+送审后才可出数，（c）Microglia/RPE/Astro 三类永久 NA（单细胞制备域通病）。即便走通，也只是"部分外部证据"，**够不上对外引用级真全局第二 F1**。
- 真全局第二 F1 的剩余路径全部在公共检索之外：① 湿实验自送带注释新库（出本域，周期=PI 决定）；② GSE201402 若 PI 决定深检，走 10x 官方 demo 全基因矩阵（外部 CDN <1GB，免勾但需方案先行）+ 新口径预注册。
- 建议：**重档的"真第二外部 F1"目标以本卡为终止判定**——板上不再挂起等待；把资源转回中档已定性的使用方式（前瞻推断+报告制，BMR 型），或立"低覆盖子集评估"新卡走预注册（不在本卡范围）。

## 5. 红线自查

零下载（仅元数据/目录清单/HEAD/盘上已读对象）✅ ｜ models/mouse_prod_v1、plans/mouse_*、kb/ 只读 ✅ ｜ 不训练不建版 ✅ ｜ >1GB 行全部"不收"→ 等 PI 勾栏=空，零自动下载 ✅ ｜ 本地已在盘未列缺口（GSE201402/147573/325477/478/137398 均标注在盘）✅ ｜ 完成落卡 ✅

## 6. 证据索引

- 9 源 accession/sampleid/age：`evidence/mouseext_probe.json` + 本卡内 MRCA obs 直读记录（脚本 `scripts/mx_gsm_check.py`、`scripts/mx_inspect325478.py`）
- GSM 交集实锤（10/10、6/6）：`scripts/mx_gsm_check.py` 输出（本文件 §2.1）
- 289 条 GEO 2024-26 全量摘要：`evidence/mouse_all_summ.json`；初筛 80：`evidence/mouse2426_summ.json`
- 候选集 supp/标签/filelist 实测：`evidence/mx_filelists.json`、`evidence/mx_probe2.json`、`evidence/mx_heads.log`
- GSE201402 标签与 panel 交集：`evidence/genes.txt`（6,275 基因）、`evidence/panel_missing.txt`（995 缺基因前 200）、§3 实测数字
