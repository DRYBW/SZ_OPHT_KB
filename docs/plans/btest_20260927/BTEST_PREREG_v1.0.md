# BTEST — RAG 自由查询 A/B 正式验证 预注册（D9 放行，判据先于执行冻结，2026-09-27）

- 卡：t_fb660dfe（AGENT_ROLE）｜ 目录：/mnt/D/EyeKB/plans/btest_20260927/
- 任务书：本目录 BRIEF_BTEST.md｜放行：WIKI/USER_DIRECTIVE_20260927_scoring_wave.md 追加二 D9+D11
- 设计蓝本：plans/rag_anno_usability_20260927/RAG_ANNOTATION_USABILITY.md §B（五要点骨架照抄）
- 本文件即判据件：落盘取 sha256（BTEST_PREREG_v1.0.md.sha256）后才允许脚本构建与起跑。
  落纸后禁一字改动（禁球门移动；任何修订须另件 v1.1 并在跑数之前，跑数后只许追加勘误不改判据）。

## 定位与诚实性声明（口径红线）
- 本轮 = B 形态（自由查询辅助）首次正式 A/B 验证：唯一变量 = 取证方式
  （A 臂赛前冻结证据面 EV_DIGEST 卡片；B 臂不给 EV_DIGEST 证据字段，判读会话内按需调用 MCP 五工具）。
- 对照 = FACEV21 冻结基线（盘上：R1=19/22、R2=0/23、保全 2/2、verdict PASS；
  scoring/FACEV21_VERDICT.json sha 见 §11）。A 臂不重跑（票档已冻结复用）。
- 双基线 15/19 写死：RUN4-r R1'=15/22 与 FACEV21 19/22。球门一字不降。
- 声明（预注册落纸）：B 臂为每簇独立会话（1 簇 × 多轮工具），A 臂为 5 簇一批单发——
  会话粒度差异属 B 形态定义的一部分（自由查询按需取证，逐簇留痕归因要求所致，RAGANNO §B.3
  "每簇留痕必须非空"），对照问题本身是"形态 A vs 形态 B"，非"仅证据来源变量"的 RCT。
  此差异不构成对球门的放松，如实登记。
- pred_hint（分类器旁证）与 depth/ambient 旗在 B 臂卡片一并撤下：两者属 A 臂卡片的预烘焙信息层，
  为守"唯一变量=取证方式"不引入"预烘焙旁证"混杂，B 臂一切辅助信息仅经工具按需获取。
- 本卡结果无论何档，只出判读与成本对照表；替代/接线/激活决策归 PI，不自动外推线上。

## §1 靶与考卷（与 FACEV21 §1 逐字同；卷面文件逐字节同一张卷）
- 卷面 = plans/face_v21_20260926/face/EV_DIGEST_SLIM_facev21.jsonl，
  sha256=c4a47e399393f2299a27e5e5b01c0e8543690d8ad5a32da9c88f2f1f7e86da5a（45 行）。
- 热点 22 = run3_M4_hotspots_v1.1.tsv high_purity=True 簇，与 RUN4_TARGETS_v1.1.json
  `hotspots_22` 逐字一致（机械断言相等，不等即中止）：
  Q1::1, Q1::9, Q2::22, Q3::13, Q3::5, Q4::14, Q4::15, Q4::19, Q4::9,
  Q5b::13, Q5b::16, Q5b::19, Q5b::20, Q5b::23, Q5b::31, Q5b::32, Q5b::35, Q5b::42, Q5b::43,
  Q5b::45, Q7::1, Q7::10
- 对照 23 = RUN4_TARGETS_v1.1.json `controls_23` 逐字一致（Q1::4, Q2::27, Q2::4, Q3::4, Q3::8,
  Q4::23, Q4::24, Q4::29, Q4::32, Q4::37, Q4::39, Q5b::17, Q5b::2, Q5b::3, Q5b::8, Q7::18,
  Q7::3, Q7::42, Q7::46, Q7::52, Q7::58, Q7::63, Q7::8）。
- 题面行数 = 45。target_role 字段禁入 B 臂卡片（防泄漏提示，构建期机械断言）。

## §2 球门与票规（C4=现行三票规，逐字复用 FACEV21/RUN4-r 实现）
- 票/truth/共识实现 = kb2_bscore_v4_truthfix_t_2ae2610d.py exec-head 逐字复用（与
  facev21_verdict.py 同一实现源）；C4 共识 = ballot(定名∧grade∈{A,B}) 多数派≥2/3，
  tie/split3/abstain3 无名。
- 主判读（D9 追加二原文三档 + 本件 tie-break 细化，全为收紧不放松）：
  - PASS"B 不劣于 A"：R1 ≥19/22 ∧ R2 ≤1/23 ∧ 保全双过（Q4::15 ∧ Q5b::13 共识==truth）。
  - 部分成立：R1 ≥15 且 <19 ∧ R2 ≤1/23（逐簇净损失归因表）。
  - B 不达（维持 A 唯一形态）：R1 <15 ∨ R2 >1/23。
  - 细化档（预注册 tie-break，防口径争议）：R1≥19 ∧ R2≤1 但保全破 → 计"部分成立"
    （PASS 三条件缺一不立，此条只收紧不放松）；R1<15 时保全状态仅报告不改变档位。
- R2 定义逐字同 FACEV21 §2：对照 23 中 r3_double_ok=True（读 run3_object_B_table_v1.1.tsv）
  而本轮共识翻错（非"共识名存在且==truth"，含 tie/abstain）的簇数 ≤1。
- 总裁决 = 稳定性门（§5）先行 ∧ 上档判定。禁调阈值。

## §3 三席与参数冻结（与 FACEV21 §3 同）
- A = qwen3.8-max ｜ B = glm-5.1 ｜ C = deepseek-v3.2（跨厂商互异；通道 = LLM_CHANNEL 既有 key，
  脚本内读取不打印）。T=0.2、max_tokens=3500/次调用、qwen 系 enable_thinking=false。
- 起跑前三席冒烟各 1 次（探针含一次真实工具回路，用合成簇 ID SMOKE::1，不入 45 簇卷面、
  不产出票），记录 logs/seat_smoke.txt；任一键败即中止。
- 留痕层：runner 进程内直调 mcp_server/server.py 工具包装函数（同一实现、同一服务端 calllog
  留痕路径），env EYEKB_MCP_TRACE_TAG=btest_d9（观察窗统计器默认排除测试流量，与 A2 分母隔离）。
  EYEKB_ACT_V6 不设 = ON 态（all=60 类，冒烟实证返回 retina_v6:: 类别）；EYEKB_MCP_SOFTFLAGS
  不设 = ON（与现服务默认一致）。

## §4 B 臂协议（本轮唯一协议变更；全部冻结文本在本节）
### 4.1 B 卡片（逐簇数据卡；渲染行 = A 臂 card_lines() 的 header 行 + top_genes 行逐字同）
- 保留行：`[{cluster_id}] member=… material=species:…/tissue:… n_cells=… qc=…` 与
  `top_genes(按序): …`（基因 symbol 渲染逻辑与 A 臂 render_genes 逐字同，≤20 基因）。
- 撤下行：kb_gene_hits / kb_celltype_ranking / lit / pred_hint / depth-ambient 旗行 /
  三处 FACEV21 规则行（旗规则/判序注记）——B 臂证据一律来自工具。
- 附冻结解释行（原文）：
  `取证方式说明（绑定）：本卡不提供任何预烘焙证据；判读所需 marker/文献/组成/疾病先验`
  `一律由你在本会话内调用工具自行取证。冻结件中"输入=EV_DIGEST.jsonl"在本模式读作`
  `"输入=数据卡+工具按需证据"；词表/等级/三门/输出字段以冻结件原文为准。`
### 4.2 五工具 function-calling schema（OpenAI-compatible tools；实测三席 tool_calls 可用）
- query_marker(genes: string[]≤40 每项≤20字, cell_type: string≤80字)；library 服务端锁 'all'。
- search_literature(cell_type≤80字, species≤20字, tissue≤40字, query≤200字, top_k∈[1,10]默认5)；
  db 参数锁 ''（=v2.0_2026-09 默认库，禁任意路径）。
- get_kb_page(scope∈{index,topic,tissue}, name≤80字)（白名单服务端已有）。
- get_tissue_composition(species≤20字, tissue≤40字, disease≤100字, development_stage≤20字)。
- get_disease_prior(disease≤100字, tissue≤60字)。
- 未知工具名/参数越界：不执行，回注 error 文本作为 tool result（计入调用数）。
- 工具返回 JSON 序列化后 ≤8000 字符，超限头部截断并附 `...[TRUNCATED]` 标记。
### 4.3 会话回路（每簇一个独立会话；run1 与 run2 全量独立，互不共享上下文）
1. 首条 user 消息 = 判读卡（含 ANNOT_INSTRUCTIONS.md 冻结件原文全文 + §4.1 卡 + 工具说明 +
   输出要求；模板全文见 scripts/btest_runner.py 内嵌，与本节口径一致，构建期 grep 对账）。
2. 循环上限 8 个 assistant 轮：有 tool_calls → 执行并回注结果继续；无 tool_calls → 按 §4.4 解析。
3. 有效票但全会话工具调用数=0 → 追加绑定提醒（原文）：
   `你尚未调用任何工具取证即给出判读，不符合本模式规程。请先调用至少一个取证工具
   （如 query_marker），然后再输出同一格式的 JSON 判定。`最多提醒 2 次。
4. 第 8 轮耗尽 → 一次无工具强制收尾调用（"基于已有证据立即输出最终单行 JSON，不得再调用工具"）。
5. 格式错误重试（回注"格式错误，只输出一行合法 JSON"）上限 3 次。
6. 簇级终态：OK（有效票∧工具调用≥1）/ PROTOCOL_FAIL（提醒耗尽仍零工具、或解析重试耗尽、
   或强制收尾仍无有效票）。PROTOCOL_FAIL 簇整体重跑（新会话）至多 3 次；仍失败 →
   该 (run,seat) 中止 missing≠0 硬断言失败上报（禁另一 run 的票顶替——独立性红线）。
7. 成本硬录：每簇 {api_calls, tool_calls 总数与分工具计数, 会话墙钟秒, prompt_tokens,
   completion_tokens, turns, reminders, forced_final}；logs/cost_r{N}_{stem}.jsonl 逐簇落盘，
   席位与总计在 COMPLETED 汇总，并与 A 臂 FACEV21 META usage 对照。
8. 并行模式：同一 run 内三席并行（3 独立进程，API-bound）；run1 完成后再跑 run2。
   断点续跑：每簇落盘后更新 checkpoint（DONEF），重跑只补缺簇（FACEV21 runner 惯例）。

### 4.4 票面格式
- 与 A 臂完全同字段：cluster_id / identity / level / grade / gates(三键) / flag / why；单行 JSON。
- identity 词表、grade A|B|C、gates 取値、flag 枚举、why≤40字：全按 ANNOT_INSTRUCTIONS.md 冻结件。
- 票文件 = annotation/ANN_{stem}_btest_r{N}.jsonl（45 行，missing=0 断言）。

## §5 稳定性门（先于 A/B 对比，独立前置）
- B 臂全量独立跑 2 次（run1、run2 各 45 簇 × 3 席）后，逐簇比较两 run 的 C4 共识名：
  一致 = 两名相同（含 None==None，即两 run 同判弃权/tie 计一致）。
- 一致率 = 一致簇数/45。门：≥90% → 即 ≥41/45（45×0.9=40.5，取整下界 41）。
- 不过门 → 判"不判、先治非确定性"：出诊断报告（不一致簇逐簇两 run 票面/工具调用差异归因），
  **禁做 A/B 对比判读**，落卡收工。
- 过门 → 进入 §2 主判读；主判读票 = run1（预注册钉死，run2 仅作稳定性样本；
  run2 的 R1/R2/保全机械复算仅作诊断列并列报告，不进判据）。
- 诊断列（不进门）：席位级 identity 一致率（run1 vs run2 逐席）、C2b 共识一致率、
  弃权率对比 A 臂。

## §6 C2b 并列读（D11 过渡条款；零额外票，同一批 B 臂票机械重算）
- C2b = TIEP scripts/t1_revote.py rule_c2(count_coarse=True) 逐字复用：≥2 席同标签即定名
  （定名票任意 grade；coarse:X 计入标签 X 法定人数；undetermined 不入数）。
- 对 run1/run2 的 45 簇三席票各算 C2b 共识名，同表并列报告 C4 与 C2b 的：
  R1 命中数、R2 翻错数（r3_double_ok ∧ ¬(C2b名∧==truth)）、保全两簇、具名数。
- 判读矩阵档位判定只按 C4（D9 原文"主读 C4"）；C2b 列只并列不进门禁。
- A 侧参照：FACEV21 票档的 C2b 机械重算，并与 TIEP out/revote_matrix.tsv（face=FACEV21）
  的 name_C2b 列逐簇对账（不等即中止——双实现交叉验证）。

## §7 判读矩阵（D9 预授权，先冻结后看数，全阴性合法）
| 结果 | 处置 |
|---|---|
| 稳定性门 <90% | 不判、先治非确定性；诊断报告收卡 |
| 过门 ∧ R1≥19 ∧ R2≤1 ∧ 保全双过 | PASS"B 不劣于 A"；出成本对照；替代价值归 PI（不自动接线） |
| 过门 ∧ 15≤R1<19 ∧ R2≤1（或 §2 细化档） | 部分成立；净损失逐簇归因表 |
| 过门 ∧ (R1<15 ∨ R2>1) | B 不达；维持 A 唯一形态 |

## §8 执行铁序
1. 本件 + sha256 落纸（先于一切构建/起跑）。
2. 脚本构建：scripts/btest_runner.py（B 臂会话 runner）、scripts/btest_verdict.py（稳定性门+
   主判读+C2b 并列+成本汇总）、scripts/btest_input_sha_check.py（PRE/POST 台账）。
   grep 自检全部硬编码路径：写入只允许 plans/btest_20260927/**（+服务端 calllog 追加，
   属正常服务副作用白名单）；读取 §11 白名单只读。输出 logs/path_grep.txt。
3. 输入 PRE sha 台账落 ledgers/INPUT_SHA_PRE.txt；起跑前逐字节复核未变。
4. 冒烟（三席 tool_calls 回路探针）→ run1 三席并行 → run2 三席并行 → 稳定性门。
5. 门过 → btest_verdict.py → scoring/BTEST_VERDICT.json + out/ 对比表与成本表；
   门不过 → 诊断报告替代步骤 5 判读。
6. BTEST_COMPLETED.md + SHA_MANIFEST.txt（含 POST sha 复核）；落卡（complete 或 block，禁裸退）。
7. 全程零下载；除本目录与 calllog 服务端追加外零写入；§11 冻结件只读禁覆盖。

## §9 红线（继承任务书 + D9/D11 + 证据消费纪律 v2）
- 冻结件零触碰：face_v21/**（卷面票档）、evalset/**（truth/靶/R2 表/指令/裁决实现）、
  run7rg/**、tiep_20260927/**（C2b 实现源）、kb/**、mcp_server/**（含 server.py/calllog.py）、
  OcularKB rag 库与模型目录——全部只读。
- mcp_server/eyekb_core/kb/面板禁改一字（B 臂只"使用"服务；calllog 追加是唯一允许的服务端写，
  属留痕层设计内副作用）。
- 禁调阈值、禁改球门、禁移动主判读 run（=run1 钉死）；禁第三轮重测（稳定性诊断之外的
  任何补跑须另卡等 PI）。
- 判分/裁定侧禁食标签派生证据（红线 v2②③）：B 臂工具返回内容仅供三席判读，
  runner/verdict 代码不得消费任何工具输出去生成档位/权重（票面字段解析除外）。
- truth/target_role/历史票/RUN 判据细节禁入 B 臂提示词（构建期 grep 断言：提示词模板中
  无 truth 字样、无簇角色字段引用）。
- key 走脚本文件读取，不落日志不打印。中间产物（票/日志/断点/成本/工具调用逐簇 json）全保留禁删。

## §10 预算
- 票量：45 簇 × 3 席 × 2 run = 270 票。API 调用：每簇会话 ≤8 轮+收尾 ≈ 3-6 次，
  上界 ≈ 270×7 = 1890 次调用（预算口径，非硬限）；实测成本列以 logs/cost_*.jsonl 为准。
- 机时：run 内三席并行，每席 ≈ 45 簇 × 30-60s ≈ 25-45 分钟/run；两 run 串行总计 ≈ 1-2 小时。
- 工具侧：query_marker 毫秒级；search_literature 首嵌模型加载一次（进程内），之后秒级。
- 零下载、零新数据、零生产写。

## §11 输入清单（只读，PRE sha 台账；起跑前复核未变，COMPLETED 附 POST 全等复核）
```
（由 scripts/btest_input_sha_check.py pre 生成，逐件 sha256 落 ledgers/INPUT_SHA_PRE.txt，
 覆盖：face/EV_DIGEST_SLIM_facev21.jsonl、ANNOT_INSTRUCTIONS.md、RUN4_TARGETS_v1.1.json、
 run3_M4_hotspots_v1.1.tsv、run4r_verdict.json、run3_object_B_table_v1.1.tsv、
 kb2_bscore_v4_truthfix_t_2ae2610d.py、FACEV21_VERDICT.json、ANN_{A,B,C}_facev21.jsonl+META、
 RUN7RG_VERDICT 源件（RG_VERDICT.json）、TIEP t1_revote.py + revote_matrix.tsv + tiep_counts.json、
 mcp_server/{server,eyekb_core,calllog,softflags}.py、markers_v6_retina_repair.json、
 markers_v6_face_increment.json、EYEKB_DB_POINTER.yaml、本 PREREG 件）
```

*BTEST 预注册 v1.0；本件落纸取 sha 后方许构建与起跑。卡 t_fb660dfe。*
