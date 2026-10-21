# VERIFY_CONTRACT_G5G6 — 镜像仓门体系增补契约（G5 / G6；v1.0, 2026-10-12）

> 性质：**新增版本文件**。`docs/VERIFY_CONTRACT.md` **零字节改动**（sha256 `02eec500f215052c15884556054650c5ee84bbdd6079c405710152f7bb068694`，本卡开工前后同值）。
> 依据：`docs/W3_VERIFY_CONTRACT_AMENDMENT_PROPOSAL.md` P1（建议件）+ 用户指令 `USER_DIRECTIVE_20261012_x10_decisions.md` **D3**（PI 原话「可以」）+ 卡 `t_9dce4923`。
> 升格来源：项目侧两件验证器 `W3_NORM/R1/scripts/validate_registry.py` 与 `validate_change_control.py`（卡 t_59266f94）——从「文档里的验证器」变成「仓内可复跑的门」。
> 边界：本件**不新增审批权**、不改任何既有门判据、不追溯历史提交（只对新提交生效，生效日=采纳日）；工程 PASS ≠ 效能 PASS。

---

## 0. 与既有四门的关系（既有门零改动）

| 门 | 名称 | 判据（权威源） | 一键复算命令 | 期望输出 |
|---|---|---|---|---|
| G1 | 环境锁 | 依赖按 `requirements.repro.txt` 钉版；模型固定 `BAAI/bge-large-en-v1.5`（`docs/VERIFY_CONTRACT.md` §G1） | `pip install -r requirements.repro.txt` | 安装成功（无版本漂移） |
| G2 | 数据锁 | 只认 Release 预建语料资产，`sha256sum -c` 通过才允许解包（§G2） | 下载 → `cat` 拼接 → `sha256sum -c` | 逐行 `OK` |
| G3 | 检索验收 | 41 查询 top5 PMID 逐位一致（§G3；锚=`tests/REPRO_EXPECTED.json`） | `python3 tests/verify_repro.py --db-dir <corpus>` | `REPRO PASS: 41/41`，rc=0 |
| G4 | 字节锚 | 三件锚逐字节一致（§G4/§G4.1；解释器钉 `pipeline_env`，`EYEKB_CN_REWRITE=0` 为门前置） | `python3 tests/verify_pipeline.py` | `G4 PASS: 3/3 byte-identical`，rc=0 |
| **G5** | **注册表强制校验（新增）** | 本文件 §G5（输入面见下表） | `python3 tests/gate_registry.py` | `[g5] … verdict=PASS`，rc=0 |
| **G6** | **变更控制（新增）** | 本文件 §G6（人读判据源=`docs/W3_CHANGE_CONTROL_CHECKLIST.md` §五） | `python3 tests/gate_change_control.py` | `[g6] … verdict=PASS`，rc=0 |

**为什么需要 G5/G6**：既有四门全部作用于「跑出来的字节是否与锚一致」（齐性），对「这次改动本身是否被合法引入」不敏感——
一次合法的代码改动与一次静默的口径漂移在 G3/G4 上可能同样 PASS。G5/G6 补的是**变更合法性**这一层。

---

## G5：注册表强制校验门（`tests/gate_registry.py`）

### G5.0 输入面（四个；两个既有只读 + 两个新增）

| 面 | 路径 | 性质 |
|---|---|---|
| 归属台账 | `docs/W3_PIPELINE_REGISTRY.tsv` | **既有件**；本门不改其内容语义。2026-10-20 路径可移植修复（预注册 `PREREG_G5_PORTABILITY_20261020.md`）把仓内 20 行的 `path` 列由绝对路径改为仓内相对路径，其余列一字节未动；仓外 80 行保持绝对 |
| 仓内门清单 | `docs/GATE_INVENTORY_G5G6.tsv` | 本卡新增（G1–G6 六门，sha 逐门实取） |
| 台账快照漂移记账 | `tests/fixtures/g5/snapshot_drift_ledger.tsv` | 本卡新增（见 §G5.3） |
| 一键入口 | `tests/run_gates.sh` | 本卡新增（未登记加载的判定面） |

### G5.1 八项检查（每项 fail-closed；FAIL 时报检查码，禁只报「整体 FAIL」）

| 码 | 判据 | 对应负例类（R1 口径） |
|---|---|---|
| G5-C01 SCHEMA | 台账/门清单必填列齐备；必填格非空；台账 `surface` 列只允许 `repo` / `local` | — |
| G5-C02 ID-UNIQUE | 件 ID / 门 ID 唯一（台账 97 行 97 ID、门清单 6 行 6 ID） | — |
| G5-C03 OWNER | 台账「变更口」非空非占位；门清单 owner 须有问责锚（维护方/卡号） | — |
| G5-C04 REF-EXIST | 路径引用在盘上存在；跨面件 ID 引用可解析。按 `surface` 分两面立硬规则（见 §G5.1b）：`repo` 行必须是仓内相对路径且缺失即 FAIL；`local` 行必须是绝对路径且位于声明的维护方本地根之下，缺失计入 `local-unavailable`（信息项，因任何 clone 都不可能含它）。detail 行显示 `surface repo=N/local=M` | **缺件** |
| G5-C05 SHA-MATCH | 现取 sha == 登记 sha（漂移行须被记账豁免）。`.git/**` 属版本控制元数据，不参与内容比对（detail 报 `vcs-metadata-skipped=N`）：其字节取决于检出方式（分支/detached），任何 clone 者都无法复现 | **摘要漂移** |
| G5-C06 LEDGER | 记账诚实：条目须对应真实行、须确实处于漂移态（过期免检条 = FAIL，防白名单化） | （本卡新增） |
| G5-C07 UNREG-LOAD | `tests/run_gates.sh` 调用的每个门脚本都须已登记且 sha 相符 | **未登记加载** |
| G5-C08 CERT-EXPIRY | 台账/清单中声明的「到期日」不得早于 `--as-of` | **过期认证** |

退出码：`0`=全 PASS；`2`=任一 FAIL（fail-closed）。默认 `--as-of 2026-10-12`。

### G5.1b 路径面（2026-10-20，预注册 `PREREG_G5_PORTABILITY_20261020.md`）

旧版 `gate_registry.py` 三处直接 `Path(row["path"])`，C07 两侧键一为台账原样字符串、一为 `(ROOT/rel).resolve()`；维护方机器上 `ROOT` 恰等于台账写死的 `/home/ubuntu/EYEKB_REPO`，两键巧合相等，故长期绿灯。换到任何其他目录（`/tmp` 另位 clone 实测）C07 恒报 4 项「registered on neither surface」，而这 4 个脚本其实都登记着。

现规则：

- `resolve_path(p)`：相对路径锚 `ROOT`；绝对路径原样。
- `is_maintainer_local(p)`：绝对路径且位于 `MAINTAINER_LOCAL_ROOTS` 之下 → 维护方本地证据。
- C04/C05/C06 全部走 `resolve_path`；C07 两侧键均经 `resolve_path(...).resolve()` 归一。
- 仓内行改为相对路径后，clone 到任何位置读数一致；仓外 80 行仍为绝对路径，缺失时显式计入 `local-unavailable` 并在 detail 行显示数字，不静默通过，也不当作缺件。

**严格性不变的证据**：负例电池 `tests/gate_g5g6_negative.py` N1（台账行指向 `/tmp/NO_SUCH_GATE_FILE_G5.py`）仍须触发 `G5-C04`；N7（`repo` 面行登记成**存在的**绝对路径——旧规则必然放过）也必须触发 `G5-C04`；电池 17/17 全符。

### G5.1c 台账双面（`surface` 列，2026-10-20，预注册 `PREREG_G5_Q1Q2_20261020.md`）

台账 100 行分成两面，机器强制，不再靠路径形式隐式推断：

| `surface` | path 形式 | 缺失时 | sha |
|---|---|---|---|
| `repo`（20 行） | 必须仓内相对路径，绝对路径即 FAIL | 缺件 FAIL | 逐字节比对 |
| `local`（80 行） | 必须绝对路径且位于 `MAINTAINER_LOCAL_ROOTS` 之下 | `local-unavailable`（计数，不 FAIL） | 存在则比对 |

这条把 2026-10-20 那个缺陷反向锁死：以后谁再把仓内文件登记成绝对路径，C04 立刻 FAIL，不会再出现「碰巧前缀相同所以绿灯」。

**`.git/**` 不入内容面**：`L6-08` 登记 `.git/HEAD`，其字节取决于检出方式（`ref: refs/heads/main` vs detached 的裸提交号）。CI 常用的 detached 检出下旧门必挂一次 C05；现按 VCS 元数据处理，不参与内容比对，detail 报 `vcs-metadata-skipped=1`。C04 存在性检查不变。故意把一条仓外行指向不存在的 `/mnt/D/EyeKB/...` → `local-unavailable=1` 且 PASS；把一条仓内相对行指向不存在的仓内文件 → `missing paths=1` 且 FAIL。

### G5.2 实测（本轮现取，完整日志 `logs/g5_standalone.log`）

```bash
cd /home/ubuntu/EYEKB_REPO && python3 tests/gate_registry.py
```
```text
[g5] entry-invoked gate scripts: 4 -> tests/gate_change_control.py, tests/gate_registry.py, tests/verify_pipeline.py, tests/verify_repro.py
[g5] rows=97 gates=6 dispensed=4 checks=8 fail=0 verdict=PASS
  PASS G5-C01 SCHEMA :: missing_columns=none; empty_required_cells=0
  PASS G5-C02 ID-UNIQUE :: ledger 97 rows/97 ids; inventory 6 rows/6 ids
  PASS G5-C03 OWNER :: empty/placeholder owners: 0（台账内短简写 16 行按「非空」放行，口径属台账本方）
  PASS G5-C04 REF-EXIST :: missing paths=0; dangling id refs=0
  PASS G5-C05 SHA-MATCH :: live-vs-registered mismatches=0; dispensed-by-ledger=4
  PASS G5-C06 LEDGER :: ledger entries=4; problems=0; stale dispensations=0
  PASS G5-C07 UNREG-LOAD :: unregistered/mismatched gate scripts invoked by the entry: 0
  PASS G5-C08 CERT-EXPIRY :: as_of=2026-10-12; expired declared certifications=0
```
（`rc=0`。JSON 输出：`--json <path>`，含逐检查 offenders；本卡逐用例见 `G5G6_RESULTS.json`。）

### G5.3 那 4 行 `dispensed` 是什么（不许被读成「门放水」）

台账是**快照语义**（构建时刻的 sha，见 `docs/W3_CHANGE_CONTROL_CHECKLIST.md` §四 F6）：快照之后被写入的件，
其行内 sha 必然与现取不等，且台账**字节不可由本卡改**（改动权属台账本方卡）。处理方式沿用 F6 原文：
「按新快照重取 + 记一条版本注记」——即 `snapshot_drift_ledger.tsv` 逐行记下 `registered→observed` 与现取时刻。
**该记账不是白名单**：
1. 只登记「确实已漂移」的行（未漂移而记账 = `stale dispensation` ⇒ G5-C06 FAIL）；
2. 记账行必须与**现取 sha 逐字节相等**，否则 G5-C05 FAIL（＝门逼你重新现取）；
3. 未记账的漂移一律 FAIL（负例 N2 即此形态）。

本轮 4 行：`L1-21 / L1-22 / L5-13`（并发写作窗口：W2/W1 卡在其台账登记窗口内又写了件）+ `L6-13`（快照后写入，cause=`ACTIVE_CONCURRENT_WRITE`）。

**门确实在工作的一次现场实录**：本轮复算期间 `L6-13`（`plans/evalset/C_ARM_PRIMAR_YLINE_FREEZE_v1.0.md`，另一张卡在编辑）
又被写入一次，G5 当场报 `G5-C05 FAIL` 并打印 `ledger stale: re-probe` 指令；重取快照（S1）后即恢复 PASS。
这不是门坏了，而是门按设计把「台账快照过期」这件事变成了一次必须处理的显式事件。

### G5.4 四类负例必须被拒（对齐 R1 口径；实测见 `G5G6_RESULTS.json`）

`tests/gate_g5g6_negative.py` 对**真件的最小突变副本**逐一跑门，断言 `rc≠0` 且命中目标检查码：

| 用例 | 突变 | 目标码 |
|---|---|---|
| P0 | 正控：未突变副本 | （须 rc=0） |
| N1 | 台账 L6-04 路径 → 不存在路径 | `G5-C04` |
| N2 | 台账 L6-04 sha256 → 全 0 | `G5-C05` |
| N3 | 入口新增一行调用未登记脚本 | `G5-C07` |
| N4 | 台账 L1-22 声明到期日 → 早于 as_of | `G5-C08` |
| N5 | 记账行改指「未漂移」件 | `G5-C06` |
| N6 | 台账 L0-06 变更口 → `TBD` | `G5-C03` |
| N7 | `repo` 面行登记成**存在的**绝对路径（旧规则会放过，见 §G5.1b） | `G5-C04` |

---

## G6：变更控制门（`tests/gate_change_control.py`）

### G6.0 输入面

| 面 | 路径 | 性质 |
|---|---|---|
| 变更实例 | `docs/CHANGE_CONTROL_G6_INSTANCE.tsv` | 本卡新增（本卡自身变更 = 自量，SPEC §4） |
| 模板 | `docs/CHANGE_CONTROL_G6_TEMPLATE.tsv` | 本卡新增（**模板示例行也必须过门**，否则「复制模板→直接失败」会被绕过） |
| 人读清单 | `docs/W3_CHANGE_CONTROL_CHECKLIST.md` | **既有件，只读**（§五 14 行判据表 = 规则↔清单映射面） |

### G6.1 八条机器规则（五问 Q1–Q5 / 三件 M1–M3 / 四证 E1–E4 为必填）

| 规则 | 内容 | 缺项后果 |
|---|---|---|
| R1 REQUIRED | 12 个内容格 + 3 个身份格非空；内容格各带 `*_evidence` | rc=2 |
| R2 EVIDENCE | 每格证据须含可核验锚（存在路径 / `文件:行:子串` / 64 位 sha / `*.sha256` / `rc=n` / 卡号） | rc=2（只写结论 = FAIL） |
| R2-CONCRETE | **引用具体阈值与动作**：M3（回归门）/E1（sha 实证）/E2（回退恒等）必须给出可执行命令或期望读数，禁「跑了，通过」 | rc=2 |
| R3 NA | 不适用须写 `NA-<规则号>` + ≥20 字理由且理由含一个存在的路径 | rc=2 |
| R4 OUTCOME1 | Q1 须含责任域层号 `L0–L6`（首因层判定） | rc=2 |
| R5 MONOTONE | Q3 须含回退/负向项（`loss|回退|负向|不单调|退步`）——禁只报增益 | rc=2 |
| R6 PREREG | Q4 须含 sha 锚（判据件开封前冻结） | rc=2 |
| R7 ESCAPE | Q5 须含开关名 `EYEKB_*` + OFF 逐字节/恒等实证说明 | rc=2 |
| R8 PRECOND | 涉及**默认 ON** 行为变更时，须登记为门的前置条件（`docs/VERIFY_CONTRACT.md` 门段） | rc=2（否则门会假 FAIL） |
| R2-PORTABLE | 路径锚按可解析规则分类计数（见 §G6.5）；**无一规则可解析**的锚单独报，不并入 R2 的「证据缺失」 | rc=2（仅对「本机与本仓都解析不到」那一类） |
| G6-MAP（结构性前置） | 人读清单 §五 14 行判据必须被「规则↔清单」映射 14/14 覆盖，无悬空行号 | rc=2 |

退出码：`0`=全 PASS；`2`=任一 FAIL。

### G6.5 锚点可解析规则（2026-10-21 追加；外部评审的可移植性整改）

一份在作者机上绿的锚表，换一台机器读会报出「证据缺失」——但缺的是**路径**，不是证据。改法是把
「本机解析不到」与「证据不在仓里」分成两条读数：

| 规则 | 何时命中 | 是否算「可核验锚」 |
|---|---|---|
| `exact` | 绝对路径原样存在 | 是 |
| `repo-relative` | 相对路径在本检出内存在 | 是 |
| `relocated` | 绝对路径不存在，但其**最长尾部**在本检出内可解析（锚记的是「别人机器上这份仓」的位置） | 是（报告里写明替换成了哪个尾部） |
| `declared-not-distributed` | 路径被本仓自己的 `.gitignore` 排除（运行期读数、本地数据）——声明就在随仓分发的 `.gitignore` 里，不是维护者私有清单 | 是（声明为「从不随仓分发」） |
| `declared-local` | 路径在声明的本地证据根下（与本仓 G5 同一份声明 `LOCAL_EVIDENCE_PREFIXES`） | 是（工作证据，不随仓分发） |
| `unresolved` | 以上都不命中 | **否**：由 R2-PORTABLE 单独报（rc=2），且与 R2 的「证据缺失」分开计 |

R2 本体（证据缺失）语义不变：证据格没有任何锚、或相对路径指向的仓内文件不存在 → FAIL。分类计数同时写进
`--json` 的 `portability` 段（逐规则计数 + 样本），使「任何克隆都解析不到」始终是一个可读数字，而不是一条
不成文的豁免。

### G6.2 实测（本轮现取，完整日志 `logs/g6_standalone.log`）

```bash
cd /home/ubuntu/EYEKB_REPO && python3 tests/gate_change_control.py
```
```text
[g6] changes=2 checks=19 fail=0 verdict=PASS (instance:PASS; template:PASS)
  PASS G6-R1 REQUIRED :: [instance] empty required cells: 0
  PASS G6-R2 EVIDENCE :: [instance] evidence cells without a resolvable anchor: 0
  PASS G6-R3 NA :: [instance] rule-numbered NA defects: 0
  PASS G6-R4 OUTCOME1 :: [instance] Q1 layer-id defects: 0
  PASS G6-R5 MONOTONE :: [instance] Q3 rollback-term defects: 0
  PASS G6-R6 PREREG :: [instance] Q4 sha-anchor defects: 0
  PASS G6-R7 ESCAPE :: [instance] Q5 escape-door defects: 0
  PASS G6-R8 PRECOND :: [instance] gate-precondition defects: 0
  PASS G6-R2-CONCRETE :: [instance] concrete-action cells without a command/threshold: 0
  …（template 同 9 项，全 PASS）…
  PASS G6-MAP :: checklist rows=14; covered=14; problems=0
```
（`rc=0`。）

### G6.3 负例（判别性；实测见 `G5G6_RESULTS.json`）

| 用例 | 突变 | 目标码 |
|---|---|---|
| P0 | 正控：未突变副本 | （须 rc=0） |
| N1 | E4 置空 | `G6-R1` |
| N2 | Q2 证据改「见报告」 | `G6-R2` |
| N3 | Q3 删除回退词 | `G6-R5` |
| N4 | Q4/Q4 证据去 sha | `G6-R6` |
| N5 | Q5 去开关名 | `G6-R7` |
| N6 | M3 声明默认 ON 未登记门前置 | `G6-R8` |
| N7 | M3 只写「跑了，通过」 | `G6-R2-CONCRETE` |
| N8 | 人读清单 §五 删第 14 行 | `G6-MAP` |

---

## 一键入口（C 节）

```bash
bash tests/run_gates.sh          # 依次 G3 → G4 → G5 → G6，末尾汇总；非零 rc = 链上有门未过
```
环境变量：`EYEKB_CORPUS`（G3 语料目录，默认 `$REPO/literature_db/v2.4.2_2026-09_slim`）、
`EYEKB_G3_PY`（G3 解释器，可选，给定时其所在目录前置到 PATH——G1 锁装的依赖可能在某个 conda/venv 里）、
`EYEKB_GATE_OUT`（读数落盘目录，默认 `$REPO/.gate_out`，运行时产物不进 git 树）。
本脚本不判 PASS/FAIL，只如实汇总各门 rc；判定在各门内部。

### 实测输出样例（2026-10-12 现取，完整日志 `logs/run_gates_sample.log`）

```text
[gates] repo=/home/ubuntu/EYEKB_REPO
[gates] corpus=/home/ubuntu/RAG_SLIM_V242/literature_db/v2.4.2_2026-09_slim
=================== G3 verify_repro (41-query retrieval anchor) ===================
REPRO PASS: 41/41 cases with position-by-position identical top5
------------------- G3 verify_repro (41-query retrieval anchor) rc=0 -------------------
=================== G4 verify_pipeline (three byte anchors) ===================
[g4] interpreter: /home/ubuntu/.conda/envs/pipeline_env/bin/python (python 3.10, source: contract default)
PASS stage_a/processed.h5ad
PASS decisions_template.csv
FAIL annotation_evidence_report.md__normalized
   got:      74a2a3b33126ba79e03f153a10578b8d86c8b012b40e02eecbfdffa4e6336dab
   expected: 2f6087ae33be7363339322675a1eafa410cb9a8e21e217de9cab993353023a14
G4 FAIL: 1/3 mismatch
------------------- G4 verify_pipeline (three byte anchors) rc=1 -------------------
=================== G5 gate_registry (registry surface enforced) ===================
[g5] rows=97 gates=6 dispensed=4 checks=8 fail=0 verdict=PASS
------------------- G5 gate_registry (registry surface enforced) rc=0 -------------------
=================== G6 gate_change_control (eight machine rules) ===================
[g6] changes=2 checks=19 fail=0 verdict=PASS (instance:PASS; template:PASS)
------------------- G6 gate_change_control (eight machine rules) rc=0 -------------------
=================== summary ===================
  G3 verify_repro (41-query retrieval anchor)          rc=0
  G4 verify_pipeline (three byte anchors)              rc=1
  G5 gate_registry (registry surface enforced)         rc=0
  G6 gate_change_control (eight machine rules)         rc=0
  ------------------------------------------------------------
  gates=4 failed=1  (CHAIN FAIL)
```

**如实说明**：本轮 G4 的 `annotation_evidence_report.md` 锚未命中（rc=1），另两锚与三跑一致性均 PASS。
差异只有一处 token：pitfalls 消费段的模型名 `astra` → `6.1sol`（`pipeline/pitfalls/consume.py:163`，属**他卡工作树**的未提交改名）。
本卡对该漂移**零因果影响**（运行期审计钩子证明：装钩子跑同一条 G4 命令时，仓内 `tests/`、`docs/` 下的打开事件仅
`tests/verify_pipeline.py` 与 `tests/G4_EXPECTED.json`，本卡新增件**零命中**），且本卡**未改任何判据/锚/期望值**。
完整取证见 `GATE_NONREGRESSION.json`（含 `G4_drift_attribution`）。re-anchor 归该 rename wave 的 closeout（另卡跟进）。

---

## D 节：登记与后续纪律

- 新门已登记进仓内门清单：`docs/GATE_INVENTORY_G5G6.tsv`（机器版）+ `docs/GATE_INVENTORY_G5G6.md`（人读版），
  与既有三锁 G1/G2/G3 并列，**sha 逐门实取（禁凭记忆）**，由 `scripts/gen_g5g6_assets.py` 同源生成。
- **后续任何仓改动必须保持六门可复跑**（与 `docs/VERIFY_CONTRACT.md` §5 变更纪律同源）；
  门的判据/期望值变更 = 维护方 evidence-bearing 行为（版本号 + 日期 + 复跑实证），克隆方无编辑权。
- `docs/W3_PIPELINE_REGISTRY.tsv` 的并入/更新、`docs/VERSION_NOTES.md` 版本注记、`git commit/push`
  均属**保留门**（本卡不执行，须另行呈报）。
- 本契约只对新提交生效，**不追溯历史提交**（与 `W3_VERIFY_CONTRACT_AMENDMENT_PROPOSAL` P1 同纪律）。

## 附：本卡产出复算入口

```bash
python3 /mnt/D/EyeKB/plans/repo_gates_20261012/run_chain.py      # S1–S6 全链复算（零网络/零 GPU）
python3 /mnt/D/EyeKB/plans/repo_gates_20261012/scripts/gen_manifest.py   # 清单是最后一步（重跑 run_chain 后须重跑）
sha256sum -c /mnt/D/EyeKB/plans/repo_gates_20261012/MANIFEST.sha256       # 逐件校验（111 件）
```

## E 节：本卡明确不做的事（边界）

- **不改**任何既有仓件字节：`docs/VERIFY_CONTRACT.md`、`docs/W3_*.md|tsv`（台账/人读清单/首因规则）、`tests/verify_repro.py`、
  `tests/verify_pipeline.py`、`tests/REPRO_EXPECTED.json`、`tests/G4_EXPECTED.json`、`requirements.repro.txt`、`README.md`、
  `docs/VERSION_NOTES.md`——本卡只**新增**文件（实证：本卡开工后仓内被写入的文件全部落在新增清单内）。
- **不**改 G1–G4 的判据、期望值、锚；**不**给既有门加白名单（若新门撞哨兵词表则改新门文件名——本轮无冲突）。
- **不**执行 `git commit` / `push`（保留门，须另行呈报）；**不**宣布任何效能结论（工程 PASS ≠ 效能 PASS）。
- 零下载 / 零网络 / 零 GPU；纯 stdlib（不引入新依赖）；数字一律盘上现取。