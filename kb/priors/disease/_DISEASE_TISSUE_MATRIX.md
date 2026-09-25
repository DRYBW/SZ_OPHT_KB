# 疾病 × 组织/材料 × 发育档 矩阵 (薄层架构总览)

> schema: eyekb-disease-matrix/1.1 | 生成: 2026-09-23 | 卡片: t_be336eee | 生成器: build_disease_v2.py (KB1v2 t_16c3e020)
> 眼科通用架构 (PI 2026-09-23): 疾病条目=叠加在组织基线 (kb/baselines/) 之上的薄层; **批量铺宽暂缓** (Astra T6) —— 先以 PDR 膜一个格子验证判读收益 (PRIOR_DIFF), 再按样本入口增量扩展。
> **KB2c 发育轴 (裁定 Q3)**: 格子键=(disease, material, organism_stage) 三键; 现网全部格=adult; 发育期/胎儿样本不进成人疾病格 (PI 指令: '即使是一个组织也不对的')。

| 疾病 | 组织/材料格 | 发育档 | development_axis (KB3) | 状态 | 说明 |
|---|---|---|---|---|---|
| PDR | fibrovascular_membrane | adult | **FILLED (示例格)** | PDR__fibrovascular_membrane.md |
| PDR | vitreous | adult | **placeholder** | 定性锚已有 (B: PMID 39220810, T 91.6%); 未达最小可用标准的独立条目门槛 — 暂记于示例格 cross_material_note |
| PDR | retina_adjacent | adult | **placeholder** | B 级文献锚 (MG_EARLY_DR/DR_RETINA_SC/MULLER_REDD1) |
| NPDR/DME | retina | adult | **placeholder** | 与 PDR 不同阶段不同材料, 不得并入 (T6: 不合成一个组成基线) |
| nAMD/GA | RPE_choroid | adult | **placeholder** | 组织基线侧 RPE/choroid 现为骨架 → 先回填 W1 骨架再谈疾病格 |
| RRD | subretinal/ERM membrane | adult | **placeholder** | GSE165784 RRD-ERM n=1 —— 单样本只可报告'该样本中观察到', 不建普遍条目 (T3) |
| ERM (特发性) | membrane | adult | **placeholder** | 与 PDR 膜同材料不同病 —— 复用概念 ID, 另立格子 |
| glaucoma | optic_nerve_RGC | adult | **placeholder** | 组织侧 optic_nerve 骨架已回填映射 (HRA006282 本地可算) |
| keratoconus | cornea | adult | **placeholder** | 组织侧 ocular_surface 基线已 filled → 该格证据门槛最低 |
| Fuchs/内皮失代偿 | corneal_endothelium | adult | **placeholder** | D002 内皮层仅 404 细胞, 基线侧先扩 |
| uveitis (中间型) | vitreous | adult | **placeholder** | 与 PDR__vitreous 共享材料概念 |
| cataract | lens | adult | **placeholder** | 组织侧 lens 骨架=LEC 域裁定 |

## 架构规则

1. 组织基线与疾病条目解耦: 疾病格不重复组织比例, 只写 疾病×材料 的预期/旗标/签名 (身份+状态两级)。
2. 同一疾病不同材料=不同格 (PDR 膜 ≠ PDR 玻璃体 ≠ 邻近视网膜; Astra T2 取样材料锚定)。
3. 同一材料不同病不合并 (PDR 膜与特发 ERM 膜复用概念 ID 但分格; T6)。
4. 开格门槛=条目最小可用标准 (见示例格), 无特异证据不单建亚型格 (T4/P4)。
5. 每格链接: 组织基线文件 ↔ RAG reason-tag (evidence_meta sidecar) ↔ 文献索引页 ↔ 概念表 (W5 四向链接)。
6. **发育轴单列 (KB2c)**: 格子键含 organism_stage; 成人疾病格只收 adult 材料, 发育期疾病样本 (如 pediatric ROP 膜) 单立新格, 禁并入成人格 (PI 红线)。

## KB3 发育轴预留格 (t_5425a7ca — 只立格不填内容)

| 疾病 | 材料格 | development_axis | 状态 |
|---|---|---|---|
| ROP (早产儿视网膜病变) | developing_retina_vascular | **fetal_neonatal** | RESERVED —— 发育轴侧血管增殖病, 与 PDR 成人格永不并池/互参照; 填格前提=发育期数据/文献锚+过裁定 |

> 架构规则 6 的占位实现: 成人格数组 rows=12 不动 (回归锁), 预留格走独立键 development_axis_reservations (双锁)。
