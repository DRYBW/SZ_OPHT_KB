# ACTIVATION_RECORD — KB9 案A（k9_ocs 词条入默认检索面）激活记录

卡: t_abfebe59（KB9ACT）· 执行: pi-chief · 日期: 2026-09-30 · 版本: KB1v2-0.6-kbgov5 → **KB1v2-0.7-k9act**
状态: **已激活·案S核定收尾**（RULING_KB9ACT_2.md 2026-09-30 裁定=案S：② 按 OB-3 冻结分解口径核定通过；全部门禁绿；生产当前=接线 ON 默认态，回退开关已在位并经演练验证；跟票观察窗口 OBSERVE_NOTE 生效至 2026-10-07）

## 1. 放行依据（逐字继承）
- PI 原话（2026-09-30, WeCom）："按照我们现有的数据，能够全部激活的就激活……验证之后确实可以的那就可以直接上传"
- 证据基座: docs/plans/obligrun_20260928/VERDICT_OBLIGRUN_v2.md = READY（OB-1..4 全清、P1 26/33≥24、P2 strict 0/33）+ out/ACTIVATION_READINESS.md 建议票
- 接线放行裁定: RULING_KB9ACT_1.md（协调者 default4，2026-09-30）——采案 wire，可写扩至 mcp_server/{eyekb_core,server}.py，diff≤20 行，禁 push
- ②号门核定裁定: RULING_KB9ACT_2.md（协调者 default4，2026-09-30）——采**案S**：② 按 OB-3 冻结分解口径核定通过（非k9子序列全等 22/22 + 新增仅案A尾部插入 + provenance/快照字段差异声明豁免 + 泪腺零泄漏）；移动球门自查已备案（字面②与 OFF 恒等门物理矛盾，实质五门零放松）
- 范围锁: 仅案A（k9_ocs 增量词条 OFF→生效）。v2.4/v2.4.1 RAG 默认切换不在本卡（门③ FAIL 在册）；face/v6 勿动；**泪腺维持禁入**。

## 2. 机制如实修正（防后人再踩）
任务书动作2前提"机制=装条时预置的开关"**为误**——生产面不存在任何预置 k9 激活开关（四源证据+假想 env 惰性实证见 FINDING_MECHANISM_GAP.md）。实际激活机制=**本次接线**: eyekb_core.py 新增硬编码白名单 `K9_DEFAULT_LIBS=("k9_ocs",)` + env 整体开关 `EYEKB_ACT_K9`（∈{0,false,off,no}=OFF 回退；未设/其余值=ON），完全仿 EYEKB_ACT_V6 语义（ACT-v6 t_5d5853c9 同构先例）。RULING §3 命名 EYEKB_ACT_K9 为准（CHECKLIST 草拟名 EYEKB_ACT_K9_OCS 被裁定覆盖）。

## 3. 接线台账
- diff: wire_diff/KB9ACT_wire_core.diff + KB9ACT_wire_server.diff + KB9ACT_wire_all.diff；**numstat: core +8/-0, server +6/-1 = 合计 15 行 ≤20 ✓**
- py_compile 双件 OK；消歧实测: k9 四条与现役 60 类**零同名冲突**（4 正名入列，无 "k9_ocs::" 别名行产生；W1.2 预设的别名路径未触发，正名机制保留原样）
- 规则内容/词条本体零改动: overlay 两件 sha 复验 = 注册落账值逐字节一致（_k9_ocs_rules_overlay_v1.json=1c733fd6…、markers_k9_ocs_increment.json=446adfd4…）
- sha 台账: ledgers/SHA_PRE_ACT_KB9ACT.txt（8 件, 02:18）+ ledgers/SHA_POST_ACT_KB9ACT.txt（接线后）；CHANGED 仅 eyekb_core.py/server.py；softflags/calllog/qa_v2/verify_repro/overlay 全 UNCHANGED

## 4. 门禁结果（执行序按 RULING §3 硬门）
| 门 | 判据 | 结果 | 证据 |
|---|---|---|---|
| a) OFF 态零漂移 | EYEKB_ACT_K9∈{0,false,off,no} 四值 × (8 探针 vs pre/default_v6on + 22 簇 vs 旧码基线 CAP_PREWIRE) canon sha 逐条全等 | **PASS**（30/30×4 值全等；版本串不在响应体，bump 零扰动） | out/CAP_OFF1..4.json, out/ROLLBACK_DRILL.log, out/MALICIOUS_ENV_GROUPS.json |
| b) 黄金 41 | tests/verify_repro.py 同口径（repo 侧引擎 + 本地 Release 预置件 RAG_SLIM_V242；T5 先例同环境锁版 training-venv） | **PASS 41/41** top5 逐位全等（42.2s, 峰值 4.6G, systemd-run MemoryMax=8G） | out/GOLDEN41_postwire.log |
| c① 词条入默认 ranking 上位 | 默认态不设 library: Q6(TRPM1/MLANA/TYRP1/PMEL/DCT/TYR)→Melanocyte **rank0 n=6**；Q7(MPZ/SCN7A/SOX2)→Schwann **rank0 n=3**；OFF 态两者零出现；Q2-Q5 cell_type 模式 markers 面 == 注册态 explicit_k9 内容逐字节（正名直取） | **PASS** | out/GATE_ON_ASSERTS.json / GATE_ON_ASSERTS_v2.json, out/CAP_ON1/2.json |
| c② 外溢=0（22 视网膜簇 vs OFF 基线逐字节全等） | **字面判据 FAIL/不可满足** → 如实停车待裁（见 §6）。分解证据: 19/22 去 provenance 后全等；3/22 差异=ranking/unranked **尾部 n=1** k9 条插入（TRPM1↔Melanocyte 2 例、炎症基因↔Conj_epithelium_suprabasal 1 例，跨组织真实共表达）；provenance.files/soft_flags.data_snapshot 差异=恰 1 行 k9 文件台账；**非 k9 子序列 22/22 逐字节全等、top 位次零位移、B5 治理字段零变化**（=放行证据基座 OB-3 的冻结判据口径，OB3_consistency.tsv 22/22 verdict 清） | **PASS（案S 分解口径核定，RULING_KB9ACT_2）** | out/GATE_ON_ASSERTS_v2.json（bad_rank 清单+分解断言全绿明细） |
| c③ 黄金 41 | =门 b | PASS | 同上 |
| c④ 泪腺硬禁 | 默认清单 64 类零 lacrimal 名；env 恶意值组（lacrimal_v6 / retina_v6,face_v6,lacrimal_v6 / ALL）响应与 ON1 态 30/30 全等=只整体开关不可注入库名；Q8 泪腺管道 payload 去台账后与 pre 全等（禁入结构不变） | **PASS** | out/MALICIOUS_ENV_GROUPS.json |
| d) 回退演练 | off→on→off→on 序列（含四 OFF 值语义）；OFF 态≡pre 基线、ON 态确定性全等；**消费方回退操作=调用进程 env 设 EYEKB_ACT_K9=0（无需改任何数据，A5 纪律）** | **PASS**（ALL PASS） | out/ROLLBACK_DRILL.log |

## 5. READINESS 四条限制（随票原样入册，非本卡新增）
① 开发集同源，本球门=工程验收非独立验证（注册包 §0/§2）；② C2b coarse:X 入数语义跃迁（协议 §4）；③ chen_cornea/chen_limbus/chen_sclera source paper 未解析的筛查残余限制（获权威映射须重跑 OB-4）；④ 激活后下游 REPOSYNC3 前置盘点项已登记（仓侧同步由协调者复核后代推，**本卡禁 push 未推**）。

## 6. ②号门争议与终裁（曾 block 本卡两轮，RULING_KB9ACT_2 已核定=案S）
任务书动作3②"非案A簇响应与 OFF 基线逐字节全等"在"词条入默认检索面"机制下**结构上不可满足**：加载库清单变化必然改写每个默认态响应的 provenance/台账（v6 激活先例同此——其字节全等门只设在 OFF 回退态），且视网膜面板与眼表词条存在真实共表达基因（TRPM1 等）致尾部 n=1 命中。两案（详见卡内 comment）:
- **案 S（建议）**: ② 判据按放行证据基座 OB-3 冻结口径核定为分解判据（非 k9 子序列逐字节全等 + 新增条仅案A尾部插入 + 台账 delta 恰等 k9 文件行 + 泪腺零泄漏）——本证据 22/22 全绿，激活维持，跟票观察按 OBSERVE_NOTE 执行；
- **案 R**: 维持字面逐字节全等 → 激活行为面不可达，回退（env EYEKB_ACT_K9=0 即回，或撤销接线），案A 维持显式路由态。
**终裁（default4，2026-09-30，RULING_KB9ACT_2.md）= 案S**：② 按 OB-3 冻结分解口径核定 PASS；实质五门（OFF 零漂移×4值组、黄金41、c①正名入列、c④泪腺硬禁、回退演练）全部按原判据跑过零放松；激活维持，OBSERVE_NOTE 跟票一周生效（采样口径同 A2 眼表模式）。收尾轮实证复核：eyekb_core.py/server.py/overlay 两件 sha256 与 SHA_POST 台账逐字节一致，无外部漂移，未重跑任何已过门禁。

## 7. 措辞纪律（对外口径）
本次激活口径=**工程验收达标激活**（门禁表 §4 为准）；**禁写"独立验证/疗效提升"**。43/60 类计数合同（all_list_plus10 系）默认清单 60→64 为激活预期变化（RULING 已锁预期值）；旧快照期望过期沿 RAGFIX 先例登记，非本卡所致。

## 8. 产物索引
FINDING_MECHANISM_GAP.md · PENDING_ACTIVATION_CHECKLIST.md · RULING_KB9ACT_1.md · ledgers/SHA_{PRE,POST}_ACT_KB9ACT.txt · pre/（8×4 基线+INDEX.json）· wire_diff/（pre/ post/ 3×diff）· out/CAP_{PREWIRE,ON1,ON2,OFF1-4,MAL1-3}.json（11 态×30 响应）· out/GATE_ON_ASSERTS{,_v2}.json · out/ROLLBACK_DRILL.log · out/MALICIOUS_ENV_GROUPS.json · out/GOLDEN41_postwire.log · scripts/kb9act{1,2,3}_*_t_abfebe59.py · OBSERVE_NOTE.md · 本件
