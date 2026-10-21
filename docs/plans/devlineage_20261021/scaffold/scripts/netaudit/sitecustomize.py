# -*- coding: utf-8 -*-
"""Audit hook: every network-ish operation performed by any Python process on this chain.

Vendored from plans/cl_depth_devlineage_20261021/scripts/netaudit/sitecustomize.py (the peer wave)
with two changes: the log path variable is this card's own (SCAFFOLD_NET_AUDIT_LOG, falling back to
the peer's name), and the event line records the audit event and its arguments so a local-only
socket call can be told apart from an outbound one.

Loaded automatically because the runner exports PYTHONPATH=<this directory> (the `site` module
imports `sitecustomize` at interpreter start). Covers child processes too, which a source-level
grep cannot do.

The first line written is a load receipt: it proves the hook was installed, so "no events" cannot be
mistaken for "the hook never ran". Count only lines after the header.
"""
import os
import sys

_LOG = os.environ.get("SCAFFOLD_NET_AUDIT_LOG") or os.environ.get("CL_DEPTH_NET_AUDIT_LOG")

if _LOG:
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(f"# hook-installed pid={os.getpid()} exe={sys.executable}\n")
    except OSError:
        pass

    def _hook(event, args):
        if event.startswith(("socket.", "urllib.", "http.client", "ftplib.", "smtplib.")):
            try:
                with open(_LOG, "a", encoding="utf-8") as f:
                    f.write(f"EVENT {event} {str(args)[:200]}\n")
            except OSError:
                pass

    sys.addaudithook(_hook)