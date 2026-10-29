#!/usr/bin/env python3
"""Recompute the wide-vs-narrow readings straight from the two scored files and
assert every printed relationship holds. Exit 1 on any mismatch."""
import json, os, sys

ROOT = os.environ.get("WIDE30_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "out") if os.path.isdir(os.path.join(ROOT, "out")) else ROOT
sys.path.insert(0, ROOT)
try:
    import score_judge as SJ          # noqa: E402
except ModuleNotFoundError:
    raise SystemExit(
        "score_judge.py is not part of this repository copy. Point WIDE30_ROOT at an\n"
        "evaluation workspace that contains score_judge.py and score_corpus.py, e.g.\n"
        "  WIDE30_ROOT=/path/to/workspace python verify_wide30.py")


N = json.load(open(os.path.join(DATA, "JUDGE_SCORE_judge_prod_think_feimao.json")))
W = json.load(open(os.path.join(DATA, "JUDGE_SCORE_judge_prod_think_wide30.json")))
OUT = json.load(open(os.path.join(DATA, "WIDE30_VS_NARROW.json")))

fails = []
def chk(name, got, want):
    ok = (got == want)
    print("  %s  %-46s got=%s want=%s" % ("PASS" if ok else "FAIL", name, got, want))
    if not ok:
        fails.append(name)


def build(score):
    d = {}
    for vd in score["volumes"]:
        for c in vd["clusters"]:
            t = c.get("truth") or {}
            if not t:
                continue
            tl = max(t.items(), key=lambda kv: kv[1])[0]
            tf = SJ.fold_answer(tl, tissue_ctx=vd.get("tissue"))
            v = c.get("voted")
            af = SJ.fold_answer(v, tissue_ctx=vd.get("tissue")) if v else None
            d[(vd["volume"], c["cluster"])] = {
                "voted": v, "af": af, "tf": tf,
                "nc": c.get("n_cells") or sum(t.values())}
    return d


n, w = build(N), build(W)
keys = sorted(set(n) & set(w))

n_ok = sum(1 for k in keys if n[k]["af"] and n[k]["af"] == n[k]["tf"])
w_ok = sum(1 for k in keys if w[k]["af"] and w[k]["af"] == w[k]["tf"])
n_ab = sum(1 for k in keys if n[k]["voted"] is None)
w_ab = sum(1 for k in keys if w[k]["voted"] is None)

print("== recomputed from the two score files ==")
chk("clusters compared", len(keys), 764)
chk("narrow correct", n_ok, 432)
chk("wide correct", w_ok, 488)
chk("narrow abstain", n_ab, 223)
chk("wide abstain", w_ab, 153)
chk("net correct gain", w_ok - n_ok, 56)
chk("coverage gain in clusters", n_ab - w_ab, 70)

print("\n== the printed decomposition ==")
ar = OUT["abstain_resolution"]
chk("223 = now_correct + wrong + still", 
    ar["now correct"]["clusters"] + ar["now answered wrong"]["clusters"]
    + ar["still abstained"]["clusters"], 223)
chk("now correct", ar["now correct"]["clusters"], 58)
chk("now answered wrong", ar["now answered wrong"]["clusters"], 26)
chk("still abstained", ar["still abstained"]["clusters"], 139)
aa = OUT["answered_arm_change"]
chk("541 = unchanged + fixed + broken", aa["unchanged"] + aa["fixed"] + aa["broken"], 541)
chk("net gain arithmetic 58-10+8", 58 - aa["broken"] + aa["fixed"], 56)

print("\n== printed percentages match the counts ==")
chk("narrow top1 pct", OUT["arms"]["10_genes"]["top1_overall_pct"],
    round(100.0 * n_ok / len(keys), 2))
chk("wide top1 pct", OUT["arms"]["30_genes"]["top1_overall_pct"],
    round(100.0 * w_ok / len(keys), 2))
chk("narrow coverage pct", OUT["arms"]["10_genes"]["coverage_pct"],
    round(100.0 * (len(keys) - n_ab) / len(keys), 2))
chk("wide coverage pct", OUT["arms"]["30_genes"]["coverage_pct"],
    round(100.0 * (len(keys) - w_ab) / len(keys), 2))

print("\n== denominator ==")
chk("cells", sum(n[k]["nc"] for k in keys), OUT["denominator"]["cells"])

print("\nfailures: %d" % len(fails))
if fails:
    print("MISMATCH:", fails); sys.exit(1)
print("READTHROUGH PASS: every wide-30 reading recomputes from the two score files.")