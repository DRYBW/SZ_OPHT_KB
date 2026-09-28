# EyeKB / SZ_OPHT_KB — 眼科知识库 MCP·RAG·Wiki·Skill 四层体系（可克隆运行镜像）

> **仓库定性（PI 2026-09-27 纠正）**：本仓 = EyeKB 四层体系的**可克隆运行镜像**，不是文档备份、不是快照存档。任何人 clone 后按本 README 配好依赖即可：①起 MCP 证据服务 ②拉 Release 恢复 RAG 语料 ③在 docs/wiki 读项目当前态 ④用 docs/skills + docs/plans 复现判读与评测流程。
> 项目本体：眼科文献二级知识库 · 证据服务（2026-09-23 PI 拍板立项）。服务版本 = `KB1v2-0.5-k9reg`（与 `mcp_server/server.py` 一致）。

## 四层体系地图

| 层 | 内容 | 仓内位置 |
|---|---|---|
| **MCP 服务层** | stdio 证据服务（5 工具）+ 调用留痕层 + 软旗层 | `mcp_server/`（server.py / eyekb_core.py / calllog.py / softflags.py） |
| **RAG 文献层** | 全眼文献库（v2.0 现役默认 174,616 chunks / 2,713 papers；v2.2–v2.4.1 见指针与 Release） | 元数据 `rag_snapshots/v2.3_2026-09/`；主库 = Release `v2.3-rag-assets`（6 件）；内核 `clients/ocularkb/rag/scripts/stage3_retrieve.py` |
| **Wiki 知识层** | 项目当前态/决策/红线/directive（脱敏镜像，含冻结哈希锚） | `docs/wiki/`（15 件，含 PROTOCOL_VOTING_v2_C2b） |
| **Skill+判读层** | 两技能镜像 + 判读协议件 + 09-26/27/28 各判读卡全量证据链 | `docs/skills/`（annotation-eval-ops、knowledge-guided-cell-annotation、protocols/）；`docs/plans/`（2260 件）；知识资产 `kb/`（104 件） |

## 一、MCP 服务层：clone 后跑起来

### 1.1 依赖

服务端本体只需 **Python ≥3.10 + `mcp`（stdio server SDK，实验室实测 v2.0.0）+ numpy + pandas + pyarrow**；检索嵌入另需 `sentence-transformers`（CPU 推理即可，GPU 留科研）。

```bash
python -m venv .venv && . .venv/bin/activate
pip install mcp numpy pandas pyarrow sentence-transformers
```

嵌入模型 = HuggingFace 公开模型 **bge-large-en-v1.5**（权重不进仓）：

```bash
huggingface-cli download BAAI/bge-large-en-v1.5 --local-dir ./models/bge-large-en-v1.5
```

并把 `clients/ocularkb/rag/scripts/stage3_retrieve.py` 顶部 `MODEL_DIR` 与 `BASE` 改为你本地路径（该内核是 OcularKB 逐字复制件，默认指向实验室工作盘）。

**关联环境注意（判读/评测脚本涉及 h5ad 时）**：本实验室读取评测集 h5ad 用 scrnaseq 环境（**anndata 0.13.2**，已验证 backed raw 模式可读）；**pipeline_env（anndata 0.11.4）对本组矩阵不兼容**（nullable-string 列加载返回 object dtype 致下游崩溃，声明为不可用环境；如坚持 0.11+ 写 h5ad 需 `anndata.settings.allow_write_nullable_strings=False`）。纯 MCP 服务与 docs 复算脚本不依赖 anndata。

### 1.2 stdio 注册样例（任意 MCP 客户端）

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

`server.py` 内 `kb_root` 按文件自身位置相对解析，clone 后即可读到 `kb/`；仅 `search_literature` 需要把 RAG 库路径指到恢复后的 literature_db（见 §二与 `kb/literature_db/EYEKB_DB_POINTER.yaml`）。本地 stdio，不开任何网络端口（SSE/远程属 P3 未授权）。

### 1.3 env 开关矩阵

| 变量 | 未设/其他值 | ∈ {0,false,off,no}（strip+casefold） | 语义 |
|---|---|---|---|
| `EYEKB_ACT_V6` | **ON**：query_marker 默认 `library=all` 并入 retina_v6+face_v6（同名类 `<库>::<类>` 别名消歧） | OFF：回退现役三库；off 态响应与 pre 基线逐字节全等（A5 机读验收） | KB7 红词条修复面板激活开关（PI 2026-09-26 批准激活；lacrimal_v6 **任何态不入默认**，仅显式查询——PI A3 暂不切） |
| `EYEKB_MCP_SOFTFLAGS` | **ON**：响应附 `soft_flags`（两口径：flag#1 rod-BC 参数并列组 / flag#2 mural TOP3 边界提醒） | OFF：`soft_flags` 整 key 不出现 | 软复核提示层（第三态=响应内无该 key，消费方按缺省处理） |
| `EYEKB_MCP_TRACE_TAG` | 留痕记录 tag 为空（真实流量） | 自设字符串 | 自测流量打标；OBS-2 统计器默认排除带 tag 记录 |
| （无 env，硬编码 OFF） | `library=k9_ocs` 仅显式查询可达（KB9 案 B 眼表 4 新条，注册默认 OFF） | 任何态不入默认 all | KB9REG-EXEC t_4bb75b26（PI D17 注册批准 2026-09-28；激活需 §10-6 义务 run+PI 另批；lacrimal_v6 同理维持 A3 登记态） |

三工具契约 + KB1v2 判读层两工具：

- `search_literature(cell_type, species?, tissue?, top_k?, query?, db?)` → 片段+PMID+期刊年份+marker 共现+相关度（v2.0 起带 inclusion_reasons/claim_relation/evidence_context 三字段联表）
- `get_kb_page(scope=index|topic|tissue, name)` → VK 索引页原文（白名单路径防越界）
- `query_marker(genes?|cell_type?, library?)` → 本地权威 marker 命中（先本地后联网的机器化）
- `get_tissue_composition(species, tissue, disease?, development_stage?)` → 供者级组成基线（KB2c 发育轴双档：adult_only 主档 + adult_pool 对照档；fetal/developing 返回转换态概念条目，禁成人桶代答）
- `get_disease_prior(disease, tissue?)` → 疾病×组织矩阵薄层条目（身份层级+状态轴+取样材料错配警示）

### 1.4 调用留痕层（calllog.py，OBS-1）

只加日志、零行为改动：每次工具响应落盘 `logs/mcp_trace/calls_YYYY-MM-DD.jsonl`（O_APPEND 行级原子写；>200MB 续写 `.partN`；不自动删除）。记录 = 工具名/入参（检索词属领域信息非个人敏感）/响应**结构摘要**（flag_id 与类目名，不记 notes 全文与片段正文）/env 态/进程 uuid+pid+宿主。观察窗统计口径见 `docs/plans/obs_followup`（09-26 卡）与 WIKI 当前态。

## 二、RAG 层：Release 恢复语料（v2.3）

主库 937MB 超 GitHub 单文件墙，走 **Release `v2.3-rag-assets` 分卷**（5×192MB parts + `.tar.sha256`，共 6 件）：

```bash
gh release download v2.3-rag-assets --repo <owner>/SZ_OPHT_KB --pattern '*'
cat EYEKB_RAG_v2.3.tar.part_* > EYEKB_RAG_v2.3.tar
sha256sum -c EYEKB_RAG_v2.3.tar.sha256          # 判据=字节数与哈希，缺一不解
tar -xf EYEKB_RAG_v2.3.tar                       # 得 literature_db/v2.3_2026-09/{chunks.parquet,papers.jsonl,manifest.yaml,build_stats.json}
```

随后把 `kb/literature_db/EYEKB_DB_POINTER.yaml` 的 `default` 指向解包目录（当前 default=v2.0，v2.2/v2.3 标 latest 待 PI 拍板切换——**勿擅改**；09-28 起指针另含 **v2.4 / v2.4.1 两块 = 冻结只读暂存，MCP/stage3 default 未切，v2.0 不变**，见下"版本注记"）。仓内 `rag_snapshots/v2.3_2026-09/` 存元数据三面（papers.jsonl/manifest.yaml/build_stats.json，与线上 v2.3 目录逐字节一致）；更完整的三路径重建说明（预置件解包/按书目重建/无文献层降级）见 `docs/RAG_REBUILD.md`。

**Release 资产纪律（09-27 REPOSYNC 实核）**：v2.3 语料侧自 09-25 打包后线上零变动（chunks.parquet/papers.jsonl/manifest.yaml/build_stats.json mtime 均 ≤09-25 08:19；papers.jsonl 与 manifest.yaml 哈希对账 rag_snapshots 全等）。Release 六件**不重传不改动**；若未来发现语料变动，如实报告并走新 tag，不覆盖。（09-28 REPOSYNC2 本地重验：tar 重切 5 卷逐卷 sha == Release 附件 digest、合并 sha == 台账，六件完整零漂移，见 `docs/plans/repo_sync2_20260928/out/t6_release_reverify.txt`。）

### 版本注记 — 09-28 改进波（REPOSYNC2）

- **RAG 指针 v2.4 / v2.4.1 两块**（`kb/literature_db/EYEKB_DB_POINTER.yaml`，终态 sha256=c7f2e0f7…，与登记件逐字对账）：
  - v2.4 = v2.3 全量继承零重算 + RAGGAP A 档 64 篇（230,426 chunks / 3,749 unique papers；卡 t_d0bea5a6 D19）。
  - v2.4.1 = v2.4 全量继承零重算 + RAGFIX2 白名单 17 篇（231,707 chunks / 3,766 unique papers；卡 t_6848d3de D21）。
  - **两块均为冻结只读暂存：MCP/stage3 default 未切换（v2.0 不变），本仓面不构成"已启用"语义**；切换权在 PI。主库本体（1.02–1.03GB 级）在 OcularKB 侧，不入本仓（沿 Release 大文件纪律）。
  - 门号链（仓面口径，逐字照登记件）：v2.4 门③（A 档覆盖）72.8% < 80% **FAIL 照实在案**；RAGFIX2 追补后 v2.4.1 门③ 原分母 92/原阈值 80%/原判据复算 78/92 = **84.8% PASS，取代 v2.4 的"最新可交付"地位**；两版本门①（黄金 41/41 off 态全等）与门②（严格 retina gate）均 PASS。v2.4→v2.4.1 单调性核 67 项零倒退。
- **kb/markers/ 两件 INERT 旁挂**（字节镜像，sha 与登记件全等）：`_raggap_errata_v1.json`（LILRB2 撤证 + sample20 误引登记，10da875a…）、`_raggap_c_linkbackfill_v1.json`（C 档 830 行索引回填，默认 OFF，b832a694…）。两件**不被 mcp_server 任何代码路径引用**（REPOSYNC2 T1 静态断言 `raggap-inerts-unwired` 在案）。
- **KBX 泪腺定量首考（t_0fb07fd6）定性照录**：O3 降档 = **考卷无效**（外部文献 Tier1 面板重建后 4/7 群 panel_unavailable），非词条判负；A3 lacrimal_v6 维持注册默认 OFF 不切；泪腺定量首考挂"待新数据"账（KBX_RULING_1 / KBX_VERDICT）。
- **KBCHAIN 全库引用链审计（t_3a35a2cc）**：链账 8,531 实例全检 + 15% 抽检，确诊误引集中于决策表转录通道（取证件全入仓，kb 面零写）。
- **RETRAIN 四对象冲击评估（t_ed4a3c52）**：结论 = **零重训**（以账回答：v2_prod/mouse_prod_v1/RAG 嵌入/面板衍生件均不读本次改动面），评估产物只读性质。
- **KBGOV / PME3 / GRADE 三线**（`kb_gov_20260928/`、`panel_pmid_20260927/` 第三批（如有增量按 sha 复核随动）、`grade_anchor_20260928/`）：候选与分析性质，**零注册、零接线、零激活**。
- docs/plans/ 新增八卡目录 + 本收尾卡目录；docs/wiki 全量刷至线上态（新增 USER_DIRECTIVE_20260928 改进波指令件）；docs/skills 镜像随动刷新。收录/排除清单与六门测试结果 = `docs/plans/repo_sync2_20260928/REPOSYNC2_COMPLETED.md`。

## 三、Wiki 层

`docs/wiki/` = OcularKB/WIKI 的脱敏镜像（当前态/决策记录/结论速查/INDEX/红线与 directive 链，含 PROTOCOL_VOTING_v2_C2b.md 票规 v2 决策件）。口径：镜像件与线上件**唯一差异=脱敏标签替换**（见 `docs/DESENS_SCAN_REPORT_20260927.md`），PI 原话保留、账号形态零命中。

## 四、Skill+判读层：评测复算入口

- **协议件**（注释判读必读，四阶段"先冻结后对照"）：`docs/skills/protocols/ANNOTATION_PROTOCOL_v1.1.md` / `v1.2.md`（判读层使用流程权威文本；红线②操作定义见 WIKI 红线改写件追加节）+ `PROTOCOL_VOTING_v2_C2b.md`（同名词票规 v2 决策件，落款后预注册 run 生效、历史裁决不回改）。
- **技能镜像**：`docs/skills/annotation-eval-ops/`（Run1–Run7+ 全量票台账与功效结论，含 run6b-run7rg 效率参考件）、`docs/skills/knowledge-guided-cell-annotation/`（KB 判读层设计与修复周期）。
- **判读卡全量证据链** `docs/plans/`（09-26/27 各卡，VERDICT/PREREG/判读表/票档/脚本成对收录）：
  - `evidence_scoring_20260926/`（E1 打分实验收口）· `e2_decontam_20260926/`（E2 去污染腿）· `e3_rescue_20260927/`（E3 救援腿 + `AUDIT_SOP_v1.0.md` 全量重跑审计 SOP）
  - `e2r_s5audit_20260927/`（E2-R S5 逐行审计）· `btest_20260927/`（自由查询 A/B 验证：PREREG+票档 annotation/*.jsonl+toolcalls+判读表）
  - `tiep_20260927/`（平票/弃权协议反事实评估）· `panel_pmid_20260927/`+`batch2/`（PME/PME2 证据链补录两批：338 键台账+pme_accounts.tsv）
  - `kb9_ocs_20260927/`（KB9 眼表注册包：五轮外审 prompt/reply 全留痕+BUILD_REPORT+REGISTER_PACKAGE v2）· `proto_v2_20260927/`（票规 v2 决策件落点）· `rag_anno_usability_20260927/` · `sync_scSOP_20260927/` · `repo_sync_20260927/`（本镜像同步任务书）
  - **09-28 改进波（REPOSYNC2 收录）**：`kbx_lacrimal_20260928/`（泪腺定量首考：PREREG v2+判读+票台+REVIEWER_LLM 送审件；两件簇级 h5ad 除外见附录 A）· `kb_chain_audit_20260928/`（全库引用链审计取证面含 epmc 批次台账 31MB 全收）· `rag_fix_20260928/`（RAGFIX v2.4 三门+errata；raw 抓取缓存 9MB 除外见附录 A）· `rag_fix2_v25_20260928/`（v2.4.1 白名单闭集+门③追补，全收）· `kb_gov_20260928/` · `rag_gap_20260928/`（三档报批清单）· `grade_anchor_20260928/` · `retrain_assess_20260928/` · `repo_sync2_20260928/`（本卡任务书+六门测试输出+收尾件）
  - 各卡复算 = 进该卡 `scripts/`，输入指针在其 PREREG/NOTE 头注；数值证据面（tsv/json/jsonl）未经任何数值改动。
- **哈希锚例外**：`btest/BTEST_PREREG_v1.0.md.sha256` 锚定线上原件（镜像内脱敏致 `sha256sum -c` 预期 FAIL），见脱敏报告"冻结哈希锚例外登记"。09-28 波同型例外逐件登记 = `docs/DESENS_SCAN_REPORT_REPOSYNC2_20260928.md`（关键件：`retrain_assess_20260928/ledgers/SHA_SELF_20260928.txt` 之 RETRAIN_VERDICT.md 行、`kb_chain_audit_20260928` 与 `rag_fix2_v25_20260928` 两卡 SHA_DELIVERABLES 中指向脱敏改名件/文本面的行、`rag_fix_20260928` 卡台账体本身含渠道字样被脱敏；另 `rag_gap_20260928/REPORT_RAGGAP.md` 与线上自身台账漂移见收尾件遗留节）。

## 五、对账表（镜像 ↔ 线上）

`docs/recon/RECON_kb_mcp_20260927.tsv`：kb/ 100 文件 + mcp_server 4 文件逐文件 sha256 对线上清单，**104/104 MATCH**（09-27 REPOSYNC 时点）；clients/scripts/evals/figures 四目录汇总 IDENTICAL（同表附页）。文档/判读层镜像为脱敏副本，不做逐字节对账（差异=标签替换，逐文件命中统计见脱敏报告）。

- **09-28 REPOSYNC2 新表**：`docs/recon/RECON_kb_mcp_reposync2_20260928.tsv`（kb/ 104 件 + mcp_server 4 件 = 108 件，含本波新增 2 INERT 旁挂与指针 v2.4/v2.4.1 块）：**103 MATCH + 4 DESSENS-VERIFIED（镜像=脱敏(线上)逐字节可复核：k9 两件 json + server/core 两件代码）+ 1 PRIOR_DESENS（softflags.py c4a8f53 注释级脱敏，协调者已批，仓 sha 与 09-28 表逐字全等）**；MISMATCH=0。
- **收录台账**：`docs/recon/REPOSYNC2_INTAKE.sha256`（覆盖=八判读卡 767 件+本卡 BRIEF，重跑 `sha256sum -c` 一致；本卡 scripts/out 生成物完整性由收尾件+T3/T4 证据另录）。

## 纪律红线（不变项）

1. **证据服务禁入打分**（红线改写 v2 条文）：任何分类器/模型打分流程禁止消费本服务输出生成分数；`soft_flags.notes` 只作可选复核线索。
2. **本地 stdio，不开网络端口**。
3. **copy 不 move**：对上游 OcularKB 零改动、只读引用。
4. 全部引用带 PMID 可溯源；注释产物默认=草稿待 PI 确认（human-in-the-loop）。
5. 判读层使用必须走 ANNOTATION_PROTOCOL（先冻结后对照）；基线/疾病条目=身份参考+背景对照+QC 旗，**不得当组成达标线**。

---

## 附录 A — 未入镜像的大表与再生产方式

| 面 | 体积 | 内容 | 再生产 |
|---|---|---|---|
| `EyeKB/plans/panel_pmid_20260927/ledgers/raw/` | 111MB / 280 件 | PubMed efetch 原始响应缓存 | 跑 `docs/plans/panel_pmid_20260927/scripts/`（efetch 抓取脚本），输入=仓内 PMID 清单 tsv（sha 见同卡 ledgers/*.tsv 台账行） |
| `EyeKB/plans/panel_pmid_20260927/batch2/ledgers/raw2/` | 59MB / 103 件 | efetch 二次检索缓存 | `batch2/scripts/` 同法（PME2 批次） |
| `EyeKB/plans/evalset/`（仓外） | 21GB 级 | 冻结考卷（含 h5ad/逐细胞预测表） | **永不入仓**（患者/项目衍生数据红线）；恢复需 OcularKB 工作盘权限 |
| `EyeKB/plans/kbx_lacrimal_20260928/out/kbx_clustered_organoid.h5ad` + `kbx_clustered_tissue.h5ad` | 105MB + 53MB | KBX 泪腺簇级 h5ad（表达层衍生件） | 跑 `docs/plans/kbx_lacrimal_20260928/scripts/kbx_p2_cluster_score.py`；输入=`GSE164403/GSE164403_annotated.h5ad`（sha 5e6d753d…，OcularKB 工作盘，不入仓）；参数族冻结于 `KBX_PREREG_v2.md`（seed random_state=20260928、scanpy 1.12.2、leiden flavor=igraph res=1.0）；台账=同卡 `ledgers/KBX_CLUSTER_TABLE*` 与 `out/KBX_LG_CROSSWALK.tsv` |
| `EyeKB/plans/rag_fix_20260928/work/chunks_ra_raw.jsonl` | 9.0MB | RAGFIX A 档 64 篇抓取原始缓存 | 跑 `docs/plans/rag_fix_20260928/scripts/ra_fetch.py`（闭集=`out/closed_set_pmids.txt` 64 PMID，端点与重试见脚本头注；输入清单=仓内 `docs/plans/rag_gap_20260928/TIER_A_approval_list.md`）；产物对账=同卡 `work/ra_fetch.log`+`work/ra_availability.tsv`（已入仓） |
| `OcularKB 侧 v2.4 / v2.4.1 主库` | 1.02GB / 1.03GB | RAG 增量主库（MCP/stage3 未切） | 不入仓（两份登记件默认裁定 + 大文件纪律）；重建路径 = Release v2.3 基座 + 各卡 `scripts/` 增量链（`docs/plans/rag_fix_20260928/`、`rag_fix2_v25_20260928/`）；库态与 sha 台账以 `kb/literature_db/EYEKB_DB_POINTER.yaml` 各块 manifest 行为准 |

已入镜像的缓存面（小体量、审计价值高于体积）：`e2r/ledgers/api/` 3.6MB、`panel_pmid/ledgers/raw_uniprot/` 0.57MB、`kb9/ledgers/epmc_raw*、ols_evidence_kb9/` <1MB。

## 附录 B — 脱敏与镜像口径

- 规则三元组 = project-github-export skill 现行清单（渠道商名→LLM_CHANNEL、裁决商名→REVIEWER_LLM、IM 平台→MSG_PLATFORM、agent 角色→AGENT_ROLE、主机名→HOST、端口→PORT（仅散文类）、密钥形态→REDACTED_SECRET（兜底实测零命中）、第三方作者邮箱→CONTACT_EMAIL）。
- 文件名+内容双扫描；改名 21 件+1 目录；替换后二次扫描零命中（幂等）。
- 个别句子有标签生硬感——本仓为安全牺牲可读性（PI 知情选择）；组内精读请回工作盘原件。

## 维护

- 下次结构变更后重同步检查项清单 = `docs/REPOSYNC_NOTE_20260927.md` 末节（供未来收口卡继承）。
- 本 README 与镜像由 2026-09-27 REPOSYNC（任务书 `docs/plans/repo_sync_20260927/BRIEF_REPOSYNC.md`）生成。
