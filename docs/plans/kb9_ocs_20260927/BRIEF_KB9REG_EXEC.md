# BRIEF_KB9REG_EXEC — KB9 案 B 注册执行（写 kb/ overlay，默认 OFF，D17）

## 上游与继承
- 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加一 D17；注册包过外审终态=kb9_ocs_20260927/register/REGISTER_PACKAGE_v2.md（REVIEWER_LLM 五轮 ACCEPTED，签发语"未授权注册或激活"→现由 PI 明确授权**注册**、仍不激活）
- 义务边界：§10-6 激活前义务清单未全清（A12 历史 ON 门/A07 诊断表首跑/22 视网膜簇一致性/lit 同源排除留档）——故本卡**只登记路由、默认 OFF，禁激活**；激活另卡等 PI + 义务 run。
- 票规语境：案 B 票面 P1 22/33 FAIL 是 C4 历史口径；C2b（票规 v2，PI 已批向前生效）下同票机械重算 29/33 过门（TIEP 实证，零翻案）——注册申请附此对照，不改 C4 历史 FAIL 记录。

## 任务
1. **装条**：案 B 四词条（Melanocyte/Schwann/Conj_suprabasal/Limbus_sclera_fib_C1）+ 屏蔽/适用性规则 + 装配规则 v2，按 KB7-WIRE 旁挂先例写成 kb/ 新版本 overlay 文件；**baseline/现役文件字节不动**（copy 不 move），旧产物留档可 diff；每条带 CL id+OLS 回证+逐基因 PMID 链（补文献=装条时把 register/ 里的证据链落到条内字段）。
2. **登记路由默认 OFF**：MCP 侧登记为可选库但**默认不纳入响应**（机读自证：ON 前后默认响应零变化，仿 KB7-WIRE/ACT 的 A5 式验收件）；服务版本按版本化惯例 bump 但默认行为不变。
3. **补 wiki**：新条进 docs/wiki（数据资产.md 词条登记、决策记录.md 注册落款、体系盘点更新泪腺/眼表新条状态、检索索引收录）；仓镜像同步（脱敏管线，push 前协调者测试门同 REPOSYNC）。
4. 产出 KB9REG_EXEC_NOTE.md：装条清单+OFF 自证 sha 台账+§10-6 义务遗留表（下一步激活前必须清的项）+wiki/仓同步对账。

## 领地与红线
- 写路径：kb/ 下**新建版本化 overlay 文件**（不原地改任何现役件）+ docs/ + 仓镜像；禁碰 mcp_server 默认响应逻辑、evalset 冻结卷、plans 在跑四卡目录（KBX/KBGOV/PME3/GRADE）；
- 禁激活/禁接线生效（默认 OFF 是唯一状态）；完成或遇阻必须落卡；分批落盘。
