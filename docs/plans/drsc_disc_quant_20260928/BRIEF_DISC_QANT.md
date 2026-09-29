# BRIEF_DISC_QANT_20260928 —— drsc 纪律 D-2/D-3 只读量化（决策依据卡，PI 拍板见 directive 追加七B）

## 目标（一句话）
把"供体翻否杠杆门"和"深度匹配 ranking 位移门"从口头纪律变成**有数字的建议档**，供 PI 勾选进协议。本卡**不改任何协议、不动任何冻结件、不出新分析结论**。

## 主检验（唯一）
对盘上已冻结产物做两项敏感性重算，产出勾选表。

## 任务 A：leave-one-donor-out 翻否杠杆（D-2）
- 输入（只读）：<EYEKB>/plans/obligrun_20260928/ 票面 v2.1（99 票三席）+ 各簇 truth/donor 映射 + <EYEKB>/plans/evalset/ 冻结卷（含 donor 列者）。
- 回跑：每个被计 hit 的单元，逐一删除其杠杆 donor（该单元真值/票源的供体）后按票规 v2 C2b 重算 named 集，记录 hit 是否翻否；同理对冻结卷复算。
- 输出：逐单元杠杆表（donor -> 删除后翻转与否）+ 分布统计（多少 % 单元"单 donor 删除即翻号"，对照 D1 线 S13 基线 5/7）+ **建议警戒阈值三档**（如：单 donor 翻转即旗标 / >=20% 单元翻转才升级警戒 / 仅记录不门控）与各自会旗标多少单元的实测数。

## 任务 B：深度匹配下 top_genes ranking 位移（D-3）
- 输入（只读）：kb/baselines/ 各面板 json 的 top_genes（v6 现役面）+ demo/评估卷的 counts 层（h5ad 在盘件）。
- 做法：对每面板核心细胞类，做测序深度匹配重抽（按 n_genes/total_counts 分位对齐抽样子集，随机 seed 冻结=20260928），重算 marker 统计（同现行口径 mean diff/score），量 top5/top10 位移率 + Kendall tau；对照=全样重算。
- 输出：逐面板位移表 + 汇总"位移超过阈值的 top_genes 行数"三档建议（如 top5 任一位移 / >=3 位移 / 仅高表达基因）+ 明确声明：位移是深度混杂证据，**不判词条对错**。

## 纪律
- 全程只读为主；解释一切"翻转/位移"仅作敏感性观察，禁因果/禁"注释有误"结论句式；两分句口径（strict/loose）并报时取严。
- 球门与票规零移动零改算，阈值只出建议档；"若此门当时上线会旗标什么"必须双口径（冻结票面 + 评估卷）都算。
- 领地：工作目录 <EYEKB>/plans/drsc_disc_quant_20260928/（唯一可写）。禁写：kb/、plans/evalset/、obligrun 目录、mcp_server/。scrnaseq env python（<CONDA_ROOT>/envs/scrnaseq/bin/python）读新格式 h5ad。
- CPU；systemd-run MemoryMax=16G；心跳带 available；产物全保留；完成或受阻落卡（kanban_complete/block）。

## 交付清单
DECISION_TABLE_composition_gates.md（勾选表：门 x 实测旗标数 x 三档建议 x 空勾选栏）+ 杠杆表/位移表 tsv + 脚本 + 日志 + 盲区声明（口径限制、可能低估/高估方向）。
