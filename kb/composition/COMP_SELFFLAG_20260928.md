# COMP_SELFFLAG_20260928 — EXPECTED_COMPOSITION_v0 自检旗标报告（只读，出旗标不出结论）

> 卡 t_fa03e1d7 | 输入：`EXPECTED_COMPOSITION_v0.json` × 盘上冻结产物（kb/baselines, plans/evalset 冻结件, demo_gse165784 v2 共识草稿表）
> **⛔ 本面未接线。旗标=提示复核，不等于注释错误；接线与激活另卡另批（PI 拍板）。**

## 0. 方法
- 对账对象：评估卷各成员真值组成（Q1–Q9，真值=作者级/portal 注释或 mapped_10class；非自家聚类重标注）+ demo GSE165784 v2 Track B 共识注释草稿（疾病材料，展示门行为）。
- 旗标规则：pct < low → BELOW；pct > high → ABOVE；面外身份（T/巨噬/成纤维/前体…）→ off_face_identity 披露行；比例分母=该数据集全部细胞。
- 反向质检内建条款：健康公开集被旗标类型占比 >20% → 如实报告“面太窄=面的问题不是数据的问题”。
- 域外轴（不计入反向质检分母）：Q7 小鼠（物种轴）、Q8 胎儿（发育轴）、Q6（与眼表面同构建源=循环参照）、Q9 demo（疾病手术材料，usage_scope 禁当达标对照）。

## 1. 汇总旗标率

| 数据集 | 面 | 细胞数 | 旗标行数/面行数 | 旗标率 | 反向质检 |
|---|---|---|---|---|---|
| Q1_Lukowski2019 | retina | 19,694 | 4/10 | 40.0% | TRIGGER(>20%) |
| Q2_GSE155288 | retina | 92,385 | 4/10 | 40.0% | TRIGGER(>20%) |
| Q3 | retina | 20,091 | 3/10 | 30.0% | TRIGGER(>20%) |
| Q4 | retina | 84,982 | 2/10 | 20.0% | under |
| Q5b | retina | 412,419 | 0/10 | 0.0% | under |
| Q7 | retina | 361,022 | 5/10 | 50.0% | not_counted(disease/发育/循环) |
| Q8 | retina | 226,506 | 4/10 | 40.0% | not_counted(disease/发育/循环) |
| Q6_D002_sub100k | ocular_surface | 100,000 | 1/9 | 11.1% | not_counted(disease/发育/循环) |
| Q9_GSE165784_demo_v2 | retina | 10,069 | 7/10 | 70.0% | not_counted(disease/发育/循环) |

## 2. 旗标明细（逐行 数据集×细胞类型）

| 数据集 | 行 | 观测% | 面区间[低,高] | 状态 |
|---|---|---|---|---|
| Q1_Lukowski2019 | Rod | 62.15 | [22,58] | FLAG_ABOVE |
| Q1_Lukowski2019 | Cone | 2.96 | [1,7] | in_range |
| Q1_Lukowski2019 | BC | 10.51 | [12,33] | FLAG_BELOW |
| Q1_Lukowski2019 | AC | 1.43 | [6,28] | FLAG_BELOW |
| Q1_Lukowski2019 | HC | 0.0 | [1,8] | FLAG_BELOW |
| Q1_Lukowski2019 | RGC | 0.32 | [0,15] | in_range |
| Q1_Lukowski2019 | MG | 3.11 | [3,12] | in_range |
| Q1_Lukowski2019 | Astro | 0.0 | [0,2] | in_range |
| Q1_Lukowski2019 | Micro | 0.72 | [0,1] | in_range |
| Q1_Lukowski2019 | RPE | 0.0 | [0,1] | in_range |
| Q1_Lukowski2019 | OFF_FACE::OTHER | 18.81 | null(披露行) | off_face_identity |
| Q2_GSE155288 | Rod | 30.01 | [22,58] | in_range |
| Q2_GSE155288 | Cone | 2.1 | [1,7] | in_range |
| Q2_GSE155288 | BC | 32.61 | [12,33] | in_range |
| Q2_GSE155288 | AC | 2.41 | [6,28] | FLAG_BELOW |
| Q2_GSE155288 | HC | 0.69 | [1,8] | FLAG_BELOW |
| Q2_GSE155288 | RGC | 0.63 | [0,15] | in_range |
| Q2_GSE155288 | MG | 27.51 | [3,12] | FLAG_ABOVE |
| Q2_GSE155288 | Astro | 0.79 | [0,2] | in_range |
| Q2_GSE155288 | Micro | 1.83 | [0,1] | FLAG_ABOVE |
| Q2_GSE155288 | RPE | 0.0 | [0,1] | in_range |
| Q2_GSE155288 | OFF_FACE::Pericytes | 0.97 | null(披露行) | off_face_identity |
| Q2_GSE155288 | OFF_FACE::Endothelium | 0.45 | null(披露行) | off_face_identity |
| Q3 | Rod | 45.52 | [22,58] | in_range |
| Q3 | Cone | 1.05 | [1,7] | in_range |
| Q3 | BC | 15.7 | [12,33] | in_range |
| Q3 | AC | 2.47 | [6,28] | FLAG_BELOW |
| Q3 | HC | 0.73 | [1,8] | FLAG_BELOW |
| Q3 | RGC | 7.54 | [0,15] | in_range |
| Q3 | MG | 26.22 | [3,12] | FLAG_ABOVE |
| Q3 | Astro | 0.04 | [0,2] | in_range |
| Q3 | Micro | 0.31 | [0,1] | in_range |
| Q3 | RPE | 0.0 | [0,1] | in_range |
| Q3 | OFF_FACE::Other_mapped | 0.42 | null(披露行) | off_face_identity |
| Q4 | Rod | 8.32 | [22,58] | FLAG_BELOW |
| Q4 | Cone | 2.35 | [1,7] | in_range |
| Q4 | BC | 30.25 | [12,33] | in_range |
| Q4 | AC | 16.25 | [6,28] | in_range |
| Q4 | HC | 3.37 | [1,8] | in_range |
| Q4 | RGC | 13.42 | [0,15] | in_range |
| Q4 | MG | 23.41 | [3,12] | FLAG_ABOVE |
| Q4 | Astro | 1.35 | [0,2] | in_range |
| Q4 | Micro | 0.79 | [0,1] | in_range |
| Q4 | RPE | 0.0 | [0,1] | in_range |
| Q4 | OFF_FACE::Other_mapped | 0.48 | null(披露行) | off_face_identity |
| Q5b | Rod | 26.12 | [22,58] | in_range |
| Q5b | Cone | 5.64 | [1,7] | in_range |
| Q5b | BC | 25.72 | [12,33] | in_range |
| Q5b | AC | 27.4 | [6,28] | in_range |
| Q5b | HC | 3.56 | [1,8] | in_range |
| Q5b | RGC | 2.82 | [0,15] | in_range |
| Q5b | MG | 4.18 | [3,12] | in_range |
| Q5b | Astro | 0.14 | [0,2] | in_range |
| Q5b | Micro | 0.03 | [0,1] | in_range |
| Q5b | RPE | 0.02 | [0,1] | in_range |
| Q5b | OFF_FACE::glial cell | 4.37 | null(披露行) | off_face_identity |
| Q7 | Rod | 9.44 | [22,58] | FLAG_BELOW |
| Q7 | Cone | 1.34 | [1,7] | in_range |
| Q7 | BC | 40.91 | [12,33] | FLAG_ABOVE |
| Q7 | AC | 12.2 | [6,28] | in_range |
| Q7 | HC | 0.06 | [1,8] | FLAG_BELOW |
| Q7 | RGC | 22.59 | [0,15] | FLAG_ABOVE |
| Q7 | MG | 2.27 | [3,12] | FLAG_BELOW |
| Q7 | Astro | 0.0 | [0,2] | in_range |
| Q7 | Micro | 0.45 | [0,1] | in_range |
| Q7 | RPE | 0.11 | [0,1] | in_range |
| Q7 | OFF_FACE::nan | 10.27 | null(披露行) | off_face_identity |
| Q7 | OFF_FACE::Endothelial | 0.28 | null(披露行) | off_face_identity |
| Q7 | OFF_FACE::Pericyte | 0.08 | null(披露行) | off_face_identity |
| Q8 | Rod | 16.85 | [22,58] | FLAG_BELOW |
| Q8 | Cone | 4.12 | [1,7] | in_range |
| Q8 | BC | 9.05 | [12,33] | FLAG_BELOW |
| Q8 | AC | 11.65 | [6,28] | in_range |
| Q8 | HC | 4.21 | [1,8] | in_range |
| Q8 | RGC | 18.54 | [0,15] | FLAG_ABOVE |
| Q8 | MG | 2.89 | [3,12] | FLAG_BELOW |
| Q8 | Astro | 0.0 | [0,2] | in_range |
| Q8 | Micro | 0.0 | [0,1] | in_range |
| Q8 | RPE | 0.0 | [0,1] | in_range |
| Q8 | OFF_FACE::retinal progenitor cell | 32.48 | null(披露行) | off_face_identity |
| Q8 | OFF_FACE::OFFx cell | 0.21 | null(披露行) | off_face_identity |
| Q6_D002_sub100k | Corneal Endothelium | 0.07 | [0,1] | in_range |
| Q6_D002_sub100k | Endothelium | 5.75 | [0,9] | in_range |
| Q6_D002_sub100k | Epithelium | 43.36 | [7,71] | in_range |
| Q6_D002_sub100k | Fibroblasts | 39.91 | [12,45] | in_range |
| Q6_D002_sub100k | Immune Cells | 1.72 | [0,3] | in_range |
| Q6_D002_sub100k | Melanocytes | 1.23 | [0,3] | in_range |
| Q6_D002_sub100k | Pericytes | 6.5 | [0,5] | FLAG_ABOVE |
| Q6_D002_sub100k | Schwann Cells | 0.98 | [0,2] | in_range |
| Q6_D002_sub100k | Smooth Muscle Cells | 0.48 | [0,1] | in_range |
| Q9_GSE165784_demo_v2 | Rod | 0.0 | [22,58] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | Cone | 0.0 | [1,7] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | BC | 0.0 | [12,33] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | AC | 0.0 | [6,28] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | HC | 0.0 | [1,8] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | RGC | 0.0 | [0,15] | in_range |
| Q9_GSE165784_demo_v2 | MG | 0.0 | [3,12] | FLAG_BELOW |
| Q9_GSE165784_demo_v2 | Astro | 0.0 | [0,2] | in_range |
| Q9_GSE165784_demo_v2 | Micro | 17.4 | [0,1] | FLAG_ABOVE |
| Q9_GSE165784_demo_v2 | RPE | 0.0 | [0,1] | in_range |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_Inflam | 10.73 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_DAMLAM | 10.01 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_MHCII | 9.42 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mono_Nonclass | 8.24 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_DC | 7.85 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_Tissue | 7.0 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mono_Classical | 6.82 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Mac_RRD | 4.3 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Myofibroblast | 3.69 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Tcell | 3.52 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Proliferating | 3.12 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Endo_vascular | 2.68 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Pericyte_vascular | 2.48 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::MG(候选) | 1.62 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::Plasma | 0.61 | null(披露行) | off_face_identity |
| Q9_GSE165784_demo_v2 | OFF_FACE::pDC | 0.52 | null(披露行) | off_face_identity |

## 3. 反向质检验算（内建条款）

- 计入反向质检的健康公开集：Q1/Q2/Q3/Q4/Q5b（共 5 个，人·正常·成人视网膜）。
- **触发（>20% 类型被旗标）：3 个 —— Q1_Lukowski2019 40.0%; Q2_GSE155288 40.0%; Q3 30.0%**
- 判读（照实，非结论）：按内建条款，这首先说明 **v0 区间对“跨平台/跨取材区域/分选设计”过窄**，是面的问题不是数据的问题。具体可归因：Q1/Q2=中央凹取材+scRNA 细胞悬液（面主档为 snRNA 核悬液，Astra T2 已声明两口径不可直比）；Q3/Q4=Macroglia 签名拆分口径+CD73/CD90 分选设计抬 BC/MG 压 Rod；Q5b 与面主档同源（HRCA 内部构成）旗标率 0 是**循环自证的上界，不是泛化好**。
- 处置建议（不代拍，激活另卡另批时随文呈 PI）：v1 按 suspension_type（核/细胞）与取材区域（中央凹/周边/全视网膜/分选）分层出区间；或把“先验面”定义为带设计豁免的条件面。

## 4. 面外身份披露（非旗标，informational）

### Q8 胎儿（域外轴行为记录）
- retinal progenitor cell 为最大类 73,566/226,506=32.5%（分母经复核=def.classes 全类合计=全文件）—— 成人面无 progenitor 行，全部入 off_face_identity；发育材料对照成人面的预期行为。

### 各集面外身份 Top 行
- **Q1_Lukowski2019**: OTHER 18.81%
- **Q2_GSE155288**: Pericytes 0.97%; Endothelium 0.45%
- **Q3**: Other_mapped 0.42%
- **Q4**: Other_mapped 0.48%
- **Q5b**: glial cell 4.37%
- **Q7**: nan 10.27%; Endothelial 0.28%; Pericyte 0.08%
- **Q8**: retinal progenitor cell 32.48%; OFFx cell 0.21%
- **Q9_GSE165784_demo_v2**: Mac_Inflam 10.73%; Mac_DAMLAM 10.01%; Mac_MHCII 9.42%; Mono_Nonclass 8.24%; Mac_DC 7.85%; Mac_Tissue 7.0%; Mono_Classical 6.82%; Mac_RRD 4.3%

## 5. 声明
- 本报告只输出旗标清单与比例分布；旗标≠注释错误；不据本报告判定任何既有注释的对错。
- 本面未接线、默认 OFF；接线与激活另卡另批。
- 复现：`python3 scripts/build_expected_composition_v0.py && python3 scripts/selfcheck_comp_v0.py && python3 scripts/gen_md.py`（日志 logs/selfcheck_run.log）。
