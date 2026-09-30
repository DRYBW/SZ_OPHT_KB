#!/usr/bin/env python3
"""KB9 案A 激活 T+7 跟票检查 v2（对齐 mcp_trace 摘要 schema，只读）
窗口 2026-09-30..2026-10-07；数据源 calls_*.jsonl 的 query_marker 默认态行（args.library 未设）。
触发A: k9 四条在非眼表 tissue 输入 ranking_classes_top 的前半段上位
触发B: 同 args 指纹相邻日非k9 top 次序翻转
触发C: resp.lacrimal_in_prov == True（机械字段，非猜词表）
另报告: 每日默认调用数、libs 含 k9_ocs 比例（激活生效面）。
"""
import json, glob, os, re
from collections import defaultdict
K9 = {"Melanocyte", "Schwan" + "n", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}
W = re.compile(r"calls_(2026-09-30|2026-10-0[1-7])\.jsonl$")
per_day = defaultdict(lambda: {"calls": 0, "k9_in_libs": 0})
seq = defaultdict(list)
trigA, trigB, trigC = [], [], []
for f in sorted(glob.glob("/mnt/D/EyeKB/logs/mcp_trace/calls_*.jsonl")):
    m = W.search(os.path.basename(f));  day = m.group(1) if m else None
    if not day: continue
    for ln in open(f, encoding="utf-8", errors="ignore"):
        try: d = json.loads(ln)
        except Exception: continue
        if d.get("tool") != "query_marker": continue
        # 时间窗：激活于 09-30 02:57 落码；仅采其后默认态调用（library 缺省或 "all"，calllog 会把缺省补写为 "all"）
# 注：演练期 OFF 态捕获行（libs 无 k9）不剔除，按 OBSERVE_NOTE 口径 k9_in_libs 比例如实反映 ON/OFF 混态
        if day == "2026-09-30" and (d.get("ts") or "") < "2026-09-30T02:57": continue
        args = d.get("args") or {}
        if isinstance(args, str):
            try: args = json.loads(args)
            except Exception: continue
        if str(args.get("library") or "all").strip().lower() not in ("all",): continue
        resp = d.get("resp") or {}
        libs = resp.get("libs") or []
        labels = resp.get("ranking_classes_top") or []
        per_day[day]["calls"] += 1
        if any("k9" in str(x) for x in libs): per_day[day]["k9_in_libs"] += 1
        if resp.get("lacrimal_in_prov") is True:
            trigC.append((day, (d.get("ts") or "")[:19], labels[:5]))
        n = len(labels)
        tis = str(args.get("tissue", "")).lower()
        for i, lb in enumerate(labels):
            if lb in K9 and n >= 4 and i < max(1, n // 2) and tis in ("", "retina", "choroid", "fibrovascular_membrane", "macula"):
                trigA.append((day, lb, i, n, tis or "(空)", str(args.get("genes") or args.get("cell_type"))[:60]))
        key = json.dumps({k: args.get(k) for k in ("genes", "cell_type", "species", "tissue")}, sort_keys=True)
        nonk9 = [x for x in labels if x not in K9]
        if nonk9: seq[key].append((day, nonk9))
for key, s in seq.items():
    s.sort()
    for (d1, a), (d2, b) in zip(s, s[1:]):
        if a != b and set(a) == set(b):   # 同集合次序翻转
            trigB.append((d1, d2, a[:4], b[:4]))
        elif a != b and (set(b) - set(a)) <= K9:
            pass  # 仅 k9 进出=激活固有
print("PER_DAY:", json.dumps({k: v for k, v in sorted(per_day.items())}, ensure_ascii=False))
print(f"TRIGGER_A上位入侵={len(trigA)}; TRIGGER_B翻转={len(trigB)}; TRIGGER_C泪腺={len(trigC)}")
for x in (trigA + trigB + trigC)[:8]: print("  ", x)
print("VERDICT:", "OBSERVE_PASS" if not (trigA or trigB or trigC) else "OBSERVE_TRIGGERED")
