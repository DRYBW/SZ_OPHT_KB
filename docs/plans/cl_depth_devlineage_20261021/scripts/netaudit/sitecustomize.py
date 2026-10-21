# -*- coding: utf-8 -*-
"""Audit hook: every network-ish operation performed by any Python process on this chain.

Loaded automatically because the runner exports PYTHONPATH=<this directory> (the `site` module
imports `sitecustomize` at interpreter start). Covers child processes too, which a source-level
grep cannot do.

The first line is a load receipt: it proves the hook was installed, so "no events" cannot be
mistaken for "the hook never ran". Count only lines after the header.
"""
import os
import sys

_LOG = os.environ.get("CL_DEPTH_NET_AUDIT_LOG")

if _LOG:
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(f"# hook-installed pid={os.getpid()} exe={sys.executable}\n")
    except OSError:
        pass

    _WATCH = ("socket.", "urllib.", "http.client", "ftplib.", "smtplib.")

    def _hook(event, args):
        if event.startswith("socket.") or event.startswith("urllib.") \
                or event.startswith("http.client") or event.startswith("ftplib.") \
                or event.startswith("smtplib."):
            try:
                with open(_LOG, "a", encoding="utf-8") as f:
                    f.write(f"EVENT {event} {str(args)[:200]}\n")
            except OSError:
                pass

    sys.addaudithook(_hook)