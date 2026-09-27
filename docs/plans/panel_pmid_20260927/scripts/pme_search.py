#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PME 检索+分级引擎（PME_PREREG_v1.md §2-§4 直译；规则冻结，禁临时加词）。
逐键落 ledgers/raw/<cls>__<gene>.json，账本追加 out/pme_hits.jsonl；断点续跑（raw 存在即跳过）。
零 LLM 调用。网络失败重试 3 次后登记 fail 继续，不中断。"""
import json, re, sys, time, urllib.parse, urllib.request, datetime, os

ROOT = '/mnt/D/EyeKB/plans/panel_pmid_20260927'
RAW = f'{ROOT}/ledgers/raw'
API = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'

# ---- 类规格（冻结自 PREREG §3）: query 短语 + 文档级 doc_re + 可选 guard ----
def _g_bipolar(doc):
    d = doc.lower()
    if 'bipolar disorder' in d or 'bipolar affective' in d:
        return any(t in d for t in ('retina', 'photorecept', 'amacrine', 'inner nuclear', 'bipolar cell of the'))
    return True
def _g_rod_cone_bare(doc):
    return 'photorecept' in doc.lower()

CLASSES = {
 'Rod':   (['"rod photoreceptor"', '"rod cell"', 'photoreceptor rods'],
           r'rod\s*photoreceptor|rod\s*cell|photoreceptor\s+rods?|\brods?\b', None),
 'Cone':  (['"cone photoreceptor"', '"cone cell"', 'cone opsin'],
           r'cone\s*photoreceptor|cone\s*cell|photoreceptor\s+cones?|\bcones?\b', None),
 'BC':    (['"retinal bipolar cell"', '"bipolar cell"'],
           r'retinal\s+bipolar|bipolar\s*cells?|bipolar\s*neurons?', _g_bipolar),
 'AC':    (['amacrine'], r'amacrine', None),
 'HC':    (['"horizontal cell"'], r'horizontal\s*cells?', None),
 'RGC':   (['"retinal ganglion cell"', 'RGC'], r'retinal\s+ganglion|\bRGC', None),
 'MG':    (['"muller glia"', '"muller cell"', '"Müller glia"', 'Mueller'],
           r'mü?l?ller?\s*glia|m[üu]ller\s*cells?|mueller', None),
 'Astro': (['astrocyte'], r'astrocyte|astroglia', None),
 'Microglia': (['microglia OR microglial'], r'microglia|microglial', None),
 'Endo':  (['"endothelial cell"', 'endothelium'], r'endotheli', None),
 'Endo_Patho': (['"tumor endothelial"', '"tumor endothelium"', '"neovascular endothelium"',
                 '"endothelial activation"', '"activated endothelium"', '"pathological endothelium"'],
           r'(tumor|tumour|neovascular\w*|activated|pathological|inflammatory|hypoxic\w*)[^.;]{0,40}endothel|endothel\w*[^.;]{0,40}(activation|dysfunction|neovascular)', None),
 'Pericyte': (['pericyte'], r'pericyte', None),
 'SMC':   (['"smooth muscle cell"'], r'smooth\s+muscle', None),
 'Fibroblast': (['fibroblast'], r'fibroblast', None),
 'Myofibroblast': (['myofibroblast'], r'myofibroblast', None),
 'Mono_Classical': (['"classical monocyte"', '"monocyte subsets"', '"CD14+ monocyte"', '"CD14 high monocyte"'],
           r'(?<!non-)classical\s+monocyte|monocyte\s+subset|CD14[^.]{0,30}monocyte', None),
 'Mono_Nonclassical': (['"nonclassical monocyte"', '"non-classical monocyte"', '"patrolling monocyte"'],
           r'non[-\s]?classical\s+monocyte|patrolling\s+monocyte', None),
 'Mac_Tissue': (['"tissue macrophage"', '"resident macrophage"', 'macrophage'], r'macrophage', None),
 'Mac_DAM_LAM': (['"disease-associated macrophage"', '"lipid-associated macrophage"'],
           r'(disease|lipid)[- ]associated\s+macrophage|\bDAMs?\b[^.]{0,60}macrophage|macrophage[^.]{0,60}\b(DAM|LAM)\b', None),
 'APC_MHCII_high': (['"MHC class II"', '"antigen-presenting cell"', '"HLA-DR"'],
           r'MHC\s*class\s*II|HLA[-\s]?[DdR]|antigen[-\s]presenting', None),
 'cDC1':  (['cDC1', '"type 1 conventional dendritic"', '"cross-presenting dendritic"'],
           r'cDC\s?-?\s?1\b|type\s*1\s*conventional\s*dendritic|cross-?presenting\s*dendritic|\bDC3\b', None),
 'cDC2':  (['cDC2', '"type 2 conventional dendritic"'],
           r'cDC\s?-?\s?2\b|type\s*2\s*conventional\s*dendritic|\bDC4\b', None),
 'pDC':   (['"plasmacytoid dendritic"', 'pDC'], r'plasmacytoid|\bpDCs?\b', None),
 'T':     (['"T cell"', '"T lymphocyte"'], r'\bT[\s-]cells?\b|\bT[\s-]lymphocyte', None),
 'NK':    (['"natural killer cell"', '"NK cell"'], r'natural\s+killer|\bNK[\s-]cells?', None),
 'B':     (['"B cell"', '"B lymphocyte"'], r'\bB[\s-]cells?\b|\bB[\s-]lymphocyte', None),
 'Plasma': (['"plasma cell"', 'plasmablast'], r'plasma\s*cells?\b|plasmablast|immunoglobulin[-\s]secreting', None),
 'Granulocyte': (['granulocyte', 'neutrophil'], r'granulocyte|neutrophil|polymorphonuclear', None),
 'Proliferating': (['proliferation', '"proliferating cell"'], r'proliferat', None),
}
# Rod guard: bare 'RODS' needs photoreceptor in doc
ROD_GUARD = True

MARKER_RE = re.compile(r'\bmarkers?\b|\bmarking\b|specific|\bexpress|defines?\b|\blabel|\bidentif|characteris|signature|hallmark|canonical|\bpositive\b|\bstain', re.I)
CS_GENES = {'CAMP'}  # 大小写敏感（防 cAMP 误配）

def slug(cls, gene):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', f'{cls}__{gene}')

def sentences(title, abstract):
    s = [t for t in [re.sub(r'<[^>]+>', '', title or '').strip()] if t]
    if abstract:
        a = re.sub(r'<[^>]+>', ' ', abstract)
        s += [x.strip() for x in re.split(r'(?<=[.?!;])\s+', a) if x.strip()]
    return s

def gene_re(gene):
    f = 0 if gene in CS_GENES else re.IGNORECASE
    return re.compile(r'\b' + re.escape(gene) + r'\b', f)

PHOTO_PHRASE = {'Rod': r'rod\s*photoreceptor|rod\s*cell',
                'Cone': r'cone\s*photoreceptor|cone\s*cell'}

def class_sent_ok(sent, cls, gene_gr, doc_all):
    doc_re = CLASSES[cls][1]; guard = CLASSES[cls][2]
    if not gene_gr.search(sent):
        return False
    if not re.search(doc_re, sent, re.I):
        return False
    if cls in PHOTO_PHRASE and not re.search(PHOTO_PHRASE[cls], sent, re.I):
        # bare rods/cones 只在文档有 photoreceptor/retina 语境时认类（防 lens cone beam 等误配）
        if not re.search(r'photorecept|retina', doc_all, re.I):
            return False
    if guard and not guard(doc_all):
        return False
    return True

def query_for(cls, gene):
    ph = ' OR '.join(CLASSES[cls][0])
    return f'({ph}) AND {gene} AND (SRC:MED)'

def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PME-evidence-chain/1.0 (offline audit)'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8')), None
        except Exception as e:
            err = f'{type(e).__name__}: {e}'
            time.sleep(5 * (i + 1))
    return None, err

def build_url(q, sort=None):
    u = f'{API}?query={urllib.parse.quote(q)}&resultType=core&pageSize=50&format=json'
    if sort:
        u += f'&sort={sort}'
    return u

def grade(cls, gene, raws):
    """raws = [pass1_json, pass2_json?] 合并候选后分级。"""
    doc_re = CLASSES[cls][1]; guard = CLASSES[cls][2]
    gr = gene_re(gene)
    res = []
    for raw in raws:
        res += (raw or {}).get('resultList', {}).get('result', []) or []
    seen = set(); cands = []
    for h in res:
        p = str(h.get('pmid') or '').strip()
        if p.isdigit() and p not in seen:
            seen.add(p); cands.append(h)
    strongs, weaks = [], []
    for h in cands:
        title = h.get('title') or ''
        ab = h.get('abstractText') or ''
        doc = title + '. ' + ab
        sents = sentences(title, ab)
        g_doc = bool(gr.search(doc))
        c_doc = bool(re.search(doc_re, doc, re.I)) and (guard(doc) if guard else True)
        if c_doc and cls in PHOTO_PHRASE and not re.search(PHOTO_PHRASE[cls], doc, re.I) \
                and not re.search(r'photorecept|retina', doc, re.I):
            c_doc = False
        ev = None
        for s in sents:
            if class_sent_ok(s, cls, gr, doc) and MARKER_RE.search(s):
                ev = {'pmid': h['pmid'], 'title': title[:200], 'sentence': s[:400],
                      'why': 'title-only' if not ab else 'abstract-sentence'}
                break
        if ev:
            strongs.append(ev)
        elif (g_doc and c_doc) or \
             (g_doc and c_doc and any(gr.search(s) and MARKER_RE.search(s) for s in sents)):
            weaks.append({'pmid': h['pmid'], 'title': title[:200]})
    if strongs:
        return 'strong', strongs[:2], weaks[:2], len(cands)
    if weaks:
        return 'weak', [], weaks[:2], len(cands)
    return 'none', [], [], len(cands)

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
_LOCK = threading.Lock()

def process_one(hits_f, cls, gene):
    rp = f'{RAW}/{slug(cls, gene)}.json'
    if os.path.exists(rp):
        try:
            old = json.load(open(rp))
            if old.get('error') is None and 'raw1' in old:
                return 'cached'
        except Exception:
            os.remove(rp)
    q = query_for(cls, gene)
    url1 = build_url(q)
    raw1, err = fetch(url1)
    rec = {'class': cls, 'gene': gene, 'query': q, 'url1': url1,
           'retrieved_at': datetime.datetime.isoformat(datetime.datetime.now()),
           'error': err, 'raw1': raw1, 'url2': None, 'raw2': None}
    raws = [raw1]
    if err is None:
        g1 = grade(cls, gene, raws)[0]
        if g1 != 'strong':  # pass2 sort=CITED（PREREG A1）
            raw2, err2 = fetch(build_url(q, sort='CITED'))
            rec['url2'] = build_url(q, sort='CITED'); rec['raw2'] = raw2
            if err2:
                rec['error2'] = err2
            else:
                raws.append(raw2)
    with open(rp, 'w') as f:
        json.dump(rec, f, ensure_ascii=False)
    if err:
        return 'FAIL'
    n = sum((r or {}).get('hitCount', 0) for r in raws)
    grade_v, strongs, weaks, ncand = grade(cls, gene, raws)
    with _LOCK:
        hits_f.write(json.dumps({'class': cls, 'gene': gene, 'query': q, 'hitCount': n,
                                 'n_candidates': ncand, 'grade': grade_v,
                                 'strong_evidence': strongs, 'weak_refs': weaks,
                                 'raw_file': os.path.basename(rp)},
                                ensure_ascii=False) + '\n')
        hits_f.flush()
    return grade_v

def main():
    keys = []
    for l in open(f'{ROOT}/data/unique_keys_280.txt'):
        c, g = l.rstrip('\n').split('|')
        keys.append((c, g))
    b1 = [(c, g) for c, g in keys if c in ('Rod', 'Cone', 'BC', 'AC', 'HC', 'RGC', 'MG', 'Astro')]
    rest = [(c, g) for c, g in keys if c not in ('Rod', 'Cone', 'BC', 'AC', 'HC', 'RGC', 'MG', 'Astro')]
    order = b1 + rest
    print(f'[PME] keys={len(keys)} batch1(v4.1 8类)={len(b1)} rest={len(rest)} threads=4', flush=True)
    hits_f = open(f'{ROOT}/out/pme_hits.jsonl', 'a')
    cnt = {'strong': 0, 'weak': 0, 'none': 0, 'cached': 0, 'FAIL': 0}
    i = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(process_one, hits_f, c, g): (c, g) for c, g in order}
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
                print(f'[{i}/{len(order)}] {c}/{g} -> {v} | so far {cnt}', flush=True)
    hits_f.close()
    print(f'[PME] DONE {cnt}', flush=True)
    sys.exit(2 if cnt.get('FAIL') else 0)

if __name__ == '__main__':
    main()
