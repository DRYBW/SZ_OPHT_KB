#!/usr/bin/env python3
"""The interface's current window: the recorded top-10 gene list of each of the 721 clusters.

This is the interface INPUT, not any reference label, so reading it violates no red line. The union of the
721 recorded windows is the observable vocabulary used by field 6. Read-only, no network.
"""
import collections
import glob
import json

WAVE = "/mnt/D/EyeKB/plans/subdivision_readiness_20261022"
OUT = f"{WAVE}/out"
BASE = "/mnt/D/EyeKB/plans/oss_check_20261019"

vocab = collections.Counter()
per_vol = {}
n_clusters = 0
widths = collections.Counter()
for p in sorted(glob.glob(f"{BASE}/dl/results/*/annotation_evidence_report.json")):
    vol = p.split("/")[-2]
    d = json.load(open(p))
    vs = set()
    for c in d.get("clusters") or []:
        genes = c.get("top_genes") or []
        widths[len(genes)] += 1
        n_clusters += 1
        for g in genes:
            vocab[g] += 1
            vs.add(g)
    per_vol[vol] = {"n_clusters": len(d.get("clusters") or []), "n_genes_in_window": len(vs),
                    "genes": sorted(vs)}

doc = {"source": f"{BASE}/dl/results/*/annotation_evidence_report.json",
       "n_clusters": n_clusters,
       "window_width_distribution": dict(sorted(widths.items())),
       "n_distinct_genes_in_window": len(vocab),
       "per_volume": per_vol,
       "definitions": {
           "observable_vocabulary": "union of the recorded top-10 gene lists of the 721 clusters",
           "reading_class": "probing/regression reading on the fixed 28-volume set, NOT validation"},
       "gene_frequency": vocab.most_common()}
json.dump(doc, open(f"{OUT}/O_observable_window.json", "w"), ensure_ascii=False, indent=1)
print(f"clusters={n_clusters}  window widths={dict(widths.most_common(3))}  "
      f"distinct genes in window={len(vocab)}")
print("wrote", f"{OUT}/O_observable_window.json")