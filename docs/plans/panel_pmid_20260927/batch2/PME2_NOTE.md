# PME2_NOTE — 面板证据链补录第二批收官（t_95cbb3ec，2026-09-27）

> **口径头（PI 锁定，D7）**："expressed in <该细胞类型>" 算 membership 型支持 = **中等档，现行正式口径**。
> 类特异严格档不再议为默认；若未来收紧须全库对称重判并另卡。放行件：USER_DIRECTIVE_20260927_scoring_wave.md 追加一 D7。

## 一句话结论
103 个非 strong 键（50 weak + 53 none）过第二检索式（UniProt 基因别名表全类对称 + 类同义词扩展 + sort=CITED desc 二遍）后，
**20 键升 strong（16 weak→strong + 4 none→strong）、5 键 none→weak**；E2 定性的 338 行"无记录文献先验"两批合计
**strong 250/338（74.0%）**，对照 E2 567 对基账本，**两批合计可核链 = 30+250 = 280/567（49.38%）**；
残余 44 none 键诚实登记（4 键四遍零候选=真缺文献，40 键=摘要级不可核）。**E2 任何数字未改，kb/ 与面板字节未动。**

## 终态账
| 层 | strong | weak | none |
|---|---|---|---|
| 本批 103 键增量 | **+20** | +16（净） | **−36 → 44** |
| 键账 280（两批终态） | **197** | 39 | 44 |
| 行账 338（两批终态） | **250（73.96%）** | 44 | 44 |
| v4.1 八类教科书锚（40） | **34/40**（一批 29/40；AC 1→3、HC 2→3、BC 3→4、MG 3→4） | — | — |

- 救回 20 键（逐键证据句+PMID 全列 out/pme2_accounts.tsv，transition=RESCUED）：
  AC/GAD2(28456934) AC/GRIK2(7952290) AC/SLC6A9(40417401) BC/GRIK1(12508320) BC/GRM5(16638174) BC/GRM7(17553999)
  BC/ISL1(18003851/17480014) Endo_Patho/DLL4(16219802) Granulocyte/FCGR3B(41967397) HC/GAD1(34209226) MG/GLUL(10908613)
  Mono_Classical/SELL(39281780) NK/KLRF1(36583228) NK/NKG7(42682208) Pericyte/CALD1(33060592) Proliferating/NUSAP1(40605080)
  SMC/DES(42638206/42074233) SMC/LMOD1(37601452) SMC/MYL9(40980809) cDC2/FCER1A(27837108)
  ——一批预言的符号欠证目标全部兑现（GLUL=glutamine synthetase、SELL=L-selectin、FCGR3B=CD16b、CALD1=Caldesmon、
  LMOD1=leiomodin-1、GAD1/GAD2=GAD67/65、GRIK1/2=GluR5/6、SLC6A9=GlyT1、KLRF1、THY1…）。
- none→weak 5 键（文档级共现新证，未达句级三条件）：AC/TFAP2A、APC_MHCII_high/FCGR1A、BC/TACR3、Mono_Classical/FCN1、Mono_Classical/SERPINA1。
- 残余 44 none **两态定性**：
  - **真缺文献（四遍零候选）4 键**：BC/COL19A1、BC/HS3ST4、BC/TMEM132C、BC/TMEM196——全为 v6 repair 统计派生基因，
    外部文献连基因∧类词汇组合都未出现，与 E2 定性一致。
  - **摘要级不可核 40 键**：检索有候选但无句/文档级 G∧C 共现（v6 sc-atlas 派生如 EYA4/SHISA6/SPHKAP/VAT1L/NAALAD2/GABRG1/
    ONECUT3、单细胞图谱断言多藏于图注/extended data，摘要级不承载）；**均维持诚实阴性，禁软证据升档未破例**。

## ⚠ 取证连带发现：一批 A1"双遍"实际从未执行（已修，二批起生效）
- 一键冒烟发现 `&sort=CITED`（裸形）被 EBI 全线 **503**；官方正确格式 `sort=CITED desc`（或 query 后缀 sort_cited:y）。
- 回查一批 ledgers/raw/：**84/84 个触发二遍的键 raw2 全 null（error2=503）——第一批账实为单遍 relevance 口径**（其数字不改，
  登记于此供口径修订引用）。二批以修正格式实跑，**CITED 遍 75/75 生效**（本批二遍触发键零失败），是本批救回量的重要通道。
- 修正先于跑数落纸：PME2_PREREG_v1.md 补记 A1'（ledgers/sha_prereg.txt 双哈希：原稿 + 补记版）。

## 方法与留痕
- 预注册 batch2/PME2_PREREG_v1.md 先于任何检索；别名表构建=UniProt human+reviewed 单端点同参数全 103 基因统一施加
  （data/alias_gene_v2.tsv：538 候选→留 481，弃 57，F1-F5 理由全登记；101/103 基因有别名；raw 全留 ledgers/raw_uniprot/）。
- 类扩展表全 29 类对称列出（含"—"类）；marker 词表 M 一字未改；分级规则与一批 §4 完全同构。
- worker 自审（零 LLM 判读）：35 条引擎 strong 证据句**全部过目**（ledgers/strong_selfaudit_v2.tsv），
  双槽核查后 **15 键降 strong→weak**（ledgers/audit_fixes_v2.tsv 逐条留痕不掩 raw）：
  机制句（TFAP2A/OTX2/TPM1/BIRC5/H2AFZ/TYROBP/CALD1 案外等）、归属错误（CD36=Kupffer、THY1=MSC、CCL3=MDM、CD4=T 细胞、
  ZBTB46=pan-DC、S100B=星形且句中 MG 阴性）、类词循环（ECSCR 类词由自身全名展开注入、TRAC 类词来自"T-cell receptor"基因名
  ——一批 A5 HLA 案镜像）。救回键中 ISL1/DES 靠 slot2 合格归属句维持 strong（与一批"双证据槽"审法一致）。
- 逐键双遍原始返回全留 ledgers/raw2/（103 文件，含两 URL+别名清单）；键账 out/pme2_accounts.tsv、
  行账 out/pme_rows338_combined.tsv、sidecar out/evidence_chain_supplement_v2.json（旁挂，v1 与 kb/ 面板零触碰）。

## 两批合计可核链覆盖·最终读数（供未来评测口径修订引用；E2 数字零改动）
- E2 基账（567 对）：文件内可核 30 / 纯内部派生 199 / 无记录先验 338。
- 两批合计 strong 行 = 250 → **可核链对 = 30+250 = 280/567 = 49.38%**（一批后为 252/567=44.44%；E2 原始基线 30/567=5.3%）。
- S1 弃权面线性预估同式更新：17.35pp × 250/338 ≈ **12.83pp** 可收敛（结构估计，未重跑 E2 打分；一批预估 11.40pp）。

## 红线遵守
- 只写 batch2/；kb/、mcp_server/、E1/E2/E2R/E3 目录、**一批全部原件**：PRE 81 条 sha vs POST **全一致**（ledgers/sha_pre.txt / sha_post.txt）。
- 零 LLM 判读、零全文下载（仅摘要级 API JSON）、**pmid_context 共现通道零使用**（E2R 告诫继承）。
- 一批 sidecar/引擎/账件仅以 in_b1_snapshot/ 只读副本复用（快照 sha 与原件逐一核对同值）。

## 已知局限（如实登记）
1. 中等档口径下 "expressed in <class>" 即算支持；若 PI 未来采类特异严格档，本批 20 救回中 GLUL/SELL/KLRF1 等强句仍稳，
   但 membership 型（如 CALD1 hPSC 衍生体系、NUSAP1 泛增殖语境）须重判——对称性风险同批1 已知局限 2。
2. 别名表源=UniProt human+reviewed；未收录的惯用名（如抗体克隆号、旧文献独占俗名）仍欠证。
3. "摘要级不可核"≠"外部文献不存在"（40 键）；升级路径=全文级断言提取（本卡禁全文下载，不执行）。
4. CALD1 证据句来自 hPSC 分化周细胞样体系（非在体视网膜），中等档下按 membership 接受，严格档下应复核。
