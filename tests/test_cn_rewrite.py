#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_cn_rewrite.py — 查询改写层（默认关）回归测试。

零依赖：不加载语料/模型（纯函数层）；桥表缺失时规则断言自动 SKIP。
运行：python tests/test_cn_rewrite.py   （退出码 0=PASS，可挂 CI/同步门）

覆盖：
  T1 开关语义  env EYEKB_CN_REWRITE ∈ {1,true,on,yes} → 开；未设/0/off/no/其他 → 关
  T2 关闭态直通  rewrite_query(q) == (q, None)（响应零新增键的服务层前提）
  T3 空输入直通  query 空/None → (q, None)（模板句路径永不改写）
  T4 桥表缺失安全  开动态桥表不存在 → (q, {status:bridge_missing}) 不抛错
  T5 规则样例（需桥表，缺失 SKIP）  视泡发育→optic vesicle / 圆锥角膜→Keratoconus /
     水平细胞 视网膜→HC / 视网膜色素上皮细胞的标志物→RPE / 缪勒胶质细胞→no_rewrite
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
    check("T2 off 直通 (q,None)", out == q and meta is None)
    os.environ["EYEKB_CN_REWRITE"] = "1"
    for bad in ("", None, "   "):
        o2, m2 = rw.rewrite_query(bad)
        check(f"T3 空输入直通 {bad!r}", o2 == bad and m2 is None)


def t4():
    os.environ["EYEKB_CN_REWRITE"] = "1"
    keep = os.environ.get("EYEKB_CN_BRIDGE_TSV")
    os.environ["EYEKB_CN_BRIDGE_TSV"] = "/nonexistent_dir_xyz/bridge.tsv"
    try:
        rw._cache.update({"key": None, "rows": None, "sha": None})
        q = "圆锥角膜"
        o, m = rw.rewrite_query(q)
        check("T4 桥表缺失→bridge_missing 不抛错",
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
        skips.append("T5 规则样例 SKIP（桥表未提供：设 EYEKB_CN_BRIDGE_TSV 后重跑）")
        print("[SKIP] T5 规则样例（桥表缺失）")
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
