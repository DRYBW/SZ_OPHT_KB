# ROUNDTWO_VERDICT — KB9 注册申请包外审链总登记（终态：ACCEPTED / 过外审待 PI 批注册）

登记卡：t_62bb0dfe ｜ 日期 2026-09-27 ｜ 登记方 AGENT_ROLE（本卡＝审核与重装执行方，签发方＝外部模型）

## 1. 裁定模型登记（铁律：登记实际裁定模型）
- **全部裁定者 = REVIEWER_LLM**（LLM_CHANNEL LLM_CHANNEL 直连流式，reasoning_effort=xhigh，max_tokens=16000/8000）。
- **qwen3.8max（LLM_CHANNEL）降级通道备而未用**：本轮次链内 REVIEWER_LLM 直连全部拿到回稿（含 attempt=2 重试成功两次），未触发 503 连败降级条件；预置降级件沿用 recheck/qwen_fallback_send.py（D6a 预授权），未执行。
- 通道留痕：round4 attempt=1 TimeoutError(2400s)→attempt=2 OK（810s）；round5 attempt=1 OK（23s）；round2 xhigh attempt=1 OK（378s）+ 同轮 high 预检件一份（登记为 REVIEWER_LLMROUND2_REPLY_high_PRECHECK.md，非正式档）。发送器=register/scripts/REVIEWER_LLMxhigh.py（reasoning_effort=xhigh 直连变体，源自既有件 verbatim）。

## 2. 审链时间线（各轮 prompt sha 见 round*/PROMPT_SHA256.txt）
| 轮 | 对象 | 裁定 | prompt 字符 | 回稿 | 用时 |
|---|---|---|---|---|---|
| R1（09-27 午前，登记于 recheck/） | KB9 执行前设计 | 修订后再冻结（接受14/待PI5） | 6345 | 5172 chars | 295s |
| R2 | 注册包 v2.0 | **REVISE**：9 闭合；A06/A09/A12/A13/A19 未闭合+强制话术1–8+284=283+表头 | 19637（sha 8f4f1c0f…；原件后被 v2.1 再生覆盖，差异已登记台账 §4） | 4244 chars | 378s |
| R3 | 注册包 v2.1（含反事实复算） | **REVISE**：A09/A12/A13 闭合；A06/A19 未闭合；最小修订清单 1–5（纯文本项，明确不要求补跑） | 39621 | 3677 chars | 1002s |
| R4 | 注册包 v2.2 | **REVISE**：清单 1/2/4/5+话术 1/4/7 闭合；唯一残留=判件反事实表"真阴性"一格 | 45085 | 1221 chars | 810s（attempt2） |
| R5 | 判件 v2.2 单项复验（唯一改动件；包体 sha 078e493b… 零改动声明） | **ACCEPTED（可送 PI 批注册）** | ≈14K | 240 chars | 23s |

## 3. 签发文本（R5 verbatim）
① 单项复验：**闭合**。
② 总签发：**ACCEPTED（可送 PI 批注册）**。本轮签发不等于 PI 批准注册，也不授权执行、接线或激活；P1=22/33 FAIL、P2=0/33 PASS 维持不变。
③ 《KB9 眼表词条注册申请包 v2.2 第五轮外审意见：ACCEPTED——单项残留复验闭合，可送 PI 批注册；未授权注册或激活》

注：签发后包体唯一后续改动=第 5 行状态行改为「过外审待 PI 批注册」+审链指针（记账性，零内容/零裁决变更；签发时包体字节 sha=078e493b…4c1fdf，终态 sha 见 REGISTER_SHA_MANIFEST.txt §5）。

## 4. 接受项终态闭合索引（14/14）
A01→包§0｜A03→§2+A03_OVERLAP_REGISTRY.tsv｜A05→§4 AV2-1..4｜A06→§3+A06_R1_ITEM_SCOPE_TABLE.tsv（身份混写修正：MG=Müller/Astro=星形/Micro=microglia，基因锚双证）｜A07→§6 诊断表规格｜A09→§5+A09_VOCAB_MAPPING_SNAPSHOT.tsv（38 候选全映射）｜A11→§9+EDITORIAL_NOTE①｜A12→§4 AV2-5 三态门（历史 ON=未证，下游强制项）｜A13→§9（缓存等同性/完整请求/tc_ref 不授权/lit 排除规则+本轮未落留档如实登记）｜A15 措辞→§8-1+§8 话术作废条｜A16→§7 算术模板（21+4−3=22 自洽）｜A17→§8-2/3｜A18→§8-4+§10-6｜A19→§8-6+A19_MINPOOL_EXEMPT_BY_ENTRY.tsv（逐词条 20 行）+MINCORE=3 生效时点条。

## 5. 待 PI 决策面（本卡零执行，禁夹带项全部未动）
1. **批不批注册**：案 A（仅 Melanocyte+Schwann 两词条，不施加 R2/R3；未单独跑票面）或案 B（全量四词条+R1/R2/R3+装配规则 v2；票面 22/33 FAIL、0/33 PASS）。
2. **suprabasal 条去留**（A15 子项）：判件 v2.2 供证据——3 core 统计值满足 §1.2 数值门槛且可复现（实现合规/文献通道不代签）；KB7"0 全过"不能作为正确执行判据后的否定结论（反事实 0→15，含 3 core）；Limbus Fib 零结果对反事实稳健；髓系共享+96.9% 供体集中限制随条呈报。
3. **A04** 独立眼表验证线（涉下载须另行批准）；**A08/A14** 下一波球门与配对重投预算；**A10** 旁挂表路线（PI D12 已裁不采，仅存档）。
4. A12 历史 ON 门、A07 诊断表首跑、22 视网膜簇完整 ranking 一致性、逐条 lit 同源排除留档=**注册条款确立但未执行**，任何激活前 run 必须先过（§10-6 义务总表）。
5. KB7 gaps 节"suprabasal 0 基因/纤维四亚型全零"两条断言之源头勘误归 PI（判件未触 KB7 发布件）。

## 6. 零接线/零 kb 写自证
本卡写路径仅：register/**（新目录）与 KB9_BUILD_REPORT.md 文末 EDITORIAL_NOTE 追加（原文前 7485 字节 sha=f4826826…364a80 追加前后一致，数字与裁决零改动）。kb/、mcp_server/、evalset/、面板冻结卷、out/、build/、recheck/ 全部只读；sha 对账=register/REGISTER_SHA_MANIFEST.txt。
