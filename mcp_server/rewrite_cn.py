#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP query-rewrite layer (2026-10-03)

In one sentence: before a Chinese search sentence is fed to the English embedding surface, it is
mechanically translated into an English search expression via the Chinese-term bridge; off by
default, and in the off state the service behaves byte-identically to history.

Rule source: pre-registered frozen rules (M1 word-level substring containment >=2 chars /
M2 query token (>=4) contained in a bridge term / longest match wins / row_id tie-break order /
search expression = English anchor + the English parts of query-relevant alias pairs, with CJK and
full-width cleanup, tokens <2 chars or purely symbolic are dropped). At runtime the frozen bridge
TSV is read; zero vocabulary re-typing, zero manual picking.

Switch: env EYEKB_CN_REWRITE read once per call; strip().casefold() ∈ {1,true,on,yes} → on;
unset/any other value → off. In the off state this module touches nothing (callers short-circuit
straight through). Bridge path: env EYEKB_CN_BRIDGE_TSV overrides; when unset the default absolute
path is used. If the bridge is missing/corrupted, the on state runs every query as-is and
discloses status=bridge_missing (no raise, no service crash).

Red line: this module is pure functions + read-only files; the returned rewrite_meta is for
auditable disclosure only and is forbidden as input to any score/weighting/ranking.
"""
import csv
import hashlib
import os
import re

BRIDGE_DEFAULT = ("/mnt/D/EyeKB/plans/devline_cnbridge_20261002/"
                  "out/CN_BRIDGE_MERGED_v1.tsv")
ON_VALUES = {"1", "true", "on", "yes"}

# —— the norm / CJK_RE / clean_part below are verbatim-identical to the frozen d1_rewrite_rules.py ——
CJK_RE = re.compile(r'[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u3400-\u4dbf]')


def norm(s):
    return re.sub(r'\s+', '', s or '')


def clean_part(s):
    """Drop CJK/full-width chars, split into tokens, remove purely symbolic and short tokens."""
    s = CJK_RE.sub(' ', s or '')
    toks = [t for t in re.split(r'\s+', s) if t]
    out = []
    for t in toks:
        core = re.sub(r'[^A-Za-z0-9]', '', t)
        if len(core) >= 2:
            out.append(t)
    return out


def enabled():
    return (os.environ.get("EYEKB_CN_REWRITE") or "").strip().casefold() in ON_VALUES


# —— bridge loading: in-process cache keyed by (path, mtime, size), same pattern as stage3 _dev_map ——
_cache = {"key": None, "rows": None, "sha": None}


def _bridge_path():
    return os.environ.get("EYEKB_CN_BRIDGE_TSV") or BRIDGE_DEFAULT


def _load_bridge():
    p = _bridge_path()
    try:
        st = os.stat(p)
    except OSError:
        return p, None, None
    key = (p, st.st_mtime, st.st_size)
    if _cache["key"] != key:
        try:
            with open(p, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f, delimiter="\t"))
            ok = rows and all(("row_id" in r and "cn_term" in r) for r in rows)
        except Exception:
            ok = False
        if not ok:
            _cache["key"], _cache["rows"], _cache["sha"] = key, None, None
            return p, None, None
        _cache["key"] = key
        _cache["rows"] = rows
        _cache["sha"] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return p, _cache["rows"], _cache["sha"]


def rewrite_query(q):
    """Rewrite a single query. q = the original search sentence (str). Returns (query_used, meta|None)."""
    if not enabled():
        return q, None
    if not q or not str(q).strip():
        return q, None
    p, bridge, bsha = _load_bridge()
    if bridge is None:
        return q, {"status": "bridge_missing", "bridge_file": p}
    qn = norm(q)
    cands = []  # (matchlen, mode, row, fragment) — one-for-one identical to the d1 frozen rules
    for b in bridge:
        tn = norm(b['cn_term'])
        if len(tn) >= 2 and tn in qn:
            cands.append((len(tn), 'M1', b, tn))
        else:
            for tok in [t for t in (q or '').split() if len(t) >= 4]:
                if norm(tok) and norm(tok) in tn:
                    cands.append((len(norm(tok)), 'M2', b, norm(tok)))
    status = 'no_rewrite'
    chosen = None
    mode = frag = ''
    if cands:
        cands.sort(key=lambda c: (-c[0], c[2]['row_id']))
        ml, mode, chosen, frag = cands[0]
    final = ''
    alias_used = []
    if chosen is not None:
        parts = []
        parts += clean_part(chosen.get('en_anchor') or '')
        for pair in (chosen.get('aliases') or '').split(';'):
            if '=' not in pair:
                continue
            x, y = pair.split('=', 1)
            if norm(x) and norm(x) in qn:
                tk = clean_part(y)
                if tk:
                    parts += tk
                    alias_used.append(pair.strip())
        seen = set()
        expr = []
        for t in parts:
            k = t.lower()
            if k not in seen:
                seen.add(k)
                expr.append(t)
        final = ' '.join(expr)
        if final.strip():
            status = 'rewrite'
        else:
            final = ''
    meta = {"status": status,
            "match_mode": mode if chosen else 'NONE',
            "row_id": chosen['row_id'] if chosen else '',
            "cn_term": chosen['cn_term'] if chosen else '',
            "matched_fragment": frag,
            "en_anchor_raw": (chosen.get('en_anchor') or '') if chosen else '',
            "final_phrase": final,
            "alias_parts_used": (';'.join(alias_used) if (chosen and status == 'rewrite') else ''),
            "bridge_file": p, "bridge_sha256": bsha}
    if status == 'rewrite':
        return final, meta
    return q, meta
