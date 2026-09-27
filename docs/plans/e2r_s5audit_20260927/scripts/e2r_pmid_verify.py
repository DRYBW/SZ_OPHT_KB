#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2R-2 身份核验：120 对 pmid_context 的 top_titles 逐题反解 PMID（E2R_PREREG §2-§5 冻结算法）。
- EuropePMC REST /search 三步 A/B/C；原始返回落 ledgers/api/；幂等：已有缓存结果则跳过。
- 产物: data/e2r_title_resolution.jsonl, data/e2r_pair_verdicts.tsv,
        data/e2r_whitelist_S5b.json, out/e2r_identity_summary.json
红线: 零 LLM、零下载（检索返回即落盘）、只写本卡目录。"""
import json, re, os, sys, time, hashlib, unicodedata, urllib.parse, urllib.request, datetime
from collections import defaultdict

ROOT = '/mnt/D/EyeKB/plans/e2r_s5audit_20260927'
API = f'{ROOT}/ledgers/api'
os.makedirs(API, exist_ok=True)
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'

H_PMIDS = {'41578023', '40660409'}                      # §3 HRCA 自引集合
H_TITLES = [
    'Single-cell atlas of the transcriptome and chromatin accessibility in the human retina',
    'A scRNA-seq reference contrasting living and early post-mortem human retina across diverse donor states',
]
CLASS_TERMS = {'BC': ['bipolar'], 'AC': ['amacrine'], 'HC': ['horizontal']}
STOP = {'the', 'a', 'an', 'of', 'and', 'in', 'to', 'for', 'with', 'on', 'at', 'by',
        'from', 'across', 'versus', 'vs', 'via', 'their', 'its', 'is', 'are'}

def strip_year(t):
    """v1.2 §2 预处理：剥离 'YYYY:' 年份前缀，返回 (clean_title, year_hint)。"""
    m = re.match(r'^(\d{4})[:：]\s*', t or '')
    if m:
        return t[m.end():], m.group(1)
    return t, None

def fold(s):
    return unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()

def norm(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', fold(s).lower())).strip()

def prefix_match(t_stored, t_cand):
    a, b = norm(t_stored), norm(t_cand)
    if not a or not b:
        return False
    if a == b:
        return True
    m = min(len(a), len(b))
    if m >= 25 and (a.startswith(b) or b.startswith(a)):
        return True
    return False

def pick_med(title, res):
    for r in res or []:
        if r.get('source') == 'MED' and r.get('pmid') and prefix_match(title, r.get('title', '')):
            return r
    return None

def api_get(url, tag):
    """带重试的 GET；原始返回落盘。返回 parsed json 或 None。"""
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'e2r-s5audit/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read().decode('utf-8', 'replace')
            with open(f'{API}/{tag}.json', 'w') as f:
                f.write(data)
            return json.loads(data)
        except Exception as e:
            last = f'{type(e).__name__}: {e}'
            time.sleep(1.5 * (attempt + 1))
    with open(f'{API}/{tag}.ERROR.json', 'w') as f:
        f.write(json.dumps({'url': url, 'error': last}))
    return None

def search(query, tag, extra=''):
    q = urllib.parse.quote(query)
    url = f'{BASE}?query={q}&format=json&resultType=core&pageSize=50{extra}'
    d = api_get(url, tag)
    if d is None:
        return None, 0, []
    res = (d.get('resultList', {}) or {}).get('result') or []
    return d, d.get('hitCount', 0), res

def resolve_title(title):
    """v1.2 §2 冻结：strip_year 预处理 + 四步（E2R_PREREG_v1.1/v1.2）。返回 dict。"""
    Tq, year_hint = strip_year(title)
    out = {'title': title, 'clean': Tq, 'year_hint': year_hint,
           'norm': norm(Tq), 'steps': [], 'algo': 'v1.2',
           'resolved_pmid': None, 'resolved_source': None, 'journal': None,
           'pub_year': None, 'doi': None, 'verifiable': False, 'journal_ok': False}
    if not Tq or not norm(Tq):
        out['fail_reason'] = 'empty_title'
        return out
    t16 = hashlib.md5((norm(Tq) + '|' + (year_hint or '')).encode()).hexdigest()[:16]
    pick = None
    # A: TITLE:"<fold 全串>"
    q = f'TITLE:"{fold(Tq).strip()}"'
    d, hc, res = search(q, f'A_{t16}')
    out['steps'].append({'step': 'A', 'query': q, 'hitCount': hc})
    pick = pick_med(Tq, res)
    # B: 前16词原序短语（len>=118 判截断、弃尾半词）
    if pick is None:
        toks = fold(Tq).split()
        if len(Tq) >= 118:
            toks = toks[:-1]
        ph = ' '.join(toks[:16])
        if len(norm(ph)) >= 20:
            q = f'TITLE:"{ph}"'
            d, hc, res = search(q, f'B_{t16}')
            out['steps'].append({'step': 'B', 'query': q, 'hitCount': hc})
            pick = pick_med(Tq, res)
    # C: TITLE 字段实词 AND
    distinct = [t.lower() for t in re.split(r'[^A-Za-z0-9]+', fold(Tq))
                if len(t) > 3 and t.lower() not in STOP][:12]
    if pick is None and distinct:
        q = 'TITLE:' + ' AND '.join(f'"{t}"' for t in distinct)
        if year_hint:
            q += f' AND YEAR:{year_hint}'
        d, hc, res = search(q, f'C_{t16}')
        out['steps'].append({'step': 'C', 'query': q, 'hitCount': hc})
        pick = pick_med(Tq, res)
        if pick is None and year_hint:  # YEAR 过窄时去年限重跑
            q2 = 'TITLE:' + ' AND '.join(f'"{t}"' for t in distinct)
            d, hc, res = search(q2, f'C2_{t16}')
            out['steps'].append({'step': 'C2', 'query': q2, 'hitCount': hc})
            pick = pick_med(Tq, res)
    # D: 去字段 + SOURCE:MED
    if pick is None and distinct:
        q = ' AND '.join(f'"{t}"' for t in distinct) + ' AND SOURCE:MED'
        if year_hint:
            q = ' AND '.join(f'"{t}"' for t in distinct) + f' AND SOURCE:MED AND YEAR:{year_hint}'
        d, hc, res = search(q, f'D_{t16}')
        out['steps'].append({'step': 'D', 'query': q, 'hitCount': hc})
        pick = pick_med(Tq, res)
        if pick is None:
            q2 = ' AND '.join(f'"{t}"' for t in distinct) + ' AND SOURCE:MED'
            d, hc, res = search(q2, f'D2_{t16}')
            out['steps'].append({'step': 'D2', 'query': q2, 'hitCount': hc})
            pick = pick_med(Tq, res)
    if pick is None:
        out['fail_reason'] = 'unresolvable'
        return out
    pmid = pick.get('pmid') or ''
    src = pick.get('source') or ''
    out['resolved_pmid'] = pmid or None
    out['resolved_source'] = src
    out['doi'] = pick.get('doi')
    out['pub_year'] = pick.get('pubYear')
    ji = (pick.get('journalInfo') or {}).get('journal') or {}
    out['journal'] = ji.get('title') or pick.get('journalTitle')
    out['journal_ok'] = bool(out['journal'])
    out['verifiable'] = bool(pmid) and src == 'MED'
    if not out['verifiable']:
        out['fail_reason'] = f'non_MED_or_no_pmid(source={src})'
    out['hrca_self'] = (pmid in H_PMIDS) or any(prefix_match(nt, pick.get('title', '')) for nt in H_TITLES)
    out['matched_title'] = pick.get('title')
    return out

def pair_flags(gene, cls, tinfo):
    tl = norm(tinfo.get('matched_title') or tinfo.get('title') or '')
    gene_hit = bool(re.search(r'(?<![a-z0-9])' + re.escape(gene.lower()) + r'(?![a-z0-9])', tl))
    terms = CLASS_TERMS.get(cls, [])
    cls_hit = any(t in tl for t in terms)
    return gene_hit, cls_hit

def main():
    pairs = [json.loads(l) for l in open(f'{ROOT}/data/e2r_pcx_pairs.jsonl')]
    # 唯一标题集合（title1 与 title2 分列；空串不查）
    uniq = set()
    for p in pairs:
        if p['title1']:
            uniq.add(p['title1'])
        if p['title2']:
            uniq.add(p['title2'])
    uniq = sorted(uniq)
    cache_path = f'{ROOT}/data/e2r_title_resolution.jsonl'
    cache = {}
    if os.path.exists(cache_path):
        for l in open(cache_path):
            d = json.loads(l)
            cache[d['title']] = d
    print(f'unique titles to resolve: {len(uniq)} (cached: {len(cache)})', flush=True)
    # ---- v1.2 验证锚（预注册件规定三锚；任一不中 exit 2 停工，不产判读）
    anchor_defs = [
        ('Non-coding RNAs in the development of sensory organs and related diseases.', '23588489'),
        ('MicroRNAs in the Neural Retina.', '24745005'),
        ('A scRNA-seq reference contrasting living and early post-mortem human retina '
         'across diverse donor states.', '40660409')]
    fh0 = open(cache_path, 'a')
    for T, want in anchor_defs:
        if T not in cache:
            r = resolve_title(T)
            cache[T] = r
            fh0.write(json.dumps(r, ensure_ascii=False) + '\n'); fh0.flush()
            time.sleep(0.45)
        else:
            r = cache[T]
        if not (r.get('resolved_pmid') == want and r.get('verifiable')):
            print(f'ANCHOR FAIL: {T[:60]} -> {json.dumps(r, ensure_ascii=False)[:300]}')
            fh0.close()
            sys.exit(2)
        print(f'ANCHOR PASS: {T[:44]}... -> {r["resolved_pmid"]}', flush=True)
    fh0.close()

    todo = [t for t in uniq if t not in cache]
    fh = open(cache_path, 'a')
    for i, t in enumerate(todo):
        r = resolve_title(t)
        cache[t] = r
        fh.write(json.dumps(r, ensure_ascii=False) + '\n'); fh.flush()
        if (i + 1) % 20 == 0:
            print(f'  resolved {i+1}/{len(todo)}', flush=True)
        time.sleep(0.45)
    fh.close()

    # 逐对四态（§5）
    verds = []
    for p in pairs:
        key = (p['cls'], p['gene'])
        ts = []
        for slot in ('title1', 'title2'):
            t = p[slot]
            if t and t in cache:
                r = cache[t]
                gh, ch = pair_flags(p['gene'], p['cls'], r)
                ts.append({'slot': slot, 'verifiable': r['verifiable'], 'hrca_self': r.get('hrca_self', False),
                           'gene_hit': gh, 'class_hit': ch, 'relevant': gh or ch,
                           'pmid': r.get('resolved_pmid'), 'journal_ok': r.get('journal_ok', False)})
            else:
                ts.append({'slot': slot, 'verifiable': False, 'hrca_self': False, 'gene_hit': False,
                           'class_hit': False, 'relevant': False, 'pmid': None, 'journal_ok': False,
                           'note': 'empty_title' if not t else 'missing'})
        verd_ok = [x for x in ts if x['verifiable']]
        credit = [x for x in verd_ok if not x['hrca_self']]
        credit_rel = [x for x in credit if x['relevant']]
        if not verd_ok:
            status = 'unverifiable'
        elif not credit:
            status = 'self_only'
        elif not credit_rel:
            status = 'creditable'          # 非自引可核但离题
        else:
            status = 'creditable_rel'
        first = next((x for x in ts if x['slot'] == 'title1'), None)
        verds.append({'cls': p['cls'], 'gene': p['gene'], 'n_hits': p['n_hits'], 'status': status,
                      'creditable': bool(credit), 'creditable_rel': bool(credit_rel),
                      'verifiable': bool(verd_ok),
                      'first_is_hrca': bool(first and first['verifiable'] and first['hrca_self']),
                      'pmids': ';'.join(sorted({x['pmid'] for x in verd_ok if x['pmid']})),
                      'titles': [ts_detail['verifiable'] for ts_detail in ts]})
    with open(f'{ROOT}/data/e2r_pair_verdicts.tsv', 'w') as f:
        f.write('\t'.join(['cls', 'gene', 'n_hits', 'status', 'verifiable', 'creditable',
                           'creditable_rel', 'first_is_hrca', 'pmids']) + '\n')
        for v in verds:
            f.write('\t'.join([v['cls'], v['gene'], str(v['n_hits']), v['status'],
                               str(int(v['verifiable'])), str(int(v['creditable'])),
                               str(int(v['creditable_rel'])), str(int(v['first_is_hrca'])),
                               v['pmids']]) + '\n')

    n = len(verds)
    stats = {
        'n_pairs': n,
        'unverifiable': sum(1 for v in verds if v['status'] == 'unverifiable'),
        'self_only': sum(1 for v in verds if v['status'] == 'self_only'),
        'creditable_offtopic': sum(1 for v in verds if v['status'] == 'creditable'),
        'creditable_rel': sum(1 for v in verds if v['status'] == 'creditable_rel'),
        'verifiable_any': sum(1 for v in verds if v['verifiable']),
        'creditable_any': sum(1 for v in verds if v['creditable']),
        'first_is_hrca': sum(1 for v in verds if v['first_is_hrca']),
        'verifiable_rate': None, 'not_self_share_among_verifiable': None,
        'offtopic_share_among_creditable': None,
    }
    stats['verifiable_rate'] = round(stats['verifiable_any'] / n, 4)
    va = stats['verifiable_any']
    stats['not_self_share_among_verifiable'] = round(stats['creditable_any'] / va, 4) if va else None
    stats['offtopic_share_among_creditable'] = round(
        stats['creditable_offtopic'] / stats['creditable_any'], 4) if stats['creditable_any'] else None
    gate = {
        'verifiable_rate_ge50': stats['verifiable_rate'] >= 0.5,
        'non_hrca_self_majority': stats['creditable_any'] > stats['self_only'],
        'mass_offtopic': (stats['offtopic_share_among_creditable'] or 0) > 0.5,
    }
    row1 = gate['verifiable_rate_ge50'] and gate['non_hrca_self_majority'] and not gate['mass_offtopic']
    row2 = (not gate['verifiable_rate_ge50']) or gate['mass_offtopic']
    gate['matrix_row'] = 'ROW1_S5b_established' if (row1 and not row2) else ('ROW2_keep_strict' if (row2 and not row1) else 'AMBIGUOUS_report')
    summary = {'stats': stats, 'gate': gate,
               'n_titles_resolved': len(cache),
               'titles_unresolvable': sum(1 for r in cache.values() if not r.get('verifiable')),
               'ran': str(datetime.datetime.now())}
    json.dump(summary, open(f'{ROOT}/out/e2r_identity_summary.json', 'w'), ensure_ascii=False, indent=1)

    wl = {'S5b': [f"retina_interneuron::{v['cls']}::{v['gene']}" for v in verds if v['creditable']],
          'S5b_rel': [f"retina_interneuron::{v['cls']}::{v['gene']}" for v in verds if v['creditable_rel']]}
    json.dump(wl, open(f'{ROOT}/data/e2r_whitelist_S5b.json', 'w'), indent=1)
    print(json.dumps(summary['stats'], ensure_ascii=False))
    print(json.dumps(summary['gate'], ensure_ascii=False))
    print('E2R_VERIFY_DONE')

if __name__ == '__main__':
    main()
