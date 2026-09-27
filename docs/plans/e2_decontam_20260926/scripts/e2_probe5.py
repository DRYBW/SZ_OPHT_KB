import json
m = json.load(open('/mnt/D/EyeKB/plans/evidence_scoring_20260926/out/e1_metrics.json'))
print('matrix:')
print(json.dumps(m['matrix'], ensure_ascii=False, indent=1))
print('faces:', m['faces'])
print('leak_rows:', m['leak_rows'])
