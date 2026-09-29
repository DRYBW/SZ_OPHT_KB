# REPOSYNC5_COMPLETED — SZ_OPHT_KB 第五轮镜像同步收尾件（追加八预授权波）

- 卡：t_433b5282 ｜ 执行=AGENT_ROLE ｜ 日期=2026-09-29
- 任务书：`docs/plans/repo_sync5_20260929/BRIEF_REPOSYNC5.md`（masked 版；线上原件留机器侧）
- 授权：USER_DIRECTIVE_20260928 追加八（PI 常设自主推进令）+ 本任务书（禁 push——push 归协调者授权窗）
- 基线：远端 main=a0ad857（REPOSYNC4）；staging 起点 HEAD=1febfee（Release 回执，领先远端 1）
- 产出：1febfee 之上叠 **1 个新 commit（REPOSYNC5 前缀）**，可快进；**本卡零 push、零动 Release、零改历史**

## 一、收录清单（四层）

| 层 | 内容 |
|---|---|
| kb 层 | `kb/composition/` v0 全 14 件（EXPECTED_COMPOSITION_v0.{json,md} 逐行 PMID、COMP_SELFFLAG、scripts 三件、ledgers/logs/selfcheck、SHA256SUMS 重锚注记头）= 文献+registry 派生，零患者数据 |
| plans 层 | `seurat_probe_20260928/`（80 件：BRIEF/REPORT v1.0/three_numbers/表 27/脚本 16/日志 34/MANIFEST；**data/ 8 件 >50MB 不收**，size 锚+DATA-EXCLUDED 行+`out/t0_large_files_excluded.tsv` 清单）· `drsc_disc_quant_20260928/`（15 件含 DECISION_TABLE 勾选表）· `comp_prior_20260928/`（DISC-COMP/COMPV1 两任务书）· `QUEUE_20260929.md` · `SYNC_NOTE_20260928_drsc_labels.md`（masked）· 本卡目录（BRIEF masked+门脚本 8 件+out/ledgers+本件） |
| WIKI 层 | directive 追加八入仓（v4+t7b 双层 masked，t7b-subs=8）· 当前状态.md（追加五~八波卡状态行）· INDEX.md 增量 · 新件 项目梳理_20260928.md（masked）；其余 12 件 v4 幂等零漂移 |
| README | 版本注记新节（REPOSYNC5）+ 附录 A 补 SEURATPROBE 大件再生产行 |

**领地剔除（命中即剔，登记待下轮）**：`kb/composition/EXPECTED_COMPOSITION_v1.{json,md}` 与 `plans/comp_prior_v1_20260929/` = COMPV1（t_37a35220）在跑产物，一律不收。

**已收目录复核**：obligrun/kbgov_b5impl/grade_h1m3impl/mouse_ext_precheck/rag_fix3 五目录内容级对账=零实质漂移（17 件差异全部 DESSENS-VERIFIED；BRIEF_REPOSYNC3 差异=t7b masked 层先例）→ 零改动。release_slim_v242 三件仓内=线上 MISSING（RS4 起即登记件）零动。

## 二、八门结果（逐门 PASS，证据=out/）

| 门 | 判据 | 结果 | 证据 |
|---|---|---|---|
| T1 | 新增文件全落对应层目录无越层；COMPV1 *v1* 零收录 | **PASS**（越层 0、out/ 证据件门运行时豁免、领地泄漏=0 剔除后复跑） | `out/gates_summary.json` |
| T2 | 冻结面 sha 前后全等 | **PASS**：evals/tests/kb/mcp_server/rag_snapshots **154 件 changed=0**（票面/registry 基线/生产 kb markers 现役件全含） | `out/gates_summary.json`（before=/tmp rs5_work/sha_before.txt 快照） |
| T3 | v4 幂等脱敏扫描 scan=0 | **PASS**：引擎 --scan 命中文件=0（引擎按路径调用不镜像入仓，沿 RS3 t5 同型）；CJK 邻界强化复扫 DIRS=0；证据件自污染已修（tmp 后落） | `out/t3_v4_engine_scan.txt` |
| T4 | T7 自家数据 token 扫描 HARD=0（永久门） | **PASS**：写作面 HARD 文件=0、字节镜像面 HARD=0；ADVISORY=35（PMC 题录通名 DR1/DR4/conbercept 级，沿 PI"通名级非患者数据可留"口径逐条可留） | `out/t4_T7_scan.tsv` + `ledgers/T7_EXCLUSIONS_RS5.tsv` |
| T5 | 黄金 41 锁环境重跑 | **PASS 41/41 top5 逐位全等**：tests/verify_repro.py @ training-venv（st6.0.0/torch2.13.0+cu130/tf5.13.1=锚定版本），db=本地 Release 预置件（worker 机 <RAG_SLIM> 目录）零下载；systemd-run MemoryMax=8G 托管，峰值 6.1G | `out/t5_golden41.txt`（journal 摘录） |
| T6 | 新鲜克隆自证 | **PASS**：git clone file:// → /tmp 干净目录，HEAD 一致、py_compile 257 件零失败、门脚本克隆内 T1/T3/T4 PASS、verify_repro 克隆内 41/41、fsck clean、tracked 2961=2961 对账全等 | `out/t6_fresh_clone.txt` |
| T7 | directive/WIKI mask 版逐件人查 | **PASS**：凭据字面=0（sk 前缀/pat 前缀/gh* 前缀/私钥块四形态机扫=门脚本 pat_secret 规则，本文件不复写其字面）；机器绝对路径在 token 化面（wiki 新增 4 件+QUEUE/SYNC_NOTE+BRIEF）=0（rs5_pathnorm v2 token 化，台账 `out/t2b_pathnorm_ledger.tsv`）；masked 再生件逐件人查记录=本表；证据镜像面机器路径=沿 RS3 先例字节直收（manifest -c 全锚：composition 9/9、drsc 14/14、seurat 79/79 OK） | `ledgers/T7_EXCLUSIONS_RS5.tsv` |
| T8 | commit 拓扑 | **PASS**：HEAD=新 commit 恰在 1febfee 之上叠 1；a0ad857（远端 main）为祖先=可快进；历史 commit 零改写（rebase/filter 未用） | `out/t8_topology.txt` |

## 三、例外与偏差登记（如实）

0. **哈希锚定局限（T6/T8 证据件）**：最终 commit sha 无法自含于其证据快照（哈希递归），权威 sha=看板 summary 回传；缓解=终态复跑门电池 6/6 PASS + tracked 对账全等。
1. **SHA256SUMS/MANIFEST 重锚头注记**：三件 manifest 各加一行 `#` 注释（RS5 re-anchor 说明），条目哈希零改动、sha256sum -c 全过。
2. **masked/token 化件线上原件全部留机器侧**：directive、项目梳理、当前状态、INDEX、QUEUE、SYNC_NOTE、BRIEF_REPOSYNC5；逐件=`ledgers/T7_EXCLUSIONS_RS5.tsv`。
3. **门体系自净豁免**：rs5_* 脚本与 t2b 台账含 needle/映射表字面（沿 RS3 t7_own_tokens 自净条款同型）。
4. **过程偏差（已闭环）**：pathnorm 首版作用域误含证据镜像面 → 触发三件 manifest 失配 → 即时撤销（rs5_pathnorm_revert.py 从线上重刷，mismatch-vs-online=0）并范围裁定沿 RS3 先例；期间一次幽灵目录污染（脚本锚定 bug）已清除，未入 commit（tracked 对账 T6=2620 全等）。
5. **gpu-exclusive-maint-toctou 技能镜像**：仓内无该镜像（docs/skills 仅两镜像+protocols）→ 按任务书"登记不造"，09-29 更新（Xid79 遥测判供电路径+flock 教训）留机器侧。
6. **>50MB 不收**：seurat data/ 8 件（最大 3.02GB）只收 size 锚+清单；`tables/trackP_DS1_celllabels.csv`(15MB)/`trackS_DS1_celllabels.csv`(17MB) <50MB 直收。
7. 资源纪律：零下载、CPU、T5 走 systemd-run --user MemoryMax=8G；线上 /mnt/D 全程只读零写入；copy 不 move。

## 四、交协调者（push 归你，本卡零 push）

- 快进推送：`git -C <staging> push origin HEAD:main`（a0ad857→REPOSYNC5 终 commit，领先恰 1+既有 1=2 commits 上远端；终 sha 以看板 summary 回传为准）
- 本地待推 commit 链：1febfee（Release 回执，追加八③授权窗自动推）→ REPOSYNC5 本 commit
- 追加八③"为纯报账类小 commit 不单独请扫码"=本 commit 随下一授权窗顺路推
- 异机真下载最后跳（clone+Release 拉取+verify_repro）=另一授权窗待办（RELEASE_PUBLISHED_20260928.md 待办节）
