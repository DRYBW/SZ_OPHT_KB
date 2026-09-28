# 仓重同步登记（本卡未 push）
登记卡: t_b94d0999 (RAGFIX3, PI 整链授权=USER_DIRECTIVE_20260928 追加五) ｜ 日期: 2026-09-28
动过的仓面（EYEKB_REPO 镜像源=/mnt/D/EyeKB）：
1. kb/literature_db/EYEKB_DB_POINTER.yaml 追加 v2.4.2 块（未触任何既有行；
   追加前缀逐字节不变断言通过=pointer_register3.py 落码）
   pre  sha256=c7f2e0f7d583cfc56ce8bfb821b0517513e81316e416b55ecd0aa30d1f6e15c7 (=ragfix2 final, 基线绑定)
   final sha256=a907260969131cdfe9b3f59860ad58c9168d9c132ad8f754914fa3d95d64e882
2. plans/rag_fix3_20260928/ 全目录（任务书 BRIEF_RAGFIX3.md 为协调者预置，本卡新增：
   判读矩阵/扫描与下载台账/门结果/8 脚本/NOTE/sha 台账）
未动: kb/markers/*.json 本体与旁挂件、mcp_server/、evals/ 冻结件、plans/rag_fix_20260928、
      plans/rag_fix2_v25_20260928、plans/obligrun_20260928（OBLIGRUN 在跑）、rag_gap_20260928/、
      kb_chain_audit_20260928/（禁写红线全程未触，SHA_PRE→POST 复核 18/19 OK，
      唯一差异=本卡指针块，见 ledgers/SHA_POST_verify_20260928.txt）。
OcularKB 侧 v2.4.2 库（1.076GB: chunks.parquet 1076.4MB + papers.jsonl 3884 行 +
build_stats.json + manifest.yaml）不在 EyeKB 仓；rag_snapshots 面是否收 v2.4.2 由同步执行卡
裁定（默认不收=不新增大文件，沿 v2.4/v2.4.1 先例）；work/xml3/ 93 篇源 XML 与
chunks_ra3_raw.jsonl 为本卡复算证据，保留于 plans/rag_fix3_20260928/work/（中间产物全保留令）。
纪律: 由协调者按 REPOSYNC 管线（exec6 镜像+脱敏扫描）择机重同步；本卡零 push。
