#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PME2 第二批检索引擎（PME2_PREREG_v1 §2.3 直译；规则冻结，零 LLM）。
复用一批引擎 pme_search（in_b1_snapshot 只读副本）的 grade/句切分/marker 词表，
monkey-patch：①类短语/doc_re 按 PREREG §2.1 扩展表（全 29 类对称列出）；
②APC doc_re 采用一批 A5 去循环修正版（继承）；③gene_re 扩展为 符号∪保留别名（PREREG §2.2 表驱动）。
逐键落 ledgers/raw2/，账本 out/pme2_hits.jsonl；双遍（A1 复用：非 strong 补 sort=CITED）；断点续跑。"""
import json, re, sys, os, time, threading, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT2 = '/mnt/D/EyeKB/plans/panel_pmid_20260927/batch2'
sys.path.insert(0, f'{ROOT2}/in_b1_snapshot')
import pme_search as ps

RAW2 = f'{ROOT2}/ledgers/raw2'
os.makedirs(RAW2, exist_ok=True)

# ---- §2.1 类扩展表（冻结；"—"类不加） ----
NEW_APC = r'MHC\s*class\s*II|\bMHC-?II\b|antigen[-\s]presenting|\bAPCs?\b|class\s*II\s+(?:HLA|MHC|antigen)'  # 一批 A5 修正版（继承）
PHRASE_ADD = {
 'Rod':   [r'"rod outer segment"'],
 'Cone':  [r'"cone outer segment"'],
 'BC':    [r'"rod bipolar cell"', r'"cone bipolar cell"', r'"ON bipolar cell"', r'"OFF bipolar cell"'],
 'AC':    [r'"amacrine cell"', r'"amacrine neuron"', r'"retinal amacrine"'],
 'HC':    [r'"retinal horizontal cell"'],
 'RGC':   [r'"retinal ganglion neuron"'],
 'MG':    [r'"muller glial cell"', r'"retinal muller"', r'"Müller glial cell"'],
 'SMC':   [r'"smooth muscle"'],
}
DOCRE_ADD = {
 'Rod':  r'rod\s*outer\s*segment',
 'Cone': r'cone\s*outer\s*segment',
 'BC':   r'rod\s+bipolar|cone\s+bipolar|\bON\s+bipolar|\bOFF\s+bipolar',
 'RGC':  r'retinal\s+ganglion\s+neuron',
 'MG':   r'm[üu]ller\s+glial|retinal\s+m[üu]ller',
 'SMC':  r'smooth\s+muscle',
 'Mac_DAM_LAM': r'\bLAM\b[^.]{0,60}macrophage',
}
for cls in ps.CLASSES:
    ph, dre, gd = ps.CLASSES[cls]
    ph = list(ph) + PHRASE_ADD.get(cls, [])
    if cls == 'APC_MHCII_high':
        dre = NEW_APC
    elif cls in DOCRE_ADD:
        dre = dre + '|' + DOCRE_ADD[cls]
    ps.CLASSES[cls] = (ph, dre, gd)

# ---- §2.2 别名表加载 + G' 正则 ----
ALIASES = {}
for i, line in enumerate(open(f'{ROOT2}/data/alias_gene_v2.tsv')):
    if i == 0:
        continue
    g, a, src, kept, why = line.rstrip('\n').split('\t')
    if kept == '1':
        ALIASES.setdefault(g, []).append(a)

def alias_re_part(alias):
    parts = [re.escape(p) for p in re.split(r'[\s\-]+', alias.strip()) if p]
    return r'\b' + r'[\s\-]?'.join(parts) + r'\b'

_orig_gene_re = ps.gene_re
def gene_re2(gene):
    r0 = _orig_gene_re(gene)  # 符号形（含 CS_GENES 大小写规则）
    als = ALIASES.get(gene, [])
    if not als:
        return r0
    f = 0 if gene in ps.CS_GENES else re.IGNORECASE
    alt = '|'.join(alias_re_part(a) for a in als)
    return re.compile(r0.pattern + '|' + alt, f)
ps.gene_re = gene_re2

# ---- 第二检索式 query ----
def query2_for(cls, gene):
    ph = ' OR '.join(ps.CLASSES[cls][0])
    terms = [gene] + [f'"{a}"' for a in ALIASES.get(gene, [])]
    gpart = terms[0] if len(terms) == 1 else '(' + ' OR '.join(terms) + ')'
    return f'({ph}) AND {gpart} AND (SRC:MED)'

ps.query_for_orig = ps.query_for
ps.query_for = query2_for

# ---- 逐键处理（一批 process_one 语义：cache 跳过、双遍、raw 留档、账本追加）----
_LOCK = threading.Lock()

def process_one(hits_f, cls, gene):
    slug2 = ps.slug(cls, gene)
    rp = f'{RAW2}/{slug2}.json'
    if os.path.exists(rp):
        try:
            old = json.load(open(rp))
            if old.get('error') is None and 'raw1' in old:
                return 'cached'
        except Exception:
            os.remove(rp)
    q = query2_for(cls, gene)
    url1 = ps.build_url(q)
    raw1, err = ps.fetch(url1)
    import datetime
    rec = {'class': cls, 'gene': gene, 'query': q, 'aliases_used': ALIASES.get(gene, []),
           'url1': url1, 'retrieved_at': datetime.datetime.isoformat(datetime.datetime.now()),
           'error': err, 'raw1': raw1, 'url2': None, 'raw2': None}
    raws = [raw1]
    if err is None:
        g1 = ps.grade(cls, gene, raws)[0]
        if g1 != 'strong':
            # A1' 修正：裸 sort=CITED 被 EBI 503 拒（一批 84/84 二遍全灭的根因），官方格式须带方向
            u2 = ps.build_url(q, sort='CITED%20desc')
            raw2, err2 = ps.fetch(u2)
            rec['url2'] = u2; rec['raw2'] = raw2
            if err2:
                rec['error2'] = err2
            else:
                raws.append(raw2)
    with open(rp, 'w') as f:
        json.dump(rec, f, ensure_ascii=False)
    if err:
        return 'FAIL'
    n = sum((r or {}).get('hitCount', 0) for r in raws)
    grade_v, strongs, weaks, ncand = ps.grade(cls, gene, raws)
    with _LOCK:
        hits_f.write(json.dumps({'class': cls, 'gene': gene, 'query': q,
                                 'aliases_used': ALIASES.get(gene, []),
                                 'hitCount': n, 'n_candidates': ncand, 'grade': grade_v,
                                 'strong_evidence': strongs, 'weak_refs': weaks,
                                 'raw_file': os.path.basename(rp)}, ensure_ascii=False) + '\n')
        hits_f.flush()
    return grade_v

def main():
    keys = []
    for l in open(f'{ROOT2}/data/batch2_keys.txt'):
        c, g = l.rstrip('\n').split('|')
        keys.append((c, g))
    print(f'[PME2] keys={len(keys)} aliased={sum(1 for c,g in keys if g in ALIASES)} threads=8', flush=True)
    hits_f = open(f'{ROOT2}/out/pme2_hits.jsonl', 'a')
    cnt = {'strong': 0, 'weak': 0, 'none': 0, 'cached': 0, 'FAIL': 0}
    i = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(process_one, hits_f, c, g): (c, g) for c, g in keys}
        for fut in as_completed(futs):
            c, g = futs[fut]
            i += 1
            try:
                v = fut.result()
            except Exception as e:
                v = 'FAIL'
                print(f'[{i}] {c}/{g} EXC {e}', flush=True)
            cnt[v] = cnt.get(v, 0) + 1
            if i % 20 == 0 or v == 'FAIL':
                print(f'[{i}/{len(keys)}] {c}/{g} -> {v} | so far {cnt}', flush=True)
    hits_f.close()
    print(f'[PME2] DONE {cnt}', flush=True)
    sys.exit(2 if cnt.get('FAIL') else 0)

if __name__ == '__main__':
    main()
