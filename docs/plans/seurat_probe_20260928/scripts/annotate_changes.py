#!/usr/bin/env python3
"""Annotate number2 change lists with literature support from kb marker libs (v4.1/v6)."""
import json, re
W = "<EYEKB>/plans/seurat_probe_20260928"
import pandas as pd

v4 = json.load(open("<EYEKB>/kb/markers/markers_v4.1_clean.json"))
v6 = json.load(open("<EYEKB>/kb/markers/markers_v6_retina_repair.json"))
CLASSES = sorted(set(v4["markers"]) | set(v6.get("markers", {})))

def find_pmids(node, best=None):
    out = set()
    def rec(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.lower() == "pmid":
                    out.add(str(v))
                rec(v)
        elif isinstance(o, list):
            for x in o: rec(x)
        elif isinstance(o, str):
            out.update(re.findall(r"PMID[:\s](\d{7,8})", o))
    rec(node)
    return out

# class->pmids: scan per-class subtrees in v6 wherever class name keys appear
pm_by_class = {}
def rec(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in CLASSES:
                s = find_pmids(v)
                pm_by_class.setdefault(k, set()).update(s)
            rec(v, path + "/" + k)
    elif isinstance(o, list):
        for x in o: rec(x, path)
rec(v6, "")
print("v6 class->PMIDs:", {k: sorted(v) for k, v in pm_by_class.items()})

def support(cls):
    inlib = cls in CLASSES
    pms = sorted(pm_by_class.get(cls, []))[:6]
    if inlib and pms: return f"kb词条({cls}, v4.1/v6)+PMID:{','.join(pms)}"
    if inlib: return f"kb词条({cls}, markers_v4.1_clean 冻结表; v6 无逐类PMID)—单条文献待补"
    return "无支持，存疑"

for tag in ["DS1", "DS2"]:
    p = f"{W}/tables/number2_changes_S_vs_P_{tag}.csv"
    df = pd.read_csv(p)
    df["kb_support_S"] = df["S_call"].map(support)
    df["kb_support_P"] = df["P_dom"].map(support)
    df.to_csv(p, index=False)
    print(tag, "changed rows:", int(df["changed"].sum()))
