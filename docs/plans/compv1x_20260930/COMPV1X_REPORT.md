# COMPV1X_REPORT — 细胞悬液参照层补装（OB-3 闭环尝试·终版）

> 卡 t_93eb78a8 | 2026-09-30 | 规则=PHASE0_INVENTORY_COMPV1X v1.0 FINAL（门先立后算）
> 外部裁定=gpt-6-astra xhigh（logs/ASTRA_REPLY_v1.md，D1/D2 ACCEPT + D3/D4/D5 MODIFY + 5 项新缺陷全吸收）

## 结论（先给）

**OB-3 终判：NOT_READY（预注册 R1A+LOSO 逐集口径，五集未全 ≤2/10）——但平台轴根因修复已被量化证明：**

| 集 | 原路由 R1A（COMPV1） | 本卡主口径 R1A | Δ | 判定 |
|---|---|---|---|---|
| Q1_Lukowski2019 (cell) | 4/10 = 40% | **2/10 = 20%** | -2 旗 | **PASS（达线）** |
| Q2_GSE155288 (cell) | 6/10 = 60% | **3/10 = 30%** | -3 旗 | TRIGGER |
| Q3_GSE137537 (cell/plate) | 5/10 = 50% | **2/10 = 20%** | -3 旗 | **PASS（达线）** |
| Q4_GSE148077 (cell+分选) | 4/10 = 40% | 4/10 = 40%（RC4 旧路由保持，astra D3） | 0 | TRIGGER（本卡不可解，缺口在册） |
| Q5b_GSE226108 (nucleus) | 4/10 = 40% | 4/10 = 40%（路由不变） | 0 | TRIGGER（与悬液层无关） |

- 合计描述性 = 15/50 = 30.0%（逐集判定不因合计改变，astra D5 条款）。
- 计算纪律：复现门先行且 5/5 PASS（R0={4,4,3,2,0}、R1A={4,6,5,4,4}、R1B={3,4,3,1,1} 逐字复算 COMPV1 冻结数），本卡全部增量严格归因于新层路由。

## 本卡交付物

1. **旁挂参照面**：kb/composition/EXPECTED_COMPOSITION_v1_cell_suspension_v1.{json,md}
   （status=not_activated、wiring=OFF；含 pooled13 暂定全量面 + 3 个 LOSO 判定折面 + RC6 描述面 +
   每行来源/PMID/悬液裁决声明 + 语义声明全集 + 覆盖缺口清单；sha 台账 ledgers/SHA_SIDECAR_ledger.txt）。
2. **RC5 未分选细胞悬液层**（13 供者×区域单元 = Lukowski 3 + GSE155288 4 + GSE137537 6；
   全部作者逐细胞注释 + 冻结映射；零自家共识；零下载；adult-only 字段实测核验）。
3. **复算全表**：ledgers/compv1x_flag_rows.tsv（主判据 + R1B/E7 成对/Q3 供者合并/pooled13/留一研究诊断
   全敏感性矩阵）、compv1x_xtab_primary.tsv（逐行归因）、compv1x_boundary_moves.tsv（十类边界移动）、
   compv1x_fold_walkthrough.tsv（每折研究/供者/单元数与支撑门走查）。
4. **Q2 悬液身份裁决**（astra 缺陷1 闭合）：细胞悬液——PMID 34341398 一手摘要"single-cell RNA
   sequencing ~93,000 cells" + GEO Series 明文；本室 E7 注记页眉"snRNA-seq"为措辞误差，登记勘误
   （原文件不动）。同时修正两处既有误记：GSE155288 实为 2 donor × {M,P} = 4 单元（非"每供者单区域"）。
5. **Q4 策略取证**（新增发现）：cellId 前缀实测 + PMID 32555229 一手方法 = Q4 是**混合操作设计**
   （12 个中央凹未分选样本 55,736 细胞 + 外周 CD73 耗杆/CD90 富 RGC 分选样本 29,246 细胞，仅 H1/H3
   含分选）。预注册后不改规则（计分保持 RC4 旧路由），拆分路径已登记为后续选项。
   取证件：ledgers/q4_sample_strategy_forensics.tsv。

## 残余触发归因（逐行，主口径）

| 集 | 残余旗标行 | 归因 |
|---|---|---|
| Q1 | MG 3.11 vs [22,32] BELOW | 跨研究解离方案异质（Lukowski 温和方案 Müller 保留率远低于 Q2/Q3——同属"悬液"仍差 8 倍）；面侧无法再拆（3 研究） |
| Q1 | Rod 62.15 vs [30,49] ABOVE | 真中央凹尺度轴（H3 继承）——Q1 fovea 取材 vs 折面供者 macula/peripheral 混合 |
| Q2 | Rod 30.01 BELOW / BC 32.61 ABOVE | 同上方案异质 + 作者 ident 粗粒度（BC 32.6% 系 ident 簇偏置，E7 敏感性未反转判定） |
| Q2 | Micro 1.83 vs [0,1] ABOVE | PERSISTS（v0 亦旗）——小胶质计数口径轴，非悬液层职责 |
| Q3 | BC 15.7 vs [16,34] BELOW | 压线 0.3pp（floor 语义的机械结果，禁手调） |
| Q3 | RGC 7.54 vs [0,1] ABOVE | ind607 central 库 RGC 43.4% 结构离群（真值构造轴，评估侧已知） |
| Q4 | BC/HC/Astro/MG 4 行 | 分选混合设计 vs 单层参照——本卡无独立分选悬液参照可用（缺口 G-1） |
| Q5b | AC/MG/RPE/Rod 4 行 | nucleus 严格带语义 + Chen_b 组成特殊性——与悬液层无关（判据另案 H4 语义） |

## 敏感性一览（全并报，均不改主判）

- pooled13 含自身：Q1 20% / Q2 10% / Q3 10%（**禁作达标声明**——自权重面，astra D2）。
- R1B 包络：Q1 10 / Q2 10 / Q3 0 / Q4 10 / Q5b 10%（后验语义，激活选择归 PI）。
- E7 成对（两侧同步）：Q1 2 / Q2 3 / Q3 2（判定不变，方向稳定）。
- Q3 供者合并：Q1 30% / Q2 40% / Q3 20%——**警示：达线两集的 PASS 对单元独立性敏感**，
  印证 astra "过门≠跨研究验证"告诫；3 研究 13 单元的悬液层只能给出**暂定**区间。
- RC6 self-only 描述命中 1/10（披露，非判定）。

## 缺口登记（后续实质路径，全部涉外部获取=下载审批另案，本卡未动）

- G-1 分选悬液独立第二研究（含逐细胞作者注释与样本级策略标签）→ 唯一能实质解 Q4 的路径。
- G-2 GSE203499 逐细胞作者注释件（10x 悬液 41 样本健康+AMD）→ 扩 RC5 折面支撑。
- G-3 foveola 尺度 A 级单元（H3 继承）。
- G-4 悬液层需 ≥3 研究/折才谈稳态；现层定位为**暂定参照面**，激活前需扩面复核。
- G-5 零带宽行（RPE [0,0]/limbus SMC）判据语义=另案（H4 继承，PI 点名）。

## 边界自证

- 冻结件零触碰：v0/v1/COMPV1 计算件/evalset defs+truthfix 件全部 mtime 早于本卡启动
  （ledgers/SHA_SIDECAR_ledger.txt + SHA_POST_verify.txt，v1 json 实时 sha 对 COMPV1 manifest 单行命中）。
- kb/composition/ 本卡新增仅旁挂两文件；kb/markers、overlay、mcp_server、evalset 未写。
- 零下载、零外网数据获取（方法学核实仅查公开题录/摘要文本，无数据下载）；禁 push 遵守。
- 计算段 obs-only backed 读取，单进程峰值 RSS 5.7GB（/usr/bin/time -v 实测），无需 systemd-run 托管段。
- 全程 available 内存 ≥179G，无并发风险；心跳已带。
- 规则变更史全留痕：v0.1 DRAFT → astra 裁定 → v1.0 FINAL，任何旗标数字产生于 v1.0 定稿之后。

## 请 PI 定夺（不自动做）

1. 旁挂面是否接线/激活（永远归 PI；本卡 wiring=OFF）。
2. R1A vs R1B 语义选择（H1 继承）——本卡数据支持"R1B 下五集 0-10%"的并排事实，但主口径未动。
3. G-1/G-2 是否立项补数据（涉下载审批）。
4. Q4 样本级策略拆分（foveal 未分选可入 RC5、外周分选建真 RC6）作为 COMPV1Y 候选——规则性改动，须重新预注册。
