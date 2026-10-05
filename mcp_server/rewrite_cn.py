#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP query-rewrite layer, v2 (CN-REWRITE-FIX1, 2026-10-05)

In one sentence: before a Chinese search sentence is fed to the English embedding surface, the
bridge terms it contains are located and their English anchors are inserted in place; the rest of
the sentence is preserved verbatim.

Why v2: the v1 layer replaced the whole sentence with a single bridge row's English anchor, which
scored well (strict hits 21/24 on the frozen challenge volume) but dropped every constraint the
sentence carried outside that row (31 rows of substantive constraint loss, G2 FAIL, report
out/REPORT_CN_CHALLENGE.md). v2 keeps the sentence and adds the anchors, so a concept can no
longer be dropped by construction, and several classes of damage disappear structurally:

  * alias-capable triggers: a bridge alias left-hand side is now a match candidate, not only the
    cn_term. The longer clinical entity an alias carries (e.g. 青光眼睫状体炎综合征 -> Posner-
    Schlossman, 早产儿视网膜病变 -> ROP, 后弹力层剥除内皮移植 -> DSEK/DSAEK, 新生血管性青光眼 ->
    NVG) therefore wins the span over the short generic word nested inside it. This is the generic-
    word guard: the bridge's own vocabulary supplies the longer entity, nothing is hand-written.
  * full-width Latin: matching is fold-insensitive (full-width -> half-width, U+3000 -> space,
    case), and an all-Latin token the bridge already knows (e.g. ＩＰＬ -> IPL) is itself a trigger.
  * no deletion: an anchor is inserted after its matched span; the original characters are never
    removed, which is also what makes the OFF-state guarantee trivially safe.

Rule chain (frozen; see plans/cn_rewrite_fix_20261005/ for the measurement):
  M1 cn_term    : normalized cn_term occurs in the folded/normalized query
  M2 token      : a query token (folded length >= 4) is contained in a cn_term
  M3 alias-LHS  : an alias left-hand side occurs in the folded/normalized query
  M4 latin      : a purely Latin query token (folded, >= 3) equals an alias right-hand side or a
                  cn_term
  selection     : longest span first, then lowest row_id; spans overlapped by a kept span are
                  dropped (a short generic word can no longer swallow a longer clinical entity)
  phrase        : "<query with each kept span followed by ' <english anchor>'>"

Switch: env EYEKB_CN_REWRITE read once per call; strip().casefold() in {1,true,on,yes} -> on;
unset/any other value -> off; the default is unchanged (off). In the off state this module touches
nothing (callers short-circuit straight through). Bridge path: env EYEKB_CN_BRIDGE_TSV overrides;
when unset the default absolute path is used. If the bridge is missing/corrupted, the on state runs
every query as-is and discloses status=bridge_missing (no raise, no service crash).

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

# —— the norm / fold / clean_part helpers below are a verbatim superset of the frozen
#    d1_rewrite_rules.py helpers (fold and the alias/anchor handling are the v2 additions) ——
CJK_RE = re.compile(r'[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u3400-\u4dbf]')
NOISE_SUFFIX = re.compile(r'\s*[—–]\s*[A-Za-z]{2,}\s*$')
LABEL_RX = re.compile(r'(?i)\b(table|fig|figure|chapter|page|ch|p)\.?\s*[0-9]'
                      r'|\b\d+\s*[-–]\s*\d+\b|^\s*\d+\s*$')


def norm(s):
    return re.sub(r'\s+', '', s or '')


def fold(s):
    """Full-width Latin -> half-width, U+3000 -> space, curly quotes -> ', then casefold."""
    out = []
    for ch in (s or ''):
        o = ord(ch)
        if 0xFF01 <= o <= 0xFF5E:
            out.append(chr(o - 0xFEE0))
        elif o == 0x3000:
            out.append(' ')
        elif o in (0x2018, 0x2019):
            out.append("'")
        else:
            out.append(ch)
    return ''.join(out).casefold()


def _fnorm(s):
    return norm(fold(s))


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


def clean_anchor(s):
    """English anchor -> printable phrase; drops a trailing page-title tail such as ' — Deep'."""
    s = re.sub(r'\s+', ' ', (s or '').strip())
    s = NOISE_SUFFIX.sub('', s)
    return ' '.join(clean_part(s))


def enabled():
    return (os.environ.get("EYEKB_CN_REWRITE") or "").strip().casefold() in ON_VALUES


def _qindex(q):
    """folded query, whitespace stripped, plus the raw index of every kept char."""
    qf = fold(q)
    idx = [i for i, ch in enumerate(qf) if not ch.isspace()]
    return ''.join(qf[i] for i in idx), idx


def _candidates(q, rows):
    """All candidate matches; every span is a RAW offset pair into q."""
    qn, idx = _qindex(q)
    if not qn:
        return []
    raw_toks = [t for t in re.split(r'\s+', q) if t]
    out = []

    def add(mode, b, frag, lo, hi):
        out.append({'mode': mode, 'row': b, 'frag': frag, 'lo': lo, 'hi': hi})

    def add_norm(mode, b, frag, nlo, nhi):
        if nhi > nlo:
            add(mode, b, frag, idx[nlo], idx[nhi - 1] + 1)

    def add_raw_tok(mode, b, tok):
        st = q.find(tok)
        if st >= 0:
            add(mode, b, tok, st, st + len(tok))

    for b in rows:
        tn = _fnorm(b.get('cn_term') or '')
        if len(tn) >= 2:
            st = qn.find(tn)
            while st >= 0:
                add_norm('M1', b, b['cn_term'], st, st + len(tn))
                st = qn.find(tn, st + 1)
        for pair in (b.get('aliases') or '').split(';'):
            if '=' not in pair:
                continue
            x, _y = pair.split('=', 1)
            xn = _fnorm(x)
            if len(xn) < 2:
                continue
            st = qn.find(xn)
            while st >= 0:
                add_norm('M3', b, x.strip(), st, st + len(xn))
                st = qn.find(xn, st + 1)
    for tok in raw_toks:
        tf = _fnorm(tok)
        if len(tf) >= 4:
            for b in rows:
                if tf and tf in _fnorm(b.get('cn_term') or ''):
                    add_raw_tok('M2', b, tok)
    for tok in raw_toks:
        tf = _fnorm(tok)
        if len(tf) < 3 or not re.fullmatch(r'[a-z0-9\-]+', tf):
            continue
        for b in rows:
            rhs = [_fnorm(p.split('=', 1)[1]) for p in (b.get('aliases') or '').split(';')
                   if '=' in p]
            if tf in rhs or tf == _fnorm(b.get('cn_term') or ''):
                add_raw_tok('M4', b, tok)
    return out


def _select(q, cands):
    """Longest span first, then lowest row_id; overlapping spans are dropped."""
    uniq = {}
    for c in cands:
        k = (c['lo'], c['hi'], c['row']['row_id'])
        if k not in uniq or c['mode'] < uniq[k]['mode']:
            uniq[k] = c
    ordered = sorted(uniq.values(),
                     key=lambda c: (-(c['hi'] - c['lo']), c['lo'], c['row']['row_id']))
    kept = []
    for c in ordered:
        if any(not (c['hi'] <= k['lo'] or c['lo'] >= k['hi']) for k in kept):
            continue
        kept.append(c)
    return sorted(kept, key=lambda c: c['lo'])


def _pair_ok(x, y):
    """Anchor-sanity filter for one alias pair (x = Chinese side, y = English side).

    Two data-grounded rejections, both measured on the frozen bridge (720 alias pairs):
      R1 label    : y is a bibliographic pointer, not a search term
                    (BRG0004 鉴别诊断 = "Table 4-3, BCSC", BRG0042 眶壁 = "p.2-5"; 10 pairs / 8 rows)
      R2 crossref : both sides are short pure-ASCII abbreviations and differ -- a cross-reference
                    pair rather than a naming pair (BRG0201 "RPE =BRB"; 1 pair; naming pairs such as
                    "RPE=RPE", "中心凹=Fovea", "IPL=IPL" are unaffected)
    A rejected pair yields no anchor; it never falls back to the row's cn_term anchor, because that
    would inject an unrelated concept (CH05's 鉴别诊断 would become "Age-Related Macular
    Degeneration").
    """
    ys = (y or '').strip()
    if not ys or LABEL_RX.search(ys):
        return False
    xs = (x or '').strip()
    ascii_only = lambda s: bool(s) and len(s) <= 4 and not re.search(r'[\u4e00-\u9fff]', s)
    if ascii_only(xs) and ascii_only(ys) and xs.casefold() != ys.casefold():
        return False
    return True


def _pair_anchor(pair):
    x, y = pair.split('=', 1)
    if not _pair_ok(x, y):
        return ''
    return clean_anchor(y)


def _anchor_of(c):
    """English anchor contributed by one candidate."""
    row = c['row']
    pairs = [p for p in (row.get('aliases') or '').split(';') if '=' in p]
    if c['mode'] == 'M3':
        for p in pairs:
            if _fnorm(p.split('=', 1)[0]) == _fnorm(c['frag']):
                a = _pair_anchor(p)
                if a:
                    return a
    elif c['mode'] == 'M4':
        for p in pairs:
            if _fnorm(p.split('=', 1)[1]) == _fnorm(c['frag']):
                a = _pair_anchor(p)
                if a:
                    return a
        a = clean_anchor(c['frag'])
        if a:
            return a
    return clean_anchor(row.get('en_anchor') or '')


def _rewrite(q, rows):
    """Mixed rewrite: insert each kept span's English anchor right after the span."""
    kept = _select(q, _candidates(q, rows))
    picked, seen, anchors = [], set(), []
    for c in kept:
        a = _anchor_of(c)
        if not a:
            continue
        picked.append(c)
        if a.casefold() not in seen:
            seen.add(a.casefold())
            anchors.append(a)
    cuts, cur = [], 0
    for c in picked:
        cuts.append(q[cur:c['hi']])
        cuts.append(' ' + _anchor_of(c))
        cur = c['hi']
    cuts.append(q[cur:])
    final = re.sub(r'\s+', ' ', ''.join(cuts)).strip() if picked else ''
    dropped = [{'row_id': c['row']['row_id'], 'cn_term': c['row'].get('cn_term'),
                'mode': c['mode'], 'matched_fragment': c['frag'],
                'span': [c['lo'], c['hi']]}
               for c in kept if not _anchor_of(c)]
    primary = picked[0] if picked else (kept[0] if kept else None)
    meta = {"status": 'rewrite' if final else 'no_rewrite',
            "rule_version": "v2",
            "match_mode": ';'.join(sorted({c['mode'] for c in picked})),
            "row_id": primary['row']['row_id'] if primary else '',
            "cn_term": primary['row'].get('cn_term', '') if primary else '',
            "matched_fragment": primary['frag'] if primary else '',
            "en_anchor_raw": primary['row'].get('en_anchor', '') if primary else '',
            "final_phrase": final,
            "alias_parts_used": ';'.join('%s=%s' % (c['frag'], _anchor_of(c))
                                         for c in picked if c['mode'] == 'M3'),
            "n_spans": len(kept), "n_anchors": len(anchors),
            "matches": [{'row_id': c['row']['row_id'], 'mode': c['mode'],
                         'matched_fragment': c['frag'], 'span': [c['lo'], c['hi']],
                         'anchor': _anchor_of(c),
                         'cn_term': c['row'].get('cn_term', '')} for c in kept],
            "no_anchor_spans": dropped}
    return (final if final else q), meta


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
    """Rewrite a single query. q = the original search sentence (str).
    Returns (query_used, meta | None); meta is None iff the switch is off."""
    if not enabled():
        return q, None
    if not q or not str(q).strip():
        return q, None
    p, bridge, bsha = _load_bridge()
    if bridge is None:
        return q, {"status": "bridge_missing", "bridge_file": p}
    used, meta = _rewrite(q, bridge)
    meta["bridge_file"] = p
    meta["bridge_sha256"] = bsha
    return used, meta
