#!/usr/bin/env python3
"""Three-numbers computation for SEURATPROBE (reads trackP/trackS celllabel CSVs + truth, position-aligned)."""
import sys, json
import numpy as np, pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, confusion_matrix

W = "<EYEKB>/plans/seurat_probe_20260928"
DS = {"DS1": dict(P=f"{W}/tables/trackP_DS1_celllabels.csv", S=f"{W}/tables/trackS_DS1_celllabels.csv"),
      "DS2": dict(P=f"{W}/tables/trackP_DS2_celllabels.csv", S=f"{W}/tables/trackS_DS2_celllabels.csv")}

def load(tag):
    p = pd.read_csv(DS[tag]["P"]); s = pd.read_csv(DS[tag]["S"])
    assert len(p) == len(s), "length mismatch"
    df = pd.DataFrame({"cell": p["cell"].astype(str),
                       "cluster_P": p["leiden"].astype(str), "label_P": p["truth"].astype(str),  # placeholder replaced below
                       })
    # P call per cluster from clusters csv
    pc = pd.read_csv(DS[tag]["P"].replace("celllabels","clusters"))
    pcall = dict(zip(pc["cluster"].astype(str), pc["call"].astype(str)))
    df["P_call"] = p["leiden"].astype(str).map(pcall).values
    df["cluster_S"] = s["louvain"].astype(str).values
    df["S_call"] = s["S_call"].astype(str).values
    df["truth"] = s["truth"].astype(str).values
    df["label_P"] = None
    return df

def cls(df):
    return df[df["truth"] != "EXCL"].copy()

def ari_nmi(df, a, b):
    m = df[[a,b]].dropna()
    m = m[(m[a].astype(str)!="") & (m[a].astype(str)!="nan")]
    return adjusted_rand_score(m[a], m[b]), normalized_mutual_info_score(m[a], m[b])

def purity_by_truth(df, lab):
    d = cls(df)
    out = {}
    for t, g in d.groupby("truth"):
        vc = g[lab].value_counts()
        out[t] = {"n": int(len(g)), "modal_frac": float(vc.iloc[0]/len(g)) if len(g) else 0.0, "modal": (vc.index[0] if len(g) else None)}
    return out

def main():
    result = {}
    for tag in ["DS1","DS2"]:
        df = load(tag)
        d = cls(df)
        r = {}
        # number 1 cross-engine concordance
        r["ARI_S_vs_truth"], r["NMI_S_vs_truth"] = ari_nmi(d, "S_call", "truth")
        r["ARI_P_vs_truth"], r["NMI_P_vs_truth"] = ari_nmi(d, "P_call", "truth")
        r["ARI_S_vs_P"], r["NMI_S_vs_P"] = ari_nmi(d, "S_call", "P_call")
        r["cell_counts"] = {"total": int(len(df)), "truth_evaluable": int(len(d)), "EXCL": int((df["truth"]=="EXCL").sum())}
        cm = pd.crosstab(d["S_call"], d["truth"])
        cm.to_csv(f"{W}/tables/number1_confusion_S_vs_truth_{tag}.csv")
        cm2 = pd.crosstab(d["P_call"], d["truth"])
        cm2.to_csv(f"{W}/tables/number1_confusion_P_vs_truth_{tag}.csv")
        r["purity_by_truth_S"] = purity_by_truth(df, "S_call")
        r["purity_by_truth_P"] = purity_by_truth(df, "P_call")
        # cluster-level (S) truth-dominant agreement
        g = d.groupby("cluster_S")["truth"].agg(lambda x: x.value_counts().index[0])
        agree = (g.values == d.groupby("cluster_S")["S_call"].first().reindex(g.index).values)
        r["cluster_S_dominant_truth_match"] = {"n_clusters": int(len(g)), "matched": int(agree.sum())}
        gp = d.groupby("cluster_P")["truth"].agg(lambda x: x.value_counts().index[0])
        agreep = (gp.values == d.groupby("cluster_P")["P_call"].first().reindex(gp.index).values)
        r["cluster_P_dominant_truth_match"] = {"n_clusters": int(len(gp)), "matched": int(agreep.sum())}
        # number 2 SingleR gain: per class agreement
        per = {}
        for t, sub in d.groupby("truth"):
            per[t] = {"n": int(len(sub)), "S_agree": float((sub["S_call"]==t).mean()), "P_agree": float((sub["P_call"]==t).mean())}
        r["per_class"] = per
        # changes list S vs P (cluster-level)
        ch = (df.groupby(["cluster_S"]).first() if False else None)
        # cluster-level call table: pairs S_call vs P_call by cell overlap (majority per S-cluster)
        rows = []
        for cS, gS in df.groupby("cluster_S"):
            s_call = gS["S_call"].mode().iloc[0]
            p_top = gS["P_call"].value_counts()
            p_dom = p_top.index[0]; p_frac = float(p_top.iloc[0]/len(gS))
            truth_top = gS["truth"].value_counts()
            tr = truth_top.index[0] if truth_top.index[0]!="EXCL" else (truth_top.index[1] if len(truth_top)>1 else "EXCL")
            rows.append({"cluster_S": cS, "n": int(len(gS)), "S_call": s_call, "P_dom": p_dom, "P_frac": round(p_frac,3),
                         "truth_dom": tr, "changed": s_call != p_dom})
        chdf = pd.DataFrame(rows)
        chdf.to_csv(f"{W}/tables/number2_changes_S_vs_P_{tag}.csv", index=False)
        r["n_changed_clusters"] = int(chdf["changed"].sum())
        # number 3 disagreement clusters = changed rows (for PI adjudication form)
        r["disagree_clusters"] = chdf[chdf["changed"]].to_dict(orient="records")
        result[tag] = r
    json.dump(result, open(f"{W}/tables/three_numbers.json","w"), indent=1, default=str)
    for tag, r in result.items():
        print(f"== {tag}: ARI(S,truth)={r['ARI_S_vs_truth']:.3f} ARI(P,truth)={r['ARI_P_vs_truth']:.3f} ARI(S,P)={r['ARI_S_vs_P']:.3f}")
        print(f"   clusters={r['cluster_S_dominant_truth_match']} Pmatch={r['cluster_P_dominant_truth_match']} changed={r['n_changed_clusters']}")

if __name__ == "__main__":
    main()
