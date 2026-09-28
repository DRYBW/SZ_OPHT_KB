# 仓重同步登记（本卡未 push）
登记卡: t_6848d3de (RAGFIX2 D21) ｜ 日期: 2026-09-28
动过的仓面（EYEKB_REPO 镜像源=/mnt/D/EyeKB）：
1. kb/literature_db/EYEKB_DB_POINTER.yaml 追加 v2.4.1 块 + 块内两处文字修正（未触任何既有行；
   追加前后缀逐字不变断言通过）
   pre  sha256=12a4462eaf819ce535fce77ddcaaa324fdf08c72584ccbb4ebc550436a1270e0
   final sha256=c7f2e0f7d583cfc56ce8bfb821b0517513e81316e416b55ecd0aa30d1f6e15c7
2. plans/rag_fix_20260928/BRIEF_RAGFIX2.md 新文件（卡体所指任务书缺件，由执行方依卡体+
   RAGFIX_DECISION_1 重建补录，头注已声明）
3. plans/rag_fix2_v25_20260928/ 全目录（脚本/台账/门结果/白名单/NOTE）
未动: kb/markers/*.json 本体与两 INERT 旁挂件（双 sha 台账见 ledgers/）、mcp_server/、evals/ 冻结件、
      kb_chain_audit_20260928/（禁写红线全程未触）、rag_gap_20260928/。
OcularKB 侧 v2.4.1 库（1.03GB）不在 EyeKB 仓；rag_snapshots 面是否收 v2.4.1 由同步执行卡裁定
（默认不收=不新增大文件，沿 v2.4 先例）。
纪律: 由协调者按 REPOSYNC 管线（exec6 镜像+脱敏扫描）择机重同步；本卡零 push。
