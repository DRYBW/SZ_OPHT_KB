# SEURATPROBE_REPORT_v1.0 — Seurat/SingleR 双轨可行性探针（t_5d18900e，2026-09-28/29）

任务书：BRIEF_SEURATPROBE.md（PI 追加七A 拍板 + 降级条款）。本卡不接线、不改生产面、全 CPU、领地=plans/seurat_probe_20260928/。

## 0. 结论速览
- **G0 装机：PASS**（conda 新 env r_seurat_probe：R 4.5.3 + Seurat 5.5.1 + SingleR 2.12.0 + scrapper 1.4.0；包归档实测下载 **305.4MB ≤ 1GB 门**，未触发报批停卡）
- **G1 试点：PASS**（20k 细胞 RSS **3.31GiB** ≤20G；端到端 **64s** ≤15min）
- **G2 全量：跑通**，三数字在案（§3-5）；全量 DS1 180k 单链 RSS **17.96GiB** / **6:47**（仍在 ≤20G/15min 形态内，需 24G cgroup 顶托管）
- **第二票转正建议（不代拍）**：**当前 SingleR 配置 = NO-GO 转正；分歧送 PI 机制 = GO 可用**（详见 §6）

## 1. Phase-0 数据集核实（详见 tables/PHASE0_dataset_verification.md）
193 个 h5ad 全盘枚举 + 11 候选 obs 列取值分布实测。真值只取 <STORE>/registry 逐细胞作者级注释标准集；明令禁用的 GSE165784/GSE160306 未用；分选池（GSE226108 神经元富集）、发育轴（GSE155288）、无 counts（GSE183320）、自家 relabeled/query 面全部排除并留证据。
- **DS1** = Shekhar 17 物种图谱人子集：180,093 × 60,671，`shekhar_class` 作者 7 类（RGC 81,085/Rod 44,903/AC 37,032/MG 5,615/BC 4,856/HC 4,577/Cone 2,025），X=原始整数 counts，symbol 索引。MG 类经 per-cell marker 检出率实测确认=Müller 胶质（RLBP1 0.42/GLUL 0.69 vs 小胶标记≈0），全数据集无小胶质细胞。
- **DS2** = Lukowski 2019 成人视网膜：19,694 × 36,475，`author_cell_type` 14 类，raw/X=counts；供体 42/53/80 岁全成年；unannotated/unspecified 3,704 记 EXCL 不入判分。
- 双集均人源 → 同物种对照 ✓；单集 ≤20 万 ✓；零新下载 ✓。

## 2. 双轨设置（同一起点 counts）
- **轨 S**（Seurat 5.5.1 + SingleR 2.12.0）：LogNormalize → HVG vst 2000 →（DS1>5万细胞时特征子集裁剪，内存修复见 §7）ScaleData → PCA50 → neighbors k=20 → Louvain res=1.0 → SingleR 簇级（cluster=簇归属），参考=**自建交叉参考**（DS1↔DS2 互为参考、按标签伪 bulk 均值 profile、HVG∩ref 前 3000 特征；选择理由：零下载纪律排除 Monaco/HCA 的 ExperimentHub 运行时下载，同物种同组织、双独立作者图谱；版本 SingleR 2.12.0/scrapper 1.4.0 落账）。
- **轨 P**（现行面镜像）：training-venv scanpy 1.12.2：normalize_total 1e4+log1p → HVG seurat 2000 → PCA50 → neighbors15 → leiden res1.0（igraph，seed=20260928）→ wilcoxon top30 → **kb/marker 面判读** = 簇 top30 与现役 marker 库（markers_v4.1_clean ∪ markers_v6_retina_repair，v6 覆盖同名类；sha256 见 trackP_*_meta.json）共享基因数 argmax，0 命中→MISS。规则只读复用，未改动。
- 词表对齐：DS2 作者 14 类映射到库 10 类（rodA/B/C→Rod、bipolarA–D→BC、Müller→MG、microglia→Micro、unannotated/unspecified→EXCL）。

## 3. 数字一 · 跨引擎一致率（逐细胞，簇级标签对真值；EXCL 剔除）

| 指标 | DS1 (n=180,093) | DS2 (n=15,990 evaluable; EXCL 3,704) |
|---|---|---|
| ARI / NMI（轨S vs 作者真值） | **0.748** / 0.730 | **0.366** / 0.571 |
| ARI / NMI（轨P vs 作者真值） | **0.821** / 0.758 | **0.823** / 0.770 |
| ARI / NMI（S vs P 跨引擎） | 0.752 / 0.792 | 0.360 / 0.525 |
| 簇主导真值匹配（S） | 17/24 | 13/21 |
| 簇主导真值匹配（P） | 15/17 | 16/22 |

簇级混淆矩阵：tables/number1_confusion_{S,P}_vs_truth_{DS1,DS2}.csv；每真值类双轨纯度：tables/three_numbers.json（purity_by_truth_*）。

## 4. 数字二 · SingleR 增益与改判清单
逐类一致（S=SingleR 簇级调用，P=kb 判读）：

| 类 | DS1 S / P | DS2 S / P |
|---|---|---|
| Rod | 0.762 / 0.776 | 0.545 / 0.930 |
| RGC | 0.926 / 0.982 | 0.873 / 0.302（真值仅 63 细胞） |
| AC | 0.999 / 0.909 | 0.673 / 0.000（AC 281 细胞散落非 AC 簇） |
| BC | 0.9996 / 0.979 | 0.986 / 0.982 |
| Cone | 1.000 / 0.994 | 0.935 / 0.918 |
| HC | **0.000** / 0.374 | —（DS2 无 HC 真值类） |
| MG(Müller) | 0.602 / 0.618 | 0.953 / 0.971 |
| Micro | —（DS1 无小胶） | 0.000 / 0.930 |

- **SingleR 无净增益**：两集对真值的 ARI 均低于轨 P；DS1 HC 全灭、DS2 Micro 全灭 = **交叉参考词表缺类**（DS1 无小胶、DS2 无 HC）导致的系统性过判（DS1 改判 8/8 簇 S 全过判 AC；DS2 c18 小胶被 S 判 Rod）。
- 改判清单（簇级 S≠P）：DS1 8 簇 / DS2 8 簇（tables/number2_changes_S_vs_P_*.csv），逐条挂文献支持：kb 词条全命中（10 类全在库）；v6 库可提取逐类 PMID 的类（BC 42124641 / AC 33393903,38087179,41037735 / RGC 24449362 / MG 29561967 / RPE 等）已写入 support 列；Rod/Cone/HC/Micro 仅 v4.1 冻结词条、无逐类 PMID → 标"单条文献待补"。

## 5. 数字三 · 分歧簇清单（=未来送 PI 裁决形态样本）
- 定义：S_call ≠ P_dom 的簇（16 条，DS1 8 + DS2 8），含 n、双轨调用、P 置信、真值主类、文献支持列 → 即为可下发的裁决包形态。
- 工作量样本：**每卷（数据集）约 8 簇待 PI 裁**；若按双集外推"一卷"（~18 万细胞级图谱）≈ 8±4 簇。
- 值得注意：分歧簇中 P 与真值更符合的占多数（DS1: P 对 5/8；DS2: P 对 2/8、S 对 1/8、双错 4/8——DS2 的 c17/c0 类混合簇是真·无单一裁决形态，正是需 PI 的样本）。

## 6. 第二票转正 GO/NO-GO 建议（建议不代拍）
- **转正当前"Seurat+SingleR（自建交叉参考）"为第二票引擎：NO-GO**。依据：增益为负（§4），且词表缺类造成系统性过判；单票噪声高于现行走 scanpy+kb 面。
- **"双轨并跑 + 一致自动过 + 分歧送 PI"机制本身：GO（机制可用）**。本探针已验证形态：一致率高（DS1 ARI(S,P)=0.75，多数簇自动过）、分歧量可控（~8 簇/卷）、裁决包字段可直接复用本表。
- **复活 SingleR 的升级前置（若 PI 想保留引擎对照选项）**：换官方/第三方同组织全类参考（Monaco/HCA 或人视网膜全类图谱）= 运行时新下载动作 → **属 >1GB/下载报批门，需 PI 批准**；或人工把 DS1+DS2 并集词表补全（HC/Micro 至少一类外源参考）后再测。本轮如实报告现状不擅自引入。
- 机器侧可行性（PI"机器不支持则只走单轨"降级条款的读数）：**机器支持**——DS1 180k 全链 RSS 17.96GiB / 6:47，24G cgroup 顶内完成；无需退回单轨。

## 7. 局限声明（如实）
1. 交叉参考粒度错配：DS1 7 粗类 vs DS2 14 细类映射后 7 类 + 两集词表互补缺口（DS1 无 Micro、DS2 无 HC/Astro/RPE）→ S 数字是"最不利参考配置"，不外推为 SingleR 上限。
2. 轨 P 判读是现行面的机械镜像（top30×marker 库 argmax + MISS）；现行生产判读含 MCP 证据分级与 LLM 票箱，本探针未复现票箱层（成本纪律），数字用于引擎对照，不等于生产准确率。
3. 全量链在 180k 时曾在未裁剪配置下触发 24G cgroup 击杀（OpenBLAS 128 线程 + 60k 全基因层复制叠加）；修复=限 16 线程 + >5 万细胞时 HVG 特征子集；修复后 PASS 留痕 logs/G2_chain.log。该教训已写入本报告的复现参数。
4. 试点门 G1 数字（3.31GiB/64s）为 20k 子集；G2 全量（17.96GiB/6:47）另行实测——两者都过，但说明 20k 试点对 180k 全量的内存外推偏乐观（~5.4×）。
5. SafetyError（TUNA r-base 解包 size 误报）不影响功能，library() 实测通过（G0 台账留痕）。
6. DS2 的 Micro 真值 n=142、RGC n=63、AC n=281：低支撑类的 S/P 数字方差大，逐类一致仅供参考。

## 8. 资源与执行台账（systemd-run --user -p MemoryMax=24G -p MemorySwapMax=2G，/usr/bin/time -v 实测）
| 步骤 | 峰值 RSS | 墙钟 | rc |
|---|---|---|---|
| G1 试点（DS1 20k，Seurat 链） | 3.31 GiB | 64 s | 0 |
| trackP DS2（scanpy+判读） | 1.72 GiB | 89 s | 0 |
| trackS DS2（Seurat+SingleR，含载入 DS1 参考 90s） | 9.59 GiB | 169 s | 0 |
| trackP DS1（scanpy+判读，180k） | 7.49 GiB | 992 s | 0 |
| trackS DS1（Seurat+SingleR，180k，特征子集修复后） | **17.96 GiB** | 406 s | 0 |
| metrics（三数字） | <1 GB | ~5 s | 0 |
心跳 free available 全程 232–237G，未触发 <40G 停并发条款。GPU 零触碰。

## 9. 证据与复现
脚本 scripts/（export_counts.py、export_ds1_sub.py、export_ds2_fix.py、ds1_mg_probe.py、phase0_scan_obs.py、phase0_pass2_detail.py、trackP_scanpy.py、g1_seurat_pilot.R、g2_seurat_singler.R、three_numbers.py、annotate_changes.py、run_g1.sh/run_g2_*.sh/g0_download_watch.sh）；日志 logs/；表件 tables/；数据件 data/（mtx 可再生，保留）。
复现顺序：export_counts.py → export_ds1_sub.py →（systemd-run）run_g1.sh →（systemd-run）run_g2_chain.sh → run_g2_final.sh → three_numbers.py → annotate_changes.py。
中间产物全保留；MANIFEST_SEURATPROBE.sha256 固化交付清单。
