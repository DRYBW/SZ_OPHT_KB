# BRIEF_RAGFIX3 — 104 备选批处置 + v2.4.2 增量（PI 整链授权，追加五）

放行依据：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加五（"除了下载1G以上的需要我批准以外，其他的你往下推进就可以"）；
上游事实链：plans/rag_fix_20260928/RAGFIX_NOTE.md（v2.4 门③ FAIL 72.8%，残差归因含"8 单元仅备选104覆盖"）、plans/rag_fix2_v25_20260928/（v2.4.1 门③ 84.8% PASS，残差 14=7 备选覆盖单元另案+6 诚实 none+LILRB2 设计缺口）、kb/literature_db/EYEKB_DB_POINTER.yaml（v2.4/v2.4.1 块，追加式，前缀字节不变断言先例）。

## 任务（产出落 /mnt/D/EyeKB/plans/rag_fix3_20260928/）
1. **机械扫描零 LLM**：从 RA 台账/whitelist 精确取出"备选 104 篇"清单与 7 个仅备选覆盖单元对应关系；逐条核：题录可核性（PMID/DOI）、是否已在库（papers.jsonl 查重）、OA 全文可得性与体积（curl -sI 实测）、HRCA 自引排除（沿 RA2 三条件）。
2. **配文入库 = v2.4.2 增量**：v2.4.1 全量继承零重算 + 本批新文 chunks；主库目录 /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09（新建版本目录，v2.4/v2.4.1 冻结不动）；embedding 用 CPU 现链（training-venv + bge-large-en-v1.5 沿 v2.4 先例）；**禁碰 GPU**（5090 被 qwen 服务占用，非 PI 指令不得腾卡；确需 GPU→block 上报）。抓取走 PORT 代理；单文 ≤ 数十 MB，波次全批预算 ≤100MB，任何单项 >1GB 一律不收并登记。
3. **门复算三件套**（判读矩阵预注册先 sha 落纸）：门①黄金 41/41 off 全等（top5 逐字对 v2.4.1 基线）/ 门②retina gate 8/10 用例级+10/10 gate 级不劣化 / 门③原分母 92 原阈值 80% 原判据复算，单调性核 v2.4.1 全项零倒退。门③不达 80% 也如实报（残差转"诚实 none/设计缺口"清单，禁回调阈值）。
4. **指针追加 v2.4.2 块**（EYEKB_DB_POINTER.yaml 追加式，前后缀逐字不变断言）；**MCP/stage3 default 未切不变**；Release 六件零触碰。
5. 收尾：仓面登记 REPO_RESYNC3_REQUIRED.md（sha 台账，本卡零 push）；RAGFIX3_NOTE.md（逐条处置+残差归因+诚实登记）；完成或遇阻必须调 kanban_complete/kanban_block 落卡。

## 领地红线
kb/、mcp_server/、evalset/ 只读；plans/rag_fix_20260928、rag_fix2_v25_20260928、obligrun_20260928（OBLIGRUN 在跑）三目录禁写；WIKI 六件套不整刷（只在指针块/登记件留痕，收口由协调者补账）；中间产物全保留。
