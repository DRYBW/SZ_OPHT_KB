#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K2: OLS 证据批跑（by_iri 直取 + label 搜索双通道存原始回函；照 kb5v3 s2 先例）。
所有词条 cl_id 必须有本目录原始回函（PREREG §0.5）。禁凭记忆写号: 号仅作为查询候选，
判定以回函 obo_id+label 为准；不符即 NO_MATCH 或换号重查，全程留痕。"""
import json, os, time, urllib.request, urllib.parse

EV = '/mnt/D/EyeKB/plans/kb9_ocs_20260927/ledgers/ols_evidence_kb9'
os.makedirs(EV, exist_ok=True)
UA = {'User-Agent': 'curl/8 KB9-cl-evidence', 'Accept': 'application/json'}

CAND = {  # kb_word -> cl id 定案由 labelsearch 命中 + by_iri 回函双重验证 (09-24 规范"禁凭记忆写号": 初候选 CL_0000134/CL_0000049 回函 label 不符被拒, 见 ERRATA_*)
    'Melanocyte': ('CL_0000148', 'melanocyte'),
    'Schwann': ('CL_0002573', 'Schwann cell'),
    'Conj_epithelium_suprabasal': ('CL_1000432', 'conjunctival epithelial cell'),  # CL 无分层条, 借父条+layer_descriptor (照 KB7 先例)
}

def fetch(url):
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode('utf-8')
        except Exception as e:
            if i == 2:
                return json.dumps({'_error': str(e)})
            time.sleep(2 * (i + 1))

parsed = []
for term, (sf, expect) in CAND.items():
    url = 'https://www.ebi.ac.uk/ols4/api/terms?iri=' + urllib.parse.quote(f'http://purl.obolibrary.org/obo/{sf}')
    raw = fetch(url)
    fn = f'{EV}/{term}_{sf}.json'
    open(fn, 'w').write(raw)
    rec = {'term': term, 'query_id': sf, 'expected_label': expect, 'ols_raw_file': os.path.basename(fn)}
    try:
        d = json.loads(raw)
        for t in d.get('_embedded', {}).get('terms', []):
            if t.get('lang', 'en') != 'en':
                continue
            syns = [s.get('val') if isinstance(s, dict) else s for s in (t.get('synonyms') or [])]
            rec.update({'obo_id': t.get('obo_id'), 'label': t.get('label'),
                        'def': (t.get('description') or [None])[0], 'syn': syns[:12],
                        'iri': t.get('iri')})
            break
    except Exception as e:
        rec['parse_error'] = str(e)
    rec['label_match'] = bool(rec.get('label')) and rec['label'].strip().lower() == expect.strip().lower()
    rec['retrieved_at'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    parsed.append(rec)
    print(json.dumps(rec, ensure_ascii=False)[:300])

# 附加: OLS label 搜索存证（"melanocyte"/"Schwann cell"/"conjunctival" 全命中清单，防挂错 term）
for q in ['melanocyte', 'Schwann cell', 'conjunctival epithelial cell']:
    url = 'https://www.ebi.ac.uk/ols4/api/search?q=' + urllib.parse.quote(q) + '&ontology=cl&rows=8'
    raw = fetch(url)
    fn = f'{EV}/labelsearch_{q.replace(" ", "_")}.json'
    open(fn, 'w').write(raw)
    try:
        d = json.loads(raw)
        hits = [(x.get('obo_id'), x.get('label')) for x in d.get('response', {}).get('docs', [])]
        print('SEARCH', q, hits[:6])
        parsed.append({'labelsearch': q, 'hits': hits, 'ols_raw_file': os.path.basename(fn),
                       'retrieved_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
    except Exception as e:
        print('SEARCH ERR', q, e)

with open(f'{EV}/_parsed.jsonl', 'w') as f:
    for r in parsed:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('OLS DONE')
