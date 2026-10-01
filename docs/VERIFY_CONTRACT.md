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
