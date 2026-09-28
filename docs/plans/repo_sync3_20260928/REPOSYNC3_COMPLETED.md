# REPOSYNC3_COMPLETED — SZ_OPHT_KB 第三轮镜像同步收尾件（追加五/追加六波）

- 卡：t_09e9a4a3 ｜ 执行=AGENT_ROLE ｜ 日期=2026-09-28
- 任务书：`docs/plans/repo_sync3_20260928/BRIEF_REPOSYNC3.md`（masked 版——追加六 token 字面枚举留机器侧，见三节例外表）｜ 上游登记件：`kbgov_b5impl_20260928/REPO_RESYNC_B5IMPL.md`、`rag_fix3_20260928/REPO_RESYNC3_REQUIRED.md`
- 授权：PI 现行口径=追加五整链自主推进 + 追加六永久门；**验过才 push**（八门全过后才推，本卡同规）。
- 基线：远端 main=ea40bea；工作副本 `EYEKB_REPO_STAGING_RS3_20260928`（copy 不 move）；线上 `/mnt/D/EyeKB`+`/mnt/D/OcularKB` 全程只读零写入。
- 脱敏器升级：本卡起规则源 = **v4**（`eyekb_desensitize_v4_reposync3.py`，v3 逐字保留 + 裁决商名 CJK 邻界强化一条——REPOSYNC2 §六-2 已知盲区按其建议落地）。

## 一、commit 清单（四层可回滚；本文件随 4/4 层入库，该层哈希=git log 顶端，push 后由看板 summary 回传）

| 层 | 内容 |
|---|---|
| 1/4 plans 面 | 五新卡目录全收：`kbgov_b5impl_20260928`（35 件）· `grade_h1m3impl_20260928`（16 件）· `obligrun_20260928`（101 件，隐藏 done 标记 3 件不收沿先例）· `mouse_ext_precheck_20260928`（24 件）· `rag_fix3_20260928`（133 件，12MB 原始缓存除外见三节）+ 本卡目录（BRIEF masked+八门脚本+out/ledgers+S9_SCREENING.md） |
| 2/4 kb+mcp 面 | 指针 v2.4.2 块（终态 sha256=a9072609… 与登记件逐字对账，追加前缀逐字节不变）+ `mcp_server/{server.py,eyekb_core.py,kbgov_vocab.json.gz}`（B5 生产码三件；server/core 仓面=脱敏 v4(线上) 逐字节可复核，kbgov_vocab 字节 MATCH） |
| 3/4 WIKI+protocols 面 | docs/wiki 全量刷至线上态（实质漂移 2 件=USER_DIRECTIVE_20260928 追加四/五/六入仓[追加六 masked 版]+当前状态.md 卡状态行；其余 13 件与仓面脱敏态幂等零漂移，含 INDEX/体系盘点/数据资产/决策记录/检索索引复扫确认）；`docs/skills/protocols/ANNOTATION_PROTOCOL_v1.3.md` 入 protocols 层（v1.1/v1.2 历史件在仓不动）；skills 两镜像随动核查=零实质漂移（脱敏叠加后与仓面幂等） |
| 4/4 README+对账收尾 | README 版本注记新节（0.6-kbgov5/26/33 主口径/激活未发生/附录 A 补 v2.4.2+ra3 行/§四§五新表引用/附录 B v4+T7 说明）+ `docs/recon/RECON_kb_mcp_reposync3_20260928.tsv` + `docs/recon/REPOSYNC3_INTAKE.sha256` + 本件 |

台账口径注：`REPOSYNC3_INTAKE.sha256` 于 T4 段生成，快照=三门复扫后的收录面；台账本体与 `t4_result.txt`=快照后生成物不在台账内（沿 REPOSYNC2"本卡生成物完整性由收尾件+证据另录"同型）。masked 两件由 `scripts/t7b_mask_specs.py` 从线上原件可复跑再生（追加六条款 token 字面含裸前缀全部描述化，非患者数据语义零改动）。

## 二、八门测试结果（push 前置硬门，逐条）

| 门 | 判据 | 结果 | 证据 |
|---|---|---|---|
| T1 | staging 起真 MCP stdio：三态断言+黄金41+probe_repo 系 | **PASS**：三态 13/13（人源零干预/鼠源 title-case+Gm/Rik 双拒/B5=0 回退位；版本=0.6-kbgov5、tools=5、Microglia 两态 top1+len 全等、KRT12 两态排序全等[治理附加字段为设计语义，序不动断言=b507 口径]、lacrimal 泄漏=0、k9 不入默认+显式路由可达）；golden41 OFF 态 **41/41** + 接线契约全 True（b504 逐字复用改 staging 被测；环境适配=s3fs 桩件，见遗留③） | `out/t1_three_state.json` `out/t1_golden41_OFF.json/.md` |
| T2 | kb/mcp 面逐件 sha 对账新表 | **PASS**：109 件 = **104 MATCH + 4 DESSENS-VERIFIED**（k9 两件 json + server/core=B5 增量叠加脱敏面）+ **1 PRIOR_DESENS**（softflags c4a8f53 沿批）；**MISMATCH=0**；登记 sha 四件强断言全过（a9072609/b832a694/10da875a/9b504a2e） | `docs/recon/RECON_kb_mcp_reposync3_20260928.tsv` + `scripts/t2_recon_kb_mcp.py` |
| T3 | README 增量可复跑实证 | **PASS** 8/8：版本串==server 逐字；禁词零（否定引用豁免注记在脚本）；26/33 主口径在文；READY+OB-5 归 PI+建议票件限定同段；B5/H1M3"已实装默认生效/向前生效"允许措辞在文；k9/v2.4.x 默认 OFF 口径在文；引用路径 21 件逐件存在；本脚本 py_compile 过 | `out/t3_readme_walkthrough.txt` |
| T4 | 收录完整性 | **PASS**：md=31 零空件零无末换行；py=48 py_compile 零失败；INTAKE 台账 **391 条**生成后重跑 `-c` 一致；卡内 sha 台账镜像重验=OK 90/DESENS 预期 17/EXCLUDED 预期 8/仓外 324/**REAL-FAIL=0** | `out/t4_result.txt` + `docs/recon/REPOSYNC3_INTAKE.sha256` |
| T5 | 脱敏双扫 0 命中 | **PASS**：v4 引擎 --scan 幂等零命中（改名 0/命中 0）；CJK 邻界强化复扫=引擎 DIRS 残差 0（且本卡把该强化规则并入 v4，pointer_register3.py 一处存量盲区当场修复归位）；kbgov_vocab.json.gz 解压复扫 0；字节镜像存量面 49 文件逐件登记不擅动 | `out/t5_final_scan.txt` `out/t5_engine_scan.txt` `out/t5_inventory_register.txt` |
| T6 | Release 六件本地重验零触碰 | **PASS**：本地 tar 重切 5 卷逐卷 sha==digest、size 面 5/5 OK、合并 sha==台账 4e7089f3…、台账附件本体 digest 全等、六件齐全；远端新鲜拉取失败（代理网络窗）→按任务书"本地重验"口径降级对 REPOSYNC2 存档逐 digest 对账=NO-DRIFT，登记于证据件首行 | `out/t6_release_reverify.txt` |
| T7 | 自家数据 token 扫描（永久门首跑） | **PASS（含处置）**：写作面八类扫描 HARD=0；首跑命中 3 件=两份规范条文自身（任务书/追加六条款原文含 token 枚举）+门脚本自净暴露——两份改 **masked 版入仓**（线上原件留机器侧，逐件登记），脚本 needle 全改运行期拼装；文献通名级 ADVISORY 32 处（PMC 题录/元数据内 DR1/DR4/conbercept 通名）逐条判读可留=PI 指令原文口径（"通名级非患者数据可留"）；字节镜像面 HARD=0 | `out/T7_scan.tsv` `ledgers/T7_EXCLUSIONS.tsv` `scripts/t7_own_tokens.py` `scripts/t7b_mask_specs.py` |
| T8 | §9 语料同源筛查前置盘点（只盘不修） | **落盘**：v2.4/v2.4.1/v2.4.2 三版语料 × registry truth 命中清单+判定+跨版本存在矩阵（36712326 自 v2.0 即在库、33865984 自 v2.1）+RAGFIX3 增量 103 篇零 watch 交集+7 study 血缘不可判残余；判定=结构性暴露面已披露、防线在票面层（沿 RULING_1）+判读协议层（v1.3），本件为 OB-4 筛查列首次落盘 | `docs/plans/repo_sync3_20260928/S9_SCREENING.md` + `out/t8_s9_hits.tsv` `out/t8_s9_stats.json` |

## 三、收录/排除与例外台账

**排除（仓面不收，逐件登记）**：`rag_fix3 work/chunks_ra3_raw.jsonl`（12MB>10MB 先质疑规则；附录 A 已登再生产=ra3_fetch.py+仓内 ra3_selected.jsonl 闭集+xml3 源件对账）· `obligrun out/.oblig_{A,B,C}_done.json`（隐藏 done 标记，沿 09-28 隐藏件先例）· 各卡 `__pycache__/` · WIKI `数据资产.md.bak_*`（.bak 先例）· OcularKB 侧 v2.4.2 主库 1.076GB+rag_snapshots 元数据三面（登记件默认裁定）。单文件 >10MB 全树复扫：收录面命中=0（仅上述点名件排除）。

**脱敏例外（本波新增）**：server.py/eyekb_core.py（B5 增量叠加 v4 脱敏面，DESSENS-VERIFIED 逐字节复核）· `kbgov_b5impl_20260928/logs` 等数值证据面零命中直收 · `rag_fix3_20260928/scripts/pointer_register3.py`（裁决商名 CJK 邻界形态一处，v4 规则当场归位）· **T7 masked 两件**（BRIEF/USER_DIRECTIVE 追加六条款，见 `ledgers/T7_EXCLUSIONS.tsv`）。哈希锚例外：各卡 SHA_* 台账指向线上原件的行=镜像内预期 FAIL-EXPECTED-DESENS/EXCLUDED，逐类计数在 T4 D 节（真失败=0）。

**在途卡领地零触碰**：本卡对 `/mnt/D/EyeKB` 与 `/mnt/D/OcularKB` 全程只读（写=仅 plans 面回写本卡产物副本，沿 REPOSYNC2 §八先例）。

## 四、在先裁决继承核对

1. 追加六红线：自家数据零入仓+永久门首跑落码（含 masked 例外逐件登记）✅
2. 激活未发生：README/WIKI/指针面零"已激活/已上线"措辞（T3 断言 2）；OB-5 归 PI ✅
3. 当期主口径=义务 run 26/33 READY（票面 v2.1 净化面）；建议票件≠激活 ✅
4. B5/H1M3=已实装默认生效可写（区别于"激活"）✅；B5 回退态=pre 基线逐字节（T1a 三态+上游 A5 台账）✅
5. Release 六件零触碰（本地重验口径）；升版与否沿 REPOSYNC2 建议案 A（default 未切不先升语料），无新变化本卡不重复呈请 ✅
6. copy 不 move；rag_snapshots 不收 ✅；隐藏件/.bak/pycache 不收 ✅
7. 语料层同源=只盘点不修库，票面层排除机制沿 RULING_1 未动 ✅

## 五、遗留事项

1. **T+7 观察窗（B5 限制条款）**：2026-10-05 前后按 `B5IMPL_COMPLETED.md` 建议采样 mouse_suspected 拒答逐例登记；误拒>0 → 回退 B4 口径需 PI 另批（观察归协调者，非本卡动作）。
2. **masked 规范文的原件管理**：追加六条款含 token 字面原文仅存机器侧/线上 WIKI——外部读者不可见门词表，属安全选择；若 PI 认为需公开口径可另批"规范文例外直收"翻案。
3. **环境观察（非本卡领地）**：venv（Hermes 离线包）botocore/aiobotocore 版本漂移致 `datasets→s3fs` 导入链 09-28 晚崩（golden41 复跑期实测，以 s3fs 桩件绕过，被测件无关）；建议协调者派 default 线修复或 pin。
4. T6 远端 API 新鲜拉取在代理窗失败一次，已按任务书"本地重验"口径降级存档对账并如实登记；如需远端亲验可复跑该脚本（网络通时）。
5. 字节镜像存量面规则命中 49 文件（`out/t5_inventory_register.txt`）清洗与否=REPOSYNC2 §六-2 同款"字节对账面 vs 净面"优先级问题，仍候 PI 裁定。
6. git 占位署名（`EyeKB <eyekb@local>`）沿先例不变；`EYEKB_REPO_STAGING_RS3_20260928` 保留作业现场，归档与否听协调者。

## 六、执行者自证

- 全程未写 `/mnt/D/EyeKB` 与 `/mnt/D/OcularKB`（只读；本卡产物副本回写 plans 面除外，见七节）；Release 零触碰；生产码零改动（同步=镜像搬运）。
- 八门全过后才 push（先测试后上传=第一纪律）。T7 首跑发现→处置→复扫闭环；T5 顺带关闭 REPOSYNC2 登记的 CJK 邻界盲区（v4）。

## 七、线上留痕

本卡产物同步回写 `/mnt/D/EyeKB/plans/repo_sync3_20260928/`（scripts/out/ledgers + S9_SCREENING + 本件），供工作盘侧追溯；该回写属 plans 写作面，不触任何只读区。

*REPOSYNC3 t_09e9a4a3 收尾件（2026-09-28 晚）。八门全绿=push 条件成立；本文件+INTAKE/RECON 两台账随 4/4 层入库。*
