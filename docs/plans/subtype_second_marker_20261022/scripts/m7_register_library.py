#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m7 -- register the `subtype_v14` library on the shipped core surface, REGISTERED DEFAULT OFF
with an EMPTY whitelist.

The edit is the house pattern for a registered-but-OFF increment (the same four anchors the
`onfibro_v13` wave used), with the property this card's red line demands: the whitelist is EMPTY, so
`EYEKB_ACT_SUBTYPE` cannot inject the library into the default `all` set in any state -- the only way
to reach it is to name it (`library="subtype_v14"`). No other wave's `*_DEFAULT_LIBS` tuple is
touched. The default route's response bytes are then MEASURED (m9), not asserted.

Every replacement asserts its anchor appears exactly once, so a silent no-op cannot pass for a
registration.

Writes out/REGISTER_LIBRARY.json.
"""
import hashlib
import json
import os

REPO = "/home/ubuntu/EYEKB_REPO"
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))

ANCHOR_LIBS = '    "onfibro_v13": MARKER_DIR / "markers_v13_onfibro_increment.json"}'
NEW_LIBS = '''    "onfibro_v13": MARKER_DIR / "markers_v13_onfibro_increment.json",
    # subtype_v14 = the second-marker increment for the 26 one-gene-thick subtype panels
    #   (2026-10-22, card t_7509a1a2): 16 entries, one per literature-consensus retinal subtype the
    #   frozen consensus wave measured as having exactly one marker clearing its pre-registered gate,
    #   each named by the Cell Ontology label of the term it carries and holding the frozen panel plus
    #   at most 2 literature-sourced candidates (segment-level attribution against the in-repo
    #   literature corpus; every candidate carries its paper ids and its per-volume measurability in
    #   the file itself).
    #   Why the anchor line above is REPEATED in this replacement: the previous wave's append dropped
    #   that very line from the dictionary (measured: the default route raised KeyError onfibro_v13),
    #   so an append that does not echo its anchor is a known way to break the shipped surface.
    #   REGISTERED_DEFAULT_OFF with an EMPTY whitelist: nothing is merged into `all` in any state, so
    #   the shipped default route is byte-identical; merging it needs its own measured harm line and
    #   separate PI approval. Rollback = delete the subtype_v14 lines and the file.
    "subtype_v14": MARKER_DIR / "markers_v14_subtype_second_increment.json"}'''

ANCHOR_PRED = 'def _antseg_act_enabled():'
NEW_PRED = '''# [SUBTYPE2 t_7509a1a2] whitelist for the second-marker subtype increment.  EMPTY BY DESIGN: the
# registration is deliberately unreachable from the default `all` set, so this predicate exists to
# make the OFF state explicit and machine-readable rather than to open a route.  Semantics follow the
# ACT-v6 discipline so a future activation wave inherits an obvious shape:
# {0,false,off,no} = OFF; unset/empty/anything else = the value of this switch, which -- with an
# empty whitelist -- still merges nothing.
SUBTYPE_DEFAULT_LIBS = ()


def _subtype_act_enabled():
    """env EYEKB_ACT_SUBTYPE in {0,false,off,no} = OFF; unset/anything else = ON.

    ON still injects nothing: SUBTYPE_DEFAULT_LIBS is empty by design (card t_7509a1a2 red line --
    this registration may not change the default response bytes). The library is reachable by name
    only, and the panel it carries is a measurement artefact, not a shipped route.
    """
    v = (os.environ.get("EYEKB_ACT_SUBTYPE") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _antseg_act_enabled():'''

ANCHOR_LOAD = '''        if _onfibro_act_enabled():
            names = names + list(ONFIBRO_DEFAULT_LIBS)  # [ONFIBRO] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit'''
NEW_LOAD = '''        if _onfibro_act_enabled():
            names = names + list(ONFIBRO_DEFAULT_LIBS)  # [ONFIBRO] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit
        if _subtype_act_enabled():
            names = names + list(SUBTYPE_DEFAULT_LIBS)  # [SUBTYPE2] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit'''

ANCHOR_ERR = '"lensiris_v11|holefill_v12|onfibro_v13|all, got: "'
NEW_ERR = '"lensiris_v11|holefill_v12|onfibro_v13|subtype_v14|all, got: "'


def sub(path, old, new):
    s = open(path, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "anchor appears %d times, refusing to guess: %r" % (n, old[:80])
    open(path, "w", encoding="utf-8").write(s.replace(old, new))


def main():
    src = open(CORE, encoding="utf-8").read()
    out_path = os.path.join(OUT, "REGISTER_LIBRARY.json")
    if '"subtype_v14": MARKER_DIR' in src and "SUBTYPE_DEFAULT_LIBS = ()" in src:
        doc = {"probe": "m7_register_library.py", "file": "mcp_server/eyekb_core.py",
               "status": "ALREADY_APPLIED (idempotent skip; the registration is on disk)",
               "library": "subtype_v14", "whitelist": "empty by design",
               "sha256": hashlib.sha256(open(CORE, "rb").read()).hexdigest()}
        json.dump(doc, open(out_path, "w"), ensure_ascii=False, indent=1)
        print(json.dumps(doc, ensure_ascii=False, indent=1))
        return
    before = hashlib.sha256(src.encode()).hexdigest()
    for old, new in ((ANCHOR_LIBS, NEW_LIBS), (ANCHOR_PRED, NEW_PRED),
                     (ANCHOR_LOAD, NEW_LOAD), (ANCHOR_ERR, NEW_ERR)):
        sub(CORE, old, new)
    import py_compile
    py_compile.compile(CORE, doraise=True)
    doc = {"probe": "m7_register_library.py", "file": "mcp_server/eyekb_core.py",
           "edits": 4, "library": "subtype_v14", "whitelist": "empty by design", "compiles": True,
           "sha256_before": before,
           "sha256": hashlib.sha256(open(CORE, "rb").read()).hexdigest(),
           "bytes": os.path.getsize(CORE)}
    json.dump(doc, open(out_path, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(doc, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()