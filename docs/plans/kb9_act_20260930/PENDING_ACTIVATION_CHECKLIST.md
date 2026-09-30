# PENDING_ACTIVATION_CHECKLIST — KB9ACT 续跑执行规格（t_abfebe59 编制，2026-09-30）

> 用途：本卡因动作 2 机制缺失 blocked（见 FINDING_MECHANISM_GAP.md）。协调者/PI 对案 wire（接线放行）
> 或案 decl（声明式激活）拍板后，续跑 worker（含本卡重派）**照本件直接执行，无需重做取证**。
> 已就位资产：ledgers/SHA_PRE_ACT_KB9ACT.txt（激活前 8 件台账）、pre/（8 探针 × 4 态 32 响应 + INDEX.json
> canon sha）、out/SELFPROOF_PRE_STATE.json（六断言全绿）、scripts/kb9act1_pre_baseline_t_abfebe59.py（可复用）。

## P0 裁定登记（block 期间禁自决）

| 项 | 内容 |
|---|---|
| 拍板方 | PI 或协调者（default4），选项=案 wire / 案 decl |
| 案 wire 放行的写面 | mcp_server/eyekb_core.py + mcp_server/server.py（仅接线最小 diff）；其余红线不变 |
| 案 wire 放行的新预期 | 默认 all 清单 60→64 类（+4 k9 条，逐条核对类名消歧口径）；版本串 bump（如 KB1v2-0.7-k9act）；回退 env=仿 _v6_act_enabled 风格整体开关 |
| 落地前状态核对 | 恢复本卡时先 `stat` pre/ 33 文件 + 台账，若 mtime 晚于 2026-09-30 02:18 且非本卡产物=基线过期，重跑动作 1 再续 |

## 案 wire 续跑规格（推荐路径，ACT-v6 同构）

### W1 接线（需放行后执行）
1. `V6_DEFAULT_LIBS` 同级新增 `K9_DEFAULT_LIBS=("k9_ocs",)`；`_load_marker_dbs` 默认分支按新 env 开关
   `EYEKB_ACT_K9_OCS ∈ {0,false,off,no}=OFF` 追加白名单；lacrimal 不入白名单结构保持。
2. 消歧口径照先例：4 条与现役 60 类同名冲突走 `k9_ocs::类名` 别名行，正名行不变（先例：v6
   "正名不变+并行列示"入观察，激活记录照登）。
3. server.py 版本 bump + docstring/description 把 REGISTERED_DEFAULT_OFF 改 ACTIVE_ON_DEFAULT(env
   可回退)；**禁改规则内容/词条本体**（两 overlay 文件字节不动，sha 复验=台账值 1c733fd6/446adfd4）。
4. 接线 diff 存 plans/kb9_act_20260930/wire_diff/（仿 exec/out/diff/ 先例）。

### W2 ON 态四断言（任务书动作 3，自建探针已部分就位）
- ① 词条参与默认 ranking 上位：Q6（TRPM1/MLANA/TYRP1/PMEL/DCT/TYR）与 Q7（MPZ/SCN7A/SOX2）
  **默认态（不设 library）** celltype_ranking 中对应类上位；逐条存 out/ON_Q*.json。
- ② 外溢=0：22 视网膜簇回归集——ranking 取自 /mnt/D/EyeKB/plans/obligrun_20260928/out/OB3_consistency.tsv
  （22/22 在册，与任务书"抽 22 视网膜簇回归集"同源锚定；执行时显式登记锚=该件，非本卡自创口径）；
  ON 态逐簇响应 canon sha == pre/default_v6on 同名 sha；**注意**：Q1 类目清单类计数 60→64 属激活
  预期变化，外溢对照须排除"清单类"本身、逐字节全等只对非案 A 簇响应。
- ③ 黄金 41 逐位：照仓侧 /home/ubuntu/EYEKB_REPO/tests/verify_repro.py（sha 18cfe145…）同口径跑
  41/41；若 k9 接线致某 golden 用例合理位移（如检索面含眼表新条），停车如实报，不放宽判据。
- ④ 泪腺硬禁：默认清单零 lacrimal 名 + env 恶意注入测试（值=lacrimal_v6/全库名等，行为=只整体
  开关，不得把 lacrimal 挤进默认）照 v6 先例四组。

### W3 回退演练（任务书动作 4，必做一遍）
设 EYEKB_ACT_K9_OCS=0 → 8 探针 canon sha 逐条 == pre/default_v6on 全等（机读，A5 式）；
切回 ON → 与 W2 输出 sha 全等。日志序列 off→on→off→on 存 out/ROLLBACK_DRILL.log。
回退操作人说明（消费方视角）写进 ACTIVATION_RECORD：env=0 即回退，无需改数据（A5 纪律）。

### W4 OBSERVE_NOTE + 激活记录（任务书动作 5-7）
- plans/kb9_act_20260930/OBSERVE_NOTE.md：仿眼表 v6 条款——激活后一周采样窗（起算=W2 全绿日），
  口径：每日 calllog（/mnt/D/EyeKB/logs/mcp_trace/calls_*.jsonl）抽 query_marker 默认态请求，
  人工/机械核异常（k9 条误上位非眼表类、ranking 异常翻转、泪腺泄漏）；任一命中即回退+登记。
- ACTIVATION_RECORD.md：前后 sha 台账（前=已就位，后=切换复跑）+ 探针输出索引 + 回退演练日志
  + READINESS 四条限制**原样**（①开发集同源非独立验证②C2b 语义跃迁③chen_* source 未解析④下游
  REPOSYNC3 登记）+ 措辞=工程验收达标激活（禁"独立验证/疗效提升"）。
- 禁 push；仓侧同步由协调者复核后走 REPOSYNC。完成→ kanban_complete；任何断言红→ 停车 block。

## 案 decl 续跑规格（若 PI 本意=声明式）
1. overlay `status` 字段：INERT_REGISTERED_DATA → ACTIVE_DATA_LAYER_DECLARATIVE（保留 INERT 原句作
   history 注）；increment `status`：REGISTERED_DEFAULT_OFF → EXPLICIT_ROUTE_ONLY（PI 2026-09-30
   放行登记）。两文件其余字段字节不动（改 status=声明式激活唯一动作，禁改规则/词条）。
2. obligations_before_activation：OB-1..OB-4 status → 清（证据指针=VERDICT_OBLIGRUN_v2 + ADD1 A4）；
   OB-5 → PI 2026-09-30 已批（WeCom 原话逐字入注）。
3. wiki 数据资产.md §8 行状态同步（KB9ACT 是否兼管 wiki 面由协调者裁定——v6 先例中 wiki 同步属
   激活卡动作）。
4. 探针改写为显式路由语义（①=library=k9_ocs 可达且上位（注册即在，如实标注"非本卡引入"）；②=
   默认态零变化逐字节=pre 全等（天然成立）；③④照跑作零扰动证明）；回退演练退化为"状态字段
   改回+sha 复验"。
5. **红线**：对外不得写"词条已入默认响应"（行为面未变），只能写"注册态由默认 OFF 转显式路由
   永久在册"。

## 禁区（两案通用）
kb/composition（COMPV1X 在跑）、mcp_server 代码（案 decl）、evalset 冻结面、RAG 目录、push；
overlay 规则内容本身；现役 baseline/v6 文件字节。
