# -*- coding: utf-8 -*-
"""Audit hook: every network-ish operation performed by any Python process on this chain.

Loaded automatically because run_all.sh exports PYTHONPATH=<this directory> (the `site` module
imports `sitecustomize` at interpreter start), so it covers child processes too — which a
source-level grep cannot.

The load receipt line is written first, on purpose: it proves the hook was installed, so "no
events" can never be mistaken for "the hook never ran". Count only lines beginning with EVENT.
"""
import os
import sys

_LOG = os.environ.get("MK_NET_AUDIT_LOG")

if _LOG:
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write("# hook-installed pid=%s exe=%s\n" % (os.getpid(), sys.executable))
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