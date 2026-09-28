# VERDICT_OBLIGRUN_v2 — KB9 k9_ocs §10-6 义务 run（案 A 续跑）终局裁决（t_c145db7c run142，2026-09-28）

**VERDICT = READY**（判读矩阵第一支：OB-1..OB-4 全"清" AND P1≥24/33 AND P2 strict≤1/33）
→ 产 out/ACTIVATION_READINESS.md 建议票；**本 run 零接线零激活零默认切换**（OB-5 激活永久门归 PI 另批）。

依据：PREREG_OBLIGRUN.md（sha bfd8836d…）+ PREREG_OBLIGRUN_ADD1.md（sha 92c2a538…，案 A 追加节）；
放行：OBLIGRUN_RULING_1.md（裁定=案 A，"原地续跑"）。v1 作废留痕件 VERDICT_OBLIGRUN.md 不动（互引）。

## 逐门数字（当期实测）

| 门 | 结果 | 证据件 |
|---|---|---|
| OB-1 历史 ON 态门 | **清**（v1 落表沿袭 + 追加节登记） | out/OB1_ledger.tsv（339 行，v1）；ADD1 A4：v2.1 面与 v1 面差异=仅 2 条 36712326 lit 行（许可漂移字段 lit 内，31 簇整行逐字节等，out/FACE_V21_ledger.tsv） |
| OB-2 A07 诊断表 | **PASS**（v2.1 机械重算） | out/pre_vote_diagnostics_v21.tsv（57 行 + delta_vs_v1 列，57/57 zero=含 31 未涉簇零变化对照）；硬断言 post_shield top3==v2.1 面 ranking **33/33 全等**；out/OB2_notes_v21.md |
| OB-3 Arm1/Arm2 一致性 | **清**（v1 落表沿袭） | out/OB3_consistency.tsv（22/22，v1）；案 A ranking 字段零动→结论可继承（裁定理由 3） |
| OB-4 lit 同源排除复筛 | **通过（0 残留）** | out/OB4_lit_screening_v21.md + OB4_lit_hits_v21.tsv（v2.1 面 62 条/11 PMID，逐条两级复筛=0 剔除）；剔除集复算=恰 {Q6::7,Q6::11}×36712326 两行（按规则非点名，血缘件含外部解析 GSE155683→33865984 Collin 登记） |
| 票面 | kb9_face_v2.1.jsonl sha **2c0649dcc2001c8b…** | 33 簇集合不变、行序=RUN5、ranking/非剔除字段逐字节零漂移（33/33 逐字节对账 PASS） |
| 正式三席票 | **99/99 票齐，预算 99/150，零重试、零缺票** | A=qwen3.8-max 33 票、B=glm-5.1 33、C=deepseek-v3.2 33（out/ANN_{A,B,C}_oblig.jsonl + META，face_sha 三席一致）；enable_thinking:false 三席探针全过并逐席带参（logs/seat_probe_*.json）；LLM_CHANNEL 通道无 429/配额事件 |
| **P1（票规 v2 C2b）** | **26/33 ≥ 24/33 → PASS** | out/oblig_verdict.json：C2b 定名 28 簇（named），其中 consensus==truth 26；missed=Q6::12/15/16/18/24/27/28（7 簇：2 named-but-wrong + 5 无名[tie×3/split3×1/abstain3×1]，全为 Fibroblasts×6/Pericytes×1 谱系带） |
| **P2 strict** | **0/33 ≤ 1/33 → PASS**（any 并报 0/33） | 违规判据逐字=k8_verdict.py（C2b 新增定名簇自动入污染检查） |
| P3 kb 空率 | 13/33 照旧记录不入门 | oblig_verdict.json p3 |

## 口径与留痕声明

- 历史 C4 P1=22/33 FAIL（out/kb9_verdict.json，冻结）不回改；TIEP C2b 反事实 29/33 为存档票混面口径，均不替代本轮当期数字 26/33（当期=全 33 簇新票、v2.1 净化面、票规 v2 C2b）。禁"将激活/接近激活"式措辞：本 VERDICT 仅判定 §10-6 义务门全清 + 球门达标，**激活与否归 PI（OB-5）**。
- 残余限制随票登记（沿 v1）：①chen_cornea/limbus/sclera 无 accession，其 source paper 本地不可解析——若获权威映射须重跑 OB-4；②案 A 为票面层最小剔除，语料检索管线层"每次重建落盘同源筛查"义务已移交 REPOSYNC3 前置盘点（裁定追溯登记）；③C2b 下 coarse:X 入数语义跃迁沿协议 §4 声明。
- 领地：kb/、mcp_server/、evalset/、注册包、overlay、lit 语料、v1 全部产物——POST sha 复验 60 件 **0 写入**（ledgers/SHA_POST_OBLIGRUN_v2.txt）；本 run 全部新产物见 ledgers/SHA_NEW_ARTIFACTS_OBLIGRUN_v2.txt，脚本六件 o5-o10 *_t_c145db7c.py。
