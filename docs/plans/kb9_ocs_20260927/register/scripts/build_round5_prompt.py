#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG 第五轮送审件：四审唯一残留项（判件反事实表'真阴性'格）修正后的单项复验。"""
import hashlib, os
ROOT='/mnt/D/EyeKB/plans/kb9_ocs_20260927'
SB=open(f'{ROOT}/register/SUPRABASAL_RECHECK.md',encoding='utf-8').read()
R4=open(f'{ROOT}/register/round4/REVIEWER_LLMROUND4_REPLY_RAW.md',encoding='utf-8').read()
PKG_SHA='078e493be5d71dd0686a4f0402bcd52768b6c6d80afbceebf3057946df4c1fdf'

body=f"""【任务】KB9 注册申请包 第五轮复核=**单项残留复验+终签发**。你是独立审稿人，无工具；材料全在本消息内。
【四审结论回显（你方上轮全文=附件 2 verbatim）】清单 1–5 中 1/2/4/5 闭合、话术 1/4/7 闭合；唯一未闭合=清单项 3/话术 2："附件 1 §3 反事实表仍写有'真阴性'；……应直接改为'在本次父组赋值反事实下仍为零，不支持用该缺陷解释其零结果'……删除该表格中的'真阴性'并保留指定反事实限定后，再行签发"。
【本轮变更】仅动判件（附件 1，v2.2）该表格一格+版本注记行，按你指定话术逐字改写：
- 改前：`| Limbus Fibroblasts | 0 | 0 | **该零对反事实稳健**（真阴性，与 KB9 k1 一致 core=[]） |`
- 改后：`| Limbus Fibroblasts | 0 | 0 | 在本次父组赋值反事实下仍为零，不支持用该缺陷解释其零结果（与 KB9 k1 core=[] 一致） |`
注册包本体（v2.2，sha256={PKG_SHA}）自四审送审字节起零改动；判件其余部分与 v2.1 一致（版本注记行为变更日志自述，非断言）。P1=22/33 FAIL、P2=0/33 PASS 不变；零执行零接线。
【请输出】①单项复验：[闭合/仍未闭合]；②总签发：ACCEPTED（可送 PI 批注册）/ REVISE / REJECTED；③你四审抬头建议句式下的最终签发抬头一行。

---
# 附件 1：suprabasal 判件 v2.2 全文（verbatim，唯一被改动件）

{SB}

---
# 附件 2：你方第四轮判词全文（verbatim，本轮复验基准）

{R4}
"""
OUT=f'{ROOT}/register/round5/REVIEWER_LLMROUND5_PROMPT.txt'
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'w',encoding='utf-8').write(body)
h=hashlib.sha256(body.encode()).hexdigest()
open(f'{ROOT}/register/round5/PROMPT_SHA256.txt','w').write(h+'\n')
print('ROUND5 chars=',len(body),'sha256=',h)
