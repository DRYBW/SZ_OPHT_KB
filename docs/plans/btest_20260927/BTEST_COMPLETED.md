# BTEST — RAG 自由查询 A/B 正式验证 完成报告（D9，2026-09-27）

- 卡：t_fb660dfe ｜ 判据件：BTEST_PREREG_v1.0.md（sha 160c53b7a3017e7f9130e1e3781c0d9b258ea8661b097a086f775e71feec2a30，落纸先于一切构建/起跑）
- 放行：USER_DIRECTIVE_20260927_scoring_wave.md 追加二 D9+D11 ｜ 设计蓝本：RAGANNO §B

## 总判定（一句话）

**稳定性门过（44/45=97.8%≥90%）→ 判：B 不达，维持 A 唯一形态。**
主判读 run1 C4：R1=17/22（部分带）但 **R2=2/23 破门（≤1）**——破门的恰是 FACEV21 三拆弹修掉的
两个鼠簇伤害点 Q7::52/Q7::58：**判读卡撤 kb 行的拆弹修复在自由查询臂不可复制**——席位自己
query_marker 一遍，v6 面板的 AC-ranking 伪影原样回流。两 run 同向（run2 R2 亦破、同两簇），非随机波动。
按预注册判读矩阵，禁第三轮重测；替代/后续修复归 PI。

## §1 三道闸门（全 PASS）

| 闸门 | 结果 |
|---|---|
| FACEV21 C4 逐字复刻（vs 已发布票档 45 簇 consensus/mode） | PASS 45/45 |
| C2b 双实现对账（vs TIEP 发布件 revote_matrix face=FACEV21 name_C2b） | PASS 45/45 |
| R1 锚点复现 | PASS 19/22 |
| 防泄漏静态检查（B 卡无 truth/target_role/kb/lit/pred_hint 字样） | PASS 45/45 |
| 输入 POST sha vs PRE（32 件冻结件） | PASS 逐字节全等 |
| 逐簇 calllog 非空硬断言（服务端 1417 行 btest_d9 留痕 × 时间窗×pid 归因） | PASS 270/270 簇零缺失 |

## §2 稳定性门（先行，过门方有资格判读）

- run1 vs run2 逐簇 C4 共识名一致：**44/45 = 97.8% ≥ 90%（≥41/45）→ 过门**。
- 唯一不一致：Q7::58（run1=AC majority ｜ run2=tie 无名）——恰为伤害簇，说明该伪影把判读推到
  "错名/弃权"随机边缘，本身就是 B 形态不稳的证据。
- 席位级 identity 一致率：A=44/45（qwen3.8-max）、B=39/45（glm-5.1）、C=31/45（deepseek-v3.2）；
  C2b 共识一致率 43/45。主判读票=run1（预注册钉死）；run2 为诊断列（R1=17、R2=2、保全过——与 run1 同档）。

## §3 主判读（run1，C4 票规，球门一字不降）

| 口径 | RUN4-r（A 基线） | FACEV21（A 现役） | **B run1** | B run2（诊断） |
|---|---|---|---|---|
| R1 热点命中 | 15/22 | 19/22 | **17/22** | 17/22 |
| R2 对照翻错 | 1/23 | 0/23 | **2/23（破）** | 2/23（破） |
| 保全 Q4::15∧Q5b::13 | — | 双过 | 双过 | 双过 |
| 档位 | — | — | **B 不达（R2 破门）** | 同 |

R2 破门簇：Q7::52（run1 票 A=AC/B=coarse:RGC/C=undet → tie 无名=翻错）、Q7::58（AC majority 错名）。
R1 五失中 Q1::1/Q1::9/Q3::13 两臂同错（结构难簇，非本轮变量）；净损失=lost 4 簇（下表）。

## §4 逐簇净损失归因（lost 4：vs FACEV21 由对转错）

| 簇 | truth | B 票（run1） | 归因 |
|---|---|---|---|
| Q7::52 | RGC | AC / coarse:RGC / undet | **query_marker 重新导入 v6 面板 AC-ranking 伪影**：席位拿鼠基因查库（鼠 symbol 大小写错位命中稀）后转查 'AC'/'RGC' 类名，Calb1/Grin3a 型假命中把 AC 顶前——与 RUN7RG (b) 拆弹的病灶同源，但拆弹修在卡片渲染层，工具路径不经过该修复 |
| Q7::58 | RGC | AC / AC / coarse:neuron | 同上（run2 翻成 tie——伤害带内方差） |
| Q2::22 | （A 臂对） | MG / MG / coarse:glia | **基因先验误导原样复发**（GLUL/VIM/CLU 共表达）：RUN7RG §6 反向验证已证误导源主要在基因集先验非仅词条；A 臂靠词条+hint 结构化上下文压住，自由查询臂逐次 marker 检索反而强化 MG 读数 |
| Q5b::35 | AC | AC(gradeC!) / AC(B) / undet | 正确名但**判读纪律降级**：席A给 AC 打 grade C → C4 有效票仅 1 → tie 无名；自由查询长会话中 grade 判序漂移 |

## §5 并列读（C2b 机械重算，零额外票，D11 过渡条款；不进门禁）

| 票池 | 协议 | R1 | R2 翻错 | 具名 | 保全 |
|---|---|---|---|---|---|
| B run1 | C4 | 17 | 2 | — | 过 |
| B run1 | **C2b** | **20** | **2** | 43/45 | 过 |
| B run2 | C2b | 19 | 2 | 41/45 | 过 |
| A FACEV21 | C2b | 19 | 0 | 42/45 | 过 |

**结论对票规则不敏感**：C2b 把 B 的 R1 抬到 20/22（≥A），但 R2 恒破 2——伤害线是取证方式的问题，
不是破平规则的问题。D11 主档切换不改变本轮档位。

## §6 成本对照（D9"成本必录"；run1=B 完整一考 vs A=FACEV21 一考）

| 指标 | A 臂（FACEV21，EV_DIGEST 5簇/批） | B 臂 run1（自由查询 1簇/会话） | 倍率 |
|---|---|---|---|
| API 调用 | 27 | 707（A220+B231+C256） | 26× |
| 工具执行 | 0 | 702 次（marker 334/lit 233/composition 135） | — |
| prompt tokens | 79,845 | 6,572,448 | 82× |
| completion tokens | 37,835 | 204,987 | 5.4× |
| 墙钟 | 三席串行 <40 分钟 | 波内并行 38 分钟（最慢席 glm-5.1 50s/簇） | ≈同 |
| 协议摩擦 | — | forced_final 17/135 会话（B 席 12、C 席 5）；零提醒即全具证 | — |

（B 臂两 run 合计 prompt ≈ 13.3M tokens；稳定性要求本身再乘 2——自由查询形态的"可复现税"。）

## §7 机制结论与三档清单更新建议（决策归 PI，本卡不接线不动面板）

1. **换取证方式 ≠ 换证据**：B 臂拿到的是同一套面板/文献库的排序伪影与基因先验，FACEV21 的
   卡片层三拆弹（撤行/判序注记）全部被工具路径绕过。本轮直接支持 RAGANNO 的核心口径——
   "证据面质量挂在词条+拆弹规则上，不在裸检索上"。
2. **修复优先级推论（供 PI 立项参考，本卡不做）**：若要做 B 形态，修复须下沉到共享层——
   ①query_marker 的鼠簇/跨物种 ranking 治理（Q7 两簇病灶在库侧，卡片撤行只是症状层）；
   ②自由查询会话的 grade 纪律锚（Q5b::35 型降级）；③稳定性门虽过，席位间一致率梯度大
   （44/39/31），deepseek-v3.2 单席噪声是主要方差源。
3. **对外口径红线不破**：19/22 仍只属 A 形态冻结面疗效；B 形态=未通过验证，禁以任何档位
   叙述进对外材料；本轮为 45 簇视网膜面，禁外推眼表/线上。
4. RAGANNO 三档清单建议改一行：B 形态由"需要一步验证"→"已验证·不达（D9 09-27，维持 A 唯一
   形态；修复路线见本件 §7.2）"。是否落改 WIKI/评估件归 PI/协调侧另卡。

## §8 产物与证据链

- 判读件：scoring/BTEST_VERDICT.json（rows=45 全票面）、out/per_cluster_table_btest.tsv、
  out/stability_mismatches.tsv、out/calllog_audit.tsv（270 簇）、out/cost_summary.tsv
- 票档：annotation/ANN_{A,B,C}_btest_run{1,2}.jsonl + META（prereg/face/instr/server sha 内嵌）
- 会话证据：annotation/ballots/、annotation/toolcalls/（逐簇工具入参+执行标记）、
  logs/cost_run{1,2}_{A,B,C}.jsonl（逐簇 api/工具/时长/token/forced_final）
- 过程件：scripts/{btest_runner,btest_verdict,btest_input_sha_check,btest_path_grep_check}.py +
  btest_chain.sh、logs/{seat_smoke,path_grep,leak_check_static,chain_status,run*,verdict*}、
  ledgers/INPUT_SHA_{PRE,POST}.txt（32 件全等）
- 执行流水：15:16 run1 起跑（三席并行）→ 15:54 run2 → 16:32 CHAIN DONE；
  服务端 calllog 独立留痕 1,417 行（tag=btest_d9，与 A2 真实流量分母隔离）
- 红线合规：冻结件零触碰（POST 全等）；产物只落本目录；零下载；禁第三轮已执行（未补跑任何票）

*BTEST COMPLETED v1.0（2026-09-27 16:4x）；卡 t_fb660dfe。*
