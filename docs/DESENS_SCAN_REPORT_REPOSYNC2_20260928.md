# 脱敏双扫描报告 — REPOSYNC2（09-28 改进波收录面）

生成卡：t_719dd225（REPOSYNC2）。规则三元组 = project-github-export 现行清单 + 09-27 新增面，本轮**未新增规则**，但**新增 CJK 边界强化词形复核**（见"边界补强"节）。
纪律沿用 09-27 版：本报告不复现任何渠道商名/裁决商名/端点串/邮箱字面——规则一律以代号指称（对照表 = `docs/plans/repo_sync2_20260928/scripts/DESENS_RULES_codename.md`）。

## 扫描面

- 本波新收：`docs/plans/{kbx_lacrimal_20260928, kb_chain_audit_20260928, rag_fix_20260928, rag_fix2_v25_20260928, kb_gov_20260928, rag_gap_20260928, grade_anchor_20260928, retrain_assess_20260928, repo_sync2_20260928}` 共 768 件（记录表 `docs/recon/REPOSYNC2_INTAKE.sha256`）
- `docs/wiki/`（15 件，含新收 USER_DIRECTIVE_20260928 指令件）
- `docs/skills/`（两技能镜像随动刷新）
- `mcp_server/`（零变动面，双扫复核）
- 排除面（字节镜像策略，不脱敏）：`kb/`、`clients/`、`scripts/`、`tests/`、`evals/`、`rag_snapshots/`、`figures/` ——其命中按"存量登记不擅动"逐件列于 `docs/plans/repo_sync2_20260928/out/t5_inventory_register.txt`。

## 文件名双扫描

- 改名 3 件（v3 引擎自动）：
  - `rag_fix_20260928/scripts/<R08 词干>_followup_probes.py` → `REVIEWER_LLM_followup_probes.py`
  - `rag_fix_20260928/out/<R08 词干>_GATE3_ADJUDICATION_reply.md` → `REVIEWER_LLM_GATE3_ADJUDICATION_reply.md`
  - `knowledge-guided-cell-annotation/references/2026-09-24-kb2-run-ledger-and-<R04 词干>-channel.md` → `…-and-llm-channel.md`（恢复至仓内既有件名，git 视作同路径内容更新）
- 改名 1 目录（人工，同 09-27"目录不落词干"先例）：`kbx_lacrimal_20260928/<R08 词干>/` → `kbx_lacrimal_20260928/REVIEWER_LLM/`（其内送审件文件名无词干，正文引用同步替换后路径与目录名逐字对应）。

## 规则命中统计（内容替换条数，apply 实录）

| 代号 | 语义 | 命中 |
|---|---|---|
| R13 | 第三方联系邮箱 | 3,704 |
| R04 | 渠道商 A 家族 | 129 |
| R08 | 外部裁决 LLM 别名 | 99 |
| R12 | 内部 agent profile 名 | 23 |
| R09 | IM 平台名 | 7 |
| R06 | 渠道商 C | 3 |
| R01 | 自家样本编号 | 2 |
| R07 | 渠道商 D | 2 |
| R15 | 本地代理端口（仅散文类） | 2 |
| R11 | 本地 LLM 栈名 | 1 |
| R14 | 内部服务端口（仅散文类） | 1 |
| R02/R03/R10/R16 | chat_id/主机名/密钥形态/会话标识 | **0** |

命中文件 355 件；实际内容变更 352 件（改名后内容仍变 2 件重叠计）；数值证据面（tsv/json/jsonl）除 R13/R04/R08/R12 字符串外无任何数值改动；R14/R15 仅散文生效，防破坏可复算数字。

## 边界补强（本文档新增动作）

现行 `\bastra\b` 类词边界在 CJK 邻接处失效（Python `\w` 含汉字），09-27 存量规则存在此盲区。本文档对**全部收录件**用强化词形 `(?<![A-Za-z])<词干>(?![A-Za-z])` 复扫：
- 收录面（docs 新波 + wiki + skills + mcp_server）：除本文档生成前既有件外**命中 0**；
- docs 面唯一非零 = `DESENS_SCAN_REPORT_20260927.md` 自引规则描述 1 处 R04 词面（09-27 存量，登记不改）；
- 策略面存量（kb/scripts/tests，字节镜像）：3,610 处，逐件登记（见上"排除面"指针）。
处置建议（待 PI/项目维护方裁定，非本文档权限）：a) 规则引擎并入强化词形（防未来波复发）；b) 若要求 kb 面也净面，与 T2 逐字节对账纪律冲突，需先裁定镜像策略优先级。
详见 `docs/plans/repo_sync2_20260928/out/t5_final_scan.txt`。

## 冻结哈希锚例外登记（本波镜像内 `sha256sum -c` 预期结果）

| 记录表件 | 预期 | 原因 |
|---|---|---|
| `kb_gov_20260928/KBGOV_PREREG_v1.{0,1}.md.sha256` | **PASS**（2/2） | 预注册件未被任何规则命中 |
| `kb_gov_20260928/SHA_MANIFEST.txt` | 31 OK + 1 行无法重验 | 1 行锚 `__pycache__/*.pyc`（按先例未收；线上原锚有效） |
| `kb_chain_audit_20260928/ledgers/SHA_DELIVERABLES.txt` | 43 OK + 79 行 FAIL-预期 | 目标件被 R13/R04/R08 脱敏（epmc 批次缓存内作者邮箱等） |
| `rag_fix2_v25_20260928/ledgers/SHA_DELIVERABLES_20260928.txt` | 27 OK + 5 行 FAIL-预期 | 同型（含改名件引用行） |
| `rag_fix_20260928/ledgers/SHA_*` 四件 | 全部锚线上绝对路径 | 镜像内不可重验，线上盘完整性为准（沿 09-27 口径） |
| `retrain_assess_20260928/ledgers/SHA_SELF_20260928.txt` | 3 OK + 1 行 FAIL-预期 | 自锚 RETRAIN_VERDICT.md 被 R08 脱敏 |
| `rag_gap_20260928/ledgers/SHA_DELIVERABLES.txt` | 20 OK + 1 行 **上游漂移** | REPORT_RAGGAP.md 线上自身即与记录表不符（ee7b6933… ≠ 42b79838…）——非镜像破坏，见收尾件遗留事项 1 |
| `grade_anchor_20260928/data/SHA_LEDGER_INPUTS.txt` / 各 PRE/POST verify | 全绝对路径 | 线上为准 |

机器可核版明细 = `docs/plans/repo_sync2_20260928/out/t4_ledger_check.txt`。
预注册冻结件 sidecar **未重写**（镜像方无权重写锚，沿 09-27 纪律）。

## 幂等验证

替换后 v3 引擎全规则复扫：**改名 0、规则命中 0、命中文件 0**（机器侧原样输出留存 /tmp，仓内以本文件+out/t5_final_scan.txt 留证）。

## Release 零触碰声明

Release `v2.3-rag-assets` 六件未下载、未上传、未改动；重验仅用本地既有 tar 重切分对 API digest（证据 `docs/plans/repo_sync2_20260928/out/t6_release_reverify.txt`）。
