# 组成基线骨架: 人 iris (字段全, 比例=待回填)

> schema: `eyekb-baseline/1.1` | entry_id: `baseline_human_iris` | 状态: skeleton_mapping_backfilled | 发育轴: **organism_stage=unknown** | 生成: 2026-09-23 | 卡片: t_16c3e020
> **KB3 发育档 (卡片 t_5425a7ca)**: development_stage=**unknown** | 适用档(回填时写死): adult —— KB3 禁令 (PI 红线 2026-09-23): 发育期数据不得进成人基线统计池, 反之亦然 —— 同一组织胎儿≠成人, adult/fetal 不互为参照。
> 本文件由 `/mnt/D/EyeKB/scripts/baselines/build_baselines.py` 从同名 .json 自动渲染 —— 改内容改 JSON+脚本, 手改 MD 会被覆盖。
> ⚠ 发育轴披露: KB2c 发育轴: 骨架条=unknown (未实算)。回填时必须按发育轴单列 — adult 材料出 adult-only 主档 (>=18y 裁定 Q2), 胎儿/发育期材料另立条目, 禁止胎儿与成人同组织混档 (PI 红线)。

**用途口径 (Astra T2 裁定固化): 本基线 = 该取样材料在该实验流程下捕获到的细胞构成的身份参考 + 背景对照; **不得当组成达标线**。疾病手术材料的取样对象 ≠ 健康器官 (如 PDR 纤维血管膜不得对照健康视网膜组成验收); 注释数据出现清单外身份 → 触发 unexpected 旗即可, 不得强制改成清单内身份 (标签接受上下文一致性核查, 非白名单定位)。**

## 证据等级口径
- **A**: 本地实测复算 (带文件路径+脚本)
- **B**: 文献原文直接报告
- **C**: A 级源数据供者级/跨研究分布推得的经验区间
- **qualitative**: 文献仅定性描述 → 只存定性, 不补造区间 (Astra T2)
- **not_estimable**: 区间无法估计 —— 合法状态, 注释仍可开展 (Astra T2)

## 发育轴口径 (KB2c 裁定 2026-09-23 — 阈值改动须过裁定)
- 顶层轴: `organism_stage` ∈ ['fetal', 'adult', 'developing', 'unknown']
- **adult**: UBERON development_stage 数字化年龄 >= 18y 判 adult; 显式成年术语 (late/prime/middle/mature/human adult stage, 年代段>=3rd) 亦判 adult 并记 rule; 阈值改动须过裁定 (KB2c Q2, 2026-09-23)
- **developing**: newborn/infant/postnatal stage 与 <18y 数字年龄/年龄段 → developing (KB2c Q2)
- **fetal**: fetal/embryonic/gestation/Carnegie 术语 → fetal; 永不并入 adult 主档 (红线1)
- **unknown**: 无年龄列/未映射术语/organoid/年龄段跨阈值 → unknown, 必须披露行, 禁静默归 adult (红线2)
- aging 正交轴: >=60 老年分层不在本轴 — aging 是正交独立轴, 将来单独立条目 (裁定 Q2)
- 两档身份: {'adult_only': 'baseline_human_iris__adult_only__kb2c', 'adult_pool': 'baseline_human_iris__adult_pool__v1.0'}

## Astra T2 元数据字段
- **取样材料**: 待定 (骨架: 建基线前必须先固定实际取样材料口径, Astra T2)
- **疾病阶段**: 待定
- **治疗背景**: 待定
- **scRNA_vs_snRNA**: 待定
- **富集步骤**: 待定
- **解离方法**: 待定
- **供者数**: 待定
- **计数分母**: 待定
- **证据来源**: 见 mapping_from_t_6f5cc731 各候选数据集

## 组成数据状态
**区间无法估计 (合法状态, Astra T2) —— 待按映射候选数据集做供者级计算; 数据不在本地者须先过下载审批铁律**

## 候选数据集映射 (t_6f5cc731 盘点回填)
- `HASA "Iris" (OA-D004/016 collection内)` [人] 57,422 cells | 注释: portal | 可得性: portal h5ad | 人虹膜唯一portal注释资源
- `GSE183690` [鼠] 8样本(control/收缩/舒张) | 注释: paper(PMID34783308) | 可得性: RAW.tar | 鼠虹膜snRNA图谱
- `GSE297613` [人] 6样本(成人虹膜+iPSC虹膜肌) | 注释: IntegratedIris.rds内嵌 | 可得性: rds+Rmd分析代码全公开 | 虹膜肌亚型;规模小
- `GSE147979_iris (OA-D019)` [人+猪] 多组织含iris | 注释: portal | 可得性: 本地(HOSCA) | 

**裁定 (t_6f5cc731)**: ✅可建参考模型-小尺度（HASA Iris 57K portal注释为主，GSE297613/GSE183690补肌型与鼠对照；类少结构简单，够用）

**回填路径**: ①候选数据本地化状态核实 → ②官方注释切片 (celltype-annotation-sourcing 纪律) → ③本脚本追加 build_<tissue>() 供者级复算 → ④基线状态改 filled_donor_level → ⑤KB2c 发育轴: 仅 adult (>=18y) 供者入主档, 非 adult 逐行披露; 胎儿/发育期材料单独立条目, 禁并入 adult

## 注意事项
1. 骨架条目不得用于'该组织已有组成基线'的对外表述 (Astra T6: 工程一致性≠正确性证据)

