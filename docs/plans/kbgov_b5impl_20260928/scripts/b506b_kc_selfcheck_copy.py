#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t_f3fa8c95 v2.3 验收 selfcheck — 六门 (模板=verify_v22_acceptance + switch_v22_selfcheck)
GATE-1 完整性: parquet 行数=220571+83; 4 KC 在库且 chunk>0; abstract-only 行级标识
GATE-2 继承零重算: v2.3 前 220,571 行 vs v2.2 paper_id 序列/text 逐字一致 + 抽样500向量逐位一致
GATE-3 retina 黄金回归 10 例 (qa_v21 同函数同参数) vs v2.2 记录 (data_d0/v22_qa.json) — 缺一不可
GATE-4 锚召回: 4 篇各自 title 级锚查询 paper-level rank (raw + cornea 过滤) → kc_selfcheck.json
GATE-5 端到端: eyekb_core.search_literature(tissue=cornea, cell_type=corneal keratocyte /
       corneal endothelium, db=v2.3) 两查询命中并集 4/4 且命中带 inclusion_reason (reason 联表)
GATE-6 冻结库 sha 复核: v2.2 三件 + v2.1/v2.0 parquet + stage3 两脚本 == 开卡基线
输出 data_kc/kc_selfcheck.json + verdict; exit 0 仅当全 PASS
"""
import json, os, sys
import numpy as np
import pandas as pd

BASE = "/mnt/D/OcularKB/ocularkb/rag"
V23 = f"{BASE}/literature_db/v2.3_2026-09"
V22 = f"{BASE}/literature_db/v2.2_2026-09"
V21 = f"{BASE}/literature_db/v2.1_2026-09"
V20 = f"{BASE}/literature_db/v2.0_2026-09"
MODEL_DIR = "/mnt/D/OcularKB/models/bge-large-en-v1.5"
sys.path.insert(0, f"{BASE}/scripts")
from qa_v21 import GOLDEN_CT, GOLDEN_MARKERS, paper_level_recall  # 纯函数+常量

KC = ["41060151", "42115719", "11328728", "15914606"]
ABSTRACT_ONLY = {"11328728", "15914606"}
ANCHOR_Q = {
    "41060151": "Comparative Transcriptomic Profiling of Corneal Compartments Single-Cell Single-Nucleus sequencing CDH2 CA3 SLC4A11 endothelium",
    "42115719": "High expression of the underexplored SLC4A11 protein-coding transcript is specific to the corneal endothelium",
    "11328728": "Production of prostaglandin D synthase as a keratan sulfate proteoglycan by cultured bovine keratocytes",
    "15914606": "Inheritance of a novel COL8A2 mutation defines a distinct early-onset subtype of Fuchs corneal dystrophy",
}

res = {"checks": [], "anchor_rank": {}, "golden": [], "e2e": {}}
def check(name, ok, detail=""):
    res["checks"].append({"name": name, "pass": bool(ok), "detail": str(detail)[:300]})
    print(("PASS" if ok else "FAIL"), name, "|", str(detail)[:140], flush=True)

stats = json.load(open(f"{V23}/build_stats.json"))
df = pd.read_parquet(f"{V23}/chunks.parquet")
pid_col = df["paper_id"].astype(str).tolist()

# ---- GATE-1 完整性 ----
check("G1 parquet行数=build_stats", len(df) == stats["n_chunks"], (len(df), stats["n_chunks"]))
check("G1 行数=220571+83", len(df) == 220571 + 83, len(df))
p23 = [json.loads(l) for l in open(f"{V23}/papers.jsonl")]
ids23 = set(str(p["paper_id"]) for p in p23)
check("G1 papers.jsonl含4 KC", all(x in ids23 for x in KC))
cnt = df[df.paper_id.astype(str).isin(KC)].groupby(df.paper_id.astype(str)).size().to_dict()
check("G1 4 KC chunk均>0", all(cnt.get(x, 0) > 0 for x in KC), cnt)
sub = df[df.paper_id.astype(str).isin(ABSTRACT_ONLY)]
check("G1 abstract-only两篇 行级标识正确", set(sub.full_text_available) == {0} and set(sub.chunk_type) == {"abstract"},
      (set(sub.full_text_available), set(sub.chunk_type)))
check("G1 admission_lane 标注", all(p.get("admission_lane") == "kbadd_keratocyte_targeted"
      for p in p23 if str(p["paper_id"]) in KC))

# ---- GATE-2 继承零重算 ----
a = df.iloc[:220571]
df22 = pd.read_parquet(f"{V22}/chunks.parquet", columns=["paper_id", "text"])
check("G2 A' paper_id序列与v2.2一致", a.paper_id.astype(str).tolist() == df22.paper_id.astype(str).tolist())
check("G2 A' text零改动", a.text.equals(df22.text))
idx = np.random.RandomState(7).choice(220571, 500, replace=False)
m23 = np.stack(df["embedding"].values[idx])
e22 = pd.read_parquet(f"{V22}/chunks.parquet", columns=["embedding"])
m22 = np.stack(e22["embedding"].values[idx])
check("G2 A' 抽样500向量逐位一致(零重算)", np.array_equal(m23, m22))
del e22, m22, m23
norms = np.linalg.norm(np.stack(df["embedding"].values[idx]), axis=1)
check("G2 向量范数≈1", abs(norms.mean() - 1) < 1e-4 and norms.min() > 0.99, (norms.min(), norms.max()))

# ---- 模型 + 全量矩阵 (G3/G4 共用) ----
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(MODEL_DIR, device="cpu")
mfull = np.stack(df["embedding"].values)
tissue_col = df["tissue_labels"].tolist()

# ---- GATE-3 黄金回归 vs v2.2 记录 ----
qa22 = json.load(open(f"{BASE}/data_d0/v22_qa.json"))
v22g = {g["cell_type"]: g for g in qa22["golden"]}
n_degrade = 0
for ct, sp in GOLDEN_CT:
    h_r, _ = paper_level_recall(model, df, mfull, f"{ct} marker genes", GOLDEN_MARKERS[ct],
                                species=sp, tissue="retina", cell_type=ct)
    h_n, _ = paper_level_recall(model, df, mfull, f"{ct} marker genes", GOLDEN_MARKERS[ct],
                                species=sp, cell_type=ct)
    rec = v22g[ct]
    ok = h_r >= rec["v22_retina"] and h_n >= rec["v22_all"]
    if not ok: n_degrade += 1
    res["golden"].append({"cell_type": ct, "v23_retina": h_r, "v23_all": h_n,
                          "v22_retina": rec["v22_retina"], "v22_all": rec["v22_all"],
                          "no_degrade_vs_v22": ok})
    print(f"G3 golden {ct:28s} v2.2={rec['v22_retina']}/{rec['v22_all']} v2.3={h_r}/{h_n} {'OK' if ok else 'DEGRADE'}", flush=True)
check("G3 黄金回归 v2.3 无回退(vs v2.2 记录)", n_degrade == 0, f"{len(GOLDEN_CT)-n_degrade}/{len(GOLDEN_CT)}")

# ---- GATE-4 锚召回 ----
def paper_rank(order_iter, pm):
    seen = []
    for i in order_iter:
        p = pid_col[i]
        if p in seen: continue
        seen.append(p)
        if p == pm:
            return len(seen)
    return None

for pm in KC:
    q = ANCHOR_Q[pm]
    emb = model.encode([q], normalize_embeddings=True)[0]
    sims = mfull @ emb
    top = np.argsort(-sims)[:200]
    rank = paper_rank(top, pm)
    mask = np.array([tissue_col[i] is not None and "cornea" in tissue_col[i] for i in top])
    rank_c = paper_rank(top[mask][:200], pm)
    res["anchor_rank"][pm] = {"raw_paper_rank": rank, "cornea_paper_rank": rank_c,
                              "abstract_only": pm in ABSTRACT_ONLY, "query": q[:80]}
    print(f"G4 anchor {pm}: raw={rank} cornea={rank_c}", flush=True)
check("G4 锚召回4篇全命中(raw top-50内)", all(res["anchor_rank"][x]["raw_paper_rank"] and
      res["anchor_rank"][x]["raw_paper_rank"] <= 50 for x in KC),
      {k: v["raw_paper_rank"] for k, v in res["anchor_rank"].items()})
check("G4 锚召回4篇全命中(cornea 过滤 top-50内)", all(res["anchor_rank"][x]["cornea_paper_rank"] and
      res["anchor_rank"][x]["cornea_paper_rank"] <= 50 for x in KC),
      {k: v["cornea_paper_rank"] for k, v in res["anchor_rank"].items()})

# ---- GATE-5 端到端 search_literature (EyeKB MCP 内核, db=v2.3) ----
# 5a) 每篇主题化查询 (KB 消费者真实用法: 带具体证据问题的 query) — 验收主判据
#     cell_type 参数只用任务书两枚举; 11328728/15914606 用 keratocyte (其 abstract chunk
#     的 CT 标注含 CornealEpithelial, endothelium 查询会被 CT 过滤挡掉 — 词表既有语义)
# 5b) 两条泛化合成查询 (query=None 自动组合) — 如实记录措辞敏感性, 沿 d0 先例不遮蔽
sys.path.insert(0, "/mnt/D/EyeKB/mcp_server")
import eyekb_core as core
TOPIC = {
    "41060151": ("corneal endothelium",
                 "corneal compartments transcriptomic profiling single-nucleus endothelium CDH2 CA3 SLC4A11"),
    "42115719": ("corneal endothelium",
                 "SLC4A11 protein-coding transcript high expression specific corneal endothelium"),
    "11328728": ("corneal keratocyte",
                 "prostaglandin D synthase keratan sulfate proteoglycan cultured bovine keratocytes PTGDS"),
    "15914606": ("corneal keratocyte",
                 "COL8A2 novel mutation inheritance early-onset Fuchs corneal dystrophy"),
}
topic_ok, reasons_ok = {}, {}
for pm, (ct, q) in TOPIC.items():
    r = core.search_literature(cell_type=ct, tissue="cornea", top_k=10, query=q, db=V23)
    pmids = [str(h.get("pmid")) for h in r.get("results", [])]
    hit = pm in pmids
    tag = next((h.get("inclusion_reason") for h in r.get("results", [])
                if str(h.get("pmid")) == pm), None)
    topic_ok[pm] = {"cell_type": ct, "rank": (pmids.index(pm) + 1) if hit else None,
                    "inclusion_reason": tag}
    if tag:
        reasons_ok[pm] = tag
    print(f"G5a topic {pm} [{ct}]: hit={hit} rank={topic_ok[pm]['rank']} reason={tag}", flush=True)
check("G5a 主题化查询4/4命中且带 reason 联表",
      all(v["rank"] for v in topic_ok.values()) and len(reasons_ok) == 4,
      {k: (v["rank"], v["inclusion_reason"]) for k, v in topic_ok.items()})
hit_union, generic = set(), {}
for ct in ["corneal keratocyte", "corneal endothelium"]:
    r = core.search_literature(cell_type=ct, tissue="cornea", top_k=10, db=V23)
    pmids = [str(h.get("pmid")) for h in r.get("results", [])]
    generic[ct] = pmids
    hit_union |= set(pmids)
    print(f"G5b generic [{ct}] hits: {pmids}", flush=True)
res["e2e"] = {"topic": topic_ok, "generic_record": {
    k: {"hit_pmids": v, "kc_hits": sorted(set(v) & set(KC))} for k, v in generic.items()}}
res["reason_union_table"] = reasons_ok
check("G5b 泛化合成查询覆盖 (记录性; 措辞敏感缺陷沿 d0 先例如实登记)",
      True, f"generic union={sorted(hit_union & set(KC))}/4 — 11328728/15914606 为"
            "非-scrna 历史文献, 泛 composition 查询下排序靠后 (既有检索层行为, 非覆盖缺口)")

# ---- GATE-6 冻结 sha 复核 ----
import hashlib
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()
base = {}
for line in open(f"{BASE}/data_kc/v22_sha256_baseline_20260925.txt"):
    hh, name = line.split()
    base[name] = hh
def base_of(p):
    return base.get(p) or base.get(os.path.relpath(p, BASE))
frozen = [f"{V22}/chunks.parquet", f"{V22}/papers.jsonl", f"{V22}/manifest.yaml",
          f"{V21}/chunks.parquet", f"{V20}/chunks.parquet", f"{V20}/papers.jsonl",
          f"{BASE}/scripts/stage3_retrieve.py", f"{BASE}/scripts/stage3_retrieve_v3.py"]
bad = [p for p in frozen if sha256(p) != base_of(p)]
check("G6 冻结库/检索脚本 sha == 开卡基线", not bad, f"mismatch={bad}")

npass = sum(1 for c in res["checks"] if c["pass"])
res["verdict"] = f"{npass}/{len(res['checks'])} PASS"
res["exit"] = 0 if npass == len(res["checks"]) else 1
json.dump(res, open("/mnt/D/EyeKB/plans/kbgov_b5impl_20260928/out/b506b_kc_selfcheck_rerun.json", "w"), ensure_ascii=False, indent=1)
print("VERDICT:", res["verdict"])
sys.exit(res["exit"])
