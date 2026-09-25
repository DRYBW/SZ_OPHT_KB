# KB2b digest 静默缺陷修复全程（2026-09-24，双盲评测证据面重建实例）

## 时序与缺陷

1. KB2 首轮评测卡 t_854ba6e6 产出 EV_DIGEST_SLIM.jsonl（45 簇证据卡，冻结 sha 9e67eb50…），作为双盲判读员的唯一证据面。
2. 第二判读员（AGENT_ROLE，卡 t_0188c99f）验收输入时发现 **40/45 簇 top_genes 为空**（仅 Q9 五簇有值），拒绝在空证据上伪造"弃权"，发阻断报告——正确行为范本。
3. 根因（其取证定位到行）：`kb2_digest2.py` 的 `member_clusters()` 走 pandas 读 clustering TSV，`leiden` 列为 int64 → 选中簇号是 int；而组均值字典键经 `.astype(str)` 是 str。`if c not in gm: out[c]=[]` 恒真 → **静默返回空列表，无异常无日志**。日志尾"Q1..Q9 genes done / GENES PART DONE"全部正常——空值路径不在 FAIL 分支内。

## 修复循环（协调者按阻断报告第三节提案执行）

1. **旧件保版本**：`cluster_selection/genes_part/EV_DIGEST_SLIM/脚本` 四件复制为 `*_r1_defective.*`，sha256 追加进 `digest/ERRATA_SOURCE_FIX_SHA_LOG.txt`（勿原地静默覆盖）。
2. **最小补丁**：仅 2 处——`astype(str)` 统一 + 兜底 `c=str(c)` + 该分支加 WARN 日志（使同类缺陷不再无声）。照阻断报告提案原样执行，不自由发挥。
3. **环境探针（关键新步骤）**：第一次重跑选 pipeline_env（anndata 0.11.4）在 Q9 读取即死——新版 h5ad 的 `/uns/log1p` null 编码旧 anndata 无 reader。正确姿势：枚举各 conda env 的关键库版本（`python -c "import anndata; print(version)"`），对**每个数据源**做小成本 backed test-read 后再发射长跑。实测 scrnaseq/eyescgpt/r-env（anndata 0.13.2）全通。
4. **重跑后先验"冻结选择不变"**：修复不改 rng 消耗序 ⇒ 同题。逐成员把新旧 selection 转 str 后 list 比对，实测 9/9 IDENTICAL 才接受（考卷换了引擎不能换题）。
5. **验收线**（照阻断报告逐条）：genes_part 45/45 非空 ✓；selection 九成员键全 str ✓；SLIM 45/45 非空 ✓；kb_marker_ranking 重算（16/45 有命中，低命中本身是信息）✓；日志 0 WARN 0 FAIL ✓。
6. **新件 sha 落日志**，canonical 文件名不变（下游引用不换名），defective 旧件永久保留。
7. **重开判读槽位**：污染过的判读员不复用（其自曝读 clustering TSV 时暴露 2 个 barcode 真值 + 读过取证材料）——新开干净卡（t_7c1630fc），任务书带盲性红线清单 + 领地声明 + 落卡纪律。

## 盲性红线清单（干净判读卡任务书模板要素）

- 只许读：digest（指定 sha）+ 判读指令文件。
- 禁读：clustering/（含逐细胞真值列）、defs/、engine/、scoring/、结果报告、任何 ERRATA/取证件、另一判读员产物（ANN_A_*）、defective 旧件、项目 WIKI。
- 禁外部检索（首轮 lit 占位，两判读员同证据面）。
- undetermined 是合法输出，禁为填满硬注。
- 产出路径/行数/cluster_id 集合与 digest 逐一对应；协调者验收 = 计数+集合比对+schema 枚举+3 行抽查 why 对应证据。

## 人类 PI 判读槽位（槽位 A）

- 同证据面下"临床专家 vs AI"一致率比双 AI 互判更贴 KB 人机交互定位；PI 走 MSG_PLATFORM 分批判读包：每批=一个成员 5 簇（top 基因 + KB 命中 + KB 排名 + n_cells），大白话回"身份+等级 A/B/C+一句话依据"，协调者忠实转录 JSONL 不加工。
- 槽位文件名保持评分脚本兼容（kb2_bscore.py 硬编码 ANN_A_pi-chief.jsonl/ANN_B_second.jsonl），来源换人时文件名不动、README/任务书声明实际判读员身份。
- 发证据卡前须自查不泄露：不给 truth、不给引擎预测、不给另一判读员意见；KB 排名要注明"检索副产物非置信度"。

## 一句话教训

自动组装"给人/给模型判读的证据卡"的脚本，必须带**逐行非空断言**并作为冻结前置验收；静默空值 + 全正常日志 = 最危险的缺陷形态，判读员侧的输入验收（空值即阻断）是最后一道也是真实起效的一道防线。