#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_cn_rewrite.py — regression test for the query-rewrite layer (off by default).

Zero dependencies: loads no corpus/model (pure function layer); rule assertions auto-SKIP when the
bridge table is absent.
Run: python tests/test_cn_rewrite.py   (exit code 0=PASS; hookable into CI / sync gates)

Coverage:
  T1 switch semantics  env EYEKB_CN_REWRITE ∈ {1,true,on,yes} -> on; unset/0/off/no/other -> off
  T2 off-path passthrough  rewrite_query(q) == (q, None) (service-layer premise of no new response keys)
  T3 empty-input passthrough  query empty/None -> (q, None) (template-query path is never rewritten)
  T4 missing-bridge safety  dynamic bridge table absent -> (q, {status:bridge_missing}), no exception
  T5 rule samples (bridge table required, SKIP when missing)  optic-vesicle-development term ->
     "optic vesicle" / keratoconus term -> "Keratoconus" / horizontal-cell + retina term -> HC /
     RPE-marker-term -> RPE / Mueller-glia term -> no_rewrite
     (the actual case inputs are the Chinese query literals in EXPECT5 below — deliberately kept)
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "mcp_server"))
import rewrite_cn as rw  # noqa: E402

fails, skips = [], []


def check(tag, cond, detail=""):
    if not cond:
        fails.append(f"{tag}: {detail}")
    print(f"[{'ok ' if cond else 'FAIL'}] {tag}" + (f" — {detail}" if detail else ""))


def t1_t3():
    for v, want in [("1", True), ("true", True), ("ON", True), ("yes", True),
                    ("0", False), ("off", False), ("no", False),
                    ("", False), ("banana", False)]:
        os.environ["EYEKB_CN_REWRITE"] = v
        check(f"T1 env={v!r}→{want}", rw.enabled() is want)
    os.environ.pop("EYEKB_CN_REWRITE", None)
    check("T1 unset→False", rw.enabled() is False)

    os.environ.pop("EYEKB_CN_REWRITE", None)
    q = "视网膜色素上皮细胞的标志物"
    out, meta = rw.rewrite_query(q)
    check("T2 off-path passthrough (q,None)", out == q and meta is None)
    os.environ["EYEKB_CN_REWRITE"] = "1"
    for bad in ("", None, "   "):
        o2, m2 = rw.rewrite_query(bad)
        check(f"T3 empty-input passthrough {bad!r}", o2 == bad and m2 is None)


def t4():
    os.environ["EYEKB_CN_REWRITE"] = "1"
    keep = os.environ.get("EYEKB_CN_BRIDGE_TSV")
    os.environ["EYEKB_CN_BRIDGE_TSV"] = "/nonexistent_dir_xyz/bridge.tsv"
    try:
        rw._cache.update({"key": None, "rows": None, "sha": None})
        q = "圆锥角膜"
        o, m = rw.rewrite_query(q)
        check("T4 bridge file missing → bridge_missing, no exception",
              o == q and m and m.get("status") == "bridge_missing", str(m)[:80])
    finally:
        if keep is None:
            os.environ.pop("EYEKB_CN_BRIDGE_TSV", None)
        else:
            os.environ["EYEKB_CN_BRIDGE_TSV"] = keep
        rw._cache.update({"key": None, "rows": None, "sha": None})


EXPECT5 = {
    "视泡发育": ("rewrite", "optic vesicle"),
    "圆锥角膜": ("rewrite", "Keratoconus"),
    "水平细胞 视网膜": ("rewrite", "HC"),
    "视网膜色素上皮细胞的标志物": ("rewrite", "RPE"),
    "缪勒胶质细胞": ("no_rewrite", None),
}


def t5():
    os.environ["EYEKB_CN_REWRITE"] = "1"
    path = os.environ.get("EYEKB_CN_BRIDGE_TSV") or rw.BRIDGE_DEFAULT
    if not os.path.isfile(path):
        skips.append("T5 rule samples SKIP (bridge table not provided: set EYEKB_CN_BRIDGE_TSV and rerun)")
        print("[SKIP] T5 rule samples (bridge file missing)")
        return
    for q, (want_status, want_phrase) in EXPECT5.items():
        o, m = rw.rewrite_query(q)
        check(f"T5 {q}", m and m.get("status") == want_status
              and (want_phrase is None or o == want_phrase),
              f"got status={m.get('status') if m else None} phrase={o[:40]!r}")


def main():
    t1_t3()
    t4()
    t5()
    os.environ.pop("EYEKB_CN_REWRITE", None)
    print(f"\nTEST_CN_REWRITE {'PASS' if not fails else 'FAIL'}: "
          f"{0 if not fails else len(fails)} fails, {len(skips)} skips")
    for f in fails:
        print("FAIL:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
