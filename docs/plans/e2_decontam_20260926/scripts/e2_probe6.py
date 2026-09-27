import json, re

MD = '/mnt/D/EyeKB/kb/markers'
v5 = json.load(open(f'{MD}/markers_v5_retina_interneuron.json'))
prov = v5.get('provenance') or {}
print('v5 prov classes:', list(prov.keys()))
for cls in v5['markers']:
    genes = v5['markers'][cls]
    pcov = [g for g in genes if g in prov.get(cls, {})]
    dd = [g for g in pcov if any(isinstance(e, dict) and e.get('type') == 'data_driven' for e in prov[cls][g])]
    pm = [g for g in pcov if re.search(r'PMID', json.dumps(prov[cls][g]))]
    print(f'  v5 {cls}: n_genes={len(genes)} with_prov={len(pcov)} data_driven={len(dd)} with PMID={len(pm)}')
    for g in genes:
        if g not in prov.get(cls, {}):
            print('    NO-PROV:', g, end='')
    print()

memb = json.load(open(f'{MD}/markers_membrane_v1.json'))
mp = memb['provenance']
for cls in ('Keratocytes', 'Corneal Endothelium'):
    types = {}
    for g, evs in (mp.get(cls) or {}).items():
        for e in evs or []:
            if isinstance(e, dict):
                types[e.get('type')] = types.get(e.get('type'), 0) + 1
    print(f'membrane {cls} evidence types:', types, '| genes:', len(memb['markers'][cls]))

v6 = json.load(open(f'{MD}/markers_v6_retina_repair.json'))
mb = v6.get('marker_blocks') or {}
mg = v6.get('microglia_repair') or {}
for cls in v6['markers']:
    genes = v6['markers'][cls]
    in_blocks = {x['gene'] for x in (mb.get(cls) or []) if isinstance(x, dict)}
    in_mg = {x['gene'] for x in (mg.get('core') or []) if isinstance(x, dict)}
    uncovered = [g for g in genes if g not in in_blocks and g not in in_mg]
    print(f'  v6 {cls}: n={len(genes)} blocks={len(in_blocks)} mg={len(in_mg)} uncovered={uncovered}')

fc = json.load(open(f'{MD}/markers_v6_face_increment.json'))
for src in ('stromal_repair', 'face_increment'):
    for cls, e in (fc.get(src) or {}).items():
        rows = []
        for g in (e.get('core') or []):
            if not isinstance(g, dict): continue
            pms = sorted(set(re.findall(r'PMID[:：]?\s*(\d{5,8})', json.dumps(g.get('evidence') or []))))
            ddt = [ev.get('id') for ev in (g.get('evidence') or []) if isinstance(ev, dict) and ev.get('type') == 'data_driven']
            rows.append((g.get('gene'), pms, [str(d)[:40] for d in ddt]))
        print(f'  face[{src}] {cls}:', json.dumps(rows, ensure_ascii=False)[:600])
