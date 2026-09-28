# KBGOV_CANDIDATE — query_marker 跨物种 ranking 治理候选（库侧拆弹，D14）

- 卡：t_ea865be1 ｜ 判据件：KBGOV_PREREG_v1.0.md（sha 33119b7d，落纸先于复刻跑数/G0）→ v1.1（sha 84d05d38，跑数前输入装配修正：canonical 列=top_genes_sym，球门零改动）
- 性质：**候选设计 + 离线证据层机械 A/B（零 LLM、零网络、零生产写）**。eyekb_core.py/server.py/kb/ 本卡零写入（sha 在 ledgers/；跑数窗口生产文件被并发实写一事如实见 §5，本卡复刻输入未受影响并有活体复验）。禁 import 生产码——ranking 逻辑实验侧独立复刻，对服务端 calllog 留痕逐行验证等价。

## 一句话结论

**五变体矩阵里，B5（confirmed+suspected 鼠源输入一律拒答具名 + AMBIG 共表达证据仅标注不删序）与 B4（仅 confirmed 拒答）、B1（纯标注）三个非破坏人源侧的组合过双门（病灶清零或物种化 ∧ 回归 230 人源簇零位移）；含 G3-removal 的破坏性变体 B2/B3 以 14.78%（34/230）位移触发预注册过杀线（>5%）回炉。主候选=B5。V-b"条件具名"被机械证据否决：1:1 ortholog 回证在 Q7::21 案实证"保护假 AC、杀掉真 BC"。**

## §1 复现与基线锚定（证据地基）

1. **G0 复刻验证门 = PASS（两次）**：对 calls_2026-09-26/27.jsonl 中 `query_marker × mode=genes × library=all × act_v6_on=true` 行（首跑 **329 行**，含 btest_d9 325 行=席位真实查询流量；21:5x 复跑 **331 行**——新增 2 行为 KB9 接线后活体流量，复跑同样 mismatch=0），复刻件 ranking 类序 vs 留痕 `ranking_classes_top`+`n_ranking` **逐行零差异**（ledgers/kbgov_replica_vs_calllog.tsv）。复刻语义：库装载序 retina→membrane→ri→retina_v6→face_v6、upper 冲突 `库::类` 别名、n_shared 降序稳定排序、重复基因双计——与生产实现逐点对照（只读）。复跑含接线后流量仍零差异 = 现库（活体）行为=复刻件的双重实证。
2. **A 基线（现库响应）病灶锚定 PASS**：
   - Q7::52（鼠池 25 基因，truth=RGC）：`[Pericyte(1|THY1), Fibroblast(1|THY1), retina_interneuron::AC(1|GRIN3A), retina_v6::AC(1|GRIN3A)]` —— BTEST §4"AC-ranking 伪影"在库侧机械复现：19/25 个鼠基因仅 2 个命中，命中的是 THY1/GRIN3A 型大小写碰撞单基因，AC 双行具名在列而真类 RGC 无踪迹。
   - Q2::22（人源 20 基因，truth=Astro）：`top1=MG(2|GLUL,VIM)` —— RUN7RG §6 共表达误导复现（CLU 不在任何现役面板，AMBIG 三支其一为惰性锚，如实登记）。
   - 席位原始入参（toolcalls run1 A/B/C 含大小写/增删变体）全部被 G0 覆盖复核，保真列=329 行对账本身。

## §2 治理规则文本（可原样装进 eyekb_core 的粒度）

### G1 输入物种判定层（query_marker genes-mode 入口，排序前）
```
输入: gl = [g.strip().upper() for g in genes]（原形另存 raw_genes 供惯例信号）
词表(离线构建, sha 锚定): HUMSYM = NCBI human gene_info Symbol∪Synonyms(upper)
                         MOUSYM = Ensembl mouse GTF gene_name(原形∪upper)
                         ORTH11 = human→mouse 1:1 symbol 表(冻结件 12,313 对)
信号: title_frac = |raw 中 ^[A-Z][a-z] 且非全大写| / |字母基因|
      msp_hits   = |raw 匹配 ^Gm\d+$ 或 .*Rik$|
      m_only     = |upper ∉HUMSYM ∧ ∈MOUSYM|
判定(冻结): T = 0.4  # 校准=data/kbgov_g1_calibration.json（人源 231 簇 title_frac max=0.0，
            # 鼠源 59 簇 min=0.8，间隙 0.8 取中点；human_misdetections=[]）
  mouse_confirmed  ⇔ title_frac≥T ∧ (msp_hits≥1 ∨ m_only≥1)
  mouse_suspected  ⇔ title_frac≥T ∧ 无佐证
  human_assumed    ⇔ 其余
```

### G2 跨物种 ranking 过滤（人面板对鼠源输入的具名条件——FACEV21 撤行 (b) 的库侧化）
```
mouse_confirmed → 具名排名清空，celltype_ranking 条目全量转 unranked_candidates，
  resp 顶层加 no_named_ranking_for='mouse_input' + species_evidence(msp/m_only 样例)
mouse_suspected → 同 V-c（主候选 B5 口径；保守备胎 B4 口径=suspected 仅标注不拒答）
凡 confirmed/suspected 输出（B1/B4 保留条目时）逐条带 cross_species_hit=true
```
**V-b"条件具名"（n_shared≥2 ∧ 共享基因全部 ORTH11 回证 ∧ ⊄AMBIG）——证据层实测否决**：Q7::15/21/22 假 AC 经 CNTN5/TMEM132D/SPHKAP 全过 1:1 回证照样具名（B2 下 Q7::15 "partial:retina_interneuron::AC" 保留伪影顶位），而 Q7::21 真 BC 因 ADARB2 不在人侧词表被回证误杀。**跨物种具名资格不是靠 ortholog 回证能补的洞——面板内容与人鼠类间混淆（AC↔BC/AC↔HC）与 orthology 正交。**

### G3 假命中防线（共表达歧义；只管证据具名资格，grade 归 D16/GRADE 卡）
```
AMBIG = {GLUL, VIM, CLU}   # 冻结锚集(BTEST §4/RUN7RG §6 点名；不用面板出现率自扩——
                           # 预演显示 ISL1/GAD1/S100B 等正当谱系共享 marker 同现率高，自扩=过杀放大器)
触发: 条目 shared_genes ⊆ AMBIG ∧ n_shared≥1
动作(主候选=标注档): 条目加 no_naming_claim=true + reason='ambiguous_coexpression_only'，
  排序与条目保留不动（消费方协议：判读席禁以 flagged 条目作 identity 定名依据）
动作(被回炉的删除档): 移出具名排名 —— 回归位移 34/230=14.78%>5%，判过杀，不采
```

## §3 证据层 A/B 结果（五变体矩阵，PREREG §5 机械执行）

### 3.1 门汇总（out/kbgov_gates_final.json）
| 变体 | 组合 | 鼠源 7 病灶 | Q2::22 | 回归 230 位移 | 门(>5%回炉) | 入围 |
|---|---|---|---|---|---|---|
| B1 | G1 标注 + G3 flag | 7/7 显式物种化 | flagged | **0 = 0.0%** | PASS | ✓（最弱干预） |
| B2 | V-b 降级 + G3 removal | 4 cleared/3 annotated | removed→Astro 顶正 | 34 = **14.78%** | **FAIL** | ✗（双轴落选） |
| B3 | V-c(confirmed) + G3 removal | 6 cleared/1 annotated | removed→Astro 顶正 | 34 = **14.78%** | **FAIL** | ✗ |
| B4 | V-c(confirmed) + G3 flag | 6 cleared/Q7::11 annotated | flagged | **0 = 0.0%** | PASS | ✓（保守备胎） |
| **B5** | **V-c(confirmed+suspected) + G3 flag** | **7/7 cleared** | flagged | **0 = 0.0%** | PASS | **✓ 主候选** |

### 3.2 病灶逐簇判词（out/kbgov_lesion_verdicts.tsv；refused/removed/kept_flagged=清零档，kept_annotated=物种化档）
- Q7::52/58/61：B2-B5 全 refused/removed；A 伪影（THY1/GRIN3A 单基因碰撞具名 Pericyte/Fibroblast/AC）在 B5 下零具名残留。
- Q7::15/21/22（truth=BC）：B3/B4/B5 refused；B2 保留假 AC（V-b 漏网实证）。
- Q7::11（鼠源，仅大小写惯例证据=suspected 档）：只有 B5 清零（removed）；B1-B4 = annotated。此簇是 confirmed/suspected 分档的判据所在——B4 与 B5 的全部差异就是这 27/59 个"纯惯例簇"要不要拒答。
- Q2::22：所有入围变体下 MG/ri::MG `no_naming_claim` 标记（具名资格剥夺、序不动）；B2/B3 删除档下 top1 变 Astro=truth。
- Q5b::35（登记不判，grade 案归 D16）：**五变体全 kept_bare、零位移** —— KBGOV 规则不触碰其 A 响应的实证 = GRADE/本卡分工边界成立。

### 3.3 过杀账（out/kbgov_overkill_ledger.json；破坏档回炉的量化理由）
- B2/B3 位移 34 簇 = **top1 位移 12 + 仅中位删条目 22**。top1 位移中 **正确名伤亡 7 簇**（Q2::0、Q3::10、Q4::13、Q4::20、Q4::35、Q4::36、Q4::37——truth==A top1（多为 MG/Astro 胶质类），但其命中证据恰为 {GLUL,VIM} 纯歧义集：删除档把"答案对、证据弱"的具名一并杀掉）。
- 标注档（B1/B4/B5）同样命中这 7 簇的 no_naming_claim（flag-casualty 3.0%）——**证据确实歧义，不因 truth 巧合而豁免**；条目保留 + 席位的定名纪律由判读协议承接（与 GRADE 卡衔接点在实装书 §3）。
- 位移 34 簇逐条含 A/B 序、removed、触发规则、truth 见 out/kbgov_regression_shift.tsv（variant 列 B2/B3 各 34 行，全 trigger=G3_removal——G1 在人源侧零误判，位移全部由删除档 G3 造成；V-c 对回归门无贡献性伤害的证据）。
- 鼠侧账（不入门）：B5 下 59/59 鼠源簇具名清零（FACEV21 (b) 撤行的库侧等价物）；B4=32（confirmed）；B2=28。

### 3.4 关键机制读数（写给 PI 的三条）
1. **BTEST 回流病灶可库侧清零**：自由查询臂绕开卡片拆弹的路径，在 query_marker 入口按 G1 判定拦截后，A 的 AC/Pericyte/Fibroblast 伪影在鼠源输入上清零且人源回归零位移——"修复须下沉到共享层"（BTEST §7.2 推论）从假设变成对账表。
2. **suspected 档是真实边界不是工程瑕疵**：27/59 鼠源簇无任何鼠独有符号/模式证据（Q7::11 案），判定只剩 MGI 大小写惯例。B5 采惯例拒答的依据=本数据 231 人源簇惯例全大写（misdetections=0）；**泛化限制**：真人源数据若以 title-case 上送将被误拒——实装必须带降级开关（见 §4）与逐例误判台账。
3. **两个病灶家族不属本卡管辖（防越界扩张）**：Q3::11/Q4::8（人源 ONECUT2 单基因入 AC=v4.1 AC 面板内容错位）归面板内容修复线（KB5-v3 口径）；Q5b::35（grade 漂移）归 D16。本卡未为过病灶扩 AMBIG——扩集=过杀放大器已在预演中实证。

## §4 实装申请书草案（三段式，全部待 PI，本卡零接线）

**段一 注册**：规则件（G1/G2/G3 文本+校准件+词表构建件）+ 验证账（本文 §1/§3 全表）+ 冻结判据（PREREG v1.1 sha）入注册线，走 KB9 型注册包流程；词表/ORTH11 三件源 sha 全锚定（HUMSYM=gene_info、MOUSYM=GTF、ORTH11=12,313 对，OcularKB 本地件路径在台账）。
**段二 OFF 态接线**：eyekb_core.query_marker 加治理分支（genes-mode 排序前 G1 判定→按 B5 输出 `input_species`/`no_named_ranking_for`/`no_naming_claim` 字段），env `EYEKB_ACT_KBGOV=0|false|off|no` 默认 OFF；OFF 态规范序列化与 pre 基线全等的等价证明照抄 t_5d5853c9 激活纪律（329 行 G0 对账件即 pre 证据）。响应体积上界：unranked_candidates 全量转列，估 <2× 现响应。
**段三 激活另批**：激活判据=①B5 病灶清零/物种化 8/8 ②回归 230 零位移 ③鼠侧 59 全拒无具名残留 ④误判台账空（对 new 人源 title-case 上送样本逐例登记后复核）。激活后一周观察窗（calllog tag 隔离）复核 suspected 拒答的真实误拒率；若误拒>0 即回退 B4 口径（confirmed 拒答+suspected 标注），回退开关 env 粒度=同接线不分叉。**席位消费协议连带项**：ANNOTATION_PROTOCOL 需加一行"no_naming_claim/cross_species_hit 条目禁作 identity 定名依据"（与 GRADE 卡 H1 判序锚衔接，归 PI 排批）。
**限制清单（随申请书呈报）**：①suspected=惯例单证据档，泛化边界见 §3.4-2；②AMBIG 三支中 CLU 不在任何现役面板（惰性锚，保留待面板补 CLU 生效）；③G1 不处理细胞类型名查询（cell_type-mode 的 'AC'/'RGC' 类名检索路径不在本卡射程——BTEST 席位转查类名的第二跳由 G1 拒答后自然消解：鼠基因首查已无具名可误导）；④ensembl ID 形态输入（ENSG）按词表 miss→human_assumed 处理，本数据无碍；⑤Q5b::35/Q3::11 型病灶的管辖归属见 §3.4-3。

## §5 红线合规与产物

零 LLM、零网络、零生产写：本卡 37 件只读输入 POST 复核 **34 件逐字节全等**；3 件不一致（`eyekb_core.py`、`server.py`、`calls_2026-09-27.jsonl`）**非本卡所写**——并发实写与行为不变实证见下段。禁 import 生产码（G0 以 calllog 留痕对账替代）。
**跑数窗口并发变更实录（如实，非本卡所写）**：21:12/21:13 `eyekb_core.py/server.py` 被 KB9 案 B 接线卡（t_4bb75b26，PI D17，k9_ocs 库**默认 OFF 不入 all**）修改，kb/markers 新增两枚 k9 件；本卡复刻所用 5 枚面板文件 sha 与 PRE 台账逐字节全等，活体 library=all 行为不变有双重实证——①装载名单源码行（k9_ocs 不入 `all`/`V6_DEFAULT_LIBS`）②G0 复跑 331 行含接线后 21:21/21:22 两条 genes-mode 活体流量仍 mismatch=0。本卡证据层对新旧态同样成立；若实装段二接线与本候选同期落地，须按 t_5d5853c9 等价纪律重跑各自 pre 对账（互不继承）。
**变体矩阵增补纪律**：B4/B5 系 BRIEF"可组合"条款下、观察 B2/B3 实测失效模式后新增的组合档（判据门/球门零改动，PREREG §3 三档响应原文已含 V-a/V-b/V-c 形态）；B1-B3 结果经五变体重跑逐值复现（确定性脚本）。修复过一处纯序列化 bug（B4/B5 flags 列未写出），修复只影响记账列不影响任何排序数值，修复前后 shift/casualty/门判定全等。
产物：本文 + KBGOV_PREREG_v1.0/1.1.md(.sha256) + scripts/{kbgov_replica,kbgov_g0_verify,kbgov_vocab_calib,kbgov_calib2,kbgov_ab,kbgov_verdicts}.py + data/{kbgov_vocab.json.gz,kbgov_vocab_stats.json,kbgov_g1_calibration(.v1.0-col).json,kbgov_g1_signals_290.json,kbgov_lesion_signals.json,kbgov_ab_lesion.tsv} + out/{kbgov_lesion_verdicts.tsv,kbgov_regression_shift.tsv,kbgov_mouse_side.tsv,kbgov_ab_metrics.json,kbgov_overkill_ledger.json,kbgov_gates_final.json} + ledgers/{INPUT_SHA_PRE,INPUT_SHA_POST,kbgov_replica_vs_calllog.tsv} + logs/{vocab_calib,kbgov_ab,kbgov_verdicts}.log。

*KBGOV_CANDIDATE v1.0（2026-09-27 夜，卡 t_ea865be1）。实装与否、B5/B4 取舍、消费协议连带项——归 PI。*
