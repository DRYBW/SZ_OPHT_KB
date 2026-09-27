# KB9REG_EXEC_NOTE — KB9 案 B 注册执行收口（t_4bb75b26 · D17 · 2026-09-28）

> 放行：USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加一 D17（PI「可以，缺文献的补文献、缺 wiki 的补」）
> 依据：register/REGISTER_PACKAGE_v2.md（reg-v2.2，外部评审五轮 ACCEPTED，2026-09-27）+ BRIEF_KB9REG_EXEC.md
> 状态：**案 B 已注册、默认 OFF、未激活**；仓镜像已 commit 未 push（测试门归协调者）。

## 1. 装条清单（任务 1 完成）

| # | 产物 | 内容 | sha256（线上权威原件，全表见 exec/out/SHA_NEW_AND_MODIFIED.txt） |
|---|---|---|---|
| ① | `kb/markers/markers_k9_ocs_increment.json` | k9.0-ocs-registered-v1：4 新条 Melanocyte(CL:0000148,10 基因)/Schwann(CL:0002573,4)/Conj_epithelium_suprabasal(CL:1000432 借父条+layer_descriptor,3)/Limbus_Sclera_fibroblast_C1(CL:0000057 挂父条+subtype,3)；每条带 CL id+OLS 回证(obo_id/label/def/raw 回函 sha+retrieved_at)+逐基因 PMID 链（build 证据链原样入条内字段=「补文献」落地）；§0 开发集限定声明随件；C2b 附注在件 | 446adfd4…（截） |
| ② | `kb/markers/_k9_ocs_rules_overlay_v1.json` | 屏蔽/适用性规则+装配规则 v2 旁挂：R1 逐条 scope 表 34 行（A06 全量，30 排除+4 反向）+R2/R3 屏蔽表 283 行（kept 225/R2R3_block 28/R1_drop 30，与注册包 §1 R-3 逐数吻合）+有效基因集(kb9_face_effective_genesets.json)+AV2-1..5 冻结文本+crosswalk_ext 11 行+A09 映射快照 38 行+A03 同源登记+A19 豁免表(20 行)+C2b 附注+§10 残留限制+义务表。**惰性数据件：不在 MARKER_LIBS、不在任何加载 glob、MCP 运行时不加载**（断言在册） | 1c733fd6…（截） |

- baseline/现役文件字节不动：copy 不 move；build/out/register/ledgers 底件只读留档可 diff（exec/out/SHA_PRE_EXEC.txt 110 件 vs POST 复跑 0 变更）。
- OLS 补回证：build 时点 Limbus CL:0000057 无 by_iri 回函 → 本卡照 k2 双通道先例补做（`ledgers/ols_evidence_kb9/*_t4bb75b26*`，回函 obo_id+label=fibroblast 判定通过，禁凭记忆写号）=「缺回证的补」。
- 发现登记（不改数）：注册包 §1 R-5 称 crosswalk_ext「6 行」，build 件实为 11 数据行（4 新条+2 KB7 条补折叠+5 face_v6 消歧名）——overlay 按实际 11 行收录并计行。

## 2. 路由登记默认 OFF + 机读自证（任务 2 完成）

| 件 | 改动 | diff |
|---|---|---|
| `mcp_server/eyekb_core.py` | MARKER_LIBS + "k9_ocs"（仅显式路由；不入 V6_DEFAULT_LIBS 白名单=不入默认）；报错枚举同步；注释块+docstring 登记（仿 lacrimal_v6/KB7-WIRE 先例） | exec/out/diff/eyekb_core.py.diff（17 行面） |
| `mcp_server/server.py` | 版本 KB1v2-0.4-actv6 → **KB1v2-0.5-k9reg**（默认行为不变）；description/query_marker docstring 登记 | exec/out/diff/server.py.diff（15 行面） |

**A5 式机读自证（默认响应零变化，全绿）**：
- exec3 `postdiff_selfproof.json`：**42/42 probe 改后 canon_sha 与 pre 基线全等**（ACT 33 电池+k9 泄漏 9；比较层级=规范序列化 sha256，仅响应对象层面，REVIEWER_LLM Q5 口径沿用）；56 项断言 0 fail：默认 all=60 类无 k9 名、EYEKB_ACT_V6=off 态（43 类）同样无 k9、显式 k9_ocs 三模式可达、白名单未扩、规则旁挂件无代码路径加载、版本已 bump。
- exec4 双态 GOLDEN41（MCP stdio 真往返，逐字继承 wire12c 判据）：**OFF 态 41/41 + 全部 9 项历史合同 True（含 all_list_plus10 历史 33+10 清单合同）；ON 态（生产默认）41/41 + 合同 True**（all_list_plus10 记 ON_NA——该合同成立于 t_5d5853c9 激活前的世界，非本卡引入，零扰动由 exec3+OFF 态另证）；本卡新增 2 合同项 no_k9_in_default / k9_route_reachable 双态均 True。首跑停车教训固化：MCP stdio 子进程默认白名单 env 不含 EYEKB_ACT_V6，OFF 态必须显式 env=dict(os.environ)（照 coordinator_probe 先例）。
- exec5 KB2C 回归：**33/33 PASS**。
- exec6/7 仓副本自测：`exec7_repo_selftest.json` **9/9 PASS**（仓 core 默认 60/off 43 类=线上、k9 markers 值逐基因=线上权威、rules 行数 283/34、stdio list_tools=5、版本串、仓 stdio k9 路由可达）。

## 3. wiki 四件同步（任务 3 完成）

线上 `OcularKB/WIKI/`：①数据资产.md 新增 §8 kb marker 库总表（k9_ocs 注册行+旁挂件说明）；②决策记录.md 落款 2026-09-28 D17 行（含 C2b 附注+Limbus 补回证声明；09-27 C2b 行原文未动）；③体系盘点 §2 前补记「marker 词条库层现状」表（retina_v6/face_v6 已激活、lacrimal_v6 登记 OFF、k9_ocs 注册 OFF+义务清单）；④检索索引.md 新增 §4b k9_ocs/lacrimal_v6 查询姿势。
仓镜像 `docs/wiki/` 同步（脱敏管线，见 §5）。

## 4. §10-6 激活前义务遗留表（下一步激活前必须清）

| # | 义务 | 状态 | 出处 |
|---|---|---|---|
| OB-1 | AV2-5(c) 历史 ON 态门（RUN5 时刻完整请求/存档快照逐字段对账+批组成快照；G1≠历史 ON 保真） | **未清** | 注册包 §4/§10-6 |
| OB-2 | A07 投票前诊断表首跑（pre_vote_diagnostics.tsv 规格 §6；票面与诊断表不一致=run 作废；Q6::26 型掏空须可指认） | **未清** | 注册包 §6/§10-6 |
| OB-3 | 22 视网膜簇 Arm1/Arm2 完整 ranking 一致性补查（排序/去重/加载序副作用） | **未清**（下一波强制输出） | 注册包 §8-4/§10-6 |
| OB-4 | lit 逐条同源排除筛查留档（每次 run 义务；KB9 实跑未落） | **未清** | 注册包 §9/§10-6 |
| OB-5 | PI 另批激活（本卡禁；默认 OFF 是唯一状态，无激活 env 机制） | **永久门** | D17/BRIEF |
| 附 | A12 历史 ON 门对账对象口径、C4 历史 FAIL 记录（22/33）保持不改写；C2b 29/33 仅作附注 | 已按口径登记 | 注册包 §1 上游 |

## 5. 仓/镜像同步对账 + 一个存量发现（上报协调者）

- 仓 `/home/ubuntu/EYEKB_REPO`：4+1 分层 commit（HEAD=01f64d9，ahead of origin/main=5），**未 push——push 前测试门归协调者**（REPOSYNC 铁律：worker 自测全绿≠已测试上传）。本卡自测面全绿：exec3/4/5 + exec7 仓副本 stdio。
- 对账新表 `docs/recon/RECON_kb_mcp_20260928.tsv`：kb+mcp 106 文件 **MATCH=101 / DESENS=4（本卡：2 词条 json+2 py，仓侧均为注释/provenance 字段级脱敏，代码语义零差异）/ PRIOR_DESENS=1（softflags.py c4a8f53 既有）/ 异常=0**。
- 脱敏增量报告 `docs/plans/kb9_ocs_20260927/exec/out/desens_scan_report_20260928.md`（代号版，规则三元组与 REPOSYNC 同源）+ 全量命中台账（线上侧）exec/out/desens_full_inventory_20260928.tsv；本卡面终检 0 泄漏。
- **⚠ 存量发现（非本卡引入，处置归协调者/PI）**：09-27 REPOSYNC 的扫描 DIRS 未含 `kb/`，且 mcp 代码内注释自带裁决商称谓——本轮全量 inventory 实证 **kb/+mcp_server/ 历史件 42 文件、约 3,600 处 R08(REVIEWER_LLM)/R12(AGENT_ROLE) 形态命中**，其中大部分已随 09-27 的字节镜像 push 存在于远端。本卡按纪律**登记不擅动**（apply 严格限定本卡 40 件同步面；顺手把本卡同步的 2 个 py 内历史称谓在仓侧脱敏，故其对账行为 DESENS 而非 MATCH）。处置选项：①对 kb/ 面补一轮脱敏+对账表改标；②判定 R08/R12 属内部协作称谓非敏感项、维持字节镜像（需 PI 表态）；③改线上原件=动基线，禁。

## 6. 红线自证

- 禁写四卡在跑目录（KBX/KBGOV/PME3/GRADE）：零触碰（全程写路径=kb/markers 新 2 件、mcp_server 2 件、plans/kb9_ocs_20260927/{exec,ledgers} 、OcularKB/WIKI 4 件、仓副本）。
- mcp 默认响应逻辑零改动：exec3 42-probe 全等 + 双态 GOLDEN41 另证；禁激活=默认 OFF 唯一状态（件内 status 字段+wiki 三处+义务表 OB-5 齐声明）。
- C4 历史 FAIL 记录不改写；evalset 冻结卷未触碰；并发核查：运行时 kb/mcp_server/plans 无外部新写入（exec1 扫描）。
- 交付物落盘核对：本 NOTE + exec/{scripts×8,out×10,pre_images×2} 全部在 `/mnt/D/EyeKB/plans/kb9_ocs_20260927/`。

*执行：AGENT_ROLE · t_4bb75b26 · 勘误走新版本文件+errata（KB7-WIRE 纪律沿用）。*
