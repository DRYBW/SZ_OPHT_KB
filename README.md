# EyeKB / SZ_OPHT_KB — 眼科知识库 MCP·RAG·Wiki·Skill 四层体系（可克隆运行镜像）

> **仓库定性（PI 2026-09-27 纠正）**：本仓 = EyeKB 四层体系的**可克隆运行镜像**，不是文档备份、不是快照存档。任何人 clone 后按本 README 配好依赖即可：①起 MCP 证据服务 ②拉 Release 恢复 RAG 语料 ③在 docs/wiki 读项目当前态 ④用 docs/skills + docs/plans 复现判读与评测流程。
> 项目本体：眼科文献二级知识库 · 证据服务（2026-09-23 PI 拍板立项）。服务版本 = `KB1v2-0.6-kbgov5`（与 `mcp_server/server.py` 一致；0.5-k9reg→0.6-kbgov5 变更=追加五队列① B5 跨物种治理实装，见版本注记）。

## 四层体系地图

| 层 | 内容 | 仓内位置 |
|---|---|---|
| **MCP 服务层** | stdio 证据服务（5 工具）+ 调用留痕层 + 软旗层 | `mcp_server/`（server.py / eyekb_core.py / calllog.py / softflags.py） |
| **RAG 文献层** | 全眼文献库（v2.0 现役默认 174,616 chunks / 2,713 papers；v2.2–v2.4.2 见指针与 Release） | 元数据 `rag_snapshots/v2.3_2026-09/`；主库 = Release `v2.3-rag-assets`（6 件）；内核 `clients/ocularkb/rag/scripts/stage3_retrieve.py` |
| **Wiki 知识层** | 项目当前态/决策/红线/directive（脱敏镜像，含冻结哈希锚） | `docs/wiki/`（15 件，含 PROTOCOL_VOTING_v2_C2b） |
| **Skill+判读层** | 两技能镜像 + 判读协议件 + 09-26/27/28 各判读卡全量证据链 | `docs/skills/`（annotation-eval-ops、knowledge-guided-cell-annotation、protocols/）；`docs/plans/`（2260 件）；知识资产 `kb/`（104 件） |

## 体系跑出来长什么样（demo 真产物）

![EyeKB demo v2 判读产物——PDR 玻璃体膜髓系亚群 UMAP](figures/umap_myeloid_sub.png)

![质检视图——compartment 分布 + doublet 打标](figures/umap_compartment_doublet.png)

- 上图（封面）= 数据集 GSE165784（PDR 玻璃体膜，scRNA）的 EyeKB demo v2 判读产物：harmonypy 批次整合 + Scrublet doublet 质检 + 髓系亚群深挖（Microglia/Macrophage/Mono/DAM-LAM 细分），KB 词条参与判读；下图 = 质检视图（compartment 分布 + doublet 打标，打标不删）。生成脚本随图收录于 `docs/plans/figure_uplift_20260928/scripts/`（逐文件 sha 台账见 `docs/recon/RECON_figures_20260928.tsv`）。
- demo 性质沿 WIKI 口径：标签 = agent 提议 + KB 证据、经 PI 逐簇确认后才为定稿；两图仅示体系工作方式，不构成任何疗效或临床结论。旧 v1 图（umap_cluster/umap_sample）移入 `figures/v1_legacy/` 仅留痕，README 不再引用。

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

随后把 `kb/literature_db/EYEKB_DB_POINTER.yaml` 的 `default` 指向解包目录（当前 default=v2.0，v2.2/v2.3 标 latest 待 PI 拍板切换——**勿擅改**；09-28 起指针另含 **v2.4 / v2.4.1 / v2.4.2 三块 = 冻结只读暂存，MCP/stage3 default 未切，v2.0 不变**，见下"版本注记"）。仓内 `rag_snapshots/v2.3_2026-09/` 存元数据三面（papers.jsonl/manifest.yaml/build_stats.json，与线上 v2.3 目录逐字节一致）；更完整的三路径重建说明（预置件解包/按书目重建/无文献层降级）见 `docs/RAG_REBUILD.md`。

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

### 版本注记 — 09-28 追加五/追加六波（REPOSYNC3）

- **生产码 B5 实装（追加五队列①，已实装默认生效）**：`mcp_server/server.py` 版本 `KB1v2-0.5-k9reg → KB1v2-0.6-kbgov5`；`eyekb_core.py` 新增 KBGOV 治理层；`kbgov_vocab.json.gz` 冻结词表随码分发（sha 9b504a2e…，对账=REPOSYNC3 T2 表 MATCH）。query_marker genes-mode 跨物种治理默认 ON：鼠源输入（confirmed∨suspected）具名排名清空转 `unranked_candidates`+`no_named_ranking_for`；AMBIG{GLUL,VIM,CLU} 纯共表达命中附 `no_naming_claim` 注记（排序不动）；人源零干预；env `EYEKB_KBGOV_B5=0|false|off|no` 整体回退=pre 基线逐字节全态（A5 式回退自证=`docs/plans/kbgov_b5impl_20260928/out/B5IMPL_A5_ROLLBACK.tsv`）。判据冻结源=KBGOV_CANDIDATE §G1-§G3；五道验收门全 PASS 见该卡 `B5IMPL_COMPLETED.md`。限制照录：title-case 真人源上送有误拒风险→T+7 观察窗，>0 回退 B4 口径需 PI 另批。
- **H1M3 判序锚实装（追加五队列②，向前生效）**：`docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md` 新增 §9 判序锚成文（§0-§8 逐字继承；历史 v1.1/v1.2 件在仓不动）；判读 runner 定名链组件落 `docs/plans/grade_h1m3impl_20260928/`（9 归档复算门全等，OBLIGRUN 敏感性对照 delta=0）。
- **RAG 指针 v2.4.2 块**（`kb/literature_db/EYEKB_DB_POINTER.yaml`，终态 sha256=a9072609…，追加前缀逐字节不变断言过）：v2.4.2 = v2.4.1 全量继承零重算 + RAGFIX3 扫描通过 103 篇 11,221 chunks（242,928 chunks / 3,869 unique papers；卡 t_b94d0999）。门③ 原分母 92/原阈值 80%/原判据复算 = **87/92 = 94.6% PASS**（判据零移动；78→87 单调性核 v2.4.1 全 78 项零倒退；残差 5 如实登记禁回调）；门① 黄金 41/41 off 态全等+top5 逐字零漂移；门② retina gate 不劣化。**仍为冻结只读暂存：MCP/stage3 default 未切，v2.0 不变**；主库本体（1.076GB）在 OcularKB 侧不入本仓。
- **义务 run 与激活口径（当期主口径，写死）**：OBLIGRUN（t_c145db7c，注册包 §10-6 义务本体）VERDICT=**READY**——P1 **26/33**（球门 ≥24 不降）/P2 0/33，四件套 OB1-4 全清；**33 簇主口径数字=26/33**（激活未发生；OB-5 激活权归 PI，`ACTIVATION_READINESS.md` 仅为建议票件；k9_ocs 与 v2.4.x 均仍默认 OFF，任何"启动／启用"式误读表述禁用）。票面同源排除沿 RULING_1（v2.1 净化面命中集恰 2 行机械复算全等）。
- **MOUSEEXT 鼠版重档预检（t_f2bd45ce）**：零下载行级报批清单（15 候选行：不收 13/待补检 1/等 PI 勾 >1GB=**0 行**）；净结论=重档大概率补不出真第二外部 F1，天花板钉死。无下载动作发生。
- **T7 自家数据 token 永久门首跑（追加六）**：收录面八类自家标识扫描=零 HARD 残留；两份规范条文自身（本卡任务书/WIKI 追加六条款原文）含 token 字面枚举→仓面存 masked 版并逐件登记 `docs/plans/repo_sync3_20260928/ledgers/T7_EXCLUSIONS.tsv`（线上原件留机器侧）；文献通名级 ADVISORY 32 处逐条判读可留（PI 指令原文口径）。
- **T8 §9 语料同源筛查前置盘点（只盘点不修库）**：v2.4/v2.4.1/v2.4.2 三版语料 × registry truth 血缘命中清单=`docs/plans/repo_sync3_20260928/S9_SCREENING.md`。
- docs/plans/ 新增五卡目录（`kbgov_b5impl_20260928/` `grade_h1m3impl_20260928/` `obligrun_20260928/` `mouse_ext_precheck_20260928/` `rag_fix3_20260928/`）+ 本卡目录；docs/wiki 全量刷至线上态（USER_DIRECTIVE_20260928 追加四/五/六入仓，追加六为 masked 版）；docs/skills protocols 层 +v1.3。收录/排除与八门结果=`docs/plans/repo_sync3_20260928/REPOSYNC3_COMPLETED.md`。

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
  - **09-28 追加五/六波（REPOSYNC3 收录）**：`kbgov_b5impl_20260928/`（B5 实装五门+A5 回退台账+词表对账，全收）· `grade_h1m3impl_20260928/`（H1M3 判读 runner+9 复算门+勘误件）· `obligrun_20260928/`（义务 run 四件套+三席票 99 张+RULING_1+PREREG 追加+票面 v2.1+VERDICT v2；隐藏 done 标记 3 件不收沿 09-28 隐藏件先例）· `mouse_ext_precheck_20260928/`（零下载预检报批清单+SHA_MANIFEST）· `rag_fix3_20260928/`（判读矩阵预注册+机械四检+三门台账+93 篇 OA 源 XML 复算证据面全收；12MB 原始抓取缓存除外见附录 A）· `repo_sync3_20260928/`（本卡任务书 masked 版+八门脚本/证据+REPOSYNC3_COMPLETED.md+S9_SCREENING.md）
  - 各卡复算 = 进该卡 `scripts/`，输入指针在其 PREREG/NOTE 头注；数值证据面（tsv/json/jsonl）未经任何数值改动。
- **哈希锚例外**：`btest/BTEST_PREREG_v1.0.md.sha256` 锚定线上原件（镜像内脱敏致 `sha256sum -c` 预期 FAIL），见脱敏报告"冻结哈希锚例外登记"。09-28 波同型例外逐件登记 = `docs/DESENS_SCAN_REPORT_REPOSYNC2_20260928.md`（关键件：`retrain_assess_20260928/ledgers/SHA_SELF_20260928.txt` 之 RETRAIN_VERDICT.md 行、`kb_chain_audit_20260928` 与 `rag_fix2_v25_20260928` 两卡 SHA_DELIVERABLES 中指向脱敏改名件/文本面的行、`rag_fix_20260928` 卡台账体本身含渠道字样被脱敏；另 `rag_gap_20260928/REPORT_RAGGAP.md` 与线上自身台账漂移见收尾件遗留节）。

## 五、对账表（镜像 ↔ 线上）

`docs/recon/RECON_kb_mcp_20260927.tsv`：kb/ 100 文件 + mcp_server 4 文件逐文件 sha256 对线上清单，**104/104 MATCH**（09-27 REPOSYNC 时点）；clients/scripts/evals/figures 四目录汇总 IDENTICAL（同表附页）。文档/判读层镜像为脱敏副本，不做逐字节对账（差异=标签替换，逐文件命中统计见脱敏报告）。

- **09-28 REPOSYNC2 新表**：`docs/recon/RECON_kb_mcp_reposync2_20260928.tsv`（kb/ 104 件 + mcp_server 4 件 = 108 件，含本波新增 2 INERT 旁挂与指针 v2.4/v2.4.1 块）：**103 MATCH + 4 DESSENS-VERIFIED（镜像=脱敏(线上)逐字节可复核：k9 两件 json + server/core 两件代码）+ 1 PRIOR_DESENS（softflags.py c4a8f53 注释级脱敏，协调者已批，仓 sha 与 09-28 表逐字全等）**；MISMATCH=0。
- **09-28 REPOSYNC3 新表**：`docs/recon/RECON_kb_mcp_reposync3_20260928.tsv`（kb/ 104 件 + mcp_server 5 件 = 109 件，含本波 kbgov_vocab.json.gz 新数据件与指针 v2.4.2 块）：**104 MATCH + 4 DESSENS-VERIFIED（k9 两件 json + server/core 两件代码=B5 增量叠加脱敏面，仓件==脱敏_v4(线上) 逐字节可复核）+ 1 PRIOR_DESENS**；MISMATCH=0；登记 sha 四件强断言全过（a9072609/b832a694/10da875a/9b504a2e）。规则源=脱敏器 v4（v3+裁决商 CJK 邻界强化，REPOSYNC2 §六-2 建议落地）。
- **收录台账**：`docs/recon/REPOSYNC2_INTAKE.sha256`（八判读卡 767 件+本卡 BRIEF）· `docs/recon/REPOSYNC3_INTAKE.sha256`（追加五/六波 379 件=五卡+本卡+protocol v1.3+vocab+指针+wiki 实质漂移两件+mcp 两件，重跑 `sha256sum -c` 一致）。

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
| `OcularKB 侧 v2.4.2 主库` | 1.076GB | RAG 增量主库 v2.4.1 全量继承+ra3 103 篇 11,221 chunks（MCP/stage3 未切） | 不入仓（登记件默认裁定+大文件纪律；rag_snapshots 沿默认不收 v2.4.x 元数据三面）；重建路径 = Release v2.3 基座 + `rag_fix_20260928`→`rag_fix2_v25_20260928`→`rag_fix3_20260928`（`ra3_scan.py` 闭集判定+`ra3_fetch.py` OA 下载[零清单外/零付费墙，清单=仓内 `work/ra3_availability.tsv`]）+`ra3_merge.py` 增量链；库态以指针 v2.4.2 块 manifest 行为准 |
| `EyeKB/plans/rag_fix3_20260928/work/chunks_ra3_raw.jsonl` | 12MB | RA3 103 篇抓取原始缓存（>10MB 先质疑规则） | 跑 `docs/plans/rag_fix3_20260928/scripts/ra3_fetch.py`（输入=仓内 `work/ra3_selected.jsonl` 闭集 103 PMID；对账=`work/ra3_fetch.log`+`work/ra3_bytes.json`+`work/xml3/` 93 篇源 XML 已入仓） |

已入镜像的缓存面（小体量、审计价值高于体积）：`e2r/ledgers/api/` 3.6MB、`panel_pmid/ledgers/raw_uniprot/` 0.57MB、`kb9/ledgers/epmc_raw*、ols_evidence_kb9/` <1MB。

## 附录 B — 脱敏与镜像口径

- 规则三元组 = project-github-export skill 现行清单（渠道商名→LLM_CHANNEL、裁决商名→REVIEWER_LLM、IM 平台→MSG_PLATFORM、agent 角色→AGENT_ROLE、主机名→HOST、端口→PORT（仅散文类）、密钥形态→REDACTED_SECRET（兜底实测零命中）、第三方作者邮箱→CONTACT_EMAIL）。
- 文件名+内容双扫描；改名 21 件+1 目录；替换后二次扫描零命中（幂等）。
- 09-28 REPOSYNC3 起规则源升级脱敏器 v4（v3 逐字保留 + 裁决商名 CJK 邻界强化一条——REPOSYNC2 §六-2 已知盲区落地）；对既有仓件幂等（零额外改动实证=命中文件数 2 均为本波新收面）。另追加六 T7 永久门=八类自家标识 token 扫描（needle 全部运行期拼装，规范文与脚本自身零字面自净）。
- 个别句子有标签生硬感——本仓为安全牺牲可读性（PI 知情选择）；组内精读请回工作盘原件。

## 维护

- 下次结构变更后重同步检查项清单 = `docs/REPOSYNC_NOTE_20260927.md` 末节（供未来收口卡继承）。
- 本 README 与镜像由 2026-09-27 REPOSYNC（任务书 `docs/plans/repo_sync_20260927/BRIEF_REPOSYNC.md`）生成。
