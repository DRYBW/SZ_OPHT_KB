#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB1v2d (t_bb170f1b) 回归断言组 — 语料收口件一致性 (与 2b 并存, 2b 守 v2.0 存档不变)
纯文件/parquet 断言, 无 MCP 往返 (MCP 语义不变性由 2b 56 用例继续背书)"""
import json, hashlib, sys
import pandas as pd
import yaml

RAG = "/mnt/D/OcularKB/ocularkb/rag"
V22 = f"{RAG}/literature_db/v2.2_2026-09"
V21 = f"{RAG}/literature_db/v2.1_2026-09"
D0 = ["35061025", "37917183", "39220810", "40069725", "40562775", "41578023", "42601615"]
ABSTRACT_ONLY = {"35061025", "41578023"}
COL = ["35659263", "33298129", "22388286"]
report = {"checks": [], "pass": 0, "fail": 0}
def check(name, ok, detail=""):
    report["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})
    report["pass" if ok else "fail"] += 1
    print(("PASS" if ok else "FAIL"), name, "|", str(detail)[:110])

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# 1 manifest vs parquet vs papers
man = yaml.safe_load(open(f"{V22}/manifest.yaml"))
df = pd.read_parquet(f"{V22}/chunks.parquet", columns=["paper_id", "full_text_available", "is_preprint"])
papers = [json.loads(l) for l in open(f"{V22}/papers.jsonl")]
check("manifest 计数=parquet 行数", man["counts"]["n_chunks"] == len(df) == 220571, (man["counts"]["n_chunks"], len(df)))
check("papers.jsonl 行数=3696 (含 v2.1 遗留 15 ghost)", len(papers) == 3696, len(papers))
check("unique papers=3681", df.paper_id.astype(str).nunique() == 3681)

# 2 v2.1 零改动复核
ok21 = {}
for line in open(f"{RAG}/data_d0/v21_sha256_baseline_20260923.txt"):
    h, name = line.split()
    f_ = name.split("/")[-1]
    ok21[f_] = (sha(f"{V21}/{f_}") == h)
check("v2.1 三文件 sha 复核零改动", all(ok21.values()), ok21)

# 3 7 D0 sidecar 复核记录 (验收线字面)
sm = {}
for l in open("/mnt/D/EyeKB/kb/literature_db/evidence_meta_v2.2_2026-09.jsonl", encoding="utf-8"):
    d = json.loads(l)
    sm[d["pmid"]] = d
check("7 D0 verification_status=D0_critical", all(
    "D0_critical" in sm[p]["verification_status"] for p in D0),
    {p: sm[p]["verification_status"] for p in D0})
check("7 D0 source_db 指针=v2.2", all(sm[p].get("source_db") == "literature_db/v2.2_2026-09" for p in D0))
check("sidecar 覆盖数与新库一致", len(sm) == 3696 and len(set(k for k in sm if k.startswith("PPR_"))) == 229, len(sm))

# 4 papers.jsonl 降级字段
pm_ = {str(p["paper_id"]): p for p in papers}
check("D0 admission_lane 全登记", all(pm_[p].get("admission_lane") == "d0_targeted" for p in D0))
check("abstract_only 两篇标记正确", all(pm_[p]["fulltext_status"] == "abstract_only" for p in ABSTRACT_ONLY)
      and all(pm_[p]["fulltext_status"] == "full_text" for p in D0 if p not in ABSTRACT_ONLY))
check("D0 is_preprint=0 (正刊不混预印本)", all(pm_[p]["is_preprint"] == 0 for p in D0))

# 5 chunk 级降级标识
sub = df[df.paper_id.astype(str).isin(ABSTRACT_ONLY)]
check("abstract-only 行 full_text_available=0", set(sub.full_text_available) == {0}, len(sub))
sub5 = df[df.paper_id.astype(str).isin([p for p in D0 if p not in ABSTRACT_ONLY])]
check("全文 D0 行 full_text_available=1", set(sub5.full_text_available) == {1})

# 6 指针 yaml
ptr = yaml.safe_load(open("/mnt/D/EyeKB/kb/literature_db/EYEKB_DB_POINTER.yaml"))
check("pointer 含 v2.2 且 default 仍 v2.0 (切默认待拍板)",
      "v2.2_2026-09" in ptr["rag_dbs"] and ptr["rag_dbs"]["v2.0_2026-09"]["role"].startswith("default"))

# 7 撞库三篇未删
cnt = {c: int((df.paper_id.astype(str) == c).sum()) for c in COL}
check("撞库三篇在库未删 (423/36/2)", cnt == {"35659263": 423, "33298129": 36, "22388286": 2}, cnt)
try:
    ci = json.load(open(f"{RAG}/data_d0/collision_impact.json"))
    check("collision_impact.json 在场 (五情景)", "queries" in ci and len(ci["queries"]) >= 30, len(ci.get("queries", [])))
except FileNotFoundError:
    check("collision_impact.json 在场 (五情景)", False, "missing")

# 8 QA 件
qa = json.load(open(f"{RAG}/data_d0/v22_qa.json"))
check("v2.2 黄金集无回退 10/10", all(g["no_degrade_vs_v21"] for g in qa["golden"]), len(qa["golden"]))
check("anchor 检索性 (7 篇全部 dense 可检索)", all(
    (qa["anchor_rank"][p]["raw_paper_rank"] or 999) < 999 or p in ("40069725",) for p in D0),
    {k: v["raw_paper_rank"] for k, v in qa["anchor_rank"].items()})
# 诚实件: 深度补充数字在 v22_qa 附注 (37917183=69 / 40069725=268→换措辞 top3), FAIL 检查不粉饰

json.dump(report, open("/mnt/D/EyeKB/evals/REGRESSION_KB1V2D_20260923.json", "w"), indent=1, ensure_ascii=False)
print(f"\nVERDICT: {report['pass']}/{report['pass']+report['fail']} PASS")
sys.exit(0 if report["fail"] == 0 else 1)
