# USER_DIRECTIVE 2026-09-24：KB 词条补录以 Cell Ontology 为命名参考（PI 指令）

## 原话语义
PI（2026-09-24 MSG_PLATFORM）："补的词条可以参考celloncology"——即 Cell Ontology（OBO CL，细胞类型国际标准本体）。

## 规范（自本件起生效）
1. **新词条命名对齐**：KB 词条层（markers_v* 的词表名、概念条 EYEKBC-*）新增细胞类型词条时，
   必须查 Cell Ontology（http://purl.obolibrary.org/obo/cl.owl）对应 term，
   记录 `cl_id`（如 CL:0000304 photoreceptor rod cell）+ 官方 label + 定义摘要。
2. **同义词映射**：作者标签/社区别名（BC/bipolar cell/Retinal bipolar cells…）统一挂到 CL term 下做别名表，
   判读 prompt 词表与 truth 映射（defs/maps_Q*.json）逐步向 CL 别名收敛，减少"同物异名"匹配失败。
3. **不冲突条款**：CL 无对应 term 的眼科特有位点（如具体 BC 亚型 DB1/DB2/FMB 若 CL 无条），
   按 CL 的命名规范自造并标注 `cl_id: NO_MATCH`，禁止硬挂近似 term。
4. **面板基因本体不动**：CL 对齐是词条/命名层增量，不改 markers_v5 已过验收的基因集合；
   v5 现有词条（含 keratocyte、中间神经元泛型）做一次性 CL 回溯注记（旁挂对齐文件，升 version 不原地改）。
5. 附属器入库（泪腺/睑板腺等待决定项）适用同一规范。

## 落地
- 执行卡：KB5-v3 缺口词条增补（Q3::13/Q5b::13/Q5b::43 三簇取证）+ v5/keratocyte 词条 CL 回溯对齐，
  任务书须引用本件。
- CL 数据获取：cl.owl / cl.obo 下载走 OBO 官方或 EBI（体积 <50MB，免审批线内），只取视网膜相关分支+全量 id-label 索引。
