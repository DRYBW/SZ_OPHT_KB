#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_cn_rewrite.py — regression test for the query-rewrite layer (default ON since v3.1).

Zero dependencies: loads no corpus/model (pure function layer); rule assertions auto-SKIP when the
bridge table is absent.
Run: python tests/test_cn_rewrite.py   (exit code 0=PASS; hookable into CI / sync gates)

Coverage:
  T1 switch semantics  unset/empty -> ON (the v3.1 default); 1/true/on/yes -> ON;
                       0/off/false/no -> OFF (the escape door); any other value -> OFF
  T2 off-path passthrough  with the door explicitly closed, rewrite_query(q) == (q, None)
                       (service-layer premise of no new response keys)
  T3 empty-input passthrough  query empty/None/blank -> (q, None) under the default
  T4 missing-bridge safety  dynamic bridge table absent -> (q, {status:bridge_missing}), no exception
  T5 rule samples (bridge table required, SKIP when missing)  Chinese inputs produce an
                       in-place insertion whose English anchor appears and whose Chinese text
                       survives character-for-character (insert-style semantics, v2 onward)
  T6 non-CJK existence gate  English / numeric / symbolic queries are never touched, including the
                       M4 true-positive set that v3 used to disturb
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


def strip_ws(s):
    return "".join(ch for ch in (s or "") if not ch.isspace())


def is_subsequence(a, b):
    it = iter(b)
    return all(c in it for c in a)


def t1_switch_semantics():
    for v, want in [("1", True), ("true", True), ("ON", True), ("yes", True), ("", True),
                    ("0", False), ("off", False), ("false", False), ("no", False),
                    ("banana", False)]:
        os.environ["EYEKB_CN_REWRITE"] = v
        check(f"T1 env={v!r}->{want}", rw.enabled() is want)
    os.environ.pop("EYEKB_CN_REWRITE", None)
    check("T1 unset->True (v3.1 default ON)", rw.enabled() is True)


def t2_t3():
    os.environ["EYEKB_CN_REWRITE"] = "0"
    q = "视网膜色素上皮细胞的标志物"
    out, meta = rw.rewrite_query(q)
    check("T2 off-path passthrough (q,None)", out == q and meta is None)

    os.environ.pop("EYEKB_CN_REWRITE", None)   # v3.1 default = ON
    check("T2b default-on enabled()", rw.enabled() is True)
    out2, meta2 = rw.rewrite_query(q)
    ok2 = bool(meta2) and meta2.get("status") in ("rewrite", "no_rewrite", "bridge_missing")
    check("T2b default-on CJK query is serviced (meta present)", ok2,
          f"status={meta2.get('status') if meta2 else None}")
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
        check("T4 bridge file missing -> bridge_missing, no exception",
              o == q and m and m.get("status") == "bridge_missing", str(m)[:80])
    finally:
        if keep is None:
            os.environ.pop("EYEKB_CN_BRIDGE_TSV", None)
        else:
            os.environ["EYEKB_CN_BRIDGE_TSV"] = keep
        rw._cache.update({"key": None, "rows": None, "sha": None})


# insert-style expectations: (status, anchor that must appear in the output)
EXPECT5 = {
    "视泡发育": ("rewrite", "optic vesicle"),
    "圆锥角膜": ("rewrite", "Keratoconus"),
    "水平细胞 视网膜": ("rewrite", "HC"),
    "视网膜色素上皮细胞的标志物": ("rewrite", "RPE"),
    "缪勒胶质细胞": ("rewrite", "cell"),
}


def t5():
    os.environ["EYEKB_CN_REWRITE"] = "1"
    path = os.environ.get("EYEKB_CN_BRIDGE_TSV") or rw.BRIDGE_DEFAULT
    if not os.path.isfile(path):
        skips.append("T5 rule samples SKIP (bridge table not provided: set EYEKB_CN_BRIDGE_TSV and rerun)")
        print("[SKIP] T5 rule samples (bridge file missing)")
        return
    for q, (want_status, want_anchor) in EXPECT5.items():
        o, m = rw.rewrite_query(q)
        st = (m or {}).get("status")
        ok = (st == want_status and want_anchor in (o or "")
              and is_subsequence(strip_ws(q), strip_ws(o)))
        check(f"T5 {q}", ok,
              f"status={st} out={o[:60]!r} (anchor {want_anchor!r} must appear; Chinese text preserved)")


# T6: pure non-CJK queries — must never be touched. Includes the M4 true-positive set that v3
# disturbed on the English face (measured 14/40 in the CN-REWRITE-FLIP card, E1-d).
NONCJK = [
    "retinal pigment epithelium markers",
    "retinal pigment epithelium (RPE)",
    "age-related macular degeneration (AMD)",
    "inner nuclear layer (INL)",
    "outer nuclear layer (ONL)",
    "ganglion cell layer (GCL)",
    "retinal ganglion cell (RGC)",
    "retinal progenitor cell (RPC)",
    "amacrine cell",
    "bipolar cell",
    "horizontal cell",
    "IPL thickness",
    "choriocapillaris",
    "coloboma / optic fissure",
    "Müller glia",
    "cone photoreceptor S-opsin",
    "123 456",
    "::::",
    "RPE",
    "a",
]


def t6():
    os.environ.pop("EYEKB_CN_REWRITE", None)   # default ON: the strictest case for the gate
    check("T6 default-on enabled()", rw.enabled() is True)
    bad = []
    for q in NONCJK:
        o, m = rw.rewrite_query(q)
        if o != q or m is not None:
            bad.append((q, o, m))
    check(f"T6 non-CJK queries untouched ({len(NONCJK)} probes)", not bad, str(bad[:3]))
    # full-width Latin is NOT folded away before the gate: it must still be serviced
    fw = "ＩＰＬ"
    o, m = rw.rewrite_query(fw)
    check("T6b full-width Latin still serviced", m is not None, f"status={(m or {}).get('status')}")


def main():
    t1_switch_semantics()
    t2_t3()
    t4()
    t5()
    t6()
    os.environ.pop("EYEKB_CN_REWRITE", None)
    print(f"\nTEST_CN_REWRITE {'PASS' if not fails else 'FAIL'}: "
          f"{0 if not fails else len(fails)} fails, {len(skips)} skips")
    for f in fails:
        print("FAIL:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
