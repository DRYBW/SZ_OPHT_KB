# EyeKB — 眼睛的单细胞注释知识库

**一个给单细胞 RNA 测序（scRNA-seq）研究用的"眼细胞词典 + 文献证据引擎"。**
当你分析眼球组织的单细胞数据、面对一个未知细胞群时，可以向它提问：这个群最可能是什么细胞？它有什么标志基因？这个判断的文献依据是哪几篇论文？

服务当前版本 `0.6`。项目由眼科研究组维护，用于自己课题组及合作者的单细胞数据注释质量控制。

**它不是**：临床诊断工具；也不是黑盒分类器——每一条返回都带 PubMed 文献号（PMID），你可以逐条核查依据。所有注释结论都应当由研究者（human-in-the-loop）确认后才算数。

## 长什么样

下面两张图是体系在真实数据上的产出示例（PDR 玻璃体膜单细胞数据集 GSE165784 的注释辅助流程：批次整合 → 双细胞质检 → 髓系亚群细分，知识库词条参与判读，标签由研究者逐簇确认后定稿）：

![PDR 玻璃体膜髓系亚群 UMAP](figures/umap_myeloid_sub.png)

![质检视图：区室分布与双细胞标记](figures/umap_compartment_doublet.png)

（两张图仅展示工作方式，不构成任何疗效或临床结论。生成脚本随图收录在 `docs/plans/figure_uplift_20260928/scripts/`。）

## 5 分钟跑通

需要 Python ≥ 3.11，一台普通 CPU 机器即可（不需要 GPU），约 4 GB 磁盘放数据。

```bash
# 1) 克隆 + 装依赖（需仓库维护者把你加为 collaborator）
git clone https://github.com/DRYBW/SZ_OPHT_KB.git && cd SZ_OPHT_KB
python3 -m venv .venv && . .venv/bin/activate
pip install "sentence-transformers>=3" pyarrow pandas numpy mcp

# 2) 下载文献语料（在 Releases 页面，不进 git 仓库）
gh release download v2.4.2-rag-assets --pattern '*'
# 没装 gh CLI 的话，直接在浏览器打开 Releases 页手动下载这三个文件：
#   EYEKB_RAG_v2.4.2_slim.tar.part_aa / part_ab / .sha256
cat EYEKB_RAG_v2.4.2_slim.tar.part_* > EYEKB_RAG_v2.4.2_slim.tar
sha256sum -c EYEKB_RAG_v2.4.2_slim.tar.sha256   # 三件齐全且哈希正确才继续
tar -xf EYEKB_RAG_v2.4.2_slim.tar               # 解出 literature_db/v2.4.2_2026-09_slim/

# 3) 命令行问一次："Müller 胶质细胞在视网膜里有什么标志基因？"
python clients/ocularkb/rag/scripts/stage3_retrieve.py \
  --cell-type "Muller glia" --tissue retina --db-dir literature_db/v2.4.2_2026-09_slim
```

第一次运行会自动从 HuggingFace 拉取嵌入模型 `BAAI/bge-large-en-v1.5`（公开权重，约 1.2 GB，本仓库不含）。**中国大陆网络拉不动时加一行镜像**：

```bash
export HF_ENDPOINT=https://hf-mirror.com   # 再跑上面第 3 步即可
```

能打出检索结果，就说明整套环境是通的。

## 接入你的 AI 工作流（MCP 服务）

本仓库自带一个标准 [MCP](https://modelcontextprotocol.io) 服务，可以接入 Claude Desktop、Cursor 等任何 MCP 客户端，让 AI 助手在帮你做细胞注释时**先查权威依据再下结论**：

```json
{
  "mcpServers": {
    "eyekb": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/SZ_OPHT_KB/mcp_server/server.py"]
    }
  }
}
```

服务只走本地 stdio，不开任何网络端口。接好后，`search_literature` 需要知道文献库存放位置：把 `kb/literature_db/EYEKB_DB_POINTER.yaml` 里的 `default` 改成你第 2 步解出的目录名（如 `v2.4.2_2026-09_slim`）；其余四个工具只读仓库自带的 `kb/`，clone 后开箱即用。

### 可以问它的 5 件事

| 工具 | 一句话说明 | 示例问法 |
|---|---|---|
| `search_literature` | 按细胞类型/组织检索文献片段，返回原文、PMID、期刊年份、与标志基因的共现 | "视网膜里的小胶质细胞，近十年文献怎么说的" |
| `query_marker` | 给一组基因，查它们指向什么细胞类型；或给细胞类型，查权威标志基因 | "CD68、P2RY12、TMEM119 共表达意味着什么" |
| `get_tissue_composition` | 正常眼组织里各细胞类型的"应有比例"基线（每行都挂文献号，供者级统计） | "正常人视网膜的视杆/视锥比例大致多少" |
| `get_disease_prior` | 疾病 × 组织的背景知识薄层（身份层级、状态轴、取材差异警示） | "PDR 的黄斑前膜样本和视网膜样本不能直接比" |
| `get_kb_page` | 读取知识库原文页面（索引/主题/组织三种页面） | "打开小胶质细胞词条" |

### 组成基线怎么用

`get_tissue_composition` 给的不是"达标线"，而是**质检参照**：如果你的数据集里某类细胞比例明显落在文献区间之外，系统会出旗标提醒你回头检查——是取材差异、富集方案，还是注释错了。2026-09 起基线已按组织区域（视网膜/黄斑/眼表各分层）和建库策略（细胞悬液/单核悬液）细化，减少"拿错尺子量错数据"的误报。

## 数据与知识规模

- **文献层**：默认库约 17.5 万条文献片段 / 2,713 篇论文；最新打包语料约 24.3 万条 / 3,869 篇（2026-09 冻结快照）。全部来自公开眼科与单细胞文献，每条都可溯到 PMID。
- **词典层**（`kb/`，100+ 件）：人眼与小鼠视网膜的细胞类型标志基因词典、组织组成基线（v0 混合设计版 + v1 分层版）、疾病先验矩阵。
- **判读协议与审计链**（`docs/`）：细胞注释的标准作业流程、历次双盲评测的完整证据（任务书、判读表、投票记录、脚本），共约 2,300 件，全部可复算。

## 如何验证你装出来的和我们的结果一致

```bash
pip install -r requirements.repro.txt   # 锁定版本环境
python tests/verify_repro.py --db-dir literature_db/v2.4.2_2026-09_slim
# 输出 REPRO PASS: 41/41 = 与全仓锚点同分布
```

这 41 道"黄金题"是全项目的回归基准：检索排序逐位对齐。如果你的环境有一题对不上，按 `docs/VERIFY_CONTRACT.md` 的三层排查走，**不要改判据凑通过**。

## 目录结构

```
mcp_server/          证据服务本体（server.py + 核心逻辑 + 留痕/软提示层）
clients/ocularkb/    检索引擎（stage3_retrieve.py 等）
kb/                  词典层：标志基因、组成基线、疾病先验（100+ 件）
rag_snapshots/       语料元数据快照
tests/               黄金 41 题复现门
docs/wiki/           项目当前状态、决策记录（脱敏镜像）
docs/skills/         判读协议与作业规范
docs/plans/          历次评测与审计全量证据链
docs/VERSION_NOTES.md  逐版本注记与对账台账（审计存档）
figures/             上文两张 demo 图
```

## 重要限制（请务必读）

1. **输出是草稿，不是结论。** 所有注释建议必须经研究者确认后使用；本项目不做临床诊断。
2. **证据只能用于"判读"，禁止喂给打分系统。** 本服务的输出可用于辅助人工判断细胞身份，但禁止被任何自动分类器/模型当作训练或评分信号消费（项目红线，写入协议）。
3. **疾病先验只是背景板。** `get_tissue_composition`/`get_disease_prior` 的区间是文献统计参照，疾病数据（如 PDR 新生血管膜）本身注释质量参差，不能当达标线。
4. **大文件走 Releases。** RAG 语料约 940 MB–3 GB 的多个版本都在 Releases 页面（带 sha256 校验），git 仓库本体保持轻量。
5. **h5ad 环境有坑：** 处理评测集请用 anndata ≥ 0.13（0.11.x 读新版矩阵会崩）。纯 MCP 服务不需要 anndata。

## 引用

本项目暂无正式论文。如在研究中使用了本知识库或其数据，建议引用：

```
EyeKB / SZ_OPHT_KB: an evidence-backed cell-type knowledge base and
literature retrieval service for ocular single-cell annotation.
GitHub repository, version 0.6 (2026). RAG corpus snapshot v2.4.2 (2026-09).
```

同时请引用你实际消费到的具体词条所挂的原始文献（每条返回都带 PMID）。

## 维护与审计

- 逐波版本变更注记、镜像对账表、收录/排除台账、脱敏口径等内部审计信息：见 [`docs/VERSION_NOTES.md`](docs/VERSION_NOTES.md)。
- 同步与复现契约：`docs/VERIFY_CONTRACT.md`、`docs/RAG_REBUILD.md`。
