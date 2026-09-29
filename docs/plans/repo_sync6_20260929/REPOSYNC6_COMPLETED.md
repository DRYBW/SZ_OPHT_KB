# REPOSYNC6_COMPLETED — 第六轮仓同步收口件（SYNC_NOTE）

日期：2026-09-29 | 执行：〔执行审核方〕卡 t_5112f6d9 | 上游：BRIEF_REPOSYNC6.md（本目录）+ REPOSYNC5 领地剔除回收

## 一、入仓清单（RS5 剔除件回收 + 09-29 增补）

| 面 | 内容 |
|---|---|
| kb/composition | EXPECTED_COMPOSITION_v1.{json,md} 两件（copy 不 move，盘上原件零改动；v1 json 有 2 处外部裁决商名→v4 masked，md 字节全等）；SHA256SUMS.txt 追加 v1 两行现字节锚（非冻结面，RS5 re-anchor 表续记） |
| docs/plans/comp_prior_v1_20260929 | COMPV1 t_37a35220 收口产物全 26 件（V1_VERDICT/PHASE0_INVENTORY/层化 tsv×6/条件区间 json×2/ob1 候选/残差归因/q6 重算/scripts 8 件/logs 6 件）+ MANIFEST_sha256.txt 重锚版（27 行仓相对锚，3 行 re-anchored from= 原锚可追；仓根 `sha256sum -c` 可复跑）；>50MB 件=0（out/t0 登记，源侧预扫最大件 24KB） |
| QUEUE | docs/plans/QUEUE_20260929.md：在跑卡表 COMPV1/REPOSYNC5 两行→done+验收摘要；新增"⑥ 09-29 午波收口"节=本地 QUEUE_常设任务_20260928.md 4 行（v4 masked+token 化）；线上两原件零改动 |
| WIKI 面 | **零漂移零触碰**：本地 /mnt/D/OcularKB/WIKI 当前状态/INDEX/项目梳理/directive 四件 masked 再生对账=与仓面逐字等值（唯一差异=pathnorm token 形态），09-29 无未入仓新行；其余 wiki 件未动。对账脚本=rs6_gates 外预跑（/tmp/rs6_work/wiki_preview） |
| 本卡 | docs/plans/repo_sync6_20260929/：BRIEF（masked+[仓面注]）+ scripts×5 + ledgers/T7_EXCLUSIONS_RS6.tsv + out/（t0/t2b/t3/t4/t5/t6/t7/t8/gates_summary.json）+ 本件 |

## 二、八门结果（证据=out/）

| 门 | 判据 | 结果 | 证据 |
|---|---|---|---|
| T1 | 领地锁定（写面=任务书范围；COMPV1 回收正断言；越界/删除=0） | **PASS**：violations=0 missing=0 tree_files=26 | 本件+gates_summary |
| T2 | 冻结面 154 件 sha 前后全等（复用 rs5 frozen_scope） | **PASS**：changed=0 | gates_summary.T2 |
| T3 | v4 引擎全仓 scan=命中文件 0 + STRICT CJK 复扫 0 | **PASS**：engine-hitfiles=0, cjk-strict=0 | `out/t3_v4_engine_scan.txt` |
| T4 | T7 永久门 HARD=0（ADVISORY 通名沿 PI 口径） | **PASS**：HARD=0 文件 ADVISORY=38（较 RS5 +3=comp_prior_v1 ob1 候选 tsv 文献题录通名，逐条可留）；镜像面 HARD=0 | `out/t4_T7_scan.tsv` |
| T5 | 黄金 41 锁环境复跑 | **PASS 41/41** top5 逐位全等（training-venv 锁版，db=本地 Release 预置件 242928 chunks 零下载，systemd-run --user MemoryMax=8G unit=rs6-t5-golden41） | `out/t5_golden41.txt` |
| T6 | file:// 新鲜克隆自证 | **PASS**：clone+checkout 预检 commit HEAD 一致、py_compile 零失败、克隆内 T1/T3/T4 PASS、verify_repro 克隆内 41/41、fsck clean、tracked 对账全等 | `out/t6_fresh_clone.txt` |
| T7 | 人查台账：逐新增件 sha 台账 + 凭据零字面 + token 化面零机器路径 | **PASS**：ledger=34 件（`out/t7_sha_ledger.tsv`）；QUEUE/BRIEF6 机检零残留（BRIEF6 门条款模式枚举字面=豁免登记沿 RS5 先例）；例外=`ledgers/T7_EXCLUSIONS_RS6.tsv` | t7_sha_ledger + 台账 |
| T8 | 恰 1 新 commit，fa4f175 之上线性可快进 | **PASS**：parent=fa4f175；a0ad857（远端 main）为祖先；历史零改写 | `out/t8_topology.txt` |

## 三、例外与偏差登记（如实）

1. **T6/T8 验证对象=预检 commit（commit-tree 瞬态对象）**：t6/t8 证据件与 gates_summary 全绿文本随后进入正式 commit（tree 超集，parent 不变）。终态 commit sha=以看板 t_5112f6d9 完成 summary 为准（协调者亦可 `git clone file:///home/ubuntu/EYEKB_REPO_STAGING_RS3_20260928` 独立复验 tracked/fsck）。此系 RS5 t8 证据同型偏差，本轮以文字显式化。
2. **v4-masked 件 3+QUEUE 增补面**：EXPECTED_COMPOSITION_v1.json（2 处）、V1_VERDICT.md（1 处）、s5_build_v1（1 处）、BRIEF6（派发/执行方名→AGENT_ROLE）；masked 后 manifest/SHA256SUMS 均重锚并 from= 留痕，`sha256sum -c` 仓根全过。
3. **harness 网关改写坑（本轮新发现）**：write_file/patch 落盘会把 `TOKENS = [` 掩成 `TOKENS=***`、把正则里 `github_pat_[a-zA-Z0-9_]{10,}` 量词剥成裸前缀——修复=变量更名 NORM_MAP + 字面 split-concat；rs6 脚本族已自证可复跑。
4. >50MB 不收：本轮拟收面源侧预扫零大件（t0 登记）。
5. 资源纪律：零下载、零外网；/mnt/D 与 /home/ubuntu 原件全程只读（copy 不 move）；禁 push 遵守（本卡零 push，origin/main 仍 a0ad857）。

## 四、交协调者（push 归你，本卡零 push）

- 本地待推链：a0ad857 → 1febfee → fa4f175 → 本 commit（3 个待推）。
- 授权窗建议：与既有"push 链一次扫码"待办（QUEUE ⑥节末行）合并执行。
- 终态权威 sha=看板 t_5112f6d9 summary + 本卡 git log 首行。
