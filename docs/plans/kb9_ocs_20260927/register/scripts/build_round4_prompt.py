#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG 第四轮送审件：v2.2 包 verbatim + 对第三轮 REVISE 最小修订清单 1–5 逐条闭合对照（判词原文 verbatim）。"""
import os, re, hashlib
ROOT='/mnt/D/EyeKB/plans/kb9_ocs_20260927'
PKG=open(f'{ROOT}/register/REGISTER_PACKAGE_v2.md',encoding='utf-8').read()
SB=open(f'{ROOT}/register/SUPRABASAL_RECHECK.md',encoding='utf-8').read()
NOTE=re.search(r'## EDITORIAL_NOTE.*', open(f'{ROOT}/KB9_BUILD_REPORT.md',encoding='utf-8').read(), re.S).group(0)
R3=open(f'{ROOT}/register/round3/REVIEWER_LLMROUND3_REPLY_RAW.md',encoding='utf-8').read()

C=[
("清单项 1（A06）", "更正表后 MG／Astro／Micro 的身份混写，删除\u201c作者/真值类缺席，因此任何命中必属误导\u201d的推论。Rod 等行中的\u201c任何命中只能来自……\u201d也改为取材范围及条目适用性陈述，不对命中来源作穷尽断言。",
 "§3：表后要点整体重写——身份统一口径行（MG=Müller 胶质 RLBP1/GLUL/SOX9/S100B；Astro=星形胶质 GFAP/AQP4/SLC1A3；Micro=microglia C1QB，旧合并表述宣告作废）；6 类+Astro 行改为\u201c判定依据=组织解剖取材范围+条目细胞身份；规则仅陈述\u2018眼表面装配不计入排名\u2019，对命中来源不作穷尽断言\u201d；内联 34 行表已按同一口径再生成（bio_reason 列同步去除\u201c任何命中只能来自\u201d句式，Rod/视网膜神经元行落为\u201c该条 scope=retina_only：眼表面材料证据装配不计入其 kb_marker_ranking（对命中来源不作穷尽断言）\u201d，Micro 行改\u201c本条在眼表面装配中不计入排名\u201d）。"),
("清单项 2（A19）", "在现有豁免表增加 entry_id／父组／比较对象／pool／适用或不适用／豁免环节，按四个申请词条明确对应；不适用的对象不得记作已实施比较后的豁免。删除\u201cKB9 生效口径\u201d，将\u201c冻结前判据补全\u201d改为\u201c本次注册条款补全\u201d。保留现有\u201c不追认……\u201d句。",
 "§8-6③ 替换为**逐词条对应表**（7 列全：entry_id/parent_group/comparator/level/pool/applies_to_entry/exempt_link，20 行，内联+载体 A19_MINPOOL_EXEMPT_BY_ENTRY.tsv；小池对象父组归属由 agg 供体对齐实算 B Cells→Fibroblast-stroma、Monocytes→Epithelium、Corneal_Endo→Keratocytes，故逐词条列出适用/不适用与豁免环节，不适用对象标注\u2018不计作已实施比较后的豁免\u2019，另有\u2018实际参与否决组数\u2019对照行）。标题已改\u201c本次注册条款补全（A19 三缺口）\u201d；\u201cKB9 生效口径\u201d字样已删（①改为\u2018自本次注册生效；事实注：KB9 实跑四新条 core 数均不低于 3，但此非当时预注册门槛\u2019）；\u201c不追认\u201d句原样保留。"),
("清单项 3（证据强度统一）", "将 §8-1、§11 和 EDITORIAL_NOTE 中超出判语 1 的表述统一收窄为：\u201c所报三基因统计值满足本判件列示数值门槛，既有输出可复现；实现完整符合冻结判据及逐基因文献支持关系不由该复算代签。\u201d删除\u201c四亚型零结果同机制解释\u201d；将 Limbus 的\u201c真实阴性\u201d改为：\u201c在本次父组赋值反事实下仍为零，不支持用该缺陷解释其零结果。\u201d",
 "三处已全部落位同一句话术（§8-1、§11 A15 行、附件 2 NOTE 第 3 条）；\u201c冻结判据正确执行\u201d\u201c§1.2 过准入\u201d字样全库清零（grep=0）。判件 v2.1：§3 机制段改为\u201c其逐目标归因不靠机制外推，见下表反事实结果\u201d；判语 2 的\u201c完整归因\u201d加限定语\u201c**对本输入、该单行干预、全过数是否为零这一输出**\u201d；Limbus 行按你话术改写并注\u201c不升级为无条件\u2018真实阴性\u2019结论\u201d；PRERAG 正字为 PREREG。"),
("清单项 4（案 A）", "将\u201c零回退面\u201d改为\u201c仅补词条，不施加 R2/R3 屏蔽规则\u201d，保留其后限制。",
 "§1 案 A 定义行已替换为该句（\u201c回退与票面含义受案 A 限制条款约束\u201d尾注+原限制段全保留；\u201c零回退面/零回退风险\u201d字样全库清零）。"),
("清单项 5（逐字核验声明）", "若继续要求\u201c八条逐字一致\u201d签认，附二轮八条完整原句；否则将\u201c逐字原文照录\u201d改为\u201c限制性要求已落位\u201d，并先消除抵牾。",
 "本对照表已把三审意见全文随件呈报、且包内不再出现\u201c逐字原文照录\u201d自我声明——采你给的降格路径：**限制性要求已落位**（各承载位置见上）；抵牾四处（表后规则/①括注/案 A/引用段）已消除。"),
]

head="""【任务】KB9 眼表词条注册申请包 v2.2 —— REVIEWER_LLM 第四轮复核。你是独立审稿人，无工具；全部材料在本消息内。
【上一轮】你方（REVIEWER_LLM xhigh，2026-09-27 第三轮，全文=附件 3 verbatim）判 REVISE：A09/A12/A13 闭合；A06/A19 仍未闭合；最小修订清单 1–5（全部为文本项，你已确认不要求补跑/接线/激活，不改 P1=22/33 FAIL、P2=0/33 PASS）。本轮 v2.2 按清单逐项修订。
【请裁定】①清单项 1–5 逐项【闭合/未闭合】；②话术 1/2/4/7 偏差复验；③签发：ACCEPTED（可送 PI 批注册）/ REVISE / REJECTED。若 ACCEPTED，请按你上轮抬头建议格式给一行签发抬头。
【声明】本包为申请文本零执行；下列对照中\u201c落位\u201d指限制性要求在包内文本已生效（不主张逐字签认）。

"""
table="## 三审最小清单 → v2.2 闭合对照（判词摘录 verbatim）\n\n"
for cid,quote,pos in C:
    table+=f"### {cid}\n- 判词摘录：{quote}\n- v2.2 落位：{pos}\n\n"

body=head+table+"""---
# 附件 0：注册包 v2.2 全文（verbatim）

"""+PKG+"""

---
# 附件 1：suprabasal 判件 v2.1（verbatim）

"""+SB+"""

---
# 附件 2：KB9_BUILD_REPORT.md 文末 EDITORIAL_NOTE（verbatim；正文其余未动）

"""+NOTE+"""

---
# 附件 3：你方第三轮判词全文（verbatim，供核对基准）

"""+R3+"""

【输出格式】
一、清单项 1–5：| # | 闭合/未闭合 | 理由 |
二、话术 1/2/4/7 复验（一行一项）
三、签发文本 + 给 PI 的签发件抬头（一行）
"""
OUT=f'{ROOT}/register/round4/REVIEWER_LLMROUND4_PROMPT.txt'
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'w',encoding='utf-8').write(head if False else body)
h=hashlib.sha256(body.encode()).hexdigest()
open(f'{ROOT}/register/round4/PROMPT_SHA256.txt','w').write(h+'\n')
print('ROUND4 PROMPT chars=',len(body),'sha256=',h)
