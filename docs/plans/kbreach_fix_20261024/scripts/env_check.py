# -*- coding: utf-8 -*-
"""env_check.py -- one-time environment preflight for the KB-REACH card (t_c19cd667).
Prints facts only; zero writes, zero network."""
import importlib.util
import json
import subprocess

OUT = {}
for exe in ("/usr/bin/python3", "/home/ubuntu/training-venv/bin/python3"):
    v = subprocess.run([exe, "-V"], capture_output=True, text=True)
    OUT[exe] = {"version": v.stdout.strip() or v.stderr.strip() or "FAILED"}
    probe = (
        "import json\n"
        "import importlib.util as u, sys\n"
        "facts={}\n"
        "for m in ('mcp','pydantic','eyekb_core'):\n"
        "    try:\n"
        "        if m=='eyekb_core':\n"
        "            sys.path.insert(0,'/home/ubuntu/EYEKB_REPO/mcp_server')\n"
        "        mod=__import__(m)\n"
        "        facts[m]='ok'\n"
        "    except Exception as e:\n"
        "        facts[m]='%s: %s' % (type(e).__name__, e)\n"
        "import pydantic\n"
        "facts['pydantic_version']=pydantic.VERSION\n"
        "print(json.dumps(facts))\n"
    )
    v2 = subprocess.run([exe, "-"], input=probe, capture_output=True, text=True,
                        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": "/home/ubuntu"})
    OUT[exe]["imports"] = (v2.stdout.strip() or ("STDERR " + v2.stderr[-300:]))
print(json.dumps(OUT, indent=1, ensure_ascii=False))
