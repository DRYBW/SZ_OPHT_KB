#!/usr/bin/env python3
"""Narrow (10-gene) vs wide (30-gene) evidence panel, same channel, same corpus.

Both arms: same external adjudication endpoint (see REPORT.md) / K=3 majority / thinking on.
Only the evidence panel width differs. Reads the two scored artefacts:
  JUDGE_SCORE_judge_prod_think_feimao.json   (ev/      10 genes)
  JUDGE_SCORE_judge_prod_think_wide30.json   (ev_wide/ 30 genes)

Folding goes through score_judge.fold_answer so author-vocabulary truth and
KB-vocabulary answers land on the same family key.
"""
import json, os, sys
from collections import Counter, defaultdict

ROOT = os.environ.get("WIDE30_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "out") if os.path.isdir(os.path.join(ROOT, "out")) else ROOT
sys.path.insert(0, ROOT)
try:
    import score_judge as SJ          # noqa: E402
except ModuleNotFoundError:
    raise SystemExit(
        "score_judge.py is not part of this repository copy. Point WIDE30_ROOT at an\n"
        "evaluation workspace that contains score_judge.py and score_corpus.py, e.g.\n"
        "  WIDE30_ROOT=/path/to/workspace python compare_wide30.py")


NARROW = json.load(open(os.path.join(DATA, "JUDGE_SCORE_judge_prod_think_feimao.json")))
WIDE = json.load(open(os.path.join(DATA, "JUDGE_SCORE_judge_prod_think_wide30.json")))


def index(score):
    """{(vol, cluster): (voted_or_None, truth_top1, family, n_cells, species)}"""
    out = {}
    for vd in score["volumes"]:
        for c in vd["clusters"]:
            truth = c.get("truth") or {}
            if not truth:
                continue
            tl = max(truth.items(), key=lambda kv: kv[1])[0]
            nc = c.get("n_cells") or sum(truth.values())
            fam = SJ.fold_answer(tl, tissue_ctx=vd.get("tissue"))
            voted = c.get("voted")
            afam = SJ.fold_answer(voted, tissue_ctx=vd.get("tissue")) if voted else None
            out[(vd["volume"], c["cluster"])] = {
                "voted": voted, "afam": afam, "truth": tl, "tfam": fam,
                "n_cells": nc, "species": vd.get("species")}
    return out


n_idx, w_idx = index(NARROW), index(WIDE)
keys = sorted(set(n_idx) & set(w_idx))


def arm_stats(idx, keys, label):
    abst = [k for k in keys if idx[k]["voted"] is None]
    answered = [k for k in keys if idx[k]["voted"] is not None]
    correct = [k for k in keys if idx[k]["afam"] and idx[k]["afam"] == idx[k]["tfam"]]
    cells = sum(idx[k]["n_cells"] for k in keys)
    return {
        "arm": label,
        "clusters": len(keys), "cells": cells,
        "abstain": len(abst),
        "abstain_pct": round(100.0 * len(abst) / len(keys), 2),
        "answered": len(answered),
        "coverage_pct": round(100.0 * len(answered) / len(keys), 2),
        "correct_clusters": len(correct),
        "top1_overall_pct": round(100.0 * len(correct) / len(keys), 2),
        "top1_in_answers_pct": (round(100.0 * len(correct) / len(answered), 2)
                                if answered else 0.0),
    }


print("== arms (all %d clusters) ==" % len(keys))
for idx, lab in ((n_idx, "10 genes"), (w_idx, "30 genes")):
    s = arm_stats(idx, keys, lab)
    print("  %-9s abstain %3d (%5.1f%%)  coverage %5.1f%%  "
          "top1 overall %5.1f%%  top1 in answers %5.1f%%"
          % (lab, s["abstain"], s["abstain_pct"], s["coverage_pct"],
             s["top1_overall_pct"], s["top1_in_answers_pct"]))

# focus: the clusters that abstained at 10 genes
was_abst = [k for k in keys if n_idx[k]["voted"] is None]
print("\n== the %d clusters that abstained at 10 genes ==" % len(was_abst))
buckets = Counter()
cells = defaultdict(int)
detail_rows = []
for k in was_abst:
    w = w_idx[k]
    nc = n_idx[k]["n_cells"]
    if w["voted"] is None:
        b = "still abstained"
    elif w["afam"] and w["afam"] == w["tfam"]:
        b = "now correct"
    else:
        b = "now answered wrong"
    buckets[b] += 1
    cells[b] += nc
    detail_rows.append({"volume": k[0], "cluster": k[1], "n_cells": nc,
                        "truth": n_idx[k]["truth"], "family": n_idx[k]["tfam"],
                        "narrow_voted": n_idx[k]["voted"],
                        "wide_voted": w["voted"], "bucket": b})
for b in ("now correct", "now answered wrong", "still abstained"):
    print("  %-20s %3d clusters  %9d cells" % (b, buckets[b], cells[b]))

# focus: did widening cost anything on clusters that already answered?
was_ans = [k for k in keys if n_idx[k]["voted"] is not None]
gain = loss = same = 0
for k in was_ans:
    n_ok = bool(n_idx[k]["afam"] and n_idx[k]["afam"] == n_idx[k]["tfam"])
    w_ok = bool(w_idx[k]["afam"] and w_idx[k]["afam"] == w_idx[k]["tfam"])
    if w_ok and not n_ok:
        gain += 1
    elif n_ok and not w_ok:
        loss += 1
    else:
        same += 1
print("\n== the %d clusters that already answered at 10 genes ==" % len(was_ans))
print("  unchanged  %3d\n  fixed      %3d (narrow wrong -> wide right)\n  broken     %3d (narrow right -> wide wrong)"
      % (same, gain, loss))

out = {
    "arms": {"10_genes": arm_stats(n_idx, keys, "10 genes"),
             "30_genes": arm_stats(w_idx, keys, "30 genes")},
    "denominator": {"clusters": len(keys),
                    "cells": sum(n_idx[k]["n_cells"] for k in keys)},
    "abstain_resolution": {b: {"clusters": buckets[b], "cells": cells[b]}
                           for b in buckets},
    "answered_arm_change": {"unchanged": same, "fixed": gain, "broken": loss},
    "per_cluster": detail_rows,
}
json.dump(out, open(os.path.join(DATA, "WIDE30_VS_NARROW.json"), "w"),
          indent=1, ensure_ascii=False)
print("\nwrote WIDE30_VS_NARROW.json")