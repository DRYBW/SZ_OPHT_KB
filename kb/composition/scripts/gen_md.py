#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_md.py — 从 EXPECTED_COMPOSITION_v0.json + selfcheck 产物渲染人读版 md (v0, 2026-09-28)"""
import json, pathlib, csv, collections
KB=pathlib.Path("<EYEKB>/kb/composition")
face=json.load(open(KB/"EXPECTED_COMPOSITION_v0.json"))
summ=json.load(open(KB/"selfcheck/summary.json"))
flags=list(csv.DictReader(open(KB/"selfcheck/flags.tsv"),delimiter="\t"))

# ---------- EXPECTED_COMPOSITION_v0.md
L=["# EXPECTED_COMPOSITION_v0 — 正常成人眼组成先验面（人读版）",
"",
f"> 生成 {face['generated']} | 卡 {face['card']} | 授权：{face['authority']}",
">",
"> **⛔ 接线状态：`"+face["wiring"]+"`** —— 本面任何运行时消费（MCP/baselines/打分/门控）须另卡另批、PI 拍板。",
"",
"## 0. 定位与口径（先读这里）",
f"- 面语义：**{face['denominator_semantics']}**",
"- 证据等级：" + "；".join(f"{k}={v}" for k,v in face["evidence_grades"].items()),
"- 谱系声明（禁循环条款）：" + face["lineage_declaration"],
"- 区间机械规则（预注册）：" + face["interval_rule"],
"- 范围：" + json.dumps(face["scope"],ensure_ascii=False),
"",]
for page,p in face["pages"].items():
    L.append(f"## 1.{list(face['pages']).index(page)+1} 页: {page}")
    L.append(f"- registry 锚: {p['registry_anchor']}")
    L.append(f"- 供者级主档: {p['donor_main']}")
    L.append("")
    L.append("| 细胞类型 | 低% | 中% | 高% | 证据 | B 状态 | 逐行 PMID | 供者级实测(median/iqr/range) |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in p["rows"]:
        am=r.get("a_measured") or {}
        meas=f"{am.get('donor_median_pct','–')} / {am.get('donor_iqr_pct','–')} / {am.get('donor_range_pct','–')}" if am else "–"
        lo,mi,hi=(r['low_pct'],r['mid_pct'],r['high_pct'])
        L.append(f"| {r['cell_type']} ({r['label_cn']}) | {lo if lo is not None else 'null'} | {mi if mi is not None else 'null'} | {hi if hi is not None else 'null'} | {r['evidence']} | {r['grade_b_status']} | {', '.join(r['pmids']) or '—'} | {meas} |")
    L.append("")
    L.append("### 逐行文献锚点（盘上已入库文献原文句，B 级可定位）")
    for r in p["rows"]:
        if not r["literature_anchors"]: continue
        L.append(f"- **{r['cell_type']}**")
        for a in r["literature_anchors"]:
            q=("“"+a["quote"]+"”") if a.get("quote") else "(题录锚, 无逐字句)"
            L.append(f"  - PMID {a['pmid']} [{a['kind']}] {q} — {a['note']}")
    L.append("")
L.append("## 2. PMID 题录三判据自检")
v=face["pmid_verification"]
L.append(f"- 判据：{v['criteria']}；PMID 总数 {v['pmids_total']}，台账不合格行 {v['ledger_fail_rows']}")
L.append("- 逐条明细见 `ledgers/PROVENANCE_COMP_v0.tsv`")
L.append("")
L.append("## 3. 已知限制与 caveat")
for c in face["caveats"]: L.append(f"- {c}")
if face.get("rows_missing_pmid"):
    L.append(f"- 缺逐行 PMID 的行（激活前义务 OB-1）：{', '.join(face['rows_missing_pmid'])}")
for ob in face.get("activation_obligations",[]): L.append(f"- 激活义务 {ob}")
L.append("- 疾病态比例不建（PDR 注释不可靠口径维持）；发育轴（fetal/organoid）数值折叠排除，引用记录留痕。")
L.append("- “INTAKE 台账 392 条”按任务书原文并入“盘上已入库 RAG 文献（papers.jsonl v2.4.2）元数据可核者”口径执行（deviation 声明：盘上未寻得名含 INTAKE 且恰 392 条的文献台账文件；methods-scrna 索引页恰 392 篇，作为可核集之一纳入）。")
L.append("")
L.append("## 4. 自检与激活")
L.append("- 自检旗标报告：`COMP_SELFFLAG_20260928.md`（只出旗标清单与比例分布，不出注释错误结论）。")
L.append("- 本面默认 OFF；接入判读层（unexpected 旗标器）为另卡另批事项。")
(KB/"EXPECTED_COMPOSITION_v0.md").write_text("\n".join(L),encoding="utf-8")

# ---------- COMP_SELFFLAG_20260928.md
R=["# COMP_SELFFLAG_20260928 — EXPECTED_COMPOSITION_v0 自检旗标报告（只读，出旗标不出结论）",
"",
f"> 卡 {face['card']} | 输入：`EXPECTED_COMPOSITION_v0.json` × 盘上冻结产物（kb/baselines, plans/evalset 冻结件, demo_gse165784 v2 共识草稿表）",
"> **⛔ 本面未接线。旗标=提示复核，不等于注释错误；接线与激活另卡另批（PI 拍板）。**",
"",
"## 0. 方法",
"- 对账对象：评估卷各成员真值组成（Q1–Q9，真值=作者级/portal 注释或 mapped_10class；非自家聚类重标注）+ demo GSE165784 v2 Track B 共识注释草稿（疾病材料，展示门行为）。",
"- 旗标规则：pct < low → BELOW；pct > high → ABOVE；面外身份（T/巨噬/成纤维/前体…）→ off_face_identity 披露行；比例分母=该数据集全部细胞。",
"- 反向质检内建条款：健康公开集被旗标类型占比 >20% → 如实报告“面太窄=面的问题不是数据的问题”。",
"- 域外轴（不计入反向质检分母）：Q7 小鼠（物种轴）、Q8 胎儿（发育轴）、Q6（与眼表面同构建源=循环参照）、Q9 demo（疾病手术材料，usage_scope 禁当达标对照）。",
"",
"## 1. 汇总旗标率",
"",
"| 数据集 | 面 | 细胞数 | 旗标行数/面行数 | 旗标率 | 反向质检 |",
"|---|---|---|---|---|---|"]
for s in summ:
    R.append(f"| {s['dataset']} | {s['page']} | {s['total_cells']:,} | {s['n_flagged']}/{s['face_rows']} | {s['flag_pct']}% | {s['reverseQC']} |")
R+=["",
"## 2. 旗标明细（逐行 数据集×细胞类型）","",
"| 数据集 | 行 | 观测% | 面区间[低,高] | 状态 |","|---|---|---|---|---|"]
byd=collections.defaultdict(list)
for f in flags: byd[f["dataset"]].append(f)
for ds,rows in byd.items():
    for f in rows:
        iv=f"[{f['low']},{f['high']}]" if f["low"] not in (None,"") else "null(披露行)"
        R.append(f"| {ds} | {f['row']} | {f['pct']} | {iv} | {f['status']} |")
R+=["","## 3. 反向质检验算（内建条款）",""]
trig=[s for s in summ if s["reverseQC"].startswith("TRIGGER")]
cnt=sum(1 for s in summ if s["in_scope"]=="yes") if False else sum(1 for s in summ if s["dataset"] in ("Q1_Lukowski2019","Q2_GSE155288","Q3","Q4","Q5b"))
R+=[f"- 计入反向质检的健康公开集：Q1/Q2/Q3/Q4/Q5b（共 {cnt} 个，人·正常·成人视网膜）。",
    f"- **触发（>20% 类型被旗标）：{len(trig)} 个 —— " + "; ".join(f"{s['dataset']} {s['flag_pct']}%" for s in trig) + "**" if trig else "- 无触发。",
    "- 判读（照实，非结论）：按内建条款，这首先说明 **v0 区间对“跨平台/跨取材区域/分选设计”过窄**，是面的问题不是数据的问题。具体可归因：Q1/Q2=中央凹取材+scRNA 细胞悬液（面主档为 snRNA 核悬液，Astra T2 已声明两口径不可直比）；Q3/Q4=Macroglia 签名拆分口径+CD73/CD90 分选设计抬 BC/MG 压 Rod；Q5b 与面主档同源（HRCA 内部构成）旗标率 0 是**循环自证的上界，不是泛化好**。",
    "- 处置建议（不代拍，激活另卡另批时随文呈 PI）：v1 按 suspension_type（核/细胞）与取材区域（中央凹/周边/全视网膜/分选）分层出区间；或把“先验面”定义为带设计豁免的条件面。",
    "",
"## 4. 面外身份披露（非旗标，informational）","",
"### Q8 胎儿（域外轴行为记录）",
"- retinal progenitor cell 为最大类 73,566/226,506=32.5%（分母经复核=def.classes 全类合计=全文件）—— 成人面无 progenitor 行，全部入 off_face_identity；发育材料对照成人面的预期行为。",
"",
"### 各集面外身份 Top 行"]
for ds,rows in byd.items():
    offs=[f for f in rows if f["status"]=="off_face_identity"][:8]
    if offs: R.append(f"- **{ds}**: "+ "; ".join(f"{f['row'].split('::',1)[1]} {f['pct']}%" for f in offs))
R+=["",
"## 5. 声明",
"- 本报告只输出旗标清单与比例分布；旗标≠注释错误；不据本报告判定任何既有注释的对错。",
"- 本面未接线、默认 OFF；接线与激活另卡另批。",
"- 复现：`python3 scripts/build_expected_composition_v0.py && python3 scripts/selfcheck_comp_v0.py && python3 scripts/gen_md.py`（日志 logs/selfcheck_run.log）。",
""]
(KB/"COMP_SELFFLAG_20260928.md").write_text("\n".join(R),encoding="utf-8")
print("md written:", (KB/'EXPECTED_COMPOSITION_v0.md').stat().st_size, (KB/'COMP_SELFFLAG_20260928.md').stat().st_size)
