# 打分线与后续迭代实录（2026-09-27/28，EyeKB）

## 迭代与卡号索引（产物路径均 /mnt/D/EyeKB/plans/）
- E1 证据入打分对照 t_a7515c0b → evidence_scoring_20260926/E1_VERDICT.md（+§9 PI 终裁"不是代替是辅助"）
- E2 去同源重测 t_35d45b74 → e2_decontam_20260926/E2_VERDICT.md（W2 生效：干净 Δ+7.66pp vs 共识/−6.63 vs 最强单席否决列/旗标无工作点）
- E3 弃权回捞正式化 t_7b5a5fb3 → e3_rescue_20260927/（R1 PASS 85.42% 限视网膜/R2 体量 FAIL/R3 双层 SOP）+ AUDIT_SOP_v1.0.md（PI 09-27 定稿，零接线）
- E2R S5 口径完成 t_dc954503 → e2r_s5audit_20260927/（120 对 pmid_context：0 虚构、83.3% 可核、79% 题名离题→"不特异不认"结案；三口径水分表 raw/S1/S5b/S5b_rel/S5；**KB 存储缺陷：pmid_context 从不存 PMID 字段、20/120 空题、YYYY: 前缀混存、题名 120 字符截断**）
- BTEST 自由查询 A/B t_fb660dfe → btest_20260927/（判定 B 不达：R2 破 2/23=Q7::52/58 库侧伪影经工具路径回流，卡片层拆弹不覆盖工具路径；成本 82× prompt tokens；C2b 并列读 R1 20/22 但 R2 恒破=伤害属取证方式非票规；稳定性门 2 跑 97.8%；席位一致率梯度 44/39/31——deepseek 席为方差主源）
- TIEP 票规反事实 t_b7c201f4 → tiep_20260927/（tie 九成系 tie@1 单有效票，真并列四面仅 1 例；C2b=29/33 过 KB9 门零翻案；RUN5 旧面越 P2 门故向前生效）→ WIKI/PROTOCOL_VOTING_v2_C2b.md
- KB9 建条+复核+注册 t_6df5b739 / KB9R 复核 t_33162166 / KB9REG 注册包 t_6d226765 → kb9_ocs_20260927/（自检 P1 22/33 FAIL 差 2、P2 接管清零 PASS、不注册；REVIEWER_LLM 五轮外审链 R2-R5 终态 ACCEPTED=案 B 四词条+R1/R2/R3 规则+装配规则 v2，"注册≠激活"，激活前义务清单 §10-6；开发集定位声明=标签派生规则的效果只能算工程验收非独立验证）
- KB9REGEXEC t_4bb75b26 → 装条进 kb/markers/ **旁挂 overlay 默认 OFF**（k9.0-ocs-registered-v1+惰性规则件，baseline 110 件字节零变更，服务 0.4-actv6→0.5-k9reg，42-probe 改前后全等、GOLDEN41 双态 41/41、KB2C 33/33）
- RAGGAP t_922cdfa0 → rag_gap_20260928/（1074 词条行×RAG v2.1 覆盖矩阵；A 档 92 基因/65 必补+104 备选 ≤85MB、B 档文献固有稀缺登记、C 档 77% 只缺索引旁挂可解；LILRB2 误引发现）
- RAGFIX t_d0bea5a6 → rag_fix_20260928/（v2.4=230,426 chunks/+9,772、13.9MB 实耗；C 档 830 行旁挂 INERT；门①41/41+门②8/10 PASS、门③ 67/92=72.8% FAIL 残差三分=16 从未配文+8 仅备选+1 撤证留空；抽 20 既有链=6 确诊误引 30% 模式 eutils PMID 错位；REVIEWER_LLM xhigh 独立裁=卡级 FAIL+建议 B 追加轮；执行脚本 block 待裁 P1/P2/P3，项目维护方按 PI"能跑就跑"落 D20-D22 解停）
- KBCHAIN t_3a35a2cc / RAGFIX2 t_6848d3de / RETRAIN t_ed4a3c52（改进波二：全链误引分层审计只取证/16 基因白名单 v2.4.1/重训四对象只读冲击评估）
- KBX 泪腺首考 t_0fb07fd6 → kbx_lacrimal_20260928/（Phase-0 取证推翻任务书真值前提→KBX_RULING_1 裁 O2 外部参考系→仅 3 群可用+锚定簇 1<8→预注册降档 O3 零票收卡="考卷无效≠词条判负"）

## 关键判读层教训（BTEST 核心产出，适用一切"修复后重测"）
判读侧修复的**作用域必须声明**：卡片渲染层（撤行/判序注记/hint）≠工具路径≠库侧——B 形态失败根因=FACEV21 三拆弹全在卡片层，自由查询臂拿原始基因查库时 v6 面板 AC-ranking 伪影与 GLUL/VIM/CLU 共表达先验原样回流。治理顺序=病灶在库侧则修复必须下沉 query_marker/面板层（KBGOV B5 候选：鼠源域拒答具名+共表达只旗不删；激进删除档触过杀线 34/230 位移回炉）。

## PI 语义与协作模式（本波实证）
- 对"我的方案是不是不行"式自我否定，正确响应=层面拆分（替代路线死≠辅助路线死）+ 量化底座（弃权带 48/41）+ A/B 两案带建议，PI 落定"不是代替，是辅助"。
- "可以，该补文献的补文献，该补rag的补，该补wiki的补"类 blanket 授权仍守闸：补文献=RAGGAP 先盘点再 A 档闭集下载（≤85MB 免批线内）；补 RAG=C 档旁挂（INERT）；补 wiki=装条时逐基因 PMID+OLS 回证入条+四件套同步。激活/注册仍另卡等 PI。
- "可以，在机器上能跑"=资源放行词，照派不啰嗦；被打断的审批（如批量 create BLOCK）待用户在场原样重试即可通过（内容不变）。

## 强制关机前完成清单（PI 主动关机场景，2026-09-27 实证）
1. 各板 running/ready 扫描；2. terminal-lane/问句型 ready 卡 **block 注明原因**（防开机误拉起，dispatcher 不拉 blocked）；3. 长跑产物已落盘+sync；4. 提醒：systemd 自启的网关（default hermes-gateway）不用管，**裸进程网关（AGENT_ROLE）开机不自恢**；5. cron 类（A2 周报）依赖调度器在线，开机后核验。

## GitHub 镜像仓（DRYBW/SZ_OPHT_KB）本波状态
REPOSYNC 五分层 commit+项目维护方独立探针 commit（tests/COOPROBE 进仓）；KB9EXEC 六 commit push 前 执行脚本 守"停手报项目维护方"，项目维护方从远端全新 clone 实测（起服/黄金式查询/ON-OFF 判别 face_v6::行/泪腺零泄漏/kb 100 件 sha 全等）后才 push。Release v2.3 六件收齐；v2.4 语料是否升 Release=同步卡评估单独报。判读层收录口径：md/json/tsv 全进，>5MB 面件走 README 附录再生产登记（170MB 两面不入库）。
