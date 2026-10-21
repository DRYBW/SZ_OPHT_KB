# -*- coding: utf-8 -*-
"""Run-time network audit hook for this card (loaded automatically via PYTHONPATH).

Any socket or urllib/http event in any Python process of the instrumented run is appended to
$V3_NET_AUDIT_LOG. The first line written at load time is a control line (prefixed with '#') so an
empty log can never be confused with "the hook never installed": the gate requires at least one
control line AND zero event lines.

This is a measurement, not a policy: it observes, it does not block.
"""
import os
import sys

_LOG = os.environ.get("V3_NET_AUDIT_LOG")
_EVENTS = ("socket.connect", "socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr",
           "socket.create_connection", "urllib.Request", "http.client.connect", "http.client.send")


def _hook(event, args):
    if not _LOG:
        return
    if event in _EVENTS or event.startswith("socket.") or event.startswith("urllib.") or \
            event.startswith("http.client."):
        try:
            with open(_LOG, "a", encoding="utf-8") as fh:
                fh.write(f"EVENT {event} pid={os.getpid()} args={str(args)[:300]}\n")
        except OSError:
            pass


if _LOG:
    try:
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"# hook-installed pid={os.getpid()} exe={sys.executable}\n")
        sys.addaudithook(_hook)
    except Exception:  # noqa: BLE001 — the audit must never break the measured run
        pass