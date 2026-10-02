#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP 查询改写层 (query-rewrite layer, 2026-10-03)

一句话：中文检索句在送入英文嵌入面之前，先经中文术语桥机械翻译成英文检索式；
默认关闭，关闭态服务行为与历史逐字节一致。

规则来源：预注册冻结规则（M1 词级子串包含 >=2 字 / M2 题面 token(>=4) 被桥词
包含 / 最长匹配优先 / row_id 平序 / 检索式=英文锚词+题面相关别名英文部分，
CJK 与全角清洗，<2 或纯符号 token 丢弃）。运行时读冻结桥表 TSV，零重打词表、
零人工挑选。

开关：env EYEKB_CN_REWRITE 每调用读一次；strip().casefold() ∈ {1,true,on,yes}
→ 开，未设/其余值一律关。关闭态本模块零触碰（调用方直通短路）。
桥表路径：env EYEKB_CN_BRIDGE_TSV 覆盖；未设时用默认绝对路径。桥表缺失/损坏时
开动态全题按原题走并披露 status=bridge_missing（不抛错、不崩服务）。

红线：本模块纯函数+只读文件；返回的 rewrite_meta 仅作可审计披露，禁止作为
任何打分/加权/排序输入。
"""
import csv
import hashlib
import os
import re

BRIDGE_DEFAULT = ("/mnt/D/EyeKB/plans/devline_cnbridge_20261002/"
                  "out/CN_BRIDGE_MERGED_v1.tsv")
ON_VALUES = {"1", "true", "on", "yes"}

# —— 以下 norm / CJK_RE / clean_part 与 d1_rewrite_rules.py 冻结版逐字一致 ——
CJK_RE = re.compile(r'[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u3400-\u4dbf]')


def norm(s):
    return re.sub(r'\s+', '', s or '')


def clean_part(s):
    """删 CJK/全角，切 token，去纯符号与短 token。"""
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


# —— 桥表加载: 进程内缓存 (path, mtime, size) 键控，模式同 stage3 _dev_map ——
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
    """单题改写。q=原始检索句 (str)。返回 (query_used, meta|None)。"""
    if not enabled():
        return q, None
    if not q or not str(q).strip():
        return q, None
    p, bridge, bsha = _load_bridge()
    if bridge is None:
        return q, {"status": "bridge_missing", "bridge_file": p}
    qn = norm(q)
    cands = []  # (matchlen, mode, row, fragment) —— 与 d1 冻结规则逐条一致
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
