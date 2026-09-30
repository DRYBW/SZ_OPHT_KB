# DRSC_REANN_REPORT — dr-sc 现栈重注一致性测试报告（t_3dd4caaf，2026-09-30）

## 0. 定性（红线，全文生效）
旧参考 = redo_v2 anno_v2 签字件（自家共识+人工签字，SIGNOFF 2026-09-28），**非外部真值**。
本测 = **一致性/漂移回归**，不是正确率评测。全文只使用"一致率/翻转/漂移/归因"措辞；
分歧簇 = 送 PI 复核候选，不判任一方错。PREREG sha=fdd4d0cbe4a31c79…（先落纸后起跑，§5 全链合规）。

## 1. 头条（两口径同时给，取严=strict 为主判）
| 指标 | strict | 谱系级 | 分母口径 |
|---|---|---|---|
| **E2-ON 主臂 vs 旧参考** | **18/19 = 94.7%** | **19/19 = 100%** | 32 − 豁免7 − 特判(簇30)1 − 无共识5 = 19 |
| E2-OFF 归因臂 vs 旧参考 | 18/20 = 90.0% | 19/20 = 95.0% | 同口径，OFF 无共识4 |
| E1 引擎臂 vs 旧参考 | 24/24 = 100% | 24/24 = 100% | 引擎恒具名（弃权不存在） |
弃权/无共识=合法结论单列出分母（ON 臂 5 簇，见 §5）。

**判读矩阵落格：格 1** —— 一致率高（≥80% strict，豁免组除外）且**意外漂移 = 0**（FAIL 档不触发）
→ 现役系统（0.7-k9act 全栈：v6 面板+face v2.1+k9 激活+B5 治理接线后）对旧好结果**稳健**，
"内容多了质量降"的疑虑在本参照上否定。唯一具名偏移（簇 23）归因=粒度墙（②桶），非新增内容位移。

## 2. 三方对照（全 32 簇）
明细 = CONSISTENCY_TABLE.tsv（cluster/anno_v2/old_grade/E2ON/E2OFF/E1/双口径/flip/票面）。
- 28/32 簇三方全部同名（含豁免组内一致簇）；
- 引擎臂与旧参考零意外分歧（30 簇=dissent、31 簇=Endo 两处在册伪影/特判，见 §5）；
- E1 对簇 31 输出 Micro（83.4% share）——与 HRCA kNN"Micro 主导 53%"同类=**引擎/参考缺 Endo 类的伪影**（E-b 在册），不读作 Endo 反证。

## 3. 激活净位移（ON vs OFF，本轮 KB9ACT 的版本归因）
- **证据面层**：双臂 digest 差异仅命中 3 簇（15/17/27 的 kb ranking 上位 Schwann/Melanocyte 眼表新词），其余 29 簇面全等（ON sha=dd4f2b1574c74065 / OFF sha=2bb82dac643ce74d）。
- **判读面层**：簇级共识翻转 = **1 簇（15）**——OFF 臂三票同向 coarse:RGC/RGC → 定名 RGC（与旧标 AC 不一致，具名错）；ON 臂三票全弃权（席 A 明写"kb 仅命中 Schwann 非视网膜词表，证据不足"）→ 无共识。
- **方向解读（如实，不判优劣）**：k9 眼表新词上位使簇 15 从"OFF 臂具名（且与旧标不一致）"移向"ON 臂弃权"——本轮激活在视网膜参照上的净位移表现为**更保守**而非改判；17/27 两簇虽面变但判读结果未动。
- 一致率差 delta(ON−OFF)= +4.7pp（strict，主因即簇 15 出分母方式不同）；谱系差 0.05。

## 4. 归因四桶（全部 strict 分歧簇）
| 桶 | 簇 | 说明 |
|---|---|---|
| ①词表/面版本位移 | （0） | 判读面 flip 仅簇 15，已按"移向弃权"记 §3，无具名改判 |
| ②粒度墙 | 23 | 旧=Astro(high)，双臂 E2 一致具名 MG（宏观胶质同谱系）；E1=Astro。ON=OFF → **非本轮激活位移**，是判读证据面与旧签字的系统性粒度分歧（MG/Astro 区分，与簇 7 骑墙在册问题同族）→ 送 PI 复核 |
| ③判读方差 | （0） | — |
| ④意外漂移 | **0 簇** | **FAIL 档不触发**（判据：old high+非豁免+谱系认错大类=0） |
豁免组（单列不计头条，DRSC_REANN_DISAGREE_attrib.tsv 有票面 basis）：
- 簇 7（E-a）：双臂 MG——与旧 provisional MG 标签一致但骑墙在册，维持限定措辞；
- 簇 31（E-b）：E2 双臂具名 **Endo**（与旧标一致，marker 证据路径）vs E1 Micro（缺类伪影）——判读臂/引擎臂在此簇分道，正是参考缺类伪影的再次印证；
- Rod 质量轴 0/4/6/8/11（E-c）：簇 11 双臂具名 MG（旧=Rod，降解轴预期）；簇 4 双臂弃权；其余一致；
- E-d RPE 对豁免：本轮未触发（无簇具名 RPE）。

## 5. 送 PI 复核候选清单（不自动判错）
1. **簇 23**：旧 Astro(high) vs 判读双臂 MG —— 粒度墙，唯一具名偏移；
2. **簇 15**：旧 AC(high)；OFF 具名 RGC、ON 弃权（k9 面影响路径样本）；
3. **弃权簇 3/13/14/26**（非豁免组无共识，合法弃权）：簇 3=应激伪影簇（三席同判 HSPA1A/FOS/JUN 主导）、13/14=低基因数+无 kb 排名、26=1 席 Micro(B) + 2 席弃权（法定人数差 1 票）；
4. **簇 30（dissent 特判）**：三方全部具名 AC（E1=86.0%、E2 双臂、kNN 92.9% 在案）——dissent 定性是否解除属**人工签字权**，本测不代拍；
5. **簇 31**：判读臂 Endo 与旧标一致、引擎臂 Micro（缺类伪影）——引用时维持 SIGNOFF 注记。

## 6. 偏差与修复记录（全如实留痕）
- **DEV-1**：首轮 OFF 臂采集失效——mcp SDK `env=None`=干净默认环境（不继承父 env），EYEKB_ACT_K9=0 未传到 server，双臂 digest 逐字节全等（dd4f2b15…）。修复=wrapper 显式 `env=dict(os.environ)` + 双臂门探针（scripts/arm_probe.py：ON 可达 Melanocyte/OFF 不可达=PASS）后**双臂重跑**（新 OFF sha=2bb82dac…，ON 复现同值佐证确定性）。首轮 OFF 件保留于 out/digest_off.firstrun_ineffective_ENV_not_forwarded/。教训：evalset 历史采集器同用 env=None，其臂语义=默认 ON（无碍历史结论）。
- **DEV-2**：指令词表段"MG(Müller)/Micro(小胶质)"注记写法诱导 9 票回写带括注 → 归一器补"剥尾括注"规则（票面未重投，单测 9/9 扩覆盖）。
- **DEV-3**：评分器初版把"谱系一致细名不一致"（lineage_only）漏出分歧枚举 → 条件修正后簇 23 正确入②桶。三处均为评分/采集侧修复，**未重跑任何判读票**。

## 7. 交付件（MANIFEST 全 sha）
DRSC_REANN_PREREG.md(+sha) / out/cluster_roster.tsv / out/inputs.sha256 / out/markers_drsc.csv+sizes_drsc.csv /
out/digest_{on,off}/（EV_DIGEST+mcp_calls+tissue_composition_rows+collect_meta）/ out/face_{on,off}/EV_DIGEST_SLIM_*+freeze(json) /
out/ANN_{A,B,C}_drsc_reann_{on,off}.jsonl+META / out/E1_engine_table.tsv / CONSISTENCY_TABLE.tsv /
DRSC_REANN_DISAGREE_attrib.tsv / out/score_summary.json / DRSC_REANN_REPORT.md / MANIFEST.sha256
判读面泄盲核查：SLIM 结构断言 PASS（无真值词）；三席文件互不可见；本报告在票面锁定+机械评分后组装。
