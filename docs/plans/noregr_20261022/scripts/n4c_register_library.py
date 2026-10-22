#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""n4c -- register the `onfibro_v13` library on the shipped core surface.

The edit is the house pattern for a registered-but-OFF increment, with one deliberate difference
that this card's red line requires: the whitelist is EMPTY. `EYEKB_ACT_ONFIBRO` therefore cannot
inject the library into the default `all` set in any state -- the only way to reach it is to name
it (`library="onfibro_v13"`), and the merged effect is measured by the harness's injected arm, not
by a shipped switch. The default route's response bytes are unchanged by construction.

Every replacement asserts its own anchor appears exactly once, so a silent no-op cannot pass for a
registration.
"""
import json
import os
import sys

REPO = "/home/ubuntu/EYEKB_REPO"
CORE = os.path.join(REPO, "mcp_server", "eyekb_core.py")

ANCHOR_LIBS = ('    "holefill_v12": MARKER_DIR / "markers_v12_holefill_increment.json"}')
NEW_LIBS = '''    # onfibro_v13 = the optic-nerve fibroblast carrier (2026-10-22, card t_0c40c7b1): ONE entry,
    #   named by the Cell Ontology label of the generic family term it carries (CL:0000057
    #   `fibroblast`, resolved against the in-repo ontology release), holding the 10 genes of the
    #   shipped generic `Fibroblast` panel plus 2 genes of the motivating cluster's recorded window
    #   (BICC1, EYA2) so the family's coarse carrier can clear the >=2 shared-gene bar.
    #   Why it exists: kb/baselines/_tissue_class_crosswalk_v1.json excludes
    #   `Limbus_Sclera_fibroblast_C1` for optic_nerve, and with EYEKB_TISSUE_SCOPE on (default) that
    #   removal left the family with no reachable carrier at all, so a coarse-but-family-correct
    #   answer degraded to an abstention (measured: CX15_optic_nerve_all cluster 31, 1,822 cells,
    #   -2.53pp cell-weighted on that volume).
    #   REGISTERED_DEFAULT_OFF with an EMPTY whitelist: nothing is merged into `all` in any state,
    #   so the shipped default route is byte-identical; merging it needs its own measured harm line
    #   and separate PI approval. Rollback = delete this line and the file.
    "onfibro_v13": MARKER_DIR / "markers_v13_onfibro_increment.json"}'''

ANCHOR_PRED = '''def _antseg_act_enabled():'''
NEW_PRED = '''# [ONFIBRO t_0c40c7b1] whitelist for the optic-nerve fibroblast carrier.  EMPTY BY DESIGN: the
# registration is deliberately unreachable from the default `all` set, so this predicate exists to
# make the OFF state explicit and machine-readable rather than to open a route.  Semantics follow
# the ACT-v6 discipline so a future activation wave inherits an obvious shape:
# {0,false,off,no} = OFF; unset/empty/anything else = the value of this switch, which -- with an
# empty whitelist -- still merges nothing.
ONFIBRO_DEFAULT_LIBS = ()


def _onfibro_act_enabled():
    """env EYEKB_ACT_ONFIBRO in {0,false,off,no} = OFF; unset/anything else = ON.

    ON still injects nothing: ONFIBRO_DEFAULT_LIBS is empty by design (card t_0c40c7b1 red line --
    this registration may not change the default response bytes). The library is reachable by name
    only, and the merged effect is a measurement artefact, not a shipped route.
    """
    v = (os.environ.get("EYEKB_ACT_ONFIBRO") or "").strip().casefold()
    return v not in {"0", "false", "off", "no"}


def _antseg_act_enabled():'''

ANCHOR_LOAD = '''        if _antseg_act_enabled():
            names = names + list(ANTSEG_DEFAULT_LIBS)  # [ANTSEG] non-retinal increment, ON since 2026-10-20'''
NEW_LOAD = '''        if _antseg_act_enabled():
            names = names + list(ANTSEG_DEFAULT_LIBS)  # [ANTSEG] non-retinal increment, ON since 2026-10-20
        if _onfibro_act_enabled():
            names = names + list(ONFIBRO_DEFAULT_LIBS)  # [ONFIBRO] empty whitelist: appends nothing,
            # and the branch is kept so the OFF state is auditable rather than implicit'''

ANCHOR_ERR = ('"lensiris_v11|holefill_v12|all, got: "')
NEW_ERR = ('"lensiris_v11|holefill_v12|onfibro_v13|all, got: "')


def sub(path, old, new):
    s = open(path, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, "anchor appears %d times, refusing to guess: %r" % (n, old[:80])
    open(path, "w", encoding="utf-8").write(s.replace(old, new))


def main():
    src = open(CORE, encoding="utf-8").read()
    if '"onfibro_v13": MARKER_DIR' in src and "ONFIBRO_DEFAULT_LIBS = ()" in src:
        out = {"probe": "n4c_register_library.py", "file": "mcp_server/eyekb_core.py",
               "status": "ALREADY_APPLIED (idempotent skip; the registration is on disk)",
               "library": "onfibro_v13", "whitelist": "empty by design",
               "sha256": __import__("hashlib").sha256(src.encode()).hexdigest()}
        p0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                          "REGISTER_LIBRARY.json")
        json.dump(out, open(os.path.abspath(p0), "w"), ensure_ascii=False, indent=1)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    for old, new in ((ANCHOR_LIBS, NEW_LIBS), (ANCHOR_PRED, NEW_PRED),
                     (ANCHOR_LOAD, NEW_LOAD), (ANCHOR_ERR, NEW_ERR)):
        sub(CORE, old, new)
    import py_compile
    py_compile.compile(CORE, doraise=True)
    out = {"probe": "n4c_register_library.py", "file": "mcp_server/eyekb_core.py",
           "edits": 4, "library": "onfibro_v13", "whitelist": "empty by design",
           "compiles": True,
           "sha256": __import__("hashlib").sha256(open(CORE, "rb").read()).hexdigest()}
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                     "REGISTER_LIBRARY.json")
    json.dump(out, open(os.path.abspath(p), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()