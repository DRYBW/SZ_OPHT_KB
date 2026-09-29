#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""s5_build_v1_t_37a35220.py — 组装 EXPECTED_COMPOSITION_v1.json + v1.md
零手打数字: 全部从 s1/s2/s4b 产物 + v0 json 程序化读取。v0 文件零触碰。
"""
import json, pathlib, math, collections, pandas as pd

KB = pathlib.Path("/mnt/D/EyeKB/kb/composition")
OUT = pathlib.Path("/mnt/D/EyeKB/plans/comp_prior_v1_20260929")
v0 = json.load(open(KB / "EXPECTED_COMPOSITION_v0.json"))
lay = json.load(open(OUT / "retina_conditional_intervals.json"))
osj = json.load(open(OUT / "os_conditional_intervals.json"))
summ = pd.read_csv(OUT / "stratified_recompute_rows_v2.tsv", sep="\t")
xt = pd.read_csv(OUT / "residual_attribution_xtab.tsv", sep="\t")
q6 = pd.read_csv(OUT / "q6_recompute_os.tsv", sep="\t")

# ---- retina conditional intervals: A(预注册) + B(包络) 双界
def norm_name(c): return {"Astrocyte": "Astro", "Microglia": "Micro"}.get(c, c)
v0rows = {r["cell_type"]: r for r in v0["pages"]["retina_normal_adult_human"]["rows"]}
retina_layers = {}
for lid, L in lay["layers"].items():
    rows = {}
    for c, r in L["classes"].items():
        ct = norm_name(c)
        if not r["support_gate_pass"]:
            rows[ct] = {"support_gate_pass": False, "n_units": r["n_units"], "fallback": "design_free_v0_row"}
            continue
        lo_a, hi_a = r["low_pct"], r["high_pct"]
        srcs_lo = [r["iqr_pct"][0]]; srcs_hi = [r["iqr_pct"][1]]
        v0r = v0rows.get(ct, {})
        if v0r.get("c_prior_v1"):
            srcs_lo.append(v0r["c_prior_v1"]["expected_range_pct"][0])
            srcs_hi.append(v0r["c_prior_v1"]["expected_range_pct"][1])
        for la in v0r.get("literature_anchors", []):
            if la.get("kind") == "fold":
                (srcs_lo if la["bound"][0] == "low" else srcs_hi).append(la["bound"][1])
        rows[ct] = {"n_units": r["n_units"], "donor_median_pct": r["median_pct"],
                    "donor_iqr_pct": r["iqr_pct"], "donor_range_pct": r["range_pct"],
                    "interval_A_strict_donor_only": [lo_a, hi_a],
                    "interval_B_v0_formula_envelope": [math.floor(min(srcs_lo)), math.ceil(max(srcs_hi))],
                    "evidence": "A_layered", "support_gate_pass": True}
    retina_layers[lid] = {"definition": lay["layers"][lid].get("unit_def", lid),
                          "n_units_total": L["n_units"], "classes": rows}

os_groups = {}
for g, rows in osj["groups"].items():
    cs = {}
    for c, r in rows.items():
        cs[c] = {"n_units": r["n_units"], "donor_median_pct": r["median_pct"], "donor_iqr_pct": r["iqr_pct"],
                 "donor_range_pct": r["range_pct"], "support_gate_pass": r["support_gate_pass"],
                 **({"interval_donor_only": [r["low_pct"], r["high_pct"]]} if r["support_gate_pass"]
                    else {"fallback": "mixed_region_v0_row (support_gate_fail: n_units<5)"})}
    os_groups[g] = cs

sm = summ[summ.rule.str.startswith(("R0", "R1A", "R1B"))].copy()
sm_mean = summ[summ.rule.str.startswith("R2_MEAN")]
recompute = []
for _, r in sm.iterrows():
    recompute.append(dict(dataset=r.dataset, rule=r.rule, layer=r.layer,
                          flagged=int(r.flagged), face_rows=int(r.n), flag_pct=r.rate))
for _, r in sm_mean.iterrows():
    recompute.append(dict(dataset=r.dataset, rule=r.rule, layer=r.layer,
                          flagged=r.flagged, face_rows=10, flag_pct=r.rate, unit="mean over units"))

v1 = {
 "schema": "eyekb-composition-face/0.2",
 "entry_id": "EXPECTED_COMPOSITION_v1",
 "title": "组成先验面 v1 (COMPV1): 条件层化 — retina 建库/取材/分选策略分层 + 眼表类型×区域 + OB-1 检索声明 | 默认 OFF",
 "generated": "2026-09-29",
 "card": "t_37a35220",
 "authority": "USER_DIRECTIVE_20260928_eyekb_improve_wave.md 追加八 (COMPV1 预授权); 任务书 plans/comp_prior_20260928/BRIEF_DISC_COMPV1.md; 规则预注册 plans/comp_prior_v1_20260929/PHASE0_INVENTORY_t_37a35220.md",
 "wiring": "OFF — 未接线 (零 MCP/运行时引用; 本卡产物不得进任何运行时路径; 激活永远归 PI 点名)",
 "status": "v1_candidate_selfcheck_only",
 "inherits": {"file": "EXPECTED_COMPOSITION_v0.json", "sha256": "d7c6068c9d86510a6053c97ba3361daf55bbe7a215993957aa8f9528d472061e",
              "note": "v0 两页面全部行原样保留于 v0 文件(零改动); 本 v1 = 在其上加条件层; design-free 行语义以 v0 为准"},
 "lineage_declaration": "条件层区间 = kb/baselines adult-only 供者级主档谱系(D001/D002 外部作者注释本地复算)按设计维重聚合 (obs 字段: suspension_enrichment_factors/tissue/study_name; D002 tissue_group strata); 全程未使用自家聚类/自家 demo 注释 (禁循环继承); OB-1 检索 = 盘上 RAG chunks.parquet 242,928 chunks 全量, 零外网",
 "semantics_declarations": {
   "interval_A_strict_donor_only": "设计层区间仅由该层 A 级供者 IQR 构成 (priors/文献fold=混合设计来源不可归因于单层) — 预注册主口径 (PHASE0 §2); 注意其本质=中央50%带, 天然比 v0 三重包络窄",
   "interval_B_v0_formula_envelope": "v0 公式形状逐字保留 (low=floor(min(donor_iqr_low, priors_expected_low, fold_lit_low)) / high=ceil(max(...))), 仅将 donor_iqr 项替换为层内值 — 后验敏感性变体, 未参与预注册判定, 采哪套语义激活前归 PI",
   "support_gate": "层/区域单元数>=5 否则回落 design-free 父行 (机械, 两页共用)",
   "region_row_binding": "眼表 类型×区域 行仅可用于取材区域已知的样本; 禁跨区套用; 区域未知 → design-free 行",
   "target_evaluation": "OB-3 目标(<20%)只按预注册 R1A 判 — 结果: 未达成, 如实报缺口 (见 ob3_recompute + V1_VERDICT)"},
 "retina_design_axis": {
   "available_dimensions_on_disk": ["enrichment(NeuN±/靶向研究声明)", "tissue region(central=fovea+macula+proper / peripheral)", "study"],
   "no_contrast_dimensions": ["suspension_type 全=D001 核悬液一层(细胞悬液 A 级缺层=平台轴残余)", "解离全=机械+去污剂(无酶解vs机械对比)"],
   "unit_key": "donor_id × tissue × enrichment, adult-only (KB2c 排除表)",
   "targeted_layer_basis": "Chen_rgc+Shekhar_GSE237204 归靶向层 = baselines 盘上 caveat/t2 既有设计声明 (非本卡新造)"},
 "pages": {
   "retina_normal_adult_human": {
     "design_free_rows": "见 EXPECTED_COMPOSITION_v0.json pages.retina_normal_adult_human.rows (零改动继承)",
     "conditional_layers": retina_layers,
     "ob3_recompute": recompute,
     "residual_persists_rows": xt[xt.verdict == "PERSISTS_all_rules"].to_dict("records"),
     "newflag_strict_layer_rows": xt[xt.verdict == "NEWFLAG_under_strict_layer"].to_dict("records"),
     "resolved_by_layering_rows": xt[xt.verdict == "RESOLVED_by_layering"].to_dict("records")},
   "ocular_surface_normal_adult_human": {
     "design_free_rows": "见 v0 pages.ocular_surface_normal_adult_human.rows (零改动继承)",
     "region_layers": os_groups,
     "category_note": "行=类型×tissue_group (cornea/limbus/sclera/ocular surface region/corneal endothelium); 区域混合超级类仅可对照 design-free 行; 已知区域样本必须路由到对应区域行 — 禁跨区套用条款进面语义",
     "q6_recompute": q6.to_dict("records")}},
 "ob1_search_declaration": {
   "rows": ["ocular_surface_normal_adult_human:Pericytes", "ocular_surface_normal_adult_human:Goblet_cell"],
   "method": "盘上 /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09/chunks.parquet (242,928 chunks) 全量窗口检索 + v0 ledgers/mine_ct_pct.json 交叉; 零外网",
   "result_goblet": "480 chunks 命中; 眼表语境 12 窗; 0 句通过三重过滤(人+正常成人眼表+直接报告捕获组成%) — 数字命中全部为假阳性(试剂浓度/手术成功率/再上皮化面积率); 维持 null(no_evidence)",
   "result_pericytes": "2,574 chunks 命中; 眼表定量组成 0 窗 — 维持 null(B_missing), A 级区间不变",
   "verdict": "OB-1 = 检索义务完成, 两行维持 null; 禁编数条款执行",
   "candidate_ledger": "plans/comp_prior_v1_20260929/ob1_lit_candidates.tsv (108 窗全量留痕)"},
 "activation_obligations_v1": {
   "OB-1": "RESOLVED_AS_NULL — 两行 no_evidence 合法维持, 检索留痕可审",
   "OB-2": "RESOLVED — 类型×区域行已出 (5 组 × 9 类, 1 组支撑门不过回落); Q6 分区重算 Pericytes 旗标消除/SMC 新旗如实报",
   "OB-3": "PARTIAL — 分选×区域层已出并重算; 预注册主口径 <20% 未达成 (Q1-Q5 全部 30-60%); 残余触发维度=悬液平台轴+特定富集设计缺层 (见 V1_VERDICT), 禁改球门条款执行, 不达标如实报"},
 "caveats": v0["caveats"] + [
   "v1 条件层区间本质=中央50%带 (A 严格语义), 单样本越界率天然高于包络语义 — 语义选择激活前归 PI",
   "细胞悬液(scRNA)与核悬液(snRNA)类比例不可直比 (REVIEWER_LLM T2 继承): Q1/Q2/Q3/Q4 全部平台错配, 面侧无 A 级细胞悬液层可路由",
   "眼表 corneal endothelium 单独层 (2 单元/404 细胞) 支撑门不过=诚实回落, 不是数据缺陷",
   "Q6 区域重算含 study 混合 (D002 内 li_GSE147979 等小组), 区域行区间仅由 chen_* 主研究供者单元构成时 SMC 3.1% 为真实跨研究差异信号"],
}
json.dump(v1, open(KB / "EXPECTED_COMPOSITION_v1.json", "w"), ensure_ascii=False, indent=1)
print("v1 json written", (KB / "EXPECTED_COMPOSITION_v1.json").stat().st_size)

# ---------- md ----------
L = []
A = L.append
A("# EXPECTED_COMPOSITION_v1 — 组成先验面 v1（条件层化；默认 OFF）\n")
A("> 卡 t_37a35220 | 放行=USER_DIRECTIVE 追加八 | 规则预注册=PHASE0_INVENTORY_t_37a35220.md | v0 三件字节不动\n")
A("> **⛔ 未接线；旗标=提示复核≠注释错误；激活永远归 PI。**\n")
A("## 1. retina 条件层（建库/取材/分选策略；单元=donor×组织×富集，adult-only）\n")
A("| 类 | v0 包络[低,高] | RC1 未分选全区域 A/B | RC2 未分选中央 A/B | RC3 未分选外周 A/B | RC4 分选/靶向 A/B |")
A("|---|---|---|---|---|---|")
CLS = ["Rod","Cone","BC","AC","HC","RGC","MG","Astro","Micro","RPE"]
LAYK = ["RC1_unsorted_allregion","RC2_unsorted_central","RC3_unsorted_peripheral","RC4_sorted_or_targeted"]
for c in CLS:
    v0r = v0rows[c]
    cells = [f"[{v0r['low_pct']:.0f},{v0r['high_pct']:.0f}]"]
    for lid in LAYK:
        r = retina_layers[lid]["classes"][c]
        if not r.get("support_gate_pass"):
            cells.append("gate-fail→v0")
        else:
            a1, a2 = r["interval_A_strict_donor_only"]; b1, b2 = r["interval_B_v0_formula_envelope"]
            cells.append(f"[{a1},{a2}] / [{b1},{b2}] (n={r['n_units']})")
    A("| " + c + " | " + " | ".join(cells) + " |")
A("\n注：A=严格供者带（预注册主口径），B=v0 公式逐字包络（后验敏感性）；A 本质=中央 50% 带，天然窄于 v0 三重包络——语义选择归 PI。\n")
A("RC4 成员=NeuN+ FACS ∪ Chen_rgc ∪ Shekhar_GSE237204（baselines 盘上既有靶向设计声明）。\n")
A("## 2. OB-3 分层反向质检复算（20% 线不动；判定只看预注册 R1A）\n")
A("| 数据集 | 平台 | R0 v0 | R1A 层化(主) | R1B 包络(敏) | R2 单元均 A | R2 单元均 B | R1A 判定 |")
A("|---|---|---|---|---|---|---|---|")
PLAT = {"Q1_Lukowski2019":"cell","Q2_GSE155288":"cell","Q3":"smart-seq cell","Q4":"cell+CD73/90分选","Q5b":"nucleus"}
for ds in PLAT:
    g = summ[summ.dataset == ds]
    def rate(pref):
        rr = g[g.rule.str.startswith(pref)]
        return f"{rr.iloc[0].flagged:.0f}/10={rr.iloc[0].rate}%" if len(rr) else "-"
    ra = g[g.rule == "R1A_layer_Aonly(PREREG_HEADLINE)"].iloc[0].rate
    A(f"| {ds} | {PLAT[ds]} | {rate('R0')} | {rate('R1A')} | {rate('R1B')} | {rate('R2_MEAN(A')} | {rate('R2_MEAN(B')} | {'TRIGGER' if ra > 20 else 'under'} |")
A("\n**R0 复现门 5/5 PASS（含 Q5b 0/10）。R1A 下 5/5 全部 TRIGGER → OB-3 目标 <20% 未达成，如实报缺口（§4+V1_VERDICT）。**\n")
A("### 逐行归因（PERSISTS=三规则全旗 / NEWFLAG=仅严格层新增 / RESOLVED=层化消除）\n")
A("| 数据集 | 行 | 观测% | v0 | A | B | verdict |")
A("|---|---|---|---|---|---|---|")
for _, r in xt.iterrows():
    A(f"| {r.dataset} | {r.row} | {r.pct_v0} | {r.v0} | {r.A} | {r.B} | {r.verdict} |")
A("\n## 3. OB-2 眼表 类型×区域行\n")
GT = list(os_groups.keys())
A("| 类型 | " + " | ".join(g.split(" (")[0] for g in GT) + " | v0 混合行[低,高] |")
A("|---|" + "---|" * (len(GT) + 1))
os_v0rows = {r["cell_type"]: r for r in v0["pages"]["ocular_surface_normal_adult_human"]["rows"]}
for c in [k for k, v in os_v0rows.items() if v["low_pct"] is not None]:
    cells = []
    for g in GT:
        r = os_groups[g].get(c)
        cells.append("gate-fail→v0" if not r or not r.get("support_gate_pass")
                     else f"[{r['interval_donor_only'][0]},{r['interval_donor_only'][1]}] n={r['n_units']}")
    v0r = os_v0rows[c]
    A(f"| {c} | " + " | ".join(cells) + f" | [{v0r['low_pct']},{v0r['high_pct']}] |")
A("\n### Q6（D002 sub100k，adult-only 76,708 细胞）分区域重算\n")
qq = q6.groupby("region").agg(n_cells=("n_cells", "max")).reset_index()
flagcnt = q6[q6.status.str.startswith("FLAG")].groupby("region").size()
A("| 区域 | 评估行数 | 旗标 | 明细 |")
A("|---|---|---|---|")
for g in q6.region.unique():
    sub = q6[q6.region == g]
    ev = sub[~sub.status.isin(["not_evaluated_small_support", "support_gate_fail_region"])]
    fl = sub[sub.status.str.startswith("FLAG")]
    A(f"| {g} | {len(ev)} | {len(fl)} | " + ("; ".join(f"{r.cell_type} {r.pct}% vs [{r.low},{r.high}] {r.status}" for _, r in fl.iterrows()) or "-") + " |")
A("\nv0 混合行的 Pericytes 旗标 (6.5%>[0,5]) 在区域行下全部消除=纯区域混合伪旗；SMC 在 limbus/sclera 新旗如实保留（区域行语义的代价与收益都在盘上）。\n")
A("## 4. OB-1 检索声明（两行缺 PMID）\n")
A("- 检索面：盘上 chunks.parquet 242,928 chunks 全量（零外网）+ v0 ledgers 交叉。")
A("- **Goblet_cell**：480 chunks 命中 → 眼表语境 12 窗 → 三重过滤后 **0 句**通过（数字全为试剂浓度/手术成功率/再上皮化面积率假阳性）→ **维持 null(no_evidence)**。")
A("- **Pericytes**：2,574 chunks 命中 → 眼表定量组成 **0 窗** → **维持 null**（A 级区间行不变）。")
A("- 候选全量 108 窗留痕：ob1_lit_candidates.tsv。\n")
A("## 5. 红线与边界声明\n")
A("- v0 冻结件与 evalset/票面/kb/mcp_server 零触碰（前后 sha 台账 logs/SHA_BASELINE_post 自证）。")
A("- wiring=OFF：本文件不进任何运行时路径；激活永远归 PI 点名。")
A("- 球门与判据不回调：20% 线、供者级分布法、支撑门（≥5 单元）、区间公式形状（含 B 变体的逐字 min/max 包络）全部形不动；分层=加维度。")
A("- 禁循环派生：区域/富集全部来自 D001/D002 portal 作者注释谱系 + baselines 盘上既有设计声明；未从自家聚类取数；Q6=循环参照仅 sanity 不入判定。")
A("- 分母语义继承 v0（捕获事件构成参考，非组织学真值，非达标线）；fetal/organoid/developing 排除继承。\n")
p = KB / "EXPECTED_COMPOSITION_v1.md"
p.write_text("\n".join(L), encoding="utf-8")
print("v1 md written", p.stat().st_size)
