# kbadd_KERATOCYTE_20260924.jsonl 归档说明 (卡片 t_e1febb8e, 2026-09-24)

本文件登记 marker 库补录 (Keratocytes/Corneal Endothelium, v1-membrane-20260924) 与
组成基线 keratocyte 参考格的**引用文献, 按入库原因归类** (PI 规则; 现役 5 枚举复用,
未发明新类)。逐条含 `retrieval_status`:

- `VERIFIED_RETRIEVABLE` / `already_in_main_db=true`: 已在现役 RAG 主库且本卡经
  `search_literature` 实测可检索 (如 PMID:34741068, 34381080 等 6 篇)。
- `PENDING_MAIN_DB`: 4 篇 (41060151/42115719/11328728/15914606) 为主库外新文献——
  物理增补 chunk 须写 OcularKB 侧 (本卡领地禁写) → **按任务书红线的阻塞项另卡处理**，
  本卡 sidecar 登记 = 归档原因可追溯, ≠ RAG 检索已覆盖 (astra R6)。
- 降级/弃用基因的历史文献 (MIME1/PDK4/CRYAB/MME/ANGPTL7/ALCAM 支持题录) 未入本
  sidecar 正式条目——其证据状态注记于 markers 库 provenance._aux_evidence /
  concepts.tsv EYEKBC-0018/0019, 避免把未核实关联包装成入库证据。

机器可读: `kbadd_KERATOCYTE_20260924.jsonl` (10 行)。
