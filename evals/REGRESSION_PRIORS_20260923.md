# KB1-K4 判读层工具黄金回归 (2026-09-23)

started: 2026-09-23 21:39:30 | **22 PASS / 6 FAIL**

- [x] TC human/retina 命中 human_retina  
- [x] TC retina rows 与 JSON 逐项一致 (10 类×数值)  10 rows
- [x] TC retina 10 类齐全  
- [x] TC retina 数值抽查 Rod=33.55/RGC=12.58/RPE=0.03  
- [x] TC human/membrane 命中 human_pdr_membrane  
- [x] TC membrane rows 与 JSON 逐项一致  8 rows
- [ ] TC membrane myeloid PDR-only=79.49  
- [ ] TC disease 参数命中 human_pdr_membrane (视网膜无 PDR 基线条)  None
- [x] DP 别名 PDR→proliferative_DR  
- [x] DP 旗/签名与 JSON 逐项一致  None
- [x] DP tissue=vitreous 过滤 (仅1组织端)  
- [ ] MD retina 主表 10 行×(类/%/区间) 与工具一致  md rows=11
- [ ] MD membrane 主表 PDR-only% 与工具一致  md=9
- [x] MD disease 条目含预期矩阵/旗/签名关键词  
- [x] 出处闭包: retina rows 全 source_ids 可解析  []
- [x] 出处闭包: membrane rows 全 source_ids 可解析  []
- [x] 出处闭包: PDR 矩阵 source_ids 可解析  []
- [x] 红线8机检: 全部 sources 带 PMID 或数据集路径  38 sources
- [x] 漂移: HRCA total=3,177,310  3177310
- [x] 漂移: HRCA Rod% 与条目一致  [1066056, 33.55]
- [x] 漂移: GSE165784 myeloid PDR% 与条目一致  [5677, 79.49]
- [x] list_tools == 五工具  ['get_disease_prior', 'get_kb_page', 'get_tissue_composition', 'query_marker', 'search_literature']
- [x] stdio TC(retina) == 直调 (深度相等)  None
- [x] stdio DP(PDR) == 直调 (深度相等)  None
- [x] 边界: 未知物种 → error+available  {'error': "无匹配组成条目 (species='dragon' tissue='retina' disease='')", 'available': 
- [x] 边界: 未知疾病 → error  {'error': "无匹配疾病条目: 'xyz-not-exist'", 'available': [{'entry_id': 'human_pdr_memb
- [ ] 旧套件不回归: regression_mcp_vs_direct_v2_20260923.py  rc=1 fails=?
- [ ] 旧套件不回归: selftest_tools_v2_20260923.py  rc=1 fails=1