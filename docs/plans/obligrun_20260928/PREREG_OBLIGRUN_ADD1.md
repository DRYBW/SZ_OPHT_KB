# PREREG_OBLIGRUN_ADD1 — 预注册追加节（案 A 执行，票面 v2.1）

- 卡：t_c145db7c run142 ｜ 日期：2026-09-28 ｜ 依据：OBLIGRUN_RULING_1.md（协调者按 PI 追加五裁=案 A，"原地续跑"；全文 ledgers 互引）
- 本件为 PREREG_OBLIGRUN.md（sha bfd8836d1ef3b83f…）的**追加节**：原件不回改（红线沿原卡），以下条款与原预注册并生效；票规版本声明（v2 C2b）、球门（P1≥24/33、P2 strict≤1/33、any 并报）、判读矩阵、三席与参数、批次结构、红线全部**原样继承，不降不放宽**。

## A1. 票面替换（冻结件唯一变更）

- 作废面：face/EV_DIGEST_SLIM_q6_oblig.jsonl（sha ba76b6ce1af1654e…）——VERDICT_OBLIGRUN.md v1 判定的受污染面，仅作血缘对照，不作投票输入。
- 新面：**face/kb9_face_v2.1.jsonl**，sha256 **2c0649dcc2001c8b3fe485dab35761a90a4f2c297df88e7a16739e3ec23929bb**。
- 生成脚本：scripts/o5_face_v21_t_c145db7c.py；对账台账：out/FACE_V21_ledger.tsv。

## A2. 剔除规则（裁定细则 1 逐字落地：按规则不按点名）

规则=「逐簇比对 lit 行 PMID 与该簇 truth 来源论文（registry 血缘件），凡同源即剔」。
- registry 血缘件=本簇供细胞 study 的 truth 来源发表文献登记表（FACE_V21_ledger.tsv 尾部注释，9 study 标签逐条 basis：6 GSM 题名解析 + GSE155683→PMID 33865984(Collin, Ocul Surf 2021) 外部只读解析登记 + 3 个 chen_* 无 accession 残余限制沿 v1）。
- 票面 12 唯一 PMID ∩ 来源论文集 {36712326, 33865984} = {36712326}；36712326 仅随 chakravarti_GSE218123 细胞供入（含 chakravarti 细胞的簇 27 个，其中 lit 含 36712326 行的=Q6::7(12 细胞)/Q6::11(3 细胞)）。
- **机械复算命中集=恰 2 行**：{Q6::7,Endo,36712326}、{Q6::11,Endo,36712326}——与裁定预期一致（无多于、无少于；多于则全剔如实登记、少于则停卡的两个分支均未触发）。
- 剔除动作=删除该 2 条 lit 条目；两簇 Endo 键各余 34381080 一条（保留），无空键清除。

## A3. 零漂移断言（裁定细则 2：33 簇集合不变、ranking 逐字节不动）

- 序列化往返自证：33/33 行 json.dumps(loads(line), ensure_ascii=False)==原行逐字节（构建前置断言）。
- 31 未涉簇整行逐字节相等；2 变化簇除 lit 数组收缩外全字段逐字节相等（含 kb_marker_ranking——显式序列化再断言）。
- 行序=RUN5/v1 面行序（批组成快照不变：7 批 5,5,5,5,5,5,3）。

## A4. 义务与投票范围（裁定细则 3-4）

- OB-1/OB-3：结论沿 v1 run（案 A ranking 字段零动，裁定理由 3）；本追加节登记 v2.1 面与 v1 面差异=仅 2 lit 行，属 OB-1(b) 许可漂移字段（lit）内，31 簇零差异。
- OB-2：对 v2.1 机械重算（out/pre_vote_diagnostics_v21.tsv，新增 delta_vs_v1 列含 31 未涉簇零变化对照；硬断言 post_shield top3==v2.1 面 ranking 33/33 先行）。
- OB-4：对 v2.1 复筛，断言 0 残留同源命中（out/OB4_lit_screening_v21.md + OB4_lit_hits_v21.tsv）。
- 正式三席票：投票输入=v2.1 面（33 簇全量新票，零复用存档票）；票面预算**重置 ≤150**（v1 作废 run 消耗 0/150 不结转；名义 99 票；硬计数器达 150 即停止一切后续请求并 block）。
- 判读矩阵、通道（LLM_CHANNEL）、三席（A=qwen3.8-max/B=glm-5.1/C=deepseek-v3.2）、enable_thinking:false 探针流程、429/配额=block 禁换通道——全部沿原预注册 §4-§7 原文。

## A5. 领地

kb/、mcp_server/、evalset/、注册包、overlay、lit 语料、v1 面与 v1 全部产物只读；v1 VERDICT 作废留痕件不动（本 run 终局=VERDICT_OBLIGRUN_v2.md 单独成件互引）。
