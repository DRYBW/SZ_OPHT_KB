#!/usr/bin/env python3
"""KB9 Case-A activation T+7 follow-up vote check v2 (aligned with mcp_trace summary schema, read-only)
Window 2026-09-30..2026-10-07; source: query_marker default-state rows in calls_*.jsonl (args.library unset).
Trigger A: any of the four k9 labels entering the front half of ranking_classes_top for non-ocular-surface tissue inputs
Trigger B: adjacent-day flip in the non-k9 top ordering under the same args fingerprint
Trigger C: resp.lacrimal_in_prov == True (mechanical field, not a guessed vocabulary)
Also reported: daily default-call count, fraction of libs containing k9_ocs (activation surface).
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
        # Time window: activation landed in code at 09-30 02:57; only sample default-state calls after it (library unset or "all"; calllog backfills unset as "all")
# Note: OFF-state capture rows from the rehearsal period (libs without k9) are not dropped; per the OBSERVE_NOTE scope, the k9_in_libs ratio honestly reflects the mixed ON/OFF state
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
                trigA.append((day, lb, i, n, tis or "(empty)", str(args.get("genes") or args.get("cell_type"))[:60]))
        key = json.dumps({k: args.get(k) for k in ("genes", "cell_type", "species", "tissue")}, sort_keys=True)
        nonk9 = [x for x in labels if x not in K9]
        if nonk9: seq[key].append((day, nonk9))
for key, s in seq.items():
    s.sort()
    for (d1, a), (d2, b) in zip(s, s[1:]):
        if a != b and set(a) == set(b):   # same set, flipped order
            trigB.append((d1, d2, a[:4], b[:4]))
        elif a != b and (set(b) - set(a)) <= K9:
            pass  # only k9 entries/exits = intrinsic to activation
print("PER_DAY:", json.dumps({k: v for k, v in sorted(per_day.items())}, ensure_ascii=False))
print(f"TRIGGER_A_front_entry={len(trigA)}; TRIGGER_B_order_flip={len(trigB)}; TRIGGER_C_lacrimal={len(trigC)}")
for x in (trigA + trigB + trigC)[:8]: print("  ", x)
print("VERDICT:", "OBSERVE_PASS" if not (trigA or trigB or trigC) else "OBSERVE_TRIGGERED")
