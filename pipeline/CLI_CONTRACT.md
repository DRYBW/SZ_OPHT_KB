# pipeline/run_pipeline.py — CLI 契约 v1

**冻结日期**：2026-10-13 ｜ **卡片**：`t_3a420805`（融合·共同前置：补 5 处入口缺口）
**来源口径**：本文件**逐条**取自 `pipeline/run_pipeline.py` 的 `argparse` 定义、`main()` 返回码与文件写入点，
以及 `pipeline/README.md` 的输出表；**非设计稿、非预期语义**——每一条都能在源码行内复核。
**性质**：README 级契约文档（新增，不修改任何算法、不改变任何既有产物）。封装（paper2mcp / MCP 工具化）前
以本契约为调用面。

---

## 0. 范围

- 单一入口：`pipeline/run_pipeline.py`（Stage S0 影子预检 + Stage A 标准处理 + Stage B 逐簇证据收集）。
- 默认**零 LLM**、**不做自动判分/自动定名**；弃权（`needs_review` / abstain）是合法输出。
- 本契约只描述**调用面**（入参 / 出参 / 退出码 / 环境开关），不描述算法内部。

## 1. 调用形态

```bash
# 形式 1：.h5ad（X = 原始 counts）
python pipeline/run_pipeline.py --input data.h5ad --species human --tissue retina \
    --group-col treatment --out results/run1

# 形式 2：10X 三件套目录（目录本身=1 样本；含多个三件套子目录的父目录=多样本）
python pipeline/run_pipeline.py --input 10x_dir/ --species human --tissue retina \
    --sample-group "S1=control;S2=case" --out results/run2

# 形式 3：不给物种/组织 —— 由 S0 预检判定并回填（默认行为）
python pipeline/run_pipeline.py --input data.h5ad --out results/run4

# 形式 4：只有 Ensembl ID 无 symbol 列
python pipeline/run_pipeline.py --input data.h5ad --species human --tissue retina \
    --ensg-map ensg2symbol.tsv --out results/run3

# 自描述：打印已知组织字典后退出（rc=0）
python pipeline/run_pipeline.py --list-tissues

# 查看参数帮助（argparse 标准行为，rc=0）
python pipeline/run_pipeline.py --help
```

- `cwd`：仓库根（脚本内 `REPO_ROOT = <script>/..` 自解析，故 `--input/--out` 相对路径按**当前 cwd** 解析）。
- 解释器锚点（G4 门钉死）：`/home/ubuntu/.conda/envs/pipeline_env/bin/python`（python 3.10.20 / scanpy 1.11.5 / anndata 0.11.4 / numpy 2.2.6 / scipy 1.15.3 / sklearn 1.7.2）。

## 2. 入参全表（逐条对 `ap.add_argument`）

| 参数 | 类型/取值 | 默认 | 必填 | 语义（源码口径） |
|---|---|---|---|---|
| `--input` | 路径 | — | **是** | 10X 三件套目录 / 含多个三件套子目录的父目录 / `.h5ad` |
| `--species` | `human`\|`mouse`\|`auto` | `auto` | 否 | `auto`=S0 判定并回填；**显式给定=人工覆盖**，记入 `s0_gate_report.json` 的 `s0_overridden_by_user`（回滚态下必填） |
| `--tissue` | 字典名 \| `auto` | `auto` | 否 | 同上；非字典名只 warn（`stderr`）不阻断 |
| `--out` | 路径 | — | **是** | 输出目录（不存在则创建） |
| `--sample-col` | 字符串 | `""` | 否 | h5ad 样本列；缺省回退 `obs.sample` / 输入名 |
| `--sample-group`（别名 `--group-col`） | 字符串 | `""` | 否 | h5ad 列名；三件套输入用 `sample=group;...` 映射。**给了才激活疾病先验比对** |
| `--disease` | 字符串 | `""` | 否 | 配合分组使用；默认查询非对照组标签 |
| `--gene-symbol-col` | 字符串 | `""` | 否 | 符号列指定 |
| `--ensg-map` | 路径 | `""` | 否 | `ENSG<TAB>SYMBOL` 两列 TSV |
| `--resolution` | float | `1.0` | 否 | Leiden 分辨率 |
| `--min-genes` | int | `200` | 否 | QC 基因数下限 |
| `--max-pct-mt` | float | `20.0` | 否 | 线粒体百分比上限 |
| `--top-genes-n` | int | `10` | 否 | 证据报告 top 基因数 |
| `--seed` | int | `20260929` | 否 | 随机种子（确定性锚） |
| `--no-scrublet` | flag | off | 否 | 关闭双细胞检测 |
| `--no-harmony` | flag | off | 否 | 关闭 Harmony 批次校正 |
| `--s0-thr` | 路径(json) | `None` | 否 | S0 阈值覆盖（敏感性扫描用；缺省用硬编码阈值） |
| `--volume-counts` | 路径(json) | `""` | 否 | `{类标签: 全片细胞数}` → Stage B 体量合理性闸（不给则惰性） |
| `--llm-assist` | flag | off | 否 | **可选**：调用户自备通道生成证据摘要草稿；默认关闭、不影响判级 |
| `--list-tissues` | flag | off | 否 | 打印已知组织字典并 `return 0` |

> 说明：`--sample-group` 与 `--group-col` 是同一 `dest=group_col` 的两个名字（源码两行 `add_argument`）。

## 3. 出参全表（全部落在 `--out` 下）

| 路径 | 内容 | 出现条件 |
|---|---|---|
| `stage_a/processed.h5ad` | QC/归一化/批次校正(Harmony 标记)/leiden 后的矩阵 | 常态 |
| `stage_a/figures/*.png` | QC 图组（mt%、检出基因数、双细胞、校正前后 UMAP） | 常态 |
| `stage_a/cluster_markers.csv` | 逐簇 wilcoxon top30 | 常态 |
| `annotation_evidence_report.json` | 逐簇五字段证据（结构=接线前契约；不含 known-issues） | 常态 |
| `annotation_evidence_report.md` | 证据报告（S0 开启时头部附「适用 claim 清单」） | 常态 |
| `decisions_template.csv` | 每簇一行待人裁决（`decision`/`proposed_label` **留空**；S0 开启时追加 `pitfall_risk_flags`/`pitfall_review_required` 两列） | 常态 |
| `mcp_calls.jsonl` | 证据服务调用审计（工具/入参/成败/耗时） | 常态 |
| `run_summary.json` | 运行摘要（`out`/`secs`/`n_clusters`/`grades`/`next_step`，S0 开启时附 `s0` 与 `pitfalls_shadow`） | 常态 |
| `s0_gate_report.json` | S0 三通道读数 + 闸门理由 + 全排序 + 覆盖审计（`mode`=shadow/enforce） | S0 开启时 |
| `REPORT_ABSTAIN.md` | 弃权记录（人影：记录性产物，**不阻断**） | 仅弃权时 |
| `shadow_attention.json` / `shadow_flags.jsonl` | 适用 claim 清单 / 逐簇风险旗标审计（自动改类计数恒为 0） | S0 开启且存在适用 claim 时 |

**stdout**：最后一行 `[pipeline] DONE {run_summary.json 全文}`；S0 开启时另有 `[run_pipeline] S0 call: ...` 首行。
**stderr**：`[run_pipeline]`/`[warn]` 前缀的诊断行。

## 4. 退出码契约（对 `main()` 的 `return`）

| 码 | 触发条件（源码） | 语义 |
|---|---|---|
| `0` | 正常跑完（含 `--list-tissues`、`--help`） | 成功 |
| `2` | `EYEKB_S0_GATE=0`（回滚态）且 `--species` 或 `--tissue` 仍为 `auto` | 回滚态要求显式参数（legacy 强制参数语义） |
| `3` | `EYEKB_S0_ENFORCE=1`（Phase-3 前向开关）且 S0 abstain | 硬闸阻断，管线停止（见 `REPORT_ABSTAIN.md`） |
| `4` | 影子态 abstain **且** 物种/组织无法从人工参数解析 | 缺参退出（**不是硬闸阻断**） |

> ⚠️ **已知歧义（如实记录，未改）**：`2` 同时是 `argparse` 用法错误的退出码。区分方式 = 看 `stderr`：
> 回滚态会打印 `[run_pipeline] EYEKB_S0_GATE=0 (rollback state) requires explicit --species and --tissue`，
> 用法错误则是 `usage: run_pipeline.py ...`。封装时不建议只按码分流，必须并读 stderr。

## 5. 环境开关

| 变量 | 取值 | 默认 | 作用 |
|---|---|---|---|
| `EYEKB_S0_GATE` | `0/false/off/no` | `1`（开） | `0`=回滚态：关闭 S0 与旗标，`--species/--tissue` 必填，用于隔空基线比对与应急 |
| `EYEKB_S0_ENFORCE` | `1/true/on/yes` | 空（关） | `1`=Phase-3 前向开关，S0 abstain 变为硬闸阻断（rc=3） |
| `EYEKB_KB9_CONSUME_GUARD` | 见 `pipeline/kb9_slot_guard.py` | — | 消费侧窄护栏（KB9 降格），不改切片深度 |
| `EYEKB_STATE_GUARD` | `0/false/off/no` | 开 | 关闭 Stage B 体量合理性闸（`--volume-counts` 惰性下无效果） |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` | — | — | 仅 `--llm-assist` 时读取的用户自备通道 |
| `OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_MAXIMUM_THREADS` | — | 脚本内 `setdefault("1")` | **确定性钉**（ERRATA-E3）：不钉则同输入簇数 16/15/16 抖动 |

## 6. 确定性 / 幂等

- 脚本顶部 `os.environ.setdefault(...)=1` 钉死 5 个线程变量 → 实测同输入两跑 `processed.h5ad` sha 一致；显式覆盖仍生效（复现契约=保留默认钉）。
- `--seed` 默认 `20260929`；单线程 wall time ≈ 多线程（Stage A 串行实现，实测 ~110 s），故确定性优先。
- 写入面**只在 `--out` 内**（`mkdir(parents=True, exist_ok=True)`）；对既有目录重复运行会**覆盖同名产物** → 复算请给新 `--out`。

## 7. 真跑证据（本契约实测，2026-10-13）

见同目录 `CLI_CONTRACT_EVIDENCE_t_3a420805.md`（命令 + 退出码 + 输出首行，逐条）。要点：
固定夹具 `pipeline/fixtures/pdr600.h5ad`（600 cells × 23,441 genes 整数 raw counts，sha256 `fa8fc609…ce44`）全链实跑一次，rc=0。

| 实测 | 命令 | rc | 输出首行 |
|---|---|---|---|
| 全链（默认 auto） | `run_pipeline.py --input pipeline/fixtures/pdr600.h5ad --out /tmp/t_3a420805_eyekb_run1` | 0 | `[pipeline] DONE {"out": ..., "secs": 55.8, "n_clusters": 11, ...}` |
| 全链（显式 species/tissue，GATES T1a 形态） | `run_pipeline.py --input .../pdr600.h5ad --species human --tissue fibrovascular_membrane --out /tmp/t_3a420805_eyekb_run2` | 0 | `[pipeline] DONE {... "n_clusters": 11 ...}` |
| 回滚态缺参 | `EYEKB_S0_GATE=0 run_pipeline.py --input ... --out /tmp/t_3a420805_eyekb_rc2` | 2 | `[run_pipeline] EYEKB_S0_GATE=0 (rollback state) requires explicit --species and --tissue ...` |
| 自描述 | `run_pipeline.py --list-tissues` | 0 | `RPE`（共 15 行；**本卡修复前为 rc=2**，见 §9） |
| 帮助 | `run_pipeline.py --help` | 0 | `usage: run_pipeline.py [-h] [--input INPUT] ...` |

两次全链运行 `stage_a/processed.h5ad` sha256 逐字节相同（`dbc657fa2bc4a9cce1060c72aa96a58d278f794612b6bb7cff81bad27f3ef7a5`），
且簇数与分级完全一致（11 簇 / consistent 2 / mixed 7 / needs_review 2）→ 确定性钉有效、入口改动无回归。

## 8. 未覆盖 / 边界（封装前的诚实清单）

1. `--input` 的 10X 父目录多子目录路径本次未实跑（夹具为 h5ad）；语义取自源码 `s0_check.gate_from_input` 的 `input_kind` 分支。
2. 回滚态（`EYEKB_S0_GATE=0`）与 enforce 态（rc=3）本次只实测了 rc=2 分支；rc=3 需构造 abstain 输入，未测。
3. `--volume-counts` 闸门惰性路径未测（需外部全片计数表）。
4. `--llm-assist` 未测（需自备 key；默认关闭）。

## 9. 本次修复的入口缺陷（实录，2026-10-13，卡 t_3a420805）

**缺陷**：`--list-tissues`（自描述/枚举组织字典）**不可达**。
`--input` / `--out` 原为 `required=True`，`argparse` 在 `parse_args()` 内即报错退出（rc=2、usage 走 stderr），
`if a.list_tissues: ... return 0` 分支永远求值不到。而 `pipeline/README.md` 与
`docs/plans/pipeline_pub_20260929/PIPELINE_COMPLETED.md` 都把该开关写作可用 —— **文档与实现不一致**。
实测（改前）：`python pipeline/run_pipeline.py --list-tissues` → `rc=2` + `usage: run_pipeline.py ...`。

**修复**（仅入参层，算法/产物口径/任何计算路径零改动）：
`--input` / `--out` 改 `required=False`，并在 `--list-tissues` 分支**之后**、`--out` 首次使用之前，
用 `ap.error("the following arguments are required: --input|--out")` 原样恢复旧语义
（`ap.error` 同样打印 usage 并退出 2 → 缺参行为逐字保持）。

**改后实测**：

| 命令 | 改前 | 改后 |
|---|---|---|
| `--list-tissues` | rc=2 + usage | **rc=0 + 15 行组织字典**（首行 `RPE`） |
| 给 `--out` 但不给 `--input` | rc=2 + usage | rc=2 + usage（**不变**） |
| 给 `--input` 但不给 `--out` | rc=2 + usage | rc=2 + `error: the following arguments are required: --out`（**不变**） |
| 全链夹具跑 | rc=0，11 簇 | rc=0，11 簇，`processed.h5ad` sha 相同（**无回归**） |

**已知残留**（未改，如实记录）：rc=`2` 同时承担「回滚态缺参」与「argparse 用法错误」两种语义，
调用方不能只按码分流，必须并读 stderr（见 §4 ⚠️）。

