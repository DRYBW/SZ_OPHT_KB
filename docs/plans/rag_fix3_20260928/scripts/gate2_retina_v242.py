#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RAGFIX3 gate2 (t_b94d0999): 严格 retina 黄金 gate 在 v2.4.2 上的复测 (判据逐字=gate2_retina_v241.py)
- 用例 10 = GOLDEN_CT; query="{ct} marker genes"; 双读=retina 过滤 / 无过滤
- no_degrade_vs_v10 定义 (qa_v21.py:149 同源): v242_retina_hits >= v10_hits OR v242_all_hits >= v10_hits
- 停车线: 用例级不劣化数 < 8/10 (v2.1 基线) → exit 1 (退化停车落卡)
基线 v10 hits 取 qa_v2.json golden_regression (不重算, 保证与既往报告逐字一致)
运行: systemd-run --user -p MemoryMax=20G pipeline_env python gate2_retina_v242.py
"""
import json, os, re, sys, time
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
sys.path.insert(0, f"{BASE}/scripts")
MODEL_DIR = "/mnt/D/OcularKB/models/bge-large-en-v1.5"
V20 = f"{BASE}/literature_db/v2.0_2026-09"
V242 = "/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.4.2_2026-09"
PLAN = "/mnt/D/EyeKB/plans/rag_fix3_20260928"

from stage3_retrieve import _ct_filter_keys
from qa_v21 import GOLDEN_CT, GOLDEN_MARKERS, marker_hit


def paper_level_recall(model, df, emb_matrix, query, markers, species=None, tissue=None,
                       cell_type=None, top_chunks_per_paper=5, n_papers=5, top_n=100):
    emb = model.encode([query], normalize_embeddings=True)[0]
    sims = emb_matrix @ emb
    d = df.assign(_sim=sims)
    if species:
        d = d[d["species"].isin([species, "both"])]
    if tissue and "tissue_labels" in d.columns:
        dt = d[d["tissue_labels"].apply(lambda l: l is not None and tissue in l)]
        if len(dt) >= 30:
            d = dt
    if cell_type:
        keys = _ct_filter_keys(cell_type)
        if keys:
            dt = d[d["cell_type_mentioned"].apply(lambda c: c is not None and any(k in c for k in keys))]
            if len(dt) >= 30:
                d = dt
    d = d.sort_values("_sim", ascending=False).head(top_n)
    by_paper = {}
    for _, r in d.iterrows():
        pid = r["paper_id"]
        if pid not in by_paper:
            by_paper[pid] = []
        if len(by_paper[pid]) < top_chunks_per_paper:
            by_paper[pid].append(r["text"])
    top_papers = []
    for pid, texts in by_paper.items():
        hit = any(marker_hit(t, markers) for t in texts)
        top_papers.append((pid, hit))
    top_papers = top_papers[:n_papers]
    return sum(1 for _, h in top_papers if h), [p for p, _ in top_papers]


def main():
    qa20 = json.load(open(f"{V20}/qa_v2.json"))
    v21 = json.load(open(f"{BASE}/literature_db/v2.1_2026-09/qa_v21.json"))
    v21_by_ct = {g["cell_type"]: g for g in v21["golden_regression"]}
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_DIR, device="cpu")
    print("[load] v2.4.2...", flush=True)
    df42 = pd.read_parquet(f"{V242}/chunks.parquet")
    m42 = np.stack(df42["embedding"].values)
    print(f"  v2.4.2 {len(df42)} chunks", flush=True)
    n_ra3_chunks = sum(1 for _ in open(f"{PLAN}/work/chunks_ra3_raw.jsonl", encoding="utf-8"))
    assert len(df42) == 231707 + n_ra3_chunks, f"corpus row count drift: {len(df42)} != 231707+{n_ra3_chunks}"

    rows = []
    n_ok = n_gate = 0
    for ct, sp in GOLDEN_CT:
        b = next(g for g in qa20["golden_regression"] if g["cell_type"] == ct)
        h42r, pm_r = paper_level_recall(model, df42, m42, f"{ct} marker genes", GOLDEN_MARKERS[ct],
                                        species=sp, tissue="retina", cell_type=ct)
        h42n, pm_n = paper_level_recall(model, df42, m42, f"{ct} marker genes", GOLDEN_MARKERS[ct],
                                        species=sp, cell_type=ct)
        ok = h42r >= b["v10_hits"] or h42n >= b["v10_hits"]
        gate = h42r >= 3 or h42n >= 3
        n_ok += int(ok); n_gate += int(gate)
        v21g = v21_by_ct[ct]
        rows.append({"cell_type": ct, "v10_hits": b["v10_hits"],
                     "v21_retina_hits": v21g["v21_retina_hits"], "v21_all_hits": v21g["v21_all_hits"],
                     "v242_retina_hits": h42r, "v242_all_hits": h42n,
                     "no_degrade_vs_v10": bool(ok), "gate_3of5": bool(gate),
                     "top5_retina": pm_r[:5]})
        print(f"golden {ct:28s} v1.0={b['v10_hits']} v2.1={v21g['v21_retina_hits']}/{v21g['v21_all_hits']} "
              f"v2.4.2={h42r}/{h42n} ok={ok} gate={gate}", flush=True)

    out = {"card": "t_b94d0999", "db": "v2.4.2_2026-09",
           "case_level_no_degrade": f"{n_ok}/10", "gate_level": f"{n_gate}/10",
           "baseline_v21_case_level": "8/10",
           "verdict": "PASS" if (n_ok >= 8 and n_gate == 10) else "FAIL_STOP",
           "rows": rows, "written_at": time.strftime("%F %T")}
    os.makedirs(f"{PLAN}/out", exist_ok=True)
    json.dump(out, open(f"{PLAN}/out/GATE2_RETINA_v242.json", "w"), indent=1, ensure_ascii=False)
    print("DONE", out["case_level_no_degrade"], out["gate_level"], out["verdict"], flush=True)
    sys.exit(0 if out["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
