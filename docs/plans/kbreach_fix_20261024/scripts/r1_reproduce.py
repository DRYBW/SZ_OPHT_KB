# -*- coding: utf-8 -*-
"""r1_reproduce.py -- KB-REACH pre-fix readings (card t_c19cd667). Every number carries the
command that produced it (this file + argv). Zero writes outside the wave dir; zero network.

Sections:
  D1  subtype_v14 body: markers key present? / explicit-route n_ranked=0 / inventory size 0
  D1c coverage oracle: the recorded explicit probe window vs the 16 entries; best recorded window
  D2  probe --baseline reproduction (rc, moved calls) under the recorded interpreter
  D3  qualified is_a counts under two 口径 in the pinned release (harness parse vs stripped)
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
PROBE_PY = "/home/ubuntu/training-venv/bin/python3"
SWITCHES = ("EYEKB_TISSUE_SCOPE", "EYEKB_ACT_V6", "EYEKB_ACT_K9", "EYEKB_ACT_ANTSEG",
            "EYEKB_ACT_ONFIBRO", "EYEKB_ACT_SUBTYPE", "EYEKB_ACT_CL56", "EYEKB_KB_ANTIUNION",
            "EYEKB_STATE_GUARD", "EYEKB_S0_ENFORCE", "EYEKB_FALLBACK_WIDEN",
            "EYEKB_FALLBACK_WIDEN_DENY_TISSUES", "EYEKB_CL_KEY", "EYEKB_KBGOV_B5", "EYEKB_ONT_LAYER")
doc = {"probe": "r1_reproduce.py", "argv": sys.argv[1:]}


def clean_env(extra=None, cwd=REPO):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith("EYEKB_"):
            e.pop(k)
    e["PYTHONHASHSEED"] = "0"
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    e["PATH"] = "/usr/bin:/bin:/usr/local/bin:/home/ubuntu/training-venv/bin"
    if extra:
        e.update(extra)
    return e


def sh(cmd, env=None, cwd=REPO):
    return subprocess.run(cmd, capture_output=True, text=True, env=env or clean_env(), cwd=cwd)


# ---------------- D1: the file body and the explicit route ----------------
lib_path = os.path.join(REPO, "kb/markers/markers_v14_subtype_second_increment.json")
raw = open(lib_path, "rb").read()
d = json.loads(raw.decode("utf-8"))
doc["D1_body"] = {
    "command": "/usr/bin/python3 r1_reproduce.py  (json.load of kb/markers markers_v14_subtype_second_increment.json)",
    "markers_key_present": "markers" in d,
    "n_entries": len(d.get("entries") or []),
    "sha256_of_bytes": hashlib.sha256(raw).hexdigest(),
    "bytes": len(raw),
    "n_class_names_distinct": len({e.get("class_name") for e in d.get("entries") or []}),
    "entries_markers_all_nonempty": all((e.get("markers") or []) for e in d.get("entries") or []),
}
# explicit-route n_ranked (clean-env child importing the shipped core)
child = (
    "import json,sys\n"
    "sys.path.insert(0,'/home/ubuntu/EYEKB_REPO/mcp_server')\n"
    "sys.path.insert(0,'/mnt/D/EyeKB/plans/noregr_20261022/scripts')\n"
    "import wave_common as W, eyekb_core as core\n"
    "probe_genes=sorted(W.load_set(), key=lambda c:-c['n_cells'])[0]['genes']\n"
    "out={'n_probe_genes':len(probe_genes)}\n"
    "try:\n"
    "    r=core.query_marker(genes=list(probe_genes), library='subtype_v14')\n"
    "    rank=r.get('celltype_ranking') or []\n"
    "    out.update(refused=False, n_ranked=len(rank), top=rank[0]['cell_type'] if rank else None)\n"
    "except Exception as e:\n"
    "    out.update(refused=True, error='%s: %s' % (type(e).__name__, e))\n"
    "inv=core.query_marker(library='subtype_v14')\n"
    "inv_cts=inv.get('cell_types') if inv.get('mode')=='list' else None\n"
    "out['inventory_mode']=inv.get('mode'); out['inventory_n']=len(inv_cts or [])\n"
    "out['inventory_sample']=(inv_cts or [])[:4]\n"
    "print(json.dumps(out))\n"
)
p = sh([PY, "-"], env=clean_env(), cwd=REPO)
p = subprocess.run([PY], input=child, capture_output=True, text=True, env=clean_env(), cwd=REPO)
try:
    doc["D1_explicit_route"] = {"command": PY + " child (clean env, imports mcp_server/eyekb_core.py)",
                                "reading": json.loads(p.stdout.strip().splitlines()[-1])}
except Exception:
    doc["D1_explicit_route"] = {"command": PY + " child", "stdout_tail": p.stdout[-400:],
                                "stderr_tail": p.stderr[-800:]}

# coverage oracle: per-entry n_shared against the recorded explicit window; and the best recorded window
sys.path.insert(0, NOREGR)
os.environ.update({k: "" for k in SWITCHES})  # inert for this path; load_set only reads the ledger
import wave_common as W  # noqa: E402

calls = W.load_set()
entries = d["entries"]
w_probe = sorted(calls, key=lambda c: -c["n_cells"])[0]
gset = set(w_probe["genes"])


def per_entry_shared(genes):
    gs = set(x.upper() for x in genes)
    rows = []
    for e in entries:
        ms = set(x.upper() for x in (e.get("markers") or []))
        rows.append({"class_name": e.get("class_name"), "n_shared": len(ms & gs)})
    return rows


oracle = {"window": {"vol": w_probe["vol"], "cluster": w_probe["cluster"],
                     "n_cells": w_probe["n_cells"], "n_genes": len(w_probe["genes"])},
          "per_entry_n_shared": per_entry_shared(w_probe["genes"]),
          "n_entries_hit": sum(1 for r in per_entry_shared(w_probe["genes"]) if r["n_shared"] > 0)}
best = None
for c in calls:
    n = sum(1 for r in per_entry_shared(c["genes"]) if r["n_shared"] > 0)
    if best is None or n > best["n_entries_hit"] or (n == best["n_entries_hit"] and c["n_cells"] > best["window"]["n_cells"]):
        best = {"n_entries_hit": n, "window": {"vol": c["vol"], "cluster": c["cluster"],
                                               "n_cells": c["n_cells"], "n_genes": len(c["genes"])}}
oracle["best_recorded_window"] = best
doc["D1c_coverage_oracle"] = {"command": "wave_common.load_set() x static marker lists (no core import)",
                              "explicit_window_reading": oracle}

# ---------------- D2: identity probe against the approved baseline ----------------
p = sh([PROBE_PY, "tests/probe_tool_panel_identity.py", "--baseline",
        "tests/fixtures/tool_panel_baseline.json"], env=clean_env({"EYEKB_PROBE_PY": PROBE_PY}))
moved = [l.strip() for l in p.stdout.splitlines() if l.strip().startswith("different:")]
tail = [l for l in p.stdout.splitlines() if l.startswith(("IDENTITY", "REFUSED"))]
doc["D2_probe_baseline"] = {
    "command": "training-venv/bin/python3 tests/probe_tool_panel_identity.py --baseline tests/fixtures/tool_panel_baseline.json (cwd=repo, clean env)",
    "returncode": p.returncode,
    "headline": tail,
    "moved_calls": [m.split("different: ", 1)[-1] for m in moved],
    "stderr_tail": p.stderr[-300:] if p.returncode >= 3 else "",
}

# ---------------- D3: qualified is_a counts, two calibers ----------------
OBO = os.path.join(REPO, "kb/ontology/cl/releases/2026-06-08/cl-base.obo")
n_terms = 0
n_active = 0
n_isa_lines = 0
n_qualified_any = 0
n_qualified_is_inferred = 0
qualifier_kinds = {}
cur = None
with open(OBO, encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.rstrip("\n")
        if line == "[Term]":
            cur = {}
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = None
            continue
        if cur is None or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if k == "id":
            cur["id"] = v
            n_terms += 1
        elif k == "is_obsolete":
            cur["obsolete"] = (v == "true")
        elif k == "is_a":
            n_isa_lines += 1
            raw_parent = v.split("!")[0].strip()
            if "{" in raw_parent:
                n_qualified_any += 1
                q = raw_parent.split("{", 1)[1].split("}", 1)[0]
                qualifier_kinds[q] = qualifier_kinds.get(q, 0) + 1
                if "is_inferred" in q:
                    n_qualified_is_inferred += 1
n_active = None
doc["D3_qualified_isa"] = {
    "command": PY + "-parse of kb/ontology/cl/releases/2026-06-08/cl-base.obo (r1_reproduce.py D3 block)",
    "obo_sha256": hashlib.sha256(open(OBO, "rb").read()).hexdigest(),
    "n_terms": n_terms,
    "n_is_a_lines": n_isa_lines,
    "qualified_any_qualifier": n_qualified_any,
    "qualified_is_inferred": n_qualified_is_inferred,
    "qualifier_kinds": qualifier_kinds,
}

with open(os.path.join(OUT, "R1_REPRODUCE.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps(doc, ensure_ascii=False, indent=1))
