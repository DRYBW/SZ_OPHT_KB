import json, re

MD = '/mnt/D/EyeKB/kb/markers'

def scan_pmids(obj):
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
                out.append((p, m.group(1)))
    walk(obj, '')
    return out

# membrane robust walk
memb = json.load(open(f'{MD}/markers_membrane_v1.json'))
pm = memb.get('provenance') or {}
dd_ids = {}
for cls, genes in pm.items():
    if not isinstance(genes, dict):
        print('  MEMB prov non-dict class:', cls, type(genes).__name__, str(genes)[:120])
        continue
    for g, evs in genes.items():
        if isinstance(evs, dict):
            evs = [evs]
        for e in (evs or []):
            if isinstance(e, dict) and e.get('type') == 'data_driven':
                dd_ids.setdefault(str(e.get('id')), set()).add(cls)
print('membrane data_driven ids -> classes:')
for k, v in sorted(dd_ids.items()):
    print('  ', k, ':', sorted(v)[:8])
# gene-level explicit PMIDs in membrane (any field)
hits = scan_pmids(pm)
print('membrane total PMID string hits:', len(hits), 'distinct:', len(set(h for _, h in hits)))
# how many are pmid_context-type (class-level) vs others
ctx = 0; other = []
for cls, genes in pm.items():
    if not isinstance(genes, dict): continue
    for g, evs in (genes or {}).items():
        if isinstance(evs, dict): evs = [evs]
        for e in (evs or []):
            if not isinstance(e, dict): continue
            for p, h in scan_pmids(e):
                if e.get('type') == 'pmid_context': ctx += 1
                else: other.append((cls, g, h, e.get('type')))
print('membrane PMID-in-context-type:', ctx, '| PMID in other evidence types:', other[:10])

# v4.1 micro/rpe candidates source
d = json.load(open(f'{MD}/markers_v4.1_clean.json'))
for key in ('micro_detail', 'rpe_detail'):
    md = d.get(key) or {}
    print(f'v4.1 {key}: candidates sample:', json.dumps((md.get('candidates') or [])[:3], ensure_ascii=False)[:300])
    print(f'   final_markers:', json.dumps(md.get('final_markers'), ensure_ascii=False)[:250])
    print(f'   negative_check_class:', md.get('negative_check_class'))

# face_v6 scan
fc = json.load(open(f'{MD}/markers_v6_face_increment.json'))
n_pairs = 0; n_ext = 0; dd = {}
for src in ('stromal_repair', 'face_increment'):
    for cls, e in (fc.get(src) or {}).items():
        core = e.get('core') or []
        for g in core:
            if not isinstance(g, dict): continue
            n_pairs += 1
            pms = set()
            for ev in (g.get('evidence') or []):
                if isinstance(ev, dict) and ev.get('type') == 'data_driven':
                    dd.setdefault(str(ev.get('id')), set()).add(cls)
                for _, h in scan_pmids(ev):
                    pms.add(h)
            if pms: n_ext += 1
print(f'face_v6 gene pairs: {n_pairs}, with explicit PMID: {n_ext}')
print('face_v6 data_driven ids -> classes:', {k: sorted(v) for k, v in dd.items()})

# d0_claims peek
dc = open('/mnt/D/EyeKB/kb/evidence/d0_claims_v1.jsonl').read().splitlines()
print('d0_claims lines:', len(dc))
print('d0 claim sample:', dc[0][:400])
