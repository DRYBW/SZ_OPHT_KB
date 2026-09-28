#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kbgov_calib2.py — G1 校准重跑（canonical 输入列 = top_genes_sym，PREREG v1.1 §1）。
旧件保留为 data/kbgov_g1_calibration.v1.0-col.json。T 取标注两侧 title_frac 经验间隙中点。"""
import json, re, gzip

OUT = "/mnt/D/EyeKB/plans/kb_gov_20260928"
V = json.load(gzip.open(f"{OUT}/data/kbgov_vocab.json.gz", "rt", encoding="utf-8"))
hum, m_raw, m_up, h2m = set(V["hum"]), set(V["m_raw"]), set(V["m_up"]), V["h2m"]
P_MSP_GM = re.compile(r"^Gm\d+$")
P_MSP_RIK = re.compile(r"Rik$")
TITLE = re.compile(r"^[A-Z][a-z]")


def signals(genes):
    letters = [g for g in genes if re.search(r"[A-Za-z]", g)]
    title = [g for g in letters if (not g.isupper()) and TITLE.match(g)]
    msp = [g for g in genes if P_MSP_GM.match(g) or P_MSP_RIK.search(g)]
    monly = [g for g in genes if g.upper() not in hum and (g.upper() in m_up or g in m_raw)]
    return {"n": len(genes),
            "title_frac": round(len(title) / max(len(letters), 1), 4),
            "msp_hits": len(msp), "m_only": len(monly),
            "msp_ex": msp[:3], "m_only_ex": monly[:3]}


rows = [json.loads(l) for l in open("/mnt/D/EyeKB/plans/evalset/digest/EV_DIGEST_SLIM_v3full.jsonl")]
cal = []
for r in rows:
    s = signals(r["top_genes_sym"][:20])
    s.update({"cluster_id": r["cluster_id"], "species_label": r["material"]["species"]})
    cal.append(s)

hu_t = sorted(c["title_frac"] for c in cal if c["species_label"] == "human")
mo_t = sorted(c["title_frac"] for c in cal if c["species_label"] == "mouse")
gap = min(mo_t) - max(hu_t)
T = round((max(hu_t) + min(mo_t)) / 2, 4)
# 判定档（冻结形态，PREREG §3 G1）
def tier(c):
    conf = c["title_frac"] >= T and (c["msp_hits"] >= 1 or c["m_only"] >= 1)
    susp = c["title_frac"] >= T and not conf
    return "mouse_confirmed" if conf else ("mouse_suspected" if susp else "human_assumed")
tiers = {}
for c in cal:
    c["tier"] = tier(c)
    tiers[c["tier"]] = tiers.get(c["tier"], 0) + 1
    c["would_misdetect"] = (c["species_label"] == "human" and c["tier"] != "human_assumed")
mis_hu = [c["cluster_id"] for c in cal if c["would_misdetect"]]
mou_susp = [c["cluster_id"] for c in cal if c["species_label"] == "mouse" and c["tier"] == "mouse_suspected"]

out = {"input_col": "top_genes_sym[:20]", "T_frozen": T,
       "hu_title_min_max": [hu_t[0], hu_t[-1]], "mo_title_min_max": [mo_t[0], mo_t[-1]],
       "gap": round(gap, 4), "tiers_counts": tiers,
       "human_misdetections": mis_hu,
       "mouse_suspected_only_convention": mou_susp,
       "note": "confirmed=suspected 之外的鼠源档需佐证（Gm/Rik/m_only）；suspected 仅惯例证据；人源误判清单=misdetections（B 位移前哨）"}
json.dump(out, open(f"{OUT}/data/kbgov_g1_calibration.json", "w"), indent=1, ensure_ascii=False)
json.dump(cal, open(f"{OUT}/data/kbgov_g1_signals_290.json", "w"), indent=1, ensure_ascii=False)

pools = {"Q7::52": {"genes": None}}
# 病灶 canonical 信号
r7 = {json.loads(l)["cluster_id"]: json.loads(l) for l in
      open("/mnt/D/EyeKB/plans/run7rg_20260926/face/EV_DIGEST_SLIM_run7rg.jsonl")}
les = {}
for cid in ("Q7::52", "Q7::58"):
    s = signals(r7[cid]["digest_pool"]); s["input"] = "run7rg_digest_pool"; s["tier"] = tier(s)
    les[cid] = s
for cid in ("Q7::11", "Q7::15", "Q7::21", "Q7::22", "Q7::61", "Q2::22", "Q5b::35"):
    c = [x for x in cal if x["cluster_id"] == cid][0]
    s = {k: c[k] for k in ("n", "title_frac", "msp_hits", "m_only", "msp_ex", "m_only_ex", "tier")}
    s["input"] = "v3full_top_genes_sym20"
    les[cid] = s
json.dump(les, open(f"{OUT}/data/kbgov_lesion_signals.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(les, indent=1, ensure_ascii=False))
