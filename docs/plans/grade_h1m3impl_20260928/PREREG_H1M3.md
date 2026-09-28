# PREREG_H1M3 — H1-M3 判序锚实装的预注册门规格（卡 t_e0f94d4f，2026-09-28）

- 任务书：/mnt/D/EyeKB/plans/grade_h1m3impl_20260928/BRIEF_H1M3.md
- 依据锚件：/mnt/D/EyeKB/plans/grade_anchor_20260928/GRADE_ANCHOR.md（H1-M3=ie=pass ∨ res=pass，
  升24/隐藏名正确91.7%/翻正7/新错0/回归0；§5 实装路径草案）
- 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加五（PI 整链授权"往下推进"，
  GRADE-H1M3 实装=接线级修复，带回归门与观察条款；激活类动作另报）
- 票规基准：PROTOCOL_VOTING_v2_C2b.md（tie/弃权处理沿 C2b 不动）；协议件 ANNOTATION_PROTOCOL v1.2→v1.3（copy 不 move）
- 性质：本件为开算前冻结规格；sha 先落纸（ledgers/PREREG_H1M3_SHA.txt），后跑门。

## 0. 领地与禁动（逐字沿任务书）

领地=ANNOTATION_PROTOCOL 升 v1.3 + 判读 runner 定名链实装（本目录内新组件）。
**零写入**：mcp_server/、kb/、evalset/（只读）、打分栈（E 系）、obligrun_20260928/、kb_gov_20260928/、
grade_anchor_20260928/、历史 run 冻结 verdict 脚本（R1-R6 原件一字不动——实装=新组件+协议条款，
历史轮 runner 不回改，生效制=向前）。与并行卡 KBGOV-B5IMPL 互斥（其领地=mcp_server/，本卡禁写）。
仓面零 push（登记件交 REPOSYNC3 收编）。

## 1. 实装规格（判读 runner 定名链组件 scripts/h1m3_runner_t_e0f94d4f.py）

1. 票形解析 parse_ballot：逐字沿 t1_revote.py/RUNNER_WATCHLIST H3 语义（NAMED/COARSE/UNDET/MISSING）。
2. H1 判序锚（档位=H1-M3，模式=**B 自动下限**，对齐锚件反事实语义）：
   - 对 kind==NAMED ∧ grade==C 票：若 gates.identity_evidence=='pass' ∨ gates.resolution=='pass'
     → 生效 grade 下限化 B，记 `anchor_applied` 旗；technical 三门不参与（3A 禁降级项，锚件定义）。
   - 未过门 → 不升，票保持 C，记 `namedC_noanchor` 旗（C4 下=不入定名数，C2b 下=照 v2 规则入数——
     H1 治 grade 语义漂移，不改写已批准票规的计票语义，锚件 §22 互补不冲突条款）。
   - coarse:X/undetermined 合法弃权形态不动；tie/abstain 处理沿 C2b（rule_c2/c2b_mode 逐字）与 C4（ballot/c4 逐字）各按其版。
   - 模式 A（拒收回炉）作为 PREREG 可声明档位提供开关；本波两门验证均按模式 B（锚件反事实=模式 B 语义，
     翻正7/新错0/回归0 仅在 B 下成立；A 拒收=降C票不入数，无翻正）。
3. 自测：锚升/不升/COARSE-UNDET 不触/模式开关四组用例断言 + C2b 语义五用例（沿 o10 selftest 逐字）。

## 2. 门1 = 复算门（9 归档反事实 × H1-M3，零 LLM 确定性重放）

输入（只读，sha 见 ledgers/SHA_PRE_inputs.txt）：
grade_anchor/data/ballot_matrix.tsv（1,817 行）；对照件=同目录 counterfactual_summary.json（H1-M3 行）。
本卡 runner 的 `c4 ∘ M3(模式B)` 对 9 archive（RUN4-r/RUN7RG/FACEV21/BTEST-run1/BTEST-run2/RUN5/RUN6A/RUN6B/KB9）
逐档重放，与锚件逐档一致（字段=n_promoted、promoted_name_hit_rate、transitions 全键、named_base、named_cf、R1、R2 集合）。

冻结预期（开算前抄录自锚件，全 9 档合计）：升 24 / 翻正 7 / 新错 0 / 回归 0；逐档：
| archive | prom | hit | 翻正 | named base→cf | R1 base→cf | R2 cf |
|---|---|---|---|---|---|---|
| RUN4-r | 0 | – | 0 | 39→39 | 15→15 | [Q1::4] |
| RUN7RG | 5 | 0.8 | 1(Q5b::2) | 37→38 | 17→17 | [Q7::52,Q4::23,Q7::58] |
| FACEV21 | 0 | – | 0 | 42→42 | 19→19 | [] |
| BTEST-run1 | 5 | 1.0 | 1(Q5b::35) | 40→41 | 17→18 | [Q7::52,Q7::58] |
| BTEST-run2 | 0 | – | 0 | 39→39 | 17→17 | [Q7::52,Q7::58] |
| RUN5 | 4 | 0.75 | 1(Q6::13) | 22→23 | – | – |
| RUN6A | 2 | 1.0 | 0 | 23→23（unchanged 33） | – | – |
| RUN6B | 1 | 1.0 | 0 | 23→23（unchanged 33） | – | – |
| KB9 | 7 | 1.0 | 4(Q6::16/26/29/30) | 17→21 | – | – |

判定：9/9 档全字段一致=PASS；任一不一致=**停卡上报（kanban_block），禁就地改锚**——差异逐档如实登记后交协调者。

## 3. 门2 = 回归门（OBLIGRUN v2 票面 99 票敏感性对照，kb9_face_v2.1，零 LLM）

输入：obligrun_20260928/out/ANN_{A,B,C}_oblig.jsonl（33×3=99 票）+ face/kb9_face_v2.1.jsonl；
当期主口径基准=oblig_verdict.json P1=26/33（**不动、不回改 verdict 件**）。
三段：
- (a) 基线复现：本卡 runner `C2b ∘ none` 重算 99 票 → 逐簇 consensus/mode 与 oblig_percluster.tsv 全一致、
  P1=26/33（证明 runner 与当期实现同源，这是"回归"的严格含义）。
- (b) 敏感性主列：`C2b ∘ M3(模式B)` 重算 P1，单独成列报数；冻结预期：P1 仍 26/33（grade 下限化不改
  NAMED/COARSE 票形→C2b 结构恒等，锚件 §4 吸收性预言在新票面复核）；named∧C=13 票（A 0/B 4/C 9，
  其中 M3 升=11、不升=2[B席 Q6::2、Q6::30 两门皆 unresolved]）；差异如实登记，任何≠预期=上报禁就地调。
- (c) 参考列（显式标注=非主口径不进任何球门）：`C4 ∘ none` 与 `C4 ∘ M3` 在同 99 票的 P1/定名数，
  量化锚在 C4 语义下的增量（对照当期 C2b 主读）。

## 4. 协议件 v1.3（新增 §9，§0-§8 与 v1.2 逐字同，copy 不 move）

§9 判序锚（H1）条款要点：①具名票 grade≥B 为协议下限，具名∧C=非法票形；②自动下限化档位=H1-M3
（ie∨res 至少一门 pass），technical 门不参与判序（3A 同构）；③每 run 预注册必须声明 H1 档位
（none/S/M3/X）与模式（A 拒收/B 下限+anchor_applied 旗）；④生效边界=条款落款（2026-09-28）之后预注册
run 起用，历史冻结判读一律不回改（与 PROTOCOL_VOTING v2 生效条款同构）；⑤H1-X 处置说明：纯一致性锚
（一律升）在 RUN5 Q6::31 实证制造"双错名互相坐实"假多数（唯一通胀案），本条款采 M3 门条件挡之，X 禁选；
⑥配套 ANNOT_INSTRUCTIONS 反例教学行（Q5b::35 run1 席A票形）以登记件形式给出（该文件属 kb/ 领地禁写，
交 REPOSYNC3 收编条款）。§9.7 H2/H3：本卡不实装（H2 软提示入判读卡冻结件=激活类动作另报；
H3 旗=复盘层，随 A4 口径），只在登记件声明待命边界。

## 5. 留痕与产物

本目录：PREREG（本件）+ scripts/{h1m3_runner,g1,g2} + out/{g1_perarchive.tsv,g1_verdict.json,
g2_p1_columns.json,g2_percluster.tsv,g2_ballot_flags.tsv} + ledgers/{PREREG sha,SHA_PRE_inputs,
SHA_NEW_ARTIFACTS,SHA_POST_readonly_recheck} + REPORT_H1M3.md + /mnt/D/EyeKB/plans/ANNOTATION_PROTOCOL_v1.3.md。
观察条款（追加五要求）：实装轮首个新预注册 run 的具名∧C 存量与 anchor_applied 账=自然观察点，登记于
REPORT 末节交 A4 复盘；禁按 run 临时改措辞/档位。

*PREREG_H1M3 v1.0：本件先 sha 落纸，后开算。完成或遇阻必须调 kanban_complete/kanban_block 落卡。*
