# -*- coding: utf-8 -*-
"""r2b_full_census.py -- full 721-window service-level census for library=subtype_v14, post-fix.
Per recorded window (721, largest-last ordering irrelevant): n_ranked + top. Writes out/R2B_CENSUS.json."""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
REPO = "/home/ubuntu/EYEKB_REPO"
PY = "/usr/bin/python3"
child = r'''
import json,sys
sys.path.insert(0,"/home/ubuntu/EYEKB_REPO/mcp_server")
sys.path.insert(0,"/mnt/D/EyeKB/plans/noregr_20261022/scripts")
import wave_common as W, eyekb_core as core
calls=W.load_set()
rows=[]
for c in calls:
    r=core.query_marker(genes=list(c["genes"]),library="subtype_v14")
    rank=r.get("celltype_ranking") or []
    rows.append({"vol":c["vol"],"cluster":c["cluster"],"n_cells":c["n_cells"],
                 "n_ranked":len(rank),"top":rank[0]["cell_type"] if rank else None})
best=max(rows,key=lambda r:(r["n_ranked"],r["n_cells"]))
census={}
for r in rows:
    census[r["n_ranked"]]=census.get(r["n_ranked"],0)+1
out={"n_windows":len(rows),"best_window":best,"census_by_n_ranked":{str(k):v for k,v in sorted(census.items())}}
print(json.dumps(out))
'''
p = subprocess.run([PY], input=child, capture_output=True, text=True,
                   env={**{k: v for k, v in os.environ.items() if not k.startswith("EYEKB_")},
                        "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
                        "PATH": "/usr/bin:/bin:/usr/local/bin:/home/ubuntu/training-venv/bin"},
                   cwd=REPO)
doc = {"probe": "r2b_full_census.py",
       "command": PY + " child (clean env): full 721-window library=subtype_v14 census"}
try:
    doc["reading"] = json.loads(p.stdout.strip().splitlines()[-1])
except Exception:
    doc["stdout_tail"] = p.stdout[-400:]
    doc["stderr_tail"] = p.stderr[-1200:]
with open(os.path.join(OUT, "R2B_CENSUS.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps(doc.get("reading", doc), ensure_ascii=False, indent=1))
