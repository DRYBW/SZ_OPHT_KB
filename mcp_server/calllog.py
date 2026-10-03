#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calllog — EyeKB MCP server-side call-tracing layer (OBS1 t_c754c4fc, 2026-09-26)

═══ Purpose and red lines ═══
- **Logging only, zero behavior change**: this module only reads the tool response, builds a
  structural digest, and writes it to disk; it never modifies resp / return values / ordering /
  soft_flags; trace() is fully wrapped in try/except — a tracing failure must never affect the
  service (no new exception sources on the return path).
- Basis: BRIEF_OBS1.md OBS-1 (inventory conclusion = zero server-side tracing, a logging layer
  must be added) + USER_DIRECTIVE_20260926 A2 observation clause (the one-week real-traffic
  follow-vote sampling needs a call-side data source).
- server.py exception semantics untouched: when a tool function raises, trace is not called
  (same as before the change).

═══ Persistence and rotation ═══
- Path: /mnt/D/EyeKB/logs/mcp_trace/calls_YYYY-MM-DD.jsonl (local date, natural daily rotation;
  when a single file exceeds 200MB, writing continues into calls_YYYY-MM-DD.part<N>.jsonl).
- Append-only (O_APPEND line-level atomic writes, safe for concurrent multi-session spawns); no
  automatic deletion — after the observation window keeps evidence for a full month and is
  reviewed, the coordinator rules on archiving (A4 card).

═══ Redaction policy ═══
- Recorded: tool name, input args (scientific search terms: genes/cell types/tissues/literature
  query — domain information, not personal data), and a **structural digest** of the response
  (mode, found, class-name lists, soft_flag flag_id lists, the provenance library set and the
  lacrimal boolean, hit counts).
- Not recorded: full soft_flags notes text, literature snippet bodies, full gene tables of the
  detail panels, baseline numeric-table contents (volume and corpus-landing control; flag_ids and
  class names already suffice for OBS-2 two-caliber statistics).
- Session-side info: process uuid/pid/host/parent cmdline (consumer attribution) + optional env
  EYEKB_MCP_TRACE_TAG (tags self-test traffic; the statistics tool excludes it by default; real
  consumers leave it unset → empty).

═══ Environment state ═══
- Every record carries the raw values of EYEKB_ACT_V6 and EYEKB_MCP_SOFTFLAGS + the effective
  verdict (the ON/OFF wording copies _v6_act_enabled()/softflags.enabled() semantics verbatim —
  the {0,false,off,no} casefold set — with no independently invented logic).
"""
import json
import os
import socket
import time
import uuid

# Trace dir: env override first; if the production path exists on this host, keep using it
# (audit continuity); otherwise fall back to the in-repo logs/mcp_trace — a clone on an
# external machine never tries to write someone else's absolute path (2026-09-29 leftover#2 fix).
def _default_trace_dir() -> str:
    cand = "/mnt/D/EyeKB/logs/mcp_trace"
    if os.path.isdir(os.path.dirname(cand)) or os.path.isdir(cand):
        return cand
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "mcp_trace")

TRACE_DIR = os.environ.get("EYEKB_TRACE_DIR") or _default_trace_dir()
MAX_DAY_BYTES = 200 * 1024 * 1024  # after 200MB write into .part<N>

_OFF_VALUES = {"0", "false", "off", "no"}

_SESSION = {
    "session_uuid": uuid.uuid4().hex[:12],
    "pid": os.getpid(),
    "ppid": os.getppid(),
    "host": socket.gethostname(),
    "proc_started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "tag": (os.environ.get("EYEKB_MCP_TRACE_TAG") or "").strip()[:64],
    "caller": "",
}


def _caller_cmdline():
    """Parent-process cmdline (consumer attribution, best-effort, truncated at 300 chars)."""
    try:
        with open(f"/proc/{_SESSION['ppid']}/cmdline", "rb") as f:
            return f.read().replace(b"\0", b" ").decode("utf-8", "replace")\
                     .strip()[:300]
    except Exception:
        return ""


try:
    _SESSION["caller"] = _caller_cmdline()
except Exception:
    pass


def _env_state():
    act = os.environ.get("EYEKB_ACT_V6")
    sf = os.environ.get("EYEKB_MCP_SOFTFLAGS")
    act_off = (act or "").strip().casefold() in _OFF_VALUES
    # softflags.enabled() semantics check: softflags.py L100-103 is
    # strip().casefold() ∈ {0,false,off,no} → off; all other values (incl. unset) → on.
    # EYEKB_ACT_V6 semantics: unset/any other value = ON (eyekb_core._v6_act_enabled).
    sf_off = (sf or "").strip().casefold() in _OFF_VALUES if sf is not None else False
    return {
        "EYEKB_ACT_V6_raw": act, "act_v6_on": (not act_off),
        "EYEKB_MCP_SOFTFLAGS_raw": sf, "softflags_on": (not sf_off),
    }


def _args_safe(args, limit=6000):
    try:
        s = json.dumps(args, ensure_ascii=False, default=str)
    except Exception:
        s = repr(args)
    if len(s) > limit:
        return {"args_trunc_json": s[:limit], "args_truncated": True}
    try:
        return json.loads(s)
    except Exception:
        return {"args_unserializable": s[:limit]}


def _resp_digest(tool, resp):
    """Structural digest of the response (read-only; any parse failure degrades to a keys list)."""
    d = {"resp_type": type(resp).__name__}
    try:
        if not isinstance(resp, dict):
            d["resp_keys"] = None
            return d
        keys = sorted(resp.keys())
        d["resp_keys"] = keys
        if tool == "query_marker":
            prov = resp.get("provenance") or {}
            files = prov.get("files") or []
            d["libs"] = sorted({f.get("library") for f in files if f.get("library")})
            d["lacrimal_in_prov"] = any(
                "lacrimal" in str(f.get("path", "")).lower()
                or "lacrimal" == str(f.get("library", "")).lower() for f in files)
            notes = (resp.get("soft_flags") or {}).get("notes") or []
            d["soft_flag_ids"] = sorted({str(n.get("flag_id")) for n in notes
                                         if isinstance(n, dict) and n.get("flag_id")})
            mode = resp.get("mode")
            d["mode"] = mode
            if mode == "list":
                ct = resp.get("cell_types") or []
                d["n_classes"] = len(ct)
                d["classes"] = [str(c)[:80] for c in ct][:80]
            elif mode == "cell_type":
                d["query"] = str(resp.get("query", ""))[:80]
                d["found"] = bool(resp.get("found"))
                d["hit_classes"] = [str(c)[:80] for c in (resp.get("markers") or {})]
            elif mode == "genes":
                d["n_ranking"] = len(resp.get("celltype_ranking") or [])
                d["ranking_classes_top"] = [
                    str(r.get("cell_type", ""))[:80]
                    for r in (resp.get("celltype_ranking") or [])[:20]]
                g2c = resp.get("gene_to_celltypes") or {}
                d["n_genes_queried"] = len(g2c)
                d["n_genes_hit"] = sum(1 for v in g2c.values() if v)
        elif tool == "search_literature":
            rs = resp.get("results") or []
            d["n_results"] = len(rs)
            d["pmids"] = sorted({str(r.get("pmid")) for r in rs
                                 if isinstance(r, dict) and r.get("pmid")})[:30]
        elif tool == "get_kb_page":
            d["found"] = bool(resp.get("found", resp.get("file")))
            d["file"] = str(resp.get("file", ""))[:120]
        elif tool == "get_tissue_composition":
            es = resp.get("entries") or resp.get("composition") or []
            d["n_entries"] = len(es) if isinstance(es, (list, dict)) else None
        elif tool == "get_disease_prior":
            d["found"] = bool(resp.get("found", resp.get("priors")))
    except Exception as e:
        d["digest_error"] = str(e)[:120]
    return d


def _target_file():
    day = time.strftime("%Y-%m-%d")
    base = os.path.join(TRACE_DIR, f"calls_{day}.jsonl")
    if not os.path.exists(base) or os.path.getsize(base) < MAX_DAY_BYTES:
        return base
    n = 2
    while True:
        p = os.path.join(TRACE_DIR, f"calls_{day}.part{n}.jsonl")
        if not os.path.exists(p) or os.path.getsize(p) < MAX_DAY_BYTES:
            return p
        n += 1


def trace(tool, args, resp):
    """Call once after a tool returns; write-only to disk, read-only on resp, all exceptions swallowed."""
    try:
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "tool": tool,
            "args": _args_safe(args),
        }
        rec.update(_env_state())
        rec.update({"session": _SESSION["session_uuid"], "pid": _SESSION["pid"],
                    "ppid": _SESSION["ppid"], "host": _SESSION["host"],
                    "tag": _SESSION["tag"], "caller": _SESSION["caller"]})
        rec["resp"] = _resp_digest(tool, resp)
        os.makedirs(TRACE_DIR, exist_ok=True)
        line = json.dumps(rec, ensure_ascii=False, default=str)
        with open(_target_file(), "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # A tracing failure must never affect service behavior (silent; never print to
        # stdout — that is the stdio protocol channel)
        pass
