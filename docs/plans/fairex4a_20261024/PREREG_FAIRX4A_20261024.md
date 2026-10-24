# PREREG_FAIRX4A_20261024 — 先落纸后跑数（两臂：X4A 宽容别名 / A1b 参考索引单变量）

卡片：t_f532079d　板：pi-briefing　日期：2026-10-24　执行：pi-chief
本文件在任何评分/任何 GPU 运算**之前**写定并冻结（sha 见 §9）。之后只允许追加"执行偏差登记"，
不允许改判据、不允许改白名单、不允许改参考索引构造规则。

---

## 0. 这张卡要settle什么

PI 2026-10-24 直接问：**"为什么人家测得高、我们测得低？解决了没有？"**
矩阵（同一引擎、同一条打分链、两卷）：
`B1a 0.5902→0.8968 | B1b 0.0676→0.8724 | A1b 0.3248→0.5068 | A1a 0.2464→0.4233 | C1 0.7433→0.5760 | C2 0.6783→0.4483`（x4a→x4b_super）。
机制已分解出一半（cw_x4a.tsv 119 行的可达性不对称 → 天花板 A1a/A1b 0.60、B1a 0.80、B1b 0.40、C1 1.00、C2 0.80），
另一半（A1b 的答案空间=**我们**建的参考索引）从未单独量过。本卡把它量出来。

**本卡不产出任何"谁更准"的结论。** 全部数字都是**命名一致度**（against 作者标签、in-sample 公开卷）。
口径令（永久）：与同类/已发表文章相同的统一标准（生信通用），不设更严门槛；严格档只作并列，不得用于承重或判阴性。
本卡不设任何通过/失败线——实验读数如实登记，不做"模型不行/工具很弱"表述。

## 1. 冻结锚（开工前实测，禁改写）

| 件 | sha256 |
|---|---|
| score_engine.py（冻结引擎，**零改动**） | `ee23ecba148155d9d92b0f41db9753312edc6ce683e02fd92d8d11ed2331e8d0` |
| arms/cw_x4a.tsv（官方映射，**零改动**） | `e54010be4f909201fb1bf80af0726e3f32d7a9f33aba2e70eec50ea5ddcd3ed3` |
| arms/engine_gold_x4a.tsv（金面，**零改动**） | `a5f9a9110afcd0d99589e0fe8571bca7c94a9d3086a1e915817e91053d0a9bb1` |
| arms/ALL_SCORES.json（官方表，**零改动**） | `f62349dff9721acb7c8723d97f939fbb1f743bea786a633a2ec610521decaa3f` |
| gold/MAP_X4A_fine2super_v1.tsv（16→5 档映射） | `0d9a7ab2f995d05f93455059c20cae75ca8945d37078584b85cb37e1a83f253b` |
| gold/x4a_input.h5ad（查询池 139,978×36,524，raw counts） | `1f46952273cd86aa70263b137e7cc0f8a12376f94770bd55d5e861ee9fe43d5a` |
| a1b_formal/meta200k.npy（官方参考索引标签，189,049 细胞/31 类） | `a61211b3a9adf1e1432d8a7dc79cf380a792fe771cd6104d29f95fa6e66c2c3d` |
| scGPT_human/best_model.pt（A1b 权重） | `6cb5d451ab5c4b33eb673adbe4fddc61d2389df1b89b7651a9fe2e557572b922` |
| scGPT_human/vocab.json | `acca93d114ca62c3f0f50debbd23e8c87f0714f4737764454f6b2b13f2e8580f` |
| HRA006282_optic_nerve.h5ad（B 臂参考候选，盘上已有） | `6b24894b857dcb609db22f5996c620512dd045db3977adbb673a8bbe91d8f010` |
| arms/pred_A1b_scgpt_x4a_raw.tsv（B0 复现门基准） | `3fdd5213cbb9a2b32c2dd54cc179aeb30ec6ff498edcb73f370f61c54772b047` |

官方 X4A 读数（引用于对比，不改）：A1b lineage macro-F1 **0.3248** / cov 0.6170 / invalid 53,621；A1a 0.2464；
B1a 0.5902；B1b 0.0676；C1 0.7433；C2 0.6783。金面 lineage 五档计数：glia 87,789 / immune 16,789 /
stromal 14,881 / pigmented 10,867 / vascular 9,652（合计 139,978）。

## 2. A 臂 — X4A 上的 X2 式宽容别名层

### 2.1 两个尺子的定义（并列报，禁只报一个）
- **严格尺**（official，`REPORT` 里照登不改）：冻结引擎 × `cw_x4a.tsv` → `ALL_SCORES.json['x4a']`。
- **宽容尺**（sensitivity）：冻结引擎 × **新**文件 `cw_x4a_lenient.tsv`。该文件 = `cw_x4a.tsv` 原样 +
  预先冻结的白名单增量行。**引擎零改动，官方表零改动，pred 零改动。**

### 2.2 白名单准入规则（先于任何打分写定）
一条增量映射（arm, raw_label → lineage, canonical_cell_type）只有同时满足下列 5 条才准进白名单：
- **R1 身份性**：该 raw_label 在 Cell Ontology / 作者定义上是目标金面类的**同义或亚型**（可cite），
  不是"看起来差不多"。
- **R2 金面内**：lineage 必须是金面五档之一（glia/immune/pigmented/stromal/vascular），
  ct 必须是金面 16 类之一（命名与 `engine_gold_x4a.tsv` 的 truth_celltype 逐字一致）。
- **R3 不看分**：候选集只能由"标签清单 × CL 身份"枚举得出，冻结并记 sha 之后才准调用引擎。
- **R4 神经元禁入**：amacrine / bipolar / horizontal / RGC / parasol / midget / rod / cone / starburst /
  photoreceptor / progenitor(RPC) 等**视网膜神经元与祖细胞身份，一律禁止**映射进金面五档。
  理由：X4A 金面的五档里**没有神经元档**（作者 curated 16 类全为 glia/immune/vascular/pigmented/stromal）；
  把神经元硬塞进 glia/vascular 不是"人类判卷会认的命名行为"，是制造位移。此条为本卡的**红线**。
- **R5 胶质内改名（Müller 家族）**：`Mueller cell` / `Mu_ller` / `imGlia` / `Glia` / `Early Glia` →
  `(glia, astrocyte)` 允许进白名单。理由：Müller 胶质是视网膜大胶质，金面胶质词表只有
  astrocyte/oligo/OPC/Schwann，同为 biglia 的 `astrocyte` 是其唯一落点；X2 先例的 Glia→glia 边即同类裁定。
  **该边单列标记 `edge_class=muller_within_glia`**，并在报告里单独给出"含/不含该边"两行。

### 2.3 预注册的必报量
1. 每臂 × 两尺的 lineage 四量（acc/macro_f1/coverage/selective）与 ct 三量（仅同阶段臂有值）；
2. **不可达质量分解**：每臂把"lineage 层落不进金面五档"的细胞按 raw_label 逐条列出计数，
   并与引擎的 `n_invalid_projection` 对账（允许因 ct 层无效而多计的差额，须逐条解释）；
3. **oracle 上界**（明确标注为"不可实现的上界，不是结果"）：若所有不可达细胞都被正确命名，
   lineage macro-F1 会到多少 —— 用来界定"任何别名层在天花板以内最多能搬多少"。

### 2.4 预注册判读
- 若宽容尺读数**不动**（Δmacro_f1=0.0000 或仅 Müller 边带来的 <0.01）：**这就是结论**，如实写
  "X4A 的读数不是词表/投影伪影"，不得为了出位移而放宽 R4。
- 若有位移：逐条给出是哪条边、搬了多少细胞、动了哪一档 F1；仍不得写成能力结论。

## 3. B 臂 — A1b 参考索引单变量替换（决定性测量）

### 3.1 一句话问题（报告里必须写在数字之前）
> 若答案空间里本来就有 X4A 金面那几类（endothelial / fibroblast / pericyte / vSMC / oligodendrocyte …），
> A1b 是**能把它们叫对**（=边界在我们建的参考索引），还是**仍然叫不对**（=边界在模型识别力）？

### 3.2 单变量原则（固定项逐条）
固定：模型构建、checkpoint（`6cb5d451…`）、gene vocab 映射（scGPT_human/vocab.json）、HVG 配方
（X4A 池 `filter_genes(min_cells=10)` + `highly_variable_genes(n_top_genes=5000, flavor='seurat_v3')`，
与 `a1b_x4_gpu.py` 逐行同配方）、kNN `k=50`、投票规则（`np.unique` 计数取最大，ties 按 np.unique 排序取首个，
逐字照抄官方代码）、embedding 调用（`sg.tasks.embed_data(..., gene_col='index', batch_size=256,
device='cuda', use_fast_transformer=False, return_new_adata=True)`，model.eval()）、L2 归一 + `IndexFlatIP`、
查询池 = X4A 全部 139,978 细胞（分母与官方完全一致）。
**唯一变量 = 参考索引的标签空间**（及其必然连带：承载该标签空间的参考细胞集合）。

### 3.3 参考索引构造规则（先冻结）
- **来源**：`/mnt/D/OcularKB/data/HRA006282_optic_nerve/HRA006282_optic_nerve.h5ad`（Chen et al. Cell 2024
  人视神经+视神经盘 snRNA，盘上已有，**零下载**）。
- **泄漏控制（按卡的三级优先序，逐条实核）**：
  - P1（study-disjoint，优先）
    - 参考**排除 X4A 的全部 19 个供者**（`donor_id ∈ X4A donor list`），并实测 cell-id 交集 = 0；
    - 实测：X4A 19 供者在 HRA006282 中占 146,121 核（source=Sanes/Harvard），
      剩余 813,508 核 67 供者全部 source=Chen/BCM（**不同贡献研究**）；
      叠加**成人闸**（`donor_age ≥ 18`，KB2c 判定）后 = **704,538 核 / 57 供者**（本次 recon 实测）。
    - ⇒ 采用 **P1（供者级零重叠 + 不同贡献研究）**；**如实披露**：两份数据同属 HRA006282 这一 CELLxGENE
      collection/同一批论文作者群，因此记为 **"study-adjacent, donor-disjoint"**，不做"完全独立研究"的宣称。
  - P2（X4A 供者级拆分）作为**备用**：若 P1 参考的类覆盖不足则不启用并说明；本卡 recon 显示 P1 覆盖齐，
    故不启用 P2。
  - P3（拿被评细胞自身当参考）：**禁用**，本卡结构上不可能发生（cell-id 交集 0 + 供者零重叠）。
- **标签空间**：= **金面自己的 16 类**（identity 映射，逐字用 `engine_gold_x4a.tsv` 的 truth_celltype），
  5 档 lineage 由 `MAP_X4A_fine2super_v1.tsv` 派生。构造映射表 `MAP_X4A_ref_HRA006282.tsv`（新增件，含
  decision ∈ {map, drop} 与逐行 evidence）。
  - `map`（同 CL 类或明确的 CL 亚型）：oligodendrocyte、astrocyte、retinal astrocyte→astrocyte、
    fibroblast、microglial cell、macrophage、OPC、{blood vessel / capillary / venule / fenestrated} endothelial
    →endothelial cell、pericyte、vSMC、{retinal pigment epithelial, pigmented epithelial}→pigmented epithelial cell、
    melanocyte、T cell、B cell、NK、{non-myelinating Schwann}→Schwann cell、myelinating Schwann cell。
  - `drop`（不在金面 16 类本体里）：全部视网膜神经元/光感受器/双极/无长突/水平/RGC/RPC、Mueller cell、
    adipocyte、mast cell、dendritic cell。**drop = "答案空间=金面本体"的实现**，落盘计数如实登记。
- **平衡抽样**：每类上限 **12,500** 细胞，seed=**20261024**，稀有类取全量。预计总量≈120,000
  （官方参考 189,049；**如实披露总量不同**，并说明 k=50 为局部投票、对总量不敏感，但这是本设计的一个未隔离变量）。
- **基因空间**：只用 X4A 池算出的那 5,000 个 HVG（symbol，经 `feature_name`），参考细胞取同一集合；
  报告实际匹配数。scGPT 的 collator 按 vocab id 排序并截断到 max_length=1200，故**列的先后不敏感、集合必须相同**。
- **S2 敏感臂（免费）**：把 Müller 细胞也纳入参考并映射 `Mueller cell→(glia, astrocyte)`，检验 R5 那条
  判断对 B 臂结果的影响。Müller 细胞一并进 embedding 池，故 S2 只需重建索引、无需重算 embedding。

### 3.4 B0 复现门（先证仪器同一，再谈结果）
用本次重算的 X4A embeddings 查询**冻结的** `formal200k.index`，与官方
`pred_A1b_scgpt_x4a_raw.tsv` 逐细胞比对：一致率必须 **≥0.99**。
不过 → **停**，如实报"仪器未能逐值复现"，不拿新数字当结论。

### 3.5 预注册判读（先写死，数字出来后只准照此填）
| 观察 | 判读（照写） |
|---|---|
| macro-F1 明显上移，且原先不可达的 stromal/vascular 出现非零 F1 ≥0.4 | **边界在参考索引（我们这边）**：A1b 的 X4A 低读数主要是答案空间边界，不是识别力失败 |
| macro-F1 基本不动（≈0.32）或新可达类仍≈0 | **边界在识别力**：即使类在答案空间里，零样本 embedding 也不分得开 |
| 中间态 | 给分量拆分：哪些类被救回、哪些没有，按 per-class F1 逐条写，不给定性帽子 |
本卡不设"通过/失败"数值线；上表是**判读口径**，不是门槛。

### 3.6 B 臂必报量
引擎同一格式六量（lineage 四+ct 三）＋ **五档 lineage per-class F1** ＋ `n_invalid_projection` ＋
`n_unmapped_label`/`n_suspended_mapping` ＋ 台账：参考类计数、被 drop 的类计数、5,000 基因匹配数、
索引 ntotal、embedding 耗时/吞吐、GPU 心跳。与官方 `0.3248 / 天花板 0.60` 直接并列同一行。

## 4. C 臂 — 收口表（放报告最前，四列同仪器）
列 = ①各自开卷切片（`TOOL_ACCESS_MATRIX.md` L23-31：A1a Microglia 79/79=100%、A1a RPE 29/48=60.4%；
A1b Microglia 79/79=100%、A1b RPE 48/48=100%；B1a/B1b 另有装机冒烟 Microglia 78/79=98.7% / 55/79=69.6%，
标"装机冒烟、n=79、非能力读数"；C1/C2 无开卷切片 → `NA`）
② X4A 严格（官方）③ X4A 宽容（A 臂）④ X4B_super（官方已测）。
**开卷切片的 n 极小（79/48 细胞）且属论文自家 eval/装机件**，同列必须标注，不得当能力证据。

## 5. 红线（逐条照做）
1. 不改冻结引擎、不改官方映射、不改官方表、不改 F_X4_RANKING.md；一切实验件走**新文件**。
2. 不做任何 accuracy 宣称；"名字与本体一致"≠"判得更准"。
3. 禁写 "scGPT is worse" / "外部工具很弱"；登记式表述：读数 conditional on 我们的冻结词表**与我们的参考索引**。
4. 每个数字必须能追到产生它的命令；`NOT_RUN`、缺前置条件一律不许当通过。
5. 零下载、零外网。
6. 本地提交，**不 push**；报 commit hash。
7. GPU 一律走 `gpu_arbiter.sh lease-acquire/lease-release`（禁手动 systemd stop qwen）；重计算段
   `systemd-run --user -p MemoryMax=<实测+余量>G -p MemorySwapMax=2G`；并发 ≤ min(8, cpu/2)；
   每 30 min 心跳带 `available`；`available < 40 GiB` 不开新活。
8. 产物双落位：大件（embeddings/index）→ `/mnt/D/EyeKB/plans/fairex4a_20261024/work/`；
   交付件（报告/表/脚本/sha）→ 仓内 `docs/plans/fairex4a_20261024/`。

## 6. 执行顺序（禁跳步）
1. 落本 PREREG + sha → 2. A 臂白名单枚举 + 冻结 sha → 3. A 臂双尺打分（纯 CPU）→ 4. 5,000 HVG 重算并落盘
→ 5. X4A embeddings（GPU 租约）→ 6. **B0 复现门**（不过即停）→ 7. 参考细胞抽取 + embeddings →
8. 建索引（主 + S2）→ 9. 查询投票 → 10. 引擎打分（新 cw：`cw_x4a_refswap.tsv`，identity 映射）→
11. C 表 + 报告 + MANIFEST + 本地 commit。

## 7. 失败与偏差登记口径
任何一步失败/降级，写入报告的"执行偏差登记"段：哪一步、实测报错、是否影响哪一列数字、如何处置。
缺前置条件 = `NOT_RUN`，禁以小样本冒充正式读数。

## 8. 预期风险（先写出来，事后不得追认为"没想到"）
- R1：B0 复现门可能不过（embedding 不确定性/环境差异）→ 若一致率 <0.99，停，报告如实写"仪器不可逐值复现"，
  并把不一致量级写清；**不拿新数字当结论**。
- R2：HRA006282 是 9.3 GB / 960k 核，随机行切片在 NTFS-FUSE 上慢 → 采用**分块顺序读**（chunk 50k 行）
  并按需筛细胞，避免整件入内存（预计峰值 <20 GB，先实测单块 RSS 再定并发）。
- R3：参考的稀有类（B/NK/myelinating Schwann）只有 300–400 细胞，投票侧对这几类的支撑弱于 X4A 自定义
  环境 → 如实登记，不外推。
- R4：A 臂可能"零位移"，这是预期内的合法结果（brief 已预告），照写。

## 9. 冻结签名
本文件 sha256 见 `MANIFEST.sha256`（生成时登记）。A 臂白名单文件 sha256 见
`out/WHITELIST_X4A.sha256`；B 臂映射表 sha 见 `out/MAP_X4A_ref_HRA006282.sha256`。
两者均在**调用引擎之前**生成并落盘。
