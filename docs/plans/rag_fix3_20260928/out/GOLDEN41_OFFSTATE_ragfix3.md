# RAGFIX3 黄金回归 (gate1, off 态)

- 用例 41 = GOLDEN 10 retina + TISSUE_SPOT 31; 判据 = strip_sidecar 全等 (现行权威口径); top5 逐字对 ragfix2 基线
- **41/41 consistent; top5 漂移 0; 接线契约 8/9 → FAIL ❌**

| 组 | cell_type | species | tissue | 一致 | top-5 PMID (两侧同) |
|---|---|---|---|---|---|
| golden_retina | Rod | human | retina | ✅ | 34006945,36261438,40531615,36630901,35212809 |
| golden_retina | Cone | human | retina | ✅ | 34006945,40531615,40660409,36261438,32023475 |
| golden_retina | Retinal Pigment Epithelium | human | retina | ✅ | 34977041,37156914,36231108,38334673,39804630 |
| golden_retina | Muller Glia | human | retina | ✅ | 35167652,36277849,40531615,36977817,35212809 |
| golden_retina | Astrocyte | human | retina | ✅ | 41892278,36277849,37749651,35212809,34341398 |
| golden_retina | Microglia | human | retina | ✅ | 35212809,38409074,34006945,40858363,34341398 |
| golden_retina | Retinal Ganglion Cell | human | retina | ✅ | 34946963,34006945,38903914,32557945,37880369 |
| golden_retina | Rod Bipolar Cell | human | retina | ✅ | 33665228,34006945,41632798,36277849,35615708 |
| golden_retina | Horizontal Cell | human | retina | ✅ | 35615708,35212809,35325233,34006945,40660409 |
| golden_retina | Amacrine Cell | human | retina | ✅ | 34006945,35615708,35212809,36277849,40531615 |
| spot_cornea | corneal epithelium | human | cornea | ✅ | 34381080,37443842,40390022,38177186,42194275 |
| spot_cornea | corneal endothelium | human | cornea | ✅ | 34741068,39732756,34381080,42194275,37443842 |
| spot_cornea | keratocyte | human | cornea | ✅ | 34381080,37443842,40390022,34741068,38177186 |
| spot_cornea | limbal stem cell | human | cornea | ✅ | 37443842,34381080,37389178,34741068,38514716 |
| spot_conjunctiva | goblet cell | human | conjunctiva | ✅ | 37389178,37443842,34638869,37507439,36932081 |
| spot_conjunctiva | conjunctival epithelium | human | conjunctiva | ✅ | 37389178,37443842,34381080,32502616,42589107 |
| spot_conjunctiva | fibroblast | human | conjunctiva | ✅ | 40238113,37569323,38177186,40576432,38514716 |
| spot_sclera | fibroblast | human | sclera | ✅ | 40402520,40576432,40677403,42378569 |
| spot_sclera | chondrocyte | human | sclera | ✅ | 40576432,40402520,41803895,40677403,42378569 |
| spot_sclera | smooth muscle | human | sclera | ✅ | 41803895,40576432,40402520,40677403 |
| spot_trabecular_meshwork | trabecular meshwork cell | human | trabecular_meshwork | ✅ | 42291280,40728983,39952952,40423739,35627267 |
| spot_trabecular_meshwork | schlemm canal endothelium | human | trabecular_meshwork | ✅ | 39422453,41636427,32832237,38394161,34754027 |
| spot_trabecular_meshwork | endothelial cell | human | trabecular_meshwork | ✅ | 39422453,32832237,40126508,41636427,38173510 |
| spot_iris | iris smooth muscle | human | iris | ✅ | 41309590,36092714 |
| spot_iris | iris pigment epithelium | human | iris | ✅ | 41309590,36582303,38587075,38670973,36645183 |
| spot_iris | astrocyte | human | iris | ✅ | 41309590,36582303,38587075,38670973,36645183 |
| spot_ciliary_body | ciliary epithelium | human | ciliary_body | ✅ | 36163311,39273233,41805112,41057298,41290721 |
| spot_ciliary_body | endothelial cell | human | ciliary_body | ✅ | 36163311,39422453,36821388,41528844,33936569 |
| spot_ciliary_body | smooth muscle | human | ciliary_body | ✅ | 36163311,40055379,41528844,38989623,36582303 |
| spot_lens | lens fiber cell | human | lens | ✅ | 40598599,38643244,41989229,34946854,37048143 |
| spot_lens | lens epithelium | human | lens | ✅ | 40598599,41020554,40408092,40643341,40507153 |
| spot_lens | fiber cell | human | lens | ✅ | 38643244,40598599,41989229,37048143,34946854 |
| spot_optic_nerve | oligodendrocyte | human | optic_nerve | ✅ | 40567162,41856199,37681863,33981197,39198924 |
| spot_optic_nerve | astrocyte | human | optic_nerve | ✅ | 37681863,33627831,37749651,41856199,37759301 |
| spot_optic_nerve | microglia | human | optic_nerve | ✅ | 41856199,37681863,41705242,40567162,35309305 |
| spot_optic_nerve | retinal ganglion cell | human | optic_nerve | ✅ | 33499292,41856199,38903914,34946963,41601638 |
| spot_RPE | retinal pigment epithelium | human | RPE | ✅ | 34977041,38528525,40882639,35882847,41851144 |
| spot_RPE | endothelial cell | human | RPE | ✅ | 41254671,38528525,37528478,39888634,36645183 |
| spot_choroid | choriocapillaris endothelium | human | choroid | ✅ | 35181781,38115754,37504962,34546342,38232696 |
| spot_choroid | melanocyte | human | choroid | ✅ | 38232696,37289546,41528844,42579800,36645183 |
| spot_choroid | pericyte | human | choroid | ✅ | 36645183,34779136,41528844,38232696,41230906 |

## 接线契约 (MCP stdio 真往返)

- retina_list10: ✅
- retina_BC_v4.1_5genes: ✅
- v5_BC_pure: ✅
- v5_AC_49: ✅
- v5_HC_31: ✅
- all_list_plus10: ❌
- v5_gene_hits_alias: ✅
- v4.1_no_new_canon: ✅
- membrane_list: ✅
