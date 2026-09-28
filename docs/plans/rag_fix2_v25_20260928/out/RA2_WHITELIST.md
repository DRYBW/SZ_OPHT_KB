# RAGFIX2 白名单（门③追补轮 v2.5 · 16 基因候选检索 + 三条件题录核验 · 已锁定闭集 17 篇）

- 卡: t_6848d3de ｜ 判据冻结: BRIEF_RAGFIX2.md §3 ｜ 明细台账: RA2_WHITELIST.tsv + RA2_candidate_ledger.tsv + work/ra2_candidates_raw.json
- C1 题录含断言词 / C2 PMID 可核 / C3 非 HRCA 自引 ∧ 不在库防重蹈（HRCA_EXCL=41578023/32555229/34691611/37388908/32946783/39117640）
- 分档: T1=标题含symbol∧语境词 · T3=语境词在标题∧symbol在摘要 · T4=语境断言词在标题 ∧ symbol 经 EPMC 引号检索命中全文域（**下载后词边界 token 终裁**，out/RA2_token_verification.tsv） · chain=kb 词条自引 PMID 回填（题录语义一致核验，防 KB6/KB9 型错位）
- 闭集=下表全部 17 PMID（out/closed_set_ra2_pmids.txt），下载实耗 2.34MB ≤ 6MB 上限，零清单外下载，禁绕付费墙

| 基因 | 档位 | PMID | 题录 | 顶岗路 | 兑现 |
|---|---|---|---|---|---|
| CALD1 | T4 首选 39195219 token 未现 | 33028893 | Quantitative proteomic comparison of myofibroblasts derived from bone marrow and cornea (face) | text_backup | ✅ |
| CDH8 | T4 | 37507918 | Oxidative Stress and Antioxidants in Age-Related Macular Degeneration | text_primary (1) | ✅ |
| CST1 | chain | 1471486 | Immunofluorescence localization of cystatins in human lacrimal gland…（kb 泪腺条自引，题录语义一致） | chain (+2029847 双链) | ✅ |
| CST4 | chain | 37894795 | Meibomian Gland Dysfunction…Cystatin-SN（kb 泪腺条自引 OA 全文） | chain | ✅ |
| FCER1G | T4 | 40098930 | Nanosecond laser…retinal pigment epithelium (retina) | text_primary (1) | ✅ |
| GPR143 | T1 | 28339057 | GPR143 mutations in Chinese patients with ocular albinism type 1 | text_primary (51) | ✅ |
| GRM5 | T4 | 40171795 | Circadian clock disruption promotes retinal photoreceptor degeneration | text_primary (1) | ✅ |
| MUC7 | chain | 17399701 | Assay of mucins in human tear fluid（kb 泪腺条自引） | chain ∧ text(3) | ✅ |
| PTPRK | T4 | 40520173 | Modified ZhuJing pill protects retinal pigment epithelium… | text_primary (1) | ✅ |
| SAMSN1 | T3 | 33326016 | Candidate Genetic Modifiers for RPGR Retinal Degeneration（摘要含 SAMSN1） | text_primary (10) | ✅ |
| — | 替补已下载未顶岗 | 2029847/26061757/34380881/34702879/34847148/37707836/39195219 | （7 篇 backup 槽，全部入语料） | — | 副产品兑现 **CPNE5**（CDH8 替补文 34847148=Copine-4 论文正文提及） |

## 诚实 none（6 基因维持缺口，三条件+可兑现无合格候选，不移动球门）
ATP8B4(眼命中19) · FAM135A(10) · FBXL7(20) · LMOD1(12) · LRRTM3(16) · SHISA6(15)
—— 全部为 symbol/别名不现于任何眼语境标题、摘要亦无 token 的稀有标记基因；RAGGAP R3 型固有稀缺在本轮二次实证。

## 范围外维持
- 备选 104 表 8 单元中的 7（C8ORF76/COL19A1/FAM107B/SLC24A3/SSR4/XCR1/ZNF804B）：PI 批不批备选面是另一决策，本卡不碰
- LILRB2：撤证设计缺口，诚实留空
- 物种注记 (ra_fetch 同源正则实测, 如实入库透传不假装人源): human=1471486/2029847/17399701/37894795/28339057/26061757/33028893/39195219/34702879 · both=40098930/40171795/34847148 · mouse=40520173/37707836 · other=37507918/33326016/34380881 (EPMC 人限定检索下的题录级混标)
