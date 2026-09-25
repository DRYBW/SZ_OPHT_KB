# EyeKB — 眼科文献二级知识库 · 证据服务

独立知识库项目（2026-09-23 PI 拍板立项，见 `plans/USER_DIRECTIVE_20260923_EyeKB_GO.md`）。
打包三层资产，通过 **MCP（本地 stdio）** 对外提供证据检索：

| 层 | 内容 | 物理位置 (P1) |
|---|---|---|
| RAG 文献库 | v2.0 全眼：11 组织 / 2,713 篇 / 174,616 chunks | 引用 OcularKB 现路径（只读，见 `kb/literature_db/EYEKB_DB_POINTER.yaml`；P2 才物理迁移） |
| VK 索引层 | 1 总目录 + 16 主题页 + 10 组织页（27 页） | `kb/vk_literature_index/`（P1a copy 收编，sha256 与源一致） |
| Marker 权威层 | markers_v4.1_clean.json（视网膜 10 类本地权威 marker） | `kb/markers/`（P0 复制品，源哈希已核） |
| **判读层 (KB1v2/KB2c)** | 眼科通用组成基线：供者级条件参考分布，D001 retina + D002 ocular_surface + optic_nerve/RPE/TM/CB 已建、5 组织骨架映射已回填；**KB2c 发育轴单列：全部 11 条重渲染为 adult-only 主档（donor≥18y）+ adult_pool 对照档双身份，非 adult 供者逐行披露**；疾病×组织×发育档矩阵（示例格 PDR__纤维血管膜）；fetal/developing 转换态概念条目；概念 ID 映射；RAG 三字段 sidecar | `kb/baselines/`（含 `_STAGE_DISCLOSURE.md` + `fetal_development_transitions.md`）+ `kb/priors/disease/` + `kb/priors/concepts.tsv` + `kb/literature_db/evidence_meta_v2.0_2026-09.jsonl`；使用流程=`plans/ANNOTATION_PROTOCOL_v1.1.md`（先冻结后对照）；裁定=`plans/KB2C_ADJUDICATION_20260923.md` |

**判读层图例（KB2c 发育轴，2026-09-23 深夜裁定固化）**：

- 顶层轴 `organism_stage` ∈ **{fetal, adult, developing, unknown}**（产物用 4 级；PI 指令 5 值集映射：postnatal→developing，organoid→unknown+旗标）；逐行 UBERON 原值可溯源（`stage_disclosure`/`excluded_nonadult_units`）。
- **adult = donor_age ≥ 18 岁**（裁定 Q2；阈值写入产物字段，改动须过裁定）；newborn/儿童/青少年→developing。**≥60 老年分层不在本轴**——aging 是正交独立轴，将来单独立条目。
- **双档身份**：主档 `..._adult_only__kb2c`（剔除非 adult 供者单元重算）与对照档 `..._adult_pool__v1.0`（v1.0 混口径原样保留）entry_id/sha256 身份签名分离，引用旧数字只能挂对照档。
- **红线**：胎儿/发育期数据**永不并入 adult 主档**（即使同一组织）；unknown（如无年龄列的 GSE158629 RPE）必须披露行，禁静默归 adult；fetal/developing 查询返回转换态概念条目（现役引擎不适用声明），禁成人桶代答。

**判读层定位（Astra T2 裁定固化，写死）**：基线与疾病条目 = 身份参考 + 背景对照 + QC 旗，
**不得当组成达标线**；清单外身份触发 unexpected 旗但不得强制改成清单内身份；禁入一切打分
（module score/标签加权/置信度加分/候选排序分/复合 QC 分）。

## 快速开始（MCP stdio）

```json
{
  "mcpServers": {
    "eyekb": {
      "command": "/home/ubuntu/training-venv/bin/python",
      "args": ["/mnt/D/EyeKB/mcp_server/server.py"]
    }
  }
}
```

三工具契约（设计稿 §3）：

- `search_literature(cell_type, species?, tissue?, top_k?, query?, db?)`
  → 文献片段 + PMID + 期刊年份 + marker 共现 + 相关度（stage3 v2.0 内核）
- `get_kb_page(scope=index|topic|tissue, name)` → VK 索引页原文（白名单路径防越界）
- `query_marker(genes? | cell_type?)` → 本地权威 marker 命中（先本地后联网的机器化）

## 纪律红线

1. **证据服务不进打分**——本服务只提供检索与引用（Claude5 冻结裁定的服务级升级）；
   任何分类器/模型打分流程禁止消费本服务输出来产生分数。
2. **本地 stdio，不开网络端口**（SSE/远程属 P3，未授权）。
3. **copy 不 move**——OcularKB 是引擎项目，本库 P1 对其零改动、只读引用。
4. 全部引用带 PMID 可溯源；注释产物默认 = 草稿待 PI 确认（human-in-loop）。
5. **发育轴红线（KB3，PI 指令 2026-09-23/24 固化，2026-09-24 t_5425a7ca 落地）：发育数据一律单列，任何组织层面 adult/fetal 不互为参照。** 基线/疾病矩阵/评估集/检索元数据四层全单列：成人档条目 `development_stage=adult` 写死+禁令入参考分布段；发育期条目独立文件（`kb/baselines/retina__fetal_developing.{json,md}`，schema `eyekb-baseline-development/1.0`，MCP 成人查询不可见）；疾病矩阵 12 格全 adult + ROP 发育轴预留格；E5(GSE268630) 与成人统计池永久分离（冻结件 KB3-ADJ 段成文）；RAG papers 级 `dev_stage` sidecar（`kb/literature_db/dev_stage_meta_v2.2_2026-09.jsonl`）+ `stage3_retrieve_v3.py --dev-stage` 过滤。执行日志 = `plans/kb3_dev_axis_log.md`。

## 目录

```
kb/            三层知识资产 + 库路径指针
mcp_server/    server.py (MCP 传输层) + eyekb_core.py (工具内核)
clients/       ocularkb 检索内核 verbatim 复制品 (stage3_retrieve.py / qa_v2.py)
evals/         自测 + MCP-vs-直调黄金集回归 (41/41 PASS, 2026-09-23)
plans/         directive + demo 线 (GSE165784 PDR 膜注释 demo)
logs/          运行日志
```

## 状态

- P0 骨架 + P1（三工具 / 回归 / demo）：**完成** 2026-09-23；
  验收证据与决策记录 = `plans/P1_DECISION_LOG_20260923.md`
  (P1a copy 零漂移 / P1c 自测 11/11 / P1d 回归 41/41 / demo = GSE165784 注释草稿待 PI 确认)
- KB1v2/KB1v2b（判读层眼科通用 + 供者级回填）：**完成** 2026-09-23（回归 28/28）
- **KB2c（发育轴单列，t_be336eee）：完成** 2026-09-23 深夜——11 条基线双档重渲染+逐行披露+矩阵三键+MCP development_stage 过滤+fetal 转换态概念条目；执行日志=`plans/kb2c_dev_axis_log.md`，回归=`evals/REGRESSION_KB2C_20260923.json`
- **KB3（发育轴全量单列，t_5425a7ca）：完成** 2026-09-24——四层落地：W1 全部基线条目 `development_stage` 必填+禁令入参考分布段+首个发育期实数据参考条 `retina__fetal_developing`（GSE268630 portal 226,506 + GSE138002 胎层 88,013，作者/portal 标签聚合，非引擎产物）；W2 疾病矩阵 `development_axis` 列+ROP 预留格；W3 E5 分离规则成文（冻结件 KB3-ADJ 增补段）+RUN1 复查无混池；W4 RAG papers 级 dev_stage sidecar+检索 `--dev-stage` 参数；W5 本 README 红线+OcularKB WIKI §6。日志=`plans/kb3_dev_axis_log.md`，回归=`evals/REGRESSION_KB3_20260924.json`
- P2（物理迁移/OcularKB 切消费路径）、P3（远程/增量更新）：**未授权，待 PI 看 demo 后拍板**
