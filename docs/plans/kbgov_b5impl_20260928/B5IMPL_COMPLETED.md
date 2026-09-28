# B5IMPL_COMPLETED — KBGOV 主候选 B5 实装收尾件（追加五预授权队列①）

- 卡：t_8960c7e0 ｜ 执行=AGENT_ROLE ｜ 日期=2026-09-28
- 任务书：BRIEF_B5IMPL.md ｜ 判据权威源：plans/kb_gov_20260928/KBGOV_CANDIDATE.md §G1-§G3（B5 主候选，机械 A/B 双门证据）+ KBGOV_PREREG_v1.1
- 改动面：仅 `/mnt/D/EyeKB/mcp_server/`（eyekb_core.py 治理层 + server.py 版本/描述注记 + kbgov_vocab.json.gz 数据件）。kb/、evalset/、注册包、overlay、plans/kb_gov_20260928 全程只读，门5 复验实证（out/b509_readonly_recheck.json）。

## 一句话结论

**B5 已实装为生产默认（server=KB1v2-0.6-kbgov5，EYEKB_KBGOV_B5 未设=ON）：五道验收门全 PASS——病灶 7/7 具名清零、人源 230 簇重放位移 0.0%（鼠侧 59/59 全拒）、golden41/42-probe/G1-G4 套/probe_repo 系回归全等（B5=0 态）、回退态与 pre 基线逐字节全等（42/42 探针 sha 台账）、只读领地零写入。**

## 实装语义（与候选件逐字对应）

- **G1 输入物种判定**（query_marker genes-mode 入口、排序前）：title_frac/msp(Gm\d+|.*Rik$)/m_only 三信号，冻结阈值 T=0.4（校准件锚定，human_misdetections=[] 在案）。响应新增 `input_species ∈ {mouse_confirmed, mouse_suspected, human_assumed}`。
- **G2 B5 拒答**：confirmed∨suspected → `celltype_ranking=[]`，原条目全量转 `unranked_candidates`（保留、非具名排名），顶层加 `no_named_ranking_for='mouse_input'` + `species_evidence`（title_frac/msp/m_only + 样例）。human_assumed 零干预。
- **G3 标注档**：shared_genes ⊆ AMBIG{GLUL,VIM,CLU} ∧ n_shared≥1 → 条目加 `no_naming_claim=true + reason='ambiguous_coexpression_only'`，**排序与条目保留不动**（B2/B3 删除档 14.78% 过杀已回炉，不采）。
- **env 开关**：`EYEKB_KBGOV_B5 ∈ {0,false,off,no}`（casefold，与 EYEKB_ACT_V6 同形）= OFF 回退态=pre 基线逐字节全等；未设/其余值 = ON。词表加载失败 → fail-soft 降级 legacy（stderr 一次性登记，不 throw；b503 实测降级态==OFF 态、恢复态==ON 态）。
- **版本**：`KB1v2-0.5-k9reg → KB1v2-0.6-kbgov5`；REGISTERED_DEFAULT_OFF 语义（k9_ocs/lacrimal_v6 不入默认 all）三态断言保持（b503）。
- **禁 import 复刻件**：治理逻辑为生产码内独立实现；双源一致=生产结果 vs 复刻件冻结表逐值对账（见门1/2）。

## 五道门结果（全 PASS）

| 门 | 判据 | 结果 | 证据 |
|---|---|---|---|
| 1 病灶 | Q7::11/15/21/22/52/58/61 B5 形态零具名残留（对照候选 7/7） | **PASS 7/7**：具名清空+拒答字段在位+unranked 镜像 A 序+OFF 态伪影还原（Pericyte/Fibroblast/AC 案）；tier/named 与复刻件 kbgov_ab_lesion.tsv 逐簇一致；Q2::22 flags==replica 且序不动；Q5b::35 kept_bare（管辖边界保持） | out/b505_gates12.json（57 断言 0 fail） |
| 2 人源零位移 | 230 簇流量重放 ranking 位移=0.0%（过杀线>5% 沿用） | **PASS 0.0%（0/230）**；鼠侧账 59/59 全拒无具名残留，与 out/kbgov_mouse_side.tsv 全等；G1 三信号+tier 对 data/kbgov_g1_signals_290.json **290/290 逐值全等（双源一致）**；候选 metrics B5 shift=0/PASS 对上 | 同上 |
| 3 回归 | 黄金 41/41 off 态全等 + 42-probe(off) + G1-G4 套 + probe_repo 系；ON 三席 smoke | **PASS**：golden41 41/41+接线契约 11 项（B5=0 双 V6 态）；42-probe B5=0 与 pre sha 全等（b503，42/42）；G1 KB5 自检 S2a PASS+S1 17/22（原生宇宙 ACT_V6=0+B5=0，与 KB8 发布同分；生产宇宙下 B5-ON 足迹=40 个 Q7 鼠源簇拒答=设计语义，人源零漂移）；G2 kc_selfcheck 16/16、G4 KB2C 33/33 均生产默认 ON 态过；probe_repo 系 stdio 断言（版本/tools/Microglia top1/两态序全等/lacrimal 泄漏0）13/13；**ON 三席 stdio 真往返 163 genes 调用=34 拒答/129 人源/0 错误**（与进程内预扫逐席一致 A48+B69+C46） | out/b504_golden41_B5OFF_{OFF,ON}.json、out/b503_selfproof.json、logs/b506a_*、out/b506b_*、out/b506c_*、out/b507_stdio_smoke.json |
| 4 回退 | EYEKB_KBGOV_B5=0 与 pre sha 台账双态对照 | **PASS**：42/42 探针 off_eq_pre=True；16 genes-mode 探针 on≠pre（治理生效面）、26 非 genes 探针 on==pre（管辖面不越界） | **out/B5IMPL_A5_ROLLBACK.tsv** + ledgers/{SHA_PRE,SHA_POST}_B5IMPL.txt |
| 5 留痕 | 只读复验零写入 | **PASS**：kb9 PRE 台账非 MCP 面 102 全等（4 例 /mnt/D/OcularKB/WIKI/* 漂移 mtime=09-27 21:16-21:17，早于本卡开工 14:55，**归因=前窗既有非本卡**）；KBGOV 输入 34/34 全等；本卡 PRE 台账 9/9+SHA_MANIFEST 32/32 全等；词表副本==源件 sha 9b504a2e…；窗口扫描 mcp_server 变更=合法 3 件（eyekb_core.py/server.py/kbgov_vocab.json.gz），白名单外命中=1 件 ANNOTATION_PROTOCOL_v1.3.md（**文件头自署并行卡 t_e0f94d4f H1M3，本卡零触碰**） | out/b509_readonly_recheck.json |

## 生效与回退操作

- 生效：新启动的 MCP server 进程默认 ON；**已在运行的 server 进程（gateway 未重启）仍是旧代码**，随下次会话/重启自然切换。判读席侧消费协议（"no_naming_claim/cross_species_hit 条目禁作 identity 定名依据"）归 H1M3/判读协议线承接（其 v1.3 §9 已在窗口内落，本卡不代写）。
- 回退：启动环境置 `EYEKB_KBGOV_B5=0`（或 false/off/no）=pre 基线逐字节全态（门4 台账即操作依据）；词表文件缺失/损坏自动降级 legacy，无需人工干预。

## 限制清单（随实装呈报，与候选件 §4 一致）

1. suspected=惯例单证据档：本数据 231 人源簇惯例全大写（misdetections=0），但**真人源 title-case 上送将被误拒**——T+7 观察窗逐例登记复核，若误拒>0 回退 B4 口径（env 粒度=同接线不分叉，改档属方法判据变更需 PI 另批）。
2. AMBIG 三支中 CLU 不在任何现役面板（惰性锚保留）。
3. 管辖面=genes-mode；cell_type-mode/list-mode/判读层三工具零扰动（门4 双态对照实证）。
4. ENSG 形态输入按词表 miss→human_assumed（候选件限制④照录）。
5. 库宇宙注：若消费方在 OFF 库宇宙（如显式 library=retina/membrane）上送鼠源基因，拒答同样生效（治理在查询装配后、与库选择正交）。

## T+7 观察建议项（给协调者，本卡不自行建 cron）

- 建议 2026-10-05 前后对 logs/mcp_trace/calls_2026-10-0{2..5}.jsonl 采样：query_marker genes-mode 中 `input_species=mouse_suspected` 且来自真实判读席的拒答逐例登记，复核误拒率（候选件 §3.4-2 泛化边界）；误拒>0 → 按门4 回退 B4 口径请示流程走。
- 观察标签建议：按 resp.input_species 字段直接筛（calllog 留痕已含治理字段，零额外埋点）。

## 产物索引

scripts/{b501_capture_pre_baseline, b503_selfproof_rollback, b504_golden41_off, b505_gates12, b506a_g1_hotspot_copy, b506b_kc_selfcheck_copy, b506c_g4_kb2c_copy, b507_stdio_smoke, b509_readonly_recheck}.py ｜ out/（12 件，见上表）｜ ledgers/{SHA_PRE,SHA_POST}_B5IMPL.txt ｜ logs/（10 件含三套 suite 日志与归因运行）
中间产物全保留；仓面零 push（登记件 REPO_RESYNC_B5IMPL.md 同目录）。

*B5IMPL t_8960c7e0 收尾件（2026-09-28 15:5x）。五门全过=实装成功，默认态已 ON；回退与观察按本件操作。*
