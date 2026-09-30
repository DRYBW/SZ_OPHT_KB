# BRIEF_COMPV1X — 组成基线扩面：细胞悬液参照层补装（OB-3 闭环尝试，PI 2026-09-30 放行"能搞完的搞完"）

## 背景与继承裁决（必读）
- COMPV1（t_37a35220，2026-09-29）OB-1/OB-2 过、OB-3 旗标率未压回 ≤20%——根因=缺**细胞悬液 A 级参照层**（现役基线主要单核悬液口径，与悬液建库数据系不匹配致假越界）
- 本卡=用盘上已有细胞悬液数据集补该参照层，复验旗标率。原 H1（R1A vs R1B 区间语义）**维持 R1A 主口径不动**（现状默认），R1B 仅作敏感性并报
- PI 放行原话："按照我们现有的数据……能够全部搞完了就搞完，搞完之后验证一下，验证……没有问题就可以直接上传"

## 任务
1. Phase-0 取证：盘点盘上细胞悬液 A 级可用集（registry 逐细胞作者注释标准集优先；禁自家共识注释当真值——09-28 纪律）；候选不足即 block 报缺口，勿硬凑
2. 按 kb/composition v1 分层版既有 schema 派生"细胞悬液建库策略"参照面（每行挂 PMID/来源声明；供者级统计；发育轴/物种分面铁律继承）
3. 复验：用新参照面重跑 COMPV1 同款旗标计算——目标 OB-3 旗标率 ≤20%；R1A 主口径 + R1B 敏感性双并报
4. 达标→新面以**旁挂版本文件**落 kb/composition/（禁覆盖现役冻结件，命名带 _cell_suspension_v1 后缀 + sha 台账）；不达标→如实 NOT_READY + 归因清单
5. 产物：/mnt/D/EyeKB/plans/compv1x_20260930/（COMPV1X_REPORT.md + ledgers/ + 中间脚本全保留）
6. 资源纪律：并发前 /usr/bin/time -v 实测 RSS 基线、systemd-run MemoryMax 托管、心跳带 available、<40G 停并发落卡

## 领地
可写：kb/composition/（仅新增旁挂文件）、plans/compv1x_20260930/
禁写：kb/markers 与 overlay（KB9ACT 卡领地）、mcp_server、evalset 冻结面
禁 push。完成或遇阻必须调 kanban_complete/kanban_block 落卡。
