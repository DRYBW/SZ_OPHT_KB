# KBX_VERDICT — 泪腺词条疗效首考终判（2026-09-28，卡 t_0fb07fd6）

**结论先行：本考按预注册 §8 降档条款触发 O3——合格锚定簇=1（线=8），零票发出（配额 0/120，未动）。
疗效数字（P1/P2）不存在；三词条注册资格判定=不可判（考卷无效 ≠ 词条判负）。
泪腺定量首考挂"待新数据/待参考系升级"账。**

- 判据件：KBX_PREREG_v2.md（sha d00180676a937c18…，先于建卷冻结；ledgers/KBX_PREREG_SHA.txt 复验 OK）
- 裁定件：KBX_RULING_1.md（O2 主档；合格锚定簇<8 自动降 O3）；外部预审：REVIEWER_LLM REVISE_FIRST 全裁定已并入（REVIEWER_LLM/A_KBX_PREREG2_REPLY.cycle1_preserved.md）
- 票规声明：本 run 预注册声明 **v2/C2b**（义务已履行于判据件；**实际首个 C2b 投票 run 未成行**——无票，如实记）

## 1. 为什么 O3：三层根因（各自有独立证据）

**① 真值系覆盖缺口（决定性）**。外部文献 Tier1 严格语境门（人×lacrimal gland×细胞类型/marker 语义，
泪囊/泪道/纯疾病蛋白语境排除；MIN_T1=3）终判七群仅 **DUCT(6)/MYOEPITH(5)/IMMUNE(3) 可用**；
ACINAR(2)/ENDO(0)/NEUROGLIA(2)/STROMA(2)=panel_unavailable（ledgers/KBX_PANEL_FINAL.tsv + eurpmc2/ 逐查询原始返回）。
上皮身份基因（KRT19/KRT7/CFTR/KRT8/KRT18、PRSS1/CTRB1/STATH/PRB2-3、PECAM1/CDH5、PLP1/S100B、DCN/LUM…）
在"基因级×泪腺"题名/摘要共现层系统性缺文献——**检索层空白，不是这些基因不是 marker，更不是词条错**。
后果：12 个组织池簇的 DUCT 检测一致性分最高仅 0.393（门槛 0.7），仅 TIS::10（87 细胞，IMMUNE 分 0.770、
首二次比 0.77/0.118）过门——单簇合格锚定，前置条件（≥8 ∧ 最大群≤40%）双双不满足。

**② 平台/数据缺口**。腺泡酶原程序独立复算再证不可检出：PRSS1 全簇 det=0.000、CTRB1≤0.006、PNLIP≈0
（out/kbx_o3_topology.tsv；与 Phase-0 取证 PRSS1 2.3/CTRB1 6.1 CPM 一致）。分选悬液不载腺泡+SORT-seq 板法——
即便 oracle 也无法命名腺泡（RULING 预判成立）。

**③ 词条侧：本考未产出任何"词条错"的证据，也未产出"词条对"的证据**（P1/P2 未发）。
O3 定性拓扑（不构成疗效数字）如实观察：
- secretory 词条 6 core 中 **LACRT 在全部上皮簇 0.885-1.000 且免疫簇 TIS::10 亦 0.793**——广谱泛亮，
  与 KB8 ambient 警示（板级本底 1.5-5k CPM）同型；CST1/CST4/SCGB2A1 仅在 TIS::9（75 细胞）达 0.8 级
  ——词条 core 的鉴别域集中且窄。
- duct 词条单基因 core **PRR27 无主导表达域**（最高 0.500@TIS::4/TIS::7，散在 0.03-0.45）——
  与该基因文献薄（KB8 缺口清单#2）相互印证的方向性观察。
- myoepithelial 警示条 core=[] 无展示通道（§10.5 先验披露），拓扑不可判。
- 敏感性网格：res=0.8/1.2 均=1 合格锚定（与主档一致，非分辨率伪影）；类器官池附录 0 锚定
  （其 DUCT 分 0.10-0.40 亦不达门——体外导管样程序同样无法被文献 Tier1 面板命名）。

## 2. 三门状态（全部如实：未发）

| 门 | 线 | 本 run | 状态 |
|---|---|---|---|
| P1 命中 | ≥60%（CP 精确 CI 并报） | — | **未发（O3）** |
| P2 词条污染 | ≤1 | — | **未发（O3）** |
| P3 归因表 | 逐簇 | out/kbx_cluster_table_raw.tsv（12+8 簇×全档分数）+ 本文 §1 | **已交付（附列归因=cons<0.7 → 真值系覆盖缺口；无 abstention/词条误导可归因，因无票）** |

多数类地板/构成：分母=1 时 max_share=1.000（退化）——正是 §3.6 前置条件拦截的情形。

## 3. 注册资格判定建议（A3 红线维持：不执行任何注册/接线/激活）

**判定=不可判（数据+参考系双重不足），非驳回三词条。** 升级条件清单（任一路径落地即可重考）：
- U1 参考系升强层：对 OA 全文做段级 marker 语义核验（gene×cell-type-context 共段）重建 Tier1——
  需单独预注册（本卡已按"一次完整冻结前重跑"执行，不再动面板=球门已落纸）。
- U2 作者标签原表（O1 路线）：Cell Stem Cell 2021 非 OA，18 簇映射需向作者/期刊索取；到手即可真值换源重考。
- U3 新数据：任何带逐细胞类型注释的人泪腺新图谱（含腺泡/内皮/神经深度）；数据获取须先列缺口清单报 PI 批准（下载审批铁律）。
- U4 词表侧：肌上皮空 core 词条在任何重考中仍无展示通道，判定应只针对 secretory/duct 两条（PREREG §10.5 继承）。

## 4. 过程与红线自证

- 领地：全部产物只落 /mnt/D/EyeKB/plans/kbx_lacrimal_20260928/（本卡目录清单：ledgers/eurpmc 88 件 v1 干跑 +
  ledgers/eurpmc2 全量分层原始返回、面板两表、PREREG sha、锚计数、票量记录；out/ 逐簇表、泄漏表、crosswalk、
  O3 拓扑、判分实现自测件；scripts/ kbx_p1/p1b/p1c/p2/p3/p3b/p4/p5/p6；REVIEWER_LLM/ 送审往返）。
- 上游只读：ledgers/SHA_UPSTREAM_PRE.txt 8 件 → 执行后 SHA_UPSTREAM_POST.txt **8/8 OK 零漂移**。
- 零数据下载（仅 EuropePMC REST 元数据检索，逐请求原始返回落盘）；零 kb/mcp/evalset 写；零激活。
- 票配额：**0 票发出/120**（O3 分支禁票，通道未消耗；冒烟探针亦未发）。
- C2b 参考实现派生件（kbx_p5_verdict.py）自测 4/4 PASS 已在盘，供下一 run 直接复用（未跑真票）。

## 5. 遗留与登记（不臆做，交协调）

1. KB9 登记件 §3"参考系=KB8 自建聚类"口径与本卡结论不冲突（本卡证明的是外部文献系在此数据不可建卷，
   非该口径错误）——建议 KB 台账把"泪腺首考=O3 挂账"登记为现行状态。
2. REVIEWER_LLM 一函（REVISE_FIRST）全部 13 条实质缺陷修复情况=PREREG 定稿 §1-§10 逐条对应；其 Q8#1"语境门把参考群排空
   会把检索失败误判生物学阴性"**本轮再次应验并被 §1① 如实归因拦住**——此教训应进 KB 考卷设计先例库。
3. LACRT 免疫簇广亮（本卡 O3 新观察）是对 secretory 词条特异性的**方向性预警**（非判负）：
   重考时建议把"LACRT ambient 阳性判读线"从 KB8 data_note 升级为判读面可见旗标（属下一 PREREG 球门设计，本卡不动）。
