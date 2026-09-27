#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG 第三轮送审件：v2.1 包 verbatim + 对第二轮（xhigh REVISE）逐条闭合对照。
信息差铁律：二审裁定原文摘录 + 三版闭合位置与文本同呈。零 LLM（纯装配）。"""
import os, hashlib

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
PKG = open(f'{ROOT}/register/REGISTER_PACKAGE_v2.md', encoding='utf-8').read()
SB  = open(f'{ROOT}/register/SUPRABASAL_RECHECK.md', encoding='utf-8').read()
import re
NOTE = re.search(r'## EDITORIAL_NOTE.*', open(f'{ROOT}/KB9_BUILD_REPORT.md', encoding='utf-8').read(), re.S).group(0)

C = [
("A06(未闭合)", "正文仍未展示逐 ID 适用范围及重复关系，且\u201cMüller 胶质（Astro）\u201d\u201cMG/Micro\u201d存在身份混写；最小修订是附出所称 34 行实际表，逐行列明 ID、生物学身份、scope、排除依据及重复项处置，并核清 Astro/MG/Micro，不能用\u201c作者词表没有该类\u201d直接证明生物学不存在。",
 "注册包 §3 现内联 34 行全表逐条呈报（不再以指针代替内容）；身份已按库内基因锚+冻结 crosswalk 别名注核清：MG=Müller 胶质（RLBP1/GLUL/SOX9/S100B）、Astro=星形胶质（GFAP/AQP4/SLC1A3）、Micro=microglia（C1QB）；排除依据全部改为组织解剖学+细胞谱系表述（ Rod/Cone/BC/AC/HC/RGC=视网膜神经层结构不在 portal 取材范围；MG/Astro=视网膜专属胶质类型；Micro=CNS 常驻小胶质谱系，眼表髓系真值由 Macrophages/Monocytes 词条承载且不削减该通道；RPE=不同胚胎起源与取材层）。'标签缺席故误导'式推论已从理由列删除。"),
("A09(未闭合)", "未展示\u201c每个候选类别→九类评价词表\u201d的完整映射；最小修订是附全候选 ID／消歧名／别名到评价类的冻结表，明确未映射及歧义项的处置，再据此定义各候选的\u201c其它类\u201d。",
 "注册包 §5 现内联 38 候选全量映射快照（运行时解析序=frozen crosswalk 优先→k4 内置扩展仅在空折叠时生效），含 ambiguous 双折叠、no_counterpart 判空不参与屏蔽、Proliferating 状态类不折叠、B/NK/Plasma UNMAPPED 如实登记；'其它 truth 类'统一定义=九类词表 − 该候选折叠集。"),
("A12(未闭合)", "AV2-5 的\u201cON 现役态、生产 query_marker 全等\u201d尚未绑定\u201cRUN5 存档票对应的 ON 状态\u201d；最小修订是明确该历史 ON 的库版本、装配参数及 ranking 对账对象，现有 G1 若不能证明对应关系，则登记该项尚未完成并列为下游保真门。",
 "注册包 §4 AV2-5 重写为三态：(a) OFF 历史门=G0 对 RUN5 冻结输入面 33/33（存档票之输入面即此冻结面）；(b) 现役 ON 门=G1 仅证明复刻当前生产语义；(c) **历史 ON 门=未完成**——KB9 无 RUN5 时刻完整请求/库版本留档且库态此后已变（Q6::21/29 回退为 KB7 条激活实证），G1 明确不得写作历史 ON 保真已证，任何复用存档票的后续 run 须先建此门（含批组成快照）。"),
("A13(未闭合)", "尚未形成完整请求层面的缓存等同性规则，lit 同源排除仍仅引用'E1 口径'，且未来 tc_ref 的自动放行超出 D10 所列适用性/屏蔽规则范围；最小修订是补完整请求及批组成的冻结与复用判定、可审核的文献排除规则和记录，并删除 tc_ref 凭限定声明即可入 prompt 的条款。",
 "注册包 §9 三处：①缓存等同性=强制话术全文入条款（完整请求为单位；单簇字段不变≠完整请求不变；KB9 8 复用簇票一律标注缓存混合结果）；②lit 同源排除改为可审核三元组（排除对象定义/两级判定标准/记录义务）且如实登记'本轮未落逐条筛查留档=下游义务'；③tc_ref 条款替换为你方话术（不授权入判读请求，D10 许可不自动扩展，开发集声明不替代单独裁定）。"),
("A19(未闭合)", "低于 MINPOOL 的亚型比较对象仅指向未附出的行，且\u201cKB9 生效口径\u201d混淆事后补定与原预注册；最小修订是按词条列全豁免对象、池量及豁免环节，并明确 MINCORE=3 自本次注册生效，不追认为原 KB9 的先验门槛。",
 "注册包 §8-6③ 现内联豁免比较组全枚举表（组级 CornealEndo=432；author 级 B Cells=212/Corneal_Endo=432/Monocytes=253；由 agg 池层直接计算，载体 A19_MINPOOL_EXEMPT_REGISTRY.tsv）+你的强制话术原文：低于 MINPOOL 或因其他资格条件未进入否决计算者逐项登记不得计作已验特异性；**MINCORE=3=本次注册明确的条款，自本次注册生效，不追认为原 KB9 build 前预注册门槛，既有结果不据此改判**。'KB9 生效口径'字样已删。"),
("判件(收窄)", "判语 1 中复用同一实现逐字节一致不独立证明实现完整符合冻结文本，且未展示逐基因文献条目不能签认外部文献通道已满足；判语 2 中\u201c父池含自身即 2× 不可达\u201d不成立（Conj_superficial 有存活基因为反例），未展示\u201c仅修正父组归属、其余不变\u201d的对照前不能把全部零结果完整归因该缺陷；\u201c无数据层否决理由\u201d应收窄。",
 "判件 v2（附件 1）逐处照你方话术收窄：判语 1=复现性证明（逐字节一致证可复现，不独立证实现合规、不代签文献通道）；判语 2=删除\u201c结构性不可达\u201d一般断言，并以**反事实复算补上你要的对照**（kb7 原脚本仅 L69 父组归属行改 score-argmax、余者逐字不变，重放结果：Conj_suprabasal 全过 0→15（词条 3 core 全在内）、C1 0→10、C2 0→7、Sclera 0→121、**Limbus Fibroblasts 0→0（真实阴性）**、Conj_basal 582→28（索引巧合歪打正着之修正）、Conj_superficial 5→4 反例保留）；逐目标归因表替代一概归因；'无数据层否决理由'收窄为'所报三基因统计值未触发已列 §1.2 数值否决门槛'。"),
("话术1-8", "三、残留限制措辞强制增补 1–8（复现认证/KB7 先例/suprabasal 生物学/豁免与后补门槛/完整请求缓存/tc_ref/案 A/未完成检查）+ 284=283+表头口径校正。",
 "1→判件 v2 判语 1；2→判件 v2 判语 2（并以反事实件强化，未超你给边界）；3→判件 §4+包 §10-5 原文照录；4→包 §8-6③ 原文照录；5→包 §9 缓存等同性原文照录；6→包 §9 tc_ref 原文照录（原'凭声明可入'条款已删）；7→包 §1 案 A 行原文照录（'零回退风险'字样已删）；8→包 §10-6 原文照录；行数口径→包 R-3 行改写为'283 条数据记录（kept 225/block 28/drop 30），含表头共 284 行'。"),
]

head = """【任务】KB9 眼表词条注册申请包 v2.1 —— REVIEWER_LLM 第三轮复核（对第二轮 REVISE 判词逐条闭合判定 + 签发）。你是独立审稿人，无工具；全部材料在本消息内。
【上一轮结果】你方（REVIEWER_LLM xhigh，2026-09-27）对 v2.0 判 REVISE：A01/A03/A05/A07/A11/A15措辞/A16/A17/A18 闭合；A06/A09/A12/A13/A19 未闭合；判件可限定采纳但须收窄两处判语并补反事实对照（或收窄归因）；强制话术 1–8；行数口径 284=283+表头。本轮 v2.1 逐处修订，下表 verbatim 引你判词+闭合位置。
【请裁定】①对未闭合 5 项逐项判【闭合/仍未闭合】；②对判件 v2（含新增反事实复算）判：两处判语收窄是否到位、反事实对照是否满足你索要的归因证据（可采性分级照旧）；③强制话术 1–8 是否逐字落位；④签发：ACCEPTED（可送 PI 批注册）/ REVISE（列条+最小修订）/ REJECTED（根本原因）。既有 P1=22/33 FAIL、P2=0/33 PASS 不改判；本包零执行零接线；勿以'注册条款≠实证完成'为标准要求补跑（你上轮已确认此界分）。

"""
table = "## 二轮判词 → v2.1 闭合对照（verbatim 摘录）\n\n"
for cid, quote, pos in C:
    table += f"### {cid}\n- 判词摘录：{quote}\n- v2.1 闭合位置：{pos}\n\n"

body = table + """---
# 附件 0：注册包 v2.1 全文（verbatim）

""" + PKG + """

---
# 附件 1：suprabasal 判件 v2（含反事实复算，verbatim）

""" + SB + """

---
# 附件 2：KB9_BUILD_REPORT.md 文末 EDITORIAL_NOTE（v2.0 审时版本；本轮未再改动）

""" + NOTE + """

【输出格式】
一、五项复判：| # | 闭合/仍未闭合 | 理由 |
二、判件 v2 复判（判语收窄+反事实对照可采性，一段）
三、话术落位核验（1–8 逐项：在位/不在位/偏差）
四、签发文本：ACCEPTED / REVISE / REJECTED + 依据行 + 给 PI 的签发件抬头建议（一行）
"""
OUT = f'{ROOT}/register/round3/REVIEWER_LLMROUND3_PROMPT.txt'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT,'w',encoding='utf-8').write(head+body)
h=hashlib.sha256((head+body).encode()).hexdigest()
open(f'{ROOT}/register/round3/PROMPT_SHA256.txt','w').write(h+'\n')
print('ROUND3 PROMPT chars=', len(head+body), 'sha256=', h)
