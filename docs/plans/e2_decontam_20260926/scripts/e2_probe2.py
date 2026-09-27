import json, re

MD = '/mnt/D/EyeKB/kb/markers'

def scan_pmids(obj, path=''):
    """extract explicit PMIDs from any nested structure, with path labels"""
    out = []
    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f'{p}.{k}')
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, p)
        elif isinstance(o, str):
            for m in re.finditer(r'PMID[:：]?\s*(\d{5,8})', o):
                out.append((p, m.group(1), o[:120]))
    walk(obj, path)
    return out

# ---- v4.1 micro/rpe detail derivation
d = json.load(open(f'{MD}/markers_v4.1_clean.json'))
for key in ('micro_detail', 'rpe_detail'):
    md = d.get(key) or {}
    print(f'--- v4.1 {key} keys:', list(md.keys()))
    print('   note:', str(md.get('note'))[:300])
    if 'auc_table' in md:
        at = md['auc_table']
        print('   auc_table type:', type(at).__name__, 'len:', len(at) if hasattr(at, '__len__') else '')
        if isinstance(at, dict):
            k0 = list(at.keys())[:3]
            print('   auc sample:', json.dumps({k: at[k] for k in k0}, ensure_ascii=False)[:400])
        elif isinstance(at, list) and at:
            print('   auc sample:', json.dumps(at[0], ensure_ascii=False)[:300])
print('   v4.1 pmid hits total:', len(scan_pmids(d)))

# ---- v5 gene-level pmid extraction demo
v5 = json.load(open(f'{MD}/markers_v5_retina_interneuron.json'))
hits5 = scan_pmids(v5.get('provenance') or {})
print('--- v5 provenance explicit PMID hits:', len(hits5), 'distinct:', len(set(h for _, h, _ in hits5)))
print('   sample:', hits5[:4])
# types present in evidence lists
types = {}
for cls, genes in (v5.get('provenance') or {}).items():
    for g, evs in genes.items():
        for e in evs or []:
            types[e.get('type')] = types.get(e.get('type'), 0) + 1
print('   v5 evidence types:', types)
# how many (cls,gene) have pmid_context n_hits>0
pc = sum(1 for cls, genes in (v5.get('provenance') or {}).items() for g, evs in genes.items()
         if any((e.get('type') == 'pmid_context' and int(e.get('n_hits') or 0) > 0) for e in evs or []))
tot = sum(len(genes) for genes in (v5.get('provenance') or {}).values())
print(f'   v5 (cls,gene) pairs: {tot}, with pmid_context n_hits>0: {pc}')
print('   v5 markers sizes:', {k: len(v) for k, v in v5['markers'].items()})

# ---- v6 retina repair: evidence scan
v6 = json.load(open(f'{MD}/markers_v6_retina_repair.json'))
hits6 = scan_pmids({k: v6[k] for k in v6 if k in ('marker_blocks', 'subtype_anchor_layer', 'microglia_repair', 'rpe_detail', 'micro_detail', 'bans', 'rgc_watchlist', 'cl_alignment')})
print('--- v6 explicit PMID hits:', len(hits6), 'distinct:', sorted(set(h for _, h, _ in hits6))[:20])
for p, h, s in hits6[:6]:
    print('   ', p, '->', h, '|', s[:80])
print('   v6 markers sizes:', {k: len(v) for k, v in v6['markers'].items()})
bans = v6.get('bans')
print('   v6 bans:', json.dumps(bans, ensure_ascii=False)[:400])

# ---- membrane: gene-level vs class-level semantics
memb = json.load(open(f'{MD}/markers_membrane_v1.json'))
pm = memb.get('provenance') or {}
types = {}
n_pairs = 0
n_with_pmidctx = 0
for cls, genes in pm.items():
    for g, evs in (genes or {}).items():
        n_pairs += 1
        tl = []
        for e in evs or []:
            tl.append(e.get('type'))
            types[e.get('type')] = types.get(e.get('type'), 0) + 1
        if 'pmid_context' in tl:
            n_with_pmidctx += 1
print('--- membrane evidence types:', types, '| pairs:', n_pairs, '| with pmid_context:', n_with_pmidctx)
# data_driven ids present
dd = set()
for cls, genes in pm.items():
    for g, evs in (genes or {}).items():
        for e in evs or []:
            if e.get('type') == 'data_driven':
                dd.add(str(e.get('id')))
print('   membrane data_driven ids:', sorted(dd))
print('   membrane Keratocytes prov sample:', json.dumps(pm.get('Keratocytes'), ensure_ascii=False)[:600])

# ---- face_v6 evidence
fc = json.load(open(f'{MD}/markers_v6_face_increment.json'))
hitsf = scan_pmids({k: fc[k] for k in fc if k in ('stromal_repair', 'face_increment')})
print('--- face_v6 explicit PMID hits:', len(hitsf), 'distinct:', len(set(h for _, h, _ in hitsf)))
types = {}
for src in ('stromal_repair', 'face_increment'):
    for cls, e in (fc.get(src) or {}).items():
        for g in (e.get('core') or []):
            for ev in (g.get('evidence') or []):
                types[ev.get('type')] = types.get(ev.get('type'), 0) + 1
print('   face_v6 evidence types:', types)
dd = set()
for src in ('stromal_repair', 'face_increment'):
    for cls, e in (fc.get(src) or {}).items():
        for g in (e.get('core') or []):
            for ev in (g.get('evidence') or []):
                if ev.get('type') == 'data_driven':
                    dd.add(str(ev.get('id')))
print('   face_v6 data_driven ids:', sorted(dd)[:12])
print('   face_v6 classes:', {src: list((fc.get(src) or {}).keys()) for src in ('stromal_repair', 'face_increment')})

# ---- cl_alignment v1 (what is it?)
ca = json.load(open(f'{MD}/markers_cl_alignment_v1.json'))
print('--- cl_alignment keys:', list(ca.keys())[:10], '| version:', ca.get('version'))
