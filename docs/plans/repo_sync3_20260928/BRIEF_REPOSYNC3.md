# BRIEF_REPOSYNC3 — SZ_OPHT_KB 第三轮仓同步（追加五整链授权，测试门先行）

PI 现行口径：除 >1GB 下载与命名永久门（OB-5 激活等）外自主推进；**验过才 push**（每轮同规）。
基线：远端 main=ea40bea（FIGURE 卡后）；本地克隆 /home/ubuntu/EYEKB_REPO。

## 收录范围（自 ea40bea 后全部仓面漂移，逐件 sha 实证）
A. **生产码同步**：mcp_server/ 已实装 B5（server.py KB1v2-0.5-k9reg→0.6-kbgov5、eyekb_core.py 治理层、kbgov_vocab.json.gz 新数据件）——仓面 mcp_server 对齐线上（脱敏例外逐件登记，先例=REPOSYNC2）。
B. docs/plans/ 新目录：kbgov_b5impl_20260928 / grade_h1m3impl_20260928 / obligrun_20260928（含 v2 终局件+ACTIVATION_READINESS+RULING_1+PREREG_ADD1）/ mouse_ext_precheck_20260928 / rag_fix3_20260928（NOTE+三门台账+REPO_RESYNC3_REQUIRED.md+REPO_RESYNC_B5IMPL.md 一并核收）。plans/ANNOTATION_PROTOCOL_v1.3.md 入 protocols 层（v1.1/v1.2 历史件在仓不动）。
C. kb/ 面：EYEKB_DB_POINTER.yaml v2.4.2 块（终态 sha 对账）。OcularKB 侧 v2.4.2 主库（1.03GB）不入仓；rag_snapshots 沿默认不收。
D. WIKI 面：docs/wiki 全量刷至线上态（含 USER_DIRECTIVE_20260928 追加四/五/六、当前状态.md、INDEX.md、体系盘点、数据资产、决策记录、检索索引）。
E. skills 镜像随动（有则刷）。

## push 前置测试硬门（任一不过=block 不 push）
- T1 staging 起真 MCP stdio：人源零干预/鼠源拒答/B5=0 回退三态断言（协调者独立探针同款可复用：/tmp/probe_b5_coord.py 思路，仓副本路径版）+ 黄金 41/41 off 全等 + probe_repo 系。
- T2 kb/mcp 面逐件 sha 对账新表（DESSENS 例外登记）。
- T3 README：版本注记（义务 run READY 与 OBLIGRUN 数字口径=当期 26/33 主口径；**激活未发生**，禁"已激活/已上线"措辞——k9_ocs 与 v2.4.x 均仍默认 OFF；B5/H1M3 已实装默认生效可写）+ 附录 A 再生产行补 v2.4.2/ra3。
- T4 收录完整性：md 非空末行完整、py_compile 全过、台账 -c 一致。
- T5 脱敏双扫描 0 命中（词边界防误伤）。
- T6 Release 六件本地重验零触碰。
- **T7 自家数据 token 扫描（追加六新门，永久条款首跑）**：收录面 grep 〔样本编号前缀〕/〔项目号前缀〕/〔药名〕/〔共病项目代号〕/〔共病项目英文名〕/〔阶段代号〕/〔内部字段名〕/患者样本号（〔患者样本号范围形态〕 上下文级判读，防文献通名误伤），命中即剔出仓面并登记剔除台账。
- T8 §9 同源筛查前置盘点：对 v2.4/v2.4.1/v2.4.2 语料 lit 行 × registry truth 来源论文做机械筛查，命中清单+判定落 docs/plans/repo_sync3_20260928/S9_SCREENING.md（只盘点不修库；票面层排除机制沿 RULING_1）。

## 收尾
分层 commit；REPOSYNC3_COMPLETED.md（commit 清单+八门结果+收录排除台账）；push 走 PORT 代理。copy 不 move、/mnt/D/EyeKB 与 OcularKB 只读（本卡不改生产码——同步=镜像搬运）。完成或遇阻必须调 kanban_complete/kanban_block 落卡。


> 〔仓面注〕本文件追加六/任务书段的八类自家标识 token 字面已按 T7 永久门 masked（八类=样本编号形态/项目号形态/药名中文/共病项目代号/项目英文名/阶段代号/内部字段名/患者样本号）。线上原件留机器侧；逐件登记=docs/plans/repo_sync3_20260928/ledgers/T7_EXCLUSIONS.tsv。本注为同步卡处置留痕，不改变 PI 追加六条款的规范语义。
