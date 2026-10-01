# EyeKB 镜像仓同质化契约（VERIFY CONTRACT，2026-09-28 立）

> 起因（PI 09-28 实测定调）：仓定性=可克隆运行的体系镜像，但"能跑"不等于"跑出同一个东西"。
> 异机各按各的理解调参/重建，产出必然异质。本契约把"球门冻结"纪律延伸到分发侧：
> **任何电脑按本契约执行，检索层产出必须逐位同质；不按契约的产出，本仓不认。**

## G1 环境锁
- 依赖一律 `pip install -r requirements.repro.txt`（精确版本，torch 用 CPU 索引即可）。
- 嵌入模型固定 `BAAI/bge-large-en-v1.5`（1024 维，normalize_embeddings=True）；本仓不含权重。
- Python 3.11+；检索判据以 G3 实跑为准，不承诺任意环境"看起来差不多"。

## G2 数据锁（唯一正式语料通道）
- **复现用途 = 只认 Release 预置件**：`v2.4.2-rag-assets`（fp16-slim 派生件，2 卷+sha）。
  下载→`cat` 拼接→`sha256sum -c` 通过→解包。哈希不过=不解。
- fp16-slim 是**派生发布件**：与冻结原件（fp32）的关系与逐位全等证明见件内 `manifest.yaml` / `conversion_note.json` / `SLIM_VERIFY.json`。
- 按 papers.jsonl 的"全量重建"路径（RAG_REBUILD.md §2）= **探索性行为**：切片/embedding 环境敏感，不承诺逐位一致，**其产出一律不得作为复现结果、不得回流本仓锚点**。

## G3 验收门（同质与否，一条命令回答）
```
python tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim
```
- 判据：41 例 top5 PMID 与 `tests/REPRO_EXPECTED.json` **逐位全等**，PASS=本机与锚点同分布。
- 锚点出身：v2.4.2 fp32 原件经三层验证（数据层列全等 / runner 锚对 官方黄金 41/41 / slim-vs-fp32 top5 逐位全等、top1 相似度漂移 0.0）后由 slim 库直出落档（见 docs/plans/release_slim_v242/）。

## G4 批注管线逐字节锚（clone 可执行，2026-10-01 改版）
背景：stage_a 的邻域/QC 计算含 BLAS 浮点归约，不固定线程数时同一输入可产生不同簇数（上游确证：scanpy #2956、numpy #29933）。`pipeline/run_pipeline.py` 入口默认钉线程（`OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_NUM_THREADS=1`，`setdefault` 保留显式覆盖）。**复现用途 = 不要覆盖这些变量。**

一条命令验收（依赖按 G1 装好、语料按 G2 解包后）：
```
python tests/verify_pipeline.py
```

### G4.1 解释器 = 契约的一部分（KB10d，2026-10-01 立）

**本门驱动管线所用的解释器钉在 `pipeline_env`，不继承调用方 `sys.executable`**——这是 G4 判据
成立的前提，不是可选项。旧版靠继承解释器：同一命令在 terminal / systemd-run scope / 另一 venv
里起手会落到不同的库栈上，同代码同 fixture 产出不同字节 ⇒ 跨环境必假 FAIL。

| 项 | 值 |
|---|---|
| 钉的解释器（生成锚的那个） | `/home/ubuntu/.conda/envs/pipeline_env/bin/python` |
| 覆盖口（唯一回退） | `EYEKB_G4_PY=<python 路径>`；非默认解释器会打印 `[g4] 注意:` 提示 |
| 钉的解释器缺失/不可执行 | `rc=2` + `ENV ERROR`（含修法），**不静默回退到当前解释器** |
| 门脚本自身 | 仅用标准库，可由任意 `python3`（3.10+）启动 |
| 每次运行 | 打印 `[g4] 解释器: <路径> (python X.Y, 来源: …)`，作为差异报告的必要附件 |

对解释器敏感的原因：`stage_a/processed.h5ad` 的字节取决于 anndata/numpy/scipy/sklearn 的
float32 写入路径。实测三栈三值（`obs`/`leiden`/counts 层全同，差异集中在
`X_pca`/`X_umap`/`var`/`dispersions` 的末位）：

| 解释器栈 | python / scanpy / anndata / numpy / scipy / sklearn | `stage_a/processed.h5ad` sha256 |
|---|---|---|
| **pipeline_env（=锚所在）** | 3.10.20 / 1.11.5 / 0.11.4 / 2.2.6 / 1.15.3 / 1.7.2 | `dbc657fa…` ✅ 锚 |
| training-venv | 3.14.4 / 1.12.2 / 0.12.19 / 2.4.6 / 1.16.3 / 1.9.0 | `f7a461f9…` |
| 离线 venv / scrnaseq | 3.14.4–3.12 / 1.12.2–1.12.1 / 0.13.2 / 2.4.6 / 1.16.3 / 1.9.0 | `10cfbe…` |

⇒ 外机两条路：①装等价批注栈后 `EYEKB_G4_PY=/path/to/python` 指过去（**非默认解释器的差异，
除非同时命中锚，否则不算新发现**）；②提交差异报告时**必须**附门打印的 `[g4] 解释器:` 行——
缺该行的差异报告无法判读：维护者无法区分"栈不对"与"真发现"。

G4 FAIL 排查顺序（与 §4 同纪律：先查环境，禁改判据凑数）：
1. 看 `[g4] 解释器:` 行 = 不是 `pipeline_env` → **环境问题，不是判据问题**，按 G4.1 修环境重跑；
2. fixture sha 未命中 → 仓库内容漂移（对照 `G4_EXPECTED.json:fixture_sha256`）；
3. `ENV ERROR: run_pipeline rc≠0` → 批注栈依赖缺失，按本文件顶部补装；
4. 上面三条都干净仍 FAIL = 真发现：带三件 `got/expected` **+ 解释器行**回报维护者，
   不要自行重锚 expected、不要改 `--seed`、不要换 fixture。

判据 = `tests/G4_EXPECTED.json` 三件锚：`stage_a/processed.h5ad` 与 `decisions_template.csv` 原始字节锚；`annotation_evidence_report.md` 先做时间戳/输出路径归一化再取 sha（报告含运行时刻，原始字节锚不可能是稳定判据——此为设计教训，v1 版锚含报告原始字节，作废）。输入 fixture = 公开 GEO 系列（GSE165784）矩阵抽样的 600 细胞子集（`pipeline/fixtures/`，无患者字段，来源注记见其 README）。

锚点出身：2026-10-01 三跑一致（生产 fp32 默认库 ×2、Release slim 库 ×1，逐字节/归一化两级全等后落档）。S0 门所需资产 `pipeline/assets/s0/species_assets.pkl` 已随仓分发（外机实测发现缺失后补入；可由 `assets/s0/build_assets.py` 从公开的 NCBI orthologs/gene_info 重建）。

历史：v1（2026-10-01 上午）为维护者侧三件 sha 锚，同日外部可用性自查发现两个真实缺陷——①clone 缺 S0 资产无法运行、②报告件含时间戳不可作字节锚——现版为修复后重锚；09-30 换锚前件（`19bf2ecb…`）属默认库切换与 S0 接线前的代码状态，归档于 `plans/wire_p1_20260930/out/baseline1/`，不再作判据。

## §4 FAIL 的三层排查顺序（禁改判据凑数）
1. G2：预置件 sha 是否对上（最常见：拿错件/拼接顺序错）；
2. G1：依赖版本是否按锁装（torch/sentence-transformers 漂移）；
3. 模型是否官方 bge-large-en-v1.5。
仍 FAIL = 真发现，请带逐例差异回报维护者，不要自行调参、改 top_k、换模型或重锚 expected。

## §5 变更纪律
- expected 锚与 requirements 锁的更新=维护者侧带证据动作（需三层验证重跑+版本号+日期），克隆者无权自改。
- 服务/引擎代码若版本变更，README 版本注记与本契约同 commit 更新。
