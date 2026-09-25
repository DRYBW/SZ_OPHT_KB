# D0 证据模型起步批 — 覆盖报告（v1.0，2026-09-24）

任务卡: t_1e783e43 ｜ 任务书: `D0_EVIDENCE_BRIEF.md` ｜ 模板: `EVIDENCE_MODEL_TEMPLATE_v1.0.md`
条目文件: `d0_claims_v1.jsonl`（35 条）｜ 校验脚本: `scripts/verify_d0_claims.py`

## 1. verbatim 字面校验结果（验收主门）

- 独立重跑（直读冻结库 `literature_db/v2.2_2026-09/chunks.parquet`，不依赖本卡中间产物）:
  **checked 35 claims, 35 pass, 0 fail → 100% PASS**
- 校验项: 枚举合法（五类/四类）/ kb_target 白名单 / verbatim ≤50 词且为对应 pmid 任一 chunk 的**字面子串**（含原文空格与大小写怪癖）/ limitation 非空 / abstract-only 篇目引文必须出自 abstract chunk。
- **"未通过校验"节: 无未通过条目。**（过程中 3 条曾因 >50 词或截句不完整被脚本级修正——D0C-011/015/017/019/021/030 按"连续裁剪/片段化"规则重写后全部重抽重验，无手打文本进入产物。）

## 2. 覆盖统计（每篇条目数，红线合规: 全部 ≤8 且 ≥3）

| pmid | 论文 | 摄入 | 条数 |
|---|---|---|---|
| 35061025 | Hu 2022 Diabetes（GSE165784 原文，微胶质） | abstract_only | 5 (D0C-001..005) |
| 41578023 | HRCA 双模态参考图谱 | abstract_only | 3 (D0C-006..008) |
| 37917183 | JCI Insight 2023 AEBP1 周细胞-肌成纤维 | full_text | 5 (D0C-009..013) |
| 39220810 | Ophthalmol Sci 2024 玻璃体液 T 细胞 | full_text | 5 (D0C-014..018) |
| 40069725 | J Transl Med 2025 MKI67+ 微胶质 | full_text | 6 (D0C-019..024) |
| 40562775 | Nat Commun 2025 Sirt3/FAO 代谢 niche | full_text | 5 (D0C-025..029) |
| 42601615 | J Transl Med 2026 SOX15 PDR 图谱 | full_text | 6 (D0C-030..035) |

合计 35 条，覆盖 D0 七篇全部（清单与例外=`data_d0/d0_admission.json`）。

### inclusion_reason 分布
core_reference 20 ｜ background 9 ｜ data_anchor 4 ｜ contradicting_evidence 1 ｜ method_anchor 1 （**五类均有实条使用**）

### claim_relation 分布
supports 21 ｜ qualifies 7 ｜ context_only 6 ｜ refutes 1

### kb_target 分布（11 个挂接点）
- `PDR__fibrovascular_membrane` 9 ｜ `human_pdr_membrane`(根) 4 ｜ `proliferative_DR` 6 ｜ `GSE165784V2` 3 ｜ `baseline_human_retina` 3
- 概念级: `human_pdr_membrane#myeloid` 2、`#myeloid_states` 3、`#myeloid_states.foam_DAM_LAM` 2、`#major_compartments` 1、`#stromal_pericyte+stromal_myofibro` 1、`#stromal_myofibro` 1
- 三条主线全覆盖: **retina 基线**（HRCA 3 条）、**PDR 膜 demo**（膜组成/髓系态/基质态 14 条）、**GSE165784 数据锚**（原文献 5 条 + 独立再分析 2 条 + 第三方引用 2 条锚定同一 accession）。

## 3. abstract-only 局限清单（full_text_available=0）

| pmid | 影响 | 条目级处置 |
|---|---|---|
| 35061025 | 无 PMCID/OA 失败 → 仅摘要可引；样本 n、cluster 数、"microglia major" 的定量口径不可从库内核验 | D0C-001..005 全部 limitation 注明 abstract-only；provenance.chunk_type=abstract |
| 41578023 | HRCA 3.9M 细胞/125 donor/130+ 类型均为摘要自述；细粒度组成表不在库内 | D0C-006..008 同上 |

两篇共 8 条（占 22.9%）为摘要级证据——按任务书允许，但**不得**作为任何 A 级数值裁决的依据（与 `human_pdr_membrane` 卡 caveat "B 级文献锚未给精确%" 口径一致）。

## 4. 本批暴露的文献张力（证据模型的价值点，登记备查）

1. **微胶质 vs 巨噬身份之争（同一 GSE165784 数据）**：35061025 主张 microglia 为主体并定义 GPNMB+ 亚群（D0C-002/003）；37917183 实测 "none of the inflammatory cells expressed microglia markers (TMEM119/P2RY12)" 反驳（D0C-011，本批唯一 refutes）；40069725 用 SELENOP/MRC1/GPNMB 等面板把同一群叫 microglia（D0C-021/022 method_anchor）——我方 Track B 把这些态标为 Macrophage。→ `human_pdr_membrane#myeloid*` 的**方向（髓系为主）稳固，身份词（microglia vs macrophage）为面板依赖**，与既有 caveat 一致。
2. **口径三分**：FVM 消化膜（GSE165784 系）≠ 玻璃体液洗涤（39220810，T 细胞 91.6%，D0C-014 qualifies）≠ PDR 供体视网膜本体（42601615，D0C-030/033）。任何"膜组成"读数不得外推到另两个腔室。
3. 42601615 转述 Hu 2022 "mesenchymal 8.2%"（D0C-034）为第三方口径，仅作 provenance，未独立复推。

## 5. 红线遵守声明

- 未动 `evalset/`、未改 v2.1/v2.2 库文件与 `d0_admission.json` 本体、未写 `kb/baselines`、`kb/markers`（只读引用其 entry_id 作 kb_target）。
- 未全库铺开：仅 pmid 过滤 196 个 D0 chunk。
- 论断 100% 脚本化抽取自 chunk 原文，零外部知识补写。
- 中间产物全保留（见 §6）。

## 6. 产物与溯源清单

正式产物（`/mnt/D/EyeKB/kb/evidence/`）:
- `EVIDENCE_MODEL_TEMPLATE_v1.0.md` — 三字段规范 v1.0（正反例各 1）
- `d0_claims_v1.jsonl` — 首批 35 条
- `D0_EVIDENCE_REPORT.md` — 本报告
- `scripts/verify_d0_claims.py` — 独立字面校验（可重跑，exit code 作门禁）
- `scripts/extract_claims.py` — 探针式抽取脚本（35 条全部经此生成）
- `scripts/build_and_validate.py` — draft→jsonl 装配 + 批内校验
- `SHA256SUMS.txt` — 产物哈希锚定

中间产物（工作区 `~/.hermes/kanban/boards/pi-briefing/workspaces/t_1e783e43/`，不删）:
`d0_chunks.parquet` / `d0_chunks.json`（196 chunk 过滤件）、`paper_*.txt`（七篇分文本）、`d0_claims_draft.json`、`validation_result.json`、`coverage_stats.json`
