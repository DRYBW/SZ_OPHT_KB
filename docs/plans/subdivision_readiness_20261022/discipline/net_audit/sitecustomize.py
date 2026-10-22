"""Zero-network audit hook for wave subdivision_readiness_20261022.

Installed via PYTHONPATH so that `site` imports it into every Python subprocess of the chain.
Every socket/urllib/http.client event is appended to $SR_NET_AUDIT_LOG.

The first line each load writes is a '#'-prefixed marker line so that an empty or missing log can
never be mistaken for "zero events": the marker proves the hook was actually installed.
"""
import os
import sys

_log = os.environ.get("SR_NET_AUDIT_LOG")

if _log:
    try:
        with open(_log, "a", encoding="utf-8") as _fh:
            _fh.write("# hook-installed pid=%d exe=%s\n" % (os.getpid(), sys.executable))
    except OSError:
        pass

    def _hook(event, args):
        if event.startswith(("socket.", "urllib.", "http.client.", "ftplib.", "smtplib.")):
            try:
                with open(_log, "a", encoding="utf-8") as _fh:
                    _fh.write("EVENT %s pid=%d %s\n" % (event, os.getpid(), repr(args)[:200]))
            except OSError:
                pass

    sys.addaudithook(_hook)
