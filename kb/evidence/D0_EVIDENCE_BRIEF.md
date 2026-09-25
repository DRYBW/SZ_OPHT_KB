# EyeKB 证据模型起步卡任务书：D0 七篇论断级核验（三字段模板 + 首批条目）

## 背景与定位
Astra 评审定的项目主线之一是"证据可审计"：RAG/MCP 文献证据不能只有 PMID 挂靠，要有**论断级**的关系与上下文。
本卡 = 三字段证据模型的**起步实施**：只做 D0 定向通道七篇（v2.2 库，d0_admission.json 有清单与例外登记），
产出可复用模板 + 首批条目。**禁止全库铺开**（教义红线）。

## 三字段定义（本卡冻结 v1.0，后续卡沿用）
1. `inclusion_reason`（入库理由，五类枚举）：core_reference（核心参考）/ method_anchor（方法锚）/ data_anchor（数据锚）/ contradicting_evidence（矛盾证据）/ background（背景）
2. `claim_relation`（与目标论断的关系枚举）：supports / refutes / qualifies（限定条件）/ context_only
3. `evidence_context`（可审计上下文）：{kb_target: 指向的 KB 条目/概念 id, section: 文内定位, verbatim: 论断原文（英，≤50词）, limitation: 该论断的适用边界一句话}

## 任务
1. 读 D0 七篇的入库材料（v2.2 库 chunks：`/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.2_2026-09/`，papers.jsonl 过滤 pmid；full_text_available=0 的两篇只用摘要级证据并在 limitation 注明）
2. 对每篇提取 3-8 条关键论断（与既有 KB 条目/概念可挂接的优先：retina 基线、PDR 膜 demo、GSE165784 数据锚），填三字段条目
3. 产出：
   - `/mnt/D/EyeKB/kb/evidence/EVIDENCE_MODEL_TEMPLATE_v1.0.md`（字段规范+填写规则+正反例各1）
   - `/mnt/D/EyeKB/kb/evidence/d0_claims_v1.jsonl`（首批条目，逐条带 pmid/kb_target/三字段）
   - `/mnt/D/EyeKB/kb/evidence/D0_EVIDENCE_REPORT.md`（覆盖统计：每篇条目数、kb_target 分布、abstract-only 局限清单）
4. 自检：每条 verbatim 必须能在对应 chunk 文本中字面找到（写个校验脚本跑一遍，结果入报告）；找不到的条目删除不留痕外无遗漏地列进报告"未通过校验"节

## 红线
- 禁动 evalset/（冻结件）、禁改 v2.1/v2.2 库文件、禁写 kb/baselines 与 kb/markers（他卡领地）
- 论断只从文献原文提取，禁止外部知识补写；提取不到就少提取，不凑数
- 中间产物全保留；完成或遇阻必须落卡

## 验收（协调者执行）
模板字段完备性 / 条目 schema 合法 / verbatim 字面校验通过率 100%（未通过项全部留痕）/ 五类 inclusion_reason 均有定义
