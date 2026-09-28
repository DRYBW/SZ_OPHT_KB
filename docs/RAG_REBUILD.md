# RAG 文献库：仓内容 / 重建 / 预置件

## 仓里有（元数据+内核，可复算可追溯）
- rag_snapshots/v2.3_2026-09/：papers.jsonl（3700 篇清单：PMID/DOI/标题）+ manifest.yaml + build_stats.json —— 库的"完整书目"
- kb/literature_db/EYEKB_DB_POINTER.yaml：库版本指针（chunks 数/角色/裁定口径）
- kb/literature_db/evidence_meta_*.jsonl：逐篇入库理由 sidecar（EyeKB 自有）
- clients/ocularkb/rag/scripts/stage3_retrieve.py：检索内核（MCP search_literature 用，已含在本仓）

## 仓里没有（体积墙）
chunks.parquet ≈ 935 MB 单文件 > GitHub 100MB 硬限。两个获取途径：
1. **预置件（推荐）**：本仓 private Release 附件 EYEKB_RAG_v2.3.tar（≈937MB，sha256 见 release note），解包到任意目录后改 EYEKB_DB_POINTER.yaml 的 path 指向即可
2. **全量重建**：按 papers.jsonl 清单从 PMC OA 重取全文→切片→用 HuggingFace 公开模型 bge-large-en-v1.5（cpu）重嵌。管线在 OcularKB 项目侧（stage1 fetch/stage2 chunk），逐字节一致性不承诺（embedding 版本敏感），但检索行为等价
   **⚠ 同质化契约注记（2026-09-28，docs/VERIFY_CONTRACT.md G2）**：本路径为探索性行为——重建产物**不得作为复现结果、不得回报注为"仓体系输出"、不得回流锚点**；复现用途只认 Release 预置件+verify_repro PASS。

## 服务接线（一步）
python 3.11+ 环境装 sentence-transformers/pyarrow/pandas 与 mcp sdk；启动 `python mcp_server/server.py`（stdio，不开端口）；search_literature 自动读指针。
