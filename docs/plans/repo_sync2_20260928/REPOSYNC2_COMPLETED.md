# REPOSYNC2_COMPLETED — SZ_OPHT_KB 第二轮镜像同步收尾件（D23）

- 卡：t_719dd225 ｜ 执行=AGENT_ROLE（pi 总协调） ｜ 日期=2026-09-28
- 授权：PI 拍板原话「可以，你验证好再上传」（2026-09-28，经协调者落卡 BRIEF_REPOSYNC2.md）。
- 任务书：`docs/plans/repo_sync2_20260928/BRIEF_REPOSYNC2.md` ｜ 上游登记件：`rag_fix_20260928/REPO_RESYNC_REQUIRED.md`、`rag_fix2_v25_20260928/REPO_RESYNC2_REQUIRED.md`。
- 基线：main=e9117cd（KB9REG-EXEC 收尾，KB9REG 波已入库）；本卡补 09-27 21:42 后改进波产物。
- 方法：staging 副本法（工作副本 `EYEKB_REPO_STAGING_20260928`，copy 不 move）；线上 `/mnt/D/EyeKB`+`/mnt/D/OcularKB` 全程只读零写入（evalset/mcp_server/kb 本体禁写遵守）；push 走本机代理；commit 分四层可回滚。

## 一、commit 清单（本文件生成时点）

| 层 | 哈希 | 内容 |
|---|---|---|
| 1/4 plans 面 | `53a44cd` | 781 件入仓=八卡 767 + 收尾卡当时 14（排除面见三），全过 v3 脱敏引擎 |
| 2/4 kb 面 | `8782493` | 2 INERT 旁挂 + 指针 v2.4/v2.4.1 块（字节镜像，登记 sha 逐字对上） |
| 3/4 WIKI+skills 面 | `180f519` | docs/wiki 全量刷至线上态 15 件 + docs/skills 两镜像随动 |
| 4/4 README+对账收尾 | （本文件随该层入库，哈希=git log 顶端，push 后由看板 summary 回传） | README 版本注记/附录A/§四§五 + RECON 新表 + INTAKE 台账 + 两份扫描报告 + 本件 |

## 二、六门测试结果（push 前置硬门，逐条）

| 门 | 判据 | 结果 | 证据 |
|---|---|---|---|
| T1 | staging 仓副本起真 MCP stdio 回归 | **PASS**：exec7 等价 11/11（9 检查+基线哈希面 2 断言）；42-probe=35 直等（kb_root 前缀归一后 canon_sha 全等）+7 脱敏可解释（逐字段双向映射证明，全为注册标签差异）+0 漂移；注册行为/白名单/旁挂惰性 15 断言全过，含新断言 `raggap-inerts-unwired` | `out/t1_exec7_staging.json` `out/t1_probe42_staging.json` |
| T2 | kb/指针/旁挂仓副本 vs 线上逐字节对账新表 | **PASS**：108 件 = 103 MATCH + 4 DESSENS-VERIFIED（k9 两件 json + server/core 代码面=脱敏(线上)逐字节可复核）+ 1 PRIOR_DESENS（softflags c4a8f53 已批件，仓 sha 与 09-28 表逐字全等复核）；**MISMATCH=0**；三登记件 sha 强断言过（10da875a/b832a694/c7f2e0f7 全等） | `docs/recon/RECON_kb_mcp_reposync2_20260928.tsv` + `scripts/t2_recon_kb_mcp.py` |
| T3 | README 增量可复跑实证 | **PASS**：附录 A 新登记三行的仓内指针件逐件 ls 实证存在、脚本 py_compile 全过；版本注记含"09-28 改进波"段；v2.4/v2.4.1 仓面零"已激活/已上线"措辞（grep 断言）。详见扫描器输出 | `out/t3_readme_walkthrough.txt` |
| T4 | 收录完整性 py_compile+台账重算 | **PASS**：md 45 件零空件、无换行结尾 5 件=与线上同源实证；py 64 件 compile 0 失败；INTAKE 台账 768 条生成后重跑 `-c` 一致；卡内 sha 台账逐件重验：FAIL-预期（脱敏）全部落例外表，真失败=0 | `out/t4_ledger_check.txt` + `docs/recon/REPOSYNC2_INTAKE.sha256` |
| T5 | 脱敏双扫 0 命中 | **PASS**：v3 引擎（文件名+内容）改名 0/命中 0/命中文件 0（幂等）；本卡另补 CJK 边界强化词形全树复扫——收录面唯一残差=09-27 存量报告自引 1 处（登记不改），策略面存量（kb/scripts/tests 字节镜像）逐件登记不擅动 | `out/t5_final_scan.txt` `out/t5_inventory_register.txt` `docs/DESENS_SCAN_REPORT_REPOSYNC2_20260928.md` |
| T6 | Release 六件本地重验零触碰 | **PASS**：本地 tar 按打包边界重切 5 卷，逐卷 sha256 == GitHub Release 附件 digest（5/5）；合并态重算 sha == 本地台账 == 4e7089f3…；.tar.sha256 附件本体 digest 亦全等；六件齐全零改动零下载 | `out/t6_release_reverify.txt` `out/t6_release_v23_assets_api.json` |

## 三、收录/排除清单（含体积）

**收录**（八卡 767 件 + 收尾卡（BRIEF/六门脚本/证据/本件）合计入库 781 件+、约 80MB；分目录：kbx_lacrimal_20260928 16MB/381 件（383-2 h5ad）、kb_chain_audit_20260928 40MB/124 件、rag_fix_20260928 15MB/107 件、rag_fix2_v25_20260928 4.1MB/56 件（全收）、kb_gov_20260928 1.3MB/32 件、rag_gap_20260928 1.9MB/43 件、grade_anchor_20260928 476KB/18 件、retrain_assess_20260928 52KB/6 件、repo_sync2_20260928 BRIEF+六门脚本+证据）+ kb 面 3 件 + wiki 15 件 + skills 两镜像。kb_chain 的 31MB epmc 批次台账按任务书"全收"落仓（S1 全检取证面，审计价值优先）。

**排除（>10MB 先质疑裁定记录）**：
- `kbx out/kbx_clustered_organoid.h5ad`（105MB）+ `kbx_clustered_tissue.h5ad`（53MB）——可再生（脚本+输入+种子+参数族），附录 A 登记，不收。
- `rag_fix work/chunks_ra_raw.jsonl`（9.0MB）——抓取原始缓存，附录 A 登记再生产（ra_fetch.py+闭集），不收（任务书点名）。
- `work/markers_v6_retina_repair.json.bak_pre_ragfix`（57KB）——改前基线 .bak，沿 09-27"`.bak` 不收"先例；其证据作用由 `ledgers/SHA_ERRATA_double.txt` 双 sha 行承担（线上侧原件哈希已锚）。
- `__pycache__/`（rag_fix、kb_gov 两处）与隐藏件（0 个）——不收；kb_gov SHA_MANIFEST 含 1 条 pyc 行，镜像内不可重验已登记（线上原锚有效）。
- v2.4/v2.4.1 主库（OcularKB 侧 1.02/1.03GB）+ rag_snapshots 大文件面——不入仓（两份登记件默认裁定），重建路径附录 A 已登记。
- 单文件 >10MB 全树扫描：收录面命中=0（仅上述两件点名 h5ad 超限被排除）。

## 四、RELEASE_ASSESS 短节（语料状态对账 + 建议；单独报 PI，本卡不执行）

对账：
1. Release v2.3 基座六件完整零漂移（T6 实证），线上 v2.3 语料侧自 09-25 后未动（09-27 已核，本卡无新增语料面触碰）。
2. v2.4（230,426 chunks，门③ 72.8% FAIL 照实在案）→ v2.4.1（231,707 chunks，门③ 84.8% PASS 取代"最新可交付"，门①②全过，单调性 67 项零倒退）——两库均冻结只读暂存，**MCP/stage3 default 未切（v2.0 不变）**，仓面/README 均未使用"已激活/已上线"措辞。
3. OcularKB 侧 v2.4/v2.4.1 元数据三面（papers/manifest/build_stats）尚未镜像进 `rag_snapshots/`（沿本卡"大文件面不收"默认裁定，登记于此）。

建议（二选一，供 PI 拍板）：
- **案 A（本卡倾向）**：Release 维持 v2.3-rag-assets 不升版——理由：clone 消费端 default=v2.0，v2.4.1 尚未激活切换，先升语料 Release 会造成"可下载库>现役库"的口径倒挂；待 PI 拍板 default 切换（v2.0→v2.4.1）时，随切换波一并出 `v2.4.1-rag-assets`（5 卷+台账 6 件）+ rag_snapshots 三面刷新 + README §二 更新，一次到位。
- 案 B：即刻追加发布 v2.4.1-rag-assets（约 1.03GB 上传，不动 v2.3 tag）——适合想把"最新可交付语料"提前给外部复算方的场景；发布后 README 需标注 default 未切防误读。
本卡对 Release 零触碰，两案均未执行。

## 五、在先裁决继承核对（§2 清单逐条）

1. KBX 口径：O3=考卷无效非词条判负/挂"待新数据"账/A3 维持不注册——README 版本注记+KBX_VERDICT/RULING_1 原文件入仓，仓面文字无"判负/换词条"表述 ✅
2. RAG 门号链：v2.4 门③ FAIL 照实、v2.4.1 84.8% PASS 取代最新可交付、门①②双过 ✅（README+指针件原文）
3. v2.4/v2.4.1=冻结只读暂存、default 未切、禁"已激活/已上线" ✅（grep 断言 0 命中）；k9_ocs=REGISTERED_DEFAULT_OFF 口径未破坏（README env 矩阵行未动）✅
4. RETRAIN=零重训结论照录，产物只读 ✅
5. KBGOV/PME3/GRADE=候选/分析、零注册零接线零激活 ✅（README 版本注记；kb 面未新增任何接线条目，本卡 kb 面仅 2 INERT+1 指针）
6. Release 六件零触碰；升版与否=第四节 RELEASE_ASSESS 交 PI ✅
7. v2.4/v2.4.1 主库与 rag_snapshots 大文件不入仓 ✅

## 六、遗留事项

1. **上游卡内台账漂移（非镜像问题）**：`rag_gap_20260928/REPORT_RAGGAP.md` 线上现字节 ee7b6933… ≠ 该卡 `ledgers/SHA_DELIVERABLES.txt` 所记 42b79838…（疑为 RAGGAP 收口后追加 §6.4 类更正未重登台账）。建议协调者派原卡补记（改卡不改仓）。
2. **规则盲区（已发现已登记）**：现行词边界规则对 CJK 邻接失效；本卡以强化词形补扫收录面 0 残差，但建议 a) 下波把强化词形并入脱敏器规则，b) kb/scripts/tests 存量 3,610 处命中是否清洗需 PI 先裁定"字节对账面"与"净面"优先级。
3. **体积观察**：仓含判读层工作树约 114MB，越出 09-27 遗留检查项"本体级 <50MB"软目标（本卡按 BRIEF 口径收录所致）。下波可评估把 `kb_chain/ledgers/batches`（31MB）与 rag_fix2 `work/xml2`（2.3MB）类原始缓存移 Release 附属或附录 A 化。
4. rag_snapshots 未收 v2.4/v2.4.1 元数据三面（RELEASE_ASSESS 第 3 条），随切换/升版波处置。
5. git 占位署名（`EyeKB <eyekb@local>`）沿 09-27 遗留不变。
6. 本地克隆 `/home/ubuntu/EYEKB_REPO` 将在 push 后 ff 同步；`EYEKB_REPO_STAGING_20260928` 保留作业现场（含 /tmp 原样扫描日志指针），归档与否听协调者。

## 七、执行者自证

- 全程未写 `/mnt/D/EyeKB`（plans 收尾目录仅按纪律回写本卡产物副本，见八）；未动线上 kb/evalset/mcp_server；Release 零触碰；本地工作克隆 push 后仅 `git fetch+ff`。
- 六门全过后才 push（先测试后上传为第一纪律；协调者将另行独立复跑 T1）。

## 八、线上留痕

本卡产物同步回写 `/mnt/D/EyeKB/plans/repo_sync2_20260928/`（BRIEF 原件 + scripts/out 副本 + 本收尾件），供工作盘侧追溯；该回写属 plans 写作面，不触任何只读区。
