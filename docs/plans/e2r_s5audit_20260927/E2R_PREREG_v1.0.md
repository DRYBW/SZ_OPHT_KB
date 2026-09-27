# E2R_PREREG_v1.0 — S5 宽容口径收口核验的机读操作定义（判据先于一切跑数冻结）

卡片 t_dc954503｜任务书 BRIEF_E2R.md｜放行依据 USER_DIRECTIVE_20260927_scoring_wave.md（D1/E2R）
继承裁决：E1_VERDICT §9 / E2_VERDICT §9（W2 生效、否决列 −6.63pp 恒定）；本卡零改判，只收 S5 尾账。

## 0. 输入一致性门（先断言后开工）
- v5 provenance 中 type=pmid_context 且 n_hits>0 的 (cls,gene) 对数 == E2 矩阵 data/e2_gene_panel_pmid.tsv 中 pcx_ext=Y 行数 == 120；且全部属于 lib=retina_interneuron；且逐对存在于面板 markers[cls]。任一不满足 → exit 2 停工。

## 1. 清单化
data/e2r_pcx_pairs.tsv：120 行 ×(lib, cls, gene, query, n_hits, title1, title2)。top_titles 原样照录（含空串与截断）。

## 2. 标题→PMID 解析（冻结算法，EuropePMC REST /search，resultType=core）
记存储标题 T（可能 120 字符截断、可能为空串）：
- A 步：`TITLE:"<T去引号全串>"`；候选归一化（小写、去非字母数字与空白）后做前缀互含匹配（norm(cand) 前缀匹配 norm(T) 或反向，因截断）。取归一化全等优先、否则首个前缀命中。
- B 步（A 零命中）：取 T 前 10 个实词拼接 `TITLE:"<短语>"` 再前缀匹配。
- C 步（B 零命中）：`"<前10实词短语>"` 不限字段、`SOURCE:MED` 过滤，同法匹配。
- 三步皆空 → 该标题判「不可解析」。空串标题直接判「不可解析」，不发 API。
- 每次 API 原始 JSON 落 ledgers/api/<sha16前缀>.json（含重试），节流 ≥0.45s/请求，429/5xx 退避重试 ≤3 次。
- 「真实存在」= 命中记录 source=MED 且带 pmid 字段；期刊字段 journalInfo.title 或 journalTitle 非空 = 期刊可解析（单列记录，不进认账门）。仅 PMC 无 MED 记录 = 不可核。

## 3. HRCA 自引集合（本体论文 + 语料内对应件）
H = {41578023（Single-cell atlas of the transcriptome and chromatin accessibility in the human retina, Nat Genet）, 40660409（A scRNA-seq reference contrasting living and early post-mortem human retina across diverse donor states——同一研究的语料内预印本对应件）}。
两条均为 kb/literature_db evidence_meta_v2.3 在册记录（inclusion_reason=composition_baseline / state_signature）。标题级兜底：解析所得标题归一化后与上述两条语料题名前缀互含 → 亦计自引。
「首条即 HRCA」= title1 按 §2 解析后 PMID∈H 或题名兜底命中。

## 4. 关键词级相关性（零 LLM，机械规则）
- gene_hit：title 中出现基因 symbol（大小写不敏感、词边界）。
- class_hit：title 含类词——BC→bipolar；AC→amacrine；HC→horizontal。
- relevant = gene_hit ∨ class_hit。retina 词频另行记录（不进门）。

## 5. 逐对四态（互斥优先序）
- unverifiable：无任何标题可解析为真实 PMID。
- self_only：可解析但全部解析结果 ∈H。
- creditable：∃ 标题解析为真实 PMID ∉ H。
- creditable_rel：creditable 且该非 H 命中标题 relevant（同一条标题双满足）。

## 6. S5b 打分复刻
- 复刻件 = E2 scripts 拷贝进本卡目录改参（e2r_common/e2r_score/e2r_metrics），禁动 E2 原文件。
- keep() 新增：variant=S5b 时仅当 (lib,cls,gene) ∈ creditable 白名单才置 PCX_SENTINEL；S5b_rel 用 creditable_rel 白名单。其余规则与 S1/S5 逐字同文。
- 验证闸（不过 exit 2）：①本卡 raw/S1/S5 三张 scores TSV 与 E2 冻结件 data/e2_scores_* 逐行零差异；②E1 锚点全复现（72.45/67.74/68.39/16.77/3.23/60.26/80.77）；③E2 锚点复现（S1@196=63.27、S5@196=71.94、S1 无泄漏=56.77、S5 无泄漏=67.74、Q5b raw 93.02/S1 60.47/水分 32.55）。

## 7. 判读矩阵（BRIEF_E2R 原样继承 + 机械化定义）
- 可核验率 = |verifiable 以上三态中含可解析|/120 = (120 − |unverifiable|)/120。
- 非 HRCA 自引占多 ⇔ |creditable| > |self_only|。
- 大量离题（否决支的第二扳机，机械定义）⇔ |creditable ∧ ¬creditable_rel| / |creditable| > 0.5。
- 行1：可核验率 ≥50% ∧ 非自引占多 ∧ ¬大量离题 → S5b 口径成立，水分账按区间报（区间 = [S5 水分, S5b 水分] 升序，S1 32.55 作参照端），交 PI 决定未来评测是否采 S5b。
- 行2：可核验率 <50% ∨ 大量离题 → S5 定性"不可核不认"维持 E2 主规则，结案。
- 无论哪行：W2 与 E1/E2 裁决零改动；虚构/不可解析 PMID 单列清单（KB 数据质量发现）。

## 8. 红线执行
全部产物只落 /mnt/D/EyeKB/plans/e2r_s5audit_20260927/；kb/、mcp_server/、evalset、evidence_scoring、e2_decontam 五面全程只读（PRE/POST sha 全等为证）；零 LLM 判读调用；零生产码 import；除 EuropePMC/PubMed 检索返回落盘外零下载。

## 9. 已知口径注记
v5 pmid_context 记录字段仅有 (type, source, query, n_hits, top_titles)，**从未存储任何 PMID**——本卡"身份核验"即对题名反解，这本身是 KB 数据质量发现，单列。
