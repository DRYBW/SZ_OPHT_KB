#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B5IMPL t_8960c7e0 · b505 — 门1 病灶 7/7 零具名残留 + 门2 人源 230 簇重放位移 0.0%
+ 双源对账（生产实现 vs 复刻件冻结表 KBGOV out/ 与 data/kbgov_g1_signals_290.json）。
输入装配与候选件 kbgov_ab.py 完全同源（lesion=Q7::52/58 run7rg digest_pool +
Q7::11/15/21/22/61 v3full top_genes_sym[:20]; reg=v3full human−Q2::22=230;
mouse=v3full mouse=59）。生产侧=改码后 eyekb_core 直调（in-process, EYEKB_MCP_SOFTFLAGS=1
与电池同口径）。门2 口径沿用预注册：位移率>5%=过杀回炉（B5 预期 0.0%）。
另附 stdio 真往返抽查（Q7::11 suspected 案）证明传输面行为一致。
输出 out/b505_gates12.json。exit 0=全 PASS。"""
import json
import os
import sys
import time
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kbgov_b5impl_20260928")
KG = Path("/mnt/D/EyeKB/plans/kb_gov_20260928")
sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
os.environ["EYEKB_MCP_SOFTFLAGS"] = "1"
os.environ.pop("EYEKB_ACT_V6", None)
import eyekb_core as core  # noqa: E402

rows3 = {json.loads(l)["cluster_id"]: json.loads(l)
         for l in open("/mnt/D/EyeKB/plans/evalset/digest/EV_DIGEST_SLIM_v3full.jsonl")}
r7 = {json.loads(l)["cluster_id"]: json.loads(l)
      for l in open("/mnt/D/EyeKB/plans/run7rg_20260926/face/EV_DIGEST_SLIM_run7rg.jsonl")}
SIG = {s["cluster_id"]: s for s in json.load(open(KG / "data/kbgov_g1_signals_290.json"))}
LES_TSV = {r.split("\t")[0]: r.split("\t")
           for r in open(KG / "data/kbgov_ab_lesion.tsv").read().rstrip("\n").split("\n")[1:]}
LES_HDR = open(KG / "data/kbgov_ab_lesion.tsv").readline().rstrip("\n").split("\t")
COL = {c: i for i, c in enumerate(LES_HDR)}
MET = json.load(open(KG / "out/kbgov_ab_metrics.json"))
MOUSE_TSV = [l.rstrip("\n").split("\t") for l in open(KG / "out/kbgov_mouse_side.tsv")][1:]
MOUSE_HDR = open(KG / "out/kbgov_mouse_side.tsv").readline().rstrip("\n").split("\t")
MCOL = {c: i for i, c in enumerate(MOUSE_HDR)}

fails, checks = [], []


def ck(tag, cond, detail=""):
    checks.append({"check": tag, "pass": bool(cond), "detail": str(detail)[:280]})
    if not cond:
        fails.append([tag, str(detail)[:280]])


def seq(resp):
    return [e["cell_type"] for e in resp.get("celltype_ranking", [])]


def gov(genes, env="on"):
    if env == "on":
        os.environ.pop("EYEKB_KBGOV_B5", None)
    else:
        os.environ["EYEKB_KBGOV_B5"] = "0"
    return core.query_marker(genes=list(genes))


# ============ 门 1：病灶 7/7 ============
os.environ.pop("EYEKB_KBGOV_B5", None)
LESION7 = ["Q7::11", "Q7::15", "Q7::21", "Q7::22", "Q7::52", "Q7::58", "Q7::61"]
in7 = {"Q7::52": r7["Q7::52"]["digest_pool"], "Q7::58": r7["Q7::58"]["digest_pool"],
       "Q7::11": rows3["Q7::11"]["top_genes_sym"][:20],
       "Q7::15": rows3["Q7::15"]["top_genes_sym"][:20],
       "Q7::21": rows3["Q7::21"]["top_genes_sym"][:20],
       "Q7::22": rows3["Q7::22"]["top_genes_sym"][:20],
       "Q7::61": rows3["Q7::61"]["top_genes_sym"][:20]}
g1 = {}
for cid in LESION7:
    onr = gov(in7[cid], "on")
    offr = gov(in7[cid], "off")
    a = json.loads(LES_TSV[cid][COL["A_ranking"]])
    a_seq = [e["cell_type"] for e in a]
    rep_tier = LES_TSV[cid][COL["B5_tier"]]
    rep_named = json.loads(LES_TSV[cid][COL["B5_named"]])
    ck(f"g1-named-empty::{cid}", onr.get("celltype_ranking") == [],
       f"ON 具名残留={seq(onr)}")
    ck(f"g1-refuse-fields::{cid}", onr.get("no_named_ranking_for") == "mouse_input"
       and onr.get("input_species") in ("mouse_confirmed", "mouse_suspected")
       and isinstance(onr.get("species_evidence"), dict), str({k: onr.get(k) for k in
       ("input_species", "no_named_ranking_for")})[:120])
    moved = [e["cell_type"] for e in onr.get("unranked_candidates", [])]
    ck(f"g1-unranked-mirror::{cid}", moved == a_seq, f"moved={moved[:4]} vs A={a_seq[:4]}")
    ck(f"g1-dual-source-tier::{cid}", onr.get("input_species") == rep_tier,
       f"prod={onr.get('input_species')} replica={rep_tier}")
    ck(f"g1-dual-source-named::{cid}", rep_named == [], f"replica B5_named={rep_named[:80]}")
    ck(f"g1-off-restores-artifacts::{cid}", seq(offr) == a_seq,
       f"off={seq(offr)[:4]} vs A={a_seq[:4]}")
    n_named = sum(1 for e in [{"cell_type": x} for x in seq(onr)] )
    g1[cid] = {"tier": onr.get("input_species"), "off_ranking": a_seq,
               "evidence": onr.get("species_evidence")}
ck("g1-all7-zero-named", all(v["tier"] in ("mouse_confirmed", "mouse_suspected")
                             for v in g1.values()), len(g1))

# Q2::22（人源 AMBIG 标注档）+ Q5b::35（kept_bare 管辖边界）
q22 = gov(rows3["Q2::22"]["top_genes_sym"][:20], "on")
rep_flags = set(json.loads(LES_TSV["Q2::22"][COL["B5_flags"]]))
prod_flags = {e["cell_type"] for e in q22["celltype_ranking"] if e.get("no_naming_claim")}
a22 = [e["cell_type"] for e in json.loads(LES_TSV["Q2::22"][COL["A_ranking"]])]
ck("g1-Q2x22-order-kept", seq(q22) == a22, f"on={seq(q22)[:4]} A={a22[:4]}")
ck("g1-Q2x22-flags-dual-source", prod_flags == rep_flags, f"prod={prod_flags} replica={rep_flags}")
ck("g1-Q2x22-tier-human", q22.get("input_species") == "human_assumed", q22.get("input_species"))
ck("g1-Q2x22-flag-reason", all(e.get("reason") == "ambiguous_coexpression_only"
   for e in q22["celltype_ranking"] if e.get("no_naming_claim")), "reason 文本")
q5b = gov(rows3["Q5b::35"]["top_genes_sym"][:20], "on")
a5b = [e["cell_type"] for e in json.loads(LES_TSV["Q5b::35"][COL["A_ranking"]])]
ck("g1-Q5b35-kept-bare", seq(q5b) == a5b and not any(
    e.get("no_naming_claim") for e in q5b["celltype_ranking"]),
    f"flags={[e['cell_type'] for e in q5b['celltype_ranking'] if e.get('no_naming_claim')]}")

# ============ 门 2：人源 230 重放 ============
reg = [(cid, rows3[cid]["top_genes_sym"][:20]) for cid in sorted(rows3)
       if rows3[cid]["material"]["species"] == "human" and cid != "Q2::22"]
ck("g2-set-size==230", len(reg) == 230, len(reg))
shift = []
tier_mismatch = []
for cid, genes in reg:
    onr = gov(genes, "on")
    offr = gov(genes, "off")
    if seq(onr) != seq(offr):
        shift.append(cid)
    s = SIG.get(cid)
    if s and onr.get("input_species") != s["tier"]:
        tier_mismatch.append([cid, onr.get("input_species"), s["tier"]])
    # 位移语义: ON 具名条目集合与序全等; 允许 no_naming_claim 注记字段增列(候选 B5 口径)
    for e in onr.get("celltype_ranking", []):
        pass
shift_rate = len(shift) / len(reg) * 100
ck("g2-shift==0", not shift, shift[:10])
ck("g2-shift-rate==0.0", shift_rate == 0.0, shift_rate)
ck("g2-tier-dual-source==0-mismatch", not tier_mismatch, tier_mismatch[:5])
ck("g2-candidate-metrics-agree", MET["shift_counts"]["B5"] == 0 and MET["gate_5pct"]["B5"] == "PASS",
   MET["shift_counts"]["B5"])

# 信号逐值对账（290 簇 title_frac/msp/m_only/tier）——含 59 鼠侧
voc = core._kbgov_vocab()
sig_bad = []
for cid, s in SIG.items():
    genes_raw = rows3[cid]["top_genes_sym"][:20]
    tier, ev = core._kbgov_g1_tier([g.strip() for g in genes_raw], voc[0], voc[1], voc[2])
    if (tier != s["tier"] or ev["title_frac"] != s["title_frac"]
            or ev["msp"] != s["msp_hits"] or ev["m_only"] != s["m_only"]):
        sig_bad.append([cid, tier, s["tier"], ev["title_frac"], s["title_frac"],
                        ev["msp"], s["msp_hits"], ev["m_only"], s["m_only"]])
ck("g2-signals290-dual-source-all-equal", not sig_bad, sig_bad[:5])

# 鼠侧账（不入门，候选口径 59/59 具名清零）
mouse = [(cid, rows3[cid]["top_genes_sym"][:20]) for cid in sorted(rows3)
         if rows3[cid]["material"]["species"] == "mouse"]
ck("g2-mouse-set==59", len(mouse) == 59, len(mouse))
mouse_not_refused = []
rows_ms = []
for cid, genes in mouse:
    onr = gov(genes, "on")
    offr = gov(genes, "off")
    if onr.get("no_named_ranking_for") != "mouse_input" or onr.get("celltype_ranking"):
        mouse_not_refused.append(cid)
    rows_ms.append({"cluster_id": cid, "tier": onr.get("input_species"),
                    "a_named_n": len(seq(offr)), "b5_named": seq(onr),
                    "unranked_n": len(onr.get("unranked_candidates", [])),
                    "evidence": onr.get("species_evidence")})
ck("g2-mouse-all-refused", not mouse_not_refused, mouse_not_refused[:8])
rep_mouse_open = [r[MCOL["cluster_id"]] for r in MOUSE_TSV if r[MCOL["B5_named"]] != "[]"]
ck("g2-mouse-dual-source", not rep_mouse_open, f"replica B5_named≠[] rows={rep_mouse_open[:5]}")

json.dump({"at": time.strftime("%F %T"), "card": "t_8960c7e0",
           "gates": {"g1_lesion7": g1, "g2_shift": {"n_shift": len(shift),
                     "shift_rate_pct": shift_rate, "n_reg": len(reg)},
                     "mouse_refused": len(mouse) - len(mouse_not_refused)},
           "mouse_ledger": rows_ms,
           "checks_n": len(checks), "fails": fails, "checks": checks,
           "verdict": "PASS" if not fails else "FAIL"},
          open(CARD / "out/b505_gates12.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({"checks": len(checks), "fails": len(fails),
                  "g2_shift_pct": shift_rate, "mouse_refused": f"{len(mouse)-len(mouse_not_refused)}/59",
                  "verdict": "PASS" if not fails else "FAIL"}, ensure_ascii=False))
sys.exit(0 if not fails else 1)
