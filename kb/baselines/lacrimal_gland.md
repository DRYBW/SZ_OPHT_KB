# 组成基线·观察档：人泪腺 (lacrimal_gland) — KB8 t_e7ec73ab, 2026-09-25

**状态=observed_single_study_pilot**：单研究（GSE164403，世界唯一人泪腺本体单细胞图谱，PMID:33730555）、
组织池 QC 后 1,076 细胞、3 供体标签（patient 3 占 76% 主导）的实测组成。**不是**跨研究参考分布，
禁当组成达标线（Astra T2 口径沿用），禁入一切打分。

## 组分区（本卡自建聚类口径——作者未沉积细胞类型标签）

| 组 | 细胞 | 占比 | 词条/参考 |
|---|---|---|---|
| Lacrimal_secretory_tearcell | 65 | 6.0% | markers_v6_lacrimal_increment（LACRT/SCGB1D1/SCGB2A1/CST4/CST1/MUC7）|
| Lacrimal_duct_epithelial | 455 | 42.3% | markers_v6_lacrimal_increment（PRR27 单基因 core）|
| Lacrimal_myoepithelial | 18 | 1.7% | 警示条 core=[]（mural×上皮双向火灾，见词条文件）|
| T cells | 106 | 9.9% | 参考层（膜 v1 面板）|
| IgA plasma cells | 292 | 27.1% | 参考层；占比上偏风险（IGH ambient 板级携带）|
| Endothelial | 14 | 1.3% | 参考层；支撑极弱 |
| Fibroblast/stroma | 115 | 10.7% | KB6b 通签注记，不入独立新词条 |
| Surface epithelium 混入 | 11 | 1.0% | 真结膜上皮（face_v6 词条审计实证命中=阳性对照）|

## 三条硬披露

1. **腺泡酶原缺口**：PRSS1/CTRB1/PNLIP 全池不可检出——"泪腺腺泡"在转录层未证；
   分泌组=LACRT+ 血清黏液池（CL:0000315 tear secreting cell）。
2. **384 孔板 ambient**：LYZ 0.8–14.9 万 CPM、LTF 0.5–5.9 万 CPM 跨组 det≈1.0；
   LACRT 非分泌组本底 1.5–5k CPM。分泌/浆细胞占比有上偏风险。
3. **类器官池（1,395 QC 细胞）永不入本档**：源论文限定类器官=导管模型；
   KB8 红线（两池分开记账）。patient "3" 跨池同号未证同体。

数据绑定 sha 见 JSON `data_binding`；复算链=词条文件 `provenance.pipeline`。
回填路径（backfill_path）：第二个独立人泪腺数据集当前世界不存在 → 本档维持 pilot 为终态直至新材料。
