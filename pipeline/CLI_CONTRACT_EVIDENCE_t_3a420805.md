# pipeline/run_pipeline.py — CLI 契约实测证据（卡 t_3a420805，2026-10-13）

配套 `CLI_CONTRACT.md`（§7 引用本文件）。全部为本次**真实执行**；解释器
`/home/ubuntu/.conda/envs/pipeline_env/bin/python`（G4 门钉死）；cwd = 仓库根。

夹具：`pipeline/fixtures/pdr600.h5ad` —— 600 cells × 23,441 genes 整数 raw counts，
sha256 `fa8fc609c3920dd2506a7b81fafe5a6e363b98eb670ee523a3f411d5c913ce44`（见 `fixtures/README.md`）。

| 命令 | rc | 输出首行 |
|---|---|---|
| `python pipeline/run_pipeline.py --input pipeline/fixtures/pdr600.h5ad --out /tmp/t_3a420805_eyekb_run1` | 0 | `[pipeline] DONE {"out": "/tmp/t_3a420805_eyekb_run1", "secs": 55.8, "n_clusters": 11, "grades": {"mixed_or_insufficient": 7, "needs_review": 2, "evidence_consistent": 2}, ... "s0": {"species": "human", "tissue": "fibrovascular_membrane", "confidence": 1.0, "abstain": false, "mode": "shadow", "overridden_by_user": false}}` |
| `python pipeline/run_pipeline.py --input …/pdr600.h5ad --species human --tissue fibrovascular_membrane --out /tmp/t_3a420805_eyekb_run2` | 0 | `[pipeline] DONE {"out": "/tmp/t_3a420805_eyekb_run2", "secs": 58.5, "n_clusters": 11, ...}` |
| `EYEKB_S0_GATE=0 python pipeline/run_pipeline.py --input …/pdr600.h5ad --out /tmp/t_3a420805_eyekb_rc2` | 2 | `[run_pipeline] EYEKB_S0_GATE=0 (rollback state) requires explicit --species and --tissue (legacy mandatory-argument semantics).` |
| `python pipeline/run_pipeline.py --list-tissues`（**本卡修复后**） | 0 | `RPE`（共 15 行；改前 rc=2 + usage，见 `CLI_CONTRACT.md` §9） |
| `python pipeline/run_pipeline.py --help` | 0 | `usage: run_pipeline.py [-h] [--input INPUT] [--species {human,mouse,auto}] ...` |
| `python pipeline/run_pipeline.py --out /tmp/x`（缺 `--input`） | 2 | `usage: run_pipeline.py [-h] [--input INPUT] ...` + `error: the following arguments are required: --input` |
| `python pipeline/run_pipeline.py --input f.h5ad`（缺 `--out`） | 2 | `error: the following arguments are required: --out` |

## 确定性与无回归

两次全链运行（run1=默认 auto；run2=显式参数）的 `stage_a/processed.h5ad`：

```
dbc657fa2bc4a9cce1060c72aa96a58d278f794612b6bb7cff81bad27f3ef7a5  /tmp/t_3a420805_eyekb_run1/stage_a/processed.h5ad
dbc657fa2bc4a9cce1060c72aa96a58d278f794612b6bb7cff81bad27f3ef7a5  /tmp/t_3a420805_eyekb_run2/stage_a/processed.h5ad
```

逐字节相同；簇数（11）与分级分布（2/7/2）一致 → 线程确定性钉有效，**入口改动无回归**。
`run1` 产物 18 个文件，与契约 §3 的出参表逐条对上（含 `s0_gate_report.json`、`shadow_attention.json`、
`shadow_flags.jsonl`、`decisions_template.csv`、`mcp_calls.jsonl` 等）。

## 原始 transcript 位置

`/home/ubuntu/Desktop/Hermes工作区/pi-bioinfo/kanban产出/t_3a420805_融合共同前置/evidence/`
（`eyekb_run1.log`、`eyekb_rc2.log`、`eyekb_AFTER_*.log`、`item*_evidence_transcript.txt` 等），
可复算脚本同目录上一级 `run_item4_evidence.sh` / `run_item5_evidence.sh` 等。
