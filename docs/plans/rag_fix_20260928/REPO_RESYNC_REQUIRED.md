# 仓重同步登记（本卡未 push）
登记卡: t_d0bea5a6 (RAGFIX D19) ｜ 日期: 2026-09-28
动过的仓面（EYEKB_REPO 镜像源=/mnt/D/EyeKB）：
1. 新增 kb/markers/_raggap_errata_v1.json (sha256=10da875a40252d5dd7014e371424bc10a996df6ae79a76c6d68249bf801ffced)
2. 新增 kb/markers/_raggap_c_linkbackfill_v1.json (sha256=b832a694035018863e58e8658335ff95bcdcdddec91f683fa4c3633bc8b17841)
3. kb/literature_db/EYEKB_DB_POINTER.yaml 追加 v2.4 块 (新 sha256=12a4462eaf819ce535fce77ddcaaa324fdf08c72584ccbb4ebc550436a1270e0; 前缀逐字不变已校验)
4. plans/rag_fix_20260928/ 全目录（脚本/台账/门结果/NOTE）
未动: kb/markers/*.json 本体（含 markers_v6_retina_repair.json，双 sha 台账）、mcp_server/、evals/ 冻结件。
OcularKB 侧 v2.4 库不在 EyeKB 仓；rag_snapshots 面是否收 v2.4（1.02GB）由同步执行卡裁定（默认不收=不新增大文件）。
纪律: 由协调者按 REPOSYNC 管线（exec6 镜像+脱敏扫描）择机重同步；本卡零 push。
