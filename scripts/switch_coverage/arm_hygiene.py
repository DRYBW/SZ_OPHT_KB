#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arm_hygiene.py -- discover, clear and assert every environment switch the router honours.

Why this module exists
----------------------
`docs/plans/noregr_20261022/scripts/wave_common.py` clears a HARD-CODED tuple of switch names
before each measurement arm. `EYEKB_ACT_ONFIBRO` was added to the router after that tuple was
written, so it was never cleared: a before arm that set `EYEKB_ACT_ONFIBRO=0` left it set for the
after arm *inside the same process*, and an after arm written as `{}` -- the natural way to say
"the tree as shipped" -- silently became a self-comparison reporting `changed = 0`.

The frozen harness is a delivered artefact and is not edited here. Instead this module derives the
switch list from the source at run time, so a switch added later cannot be forgotten, and exposes
`assert_arms_differ()` so a comparison refuses to produce numbers when its two arms are not
actually in different states.

Discovered read forms: `os.environ.get("EYEKB_...")` and `os.environ["EYEKB_..."]`.
Nothing here writes to disk or touches the network.
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))  # scripts/switch_coverage -> repo root
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
SCAN_DIRS = (os.path.join(REPO, "mcp_server"), os.path.join(REPO, "pipeline"))

_READ = re.compile(r'os\.environ(?:\.get\(|\[)\s*["\'](EYEKB_[A-Z0-9_]+)["\']')

# Fail-closed classification. A name is treated as ANSWER-AFFECTING -- i.e. capable of moving a
# recorded-set ranking or grade -- unless it appears here with a reason to the contrary. Keeping the
# benign list explicit and short is deliberate: an unrecognised switch added by a later card is
# then treated as dangerous rather than silently waved through.
BENIGN = {
    "EYEKB_ABSTAIN_REASON": "supplies the human-readable abstention reason string; it does not "
                            "change which candidate is ranked first or how a cluster is graded",
    "EYEKB_DB_DIR": "selects the directory the marker libraries are read from",
    "EYEKB_MCP_SOFTFLAGS": "display flag on the tool response",
    "EYEKB_MCP_TRACE_TAG": "trace tag on the tool response",
    "EYEKB_TRACE_DIR": "directory that trace output is written to",
}


def answer_affecting(names=None):
    """Discovered names minus the declared-benign list. Fail-closed by construction."""
    names = discover() if names is None else list(names)
    return sorted(n for n in names if n not in BENIGN)


def required_explicit():
    """Answer-affecting names the frozen harness does not clear: an arm that sets one must set it
    in every arm of the same comparison."""
    cleared = set(harness_switches())
    return tuple(n for n in answer_affecting() if n not in cleared)


def contaminating(names_before, names_after):
    """The names that make a comparison unsafe: set in one arm, not in the other, and not cleared
    by the frozen harness between arms."""
    cleared = set(harness_switches())
    b, a = set(names_before or ()), set(names_after or ())
    return sorted(((b | a) - cleared) - ((b & a)))


def discover(dirs=SCAN_DIRS):
    """Every EYEKB_* environment name the code under `dirs` reads, sorted."""
    found = set()
    for d in dirs:
        for root, _sub, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                try:
                    with open(os.path.join(root, fn), encoding="utf-8", errors="replace") as fh:
                        found.update(_READ.findall(fh.read()))
                except OSError:
                    continue
    return sorted(found)


def harness_switches():
    """The name tuple the frozen recorded-set harness clears, read without importing it."""
    path = os.path.join(REPO, "docs", "plans", "noregr_20261022", "scripts", "wave_common.py")
    import ast
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "SWITCHES":
                    return tuple(ast.literal_eval(node.value))
    raise RuntimeError("SWITCHES not found in %s" % path)


def clear_all(extra_dirs=None):
    """Pop every EYEKB_* switch the code reads. Returns the names removed."""
    names = discover() if not extra_dirs else discover(extra_dirs)
    removed = []
    for n in names:
        if os.environ.pop(n, None) is not None:
            removed.append(n)
    return removed


def fresh_core(overlay_env=None, wave_scripts=None):
    """Import eyekb_core with the complete switch set cleared, then apply `overlay_env`.

    Deliberately does NOT call the frozen `wave_common.clear_switches()`: that is the function
    whose incomplete list caused the contamination this module exists to prevent.
    """
    clear_all()
    for k, v in (overlay_env or {}).items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    for m in [k for k in list(sys.modules) if k == "eyekb_core" or k.startswith("eyekb_core.")]:
        del sys.modules[m]
    core_dir = os.path.join(REPO, "mcp_server")
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)
    if overlay_env is not None:
        for n in answer_affecting():
            if n not in (overlay_env or {}) and os.environ.get(n) is not None:
                raise RuntimeError("switch %s survived clear_all()" % n)
    import eyekb_core as core
    return core


def probe_state(env, probes):
    """Realise one arm and read back the switches named in `probes` ({label: (attr, envname)})."""
    core = fresh_core(env)
    return {label: bool(getattr(core, attr)()) for label, (attr, _env) in probes.items()}


def assert_arms_differ(before_env, after_env, probes, label=""):
    """Refuse a comparison whose two arms land in the same state on every probed switch."""
    b = probe_state(before_env, probes)
    a = probe_state(after_env, probes)
    differs = sorted(k for k in probes if b[k] != a[k])
    if not differs:
        raise SystemExit("ARM HYGIENE FAIL%s: arms are not in different states on any probed "
                         "switch (%s); this comparison would report a self-comparison as a null"
                         % ((" [%s]" % label) if label else "", ", ".join(sorted(probes))))
    return {"before": b, "after": a, "differs_on": differs}


if __name__ == "__main__":
    d = discover()
    sw = set(harness_switches())
    req = set(required_explicit())
    print("discovered %d EYEKB_* switches; %d answer-affecting; %d not cleared by the frozen harness"
          % (len(d), len(answer_affecting()), len(req)))
    for n in d:
        mark = "answer-affecting" if n in answer_affecting() else "declared benign"
        clear = "cleared by frozen harness" if n in sw else "NOT cleared by frozen harness"
        tail = "  <-- an arm that sets it must set it in every arm" if n in req else ""
        print("  %-36s %-19s %s%s" % (n, mark, clear, tail))