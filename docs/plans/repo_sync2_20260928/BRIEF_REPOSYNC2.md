# BRIEF_REPOSYNC2 — SZ_OPHT_KB 第二轮仓同步（D23）

批准：PI 2026-09-28 原话"可以，你验证好再上传"——**测试先行、验过才 push** 是本卡第一纪律。
上游依据：WIKI/USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加三节（D23 条目）；
两份登记件 plans/rag_fix_20260928/REPO_RESYNC_REQUIRED.md 与 plans/rag_fix2_v25_20260928/REPO_RESYNC2_REQUIRED.md。

## 0. 现状基线（协调者已实测，2026-09-28 早）

- 本地克隆 /home/ubuntu/EYEKB_REPO：main == origin/main == e9117cd（2026-09-27 21:42，KB9REG-EXEC 收尾已自行同步并推送）。
- 即 t_6d226765（整仓对齐）+ KB9REG 波已入库；本卡补的是 **09-27 21:42 之后的改进波产物**。
- kb/mcp 面自证：server.py/eyekb_core.py mtime 21:12-21:13 早于 KB9REG 收尾对账（21:39，0.5-k9reg 已入仓），本卡只需 sha 对账复核，预期 0 漂移；有漂移逐件登记并收齐。

## 1. 收录范围（逐目录）

A. docs/plans/ 新增八卡产物目录（源=/mnt/D/EyeKB/plans/）：
   1. kbx_lacrimal_20260928（173M，362 件）——**out/kbx_clustered_organoid.h5ad(105M) 与 out/kbx_clustered_tissue.h5ad(53M) 两面不收**，照 repo_sync_20260927 先例在 README 附录 A 登记再生产方式（脚本+输入+种子）；其余判读/预注册/裁定/台账全收。
   2. kb_chain_audit_20260928（40M）
   3. rag_fix_20260928（24M）——work/chunks_ra_raw.jsonl(9.0M) 属抓取原始缓存，两面不收，登记再生产方式；其余收。
   4. rag_fix2_v25_20260928（4.1M，全收）
   5. kb_gov_20260928（1.3M）、rag_gap_20260928（1.9M）、grade_anchor_20260928（463K）、retrain_assess_20260928（37K，全收）
   通用体积规则：单文件 >10MB 一律先质疑是否缓存/衍生件；可再生的不收+附录 A 登记，不可再生的停卡上报。
   另收 plans/repo_sync_20260928/（本卡 BRIEF+收尾件自身目录）。
B. kb/ 面两件 INERT 旁挂 + 一指针（sha 以登记件为准）：
   - kb/markers/_raggap_errata_v1.json (10da875a...)
   - kb/markers/_raggap_c_linkbackfill_v1.json (b832a694...)
   - kb/literature_db/EYEKB_DB_POINTER.yaml（含 v2.4 与 v2.4.1 两块，终态 sha256=c7f2e0f7d583cfc56ce8bfb821b0517513e81316e416b55ecd0aa30d1f6e15c7，入仓后须逐字对账）
C. WIKI/ 面全量刷至线上态（09-27 21:00 后有变的）：USER_DIRECTIVE_20260928_eyekb_improve_wave.md、当前状态.md、INDEX.md、检索索引.md、体系盘点_MCP-RAG-Wiki-Skill_20260924.md、数据资产.md、决策记录.md（worker 以 mtime+内容 diff 自核，防漏防多）。
D. skills 镜像：若 AGENT_ROLE skills 面有本波新增/修订（对照上次同步清单），刷新收录；无变则记"零漂移"。

## 2. 在先裁决继承清单（仓面文字必须按此口径，逐条核对）

1. KBX：O3 降档 = 考卷无效，非词条判负；泪腺定量首考挂"待新数据"账；A3 维持不注册（KBX_RULING_1.md / KBX_VERDICT.md）。
2. RAG 门号链：v2.4 门③ 72.8% FAIL 照实保留在案；RAGFIX2 追补后 v2.4.1 门③ 84.8% PASS 取代其"最新可交付"地位；v2.4/v2.4.1 门①黄金 41/41 off 全等、门② retina gate 均 PASS。
3. **v2.4/v2.4.1 主库 = 冻结只读暂存，MCP/stage3 default 未切（v2.0 不变）**——README/WIKI 仓面严禁"已激活/已上线"措辞；k9_ocs = REGISTERED_DEFAULT_OFF 沿 KB9REG 口径勿破坏。
4. RETRAIN：四对象冲击评估结论 = 零重训（以账回答），评估产物只读性质。
5. KBGOV/PME3(=panel_pmid，若 sha 复核有增改则补)/GRADE：候选与分析性质，零注册零接线零激活。
6. Release 六件（v2.3 分卷）本卡零触碰零重传；是否升 v2.4.x 由本卡产 RELEASE_ASSESS 短节（语料状态对账 + 建议，单独报 PI，不执行）。
7. OcularKB 侧 v2.4/v2.4.1 主库（1.03GB 级）与 rag_snapshots 大文件：不入 EyeKB 仓（沿两份登记件默认裁定）。

## 3. push 前置测试硬门（六条，任何一项不过 = 不 push，直接 block 回报）

- T1 staging 仓副本起真 MCP stdio 回归通过（沿用 exec7 9/9 与 42-probe 基线口径，探针脚本仓内已有，协调者会另行独立复跑）。
- T2 kb 面/指针/旁挂件仓副本与线上逐字节 sha 对账新表（脱敏例外逐件登记，先例=KB9REG 对账表格式）。
- T3 README 增量可复跑：新登记的再生产方式/路径逐条 ls 实证存在、命令可执行；版本注记加"09-28 改进波"段。
- T4 收录面完整性：每份 .md 非空且末行完整；全部 .py 通过 python -m py_compile；台账（sha256 清单）重算一致。
- T5 脱敏扫描复跑 0 命中（文件名+内容双扫描；词边界防误伤：astrocyte/secretory 类生物词；已登记例外逐件列明）。
- T6 Release 六件本地重验证：分卷合并 sha 与台账对账（本地重算即可，不上传不改动）。

## 4. 工程纪律

- staging 副本法（copy 不 move），/mnt/D/EyeKB 线上全程只读；evalset/、mcp_server/、kb/ 本体禁任何写。
- push 走 HTTPS_PROXY=http://127.0.0.1:PORT（本机 GitHub 直连不通；gh 不认 --proxy flag，环境代理导出即可）。
- commit 按层分：plans 面 / kb 面 / WIKI 面 / README+对账收尾，各层可回滚。
- 中间产物（对账表、扫描日志、测试输出、脱敏台账）全部入 commit 留痕，禁止清理删除。
- 完成时产 plans/repo_sync2_20260928/REPOSYNC2_COMPLETED.md：commit 清单（hash+摘要）、六门测试结果逐条、收录/排除清单（含体积）、RELEASE_ASSESS 短节、遗留事项。
- **完成或遇阻必须调 kanban_complete / kanban_block 落卡**（协议违规退出前科纪律）。
