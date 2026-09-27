import json, re
d = json.load(open('/mnt/D/EyeKB/kb/markers/markers_v4.1_clean.json'))
print('V4.1 version:', d.get('version'), '| created:', d.get('created'))
print('V4.1 note:', str(d.get('note'))[:900])
print('V4.1 classes:', list(d['markers'].keys()))
print()
m = json.load(open('/mnt/D/EyeKB/kb/markers/markers_membrane_v1.json'))
print('MEMB version:', m.get('version'))
print('MEMB scope:', str(m.get('scope'))[:300])
print('MEMB classes:', list(m['markers'].keys()))
prov = m.get('provenance') or {}
print('MEMB prov classes:', list(prov.keys()))
if prov:
    k0 = list(prov.keys())[0]
    print('MEMB prov sample', k0, ':', json.dumps(prov[k0], ensure_ascii=False)[:800])
print()
v6 = json.load(open('/mnt/D/EyeKB/kb/markers/markers_v6_retina_repair.json'))
print('V6 version:', v6.get('version'))
print('V6 note:', str(v6.get('note'))[:500])
mb = v6.get('marker_blocks') or {}
print('V6 marker_blocks classes:', list(mb.keys()))
print('V6 subtype_anchor_layer type:', type(v6.get('subtype_anchor_layer')))
sal = v6.get('subtype_anchor_layer')
if isinstance(sal, dict):
    k0 = list(sal.keys())[0]
    print('  SAL sample', k0, ':', json.dumps(sal[k0], ensure_ascii=False)[:500])
mr = v6.get('microglia_repair')
print('V6 microglia_repair:', json.dumps(mr, ensure_ascii=False)[:500] if mr else None)
br = v6.get('baseline_retina4_disposition')
print('V6 baseline_retina4_disposition:', json.dumps(br, ensure_ascii=False)[:400] if br else None)
print('V6 classes:', list(v6['markers'].keys()))
print('V6 rpe_detail keys:', list((v6.get('rpe_detail') or {}).keys())[:8])
print('V6 micro_detail keys:', list((v6.get('micro_detail') or {}).keys())[:8])
