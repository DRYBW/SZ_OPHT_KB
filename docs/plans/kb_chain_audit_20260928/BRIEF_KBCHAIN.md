# BRIEF_KBCHAIN — 全库引用链误引审计（只取证不修，D20）

## 上游与继承
- 放行：PI 2026-09-28"缺文献的补文献/能跑就跑"语境+RAGFIX 抽 20 复核发现既有链确诊误引（eutils 建链通道 PMID 错位：note 描述真实眼科文献、PMID 指向无关论文）——该模式覆盖 KB6/KB9 建链期，必须全量定界（对应 RAGFIX block 问句 P2=立项批准）
- 已有账（起点不作空白）：rag_fix_20260928/chain_audit_random20.tsv（6 确诊+1 存疑逐条）、_raggap_errata_v1.json（LILRB2 已撤证）、out/e2r_quality_findings.tsv（120 对 pmid_context 无 PMID 字段等 4 项存储缺陷）

## 任务（预注册判据先落纸）
1. **分层全检/抽检**：S1 层=KB6/KB9 建链期产物**全检**（REVCAND_KB6_v2 修订链、k9 新条链、E2R 白名单 100 对——已知高危面一条不落）；S2 层=其余历史链按库×年份×基因分层随机抽 15%（seed 冻结）；每链 EPMC eutils 题录复核三判据（PMID 可解析/标题与基因词面相关/与断言语境相符），判级 good/错配/存疑，逐链留原始返回 ledgers/。
2. **分档误引率表**：全检层逐档、抽检层计抽样误差（二项 95%CI），输出"哪条通道/哪批建链可信度几何"的定界结论。
3. **撤证候选清单**：确诊错配逐条给处置建议（撤证/换 PMID/降 weak），**只列不动 kb**——修链执行卡等 PI 看账后批。
4. **eutils 通道缺陷取证归因**：错配的成因定位（ID 错位/检索串扰/搬运截断），给建链工具修复建议（供 RAGFIX2/未来建库卡继承"禁裸用 eutils 通道回填"告诫）。

## 领地与红线
- 只写 /mnt/D/EyeKB/plans/kb_chain_audit_20260928/；kb/、plans 各在跑与已收卡目录只读（RAGFIX2 并行在跑，勿写 rag_fix_20260928/batch_v25/）；零生产写零 LLM 判读；网络=EPMC 元数据级零全文；完成或遇阻必须落卡；分批落盘。
