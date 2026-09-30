#!/usr/bin/env python3
"""KB9 案A 激活每日跟票巡检（no_agent watchdog，仿 A2 眼表模式）
口径=/mnt/D/EyeKB/plans/kb9_act_20260930/OBSERVE_NOTE.md；判定逻辑对齐 kb9act_t7_check.py。
目标日=昨日（完整 trace）；可用 env KB9_DAY=YYYY-MM-DD 指定（测试用）。
stdout 语义：正常/空采=零输出（不打扰）；触发A/B/C 或窗口结束提醒=非零输出（告警送达）。
台账：ledgers/kb9act_daily_log.tsv 每日一行；state 存非k9次序指纹 sha（触发B 日际对比）。
幂等：同日重跑不重复记行（测试模式 KB9_TEST=1 时改写 /tmp 副本，不污染正账）。
"""
import json, os, re, sys, datetime, hashlib

BASE = "/mnt/D/EyeKB/plans/kb9_act_20260930"
TRACE = os.environ.get("KB9_TRACE") or "/mnt/D/EyeKB/logs/mcp_trace"
LOG = BASE + "/ledgers/kb9act_daily_log.tsv"
STATE = BASE + "/ledgers/kb9act_daily_state.json"
K9 = {"Melanocyte", "Schwan" + "n", "Conj_epithelium_suprabasal", "Limbus_Sclera_fibroblast_C1"}
ACT_T0 = "2026-09-30T02:57"          # 落码时刻；此前调用不算激活态样本
WIN_START, WIN_END = "2026-09-30", "2026-10-07"
RET_TISSUES = ("", "retina", "choroid", "fibrovascular_membrane", "macula")

TEST = os.environ.get("KB9_TEST") == "1"
if TEST:
    LOG, STATE = "/tmp/kb9act_daily_log.test.tsv", "/tmp/kb9act_daily_state.test.json"

day = os.environ.get("KB9_DAY") or (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
if day < WIN_START:
    sys.exit(0)                                   # 窗口前，静默
trace = os.path.join(TRACE, f"calls_{day}.jsonl")

calls = k9libs = 0
trigA, trigB, trigC = [], [], []
seq = {}                                          # 指纹 -> 当日非k9次序（同日取首次观测）
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
            continue                               # 非默认态不采
        resp = d.get("resp") or {}
        libs = resp.get("libs") or []
        labels = resp.get("ranking_classes_top") or []
        calls += 1
        if any("k9" in str(x) for x in libs):
            k9libs += 1
        # 触发C：泪腺泄漏（机械字段 + provenance 兜底扫名）
        if resp.get("lacrimal_in_prov") is True:
            trigC.append((day, (d.get("ts") or "")[:19], "lacrimal_in_prov=True", labels[:5]))
        # 触发A：k9 在非眼表输入的 ranking 前段上位
        n = len(labels)
        tis = str(args.get("tissue", "")).lower()
        for i, lb in enumerate(labels):
            if lb in K9 and n >= 4 and i < max(1, n // 2) and tis in RET_TISSUES:
                trigA.append((day, lb, i, n, tis or "(空)",
                              str(args.get("genes") or args.get("cell_type"))[:60]))
        # 触发B 素材：同指纹非k9次序
        key = hashlib.sha256(json.dumps(
            {k: args.get(k) for k in ("genes", "cell_type", "species", "tissue")},
            sort_keys=True, default=str).encode()).hexdigest()[:16]
        nonk9 = [x for x in labels if x not in K9]
        if nonk9 and key not in seq:
            seq[key] = nonk9

# 触发B：与昨日 state 对比（同集合次序翻转=触发；集合变化但差异全为k9进出=激活固有，不触发）
state = {}
if os.path.exists(STATE):
    try:
        state = json.load(open(STATE))
    except Exception:
        state = {}
prev_day, prev_seq = state.get("day"), state.get("seq") or {}
if prev_day and prev_day < day:                   # state 落后于目标日才比对
    for key, cur in seq.items():
        old = prev_seq.get(key)
        if old and old != cur:
            if set(old) == set(cur):
                trigB.append((prev_day, day, old[:4], cur[:4]))
            # 集合变化：非k9成员本身变了，评估侧输入变化常见，不触发（保守：只报次序翻转）
state = {"day": day, "seq": seq}                  # 滚动替换为当日快照

verdict = "TRIGGERED" if (trigA or trigB or trigC) else ("EMPTY" if calls == 0 else "OK")
row = [day, str(calls), f"{k9libs}/{calls}", str(len(trigA)), str(len(trigB)), str(len(trigC)), verdict]

# 台账幂等追加
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

# ── 输出（仅异常出声）──
if trigA or trigB or trigC:
    print(f"[KB9跟票·触发] {day} 默认态调用{calls} A={len(trigA)} B={len(trigB)} C={len(trigC)}")
    for x in (trigA + trigB + trigC)[:8]:
        print("  ", x)
    print("处置=按 OBSERVE_NOTE：调用方 env EYEKB_ACT_K9=0 回退（A5 纪律），登记证据后上报。")
elif day > WIN_END:
    already = "WINDOW_DONE" in done_days
    if not already:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("WINDOW_DONE\t\t\t\t\t\tpatrol_end\n")
        print("[KB9跟票] 窗口已过 10-07；10-07 09:00 收口检查在案，本巡检任务可移除（coord 删除 no_agent cron kb9act-daily-t7-window）。")
