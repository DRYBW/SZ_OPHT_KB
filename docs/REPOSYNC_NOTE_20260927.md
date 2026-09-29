# REPOSYNC_NOTE — SZ_OPHT_KB 整仓对齐"可克隆运行四层系统"（2026-09-27）

任务书：`docs/plans/repo_sync_20260927/BRIEF_REPOSYNC.md`（PI 纠正定性：本仓=四层体系可克隆运行镜像，非文档备份）。
执行=staging 副本法：工作副本 `/home/ubuntu/EYEKB_REPO` 先 fetch 核对远端（main 与 origin/main 平齐、干净）→ 旁建 `EYEKB_REPO_STAGING_20260927` 作业 → 分层 commit push。线上 `/mnt/D/EyeKB` 与 `/mnt/D/OcularKB` 全程只读、零写入。

## 一、五块缺口 → 处置

| # | 缺口（实证） | 处置 |
|---|---|---|
| 1 | `mcp_server/server.py` 停 KB1v2-**0.3**-kb7wire（线上 0.4-actv6）；`eyekb_core.py` 落后 1764B；`calllog.py`（留痕层）整文件缺 | 三件按线上同步（字节级全等，对账表 MATCH）；softflags.py 原本已一致未动 |
| 2 | `docs/skills` 仅 2 镜像且 09-26 版旧；判读协议件 ANNOTATION_PROTOCOL 与票规 v2 决策件未镜像 | 两 skill 全量刷新（annotation-eval-ops 补 run6b-run7rg 效率参考件，SKILL.md 至 09-27 版；knowledge-guided 至 09-26 22:26 版）；新增 `docs/skills/protocols/`：ANNOTATION_PROTOCOL_v1.1/v1.2 + PROTOCOL_VOTING_v2_C2b.md |
| 3 | WIKI 镜像停 09-26 晚：INDEX/当前状态/结论速查 09-26 深夜→09-27 全缺、scoring_wave directive（含追加一/二）、红线追加节（操作定义）、PROTOCOL_VOTING_v2_C2b、AUDIT_SOP 未镜像 | 14 件全量刷新（其中 12 件 stale 更新 + scoring_wave/PROTOCOL_VOTING 2 件新增；红线追加节随 redline_rewrite 更新进仓；AUDIT_SOP_v1.0 实体在 E3 卡目录，随判读层入仓 `docs/plans/e3_rescue_20260927/AUDIT_SOP_v1.0.md`） |
| 4 | 09-27 注释证据报告层零镜像 | `docs/plans/` 收 12 卡目录 **1439 件 / 9.6MB**：evidence_scoring、e2_decontam、e3_rescue、e2r_s5audit、btest、tiep、panel_pmid(+batch2)、kb9_ocs、proto_v2、rag_anno_usability、sync_scSOP、repo_sync。口径=md/json/tsv 判读件全进+票档 annotation/*.jsonl 进+scripts/ 链路进+小体量 ledgers 进；raw 抓取缓存两大面（111MB+59MB）不进、登记附录 A；>5MB 单文件、npz/h5ad、.bak、隐藏哨兵文件不进 |
| 5 | README 无"clone 后跑起来"路径 | 重写为四层运行指南：依赖（含 scrnaseq env anndata 0.13.2 注意点与 pipeline_env 不兼容声明）、stdio 注册样例、env 开关矩阵（EYEKB_ACT_V6/softflags 三态/TRACE_TAG）、Release v2.3 分卷下载合并+sha256 核验命令、评测复算入口（各卡 scripts/ 指针）、对账与脱敏口径、附录 A/B |

## 二、对账表

- `docs/recon/RECON_kb_mcp_20260927.tsv`：kb/ 100 件 + mcp_server 4 件逐文件 sha256 对线上 → **104/104 MATCH，0 MISMATCH**。
- `docs/recon/RECON_other_dirs_20260927.tsv`：clients/scripts/evals/figures 汇总 IDENTICAL。
- 文档/判读层镜像=脱敏副本，不做逐字节对账（差异面=标签替换，逐规则统计见 `docs/DESENS_SCAN_REPORT_20260927.md`）。
- Release 资产六件核实未动（线上 v2.3 语料 mtime ≤09-25 08:19；papers.jsonl/manifest.yaml 与 rag_snapshots 逐字节等，build_stats 同步一致）；未重传未改 tag。

## 三、脱敏双扫描命中统计（详见仓内报告）

规则命中：REVIEWER_LLM 353 / CONTACT_EMAIL 259 / LLM_CHANNEL 44+14+2+2 / AGENT_ROLE 29 / MSG_PLATFORM 7 / PORT 4+1（仅散文类）/ OWN_MOUSE_DR_DATASET 2 / LOCAL_LLM 1。
零命中兜底：密钥形态 0、IM chat_id 0、主机名 0、会话标识 0（票档 toolcalls 实测无会话字段）。改名 21 件+1 目录。替换后二次扫描幂等（0 命中）。
关键例外：BTEST_PREREG sidecar 哈希锚保持线上原件（镜像内 `sha256sum -c` 预期 FAIL，非篡改）。

## 四、遗留与"下次结构变更后重同步检查项"（供未来收尾文档继承）

1. **代码面**：server/eyekb_core/calllog/softflags 任一变更 → 重跑对账表并覆盖 `docs/recon/`；代码头部若新增渠道/主机字样须先过脱敏规则再入仓。
2. **WIKI**：新增/改名件 → 全量重刷 `docs/wiki/`（.bak 跳过规则保留）；红线/directive 追加节随母件走。
3. **判读层**：新任务目录 → 按本文档口径收 `docs/plans/`（md/json/tsv+annotation/*.jsonl+scripts；ledgers raw 面 >5MB 一律登记附录 A 不入库）；预注册冻结件的 .sha256 sidecar **禁止镜像方重写**。
4. **RAG 语料变动** → 新 Release tag（不覆盖 v2.3-rag-assets）+ `rag_snapshots/` 三面刷新 + README §二 命令更新。
5. **指针待决定**：`EYEKB_DB_POINTER.yaml` default 仍 v2.0（v2.2/v2.3 标 latest）——PI 决定切换后同步指针与 README。
6. **calllog TRACE_DIR 硬编码** `/mnt/D/EyeKB/logs/mcp_trace`：异地部署按 README §1.4 自改（留痕失败静默兜底，不影响服务）。
7. **git 署名**仍为占位 `EyeKB <eyekb@local>`（09-25/26 首导出既定，历史一致）；如需换真实 GitHub 身份，amend 属重写历史，须 PI 决定后单独执行。
8. **stage3_retrieve 内核路径**：MODEL_DIR/BASE 指实验室工作盘——clone 用户需本地化（README 已写）；若上游 OcularKB 侧内核升级，按"verbatim 复制件"纪律同步。
9. **本地大文件墙**：本仓工作树目标保持"本体级 <50MB"（当前含判读层约 35MB），新增判读面若逼近上限 → 优先拆 Release 而非入仓。
