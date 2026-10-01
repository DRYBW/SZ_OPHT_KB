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

## G4 批注管线逐字节锚（2026-10-01 增补）
背景：管线 stage_a 的邻域/QC 计算含 BLAS 浮点归约。**不固定线程数时，同一输入连跑可产生不同簇数**——上游确证行为：scanpy #2956（维护者声明：跨机器/跨线程数不保证构图可复现）、numpy #29933（浮点归约非结合律，随机种子不覆盖该来源）。本仓 `pipeline/run_pipeline.py` 入口已默认钉线程（`OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_NUM_THREADS=1`，`setdefault` 写法保留显式覆盖；实测无性能代价）。**复现用途 = 不得覆盖这些变量。**
维护者侧锚点（2026-09-30 钉内重生成；修复前产物以 `*_PRE-E3-unpinned_*` 归档留痕）：
| 产物 | sha256 |
|---|---|
| `stage_a/processed.h5ad` | `19bf2ecbc231fba39604c282775ab42a822df163d2e2921dd6c28870722f1f58` |
| `decisions_template.csv` | `1c4a4722036de22b707599c72e8f5e9b908946581f903bf0173508369a9b7dbc` |
| `annotation_evidence_report.md` | `c882781ee707f8d6db56cae2826ed598f69bae3ecd39efe82b21536e9a2d8850` |
适用范围：当前为**维护者侧回归锚**（防管线改动重新引入非确定性）。克隆者侧跑 G4 需附带输入 fixture（h5ad 未随 Release 分发）——是否打包小体积 fixture 属开放项，另行决定后本节升为全量门。

## §4 FAIL 的三层排查顺序（禁改判据凑数）
1. G2：预置件 sha 是否对上（最常见：拿错件/拼接顺序错）；
2. G1：依赖版本是否按锁装（torch/sentence-transformers 漂移）；
3. 模型是否官方 bge-large-en-v1.5。
仍 FAIL = 真发现，请带逐例差异回报维护者，不要自行调参、改 top_k、换模型或重锚 expected。

## §5 变更纪律
- expected 锚与 requirements 锁的更新=维护者侧带证据动作（需三层验证重跑+版本号+日期），克隆者无权自改。
- 服务/引擎代码若版本变更，README 版本注记与本契约同 commit 更新。
