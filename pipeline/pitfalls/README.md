# pipeline/pitfalls — 已知问题（known-issues）结构化消费模块（WIRE-P1 · REV-1=astra 定盘版）

上游原稿（只读、不在仓内改动范围）：`/mnt/D/EyeKB/kb/known_issues/`（六格 59 条，
status=draft_for_PI 的内容层由 KNOWNISSUES-B1 卡维护）。本模块=**原子 claim 契约的
转换与运行时消费层**：原稿不动，产物另放；单一事实源=`build_claims.py`
（改裁决改脚本重跑；`pages/` 与 `MANIFEST.sha256` 是机器产物，不手改）。
本契约取代 2026-09-30 17:3x 的 qwen 代审版四页型契约（GLOBAL 废止，五支树+shadow）。

## 文件

| 件 | 作用 |
|---|---|
| `COORDINATE_TAXONOMY_v0.md` | 词表前置件：物种×组织×assay 受控词表 + 基线面↔设计组织映射 + 缺失登记（"17 面"口径核实=12 组织面+5 元/变体件）。归属以它为准，映射不进词表=UNMAPPED |
| `build_claims.py` | 59 条→原子 claim（一 scope 一 claim）；逐条裁决表+派生规则+机械校验（词表合规/唯一 Home/链接 100% 解析/字段完整性）；`--check`=脚本↔产物互证门 |
| `pages/cells/*.json` | CELL 页（species__tissue）：本格 Home 条目 + 被引指针（pattern/species 覆盖条） |
| `pages/species/*.json`、`pages/tissue/*.json`、`pages/patterns/*.json` | SPECIES/TISSUE/PATTERN 页（五支树；本批 tally：cell 36 / species 1 / tissue 0 / pattern 13 / unmapped 0=50 条入账） |
| `pages/EXCLUSIONS.json` | 不入账登记（9 条：6 盲区声明+3 社区空白——无失效模式/无量纲，不得当 claim） |
| `pages/INDEX.json` | claim 清单 + 各页 sha + **legend**（全部枚举含义，禁裸 A/B/C，历史映射仅存 legend） |
| `consume.py` | 运行时 shadow 消费：按坐标拉页→风险旗标（**无 cap/无 override**）→人类面渲染+审计件 |
| `MANIFEST.sha256` | 产物书面校验 |

## 契约要点（裁决依据：astra 正式审 ROUTER_V0_ASTRa_R1.md + 卡内 REV-1 更正令）

- **原子 claim schema**：`claim_id / scope{species,tissue,assay,preparation,disease_or_treatment}
  / failure_mode / observable_signature / risk_level / mitigation / evidence_source_type
  (internal_observation|peer_reviewed_literature|community_lead) / source_check
  (unchecked|locator_verified|claim_curated) / home{kind,id} / visibility
  (pre_annotation|post_decision|curator_only) / blind_safe / answer_dependency
  (none|sample_specific|dataset_specific) / status / owner / last_reviewed / links`。
- **归属五支树**：单物种全组织→SPECIES；单组织全物种→TISSUE；单坐标→CELL；
  多但非全或由 assay/制备/疾病条件决定→PATTERN；映射不进词表→UNMAPPED（禁自动注入）。
- **证据核验分层**：题录/文件指针核过=locator_verified（≠claim 成立）；
  `claim_curated` 只在人工复审接受后授予——本批全部为 `migrated_draft_pending_audit`，
  等六格人工审计（astra T4 通过条件"接受的 claim 100% 有 scope、来源和 owner"）。
- **社区经验限制**（评审停令 3）：`community_lead` 条目只能产生线索/复核要求，
  永不产生 hard_gate/panel_activation/named_label。

## 消费语义=shadow（T5 定盘，取更严者；qwen 版 PITFALL_OVERRIDE 作废）

- 拉页+旗标+审计照做，但**坑页不得直接改任何标签**：不产生 suggested_grade_cap、
  不自动降档、不翻案票面。判读改判仍走三独立判读票与硬门。
- 盲评前只注入**结构化旗标**（md 头段=旗标表；decisions 两列=`pitfall_risk_flags`
  / `pitfall_review_required`）；条目自由文本（failure_mode/mitigation）不随——
  astra 保守默认"盲评前不给坑页自由文本"。
- `answer_dependency≠none`（=blind_safe=false）条目：预标注面只有 claim_id+risk+
  复核要求；其文本在 run 产物（含机读件）内一律 `REDACTED:post_decision`。
- 每 run 产出 `shadow_attention.json`（适用 claim 结构化清单+链接解析状态）与
  `shadow_flags.jsonl`（逐簇旗标审计，`action:"risk_flag_only(no_auto_override)"`；
  自动具名/降级变化恒=0——终止条件监控项）。
- `EYEKB_S0_GATE=0`（整体回退）同时关闭 S0 与本注入（旧行为逐字节等价，G3 门已验）。

## RAG 隔离

known-issues 文本永不并入 RAG 语料；WIRE 全程锁现役 RAG（禁顺带激活暂存库）——
全量声明见 `docs/PITFALLS_RAG_ISOLATION.md`。

## 范围

Phase 1=六格闭环（本批）。Phase 2（72 格占位/24 格深补/全网重构）**未做**，
等本批验收与交叉审；扩展限额与五态格子状态机见词表件 §5。
