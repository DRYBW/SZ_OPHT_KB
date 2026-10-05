#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP query-rewrite layer, v3.1 (CN-REWRITE-FLIP, 2026-10-05)

In one sentence: before a Chinese search sentence is fed to the English embedding surface, the
bridge terms it contains are located and their English anchors are inserted in place; the rest of
the sentence is preserved verbatim. Search text that contains no Chinese character is never
touched.

v3.1 = v3 plus the two changes ordered by BRIEF_CN_REWRITE_FLIP.md (coordinator ruling chain
astra_cnrewrite_20261005 -> DECISION_DEFAULT_SWITCH -> RULING_FIX1 -> FIX2 vol3 pass):

  CH-3 (existence gate, new) — a query containing no CJK character at all is returned unchanged
      with NO disclosure meta, before the bridge is consulted. Rationale: the layer exists to route
      a Chinese query into the English retrieval surface; English search text is already inside the
      corpus language, so anchor injection has no upside and only adds disturbance. Repaired defect
      (coordinator behavioural probe, 2026-10-05): v3's M4 rule (a purely Latin token matched
      against an alias right-hand side or a cn_term) rewrote purely English queries, e.g.
      'retinal pigment epithelium markers' -> '... Epithelium markers'. The gate is mechanical:
      the ORIGINAL query string is searched for any character in CJK_RE, which includes the
      full-width forms (U+FF00-FFEF) — so a query that mixes full-width Latin, e.g. a full-width
      'IPL', is still serviced. Detection runs on the raw query, not on the folded one, because
      folding maps full-width Latin to half-width and would erase the only non-ASCII marker.

  CH-4 (default flip) — the switch default is ON: an UNSET EYEKB_CN_REWRITE means enabled. The
      escape door is kept forever: an explicit 0 / off / false / no turns the layer off, restoring
      byte-identical pre-rewrite behaviour. 1 / true / on / yes stay ON.

v3 = v2 (mixed in-place anchor insertion) plus the two repairs ordered by RULING_FIX1_20261005
§放行前置 1:

  CH-1 (R1 defect, mandatory) — same-span tie-break by MATCH-MODE PRIORITY.
      v2's selection sorts candidate spans by (length desc, leftmost, row_id). When a generic short
      word is present as a whitespace-delimited token, it can be matched twice on the very same
      span: once as M1/M3 by its OWN row A (the generic word is A's cn_term or alias), and once as
      M2 by a LONGER row B whose cn_term contains it and whose row_id is lower (M2 = "a query token
      is contained in this row's cn_term"). With equal length and equal left edge the v2 ordering
      fell through to row_id, so B won and the generic word inherited the longer entity's anchor
      (observed on the vol2 challenge volume: 视网膜病 -> "Diabetic Retinopathy"). v3 inserts the
      match-mode priority key AFTER the left edge, i.e. it can only decide comparisons that were
      already a same-span tie: M1/M3 (0) > M4 (1) > M2 (2). The primary ordering (longest span
      first, then leftmost) is untouched, so no span that used to win can be displaced by a shorter
      or righter one.

  CH-2 (R3 defect, option measured by the FIX2 card) — negation scope guard.
      v2 had no negation scoping: in a contrast question ("A 不是 B") the EXCLUDED side B also
      received an English anchor, i.e. the layer reinforced the very entity the question excludes.
      With NEG_SCOPE_ENABLED, a kept candidate whose matched fragment's LEFT EDGE is immediately
      preceded (in whitespace-stripped coordinates, so 「不是 B」 and 「不是B」 behave alike) by a
      registered negation cue (NEG_CUES) contributes no anchor. The span is still reserved and the
      original characters are still preserved verbatim — zero deletion is unaffected; only the
      English anchor injection is skipped, and the candidate is disclosed under no_anchor_spans with
      reason "neg_scope:<cue>".

Rule chain (v3.1; see plans/cn_rewrite_fix2_20261005/ and plans/cn_rewrite_flip_20261005/ for the
measurements):
  existence gate: a query with no CJK character is returned unchanged with no meta (CH-3); it is
                  evaluated first, so the modes below are only reached by CJK-bearing queries
  M1 cn_term    : normalized cn_term occurs in the folded/normalized query
  M2 token      : a query token (folded length >= 4) is contained in a cn_term
  M3 alias-LHS  : an alias left-hand side occurs in the folded/normalized query
  M4 latin      : a purely Latin query token (folded, >= 3) equals an alias right-hand side or a
                  cn_term
  selection     : longest span first, then leftmost, then match-mode priority (M1/M3 > M4 > M2),
                  then lowest row_id; spans overlapped by a kept span are dropped
  negation scope: a kept span whose left edge is immediately preceded by a registered negation cue
                  contributes no anchor (span reserved; text preserved)
  phrase        : "<query with each kept span followed by ' <english anchor>'>"

Existence rule for the disclosure key (v3.1): rewrite_meta is None in exactly three cases —
(a) the switch is off, (b) the query is blank, (c) the query contains no CJK character. Cases (b)
and (c) are the documented zero-intervention promise: the layer is invisible to English / numeric /
purely symbolic search text no matter how the switch is set.

Switch: env EYEKB_CN_REWRITE, read once per call. v3.1 default: unset (or empty) -> ON. Explicit
1/true/on/yes -> ON. Escape door, kept forever: 0/off/false/no -> OFF. Any other unrecognised value
-> OFF (resolves to the safe side). In the off state this module touches nothing (callers
short-circuit straight through, zero new response keys). Bridge path: env EYEKB_CN_BRIDGE_TSV
overrides; when unset the default absolute path is used. If the bridge is missing/corrupted, the on
state runs every query as-is and discloses status=bridge_missing (no raise, no service crash).

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
OFF_VALUES = {"0", "false", "off", "no"}
RULE_VERSION = "v3.1"

# CH-1: match-mode priority, used ONLY to break a same-span tie (lower wins).
MODE_PRI = {'M1': 0, 'M3': 0, 'M4': 1, 'M2': 2}

# CH-2: registered negation-cue list (self-defined per RULING_FIX1 §逐残差裁定 R3-a, 词表自定+登记).
# The cue must END exactly at the matched fragment's left edge ("左缘紧邻"); longest wins. The guard
# is enabled or disabled by the single constant below (the FIX2 card measured both settings and the
# measurement that selected the setting is registered in the card's report).
NEG_CUES = ('区别于', '不同于', '而不是', '并不是', '不是', '并非', '除外')
NEG_SCOPE_ENABLED = True

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
    """v3.1 default-ON semantics (CH-4).

    unset or empty      -> True   (the v3.1 default; the layer is active without configuration)
    1/true/on/yes       -> True
    0/off/false/no      -> False  (the escape door; byte-identical pre-rewrite behaviour)
    anything else       -> False  (an unrecognised value resolves to the safe/passive side)
    """
    v = os.environ.get("EYEKB_CN_REWRITE")
    if v is None or v.strip() == "":
        return True
    s = v.strip().casefold()
    if s in ON_VALUES:
        return True
    if s in OFF_VALUES:
        return False
    return False


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
    """Longest span first, then leftmost, then (CH-1) match-mode priority, then lowest row_id;
    overlapping spans are dropped. The priority key sits AFTER the left edge so it can only break a
    tie the v2 ordering left to row_id, i.e. two candidates on the SAME span."""
    uniq = {}
    for c in cands:
        k = (c['lo'], c['hi'], c['row']['row_id'])
        if k not in uniq or c['mode'] < uniq[k]['mode']:
            uniq[k] = c
    ordered = sorted(uniq.values(),
                     key=lambda c: (-(c['hi'] - c['lo']), c['lo'], MODE_PRI.get(c['mode'], 1),
                                    c['row']['row_id']))
    kept = []
    for c in ordered:
        if any(not (c['hi'] <= k['lo'] or c['lo'] >= k['hi']) for k in kept):
            continue
        kept.append(c)
    return sorted(kept, key=lambda c: c['lo'])


def _neg_cue_at(qn, idx, lo):
    """CH-2: the registered negation cue that ENDS exactly at the fragment's left edge, else ''.

    Comparison is done in folded, whitespace-stripped coordinates so a cue and the fragment stay
    adjacent across a space. `idx` maps normalized positions back to raw offsets.
    """
    from bisect import bisect_left
    i = bisect_left(idx, lo)
    if i >= len(idx) or idx[i] != lo:
        return ''
    for cue in sorted(NEG_CUES, key=len, reverse=True):
        s = i - len(cue)
        if s >= 0 and qn[s:i] == cue:
            return cue
    return ''


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
    """English anchor contributed by one candidate.

    An alias-derived candidate never falls back to its row's cn_term anchor: if the matched alias
    pair exists but is rejected by the anchor-sanity filter, the candidate contributes nothing.
    (Without that rule CH05's 鉴别诊断 would fall back to BRG0004's cn_term anchor and inject
    "Age-Related Macular Degeneration" into a glaucoma query.)
    """
    row = c['row']
    pairs = [p for p in (row.get('aliases') or '').split(';') if '=' in p]
    if c['mode'] == 'M3':
        for p in pairs:
            if _fnorm(p.split('=', 1)[0]) == _fnorm(c['frag']):
                return _pair_anchor(p)
        return ''
    if c['mode'] == 'M4':
        for p in pairs:
            if _fnorm(p.split('=', 1)[1]) == _fnorm(c['frag']):
                return _pair_anchor(p)
        return clean_anchor(c['frag'])
    return clean_anchor(row.get('en_anchor') or '')


def _rewrite(q, rows):
    """Mixed rewrite: insert each kept span's English anchor right after the span.

    CH-2: kept spans whose left edge is immediately preceded by a registered negation cue are
    disclosed in no_anchor_spans (reason neg_scope:<cue>) and contribute no anchor.
    """
    kept = _select(q, _candidates(q, rows))
    suppressed = {}
    if NEG_SCOPE_ENABLED:
        qn, idx = _qindex(q)
        for c in kept:
            cue = _neg_cue_at(qn, idx, c['lo'])
            if cue:
                suppressed[(c['lo'], c['hi'], c['row']['row_id'])] = cue
    picked, anchors = [], []
    seen = set()
    for c in kept:
        if (c['lo'], c['hi'], c['row']['row_id']) in suppressed:
            continue
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

    def _na(c):
        key = (c['lo'], c['hi'], c['row']['row_id'])
        d = {'row_id': c['row']['row_id'], 'cn_term': c['row'].get('cn_term'),
             'mode': c['mode'], 'matched_fragment': c['frag'], 'span': [c['lo'], c['hi']]}
        d['reason'] = ('neg_scope:' + suppressed[key]) if key in suppressed else 'anchor_rejected'
        return d

    dropped = [_na(c) for c in kept
               if (not _anchor_of(c)) or (c['lo'], c['hi'], c['row']['row_id']) in suppressed]
    primary = picked[0] if picked else (kept[0] if kept else None)
    meta = {"status": 'rewrite' if final else 'no_rewrite',
            "rule_version": RULE_VERSION,
            "neg_scope": bool(NEG_SCOPE_ENABLED),
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
    Returns (query_used, meta | None); meta is None iff the switch is off, the query is blank, or
    the query contains no CJK character (the CH-3 zero-intervention promise)."""
    if not enabled():
        return q, None
    if not q or not str(q).strip():
        return q, None
    if not CJK_RE.search(q if isinstance(q, str) else str(q)):
        # CH-3 existence gate: no CJK character anywhere -> the query is already in the retrieval
        # surface's own language; skip every anchor mode (M3/M4 included) and disclose nothing.
        return q, None
    p, bridge, bsha = _load_bridge()
    if bridge is None:
        return q, {"status": "bridge_missing", "bridge_file": p}
    used, meta = _rewrite(q, bridge)
    meta["bridge_file"] = p
    meta["bridge_sha256"] = bsha
    return used, meta
