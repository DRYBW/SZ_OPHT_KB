# -*- coding: utf-8 -*-
"""r2_after_fix.py DEFECT-1 acceptance readings (post-fix). Zero writes outside out/.
 (1) row-level diff PRE vs POST for the three replay arms (differing rows must be 0);
 (2) explicit-route readings for library=subtype_v14: inventory size (0 -> 16 classes),
     best recorded window n_ranked (pre 0 -> post N), previously-ranked-0 window unchanged;
 (3) the full 721-window hit census for the 16 entries (max hit window), for the record.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "out")
REPO = "/home/ubuntu/EYEKB_REPO"
NOREGR = "/mnt/D/EyeKB/plans/noregr_20261022/scripts"
L6CL = "/mnt/D/EyeKB/plans/cl56_adopt_20261022/scripts"
PY = "/usr/bin/python3"
doc = {"probe": "r2_after_fix.py"}


def rowdiff(a_path, b_path):
    a = json.load(open(a_path, encoding="utf-8"))["rows"]
    b = json.load(open(b_path, encoding="utf-8"))["rows"]
    assert set(a) == set(b), (len(a), len(b))
    d_raw = [k for k in a if a[k]["raw_md5"] != b[k]["raw_md5"]]
    d_can = [k for k in a if a[k]["canon_md5"] != b[k]["canon_md5"]]
    return {"n_rows": len(a), "n_differing_raw": len(d_raw), "n_differing_canonical": len(d_can),
            "differing_raw": d_raw[:10], "differing_canonical": d_can[:10]}


for m in ("clusters", "battery", "explicit"):
    doc["rowdiff_" + m] = rowdiff(os.path.join(OUT, "PRE_%s.json" % m),
                                  os.path.join(OUT, "POST_%s.json" % m))

# explicit-route readings for subtype_v14
child = r'''
import json,sys
sys.path.insert(0,"/home/ubuntu/EYEKB_REPO/mcp_server")
sys.path.insert(0,"/mnt/D/EyeKB/plans/noregr_20261022/scripts")
import wave_common as W, eyekb_core as core
calls=W.load_set()
inv=core.query_marker(library="subtype_v14")
cts=inv.get("cell_types") if inv.get("mode")=="list" else None
rows=[]
for c in sorted(calls,key=lambda x:-x["n_cells"]):
    r=core.query_marker(genes=list(c["genes"]),library="subtype_v14")
    rank=r.get("celltype_ranking") or []
    rows.append({"vol":c["vol"],"cluster":c["cluster"],"n_cells":c["n_cells"],
                 "n_genes":len(c["genes"]),"n_ranked":len(rank),
                 "top":rank[0]["cell_type"] if rank else None})
    if len(rows)>=200: break
best=max(rows,key=lambda r:(r["n_ranked"],r["n_cells"]))
probe_top=sorted(calls,key=lambda c:-c["n_cells"])[0]
r_probe=core.query_marker(genes=list(probe_top["genes"]),library="subtype_v14")
out={"inventory_mode":inv.get("mode"),"inventory_n":len(cts or []),"inventory_classes":cts,
     "best_window":best,
     "explicit_probe_window":probe_top,"explicit_probe_n_ranked":len(r_probe.get("celltype_ranking") or []),
     "windows_scanned":len(rows),
     "hit_census":{str(n):sum(1 for r in rows if r["n_ranked"]==n) for n in range(0,17) if any(r["n_ranked"]==n for r in rows)}}
print(json.dumps(out))
'''
p = subprocess.run([PY], input=child, capture_output=True, text=True,
                   env={**{k: v for k, v in os.environ.items() if not k.startswith("EYEKB_")},
                        "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
                        "PATH": "/usr/bin:/bin:/usr/local/bin:/home/ubuntu/training-venv/bin"},
                   cwd=REPO)
try:
    doc["D1_after"] = {"command": PY + " child (clean env): inventory + best-window + hit census, library=subtype_v14",
                       "reading": json.loads(p.stdout.strip().splitlines()[-1])}
except Exception:
    doc["D1_after"] = {"stdout_tail": p.stdout[-500:], "stderr_tail": p.stderr[-1500:]}

with open(os.path.join(OUT, "R2_AFTER_FIX.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps({k: doc[k] for k in ("rowdiff_clusters", "rowdiff_battery", "rowdiff_explicit")},
                 indent=1))
a = doc.get("D1_after", {}).get("reading") or {}
print(json.dumps({k: a.get(k) for k in ("inventory_n", "inventory_classes", "best_window",
                                        "explicit_probe_n_ranked", "windows_scanned", "hit_census")},
                 ensure_ascii=False, indent=1)[:1800])
