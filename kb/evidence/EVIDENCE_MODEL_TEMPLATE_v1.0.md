# EyeKB 证据模型三字段模板 v1.0（D0 起步冻结）

冻结日期: 2026-09-24 ｜ 来源卡: t_1e783e43 ｜ 上游任务书: `/mnt/D/EyeKB/kb/evidence/D0_EVIDENCE_BRIEF.md`
适用范围: RAG/MCP 文献证据的**论断级**挂接。本模板为首版（v1.0），后续卡沿用；改字段定义必须 bump 版本并重跑存量校验。

## 1. 记录结构（JSONL，一行一条论断）

```json
{
 "claim_id": "D0C-NNN",
 "pmid": "8位数字",
 "title": "论文标题（自 admission 记录带入）",
 "inclusion_reason": "五类枚举之一",
 "claim_relation": "四类枚举之一",
 "evidence_context": {
   "kb_target": "KB 条目/概念 id（允许 '#' 后缀指概念）",
   "section": "文内定位（chunk 的 section 原值；空则用 chunk_type）",
   "verbatim": "论断原文（英文，≤50 词，必须是库内 chunk 的字面子串）",
   "limitation": "该论断适用边界一句话（必填，不得为空）"
 },
 "provenance": {
   "chunk_type": "abstract|paragraph|table_row（抽取命中的 chunk 类型）",
   "ingested": "full_text|abstract_only（自 d0_admission.json）",
   "extract_mode": "scripted_probe_sentence|scripted_probe_fragment",
   "generated_by": "产出脚本标识"
 }
}
```

## 2. 字段规范与填写规则

### 2.1 `inclusion_reason`（入库理由，五类，冻结枚举）

| 枚举值 | 定义 | 判据 |
|---|---|---|
| `core_reference` | 某 KB 条目/概念的主证据文献 | 删掉这条，该 KB 概念失去最直接的文献支撑 |
| `method_anchor` | 分析/处理**方法**的参照点（QC 阈值、整合策略、注释面板） | 论断内容关于"怎么做的"，不是"发现了什么" |
| `data_anchor` | 数据集**身份/出处**锚（GEO accession、样本构成、原始文献绑定） | 论断回答"这份数据是什么/从哪来" |
| `contradicting_evidence` | 与 KB 现行结论**方向相反**的论断 | 同一问题上的相反证据，必须保留不许删 |
| `background` | 语境性/框架性陈述，不直接支撑某数值结论 | 帮助读者理解 scope/局限/来龙去脉 |

### 2.2 `claim_relation`（与目标论断的关系，四类）

| 枚举值 | 定义 |
|---|---|
| `supports` | 支持 kb_target 的方向性陈述 |
| `refutes` | 反驳 kb_target 或其某成分的方向性陈述 |
| `qualifies` | 不改变方向，但限定成立条件/口径/适用边界 |
| `context_only` | 仅语境挂接，不构成对 kb_target 的方向性证据 |

### 2.3 `evidence_context`（可审计上下文）

- **kb_target**: 只允许挂**已存在**的 KB id（前缀白名单：`baseline_human_retina`、`human_retina`、`human_pdr_membrane`、`PDR__fibrovascular_membrane`、`proliferative_DR`、`GSE165784V2`）；`#` 后可指到条目内概念（如 `human_pdr_membrane#myeloid_states.foam_DAM_LAM`）。禁止虚构未注册 id。
- **section**: 逐字取所抽 chunk 的 `section` 原值，为空时用 `chunk_type` 顶替。
- **verbatim**: 英文原文 ≤50 词；**必须是 v2.2 库中该 pmid 任一 chunk 的字面子串**（含原文的空格/大小写怪癖，如 `MKI67 +  microglia`）；由脚本从 chunk 抽取，禁止手打/手改。截长句时只允许从头/尾**连续**裁剪。
- **limitation**: 一句话写明适用边界——物种/组织口径（膜≠视网膜≠玻璃体液）、样本量、推断层级（注释/拟时序/配受体推断≠实验验证）、abstract-only 等。**abstract-only 文献（full_text_available=0）的每条 limitation 必须注明 abstract-only。**

## 3. 正反例

### ✅ 正例（D0C-011，contradicting_evidence + refutes）
```json
{"claim_id":"D0C-011","pmid":"37917183","inclusion_reason":"contradicting_evidence",
 "claim_relation":"refutes",
 "evidence_context":{"kb_target":"human_pdr_membrane#myeloid",
  "section":"Discussion",
  "verbatim":"none of the inflammatory cells expressed microglia markers, such as  TMEM119  and  P2RY12 , in contrast to recent work that claimed microglial population as a main cell type involved in the fibrovascular membrane formation in PDR, with a subpopulation of microglia presenting fibrogenic properties ( 42 ).",
  "limitation":"Absence-of-evidence on TMEM119/P2RY12 in their own 4-sample dataset (homeostatic microglia markers can be lost upon activation/dissociation); refutes the microglial *identity* label, not the myeloid-dominant composition itself."}}
```
为什么是正例: 字面子串可机检；五要素齐全；refutes 的边界说清（驳"身份标注"不驳"髓系占比"）；保留了与 GSE165784 原文献（D0C-002）的张力而不是删掉任何一方。

### ❌ 反例（禁止写法）
```json
{"claim_id":"BAD-001","pmid":"35061025","inclusion_reason":"supporting_evidence",
 "claim_relation":"supports",
 "evidence_context":{"kb_target":"human_pdr_membrane#macrophage_fraction=79.5%",
  "section":"Results",
  "verbatim":"Hu et al. reported that macrophages comprise roughly 80% of the membrane immune infiltrate.",
  "limitation":""}}
```
为什么是反例（4 处违规）:
1. `inclusion_reason` 造词（枚举只有五类）；
2. `verbatim` 是**改写/外部知识补写**，库内任何 chunk 都不含该句，字面校验必挂；
3. kb_target 把具体数值写进 id 且该粒度概念未注册；
4. `limitation` 为空——abstract-only 文献（35061025）更是禁止配不到边界的条目。

## 4. 校验规约（验收同口径）

- 独立校验脚本: `scripts/verify_d0_claims.py`（直读冻结库 `chunks.parquet`，不依赖中间产物），逐条查: 枚举合法 / kb_target 白名单 / verbatim ≤50 词且为字面子串 / limitation 非空 / abstract-only 条目的 provenance.chunk_type=abstract。
- **通过率必须 100%**；任何未通过条目从 JSONL 删除并**全数**登记进当批报告的"未通过校验"节，不留痕外遗漏。
- 中间产物（抽取脚本、draft JSON、chunk dump）随批保留，不得清理。

## 5. 教义边界（沿用任务书红线）

- 本模型只覆盖 **D0 定向通道七篇**；全库铺开属后续卡，且须重新过 astra 评审。
- 论断只从文献原文提取；**禁止外部知识补写**；提取不到就少提取，不凑数。
- 禁动 `evalset/`（冻结件）、禁改 v2.1/v2.2 库文件本体、禁写 `kb/baselines`、`kb/markers`（他卡领地）。
