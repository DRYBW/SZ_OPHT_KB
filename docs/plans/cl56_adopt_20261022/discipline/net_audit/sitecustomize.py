# -*- coding: utf-8 -*-
"""Audit hook: every network-ish operation performed by any Python process on this chain.

Loaded automatically because the runner exports PYTHONPATH=<this directory> (the `site` module
imports `sitecustomize` at interpreter start). Covers child processes too, which a source-level grep
cannot do.

The hook writes a load receipt line (prefixed `#`) so "no events" can never be mistaken for "the hook
never ran". Count only lines after the header.

Absorbed from the CL-depth wave's identical hook (plans/cl_depth_devlineage_20261021/scripts/netaudit);
the only change is the log-variable name.
"""
import os
import sys

_LOG = os.environ.get("CL56_NET_AUDIT_LOG")

if _LOG:
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write("# hook-installed pid=%d exe=%s\n" % (os.getpid(), sys.executable))
    except OSError:
        pass

    def _hook(event, args):
        if (event.startswith("socket.") or event.startswith("urllib.")
                or event.startswith("http.client") or event.startswith("ftplib.")
                or event.startswith("smtplib.")):
            try:
                with open(_LOG, "a", encoding="utf-8") as f:
                    f.write("EVENT %s %s\n" % (event, str(args)[:200]))
            except OSError:
                pass

    sys.addaudithook(_hook)