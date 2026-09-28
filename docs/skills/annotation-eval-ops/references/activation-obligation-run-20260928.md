# 激活前置义务 run 实录 — 2026-09-28（OBLIGRUN / B5IMPL / H1M3 / RAGFIX3 / MOUSEEXT / REPOSYNC3）

## OBLIGRUN 两轮链（plans/obligrun_20260928/）

时间线：BRIEF（判读矩阵预注册）→ run1：OB-1 清（339 行台账，RUN5 请求确定性重渲染逐字节等价 21/21 替代未留档原文）/ OB-2 PASS（诊断表 57 行 11 列，硬断言 post_shield top3==票面 33/33）/ OB-3 清（22/22）/ **OB-4 不清→票面作废分支**→ 0 票 block。协调者 RULING_1=案 A → comment 指路 + unblock 原地续跑 → run2 全绿 done。

终局数字：**P1(C2b)=26/33**（named 28，missed 7 簇全落 Fibroblasts/Pericytes 谱系带：5 无名+2 named-but-wrong）、**P2 strict=0/33**、票预算 99/150 零缺票、三席 face_sha 一致。VERDICT_OBLIGRUN_v2.md=READY；ACTIVATION_READINESS.md=建议票（激活仍归 PI OB-5）；v1 作废留痕件不回改、互引。

关键件：PREREG_OBLIGRUN.md（sha bfd8836d）/ PREREG_OBLIGRUN_ADD1.md（案 A 追加节 sha 92c2a538）/ OBLIGRUN_RULING_1.md / face/kb9_face_v2.1.jsonl（sha 2c0649dc）/ out/FACE_V21_ledger.tsv（31 簇整行逐字节等）/ pre_vote_diagnostics_v21.tsv（delta_vs_v1 列）/ OB4_lit_screening_v21.md（0 残留）。

案 A 命中的论文三重证据配方（可复用为同源判据模板）：①论文 Data Availability 自存 GSE accession ②GEO 系列题名与论文题名逐字一致 ③评测对象 obs.study×GSM 直读细胞数吻合。chen_* 无 accession 不可解析=残余限制如实登记（获权威映射须重跑筛查）。

## 协调者复算脚本坑（verify recipe）

- naive 三席多数：把 `coarse:Fibroblasts` 当独立标签 → named=31；C2b 语义 `coarse:X`≡`X` 归一 → named=28；**hit 集合两版都=worker 的 26 簇全等**→ 判 PASS。字段：ANN 行 = cluster_id/identity/level/grade/gates/flag/why。
- truth 表在 kb9 build 目录 out/kb9_truth_table.tsv（列含 consensus/p1_hit 等当期字段，复算只用 truth 列防循环）。

## B5IMPL（plans/kbgov_b5impl_20260928/）

B5=鼠源输入（title_frac 惯例 + Gm\d+/.*Rik$/m_only 三信号，冻结阈值 T=0.4）→ celltype_ranking=[] + unranked_candidates 全保留 + no_named_ranking_for；AMBIG{GLUL,VIM,CLU} 共表达仅 no_naming_claim 标注不删序。人源零干预；cell_type/list-mode 三工具零扰动（管辖面=genes-mode）。五门全 PASS（病灶 7/7、人源 230 簇位移 0.0%、鼠侧 59/59 全拒、黄金 41/41 off 全等、回退 42 探针逐字节、只读零写入）。fail-soft：词表缺失自动降级 legacy（==OFF 态实证）。
**已知残余风险**：真人源 title-case 送上游会误拒（本数据 misdetections=0 但不保证）→ T+7 calllog 逐例复核，误拒>0 报 PI 切 B4 档（suspected 仅标注不拒答）——改档=方法判据变更须 PI 批，env 粒度同接线不分叉。
协调者活探针三态脚本：training-venv stdio 起生产码；HUM KERA/ALDH3A1（具名 human_assumed）、MOUSE Thy1+Grin3a（suspected 拒答）、Gm3339 组（confirmed 拒答）；B5=0 对照还原 legacy。

## H1M3（plans/grade_h1m3impl_20260928/）

判读协议 v1.3 §9=H1-M3 定名资格 `ie=pass ∨ res=pass`（technical 三门不参与），**向前生效**（落款日后预注册 run 起），9 归档反事实复算与锚件全等（升 24/翻正 7/新错 0/回归 0）；对 OBLIGRUN v2.1 面 99 票做 H1-M3 敏感性对照 delta=0 单独成列（主口径 26/33 不回改）。worker 自曝 PREREG 手抄表 RUN6A"23→23"笔误（真值 24→24）→ ERRATA_PREREG 增量件：判据对照对象是冻结 json 锚件非手抄表，门有效性零影响——手抄表单格笔误+勘误件模式可复用。

## RAGFIX3 三门（v2.4.2=242,928 chunks/3,869 篇）

门③ 87/92=94.6% 首破 80%（原分母原阈值原判据；78→87 单调零倒退）；104 行→准入 103 拒 1（防双计）；7 目标单元兑现 6+C8ORF76 诚实 MISS（全文在库但无词边界 token）+副产品 3；下载 19.33MB≤100MB 预算零 >1GB；CPU embedding 链（禁 GPU 条款下可行）。

## MOUSEEXT 重档判死（plans/mouse_ext_precheck_20260928/）

7 候选行级取证全不收/悬案：GSE137400/81905=训练池母系列（GSM 级实锤 10/10、6/6 包含）；GSE255520=训练细胞重测（收=循环）；GSE63472=P14 发育域+标签不在 GEO；GSE150703/184933=发育/扰动域无标签；唯一悬案 GSE201402（在盘 1.3GB 零下载，7/10 类但 panel 覆盖 50.25%<90% 冻结断言待补检）。**教训句式：标签达标≠独立性达标**；公开资源补不出真第二外部 F1=08-26 limitation 的钉死确认。

## REPOSYNC3 八门 + GitHub 凭据过期（push 通道）

T1-T8 全过（含 T7 自家数据 token 扫描首跑=HARD 0/masked 例外 2 件登记；T8 §9 三版语料筛查=36712326 自 v2.0 在库非本波引入，own-deposit+指派句式复核在案；ra3 103 篇零 watch 交集）。四层 commit 本地就绪（11f9649→73e9cd3→1f547f3→cf254ab，树净 main）后 **push 卡死=gh token 静默过期**（hosts.yml 空壳、缓存令牌 401、SSH key 未注册）→ 协调者设备码流救场（配方在 research-repo-publish）：curl device/code（**Accept: application/json 必须带，否则返回 form-encoded，双格式解析兜底**）→ user_code 发 PI → 轮询取 token → 自动 push。网络异常期 pgrep/全量 ps 扫 /proc 会卡死（某进程 D 态），单命令 echo/date 正常——诊断用定点命令勿全表扫描。
