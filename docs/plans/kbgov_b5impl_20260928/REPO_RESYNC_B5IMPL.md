# REPO_RESYNC_B5IMPL — 仓面同步登记件（本卡零 push）

- 卡：t_8960c7e0 ｜ 日期=2026-09-28 ｜ 依据：BRIEF_B5IMPL 纪律"仓面零 push，REPO_RESYNC_B5IMPL.md 登记"
- 仓面 `/home/ubuntu/EYEKB_REPO` 本卡未动、未 push。待 REPOSYNC3 收编的线上增量=

## 待同步清单（mcp_server 面，3 件）

| 文件 | 线上 sha256(前12) | 仓面现 sha(前12) | 增量内容 |
|---|---|---|---|
| mcp_server/eyekb_core.py | aae705453aaa | 1988685b36a6 | KBGOV-B5 治理层（+gzip/re import、_kbgov_b5_enabled/_kbgov_vocab/_kbgov_g1_tier/_kbgov_govern_genes_resp、genes-mode raw_gl 重构+治理分支）；注意仓面该件自 REPOSYNC2 起即含既有脱敏 diff，B5 增量应叠加而非整件覆盖 |
| mcp_server/server.py | 605de72a8bb1 | b28a23e37237 | version 0.5-k9reg→0.6-kbgov5 + description/query_marker docstring B5 段 |
| mcp_server/kbgov_vocab.json.gz | 9b504a2e7cdc | （缺） | KBGOV 冻结词表逐字节副本（1,000,201 B），随码分发；入仓需过脱敏引擎（纯基因符号集，预期零命中） |

未动面：kb/、evals/、tests/、clients/ 仓面零变化；calllog.py/softflags.py 本卡未改（calllog 仓==线上 840b0e9189a3；softflags 差异=REPOSYNC2 在案 PRIOR_DESENS c4a8f53 项，非本卡）。

## 同步时应带上（plans 面）

- plans/kbgov_b5impl_20260928/ 全目录（BRIEF+本件+B5IMPL_COMPLETED.md+scripts/out/ledgers/logs）——KBGOV_CANDIDATE/PREREG 已在仓（REPOSYNC2 已收 32 件），本卡为其执行波，证据链应同树可溯。
- README 版本注记行：server=KB1v2-0.6-kbgov5（追加五队列① 实装，env EYEKB_KBGOV_B5 默认 ON，A5 回退自证=out/B5IMPL_A5_ROLLBACK.tsv）。
- 连带提示：并行卡 t_e0f94d4f（H1M3，队列②）已产 ANNOTATION_PROTOCOL_v1.3.md（plans 根），REPOSYNC3 一并收录；本卡与彼卡领地互斥已实证（门5 归因表）。

*B5IMPL t_8960c7e0 登记，执行权在 REPOSYNC3 协调线。*
