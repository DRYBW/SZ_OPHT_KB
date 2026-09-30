# FINDING_MECHANISM_GAP — KB9ACT 卡动作2 前提与生产事实矛盾（t_abfebe59，2026-09-30）

**性质**：本卡停在动作 2（切换机制）上报裁定；未扩权、未改 mcp_server 代码、未做任何激活写动作。
**判据原句（任务书首节禁扩权条款）**：动作 2 =「按 overlay 文件内 activation 开关条款执行切换（机制=装条时预置的开关，env/配置级可回退=A5 纪律）」。
**实测结论**：该"预置开关"在生产面**不存在**——四源证据 + 本卡机器可读实证，一致。

## 证据链（四源）

1. **生产码**（`/mnt/D/EyeKB/mcp_server/eyekb_core.py`，sha aae70545…，台账 SHA_PRE_ACT_KB9ACT.txt）：
   - `_load_marker_dbs("all")` = 现役三库 + `V6_DEFAULT_LIBS`（硬编码 `("retina_v6","face_v6")`，行156）；k9_ocs 不在白名单。
   - `MARKER_LIBS` 为静态 dict（行142-153），无数据驱动注入点；kb/baselines 的 `_marker_repair_*` glob 与 kb/priors rglob 属工具 4/5（判读层先验），不进 query_marker 词条路径。
   - 全码面 env 消费者仅 4 个：EYEKB_ACT_V6 / EYEKB_KBGOV_B5 / EYEKB_MCP_SOFTFLAGS / EYEKB_MCP_TRACE_TAG——无任何 k9 激活 env。
   - 代码注释自证（行136-138）：「本登记不含激活机制」。
2. **注册收口件** `plans/kb9_ocs_20260927/KB9REG_EXEC_NOTE.md` §4 OB-5 行：「默认 OFF 是唯一状态，**无激活 env 机制**」。
3. **仓镜像自证表** `plans/kb9_ocs_20260927/exec/scripts/exec6_repo_mirror.py:175`：「**（无 env，硬编码 OFF）** | library=k9_ocs 仅显式查询可达」；仓侧 eyekb_core.py 同步核对无 k9 开关。
4. **本卡机器可读实证**（out/SELFPROOF_PRE_STATE.json，stdio 真往返 KB1v2-0.6-kbgov5）：
   - A5：同时设 EYEKB_ACT_K9=on / EYEKB_ACT_K9_OCS=1 / EYEKB_K9_OCS=1 / EYEKB_K9_ACT=1 → 8 探针响应规范序列化 sha 与现役态**逐条全等** = 假想开关名全部惰性。
   - A1/A6：双态默认清单无 k9 四名、provenance 无 k9 文件；A3/A4：显式 library=k9_ocs 四词条可达（注册即在，非激活态——注册码注「激活前既可达，激活不改其语义」）。

## 语义矛盾点

- 探针①「案 A 词条参与 query_marker ranking（目标细胞类上位）」要构成激活前后对照，**必须**改默认路径行为；而改行为只有一条路 = 动 mcp_server 码（白名单/env 开关），本卡红线「禁改 mcp_server 代码」直接封死。
- 本卡可写面「kb/markers overlay 开关态」实际只有件内 `status` 声明字段——MCP 运行时不读 overlay（件内自注 INERT），改它**零行为变化**。若照此执行再报"已激活"，与探针①②的行为级语义相悖，构成虚假动作。

## 待裁两案

**案 wire（建议，先例同构 = ACT-v6 t_5d5853c9）**：协调者照 v6 激活先例扩本卡领地（或另发一张 KB9ACT-WIRE 卡），放行 mcp_server/{eyekb_core.py, server.py} 接线：k9_ocs 入默认白名单 + 仿 `_v6_act_enabled` 的 env 整体回退开关（泪腺/其他库禁入结构保持、恶意值注入拦截照搬）、版本 bump。预估 diff ≤20 行。放行后本卡即续跑动作 2-5：ON 态四断言（①词条入默认 ranking 上位；②22 视网膜簇回归集对 pre/OFF 逐字节全等外溢=0；③黄金 41 tests/verify_repro.py 同口径逐位；④泪腺硬禁不变）+ 回退演练（on→off→on 序列日志，off 态与 pre 全等）+ OBSERVE_NOTE + ACTIVATION_RECORD。
- 注意接线时须一并裁定词条与现役 60 类的**类名消歧口径**（跨库同名走 `k9_ocs::类名` 别名行，先例：v6 正名不变+并行列示）；43/60 类计数合同（all_list_plus10 系）将随默认清单 60→64 变，需在新任务书写死预期值。

**案 decl（纯声明式激活）**：只翻 overlay/increment 的 status 字段+OB-1..5 状态更新（指向 obligrun v2 证据）+wiki 行更新+OBSERVE_NOTE——行为面零变化（词条仍仅显式路由可达）。若 PI「能够全部激活的就激活」本意即此，探针①②须由协调者改写为显式路由语义后方可收卡。

## 本卡已做（全部在可写领地内，两案通用、不可作废）

- ledgers/SHA_PRE_ACT_KB9ACT.txt：激活前 8 件 sha+mtime（overlay 两件与注册落账值 1c733fd6/446adfd4 逐字节一致=无漂移实证）。
- pre/：8 探针 × {default_v6on, default_v6off, explicit_k9, envprobe} = 32 响应件 + INDEX.json（逐条 canon sha）。
- out/SELFPROOF_PRE_STATE.json：六断言全绿。
- scripts/kb9act1_pre_baseline_t_abfebe59.py：自建探针脚本（机读断言，续跑可直接复用）。

## 未做（ contingent on 动作2 裁定）

动作 2（切换）/3（ON 态验证）/4（回退演练）/5（OBSERVE_NOTE）/6-7（ACTIVATION_RECORD 定稿）。
READINESS 四条限制已锁定，届时原样进激活记录：①开发集同源（球门=工程验收非独立验证）；②C2b coarse:X 入数语义跃迁（协议 §4）；③chen_cornea/limbus/sclera source paper 未解析（获权威映射须重跑 OB-4）；④下游 REPOSYNC3 前置盘点已登记。
措辞口径（本卡全程）：工程验收达标激活；禁"独立验证/疗效提升"。
