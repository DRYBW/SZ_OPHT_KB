# GATES — PIPELINE 卡六门验收记录（2026-09-29 实测）

任务书：`BRIEF_PIPELINE.md`（本目录，sha256=12535eee…46fb4，与 /mnt/D/EyeKB/plans/pipeline_pub_20260929/ 原件逐字节全等）。
全部命令在 staging 仓根目录执行；解释器 = `/home/ubuntu/training-venv/bin/python`
（Python 3.14.4，scanpy 1.12.2 / harmonypy 2.0.0 / scrublet 0.2.3 / mcp 2.0.0，与 `pipeline/requirements.txt` 锁一致）。

## T1 冒烟端到端 — PASS

输入构造：`make_smoke_fixture.py`（从盘上冻结卷 `/mnt/D/EyeKB/plans/demo_gse165784/proc/00_merged_raw.h5ad`
取 RRD-ERM1 与 PDR-ERM-210630 各 1000 细胞，seed=20260929，共 2000 细胞 ≤ 上限；源卷只读）
→ `fixtures/smoke.h5ad`（两形态之一）+ `fixtures/10x_both/RRD-ERM1/`+`PDR-ERM-210630/`（三件套）
+ `fixtures/smoke_ensg.h5ad`（真实场景变体：输入只有 Ensembl ID）。

| 形态 | 命令 | rc | 结果 |
|---|---|---|---|
| T1a h5ad | `run_pipeline.py --input fixtures/smoke.h5ad --species human --tissue fibrovascular_membrane --group-col disease --out out/smoke_h5ad` | 0 | 14 簇；三件报告齐；五字段逐簇非空；文献结果 93 条带 PMID；分级 11 consistent / 3 mixed（触发规则逐条在报告内） |
| T1b 10X 三件套（2 样本） | `run_pipeline.py --input fixtures/10x_both --species human --tissue fibrovascular_membrane --sample-group "RRD-ERM1=control;PDR-ERM-210630=PDR" --disease PDR --out out/smoke_10x` | 0 | 14 簇；同上断言全过（96 条带 PMID）；疾病先验启用（条目 PDR__fibrovascular_membrane） |
| T1c ENSG 未映射（弃权路径证明） | 同 T1a，输入 `smoke_ensg.h5ad` → `out/smoke_degraded` | 0 | 15 簇全部 needs_review（规则 `no_named_marker_candidates`/`no_literature_results` 诚实触发）；decisions_template.csv 出现 `ABSTAIN(no candidate)` 行且裁决列全空 |
| T1d --ensg-map 恢复 | 同 T1c 加 `--ensg-map`（ENSG↔SYMBOL 两列 TSV，40609 行）→ `out/smoke_ensgmap` | 0 | symbol_source=ensg-map；分级回到与 T1a 同分布（11/3）——映射缺失是弃权根因，给图即恢复 |

弃权路径说明：T1a/T1b 数据符号干净、天然无 needs_review 簇；"弃权路径通"以 T1c
（真实可发生的 ENSG 未映射输入，15/15 needs_review）实证，不向干净数据注水。
五字段断言/三件套齐/裁决列空的机读核对输出：`logs/T1_assertions.txt`。

## T2 黄金 41 不变 — PASS

`python tests/verify_repro.py --db-dir /home/ubuntu/RAG_SLIM_V242/literature_db/v2.4.2_2026-09_slim`
→ `REPRO PASS: 41/41 例 top5 逐位全等`（rc=0，日志 `logs/T2_golden41.log`）。
本次新增代码不在检索路径上（pipeline 是消费方），41/41 证明零漂移。

## T3 密钥扫描零真实值 + 生产盘零侵入 — PASS（附一项如实登记）

- `grep -rnE 'github_pat|ghp_|sk-[A-Za-z0-9]|Bearer ' pipeline/` → 唯一命中
  `pipeline/llm_assist.py:77` 的 `f"Bearer {key}"`（运行时从环境变量取值的代码模板，
  非真实值；仓内零真实 key/URL）。README 新增段扫描 = 0。提交前已删
  `pipeline/__pycache__/`。
- 生产盘 `/mnt/D/EyeKB/kb` + `mcp_server` 全量 sha256 台账（125 件）前后全等：
  `T3_sha_PRE.txt` = `T3_sha_POST.txt`（逐行 diff 空）。
- **如实登记（附带作用）**：阶段 B 按任务书要求 stdio 拉起仓内 `mcp_server/server.py`，
  其自带的 `calllog.py` 服务端留痕层把调用轨迹**追加**写入
  `/mnt/D/EyeKB/logs/mcp_trace/calls_2026-09-29.jsonl`（该文件本次新增约 230 行，
  追加式、不改不删任何既有行；日志目录不在 T3 台账范围内）。这是随仓代码的固有行为
  （生产环境历次评测运行同样如此），mcp_server/ 禁改故本卡未动；公开机上该路径不存在，
  calllog 自带 try/except 兜底不影响服务。建议后续卡给 TRACE_DIR 加 env 覆盖。

## T4 零 LLM 默认 — PASS

- 上表 T1a/T1b 全部在 `env -u OPENAI_API_KEY -u OPENAI_BASE_URL -u OPENAI_MODEL` 下完成。
- 强化断网语义：`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 https_proxy=http://127.0.0.1:9
  HTTP_PROXY=http://127.0.0.1:9` + 无 API 变量，全流程照跑完（`out/T4_offline`，rc=0，
  分级与 T1a 同分布 11/3，日志 `logs/T4_offline.log`）。
- `--llm-assist` 双向降级实测（`logs/T4_llm_assist_microtest.txt`）：无 key → 报告注明
  未启用照跑；有 key 但通道不可达 → 每簇落"[LLM 辅助不可用]"，主流程零异常。

## T5 README — PASS

- 仓根 README 新增《批量注释（pipeline/）》一节：三行命令（h5ad / 10X 三件套 / ENSG 映射）
  + 输入要求回链《输入与输出》+ 弃权声明（"弃权是合法输出，本入口不把存疑结果写成确定标签"）；
  《知识库的组织结构》表补"批量入口层 pipeline/"行。
- `pipeline/README.md`：用法、产出表、三条纪律、B5 跨物种提示、依赖、已知边界。
- 黑话扫描：`grep -nE '拍板|派卡|波次|收口|判读卡'` 于 README 新增段与 pipeline/ 全部文件
  新增文本 = 0 命中。

## T6 中间产物全保留 — PASS（数据件按仓规不入库）

- 保留在盘（本目录）：脚本（pipeline/ 4 件 + make_smoke_fixture.py）、全部运行日志
  （logs/）、四组冒烟输出（out/：报告 json/md/csv、mcp_calls.jsonl、stage_a 指标与
  质控图 PNG）、T3 台账两件、本验收记录。零删除。
- 入库边界：`fixtures/*.h5ad`（43MB 病人来源子集）与 `out/*/stage_a/processed.h5ad` 按仓
  `.gitignore` 既有规则（`*.h5ad` 病人衍生数据永不入库）不 commit、只留盘——与 T6
  ".gitignore 只排除 >50MB 数据件"的字面差异，取隐私红线优先（任务书禁改 .gitignore 所在
  仓根策略文件），登记于此供协调者复核；`10x_both/*matrix.mtx` 同理不 add（路径排除法，
  未改 .gitignore）。证据链的文本件（json/md/csv/png/log/tsv）全部入库。

## 执行中修复（试跑产物保留）

| 发现 | 修复 |
|---|---|
| numpy 2.4 无 `np.cpu_count` | 改 `os.cpu_count` |
| pandas Index 无 `.str` 链式 `.values` | 线粒体判定改 Series 构造 |
| `sc.read_mtx` 返回 AnnData 非矩阵 | 三件套读取改 `scipy.io.mmread` + csc.T |
| 跨样本重复 barcode 致 scrublet 重排爆炸（真实场景，同 GSE183320 127 例教训） | 装载后 `obs_names_make_unique` 并记日志 |
| ENSG 判定只扫 var 轴头部 2000 项，被字母序前段的基因座符号系统性低估 | 改全轴均匀抽样 |
| `Index.map().fillna(Index)` TypeError | 符号映射改 Series 实现 |
| 疾病先验缓存定义在 async 闭包内致 NameError | 缓存提升外层作用域，闭包内 clear+填充 |
