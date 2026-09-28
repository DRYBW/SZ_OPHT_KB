#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kbgov_ab.py — 证据层机械 A/B（KBGOV_PREREG_v1.1 §1-§5，零 LLM 零网络零生产写）。
A = G0 已验证的复刻 ranking（现库激活态）；B1/B2/B3 = G1+G2+G3 叠加变体。
输出：data/kbgov_ab_lesion.tsv、out/kbgov_regression_shift.tsv、out/kbgov_mouse_side.tsv、
      out/kbgov_ab_metrics.json、logs/kbgov_ab.log。"""
import json, re, csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kbgov_replica import load_markers, rank_genes

OUT = "/mnt/D/EyeKB/plans/kb_gov_20260928"
import gzip
VOC = json.load(gzip.open(f"{OUT}/data/kbgov_vocab.json.gz", "rt", encoding="utf-8"))
HUM, M_RAW, M_UP, H2M = set(VOC["hum"]), set(VOC["m_raw"]), set(VOC["m_up"]), VOC["h2m"]
CAL = json.load(open(f"{OUT}/data/kbgov_g1_calibration.json"))
T = CAL["T_frozen"]
VARIANTS = ("B1", "B2", "B3", "B4", "B5")
AMBIG = {"GLUL", "VIM", "CLU"}  # PREREG §3 G3 冻结锚集
P_GM, P_RIK, P_TITLE = re.compile(r"^Gm\d+$"), re.compile(r"Rik$"), re.compile(r"^[A-Z][a-z]")

mk, ow = load_markers()


def tier_of(genes):
    letters = [g for g in genes if re.search(r"[A-Za-z]", g)]
    title = [g for g in letters if (not g.isupper()) and P_TITLE.match(g)]
    msp = [g for g in genes if P_GM.match(g) or P_RIK.search(g)]
    monly = [g for g in genes if g.upper() not in HUM and (g.upper() in M_UP or g in M_RAW)]
    tf = len(title) / max(len(letters), 1)
    if tf < T:
        return "human_assumed", {"title_frac": round(tf, 3), "msp": len(msp), "m_only": len(monly)}
    ev = {"title_frac": round(tf, 3), "msp": len(msp), "m_only": len(monly)}
    return ("mouse_confirmed" if (msp or monly) else "mouse_suspected"), ev


def g3_hit(shared):
    return len(shared) >= 1 and set(shared) <= AMBIG


def g2_eligible(n, shared):
    return n >= 2 and all(g in H2M for g in shared) and not set(shared) <= AMBIG


def apply_B(genes, variant):
    r, gl = rank_genes(genes, mk, ow)
    t, ev = tier_of(genes)
    if variant == "B1":
        named = [c for c, n, s in r]
        info = {"tier": t, "tier_evidence": ev, "species_qualified": t != "human_assumed",
                "no_naming_flags": [c for c, n, s in r if g3_hit(s)],
                "removed": [], "unranked": []}
    elif variant == "B2":
        removed = []
        if t == "mouse_confirmed":
            named = [c for c, n, s in r if g2_eligible(n, s)]
            removed = [c for c, n, s in r if c not in named]
        else:
            named = [c for c, n, s in r if not g3_hit(s)]
            removed = [c for c, n, s in r if g3_hit(s)]
        info = {"tier": t, "tier_evidence": ev, "species_qualified": t != "human_assumed",
                "removed": removed, "unranked": removed}
    elif variant == "B3":
        removed = []
        if t == "mouse_confirmed":
            named = []
            removed = [c for c, n, s in r]
            refused = True
        elif t == "mouse_suspected":
            named = [c for c, n, s in r if not g3_hit(s)]
            removed = [c for c, n, s in r if g3_hit(s)]
            refused = False
        else:
            named = [c for c, n, s in r if not g3_hit(s)]
            removed = [c for c, n, s in r if g3_hit(s)]
            refused = False
        info = {"tier": t, "tier_evidence": ev, "species_qualified": t != "human_assumed",
                "refused": refused, "removed": removed, "unranked": removed}
    elif variant == "B4":
        # 组合：V-c 仅 confirmed 拒答 + G3 flag-only（位移设计=0；人源非破坏）
        r_named = [c for c, n, s in r]
        if t == "mouse_confirmed":
            named = []
            removed = list(r_named)
        else:
            named = r_named
            removed = []
        info = {"tier": t, "tier_evidence": ev, "species_qualified": t != "human_assumed",
                "refused": t == "mouse_confirmed",
                "no_naming_flags": [c for c, n, s in r if g3_hit(s)],
                "removed": removed, "unranked": removed}
    elif variant == "B5":
        # 组合：V-c 扩至 suspected（鼠源域全拒=FACEV21(b) 库侧化）+ G3 flag-only
        r_named = [c for c, n, s in r]
        if t in ("mouse_confirmed", "mouse_suspected"):
            named = []
            removed = list(r_named)
        else:
            named = r_named
            removed = []
        info = {"tier": t, "tier_evidence": ev, "species_qualified": t != "human_assumed",
                "refused": t in ("mouse_confirmed", "mouse_suspected"),
                "no_naming_flags": [c for c, n, s in r if g3_hit(s)],
                "removed": removed, "unranked": removed}
    return r, named, info


# ---- truth 连接 ----
truth = {}
with open("/mnt/D/EyeKB/plans/evalset/scoring/run3_object_B_table_v1.1.tsv") as f:
    rd = csv.DictReader(f, delimiter="\t")
    for row in rd:
        t_ = (row.get("truth") or "").strip()
        if t_ and t_.lower() not in ("nan", "none", ""):
            truth[row["cluster_id"]] = t_

# ---- 输入装配 ----
rows3 = {json.loads(l)["cluster_id"]: json.loads(l)
         for l in open("/mnt/D/EyeKB/plans/evalset/digest/EV_DIGEST_SLIM_v3full.jsonl")}
r7 = {json.loads(l)["cluster_id"]: json.loads(l)
      for l in open("/mnt/D/EyeKB/plans/run7rg_20260926/face/EV_DIGEST_SLIM_run7rg.jsonl")}
LESION = [("Q7::52", r7["Q7::52"]["digest_pool"], "run7rg_digest_pool"),
          ("Q7::58", r7["Q7::58"]["digest_pool"], "run7rg_digest_pool"),
          ("Q7::11", rows3["Q7::11"]["top_genes_sym"][:20], "v3full_sym20"),
          ("Q7::15", rows3["Q7::15"]["top_genes_sym"][:20], "v3full_sym20"),
          ("Q7::21", rows3["Q7::21"]["top_genes_sym"][:20], "v3full_sym20"),
          ("Q7::22", rows3["Q7::22"]["top_genes_sym"][:20], "v3full_sym20"),
          ("Q7::61", rows3["Q7::61"]["top_genes_sym"][:20], "v3full_sym20"),
          ("Q2::22", rows3["Q2::22"]["top_genes_sym"][:20], "v3full_sym20"),
          ("Q5b::35", rows3["Q5b::35"]["top_genes_sym"][:20], "v3full_sym20 (登记不判)")]

# A 基线锚定断言（PREREG §5.1）：Q7::52 A top 含 AC 具名；Q2::22 A top1=MG
rA52, _, _ = apply_B(r7["Q7::52"]["digest_pool"], "B1")
assert any("AC" == c.split("::")[-1] for c, n, s in rA52), "锚定失败: Q7::52 A 响应不含 AC 具名条目"
rA22, _, _ = apply_B(rows3["Q2::22"]["top_genes_sym"][:20], "B1")
assert rA22 and rA22[0][0] == "MG", f"锚定失败: Q2::22 A top1={rA22[0] if rA22 else None} != MG"
print("A 基线锚定 PASS: Q7::52 含 AC 具名条目；Q2::22 top1=MG")

# ---- 病灶集 A/B ----
les_rows = []
for cid, genes, src in LESION:
    A, _ = rank_genes(genes, mk, ow)
    a_named = [c for c, n, s in A]
    rec = {"cluster_id": cid, "input_src": src, "n_genes": len(genes),
           "truth": truth.get(cid, ""), "A_ranking": json.dumps(
               [{"cell_type": c, "n_shared": n, "shared": s} for c, n, s in A], ensure_ascii=False)}
    for var in VARIANTS:
        _, named, info = apply_B(genes, var)
        rec[f"{var}_named"] = json.dumps(named, ensure_ascii=False)
        rec[f"{var}_tier"] = info["tier"]
        rec[f"{var}_removed"] = json.dumps(info["removed"], ensure_ascii=False)
        rec[f"{var}_qualified"] = str(info["species_qualified"])
        rec[f"{var}_flags"] = json.dumps(info.get("no_naming_flags", []), ensure_ascii=False)
    # 判词
    a_artifacts = [c for c, n, s in A]  # A 全部具名条目=候选伪影
    for var in VARIANTS:
        _, named, info = apply_B(genes, var)
        if var == "B1":
            v = "qualified" if info["species_qualified"] else ("flag" if info["no_naming_flags"] else "none")
        else:
            kept = [c for c in named if c in a_artifacts]
            dropped = [c for c in a_artifacts if c not in named]
            if not a_artifacts:
                v = "A_no_artifact"
            elif not named:
                v = "cleared"
            elif not dropped:
                v = "NOT"
            elif kept:
                v = "partial:" + ",".join(kept)
            else:
                v = "cleared"
            if info["tier"] != "human_assumed" and v in ("NOT",) and info.get("species_qualified"):
                v = "NOT(annotated)"
        rec[f"{var}_verdict"] = v
    les_rows.append(rec)

with open(f"{OUT}/data/kbgov_ab_lesion.tsv", "w") as f:
    cols = ["cluster_id", "input_src", "n_genes", "truth", "A_ranking"]
    for var in VARIANTS:
        cols += [f"{var}_named", f"{var}_tier", f"{var}_removed", f"{var}_flags",
                 f"{var}_qualified", f"{var}_verdict"]
    f.write("\t".join(cols) + "\n")
    for rec in les_rows:
        f.write("\t".join(str(rec.get(c, "")) for c in cols) + "\n")

# ---- 回归集（人源 230，剔 Q2::22） ----
reg = [(cid, r["top_genes_sym"][:20]) for cid, r in rows3.items()
       if r["material"]["species"] == "human" and cid != "Q2::22"]
shift_rows, metrics = [], {v: [] for v in VARIANTS}
casualty = {v: [] for v in VARIANTS}
for cid, genes in sorted(reg):
    A, _ = rank_genes(genes, mk, ow)
    a_seq = [c for c, n, s in A]
    for var in VARIANTS:
        _, named, info = apply_B(genes, var)
        if named != a_seq:
            trig = "G3_removal" if info["tier"] == "human_assumed" else f"G1_{info['tier']}"
            shift_rows.append({"variant": var, "cluster_id": cid, "tier": info["tier"],
                               "A": json.dumps(a_seq, ensure_ascii=False),
                               "B": json.dumps(named, ensure_ascii=False),
                               "removed": json.dumps(info["removed"], ensure_ascii=False),
                               "trigger_rule": trig, "truth": truth.get(cid, ""),
                               "correct_name_casualty": str(bool(truth.get(cid)) and a_seq
                                                             and truth[cid] == a_seq[0])})
            metrics[var].append(cid)
        if truth.get(cid) and a_seq and truth[cid] == a_seq[0]:
            if info.get("no_naming_flags") and a_seq[0] in info["no_naming_flags"]:
                casualty[var].append(cid)
            elif a_seq[0] not in named:
                casualty[var].append(cid)
with open(f"{OUT}/out/kbgov_regression_shift.tsv", "w") as f:
    cols = ["variant", "cluster_id", "tier", "A", "B", "removed", "trigger_rule", "truth", "correct_name_casualty"]
    f.write("\t".join(cols) + "\n")
    for r in shift_rows:
        f.write("\t".join(str(r[c]) for c in cols) + "\n")

# ---- 鼠侧账（59 簇，不入门） ----
mouse = [(cid, r["top_genes_sym"][:20]) for cid, r in rows3.items()
         if r["material"]["species"] == "mouse"]
mouse_rows = []
for cid, genes in sorted(mouse):
    A, _ = rank_genes(genes, mk, ow)
    a_seq = [c for c, n, s in A]
    rec = {"cluster_id": cid, "A": json.dumps(a_seq, ensure_ascii=False), "truth": truth.get(cid, "")}
    for var in VARIANTS:
        _, named, info = apply_B(genes, var)
        rec[f"{var}_tier"] = info["tier"]
        rec[f"{var}_shift"] = str(named != a_seq)
        rec[f"{var}_named"] = json.dumps(named, ensure_ascii=False)
    mouse_rows.append(rec)
with open(f"{OUT}/out/kbgov_mouse_side.tsv", "w") as f:
    cols = ["cluster_id", "truth", "A"]
    for var in VARIANTS:
        cols += [f"{var}_tier", f"{var}_shift", f"{var}_named"]
    f.write("\t".join(cols) + "\n")
    for r in mouse_rows:
        f.write("\t".join(str(r[c]) for c in cols) + "\n")

n_reg = len(reg)
res = {"n_regression_human": n_reg,
       "shift_counts": {v: len(metrics[v]) for v in metrics},
       "shift_rate": {v: round(len(metrics[v]) / n_reg, 4) for v in metrics},
       "correct_name_casualty": {v: casualty[v] for v in casualty},
       "gate_5pct": {v: ("FAIL_OVERKILL" if len(metrics[v]) / n_reg > 0.05 else "PASS") for v in metrics},
       "mouse_side_shift_counts": {v: sum(1 for r in mouse_rows if r[f"{v}_shift"] == "True")
                                   for v in VARIANTS},
       "lesion_verdicts": {rec["cluster_id"]: {v: rec[f"{v}_verdict"] for v in VARIANTS}
                           for rec in les_rows}}
json.dump(res, open(f"{OUT}/out/kbgov_ab_metrics.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: res[k] for k in ("shift_counts", "shift_rate", "gate_5pct",
                                      "mouse_side_shift_counts")}, indent=1))
print("casualty:", json.dumps({v: casualty[v] for v in casualty}, ensure_ascii=False))
print("lesion:", json.dumps(res["lesion_verdicts"], ensure_ascii=False, indent=1))
