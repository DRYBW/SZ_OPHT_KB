# VERIFY_CONTRACT_AMENDMENT_PROPOSAL — 镜像仓复现门体系增补建议件（v1.0, 2026-10-12）

> 对接对象：`/home/ubuntu/EYEKB_REPO/docs/VERIFY_CONTRACT.md`（9,776 B, sha256 `02eec500f215052c15884556054650c5ee84bbdd6079c405710152f7bb068694`）
> 性质：**建议件，不改仓冻结契约的任何一个字节**。采纳与否由维护方按该契约 §5「变更纪律」走
> （更新锚/依赖锁 = 维护方 evidence-bearing 行为；克隆方无编辑权）。
> 依据：`USER_DIRECTIVE_20261012_upstream_first_normalization.md` §二/§四（"与镜像仓既有 VERIFY_CONTRACT 对接：
> 新变更门纳入仓的复现门体系"）。同目录配套件：`PIPELINE_REGISTRY.tsv`、`CHANGE_CONTROL_CHECKLIST.md`、`UPSTREAM_FIRST_RULE.md`。

---

## 0. 现状（盘上实测，2026-10-12）

| 项 | 实测值 |
|---|---|
| 契约本体 | `docs/VERIFY_CONTRACT.md` 9,776 B，sha256 `02eec500…8694` |
| 现行门 | G1 环境锁 / G2 数据锁（唯一官方语料通道）/ G3 检索验收（41 查询 top5 逐字节）/ G4 字节锚（三件锚 + G4.1 解释器钉死）+ §4 三层 triage + §5 变更纪律 |
| 门前置条件（已成文） | `EYEKB_CN_REWRITE=0`（默认 ON 的改写层会改变归一化报告体 → 配置性假 FAIL） |
| 解释器钉死 | `/home/ubuntu/.conda/envs/pipeline_env/bin/python`（G4.1）；覆盖钩子 `EYEKB_G4_PY=`，非默认时打印 `[g4] note:` |
| 现行锚 | `tests/G4_EXPECTED.json`（1,560 B, sha256 `4250d575…f668`）+ 三份历史锚（PRE-ENGMIG / PRE-KB9B / PRE-X4BFIX）并存 |
| 仓态 | HEAD `b92fbfed05d8f686ded9cf01e20a7ba0e7122d45`（本地 commit，不 push） |

**观察**：现行四门全部作用于「**跑出来的字节是否与锚一致**」（齐性），没有一门作用于
「**这次改动本身是否被合法地引入**」（变更合法性）。本建议件即补这一层。

---

## 1. 建议增补（5 条，逐条给出动机 / 盘上证据 / 落点 / 机械判据）

### P1 新增 G5「变更门」：改动必须自带影响面清单与逃生门登记
- **动机**：齐性门（G1-G4）对「改了什么、会影响谁」是不敏感的——一次合法的代码改动与一次静默的口径漂移在 G3/G4 上可能同样 PASS。
- **盘上证据**：本项目 2026-10-12 已实证「补词表」这类上游增量会造成**负面**读数（`plans/x10_improve_20261012/X10D/REACH_DIFF_X9A_X9B.tsv`：Astrocyte top3 `0.8399→0.0`，`loss_cells_top3=1652`），而这种回退在 G1-G4 下**完全不可见**。
- **落点建议**：`docs/VERIFY_CONTRACT.md` 新增 **G5** 段（与 G1-G4 并列，不改其字节），内容 = `CHANGE_CONTROL_CHECKLIST.md` 的机械可查子集：
  1. 变更附**影响面清单**（逐文件/逐维度，含不动项与不单调性条目）；
  2. 变更附**逃生门**（开关名 + 入册 + OFF 态逐字节回旧行为的实证）；
  3. 变更附**现行指针**（见 P3）。
- **机械判据**：仓内新增 `tests/verify_change_gate.py`（建议名，避免哨兵词，见 §2 坑一）：
  - 输入 = 被改文件列表 + 变更单路径 → 检查影响面清单条目数 ≥ 被改文件数、每条含「臂/读数/预期方向」、逃生门段非空；
  - 输出 `rc=0` 且打印 `[g5] files=<n> impacts=<n> escape=<name>`，任一不齐 `rc=2`。
- **风险**：会要求历史提交补件。建议 G5 **只对新提交生效**（生效日=采纳日），历史不追溯（避免与 §5 冲突）。

### P2 G4 段增补：门锚变更须与「归属台账」同 commit 更新
- **动机**：G4 已有 §5「引擎版本变→README 版本注记与契约同 commit 更新」；但**归属登记件**（哪一件归哪层、变更口是谁）不在同一条款内，导致「改了锚但台账没更新」的漂移不可检。
- **盘上证据**：本项目归属表 `plans/x10_improve_20261012/W3_NORM/PIPELINE_REGISTRY.tsv`（97 件登记行，快照时刻在 `REGISTRY_BUILD_REPORT.json`）与仓内锚件之间**目前无任何机械绑定**。
- **落点建议**：G4 段追加一句：变更 `tests/G4_EXPECTED.json` / `requirements.repro.txt` / 引擎代码版本号时，须同 commit 更新仓侧归属登记件（建议路径 `docs/PIPELINE_REGISTRY.tsv`，见 P5 交付面）。
- **机械判据**：`git diff --name-only HEAD~1` 中若出现锚/锁/引擎文件，则须同时出现登记件（否则 G5 `rc=2`）。

### P3 新增「多版本冻结清单现行指针」条款（对应 `CHANGE_CONTROL_CHECKLIST.md` §四 F1）
- **动机**：多版本冻结清单并存时，旧清单的 `sha256sum -c` 必然 FAIL，而 FAIL 无法区分「磁盘损坏」与「已被新版本取代」——验收方会误判为事故。
- **盘上证据（今日实测）**：
  - `plans/x9_fresh_20261012/s1_adult/gold/FREEZE_GOLD_X9A.sha256`（v1，516 B）与 `FREEZE_GOLD_X9A_v11.sha256`（v11，81 B）并存；
  - `sha256sum -c FREEZE_GOLD_X9A.sha256` → 5 件 OK、`x9a_input.h5ad` **FAILED**（v1 记 `f50d93165ff7…`，盘上 v11 值 = `e1c19466f704…`）；
  - 该清单**自身无任何 superseded/现行指针标注**。
- **落点建议**：契约增加一条一般纪律：凡 `*FREEZE*.sha256` 多版本共存，必须存在显式**现行指针**（清单头注记一行 / 同名 `*.POINTER` 文件），指针须指明「现行版本 + 生效日期 + 被取代项清单」。
- **机械判据**：扫描同一目录下匹配 `*FREEZE*.sha256` 的文件数 >1 时，须能找到指针件；找不到 → `rc=2`。

### P4 交付面把「默认 ON 的行为变更」登记为门的前置条件（把既有先例制度化）
- **动机**：`EYEKB_CN_REWRITE` 于 2026-10-05 默认翻转为 ON，导致 G4 在未显式关断时产生**配置性假 FAIL**——该事项目前只写在 G4 段落的一句里，未形成通用规则。
- **盘上证据**：`docs/VERIFY_CONTRACT.md` G4「Rewrite-layer precondition (2026-10-05, mandatory)」段；`mcp_server/rewrite_cn.py:165` 读 env、`:75` 说明「unset → ON」；`pipeline/README.md` 与 `run_pipeline.py` 亦受此层影响。
- **落点建议**：契约新增小节「门的前置条件表」：任何**默认 ON** 且会改变门比对对象（报告体/锚字节）的行为层，必须在表中登记：开关名 / 默认态 / 门的**规定取值** / 违反时的现象（假 FAIL 而非真 FAIL）。
- **机械判据**：`tests/verify_pipeline.py` 运行时若检测到未按规定取值的前置开关，打印 `[g4] precondition: <name>=<actual> (required <value>)` 并可选择 `rc=2`（**建议先 warning-only，一版后再升 fail-closed**，避免误伤）。

### P5 真值红线静态检查项（对应 DIRECTIVE §二8；本项目教材案 4）
- **动机**：从**被评测卷的真值文件**现取闭集/映射/词表 = 循环性与不可比，且违反真值红线；此类缺陷在下游提示词层**无法修复**。
- **盘上证据**：`plans/x9_fresh_20261012/s1_adult/scripts/judge_x9a_arms.py` 第 27 行
  `LABELS = [r["truth"] for r in csv.DictReader(open(GOLD_FINE), delimiter="\t")]` + 紧接 `assert len(LABELS) == 26`；
  该件 docstring 自述「闭集=本卷 gold fine 类（26 类）+ unknown」。
- **落点建议**：新增静态检查项（建议并入 S0 防火墙 T 系列或 G5 的子检查）：判读/生成脚本不得在运行时从**评测卷 gold 文件**构造合法输出集；合法输出集必须为其自身的冻结件（本项目修复形态 = `C1_IMPL/M1_CONTRACT/legal_output_sets_X10C.tsv`）。
- **机械判据**：正则扫描判读/评分类脚本中对 gold/真值文件的读取是否**仅用于计分**（而非构造 `LABELS`/闭集/映射）；命中构造用途 → 报 `rc=2` 并列出 `file:line`。
- ⚠ **扫描器自匹配坑**（本项目已实证）：扫描器的模式字面与描述性文案会自命中。请把扫描器自身文件加入排除列表，且**模式只写形态不写词**（详见 §2 坑二）。

---

## 2. 实施路径（含两个本项目已踩过的坑）

### 坑一：S0 防火墙 T4 哨兵词的 substring 误报
- 实证：`EYEKB_REPO` commit `8cd0ce8`——模块名 `kb9_consume_guard` 因含 `consume` 触发 S0 T4 防火墙的哨兵子串检查**误报**，被迫改名为 `kb9_slot_guard`（守卫体本身零 pitfall 引用，防火墙未被削弱）。
- 要求：新门脚本的**文件名、变量名、docstring** 均须避开 S0 防火墙的哨兵词表；命名先跑一次 S0 自检。

### 坑二：门脚本的静态扫描会自匹配
- 实证（本项目 2026-10-12 X11-D 卡）：5 项门禁检查中有 2 项因**扫描器自身的模式字面**与**描述性文案**命中而假 FAIL。
- 要求：①排除扫描器自身文件；②模式写**形态**（如 `(?:^|[\s;&|(])(?:curl|wget|aria2c)\s+-\S`）而非**词**（如 `"curl "`）；③优先用**运行期证据**（如 `sys.addaudithook` 审计网络事件）替代文本 grep。

### 采纳流程（建议）
1. 维护方按 §5 变更纪律，先出**三跑一致**实证（新门脚本对现行仓状态 PASS/FAIL 稳定）；
2. 契约与 README 版本注记、归属登记件**同 commit** 更新（即 P2 条款的首个执行样例）；
3. 版本号 + 日期进 `docs/VERSION_NOTES.md`；
4. 旧契约版本原样保留（append-only 修订或另存 `VERIFY_CONTRACT_v<N>.md`），旧锚不删。

---

## 3. 明确不做的事（边界）

- **不改** `docs/VERIFY_CONTRACT.md` 现行字节（sha `02eec500…8694` 保持有效）；
- **不改** 任何门锚（`tests/G4_EXPECTED.json` `4250d575…f668`、`tests/REPRO_EXPECTED.json`）与依赖锁（`requirements.repro.txt` `8c0af43f…8f43`）；
- **不新增门禁执行**：本件只是建议书，零脚本落地、零门跑；
- **不涉及下载**、**不涉及确认性评测**；
- 与 PI 保留门的关系：任何资产激活仍属 PI 保留门，本件不代行批准。

---

## 4. 附：与 W3 三件的关系

| W3 件 | 与仓门的接口 |
|---|---|
| `PIPELINE_REGISTRY.tsv` | 归属表本体；L6 段已把 `VERIFY_CONTRACT.md`/`G4_EXPECTED.json`/`verify_*.py`/`requirements.repro.txt`/README/HEAD 逐件登记（变更口=维护方、冻结门=G1-G4、回归门=G3/G4） |
| `CHANGE_CONTROL_CHECKLIST.md` | G5 的判据来源（机械子集 = §五 13 项判据表） |
| `UPSTREAM_FIRST_RULE.md` | G5 的第 0 步（首因层判定）来源；教材案 4 直接对应 P5 |