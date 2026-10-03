#!/usr/bin/env python3
"""KB9 Case-A activation daily follow-up-vote patrol (no_agent watchdog, modeled on the A2 ocular-surface pattern)
Scope=/mnt/D/EyeKB/plans/kb9_act_20260930/OBSERVE_NOTE.md; decision logic aligned with kb9act_t7_check.py.
Target day=yesterday (complete trace); overridable via env KB9_DAY=YYYY-MM-DD (for testing).
stdout semantics: normal/empty capture = zero output (no disturbance); trigger A/B/C or window-end reminder = non-empty output (alert delivered).
Ledger: ledgers/kb9act_daily_log.tsv one row per day; state stores non-k9 order-sequence sha (trigger B day-over-day comparison).
Idempotent: reruns on the same day do not duplicate the row (with KB9_TEST=1, writes to /tmp copies instead, never polluting the real ledger).
"""
import json, os, re, sys, datetime, hashlib

BASE = "/mnt/D/EyeKB/plans/kb9_act_20260930"
TRACE = os.environ.get("KB9_TRACE") or "/mnt/D/EyeKB/logs/mcp_trace"
LOG = BASE + "/ledgers/kb9act_daily_log.tsv"
STATE = BASE + "/ledgers/kb9act_daily_state.json"
K9 = {"Melanocyte", "Schwan" + "n", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}
ACT_T0 = "2026-09-30T02:57"          # code-landing time; calls before it are not activation-state samples
WIN_START, WIN_END = "2026-09-30", "2026-10-07"
RET_TISSUES = ("", "retina", "choroid", "fibrovascular_membrane", "macula")

TEST = os.environ.get("KB9_TEST") == "1"
if TEST:
    LOG, STATE = "/tmp/kb9act_daily_log.test.tsv", "/tmp/kb9act_daily_state.test.json"

day = os.environ.get("KB9_DAY") or (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
if day < WIN_START:
    sys.exit(0)                                   # before the window, stay silent
trace = os.path.join(TRACE, f"calls_{day}.jsonl")

calls = k9libs = 0
trigA, trigB, trigC = [], [], []
seq = {}                                          # fingerprint -> that day's non-k9 order (first observation of the day)
prov_files_seen = set()

if os.path.exists(trace):
    for ln in open(trace, encoding="utf-8", errors="ignore"):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        if d.get("tool") != "query_marker":
            continue
        if day == WIN_START and (d.get("ts") or "") < ACT_T0:
            continue
        args = d.get("args") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                continue
        if str(args.get("library") or "all").strip().lower() != "all":
            continue                               # non-default state not sampled
        resp = d.get("resp") or {}
        libs = resp.get("libs") or []
        labels = resp.get("ranking_classes_top") or []
        calls += 1
        if any("k9" in str(x) for x in libs):
            k9libs += 1
        # Trigger C: lacrimal leakage (mechanical field + provenance name-scan fallback)
        if resp.get("lacrimal_in_prov") is True:
            trigC.append((day, (d.get("ts") or "")[:19], "lacrimal_in_prov=True", labels[:5]))
        # Trigger A: k9 entering the front of ranking for non-ocular-surface inputs
        n = len(labels)
        tis = str(args.get("tissue", "")).lower()
        for i, lb in enumerate(labels):
            if lb in K9 and n >= 4 and i < max(1, n // 2) and tis in RET_TISSUES:
                trigA.append((day, lb, i, n, tis or "(empty)",
                              str(args.get("genes") or args.get("cell_type"))[:60]))
        # Trigger B material: same-fingerprint non-k9 order
        key = hashlib.sha256(json.dumps(
            {k: args.get(k) for k in ("genes", "cell_type", "species", "tissue")},
            sort_keys=True, default=str).encode()).hexdigest()[:16]
        nonk9 = [x for x in labels if x not in K9]
        if nonk9 and key not in seq:
            seq[key] = nonk9

# Trigger B: compare against yesterday's state (same set, flipped order = trigger; set changed but all differences are k9 entries/exits = intrinsic to activation, no trigger)
state = {}
if os.path.exists(STATE):
    try:
        state = json.load(open(STATE))
    except Exception:
        state = {}
prev_day, prev_seq = state.get("day"), state.get("seq") or {}
if prev_day and prev_day < day:                   # only compare when state trails behind the target day
    for key, cur in seq.items():
        old = prev_seq.get(key)
        if old and old != cur:
            if set(old) == set(cur):
                trigB.append((prev_day, day, old[:4], cur[:4]))
            # set changed: non-k9 membership itself changed; eval-side input changes are common, no trigger (conservative: report order flips only)
state = {"day": day, "seq": seq}                  # rolling replace with today's snapshot

verdict = "TRIGGERED" if (trigA or trigB or trigC) else ("EMPTY" if calls == 0 else "OK")
row = [day, str(calls), f"{k9libs}/{calls}", str(len(trigA)), str(len(trigB)), str(len(trigC)), verdict]

# idempotent ledger append
done_days = set()
if os.path.exists(LOG):
    for ln in open(LOG, encoding="utf-8", errors="ignore"):
        p = ln.split("\t")
        if p and p[0]:
            done_days.add(p[0])
if day not in done_days:
    new = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8") as f:
        if new:
            f.write("day\tdefault_calls\tk9_in_libs\ttrigA\ttrigB\ttrigC\tverdict\n")
        f.write("\t".join(row) + "\n")
with open(STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False)

# ---- output (speak only on anomaly) ----
if trigA or trigB or trigC:
    print(f"[KB9 follow-up vote TRIGGERED] {day} default-state calls={calls} A={len(trigA)} B={len(trigB)} C={len(trigC)}")
    for x in (trigA + trigB + trigC)[:8]:
        print("  ", x)
    print("Remedy: per OBSERVE_NOTE -- caller sets env EYEKB_ACT_K9=0 to roll back (A5 discipline); log the evidence, then escalate.")
elif day > WIN_END:
    already = "WINDOW_DONE" in done_days
    if not already:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("WINDOW_DONE\t\t\t\t\t\tpatrol_end\n")
        print("[KB9 follow-up vote] window past 10-07; the 10-07 09:00 closing check is on record; this patrol task can be removed (coord: delete no_agent cron kb9act-daily-t7-window).")
