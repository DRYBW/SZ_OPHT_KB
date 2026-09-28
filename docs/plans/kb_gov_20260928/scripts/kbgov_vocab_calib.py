#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kbgov_vocab_calib.py — §1.3 词表提取 + §4 G1 校准（零 LLM、全本地、先于 B 跑）。
产物: data/kbgov_vocab_stats.json, data/kbgov_g1_calibration.json（含 title_frac 分布极值/间隙/T
      及 290 簇逐簇信号 + 病灶池信号），均带 sha 台账。"""
import json, re, gzip, csv, sys, os

OUT = "/mnt/D/EyeKB/plans/kb_gov_20260928"

# ---- HUMSYM: NCBI human gene_info Symbol ∪ Synonyms (uppercase forms) ----
hum = set()
with gzip.open("/mnt/D/OcularKB/data/ncbi_orthologs/gene_info/Homo_sapiens.gene_info.gz",
               "rt", encoding="latin-1", errors="ignore") as fh:
    rd = csv.reader(fh, delimiter="\t", quotechar='"')
    hdr = next(rd)
    i_sym, i_syn = hdr.index("Symbol"), hdr.index("Synonyms")
    for row in rd:
        if len(row) <= i_syn:
            continue
        s = row[i_sym].strip()
        if s:
            hum.add(s.upper())
        for x in row[i_syn].split("|"):
            x = x.strip()
            if x and x != "-":
                hum.add(x.upper())
print("HUMSYM:", len(hum))

# ---- MOUSYM: Ensembl mouse 104 GTF gene_name (原形 + upper 双形态) ----
m_raw, m_up = set(), set()
pat_gene = re.compile(r'gene_name "([^"]+)"')
with gzip.open("/mnt/D/OcularKB/data/ensembl_gtf_104/mus_musculus.104.gtf.gz",
               "rt", encoding="latin-1", errors="ignore") as fh:
    for line in fh:
        if line.startswith("#"):
            continue
        m = pat_gene.search(line)
        if m:
            g = m.group(1)
            m_raw.add(g)
            m_up.add(g.upper())
print("MOUSYM raw:", len(m_raw), "upper:", len(m_up))

# ---- ORTH11 frozen ----
h2m = json.load(open("/mnt/D/EyeKB/plans/mouse_model_20260925/work_t_a5d05be3/human2mouse_1to1_symbols.json"))
print("ORTH11:", len(h2m))

json.dump({"HUMSYM_n": len(hum), "MOUSYM_raw_n": len(m_raw), "MOUSYM_upper_n": len(m_up),
           "ORTH11_n": len(h2m),
           "sources": {"HUMSYM": "ncbi gene_info Homo_sapiens Symbol+Synonyms upper",
                       "MOUSYM": "ensembl_gtf_104 mus_musculus gene_name",
                       "ORTH11": "mouse_model_20260925 work human2mouse_1to1_symbols.json"}},
          open(f"{OUT}/data/kbgov_vocab_stats.json", "w"), indent=1, ensure_ascii=False)

# 供后续脚本复用：紧凑落盘符号集
json.dump({"hum": sorted(hum), "m_raw": sorted(m_raw), "m_up": sorted(m_up), "h2m": h2m},
          gzip.open(f"{OUT}/data/kbgov_vocab.json.gz", "wt", encoding="utf-8"))

# ---- G1 信号 per cluster (v3full 290) ----
P_MSP = [(re.compile(r"^Gm\d+$"), "Gm"), (re.compile(r"Rik$"), "Rik")]


def signals(genes):
    letters = [g for g in genes if re.search(r"[A-Za-z]", g)]
    title = [g for g in letters if (not g.isupper()) and re.match(r"^[A-Z][a-z]", g)]
    msp = [g for g in genes if any(p[0].match(g) or p[0].search(g) for p in P_MSP)]
    monly = [g for g in genes if g.upper() not in hum and g.upper() in m_up]
    nonhum = [g for g in genes if g.upper() not in hum]
    return {"n": len(genes), "title_frac": round(len(title) / max(len(letters), 1), 4),
            "msp_hits": len(msp), "m_only": len(monly), "not_in_human": len(nonhum),
            "msp_ex": msp[:3], "m_only_ex": monly[:3], "nonhum_ex": nonhum[:5]}


rows = [json.loads(l) for l in open(f"/mnt/D/EyeKB/plans/evalset/digest/EV_DIGEST_SLIM_v3full.jsonl")]
cal = []
for r in rows:
    s = signals(r["top_genes"])
    s["cluster_id"] = r["cluster_id"]
    s["species_label"] = r["material"]["species"]
    cal.append(s)

hu_t = sorted(c["title_frac"] for c in cal if c["species_label"] == "human")
mo_t = sorted(c["title_frac"] for c in cal if c["species_label"] == "mouse")
# 最大间隙分隔点 = 标注两侧经验分布间隙的中点（PREREG §4；网格扫描取"存在干净间隙"的证据）
gap = min(mo_t) - max(hu_t)
grid_clean = [i / 20.0 for i in range(1, 20)
              if sum(1 for x in hu_t if x >= i / 20.0) == 0
              and sum(1 for x in mo_t if x < i / 20.0) == 0]
best = {"t": round((max(hu_t) + min(mo_t)) / 2, 4), "gap": round(gap, 4),
        "grid_clean_range": [grid_clean[0], grid_clean[-1]] if grid_clean else None}
mism = {"human_msp_or_monly": [c["cluster_id"] for c in cal
                               if c["species_label"] == "human" and (c["msp_hits"] + c["m_only"]) > 0],
        "mouse_no_corroboration": [c["cluster_id"] for c in cal
                                   if c["species_label"] == "mouse" and (c["msp_hits"] + c["m_only"]) == 0]}
out = {"hu_title_min_max": [hu_t[0], hu_t[-1]], "mo_title_min_max": [mo_t[0], mo_t[-1]],
       "separator": best, "T_frozen": best["t"] if best else 0.5,
       "mismatches": mism,
       "note": "T=最大间隙分隔点（PREREG §4）；mouse_no_corroboration=只靠大小写惯例判定的簇（suspected 档，边界样例逐簇列出）"}
json.dump(out, open(f"{OUT}/data/kbgov_g1_calibration.json", "w"), indent=1, ensure_ascii=False)
json.dump(cal, open(f"{OUT}/data/kbgov_g1_signals_290.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))

# 病灶池信号
pools = {}
for l in open("/mnt/D/EyeKB/plans/run7rg_20260926/face/EV_DIGEST_SLIM_run7rg.jsonl"):
    r = json.loads(l)
    if r["cluster_id"] in ("Q7::52", "Q7::58"):
        pools[r["cluster_id"] + "_run7rg_pool"] = signals(r["digest_pool"])
for r in rows:
    if r["cluster_id"] in ("Q7::11", "Q7::15", "Q7::21", "Q7::22", "Q7::61", "Q2::22", "Q5b::35"):
        pools[r["cluster_id"]] = signals(r["top_genes"])
json.dump(pools, open(f"{OUT}/data/kbgov_lesion_signals.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(pools, indent=1, ensure_ascii=False))
