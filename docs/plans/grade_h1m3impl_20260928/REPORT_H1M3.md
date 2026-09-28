# REPORT_H1M3 — GRADE 判序锚 H1-M3 实装终报（卡 t_e0f94d4f，2026-09-28）

**判定：两门全 PASS，实装收口。** 领地=判读协议 ANNOTATION_PROTOCOL v1.3 + 判读 runner 定名链组件；
mcp_server/、kb/、打分栈（E 系）、evalset/ 零触碰（与并行卡 KBGOV-B5IMPL 互斥面已核）；仓面零 push。
生效制=**向前生效**（v1.3 §9.4：2026-09-28 落款后预注册 run 起用，历史冻结判读零回改）。

## 1. 交付清单

| 件 | 路径 | 说明 |
|---|---|---|
| 协议件 v1.3 | /mnt/D/EyeKB/plans/ANNOTATION_PROTOCOL_v1.3.md | copy 不 move；§0-§8 逐字继承 v1.2（diff 实证仅 header 2 行），唯一增补 §9 判序锚 H1（档位/模式/生效边界/H1-X 处置说明/红线） |
| runner 定名链组件 | scripts/h1m3_runner_t_e0f94d4f.py | 票形解析（C2b 决策件参考实现逐字语义）+ H1 锚（none/S/M/M2/M3/X × 模式 A/B）+ C4/C2b 计票（tie/弃权沿 C2b 不动）；自测 8 组 PASS（含 Q6::31 通胀案 X 升/M3 挡的最小机制复现） |
| 预注册件 | PREREG_H1M3.md（sha 14fc3f8f… 先落纸后开算，15:03:57） | 冻结预期全量入文（§2 逐档表/§3 三段规格） |
| 门1 复算门 | scripts/g1_…py + out/g1_verdict.json + out/g1_perarchive.tsv | **PASS** |
| 门2 回归门 | scripts/g2_…py + out/g2_p1_columns.json + g2_percluster.tsv + g2_ballot_flags.tsv | **PASS** |
| 台账 | ledgers/{PREREG_H1M3_SHA,SHA_PRE_inputs,SHA_NEW_ARTIFACTS,SHA_POST_readonly_recheck}.txt | sha 全链 |

## 2. 门1 = 复算门（9 归档 × H1-M3(模式B)，经**实装组件**重放，非锚件脚本复跑）

对照件=冻结锚件 grade_anchor/data/counterfactual_summary.json（H1-M3 行，SHA_PRE 在册）。
**逐档全字段一致**（n_clusters/n_promoted/hit_rate/transitions 全键/named_base→cf/R1/R2 集合）：

| archive | prom | 翻正 | named | R1 | 一致 |
|---|---|---|---|---|---|
| RUN4-r | 0 | 0 | 39→39 | 15→15 | ✔ |
| RUN7RG | 5 | 1 (Q5b::2) | 37→38 | 17→17 | ✔ |
| FACEV21 | 0 | 0 | 42→42 | 19→19 | ✔ |
| BTEST-run1 | 5 | 1 (Q5b::35) | 40→41 | 17→18 | ✔ |
| BTEST-run2 | 0 | 0 | 39→39 | 17→17 | ✔ |
| RUN5 | 4 | 1 (Q6::13) | 22→23 | – | ✔ |
| RUN6A | 2 | 0 | 24→24 | – | ✔ |
| RUN6B | 1 | 0 | 23→23 | – | ✔ |
| KB9 | 7 | 4 (Q6::16/26/29/30) | 17→21 | – | ✔ |

合计=**升 24 / 隐藏名正确 22/24=91.7% / 翻正 7 / 新错 0 / 回归 0**——与 GRADE_ANCHOR §3 网格/§4 全等。
R2 集合按内容比较（锚件列表序=其进程 set 迭代序，Python 哈希随机化不可逐字节复现；内容全等即一致，口径如实声明）。
无"就地改锚"事件：0 档差异。

## 3. 门2 = 回归门（OBLIGRUN v2 票面 kb9_face_v2.1，99 票=33 簇×3 席）

- **基线复现**：组件 `C2b∘none` 重放 → 逐簇 consensus/mode 与 obligrun 发布件 oblig_percluster.tsv
  **33/33 全等**；P1=**26/33**，命中簇清单与 oblig_verdict.json 全等（证明实装组件与当期实现同源）。
- **敏感性主列（单独成列）**：`C2b ∘ H1-M3(模式B)` 重算 P1=**26/33，delta=0，逐簇共识差异=0**——
  锚件 §4 "C2b 吸收性（grade 下限化不改 NAMED/COARSE 票形→结构恒等）"的预言在当期新票面复核成立。
  **主口径当期 26/33 不动、VERDICT_OBLIGRUN_v2.md 不回改**（本行数字仅入本报告与 out/ 件）。
- **票面清点（差异如实登记）**：具名∧C=**13 票**（A 席 0 / B 席 glm 4 / C 席 deepseek 9）；
  M3 过门升（anchor_applied）=**11**、未过门（namedC_noanchor，两门皆 unresolved）=**2**（B 席 Q6::2/Q6::30）。
  13 票隐藏名 **全部==truth**——"过度保守弃正确名"形态在当期新票面第三次独立复现；
  未升 2 票无后果（同簇另席已 carry，Q6::2/30 共识不受扰动）。
- **C4 参考列（非主口径，不进任何球门）**：同 99 票 `C4∘none` P1=18/33（定名 20）→ `C4∘M3` P1=23/33
  （定名 25，**+5 簇全为翻正**）——锚在 C4 语义下的增量量化，与 §2 九档口径同向。

## 4. 协议 v1.3 §9 要点（成文件为准，此处索引）

§9.1 具名票 grade≥B 协议下限、具名∧C=非法票形；§9.2 档位族+M3 推荐（technical 不参与，3A 同构）+
**每 run PREREG 必须声明 H1档位/模式**（与 §8 票规声明并列硬条款）；§9.3 模式 A 拒收回炉/模式 B 自动下限+旗，
球门不动、翻正案单独列账；§9.4 **向前生效**、不回改历史、不改写已批准票规计票语义（C4/C2b 各自语义守恒）；
§9.5 **H1-X 处置说明**：RUN5 Q6::31 通胀案（双错名互相坐实假多数，唯一实证新错）由 M3 门条件挡下，
**X 禁选**；§9.6 实装组件+两门留痕+kb/mcp 生产接线交 REPOSYNC3 同源；§9.7 H2 软提示=激活类另报、
H3 旗=A4 复盘 shadow、ANNOT_INSTRUCTIONS 反例行登记（kb/ 禁动）；§9.8 §0 红线对 H1 全档同等生效。

## 5. 领地审计（零写入断言）

SHA_PRE（24 件输入）→ SHA_POST 复验全等=**0 篡改**；本卡全部新写入=
plans/grade_h1m3impl_20260928/** + plans/ANNOTATION_PROTOCOL_v1.3.md 两处（SHA_NEW_ARTIFACTS 全列）。
mcp_server/、kb/、evalset/、obligrun_20260928/、kb_gov_20260928/、grade_anchor_20260928/、
历史 runner R1-R6 原件：本卡零写（历史件 sha 复验在册；并行卡 B5IMPL 对 mcp_server 的动作为其领地，与本卡互斥面=无交集文件）。
另：PREREG §2 手抄预期表发现一处笔误（RUN6A 23→23，锚件真值 24→24），已按"冻结件不回改"惯例出增量勘误件
ERRATA_PREREG_H1M3_v1.0.md；门1 对照对象=冻结锚件 JSON，判据与结论不受影响。

## 6. 观察条款（追加五要求）与下一步

1. **实装轮自然观察点**：首个按 v1.3 §9.2 声明的新预注册 run，报"具名∧C 存量（模式 A 应=0 /
   模式 B anchor_applied+noanchor 逐案账）× 翻正/新错账"，交 A4 复盘；禁按 run 临时改措辞/档位。
2. **生产同源接线**：kb/ 与 mcp_server/ 两处票面校验的 §9 条款接线 + ANNOT_INSTRUCTIONS 反例行 +
   RUNNER_WATCHLIST 分叉指引补"H1 声明行"——全部登记交 **REPOSYNC3 收编**（本卡禁动领地）。
3. **激活边界重申**：本卡=接线级实装（协议成文+组件落盘+两门验证）；H2 尾句进判读卡冻结件、
   KB1/注册包接线等激活类动作**另报 PI**（追加五纪律）。

*REPORT_H1M3 v1.0；卡 t_e0f94d4f；两门 PASS=1，无停卡事件，无就地改锚事件。*
